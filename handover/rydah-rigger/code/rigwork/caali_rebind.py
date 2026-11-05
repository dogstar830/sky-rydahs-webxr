import json,shutil,numpy as np
from glb import *; from joints import worlds
R='/workspace/skyrydahs-characters/wardrobe/riders/'; TS='20261030-0327'; rep={}
ARM=lambda n:any(k in n for k in ['Arm','Hand'])  # Arm, ArmTwist, ForeArm(Twist), Hand, fingers
LEG=lambda n:any(k in n for k in ['Hips','UpLeg','Leg','Foot','Toe'])
def skin(j,b,P,J,Wt,order):
  Wd=worlds(j); sk=j['skins'][0]; IB=acc(j,b,sk['inverseBindMatrices']).reshape(-1,4,4).transpose(0,2,1)
  Mx=np.stack([Wd[n]@IB[k] for k,n in enumerate(order)]); Ph=np.c_[P,np.ones(len(P))]
  out=np.zeros_like(P)
  for k in range(4): out+=Wt[:,k:k+1]*np.einsum('nij,nj->ni',Mx[J[:,k]],Ph)[:,:3]
  return out
for f in ['caali-g-v2','caali-g-v2-hd','caali-g-v2.quest','caali-g-v2.quest-ktx2']:
  cur=R+f+'.rigged.glb'; pre=R+f+'.rigged.prespring-20261030-0319.glb'
  import os
  if not os.path.exists(R+f+'.rigged.prerebind-'+TS+'.glb'): shutil.copy(cur,R+f+'.rigged.prerebind-'+TS+'.glb')
  jc,bc=load(cur); j,b=load(pre); sk=j['skins'][0]; order=[j['nodes'][i]['name'] for i in sk['joints']]
  for i in sk['joints']:
    assert jc['nodes'][i]['name']==j['nodes'][i]['name']; j['nodes'][i]['translation']=jc['nodes'][i]['translation']
  IBc=acc(jc,bc,jc['skins'][0]['inverseBindMatrices']).astype(np.float32)
  # recompute IBM = inv(bind world) exactly in float64 from new joints
  Wd=worlds(j); IB=np.stack([np.linalg.inv(Wd[n]).T.reshape(-1) for n in order]).astype(np.float32)
  a=j['accessors'][sk['inverseBindMatrices']]; v=j['bufferViews'][a['bufferView']]; o=v.get('byteOffset',0)+a.get('byteOffset',0); b[o:o+IB.nbytes]=IB.tobytes()
  isA=np.array([ARM(n) for n in order]); isL=np.array([LEG(n) for n in order]); mr={}
  for ni,nm,p in prims(j,b):
    at=p['attributes']; P=acc(j,b,at['POSITION']).astype(np.float64); J=acc(j,b,at['JOINTS_0']).astype(np.int64); Wt=acc(j,b,at['WEIGHTS_0']).astype(np.float64)
    dom=J[np.arange(len(J)),Wt.argmax(1)]; wA=(Wt*isA[J]).sum(1); wL=(Wt*isL[J]).sum(1); hd=np.array(['Hand' in n for n in order]); wH=(Wt*hd[J]).sum(1)
    mix0=int(((wH>0)&(wL>0)).sum())
    lock=(wA>0)&(P[:,1]<0.93)&~isA[dom]; locked=int(lock.sum())   # pants/pocket/chain zone: no arm/hand influence
    Wt=np.where(lock[:,None]&isA[J],0,Wt)
    hm=(wH>0)&(wL>0); Wt=np.where((hm&(wH<wL))[:,None]&hd[J],0,Wt); Wt=np.where((hm&(wH>=wL))[:,None]&isL[J],0,Wt)
    Wt/=Wt.sum(1,keepdims=True); Wt=Wt.astype(np.float32); J=np.where(Wt>0,J,0)
    A=j['accessors'][at['JOINTS_0']]; Jw=J.astype(np.uint16 if A['componentType']==5123 else np.uint8); vv=j['bufferViews'][A['bufferView']]; o=vv.get('byteOffset',0)+A.get('byteOffset',0); b[o:o+Jw.nbytes]=Jw.tobytes()
    A=j['accessors'][at['WEIGHTS_0']]; vv=j['bufferViews'][A['bufferView']]; o=vv.get('byteOffset',0)+A.get('byteOffset',0); b[o:o+Wt.nbytes]=Wt.tobytes()
    wA2=(Wt*hd[J]).sum(1); wL2=(Wt*isL[J]).sum(1); jhem=int(((Wt*isA[J]).sum(1)>0).__and__(isL[dom]).sum())
    S=skin(j,b,P,J,Wt.astype(np.float64),order); dmax=float(np.abs(S-P).max())
    mr[nm]={'jacketHemLegDomWithArm_leftAsIs':jhem,'mixedHandLegBefore':mix0,'lockedLegVerts':locked,'mixedAfter':int(((wA2>0)&(wL2>0)).sum()),'bindMaxDelta_m':dmax}
  j['asset'].setdefault('extras',{})['caaliArmTargets']='per-rider joint targets (Forge 03:18) Arm x+-0.19 y1.33, ForeArm y1.065, Hand y0.80; weights = prespring-0319 kept, only pants/pocket zone (y<0.93) verts stripped of arm/hand influence'
  save(cur,j,b); rep[f]=mr; print(f,mr)
rp=R+'caali-g-v2.rig-report.json'; r=json.load(open(rp)); r['perRiderJointOffsets_0320']['note']='Caali G v2 only. Joints moved to targets, IBMs recomputed (inv bind world), vertex weights = *.prespring-20261030-0319 unchanged except pants/pocket zone (y<0.93, non-arm-dominant) verts zeroed on arm/hand bones (0327 rebind); 0 hand+leg mixed verts. Fingertips not moved (Forge call).'
r['perRiderJointOffsets_0320']['rebind_0327']=rep; json.dump(r,open(rp,'w'),indent=1)
