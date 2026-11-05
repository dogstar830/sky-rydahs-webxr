# lift AT skate v2 so wheel bottoms sit at y=0 at bind (scale 1). in-place byte edit of a flat (de-interleaved) GLB
import sys,json,struct,numpy as np; sys.path.insert(0,'/workspace/forge_kit/gr8/fix'); from glbio import *
src,dst,d=sys.argv[1],sys.argv[2],float(sys.argv[3]); j,b=load(src); W=worlds(j)
par={c:i for i,n in enumerate(j['nodes']) for c in n.get('children',[])}
def shift(i):
    n=j['nodes'][i]; R=np.linalg.inv(W[par[i]][:3,:3]) if i in par else np.eye(3); n['translation']=[float(x) for x in np.array(n.get('translation',[0,0,0]))+R@np.array([0,d,0])]
if j.get('skins'):   # merged: skinned verts in armature space -> edit POSITION; sockets via the AT roots
    done=set()
    for n in j['nodes']:
        if 'mesh' in n:
            for p in j['meshes'][n['mesh']]['primitives']:
                ai=p['attributes']['POSITION']
                if ai in done: continue
                done.add(ai); a=j['accessors'][ai]; v=j['bufferViews'][a['bufferView']]; o=v.get('byteOffset',0)+a.get('byteOffset',0)
                P=np.frombuffer(bytes(b[o:o+a['count']*12]),np.float32).reshape(-1,3).copy(); P[:,1]+=d; b[o:o+a['count']*12]=P.tobytes(); a['min']=[float(x) for x in P.min(0)]; a['max']=[float(x) for x in P.max(0)]
    for i,n in enumerate(j['nodes']):
        if n['name'][:5] in ('L_at_','R_at_'): shift(i)   # sockets only; *_AT_Root stays on the foot (= scale pivot)
else:
    for i in j['scenes'][0]['nodes']: shift(i)
js=json.dumps(j,separators=(',',':')).encode(); js+=b' '*((4-len(js)%4)%4)
open(dst,'wb').write(b'glTF'+struct.pack('<II',2,12+8+len(js)+8+len(b))+struct.pack('<I',len(js))+b'JSON'+js+struct.pack('<I',len(b))+b'BIN\x00'+bytes(b))
