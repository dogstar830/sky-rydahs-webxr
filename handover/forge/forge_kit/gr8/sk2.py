import bpy
from mathutils import Vector
with bpy.data.libraries.load('/workspace/skyrydahs-characters/shared/at-skate/at-skate-meshy.blend') as (s,d): d.objects=[n for n in s.objects if n.endswith('L0') or n=='Skate_LOD0']
for o in d.objects:
    bpy.context.collection.objects.link(o)
bpy.context.view_layer.update()
for o in d.objects:
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; print('SK',o.name,o.type,len(o.data.polygons) if o.type=='MESH' else '',o.parent.name if o.parent else None,[(round(min(v[i] for v in bb),3),round(max(v[i] for v in bb),3)) for i in range(3)], [m.name for m in o.data.materials] if o.type=='MESH' else '')
