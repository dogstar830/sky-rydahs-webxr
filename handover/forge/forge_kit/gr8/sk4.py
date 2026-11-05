import bpy
with bpy.data.libraries.load('/workspace/skyrydahs-characters/shared/at-skate/at-skate-meshy.blend') as (s,d): d.materials=['AT_bake']; d.objects=['ShellBlend_L0']
m=d.materials[0]
for n in m.node_tree.nodes: print('N',n.type,n.name,getattr(n,'image',None) and n.image.filepath, getattr(n,'layer_name',''), getattr(n,'uv_map',''))
for l in m.node_tree.links: print('L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
o=d.objects[0]; print('UV',[u.name for u in o.data.uv_layers],'active',o.data.uv_layers.active.name, 'col',[c.name for c in o.data.color_attributes])
import numpy as np
uv=np.array([x.uv[:] for x in o.data.uv_layers.active.data]); print('UVRANGE',uv.min(0),uv.max(0))
