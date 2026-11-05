import sys,json,numpy as np
from glb import *; from joints import worlds
import rig
rig.THIGHGUARD=True
from rig import M,weights,pack,subtree
R='/workspace/skyrydahs-characters/wardrobe/riders/'
T={'Left':(0.19,1.33),'Right':(-0.19,1.33)}; EY,WY=1.065,0.80
rep={}
for f in ['caali-g-v2','caali-g-v2-hd','caali-g-v2.quest','caali-g-v2.quest-ktx2']:
  fn=R+f+'.rigged.glb'; j,b=load(fn); W=worlds(j); sk=j['skins'][0]; order=[j['nodes'][i]['name'] for i in sk['joints']]
  P0={n:W[n][:3,3].copy() for n in order}; Rw={n:W[n][:3,:3] for n in order}; P1=dict(P0); d={}
  for S,(x,y) in T.items():
    A0,E0,H0=P0[M(S+'Arm')],P0[M(S+'ForeArm')],P0[M(S+'Hand')]
    A1=np.array([x,y,A0[2]]); d1=(E0-A0)/np.linalg.norm(E0-A0); E1=A1+d1*((EY-A1[1])/d1[1]); d2=(H0-E0)/np.linalg.norm(H0-E0); H1=E1+d2*((WY-E1[1])/d2[1])
    for tw,(a0,b0,a1,b1) in {M(S+'ArmTwist'):(A0,E0,A1,E1),M(S+'ForeArmTwist'):(E0,H0,E1,H1)}.items():
      t=(P0[tw]-a0)@(b0-a0)/((b0-a0)@(b0-a0)); P1[tw]=a1+t*(b1-a1)
    P1[M(S+'Arm')],P1[M(S+'ForeArm')],P1[M(S+'Hand')]=A1,E1,H1
    for n in subtree(M(S+'Hand'))[1:]: P1[n]=P0[n]+(H1-H0)
    for n in [M(S+'Arm'),M(S+'ForeArm'),M(S+'Hand'),M(S+'HandMiddle4')]: d[n]={'old':P0[n].round(4).tolist(),'new':P1[n].round(4).tolist(),'delta':(P1[n]-P0[n]).round(4).tolist()}
  # node locals (rotations unchanged)
  idx={j['nodes'][i]['name']:i for i in sk['joints']}; par={}
  for i,n in enumerate(j['nodes']):
    for c in n.get('children',[]): par[c]=i
  for n in order:
    i=idx[n]
    if par.get(i) in [idx[m] for m in order]:
      pn=j['nodes'][par[i]]['name']; j['nodes'][i]['translation']=[float(v) for v in Rw[pn].T@(P1[n]-P0[pn]+ (P0[pn]-P1[pn])*0 ) ] if False else [float(v) for v in Rw[pn].T@(P1[n]-P1[pn])]
  IB=np.stack([np.linalg.inv(np.r_[np.c_[Rw[n],P1[n]],[[0,0,0,1]]]).T.reshape(-1) for n in order]).astype(np.float32)
  a=j['accessors'][sk['inverseBindMatrices']]; v=j['bufferViews'][a['bufferView']]; o=v.get('byteOffset',0)+a.get('byteOffset',0); b[o:o+IB.nbytes]=IB.tobytes()
  # reweight in bind (mesh already hangs in bind; skate stripped by Forge)
  mrep={}
  for ni,nm,p in prims(j,b):
    at=p['attributes']; Pm=acc(j,b,at['POSITION']).astype(np.float64); tris=acc(j,b,p['indices']).reshape(-1,3).astype(np.int64)
    Cc=acc(j,b,at['COLOR_0']); ct=j['accessors'][at['COLOR_0']]['componentType']; Cc=Cc/65535. if ct==5123 else (Cc/255. if ct==5121 else Cc); sid=np.floor(Cc[:,0]*16+.5)
    Wv=weights(Pm,tris,sid,None,P1,1.0); jj,ww,bad=pack(Wv,order,len(Pm))
    for key,arr,ctype in [('JOINTS_0',jj,None),('WEIGHTS_0',ww,None)]:
      A=j['accessors'][at[key]]; want=rig.np.uint8 if key=='JOINTS_0' else rig.np.float32
      if key=='JOINTS_0' and A['componentType']==5123: arr=arr.astype(np.uint16)
      assert (key=='WEIGHTS_0' and A['componentType']==5126) or key=='JOINTS_0'
      vv=j['bufferViews'][A['bufferView']]; o=vv.get('byteOffset',0)+A.get('byteOffset',0); arr=np.ascontiguousarray(arr); assert arr.nbytes==A['count']*arr.itemsize*4; b[o:o+arr.nbytes]=arr.tobytes()
    mrep[nm]={'tris':len(tris),'maxinf':int((ww>0).sum(1).max()),'unweighted':int(bad.sum()),'skate_verts':int((sid>=11).sum())}
  j['asset'].setdefault('extras',{})['caaliArmTargets']='per-rider joint targets (Forge 03:18): Arm x+-0.19 y1.33, ForeArm y1.065, Hand y0.80; shared rider-skeleton.glb unchanged'
  save(fn,j,b); rep[f]={'joints':d,'meshes':mrep}; print(f,mrep)
rp=R+'caali-g-v2.rig-report.json'; r=json.load(open(rp)); r['perRiderJointOffsets_0320']={'note':'Caali G v2 only; bind units (file-native); rotations = shared rest; IBMs recomputed; weights recomputed in bind with the new joints','targets':{'Arm':'x +-0.19, y 1.33','ForeArm':'y 1.065 (along the existing upper-arm direction)','Hand':'y 0.80 (along the existing forearm direction)','twists':'same fraction along their segment','fingers':'translated with Hand (Forge RightHand chain kept)'},'files':rep}
json.dump(r,open(rp,'w'),indent=1)
