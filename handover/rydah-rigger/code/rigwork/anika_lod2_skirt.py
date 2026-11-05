import numpy as np,json
from glb import *; from joints import worlds
from rig import K,DECK,segdist
from scipy.spatial import cKDTree
A='/workspace/skyrydahs-characters/anika/'
xi=json.load(open('out/anika-rig-report.json'))['fit']['extra']['skirt']; yt,yh=xi['top'],xi['hem']
cache={}
for f in ['anika-rider','anika-rider.quest','anika-rider.quest-ktx2','anika-npc','anika-npc.quest','anika-npc.quest-ktx2']:
  j,b=load(A+f+'.glb'); sk=j['skins'][0]; order=[j['nodes'][i]['name'] for i in sk['joints']]; W=worlds(j); idx={n:k for k,n in enumerate(order)}
  for ni,nm,p in prims(j,b):
    if 'LOD2' not in nm: continue
    at=p['attributes']; P=acc(j,b,at['POSITION']).astype(float); Pd=(P+[0,DECK,0])/K
    if 'ktx2' in f: slots=cache[(f.replace('.quest-ktx2','.quest'),nm)]; QP,qs=slots; _,ii=cKDTree(QP).query(P); slots=qs[ii]
    else: slots=slots_anika(Pd,vcolors(j,b,p),acc(j,b,at['TEXCOORD_0'])); cache[(f,nm)]=(P,slots)
    for S in ['Left','Right']:
      d,_=segdist(P,W['mixamorig:'+S+'UpLeg'][:3,3],W['mixamorig:'+S+'Leg'][:3,3]); slots=np.where((slots=='skirt')&(d<0.085),'body',slots)
    J=acc(j,b,at['JOINTS_0']).copy(); Wt=acc(j,b,at['WEIGHTS_0']).copy()
    # only verts that are currently pure Hips (folded skirt) inside the skirt slot
    hips=idx['mixamorig:Hips']; m=(slots=='skirt')&(((J==hips)*Wt).sum(1)>0.99)
    q=P[m]; c=W['mixamorig:Hips'][:3,3]
    t=np.clip((yt-q[:,1])/(yt-yh),0,1); s=np.clip(t/0.45,0,1); s=s*s*(3-2*s)
    ang=(np.degrees(np.arctan2(q[:,0]-c[0],q[:,2]-c[2]))%360)/60.; a0=np.floor(ang).astype(int)%6; al=ang-np.floor(ang)
    nJ=np.zeros((len(q),4),J.dtype); nW=np.zeros((len(q),4),np.float32)
    nJ[:,0]=hips; nW[:,0]=1-s; nJ[:,1]=[idx[f'Anika_Skirt_{k:02d}'] for k in a0]; nW[:,1]=s*(1-al); nJ[:,2]=[idx[f'Anika_Skirt_{(k+1)%6:02d}'] for k in a0]; nW[:,2]=s*al
    nW/=nW.sum(1,keepdims=True); J[m]=nJ; Wt[m]=nW
    for key,arr in [('JOINTS_0',J),('WEIGHTS_0',Wt)]:
      Ac=j['accessors'][at[key]]; v=j['bufferViews'][Ac['bufferView']]; o=v.get('byteOffset',0)+Ac.get('byteOffset',0); arr=np.ascontiguousarray(arr); b[o:o+arr.nbytes]=arr.tobytes()
    print(f,nm,'skirt verts re-sprung',int(m.sum()))
  ex=sk.setdefault('extras',{}); ch=ex.setdefault('springChains',{})
  for k in ['Anika_BraidL','Anika_BraidR']:
    if k in ch: ch[k]['lod']='weighted on LOD0/LOD1/LOD2 (braids split from the top by Forge 03:08: braid verts on Braid*_01..05 + Head only). Simulate LOD0 within 14 m; LOD1/LOD2 may run at rest or reduced rate (lite: frozen)'
  if 'Anika_Skirt' in ch: ch['Anika_Skirt']['lod']='weighted on LOD0/LOD1/LOD2 (LOD2 re-sprung 03:2x, no longer folded into Hips)'
  for nd in j['nodes']:
    if nd.get('name','').startswith('Anika_') and 'extras' in nd: nd['extras']['spring']['lods']=[0,1,2]
  save(A+f+'.glb',j,b)
