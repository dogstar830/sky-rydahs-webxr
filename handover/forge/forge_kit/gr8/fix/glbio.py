import json,struct,numpy as np
CT={5120:np.int8,5121:np.uint8,5122:np.int16,5123:np.uint16,5125:np.uint32,5126:np.float32}
NC={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
def load(f):
    d=open(f,'rb').read(); jl=struct.unpack('<I',d[12:16])[0]; j=json.loads(d[20:20+jl]); b=d[20+jl+8:]; return j,bytearray(b)
def acc(j,b,i):
    a=j['accessors'][i]; v=j['bufferViews'][a['bufferView']]; n=NC[a['type']]; dt=CT[a['componentType']]
    o=v.get('byteOffset',0)+a.get('byteOffset',0); st=v.get('byteStride')
    if st and st!=np.dtype(dt).itemsize*n: raise Exception('strided')
    x=np.frombuffer(bytes(b[o:o+a['count']*n*np.dtype(dt).itemsize]),dtype=dt).reshape(a['count'],n) if n>1 else np.frombuffer(bytes(b[o:o+a['count']*np.dtype(dt).itemsize]),dtype=dt).copy()
    if a.get('normalized') and dt!=np.float32: x=x.astype(np.float32)/np.iinfo(dt).max
    return x.copy()
def quat(q):
    x,y,z,w=q; return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def local(n):
    if 'matrix' in n: return np.array(n['matrix']).reshape(4,4).T
    M=np.eye(4); R=quat(n.get('rotation',[0,0,0,1])); S=np.diag(n.get('scale',[1,1,1])); M[:3,:3]=R@S; M[:3,3]=n.get('translation',[0,0,0]); return M
def worlds(j):
    par={}
    for i,n in enumerate(j['nodes']):
        for c in n.get('children',[]): par[c]=i
    W={}
    def w(i):
        if i in W: return W[i]
        M=local(j['nodes'][i]); W[i]=(w(par[i])@M) if i in par else M; return W[i]
    for i in range(len(j['nodes'])): w(i)
    return W
def save(f,j,bufs):
    """bufs: list of (accessor_dict, np.array, target) appended fresh; rebuild bin from scratch keeping images. Simplest: caller provides full rebuild."""
    raise NotImplementedError
