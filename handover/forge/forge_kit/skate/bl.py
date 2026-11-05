import bpy
for o in bpy.data.objects: print('O',o.name,o.type,o.data.name if o.data else '',len(o.data.polygons) if o.type=='MESH' else '',tuple(round(x,4) for x in o.location),tuple(round(x,4) for x in o.rotation_euler),tuple(round(x,4) for x in o.scale),o.parent.name if o.parent else '',[m.type for m in o.modifiers], [c.name for c in o.users_collection])
for t in bpy.data.texts: print('TEXT',t.name,len(t.as_string())); 
for i in bpy.data.images: print('IMG',i.name,i.filepath,i.size[:])
