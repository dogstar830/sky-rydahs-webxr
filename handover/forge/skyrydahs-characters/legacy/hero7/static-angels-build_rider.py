# static-angels rider — per-crew config + crew-specific geometry. Shared pipeline: ../../shared/rider_lib.py
import sys; sys.path.insert(0, "/workspace/skyrydahs-characters/shared")
from rider_lib import *
CFG = {'name': 'static-angels', 'out': '/workspace/skyrydahs-characters/static-angels/', 'prefix': 'StaticAngels', 'glowpts': [('GlowPt_halo', 'head', (0, 0.03, 1.93), 0.55)]}
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
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=0.028,location=(0.037*s,-0.097,1.655)); e=bpy.context.object
    e.scale=(1.0,0.35,0.95); e.rotation_euler=(0,0,math.radians(10*s)); bpy.ops.object.transform_apply(scale=True,rotation=True); finish(e,'eyes','head')
    bpy.ops.mesh.primitive_uv_sphere_add(segments=10,ring_count=6,radius=0.018,location=(0.036*s,-0.1035,1.651)); e=bpy.context.object
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
module('hair')
# ---------- spiky hair ----------
bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=0.115,location=(0,0.012,1.675))
cap=bpy.context.object; cap.name="hairCap"
bm=bmesh.new(); bm.from_mesh(cap.data)
bmesh.ops.delete(bm,geom=[v for v in bm.verts if (v.co.y<-0.02 and v.co.z<0.05) or v.co.z<-0.07 or (v.co.y<0.03 and v.co.z<-0.01)],context='VERTS')
bm.to_mesh(cap.data); bm.free(); cap.scale=(0.95,1.05,1); bpy.ops.object.transform_apply(scale=True); finish(cap,'hair','head')
# soft swept bangs
for x,l in [(-0.07,0.09),(-0.035,0.11),(0.0,0.12),(0.035,0.11),(0.07,0.09),(-0.095,0.10),(0.095,0.10)]:
    spike(Vector((x*3.5,-0.85,0.15)),l,0.034,bend=0.55)
# crown volume (short, rounded locks)
for i in range(10):
    th=i/10*2*math.pi
    spike(Vector((math.cos(th)*0.7,math.sin(th)*0.7+0.3,0.75)),0.07,0.05,bend=0.3)
# side locks framing face
for sx in (1,-1): spike(Vector((sx*0.8,-0.45,-0.5)),0.14,0.03,bend=-0.2)
# twin tails (skin-modifier strands) + purple hair ties
for sx in (1,-1):
    pts=[(0.105*sx,0.04,1.76),(0.17*sx,0.07,1.72),(0.21*sx,0.09,1.6),(0.22*sx,0.10,1.45),(0.2*sx,0.12,1.32),(0.17*sx,0.12,1.22)]
    rr=[0.032,0.05,0.055,0.048,0.035,0.012]
    finish(skin_obj("tail",pts,[(i,i+1) for i in range(len(pts)-1)],rr),'hair','head')
    bpy.ops.mesh.primitive_torus_add(major_radius=0.028,minor_radius=0.01,major_segments=12,minor_segments=4,location=(0.125*sx,0.05,1.755),rotation=(0,math.radians(70*sx),0)); finish(bpy.context.object,'gold','head')
# HALO ring (emissive) floating above head
bpy.ops.mesh.primitive_torus_add(major_radius=0.13,minor_radius=0.009,major_segments=32,minor_segments=6,location=(0,0.03,1.93),rotation=(math.radians(-10),0,0)); finish(bpy.context.object,'glow2','head')
# earrings
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
module('accessory','wings')
# mechanical angel wings: carbon spine + 4 feather blades + LED edges, mounted on a back plate
cube((0,0.13,1.38),(0.12,0.03,0.09),'metal',0.01,'chest')
for s_ in (1,-1):
    root=Vector((0.06*s_,0.15,1.40))
    for k in range(4):
        ang=math.radians(20+k*22)
        L=0.44-0.06*k
        d=Vector((math.cos(ang)*s_*0.8,0.5,math.sin(ang)*0.9+0.2-0.25*k)).normalized()
        c=root+d*L*0.5+Vector((0,0.02*k,0))
        rot=Vector((1,0,0)).rotation_difference(d).to_euler()
        cube(tuple(c),(L,0.008,0.04),'metal',0.004,'chest',tuple(rot))
        cube(tuple(c-Vector((0,0,0.022))),(L*0.9,0.01,0.006),'glow2',0,'chest',tuple(rot))

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
module('accessory','battery')
# waist battery pack (AtmosGear-style) + cables to each skate
cube((0,0.13,0.97),(0.17,0.06,0.09),'skate',0.015)
cube((0,0.162,0.97),(0.12,0.006,0.012),'wheelGlow',0)
for s in (1,-1):
    pts=[(0.07*s,0.15,0.94),(0.17*s,0.09,0.86),(0.20*s,0.06,0.62),(0.17*s,0.08,0.46),(0.13*s,0.12,0.37)]
    finish(skin_obj("cable",pts,[(i,i+1) for i in range(len(pts)-1)],[0.007]*len(pts),0),'skate')


build_skates()
build_inventory()
finalize()
