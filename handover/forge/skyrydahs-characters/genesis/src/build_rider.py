# genesis rider — per-crew config + crew-specific geometry. Shared pipeline: ../../shared/rider_lib.py
# Shared base body (pants/shirt/jacket/head/face/belt/cargo) is the Code : E base; crew silhouette parts below.
import sys; sys.path.insert(0, "/workspace/skyrydahs-characters/shared")
from rider_lib import *
import rider_lib as RL
from hero_face import *
import hero_face as HF
CFG = {'name': 'genesis', 'out': '/workspace/skyrydahs-characters/genesis/', 'prefix': 'Genesis', 'glowpts': [], 'painted': True, 'bake': True, 'bulk': (1.03, 1.0)}
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
FACE = HF.hero_head(dict(jaw=0.4, chin=0.003, mouth_w=1.1, lips=0.6, eye=dict(w=1.18, h=0.58, rot=14, iris=0.9, lash=1.25, flick=1.4), brow=dict(inner=1.686, mid=1.698, outer=1.69, thick=0.9)))
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

module('accessory','puffer')
# SIGNATURE: cropped high-shine puffer with oversized shoulder pods (wide inverted-triangle silhouette)
for k,z in enumerate((1.10,1.19,1.28,1.37)):
    bpy.ops.mesh.primitive_torus_add(major_radius=0.155+0.01*(k==2),minor_radius=0.036,major_segments=20,minor_segments=6,location=(0,0.005,z))
    o=bpy.context.object; o.scale=(1,0.78,1); bpy.ops.object.transform_apply(scale=True); finish(o,'jacket')
ring("hemGold",(0,0.005,1.06),0.165,0.012,sc=(1,0.78,1))
module('accessory','pods')
for s in (1,-1):
    L='L' if s>0 else 'R'
    bpy.ops.mesh.primitive_uv_sphere_add(segments=14,ring_count=8,radius=0.11,location=(0.24*s,0.0,1.45)); o=bpy.context.object
    o.scale=(1.35,1.05,0.85); bpy.ops.object.transform_apply(scale=True); finish(o,'jacket','upperarm.'+L)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.075,minor_radius=0.025,major_segments=14,minor_segments=5,location=(0.32*s,0.005,1.30),rotation=(0,math.radians(-45*s),0))
    finish(bpy.context.object,'jacket','upperarm.'+L)
    ring("podGold",(0.33*s,0.0,1.43),0.11,0.01,rot=(0,math.radians(-60*s),0),mat='gold',bone='upperarm.'+L)
module('top')
ring("collarGold",(0,0.01,1.555),0.12,0.014,sc=(1,0.85,1))
module('hair')
# tall glossy pompadour built from big swept clumps rolling up-and-back, slicked sides
HF.hair_cap(0.05)
rnd=random.Random(2)
for i,x in enumerate((-0.06,-0.035,-0.012,0.012,0.035,0.06)):
    d=Vector((x*6,-0.8,0.55))
    HF.clump(d,Vector((x*2,-0.25,1)),0.15+0.02*(1-abs(x)/0.06),0.045,0.022,bend=Vector((0,0.55,-0.1)))
for i in range(10):
    az=math.radians(rnd.uniform(70,290)); el=math.radians(rnd.uniform(0,35))
    d=Vector((math.sin(az)*math.cos(el),-math.cos(az)*math.cos(el),math.sin(el)))
    HF.clump(d,Vector((d.x*0.25,0.9,-0.25)),rnd.uniform(0.09,0.12),0.05,0.012,bend=Vector((0,0,-0.15)))
module('accessory','shades')
# slim wrap shield shades (v2: thinner band, tighter arc, sits on the face) with fine gold brow bar
bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=0.119,depth=0.026,location=(0,0.0,1.657)); o=bpy.context.object
bm=bmesh.new(); bm.from_mesh(o.data); bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.y>-0.07],context='VERTS'); bm.to_mesh(o.data); bm.free()
m=o.modifiers.new("s",'SOLIDIFY'); m.thickness=0.003; apply_all(o); finish(o,'iris','head',True)
cube((0,-0.119,1.672),(0.13,0.004,0.004),'gold',0,'head')
module('accessory','chains')
chain([Vector((-0.075,-0.06,1.47)),Vector((-0.04,-0.15,1.36)),Vector((0.04,-0.15,1.36)),Vector((0.075,-0.06,1.47))],16,0.013)
flat("pendant",star(0.035,0.015),'gold',(0,-0.16,1.31),(0,0,0),'chest',0.008)
module('accessory','emblem')
# BACK EMBLEM: winged five-point star (premium crest), gold on magenta
flat("star",star(0.075,0.032),'gold',(0,0.162,1.28),(0,0,0),'chest',0.006)
for s in (1,-1):
    wing=[(0.05*s,0.025),(0.2*s,0.095),(0.17*s,0.045),(0.21*s,0.03),(0.16*s,0.0),(0.18*s,-0.03),(0.12*s,-0.03),(0.05*s,-0.02)]
    flat("wing",wing,'gold',(0,0.165,1.28),(0,0,0),'chest',0.006)

HF.add_expressions(FACE)
build_skates()
build_inventory()
finalize()
