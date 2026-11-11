#!/usr/bin/env python3
"""Read-only official CIST CSV adapter. No Notion writes or third-party schedules."""
import argparse
import csv
import datetime as dt
import hashlib
import html
import http.cookiejar
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import unicodedata
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

BASE = 'https://cist2.nure.ua/ias/app/tt/'
ZONE = ZoneInfo('Europe/Kyiv')
HEADERS = ['Тема', 'Дата начала', 'Время начала', 'Дата завершения', 'Время завершения',
           'Ежедневное событие', 'Оповещение вкл/выкл', 'Дата оповещения',
           'Время оповещения', 'В это время', 'Важность', 'Описание', 'Пометка']

def interval(start, end):
    a,b=dt.date.fromisoformat(start),dt.date.fromisoformat(end)
    if b<a or (b-a).days>370:
        raise ValueError('Період повинен бути впорядкований і не довший за 371 день')
    return a,b

def url(kind, identity, start, end):
    a,b=interval(start,end)
    if kind not in ('group','teacher') or not str(identity).isdigit() or int(identity)<=0:
        raise ValueError('Некоректні тип розкладу або ID')
    query=dict(ATypeDoc=3,ADateStart=a.strftime('%d.%m.%Y'),ADateEnd=b.strftime('%d.%m.%Y'),AMultiWorkSheet=0)
    if kind=='group':
        endpoint='WEB_IAS_TT_GNR_RASP.GEN_GROUP_POTOK_RASP';query.update(Aid_group=identity,Aid_potok=0)
    else:
        endpoint='WEB_IAS_TT_GNR_RASP.GEN_TEACHER_KAF_RASP';query.update(Aid_sotr=identity,Aid_kaf=0)
    return BASE+endpoint+'?'+urllib.parse.urlencode(query)

def read_url(address, opener=None):
    opener=opener or urllib.request.build_opener()
    with opener.open(address,timeout=25) as response:
        parsed=urllib.parse.urlparse(response.url)
        if parsed.scheme!='https' or parsed.hostname!='cist2.nure.ua':
            raise ValueError('Неочікуване перенаправлення за межі офіційного CIST')
        body=response.read(8_000_001)
        if len(body)>8_000_000:
            raise ValueError('Відповідь надто велика')
        return body

def parse_csv(body, kind, identity, start, end):
    a,b=interval(start,end)
    try:
        text=body.decode('utf-8-sig')
        encoding='utf-8'
    except UnicodeDecodeError:
        text=body.decode('cp1251');encoding='windows-1251'
    if text.lstrip().startswith('<'):
        raise ValueError('Замість CSV отримано HTML; попередні дані залишаються чинними з позначкою застарілості')
    rows=list(csv.reader(io.StringIO(text,newline=''),strict=True))
    if not rows or rows[0]!=HEADERS:
        raise ValueError('Невідомий формат CSV CIST')
    events=[];seen=set();duplicates=[]
    for index,row in enumerate(rows[1:],2):
        if len(row)!=len(HEADERS):
            raise ValueError(f'Некоректна кількість полів у рядку {index}')
        begin=dt.datetime.strptime(row[1]+' '+row[2],'%d.%m.%Y %H:%M:%S').replace(tzinfo=ZONE)
        finish=dt.datetime.strptime(row[3]+' '+row[4],'%d.%m.%Y %H:%M:%S').replace(tzinfo=ZONE)
        if finish<=begin or not a<=begin.date()<=b or not a<=finish.date()<=b:
            raise ValueError(f'Дата поза запитаним періодом або некоректний час у рядку {index}')
        # Notification fields change without changing the lesson itself.
        natural=[kind,str(identity),row[0],begin.isoformat(),finish.isoformat(),row[11]]
        key=hashlib.sha256(json.dumps(natural,ensure_ascii=False).encode()).hexdigest()[:24]
        if key in seen:duplicates.append(index)
        seen.add(key)
        events.append(dict(source_key=key,title=row[0],starts_at=begin.isoformat(),ends_at=finish.isoformat(),
                           description=row[11],raw=dict(zip(HEADERS,row))))
    return dict(schema_version=1,source='official-cist2',kind=kind,identity=str(identity),
                period=dict(start=start,end=end),fetched_at=dt.datetime.now(ZONE).isoformat(),
                source_url=url(kind,identity,start,end),sha256=hashlib.sha256(body).hexdigest(),encoding=encoding,
                events=events,warnings=['CSV містить заняття, а не підтверджені захисти.',
                'Вибіркові дисципліни та потоки потребують перевірки.']+
                ([f'Повторні записи збережено, рядки: {duplicates}'] if duplicates else []))

def lookup_group(name):
    opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    text=read_url(BASE+'f?p=778:2:0',opener).decode('cp1251')
    entries=re.findall(r"IAS_ADD_Group_in_List\('([^']+)',\s*(\d+)\)",text)
    norm=lambda s:unicodedata.normalize('NFKC',s).strip().casefold()
    found=list(dict.fromkeys((label,key) for label,key in entries if norm(label)==norm(name)))
    if len(found)!=1:
        raise ValueError('Групу не знайдено однозначно в поточному офіційному довіднику')
    return dict(name=found[0][0],id=found[0][1],source_url=BASE+'f?p=778:2:0')

def parse_teaching(body):
    """Official HTML export legend: preserve separate teaching roles and streams."""
    text=body.decode('cp1251')
    footer=re.search(r'<table\b[^>]*class="footer"[^>]*>(.*?)</table>',text,re.S|re.I)
    if not footer:
        raise ValueError('В офіційному HTML немає довідки про викладачів')
    plain=lambda value:' '.join(html.unescape(re.sub(r'<[^>]*>',' ',value)).split())
    courses=[]
    for row in re.findall(r'<tr\b[^>]*>(.*?)</tr>',footer.group(1),re.S|re.I):
        cells=re.findall(r'<td\b[^>]*>(.*?)</td>',row,re.S|re.I)
        if len(cells)!=2:continue
        subject=re.search(r'<a\b[^>]*name="(\d+)"[^>]*>(.*?)</a>',cells[0],re.S|re.I)
        if not subject:continue
        assignments=[]; previous=0
        for match in re.finditer(r'<a\b[^>]*href="([^"]*P202_SOTR[^"]*)"[^>]*>(.*?)</a>',cells[1],re.S|re.I):
            prefix=plain(cells[1][previous:match.start()])
            role=list(re.finditer(r'(Лк|Лб|Пз|Конс|Зал|Екз)\s*\(\d+\)\s*-\s*',prefix))
            identity=re.search(r'P202_SOTR,P202_KAF:[^,]*,[^,]*,(\d+),',html.unescape(match.group(1)))
            if not role or not identity:
                raise ValueError('Не вдалося однозначно зіставити викладача з видом заняття')
            current=role[-1]
            assignments.append(dict(kind=current.group(1),teacher=plain(match.group(2)),
                                    teacher_id=identity.group(1),groups=prefix[current.end():].rstrip(' ,:')))
            previous=match.end()
        if assignments:
            courses.append(dict(subject_id=subject.group(1),alias=plain(subject.group(2)),
                                name=plain(cells[1]).split(' : ',1)[0],assignments=assignments))
    if not courses:raise ValueError('Довідка не містить розпізнаних викладачів')
    return courses

def save_atomic(path, value):
    destination=Path(path);destination.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(dir=destination.parent,prefix='.cist-')
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as file:
            json.dump(value,file,ensure_ascii=False,indent=2,allow_nan=False);file.write('\n')
            file.flush();os.fsync(file.fileno())
        os.replace(name,destination)
    finally:
        if os.path.exists(name):os.unlink(name)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    lookup=commands.add_parser('lookup-group');lookup.add_argument('name')
    for command in ('fetch','teaching'):
        fetch=commands.add_parser(command)
        if command=='fetch':fetch.add_argument('--kind',choices=['group','teacher'],required=True)
        fetch.add_argument('--id',required=True)
        fetch.add_argument('--from',dest='start',required=True)
        fetch.add_argument('--to',dest='end',required=True)
        fetch.add_argument('--output',help='JSON-файл кешу; замінюється лише після повної перевірки')
    args=parser.parse_args()
    if args.command=='lookup-group':result=lookup_group(args.name)
    elif args.command=='fetch':
        address=url(args.kind,args.id,args.start,args.end)
        result=parse_csv(read_url(address),args.kind,args.id,args.start,args.end)
        if args.output:save_atomic(args.output,result)
    else:
        address=url('group',args.id,args.start,args.end).replace('ATypeDoc=3','ATypeDoc=1')
        result=dict(source_url=address,fetched_at=dt.datetime.now(ZONE).isoformat(),
                    group_id=args.id,period=dict(start=args.start,end=args.end),
                    courses=parse_teaching(read_url(address)))
        if args.output:save_atomic(args.output,result)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':
    try:main()
    except Exception as error:
        print(json.dumps(dict(error=str(error),saved=False),ensure_ascii=False),file=sys.stderr);sys.exit(1)
