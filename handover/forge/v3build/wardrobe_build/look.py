import bpy, glob, numpy as np, sys
from mathutils import Vector
files=sorted(glob.glob('/home/box/Downloads/Meshy_AI_*_10282*_texture.glb'))+['/home/box/Downloads/Meshy_AI_Thunderstride_Outlaw_20261028_part-segmentation_split.glb']
for f in files:
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=f)
    obs=[o for o in bpy.data.objects if o.type=='MESH']
    pts=np.concatenate([np.array([o.matrix_world@o.data.vertices[i].co for i in range(0,len(o.data.vertices),max(1,len(o.data.vertices)//4000))]) for o in obs])
    print('FILE',f.split('/')[-1][8:40],[ (o.name,len(o.data.polygons)) for o in obs][:9],'bb',pts.min(0).round(3),pts.max(0).round(3))
    sc=bpy.context.scene; sc.render.engine='BLENDER_WORKBENCH'; sc.display.shading.color_type='TEXTURE' if 'split' not in f else 'RANDOM'; sc.render.resolution_x=400; sc.render.resolution_y=400
    cam=bpy.data.objects.new('c',bpy.data.cameras.new('c')); sc.collection.objects.link(cam); sc.camera=cam; cam.data.type='ORTHO'
    c=(pts.min(0)+pts.max(0))/2; cam.data.ortho_scale=float((pts.max(0)-pts.min(0)).max())*1.1; cam.location=Vector(c)+Vector((0,-5,0)); cam.rotation_euler=(1.5708,0,0)
    sc.render.filepath='/tmp/wl_'+f.split('/')[-1][8:20]+'.png'; bpy.ops.render.render(write_still=True)
