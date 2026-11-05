import bpy,sys
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=sys.argv[-1])
bpy.context.view_layer.update()
for o in bpy.data.objects:
    if o.type=='MESH':
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]; print('MESH',o.name,[ (round(min(v[i] for v in bb),3),round(max(v[i] for v in bb),3)) for i in range(3)])
    if o.type=='ARMATURE':
        for b in ['mixamorig:Hips','mixamorig:HeadTop_End','mixamorig:LeftFoot','mixamorig:LeftHand']:
            if b in o.data.bones: print('BONE',b,[round(x,3) for x in o.matrix_world@o.data.bones[b].head_local])
