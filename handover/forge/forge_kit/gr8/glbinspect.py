import bpy,sys
from mathutils import Vector
f=sys.argv[-1]
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=f)
for o in bpy.data.objects:
    print('OBJ',o.name,o.type,o.parent.name if o.parent else None, tuple(round(x,3) for x in o.scale))
    if o.type=='MESH':
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        print('  faces',len(o.data.polygons),'verts',len(o.data.vertices),'mats',[m.name for m in o.data.materials],'uv',len(o.data.uv_layers))
        for i in range(3): print('  ax',i,round(min(v[i] for v in bb),3),round(max(v[i] for v in bb),3))
for im in bpy.data.images: print('IMG',im.name,im.size[:])
for m in bpy.data.materials:
    if m.node_tree:
        for l in m.node_tree.links: print('LINK',m.name,l.from_node.name,'->',l.to_node.name,l.to_socket.name)
