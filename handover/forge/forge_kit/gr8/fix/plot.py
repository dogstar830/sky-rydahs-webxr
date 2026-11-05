import sys; sys.path.insert(0,'.'); from glbio import *
from PIL import Image,ImageDraw
f,out=sys.argv[1:3]; j,b=load(f); sk=j['skins'][0]; jn=[j['nodes'][i]['name'] for i in sk['joints']]
IBM=acc(j,b,sk['inverseBindMatrices']).reshape(-1,4,4).transpose(0,2,1); JP=np.array([np.linalg.inv(m)[:3,3] for m in IBM])
p=j['meshes'][0]['primitives'][0]; P=acc(j,b,p['attributes']['POSITION'])
S=500; im=Image.new('RGB',(1000,1000),'white'); d=ImageDraw.Draw(im)
X=lambda x,y:(int(500+x*S),int(950-y*S))
for q in P[::3]: d.point(X(q[0],q[1]),fill=(150,150,150))
par={}
for i,n in enumerate(j['nodes']):
    for c in n.get('children',[]): par[c]=i
for k,ji in enumerate(sk['joints']):
    pi=par.get(ji)
    if pi in sk['joints']:
        a=JP[sk['joints'].index(pi)]; c=JP[k]; d.line([X(a[0],a[1]),X(c[0],c[1])],fill=(255,0,0),width=2)
    d.ellipse([X(JP[k][0],JP[k][1])[0]-2,X(JP[k][0],JP[k][1])[1]-2,X(JP[k][0],JP[k][1])[0]+2,X(JP[k][0],JP[k][1])[1]+2],fill=(0,0,255))
im.save(out)
