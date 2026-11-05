import json,struct,numpy as np,copy
D='/workspace/skyrydahs-characters/wardrobe/skates/'
G=np.load('/workspace/forge_kit/skate/skate_v2_geo.npz')
def readglb(f):
  d=open(f,'rb').read();l=struct.unpack('<I',d[12:16])[0];return json.loads(d[20:20+l]),d[20+l+8:]
OM,_=readglb(D+'at-skate-meshy.glb'); MM,MB=readglb(D+'at-skate-meshy.merged.glb')
WC={'F':np.array([0,-0.0425,0.0895],np.float32),'R':np.array([0,-0.0485,-0.1715],np.float32)}
FRAME_Y=-0.02
class W:
  def __init__(s): s.bin=bytearray(); s.bv=[]; s.acc=[]
  def add(s,arr,ctype,typ,target=None,norm=False,minmax=False):
    while len(s.bin)%4: s.bin.append(0)
    o=len(s.bin); b=arr.tobytes(); s.bin+=b; v={'buffer':0,'byteOffset':o,'byteLength':len(b)}
    if target: v['target']=target
    s.bv.append(v); a={'bufferView':len(s.bv)-1,'componentType':ctype,'count':int(arr.shape[0]),'type':typ}
    if norm: a['normalized']=True
    if minmax: a['min']=arr.min(0).tolist(); a['max']=arr.max(0).tolist()
    s.acc.append(a); return len(s.acc)-1
  def glb(s,j,path):
    while len(s.bin)%4: s.bin.append(0)
    j['bufferViews']=s.bv; j['accessors']=s.acc; j['buffers']=[{'byteLength':len(s.bin)}]
    js=json.dumps(j,separators=(',',':')).encode(); js+=b' '*((4-len(js)%4)%4)
    open(path,'wb').write(b'glTF'+struct.pack('<II',2,12+8+len(js)+8+len(s.bin))+struct.pack('<I',len(js))+b'JSON'+js+struct.pack('<I',len(s.bin))+b'BIN\x00'+bytes(s.bin))
def masks(P,wheel):
  n=len(P); c0=np.zeros((n,4),np.uint8); c0[:,3]=255; c1=np.zeros((n,4),np.uint16); c1[:,3]=65535
  if wheel: c0[:,2]=255; c1[:,0]=49151; c1[:,1]=65535
  else:
    fr=P[:,1]<FRAME_Y; c0[fr,1]=255; c0[~fr,0]=255; c1[:,0]=45055
  return c0,c1
def prim(w,P,N,U,I,extra=None):
  att={'POSITION':w.add(P.astype(np.float32),5126,'VEC3',34962,minmax=True),'NORMAL':w.add(N.astype(np.float32),5126,'VEC3',34962),'TEXCOORD_0':w.add(U.astype(np.float32),5126,'VEC2',34962)}
  for k,(arr,ct,tp,nm) in (extra or {}).items(): att[k]=w.add(arr,ct,tp,34962,norm=nm)
  ix=I.reshape(-1); ix=ix.astype(np.uint16 if ix.max()<65535 else np.uint32)
  return {'attributes':att,'indices':w.add(ix.reshape(-1,1) if False else ix,5123 if ix.dtype==np.uint16 else 5125,'SCALAR',34963),'material':0,'mode':4}
def part(name,i):
  g=lambda k:G['%s%d_%s'%(name,i,k)]; return g('P'),g('N'),g('U'),g('I')
# ---------- module v2
w=W(); j={'asset':copy.deepcopy(OM['asset']),'scene':0,'materials':copy.deepcopy(OM['materials'])}
j['asset']['extras']['at_v2']='Rydah Forge 2026-10-30: shell rebuilt from airtreck-meshy.glb (welded half, decimated, watertight per part), 1K rebake -> shared/at-skate/at-skate-meshy-v2-1k*.png; wheels procedural (gold hub + 5 spokes, cyan rim texels); wheel nodes moved to true axle centres; sockets unchanged'
meshes=[]; nodes=[]
for i in range(3):
  base=len(nodes)
  P,N,U,I=part('shell',i); c0,c1=masks(P,False)
  meshes.append({'name':'ShellBlend_L%d'%i,'primitives':[prim(w,P,N,U,I,{'COLOR_0':(c0,5121,'VEC4',True),'COLOR_1':(c1,5123,'VEC4',True)})]})
  nodes.append({'name':'ShellBlend_L%d'%i,'mesh':len(meshes)-1})
  for wn in 'FR':
    P,N,U,I=part('wheel'+wn,i); c0,c1=masks(P,True)
    meshes.append({'name':'Wheel_%s_L%d'%(wn,i),'primitives':[prim(w,P,N,U,I,{'COLOR_0':(c0,5121,'VEC4',True),'COLOR_1':(c1,5123,'VEC4',True)})]})
    nodes.append({'name':'Wheel_%s_L%d'%(wn,i),'translation':WC[wn].tolist(),'mesh':len(meshes)-1})
  nodes.append({'name':'Skate_LOD%d'%i,'children':[base,base+1,base+2]})
socks=[n for n in OM['nodes'] if 'at_socket' in n.get('extras',{})]
s0=len(nodes); nodes+=copy.deepcopy(socks); nodes[3]['children']+=list(range(s0,s0+len(socks)))
j['nodes']=nodes; j['meshes']=meshes; j['scenes']=[{'nodes':[3,7,11]}]
w.glb(j,'/workspace/forge_kit/skate/at-skate-meshy.v2.raw.glb')
# ---------- merged v2
w=W(); j={'asset':copy.deepcopy(MM['asset']),'scene':0,'materials':copy.deepcopy(MM['materials'])}
nodes=copy.deepcopy(MM['nodes'][:25])
foot={'L':np.array(MM['nodes'][1]['translation'],np.float32),'R':np.array(MM['nodes'][13]['translation'],np.float32)}
piv=np.array([0,0.12,-0.06],np.float32)
lods=[]; meshes=[]
for i in range(3):
  Ps=[];Ns=[];Us=[];Is=[];C0=[];C1=[];WCa=[];J=[]; off=0
  for side,jn in (('L',0),('R',1)):
    for nm,wc in (('shell',None),('wheelF',WC['F']),('wheelR',WC['R'])):
      P,N,U,I=part(nm,i); P=P.copy(); N=N.copy(); I=I.copy()
      if wc is not None: P=P+wc
      c0,c1=masks(P,wc is not None)
      cen=(wc if wc is not None else None)
      if side=='R': P[:,0]*=-1; N[:,0]*=-1; I=I[:,[0,2,1]]
      P=P-piv+foot[side]
      if wc is not None: cc=wc.copy(); cc[0]*=(-1 if side=='R' else 1); cc=cc-piv+foot[side]; WCa.append(np.tile(cc,(len(P),1)))
      else: WCa.append(np.zeros((len(P),3),np.float32))
      Ps.append(P);Ns.append(N);Us.append(U);Is.append(I+off);C0.append(c0);C1.append(c1); J.append(np.tile(np.array([jn,0,0,0],np.uint8),(len(P),1))); off+=len(P)
  P=np.vstack(Ps);N=np.vstack(Ns);U=np.vstack(Us);I=np.vstack(Is)
  Wt=np.zeros((len(P),4),np.float32); Wt[:,0]=1
  meshes.append({'name':'ATSkate_LOD%d'%i,'primitives':[prim(w,P,N,U,I,{'COLOR_0':(np.vstack(C0),5121,'VEC4',True),'COLOR_1':(np.vstack(C1),5123,'VEC4',True),'_WC':(np.vstack(WCa).astype(np.float32),5126,'VEC3',False),'JOINTS_0':(np.vstack(J),5121,'VEC4',False),'WEIGHTS_0':(Wt,5126,'VEC4',False)})]})
  lods.append({'lod':i,'verts':int(len(P)),'tris':int(len(I)),'prims':1})
  nodes.append({'name':'ATSkate_LOD%d'%i,'mesh':i,'skin':0})
nodes[0]['children']=[1,13,25,26,27]
# IBM copy
a=MM['accessors'][MM['skins'][0]['inverseBindMatrices']]; v=MM['bufferViews'][a['bufferView']]; ibm=np.frombuffer(MB,np.float32,count=32,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(2,16).copy()
ia=w.add(ibm,5126,'MAT4')
j['skins']=[{'name':'ATSkateSkin','inverseBindMatrices':ia,'joints':[1,13]}]
j['nodes']=nodes; j['meshes']=meshes; j['scenes']=[{'nodes':[0]}]
j['asset']['extras']['lods']=lods; j['asset']['extras']['source']='wardrobe/skates/at-skate-meshy.v2.glb'
j['asset']['extras']['v2']='Rydah Forge 2026-10-30: same layout/attributes as v1 (COLOR_0 mask, COLOR_1 legacy flag, _WC, rigid skin to Left/RightFoot, same sockets); new shell + gold-hub wheels; textures shared/at-skate/at-skate-meshy-v2-1k*.png'
w.glb(j,'/workspace/forge_kit/skate/at-skate-meshy.merged.v2.raw.glb')
print('lods',lods)
