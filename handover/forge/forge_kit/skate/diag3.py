import bpy,bmesh,mathutils
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath='/workspace/skyrydahs-characters/meshy/airtreck-meshy.glb')
o=[o for o in bpy.context.scene.objects if o.type=='MESH'][0]
bm=bmesh.new(); bm.from_mesh(o.data); bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=1e-5)
print('SRC tris',len(bm.faces),'boundaryE',sum(1 for e in bm.edges if e.is_boundary),'nonman',sum(1 for e in bm.edges if not e.is_manifold and not e.is_boundary))
bm.verts.ensure_lookup_table()
print('SRC bbox',[round(min(v.co[i] for v in bm.verts),3) for i in range(3)],[round(max(v.co[i] for v in bm.verts),3) for i in range(3)], 'mw',o.matrix_world.to_scale())
