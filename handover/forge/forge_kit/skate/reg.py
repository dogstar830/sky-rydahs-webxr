import numpy as np, itertools
from scipy.spatial import cKDTree
S=np.load('src_pts.npy'); O=np.load('old_pts.npy')
rng=np.random.default_rng(0)
def umeyama(A,B):  # find s,R,t: B ~ s R A + t
  ma,mb=A.mean(0),B.mean(0); a,b=A-ma,B-mb; U,D,Vt=np.linalg.svd(b.T@a/len(A)); Sg=np.eye(3)
  if np.linalg.det(U@Vt)<0: Sg[2,2]=-1
  R=U@Sg@Vt; s=np.trace(np.diag(D)@Sg)/a.var(0).sum(); return s,R,mb-s*R@ma
best=None
for half in (0,1):
  H=S[S[:,0]>0] if half else S[S[:,0]<0]; H=H[rng.choice(len(H),20000,replace=False)]
  tO=cKDTree(O)
  # PCA frames
  def frame(X): c=X.mean(0); w,v=np.linalg.eigh(np.cov((X-c).T)); return c,v[:,::-1],np.sqrt(w[::-1])
  cH,vH,sH=frame(H); cO,vO,sO=frame(O); s0=(sO/sH).mean()
  for signs in itertools.product((1,-1),repeat=3):
   for perm in itertools.permutations(range(3)):
    M=np.zeros((3,3))
    for i,p in enumerate(perm): M[:,p]=vO[:,i]*0  # placeholder
    R0=vO[:,list(perm)]@np.diag(signs)@vH.T
    if np.linalg.det(R0)<0: continue
    s,R,t=s0*(sO[list(perm)]/sH).mean()/s0 if False else s0,R0,cO-s0*R0@cH
    for it in range(40):
      X=(s*(R@H.T)).T+t
      # O->X correspondences (old points onto source surface) more robust: for each old pt nearest transformed src
      tX=cKDTree(X); d,i=tX.query(O); keep=d<np.percentile(d,90)
      s,R,t=umeyama(H[i[keep]],O[keep])
    X=(s*(R@H.T)).T+t; d1,_=cKDTree(X).query(O); d2,_=tO.query(X)
    err=np.median(d1)+np.median(d2)
    if best is None or err<best[0]: best=(err,half,s,R,t,perm,signs)
print('BEST err',best[0],'half',best[1],'s',best[2]); print(best[3]); print(best[4])
np.savez('xf.npz',s=best[2],R=best[3],t=best[4],half=best[1])
