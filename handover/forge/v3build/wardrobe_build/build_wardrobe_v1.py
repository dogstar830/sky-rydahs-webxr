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
BV=np.array([body.matrix_world@v.co for v in body.data.vertices])
def grp_pts(names,thr=.4):
    ids={body.vertex_groups['mixamorig:'+n].index for n in names if 'mixamorig:'+n in body.vertex_groups}
    return np.array([BV[v.index] for v in body.data.vertices if any(g.group in ids and g.weight>thr for g in v.groups)])
def sel(*obs):
    bpy.ops.object.select_all(action='DESELECT')
    for o in obs: o.select_set(True)
    bpy.context.view_layer.objects.active=obs[0]
def tri(o): return sum(len(p.vertices)-2 for p in o.data.polygons)
def imp(fn):
    before=set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=DL+fn)
    new=[o for o in bpy.data.objects if o not in before]; ms=[o for o in new if o.type=='MESH']
    for o in new:
        if o.type!='MESH': bpy.data.objects.remove(o)
    o=ms[0]; o.parent=None; return o
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
def push_out(o,off=.006,iters=2):
    """pull any item vertex that is inside / too close to the body back out along the body normal (cheap anti-poke)"""
    dg=bpy.context.evaluated_depsgraph_get(); be=body.evaluated_get(dg); bm=bmesh.new(); bm.from_mesh(be.to_mesh()); bm.transform(body.matrix_world); tree=BVHTree.FromBMesh(bm)
    for _ in range(iters):
        for v in o.data.vertices:
            w=o.matrix_world@v.co; loc,nor,i,d=tree.find_nearest(w)
            if loc is None: continue
            s=(w-loc).dot(nor)
            if s<off: v.co=o.matrix_world.inverted()@(loc+nor*off)
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
    for side,sg in (('Left',1),('Right',-1)):
        pb=arm.pose.bones['mixamorig:'+side+'Arm']; pb.rotation_mode='QUATERNION'
        if theta_deg==0: pb.rotation_quaternion=(1,0,0,0); continue
        Rw=Matrix.Rotation(math.radians(theta_deg)*sg,4,'Y')  # world: +Y is back; left arm (+X) raises with +rot about Y
        bone_w=arm.matrix_world@pb.bone.matrix_local; head=bone_w.to_translation()
        new_w=Matrix.Translation(head)@Rw@Matrix.Translation(-head)@bone_w
        pb.matrix=arm.matrix_world.inverted()@new_w
    bpy.context.view_layer.update(); bpy.ops.object.mode_set(mode='OBJECT')
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
def export_item(slot,name,lods,extra_objs=()):
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
def garment_top(slot,fn,name,z_hem,targets):
    o=imp(fn); apply_xf(o)
    P=pts(o); a,b=P.min(0),P.max(0); s=(LAND['neck'].z+.04-z_hem)/(b[2]-a[2])
    o.scale=(s,s,s); o.location=Vector((LAND['hips'].x-(a[0]+b[0])/2*s, TY-(a[1]+b[1])/2*s, z_hem-a[2]*s)); apply_xf(o)
    th=sleeve_angle(o); print(slot,'sleeve angle',round(th,1))
    pose_arms(th); decimate(o,targets[0]*3); push_out(o,.008); weights_from_body(o)
    rest_bake(o); push_out(o,.006)
    downsize_images(o); lods=make_lods(o,targets); export_item(slot,name,lods); covered[slot]=lods[0]
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
if want('body'):
    b=body.copy(); b.data=body.data.copy(); bpy.context.collection.objects.link(b); b.parent=arm; b.matrix_parent_inverse=body.matrix_parent_inverse.copy()
    if not b.modifiers.get('Armature'): am=b.modifiers.new('Armature','ARMATURE'); am.object=arm
    downsize_images(b,1024,512); BODY_LODS=make_lods(b,[9000,4500,1600])
# ---------------- garments ----------------
if want('jacket'): garment_top('jacket','Meshy_AI_cropped_black_bomber__1028203848_texture.glb','caali_bomber',LAND['hips'].z+.07,[3600,1800,600])
if want('top'):    garment_top('top','Meshy_AI_black_crew_neck_t_shi_1028204645_texture.glb','caali_grb_zone_tee',LAND['hips'].z-.08,[1500,750,260])
if want('pants'):
    o=imp('Meshy_AI_black_cargo_pants_wit_1028203304_texture.glb'); apply_xf(o); P=pts(o); a,b=P.min(0),P.max(0)
    zt=LAND['hips'].z+.05; zb=.10; s=(zt-zb)/(b[2]-a[2]); legs=grp_pts(['LeftUpLeg','RightUpLeg']); hipw=legs[:,0].max()-legs[:,0].min()
    sx=min(s,hipw*1.3/(b[0]-a[0])); o.scale=(sx,s*.95,s); o.location=Vector((LAND['hips'].x-(a[0]+b[0])/2*sx, TY+.01-(a[1]+b[1])/2*s*.95, zb-a[2]*s)); apply_xf(o)
    decimate(o,9000); push_out(o,.01); weights_from_body(o); downsize_images(o); lods=make_lods(o,[2600,1300,450]); export_item('pants','caali_cargo',lods); covered['pants']=lods[0]
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
    lods=make_lods(g,[900,450,150]); export_item('gloves','caali_fingerless',lods); covered['gloves']=lods[0]
if want('neck'):
    o=imp('Meshy_AI_a_thick_gold_chain_ne_1028203541_texture.glb'); apply_xf(o); decimate(o,1200)
    o.rotation_euler=(math.radians(-72),0,0); apply_xf(o); P=pts(o); a,b=P.min(0),P.max(0); s=.25/(b[0]-a[0]); o.scale=(s,s,s); apply_xf(o)
    P=pts(o); o.location=Vector((LAND['neck'].x-P[:,0].mean(), TY-.01-P[:,1].mean(), LAND['neck'].z-.085-P[:,2].mean())); apply_xf(o)
    push_out(o,.012,3); weights_from_body(o,rigid={'Spine2':.7,'Neck':.3}); downsize_images(o,512,256)
    lods=make_lods(o,[600,300,90]); export_item('neck','gold_chain_thick',lods); covered['neck']=lods[0]
if want('hair') or want('head'):
    o=imp('Meshy_AI_short_black_curly_hai_1028203645_texture.glb'); apply_xf(o); decimate(o,14000)
    # split hair vs head (skin) by base-colour luminance at each face's UV centre
    mat=o.data.materials[0]; img=[n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and any(l.to_socket.name=='Base Color' for l in n.outputs['Color'].links)][0].image
    W_,H_=img.size; px=np.array(img.pixels[:]).reshape(H_,W_,4)
    uvl=o.data.uv_layers.active.data; skin=[]
    for p in o.data.polygons:
        u=sum((uvl[li].uv for li in p.loop_indices),Vector((0,0)))/len(p.loop_indices); c=px[min(H_-1,int(u.y*H_)),min(W_-1,int(u.x*W_))]
        skin.append(c[0]>.16 and c[0]>c[2]*1.15)   # warm brown skin vs near-black hair
    # fit whole head+hair to the Ikki head: chin at the neck joint, height to the head top (+hair volume)
    P=pts(o); a,b=P.min(0),P.max(0); H=(LAND['top'].z+.07)-(LAND['head'].z-.03); s=H/(b[2]-a[2]); hp=grp_pts(['Head'],.6)
    o.scale=(s,s,s); o.location=Vector((hp[:,0].mean()-(a[0]+b[0])/2*s, hp[:,1].mean()-.005-(a[1]+b[1])/2*s, LAND['head'].z-.03-a[2]*s)); apply_xf(o)
    parts={}
    for nm,flag in (('head',True),('hair',False)):
        c=o.copy(); c.data=o.data.copy(); bpy.context.collection.objects.link(c)
        bm=bmesh.new(); bm.from_mesh(c.data); bm.faces.ensure_lookup_table(); bmesh.ops.delete(bm,geom=[f for f in bm.faces if skin[f.index]!=flag],context='FACES'); bm.to_mesh(c.data); bm.free()
        weights_from_body(c,rigid={'Head':1.0}); downsize_images(c,512,256); parts[nm]=c
    bpy.data.objects.remove(o)
    if want('hair'): lods=make_lods(parts['hair'],[1800,900,300]); export_item('hair','caali_curly_short',lods); covered['hair']=lods[0]
    if want('head'): lods=make_lods(parts['head'],[1300,650,250]); export_item('head','caali_head',lods); covered['head']=lods[0]
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
    dg=bpy.context.evaluated_depsgraph_get(); trees={}
    for sl,it in covered.items():
        bm=bmesh.new(); bm.from_mesh(it.data); bm.transform(it.matrix_world); trees[sl]=BVHTree.FromBMesh(bm); bm.free()
    import pickle
    def mask_for(o):
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
    for o in BODY_LODS:
        at=o.data.attributes.new('_BM','FLOAT','POINT'); at.data.foreach_set('value',mask_for(o))
    for i,o in enumerate(BODY_LODS): o.name=f'body_base_LOD{i}'; o.data.name=o.name
    sel(arm,*BODY_LODS); fn=OUT+'body/base.glb'
    bpy.ops.export_scene.gltf(filepath=fn,export_format='GLB',use_selection=True,export_animations=False,export_skins=True,export_morph=False,export_image_format='WEBP',export_image_quality=80,export_yup=True,export_attributes=True)
    print('EXPORT',fn,[tri(o) for o in BODY_LODS],os.path.getsize(fn)//1024,'KB')
    # also save a per-original-vertex mask for other monolithic bodies built from this mesh (Ikki's GLB)
    np.save(OUT+'body/base_mask_rigged_verts.npy',np.array(mask_for(body)))
json.dump({'slots':SLOTS,'bits':BIT},open(OUT+'slots.json','w'))
