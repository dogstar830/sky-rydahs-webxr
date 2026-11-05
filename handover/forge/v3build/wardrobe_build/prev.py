import bpy,sys,math
from mathutils import Vector
fs=sys.argv[sys.argv.index('--')+1:]; out=fs.pop(0)
bpy.ops.wm.read_factory_settings(use_empty=True)
for f in fs: bpy.ops.import_scene.gltf(filepath=f)
for o in list(bpy.data.objects):
    if o.type=='MESH' and ('Ico' in o.name or ('LOD' in o.name and not o.name.endswith('LOD0'))): bpy.data.objects.remove(o)
if __import__('os').environ.get('POSED'):
    from mathutils import Euler
    for a in [o for o in bpy.data.objects if o.type=='ARMATURE']:
        if a.animation_data: a.animation_data_clear()
        for pb in a.pose.bones:
            n=pb.name; pb.rotation_mode='XYZ'
            if n.endswith('LeftArm') or n.endswith('RightArm'): pb.rotation_euler=(0.6,0,0.5 if 'Left' in n else -0.5)
            elif 'ForeArm' in n: pb.rotation_euler=(0,0,0.9 if 'Left' in n else -0.9)
            elif 'UpLeg' in n: pb.rotation_euler=(-0.5,0,0)
            elif n.endswith('Leg'): pb.rotation_euler=(0.8,0,0)
            elif n.endswith('Spine1'): pb.rotation_euler=(0.25,0.3,0)
    bpy.context.view_layer.update()
ms=[o for o in bpy.data.objects if o.type=='MESH']
import numpy as np
dg=bpy.context.evaluated_depsgraph_get(); P=np.array([o.matrix_world@v.co for o in ms for v in o.evaluated_get(dg).to_mesh().vertices]); a,b=P.min(0),P.max(0); c=Vector((a+b)/2); r=max(b-a)
sc=bpy.context.scene; sc.render.engine='BLENDER_EEVEE_NEXT'; sc.render.resolution_x=sc.render.resolution_y=600
w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[1].default_value=1.0
cam=bpy.data.objects.new('c',bpy.data.cameras.new('c')); sc.collection.objects.link(cam); sc.camera=cam
az=float(__import__('os').environ.get('AZ','0'))
cam.location=c+Vector((math.sin(az)*r*1.6,-math.cos(az)*r*1.6,0)); cam.rotation_euler=(math.pi/2,0,az)
l=bpy.data.objects.new('l',bpy.data.lights.new('l','SUN')); sc.collection.objects.link(l); l.rotation_euler=(.8,0,.3); l.data.energy=float(__import__('os').environ.get('EN','3'))
sc.render.filepath=out; bpy.ops.render.render(write_still=True)
