import bpy, bmesh, math, random
from mathutils import Vector, Matrix
random.seed(7)
OUT="/workspace/skyrydahs-characters/static-angels/"
bpy.ops.wm.read_factory_settings(use_empty=True)
scn=bpy.context.scene

# ---------- palette atlas (hand-painted-ish color bands) ----------
SW={'skin':(0.80,0.58,0.44),'hair':(0.12,0.12,0.30),'jacket':(0.15,0.80,0.86),'cloth':(0.10,0.10,0.13),
    'gold':(0.62,0.25,0.95),'metal':(0.55,0.57,0.62),'skate':(0.24,0.24,0.26),'wheelGlow':(0.0,0.9,1.0),
    'glow2':(0.3,0.9,1.0),'eyes':(0.95,0.95,0.97),'iris':(0.62,0.35,0.95)}
names=list(SW.keys()); N=len(names); W=1024; H=64
img=bpy.data.images.new("static_angels_atlas",W,H)
px=[0.0]*(W*H*4)
for y in range(H):
    v=y/(H-1)
    band = 0.80 if v<0.33 else (0.92 if v<0.7 else 1.0)   # three painted bands
    for x in range(W):
        i=int(x/W*N); c=(1,1,1)
        n=1.0+0.03*math.sin(x*0.05+y*0.21)  # brush grain
        k=(y*W+x)*4
        for j in range(3): px[k+j]=max(0,min(1,c[j]*band*n))
        px[k+3]=1
img.pixels=px
img.filepath_raw=OUT+"src/atlas.png"; img.file_format='PNG'; img.save()
img.pack()
MATS={}
for nm in names:
    m=bpy.data.materials.new(nm); m.use_nodes=True
    b=m.node_tree.nodes["Principled BSDF"]
    t=m.node_tree.nodes.new("ShaderNodeTexImage"); t.image=img; t.interpolation='Closest'
    mx=m.node_tree.nodes.new("ShaderNodeMix"); mx.data_type='RGBA'; mx.blend_type='MULTIPLY'; mx.inputs[0].default_value=1
    mx.inputs[7].default_value=(*[c**2.2 for c in SW[nm]],1)
    m.node_tree.links.new(t.outputs[0],mx.inputs[6]); m.node_tree.links.new(mx.outputs[2],b.inputs["Base Color"])
    b.inputs["Roughness"].default_value=0.35 if nm in('gold','metal') else 0.8
    b.inputs["Metallic"].default_value=0.8 if nm in('gold','metal') else 0
    if nm in ('wheelGlow','glow2'):
        b.inputs["Emission Color"].default_value=(0.0,0.8,1,1); b.inputs["Emission Strength"].default_value=3
    MATS[nm]=m

PARTS=[]  # (obj, material, bone or None)
def finish(o,mat,bone=None,smooth=True):
    o.data.materials.clear(); o.data.materials.append(MATS[mat])
    for p in o.data.polygons: p.use_smooth=smooth
    PARTS.append((o,mat,bone)); return o
def apply_all(o):
    bpy.context.view_layer.objects.active=o
    for m in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=m.name)

# ---------- skin-modifier body sculpt ----------
def skin_obj(name,verts,edges,radii,subd=1):
    me=bpy.data.meshes.new(name); me.from_pydata(verts,edges,[]); o=bpy.data.objects.new(name,me)
    scn.collection.objects.link(o)
    o.modifiers.new("skin",'SKIN'); 
    for i,r in enumerate(radii):
        sv=me.skin_vertices[0].data[i]; sv.radius=r if isinstance(r,tuple) else (r,r)
    me.skin_vertices[0].data[0].use_root=True
    if subd: s=o.modifiers.new("sub",'SUBSURF'); s.levels=subd; s.render_levels=subd
    apply_all(o); return o

def mirror_pts(pts): return [(-x,y,z) for x,y,z in pts]
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
def cube(loc,sc,mat,bevel=0.01,bone=None,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc,rotation=rot); o=bpy.context.object; o.scale=sc
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        m=o.modifiers.new("b",'BEVEL'); m.width=bevel; m.segments=2; apply_all(o)
    return finish(o,mat,bone,False)
def ring(name,loc,r,h,rot=(0,0,0),mat='gold',segs=16,sc=(1,1,1),bone=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=segs,radius=r,depth=h,location=loc,rotation=rot)
    o=bpy.context.object; o.name=name; o.scale=sc; bpy.ops.object.transform_apply(scale=True)
    return finish(o,mat,bone)
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
# ---------- spiky hair ----------
bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=0.115,location=(0,0.012,1.675))
cap=bpy.context.object; cap.name="hairCap"
bm=bmesh.new(); bm.from_mesh(cap.data)
bmesh.ops.delete(bm,geom=[v for v in bm.verts if (v.co.y<-0.02 and v.co.z<0.05) or v.co.z<-0.07 or (v.co.y<0.03 and v.co.z<-0.01)],context='VERTS')
bm.to_mesh(cap.data); bm.free(); cap.scale=(0.95,1.05,1); bpy.ops.object.transform_apply(scale=True); finish(cap,'hair','head')
center=Vector((0,0.015,1.67))
def spike(dirv,length,rad,bend=0.0):
    dirv=dirv.normalized()
    base=center+dirv*0.085
    bpy.ops.mesh.primitive_cone_add(vertices=5,radius1=rad,radius2=0.0,depth=length,location=(0,0,0))
    o=bpy.context.object
    # bend: shear tip downward/back
    for vv in o.data.vertices:
        t=(vv.co.z+length/2)/length
        vv.co.x*=1.0; vv.co.y+=bend*t*t*length
        vv.co.z+=length/2
    rot=Vector((0,0,1)).rotation_difference(dirv).to_matrix().to_4x4()
    o.matrix_world=Matrix.Translation(base)@rot
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    finish(o,'hair','head',True)
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

# ---------- chains (metal links along hip + to pocket) ----------
def chain(pts,n,r=0.011):
    for i in range(n):
        t=i/(n-1); k=t*(len(pts)-1); a=int(min(k,len(pts)-2)); f=k-a
        p=pts[a].lerp(pts[a+1],f); dv=(pts[a+1]-pts[a]).normalized()
        bpy.ops.mesh.primitive_torus_add(major_radius=r,minor_radius=0.0035,major_segments=6,minor_segments=3,location=p)
        o=bpy.context.object
        q=Vector((0,0,1)).rotation_difference(dv); o.rotation_euler=q.to_euler()
        o.rotation_euler.rotate_axis('Z',math.radians(90*(i%2)))
        o.scale=(1,1.6,1) if False else (1,1,1)
        o.rotation_euler.rotate_axis('X',math.radians(90))
        bpy.ops.object.transform_apply(location=True,rotation=True); finish(o,'metal')
chain([Vector((0.06,-0.13,0.97)),Vector((0.13,-0.13,0.86)),Vector((0.17,-0.06,0.84))],12)
chain([Vector((0.16,-0.04,0.97)),Vector((0.21,0.0,0.86)),Vector((0.16,0.08,0.95))],10)

# belt
ring("belt",(0,0,0.99),0.155,0.035,mat='skate',sc=(1,0.75,1))
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,-0.118,0.99)); o=bpy.context.object; o.scale=(0.05,0.01,0.035); bpy.ops.object.transform_apply(scale=True); finish(o,'gold',None,False)

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
# ---------- gold lightning accents on jacket ----------
def bolt(pos,normal,size,flip=1):
    pts2=[(0,0.5),(0.18,0.5),(0.05,0.08),(0.22,0.08),(-0.12,-0.5),(-0.0,-0.05),(-0.18,-0.05)]
    me=bpy.data.meshes.new("bolt"); 
    bm=bmesh.new(); vs=[bm.verts.new((x*size*flip,0,y*size)) for x,y in pts2]; bm.faces.new(vs)
    bmesh.ops.triangulate(bm,faces=bm.faces[:])
    r=bmesh.ops.extrude_face_region(bm,geom=bm.faces[:]); 
    bmesh.ops.translate(bm,verts=[v for v in r['geom'] if isinstance(v,bmesh.types.BMVert)],vec=(0,0.006,0))
    bm.to_mesh(me); bm.free()
    o=bpy.data.objects.new("bolt",me); scn.collection.objects.link(o)
    rot=Vector((0,-1,0)).rotation_difference(Vector(normal).normalized()).to_matrix().to_4x4()
    o.matrix_world=Matrix.Translation(pos)@rot; bpy.context.view_layer.objects.active=o; o.select_set(True)
    bpy.ops.object.transform_apply(location=True,rotation=True); o.select_set(False)
    finish(o,'gold',None,False)
# back emblem: stylized wing (crew mark)
for s_ in (1,-1):
    for k in range(3):
        cube((0.045*s_+0.03*k*s_,0.128,1.36-0.03*k),(0.07-0.015*k,0.004,0.014),'gold',0,None,(0,math.radians(-25*s_),0))
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
# waist battery pack (AtmosGear-style) + cables to each skate
cube((0,0.13,0.97),(0.17,0.06,0.09),'skate',0.015)
cube((0,0.162,0.97),(0.12,0.006,0.012),'wheelGlow',0)
for s in (1,-1):
    pts=[(0.07*s,0.15,0.94),(0.17*s,0.09,0.86),(0.20*s,0.06,0.62),(0.17*s,0.08,0.46),(0.13*s,0.12,0.37)]
    finish(skin_obj("cable",pts,[(i,i+1) for i in range(len(pts)-1)],[0.007]*len(pts),0),'skate')

# ---------- Air Treck skates (aggressive boot + hub motors) ----------
def wheel(x,y,r,w,bn,hub=False):
    bpy.ops.mesh.primitive_cylinder_add(vertices=14,radius=r,depth=w,location=(x,y,r),rotation=(0,math.radians(90),0))
    o=bpy.context.object; m=o.modifiers.new("b",'BEVEL'); m.width=r*0.3; m.segments=2; apply_all(o); finish(o,'skate',bn)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=r*0.55,depth=w+0.004,location=(x,y,r),rotation=(0,math.radians(90),0)); finish(bpy.context.object,'metal',bn,False)
    if hub:
        for sd in (1,-1):
            bpy.ops.mesh.primitive_torus_add(major_radius=r*0.72,minor_radius=0.0045,major_segments=18,minor_segments=4,location=(x+sd*(w/2+0.001),y,r),rotation=(0,math.radians(90),0))
            finish(bpy.context.object,'wheelGlow',bn)
for s in (1,-1):
    x=0.11*s; bn="foot."+("L" if s>0 else "R")
    # anti-rocker setup: big hub-motor outer wheels, small hard middle wheels
    wheel(x,-0.145,0.038,0.03,bn,True); wheel(x,0.145,0.038,0.03,bn,True)
    wheel(x,-0.05,0.026,0.026,bn); wheel(x,0.05,0.026,0.026,bn)
    # low-profile frame with H-block groove
    for y0 in (-0.105,0.105):
        cube((x,y0,0.07),(0.056,0.15,0.05),'skate',0.008,bn)
    cube((x,0,0.082),(0.04,0.06,0.026),'metal',0.004,bn)                   # H-block
    for y in (-0.145,0.145):
        for sd in (1,-1): cube((x+sd*0.029,y,0.065),(0.004,0.014,0.014),'metal',0,bn)
    # motor controller pod on frame (outer side)
    cube((x+0.034*s,0.0,0.066),(0.012,0.07,0.03),'metal',0.004,bn)
    cube((x+0.041*s,0.0,0.066),(0.003,0.05,0.006),'wheelGlow',0,bn)
    # integrated soul plate (wide grind band)
    bpy.ops.mesh.primitive_cube_add(size=1,location=(x,-0.02,0.108)); o=bpy.context.object; o.scale=(0.125,0.37,0.03); bpy.ops.object.transform_apply(scale=True)
    m=o.modifiers.new("b",'BEVEL'); m.width=0.012; m.segments=3; apply_all(o); finish(o,'metal',bn)
    cube((x,-0.02,0.094),(0.127,0.372,0.004),'gold',0,bn)                  # soul plate accent line
    # lower shell (glossy skin), sloped toe
    bpy.ops.mesh.primitive_cube_add(size=1,location=(x,-0.035,0.165)); b=bpy.context.object
    b.scale=(0.13,0.36,0.11); bpy.ops.object.transform_apply(scale=True)
    for vv in b.data.vertices:
        if vv.co.z>0.19 and vv.co.y<-0.05: vv.co.y+=0.07; vv.co.z-=0.025
    m=b.modifiers.new("s",'SUBSURF'); m.levels=2; apply_all(b); finish(b,'skate',bn)
    # liner: tapered padded sleeve + rolled collar
    bpy.ops.mesh.primitive_cone_add(vertices=20,radius1=0.07,radius2=0.08,depth=0.2,location=(x,0.0,0.30)); c=bpy.context.object
    c.scale=(0.95,1.12,1); bpy.ops.object.transform_apply(scale=True)
    m=c.modifiers.new("s",'SUBSURF'); m.levels=1; apply_all(c); finish(c,'cloth',bn)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.078,minor_radius=0.014,major_segments=20,minor_segments=6,location=(x,0.005,0.405))
    o=bpy.context.object; o.scale=(0.95,1.12,1); bpy.ops.object.transform_apply(scale=True); finish(o,'cloth',bn)
    for k in range(3): cube((x,-0.072+0.008*k,0.235+0.035*k),(0.04,0.006,0.005),'gold',0,bn,(math.radians(-20),0,0))
    # hard cuff: tapered, forward-leaning shell, open at the front, rounded edges
    bpy.ops.mesh.primitive_cone_add(vertices=24,radius1=0.08,radius2=0.092,depth=0.17,location=(x,0.014,0.325)); c=bpy.context.object
    c.scale=(0.98,1.12,1); c.rotation_euler=(math.radians(-7),0,0); bpy.ops.object.transform_apply(scale=True,rotation=True)
    bm=bmesh.new(); bm.from_mesh(c.data)
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_center_median().y-0.014<-0.055 or abs(f.normal.z)>0.9],context='FACES')
    bm.to_mesh(c.data); bm.free()
    m=c.modifiers.new("s",'SOLIDIFY'); m.thickness=0.012; m2=c.modifiers.new("ss",'SUBSURF'); m2.levels=1; apply_all(c); finish(c,'skate',bn)
    # gold armor side plates (per Gold sheet 08 / AT-07 chassis plate)
    for sd in (1,-1):
        cube((x+sd*0.06,0.04,0.175),(0.006,0.13,0.035),'gold',0.004,bn,(math.radians(8),0,0))
        cube((x+sd*0.093,0.02,0.32),(0.006,0.07,0.09),'gold',0.004,bn,(math.radians(-7),0,0))
    for sd in (1,-1):
        bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=0.016,depth=0.008,location=(x+sd*0.098,0.015,0.27),rotation=(0,math.radians(90),0)); finish(bpy.context.object,'metal',bn,False)
    # power strap over instep + top cuff strap, buckle latches
    cube((x,-0.06,0.235),(0.135,0.035,0.016),'skate',0.004,bn,(math.radians(-35),0,0))
    cube((x+0.06*s,-0.065,0.23),(0.02,0.03,0.025),'gold',0.003,bn)
    cube((x,-0.03,0.395),(0.18,0.05,0.016),'gold',0.004,bn,(math.radians(-20),0,0))
    cube((x+0.085*s,-0.02,0.39),(0.014,0.03,0.03),'metal',0.003,bn)
    # swappable battery pod on cuff spine + LED strip, cable port
    cube((x,0.105,0.30),(0.06,0.03,0.13),'metal',0.01,bn)
    cube((x,0.121,0.30),(0.008,0.004,0.1),'wheelGlow',0,bn)
    for sd in (1,-1): cube((x+sd*0.056,-0.03,0.14),(0.004,0.16,0.008),'wheelGlow',0,bn)   # shell LED strips
# ---------- join by material ----------
merged={}
for o,mat,bone in PARTS:
    merged.setdefault(mat,[]).append((o,bone))
# store forced-bone as vertex attribute via vertex group later
BONES=[("hips",(0,0,0.95),(0,0,1.10),None),("spine",(0,0,1.10),(0,0,1.32),"hips"),("chest",(0,0,1.32),(0,0,1.47),"spine"),
 ("neck",(0,0.01,1.47),(0,0.01,1.57),"chest"),("head",(0,0.01,1.57),(0,0.01,1.80),"neck")]
for s,L in ((1,"L"),(-1,"R")):
    BONES+= [("shoulder."+L,(0.05*s,0,1.43),(0.19*s,0,1.42),"chest"),("upperarm."+L,(0.19*s,0,1.42),(0.40*s,0,1.20),"shoulder."+L),
     ("forearm."+L,(0.40*s,0,1.20),(0.59*s,0,1.03),"upperarm."+L),("hand."+L,(0.59*s,0,1.03),(0.71*s,0,0.91),"forearm."+L),
     ("thigh."+L,(0.10*s,0,0.97),(0.12*s,-0.02,0.58),"hips"),("shin."+L,(0.12*s,-0.02,0.58),(0.11*s,0,0.24),"thigh."+L),
     ("foot."+L,(0.11*s,0,0.24),(0.11*s,-0.17,0.12),"shin."+L)]
arm_d=bpy.data.armatures.new("rig"); arm=bpy.data.objects.new("StaticAngels_Rig",arm_d); scn.collection.objects.link(arm)
bpy.context.view_layer.objects.active=arm; bpy.ops.object.mode_set(mode='EDIT')
for n,h,t,p in BONES:
    b=arm_d.edit_bones.new(n); b.head=h; b.tail=t
    if p: b.parent=arm_d.edit_bones[p]; b.use_connect=False
bpy.ops.object.mode_set(mode='OBJECT')
segs=[(n,Vector(h),Vector(t)) for n,h,t,p in BONES]
def segdist(p,a,b):
    ab=b-a; t=max(0,min(1,(p-a).dot(ab)/ab.length_squared)); return (a+ab*t-p).length
total=0
for mat,lst in merged.items():
    for o,bone in lst:
        o.vertex_groups.clear()
        vgs={n:o.vertex_groups.new(name=n) for n,_,_,_ in BONES}
        for v in o.data.vertices:
            p=o.matrix_world@v.co
            if bone: vgs[bone].add([v.index],1.0,'REPLACE'); continue
            ds=sorted((segdist(p,a,b),n) for n,a,b in segs)
            (d0,n0),(d1,n1)=ds[0],ds[1]
            if d1-d0<0.04:   # soft blend near joints
                w=0.5+0.5*(d1-d0)/0.04
                vgs[n0].add([v.index],w,'REPLACE'); vgs[n1].add([v.index],1-w,'REPLACE')
            else: vgs[n0].add([v.index],1.0,'REPLACE')
    bpy.ops.object.select_all(action='DESELECT')
    for o,_ in lst: o.select_set(True)
    bpy.context.view_layer.objects.active=lst[0][0]
    bpy.ops.object.join()
    o=bpy.context.object; o.name="StaticAngels_"+mat
    # UVs: map into this material's atlas swatch, v by height (painted bands)
    i=names.index(mat); u0=(i+0.15)/N; u1=(i+0.85)/N
    zs=[v.co.z for v in o.data.vertices]; zmin,zmax=min(zs),max(zs)
    while o.data.uv_layers: o.data.uv_layers.remove(o.data.uv_layers[0])
    uv=o.data.uv_layers.new(name="UVMap")
    for l in o.data.loops:
        co=o.data.vertices[l.vertex_index].co
        n=o.data.vertices[l.vertex_index].normal
        hv=(co.z-zmin)/max(1e-5,zmax-zmin)
        v=0.15+0.7*max(0,min(1,0.5*hv+0.5*(0.5+0.5*n.z)))
        uv.data[l.index].uv=(u0+(u1-u0)*(0.5+0.5*n.x),v)
    m=o.modifiers.new("arm",'ARMATURE'); m.object=arm; o.parent=arm
    o.data.calc_loop_triangles(); total+=len(o.data.loop_triangles)
print("TRIS",total)
bpy.ops.wm.save_as_mainfile(filepath=OUT+"src/static-angels-rider.blend")
bpy.ops.export_scene.gltf(filepath=OUT+"static-angels-rider.glb",export_format='GLB',export_skins=True,export_apply=False,export_yup=True,export_image_format='WEBP' if False else 'AUTO')
