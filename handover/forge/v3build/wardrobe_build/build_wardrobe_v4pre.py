# Modular wardrobe builder: one shared skeleton (Meshy rig used by Ikki; caali-meshy-rigged.glb is byte-identical to it),
# a shared base body, and per-slot clothing pieces fitted + skinned to it, each exported as its own GLB (LOD0/1/2) under
# skyrydahs-characters/wardrobe/<slot>/<item>.glb. All items are baked into the SAME bind pose as the body, so at runtime
# they bind straight to the shared bones and can be merged into one skinned mesh. Body coverage masks -> body attribute _BM.
import bpy, bmesh, math, json, os, sys, numpy as np
from mathutils import Vector, Matrix, kdtree
from mathutils.bvhtree import BVHTree
DL='/home/box/Downloads/'; OUT='/workspace/skyrydahs-characters/wardrobe/'
ONLY=os.environ.get('ONLY','')  # comma list of slots to rebuild
SLOTS=['hair','head','top','jacket','pants','gloves','neck','accessory','skates']; BIT={s:1<<i for i,s in enumerate(SLOTS)}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath='/workspace/skyrydahs-characters/meshy/ikki-meshy-rigged.glb')
arm=[o for o in bpy.data.objects if o.type=='ARMATURE'][0]; body=[o for o in bpy.data.objects if o.type=='MESH' and o.parent==arm][0]
for a in list(bpy.data.actions): bpy.data.actions.remove(a)
if arm.animation_data: arm.animation_data_clear()
for o in list(bpy.data.objects):
    if o not in (arm,body) and o.parent!=arm and o.type=='MESH': bpy.data.objects.remove(o)
Bn=lambda n: arm.data.bones['mixamorig:'+n]; Wp=lambda v: arm.matrix_world@v
# v2 body: relaxed slim-athletic streetwear volume. Normal offsets (m) by bone region, weight-blended so seams stay smooth.
INFL={'Arm':.009,'ForeArm':.008,'Spine':.016,'Spine1':.015,'Spine2':.012,'Hips':.010,'Shoulder':.006}
def inflate_body():
    gi={g.index:g.name.replace('mixamorig:','') for g in body.vertex_groups}; me=body.data; me.calc_normals_split() if hasattr(me,'calc_normals_split') else None
    N=[v.normal.copy() for v in me.vertices]; n=0
    for v in me.vertices:
        off=0.
        for g in v.groups:
            nm=gi[g.group]; k=nm.replace('Left','').replace('Right','')
            if k in INFL: off+=INFL[k]*g.weight
        if off>0: v.co=v.co+N[v.index]*off; n+=1
    me.update(); print('inflate body verts',n)
if os.environ.get('BODY_V','2')=='2': inflate_body()
BV=np.array([body.matrix_world@v.co for v in body.data.vertices]); BV2=BV
def grp_pts(names,thr=.4):
    ids={body.vertex_groups['mixamorig:'+n].index for n in names if 'mixamorig:'+n in body.vertex_groups}
    return np.array([BV[v.index] for v in body.data.vertices if any(g.group in ids and g.weight>thr for g in v.groups)])
def sel(*obs):
    bpy.ops.object.select_all(action='DESELECT')
    for o in obs: o.select_set(True)
    bpy.context.view_layer.objects.active=obs[0]
def tri(o): return sum(len(p.vertices)-2 for p in o.data.polygons)
def imp(fn,weld=True):
    before=set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=DL+fn)
    new=[o for o in bpy.data.objects if o not in before]; ms=[o for o in new if o.type=='MESH']
    for o in new:
        if o.type!='MESH': bpy.data.objects.remove(o)
    o=ms[0]; o.parent=None
    for x in ms[1:]: bpy.data.objects.remove(x)
    # glTF import splits verts at every UV seam -> the decimator tears those seams into shards. Weld first (UVs live on loops).
    if not weld: return o
    bm=bmesh.new(); bm.from_mesh(o.data); n0=len(bm.verts); bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=1e-5); bm.to_mesh(o.data); print('weld',fn[:30],n0,'->',len(bm.verts)); bm.free(); return o
def decimate(o,target):
    sel(o); m=o.modifiers.new('d','DECIMATE'); m.ratio=min(1.,target/max(1,tri(o))); m.use_collapse_triangulate=True; bpy.ops.object.modifier_apply(modifier=m.name)
def apply_xf(o): sel(o); bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
def pts(o): return np.array([o.matrix_world@v.co for v in o.data.vertices])
def fit_box(o,lo,hi,axes=(0,1,2),uniform=True):
    """scale+translate so the object's bbox spans [lo,hi] on the given axes (uniform: scale from the first axis)"""
    P=pts(o); a,b=P.min(0),P.max(0); lo,hi=np.array(lo,float),np.array(hi,float)
    s=np.ones(3)
    for ax in axes: s[ax]=(hi[ax]-lo[ax])/(b[ax]-a[ax])
    if uniform: s[:]=s[axes[0]]
    o.scale=Vector(s); o.location=Vector((lo+hi)/2-((a+b)/2)*s); apply_xf(o)
def push_out(o,off=.006,iters=3):
    """anti-poke: push item verts that are inside / too close to the body out along the body normal, with the displacement
    field Laplacian-smoothed over the item mesh so cloth moves as a sheet (per-vertex pushes crumple it into shards)"""
    dg=bpy.context.evaluated_depsgraph_get(); be=body.evaluated_get(dg); bm=bmesh.new(); bm.from_mesh(be.to_mesh()); bm.transform(body.matrix_world); tree=BVHTree.FromBMesh(bm)
    me=o.data; n=len(me.vertices); E_=np.array([e.vertices[:] for e in me.edges]) if len(me.edges) else np.zeros((0,2),int)
    deg=np.bincount(E_.ravel(),minlength=n).astype(float)+1e-9; Mw=np.array(o.matrix_world); Mi=np.linalg.inv(Mw)
    for _ in range(iters):
        X=np.array([v.co for v in me.vertices]); Wd=X@Mw[:3,:3].T+Mw[:3,3]; D=np.zeros((n,3)); need=np.zeros(n,bool)
        for i,w in enumerate(Wd):
            loc,nor,_i,d=tree.find_nearest(Vector(w))
            if loc is None: continue
            s_=(Vector(w)-loc).dot(nor)
            if s_<off: D[i]=np.array(nor)*(off-s_); need[i]=True
        if not need.any(): break
        for k in range(12):   # smooth the push field, never below the required push
            A=np.zeros((n,3)); np.add.at(A,E_[:,0],D[E_[:,1]]); np.add.at(A,E_[:,1],D[E_[:,0]]); S=A/deg[:,None]
            D=np.where(need[:,None]&(np.linalg.norm(D,axis=1,keepdims=True)>=np.linalg.norm(S,axis=1,keepdims=True)),D,S*.9+D*.1) if k<11 else D
        Wd=Wd+D; X=Wd@Mi[:3,:3].T+Mi[:3,3]; me.vertices.foreach_set('co',X.astype(np.float32).ravel()); me.update()
    be.to_mesh_clear(); bm.free()
def weights_from_body(o,rigid=None):
    sel(o)
    for vg in list(o.vertex_groups): o.vertex_groups.remove(vg)
    if rigid:
        for bname,w in rigid.items(): g=o.vertex_groups.new(name='mixamorig:'+bname); g.add(list(range(len(o.data.vertices))),w,'REPLACE')
    else:
        for vg in body.vertex_groups: o.vertex_groups.new(name=vg.name)
        m=o.modifiers.new('dt','DATA_TRANSFER'); m.object=body; m.use_vert_data=True; m.data_types_verts={'VGROUP_WEIGHTS'}; m.vert_mapping='POLYINTERP_NEAREST'
        m.layers_vgroup_select_src='ALL'; m.layers_vgroup_select_dst='NAME'; bpy.ops.object.modifier_apply(modifier=m.name)
        # smooth a little so cloth doesn't inherit sharp body seams; keep <=4 influences
        bpy.ops.object.mode_set(mode='WEIGHT_PAINT'); bpy.ops.object.vertex_group_smooth(group_select_mode='ALL',factor=.5,repeat=2); bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL',limit=4); bpy.ops.object.vertex_group_normalize_all(lock_active=False); bpy.ops.object.mode_set(mode='OBJECT')
    o.parent=arm; o.matrix_parent_inverse=arm.matrix_world.inverted(); am=o.modifiers.new('Armature','ARMATURE'); am.object=arm
def pose_arms(theta_deg):
    """rotate both upper arms outward (about the character's front axis) to match a garment's sleeve angle; 0 = rest (arms down)"""
    bpy.context.view_layer.objects.active=arm; bpy.ops.object.mode_set(mode='POSE')
    for side,sg in (('Left',-1),('Right',1)):
        pb=arm.pose.bones['mixamorig:'+side+'Arm']; pb.rotation_mode='QUATERNION'
        if theta_deg==0: pb.rotation_quaternion=(1,0,0,0); continue
        Rw=Matrix.Rotation(math.radians(theta_deg)*sg,4,'Y')  # world: +Y is back; left arm (+X) raises with +rot about Y
        bone_w=arm.matrix_world@pb.bone.matrix_local; head=bone_w.to_translation()
        new_w=Matrix.Translation(head)@Rw@Matrix.Translation(-head)@bone_w
        pb.matrix=arm.matrix_world.inverted()@new_w
    bpy.context.view_layer.update(); bpy.ops.object.mode_set(mode='OBJECT')
def sleeve_dirs(o):
    # principal axis of each sleeve (verts outboard of the shoulder), oriented away from the shoulder
    P=pts(o); cx=LAND['hips'].x; out={}
    for side,sg,sh in (('Left',1,LAND['lsh']),('Right',-1,LAND['rsh'])):
        S=P[sg*(P[:,0]-cx)>abs(sh.x-cx)+.03]
        if len(S)<30: out[side]=None; continue
        c=S.mean(0); U=np.linalg.svd(S-c,full_matrices=False)[2][0]
        if U@(c-np.array(sh))<0: U=-U
        out[side]=U
    # garments are symmetric: a missing / implausible side (PCA grabbed the torso) mirrors the other one
    ang=lambda side,u: math.degrees((Wp(Bn(side+'Hand').head_local)-Wp(Bn(side+'Arm').head_local)).normalized().angle(Vector(u))) if u is not None else 999
    aL,aR=ang('Left',out['Left']),ang('Right',out['Right']); mir=lambda u: np.array([-u[0],u[1],u[2]])
    if aL>45 and aR<=45: out['Left']=mir(out['Right'])
    elif aR>45 and aL<=45: out['Right']=mir(out['Left'])
    elif aL>45 and aR>45: out={'Left':None,'Right':None}
    return out
def pose_arms_vec(dirs):
    # rotate each upper arm (about the shoulder joint, in 3D) so shoulder->hand points along the sleeve axis; v2 only abducted
    bpy.context.view_layer.objects.active=arm; bpy.ops.object.mode_set(mode='POSE')
    for side,u in dirs.items():
        pb=arm.pose.bones['mixamorig:'+side+'Arm']; pb.rotation_mode='QUATERNION'; pb.rotation_quaternion=(1,0,0,0)
        if u is None: continue
        bone_w=arm.matrix_world@pb.bone.matrix_local; head=bone_w.to_translation(); hand=Wp(Bn(side+'Hand').head_local)
        R=(hand-head).normalized().rotation_difference(Vector(u)).to_matrix().to_4x4()
        pb.matrix=arm.matrix_world.inverted()@(Matrix.Translation(head)@R@Matrix.Translation(-head)@bone_w)
        print('pose',side,'sleeve dir',np.round(u,2),'angle',round(math.degrees((hand-head).normalized().angle(Vector(u))),1))
    bpy.context.view_layer.update(); bpy.ops.object.mode_set(mode='OBJECT')
LOOSE={'jacket':1.2,'top':1.2,'pants':1.2}
def loosen(o,slot):
    # relaxed streetwear volume: weight-blended radial scale about each cloth bone's axis (smooth across shoulder/elbow/hip seams)
    k=LOOSE.get(slot); bones=RAD_BONES.get(slot)
    if not k: return
    gi={g.index:g.name.replace('mixamorig:','') for g in o.vertex_groups}; Mw=o.matrix_world; Mi=Mw.inverted(); X=[]
    for vx in o.data.vertices:
        w=np.array(Mw@vx.co); acc=np.zeros(3); tw=0
        for g in vx.groups:
            b=gi.get(g.group)
            if b in bones and g.weight>0:
                h,d,u,v,L,prof=body_profile(b); Q=w-h; ax=h+d*(Q@d); acc+=(ax+(w-ax)*k)*g.weight; tw+=g.weight
        X.append(w if tw==0 else (acc+w*max(0,1-tw))/max(tw,1.) if tw>=1 else acc+w*(1-tw))
    for vx,x in zip(o.data.vertices,X): vx.co=Mi@Vector(x)
    o.data.update()
def bake_to_rest(o):
    """item was fitted on a posed body: return the skeleton to rest and bake the deformation into the mesh (weights kept)"""
    pose_arms(0); sel(o); am=o.modifiers.get('Armature')
    # evaluate with posed? we already returned to rest -> the cloth follows the arms down through its weights
    bpy.context.view_layer.update(); m=o.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
    o.data=bpy.data.meshes.new_from_object(o.evaluated_get(bpy.context.evaluated_depsgraph_get())) ; 
def downsize_images(o,base=1024,aux=512):
    for mat in o.data.materials:
        if not mat or not mat.use_nodes: continue
        for n in mat.node_tree.nodes:
            if n.type=='TEX_IMAGE' and n.image:
                im=n.image; isbase=any(l.to_socket.name=='Base Color' for l in n.outputs['Color'].links); t=base if isbase else aux
                if max(im.size)>t: im.scale(t,t)
RAD_BONES={'jacket':['LeftArm','LeftForeArm','RightArm','RightForeArm','Spine','Spine1','Spine2'],'top':['LeftArm','LeftForeArm','RightArm','RightForeArm','Spine','Spine1','Spine2'],
           'pants':['Hips','LeftUpLeg','LeftLeg','RightUpLeg','RightLeg']}
RAD_MARGIN={'jacket':.022,'top':.009,'pants':.014}
_prof={}
def body_profile(b):
    if b in _prof: return _prof[b]
    bo=arm.data.bones['mixamorig:'+b]; h=np.array(Wp(bo.head_local)); t=np.array(Wp(bo.tail_local))
    if b.startswith('Spine') or b=='Hips': t=h+np.array([0,0,np.linalg.norm(t-h)])   # torso: vertical axis
    d=t-h; L=np.linalg.norm(d); d/=L; u=np.cross(d,[0,1,0] if abs(d[1])<.9 else [1,0,0]); u/=np.linalg.norm(u); v=np.cross(d,u)
    gidx=body.vertex_groups['mixamorig:'+b].index; ids=[x.index for x in body.data.vertices if any(g.group==gidx and g.weight>.35 for g in x.groups)]
    Q=BV2[ids]-h; tt=Q@d/L; R=Q-np.outer(Q@d,d); ang=np.arctan2(R@v,R@u); rr=np.linalg.norm(R,axis=1)
    TB,AB=10,16; prof=np.zeros((TB,AB))
    for i in range(TB):
        for j in range(AB):
            m=(np.clip((tt*TB).astype(int),0,TB-1)==i)&(((ang+np.pi)/(2*np.pi)*AB).astype(int)%AB==j)
            prof[i,j]=np.percentile(rr[m],90) if m.sum()>2 else 0
    for _ in range(3):   # fill empty bins from neighbours
        z=prof==0; nb=(np.roll(prof,1,1)+np.roll(prof,-1,1))/2; prof[z]=nb[z]
    _prof[b]=(h,d,u,v,L,prof); return _prof[b]
def radial_fit(o,slot):
    if slot not in RAD_BONES: return
    gi={g.index:g.name.replace('mixamorig:','') for g in o.vertex_groups}; Mw=o.matrix_world; Mi=Mw.inverted(); moved=0
    for vx in o.data.vertices:
        best=max(vx.groups,key=lambda g:g.weight,default=None)
        if best is None or gi.get(best.group) not in RAD_BONES[slot]: continue
        h,d,u,v,L,prof=body_profile(gi[best.group]); w=np.array(Mw@vx.co); Q=w-h; t=Q@d/L
        if t<-.05 or t>1.05: continue
        R=Q-d*(Q@d); r=np.linalg.norm(R)
        if r<1e-5: continue
        a=np.arctan2(R@v,R@u); i=min(9,max(0,int(t*10))); j=int((a+np.pi)/(2*np.pi)*16)%16; need=prof[i,j]+RAD_MARGIN[slot]
        if r<need: vx.co=Mi@Vector(h+d*(Q@d)+R*(need/r)); moved+=1
    o.data.update(); return moved
def export_item(slot,name,lods,extra_objs=()):
    for o in lods:
        mv=radial_fit(o,slot)
        if mv is not None: print('radial fit',slot,o.name,mv,'verts')
    for i,o in enumerate(lods): o.name=f'{name}_LOD{i}'; o.data.name=o.name
    sel(arm,*lods); fn=OUT+f'{slot}/{name}.glb'
    bpy.ops.export_scene.gltf(filepath=fn,export_format='GLB',use_selection=True,export_animations=False,export_skins=True,export_morph=False,export_image_format='WEBP',export_image_quality=80,export_yup=True,export_vertex_color='ACTIVE')
    print('EXPORT',fn,[tri(o) for o in lods],os.path.getsize(fn)//1024,'KB')
def make_lods(o,targets):
    out=[o]; decimate(o,targets[0])
    for t in targets[1:]:
        c=o.copy(); c.data=o.data.copy(); bpy.context.collection.objects.link(c); decimate(c,t); out.append(c)
    return out
LAND=dict(neck=Wp(Bn('Neck').head_local), head=Wp(Bn('Head').head_local), top=Wp(Bn('HeadTop_End').head_local), hips=Wp(Bn('Hips').head_local),
          lsh=Wp(Bn('LeftArm').head_local), rsh=Wp(Bn('RightArm').head_local), lhand=Wp(Bn('LeftHand').head_local), rhand=Wp(Bn('RightHand').head_local),
          lfoot=Wp(Bn('LeftFoot').head_local), rfoot=Wp(Bn('RightFoot').head_local), sp2=Wp(Bn('Spine2').head_local))
torso=grp_pts(['Spine','Spine1','Spine2']); TY=float(np.median(torso[:,1])); print('torso y',TY,'landmarks',{k:tuple(round(x,3) for x in v) for k,v in LAND.items()})
covered={}   # slot -> list of item objects (LOD0) used for body masks
def want(s): return not ONLY or s in ONLY.split(',')
def sleeve_angle(o):
    P=pts(o); hw=(P[:,0].max()-P[:,0].min())/2; cx=(P[:,0].max()+P[:,0].min())/2; sl=P[np.abs(P[:,0]-cx)>hw*.7]; tip=sl[np.argmin(sl[:,2])] if len(sl) else None
    # far cuff point vs shoulder (top-outer)
    far=P[np.argmax(np.abs(P[:,0]-cx))]; sh=np.array([cx+np.sign(far[0]-cx)*hw*.38,0,P[:,2].max()-(P[:,2].max()-P[:,2].min())*.12])
    d=far-sh; return math.degrees(math.atan2(abs(d[0]),-d[2]))
def stamp_logo(o,png,width=.20):
    # 1) erase the misspelled AI text (gold texels -> tee black)  2) project the real 'Gr8yzone' logo onto the chest front, baked in UV space
    from PIL import Image
    mat=o.data.materials[0]; img=[n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and any(l.to_socket.name=='Base Color' for l in n.outputs['Color'].links)][0].image
    W_,H_=img.size; px=np.array(img.pixels[:],np.float32).reshape(H_,W_,4); c=px[...,:3]
    gold=(c[...,0]>.30)&(c[...,0]>c[...,2]*2.2)&(c[...,1]>c[...,2]*1.4)&(c[...,1]>.15); blk=np.median(c[(c.max(-1)<.12)],axis=0)
    c[gold]=blk; print('logo: erased',int(gold.sum()),'gold texels; black',blk)
    L=np.array(Image.open(png).convert('RGBA'),np.float32)/255.; lh,lw=L.shape[:2]; h=width*lh/lw
    xc=LAND['hips'].x; zc=(LAND['sp2'].z+LAND['neck'].z)/2-.035; x0=xc-width/2; zt=zc+h/2
    me=o.data; uv=me.uv_layers.active.data; V=np.array([o.matrix_world@v.co for v in me.vertices]); n_hit=0
    for f in me.polygons:
        if (o.matrix_world.to_3x3()@f.normal).y>-.3: continue
        vi=list(f.vertices); P=V[vi]
        if P[:,0].max()<x0 or P[:,0].min()>x0+width or P[:,2].max()<zt-h or P[:,2].min()>zt: continue
        U=np.array([[uv[l].uv.x*W_,uv[l].uv.y*H_] for l in f.loop_indices])
        for t in range(1,len(vi)-1):
            tri_=[0,t,t+1]; A=U[tri_]; Pw=P[tri_]; lo=np.floor(A.min(0)).astype(int); hi=np.ceil(A.max(0)).astype(int)
            gx,gy=np.meshgrid(np.arange(lo[0],hi[0]+1),np.arange(lo[1],hi[1]+1)); Q=np.stack([gx.ravel()+.5,gy.ravel()+.5],1)
            T=np.array([A[1]-A[0],A[2]-A[0]]).T
            if abs(np.linalg.det(T))<1e-9: continue
            b=np.linalg.solve(T,(Q-A[0]).T).T; w=np.c_[1-b.sum(1),b]; ok=(w>=-.02).all(1)
            Wp=w[ok]@Pw; lu=(Wp[:,0]-x0)/width; lv=(zt-Wp[:,2])/h; in_=(lu>=0)&(lu<1)&(lv>=0)&(lv<1)
            qx=gx.ravel()[ok][in_]%W_; qy=gy.ravel()[ok][in_]%H_; s_=L[(lv[in_]*lh).astype(int),(lu[in_]*lw).astype(int)]
            a=s_[:,3:4]; c[qy,qx]=c[qy,qx]*(1-a)+s_[:,:3]**2.2*a; n_hit+=len(qx)
    px[...,:3]=c; img.pixels.foreach_set(px.ravel()); img.update(); print('logo: stamped texels',n_hit)
def garment_top(slot,fn,name,z_hem,targets):
    o=imp(fn); apply_xf(o)
    P=pts(o); a,b=P.min(0),P.max(0); s=(LAND['neck'].z+.04-z_hem)/(b[2]-a[2])
    o.scale=(s,s,s); o.location=Vector((LAND['hips'].x-(a[0]+b[0])/2*s, TY-(a[1]+b[1])/2*s, z_hem-a[2]*s)); apply_xf(o)
    pose_arms_vec(sleeve_dirs(o)); decimate(o,targets[0]*4); push_out(o,.02 if slot=='jacket' else .006); weights_from_body(o)
    rest_bake(o); loosen(o,slot); push_out(o,.018 if slot=='jacket' else .006)
    downsize_images(o); lods=make_lods(o,targets)
    if slot=='top': stamp_logo(lods[0],OUT+'top/gr8yzone_logo.png')
    export_item(slot,name,lods); covered[slot]=lods[0]
def rest_bake(o):
    """fitted with arms raised to the sleeve angle -> drop the skeleton to rest, bake that deformation into the mesh"""
    dg=bpy.context.evaluated_depsgraph_get(); posed=[pb.matrix.copy() for pb in arm.pose.bones]
    pose_arms(0)  # cloth now follows the arms down through the transferred weights; but Blender needs the deformation relative to the fitting pose:
    # re-express: set rest = fitting pose temporarily is costly; instead compute deformation = rest_pose_skin(v) using bone deltas fit->rest
    me=o.data; vg={g.index:g.name for g in o.vertex_groups}
    D={}
    for pb,pm in zip(arm.pose.bones,posed): D[pb.name]=(arm.matrix_world@pb.matrix)@(arm.matrix_world@pm).inverted()   # fit-pose -> rest-pose bone delta (world)
    for v in me.vertices:
        w=o.matrix_world@v.co; acc=Vector((0,0,0)); tw=0
        for g in v.groups:
            n=vg[g.group]
            if n in D and g.weight>0: acc+=(D[n]@w)*g.weight; tw+=g.weight
        if tw>0: v.co=o.matrix_world.inverted()@(acc/tw)
    me.update()
# ---------------- base body ----------------
CAALI_SKIN=np.array([.80,.58,.42])
def recolor_body(o):
    # neutral base: skin texels -> canon Caali tan (shading kept), eye whites kept, head-region iris -> brown, everything else (Ikki's clothes) -> charcoal bodysuit
    from PIL import Image, ImageDraw
    mat=o.data.materials[0]; img=[n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and any(l.to_socket.name=='Base Color' for l in n.outputs['Color'].links)][0].image
    W_,H_=img.size; px=np.array(img.pixels[:]).reshape(H_,W_,4)
    hid=o.vertex_groups['mixamorig:Head'].index; nid=o.vertex_groups['mixamorig:Neck'].index
    hv=set(v.index for v in o.data.vertices if any(g.group in (hid,nid) and g.weight>.4 for g in v.groups))
    m=Image.new('L',(W_,H_),0); d=ImageDraw.Draw(m); uv=o.data.uv_layers.active.data
    for p in o.data.polygons:
        if all(v in hv for v in p.vertices): d.polygon([(uv[l].uv.x*W_,uv[l].uv.y*H_) for l in p.loop_indices],fill=255)
    head=np.array(m)>0   # PIL row0 = v=0 = blender pixel row 0
    rgb=px[...,:3]; mx=rgb.max(-1); mn=rgb.min(-1); sat=(mx-mn)/np.maximum(mx,1e-3); lum=rgb@np.array([.3,.59,.11])
    skin=(rgb[...,0]>rgb[...,1])&(rgb[...,1]>rgb[...,2]*1.02)&(rgb[...,0]>.28)&(sat<.6)
    white=(lum>.62)&(sat<.18)
    ref=np.median(lum[skin&head]) if (skin&head).any() else .6
    out=rgb.copy()
    t=CAALI_SKIN*np.clip(lum/ref,.35,1.4)[...,None]; out[skin]=t[skin]
    iris=head&~skin&~white&(sat>.3)&(lum>.08)&(rgb[...,2]>rgb[...,0]*1.3)&(rgb[...,1]>rgb[...,0]*1.1); out[iris]=(np.array([.30,.17,.08])*np.clip(lum/.35,.5,1.6)[...,None])[iris]
    rest=~head&~skin; out[rest]=(np.array([.055,.055,.065])*np.clip(lum/.25,.6,1.6)[...,None])[rest]
    px[...,:3]=out; img.pixels.foreach_set(px.ravel().astype(np.float32)); img.update(); print('recolor body: skin px',int(skin.sum()),'iris',int(iris.sum()),'ref',round(float(ref),3))
if want('body'):
    BB=body.copy(); BB.data=body.data.copy(); bpy.context.collection.objects.link(BB); BB.parent=arm; BB.matrix_parent_inverse=body.matrix_parent_inverse.copy()
    if not BB.modifiers.get('Armature'): am=BB.modifiers.new('Armature','ARMATURE'); am.object=arm
    downsize_images(BB,1024,512); recolor_body(BB)
# ---------------- garments ----------------
if want('jacket'): garment_top('jacket','Meshy_AI_cropped_black_bomber__1028203848_texture.glb','caali_bomber',LAND['hips'].z+.07,[3600,1800,600])
if want('top'):    garment_top('top','Meshy_AI_black_crew_neck_t_shi_1028214248_texture.glb','caali_gr8yzone_tee',LAND['hips'].z-.08,[1400,700,250])
if want('pants'):
    o=imp('Meshy_AI_black_cargo_pants_wit_1028203304_texture.glb'); apply_xf(o); P=pts(o); a,b=P.min(0),P.max(0)
    zt=LAND['hips'].z+.05; zb=.10; s=(zt-zb)/(b[2]-a[2]); legs=grp_pts(['LeftUpLeg','RightUpLeg']); hipw=legs[:,0].max()-legs[:,0].min()
    sx=min(s,hipw*1.3/(b[0]-a[0])); o.scale=(sx,s*.95,s); o.location=Vector((LAND['hips'].x-(a[0]+b[0])/2*sx, TY+.01-(a[1]+b[1])/2*s*.95, zb-a[2]*s)); apply_xf(o)
    decimate(o,12000); push_out(o,.01); weights_from_body(o); loosen(o,'pants'); push_out(o,.01); downsize_images(o); lods=make_lods(o,[3000,1500,500]); export_item('pants','caali_cargo',lods); covered['pants']=lods[0]
if want('gloves'):
    o=imp('Meshy_AI_a_pair_of_black_finge_1028203443_texture.glb'); apply_xf(o); decimate(o,4000)
    bm=bmesh.new(); bm.from_mesh(o.data); P=np.array([v.co for v in bm.verts]); cx=(P[:,0].min()+P[:,0].max())/2; bm.free()
    gl=[]
    for side,keep in (('Right',lambda x:x<cx),('Left',lambda x:x>=cx)):   # image-left glove -> mirrored by the 180deg flip below
        c=o.copy(); c.data=o.data.copy(); bpy.context.collection.objects.link(c)
        bm=bmesh.new(); bm.from_mesh(c.data); bmesh.ops.delete(bm,geom=[v for v in bm.verts if keep(v.co.x)],context='VERTS'); bm.to_mesh(c.data); bm.free()
        hp=grp_pts([side+'Hand']+[side+'Hand'+f+str(k) for f in ('Index','Middle','Ring','Pinky','Thumb') for k in (1,2,3)],.3)
        c.rotation_euler=(0,math.pi,(-math.pi/2 if side=='Left' else math.pi/2)); apply_xf(c)
        a,b=hp.min(0),hp.max(0); pad=np.array([.012,.012,.0]); fit_box(c,a-pad-np.array([0,0,.03]),b+pad,axes=(2,),uniform=True)
        Q=pts(c); c.location=Vector((hp[:,0].mean()-Q[:,0].mean(), hp[:,1].mean()-Q[:,1].mean(), 0)); apply_xf(c)
        push_out(c,.004); weights_from_body(c); gl.append(c)
    bpy.data.objects.remove(o); sel(*gl); bpy.ops.object.join(); g=bpy.context.object; downsize_images(g,512,256)
    lods=make_lods(g,[700,350,120]); export_item('gloves','caali_fingerless',lods); covered['gloves']=lods[0]
if want('neck'):
    o=imp('Meshy_AI_a_thick_gold_chain_ne_1028203541_texture.glb'); apply_xf(o); decimate(o,1200)
    o.rotation_euler=(math.radians(-72),0,0); apply_xf(o); P=pts(o); a,b=P.min(0),P.max(0); s=.25/(b[0]-a[0]); o.scale=(s,s,s); apply_xf(o)
    P=pts(o); o.location=Vector((LAND['neck'].x-P[:,0].mean(), TY-.01-P[:,1].mean(), LAND['neck'].z-.085-P[:,2].mean())); apply_xf(o)
    push_out(o,.012,3); weights_from_body(o,rigid={'Spine2':.7,'Neck':.3}); downsize_images(o,512,256)
    lods=make_lods(o,[450,220,80]); export_item('neck','gold_chain_thick',lods); covered['neck']=lods[0]
if want('hair'):
    o=imp('Meshy_AI_short_black_curly_hai_1028203645_texture.glb',weld=False); apply_xf(o)
    # fit whole head+hair to the shared head: chin at the neck joint, height to the head top (+hair volume)
    P=pts(o); a,b=P.min(0),P.max(0); H=(LAND['top'].z+.07)-(LAND['head'].z-.03); s=H/(b[2]-a[2]); hp=grp_pts(['Head'],.6)
    o.scale=(s,s,s); o.location=Vector((hp[:,0].mean()-(a[0]+b[0])/2*s, hp[:,1].mean()-.005-(a[1]+b[1])/2*s, LAND['head'].z-.03-a[2]*s)); apply_xf(o)
    # the bald Meshy head is the single largest loose part -> drop it (the shared body head + face is used); curls = everything else
    src=o.copy(); src.data=o.data.copy(); bpy.context.collection.objects.link(src)
    bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table(); seen=set(); isl=[]
    for v in bm.verts:
        if v.index in seen: continue
        st=[v]; comp=[]; seen.add(v.index)
        while st:
            x=st.pop(); comp.append(x)
            for e in x.link_edges:
                y=e.other_vert(x)
                if y.index not in seen: seen.add(y.index); st.append(y)
        isl.append(comp)
    big=max(isl,key=len); print('hair islands',len(isl),'head part verts',len(big))
    bmesh.ops.delete(bm,geom=big,context='VERTS'); bm.to_mesh(o.data); bm.free()
    # refit the curls alone to the shared scalp (head-weighted body verts), a little proud of it; bottom at the ear line
    hh_=LAND['top'].z-LAND['head'].z; HP=grp_pts(['Head'],.6); lo=HP.min(0)-np.array([.018,.018,0]); hi=HP.max(0)+np.array([.018,.022,.035]); lo[2]=LAND['head'].z+.28*hh_
    fit_box(o,lo,hi,axes=(0,1,2),uniform=False)
    # single watertight shell: voxel remesh closes the curl gaps so the decimator can actually reduce it
    sel(o); m=o.modifiers.new('r','REMESH'); m.mode='VOXEL'; m.voxel_size=.015; m.adaptivity=0; bpy.ops.object.modifier_apply(modifier=m.name)
    bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table(); seen=set(); kill=[]
    for v in bm.verts:
        if v.index in seen: continue
        st=[v]; comp=[]; seen.add(v.index)
        while st:
            x=st.pop(); comp.append(x)
            for e in x.link_edges:
                y=e.other_vert(x)
                if y.index not in seen: seen.add(y.index); st.append(y)
        if len(comp)<400: kill+=comp
    print('remesh: dropping',len(kill),'verts of crumbs'); bmesh.ops.delete(bm,geom=kill,context='VERTS'); bm.to_mesh(o.data); bm.free()
    # open the face: no curls below the brow line in front, none below the ear line anywhere (eyes/brows must read)
    hy=float(np.median(grp_pts(['Head'],.6)[:,1])); hh=LAND['top'].z-LAND['head'].z
    bm=bmesh.new(); bm.from_mesh(o.data); cut=[v for v in bm.verts if (v.co.y<hy-.025 and v.co.z<LAND['head'].z+.66*hh) or v.co.z<LAND['head'].z+.30*hh]
    print('hair trim',len(cut),'of',len(bm.verts)); bmesh.ops.delete(bm,geom=cut,context='VERTS'); bm.to_mesh(o.data); bm.free()
    sel(o); m=o.modifiers.new('sm','SMOOTH'); m.iterations=2; m.factor=.4; bpy.ops.object.modifier_apply(modifier=m.name)
    # LODs from the clean shell FIRST (per-face UV transfer creates seams everywhere and blocks the decimator), then texture each LOD
    lods=[o]
    for t in (700,250):
        c=o.copy(); c.data=o.data.copy(); bpy.context.collection.objects.link(c); lods.append(c)
    for c,t in zip(lods,(1300,650,240)):
        decimate(c,t); c.data.materials.clear(); c.data.materials.append(src.data.materials[0]); c.data.uv_layers.new(name='UVMap')
        sel(c); m=c.modifiers.new('dt','DATA_TRANSFER'); m.object=src; m.use_loop_data=True; m.data_types_loops={'UV'}; m.loop_mapping='POLYINTERP_NEAREST'; bpy.ops.object.modifier_apply(modifier=m.name)
        sel(c); bpy.ops.object.shade_smooth(); push_out(c,.006); weights_from_body(c,rigid={'Head':1.0})
    bpy.data.objects.remove(src); downsize_images(o,512,256)
    export_item('hair','caali_curly_short',lods); covered['hair']=lods[0]
if want('accessory'):
    # original gold pants chains (none on the Meshy pants): two swags of torus links, belt-front -> thigh -> back pocket, each side
    links=[]; bm=bmesh.new()
    def swag(p0,p1,p2,n):
        for i in range(n):
            t=i/(n-1); q=(1-t)**2*np.array(p0)+2*(1-t)*t*np.array(p1)+t*t*np.array(p2)
            r=bmesh.ops.create_circle(bm,cap_ends=False,segments=6,radius=.007)
            # make it a flat torus-ish link: use a small cone ring instead (cheap); orient alternately
            M=Matrix.Translation(Vector(q))@Matrix.Rotation((math.pi/2)*(i%2),4,'Z')@Matrix.Rotation(math.pi/2,4,'X')
            bmesh.ops.transform(bm,matrix=M,verts=r['verts'])
            # give the ring thickness
            ex=bmesh.ops.extrude_edge_only(bm,edges=list({e for v in r['verts'] for e in v.link_edges})); bmesh.ops.translate(bm,vec=(M.to_3x3()@Vector((0,0,.004))),verts=[v for v in ex['geom'] if isinstance(v,bmesh.types.BMVert)])
    hz=LAND['hips'].z
    for sx in (1,-1):
        swag((sx*.11,TY-.13,hz-.02),(sx*.17,TY-.06,hz-.2),(sx*.15,TY+.11,hz-.04),16)
    me=bpy.data.meshes.new('chains'); bm.to_mesh(me); bm.free(); o=bpy.data.objects.new('chains',me); bpy.context.collection.objects.link(o)
    gm=bpy.data.materials.new('gold'); gm.use_nodes=True; bs=gm.node_tree.nodes['Principled BSDF']; gi=bpy.data.images.new('gold',16,16); gi.pixels=[.85,.62,.12,1]*256
    tn=gm.node_tree.nodes.new('ShaderNodeTexImage'); tn.image=gi; gm.node_tree.links.new(tn.outputs['Color'],bs.inputs['Base Color']); bs.inputs['Metallic'].default_value=1; bs.inputs['Roughness'].default_value=.3; me.materials.append(gm)
    me.uv_layers.new(); push_out(o,.01); weights_from_body(o)
    lods=make_lods(o,[tri(o),tri(o)//2,0]) if False else [o]
    c1=o.copy(); c1.data=o.data.copy(); bpy.context.collection.objects.link(c1); decimate(c1,tri(o)//2)
    c2=c1.copy(); c2.data=c1.data.copy(); bpy.context.collection.objects.link(c2); export_item('accessory','gold_pants_chains',[o,c1,c2]); covered['accessory']=o
# ---------------- body coverage masks (_BM bitfield per body vertex) ----------------
if want('body'):
    for sl in ('jacket','top','pants','gloves','neck','hair','accessory'):
        if sl not in covered:
            import glob; fn=glob.glob(OUT+sl+'/*.glb')[0]; before=set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=fn)
            nw=[o for o in bpy.data.objects if o not in before]; covered[sl]=[o for o in nw if o.type=='MESH' and o.name.endswith('LOD0')][0]
            for o in nw:
                if o is not covered[sl] and o.type!='ARMATURE': bpy.data.objects.remove(o)
            print('mask uses existing',fn)
    dg=bpy.context.evaluated_depsgraph_get(); trees={}
    for sl,it in covered.items():
        bm=bmesh.new(); bm.from_mesh(it.data); bm.transform(it.matrix_world); trees[sl]=BVHTree.FromBMesh(bm); bm.free()
    import pickle
    def mask_for(o):
        M=[]; img=None
        mat=o.data.materials[0]; img=[n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and any(l.to_socket.name=='Base Color' for l in n.outputs['Color'].links)][0].image
        W_,H_=img.size; px=np.array(img.pixels[:]).reshape(H_,W_,4); vuv={}
        for p in o.data.polygons:
            for li in p.loop_indices: vuv[o.data.loops[li].vertex_index]=o.data.uv_layers.active.data[li].uv
        hz=LAND['head'].z+.50*(LAND['top'].z-LAND['head'].z); hy=float(np.median(grp_pts(['Head'],.6)[:,1]))
        for v in o.data.vertices:
            w=o.matrix_world@v.co; nrm=(o.matrix_world.to_3x3()@v.normal).normalized(); m=0
            for sl,t in trees.items():
                hit=t.ray_cast(w+nrm*.002,nrm,.06)
                if hit[0] is not None: m|=BIT[sl]
            if 'hair' in trees and any(g.weight>.3 and o.vertex_groups[g.group].name=='mixamorig:Head' for g in v.groups):
                u=vuv.get(v.index); c=px[min(H_-1,int(u.y*H_)),min(W_-1,int(u.x*W_))] if u is not None else (0,0,0,1)
                skin=abs(c[0]-CAALI_SKIN[0]*c[1]/CAALI_SKIN[1])<.12 and c[0]>c[2]*1.2
                if not skin and (w.z>hz or w.y>hy+.01 or (w-LAND['head']).length>.20): m|=BIT['hair']   # Ikki's spikes/goggles hide under Caali's curls
            M.append(float(m))
        return M
    def _old_mask_for(o):
        M=[]
        for v in o.data.vertices:
            w=o.matrix_world@v.co; nrm=(o.matrix_world.to_3x3()@v.normal).normalized(); m=0
            for sl,t in trees.items():
                # hidden if a garment surface sits just outside this body point (ray along the body normal hits it within 6 cm)
                hit=t.ray_cast(w+nrm*.002,nrm,.06)
                if hit[0] is not None: m|=BIT[sl]
            if any(g.weight>.5 and o.vertex_groups[g.group].name=='mixamorig:Head' for g in v.groups) and 'head' in trees: m|=BIT['head']
            M.append(float(m))
        return M
    # weighted LODs: covered skin gets collapsed hardest
    b=BB; m0=mask_for(b); kg=b.vertex_groups.new(name='keep')
    for i,mv in enumerate(m0): kg.add([i],1. if mv==0 else .35,'REPLACE')
    BODY_LODS=[b]; vis=lambda o,M: sum(1 for p in o.data.polygons if all(M[k]==0 for k in p.vertices))
    for t in (4400,2200,900):
        c=b.copy(); c.data=b.data.copy(); bpy.context.collection.objects.link(c); sel(c); md=c.modifiers.new('d','DECIMATE'); md.ratio=t/tri(b); md.use_collapse_triangulate=True
        md.vertex_group='keep'; md.invert_vertex_group=True; md.vertex_group_factor=8; bpy.ops.object.modifier_apply(modifier=md.name)
        if tri(c)>t*1.08: decimate(c,t)
        BODY_LODS.append(c)
    bpy.data.objects.remove(BODY_LODS.pop(0))
    for o in BODY_LODS:
        Mv=mask_for(o); print('body LOD tris',tri(o),'visible-with-full-outfit',vis(o,Mv))
        at=o.data.attributes.new('_BM','FLOAT','POINT'); at.data.foreach_set('value',mask_for(o))
    for i,o in enumerate(BODY_LODS): o.name=f'body_base_LOD{i}'; o.data.name=o.name
    sel(arm,*BODY_LODS); fn=OUT+'body/base.glb'
    bpy.ops.export_scene.gltf(filepath=fn,export_format='GLB',use_selection=True,export_animations=False,export_skins=True,export_morph=False,export_image_format='WEBP',export_image_quality=80,export_yup=True,export_attributes=True)
    print('EXPORT',fn,[tri(o) for o in BODY_LODS],os.path.getsize(fn)//1024,'KB')
    # also save a per-original-vertex mask for other monolithic bodies built from this mesh (Ikki's GLB)
    np.save(OUT+'body/base_mask_rigged_verts.npy',np.array(mask_for(body)))
json.dump({'slots':SLOTS,'bits':BIT},open(OUT+'slots.json','w'))
