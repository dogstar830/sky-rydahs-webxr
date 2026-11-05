import numpy as np
from scipy.sparse import coo_matrix
from glb import hls
def braid_mask(P,c,slots,tris,jawY_deliv=1.47,thr=9.0,maxit=400):
  """grow the fused braids from the hair seeds below the jaw over hair-coloured verts (welded graph)"""
  key=np.round(P/1e-5).astype(np.int64); _,uid,inv=np.unique(key,axis=0,return_index=True,return_inverse=True); inv=inv.ravel()
  n=len(uid); t=inv[tris]; e=np.r_[t[:,[0,1]],t[:,[1,2]],t[:,[2,0]]]; e=np.r_[e,e[:,::-1]]
  A=coo_matrix((np.ones(len(e),np.float32),(e[:,0],e[:,1])),shape=(n,n)).tocsr()
  hair=np.zeros(n,bool); np.logical_or.at(hair,inv,slots=='hair')
  Uc=np.zeros((n,3)); Uc[inv]=c; U=P[uid]
  seed=hair&(U[:,1]<jawY_deliv)&(np.abs(U[:,0])>0.035)
  f=lambda cc: np.c_[cc/(cc.sum(1,keepdims=True)+1e-4), cc.mean(1)]
  F=f(Uc); mu=F[seed].mean(0); cov=np.cov(F[seed].T)+np.eye(4)*1e-5; ic=np.linalg.inv(cov); d=np.einsum('ij,jk,ik->i',F-mu,ic,F-mu)
  ok=(d<thr)&(U[:,1]<jawY_deliv)&(U[:,1]>0.9)&(np.abs(U[:,0])>0.02)
  m=seed.copy()
  for _ in range(maxit):
    nm=m|((A@m.astype(np.float32))>0)&ok
    if nm.sum()==m.sum(): break
    m=nm
  return m[inv]
