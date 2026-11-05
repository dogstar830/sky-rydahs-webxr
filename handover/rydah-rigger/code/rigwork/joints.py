import sys,numpy as np
from glb import *
def worlds(j):
  sk=j['skins'][0]; names={}; W={}
  par={}
  for i,n in enumerate(j['nodes']):
    for c in n.get('children',[]): par[c]=i
  def M(i):
    n=j['nodes'][i]; t=np.array(n.get('translation',[0,0,0])); q=n.get('rotation',[0,0,0,1]); x,y,z,w=q
    R=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
    T=np.eye(4); T[:3,:3]=R; T[:3,3]=t; return T
  def Wm(i): return Wm(par[i])@M(i) if i in par else M(i)
  return {j['nodes'][i]['name']:Wm(i) for i in sk['joints']}
if __name__=='__main__':
  j,b=load(sys.argv[1]); W=worlds(j); ib=acc(j,b,j['skins'][0]['inverseBindMatrices']).reshape(-1,4,4).transpose(0,2,1)
  err=max(np.abs(W[j['nodes'][i]['name']]@ib[k]-np.eye(4)).max() for k,i in enumerate(j['skins'][0]['joints']))
  print('W*IBM-I max',err)
  for n in sys.argv[2:]: print(n,W[n][:3,3].round(4))
