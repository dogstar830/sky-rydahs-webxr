"""Blender 4.3 headless: build low-poly Sky Rydahs crew coins and export GLB + .blend.
blender -b -P build_coins.py -- [crew ...]"""
import bpy, bmesh, math, sys, os
D = os.path.dirname(os.path.abspath(__file__)); TX = os.path.join(D, 'textures')
CREWS = ['code-e', 'kogarasumaru', 'volt', 'rust-claw',   # 'team-storm' = alias (build explicitly)
         'anubis', 'static-angels', 'sleeping-forest', 'behemoth', 'genesis', 'tool-toul-to']
S = 128; RF = 0.0130; RR = 0.01325; T = 0.001; TB = 0.00085   # US dollar coin: 26.5 mm x 2.0 mm

def img(path, color):
    im = bpy.data.images.load(path, check_existing=True)
    im.colorspace_settings.name = 'sRGB' if color else 'Non-Color'
    return im

def material(name, prefix):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; P = nt.nodes['Principled BSDF']
    b = nt.nodes.new('ShaderNodeTexImage'); b.image = img(next(p for p in (f'{prefix}-basecolor.jpg', f'{prefix}-basecolor.png') if os.path.exists(p)), True)
    o = nt.nodes.new('ShaderNodeTexImage'); o.image = img(next(p for p in (f'{prefix}-orm.jpg', f'{prefix}-orm.png') if os.path.exists(p)), False)
    n = nt.nodes.new('ShaderNodeTexImage'); n.image = img(next(p for p in (f'{prefix}-normal.jpg', f'{prefix}-normal.png') if os.path.exists(p)), False)
    sep = nt.nodes.new('ShaderNodeSeparateColor'); nm = nt.nodes.new('ShaderNodeNormalMap')
    nt.links.new(b.outputs['Color'], P.inputs['Base Color'])
    nt.links.new(o.outputs['Color'], sep.inputs['Color'])
    nt.links.new(sep.outputs['Green'], P.inputs['Roughness']); nt.links.new(sep.outputs['Blue'], P.inputs['Metallic'])
    nt.links.new(n.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], P.inputs['Normal'])
    return m

def build(k):
    bm = bmesh.new(); uv = bm.loops.layers.uv.new('UVMap')
    ang = [2*math.pi*i/S for i in range(S)]
    def ring(r, z): return [bm.verts.new((r*math.cos(a), r*math.sin(a), z)) for a in ang]
    faces = []
    # front cap (mat 0) / back cap (mat 1): fans, planar UV
    for side, z, mi in ((1, T, 0), (-1, -T, 1)):
        c = bm.verts.new((0, 0, z)); rg = ring(RF, z)
        for i in range(S):
            a, b = rg[i], rg[(i+1) % S]
            f = bm.faces.new((c, a, b) if side > 0 else (c, b, a)); f.material_index = mi; f.smooth = False
            for l in f.loops:
                x, y, _ = l.vert.co
                l[uv].uv = (0.5+side*x/(2*RF), 0.5+y/(2*RF))
    # edge: bevel / reeded side / bevel (mat 2), smooth, cylindrical UV repeated 3x
    prof = [(RF, T, 1.0), (RR, TB, 0.88), (RR, -TB, 0.12), (RF, -T, 0.0)]
    rings = [[bm.verts.new((r*math.cos(a), r*math.sin(a), z)) for a in ang] + [None] for r, z, _ in prof]
    for j in range(3):
        for i in range(S):
            i2 = (i+1) % S
            vs = (rings[j][i], rings[j+1][i], rings[j+1][i2], rings[j][i2])
            f = bm.faces.new(vs); f.material_index = 2; f.smooth = True
            uvs = ((i/S*3, prof[j][2]), (i/S*3, prof[j+1][2]), ((i+1)/S*3, prof[j+1][2]), ((i+1)/S*3, prof[j][2]))
            for l, u in zip(f.loops, uvs): l[uv].uv = u
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(f'{k}-coin'); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(f'{k}-coin', me); bpy.context.scene.collection.objects.link(ob)
    for side in ('front', 'back', 'edge'):
        me.materials.append(material(f'{k}-{side}', os.path.join(TX, f'{k}-{side}')))
    return ob

if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    for k in (args or CREWS):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        ob = build(k)
        bpy.context.view_layer.objects.active = ob; ob.select_set(True)
        bpy.ops.export_scene.gltf(filepath=os.path.join(D, f'{k}-coin.glb'), export_format='GLB', use_selection=True,
                                  export_image_format='AUTO', export_apply=True)
        bpy.ops.file.pack_all()
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, 'blend', f'{k}-coin.blend'), compress=True)
        print('BUILT', k, len(ob.data.polygons), 'tris')
