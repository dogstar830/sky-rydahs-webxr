#!/usr/bin/env python3
"""JSON-only normal-map strip: drop material.normalTexture, then unreferenced textures/images and their bufferViews.
All other bufferViews (incl. Draco/accessor data) are copied byte-for-byte; only offsets are compacted. usage: IN OUT"""
import json,struct,sys,os
IN,OUT=sys.argv[1],sys.argv[2]; assert os.path.abspath(IN)!=os.path.abspath(OUT) and not os.path.exists(OUT)
b=open(IN,'rb').read(); jl=struct.unpack('<I',b[12:16])[0]; j=json.loads(b[20:20+jl]); bo=20+jl; bl=struct.unpack('<I',b[bo:bo+4])[0]; BIN=b[bo+8:bo+8+bl]
for m in j.get('materials',[]): m.pop('normalTexture',None)
def texrefs(o,acc):
    if isinstance(o,dict):
        for k,v in o.items():
            if k.endswith('Texture') and isinstance(v,dict) and 'index' in v: acc.add(v['index'])
            texrefs(v,acc)
    elif isinstance(o,list):
        for v in o: texrefs(v,acc)
used=set(); texrefs(j.get('materials',[]),used)
tmap={o:n for n,o in enumerate(sorted(used))}
def remap(o):
    if isinstance(o,dict):
        for k,v in o.items():
            if k.endswith('Texture') and isinstance(v,dict) and 'index' in v: v['index']=tmap[v['index']]
            remap(v)
    elif isinstance(o,list):
        for v in o: remap(v)
remap(j['materials']); j['textures']=[j['textures'][o] for o in sorted(used)]
def srcs(t): return [t.get('source')]+[e.get('source') for e in t.get('extensions',{}).values()]
iu=sorted({s for t in j['textures'] for s in srcs(t) if s is not None}); imap={o:n for n,o in enumerate(iu)}
for t in j['textures']:
    if 'source' in t: t['source']=imap[t['source']]
    for e in t.get('extensions',{}).values():
        if 'source' in e: e['source']=imap[e['source']]
j['images']=[j['images'][o] for o in iu]
# bufferViews still referenced
def bvrefs(o,acc):
    if isinstance(o,dict):
        for k,v in o.items():
            if k=='bufferView' and isinstance(v,int): acc.add(v)
            bvrefs(v,acc)
    elif isinstance(o,list):
        for v in o: bvrefs(v,acc)
keep=set(); bvrefs({k:v for k,v in j.items() if k!='bufferViews'},keep)
order=sorted(keep); bmap={o:n for n,o in enumerate(order)}; nb=bytearray(); nbv=[]
for o in order:
    v=dict(j['bufferViews'][o]); s=v.get('byteOffset',0); d=BIN[s:s+v['byteLength']]
    while len(nb)%4: nb.append(0)
    v['byteOffset']=len(nb); nb+=d; nbv.append(v)
def bvremap(o):
    if isinstance(o,dict):
        for k,v in o.items():
            if k=='bufferView' and isinstance(v,int): o[k]=bmap[v]
            else: bvremap(v)
    elif isinstance(o,list):
        for v in o: bvremap(v)
bvremap({k:v for k,v in j.items() if k!='bufferViews'}); j['bufferViews']=nbv
while len(nb)%4: nb.append(0)
j['buffers'][0]['byteLength']=len(nb)
js=json.dumps(j,separators=(',',':')).encode(); js+=b' '*((4-len(js)%4)%4)
out=b'glTF'+struct.pack('<II',2,12+8+len(js)+8+len(nb))+struct.pack('<I',len(js))+b'JSON'+js+struct.pack('<I',len(nb))+b'BIN\x00'+bytes(nb)
open(OUT,'wb').write(out); print(OUT,len(b),'->',len(out),'textures',len(j['textures']),'images',len(j['images']))
