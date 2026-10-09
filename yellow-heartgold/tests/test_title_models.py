"""Nitro serialization checks for node bounds, motion and DS geometry limits."""
import struct
import sys
import unittest
from pathlib import Path
import ndspy.model
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from title_models import psyduck,animation,water_model


def models(raw):
    block=struct.unpack_from('<I',raw,16)[0]
    mdl_offset=struct.unpack_from('<I',raw,block+28)[0]
    return raw[block+mdl_offset:]


def dictionary(data,at):
    count,size,entry=struct.unpack_from('<xBHxxH',data,at)
    return count,size,[struct.unpack_from('<I',data,at+entry+4+4*i)[0] for i in range(count)]


class TitleModelTests(unittest.TestCase):
    def test_psyduck_nodes_point_to_translated_identity_matrices(self):
        raw=psyduck();ndspy.model.NSBMD(raw);mdl=models(raw)
        count,size,offsets=dictionary(mdl,64)
        self.assertEqual(count,4)
        self.assertEqual(mdl[23],4)
        for off,position in zip(offsets,[(0,0,0),(-26,15,3),(26,15,3),(0,.6,0)]):
            self.assertEqual(off,size+offsets.index(off)*16)
            self.assertEqual(struct.unpack_from('<HH',mdl,64+off),(6,0))
            self.assertEqual(struct.unpack_from('<3i',mdl,64+off+4),tuple(round(v*4096) for v in position))

    def test_gpu_geometry_fits_native_ds_vertex_and_polygon_limits(self):
        mdl=models(psyduck());shape_at=struct.unpack_from('<I',mdl,12)[0]
        count,_,offsets=dictionary(mdl,shape_at);vertices=0
        for off in offsets:
            at=shape_at+off
            display_offset,size=struct.unpack_from('<II',mdl,at+8)
            commands=ndspy.model.NSBMD._parseDisplayList(mdl[at+display_offset:at+display_offset+size])
            vertices+=sum(command.type is ndspy.model._COMMANDS_BY_ID[0x23] for command in commands)
        self.assertEqual(count,4)
        self.assertLessEqual(vertices,6144)
        self.assertLessEqual(vertices//3,2048)

    def test_each_animation_joint_has_bounded_sample_arrays(self):
        raw=animation('Paddling',[(0,0,0),(-26,15,3),(26,15,3),(0,.6,0)])
        block=struct.unpack_from('<I',raw,16)[0];anm=raw[block+48:]
        self.assertEqual(anm[:4],b'J\0AC')
        frames,count=struct.unpack_from('<HH',anm,4)
        self.assertEqual((frames,count),(120,4))
        for i in range(count):
            off=struct.unpack_from('<H',anm,20+2*i)[0]
            self.assertEqual(anm[off+3],i)
            for axis in range(3):
                pointer=struct.unpack_from('<I',anm,off+8+axis*8)[0]
                self.assertLessEqual(pointer+frames*4,len(anm))
        root=struct.unpack_from('<H',anm,20)[0];wake=struct.unpack_from('<H',anm,26)[0]
        root_y=struct.unpack_from('<I',anm,root+16)[0];wake_y=struct.unpack_from('<I',anm,wake+16)[0]
        for frame in range(frames):
            y=struct.unpack_from('<i',anm,root_y+4*frame)[0]+struct.unpack_from('<i',anm,wake_y+4*frame)[0]
            self.assertLessEqual(abs(y-round(.6*4096)),1)

    def test_water_has_one_joint_and_a_palette_that_fits_texture_vram(self):
        image=Image.new('RGB',(256,256),(40,160,205)).quantize(colors=16)
        raw=water_model(image);model=ndspy.model.NSBMD(raw)
        self.assertEqual(models(raw)[23],1)
        self.assertEqual(len(model.textures),1)
        tex=model.textures[0][1]
        self.assertEqual((tex.width,tex.height),(256,256))
        self.assertEqual(len(tex.data1),32768)
        self.assertTrue(tex.repeatS and tex.repeatT)
