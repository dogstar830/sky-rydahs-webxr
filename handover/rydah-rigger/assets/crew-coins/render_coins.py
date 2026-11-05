"""Blender 4.3 headless renders for Sky Rydahs crew coins (imports the exported GLBs).
blender -b -P render_coins.py -- contact|turntable|hand|test"""
import bpy, math, os, sys
from mathutils import Vector, Euler
D = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(D, 'renders')
CREWS = ['code-e', 'kogarasumaru', 'volt', 'rust-claw',   # VOLT in the storm slot; team-storm-coin.glb = alias
         'anubis', 'static-angels', 'sleeping-forest', 'behemoth', 'genesis', 'tool-toul-to']
mode = sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'test'

def scene_base(res=(1600, 900), samples=96):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
    sc.cycles.samples = samples; sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.film_transparent = False
    sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Punchy'
    w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (0.012, 0.012, 0.02, 1); bg.inputs[1].default_value = 1
    # floor
    bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, -0.0011))
    fl = bpy.context.object; m = bpy.data.materials.new('floor'); m.use_nodes = True
    P = m.node_tree.nodes['Principled BSDF']; P.inputs['Base Color'].default_value = (0.004, 0.004, 0.006, 1); P.inputs['Roughness'].default_value = 0.6
    fl.data.materials.append(m)
    return sc

def neutral_world(cam_dark=(0.018, 0.018, 0.022), cam_top=(0.06, 0.06, 0.07)):
    """Seamless studio: camera rays see a plain dark gradient; reflections see a soft neutral
    studio dome (bright top, mid-grey horizon) so metal stays bright even edge-on."""
    sc = bpy.context.scene
    for o in [o for o in sc.objects if o.type == 'MESH' and o.name.startswith('Plane')]: bpy.data.objects.remove(o)
    w = sc.world; nt = w.node_tree; nt.nodes.clear()
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['Generated'], sep.inputs[0])
    def ramp(stops):
        r = nt.nodes.new('ShaderNodeValToRGB'); r.color_ramp.elements[0].position, r.color_ramp.elements[0].color = stops[0]
        r.color_ramp.elements[1].position, r.color_ramp.elements[1].color = stops[-1]
        for p, c in stops[1:-1]: e = r.color_ramp.elements.new(p); e.color = c
        mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = -1; mr.inputs['From Max'].default_value = 1
        nt.links.new(sep.outputs['Z'], mr.inputs['Value']); nt.links.new(mr.outputs['Result'], r.inputs['Fac']); return r
    camr = ramp([(0.0, (*cam_dark, 1)), (1.0, (*cam_top, 1))])
    envr = ramp([(0.0, (0.05, 0.05, 0.05, 1)), (0.45, (0.22, 0.22, 0.23, 1)), (0.6, (0.55, 0.55, 0.56, 1)), (1.0, (0.95, 0.95, 0.96, 1))])
    b1 = nt.nodes.new('ShaderNodeBackground'); b2 = nt.nodes.new('ShaderNodeBackground'); b2.inputs[1].default_value = 1.0
    nt.links.new(camr.outputs[0], b1.inputs[0]); nt.links.new(envr.outputs[0], b2.inputs[0])
    lp = nt.nodes.new('ShaderNodeLightPath'); mx = nt.nodes.new('ShaderNodeMixShader'); out = nt.nodes.new('ShaderNodeOutputWorld')
    nt.links.new(lp.outputs['Is Camera Ray'], mx.inputs[0]); nt.links.new(b2.outputs[0], mx.inputs[1]); nt.links.new(b1.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs[0])

def neutral_lights(target=(0, 0, 0), s=1.0):
    t = Vector(target)
    softbox(t+Vector((-0.10, -0.14, 0.16))*s, 0.16*s, 5.0, (1, 0.98, 0.95), target)   # key
    softbox(t+Vector((0.16, -0.10, 0.06))*s, 0.14*s, 2.5, (0.95, 0.97, 1.0), target)  # fill
    softbox(t+Vector((0.0, 0.16, 0.12))*s, 0.20*s, 3.0, (1, 1, 1), target)            # back/rim (white)
    softbox(t+Vector((-0.16, 0.02, 0.02))*s, 0.10*s, 2.0, (1, 1, 1), target)          # side strip for the reeded edge
    softbox(t+Vector((0.0, -0.22, 0.03))*s, 0.20*s, 1.5, (1, 1, 1), target)           # frontal card

def light(name, kind, loc, energy, color=(1, 1, 1), size=0.1, target=(0, 0, 0)):
    ld = bpy.data.lights.new(name, kind); ld.energy = energy; ld.color = color
    if kind == 'AREA': ld.size = size
    ob = bpy.data.objects.new(name, ld); bpy.context.scene.collection.objects.link(ob); ob.location = loc
    d = Vector(target)-Vector(loc); ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return ob

def softbox(loc, size, strength, color=(1, 1, 1), target=(0, 0, 0)):
    bpy.ops.mesh.primitive_plane_add(size=size, location=loc); p = bpy.context.object
    d = Vector(target)-Vector(loc); p.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    m = bpy.data.materials.new('sb'); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    e = nt.nodes.new('ShaderNodeEmission'); e.inputs[0].default_value = (*color, 1); e.inputs[1].default_value = strength
    o = nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(e.outputs[0], o.inputs[0])
    p.data.materials.append(m); p.visible_camera = False
    return p

def studio(scale=1.0, neon=9.0):
    s = scale
    softbox((-0.12*s, -0.10*s, 0.20*s), 0.16*s, 5)                    # key softbox
    softbox((0.15*s, 0.05*s, 0.12*s), 0.10*s, 2.5, (1, 0.95, 0.9))      # fill
    softbox((0.0, 0.03*s, 0.30*s), 0.22*s, 1.6)                         # overhead soft (face reflection)
    softbox((0.0, 0.20*s, 0.015*s), 0.20*s, neon, (0.1, 0.85, 1.0), (0, 0, 0.02*s))   # low neon cyan rim (edges only)
    softbox((-0.20*s, 0.0, 0.015*s), 0.14*s, neon, (1.0, 0.15, 0.75), (0, 0, 0.02*s)) # low neon magenta rim
    softbox((0.0, -0.2*s, 0.02*s), 0.3*s, 0.6, (0.9, 0.9, 1.0))         # low front kicker

def coin(k):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(D, f'{k}-coin.glb'))
    ob = [o for o in bpy.data.objects if o not in before and o.type == 'MESH'][0]
    ob.rotation_mode = 'XYZ'
    return ob

def cam(loc, target, lens=85):
    cd = bpy.data.cameras.new('cam'); cd.lens = lens; cd.clip_start = 0.001
    ob = bpy.data.objects.new('cam', cd); bpy.context.scene.collection.objects.link(ob); ob.location = loc
    ob.rotation_euler = (Vector(target)-Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = ob; return ob

os.makedirs(R, exist_ok=True)
if mode in ('test', 'contact'):
    crews = CREWS if mode == 'contact' else ['code-e']
    cols = 5 if mode == 'contact' else 1; sp = 0.031
    rows = 2*math.ceil(len(crews)/cols)
    sc = scene_base((2000, int(2000*rows/cols*0.98)) if mode == 'contact' else (900, 1700), 64)
    for i, k in enumerate(crews):
        cx, cy = i % cols, (i//cols)*2
        for row, flip in ((cy, False), (cy+1, True)):
            ob = coin(k); ob.location = ((cx-(cols-1)/2)*sp, ((rows-1)/2-row)*sp, 0)
            ob.rotation_euler = (0, math.pi if flip else 0, 0)
    neutral_world(); neutral_lights((0, 0, 0), 2.6)
    softbox((0.12, -0.10, 0.6), 0.35, 3.0)          # broad overhead for top-down faces
    c = cam((0, -0.02, 0.5), (0, 0, 0)); c.data.type = 'ORTHO'; c.data.ortho_scale = cols*sp*1.06
    c.rotation_euler = (math.atan2(0.02, 0.5), 0, 0)
    sc.render.filepath = os.path.join(R, 'coins-contact-raw.png' if mode == 'contact' else 'test.png')
    bpy.ops.render.render(write_still=True)
elif mode == 'turntable':
    sc = scene_base((560, 560), 48); neutral_world(); neutral_lights((0, 0, 0.016), 1.0); sc.view_settings.exposure = 0.35
    ob = coin('code-e'); ob.location = (0, 0, 0.016)
    ob.rotation_mode = 'XYZ'
    cam((0, -0.085, 0.03), (0, 0, 0.014), 70)
    n = 24
    for f in range(n):
        ob.rotation_euler = (math.radians(90), 0, 2*math.pi*f/n)
        sc.render.filepath = os.path.join(R, 'turntable-code-e', f'frame_{f:03d}.png')
        bpy.ops.render.render(write_still=True)
elif mode == 'hand':
    sc = scene_base((1200, 900), 96)
    import bmesh
    # stylized open palm from metaballs (no real person)
    mb = bpy.data.metaballs.new('hand'); mb.resolution = 0.0016; mb.render_resolution = 0.0012; mb.threshold = 0.5
    def el(co, r, sz=None):
        e = mb.elements.new(); e.co = co; e.radius = r
        if sz: e.type = 'ELLIPSOID'; e.size_x, e.size_y, e.size_z = sz
        return e
    el((0, -0.012, 0), 0.05, (0.95, 1.1, 0.32))                      # palm, ~90 mm wide
    el((0, -0.03, -0.004), 0.045, (0.9, 1.0, 0.35))
    for x, L, a0 in ((-0.031, .062, 0.12), (-0.011, .074, 0.04), (0.009, .072, -0.03), (0.028, .058, -0.1)):
        for t in range(9):
            u = t/8; y = 0.018+u*(L+0.017); z = 0.003+0.012*u*u
            el((x+math.sin(a0)*u*L, y, z), 0.0125-0.003*u)              # slightly curled fingers
    for x in (-0.031, -0.011, 0.009, 0.028): el((x, 0.026, 0.002), 0.016)   # knuckles
    for t in range(9):
        u = t/8; el((-0.03-0.035*u, -0.028+0.03*u, 0.006+0.006*u), 0.0145-0.003*u)  # thumb
    el((0, -0.075, -0.004), 0.04, (0.8, 1.2, 0.5))                   # wrist
    ho = bpy.data.objects.new('hand', mb); sc.collection.objects.link(ho)
    hm = bpy.data.materials.new('skin'); hm.use_nodes = True; P = hm.node_tree.nodes['Principled BSDF']
    P.inputs['Base Color'].default_value = (0.55, 0.36, 0.27, 1); P.inputs['Roughness'].default_value = 0.5
    P.inputs['Subsurface Weight'].default_value = 0.3; P.inputs['Subsurface Radius'].default_value = (0.004, 0.0015, 0.001)
    ho.data.materials.append(hm)
    ho.location = (0, 0, 0.012); ho.rotation_euler = (0, 0, math.radians(-15))
    ob = coin('code-e'); ob.location = (0.002, -0.008, 0.0225); ob.rotation_euler = (math.radians(-8), math.radians(6), 0)
    studio(2.5, neon=2.5)
    softbox((0.0, 0.17, 0.25), 0.16, 4.0, (1, 0.96, 0.9), (0, 0, 0.02))   # mirror-angle softbox: gold face reflects warm white
    softbox((0.05, 0.02, 0.35), 0.3, 2.0)          # overhead neutral softbox (keeps gold reading gold)
    cam((0.0, -0.17, 0.24), (0, 0.012, 0.012), 50)
    sc.render.filepath = os.path.join(R, 'coin-in-hand.png')
    bpy.ops.render.render(write_still=True)
