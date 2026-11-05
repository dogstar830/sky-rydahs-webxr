import bpy, bmesh, math, random
from mathutils import Vector, Matrix
random.seed(7)
OUT="/workspace/skyrydahs-characters/code-e/"
bpy.ops.wm.read_factory_settings(use_empty=True)
scn=bpy.context.scene

# ---------- palette atlas (hand-painted-ish color bands) ----------
SW={'skin':(0.98,0.80,0.66),'hair':(0.13,0.12,0.20),'jacket':(0.21,0.21,0.24),'cloth':(0.20,0.19,0.30),
    'gold':(1.0,0.84,0.0),'metal':(0.55,0.57,0.62),'skate':(0.24,0.24,0.26),'wheelGlow':(1.0,0.85,0.2),
    'eyes':(0.95,0.95,0.97),'iris':(0.95,0.70,0.05)}
names=list(SW.keys()); N=len(names); W=1024; H=64
img=bpy.data.images.new("code_e_atlas",W,H)
px=[0.0]*(W*H*4)
for y in range(H):
    v=y/(H-1)
    band = 0.78 if v<0.33 else (0.92 if v<0.7 else 1.06)   # three painted bands
    for x in range(W):
        i=int(x/W*N); c=SW[names[i]]
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
    m.node_tree.links.new(t.outputs[0],b.inputs["Base Color"])
    b.inputs["Roughness"].default_value=0.35 if nm in('gold','metal') else 0.8
    b.inputs["Metallic"].default_value=0.8 if nm in('gold','metal') else 0
    if nm=='wheelGlow':
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
    s=o.modifiers.new("sub",'SUBSURF'); s.levels=subd; s.render_levels=subd
    apply_all(o); return o

def mirror_pts(pts): return [(-x,y,z) for x,y,z in pts]
# legs / pelvis (baggy pants)
for side in (1,-1):
    v=[(0.0,0,1.00),(0.10*side,0,0.97),(0.115*side,-0.01,0.78),(0.12*side,-0.02,0.58),(0.115*side,0,0.40),(0.11*side,0.0,0.27)]
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
def ring(name,loc,r,h,rot=(0,0,0),mat='gold',segs=16,sc=(1,1,1),bone=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=segs,radius=r,depth=h,location=loc,rotation=rot)
    o=bpy.context.object; o.name=name; o.scale=sc; bpy.ops.object.transform_apply(scale=True)
    return finish(o,mat,bone)
ring("hem",(0,0.005,1.0),0.16,0.035,sc=(1,0.74,1))
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
for i in range(26):
    th=random.uniform(0,2*math.pi); ph=random.uniform(0.15,1.35)
    d=Vector((math.sin(ph)*math.cos(th),math.sin(ph)*math.sin(th)*1.0,math.cos(ph)))
    if d.y<-0.35 and d.z<0.6: d.y*=0.3; d.z+=0.4
    d.y+=0.25; d.z+=0.25
    spike(d,random.uniform(0.09,0.17),random.uniform(0.03,0.045),bend=0.25)
# front bangs falling over forehead
for x,l in [(-0.06,0.10),(-0.025,0.12),(0.015,0.13),(0.055,0.10),(0.08,0.08),(-0.085,0.08)]:
    spike(Vector((x*4,-0.8,0.25)),l*0.8,0.03,bend=0.4)
# sideburn spikes
for s in (1,-1): spike(Vector((s*0.9,-0.2,-0.6)),0.09,0.025)

# ---------- chains (metal links along hip + to pocket) ----------
def chain(pts,n,r=0.011):
    for i in range(n):
        t=i/(n-1); k=t*(len(pts)-1); a=int(min(k,len(pts)-2)); f=k-a
        p=pts[a].lerp(pts[a+1],f); dv=(pts[a+1]-pts[a]).normalized()
        bpy.ops.mesh.primitive_torus_add(major_radius=r,minor_radius=0.0035,major_segments=8,minor_segments=4,location=p)
        o=bpy.context.object
        q=Vector((0,0,1)).rotation_difference(dv); o.rotation_euler=q.to_euler()
        o.rotation_euler.rotate_axis('Z',math.radians(90*(i%2)))
        o.scale=(1,1.6,1) if False else (1,1,1)
        o.rotation_euler.rotate_axis('X',math.radians(90))
        bpy.ops.object.transform_apply(location=True,rotation=True); finish(o,'metal')
chain([Vector((0.15,-0.06,0.97)),Vector((0.08,-0.135,0.86)),Vector((-0.06,-0.13,0.88)),Vector((-0.14,-0.07,0.96))],16)
chain([Vector((0.16,-0.04,0.97)),Vector((0.21,0.0,0.86)),Vector((0.16,0.08,0.95))],10)
chain([Vector((-0.06,-0.09,1.44)),Vector((0.0,-0.13,1.30)),Vector((0.06,-0.09,1.44))],12,0.009)
bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=0.022,depth=0.008,location=(0,-0.135,1.285),rotation=(math.radians(90),0,0)); finish(bpy.context.object,'gold',None,False)
# belt
ring("belt",(0,0,0.99),0.155,0.035,mat='skate',sc=(1,0.75,1))
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,-0.118,0.99)); o=bpy.context.object; o.scale=(0.05,0.01,0.035); bpy.ops.object.transform_apply(scale=True); finish(o,'gold',None,False)

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
bolt(Vector((0,0.128,1.27)),(0,1,0),0.26)          # big back bolt
bolt(Vector((0.10,-0.115,1.33)),(0.2,-1,0),0.09)    # chest
for s in (1,-1):
    bolt(Vector((0.36*s,0.0,1.26+0.0)),(s*0.7,0,0.7),0.11,s)  # sleeve bolts
    bolt(Vector((0.36*s,0.05,1.27)),(0,1,0.2),0.08,s)

# ---------- Air Treck skates ----------
def cube(loc,sc,mat,bevel=0.01,bone=None,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc,rotation=rot); o=bpy.context.object; o.scale=sc
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        m=o.modifiers.new("b",'BEVEL'); m.width=bevel; m.segments=2; apply_all(o)
    return finish(o,mat,bone,False)
for s in (1,-1):
    x=0.11*s; bn="foot."+("L" if s>0 else "R")
    # boot shell (sculpted from subdivided cube)
    bpy.ops.mesh.primitive_cube_add(size=1,location=(x,-0.03,0.19)); b=bpy.context.object
    b.scale=(0.13,0.30,0.14); bpy.ops.object.transform_apply(scale=True)
    for vv in b.data.vertices:
        if vv.co.z>0.2 and vv.co.y<0: vv.co.y+=0.10; vv.co.z-=0.03   # sloped toe
        if vv.co.y>0.08: vv.co.y-=0.02
    m=b.modifiers.new("s",'SUBSURF'); m.levels=2; apply_all(b); finish(b,'skate',bn)
    # cuff/ankle collar
    bpy.ops.mesh.primitive_cylinder_add(vertices=14,radius=0.085,depth=0.15,location=(x,0.025,0.31)); c=bpy.context.object
    c.scale=(0.95,1.05,1); bpy.ops.object.transform_apply(scale=True)
    m=c.modifiers.new("b",'BEVEL'); m.width=0.015; m.segments=2; apply_all(c); finish(c,'skate',bn)
    # straps (gold)
    for z,y in [(0.24,-0.06),(0.33,0.02),(0.38,0.02)]:
        cube((x,y,z),(0.15 if z<0.3 else 0.18,0.035,0.022),'gold',0.004,bn)
    # toe cap + heel plate metal
    cube((x,-0.17,0.155),(0.12,0.07,0.07),'metal',0.02,bn)
    # frame
    cube((x,-0.02,0.085),(0.035,0.36,0.045),'metal',0.006,bn)
    # wheels + motors + glow rings
    for i,y in enumerate((-0.16,-0.055,0.05,0.155)):
        bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=0.045,depth=0.034,location=(x,y,0.048),rotation=(0,math.radians(90),0))
        w=bpy.context.object; m=w.modifiers.new("b",'BEVEL'); m.width=0.008; m.segments=2; apply_all(w); finish(w,'skate',bn)
        for side in (1,-1):
            bpy.ops.mesh.primitive_torus_add(major_radius=0.034,minor_radius=0.006,major_segments=16,minor_segments=4,location=(x+side*0.018,y,0.048),rotation=(0,math.radians(90),0))
            finish(bpy.context.object,'wheelGlow',bn)
        bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=0.016,depth=0.05,location=(x,y,0.048),rotation=(0,math.radians(90),0)); finish(bpy.context.object,'metal',bn)
    # rear motor pod
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=0.04,depth=0.07,location=(x+0.075*s,0.10,0.15),rotation=(0,math.radians(90),0))
    o=bpy.context.object; m=o.modifiers.new("b",'BEVEL'); m.width=0.01; m.segments=2; apply_all(o); finish(o,'metal',bn)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.028,minor_radius=0.006,major_segments=12,minor_segments=4,location=(x+0.111*s,0.10,0.15),rotation=(0,math.radians(90),0)); finish(bpy.context.object,'wheelGlow',bn)
    # LED strips along boot sides
    for side in (1,-1):
        cube((x+side*0.066,-0.04,0.13),(0.006,0.2,0.012),'wheelGlow',0,bn)
    cube((x,0.105,0.24),(0.07,0.008,0.02),'wheelGlow',0,bn)

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
arm_d=bpy.data.armatures.new("rig"); arm=bpy.data.objects.new("CodeE_Rig",arm_d); scn.collection.objects.link(arm)
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
    o=bpy.context.object; o.name="CodeE_"+mat
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
bpy.ops.wm.save_as_mainfile(filepath=OUT+"src/code-e-rider.blend")
bpy.ops.export_scene.gltf(filepath=OUT+"code-e-rider.glb",export_format='GLB',export_skins=True,export_apply=False,export_yup=True,export_image_format='WEBP' if False else 'AUTO')
