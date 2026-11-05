import numpy as np
X=np.load('xf.npz'); S=np.load('src_pts.npy'); H=S[S[:,0]<0]; P=(X['s']*(X['R']@H.T)).T+X['t']
for nm,c,xc in (('F',(-0.0778,-0.051),-0.006),('R',(0.1739,-0.046),0.0184)):
  m=np.abs(P[:,0]-xc)<0.02; r=np.hypot(P[m,1]-c[0],P[m,2]-c[1]); ang=np.arctan2(P[m,2]-c[1],P[m,1]-c[0])
  low=(ang<-0.3)&(ang>-2.8)  # lower half (below axle)
  h,e=np.histogram(r[low],bins=np.arange(0,0.12,0.004)); print(nm,list(zip(e[:-1].round(3),h)))
  # x extent of tyre at r~0.06
  mm=(np.hypot(P[:,1]-c[0],P[:,2]-c[1])>0.055)&(np.hypot(P[:,1]-c[0],P[:,2]-c[1])<0.08)&(P[:,2]<c[1]-0.03)
  print(' x tyre pct',np.percentile(P[mm,0],[2,50,98]).round(4),'zmin',P[:,2].min().round(4))
