# behemoth rider — per-crew config + crew-specific geometry. Shared pipeline: ../../shared/rider_lib.py
import sys; sys.path.insert(0, "/workspace/skyrydahs-characters/shared")
from rider_lib import *
import rider_lib as RL
from hero_face import *
CFG = {'name': 'behemoth', 'out': '/workspace/skyrydahs-characters/behemoth/', 'prefix': 'Behemoth', 'glowpts': [], 'bulk': (1.22, 1.18), 'painted': True, 'bake': True}
init(CFG)
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
FACE = hero_head(dict(jaw=0.2, width=0.95, chin=0.006, nose=1.3, mouth_w=1.15, cheek=1.5, ear=1.1, browridge=2.0, eye=dict(x=0.036, w=1.0, h=0.45, rot=6, iris=0.8, lash=0.8, flick=0.5), brow=dict(inner=1.683, mid=1.69, outer=1.689, thick=1.6)))
module('hair')
# shaved sides + tall clumped mohawk; dust-mask gaiter pulled down to the neck so the face reads
hair_cap(0.06, 0.109)
for k in range(9):
    t=k/8; d=Vector((0,-0.65+1.45*t,1.0-0.45*abs(t-0.35)))
    clump(d,Vector((0,0.25*t-0.05,1)),0.1-0.03*abs(t-0.35),0.022,0.03,bend=Vector((0,0.25,-0.1)))
bpy.ops.mesh.primitive_torus_add(major_radius=0.078,minor_radius=0.032,major_segments=18,minor_segments=6,location=(0,0.005,1.5)); o=bpy.context.object
o.scale=(1,0.95,0.8); bpy.ops.object.transform_apply(scale=True); finish(o,'cloth','chest')
module('accessory','chains')
# ---------- chains (metal links along hip + to pocket) ----------
chain([Vector((0.15,-0.06,0.97)),Vector((0.08,-0.135,0.86)),Vector((-0.06,-0.13,0.88)),Vector((-0.14,-0.07,0.96))],16)
chain([Vector((0.16,-0.04,0.97)),Vector((0.21,0.0,0.86)),Vector((0.16,0.08,0.95))],10)

module('body')
# belt
ring("belt",(0,0,0.99),0.155,0.035,mat='skate',sc=(1,0.75,1))
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,-0.118,0.99)); o=bpy.context.object; o.scale=(0.05,0.01,0.035); bpy.ops.object.transform_apply(scale=True); finish(o,'gold',None,False)

module('top')
# zipper teeth + gold lining at open front, rib waistband/cuffs, sleeve utility pocket, flap pockets, seam piping
for s in (1,-1):
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

module('accessory','emblem')
# ---------- gold lightning accents on jacket ----------
module('top')
# padded hi-vis utility vest (ANSI 107 style bands), worn over black hoodie
vv=skin_obj("vest",[(0,0.005,1.03),(0,0.005,1.20),(0,0.005,1.36),(0,0.005,1.45)],[(0,1),(1,2),(2,3)],[(0.18,0.135),(0.175,0.13),(0.195,0.135),(0.15,0.11)])
bm=bmesh.new(); bm.from_mesh(vv.data)
bmesh.ops.delete(bm,geom=[f for f in bm.faces if (lambda c:(c.y<-0.07 and abs(c.x)<0.05) or c.z>1.5 or (abs(c.x)>0.17 and c.z>1.30))(f.calc_center_median())],context='FACES')
bm.to_mesh(vv.data); bm.free(); m=vv.modifiers.new("s",'SOLIDIFY'); m.thickness=0.02; apply_all(vv); finish(vv,'gold')
for z in (1.12,1.24): ring("band",(0,0.005,z),0.2,0.025,mat='metal',segs=18,sc=(1,0.73,1))
for s_ in (1,-1):
    cube((0.09*s_,-0.135,1.33),(0.035,0.012,0.22),'metal',0,None,(math.radians(-8),0,0))
    cube((0.09*s_,0.135,1.33),(0.035,0.012,0.22),'metal',0,None,(math.radians(8),0,0))
    for k in range(2): cube((0.11*s_,-0.15,1.07+0.09*k),(0.08,0.03,0.07),'cloth',0.008)
    cube((0.15*s_,-0.12,1.40),(0.03,0.02,0.04),'skate',0.004)
for k in range(4): cube((0,-0.115,1.10+0.08*k),(0.03,0.02,0.015),'skate',0.003)
bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=0.12,location=(0,0.13,1.47)); o=bpy.context.object
o.scale=(1.0,0.55,0.75); bpy.ops.object.transform_apply(scale=True); finish(o,'jacket','chest')
for s_ in (1,-1): cube((0.2*s_,-0.03,1.47),(0.04,0.02,0.02),'glow2',0,'shoulder.'+('L' if s_>0 else 'R'))
module('body')
# ---------- cargo pants details ----------
for s in (1,-1):
    cube((0.175*s,-0.01,0.74),(0.035,0.11,0.12),'cloth',0.01)            # bellows cargo pocket
    cube((0.178*s,-0.01,0.80),(0.045,0.12,0.03),'cloth',0.006)           # flap
    cube((0.197*s,-0.01,0.80),(0.006,0.02,0.012),'gold',0)                # snap
    ring("strap",(0.115*s,-0.012,0.68),0.088,0.022,mat='skate',sc=(1,0.95,1),bone='thigh.'+('L' if s>0 else 'R'))   # thigh webbing strap
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


add_expressions(FACE)
build_skates()
build_inventory()
finalize()
