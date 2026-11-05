# kogarasumaru rider — per-crew config + crew-specific geometry. Shared pipeline: ../../shared/rider_lib.py
import sys; sys.path.insert(0, "/workspace/skyrydahs-characters/shared")
from rider_lib import *
import rider_lib as RL
from hero_face import *
CFG = {'name': 'kogarasumaru', 'out': '/workspace/skyrydahs-characters/kogarasumaru/', 'prefix': 'Kogarasumaru', 'glowpts': [('GlowPt_visor', 'head', (0, -0.2, 1.725), 0.15)], 'painted': True, 'bake': True, 'bulk': (0.96, 0.97)}
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
FACE = hero_head(dict(jaw=0.45, chin=0.004, nose=1.1, width=0.89, eye=dict(w=1.2, h=0.46, rot=16, iris=0.85, lash=1.1, flick=1.3), brow=dict(inner=1.682, mid=1.693, outer=1.697, thick=1.1)))
module('accessory','visor')
# beak-visor goggles pushed up on forehead: band + single wraparound visor tapering to a beak point
bpy.ops.mesh.primitive_torus_add(major_radius=0.113,minor_radius=0.008,major_segments=28,minor_segments=4,location=(0,0.012,1.712),rotation=(math.radians(-12),0,0))
g=bpy.context.object; g.scale=(0.93,1.04,1.6); bpy.ops.object.transform_apply(scale=True); finish(g,'skate','head')
bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,radius=0.122,location=(0,0.0,1.725)); v=bpy.context.object
bm=bmesh.new(); bm.from_mesh(v.data)
bmesh.ops.delete(bm,geom=[q for q in bm.verts if q.co.y>-0.02 or abs(q.co.z)>0.03],context='VERTS')
for q in bm.verts:
    t=max(0,(-q.co.y-0.06)/0.06)*max(0,1-abs(q.co.x)/0.08)
    q.co.y-=0.08*t*t  # pull centre forward into a beak
bm.to_mesh(v.data); bm.free(); v.scale=(0.95,1,1.0); bpy.ops.object.transform_apply(scale=True)
m=v.modifiers.new("s",'SOLIDIFY'); m.thickness=0.006; apply_all(v); finish(v,'skate','head')
bpy.ops.mesh.primitive_cone_add(vertices=4,radius1=0.03,radius2=0,depth=0.075,location=(0,-0.225,1.722),rotation=(math.radians(90),0,math.radians(45)))
o=bpy.context.object; o.scale=(1,0.45,1); bpy.ops.object.transform_apply(scale=True); finish(o,'gold','head',False)
# red visor lens strip
bpy.ops.mesh.primitive_torus_add(major_radius=0.124,minor_radius=0.006,major_segments=24,minor_segments=4,location=(0,0.0,1.725)); o=bpy.context.object
bm=bmesh.new(); bm.from_mesh(o.data); bmesh.ops.delete(bm,geom=[q for q in bm.verts if q.co.y>-0.04],context='VERTS'); bm.to_mesh(o.data); bm.free(); o.scale=(0.95,1,1); bpy.ops.object.transform_apply(scale=True); finish(o,'glow2','head')
module('hair')
# black crow-crest: back-swept spiky clumps, long "tail-feather" locks at the nape, sharp short bangs
hair_cap(0.03)
bangs([(-0.04,0.075,-0.35),(-0.012,0.085,-0.05),(0.016,0.08,0.15),(0.045,0.07,0.4),(0.07,0.06,0.6)],0.03,0.011)
rnd=random.Random(9)
for i in range(16):
    az=math.radians(rnd.uniform(-80,80)); el=math.radians(rnd.uniform(35,70))
    d=Vector((math.cos(el)*math.sin(az),-math.cos(el)*math.cos(az)*0.5,math.sin(el)))
    clump(d,Vector((d.x*0.6,0.9,0.35)),rnd.uniform(0.13,0.18),0.05,0.016,bend=Vector((0,0.1,-0.15)))
for i in range(10):
    az=math.radians(rnd.uniform(100,260)); el=math.radians(rnd.uniform(-20,25))
    d=Vector((math.sin(az)*math.cos(el),-math.cos(az)*math.cos(el),math.sin(el)))
    clump(d,d*0.6+Vector((0,0.5,-0.7)),rnd.uniform(0.12,0.2),0.045,0.014,bend=Vector((0,0.15,-0.1)))
for s in (1,-1): clump(Vector((0.85*s,-0.35,0.3)),Vector((0.2*s,-0.2,-1)),0.09,0.026,0.01,bend=Vector((0,0,-0.1)))
module('accessory','chains')
# ---------- chains (metal links along hip + to pocket) ----------
chain([Vector((0.15,-0.06,0.97)),Vector((0.08,-0.135,0.86)),Vector((-0.06,-0.13,0.88)),Vector((-0.14,-0.07,0.96))],16)
chain([Vector((0.16,-0.04,0.97)),Vector((0.21,0.0,0.86)),Vector((0.16,0.08,0.95))],10)

bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=0.022,depth=0.008,location=(0,-0.135,1.285),rotation=(math.radians(90),0,0)); finish(bpy.context.object,'gold',None,False)
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
cube((-0.1,-0.122,1.36),(0.045,0.01,0.022),'gold',0.004)
module('accessory','emblem')
# ---------- gold lightning accents on jacket ----------
# crow emblem on back: body + spread wings + beak (flat red pieces)
cube((0,0.128,1.27),(0.05,0.004,0.11),'gold',0,None,(0,0,0))
cube((0,0.128,1.345),(0.04,0.004,0.04),'gold',0)
for s_ in (1,-1):
    for k in range(4):
        cube((s_*(0.06+0.03*k),0.126,1.31-0.025*k),(0.07,0.004,0.016),'gold',0,None,(0,math.radians(30*s_+8*k*s_),0))
bpy.ops.mesh.primitive_cone_add(vertices=3,radius1=0.012,radius2=0,depth=0.03,location=(0.03,0.128,1.35),rotation=(0,math.radians(90),0)); finish(bpy.context.object,'gold',None,False)
module('accessory','cape')
# feathered shoulder cape (mantle): rows of layered blade feathers around shoulders/back
def feather(pos,dirv,L,W,mat='jacket',bone='chest'):
    me=bpy.data.meshes.new("f"); bm=bmesh.new()
    pts=[(0,0),(W*0.5,L*0.25),(W*0.35,L*0.8),(0,L),(-W*0.35,L*0.8),(-W*0.5,L*0.25)]
    vs=[bm.verts.new((x,0,-y)) for x,y in pts]; bm.faces.new(vs)
    r=bmesh.ops.extrude_face_region(bm,geom=bm.faces[:]); bmesh.ops.translate(bm,verts=[q for q in r['geom'] if isinstance(q,bmesh.types.BMVert)],vec=(0,0.006,0))
    bm.to_mesh(me); bm.free(); o=bpy.data.objects.new("feather",me); bpy.context.scene.collection.objects.link(o)
    o.matrix_world=Matrix.Translation(pos)@dirv; bpy.context.view_layer.objects.active=o; o.select_set(True)
    bpy.ops.object.transform_apply(location=True,rotation=True); o.select_set(False); finish(o,mat,bone,False)
for row in range(3):
    n=13-row*2; rad=0.17+row*0.025; z=1.47-row*0.06
    for i in range(n):
        th=math.radians(-150+300*i/(n-1))   # wrap around back and shoulders, open at the front
        x=math.sin(th)*rad*1.25; y=math.cos(th)*rad*0.85
        if y<-0.05 and abs(x)<0.11: continue
        rot=(Matrix.Rotation(-th,4,'Z')@Matrix.Rotation(math.radians(28+row*8),4,'X'))
        feather(Vector((x,y+0.01,z)),rot,0.16+row*0.03,0.07,'gold' if (row==2 and i%3==1) else 'jacket')
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


add_expressions(FACE)
build_skates()
build_inventory()
finalize()
