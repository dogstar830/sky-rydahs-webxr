import sys,json,numpy as np
from rig import *
from glb import *
RID=sys.argv[1]; files=sys.argv[2].split(','); outdir=sys.argv[3]
H={'anika':1.68,'caali':1.916}[RID]
def mesh_data(j,b,p):
  a=p['attributes']; P=acc(j,b,a['POSITION']).astype(np.float64); C=acc(j,b,a['COLOR_0'])
  ct=j['accessors'][a['COLOR_0']]['componentType']; C=C/65535. if ct==5123 else (C/255. if ct==5121 else C)
  sid=np.floor(C[:,0]*16+.5); tris=acc(j,b,p['indices']).reshape(-1,3).astype(np.int64); return P,sid,tris
# ---- fit once per rider from the rider LOD0
j0,b0=load('dec/'+files[0]); n0,nm0,p0=prims(j0,b0)[0]; assert 'LOD0' in nm0,nm0
P0,sid0,_=mesh_data(j0,b0,p0)
J,arms,finfo=fit(P0,sid0,H)
r=finfo['r']
def mesh_pose(J):
  Jm=dict(J)
  for S in ['Left','Right']:
    Sh=J[M(S+'Arm')]; R=arms[S]
    for n in subtree(M(S+'Arm')): Jm[n]=Sh+R@(J[n]-Sh)
  return Jm
Jm=mesh_pose(J)
SL0=None; extra_def=None; EX=[]
if RID=='anika':
  c0=vcolors(j0,b0,p0); uv0=acc(j0,b0,p0['attributes']['TEXCOORD_0'])
  SL0=slots_anika(native(P0)/1,c0,uv0)   # thresholds are in the delivered frame -> classify on raw P0 instead
  SL0=slots_anika(P0,c0,uv0)
  Pm0=native(P0)
  # refine skirt: not thigh (inside UpLeg capsule r .085)
  for S in ['Left','Right']:
    d,_=segdist(Pm0,Jm[M(S+'UpLeg')],Jm[M(S+'Leg')]); SL0[(SL0=='skirt')&(d<0.085*r/0.877*0.877)]='body'
  EX,xinfo=extra_bones_anika(Jm,Pm0,SL0); finfo['extra']=xinfo
EXN=[e[0] for e in EX]; ORDER=NAMES+EXN
def bind_mats():
  Wm={}
  for n in NAMES:
    T=np.eye(4); T[:3,:3]=WR[n]; T[:3,3]=J[n]; Wm[n]=T
  for n,par,h,t in EX:
    T=np.eye(4); T[:3,:3]=rot_between(np.array([0,1.,0]),t-h) if True else np.eye(3); T[:3,3]=h; Wm[n]=T
  return Wm
WM=bind_mats()
def anika_extra(Wv,Pm,slots):
  V=len(Pm)
  def zero(mask):
    for n in Wv: Wv[n]=np.where(mask,0,Wv[n])
  # braids (fused into the top in the Meshy shell): soft tube falloff around the braid polyline, so nothing tears
  for S,sd in [('L',1),('R',-1)]:
    pts=np.array([e[2] for e in EX if e[0].startswith(f'Anika_Braid{S}')]+[EX[[e[0] for e in EX].index(f'Anika_Braid{S}_05')][3]])
    best=np.full(V,1e9); s_=np.zeros(V)
    for i in range(5):
      d,t=segdist(Pm,pts[i],pts[i+1]); upd=d<best; best[upd]=d[upd]; s_[upd]=i+t[upd]
    side=Pm[:,0]*sd>0.02
    wb=np.where(side,1-np.clip((best-0.010)/(0.026-0.010),0,1),0); wb=wb*wb*(3-2*wb)
    wb*=np.clip(s_/0.6,0,1)      # root of bone 01 fades into Head (tie point)
    m=wb>1e-3; idx=np.where(m)[0]; s_=np.clip(s_[m],0,4.999); i0=np.floor(s_).astype(int); f=s_-i0; w=wb[m]
    for n in Wv: Wv[n][idx]*=1-w
    names=[f'Anika_Braid{S}_{k+1:02d}' for k in range(5)]
    for n in names: Wv.setdefault(n,np.zeros(V,np.float32))
    hb=(1-np.clip(s_/0.6,0,1))   # unused share already left on body/Head
    for k,n in enumerate(names):
      bw=np.where(i0==k,1-np.clip((f-0.7)/0.3,0,1)*0.5-np.where(k>0,np.clip((0.3-f)/0.3,0,1)*0.5,0),0)
      bw+=np.where(i0==k-1,np.clip((f-0.7)/0.3,0,1)*0.5,0)
      bw+=np.where(i0==k+1,np.clip((0.3-f)/0.3,0,1)*0.5,0)
      Wv[n][idx]+=w*bw
  # skirt: Hips at the waistband -> skirt bones at the hem; 2 nearest sectors
  m=slots=='skirt'; q=Pm[m]; idx=np.where(m)[0]; xi=finfo['extra']['skirt']; yt,yh=xi['top'],xi['hem']
  t=np.clip((yt-q[:,1])/(yt-yh),0,1); s=np.clip(t/0.45,0,1); s=s*s*(3-2*s)
  c=np.array([J[M('Hips')][0],0,J[M('Hips')][2]]); ang=(np.degrees(np.arctan2(q[:,0]-c[0],q[:,2]-c[2]))%360)/60.; a0=np.floor(ang).astype(int)%6; al=ang-np.floor(ang)
  zero(m)
  for k in range(6): Wv.setdefault(f'Anika_Skirt_{k:02d}',np.zeros(V,np.float32))
  for k in range(6):
    w=np.where(a0==k,1-al,0)+np.where((a0+1)%6==k,al,0); Wv[f'Anika_Skirt_{k:02d}'][idx]=s*w
  Wv[M('Hips')][idx]=1-s
  # gold chain / anything else in the skirt band outside the thighs: rigid Hips
  band=(slots=='body')&(Pm[:,1]<yt-0.01)&(Pm[:,1]>yh-0.05)&(abs(Pm[:,0])<0.25*r/0.877)
  for S in ['Left','Right']:
    d,_=segdist(Pm,Jm[M(S+'UpLeg')],Jm[M(S+'Leg')]); band&=d>0.085
  zero(band); Wv[M('Hips')][band]=1
  return Wv
report={'rider':RID,'H':H,'fit':finfo,'files':{}}
for f in files:
  j,b=load('dec/'+f); qsrc=None
  if RID=='anika' and 'ktx2' in f: qj,qb=load('dec/'+f.replace('.quest-ktx2','.quest'))
  bones_used=set(); rep={}
  for ni,nm,p in prims(j,b):
    P,sid,tris=mesh_data(j,b,p); Pm=native(P)
    slots=None
    if RID=='anika':
      if 'ktx2' in f:
        qp=[pp for _,nn,pp in prims(qj,qb) if nn==nm][0]; QP=acc(qj,qb,qp['attributes']['POSITION']); qs=slots_anika(QP,vcolors(qj,qb,qp),acc(qj,qb,qp['attributes']['TEXCOORD_0']))
        _,ii=cKDTree(QP).query(P); slots=qs[ii]
      else: slots=slots_anika(P,vcolors(j,b,p),acc(j,b,p['attributes']['TEXCOORD_0']))
      for S in ['Left','Right']:
        d,_=segdist(Pm,Jm[M(S+'UpLeg')],Jm[M(S+'Leg')]); slots[(slots=='skirt')&(d<0.085)]='body'
    lod=int(nm.split('LOD')[1][0])
    Wv=weights(Pm,tris,sid,slots,Jm,r,extra=(lambda W,Pq,sl=slots: anika_extra(W,Pq,sl)) if RID=='anika' else None)
    if RID=='anika' and lod==2:   # LOD2: braid/skirt frozen -> fold the chains into their parents
      for n in list(Wv):
        if n.startswith('Anika_Braid'): Wv[M('Head')]=Wv[M('Head')]+Wv.pop(n)
        elif n.startswith('Anika_Skirt'): Wv[M('Hips')]=Wv[M('Hips')]+Wv.pop(n)
    jj,ww,bad=pack(Wv,ORDER,len(P))
    # re-pose: arm subtree back to the shared bind (arms hanging, as the poser expects)
    a=p['attributes']; Nn=acc(j,b,a['NORMAL']).astype(np.float64)
    armw={S:sum(Wv[n] for n in subtree(M(S+'Arm')) if n in Wv) for S in ['Left','Right']}
    Pb=Pm.copy(); Nb=Nn.copy()
    for S in ['Left','Right']:
      Sh=J[M(S+'Arm')]; Rt=arms[S].T; w=np.clip(armw[S],0,1)[:,None]
      Pb=Pb+w*(((Pm-Sh)@Rt.T+Sh)-Pm); Nb=Nb+w*((Nn@Rt.T)-Nn)
    Nb/=np.linalg.norm(Nb,axis=1,keepdims=True)+1e-12
    # write POSITION / NORMAL / _WC in place (same count/type)
    def put(ai,arr):
      A=j['accessors'][ai]; v=j['bufferViews'][A['bufferView']]; o=v.get('byteOffset',0)+A.get('byteOffset',0); arr=np.ascontiguousarray(arr.astype(np.float32)); b[o:o+arr.nbytes]=arr.tobytes(); return arr
    pa=put(a['POSITION'],Pb); j['accessors'][a['POSITION']]['min']=pa.min(0).tolist(); j['accessors'][a['POSITION']]['max']=pa.max(0).tolist()
    put(a['NORMAL'],Nb)
    WC=acc(j,b,a['_WC']).astype(np.float64); nz=np.abs(WC).sum(1)>0; WC[nz]=native(WC[nz]); wca=put(a['_WC'],WC)
    if 'min' in j['accessors'][a['_WC']]: j['accessors'][a['_WC']]['min']=wca.min(0).tolist(); j['accessors'][a['_WC']]['max']=wca.max(0).tolist()
    p['attributes']['JOINTS_0']=add(j,b,jj,5121,'VEC4',34962); p['attributes']['WEIGHTS_0']=add(j,b,ww,5126,'VEC4',34962)
    j['nodes'][ni]['skin']=0
    used=np.unique(jj[ww>0]); bones_used|=set(ORDER[k] for k in used)
    rep[nm]={'tris':len(tris),'verts':len(P),'maxinf':int((ww>0).sum(1).max()),'unweighted':int(bad.sum()),'wsum_err':float(abs(ww.sum(1)-1).max()),
             'bone_verts':{k:int(((jj==ORDER.index(k))&(ww>0)).any(1).sum()) for k in ORDER if k.startswith('Anika')},
             'skate_rigid':bool(np.all(ww[sid>=11,0]==1)), 'slots':({k:int((slots==k).sum()) for k in np.unique(slots)} if slots is not None else None)}
  # joints nodes
  base=len(j['nodes']); idx={n:base+i for i,n in enumerate(ORDER)}
  parents={**PAR,**{e[0]:e[1] for e in EX}}
  for n in ORDER:
    Wn=WM[n]; pn=parents[n]
    if pn is None: R=Wn[:3,:3]; t=Wn[:3,3]
    else: Wp=WM[pn]; R=Wp[:3,:3].T@Wn[:3,:3]; t=Wp[:3,:3].T@(Wn[:3,3]-Wp[:3,3])
    nd={'name':n,'translation':[float(x) for x in t],'rotation':[float(x) for x in m2q(R)]}
    if n.startswith('Anika_'):
      ch='braid' if 'Braid' in n else 'skirt'
      nd['extras']={'spring':{'chain':n.rsplit('_',1)[0],'index':int(n.rsplit('_',1)[1]),'kind':ch,'tail':[float(x) for x in (WM[n][:3,:3].T@([e for e in EX if e[0]==n][0][3]-WM[n][:3,3]))]}}
    j['nodes'].append(nd)
  for n in ORDER:
    ch=[idx[c] for c in ORDER if parents[c]==n]
    if ch: j['nodes'][idx[n]]['children']=ch
  arm_node=len(j['nodes']); j['nodes'].append({'name':'RiderArmature','children':[idx[M('Hips')]]})
  j['scenes'][j.get('scene',0)]['nodes'].append(arm_node)
  IBM=np.stack([np.linalg.inv(WM[n]).T.reshape(-1) for n in ORDER])   # column-major
  j['skins']=[{'name':'RiderSkin','joints':[idx[n] for n in ORDER],'inverseBindMatrices':add(j,b,IBM,5126,'MAT4'),'skeleton':idx[M('Hips')]}]
  if RID=='anika':
    j['skins'][0]['extras']={'springChains':{
      'Anika_BraidL':{'bones':[f'Anika_BraidL_{i:02d}' for i in range(1,6)],'parent':'mixamorig:Head','k':60,'kRoot':90,'damping':0.35,'maxSwingRootDeg':70,'maxSwingLinkDeg':35,'gravity':True,'colliders':'Neck,Spine2(r.11),Shoulders(r.07),UpLegs(r.08)','lod':'LOD0 only, frozen in lite/LOD1+ beyond 14 m; LOD2 weights folded into Head'},
      'Anika_BraidR':{'bones':[f'Anika_BraidR_{i:02d}' for i in range(1,6)],'parent':'mixamorig:Head','k':60,'kRoot':90,'damping':0.35,'maxSwingRootDeg':70,'maxSwingLinkDeg':35,'gravity':True},
      'Anika_Skirt':{'bones':[f'Anika_Skirt_{i:02d}' for i in range(6)],'parent':'mixamorig:Hips','sectors':'00 front,01 front-L,02 back-L,03 back,04 back-R,05 front-R','k':80,'damping':0.5,'thighRule':'push out by UpLeg flex in sector, front x0.6','colliders':'UpLeg capsules r .085 +1 cm','lod':'LOD2 folded into Hips'}},
      'boneAxis':'+Y (head->tail)'}
  j.setdefault('asset',{})['extras']={'rig':'Rydah Rigger 2026-10-30, shared rider-skeleton 91 joints'+(' + 16 Anika springs' if EXN else ''),'bind':'shared rest rotations, joints snapped to the mesh (lengths only); arms re-posed from the Meshy A-pose to the shared hanging bind','heightRef':H}
  save(outdir+'/'+f,j,b); report['files'][f]={'meshes':rep,'joints':len(ORDER),'bones_with_weights':len(bones_used)}
  print('wrote',f,{k:(v['tris'],v['maxinf'],v['unweighted']) for k,v in rep.items()})
json.dump(report,open(outdir+f'/{RID}-rig-report.json','w'),indent=1,default=lambda o: o.tolist() if hasattr(o,'tolist') else str(o))
print(json.dumps(finfo,default=str)[:3000])
