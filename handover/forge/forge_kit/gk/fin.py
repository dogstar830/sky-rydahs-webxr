import bpy,sys
n=sys.argv[sys.argv.index('--')+1]; G='/workspace/forge_kit/gk/'
m=bpy.data.materials[n+'_mat']; nt=m.node_tree; b=nt.nodes['Principled BSDF']
for nd in nt.nodes:
  if nd.type=='TEX_IMAGE':
    k=nd.image.name.split('_')[-1]; im=bpy.data.images.load(G+n+'_'+k+'.png'); im.colorspace_settings.name='sRGB' if k=='col' else 'Non-Color'; nd.image=im
if n=='desk':
  e=nt.nodes.new('ShaderNodeTexImage'); e.image=bpy.data.images.load(G+'desk_em.png'); nt.links.new(e.outputs[0],b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value=0.35
bpy.ops.export_scene.gltf(filepath=G+n+'_raw.glb',export_format='GLB',export_yup=True,export_apply=True,export_image_format='JPEG',export_jpeg_quality=90)
