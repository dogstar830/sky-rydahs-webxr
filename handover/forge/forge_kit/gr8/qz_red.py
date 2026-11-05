import bpy,sys,math
bl,ob,outp,z,sz=sys.argv[-5:]; z=float(z); sz=float(sz)
bpy.ops.wm.open_mainfile(filepath=bl); sc=bpy.context.scene
for o in bpy.data.objects: o.hide_render=(o.name!=ob)
m=bpy.data.objects[ob].data.materials[0]; nt=m.node_tree
for n in nt.nodes:
    if n.type=='TEX_IMAGE' and n.image.colorspace_settings.name=='Non-Color' and 'orm' in n.image.name:
        for l in list(n.outputs[0].links): nt.links.remove(l)
sc.render.engine='CYCLES'; sc.cycles.samples=16; sc.render.resolution_x=800; sc.render.resolution_y=500
w=bpy.data.worlds.new('w'); sc.world=w; w.color=(1,0,0)
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera=cam; cam.data.type='ORTHO'; cam.data.ortho_scale=sz
cam.location=(1.2,-2.5,z); cam.rotation_euler=(math.radians(90),0,math.radians(25)); sc.render.filepath=outp; bpy.ops.render.render(write_still=True)
