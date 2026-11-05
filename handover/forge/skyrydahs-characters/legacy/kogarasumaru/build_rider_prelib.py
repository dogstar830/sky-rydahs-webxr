import bpy, bmesh, math, random
from mathutils import Vector, Matrix
random.seed(7)
OUT="/workspace/skyrydahs-characters/kogarasumaru/"
bpy.ops.wm.read_factory_settings(use_empty=True)
scn=bpy.context.scene

# ---------- palette atlas (hand-painted-ish color bands) ----------
SW={'skin':(0.92,0.74,0.60),'hair':(0.13,0.12,0.20),'jacket':(0.21,0.21,0.24),'cloth':(0.20,0.19,0.30),
    'gold':(0.85,0.08,0.1),'metal':(0.55,0.57,0.62),'skate':(0.24,0.24,0.26),'wheelGlow':(1.0,0.12,0.1),
    'glow2':(0.3,0.9,1.0),'eyes':(0.95,0.95,0.97),'iris':(0.9,0.12,0.12)}
names=list(SW.keys()); N=len(names); W=1024; H=64
img=bpy.data.images.new("kogarasumaru_atlas",W,H)
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
        b.inputs["Emission Color"].default_value=(1,0.75,0.05,1); b.inputs["Emission Strength"].default_value=3
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
    r=[(0.15,0.11),(0.10,0.10),(0.095,0.09),(0.075,0.075),(0.085,0.08),(0.075,0.075)]
    finish(skin_obj("pants"+("L" if side>0 else "R"),v,e,r),'cloth')
# shirt torso core (visible at open jacket)
v=[(0,0,0.98),(0,0,1.15),(0,0.0,1.32),(0,0,1.45)]
finish(skin_obj("shirt",v,[(0,1),(1,2),(2,3)],[(0.13,0.09),(0.12,0.085),(0.15,0.095),(0.10,0.08)]),'cloth')
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
bpy.ops.mesh.primitive_uv_sphere_add(segments=22,ring_count=14,radius=0.105,location=(0,0,1.66))
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
# crown + back spikes
for i in range(22):
    th=random.uniform(0,2*math.pi); ph=random.uniform(0.15,1.35)
    d=Vector((math.sin(ph)*math.cos(th),math.sin(ph)*math.sin(th)*1.0,math.cos(ph)))
    if d.y<-0.35 and d.z<0.6: d.y*=0.3; d.z+=0.4
    d.y+=0.25; d.z+=0.25
    d.y+=0.5; d.z-=0.1
    spike(d,random.uniform(0.10,0.16),random.uniform(0.032,0.045),bend=0.6)
# front bangs falling over forehead
for x,l in [(-0.06,0.10),(-0.025,0.12),(0.015,0.13),(0.055,0.10),(0.08,0.08),(-0.085,0.08)]:
    spike(Vector((x*4,-0.8,0.25)),l*0.8,0.03,bend=0.4)
# sideburn spikes
for s in (1,-1): spike(Vector((s*0.9,-0.2,-0.6)),0.09,0.025)
# back tail feathers of hair at nape
for k,x in enumerate((-0.05,0,0.05)): spike(Vector((x*4,0.9,-0.5)),0.13,0.035,bend=0.2)

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
chain([Vector((0.15,-0.06,0.97)),Vector((0.08,-0.135,0.86)),Vector((-0.06,-0.13,0.88)),Vector((-0.14,-0.07,0.96))],16)
chain([Vector((0.16,-0.04,0.97)),Vector((0.21,0.0,0.86)),Vector((0.16,0.08,0.95))],10)

bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=0.022,depth=0.008,location=(0,-0.135,1.285),rotation=(math.radians(90),0,0)); finish(bpy.context.object,'gold',None,False)
# belt
ring("belt",(0,0,0.99),0.155,0.035,mat='skate',sc=(1,0.75,1))
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,-0.118,0.99)); o=bpy.context.object; o.scale=(0.05,0.01,0.035); bpy.ops.object.transform_apply(scale=True); finish(o,'gold',None,False)

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
# crow emblem on back: body + spread wings + beak (flat red pieces)
cube((0,0.128,1.27),(0.05,0.004,0.11),'gold',0,None,(0,0,0))
cube((0,0.128,1.345),(0.04,0.004,0.04),'gold',0)
for s_ in (1,-1):
    for k in range(4):
        cube((s_*(0.06+0.03*k),0.126,1.31-0.025*k),(0.07,0.004,0.016),'gold',0,None,(0,math.radians(30*s_+8*k*s_),0))
bpy.ops.mesh.primitive_cone_add(vertices=3,radius1=0.012,radius2=0,depth=0.03,location=(0.03,0.128,1.35),rotation=(0,math.radians(90),0)); finish(bpy.context.object,'gold',None,False)
# feathered shoulder cape (mantle): rows of layered blade feathers around shoulders/back
def feather(pos,dirv,L,W,mat='jacket',bone='chest'):
    me=bpy.data.meshes.new("f"); bm=bmesh.new()
    pts=[(0,0),(W*0.5,L*0.25),(W*0.35,L*0.8),(0,L),(-W*0.35,L*0.8),(-W*0.5,L*0.25)]
    vs=[bm.verts.new((x,0,-y)) for x,y in pts]; bm.faces.new(vs)
    r=bmesh.ops.extrude_face_region(bm,geom=bm.faces[:]); bmesh.ops.translate(bm,verts=[q for q in r['geom'] if isinstance(q,bmesh.types.BMVert)],vec=(0,0.006,0))
    bm.to_mesh(me); bm.free(); o=bpy.data.objects.new("feather",me); scn.collection.objects.link(o)
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
# ---------- cargo pants details ----------
for s in (1,-1):
    cube((0.175*s,-0.01,0.74),(0.035,0.11,0.12),'cloth',0.01)            # bellows cargo pocket
    cube((0.178*s,-0.01,0.80),(0.045,0.12,0.03),'cloth',0.006)           # flap
    cube((0.197*s,-0.01,0.80),(0.006,0.02,0.012),'gold',0)                # snap
    ring("strap",(0.115*s,-0.015,0.66),0.1,0.022,mat='skate',sc=(1,1,1))   # thigh webbing strap
    cube((0.115*s,-0.112,0.66),(0.035,0.012,0.03),'gold',0.003)          # buckle
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
arm_d=bpy.data.armatures.new("rig"); arm=bpy.data.objects.new("Kogarasumaru_Rig",arm_d); scn.collection.objects.link(arm)
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
    o=bpy.context.object; o.name="Kogarasumaru_"+mat
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
bpy.ops.wm.save_as_mainfile(filepath=OUT+"src/kogarasumaru-rider.blend")
bpy.ops.export_scene.gltf(filepath=OUT+"kogarasumaru-rider.glb",export_format='GLB',export_skins=True,export_apply=False,export_yup=True,export_image_format='WEBP' if False else 'AUTO')
