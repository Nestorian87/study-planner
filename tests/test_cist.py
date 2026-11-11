import csv
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

SPEC=importlib.util.spec_from_file_location('cist',Path(__file__).resolve().parents[1]/'skills/study-planner/scripts/cist.py')
cist=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(cist)

def fixture(title='Лабораторна ГРУПА-1',date='11.11.2026'):
    out=io.StringIO(newline='');writer=csv.writer(out,lineterminator='\r')
    writer.writerow(cist.HEADERS);writer.writerow([title,date,'11:15:00',date,'12:50:00','Ложь','Истина',date,'11:10:00','2','Обычная',title,'Обычный'])
    return out.getvalue().encode('cp1251')

class CistTests(unittest.TestCase):
    def parse(self,b):return cist.parse_csv(b,'group','12345678','2026-11-09','2026-11-15')
    def test_cp1251_cr_and_timezone(self):
        p=self.parse(fixture());self.assertEqual(len(p['events']),1);self.assertTrue(p['events'][0]['starts_at'].endswith('+02:00'))
        self.assertIn('ГРУПА',p['events'][0]['title'])
    def test_utf8(self):
        self.assertEqual(self.parse(fixture())['events'],self.parse(fixture().decode('cp1251').encode('utf-8-sig'))['events'])
    def test_html_is_not_empty_schedule(self):
        with self.assertRaises(ValueError):self.parse(b'<html>Oracle error</html>')
    def test_unknown_format(self):
        with self.assertRaises(ValueError):self.parse(b'title,start\rabc,2026\r')
    def test_out_of_range(self):
        with self.assertRaises(ValueError):self.parse(fixture(date='01.12.2026'))
    def test_truncated_row(self):
        with self.assertRaises(ValueError):self.parse(fixture()+b'broken\r')
    def test_identity_stable_but_content_change_detected(self):
        a=self.parse(fixture());b=self.parse(fixture());changed=self.parse(fixture('Інша робота'))
        self.assertEqual(a['events'][0]['source_key'],b['events'][0]['source_key']);self.assertNotEqual(a['sha256'],changed['sha256'])
    def test_empty_export_explicit(self):
        self.assertEqual(self.parse(fixture().split(b'\r')[0]+b'\r')['events'],[])
    def test_invalid_range_and_id(self):
        for start,end in [('2026-11-15','2026-11-09'),('2025-01-01','2026-11-09')]:
            with self.assertRaises(ValueError):cist.url('group','123',start,end)
        with self.assertRaises(ValueError):cist.url('group','../bad','2026-11-09','2026-11-15')
    def test_teaching_keeps_lab_practice_lecturer_separate(self):
        source='''<table class="footer"><tr><td><a name="10">SUBJ</a></td><td>Subject :
        Лк (20) - Group, <a href="f?p=:202::::202:P202_FIRST_DATE,P202_LAST_DATE,P202_SOTR,P202_KAF:01.09.2026,28.02.2027,100,0:">Lecturer</a>:
        Пз (4) - Group, <a href="f?p=:202::::202:P202_FIRST_DATE,P202_LAST_DATE,P202_SOTR,P202_KAF:01.09.2026,28.02.2027,200,0:">Practical teacher</a>:
        Лб (16) - Group, <a href="f?p=:202::::202:P202_FIRST_DATE,P202_LAST_DATE,P202_SOTR,P202_KAF:01.09.2026,28.02.2027,300,0:">Lab teacher</a>:
        </td></tr></table>'''
        actual=cist.parse_teaching(source.encode('cp1251'))[0]['assignments']
        self.assertEqual([(x['kind'],x['teacher_id']) for x in actual],[('Лк','100'),('Пз','200'),('Лб','300')])
    def test_missing_teaching_legend_is_not_empty_success(self):
        with self.assertRaises(ValueError):cist.parse_teaching(b'<html>No footer</html>')
    def test_failed_parse_does_not_replace_good_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'cache.json';cist.save_atomic(p,self.parse(fixture()));before=p.read_bytes()
            try:cist.save_atomic(p,self.parse(b'<html>error</html>'))
            except ValueError:pass
            self.assertEqual(p.read_bytes(),before)

if __name__=='__main__':unittest.main()
