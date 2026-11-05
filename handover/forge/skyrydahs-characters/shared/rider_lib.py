"""Sky Rydah's shared rider build library (Blender 4.x, headless).

Per-crew config scripts (<crew>/src/build_rider.py) do:
    from rider_lib import *
    init(CFG)            # CFG = dict(name, out, prefix, ...)
    module('body'); ...crew geometry via finish()/cube()/ring()/skin_obj()/spike()/chain()...
    module('hair'); ...
    build_skates(); build_inventory()
    finalize()
Pipeline (finalize): bulk scale -> armature -> attachment/glow empties -> nearest-bone weights,
smoothed + limited to 4 influences -> merge per module (body/hair/top/skates/accessory/glow) ->
per-module tri budgets (auto-decimate) -> LOD1/LOD2 -> main GLB, first-person GLB, rig pose test.
Colour: one grey-banded atlas; each palette slot owns an atlas cell (u range), so the loader
recolours per slot from crewColors with a single material (slot = floor(u * NSLOTS)).
"""
import bpy, bmesh, math, random, json
from mathutils import Vector, Matrix

# palette slots -> atlas cells. Palette roles (Roblox-style recolour masks) map onto slots.
SLOTS = ['skin','hair','jacket','cloth','gold','metal','skate','eyes','iris','wheelGlow','glow2']
ROLES = {'primary':'jacket','secondary':'cloth','accent':'gold','trim':'skate','skin':'skin'}
GLOW = ('wheelGlow','glow2')
BUDGET = {'body':10000,'hair':2500,'top':3000,'skates':2000,'accessory':1000}
MODULES = ['body','hair','top','skates','accessory','glow']
NS = len(SLOTS)
scn = None; CFG = {}; PARTS = []; CUR = ['body', None]; MATS = {}; ATLAS = None; NRM = None

def init(cfg):
    global scn, CFG, PARTS, ATLAS
    CFG = dict(bulk=(1.0,1.0), preview={}, glowpts=[], lod=(8000,3000), total_max=19800)
    CFG.update(cfg); PARTS = []; CUR[0] = 'body'
    random.seed(CFG.get('seed',7))
    bpy.ops.wm.read_factory_settings(use_empty=True); scn = bpy.context.scene
    globals()['scn'] = scn; globals()['PARTS'] = PARTS
    if CFG.get('painted'): img = paint_atlas(CFG['prefix'])
    else:
      # grey-banded atlas: NS cells x 3 painted value bands (+ faint grain); 256x32
      W, H = 256, 32; img = bpy.data.images.new(CFG['prefix'] + "_atlas", W, H); px = [0.0]*(W*H*4)
      for y in range(H):
        v = y/(H-1); band = 0.80 if v < 0.33 else (0.92 if v < 0.7 else 1.0)
        for x in range(W):
            n = 1.0 + 0.03*math.sin(x*0.4 + y*0.9); k = (y*W + x)*4
            px[k] = px[k+1] = px[k+2] = max(0, min(1, band*n)); px[k+3] = 1
      img.pixels = px
    img.filepath_raw = CFG['out'] + "src/atlas.png"; img.file_format = 'PNG'; img.save(); img.pack()
    ATLAS = img; globals()['ATLAS'] = img
    for nm in SLOTS:  # build-time slot materials (preview colours); replaced at merge
        m = bpy.data.materials.new("slot_" + nm); m.use_nodes = True
        m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*CFG['preview'].get(nm, (0.6,0.6,0.6)), 1)
        MATS[nm] = m

def paint_atlas(prefix):
    """Hand-painted grey atlas, 512x128: one cell per slot. Values <=0.9 = albedo bands (recoloured by crewColors);
    values ~1.0 = painted highlight (hair angel-ring, iris catchlight, metal wear) picked up by the loader's HL term."""
    W, H = 512, 128; img = bpy.data.images.new(prefix + "_atlas", W, H); px = [0.0]*(W*H*4); rnd = random.Random(3)
    specks = {(rnd.randrange(W), rnd.randrange(H)) for _ in range(500)}
    def val(slot, u, v, x, y):
        n = 0.5*math.sin(u*37 + v*9) + 0.5*math.sin(u*11 - v*23 + 1.3)          # brush grain
        band = 0.74 if v < 0.33 else (0.83 if v < 0.7 else 0.9)
        if slot == 'skin': return 0.84 + 0.06*v
        if slot == 'hair':
            ring = 0.72 + 0.025*math.sin(u*9)                                    # zig-zag angel ring
            if abs(v - ring) < 0.035: return 1.0
            return 0.55 + 0.3*v + 0.02*n
        if slot == 'eyes': return 0.68 if v > 0.78 else 0.9                     # upper-lid shadow
        if slot == 'iris':
            du, dv = (u - 0.5), (v - 0.5); r = math.hypot(du, dv)*2
            if math.hypot(u - 0.36, v - 0.68) < 0.09: return 1.0                 # catchlight
            if math.hypot(u - 0.62, v - 0.36) < 0.045: return 1.0
            if r < 0.34: return 0.08                                             # pupil
            if r < 0.86: return 0.3 + 0.55*(1 - v) + 0.04*math.sin(math.atan2(dv, du)*14)   # iris: dark top -> bright bottom, radial striations
            return 0.18                                                          # limbal ring
        if slot in GLOW: return 1.0
        if slot == 'metal': return 1.0 if (x, y) in specks else band + 0.03*n
        seam = 0.62 if (abs(v - 0.33) < 0.012 or abs(v - 0.7) < 0.012) else 1.0  # painted seam lines at band edges
        stitch = 0.8 if (abs(v - 0.36) < 0.006 and (x//3) % 2 == 0) else 1.0      # stitch dashes
        return max(0.05, min(0.9, (band + 0.035*n)*seam*stitch))
    for y in range(H):
        v = (y + 0.5)/H
        for x in range(W):
            i = min(NS - 1, int(x*NS/W)); u = (x*NS/W) - i; k = (y*W + x)*4
            px[k] = px[k+1] = px[k+2] = val(SLOTS[i], u, v, x, y); px[k+3] = 1
    img.pixels = px; return img

def module(name, item=None):
    """Set the modular slot for following parts. Accessories carry an item name; budget = 1k tris per item."""
    assert name in MODULES; CUR[0] = name; CUR[1] = item or (name if name != 'accessory' else 'misc')

def finish(o, mat, bone=None, smooth=True, mod=None):
    o.data.materials.clear(); o.data.materials.append(MATS[mat])
    for p in o.data.polygons: p.use_smooth = smooth
    PARTS.append(dict(obj=o, slot=mat, bone=bone, mod=('glow' if mat in GLOW else (mod or CUR[0])), item=CUR[1]))
    return o

def apply_all(o):
    bpy.context.view_layer.objects.active = o
    for m in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=m.name)

def skin_obj(name, verts, edges, radii, subd=1):
    me = bpy.data.meshes.new(name); me.from_pydata(verts, edges, []); o = bpy.data.objects.new(name, me)
    scn.collection.objects.link(o); o.modifiers.new("skin", 'SKIN')
    for i, r in enumerate(radii):
        me.skin_vertices[0].data[i].radius = r if isinstance(r, tuple) else (r, r)
    me.skin_vertices[0].data[0].use_root = True
    if subd: s = o.modifiers.new("sub", 'SUBSURF'); s.levels = subd; s.render_levels = subd
    apply_all(o); return o

def mirror_pts(pts): return [(-x, y, z) for x, y, z in pts]

def cube(loc, sc, mat, bevel=0.01, bone=None, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot); o = bpy.context.object; o.scale = sc
    bpy.ops.object.transform_apply(scale=True)
    if bevel: m = o.modifiers.new("b", 'BEVEL'); m.width = bevel; m.segments = 2; apply_all(o)
    return finish(o, mat, bone, False)

def ring(name, loc, r, h, rot=(0,0,0), mat='gold', segs=16, sc=(1,1,1), bone=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=segs, radius=r, depth=h, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; o.scale = sc; bpy.ops.object.transform_apply(scale=True)
    return finish(o, mat, bone)

def tcube(loc, sc, mat, bone, taper=(1,1), sub=1, rot=(0,0,0), smooth=True):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot); o = bpy.context.object; o.scale = sc
    bpy.ops.object.transform_apply(scale=True, rotation=False)
    for vv in o.data.vertices:
        if vv.co.y < loc[1]:
            vv.co.x = loc[0] + (vv.co.x - loc[0])*taper[0]; vv.co.z = loc[2] + (vv.co.z - loc[2])*taper[1]
    if sub: m = o.modifiers.new("s", 'SUBSURF'); m.levels = sub; apply_all(o)
    return finish(o, mat, bone, smooth)

HEAD_CENTER = Vector((0, 0.015, 1.67))
def spike(dirv, length, rad, bend=0.0, center=None, mat='hair'):
    center = center or HEAD_CENTER; dirv = dirv.normalized(); base = center + dirv*0.085
    bpy.ops.mesh.primitive_cone_add(vertices=5, radius1=rad, radius2=0.0, depth=length, location=(0,0,0))
    o = bpy.context.object
    for vv in o.data.vertices:
        t = (vv.co.z + length/2)/length; vv.co.y += bend*t*t*length; vv.co.z += length/2
    o.matrix_world = Matrix.Translation(base) @ Vector((0,0,1)).rotation_difference(dirv).to_matrix().to_4x4()
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return finish(o, mat, 'head', True)

def chain(pts, n, r=0.011):
    for i in range(n):
        t = i/(n-1); k = t*(len(pts)-1); a = int(min(k, len(pts)-2)); f = k - a
        p = pts[a].lerp(pts[a+1], f); dv = (pts[a+1] - pts[a]).normalized()
        bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=0.0035, major_segments=6, minor_segments=3, location=p)
        o = bpy.context.object; o.rotation_euler = Vector((0,0,1)).rotation_difference(dv).to_euler()
        o.rotation_euler.rotate_axis('Z', math.radians(90*(i % 2))); o.rotation_euler.rotate_axis('X', math.radians(90))
        bpy.ops.object.transform_apply(location=True, rotation=True); finish(o, 'metal', mod='accessory'); PARTS[-1]['item'] = 'chains'

def bolt(pos, normal, size, flip=1, mat='gold'):
    pts2 = [(0,0.5),(0.18,0.5),(0.05,0.08),(0.22,0.08),(-0.12,-0.5),(-0.0,-0.05),(-0.18,-0.05)]
    me = bpy.data.meshes.new("bolt"); bm = bmesh.new(); vs = [bm.verts.new((x*size*flip, 0, y*size)) for x, y in pts2]
    bm.faces.new(vs); bmesh.ops.triangulate(bm, faces=bm.faces[:])
    r = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
    bmesh.ops.translate(bm, verts=[v for v in r['geom'] if isinstance(v, bmesh.types.BMVert)], vec=(0, 0.006, 0))
    bm.to_mesh(me); bm.free(); o = bpy.data.objects.new("bolt", me); scn.collection.objects.link(o)
    o.matrix_world = Matrix.Translation(pos) @ Vector((0,-1,0)).rotation_difference(Vector(normal).normalized()).to_matrix().to_4x4()
    bpy.context.view_layer.objects.active = o; o.select_set(True); bpy.ops.object.transform_apply(location=True, rotation=True); o.select_set(False)
    return finish(o, mat, None, False)

# ---------------- Air Treck skates (shared construction, see REFERENCES 1-2, AT-07 sheet) ----------------
def wheel(x, y, r, w, bn, hub=False):
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=r, depth=w, location=(x, y, r), rotation=(0, math.radians(90), 0))
    o = bpy.context.object; m = o.modifiers.new("b", 'BEVEL'); m.width = r*0.3; m.segments = 1; apply_all(o); finish(o, 'skate', bn)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=r*0.55, depth=w+0.004, location=(x, y, r), rotation=(0, math.radians(90), 0)); finish(bpy.context.object, 'metal', bn, False)
    if hub:
        for sd in (1, -1):
            bpy.ops.mesh.primitive_torus_add(major_radius=r*0.72, minor_radius=0.0045, major_segments=12, minor_segments=3, location=(x+sd*(w/2+0.001), y, r), rotation=(0, math.radians(90), 0))
            finish(bpy.context.object, 'wheelGlow', bn)

def build_skates():
    prev = CUR[0]; module('skates')
    for s in (1, -1):
        x = 0.11*s; bn = "foot." + ("L" if s > 0 else "R")
        if CFG.get('wheels4'):
            for wy in (-0.15, -0.05, 0.05, 0.15): wheel(x, wy, 0.036, 0.03, bn, True)
        else:
            wheel(x, -0.145, 0.038, 0.03, bn, True); wheel(x, 0.145, 0.038, 0.03, bn, True)
            wheel(x, -0.05, 0.026, 0.026, bn); wheel(x, 0.05, 0.026, 0.026, bn)
        for y0 in (-0.105, 0.105): cube((x, y0, 0.07), (0.056, 0.15, 0.05), 'skate', 0, bn)
        cube((x, 0, 0.082), (0.04, 0.06, 0.026), 'metal', 0, bn)
        cube((x+0.034*s, 0.0, 0.066), (0.012, 0.07, 0.03), 'metal', 0, bn)
        cube((x+0.041*s, 0.0, 0.066), (0.003, 0.05, 0.006), 'wheelGlow', 0, bn)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, -0.02, 0.108)); o = bpy.context.object; o.scale = (0.125, 0.37, 0.03); bpy.ops.object.transform_apply(scale=True)
        m = o.modifiers.new("b", 'BEVEL'); m.width = 0.012; m.segments = 1; apply_all(o); finish(o, 'metal', bn)
        cube((x, -0.02, 0.094), (0.127, 0.372, 0.004), 'gold', 0, bn)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, -0.035, 0.165)); b = bpy.context.object
        b.scale = (0.13, 0.36, 0.11); bpy.ops.object.transform_apply(scale=True)
        for vv in b.data.vertices:
            if vv.co.z > 0.19 and vv.co.y < -0.05: vv.co.y += 0.07; vv.co.z -= 0.025
        m = b.modifiers.new("s", 'SUBSURF'); m.levels = 1; apply_all(b); finish(b, 'skate', bn)
        bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.07, radius2=0.08, depth=0.2, location=(x, 0.0, 0.30)); c = bpy.context.object
        c.scale = (0.95, 1.12, 1); bpy.ops.object.transform_apply(scale=True); finish(c, 'cloth', bn)
        bpy.ops.mesh.primitive_torus_add(major_radius=0.078, minor_radius=0.014, major_segments=12, minor_segments=4, location=(x, 0.005, 0.405))
        o = bpy.context.object; o.scale = (0.95, 1.12, 1); bpy.ops.object.transform_apply(scale=True); finish(o, 'cloth', bn)
        bpy.ops.mesh.primitive_cone_add(vertices=14, radius1=0.08, radius2=0.092, depth=0.17, location=(x, 0.014, 0.325)); c = bpy.context.object
        c.scale = (0.98, 1.12, 1); c.rotation_euler = (math.radians(-7), 0, 0); bpy.ops.object.transform_apply(scale=True, rotation=True)
        bm = bmesh.new(); bm.from_mesh(c.data)
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.calc_center_median().y - 0.014 < -0.055 or abs(f.normal.z) > 0.9], context='FACES')
        bm.to_mesh(c.data); bm.free()
        m = c.modifiers.new("s", 'SOLIDIFY'); m.thickness = 0.012; apply_all(c); finish(c, 'skate', bn)
        for sd in (1, -1):
            cube((x+sd*0.06, 0.04, 0.175), (0.006, 0.13, 0.035), 'gold', 0, bn, (math.radians(8), 0, 0))
            cube((x+sd*0.093, 0.02, 0.32), (0.006, 0.07, 0.09), 'gold', 0, bn, (math.radians(-7), 0, 0))
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.016, depth=0.008, location=(x+sd*0.098, 0.015, 0.27), rotation=(0, math.radians(90), 0)); finish(bpy.context.object, 'metal', bn, False)
        cube((x, -0.06, 0.235), (0.135, 0.035, 0.016), 'skate', 0, bn, (math.radians(-35), 0, 0))
        cube((x+0.06*s, -0.065, 0.23), (0.02, 0.03, 0.025), 'gold', 0, bn)
        cube((x, -0.03, 0.395), (0.18, 0.05, 0.016), 'gold', 0, bn, (math.radians(-20), 0, 0))
        cube((x, 0.105, 0.30), (0.06, 0.03, 0.13), 'metal', 0, bn)
        cube((x, 0.121, 0.30), (0.008, 0.004, 0.1), 'wheelGlow', 0, bn)
        for sd in (1, -1): cube((x+sd*0.056, -0.03, 0.14), (0.004, 0.16, 0.008), 'wheelGlow', 0, bn)
    CUR[0] = prev

# ---------------- body-as-inventory (REFERENCES 10): spray cans on hips, wrist radio, glove display ----------------
def spray_can(pos, bone, mod='accessory'):
    x, y, z = pos
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.026, depth=0.11, location=(x, y, z)); finish(bpy.context.object, 'gold', bone, True, mod)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.02, depth=0.025, location=(x, y, z+0.065)); finish(bpy.context.object, 'metal', bone, True, mod)
    cube((x, y-0.018, z+0.08), (0.008, 0.012, 0.008), 'skate', 0, bone); PARTS[-1]['mod'] = mod
    ring("holster", (x, y, z-0.01), 0.03, 0.02, mat='skate', segs=8, bone=bone); PARTS[-1]['mod'] = mod

def wrist_radio(pos, bone, rot=(0,0,0), mod='accessory'):
    cube(pos, (0.045, 0.03, 0.03), 'metal', 0, bone, rot); PARTS[-1]['mod'] = mod
    cube((pos[0], pos[1]-0.016, pos[2]+0.005), (0.012, 0.004, 0.008), 'wheelGlow', 0, bone, rot)
    cube((pos[0], pos[1]+0.005, pos[2]+0.03), (0.006, 0.006, 0.04), 'skate', 0, bone, rot); PARTS[-1]['mod'] = mod

def glove_display(pos, bone, rot=(0,0,0), mod='accessory'):
    cube(pos, (0.05, 0.012, 0.035), 'skate', 0, bone, rot); PARTS[-1]['mod'] = mod
    cube((pos[0], pos[1]-0.007, pos[2]), (0.04, 0.004, 0.026), 'glow2', 0, bone, rot)

def build_inventory():
    module('accessory', 'spraycans')
    for s in (1, -1):
        spray_can((0.19*s, 0.02, 0.9), 'hips')
    module('accessory', 'radio')
    wrist_radio((-0.56, -0.02, 1.06), 'forearm.R', (0, math.radians(45), 0))
    module('accessory', 'display')
    glove_display((0.55, -0.045, 1.07), 'forearm.L', (0, math.radians(-45), 0))

# ---------------- rig ----------------
def base_bones():
    B = [("hips",(0,0,0.95),(0,0,1.10),None),("spine",(0,0,1.10),(0,0,1.32),"hips"),("chest",(0,0,1.32),(0,0,1.47),"spine"),
         ("neck",(0,0.01,1.47),(0,0.01,1.57),"chest"),("head",(0,0.01,1.57),(0,0.01,1.80),"neck")]
    for s, L in ((1,"L"), (-1,"R")):
        B += [("shoulder."+L,(0.05*s,0,1.43),(0.19*s,0,1.42),"chest"),("upperarm."+L,(0.19*s,0,1.42),(0.40*s,0,1.20),"shoulder."+L),
              ("forearm."+L,(0.40*s,0,1.20),(0.59*s,0,1.03),"upperarm."+L),("hand."+L,(0.59*s,0,1.03),(0.71*s,0,0.91),"forearm."+L),
              ("thigh."+L,(0.10*s,0,0.97),(0.12*s,-0.02,0.58),"hips"),("shin."+L,(0.12*s,-0.02,0.58),(0.11*s,0,0.24),"thigh."+L),
              ("foot."+L,(0.11*s,0,0.24),(0.11*s,-0.17,0.12),"shin."+L)]
    return B

ATTS = [("Hat","head",(0,0.01,1.83)),("Hair","head",(0,0.03,1.75)),("Face","head",(0,-0.11,1.65)),("Neck","neck",(0,0.01,1.52)),
        ("Collar","chest",(0,0.0,1.47)),("ShoulderL","upperarm.L",(0.21,0,1.45)),("ShoulderR","upperarm.R",(-0.21,0,1.45)),
        ("BodyFront","chest",(0,-0.13,1.32)),("BodyBack","chest",(0,0.13,1.32)),("Waist","hips",(0,0,0.98)),
        ("GripL","hand.L",(0.66,-0.02,0.96)),("GripR","hand.R",(-0.66,-0.02,0.96)),("FootL","foot.L",(0.11,-0.03,0.06)),("FootR","foot.R",(-0.11,-0.03,0.06))]

def make_armature(name, bones):
    ad = bpy.data.armatures.new(name); arm = bpy.data.objects.new(name, ad); scn.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode='EDIT')
    for n, h, t, p in bones:
        b = ad.edit_bones.new(n); b.head = h; b.tail = t
        if p: b.parent = ad.edit_bones[p]; b.use_connect = False
    bpy.ops.object.mode_set(mode='OBJECT'); return arm

def empty_on_bone(name, arm, bone, pos, size=0.03):
    e = bpy.data.objects.new(name, None); e.empty_display_size = size; scn.collection.objects.link(e)
    e.parent = arm; e.parent_type = 'BONE'; e.parent_bone = bone
    bpy.context.view_layer.update(); e.matrix_world = Matrix.Translation(pos); return e

def segdist(p, a, b):
    ab = b - a; t = max(0, min(1, (p - a).dot(ab)/ab.length_squared)); return (a + ab*t - p).length

def weight_part(o, bone, segs, blend=0.07):
    o.vertex_groups.clear(); vgs = {n: o.vertex_groups.new(name=n) for n, _, _ in segs}
    for v in o.data.vertices:
        if bone: vgs[bone].add([v.index], 1.0, 'REPLACE'); continue
        p = o.matrix_world @ v.co
        ds = sorted((segdist(p, a, b), n) for n, a, b in segs)
        (d0, n0), (d1, n1) = ds[0], ds[1]
        if d1 - d0 < blend:
            w = 0.5 + 0.5*(d1 - d0)/blend
            vgs[n0].add([v.index], w, 'REPLACE'); vgs[n1].add([v.index], 1 - w, 'REPLACE')
        else: vgs[n0].add([v.index], 1.0, 'REPLACE')

def uv_part(o, slot, mode=None):
    """UV into the slot's atlas cell; v spans the painted value bands by height + normal.
    mode='planar': local x/z bbox -> full cell (iris, eye whites); mode='hair': v = world height on the head (angel ring)."""
    i = SLOTS.index(slot); u0 = (i + 0.2)/NS; u1 = (i + 0.8)/NS
    if mode:
        while o.data.uv_layers: o.data.uv_layers.remove(o.data.uv_layers[0])
        uv = o.data.uv_layers.new(name="UVMap"); mw = o.matrix_world
        xs = [v.co.x for v in o.data.vertices]; zs = [v.co.z for v in o.data.vertices]
        for l in o.data.loops:
            vt = o.data.vertices[l.vertex_index]
            if mode == 'planar':
                a = (vt.co.x - min(xs))/max(1e-6, max(xs) - min(xs)); b = (vt.co.z - min(zs))/max(1e-6, max(zs) - min(zs))
                uv.data[l.index].uv = ((i + 0.02 + 0.96*a)/NS, 0.02 + 0.96*b)
            else:
                w = mw @ vt.co; b = max(0.02, min(0.98, (w.z - 1.50)/0.36))
                uv.data[l.index].uv = (u0 + (u1 - u0)*(0.5 + 0.5*vt.normal.x), b)
        return
    zs = [v.co.z for v in o.data.vertices] or [0]; zmin, zmax = min(zs), max(zs)
    while o.data.uv_layers: o.data.uv_layers.remove(o.data.uv_layers[0])
    uv = o.data.uv_layers.new(name="UVMap")
    for l in o.data.loops:
        vtx = o.data.vertices[l.vertex_index]; hv = (vtx.co.z - zmin)/max(1e-5, zmax - zmin)
        vv = 0.1 + 0.8*max(0, min(1, 0.5*hv + 0.5*(0.5 + 0.5*vtx.normal.z)))
        uv.data[l.index].uv = (u0 + (u1 - u0)*(0.5 + 0.5*vtx.normal.x), vv)

def final_materials():
    out = {}
    for nm in ('riderToon', 'riderGlow'):
        m = bpy.data.materials.new(nm); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
        t = nt.nodes.new("ShaderNodeTexImage"); t.image = ATLAS; t.interpolation = 'Closest'
        nt.links.new(t.outputs[0], b.inputs["Base Color"])
        if nm == 'riderToon' and NRM is not None:
            uvn = nt.nodes.new("ShaderNodeUVMap"); uvn.uv_map = "nrm"; tn = nt.nodes.new("ShaderNodeTexImage"); tn.image = NRM
            NRM.colorspace_settings.name = 'Non-Color'; nm_ = nt.nodes.new("ShaderNodeNormalMap"); nm_.uv_map = "nrm"
            nt.links.new(uvn.outputs[0], tn.inputs[0]); nt.links.new(tn.outputs[0], nm_.inputs["Color"]); nt.links.new(nm_.outputs[0], b.inputs["Normal"])
        if nm == 'riderGlow': b.inputs["Emission Strength"].default_value = 2; nt.links.new(t.outputs[0], b.inputs["Emission Color"])
        out[nm] = m
    return out

def bake_normals(lod0, size=512):
    """High-poly (simple-subdiv x2 + fold/wear displacement on cloth slots) -> tangent normal map on a unique 2nd UV ('nrm')."""
    global NRM
    objs = [o for m, o in lod0.items() if m != 'glow']
    for o in objs:
        o.data.uv_layers.new(name="nrm"); o.data.uv_layers.active = o.data.uv_layers["nrm"]
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.004); bpy.ops.object.mode_set(mode='OBJECT')
    img = bpy.data.images.new(CFG['prefix'] + "_nrm", size, size); img.generated_color = (0.5, 0.5, 1.0, 1.0)
    img.colorspace_settings.name = 'Non-Color'; NRM = img; globals()['NRM'] = img
    for m in MATS.values():
        t = m.node_tree.nodes.new("ShaderNodeTexImage"); t.image = img; m.node_tree.nodes.active = t
    folds = bpy.data.textures.new("folds", 'MARBLE'); folds.marble_type = 'SHARPER'; folds.noise_scale = 0.05; folds.turbulence = 5; folds.noise_depth = 2
    wear = bpy.data.textures.new("wear", 'CLOUDS'); wear.noise_scale = 0.008
    cloth_cells = {SLOTS.index(k) for k in ('jacket', 'cloth', 'skate', 'gold')}
    s = bpy.context.scene; s.render.engine = 'CYCLES'; s.cycles.samples = 1; s.cycles.device = 'CPU'
    s.render.bake.use_selected_to_active = True; s.render.bake.cage_extrusion = 0.006; s.render.bake.max_ray_distance = 0.02
    s.render.bake.margin = 3; s.render.bake.use_clear = False
    for o in objs:
        h = dup(o, o.name + "_HI"); h.shape_key_clear() if h.data.shape_keys else None
        vg = h.vertex_groups.new(name="fold"); uvl = h.data.uv_layers["UVMap"].data; wts = {}
        for l in h.data.loops: wts[l.vertex_index] = 1.0 if int(uvl[l.index].uv.x*NS) in cloth_cells else 0.0
        for vi, w in wts.items(): vg.add([vi], w, 'REPLACE')
        m = h.modifiers.new("sub", 'SUBSURF'); m.subdivision_type = 'SIMPLE'; m.levels = 2
        d = h.modifiers.new("folds", 'DISPLACE'); d.texture = folds; d.texture_coords = 'GLOBAL'; d.strength = 0.005; d.vertex_group = "fold"
        d2 = h.modifiers.new("wear", 'DISPLACE'); d2.texture = wear; d2.texture_coords = 'GLOBAL'; d2.strength = 0.0012
        apply_all(h)
        bpy.ops.object.select_all(action='DESELECT'); h.select_set(True); o.select_set(True); bpy.context.view_layer.objects.active = o
        bpy.ops.object.bake(type='NORMAL', normal_space='TANGENT', use_selected_to_active=True, cage_extrusion=0.006, max_ray_distance=0.02, margin=3, use_clear=False)
        bpy.data.objects.remove(h, do_unlink=True)
    for o in objs:
        o.data.uv_layers.active = o.data.uv_layers["UVMap"]; o.data.uv_layers["UVMap"].active_render = True
    img.filepath_raw = CFG['out'] + "src/normal_bake.png"; img.file_format = 'PNG'; img.save(); img.pack()

def tris(o):
    o.data.calc_loop_triangles(); return len(o.data.loop_triangles)

def decimate(o, ratio):
    if ratio >= 0.999: return
    m = o.modifiers.new("dec", 'DECIMATE'); m.ratio = max(0.02, ratio); m.use_collapse_triangulate = True
    bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier="dec")

def join(objs, name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.join(); o = bpy.context.object; o.name = name; o.data.name = name
    return o

def clean_weights(o, smooth=True):
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
    if smooth:
        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
        bpy.ops.object.vertex_group_smooth(group_select_mode='ALL', factor=0.5, repeat=3)
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL', limit=4)
    bpy.ops.object.vertex_group_normalize_all(group_select_mode='ALL', lock_active=False)

def dup(o, name):
    n = o.copy(); n.data = o.data.copy(); n.name = name; n.data.name = name; scn.collection.objects.link(n); return n

def bind(o, arm, mat):
    o.data.materials.clear(); o.data.materials.append(mat)
    for m in list(o.modifiers): o.modifiers.remove(m)
    m = o.modifiers.new("arm", 'ARMATURE'); m.object = arm; o.parent = arm; o.matrix_parent_inverse = arm.matrix_world.inverted()

# ---------------- first-person rig: gloves/forearms + skates + inventory, no body ----------------
def build_fp(main_skates):
    P = CFG['prefix']; segs = []
    # eye at ~(0,1.62,0): short forearms ending ~0.45 m out, gloves ~1.4x so hands read at natural size
    G = 1.4; Y0, Y1, Y2 = -0.16, -0.34, -0.50; Z = 1.12
    bones = [("hips",(0,0,0.90),(0,0,1.05),None)]
    for s, L in ((1,"L"), (-1,"R")):
        bones += [("forearm."+L,(0.19*s,Y0,Z),(0.19*s,Y1,Z-0.02),"hips"),("hand."+L,(0.19*s,Y1,Z-0.02),(0.19*s,Y2,Z-0.04),"forearm."+L),
                  ("foot."+L,(0.11*s,0,0.24),(0.11*s,-0.17,0.12),"hips")]
    arm = make_armature(P + "_FP_Rig", bones); start = len(PARTS)
    for s, L in ((1,"L"), (-1,"R")):
        x = 0.19*s; z = Z - 0.02
        bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.05, radius2=0.044, depth=0.2, location=(x, (Y0+Y1)/2, Z-0.01), rotation=(math.radians(90), 0, 0))
        finish(bpy.context.object, 'jacket', 'forearm.'+L, True, 'fp')
        ring("cuff", (x, Y1+0.02, z), 0.05*1.1, 0.035, rot=(math.radians(90), 0, 0), mat='gold', segs=12, bone='forearm.'+L); PARTS[-1]['mod'] = 'fp'
        h = skin_obj("glove", [(x, Y1, z), (x, Y1-0.06*G, z-0.005), (x, Y1-0.11*G, z-0.015)], [(0,1),(1,2)], [(0.035*G,0.025*G),(0.044*G,0.024*G),(0.04*G,0.022*G)])
        finish(h, 'skate', 'hand.'+L, True, 'fp')
        for k in range(4):
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.009*G, depth=0.03*G, location=(x - (0.024*s - 0.016*k*s)*G, Y1-0.13*G, z-0.025), rotation=(math.radians(90), 0, 0))
            finish(bpy.context.object, 'skin', 'hand.'+L, True, 'fp')
        th = skin_obj("thumb", [(x - 0.04*s*G, Y1-0.04*G, z-0.01), (x - 0.05*s*G, Y1-0.09*G, z-0.015)], [(0,1)], [0.013*G, 0.011*G]); finish(th, 'skin', 'hand.'+L, True, 'fp')
        cube((x, Y1-0.07*G, z+0.03*G), (0.05*G, 0.03*G, 0.012*G), 'metal', 0, 'hand.'+L); PARTS[-1]['mod'] = 'fp'
    glove_display((0.19, (Y0+Y1)/2, Z+0.055), 'forearm.L', (0, 0, 0), 'fp')
    for p in PARTS[-2:]: p['mod'] = 'fp'
    wrist_radio((-0.19, (Y0+Y1)/2, Z+0.055), 'forearm.R', (0, 0, 0), 'fp')
    for p in PARTS[-3:]: p['mod'] = 'fp'
    for s in (1, -1): spray_can((0.2*s, 0.03, 0.9), 'hips', 'fp')
    for p in PARTS[start:]:
        if p['slot'] in GLOW: p['mod'] = 'fpglow'
    segs = [(n, Vector(h), Vector(t)) for n, h, t, p in bones]
    body, glow = [], []
    for p in PARTS[start:]:
        weight_part(p['obj'], p['bone'], segs); uv_part(p['obj'], p['slot'])
        (glow if p['mod'] == 'fpglow' else body).append(p['obj'])
    sk = dup(main_skates, P + "_FP_skates_tmp")
    mats = bpy.data.materials
    fb = join(body + [sk], P + "_FP_body"); bind(fb, arm, mats['riderToon'])
    out = [fb]
    if glow: fg = join(glow, P + "_FP_glow"); bind(fg, arm, mats['riderGlow']); out.append(fg)
    for nm, bn, pos in (("GripL","hand.L",(0.19,Y1-0.1*G,Z-0.03)),("GripR","hand.R",(-0.19,Y1-0.1*G,Z-0.03)),("Waist","hips",(0,0,0.95))):
        empty_on_bone(nm + "_Att", arm, bn, Vector(pos))
    return arm, out

def export(path, objs):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True, export_skins=True, export_apply=False,
                              export_yup=True, export_extras=True, export_animations=False)

def pose_test(arm, objs, path):
    """Bend knees + elbows 60deg, render workbench front/side to check pinching."""
    for o in bpy.data.objects:
        if o.type == 'MESH': o.hide_render = o not in objs
    bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode='POSE')
    for n, ax in (("shin.L",'X'),("shin.R",'X'),("forearm.L",'Z'),("forearm.R",'Z'),("thigh.L",'X'),("thigh.R",'X')):
        pb = arm.pose.bones[n]; pb.rotation_mode = 'XYZ'
        ang = {'shin':60, 'forearm':60, 'thigh':-30}[n.split('.')[0]]
        if n.startswith('forearm'): ang *= (1 if n.endswith('L') else -1)
        setattr(pb.rotation_euler, ax.lower(), math.radians(ang))
    bpy.ops.object.mode_set(mode='OBJECT')
    r = scn.render; r.engine = 'BLENDER_WORKBENCH'; r.resolution_x = 900; r.resolution_y = 700; r.film_transparent = False
    scn.display.shading.light = 'STUDIO'; scn.display.shading.color_type = 'TEXTURE'; scn.display.shading.show_cavity = True
    world = bpy.data.worlds.new("w"); scn.world = world
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); scn.collection.objects.link(cam); scn.camera = cam
    cam.data.lens = 50
    for tag, loc in (("front", (1.6, -3.2, 1.1)), ("side", (3.6, 0.0, 1.0))):
        cam.location = loc; d = Vector((0, 0, 0.9)) - cam.location; cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
        r.filepath = path.replace(".png", "_" + tag + ".png"); bpy.ops.render.render(write_still=True)
    bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode='POSE')
    for pb in arm.pose.bones: pb.rotation_euler = (0, 0, 0)
    bpy.ops.object.mode_set(mode='OBJECT')

def finalize():
    P = CFG['prefix']; OUT = CFG['out']; SX, SY = CFG['bulk']
    # 1. bulk silhouette scale (everything below the head)
    if (SX, SY) != (1.0, 1.0):
        for p in PARTS:
            if p['bone'] == 'head': continue
            o = p['obj']; mw = o.matrix_world; inv = mw.inverted()
            for v in o.data.vertices:
                w = mw @ v.co; w.x *= SX; w.y *= SY; v.co = inv @ w
    bones = [(n, (h[0]*SX, h[1]*SY, h[2]), (t[0]*SX, t[1]*SY, t[2]), p) if n not in ('head', 'neck') else (n, h, t, p) for n, h, t, p in base_bones()]
    arm = make_armature(P + "_Rig", bones); arm["slots"] = ",".join(SLOTS); arm["roles"] = json.dumps(ROLES)
    sc = lambda q: Vector((q[0]*SX, q[1]*SY, q[2]))
    empties = [empty_on_bone(n + "_Att", arm, b, sc(pos) if b not in ('head', 'neck') else Vector(pos)) for n, b, pos in ATTS]
    gp = [("GlowPt_wheel_%s%d" % (L, k), "foot." + L, (0.11*s + 0.02*s, y, 0.038), 0.12) for s, L in ((1, "L"), (-1, "R")) for k, y in enumerate((-0.145, 0.145))]
    gp += CFG['glowpts']
    for n, b, pos, size in gp:
        e = empty_on_bone(n, arm, b, sc(pos) if b not in ('head', 'neck') else Vector(pos)); e["glowSize"] = size; empties.append(e)
    # 2. weights + atlas-cell UVs per part
    segs = [(n, Vector(h), Vector(t)) for n, h, t, p in bones]
    for p in PARTS:
        weight_part(p['obj'], p['bone'], segs); uv_part(p['obj'], p['slot'], p.get('uv'))
    mats = None
    # 3. merge per module, enforce slot budgets
    lod0 = {}; report = {}
    for mod in MODULES:
        objs = sorted([p['obj'] for p in PARTS if p['mod'] == mod], key=lambda o: o.data.shape_keys is None)
        if not objs: continue
        o = join(objs, "%s_LOD0_%s" % (P, mod))
        clean_weights(o, smooth=mod in ('body', 'top'))
        t0 = tris(o)
        bud = BUDGET.get(mod)
        if mod == 'accessory': bud = 1000*len({p['item'] for p in PARTS if p['mod'] == 'accessory'})
        if bud and t0 > bud: decimate(o, bud/t0*0.98)
        o["budget"] = bud or 0
        o["module"] = mod; lod0[mod] = o; report[mod] = (t0, tris(o), bud)
    total = sum(tris(o) for o in lod0.values())
    if total > CFG['total_max']:
        for mod in ('body', 'top'):
            if mod in lod0: decimate(lod0[mod], 1 - (total - CFG['total_max'])/max(1, tris(lod0[mod])*2)); 
        total = sum(tris(o) for o in lod0.values())
    if CFG.get('bake'): bake_normals(lod0)
    mats = final_materials()
    # 4. LODs
    lods = {0: lod0}
    for li, target in ((1, CFG['lod'][0]), (2, CFG['lod'][1])):
        lods[li] = {}
        for mod, o in lod0.items():
            if li == 2 and mod == 'accessory' and not CFG.get('lod2_accessory'): continue   # drop small inventory bits far away
            d = dup(o, "%s_LOD%d_%s" % (P, li, mod)); d.shape_key_clear() if d.data.shape_keys else None; decimate(d, target/total); clean_weights(d, False); d["module"] = mod; lods[li][mod] = d
    for li, dd in lods.items():
        for mod, o in dd.items(): bind(o, arm, mats['riderGlow' if mod == 'glow' else 'riderToon'])
    stats = {li: sum(tris(o) for o in dd.values()) for li, dd in lods.items()}
    # 5. first-person rig (built from LOD0 skates)
    fp_arm, fp_objs = build_fp(lod0['skates'])
    fp_tris = sum(tris(o) for o in fp_objs)
    # 6. export
    main = [arm] + empties + [o for dd in lods.values() for o in dd.values()]
    bpy.ops.wm.save_as_mainfile(filepath=OUT + "src/" + CFG['name'] + "-rider.blend")
    export(OUT + CFG['name'] + "-rider.glb", main)
    export(OUT + CFG['name'] + "-fp.glb", [fp_arm] + fp_objs + [c for c in bpy.data.objects if c.parent == fp_arm and c.type == 'EMPTY'])
    for o in fp_objs: o.hide_render = True
    # 7. rig sanity pose test (LOD0)
    pose_test(arm, list(lod0.values()), OUT + "renders/rigtest.png")
    items = sorted({p['item'] for p in PARTS if p['mod'] == 'accessory'})
    rep = dict(name=CFG['name'], lod_tris=stats, modules={k: {'raw': a, 'final': b, 'budget': c} for k, (a, b, c) in report.items()}, accessory_items=items, fp_tris=fp_tris)
    json.dump(rep, open(OUT + "src/build_report.json", "w"), indent=1); print("REPORT", json.dumps(rep))
