# tool-toul-to rider — per-crew config + crew-specific geometry. Shared pipeline: ../../shared/rider_lib.py
# Shared base body (pants/shirt/jacket/head/face/belt/cargo) is the Code : E base; crew silhouette parts below.
import sys; sys.path.insert(0, "/workspace/skyrydahs-characters/shared")
from rider_lib import *
CFG = {'name': 'tool-toul-to', 'out': '/workspace/skyrydahs-characters/tool-toul-to/', 'prefix': 'ToolToulTo', 'glowpts': [('GlowPt_stacks', 'chest', (0, 0.25, 1.72), 0.12)]}
init(CFG)
random.seed(7)

from mathutils import Matrix
def flat(name, pts, mat, loc, rot=(0,0,0), bone=None, th=0.008, plane='xz'):
    """flat polygon cut-out (coat tails, leaves, wings, emblems); pts 2D in the given plane"""
    vs=[(a,0,b) if plane=='xz' else (a,b,0) for a,b in pts]
    me=bpy.data.meshes.new(name); me.from_pydata(vs,[],[list(range(len(vs)))]); o=bpy.data.objects.new(name,me)
    bpy.context.scene.collection.objects.link(o); bpy.context.view_layer.objects.active=o
    m=o.modifiers.new("s",'SOLIDIFY'); m.thickness=th; m.offset=0; apply_all(o)
    o.location=loc; o.rotation_euler=[math.radians(r) for r in rot]
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    return finish(o,mat,bone,False)
def circle(r,n=14,cx=0,cz=0): return [(cx+r*math.cos(2*math.pi*i/n),cz+r*math.sin(2*math.pi*i/n)) for i in range(n)]
def star(ro,ri,n=5): return [((ro if i%2==0 else ri)*math.sin(math.pi*i/n),(ro if i%2==0 else ri)*math.cos(math.pi*i/n)) for i in range(2*n)]
def pivot_rot(o, pivot, ax_deg):
    pv=Vector(pivot); o.matrix_world = Matrix.Translation(pv) @ Matrix.Rotation(math.radians(ax_deg),4,'X') @ Matrix.Translation(-pv) @ o.matrix_world
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active=o; bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
def hair_cap():
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=0.115,location=(0,0.012,1.675))
    cap=bpy.context.object; bm=bmesh.new(); bm.from_mesh(cap.data)
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if (v.co.y<-0.02 and v.co.z<0.05) or v.co.z<-0.07 or (v.co.y<0.03 and v.co.z<-0.01)],context='VERTS')
    bm.to_mesh(cap.data); bm.free(); cap.scale=(0.95,1.05,1); bpy.ops.object.transform_apply(scale=True); finish(cap,'hair','head')
module('body')
# legs / pelvis (baggy pants)
for side in (1,-1):
    v=[(0.0,0,1.00),(0.10*side,0,0.97),(0.115*side,-0.01,0.78),(0.12*side,-0.02,0.58),(0.115*side,0,0.46),(0.11*side,0.0,0.39)]
    e=[(i,i+1) for i in range(len(v)-1)]
    r=[(0.15,0.11),(0.10,0.10),(0.095,0.09),(0.075,0.075),(0.085,0.08),(0.075,0.075)]
    finish(skin_obj("pants"+("L" if side>0 else "R"),v,e,r),'cloth')
# shirt torso core (visible at open jacket)
v=[(0,0,0.98),(0,0,1.15),(0,0.0,1.32),(0,0,1.45)]
finish(skin_obj("shirt",v,[(0,1),(1,2),(2,3)],[(0.13,0.09),(0.12,0.085),(0.15,0.095),(0.10,0.08)]),'cloth')
module('top')
# jacket: torso + sleeves, A-pose
jv=[(0,0.005,1.02),(0,0.005,1.18),(0,0.005,1.34),(0,0.005,1.44),
    (0.2,0.005,1.42),(0.31,0.005,1.31),(0.42,0.005,1.20),(0.53,0.005,1.09),
    (-0.2,0.005,1.42),(-0.31,0.005,1.31),(-0.42,0.005,1.20),(-0.53,0.005,1.09)]
je=[(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(3,8),(8,9),(9,10),(10,11)]
jr=[(0.155,0.115),(0.145,0.105),(0.175,0.115),(0.12,0.09),(0.075,0.075),(0.068,0.068),(0.058,0.058),(0.062,0.062),
    (0.075,0.075),(0.068,0.068),(0.058,0.058),(0.062,0.062)]
jk=skin_obj("jacket",jv,je,jr)
# open front: delete faces in a front strip
bm=bmesh.new(); bm.from_mesh(jk.data)
kill=[f for f in bm.faces if (lambda c: c.y<-0.06 and abs(c.x)<0.045 and 1.0<c.z<1.47)(f.calc_center_median())]
bmesh.ops.delete(bm,geom=kill,context='FACES')
sol=bmesh.ops.extrude_face_region(bm,geom=bm.faces[:])  # thickness
bmesh.ops.delete(bm,geom=[f for f in sol['geom'] if isinstance(f,bmesh.types.BMFace)][:0],context='FACES')
bm.to_mesh(jk.data); bm.free()
sol=jk.modifiers.new("sol",'SOLIDIFY'); sol.thickness=0.012; apply_all(jk)
finish(jk,'jacket')
# jacket hem + cuffs (gold trim bands)
ring("hem",(0,0.005,1.03),0.162,0.008,sc=(1,0.76,1))
for s in (1,-1):
    a=math.atan2(-0.11,0.11)  # sleeve direction
    ring("cuff",(0.555*s,0.005,1.065),0.064,0.04,rot=(0,math.radians(-45*s),0),mat='gold')
# popped collar
bpy.ops.mesh.primitive_cone_add(vertices=16,radius1=0.085,radius2=0.12,depth=0.11,location=(0,0.01,1.50))
c=bpy.context.object; c.scale=(1,0.85,1); bpy.ops.object.transform_apply(scale=True)
bm=bmesh.new(); bm.from_mesh(c.data)
bmesh.ops.delete(bm,geom=[f for f in bm.faces if abs(f.normal.z)>0.9 or (f.calc_center_median().y<-0.07 and abs(f.calc_center_median().x)<0.03)],context='FACES')
bm.to_mesh(c.data); bm.free()
m=c.modifiers.new("s",'SOLIDIFY'); m.thickness=0.01; apply_all(c); finish(c,'jacket')
module('body')
# neck
finish(skin_obj("neck",[(0,0.01,1.42),(0,0.01,1.56)],[(0,1)],[0.045,0.042]),'skin','head')
# hands (fingerless-glove fists) + fingers
for s in (1,-1):
    w=Vector((0.60*s,0,1.02)); d=Vector((0.70*s,0,0.92))-w
    v=[tuple(w),tuple(w+d*0.5),tuple(w+d)]
    h=skin_obj("hand",v,[(0,1),(1,2)],[(0.032,0.022),(0.042,0.022),(0.03,0.02)])
    finish(h,'skin')
    th=skin_obj("thumb",[tuple(w+d*0.2+Vector((0,-0.03,0))),tuple(w+d*0.55+Vector((0,-0.045,0)))],[(0,1)],[0.014,0.012]); finish(th,'skin')
    ring("glove",tuple(w+d*0.12),0.04,0.04,rot=(0,math.radians(-45*s),0),mat='skate')

module('body')
# ---------- head ----------
bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,radius=0.105,location=(0,0,1.66))
hd=bpy.context.object; hd.name="head"
for vv in hd.data.vertices:
    p=vv.co
    p.y*=1.05; p.x*=0.9
    if p.z<0:  # jaw taper to anime chin
        t=min(1,-p.z/0.105); p.x*=1-0.45*t*t; p.y*=1-0.15*t; 
        if p.y<0: p.y-=0.015*t
        p.z*=1.12
    if p.y<-0.06 and p.z<0.02 and abs(p.x)<0.02: p.y-=0.008  # nose ridge
finish(hd,'skin','head')
# ears
for s in (1,-1):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=6,radius=0.025,location=(0.092*s,0.01,1.65)); e=bpy.context.object
    e.scale=(0.4,0.8,1.1); bpy.ops.object.transform_apply(scale=True); finish(e,'skin','head')
# eyes: whites + gold iris + dark brow
for s in (1,-1):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=0.025,location=(0.037*s,-0.097,1.655)); e=bpy.context.object
    e.scale=(1.1,0.35,0.8); e.rotation_euler=(0,0,math.radians(10*s)); bpy.ops.object.transform_apply(scale=True,rotation=True); finish(e,'eyes','head')
    bpy.ops.mesh.primitive_uv_sphere_add(segments=10,ring_count=6,radius=0.015,location=(0.036*s,-0.1035,1.651)); e=bpy.context.object
    e.scale=(0.85,0.3,1.25); bpy.ops.object.transform_apply(scale=True); finish(e,'iris','head')
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=6,radius=0.007,location=(0.036*s,-0.1075,1.651)); e=bpy.context.object
    e.scale=(0.8,0.3,1.3); bpy.ops.object.transform_apply(scale=True); finish(e,'hair','head')
    bpy.ops.mesh.primitive_cube_add(size=1,location=(0.04*s,-0.101,1.685)); e=bpy.context.object
    e.scale=(0.042,0.008,0.008); e.rotation_euler=(0,math.radians(-16*s),math.radians(-10*s)); bpy.ops.object.transform_apply(scale=True,rotation=True); finish(e,'hair','head',False)
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,-0.1,1.603)); e=bpy.context.object
e.scale=(0.022,0.006,0.0035); bpy.ops.object.transform_apply(scale=True); finish(e,'hair','head',False)
# nose (subtle wedge)
bpy.ops.mesh.primitive_cone_add(vertices=4,radius1=0.009,radius2=0.0,depth=0.026,location=(0,-0.107,1.628),rotation=(math.radians(-70),0,math.radians(45)))
e=bpy.context.object; e.scale=(1,0.7,1); bpy.ops.object.transform_apply(scale=True); finish(e,'skin','head',True)
for s in (1,-1):
    # upper lash line (thick anime liner) + catchlight
    bpy.ops.mesh.primitive_cube_add(size=1,location=(0.038*s,-0.1035,1.667)); e=bpy.context.object
    e.scale=(0.05,0.008,0.0055); e.rotation_euler=(0,math.radians(-8*s),math.radians(-10*s)); bpy.ops.object.transform_apply(scale=True,rotation=True); finish(e,'hair','head',False)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=6,ring_count=4,radius=0.0035,location=(0.032*s,-0.1085,1.658)); finish(bpy.context.object,'eyes','head')
module('body')
# belt
ring("belt",(0,0,0.99),0.155,0.035,mat='skate',sc=(1,0.75,1))
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,-0.118,0.99)); o=bpy.context.object; o.scale=(0.05,0.01,0.035); bpy.ops.object.transform_apply(scale=True); finish(o,'gold',None,False)

module('top')
# zipper teeth + gold lining at open front, rib waistband/cuffs, sleeve utility pocket, flap pockets, seam piping
for s in (1,-1):
    cube((0.05*s,-0.116,1.24),(0.006,0.005,0.38),'metal',0)
    cube((0.043*s,-0.11,1.24),(0.005,0.004,0.38),'gold',0)
    cube((0.105*s,-0.112,1.07),(0.075,0.02,0.07),'jacket',0.006)       # lower flap pocket
    cube((0.105*s,-0.124,1.10),(0.08,0.012,0.022),'jacket',0.004)      # flap
    cube((0.105*s,-0.13,1.10),(0.012,0.004,0.01),'gold',0)             # snap
    # shoulder yoke seam piping (taped seam)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.072,minor_radius=0.005,major_segments=14,minor_segments=4,location=(0.205*s,0.005,1.405),rotation=(0,math.radians(90-45*s+0),0))
    o=bpy.context.object; o.rotation_euler=(0,math.radians(50*s),0); finish(o,'cloth')
    # elbow articulation seam
    bpy.ops.mesh.primitive_torus_add(major_radius=0.06,minor_radius=0.004,major_segments=12,minor_segments=4,location=(0.42*s,0.005,1.20),rotation=(0,math.radians(45*s),0)); finish(bpy.context.object,'cloth')
# sleeve utility zip pocket on left upper arm
cube((0.30,-0.045,1.33),(0.06,0.02,0.08),'jacket',0.006,None,(0,math.radians(-45),math.radians(-10)))
cube((0.302,-0.058,1.355),(0.05,0.006,0.008),'gold',0,None,(0,math.radians(-45),math.radians(-10)))
# rib-knit waistband over hem
for k in range(3): ring("rib",(0,0.005,0.985+k*0.016),0.158,0.012,mat='jacket',sc=(1,0.76,1))
# chest oxygen-tab (MA-1 nod)
module('body')
# ---------- cargo pants details ----------
for s in (1,-1):
    cube((0.175*s,-0.01,0.74),(0.035,0.11,0.12),'cloth',0.01)            # bellows cargo pocket
    cube((0.178*s,-0.01,0.80),(0.045,0.12,0.03),'cloth',0.006)           # flap
    cube((0.197*s,-0.01,0.80),(0.006,0.02,0.012),'gold',0)                # snap
    ring("strap",(0.115*s,-0.012,0.68),0.088,0.022,mat='skate',sc=(1,0.95,1),bone='thigh.'+('L' if s>0 else 'R'))   # thigh webbing strap (rigid to thigh)
    cube((0.115*s,-0.098,0.68),(0.035,0.012,0.03),'gold',0.003,'thigh.'+('L' if s>0 else 'R'))          # buckle
    ring("knee",(0.12*s,-0.02,0.53),0.078,0.008,mat='jacket',bone='shin.'+('L' if s>0 else 'R'))            # knee panel seam
    ring("cinch",(0.11*s,0,0.41),0.083,0.03,mat='skate')                 # snap-tab ankle cinch
module('accessory','battery')
# waist battery pack (AtmosGear-style) + cables to each skate
cube((0,0.13,0.97),(0.17,0.06,0.09),'skate',0.015)
cube((0,0.162,0.97),(0.12,0.006,0.012),'wheelGlow',0)
for s in (1,-1):
    pts=[(0.07*s,0.15,0.94),(0.17*s,0.09,0.86),(0.20*s,0.06,0.62),(0.17*s,0.08,0.46),(0.13*s,0.12,0.37)]
    finish(skin_obj("cable",pts,[(i,i+1) for i in range(len(pts)-1)],[0.007]*len(pts),0),'skate')

module('accessory','workwear')
# coverall details: rolled sleeves + knee pads
for s in (1,-1):
    L='L' if s>0 else 'R'
    ring("roll",(0.42*s,0.005,1.20),0.072,0.06,rot=(0,math.radians(-45*s),0),mat='jacket',bone='upperarm.'+L)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=10,ring_count=6,radius=0.065,location=(0.12*s,-0.08,0.56)); o=bpy.context.object
    o.scale=(1,0.55,1.1); bpy.ops.object.transform_apply(scale=True); finish(o,'skate','shin.'+L)
    cube((0.09*s,-0.135,0.93),(0.07,0.04,0.08),'skate',0.008,'hips')                 # leather tool pouches
    for k in range(2):
        bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=0.007,depth=0.08,location=(0.08*s+0.02*k,-0.135,1.0)); finish(bpy.context.object,'metal','hips')
module('hair')
hair_cap()
for i in range(12):
    th=random.uniform(0,2*math.pi); ph=random.uniform(0.6,1.3)
    d=Vector((math.sin(ph)*math.cos(th),abs(math.sin(ph)*math.sin(th))*0.8+0.3,math.cos(ph)))
    spike(d,random.uniform(0.05,0.08),0.03,bend=0.1)
ring("bandana",(0,0.012,1.705),0.112,0.03,rot=(math.radians(-10),0,0),mat='gold',segs=18,bone='head')
module('accessory','welder')
# SIGNATURE 1: welding helmet flipped up on top of the head
bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=10,radius=0.135,location=(0,0.0,1.66)); sh=bpy.context.object
sh.scale=(1,1,1.15); bpy.ops.object.transform_apply(scale=True)
bm=bmesh.new(); bm.from_mesh(sh.data); bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.y>-0.03],context='VERTS'); bm.to_mesh(sh.data); bm.free()
m=sh.modifiers.new("s",'SOLIDIFY'); m.thickness=0.012; apply_all(sh); finish(sh,'skate','head')
lens=cube((0,-0.138,1.675),(0.1,0.012,0.04),'hair',0.003,'head'); led=cube((0.06,-0.14,1.62),(0.012,0.006,0.012),'glow2',0,'head')
for o in (sh,lens,led): pivot_rot(o,(0,0.0,1.72),-78)
for s in (1,-1):
    bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=0.025,depth=0.02,location=(0.138*s,0.0,1.72),rotation=(0,math.radians(90),0)); finish(bpy.context.object,'metal','head')
module('accessory','toolpack')
# SIGNATURE 2: workshop tool-pack with twin exhaust stacks and an oversized spanner breaking the silhouette
cube((0,0.215,1.26),(0.3,0.15,0.34),'cloth',0.025,'chest')
for s in (1,-1):
    cube((0.12*s,0.13,1.28),(0.04,0.03,0.34),'skate',0.004,'chest')                    # shoulder straps
    bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=0.026,depth=0.34,location=(0.115*s,0.25,1.55)); finish(bpy.context.object,'metal','chest')
    ring("stackTip",(0.115*s,0.25,1.72),0.03,0.03,mat='gold',segs=10,bone='chest')
cube((0.0,0.3,1.27),(0.2,0.012,0.012),'skate',0,'chest')
sp=cube((-0.06,0.3,1.56),(0.035,0.018,0.42),'metal',0.005,'chest',(0,math.radians(-22),0))
bpy.ops.mesh.primitive_torus_add(major_radius=0.045,minor_radius=0.017,major_segments=12,minor_segments=5,location=(-0.14,0.3,1.76),rotation=(math.radians(90),0,0)); finish(bpy.context.object,'metal','chest')
cube((-0.14,0.3,1.815),(0.03,0.03,0.04),'cloth',0,'chest')                               # open jaw notch
module('accessory','emblem')
# BACK EMBLEM (board 04 "gear" language, original): rust gear + spanner + spark
bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=0.075,depth=0.012,location=(0,0.296,1.25),rotation=(math.radians(90),0,0)); finish(bpy.context.object,'gold','chest')
for k in range(8):
    a=2*math.pi*k/8; cube((0.088*math.cos(a),0.296,1.25+0.088*math.sin(a)),(0.026,0.012,0.026),'gold',0,'chest',(0,-a,0))
flat("hub",circle(0.035,10),'cloth',(0,0.304,1.25),(0,0,0),'chest',0.004)
flat("spanner",[(-0.012,-0.08),(0.012,-0.08),(0.012,0.06),(0.03,0.075),(0.012,0.09),(-0.012,0.09),(-0.03,0.075),(-0.012,0.06)],'metal',(0,0.308,1.25),(0,-35,0),'chest',0.004)
flat("spark",[(0,0.03),(0.008,0.005),(0.025,0),(0.008,-0.005),(0,-0.03),(-0.008,-0.005),(-0.025,0),(-0.008,0.005)],'glow2',(0.05,0.31,1.3),(0,0,0),'chest',0.004)

build_skates()
build_inventory()
finalize()
