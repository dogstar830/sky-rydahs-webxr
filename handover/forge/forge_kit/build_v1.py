import bpy,math,sys
from mathutils import Vector
which=sys.argv[sys.argv.index('--')+1]
bpy.ops.wm.read_factory_settings(use_empty=True)
D='/workspace/forge_kit/'
def mat():
    m=bpy.data.materials.new(which+'_mat'); m.use_nodes=True; nt=m.node_tree; b=nt.nodes['Principled BSDF']
    c=nt.nodes.new('ShaderNodeTexImage'); c.image=bpy.data.images.load(D+'pal_col.png')
    e=nt.nodes.new('ShaderNodeTexImage'); e.image=bpy.data.images.load(D+'pal_em.png')
    nt.links.new(c.outputs[0],b.inputs['Base Color']); nt.links.new(e.outputs[0],b.inputs['Emission Color'])
    b.inputs['Emission Strength'].default_value=1.0; b.inputs['Roughness'].default_value=0.35; b.inputs['Metallic'].default_value=0.1
    return m
M=mat()
def cell(o,k):
    x,y=k%4,k//4; u=(x+.5)/4; v=1-(y+.5)/4
    me=o.data
    if not me.uv_layers: me.uv_layers.new()
    for l in me.uv_layers[0].data: l.uv=(u,v)
    me.materials.clear(); me.materials.append(M)
def fin(o,k,name=None,smooth=True):
    bpy.context.view_layer.objects.active=o; o.select_set(True)
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    if smooth: bpy.ops.object.shade_smooth()
    o.select_set(False); cell(o,k)
    if name: o.name=name
    return o
def cyl(r,d,loc,rot=(0,0,0),v=32,k=0,sc=(1,1,1),cap='NGON'):
    bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=d,location=loc,rotation=rot,end_fill_type=cap)
    o=bpy.context.object; o.scale=sc; return fin(o,k)
def box(s,loc,k,rot=(0,0,0),bev=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc,rotation=rot); o=bpy.context.object; o.scale=s
    fin(o,k,smooth=False)
    if bev:
        md=o.modifiers.new('b','BEVEL'); md.width=bev; md.segments=2
        bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier='b')
    return o
def tor(R,r,loc,rot,k,sc=(1,1,1),maj=40,mn=8):
    bpy.ops.mesh.primitive_torus_add(major_radius=R,minor_radius=r,major_segments=maj,minor_segments=mn,location=loc,rotation=rot)
    o=bpy.context.object; o.scale=sc; return fin(o,k)
def join(objs,name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active=objs[0]; bpy.ops.object.join(); o=bpy.context.object; o.name=name; o.data.name=name; return o
X90=(math.pi/2,0,0)
if which=='pod':
    R=0.62; L=2.1; H=0.18+R*0.92; sy=(1,1,0.92)  # capsule axis along Blender Y (front = -Y)
    parts=[]
    # shell: open-front cylinder + rounded back
    parts.append(cyl(R,L,(0,0,H),X90,48,0,sc=(1,1,.92),cap='NOTHING'))
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=12,radius=R,location=(0,L/2,H)); s=bpy.context.object; s.scale=(1,.35,.92)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='DESELECT'); bpy.ops.object.mode_set(mode='OBJECT')
    for v in s.data.vertices: v.select = v.co.y < -1e-4
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.delete(type='VERT'); bpy.ops.object.mode_set(mode='OBJECT')
    parts.append(fin(s,0))
    # interior liner (emissive), normals inward
    li=cyl(R-0.05,L-0.04,(0,0.02,H),X90,48,3,sc=(1,1,.92),cap='NOTHING')
    parts.append(cyl(R-0.05,0.01,(0,L/2-0.01,H),X90,48,3,sc=(1,1,.92)))
    bpy.context.view_layer.objects.active=li; li.select_set(True); bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.flip_normals(); bpy.ops.object.mode_set(mode='OBJECT'); li.select_set(False)
    # cut front cap of liner: remove faces facing (after flip) +Y at front
    bpy.ops.object.mode_set(mode='OBJECT')
    import bmesh
    bm=bmesh.new(); bm.from_mesh(li.data)
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_center_median().y< -L/2+0.05],context='FACES'); bm.to_mesh(li.data); bm.free()
    parts.append(li)
    # front rim (gray trim) + emissive rim strip
    parts.append(tor(R-0.02,0.05,(0,-L/2,H),X90,1,sc=(1,1,.92)))
    parts.append(tor(R-0.085,0.012,(0,-L/2-0.03,H),X90,3,sc=(1,1,.92),maj=48,mn=4))
    # mattress + pillow
    parts.append(box((R*1.5,L-0.25,0.12),(0,0.05,H-R*0.62),5,bev=0.04))
    parts.append(box((R*0.9,0.3,0.1),(0,L/2-0.35,H-R*0.62+0.1),5,bev=0.04))
    # plinth base
    parts.append(box((R*1.7,L*0.9,0.16),(0,0,0.08),2,bev=0.02))
    parts.append(box((R*1.6,0.02,0.02),(0,-L*0.45-0.005,0.09),3))
    # door: oval disc, hinged at +X side of opening, swung ~105deg outward
    hx=R-0.02; door=[]
    door.append(cyl(R-0.03,0.07,(0,0,0),X90,40,0,sc=(1,1,.92)))
    door.append(tor(R-0.11,0.01,(0,-0.036,0),X90,3,sc=(1,1,.92),maj=40,mn=4))
    door.append(box((0.18,0.03,0.05),(0,-0.05,0.25),2))
    d=join(door,'door')
    for v in d.data.vertices: v.co.x-=hx
    d.location=(hx,-L/2-0.06,H); d.rotation_euler=(0,0,math.radians(-105))
    bpy.context.view_layer.objects.active=d; d.select_set(True); bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    join(parts+[d],'pod')
else:
    parts=[]
    parts.append(box((0.16,0.22,0.07),(0,0,0.14),2,bev=0.02))
    parts.append(box((0.11,0.15,0.03),(0,0,0.19),4,bev=0.01))
    parts.append(box((0.12,0.008,0.012),(0,-0.111,0.145),3))  # emissive strip front
    parts.append(box((0.008,0.16,0.01),(0.081,0,0.14),3)); parts.append(box((0.008,0.16,0.01),(-0.081,0,0.14),3))
    parts.append(cyl(0.025,0.03,(0,-0.1,0.1),X90,12,2))  # camera
    parts.append(cyl(0.018,0.005,(0,-0.116,0.1),X90,12,3))
    P={'FL':(-1,-1),'FR':(1,-1),'BL':(-1,1),'BR':(1,1)}; a=0.17
    for n,(sx,sy) in P.items():
        x,y=sx*a,sy*a
        b=box((0.022,math.hypot(x,y),0.016),(x/2,y/2,0.15),4,rot=(0,0,math.atan2(-x,y)))
        parts+= [b, cyl(0.022,0.04,(x,y,0.16),v=12,k=2), cyl(0.024,0.006,(x,y,0.16),v=12,k=3)]
    for sx in (-1,1):
        parts.append(box((0.01,0.2,0.01),(sx*0.07,0,0.005),2))
        parts.append(box((0.008,0.008,0.1),(sx*0.07,0.06,0.055),2)); parts.append(box((0.008,0.008,0.1),(sx*0.07,-0.06,0.055),2))
    body=join(parts,'drone_body')
    bpy.ops.object.empty_add(location=(0,0,0)); root=bpy.context.object; root.name='drone'
    body.parent=root
    for n,(sx,sy) in P.items():
        x,y=sx*a,sy*a
        hub=cyl(0.008,0.012,(0,0,0),v=8,k=2)
        bl=box((0.17,0.018,0.003),(0,0,0.003),1,rot=(0,0,math.radians(15)))
        r=join([hub,bl],'rotor_'+n); r.location=(x,y,0.186); r.parent=root
bpy.ops.export_scene.gltf(filepath=D+which+'_raw.glb',export_format='GLB',export_yup=True,export_apply=True)
