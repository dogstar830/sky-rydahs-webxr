import bpy
from mathutils import Vector
me=bpy.data.objects['desk'].data
print('bbox',[round(min(v.co[i] for v in me.vertices),2) for i in range(3)],[round(max(v.co[i] for v in me.vertices),2) for i in range(3)])
for x0 in [i/20 for i in range(-6,6)]:
  s=[p for p in me.polygons if x0<=p.center.x<x0+.05 and p.center.z>0.62 and abs(p.normal.y)>0.5]
  if s:
    n=sum((p.normal*p.area for p in s),Vector()); print(round(x0,2),len(s),'z',round(max(p.center.z for p in s),2),'y',round(min(p.center.y for p in s),2),round(max(p.center.y for p in s),2),'n',tuple(round(v,2) for v in n.normalized()))
