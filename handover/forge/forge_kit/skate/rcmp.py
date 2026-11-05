import bpy,sys,math
from mathutils import Vector
a=sys.argv[sys.argv.index('--')+1:]; f,tex,out,view=a
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=f)
T={k:bpy.data.images.load(tex+s) for k,s in (('col','.png'),('mr','-mr.png'),('nrm','-normal.png'))}
for k in ('mr','nrm'): T[k].colorspace_settings.name='Non-Color'
T['col'].colorspace_settings.name='Non-Color'  # game loads LinearEncoding
for o in list(bpy.context.scene.objects):
  if o.type=='MESH' and not o.name.endswith('_L0'): o.hide_render=True
  if o.type=='MESH':
    for sl in o.material_slots:
      m=sl.material; nt=m.node_tree; b=nt.nodes['Principled BSDF']
      for l in list(nt.links):
        if l.to_node==b: nt.links.remove(l)
      n={k:nt.nodes.new('ShaderNodeTexImage') for k in T}
      for k in T: n[k].image=T[k]
      nt.links.new(n['col'].outputs[0],b.inputs['Base Color'])
      sp=nt.nodes.new('ShaderNodeSeparateColor'); nt.links.new(n['mr'].outputs[0],sp.inputs[0]); nt.links.new(sp.outputs[1],b.inputs['Roughness']); nt.links.new(sp.outputs[2],b.inputs['Metallic'])
      nm=nt.nodes.new('ShaderNodeNormalMap'); nt.links.new(n['nrm'].outputs[0],nm.inputs['Color']); nt.links.new(nm.outputs[0],b.inputs['Normal'])
      sc=nt.nodes.new('ShaderNodeSeparateColor'); nt.links.new(n['col'].outputs[0],sc.inputs[0])
      mr=nt.nodes.new('ShaderNodeMapRange'); mr.inputs[1].default_value=0.45; mr.inputs[2].default_value=0.75; nt.links.new(sc.outputs[2],mr.inputs[0])
      nt.links.new(n['col'].outputs[0],b.inputs['Emission Color']); nt.links.new(mr.outputs[0],b.inputs['Emission Strength'])
s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.samples=64; s.cycles.use_denoising=True; s.render.resolution_x=1440; s.render.resolution_y=810
w=bpy.data.worlds.new('w'); s.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(0.32,0.33,0.36,1); w.node_tree.nodes['Background'].inputs[1].default_value=1.2
bpy.ops.object.light_add(type='AREA',location=(0.6,-0.6,0.8)); L=bpy.context.object; L.data.energy=60; L.data.size=0.6; L.rotation_euler=(0.75,0,0.8)
tgt=Vector((0,0.04,0.05))
loc={'side':Vector((1.35,0.04,0.12)),'34':Vector((0.9,-0.95,0.4))}[view]
bpy.ops.object.camera_add(location=loc); c=bpy.context.object; s.camera=c; c.data.lens=70
cn=c.constraints.new('TRACK_TO'); bpy.ops.object.empty_add(location=tgt); cn.target=bpy.context.object
s.view_settings.exposure=-1.3; s.view_settings.view_transform='AgX'
s.render.filepath=out; bpy.ops.render.render(write_still=True)
