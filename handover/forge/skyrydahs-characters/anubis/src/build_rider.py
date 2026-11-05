# anubis rider — per-crew config + crew-specific geometry. Shared pipeline: ../../shared/rider_lib.py
import sys; sys.path.insert(0, "/workspace/skyrydahs-characters/shared")
from rider_lib import *
import rider_lib as RL
import hero_face as HF
CFG = {'name': 'anubis', 'out': '/workspace/skyrydahs-characters/anubis/', 'prefix': 'Anubis', 'glowpts': [('GlowPt_eyes', 'head', (0, -0.15, 1.685), 0.18)], 'lod2_accessory': True, 'painted': True, 'bake': True, 'bulk': (1.06, 1.04)}
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
    finish(h,'skate')
    cube(tuple(w+d*0.62+Vector((0,-0.025,0))),(0.05,0.012,0.03),'metal',0,'hand.'+('L' if s>0 else 'R'),(0,math.radians(-45*s),0))   # knuckle plate
    cube(tuple(w+d*0.3+Vector((0,-0.03,0))),(0.03,0.006,0.008),'glow2',0,'hand.'+('L' if s>0 else 'R'),(0,math.radians(-45*s),0))
    th=skin_obj("thumb",[tuple(w+d*0.2+Vector((0,-0.03,0))),tuple(w+d*0.55+Vector((0,-0.045,0)))],[(0,1)],[0.014,0.012]); finish(th,'skate')
    ring("glove",tuple(w+d*0.12),0.04,0.04,rot=(0,math.radians(-45*s),0),mat='skate')

module('hair')
# ---------- jackal full-face helmet (hard shell + visor + chin bar, per UN R22 anatomy) ----------
bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=14,radius=0.122,location=(0,0.01,1.675))
h=bpy.context.object; h.scale=(0.88,1.05,1.05); bpy.ops.object.transform_apply(scale=True); finish(h,'skate','head')
tcube((0,-0.13,1.635),(0.11,0.17,0.085),'skate','head',(0.45,0.55))          # snout / chin bar
tcube((0,-0.215,1.645),(0.03,0.03,0.025),'metal','head',(1,1),1)             # nose tip
tcube((0,-0.11,1.70),(0.11,0.07,0.05),'skate','head',(0.7,0.8))              # brow ridge
for s in (1,-1):
    # tall jackal ears: flattened pyramids, glowing inner strip
    bpy.ops.mesh.primitive_cone_add(vertices=4,radius1=0.05,radius2=0.0,depth=0.18,location=(0.065*s,0.03,1.84),rotation=(math.radians(-8),math.radians(14*s),math.radians(45)))
    e=bpy.context.object; e.scale=(1,0.45,1); bpy.ops.object.transform_apply(scale=True); finish(e,'skate','head',False)
    bpy.ops.mesh.primitive_cone_add(vertices=3,radius1=0.022,radius2=0.0,depth=0.12,location=(0.066*s,0.012,1.83),rotation=(math.radians(-8),math.radians(14*s),0))
    e=bpy.context.object; e.scale=(1,0.3,1); bpy.ops.object.transform_apply(scale=True); finish(e,'glow2','head',False)
    # cheek vents + side teal panel
    for k in range(3): cube((0.085*s,-0.08+0.02*k,1.61),(0.008,0.006,0.03),'metal',0,'head')
    cube((0.104*s,0.02,1.67),(0.006,0.07,0.035),'gold',0.003,'head')
cube((0,-0.08,1.755),(0.012,0.12,0.008),'gold',0,'head',(math.radians(20),0,0))   # crest stripe
bpy.ops.mesh.primitive_torus_add(major_radius=0.075,minor_radius=0.018,major_segments=16,minor_segments=5,location=(0,0.01,1.545)); finish(bpy.context.object,'cloth','head')

module('body')
# LED optics (sheet 09 cyan optics): emissive 'iris' flats on the visor carry the 8 expression morphs (blink/angry/... read as LED shape changes)
ANU=[]
for s in (1,-1):
    pts=[(-0.028*s,-0.009),(0.026*s,-0.002),(0.024*s,0.011),(-0.024*s,0.005)]
    if s<0: pts=pts[::-1]
    ANU.append((HF.flat("ledEye",pts,'iris',(0.047*s,-0.153,1.685),(0,0,-16*s),'head',0.004),'eye',1.685))
    ANU.append((HF.flat("ledBrow",HF.stroke((0.018*s,0.0),(0.07*s,0.006),0.005),'iris',(0,-0.15,1.712),(0,0,0),'head',0.003),'brow',1.685))
mo=HF.flat("ledMouth",[(-0.026,-0.0012),(0.026,-0.0012),(0.026,0.0012),(-0.026,0.0012)],'iris',(0,-0.205,1.622),(0,0,0),'head',0.003)
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
    cube((0.05*s,-0.116,1.24),(0.006,0.005,0.38),'metal',0)
    cube((0.043*s,-0.11,1.24),(0.005,0.004,0.38),'gold',0)
    cube((0.105*s,-0.112,1.07),(0.075,0.02,0.07),'jacket',0.006)       # lower flap pocket
    cube((0.105*s,-0.124,1.10),(0.08,0.012,0.022),'jacket',0.004)      # flap
    cube((0.105*s,-0.13,1.10),(0.012,0.004,0.01),'gold',0)             # snap
# sleeve utility zip pocket on left upper arm
cube((0.30,-0.045,1.33),(0.06,0.02,0.08),'jacket',0.006,None,(0,math.radians(-45),math.radians(-10)))
cube((0.302,-0.058,1.355),(0.05,0.006,0.008),'gold',0,None,(0,math.radians(-45),math.radians(-10)))
# rib-knit waistband over hem
for k in range(3): ring("rib",(0,0.005,0.985+k*0.016),0.158,0.012,mat='jacket',sc=(1,0.76,1))
# chest oxygen-tab (MA-1 nod)

module('accessory','emblem')
# ---------- gold lightning accents on jacket ----------
module('accessory','chestplate')
# ---------- segmented hard-shell armor (Leatt-style multi-plate, lamellar lames) ----------
cube((0,-0.125,1.34),(0.24,0.035,0.17),'skate',0.02,'chest',(math.radians(-6),0,0))       # chest plate
cube((0,-0.145,1.36),(0.08,0.01,0.05),'gold',0.004,'chest')                               # teal core panel
cube((0,-0.152,1.36),(0.03,0.006,0.02),'glow2',0,'chest')
for k in range(3): cube((0,-0.118+0.004*k,1.225-0.045*k),(0.2-0.015*k,0.03,0.035),'skate',0.008,'spine')   # ab lames
module('accessory','backplate')
cube((0,0.13,1.30),(0.22,0.05,0.24),'skate',0.02,'chest')                                 # back protector / booster
for s in (1,-1):
    cube((0.07*s,0.17,1.33),(0.035,0.05,0.2),'metal',0.01,'chest')                         # thruster pods
    cube((0.07*s,0.197,1.33),(0.012,0.004,0.16),'glow2',0,'chest')
    module('accessory','pauldrons')
    for k in range(3):                                                                    # pauldron lames
        cube((0.2*s+0.035*k*s,0.005,1.45-0.035*k),(0.13-0.015*k,0.15,0.03),'skate',0.01,'shoulder.'+('L' if s>0 else 'R'),(0,math.radians(-35*s),0))
    cube((0.24*s,-0.07,1.40),(0.03,0.006,0.02),'gold',0,'shoulder.'+('L' if s>0 else 'R'),(0,math.radians(-35*s),0))
    module('accessory','vambraces')
    # vambrace (forearm) + elbow cop
    bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=0.066,depth=0.13,location=(0.49*s,0.005,1.135),rotation=(0,math.radians(-45*s),0))
    finish(bpy.context.object,'skate','forearm.'+('L' if s>0 else 'R'),False)
    cube((0.49*s+0.03*s,-0.055,1.135+0.03),(0.06,0.006,0.012),'glow2',0,'forearm.'+('L' if s>0 else 'R'),(0,math.radians(-45*s),0))
    cube((0.42*s,0.04,1.20),(0.07,0.05,0.05),'skate',0,'upperarm.'+('L' if s>0 else 'R'),(0,math.radians(-45*s),0))
    module('accessory','legguards')
    # knee cop + shin guard
    bpy.ops.mesh.primitive_uv_sphere_add(segments=10,ring_count=6,radius=0.06,location=(0.12*s,-0.075,0.58)); o=bpy.context.object
    o.scale=(1,0.6,1); bpy.ops.object.transform_apply(scale=True); finish(o,'skate','shin.'+('L' if s>0 else 'R'))
    cube((0.12*s,-0.078,0.465),(0.09,0.03,0.13),'skate',0.012,'shin.'+('L' if s>0 else 'R'))
    cube((0.12*s,-0.095,0.465),(0.012,0.006,0.09),'glow2',0,'shin.'+('L' if s>0 else 'R'))
    # thigh plate
    cube((0.16*s,-0.06,0.78),(0.07,0.03,0.14),'skate',0.012,'thigh.'+('L' if s>0 else 'R'),(0,0,math.radians(-5*s)))
module('body')
# ---------- cargo pants details ----------
for s in (1,-1):
    cube((0.175*s,-0.01,0.74),(0.035,0.11,0.12),'cloth',0.01)            # bellows cargo pocket
    cube((0.178*s,-0.01,0.80),(0.045,0.12,0.03),'cloth',0.006)           # flap
    cube((0.197*s,-0.01,0.80),(0.006,0.02,0.012),'gold',0)                # snap
    ring("strap",(0.115*s,-0.015,0.66),0.1,0.022,mat='skate',sc=(1,1,1))   # thigh webbing strap
    cube((0.115*s,-0.112,0.66),(0.035,0.012,0.03),'gold',0.003)          # buckle
    ring("knee",(0.12*s,-0.02,0.56),0.082,0.008,mat='jacket')            # knee panel seam
    ring("cinch",(0.11*s,0,0.41),0.083,0.03,mat='skate')                 # snap-tab ankle cinch
module('accessory','battery')
# waist battery pack (AtmosGear-style) + cables to each skate
cube((0,0.13,0.97),(0.17,0.06,0.09),'skate',0.015)
cube((0,0.162,0.97),(0.12,0.006,0.012),'wheelGlow',0)
for s in (1,-1):
    pts=[(0.07*s,0.15,0.94),(0.17*s,0.09,0.86),(0.20*s,0.06,0.62),(0.17*s,0.08,0.46),(0.13*s,0.12,0.37)]
    finish(skin_obj("cable",pts,[(i,i+1) for i in range(len(pts)-1)],[0.007]*len(pts),0),'skate')


for o,k,c in ANU: HF.add_keys(o,k,c)
HF.add_keys(mo,'mouth',1.685,1.622)
build_skates()
build_inventory()
finalize()
