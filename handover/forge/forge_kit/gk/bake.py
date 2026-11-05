import bpy,sys,math,bmesh
from mathutils import Vector
a=sys.argv[sys.argv.index('--')+1:]; n=a[0]; axis=a[1]; size=float(a[2]); tgt=int(a[3])
G='/workspace/forge_kit/gk/'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath='/home/box/Downloads/garage-kit/'+n+'.glb')
hi=[o for o in bpy.context.scene.objects if o.type=='MESH'][0]
for o in bpy.context.scene.objects: o.select_set(o==hi)
bpy.context.view_layer.objects.active=hi
bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM'); bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
bb=[Vector(c) for c in hi.bound_box]; mn=Vector((min(v.x for v in bb),min(v.y for v in bb),min(v.z for v in bb))); mx=Vector((max(v.x for v in bb),max(v.y for v in bb),max(v.z for v in bb)))
d=mx-mn; S=size/{'x':d.x,'y':d.y,'z':d.z}[axis]
me=hi.data; c=Vector(((mn.x+mx.x)/2,(mn.y+mx.y)/2,mn.z))
for v in me.vertices: v.co=(v.co-c)*S
me.update(); print('DIMS',n,[round(x*S,3) for x in d])
# swap in edited textures
m=hi.material_slots[0].material; nt=m.node_tree
for nd in nt.nodes:
    if nd.type=='TEX_IMAGE':
        nm=nd.image.name
for nd in nt.nodes:
    if nd.type=='TEX_IMAGE':
        links=[l.to_socket.name for l in nd.outputs[0].links]+[l.to_socket.name for l in nd.outputs[1].links]
        print('TEX',nd.image.name,links)
# identify by connection
bsdf=nt.nodes['Principled BSDF']
def src(sock):
    for l in nt.links:
        if l.to_socket==sock: return l.from_node
col=src(bsdf.inputs['Base Color'])
nm_node=src(bsdf.inputs['Normal'])
orm=None
for nd in nt.nodes:
    if nd.type=='TEX_IMAGE' and nd not in (col,) and (nm_node is None or nd!=src(nm_node.inputs['Color'])): orm=nd
col.image=bpy.data.images.load(G+n+'_col_src.png'); orm.image=bpy.data.images.load(G+n+'_orm_src.png'); orm.image.colorspace_settings.name='Non-Color'
# low poly
lo=hi.copy(); lo.data=hi.data.copy(); bpy.context.collection.objects.link(lo); lo.name=n
bpy.context.view_layer.objects.active=lo
for o in bpy.context.scene.objects: o.select_set(o==lo)
VOX=float(a[6]) if len(a)>6 else 0.01
rm=lo.modifiers.new('r','REMESH'); rm.mode='VOXEL'; rm.voxel_size=VOX; rm.use_smooth_shade=True
bpy.ops.object.modifier_apply(modifier='r')
tris=sum(len(p.vertices)-2 for p in lo.data.polygons); print('VOXTRIS',tris)
md=lo.modifiers.new('d','DECIMATE'); md.ratio=tgt/tris; md.use_collapse_triangulate=True
bpy.ops.object.modifier_apply(modifier='d')
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.quads_convert_to_tris(); bpy.ops.mesh.normals_make_consistent(inside=False)
while lo.data.uv_layers: bpy.ops.object.mode_set(mode='OBJECT'); lo.data.uv_layers.remove(lo.data.uv_layers[0]); bpy.ops.object.mode_set(mode='EDIT')
lo.data.uv_layers.new(name='UVMap'); bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=0.003,area_weight=0.0)
bpy.ops.object.mode_set(mode='OBJECT'); bpy.ops.object.shade_smooth()
print('LOTRIS',n,len(lo.data.polygons))
# low material + bake targets
R=1024
def img(nm,nc): i=bpy.data.images.new(nm,R,R); 
def mk(nm,nc):
    i=bpy.data.images.new(n+'_'+nm,R,R,alpha=False); i.colorspace_settings.name='Non-Color' if nc else 'sRGB'; return i
I={'col':mk('col',0),'orm':mk('orm',1),'nrm':mk('nrm',1)}
lm=bpy.data.materials.new(n+'_mat'); lm.use_nodes=True; lt=lm.node_tree; lb=lt.nodes['Principled BSDF']
T={k:lt.nodes.new('ShaderNodeTexImage') for k in I}
for k in I: T[k].image=I[k]
lo.data.materials.clear(); lo.data.materials.append(lm)
s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.samples=1; s.cycles.device='CPU'
bk=s.render.bake; bk.use_selected_to_active=True; bk.cage_extrusion=float(a[4]) if len(a)>4 else 0.04; bk.max_ray_distance=float(a[5]) if len(a)>5 else 0.2; bk.margin=6
for o in bpy.context.scene.objects: o.select_set(o in (hi,lo))
bpy.context.view_layer.objects.active=lo
def bake(k,typ):
    for kk in T: T[kk].select=False
    lt.nodes.active=T[k]; T[k].select=True
    bpy.ops.object.bake(type=typ,normal_space='TANGENT') if typ=='NORMAL' else bpy.ops.object.bake(type=typ)
    I[k].filepath_raw=G+n+'_'+k+'.png'; I[k].file_format='PNG'; I[k].save(); print('BAKED',k)
bake('nrm','NORMAL')
em=nt.nodes.new('ShaderNodeEmission'); out=nt.nodes['Material Output']
nt.links.new(col.outputs[0],em.inputs[0]); nt.links.new(em.outputs[0],out.inputs['Surface']); bake('col','EMIT')
nt.links.new(orm.outputs[0],em.inputs[0]); bake('orm','EMIT')
# wire low material and export
nt2=lt
nt2.links.new(T['col'].outputs[0],lb.inputs['Base Color'])
sp=nt2.nodes.new('ShaderNodeSeparateColor'); nt2.links.new(T['orm'].outputs[0],sp.inputs[0]); nt2.links.new(sp.outputs[1],lb.inputs['Roughness']); nt2.links.new(sp.outputs[2],lb.inputs['Metallic'])
nmap=nt2.nodes.new('ShaderNodeNormalMap'); nt2.links.new(T['nrm'].outputs[0],nmap.inputs['Color']); nt2.links.new(nmap.outputs[0],lb.inputs['Normal'])
bpy.data.objects.remove(hi,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=G+n+'_lo.blend')
bpy.ops.export_scene.gltf(filepath=G+n+'_raw.glb',export_format='GLB',export_yup=True,export_apply=True)
print('DONE',n)
