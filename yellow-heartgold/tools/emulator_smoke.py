import ctypes as C,sys,json,os
from pathlib import Path
from PIL import Image
PROJECT=Path(__file__).resolve().parents[1]
core=C.CDLL(str(PROJECT/'.tools/emulator/desmume_libretro.so'))
root=Path(sys.argv[sys.argv.index('--output-dir')+1]) if '--output-dir' in sys.argv else PROJECT/'build/emulator'
root=root.resolve()
root.mkdir(parents=True,exist_ok=True)
opts={b'desmume_pointer_mouse':b'enabled',b'desmume_pointer_type':b'touch',b'desmume_cpu_mode':b'jit',b'desmume_use_external_bios':b'disabled',b'desmume_opengl_mode':b'disabled',b'desmume_screens_layout':b'top/bottom',b'desmume_internal_resolution':b'256x192'}
strings=[C.create_string_buffer(str(root).encode())]
class Var(C.Structure):_fields_=[('key',C.c_char_p),('value',C.c_char_p)]
class Game(C.Structure):_fields_=[('path',C.c_char_p),('data',C.c_void_p),('size',C.c_size_t),('meta',C.c_char_p)]
@C.CFUNCTYPE(None,C.c_int,C.c_char_p)
def logger(level, message):
    pass
fmt=0;frame=None;buttons=set();touch=None
@C.CFUNCTYPE(C.c_bool,C.c_uint,C.c_void_p)
def env(cmd,p):
 global fmt
 if cmd==27:C.cast(p,C.POINTER(C.c_void_p))[0]=C.cast(logger,C.c_void_p);return True
 if cmd in (9,31,39):C.cast(p,C.POINTER(C.c_char_p))[0]=C.cast(strings[0],C.c_char_p);return True
 if cmd==10:fmt=C.cast(p,C.POINTER(C.c_uint))[0];return True
 if cmd==15:
  v=C.cast(p,C.POINTER(Var)).contents
  if v.key in opts:v.value=opts[v.key];return True
  return False
 if cmd==17:C.cast(p,C.POINTER(C.c_bool))[0]=False;return True
 if cmd==3:C.cast(p,C.POINTER(C.c_bool))[0]=True;return True
 if cmd==52:C.cast(p,C.POINTER(C.c_uint))[0]=0;return True
 if cmd in (16,18,35):return True
 return False
@C.CFUNCTYPE(None,C.c_void_p,C.c_uint,C.c_uint,C.c_size_t)
def video(data,w,h,pitch):
 global frame
 if data and data != C.c_void_p(-1).value:frame=(C.string_at(data,pitch*h),w,h,pitch,fmt)
@C.CFUNCTYPE(None,C.c_int16,C.c_int16)
def audio(a,b):pass
@C.CFUNCTYPE(C.c_size_t,C.c_void_p,C.c_size_t)
def batch(data,n):return n
@C.CFUNCTYPE(None)
def poll():pass
@C.CFUNCTYPE(C.c_int16,C.c_uint,C.c_uint,C.c_uint,C.c_uint)
def inputs(port,device,index,ident):
 if device==1:return int(ident in buttons)
 if device==6 and touch:
  if ident==0:return int(touch[0]/255*65534-32767)
  if ident==1:return int(touch[1]/383*65534-32767)
  if ident==2:return 1
 return 0
for name,fn in [('environment',env),('video_refresh',video),('audio_sample',audio),('audio_sample_batch',batch),('input_poll',poll),('input_state',inputs)]:getattr(core,'retro_set_'+name)(fn)
core.retro_init()
core.retro_load_game.argtypes=[C.POINTER(Game)];core.retro_load_game.restype=C.c_bool
rom=Path(sys.argv[1]);raw=rom.read_bytes();buf=C.create_string_buffer(raw)
game=Game(str(rom).encode(),C.cast(buf,C.c_void_p),len(raw),None)
assert core.retro_load_game(C.byref(game))
core.retro_serialize_size.restype=C.c_size_t
core.retro_serialize.argtypes=[C.c_void_p,C.c_size_t];core.retro_serialize.restype=C.c_bool
core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];core.retro_unserialize.restype=C.c_bool
state=root/'state.bin'
if state.exists() and '--fresh' not in sys.argv:
 rawstate=state.read_bytes();saved=C.create_string_buffer(rawstate);assert core.retro_unserialize(saved,len(rawstate))
actions=json.loads(sys.argv[2]);total=0
for a in actions:
 buttons=set(a.get('buttons',[]));touch=a.get('touch')
 for _ in range(a['frames']):core.retro_run();total+=1
 if 'screenshot' in a and frame:
  data,w,h,pitch,pix=frame
  if pix==1:img=Image.frombytes('RGB',(w,h),data,'raw','BGRX',pitch)
  else:
   out=bytearray()
   for y in range(h):
    for x in range(w):
     v=int.from_bytes(data[y*pitch+x*2:y*pitch+x*2+2],'little')
     if pix==2:r,g,b=(v>>11)&31,(v>>5)&63,v&31;out.extend((r*255//31,g*255//63,b*255//31))
     else:r,g,b=(v>>10)&31,(v>>5)&31,v&31;out.extend((r*255//31,g*255//31,b*255//31))
   img=Image.frombytes('RGB',(w,h),bytes(out))
  img.save(root/a['screenshot'])
core.retro_get_memory_data.restype=C.c_void_p
core.retro_get_memory_size.restype=C.c_size_t
ram_ptr=core.retro_get_memory_data(2);ram_size=core.retro_get_memory_size(2)
if ram_ptr and ram_size:(root/'ram.bin').write_bytes(C.string_at(ram_ptr,ram_size))
n=core.retro_serialize_size();saved=C.create_string_buffer(n);assert core.retro_serialize(saved,n);state.write_bytes(saved.raw)
print('Frames',total,'state bytes',n,'pixel format',fmt,flush=True)
core.retro_unload_game();core.retro_deinit()
