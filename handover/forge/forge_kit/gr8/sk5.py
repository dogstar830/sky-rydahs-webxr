import bpy,math
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load('/workspace/skyrydahs-characters/shared/at-skate/at-skate-meshy.blend') as (s,d): d.objects=['ShellBlend_L0','Wheel_F_L0','Wheel_R_L0']
sc=bpy.context.scene
for o in d.objects:
    sc.collection.objects.link(o); o.parent=None
    m=o.data.materials[0]; nt=m.node_tree; t=[n for n in nt.nodes if n.type=='TEX_IMAGE'][0]; nt.links.new(t.outputs[0],nt.nodes['Principled BSDF'].inputs['Base Color'])
sc.render.engine='CYCLES'; sc.cycles.samples=16; sc.render.resolution_x=600; sc.render.resolution_y=500
w=bpy.data.worlds.new('w'); sc.world=w; w.color=(1,1,1)
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera=cam; cam.data.type='ORTHO'; cam.data.ortho_scale=.6
cam.location=(1.5,0.05,0.05); cam.rotation_euler=(math.radians(90),0,math.radians(90)); sc.render.filepath='/workspace/forge_kit/gr8/sk5.png'; bpy.ops.render.render(write_still=True)
