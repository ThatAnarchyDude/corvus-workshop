"""Single-thread-owned DeSmuME libretro adapter. Never shares live RAM pointers."""
import ctypes as C
import struct
from pathlib import Path
from PIL import Image

class Variable(C.Structure):
    _fields_ = [('key', C.c_char_p), ('value', C.c_char_p)]
class Game(C.Structure):
    _fields_ = [('path', C.c_char_p), ('data', C.c_void_p), ('size', C.c_size_t), ('meta', C.c_char_p)]
class Geometry(C.Structure):
    _fields_ = [('base_width', C.c_uint), ('base_height', C.c_uint),
                ('max_width', C.c_uint), ('max_height', C.c_uint), ('aspect_ratio', C.c_float)]
class Timing(C.Structure):
    _fields_ = [('fps', C.c_double), ('sample_rate', C.c_double)]
class AVInfo(C.Structure):
    _fields_ = [('geometry', Geometry), ('timing', Timing)]

BUTTONS = {'b':0, 'select':2, 'start':3, 'up':4, 'down':5, 'left':6, 'right':7, 'a':8, 'x':9, 'l':10, 'r':11, 'y':1}

class Emulator:
    def __init__(self, core_path, rom_path, save_dir, capture_audio=False):
        self.core = C.CDLL(str(core_path))
        self.frame = None
        self.buttons = set()
        self.pixel = 0
        self.callbacks = []
        self.capture_audio = capture_audio
        self.audio_chunks = []
        self.directory = C.create_string_buffer(str(save_dir).encode())
        opts = {b'desmume_cpu_mode':b'jit', b'desmume_use_external_bios':b'disabled',
                b'desmume_opengl_mode':b'disabled', b'desmume_screens_layout':b'top/bottom',
                b'desmume_internal_resolution':b'256x192'}
        def environment(cmd, p):
            if cmd == 27:
                C.cast(p, C.POINTER(C.c_void_p))[0] = C.cast(self.logger, C.c_void_p); return True
            if cmd in (9,31,39):
                C.cast(p, C.POINTER(C.c_char_p))[0] = C.cast(self.directory,C.c_char_p); return True
            if cmd == 10:
                self.pixel = C.cast(p,C.POINTER(C.c_uint))[0]; return True
            if cmd == 15:
                v = C.cast(p,C.POINTER(Variable)).contents
                if v.key in opts: v.value=opts[v.key]; return True
                return False
            if cmd == 17: C.cast(p,C.POINTER(C.c_bool))[0]=False; return True
            if cmd == 3: C.cast(p,C.POINTER(C.c_bool))[0]=True; return True
            if cmd == 52: C.cast(p,C.POINTER(C.c_uint))[0]=0; return True
            return cmd in (16,18,35)
        def video(data,w,h,pitch):
            if not data or data == C.c_void_p(-1).value: return
            self.frame = (C.string_at(data,pitch*h),w,h,pitch,self.pixel)
        self.logger = C.CFUNCTYPE(None,C.c_int,C.c_char_p)(lambda *_:None)
        def audio_sample(left, right):
            if self.capture_audio: self.audio_chunks.append(struct.pack('<hh', left, right))
        def audio_batch(data, count):
            if self.capture_audio and data and count:
                self.audio_chunks.append(C.string_at(data, count * 4))
            return count
        signatures = [
            ('environment', C.CFUNCTYPE(C.c_bool,C.c_uint,C.c_void_p), environment),
            ('video_refresh', C.CFUNCTYPE(None,C.c_void_p,C.c_uint,C.c_uint,C.c_size_t),video),
            ('audio_sample', C.CFUNCTYPE(None,C.c_int16,C.c_int16),audio_sample),
            ('audio_sample_batch',C.CFUNCTYPE(C.c_size_t,C.c_void_p,C.c_size_t),audio_batch),
            ('input_poll',C.CFUNCTYPE(None),lambda:None),
            ('input_state',C.CFUNCTYPE(C.c_int16,C.c_uint,C.c_uint,C.c_uint,C.c_uint),
             lambda port,device,index,ident:int(device==1 and ident in self.buttons))]
        for name, signature, fn in signatures:
            callback=signature(fn); self.callbacks.append(callback)
            getattr(self.core,'retro_set_'+name)(callback)
        self.core.retro_init()
        self.core.retro_load_game.argtypes=[C.POINTER(Game)]
        self.core.retro_load_game.restype=C.c_bool
        self.rom=C.create_string_buffer(Path(rom_path).read_bytes())
        game=Game(str(rom_path).encode(),C.cast(self.rom,C.c_void_p),len(self.rom)-1,None)
        if not self.core.retro_load_game(C.byref(game)): raise RuntimeError('ROM rejected')
        info = AVInfo()
        self.core.retro_get_system_av_info.argtypes = [C.POINTER(AVInfo)]
        self.core.retro_get_system_av_info(C.byref(info))
        self.fps = info.timing.fps
        self.sample_rate = info.timing.sample_rate
        self.core.retro_get_memory_data.argtypes=[C.c_uint]
        self.core.retro_get_memory_data.restype=C.c_void_p
        self.core.retro_get_memory_size.argtypes=[C.c_uint]
        self.core.retro_get_memory_size.restype=C.c_size_t
    def run(self): self.core.retro_run()
    def drain_audio(self):
        data = b''.join(self.audio_chunks)
        self.audio_chunks.clear()
        return data
    def ram(self):
        ptr=self.core.retro_get_memory_data(2); size=self.core.retro_get_memory_size(2)
        return C.string_at(ptr,size) if ptr and size else b''
    def image(self):
        if self.frame is None: return None
        data,w,h,pitch,pixel=self.frame
        if pixel==1: return Image.frombytes('RGB',(w,h),data,'raw','BGRX',pitch)
        out=bytearray(w*h*3)
        for y in range(h):
            for x in range(w):
                v=struct.unpack_from('<H',data,y*pitch+x*2)[0]
                r,g,b=((v>>11)&31,(v>>5)&63,v&31) if pixel==2 else ((v>>10)&31,(v>>5)&31,v&31)
                i=(y*w+x)*3; out[i:i+3]=bytes((r*255//31,g*255//(63 if pixel==2 else 31),b*255//31))
        return Image.frombytes('RGB',(w,h),bytes(out))
    def close(self):
        self.core.retro_unload_game(); self.core.retro_deinit()


def field_metrics(ram, hint=None):
    """Validated HG FieldSystem/save-block pointers; unknown is never treated as zero."""
    def u32(p): return struct.unpack_from('<I',ram,p)[0]
    def ptr(p, n=4):
        value=u32(p)-0x02000000
        if not 0x100000 <= value <= len(ram)-n: raise ValueError('Invalid pointer')
        return value
    def inspect(fs):
        location=ptr(fs+0x20,20); avatar=ptr(fs+0x40,0x3C)
        map_id=u32(location)
        if not 0 < map_id < 600: return None
        player=ptr(avatar+0x30,0x70); xyz=struct.unpack_from('<3i',ram,player+0x64)
        if not all(0 <= x < 2000 for x in xyz): return None
        save=ptr(fs+12,0x2330C)
        def block(index,n):
            ident,_,off=struct.unpack_from('<3I',ram,save+0x23014+index*16)
            at=save+16+off
            if ident!=index or not 0<=at<=len(ram)-n: raise ValueError('Invalid save block')
            return at
        party=block(2,8); capacity,count=struct.unpack_from('<2I',ram,party)
        if capacity!=6 or not 1<=count<=6: return None
        dex=block(6,0x338)
        if u32(dex)!=0xBEEFCAFE: return None
        state=block(4,1100)
        parcel=struct.unpack_from('<H',ram,state+2*(0x416A-0x4000))[0]
        return dict(field_system=hex(fs+0x02000000),map_id=map_id,
                    player={'x':xyz[0],'y':xyz[2],'height':xyz[1]},party_count=count,
                    parcel_state=parcel,national_dex=bool(ram[dex+0x337]),
                    text_box='unavailable (no validated hook)',battle='unavailable (no validated hook)')
    if len(ram)<0x2330C: return None
    offsets=[hint] if hint is not None else range(0x100000,len(ram)-0x100,4)
    for fs in offsets:
        try:
            result=inspect(fs)
            if result: return result
        except (ValueError,struct.error,IndexError): pass
    return None
