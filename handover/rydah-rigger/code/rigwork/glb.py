import json,struct,numpy as np
CT={5120:np.int8,5121:np.uint8,5122:np.int16,5123:np.uint16,5125:np.uint32,5126:np.float32}
NC={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
def load(f):
  d=open(f,'rb').read(); jl=struct.unpack('<I',d[12:16])[0]; j=json.loads(d[20:20+jl]); b=bytearray(d[20+jl+8:]); return j,b
def acc(j,b,i):
  a=j['accessors'][i]; v=j['bufferViews'][a['bufferView']]; dt=CT[a['componentType']]; n=NC[a['type']]
  o=v.get('byteOffset',0)+a.get('byteOffset',0); st=v.get('byteStride')
  if st and st!=np.dtype(dt).itemsize*n: raise Exception('interleaved')
  return np.frombuffer(bytes(b[o:o+a['count']*n*np.dtype(dt).itemsize]),dt).reshape(a['count'],n)
def add(j,b,arr,ctype,typ,target=None,minmax=False):
  while len(b)%4: b.append(0)
  arr=np.ascontiguousarray(arr.astype(CT[ctype])); o=len(b); b+=arr.tobytes()
  v={'buffer':0,'byteOffset':o,'byteLength':arr.nbytes}
  if target: v['target']=target
  j['bufferViews'].append(v); a={'bufferView':len(j['bufferViews'])-1,'componentType':ctype,'count':len(arr),'type':typ}
  if minmax: a['min']=arr.min(0).tolist(); a['max']=arr.max(0).tolist()
  j['accessors'].append(a); return len(j['accessors'])-1
def save(f,j,b):
  while len(b)%4: b.append(0)
  j['buffers']=[{'byteLength':len(b)}]
  js=json.dumps(j,separators=(',',':')).encode(); js+=b' '*((4-len(js)%4)%4)
  open(f,'wb').write(b'glTF'+struct.pack('<II',2,28+len(js)+len(b))+struct.pack('<I',len(js))+b'JSON'+js+struct.pack('<I',len(b))+b'BIN\x00'+bytes(b))
import io
from PIL import Image
def prims(j,b):
  out=[]
  for ni,n in enumerate(j['nodes']):
    if 'mesh' in n:
      for pi,p in enumerate(j['meshes'][n['mesh']]['primitives']): out.append((ni,n.get('name'),p))
  return out
def basecolor_img(j,b,p):
  m=j['materials'][p['material']]; t=m['pbrMetallicRoughness']['baseColorTexture']['index']; tex=j['textures'][t]
  src=tex.get('source')
  if src is None: src=tex.get('extensions',{}).get('EXT_texture_webp',{}).get('source')
  if src is None: return None
  im=j['images'][src]; v=j['bufferViews'][im['bufferView']]; o=v.get('byteOffset',0)
  return np.asarray(Image.open(io.BytesIO(bytes(b[o:o+v['byteLength']]))).convert('RGB')).astype(np.float32)/255
def vcolors(j,b,p):
  img=basecolor_img(j,b,p); uv=acc(j,b,p['attributes']['TEXCOORD_0']).astype(float)
  h,w,_=img.shape; x=np.clip((uv[:,0]%1)*w,0,w-1).astype(int); y=np.clip((uv[:,1]%1)*h,0,h-1).astype(int); return img[y,x]
def hls(c):
  mx=c.max(1); mn=c.min(1); l=(mx+mn)/2; d=mx-mn
  s=np.where(d<1e-6,0,np.where(l<=.5,d/np.maximum(mx+mn,1e-6),d/np.maximum(2-mx-mn,1e-6)))
  r,g,b=c[:,0],c[:,1],c[:,2]; dd=np.maximum(d,1e-6)
  h=np.where(mx==r,((g-b)/dd)%6,np.where(mx==g,(b-r)/dd+2,(r-g)/dd+4))/6; h=np.where(d<1e-6,0,h)
  return h,l,s
def slots_anika(P,c,uv):
  h,l,s=hls(c); z=P[:,1]; x=abs(P[:,0]); out=np.full(len(P),'body',dtype=object)
  pinkish=(h>.85)|(h<.03)
  sk=(uv[:,0]%1)>.75
  hair=(z>1.30)&(h<.14)&(s>.25)&(l>.35)&~((h<.06)&(s>.5))
  out[(z>1.42)&~hair]='head'; out[hair]='hair'
  rest=(out=='body')
  out[rest&pinkish&(s>.35)&(l>.25)&(z>.98)]='top'; rest=(out=='body')
  out[rest&(z>.74)&(z<1.02)&(x<.25)&(pinkish|(s<.35))]='skirt'; rest=(out=='body')
  out[rest&(l>.72)&(s<.45)&(z<.8)]='legwear'; out[rest&pinkish&(s>.4)&(z<.8)]='legwear'
  out[sk]='skates'; return out
