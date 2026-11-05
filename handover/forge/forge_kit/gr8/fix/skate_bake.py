# module at-skate v2: bake the Skate_LOD* root translation into children (shell verts, wheel node + socket translations), roots -> identity
import sys,json,struct,numpy as np; sys.path.insert(0,'/workspace/forge_kit/gr8/fix'); from glbio import *
src,dst=sys.argv[1:3]; j,b=load(src); N=j['nodes']; done=set()
for r in j['scenes'][0]['nodes']:
    t=np.array(N[r].pop('translation',[0,0,0])); assert not any(k in N[r] for k in('rotation','scale','matrix'))
    for c in N[r].get('children',[]):
        n=N[c]
        if 'translation' in n or 'mesh' not in n: n['translation']=[float(x) for x in np.array(n.get('translation',[0,0,0]))+t]   # wheels (verts local to their axle) + sockets
        else:
            for p in j['meshes'][n['mesh']]['primitives']:
                ai=p['attributes']['POSITION']
                if ai in done: continue
                done.add(ai); a=j['accessors'][ai]; v=j['bufferViews'][a['bufferView']]; o=v.get('byteOffset',0)+a.get('byteOffset',0)
                P=np.frombuffer(bytes(b[o:o+a['count']*12]),np.float32).reshape(-1,3).copy(); P+=t.astype(np.float32); b[o:o+a['count']*12]=P.tobytes(); a['min']=[float(x) for x in P.min(0)]; a['max']=[float(x) for x in P.max(0)]
    print(N[r]['name'],'baked',t.tolist())
js=json.dumps(j,separators=(',',':')).encode(); js+=b' '*((4-len(js)%4)%4)
open(dst,'wb').write(b'glTF'+struct.pack('<II',2,12+8+len(js)+8+len(b))+struct.pack('<I',len(js))+b'JSON'+js+struct.pack('<I',len(b))+b'BIN\x00'+bytes(b))
