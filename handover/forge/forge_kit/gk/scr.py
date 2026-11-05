import bpy,json
me=bpy.data.objects['desk'].data; uv=me.uv_layers.active.data; out=[]
for p in me.polygons:
  c=p.center
  if p.normal.y<-0.7 and 0.13<c.y<0.21 and -0.27<c.x<0.09 and 0.56<c.z<0.77:
    out.append([[uv[i].uv[0],uv[i].uv[1]] for i in p.loop_indices])
print('SCREENFACES',len(out),sum(p.area for p in me.polygons if 0))
json.dump(out,open('/workspace/forge_kit/gk/screen_uv.json','w'))
