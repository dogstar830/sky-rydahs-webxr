import bpy,math,sys
bpy.ops.wm.read_factory_settings(use_empty=True); f=sys.argv[-2]
if f.endswith('.bak-202610290442'):
    import shutil; shutil.copy(f,'/tmp/forge_sk_bak.glb'); f='/tmp/forge_sk_bak.glb'
bpy.ops.import_scene.gltf(filepath=f); sc=bpy.context.scene
for o in bpy.data.objects:
    if o.type=='MESH': print('M',o.name,len(o.data.polygons),[i.name for i in bpy.data.images])
sc.render.engine='CYCLES'; sc.cycles.samples=16; sc.render.resolution_x=600; sc.render.resolution_y=500
w=bpy.data.worlds.new('w'); sc.world=w; w.color=(1,1,1)
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera=cam; cam.data.type='ORTHO'; cam.data.ortho_scale=.6
cam.location=(1.5,0.05,0.05); cam.rotation_euler=(math.radians(90),0,math.radians(90)); sc.render.filepath=sys.argv[-1]; bpy.ops.render.render(write_still=True)
