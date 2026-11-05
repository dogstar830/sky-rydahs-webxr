import bpy,sys
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=sys.argv[-1]); bpy.context.view_layer.update()
for o in bpy.data.objects:
    s=''
    if o.type=='MESH':
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]; s=(len(o.data.polygons),[m.name for m in o.data.materials],[(round(min(v[i] for v in bb),3),round(max(v[i] for v in bb),3)) for i in range(3)],list(o.data.attributes.keys()))
    print('SK',o.name,o.type,o.parent.name if o.parent else None,s)
for im in bpy.data.images: print('SKIMG',im.name,im.size[:])
