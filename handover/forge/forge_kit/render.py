import bpy,sys,math
a=sys.argv[sys.argv.index('--')+1:]; src,out,dist,tz=a[0],a[1],float(a[2]),float(a[3])
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
for m in bpy.data.materials:
    if m.use_nodes:
        b=m.node_tree.nodes.get('Principled BSDF')
        for l in list(m.node_tree.links):
            if l.to_socket==b.inputs['Emission Color']:
                mix=m.node_tree.nodes.new('ShaderNodeMix'); mix.data_type='RGBA'; mix.blend_type='MULTIPLY'; mix.inputs[0].default_value=1
                m.node_tree.links.new(l.from_socket,mix.inputs[6]); mix.inputs[7].default_value=(0,0.9,1,1)
                m.node_tree.links.new(mix.outputs[2],b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value=1.0
s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.samples=48; s.cycles.use_denoising=True; s.render.resolution_x=1000; s.render.resolution_y=750
w=bpy.data.worlds.new('w'); s.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(0.02,0.025,0.03,1); w.node_tree.nodes['Background'].inputs[1].default_value=1
bpy.ops.mesh.primitive_plane_add(size=40); p=bpy.context.object; pm=bpy.data.materials.new('f'); pm.use_nodes=True; pm.node_tree.nodes['Principled BSDF'].inputs[0].default_value=(0.03,0.03,0.035,1); pm.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=0.3; p.data.materials.append(pm)
bpy.ops.object.light_add(type='AREA',location=(dist*0.6,-dist*0.8,dist)); l=bpy.context.object; l.data.energy=60*dist*dist; l.data.size=dist; l.rotation_euler=(0.7,0,0.6)
bpy.ops.object.light_add(type='AREA',location=(-dist,dist*0.5,dist*0.6)); l=bpy.context.object; l.data.energy=20*dist*dist; l.data.color=(0.4,0.8,1); l.rotation_euler=(-0.9,-0.9,0)
bpy.ops.object.camera_add(location=(dist*0.3,-dist*1.1,dist*0.55+tz)); c=bpy.context.object; s.camera=c
cn=c.constraints.new('TRACK_TO'); bpy.ops.object.empty_add(location=(0,0,tz)); cn.target=bpy.context.object
s.view_settings.view_transform='AgX'; s.render.filepath=out; bpy.ops.render.render(write_still=True)
