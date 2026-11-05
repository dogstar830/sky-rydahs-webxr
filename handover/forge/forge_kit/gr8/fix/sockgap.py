import sys;sys.path.insert(0,'/workspace/forge_kit/gr8/fix');from glbio import *;import numpy as np
def ptri(p,A,B,C):  # exact closest distance point->triangles (Ericson)
    ab=B-A;ac=C-A;ap=p-A;d1=(ab*ap).sum(1);d2=(ac*ap).sum(1);bp=p-B;d3=(ab*bp).sum(1);d4=(ac*bp).sum(1);cp=p-C;d5=(ab*cp).sum(1);d6=(ac*cp).sum(1)
    va=d3*d6-d5*d4;vb=d5*d2-d1*d6;vc=d1*d4-d3*d2;den=1/np.where(va+vb+vc==0,1e-12,va+vb+vc);v=vb*den;w=vc*den;Q=A+ab*v[:,None]+ac*w[:,None]
    m=(d1<=0)&(d2<=0);Q[m]=A[m];m=(d3>=0)&(d4<=d3);Q[m]=B[m];m=(d6>=0)&(d5<=d6);Q[m]=C[m]
    m=(vc<=0)&(d1>=0)&(d3<=0);t=d1/np.where(d1-d3==0,1e-12,d1-d3);Q[m]=(A+ab*t[:,None])[m]
    m=(vb<=0)&(d2>=0)&(d6<=0);t=d2/np.where(d2-d6==0,1e-12,d2-d6);Q[m]=(A+ac*t[:,None])[m]
    m=(va<=0)&((d4-d3)>=0)&((d5-d6)>=0);t=(d4-d3)/np.where((d4-d3)+(d5-d6)==0,1e-12,(d4-d3)+(d5-d6));Q[m]=(B+(C-B)*t[:,None])[m]
    return np.linalg.norm(p-Q,axis=1).min()
def gaps(f):
    j,b=load(f);W=worlds(j);T=[];ymin=9
    for i,n in enumerate(j['nodes']):
        if 'mesh' not in n: continue
        for p in j['meshes'][n['mesh']]['primitives']:
            P=acc(j,b,p['attributes']['POSITION']);P=P if 'skin' in n else (W[i]@np.c_[P,np.ones(len(P))].T).T[:,:3]; ymin=min(ymin,P[:,1].min())
            if 'LOD0' in n['name'] or n['name'].endswith('_L0'):
                F=acc(j,b,p['indices']).reshape(-1,3)
                if 'Shell' in n['name'] or 'skin' in n:
                    if 'skin' in n and 'COLOR_0' in p['attributes']:
                        C=acc(j,b,p['attributes']['COLOR_0']); F=F[(C[F][:,:,2]<.5).all(1)]   # shell only (B=wheel)
                    T.append(P[F])
    T=np.concatenate(T);A,B,C=T[:,0],T[:,1],T[:,2]
    return {n['name']:(ptri(W[i][:3,3],A,B,C),W[i][:3,3]) for i,n in enumerate(j['nodes']) if n['name'][:5] in('L_at_','R_at_')},ymin
for f in ['at-skate-meshy.v2','at-skate-meshy.merged.v2']+sys.argv[1:]:
    fs=[f'/tmp/fg_{f}.bak-forge-0352.glb',f'/tmp/fg_{f}.live.glb'] if not f.endswith('.glb') else [sys.argv[1].replace('NEW','OLD'),f]
    if f.endswith('.glb'): continue
    (go,yo),(gn,yn)=gaps(fs[0]),gaps(fs[1]); print(f'## {f}  lowest y old {yo*1000:.2f} mm, new {yn*1000:.2f} mm')
    for k in go: print(f'{k:22s} {go[k][0]*1000:7.2f} {gn[k][0]*1000:7.2f}  d={1000*(gn[k][0]-go[k][0]):+6.2f}  move={np.round(1000*(gn[k][1]-go[k][1]),2).tolist()}')
