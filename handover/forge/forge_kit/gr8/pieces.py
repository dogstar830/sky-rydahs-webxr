# Tag LOD0 faces into wardrobe slots (vertex groups slot_<name>) by baked colour + height; save <n>_pieces.blend + json counts for Rigger.
import bpy,sys,json,numpy as np,colorsys
bl,ob,rider,outp=sys.argv[-4:]
bpy.ops.wm.open_mainfile(filepath=bl)
for o in list(bpy.data.objects):
    if o.name!=ob: bpy.data.objects.remove(o)
o=bpy.data.objects[ob]; me=o.data; im=[n for n in me.materials[0].node_tree.nodes if n.type=='TEX_IMAGE' and n.image.size[0]>=2048][0].image
W,H=im.size; px=np.empty(W*H*4,dtype=np.float32); im.pixels.foreach_get(px); px=px.reshape(H,W,4)
uv=me.uv_layers.active.data; wc=me.attributes['_WC'].data
def cls(p):
    u=sum(uv[i].uv.x for i in p.loop_indices)/3; v=sum(uv[i].uv.y for i in p.loop_indices)/3
    if u>.75: return 'skates'
    r,g,b=px[min(H-1,int(v*H)),min(W-1,int(u*W)),:3]; h,s,l=colorsys.rgb_to_hls(r,g,b); z=p.center.z; x=abs(p.center.x)
    if rider=='anika':
        if z>1.30 and (h<.14 and s>.25 and l>.35 and not (h<.06 and s>.5)): return 'hair'
        if z>1.42: return 'head'
        if (h>.85 or h<.03) and s>.35 and l>.25 and z>.98: return 'top'
        if z>.74 and z<1.02 and x<.25 and ((h>.85 or h<.03) or s<.35): return 'pants'   # skirt in the pants slot
        if l>.72 and s<.45 and z<.8: return 'legwear'
        if (h>.85 or h<.04) and s>.4 and z<.8: return 'legwear'   # bows
        return 'body'
    else:
        if z>1.62 and (h>.7 and h<.85 and s>.2): return 'hat'
        if z>1.55 and l>.6 and s<.25: return 'hat'   # headphones ride with the cap
        if z>1.55: return 'head'
        if z>1.0 and l<.2: return 'jacket' if x>.06 else 'top'
        if z>.4 and z<1.05 and x<.28 and l<.2: return 'pants'
        if .5<z<1.0 and x>.25: return 'gloves'
        return 'body'
groups={}
for p in me.polygons:
    c=cls(p); groups.setdefault(c,set()).update(p.vertices)
for c,vs in groups.items():
    g=o.vertex_groups.new(name='slot_'+c); g.add(list(vs),1.,'REPLACE')
bpy.ops.wm.save_as_mainfile(filepath=outp); print('PIECES',json.dumps({c:len(v) for c,v in groups.items()}))
