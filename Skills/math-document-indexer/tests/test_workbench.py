import io
import json
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import mathdoc
import workbench


class UploadTests(unittest.TestCase):
    def setUp(self):
        (ROOT/'work').mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT/'work')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.server = workbench.create_server(port=0,workspace=self.root)
        self.thread = threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()
        self.addCleanup(self.close)
        self.url = f'http://127.0.0.1:{self.server.server_port}'
        self.token = self.request('/api/info')[1]['token']

    def close(self):
        self.server.shutdown()
        self.thread.join()
        self.server.server_close()

    def request(self,path,data=None,headers=None):
        request = Request(self.url+path,data=data,headers={'X-Mathdoc-Token':getattr(self,'token',''),**(headers or {})})
        try:
            response = urlopen(request,timeout=10)
        except HTTPError as error:
            response = error
        with response:
            raw = response.read()
            try: value = json.loads(raw)
            except ValueError: value = raw
            return response.status,value,response.headers

    def wait_job(self,key):
        deadline = time.monotonic()+15
        while time.monotonic()<deadline:
            job = self.request('/api/job?key='+key)[1]
            if job['status']!='processing': return job
            time.sleep(.03)
        self.fail('Upload did not finish')

    def test_upload_tex_activate_persist_and_save(self):
        self.assertIsNone(self.request('/api/document')[1])
        data = (ROOT/'assets/example.tex').read_bytes()
        status,job,_ = self.request('/api/upload',data,{'X-File-Name':'paper.tex'})
        self.assertEqual(status,202)
        result = self.wait_job(job['key']);self.assertEqual(result['status'],'completed')
        self.assertIsNone(self.request('/api/document')[1])
        self.request('/api/activate',json.dumps({'key':job['key']}).encode())
        _,doc,headers = self.request('/api/document')
        self.assertEqual(doc['review']['status'],'draft')
        self.assertEqual(doc['source']['title'],'paper')
        self.assertEqual(self.request('/source')[1],data)
        self.assertEqual(self.request('/api/save',mathdoc.dumps(doc),{'If-Match':'stale'})[0],409)
        self.assertEqual(self.request('/api/save',mathdoc.dumps(doc),{'If-Match':headers['ETag']})[0],200)
        restarted = workbench.Workspace(self.root)
        self.assertEqual(restarted.active,job['key'])
        self.assertEqual(len(restarted.library()),1)
        self.assertTrue(restarted.paths()[0].is_file())

    def test_pdf_scanned_partial_range_and_failed_job_preserve_active_document(self):
        from pypdf import PdfWriter
        writer = PdfWriter();writer.add_blank_page(100,100);writer.add_blank_page(100,100)
        stream = io.BytesIO();writer.write(stream)
        _,job,_ = self.request('/api/upload?pages=2&render=1',stream.getvalue(),{'X-File-Name':'scan.pdf'})
        self.assertEqual(self.wait_job(job['key'])['status'],'completed')
        self.request('/api/activate',mathdoc.dumps({'key':job['key']}))
        doc = self.request('/api/document')[1]
        self.assertEqual(doc['source']['processed_pages'],[2]);self.assertFalse(doc['source']['complete'])
        self.assertTrue(doc['unresolved']);self.assertEqual(doc['source']['kind'],'scan_pdf')
        self.assertTrue((self.root/'documents'/job['key']/'prepared/pages/0002.png').is_file())
        _,bad,_ = self.request('/api/upload?pages=8',stream.getvalue(),{'X-File-Name':'bad.pdf'})
        self.assertEqual(self.wait_job(bad['key'])['status'],'failed')
        self.assertEqual(self.request('/api/info')[1]['active'],job['key'])
        self.assertEqual(len(self.request('/api/library')[1]),1)

    def test_upload_validation_and_request_auth(self):
        for filename,data in [('paper.exe',b'bad'),('paper.pdf',b'not PDF'),('paper.tex',b'\xff')]:
            self.assertEqual(self.request('/api/upload',data,{'X-File-Name':filename})[0],400)
        for headers in [{'X-Mathdoc-Token':'wrong'},{'Origin':'https://example.com'},{'Host':'example.com'}]:
            self.assertEqual(self.request('/api/upload',b'hello',{'X-File-Name':'paper.tex',**headers})[0],403)
        _,job,_ = self.request('/api/upload',b'An original statement.',{'X-File-Name':'../../escape.tex'})
        self.assertEqual(self.wait_job(job['key'])['status'],'completed')
        self.assertFalse((self.root.parent/'escape.tex').exists())

    def test_import_json_does_not_bind_to_another_source_and_stale_tab_cannot_save(self):
        doc = mathdoc.read(ROOT/'assets/example.indexed.json')
        first = self.request('/api/import-json',mathdoc.dumps(doc))[1]['key']
        second = self.request('/api/import-json',mathdoc.dumps(doc))[1]['key']
        self.request('/api/activate',mathdoc.dumps({'key':first}))
        etag = self.request('/api/document')[2]['ETag']
        self.assertFalse(self.request('/api/info')[1]['source_available'])
        self.request('/api/activate',mathdoc.dumps({'key':second}))
        self.assertEqual(self.request('/api/save',mathdoc.dumps(doc),{'If-Match':etag})[0],409)
        self.assertEqual(len(self.request('/api/library')[1]),2)


if __name__=='__main__': unittest.main()
