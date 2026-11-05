import bpy,sys,math,mathutils
a=sys.argv[sys.argv.index('--')+1:]; src,out=a[0],a[1]; tex=a[2] if len(a)>2 else ''
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
ms=[o for o in bpy.context.scene.objects if o.type=='MESH']
if tex:
  for o in ms:
    for sl in o.material_slots:
      m=sl.material; nt=m.node_tree; b=nt.nodes['Principled BSDF']; t=nt.nodes.new('ShaderNodeTexImage'); t.image=bpy.data.images.load(tex); nt.links.new(t.outputs[0],b.inputs['Base Color'])
pts=[o.matrix_world@mathutils.Vector(c) for o in ms for c in o.bound_box]
mn=mathutils.Vector([min(p[i] for p in pts) for i in range(3)]); mx=mathutils.Vector([max(p[i] for p in pts) for i in range(3)]); c=(mn+mx)/2; r=(mx-mn).length
print('BBOX',[round(x,3) for x in mn],[round(x,3) for x in mx])
s=bpy.context.scene; s.render.engine='BLENDER_WORKBENCH'; s.render.resolution_x=1200; s.render.resolution_y=600
s.display.shading.light='STUDIO'; s.display.shading.color_type='TEXTURE' if tex or True else 'MATERIAL'
for i,(dx,dy) in enumerate([(1,0),(0.7,-0.7)]):
  pass
bpy.ops.object.camera_add(location=c+mathutils.Vector(tuple(float(x) for x in (a[3] if len(a)>3 else "1.2,0,0.15").split(",")))*r); cam=bpy.context.object; s.camera=cam
cn=cam.constraints.new('TRACK_TO'); bpy.ops.object.empty_add(location=c); cn.target=bpy.context.object
cam.data.type='ORTHO'; cam.data.ortho_scale=r*1.05
s.render.filepath=out; bpy.ops.render.render(write_still=True)
