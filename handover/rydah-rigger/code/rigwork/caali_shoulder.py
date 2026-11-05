import json,numpy as np
from glb import *; from joints import worlds
R='/workspace/skyrydahs-characters/wardrobe/riders/'; out={}
for f in ['caali-g-v2','caali-g-v2-hd','caali-g-v2.quest','caali-g-v2.quest-ktx2']:
  fn=R+f+'.rigged.glb'; j,b=load(fn); sk=j['skins'][0]; order=[j['nodes'][i]['name'] for i in sk['joints']]; Wd=worlds(j)
  ix={n.replace('mixamorig:','').replace('mixamorig',''):k for k,n in enumerate(order)}; mr={}
  for ni,nm,p in prims(j,b):
    at=p['attributes']; P=acc(j,b,at['POSITION']).astype(np.float64); J=acc(j,b,at['JOINTS_0']).astype(np.int64); Wt=acc(j,b,at['WEIGHTS_0']).astype(np.float64); n=0
    for S,sg in [('Left',1),('Right',-1)]:
      A=Wd[order[ix[S+'Arm']]][:3,3]; sh=ix[S+'Shoulder']; arm=[ix[S+'Arm'],ix.get(S+'ArmTwist',-1)]
      x=P[:,0]*sg; inner=(A[0]*sg-x); band=(P[:,1]>A[1]-0.30)&(P[:,1]<A[1]+0.08)
      f_=np.clip((inner-0.02)/0.06,0,1)*band      # medial of shoulder pivot -> fade arm weight onto Shoulder
      isarm=np.isin(J,arm); wa=(Wt*isarm).sum(1); move=wa*f_; m=move>1e-4; n+=int(m.sum())
      Wt=np.where(isarm,Wt*(1-f_)[:,None],Wt)
      # put moved weight onto Shoulder slot (existing or the smallest slot)
      has=(J==sh)
      for v in np.where(m)[0]:
        k=np.where(has[v])[0]; k=k[0] if len(k) else int(Wt[v].argmin()); 
        if not has[v].any(): J[v,k]=sh; Wt[v,k]=0
        Wt[v,k]+=move[v]
    Wt/=Wt.sum(1,keepdims=True); J=np.where(Wt>0,J,0)
    for key,arr in [('WEIGHTS_0',Wt.astype(np.float32)),('JOINTS_0',J)]:
      A_=j['accessors'][at[key]]
      if key=='JOINTS_0': arr=arr.astype(np.uint16 if A_['componentType']==5123 else np.uint8)
      vv=j['bufferViews'][A_['bufferView']]; o=vv.get('byteOffset',0)+A_.get('byteOffset',0); b[o:o+arr.nbytes]=arr.tobytes()
    mr[nm]=n
  save(fn,j,b); out[f]=mr; print(f,mr)
rp=R+'caali-g-v2.rig-report.json'; r=json.load(open(rp)); r['perRiderJointOffsets_0320']['shoulderBandSmooth_0330']={'rule':'verts medial of the moved shoulder pivot (2-8 cm, band y Arm-0.30..+0.08) fade Arm/ArmTwist weight onto Shoulder','verts':out}; json.dump(r,open(rp,'w'),indent=1)
