import bpy,math
bpy.ops.wm.read_factory_settings(use_empty=True)
D='/workspace/forge_kit/'
W,H,T=1.56,0.88,0.028  # ~70in 16:9 screen (1.54x0.87 active)
def mat(nm,col=None,em=None,rough=.35):
    m=bpy.data.materials.new(nm); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
    if col: c=m.node_tree.nodes.new('ShaderNodeTexImage'); c.image=bpy.data.images.load(D+col); m.node_tree.links.new(c.outputs[0],b.inputs['Base Color'])
    else: b.inputs['Base Color'].default_value=(0.01,0.01,0.012,1)
    if em: b.inputs['Emission Color'].default_value=(1,1,1,1); b.inputs['Emission Strength'].default_value=em
    b.inputs['Roughness'].default_value=rough; b.inputs['Metallic'].default_value=0; return m
M=mat('tv_mat','pal_col.png',rough=.4); MS=mat('screen',em=0.6,rough=.15)
def box(s,loc,k):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.scale=s; bpy.ops.object.transform_apply(scale=True)
    x,y=k%4,k//4; u,v=(x+.5)/4,1-(y+.5)/4
    for l in o.data.uv_layers[0].data: l.uv=(u,v)
    o.data.materials.append(M); return o
# Blender: front = -Y, up = Z. TV bottom at z=0, back of bracket at y=+0.06
y0=0.0
parts=[box((W+0.02,T,H+0.02),(0,y0,(H+0.02)/2),2),              # body/bezel
       box((0.9,0.015,0.5),(0,y0+T/2+0.0075,(H+0.02)/2),4),       # rear panel bump
       box((0.6,0.02,0.04),(0,y0+T/2+0.025,(H+0.02)/2+0.18),1),     # bracket rails
       box((0.6,0.02,0.04),(0,y0+T/2+0.025,(H+0.02)/2-0.18),1),
       box((0.04,0.02,0.5),(-0.2,y0+T/2+0.045,(H+0.02)/2),1),        # wall plate uprights
       box((0.04,0.02,0.5),(0.2,y0+T/2+0.045,(H+0.02)/2),1),
       box((0.05,0.004,0.006),(0,y0-T/2-0.002,0.008),3)]            # emissive standby LED
bpy.ops.object.select_all(action='DESELECT')
for o in parts: o.select_set(True)
bpy.context.view_layer.objects.active=parts[0]; bpy.ops.object.join(); body=bpy.context.object; body.name='tv_body'; body.data.name='tv_body'
bpy.ops.mesh.primitive_plane_add(size=1,location=(0,y0-T/2-0.0015,(H+0.02)/2),rotation=(math.pi/2,0,0)); s=bpy.context.object; s.scale=(W-0.02,H-0.02,1)
bpy.ops.object.transform_apply(location=False,rotation=True,scale=True); s.name='screen'; s.data.name='screen'; s.data.materials.append(MS)
# uv 0..1 already from plane; make sure orientation upright
bpy.ops.object.empty_add(location=(0,0,0)); r=bpy.context.object; r.name='tv'
body.parent=r; s.parent=r
bpy.ops.export_scene.gltf(filepath=D+'gk/tv_raw.glb',export_format='GLB',export_yup=True,export_apply=True)
