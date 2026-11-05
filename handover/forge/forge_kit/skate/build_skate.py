import bpy,bmesh,math,numpy as np
from mathutils import Vector,Matrix
G='/workspace/forge_kit/skate/'
import sys
VOXS=float(sys.argv[sys.argv.index('--')+1]); MINISL=float(sys.argv[sys.argv.index('--')+2])
X=np.load(G+'xf.npz'); s=float(X['s']); R=X['R']; t=X['t']
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath='/workspace/skyrydahs-characters/meshy/airtreck-meshy.glb')
hi=[o for o in bpy.context.scene.objects if o.type=='MESH'][0]; hi.name='hi'
bm=bmesh.new(); bm.from_mesh(hi.data)
bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.x>=0],context='VERTS')
M=Matrix([[*(s*R[i]),t[i]] for i in range(3)]+[[0,0,0,1]]); bm.transform(M)
bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=1e-6)
# wheels
W={'F':[Vector((0,-0.0895,-0.0425)),0.0725,0.006,0.032],'R':[Vector((0,0.1715,-0.0485)),0.0685,0.006,0.032]}
dele=[]
for f in bm.faces:
  for k,(c,r,xc,hw) in W.items():
    cc=f.calc_center_median(); ok=math.hypot(cc.y-c.y,cc.z-c.z)<r+0.004 and abs(cc.x-xc)<hw+0.004 and cc.z<c.z+0.05
    if ok: dele.append(f); break
bmesh.ops.delete(bm,geom=dele,context='FACES'); print('CUT faces',len(dele))
bm.to_mesh(hi.data); bm.free(); hi.matrix_world=Matrix.Identity(4)
np.save(G+'wheels.npy',np.array([[*W[k][0],W[k][1],W[k][2],W[k][3]] for k in 'FR']))
# low shell
def sel(o):
  for x in bpy.context.scene.objects: x.select_set(x==o)
  bpy.context.view_layer.objects.active=o
lo=hi.copy(); lo.data=hi.data.copy(); bpy.context.collection.objects.link(lo); lo.name='shell0'; sel(lo)
if VOXS>0:
  pass
print('VOX',len(lo.data.polygons))
bm=bmesh.new(); bm.from_mesh(lo.data); print('PRE bnd',sum(1 for e in bm.edges if e.is_boundary),'nonman',sum(1 for e in bm.edges if not e.is_manifold)); bm.free()
md=lo.modifiers.new('d','DECIMATE'); md.ratio=7200/sum(len(p.vertices)-2 for p in lo.data.polygons); md.use_collapse_triangulate=True; bpy.ops.object.modifier_apply(modifier='d')
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.quads_convert_to_tris(); bpy.ops.mesh.normals_make_consistent(inside=False)
while lo.data.uv_layers:
  bpy.ops.object.mode_set(mode='OBJECT'); lo.data.uv_layers.remove(lo.data.uv_layers[0]); bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.object.mode_set(mode='OBJECT'); lo.data.uv_layers.new(name='UVMap'); bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=0.003,area_weight=0.0)
bpy.ops.object.mode_set(mode='OBJECT'); bpy.ops.object.shade_smooth()
V0=72/1024  # reserve bottom strip for wheel palette
for l in lo.data.uv_layers[0].data: l.uv=(l.uv[0], V0+l.uv[1]*(1-V0))
print('LO0',len(lo.data.polygons))
# bake
Rz=1024
def mk(n,nc):
  i=bpy.data.images.new(n,Rz,Rz,alpha=False); i.colorspace_settings.name='Non-Color' if nc else 'sRGB'; return i
I={'col':mk('col',0),'mr':mk('mr',1),'nrm':mk('nrm',1)}
lm=bpy.data.materials.new('AT_bake'); lm.use_nodes=True; lt=lm.node_tree; T={k:lt.nodes.new('ShaderNodeTexImage') for k in I}
for k in I: T[k].image=I[k]
lo.data.materials.clear(); lo.data.materials.append(lm)
m=hi.material_slots[0].material; nt=m.node_tree; b=nt.nodes['Principled BSDF']
def src(sock):
  for l in nt.links:
    if l.to_socket==sock: return l.from_node
col=src(b.inputs['Base Color']); nmn=src(b.inputs['Normal']); nimg=src(nmn.inputs['Color'])
orm=[n for n in nt.nodes if n.type=='TEX_IMAGE' and n not in (col,nimg)][0]
sc=bpy.context.scene; sc.render.engine='CYCLES'; sc.cycles.samples=1
bk=sc.render.bake; bk.use_selected_to_active=True; bk.cage_extrusion=0.004; bk.max_ray_distance=0.02; bk.margin=4
for o in bpy.context.scene.objects: o.select_set(o in (hi,lo))
bpy.context.view_layer.objects.active=lo
def bake(k,typ):
  for kk in T: T[kk].select=False
  lt.nodes.active=T[k]; T[k].select=True
  bpy.ops.object.bake(type=typ) ; I[k].filepath_raw=G+'bake_'+k+'.png'; I[k].file_format='PNG'; I[k].save(); print('BAKED',k)
bake('nrm','NORMAL')
em=nt.nodes.new('ShaderNodeEmission'); nt.links.new(em.outputs[0],nt.nodes['Material Output'].inputs['Surface'])
nt.links.new(col.outputs[0],em.inputs[0]); bake('col','EMIT')
nt.links.new(orm.outputs[0],em.inputs[0]); bake('mr','EMIT')
bpy.data.objects.remove(hi,do_unlink=True)
# LOD1/2 from LOD0 (UVs preserved by collapse)
for i,tg in ((1,2200),(2,560)):
  o=lo.copy(); o.data=lo.data.copy(); bpy.context.collection.objects.link(o); o.name='shell%d'%i; sel(o)
  md=o.modifiers.new('d','DECIMATE'); md.ratio=tg/len(lo.data.polygons); md.use_collapse_triangulate=True; bpy.ops.object.modifier_apply(modifier='d'); print('LO%d'%i,len(o.data.polygons))
bpy.ops.wm.save_as_mainfile(filepath=G+'skate_v2_work.blend')
