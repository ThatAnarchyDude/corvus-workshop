"""Exercise the actual HTTP bridge, stream pause, input bounds and RAM validation."""
import io,json,threading,unittest
from types import SimpleNamespace
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer
from PIL import Image
from cloud_test_suite import Session,handler_for,RAMProbe
from unittest.mock import patch
from live_core import field_metrics

class LiveTesting(unittest.TestCase):
    def setUp(self):
        self.session=Session(SimpleNamespace())
        self.server=ThreadingHTTPServer(('127.0.0.1',0),handler_for(self.session,'test-token','view-token'))
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
    def test_public_viewer_reads_but_cannot_control(self):
        with self.request('/status',token='view-token') as r:self.assertFalse(json.load(r)['can_control'])
        with self.request('/status') as r:self.assertTrue(json.load(r)['can_control'])
        with self.request('/audio.pcm',token='view-token') as r:self.assertEqual(r.status,200)
        for body in ({'video':True},{'button':'a'},{'stop':True},{'activity':'public rewrite'},{'touch':[1,200]}):
            with self.assertRaises(HTTPError) as exc:self.request('/control',body,token='view-token')
            self.assertEqual(exc.exception.code,403)
        self.assertFalse(self.session.video);self.assertTrue(self.session.commands.empty());self.assertFalse(self.session.stop.is_set())

    def test_default_off_and_token_required(self):
        with self.request('/status') as r:self.assertFalse(json.load(r)['video'])
        with self.assertRaises(HTTPError) as exc:self.request('/status',token='wrong')
        self.assertEqual(exc.exception.code,403)
    def test_audio_requires_token_and_tracks_new_chunks(self):
        self.session.audio.extend([(1,b'\x01\x00\x02\x00'),(2,b'\x03\x00\x04\x00')])
        self.session.audio_sequence=2
        with self.assertRaises(HTTPError) as exc:self.request('/audio',token='wrong')
        self.assertEqual(exc.exception.code,403)
        import base64
        with self.request('/audio?after=1') as r: data=json.load(r)
        self.assertEqual(base64.b64decode(data['pcm']),b'\x03\x00\x04\x00')
        with self.request('/audio?after=2') as r:self.assertEqual(json.load(r)['pcm'],'')
        with self.assertRaises(HTTPError) as exc:self.request('/audio?after=invalid')
        self.assertEqual(exc.exception.code,400)

    def test_activity_label_is_bounded_and_exposed(self):
        self.request('/control',{'activity':'Editing Route 5; feed paused'}).close()
        with self.request('/status') as r:self.assertEqual(json.load(r)['activity'],'Editing Route 5; feed paused')
        for value in (123,'x'*161):
            with self.assertRaises(HTTPError) as exc:self.request('/control',{'activity':value})
            self.assertEqual(exc.exception.code,400)

    def test_touch_input_bounds(self):
        self.request('/control',{'touch':[124,268],'frames':8}).close()
        self.assertEqual(self.session.commands.get_nowait(),([124,268],8))
        for point in ([256,0],[0,384],[-1,0],[1.5,2],[1]):
            with self.assertRaises(HTTPError) as exc:self.request('/control',{'touch':point})
            self.assertEqual(exc.exception.code,400)

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
    def test_ram_discovery_retries_after_initial_boot(self):
        probe=RAMProbe(); result={'field_system':'0x22a01e8'}
        with patch('cloud_test_suite.field_metrics',side_effect=[None,result]) as scan:
            self.assertIsNone(probe.read(b'boot',0))
            self.assertIsNone(probe.read(b'intro',1))
            self.assertIsNone(probe.read(b'menu',2))
            self.assertEqual(scan.call_count,1)
            self.assertEqual(probe.read(b'field',5),result)
            self.assertEqual(scan.call_count,2)

    def test_unknown_ram_is_not_fabricated(self):
        self.assertIsNone(field_metrics(b'\0'*0x400000))
        self.assertIsNone(field_metrics(b'short'))


class DashboardStartup(unittest.TestCase):
    def test_script_initializes_status_and_both_screens(self):
        import subprocess,shutil
        from cloud_test_suite import PAGE
        node=shutil.which('node')
        if not node:self.skipTest('Node.js unavailable for dashboard execution')
        script=PAGE.split('<script>',1)[1].split('</script>',1)[0]
        runner=r"""
const vm=require('node:vm'),assert=require('node:assert/strict');
let raw='';process.stdin.setEncoding('utf8');process.stdin.on('data',x=>raw+=x);
process.stdin.on('end',async()=>{
 const elements={},draws=[],animation=[];
 function element(id){return elements[id]??= {hidden:false,naturalWidth:256,style:{},
  append(){},removeAttribute(k){delete this[k]},
  getContext(){return {drawImage(...v){draws.push({id,v})},fillRect(){},fillText(){}}}}}
 const ctx={URLSearchParams,location:{hash:'#token=view-token'},
  document:{querySelector:element,createElement:()=>element('button')},
  requestAnimationFrame:fn=>animation.push(fn),setTimeout(){},
  fetch:async()=>({ok:true,json:async()=>({video:true,can_control:false,label:'test',activity:'test'})})};
 vm.createContext(ctx);vm.runInContext(raw,ctx);
 await new Promise(resolve=>setImmediate(resolve));
 assert.equal(elements['#state'].textContent,'Video ON');
 assert.equal(elements['#video-controls'].hidden,true);
 assert.equal(elements['#buttons'].hidden,true);
 assert.match(elements['#video'].src,/stream\.mjpg\?token=view-token/);
 assert.equal(animation.length,1);animation.shift()();
 assert.deepEqual(draws.map(x=>x.id),['#topscreen','#touchscreen']);
 console.log('Dashboard startup, viewer restrictions and both screen draws PASS');
});
"""
        result=subprocess.run([node,'-e',runner],input=script,text=True,capture_output=True,timeout=10)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('both screen draws PASS',result.stdout)

if __name__=='__main__':unittest.main()
