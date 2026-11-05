# static-angels rider — per-crew config + crew-specific geometry. Shared pipeline: ../../shared/rider_lib.py
import sys; sys.path.insert(0, "/workspace/skyrydahs-characters/shared")
from rider_lib import *
import rider_lib as RL
from hero_face import *
CFG = {'name': 'static-angels', 'out': '/workspace/skyrydahs-characters/static-angels/', 'prefix': 'StaticAngels', 'glowpts': [('GlowPt_halo', 'head', (0, 0.03, 1.93), 0.55)], 'painted': True, 'bake': True, 'wheels4': True, 'bulk': (0.93, 0.95)}
init(CFG)
module('body')
# legs / pelvis (baggy pants)
for side in (1,-1):
    v=[(0.0,0,1.00),(0.10*side,0,0.97),(0.115*side,-0.01,0.78),(0.12*side,-0.02,0.58),(0.115*side,0,0.46),(0.11*side,0.0,0.39)]
    e=[(i,i+1) for i in range(len(v)-1)]
    r=[(0.16,0.115),(0.11,0.105),(0.10,0.095),(0.08,0.08),(0.09,0.085),(0.078,0.078)]
    finish(skin_obj("pants"+("L" if side>0 else "R"),v,e,r),'cloth')
# shirt torso core (visible at open jacket)
# bare midriff (skin) + black crop top
finish(skin_obj("midriff",[(0,0,0.98),(0,0,1.10),(0,0,1.24)],[(0,1),(1,2)],[(0.135,0.09),(0.105,0.075),(0.115,0.08)]),'skin')
finish(skin_obj("croptop",[(0,0,1.22),(0,-0.005,1.33),(0,0,1.45)],[(0,1),(1,2)],[(0.125,0.085),(0.135,0.10),(0.10,0.075)]),'cloth')
module('top')
# jacket: torso + sleeves, A-pose
jv=[(0,0.005,1.24),(0,0.005,1.30),(0,0.005,1.34),(0,0.005,1.44),
    (0.18,0.005,1.42),(0.30,0.005,1.31),(0.42,0.005,1.20),(0.53,0.005,1.09),
    (-0.18,0.005,1.42),(-0.30,0.005,1.31),(-0.42,0.005,1.20),(-0.53,0.005,1.09)]
je=[(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(3,8),(8,9),(9,10),(10,11)]
jr=[(0.15,0.11),(0.15,0.11),(0.165,0.12),(0.11,0.085),(0.07,0.07),(0.066,0.066),(0.06,0.06),(0.066,0.066),
    (0.07,0.07),(0.066,0.066),(0.06,0.06),(0.066,0.066)]
jk=skin_obj("jacket",jv,je,jr)
# open front: delete faces in a front strip
bm=bmesh.new(); bm.from_mesh(jk.data)
kill=[f for f in bm.faces if (lambda c: c.y<-0.06 and abs(c.x)<0.05 and 1.2<c.z<1.47)(f.calc_center_median())]
bmesh.ops.delete(bm,geom=kill,context='FACES')
sol=bmesh.ops.extrude_face_region(bm,geom=bm.faces[:])  # thickness
bmesh.ops.delete(bm,geom=[f for f in sol['geom'] if isinstance(f,bmesh.types.BMFace)][:0],context='FACES')
bm.to_mesh(jk.data); bm.free()
sol=jk.modifiers.new("sol",'SOLIDIFY'); sol.thickness=0.012; apply_all(jk)
finish(jk,'jacket')
# jacket hem + cuffs (gold trim bands)
ring("hem",(0,0.005,1.205),0.155,0.03,mat='gold',sc=(1,0.76,1))
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
FACE = hero_head(dict(jaw=0.5, width=0.87, nose=0.8, mouth_w=0.9, lips=1, cheek=0.8, eye=dict(w=1.2, h=0.62, rot=12, iris=0.95, lash=1.45, flick=1.7, lower=1.2), brow=dict(inner=1.689, mid=1.696, outer=1.693, thick=0.7)))
module('hair')
# Halo (sheet 10): navy twin tails high on the head, soft swept bangs, side locks; halo ring; purple ties; earrings
hair_cap(0.035)
bangs([(-0.045,0.07,-0.3),(-0.02,0.055,0.0),(0.008,0.055,0.1),(0.034,0.085,0.3),(0.062,0.075,0.5),(-0.07,0.072,-0.5)],0.034,0.011)
rnd=random.Random(5)
for i in range(12):
    az=2*math.pi*i/12; d=Vector((math.sin(az)*0.75,-math.cos(az)*0.6+0.25,0.75))
    clump(d,Vector((d.x*0.9,d.y*0.9+0.3,-0.35)),rnd.uniform(0.08,0.11),0.055,0.014,bend=Vector((0,0,-0.3)))
for i in range(8):
    az=math.radians(110+i*20); d=Vector((math.sin(az),-math.cos(az),0.1))
    clump(d,d*0.4+Vector((0,0.1,-1)),rnd.uniform(0.1,0.13),0.045,0.015,bend=Vector((0,0,-0.05)))
for s in (1,-1):
    clump(Vector((0.92*s,-0.1,0.25)),Vector((0.12*s,0.05,-1)),0.14,0.028,0.01,bend=Vector((0,0,0)))
    tie=Vector((0.118*s,0.04,0.085)); L=tie.length
    for k,(ox,oy) in enumerate(((0,0),(0.012,0.01),(-0.01,0.012),(0.006,-0.008),(0.0,0.02),(0.02,0))):
        clump(tie,Vector((0.6*s+ox*10,0.3+oy*10,-0.35)),rnd.uniform(0.42,0.52),0.065,0.04,bend=Vector((-0.15*s,0,-0.6)),segs=7,root_r=(L,L,L))
    bpy.ops.mesh.primitive_torus_add(major_radius=0.026,minor_radius=0.01,major_segments=12,minor_segments=4,location=(0.122*s,0.055,1.762),rotation=(0,math.radians(70*s),0)); finish(bpy.context.object,'gold','head')
bpy.ops.mesh.primitive_torus_add(major_radius=0.13,minor_radius=0.009,major_segments=32,minor_segments=6,location=(0,0.03,1.93),rotation=(math.radians(-10),0,0)); finish(bpy.context.object,'glow2','head')
for sx in (1,-1):
    bpy.ops.mesh.primitive_torus_add(major_radius=0.008,minor_radius=0.002,major_segments=8,minor_segments=3,location=(0.094*sx,0.0,1.615),rotation=(0,math.radians(90),0)); finish(bpy.context.object,'metal','head')
module('accessory','chains')
# ---------- chains (metal links along hip + to pocket) ----------
chain([Vector((0.06,-0.13,0.97)),Vector((0.13,-0.13,0.86)),Vector((0.17,-0.06,0.84))],12)
chain([Vector((0.16,-0.04,0.97)),Vector((0.21,0.0,0.86)),Vector((0.16,0.08,0.95))],10)

module('body')
# belt
ring("belt",(0,0,0.99),0.155,0.035,mat='skate',sc=(1,0.75,1))
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,-0.118,0.99)); o=bpy.context.object; o.scale=(0.05,0.01,0.035); bpy.ops.object.transform_apply(scale=True); finish(o,'gold',None,False)

module('top')
# zipper teeth + gold lining at open front, rib waistband/cuffs, sleeve utility pocket, flap pockets, seam piping
for s in (1,-1):
    cube((0.052*s,-0.112,1.34),(0.006,0.005,0.24),'metal',0)
    cube((0.045*s,-0.106,1.34),(0.005,0.004,0.24),'gold',0)
    cube((0.06*s,-0.12,1.28),(0.006,0.006,0.035),'gold',0)            # zip pulls
    # shoulder yoke seam piping (taped seam)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.072,minor_radius=0.005,major_segments=14,minor_segments=4,location=(0.205*s,0.005,1.405),rotation=(0,math.radians(90-45*s+0),0))
    o=bpy.context.object; o.rotation_euler=(0,math.radians(50*s),0); finish(o,'cloth')
    # elbow articulation seam
    bpy.ops.mesh.primitive_torus_add(major_radius=0.06,minor_radius=0.004,major_segments=12,minor_segments=4,location=(0.42*s,0.005,1.20),rotation=(0,math.radians(45*s),0)); finish(bpy.context.object,'cloth')
# sleeve utility zip pocket on left upper arm
cube((0.30,-0.045,1.33),(0.06,0.02,0.08),'jacket',0.006,None,(0,math.radians(-45),math.radians(-10)))
cube((0.302,-0.058,1.355),(0.05,0.006,0.008),'gold',0,None,(0,math.radians(-45),math.radians(-10)))
# rib-knit waistband over hem

# chest oxygen-tab (MA-1 nod)
cube((0.29,-0.03,1.34),(0.05,0.03,0.05),'gold',0.004,None,(0,math.radians(-45),0))   # sleeve patch
for s in (1,-1): cube((0.36*s,0.0,1.26),(0.012,0.09,0.012),'gold',0,None,(0,math.radians(-45*s),0))  # sleeve straps
module('accessory','emblem')
# ---------- gold lightning accents on jacket ----------
# back emblem: stylized wing (crew mark)
for s_ in (1,-1):
    for k in range(3):
        cube((0.045*s_+0.03*k*s_,0.128,1.36-0.03*k),(0.07-0.015*k,0.004,0.014),'gold',0,None,(0,math.radians(-25*s_),0))
module('body')
# ---------- cargo pants details ----------
for s in (1,-1):
    cube((0.175*s,-0.01,0.74),(0.035,0.11,0.12),'cloth',0.01)            # bellows cargo pocket
    cube((0.178*s,-0.01,0.80),(0.045,0.12,0.03),'cloth',0.006)           # flap
    cube((0.197*s,-0.01,0.80),(0.006,0.02,0.012),'gold',0)                # snap
    cube((0.06*s,-0.112,0.82),(0.022,0.008,0.30),'gold',0.003)          # hanging strap front
    cube((0.06*s,-0.118,0.70),(0.03,0.012,0.02),'metal',0.002)          # strap buckle
    cube((0.10*s,0.11,0.80),(0.022,0.008,0.32),'gold',0.003)            # hanging strap back
    cube((0.17*s,-0.02,0.60),(0.02,0.006,0.22),'gold',0.003,None,(0,0,0))   # side strap
    ring("knee",(0.12*s,-0.02,0.56),0.082,0.008,mat='jacket')            # knee panel seam
    ring("cinch",(0.11*s,0,0.41),0.083,0.03,mat='skate')                 # snap-tab ankle cinch
add_expressions(FACE)
build_skates()
build_inventory()
finalize()
