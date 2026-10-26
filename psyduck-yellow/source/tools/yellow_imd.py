"""Write a Yellow floor as a Nintendo .imd and convert it with the owner's g3dcvtr.exe (G3DCVTR.zip, Windows, run through WSL interop).

The .imd layout follows Pokemon DS Map Studio 2.2's own exports (map examples/Map_Platinum_Unfinished/*.imd): one texture (2 bits per pixel, 4 colours),
one palette, one material, one quad polygon, one node. Units: 1.0 = 64 world units (a 32-tile chunk is 8.0 wide, one tile is 0.25).
g3dcvtr.exe and its dll live in a Windows folder (WORK, default C:\\Users\\thata\\AppData\\Local\\Temp\\psyduck-tools\\work); they are the owner's tools and are not committed.
"""
import os
import subprocess
from pathlib import Path

WORK = Path(os.environ.get('PSYDUCK_G3D_WORK', '/mnt/c/Users/thata/AppData/Local/Temp/psyduck-tools/work'))
EXE = Path(os.environ.get('PSYDUCK_G3DCVTR', '/mnt/c/Users/thata/AppData/Local/Temp/psyduck-tools/G3DCVTR/g3dcvtr.exe'))


def words(data):
    return ' '.join('%04x' % (data[i] | data[i + 1] << 8) for i in range(0, len(data), 2))


def imd(name, pixels, size, palette, x0, z0, x1, z1, uv):
    """pixels: packed 2bpp bytes for a size x size texture; palette: 4 (r,g,b) 5-bit tuples; uv = (u1, v1) texel extent of the quad."""
    pal = ' '.join('%04x' % (r | g << 5 | b << 10) for r, g, b in palette)
    u1, v1 = uv
    quad = [(x0, z0, 0, 0), (x0, z1, 0, v1), (x1, z1, u1, v1), (x1, z0, u1, 0)]
    prims = ''.join(f'''
                        <tex st="{s:.6f} {t:.6f}"/>
                        <nrm xyz="0.000000 0.997000 0.000000"/>
                        <pos_xyz xyz="{x:.6f} 0.000000 {z:.6f}"/>''' for x, z, s, t in quad)
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<imd version="1.6.0">
    <head>
        <create date="2026-10-25T00:00:00" host="unknown" source="untitled" user="unknown"/>
        <title>Model Data for NINTENDO NITRO-System</title>
        <generator name="Psyduck Yellow yellow_imd.py" version="1.0"/>
    </head>
    <body>
        <original_create date="2026-10-25T00:00:00" host="unknown" source="untitled" user="unknown"/>
        <original_generator name="Psyduck Yellow yellow_imd.py" version="1.0"/>
        <model_info compress_material="on" compress_node="merge" force_full_weight="off" magnify="1" material_size="3 3" node_size="1 1" output_texture="used" pos_scale="6" scaling_rule="standard" tex_matrix_mode="maya" tool_start_frame="1" use_primitive_strip="on" vertex_style="direct"/>
        <box_test pos_scale="7" whd="{x1 - x0:.6f} 0.100000 {z1 - z0:.6f}" xyz="{x0:.6f} 0.000000 {z0:.6f}"/>
        <tex_image_array size="1">
            <tex_image color0_mode="color" format="palette4" height="{size}" index="0" name="{name}" original_height="{size}" original_width="{size}" palette_name="{name}" path="" width="{size}">
                <bitmap size="{len(pixels) // 2}"> {words(pixels)} </bitmap>
            </tex_image>
        </tex_image_array>
        <tex_palette_array size="1">
            <tex_palette color_size="4" index="0" name="{name}"> {pal} </tex_palette>
        </tex_palette_array>
        <material_array size="1">
            <material alpha="31" ambient="31 31 31" depth_test_decal="off" diffuse="31 31 31" emission="0 0 0" face="both" far_clipping="off" fog_flag="on" index="0" light0="on" light1="off" light2="off" light3="off" name="{name}" polygon_id="0" polygon_mode="modulate" render_1_pixel="off" shininess_table_flag="off" specular="0 0 0" tex_gen_mode="none" tex_image_idx="0" tex_palette_idx="0" tex_rotate="0.000000" tex_scale="1.000000 1.000000" tex_tiling="repeat repeat" tex_translate="0.000000 0.000000" translucent_update_depth="off" wire_mode="off"/>
        </material_array>
        <matrix_array size="1">
            <matrix index="0" mtx_weight="1" node_idx="0"/>
        </matrix_array>
        <polygon_array size="1">
            <polygon clr_flag="off" index="0" mtx_prim_size="1" name="polygon0" nrm_flag="on" polygon_size="1" quad_size="1" tex_flag="on" triangle_size="0" vertex_size="4" volume_max="3.000000 3.000000 3.000000" volume_min="-3.000000 -3.000000 -3.000000" volume_r="3.000000">
                <mtx_prim index="0">
                    <mtx_list size="1">0</mtx_list>
                    <primitive_array size="1">
                        <primitive index="0" type="quads" vertex_size="4">
                            <mtx idx="0"/>{prims}
                        </primitive>
                    </primitive_array>
                </mtx_prim>
            </polygon>
        </polygon_array>
        <node_array size="1">
            <node billboard="off" brother_next="-1" brother_prev="-1" child="-1" display_size="1" draw_mtx="on" index="0" kind="mesh" name="world_root" parent="-1" polygon_size="1" quad_size="1" rotate="0.000000 0.000000 0.000000" scale="1.000000 1.000000 1.000000" translate="0.000000 0.000000 0.000000" triangle_size="0" vertex_size="4" visibility="on" volume_max="0.000000 0.000000 0.000000" volume_min="0.000000 0.000000 0.000000" volume_r="0.000000">
                <display index="0" material="0" polygon="0" priority="0"/>
            </node>
        </node_array>
        <output_info polygon_size="1" quad_size="1" triangle_size="0" vertex_size="4"/>
    </body>
</imd>
'''


def convert(text, stem):
    """Run g3dcvtr.exe on the .imd text: returns (nsbmd bytes, nsbtx bytes). Files go to the Windows-side WORK folder."""
    WORK.mkdir(parents=True, exist_ok=True)
    src = WORK / f'{stem}.imd'
    src.write_text(text, encoding='utf-8')
    out = {}
    for flag, ext in (('-emdl', 'nsbmd'), ('-etex', 'nsbtx')):
        dst = WORK / f'{stem}.{ext}'
        dst.unlink(missing_ok=True)
        run = subprocess.run([str(EXE), f'{stem}.imd', flag, '-o', f'{stem}.{ext}'], cwd=WORK, capture_output=True, text=True, timeout=120)
        if not dst.exists():
            raise RuntimeError(f'g3dcvtr failed ({flag}): {run.stdout} {run.stderr}')
        out[ext] = dst.read_bytes()
    return out['nsbmd'], out['nsbtx']


def imd_multi(textures, mats, quads, x0, z0, x1, z1, top):
    """Several textures/materials. textures: [dict(name, w, h, pixels (4bpp bytes), palette [(r,g,b)] up to 16)];
    mats: [(material name, texture index, quads key)]; quads: {key: [4 x (x, y, z, s, t, nx, ny, nz)]} with s, t in whole-texture repeats."""
    tex_xml, pal_xml = [], []
    for i, t in enumerate(textures):
        fmt, size = ('palette4', 4) if t.get('fmt') == 2 else ('palette16', 16)
        colors = list(t['palette'])[:size] + [(0, 0, 0)] * (size - len(t['palette']))
        pal = ' '.join('%04x' % (r | g << 5 | b << 10) for r, g, b in colors)
        tex_xml.append(f'''            <tex_image color0_mode="color" format="{fmt}" height="{t['h']}" index="{i}" name="{t['name']}" original_height="{t['h']}" original_width="{t['w']}" palette_name="{t['name']}" path="" width="{t['w']}">
                <bitmap size="{len(t['pixels']) // 2}"> {words(t['pixels'])} </bitmap>
            </tex_image>''')
        pal_xml.append(f'            <tex_palette color_size="{size}" index="{i}" name="{t["name"]}"> {pal} </tex_palette>')
    mat_xml, poly_xml, disp_xml = [], [], []
    total_quads = total_verts = 0
    pi = 0
    for entry in mats:
        name, ti, key = entry[:3]
        diffuse, ambient = entry[3] if len(entry) > 3 else (31, 31)
        qs = quads.get(key) or []
        if not qs:
            continue
        t = textures[ti]
        prims = ''
        for q in qs:
            for (x, y, z, s, tt, nx, ny, nz) in q:
                prims += f'''
                            <tex st="{s * t['w']:.6f} {tt * t['h']:.6f}"/>
                            <nrm xyz="{nx * 0.997:.3f} {ny * 0.997:.3f} {nz * 0.997:.3f}"/>
                            <pos_xyz xyz="{x:.6f} {y:.6f} {z:.6f}"/>'''
        n = len(qs)
        mat_xml.append(f'''            <material alpha="31" ambient="{ambient} {ambient} {ambient}" depth_test_decal="off" diffuse="{diffuse} {diffuse} {diffuse}" emission="0 0 0" face="both" far_clipping="off" fog_flag="on" index="{pi}" light0="on" light1="off" light2="off" light3="off" name="{name}" polygon_id="0" polygon_mode="modulate" render_1_pixel="off" shininess_table_flag="off" specular="0 0 0" tex_gen_mode="none" tex_image_idx="{ti}" tex_palette_idx="{ti}" tex_rotate="0.000000" tex_scale="1.000000 1.000000" tex_tiling="repeat repeat" tex_translate="0.000000 0.000000" translucent_update_depth="off" wire_mode="off"/>''')
        poly_xml.append(f'''            <polygon clr_flag="off" index="{pi}" mtx_prim_size="1" name="polygon{pi}" nrm_flag="on" polygon_size="{n}" quad_size="{n}" tex_flag="on" triangle_size="0" vertex_size="{4 * n}" volume_max="4.000000 4.000000 4.000000" volume_min="-4.000000 -4.000000 -4.000000" volume_r="4.000000">
                <mtx_prim index="0">
                    <mtx_list size="1">0</mtx_list>
                    <primitive_array size="1">
                        <primitive index="0" type="quads" vertex_size="{4 * n}">
                            <mtx idx="0"/>{prims}
                        </primitive>
                    </primitive_array>
                </mtx_prim>
            </polygon>''')
        disp_xml.append(f'                <display index="{pi}" material="{pi}" polygon="{pi}" priority="0"/>')
        total_quads += n
        total_verts += 4 * n
        pi += 1
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<imd version="1.6.0">
    <head>
        <create date="2026-10-25T00:00:00" host="unknown" source="untitled" user="unknown"/>
        <title>Model Data for NINTENDO NITRO-System</title>
        <generator name="Psyduck Yellow yellow_imd.py" version="1.0"/>
    </head>
    <body>
        <original_create date="2026-10-25T00:00:00" host="unknown" source="untitled" user="unknown"/>
        <original_generator name="Psyduck Yellow yellow_imd.py" version="1.0"/>
        <model_info compress_material="on" compress_node="merge" force_full_weight="off" magnify="1" material_size="3 3" node_size="1 1" output_texture="used" pos_scale="6" scaling_rule="standard" tex_matrix_mode="maya" tool_start_frame="1" use_primitive_strip="on" vertex_style="direct"/>
        <box_test pos_scale="7" whd="{min(x1 - x0, 7.9):.6f} {top:.6f} {min(z1 - z0, 7.9):.6f}" xyz="{x0:.6f} 0.000000 {z0:.6f}"/>
        <tex_image_array size="{len(textures)}">
{chr(10).join(tex_xml)}
        </tex_image_array>
        <tex_palette_array size="{len(textures)}">
{chr(10).join(pal_xml)}
        </tex_palette_array>
        <material_array size="{pi}">
{chr(10).join(mat_xml)}
        </material_array>
        <matrix_array size="1">
            <matrix index="0" mtx_weight="1" node_idx="0"/>
        </matrix_array>
        <polygon_array size="{pi}">
{chr(10).join(poly_xml)}
        </polygon_array>
        <node_array size="1">
            <node billboard="off" brother_next="-1" brother_prev="-1" child="-1" display_size="{pi}" draw_mtx="on" index="0" kind="mesh" name="world_root" parent="-1" polygon_size="{total_quads}" quad_size="{total_quads}" rotate="0.000000 0.000000 0.000000" scale="1.000000 1.000000 1.000000" translate="0.000000 0.000000 0.000000" triangle_size="0" vertex_size="{total_verts}" visibility="on" volume_max="0.000000 0.000000 0.000000" volume_min="0.000000 0.000000 0.000000" volume_r="0.000000">
{chr(10).join(disp_xml)}
            </node>
        </node_array>
        <output_info polygon_size="{total_quads}" quad_size="{total_quads}" triangle_size="0" vertex_size="{total_verts}"/>
    </body>
</imd>
'''
