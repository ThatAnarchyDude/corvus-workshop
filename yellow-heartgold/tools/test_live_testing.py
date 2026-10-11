"""Exercise the actual HTTP bridge, stream pause, input bounds and RAM validation."""
import io,json,threading,unittest
from types import SimpleNamespace
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer
from PIL import Image
from cloud_test_suite import Session,handler_for
from live_core import field_metrics

class LiveTesting(unittest.TestCase):
    def setUp(self):
        self.session=Session(SimpleNamespace())
        self.server=ThreadingHTTPServer(('127.0.0.1',0),handler_for(self.session,'test-token'))
        self.server.daemon_threads=True
        self.thread=threading.Thread(target=self.server.serve_forever);self.thread.start()
        self.url=f'http://127.0.0.1:{self.server.server_port}'
    def tearDown(self):
        self.session.stop.set()
        with self.session.lock:self.session.lock.notify_all()
        self.server.shutdown();self.thread.join();self.server.server_close()
    def request(self,path,body=None,token='test-token',origin=None):
        headers={'X-Live-Token':token}
        if origin:headers['Origin']=origin
        return urlopen(Request(self.url+path,data=json.dumps(body).encode() if body is not None else None,headers=headers),timeout=2)
    def test_default_off_and_token_required(self):
        with self.request('/status') as r:self.assertFalse(json.load(r)['video'])
        with self.assertRaises(HTTPError) as exc:self.request('/status',token='wrong')
        self.assertEqual(exc.exception.code,403)
    def test_control_input_and_pause(self):
        self.request('/control',{'button':'a','frames':12}).close()
        self.assertEqual(self.session.commands.get_nowait(),('a',12))
        self.request('/control',{'video':True}).close()
        self.assertTrue(self.session.video)
        self.session.jpeg=b'private frame'
        self.request('/control',{'video':False}).close()
        self.assertIsNone(self.session.jpeg)
    def test_reject_bad_duration_and_cross_origin(self):
        for body in ({'button':'a','frames':0},{'video':'false'},{'button':'not-a-button'}):
            with self.assertRaises(HTTPError) as exc:self.request('/control',body)
            self.assertEqual(exc.exception.code,400)
        with self.assertRaises(HTTPError) as exc:self.request('/control',{'video':True},origin='https://other.invalid')
        self.assertEqual(exc.exception.code,403)
    def test_mjpeg_contains_real_decodable_frame(self):
        self.session.video=True
        b=io.BytesIO();Image.new('RGB',(256,384),'yellow').save(b,'JPEG')
        self.session.jpeg=b.getvalue();self.session.sequence=1
        with self.request('/stream.mjpg?token=test-token') as response:
            self.assertIn('multipart',response.headers['Content-Type'])
            self.assertEqual(response.readline(),b'--frame\r\n')
            response.readline(); length=int(response.readline().split(b':')[1]);response.readline()
            image=Image.open(io.BytesIO(response.read(length)))
            self.assertEqual(image.size,(256,384))
    def test_unknown_ram_is_not_fabricated(self):
        self.assertIsNone(field_metrics(b'\0'*0x400000))
        self.assertIsNone(field_metrics(b'short'))

if __name__=='__main__':unittest.main()
