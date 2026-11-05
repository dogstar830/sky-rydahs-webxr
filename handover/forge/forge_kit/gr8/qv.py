import bpy,sys,math,os
b,ob,outp=sys.argv[-3:]
bpy.ops.wm.open_mainfile(filepath=b); sc=bpy.context.scene
for o in bpy.data.objects: o.hide_render=(o.name!=ob)
o=bpy.data.objects[ob]; H=max(v.co.z for v in o.data.vertices)
sc.render.engine='BLENDER_WORKBENCH'; sc.display.shading.light='STUDIO'; sc.display.shading.color_type=os.environ.get('CT','TEXTURE')
sc.render.resolution_x=700; sc.render.resolution_y=1100
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera=cam; cam.data.type='ORTHO'; cam.data.ortho_scale=H*1.05

for nm,pos,rot in (('front',(0,-5,H/2),(90,0,0)),('back',(0,5,H/2),(90,0,180)),('q',(3.5,-3.5,H/2),(90,0,45))):
    cam.location=pos; cam.rotation_euler=[math.radians(a) for a in rot]; sc.render.filepath=f'{outp}_{nm}.png'; bpy.ops.render.render(write_still=True)
