import bpy,numpy as np
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath='/workspace/skyrydahs-characters/wardrobe/skates/at-skate-meshy.glb')
for n in ['Wheel_F_L0','Wheel_R_L0','ShellBlend_L0']:
  o=bpy.data.objects[n]; P=np.array([tuple(o.matrix_world@v.co) for v in o.data.vertices]); c=np.array(o.matrix_world.translation)
  r=np.hypot(P[:,1]-c[1],P[:,2]-c[2])
  print(n,'c',c.round(4),'x',P[:,0].min().round(3),P[:,0].max().round(3),'r50/95/max',np.percentile(r,[50,95,100]).round(4),'z',P[:,2].min().round(3),P[:,2].max().round(3),'y',P[:,1].min().round(3),P[:,1].max().round(3))
