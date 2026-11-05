import bpy,sys,math
from mathutils import Vector
a=sys.argv[sys.argv.index('--')+1:]; out=a[0]; which=a[1]
for o in list(bpy.data.objects):
  if o.type=='MESH' and o.name!=which: o.hide_render=True
m=bpy.data.materials['AT_bake']; nt=m.node_tree; b=nt.nodes['Principled BSDF']
im={n.image.name:n for n in nt.nodes if n.type=='TEX_IMAGE'}
for k,n in im.items(): n.image=bpy.data.images.load('/workspace/forge_kit/skate/bake_%s.png'%k); n.image.colorspace_settings.name='sRGB' if k=='col' else 'Non-Color'
nt.links.new(im['col'].outputs[0],b.inputs['Base Color']); sp=nt.nodes.new('ShaderNodeSeparateColor'); nt.links.new(im['mr'].outputs[0],sp.inputs[0]); nt.links.new(sp.outputs[1],b.inputs['Roughness']); nt.links.new(sp.outputs[2],b.inputs['Metallic'])
nm=nt.nodes.new('ShaderNodeNormalMap'); nt.links.new(im['nrm'].outputs[0],nm.inputs['Color']); nt.links.new(nm.outputs[0],b.inputs['Normal'])
s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.samples=32; s.cycles.use_denoising=True; s.render.resolution_x=900; s.render.resolution_y=700
w=bpy.data.worlds.new('w'); s.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(0.5,0.5,0.52,1)
bpy.ops.object.camera_add(location=(0.55,-0.35,0.2)); c=bpy.context.object; s.camera=c; cn=c.constraints.new('TRACK_TO'); bpy.ops.object.empty_add(location=(0,0.04,0.04)); cn.target=bpy.context.object; c.data.lens=60
s.render.filepath=out; bpy.ops.render.render(write_still=True)
