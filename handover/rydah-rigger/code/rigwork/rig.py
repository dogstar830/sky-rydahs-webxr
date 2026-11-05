# Rydah Rigger 2026-10-30: skin static Meshy riders to the shared 91-joint skeleton (+ Anika springs). numpy only.
import json,sys,numpy as np
from glb import *
from scipy.spatial import cKDTree
SK=json.load(open('/workspace/skyrydahs-characters/shared/skeleton/rider-skeleton.bones.json'))['bones']
K=(1.7+0.152)/1.916; DECK=0.152     # file-native frame (loadIkki s=refH/(1.7+IKKI_DECK_REST)); wheels at -DECK
M=lambda s:'mixamorig:'+s
def q2m(q):
  x,y,z,w=q; return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def m2q(R):
  t=np.trace(R)
  if t>0: s=np.sqrt(t+1)*2; q=[(R[2,1]-R[1,2])/s,(R[0,2]-R[2,0])/s,(R[1,0]-R[0,1])/s,.25*s]
  elif R[0,0]>R[1,1] and R[0,0]>R[2,2]: s=np.sqrt(1+R[0,0]-R[1,1]-R[2,2])*2; q=[.25*s,(R[0,1]+R[1,0])/s,(R[0,2]+R[2,0])/s,(R[2,1]-R[1,2])/s]
  elif R[1,1]>R[2,2]: s=np.sqrt(1+R[1,1]-R[0,0]-R[2,2])*2; q=[(R[0,1]+R[1,0])/s,.25*s,(R[1,2]+R[2,1])/s,(R[0,2]-R[2,0])/s]
  else: s=np.sqrt(1+R[2,2]-R[0,0]-R[1,1])*2; q=[(R[0,2]+R[2,0])/s,(R[1,2]+R[2,1])/s,.25*s,(R[1,0]-R[0,1])/s]
  q=np.array(q); return q/np.linalg.norm(q)
def rot_between(a,b):
  a=a/np.linalg.norm(a); b=b/np.linalg.norm(b); v=np.cross(a,b); c=a@b; s=np.linalg.norm(v)
  if s<1e-9: return np.eye(3)
  vx=np.array([[0,-v[2],v[1]],[v[2],0,-v[0]],[-v[1],v[0],0]]); return np.eye(3)+vx+vx@vx*((1-c)/s**2)
NAMES=[b['name'] for b in SK]; PAR={b['name']:b['parent'] for b in SK}
# shared rest world rotations
WR={}; WP={}
for b in SK:
  R=q2m(b['r']); t=np.array(b['t'])
  if b['parent'] is None: WR[b['name']]=R; WP[b['name']]=t
  else: p=b['parent']; WR[b['name']]=WR[p]@R; WP[b['name']]=WP[p]+WR[p]@t
assert max(np.abs(WP[b['name']]-np.array(b['world'])).max() for b in SK)<2e-4
def subtree(root):
  out=[root]; ch=True
  while ch:
    ch=False
    for n in NAMES:
      if PAR[n] in out and n not in out: out.append(n); ch=True
  return out

def native(P): return P*K+np.array([0,-DECK,0])
def fit(P,sid,H,slots=None):
  """bind joint world positions (native frame) + per-side arm rotations for the A-pose mesh pose"""
  r=H/1.916; Pn=native(P); sk=sid>=11; nb=Pn[~sk]
  J={n:WP[n]*r for n in NAMES}
  top=Pn[:,1].max(); info={'r':r,'top':top}
  ank={}
  for sd,S in [(1,'Left'),(-1,'Right')]:
    q=Pn[sk&(Pn[:,0]*sd>0)]; mn,mx=q.min(0),q.max(0); hs=mx[1]-mn[1]; ks=hs/0.329
    A=np.array([(mn[0]+mx[0])/2, mn[1]+0.234*ks, mn[2]+0.181/0.387*(mx[2]-mn[2])]); ank[S]=(A,ks)
    info[S+'_skate']={'h':hs,'scale':ks,'ankle':A.round(4).tolist()}
  sole=np.mean([ank[s][0][1]-0.07*ank[s][1] for s in ank]); Hb=top-sole
  upY=sole+0.52*Hb; hipsY=upY+(WP[M('Hips')][1]-WP[M('LeftUpLeg')][1])*r
  # torso: Hips..HeadTop affine in y (keeps x/z * r)
  h0=WP[M('Hips')][1]*r; ht0=WP[M('HeadTop_End')][1]*r; htN=top-0.018*r; fy=(htN-hipsY)/(ht0-h0); info['torso_fy']=fy
  legs=set(subtree(M('LeftUpLeg'))+subtree(M('RightUpLeg')))
  for n in NAMES:
    if n in legs: continue
    p=WP[n]*r; J[n]=np.array([p[0],hipsY+(p[1]-h0)*fy,p[2]])
  arms={}
  for sd,S in [(1,'Left'),(-1,'Right')]:
    A,ks=ank[S]; U=J[M(S+'UpLeg')]=np.array([WP[M(S+'UpLeg')][0]*r,upY,WP[M(S+'UpLeg')][2]*r])
    # knee on the U->A line at the shared fraction, plus the shared off-line offset (scaled)
    u0,k0,a0=WP[M(S+'UpLeg')],WP[M(S+'Leg')],WP[M(S+'Foot')]; f=(k0-u0)@(a0-u0)/((a0-u0)@(a0-u0)); off=(k0-(u0+f*(a0-u0)))*r
    J[M(S+'Leg')]=U+f*(A-U)+off; J[M(S+'Foot')]=A
    for n in subtree(M(S+'Foot'))[1:]+subtree(S[0]+'_AT_Root'):
      J[n]=A+(WP[n]-WP[M(S+'Foot')])*ks
    # arm: centreline of the A-pose sleeve (slice centroids), wrist = centreline point one hand-length before the fingertip
    side=nb[nb[:,0]*sd>0]; tip=side[np.argmax(abs(side[:,0]))]
    Sh=J[M(S+'Arm')]; d0=(tip-Sh)/np.linalg.norm(tip-Sh); L=np.linalg.norm(tip-Sh)
    rel=side-Sh; u=rel@d0; rad=np.linalg.norm(rel-np.outer(u,d0),axis=1)
    cs=[]
    for f in np.linspace(0.2,0.7,11):
      m=(abs(u-f*L)<0.015)&(rad<0.14*r)
      if m.sum()>10: cs.append(side[m].mean(0))
    cs=np.array(cs); c0=cs.mean(0); _,_,vt=np.linalg.svd(cs-c0); d=vt[0]*np.sign(vt[0]@d0)
    hand0=np.linalg.norm(WP[M(S+'HandMiddle4')]-WP[M(S+'Hand')])
    hl=hand0*(L/np.linalg.norm(WP[M(S+'HandMiddle4')]-WP[M(S+'Arm')]))
    wr=c0+d*(((tip-c0)@d)-hl)
    fa=np.linalg.norm(wr-Sh)/np.linalg.norm(WP[M(S+'Hand')]-WP[M(S+'Arm')])
    for n in subtree(M(S+'Arm'))[1:]: J[n]=Sh+(WP[n]-WP[M(S+'Arm')])*fa
    Rarm=rot_between(J[M(S+'Hand')]-Sh, wr-Sh)
    arms[S]=Rarm; info[S+'_arm']={'scale':float(fa),'deg':float(np.degrees(np.arccos(np.clip((np.trace(Rarm)-1)/2,-1,1)))),'tip':tip.round(3).tolist(),'wrist':wr.round(3).tolist(),'centroids':len(cs)}
  return J,arms,info

def extra_bones_anika(J,Pm,slots):
  """braid chains (2x5) under Head, skirt (6) under Hips. Returns list of (name,parent,head,tail) in mesh-pose == bind (head/torso don't move)."""
  ex=[]; info={}
  hair=(slots=='hair')
  for sd,S in [(1,'L'),(-1,'R')]:
    q=Pm[hair&(Pm[:,0]*sd>0.035)]
    ytop=q[:,1].max() if False else None
    # braid = hair below the jaw line (the hair cap above stays 100% Head)
    jaw=J[M('Head')][1]+0.02; br=q[q[:,1]<jaw]
    ys=np.linspace(br[:,1].max(),br[:,1].min(),6)
    pts=[]
    for i,y in enumerate(ys):
      m=abs(br[:,1]-y)<0.015
      if m.sum()<5: m=np.argsort(abs(br[:,1]-y))[:20]
      c=br[m].mean(0); c[1]=y; pts.append(c)
    pts=np.array(pts); info['Braid'+S]={'points':pts.round(4).tolist(),'len':float(np.linalg.norm(np.diff(pts,axis=0),axis=1).sum()),'verts':int(len(br))}
    par=M('Head')
    for i in range(5):
      n=f'Anika_Braid{S}_{i+1:02d}'; ex.append((n,par,pts[i],pts[i+1])); par=n
  sk=Pm[slots=='skirt']; ytop=0.99*K-DECK+0.0 ; yt=np.percentile(sk[:,1],98); yh=np.percentile(sk[:,1],1)
  c=np.array([J[M('Hips')][0],0,J[M('Hips')][2]])
  for i in range(6):
    a=np.radians(60*i); d=np.array([np.sin(a),0,np.cos(a)])
    def rad(y):
      m=(abs(sk[:,1]-y)<0.02); v=sk[m]-c; ang=np.arctan2(v[:,0],v[:,2]); dd=np.angle(np.exp(1j*(ang-a))); mm=abs(dd)<np.radians(15)
      return np.percentile(v[mm][:,[0,2]]@d[[0,2]],80) if mm.sum()>3 else 0.12
    h=c+d*rad(yt-0.02); h[1]=yt-0.02; t=c+d*rad(yh+0.01); t[1]=yh+0.01
    ex.append((f'Anika_Skirt_{i:02d}',M('Hips'),h,t))
  info['skirt']={'top':float(yt),'hem':float(yh),'verts':int(len(sk))}
  return ex,info

DEF={}  # deform bone -> tail joint
for S in ['Left','Right']:
  DEF.update({M(S+'Shoulder'):M(S+'Arm'),M(S+'Arm'):M(S+'ForeArm'),M(S+'ForeArm'):M(S+'Hand'),M(S+'Hand'):M(S+'HandMiddle1'),
    M(S+'UpLeg'):M(S+'Leg'),M(S+'Leg'):M(S+'Foot'),M(S+'Foot'):M(S+'ToeBase'),M(S+'ToeBase'):M(S+'Toe_End')})
  for f in ['Thumb','Index','Middle','Ring','Pinky']:
    for k in (1,2,3): DEF[M(f'{S}Hand{f}{k}')]=M(f'{S}Hand{f}{k+1}')
DEF.update({M('Hips'):M('Spine'),M('Spine'):M('Spine1'),M('Spine1'):M('Spine2'),M('Spine2'):M('Neck'),M('Neck'):M('Head'),M('Head'):M('HeadTop_End')})
DB=list(DEF)
def adj_of(n):
  a={n}
  if PAR.get(n) in DEF: a.add(PAR[n])
  for c in DB:
    if PAR[c]==n: a.add(c)
  return a
ADJ={n:adj_of(n) for n in DB}
def segdist(P,a,b):
  ab=b-a; t=np.clip(((P-a)@ab)/(ab@ab),0,1); return np.linalg.norm(P-(a+t[:,None]*ab),axis=1),t
def sigma(n,r):
  if 'Hand' in n and n[-1] in '123' : return 0.006*r
  if n.endswith('Hand'): return 0.012*r
  if 'Foot' in n or 'Toe' in n: return 0.015*r
  return 0.028*r

THIGHGUARD=False
def weights(Pm,tris,sid,slots,Jm,r,extra=None):
  """Pm mesh-pose positions; Jm mesh-pose joints. Returns dict bone->weights (V,)"""
  key=np.round(Pm/1e-5).astype(np.int64); _,uid,inv=np.unique(key,axis=0,return_index=True,return_inverse=True); inv=inv.ravel()
  U=Pm[uid]; nU=len(U); Ws=np.zeros((nU,len(DB)),np.float32)
  D=np.zeros((nU,len(DB)),np.float32); T=np.zeros((nU,len(DB)),np.float32)
  for i,n in enumerate(DB):
    d,t=segdist(U,Jm[n],Jm[DEF[n]])
    if n==M('Hips'):   # pelvis: also Hips -> mid UpLegs
      d2,_=segdist(U,Jm[n],(Jm[M('LeftUpLeg')]+Jm[M('RightUpLeg')])/2); d=np.minimum(d,d2)
    cap=None
    if n.endswith('Arm') and 'Fore' not in n: cap=0.13
    elif n.endswith('ForeArm'): cap=0.11
    elif n.endswith('Hand'): cap=0.065
    elif 'Hand' in n: cap=0.035
    if cap: d=np.where(d>cap*r,1e3,d)     # radial cap: jacket/torso next to an A-pose arm is never arm-weighted
    D[:,i]=d; T[:,i]=t
  if THIGHGUARD:   # hanging-arm bind: pants/pocket verts nearer a thigh than the hand chain never go to the arm
    dl=np.minimum(segdist(U,Jm[M('LeftUpLeg')],Jm[M('LeftLeg')])[0],segdist(U,Jm[M('RightUpLeg')],Jm[M('RightLeg')])[0])
    for i,n in enumerate(DB):
      if ('Hand' in n or 'ForeArm' in n): D[:,i]=np.where(dl<D[:,i]+0.01,1e3,D[:,i])
  near=D.argmin(1)
  for i,n in enumerate(DB):
    sel=near==i; cand=[DB.index(a) for a in ADJ[n]]
    for c in cand:
      Ws[sel,c]=np.exp(-np.minimum(D[sel,c]-D[sel,i],50)/sigma(DB[c],r))
  # smooth over the welded surface graph (2 passes)
  tu=inv[tris]; e=np.r_[tu[:,[0,1]],tu[:,[1,2]],tu[:,[2,0]]]; e=np.r_[e,e[:,::-1]]
  from scipy.sparse import coo_matrix
  A=coo_matrix((np.ones(len(e),np.float32),(e[:,0],e[:,1])),shape=(nU,nU)).tocsr(); deg=np.asarray(A.sum(1)).ravel()+1e-9
  Ws/=Ws.sum(1,keepdims=True)
  for _ in range(2): Ws=0.5*Ws+0.5*(A@Ws)/deg[:,None]
  W={n:Ws[:,i] for i,n in enumerate(DB)}
  # twist gradients
  for S in ['Left','Right']:
    ia=DB.index(M(S+'Arm')); ifa=DB.index(M(S+'ForeArm'))
    wa=W[M(S+'Arm')]; u=T[:,ia]; fat=0.5*np.clip((0.5-u)/0.5,0,1)   # shoulder half -> ArmTwist (counter-roll share)
    W[M(S+'ArmTwist')]=wa*fat; W[M(S+'Arm')]=wa*(1-fat)
    wf=W[M(S+'ForeArm')]; u=T[:,ifa]; ft=0.5*np.clip(u,0,1)              # ForeArmTwist 0 -> 0.5 elbow -> wrist
    W[M(S+'ForeArmTwist')]=wf*ft; W[M(S+'ForeArm')]=wf*(1-ft)
  Wv={n:w[inv] for n,w in W.items()}; V=len(Pm)
  def setrig(mask,bone):
    for n in Wv: Wv[n]=np.where(mask,0,Wv[n])
    if bone not in Wv: Wv[bone]=np.zeros(V,np.float32)
    Wv[bone]=np.where(mask,1,Wv[bone])
  # skates: rigid to the foot (spec §1 shell rigid, toe 0%), by side
  sk=sid>=11
  setrig(sk&(Pm[:,0]>0),M('LeftFoot')); setrig(sk&(Pm[:,0]<=0),M('RightFoot'))
  if slots is not None:
    setrig((slots=='hair')&(Pm[:,1]>Jm[M('Head')][1]+0.02),M('Head'))
    lw=slots=='legwear'                                   # thigh-high top band: no Hips bleed
    if M('Hips') in Wv: Wv[M('Hips')]=np.where(lw,0,Wv[M('Hips')])
  if extra is not None: extra(Wv,Pm)
  return Wv

def pack(Wv,order,V):
  names=[n for n in order if n in Wv]; Wm=np.stack([Wv[n] for n in names],1).astype(np.float64); Wm[Wm<1e-4]=0
  idx=np.argsort(-Wm,1)[:,:4]; w=np.take_along_axis(Wm,idx,1); w[w<0.01]=0; s=w.sum(1,keepdims=True); 
  bad=s[:,0]<=0
  w=w/np.where(s>0,s,1); j=np.array([order.index(names[k]) for k in range(len(names))])[idx]
  j=np.where(w>0,j,0); return j.astype(np.uint8),w.astype(np.float32),bad
