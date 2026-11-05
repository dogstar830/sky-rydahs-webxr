import bpy,sys,numpy as np,re,json
from scipy.spatial import ConvexHull
fs=sys.argv[sys.argv.index('--')+1:]; OUT={}
def perim(X):
    if len(X)<8: return None
    h=ConvexHull(X); p=X[h.vertices]; return round(float(np.sum(np.linalg.norm(p-np.roll(p,1,0),axis=1))),3)
for f in fs:
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=f)
    arm=[o for o in bpy.data.objects if o.type=='ARMATURE'][0]
    ms=[o for o in bpy.data.objects if o.type=='MESH' and 'LOD0' in o.name] or [o for o in bpy.data.objects if o.type=='MESH' and len(o.data.vertices)>1000]
    o=ms[0]
    if 'INFL' in f:
        pass
    import os
    if os.environ.get('INFLATE') and 'rigged' in f:
        INFL={'Arm':.009,'ForeArm':.008,'Spine':.016,'Spine1':.015,'Spine2':.012,'Hips':.010,'Shoulder':.006}; gi={g.index:g.name.replace('mixamorig:','') for g in o.vertex_groups}
        for vv in o.data.vertices:
            off=sum(INFL.get(gi[g.group].replace('Left','').replace('Right',''),0)*g.weight for g in vv.groups); vv.co=vv.co+vv.normal*off
    P=np.array([o.matrix_world@v.co for v in o.data.vertices]); names={g.index:g.name.replace('mixamorig:','') for g in o.vertex_groups}
    W={}
    for v in o.data.vertices:
        for g in v.groups: W.setdefault(names[g.group],{})[v.index]=g.weight
    wt=lambda n: np.array([W.get(n,{}).get(i,0) for i in range(len(P))])
    H=lambda n: np.array(arm.matrix_world@arm.data.bones['mixamorig:'+n].head_local); T=lambda n: np.array(arm.matrix_world@arm.data.bones['mixamorig:'+n].tail_local)
    armw=sum(wt(s+b) for s in ('Left','Right') for b in ('Shoulder','Arm','ForeArm','Hand'))
    r={}
    for nm,b in (('upperarm','LeftArm'),('forearm','LeftForeArm')):
        h,t=H(b),T(b); d=(t-h)/np.linalg.norm(t-h); c=h+(t-h)*.5; m=(wt(b)>.4)&(np.abs((P-c)@d)<.015)
        u=np.cross(d,[0,1,0]); u/=np.linalg.norm(u); v=np.cross(d,u); Q=P[m]-c; r[nm]=perim(np.c_[Q@u,Q@v])
    for nm,b in (('waist','Spine'),('chest','Spine2')):
        z=H(b)[2]+(.04 if nm=='chest' else 0); m=(np.abs(P[:,2]-z)<.03)&(armw<.2)&(np.abs(P[:,0]-H('Hips')[0])<.25); r[nm]=perim(P[m][:,:2]); print('dbg',nm,z,m.sum(),P[:,2].min(),P[:,2].max(),H('Hips'))
    OUT[f.split('/')[-1]]=r; print('MEAS',f.split('/')[-1],r)
json.dump(OUT,open('/tmp/meas.json','w'))
