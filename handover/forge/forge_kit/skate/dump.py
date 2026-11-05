import bpy,numpy as np,sys
f,out=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=f)
P=[]
for o in bpy.context.scene.objects:
  if o.type=='MESH' and (o.name.endswith('_L0') or 'mesh0' in o.name or o.name.startswith('Mesh')):
    mw=o.matrix_world; P+= [tuple(mw@v.co) for v in o.data.vertices]; print('USE',o.name)
np.save(out,np.array(P,dtype=np.float32)); print('N',len(P))
