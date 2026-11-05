import json,shutil,os,numpy as np
from glb import *; from joints import worlds
A='/workspace/skyrydahs-characters/anika/'; TS='20261030-0331'; rep={}
FS=['anika-rider','anika-rider.quest','anika-rider.quest-ktx2','anika-npc','anika-npc.quest','anika-npc.quest-ktx2']
for f in FS:
  fn=A+f+'.glb'; bk=A+f+'.presym-'+TS+'.glb'
  if not os.path.exists(bk): shutil.copy(fn,bk)
  j,b=load(bk); sk=j['skins'][0]; order=[j['nodes'][i]['name'] for i in sk['joints']]; Wd=worlds(j)
  name2i={n['name']:i for i,n in enumerate(j['nodes'])}; par={c:i for i,n in enumerate(j['nodes']) for c in n.get('children',[])}
  L=[n for n in order if n.endswith('LeftArm')][0]; Rn=[n for n in order if n.endswith('RightArm')][0]
  pL,pR=Wd[L][:3,3],Wd[Rn][:3,3]; y=(pL[1]+pR[1])/2; z=(pL[2]+pR[2])/2
  new={L:np.array([0.135,y,pL[2]]),Rn:np.array([-0.135,y,pR[2]])}; d={}
  for n,P1 in new.items():
    i=name2i[n]; pw=Wd[j['nodes'][par[i]]['name']]; P0=Wd[n][:3,3]
    j['nodes'][i]['translation']=[float(v) for v in pw[:3,:3].T@(P1-pw[:3,3])]   # parent has no scale (checked: rest = rotations)
    Rw=Wd[n][:3,:3]
    for c in j['nodes'][i].get('children',[]):   # keep children world positions
      cw=Wd[j['nodes'][c]['name']][:3,3]; j['nodes'][c]['translation']=[float(v) for v in Rw.T@(cw-P1)]
    d[n.split(':')[-1]]={'old':P0.round(4).tolist(),'new':P1.round(4).tolist(),'delta':(P1-P0).round(4).tolist()}
  W2=worlds(j)
  for n in order:
    if n not in new: assert np.abs(W2[n][:3,3]-Wd[n][:3,3]).max()<1e-6,n
  IB=np.stack([np.linalg.inv(W2[n]).T.reshape(-1) for n in order]).astype(np.float32)
  a=j['accessors'][sk['inverseBindMatrices']]; v=j['bufferViews'][a['bufferView']]; o=v.get('byteOffset',0)+a.get('byteOffset',0); b[o:o+IB.nbytes]=IB.tobytes()
  save(fn,j,b); rep[f]=d; print(f,d)
rp=A+'anika-rig-report.json'; r=json.load(open(rp)); r['symShoulders_0331']={'note':'LeftArm/RightArm bind joints set symmetric x +-0.135, y = mean of both sides, z kept per side; children world positions kept; IBMs = inv(bind world); weights, spring bones, springChains, _WC/_WA unchanged','files':rep}; json.dump(r,open(rp,'w'),indent=1)
