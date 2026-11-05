import bpy,numpy as np,sys
fs=sys.argv[sys.argv.index('--')+1:]
for f in fs:
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=f)
    arm=[o for o in bpy.data.objects if o.type=='ARMATURE'][0]; o=[o for o in bpy.data.objects if o.type=='MESH' and ('LOD0' in o.name or len(o.data.vertices)>3000)][0]
    P=np.array([o.matrix_world@v.co for v in o.data.vertices]); gi={g.index:g.name for g in o.vertex_groups}
    for b in ('mixamorig:LeftArm','mixamorig:LeftForeArm'):
        bo=arm.data.bones[b]; h=np.array(arm.matrix_world@bo.head_local); t=np.array(arm.matrix_world@bo.tail_local); d=(t-h)/np.linalg.norm(t-h); L=np.linalg.norm(t-h)
        dom=[i for i,v in enumerate(o.data.vertices) if v.groups and gi[max(v.groups,key=lambda g:g.weight).group]==b]
        Q=P[dom]-h; tt=Q@d/L; R=np.linalg.norm(Q-np.outer(Q@d,d),axis=1); m=(tt>.35)&(tt<.65)
        off=(Q-np.outer(Q@d,d))[m].mean(0) if m.any() else None; print('OFF',b[10:],np.round(off,3),'axis',np.round(d,2),'head',np.round(h,2)); print('SLV',f.split('/')[-1][:18],b[10:],'dominant verts',len(dom),'mid n',m.sum(),'radius med/max',np.round(np.median(R[m]),3) if m.any() else None,np.round(R[m].max(),3) if m.any() else None,'-> circ~',np.round(2*np.pi*np.median(R[m]),3) if m.any() else None)
