# De-interleave a GLB: every accessor in a strided bufferView gets its own tightly-packed view. Everything else byte-identical.
import sys,json,struct
CS={5120:1,5121:1,5122:2,5123:2,5125:4,5126:4}; NC={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
src,dst=sys.argv[1],sys.argv[2]; d=open(src,'rb').read()
jl=struct.unpack('<I',d[12:16])[0]; j=json.loads(d[20:20+jl]); bin_=d[20+jl+8:]
bv,acc=j['bufferViews'],j['accessors']; out=bytearray(); nbv=[]; remap={}
def pad(): 
  while len(out)%4: out.append(0)
users={}
for i,a in enumerate(acc):
  if 'bufferView' in a: users.setdefault(a['bufferView'],[]).append(i)
for vi,v in enumerate(bv):
  st=v.get('byteStride'); base=v.get('byteOffset',0)
  if st and vi in users:
    for ai in users[vi]:
      a=acc[ai]; es=CS[a['componentType']]*NC[a['type']]; o=base+a.get('byteOffset',0); pad(); start=len(out)
      for k in range(a['count']): out+=bin_[o+k*st:o+k*st+es]
      nv={'buffer':0,'byteOffset':start,'byteLength':len(out)-start}
      if 'target' in v: nv['target']=v['target']
      a['bufferView']=len(nbv); a.pop('byteOffset',None); nbv.append(nv)
  else:
    pad(); start=len(out); out+=bin_[base:base+v['byteLength']]; nv=dict(v); nv['byteOffset']=start; remap[vi]=len(nbv); nbv.append(nv)
    for ai in users.get(vi,[]): acc[ai]['bufferView']=remap[vi]
for key in ('images',):
  for im in j.get(key,[]):
    if 'bufferView' in im: im['bufferView']=remap[im['bufferView']]
pad(); j['bufferViews']=nbv; j['buffers']=[{'byteLength':len(out)}]
js=json.dumps(j,separators=(',',':')).encode(); js+=b' '*((4-len(js)%4)%4)
glb=b'glTF'+struct.pack('<II',2,12+8+len(js)+8+len(out))+struct.pack('<I',len(js))+b'JSON'+js+struct.pack('<I',len(out))+b'BIN\x00'+bytes(out)
open(dst,'wb').write(glb); print(dst,len(glb))
