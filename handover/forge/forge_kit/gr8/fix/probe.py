import sys,io,numpy as np; sys.path.insert(0,'.'); from glbio import *; from PIL import Image
j,b=load('/workspace/skyrydahs-characters/anika/anika-rider.glb'); sk=j['skins'][0]; JN=[j['nodes'][i]['name'] for i in sk['joints']]
IBM=acc(j,b,sk['inverseBindMatrices']).reshape(-1,4,4).transpose(0,2,1); JP=np.array([np.linalg.inv(m)[:3,3] for m in IBM])
p=j['meshes'][0]['primitives'][0]; P=acc(j,b,p['attributes']['POSITION']); UV=acc(j,b,p['attributes']['TEXCOORD_0']); F=acc(j,b,p['indices']).reshape(-1,3)
im=[i for i in j['images'] if i['name']=='anika_LOD0_col'][0]; v=j['bufferViews'][im['bufferView']]; o=v.get('byteOffset',0)
C=np.asarray(Image.open(io.BytesIO(bytes(b[o:o+v['byteLength']]))).convert('RGB'),dtype=np.float32)/255; H,W=C.shape[:2]
cen=P[F].mean(1); cuv=UV[F].mean(1); px=C[np.clip((cuv[:,1]*H).astype(int),0,H-1),np.clip((cuv[:,0]*W).astype(int),0,W-1)]
for sd in 'LR':
  pts=JP[[JN.index(f'Anika_Braid{sd}_0{k}') for k in range(1,6)]]; print(sd,pts.round(3).tolist())
  d=np.full(len(F),9.)
  for a,c in zip(pts[:-1],pts[1:]):
    ab=c-a;t=np.clip(((cen-a)@ab)/(ab@ab),0,1);d=np.minimum(d,np.linalg.norm(cen-(a+t[:,None]*ab),axis=1))
  for r in (.02,.03,.045,.06):
    s=d<r; print(r,s.sum(),np.percentile(px[s],[10,50,90],axis=0).round(2).tolist())
hair=(px[:,1]/(px[:,0]+1e-4)>.8)&(px[:,1]>=px[:,2])&(px.max(1)>.25)
for sd in 'LR':
  pts=JP[[JN.index(f'Anika_Braid{sd}_0{k}') for k in range(1,6)]]; pts=np.vstack([pts,pts[-1]+(pts[-1]-pts[-2])])
  d=np.full(len(F),9.)
  for a,c in zip(pts[:-1],pts[1:]):
    ab=c-a;t=np.clip(((cen-a)@ab)/(ab@ab),0,1);d=np.minimum(d,np.linalg.norm(cen-(a+t[:,None]*ab),axis=1))
  for r in (.03,.045,.06,.08): print(sd,r,(hair&(d<r)).sum(),(d<r).sum())
print('hair total',hair.sum(), 'hair below 1.25',(hair&(cen[:,1]<1.25)).sum())
h=hair&(cen[:,1]<1.30)
for sx in (1,-1):
  s=h&(np.sign(cen[:,0])==sx); c=cen[s]; print(sx,s.sum(),c.min(0).round(3),c.max(0).round(3),np.median(c,0).round(3))
  for y0 in np.arange(1.0,1.31,.05):
    q=c[(c[:,1]>=y0)&(c[:,1]<y0+.05)]
    if len(q): print('  y',round(y0,2),len(q),q.mean(0).round(3))
print('head',JP[JN.index('mixamorig:Head')].round(3), 'neck',JP[JN.index('mixamorig:Neck')].round(3))
s=cen[:,1]>1.40; print('crown',s.sum(),np.percentile(px[s],[10,50,90],axis=0).round(2).tolist())
for y0 in (1.05,1.1,1.15,1.2):
  s=(cen[:,1]>y0)&(cen[:,1]<y0+.05)&(np.abs(cen[:,0])>.06)&(np.abs(cen[:,0])<.2)&(cen[:,2]>-0.02); print(y0,s.sum(),np.percentile(px[s],[10,50,90],axis=0).round(2).tolist())
hair=(px[:,2]<0.82*px[:,1])&(px[:,1]>0.55*px[:,0])&(cen[:,1]>.5)
print('crownhair frac',hair[cen[:,1]>1.40].mean())
for sd in 'LR':
  pts=JP[[JN.index(f'Anika_Braid{sd}_0{k}') for k in range(1,6)]]; pts=np.vstack([pts,pts[-1]+(pts[-1]-pts[-2])])
  d=np.full(len(F),9.)
  for a,c in zip(pts[:-1],pts[1:]):
    ab=c-a;t=np.clip(((cen-a)@ab)/(ab@ab),0,1);d=np.minimum(d,np.linalg.norm(cen-(a+t[:,None]*ab),axis=1))
  for r in (.03,.045,.06): print(sd,r,(hair&(d<r)).sum(),(d<r).sum())
