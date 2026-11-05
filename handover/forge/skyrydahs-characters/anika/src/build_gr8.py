# GR8 build (Rydah Forge 2026-10-30): Meshy hi -> strip Meshy skates -> shared A-T -> voxel remesh+decimate per LOD ->
# smart UV in body cell (u 0-.75) -> bake col/nrm/orm from hi -> decals -> skate tex in cell (u .75-1, v .5-1) -> one material per LOD.
import bpy,bmesh,math,os,sys,json,numpy as np
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
G='/workspace/forge_kit/gr8/'; N=os.environ['N']; CFG=json.loads(os.environ['CFG'])
def sel(*obs):
    bpy.ops.object.select_all(action='DESELECT')
    for o in obs: o.select_set(True)
    bpy.context.view_layer.objects.active=obs[0]
tri=lambda o: sum(len(p.vertices)-2 for p in o.data.polygons)
bpy.ops.wm.open_mainfile(filepath=G+N+'_hi.blend'); sc=bpy.context.scene
for o in list(bpy.data.objects):
    if o.name!='HI': bpy.data.objects.remove(o)
hi=bpy.data.objects['HI']; Mw=hi.matrix_world
co=np.zeros(len(hi.data.vertices)*3); hi.data.vertices.foreach_get('co',co); co=co.reshape(-1,3)
# --- 1) Meshy skate footprint per side (z<.06): centre + length -> shared skate placement
FOOT={}
for side,sg in (('Left',1),('Right',-1)):   # Blender +X = rider's left (faces -Y)
    b=co[(co[:,2]<.06)&(co[:,0]*sg>0)]; FOOT[side]=dict(cx=float((b[:,0].min()+b[:,0].max())/2),cy=float((b[:,1].min()+b[:,1].max())/2),L=float(b[:,1].max()-b[:,1].min()))
print('FOOT',FOOT)
MODULE='/workspace/skyrydahs-characters/shared/at-skate/at-skate-meshy.blend'
def attrs(me):
    if 'Col' not in me.color_attributes:
        ca=me.color_attributes.new('Col','FLOAT_COLOR','POINT')
        for d in ca.data: d.color=(0,0,0,1)
    for nm in ('_WC','_WA'):
        if nm not in me.attributes: me.attributes.new(nm,'FLOAT_VECTOR','POINT')
MODLEN=None
def skate(side,lod,cell=True):
    global MODLEN
    with bpy.data.libraries.load(MODULE) as (src,dst): dst.objects=[n for n in src.objects if n.endswith(f'_L{lod}')]
    if MODLEN is None:
        ys=[]
        for ob in dst.objects:
            if ob.name.startswith('ShellBlend'):
                ys=[(ob.matrix_basis@v.co).y for v in ob.data.vertices]
        MODLEN=max(ys)-min(ys); print('MODLEN',MODLEN)
    f=FOOT[side]; k=f['L']/MODLEN*CFG.get('skk',1.0)
    M=Matrix.Translation((f['cx'],f['cy'],0))@Matrix.Diagonal(((k if side=='Left' else -k),k,k,1))
    ps=[]
    for ob in dst.objects:
        bpy.context.collection.objects.link(ob); ob.parent=None; ob.matrix_world=M@ob.matrix_basis
        me=ob.data=ob.data.copy(); wheel=ob.name.startswith('Wheel'); cc=ob.matrix_world.to_translation(); ax=(ob.matrix_world.to_3x3()@Vector((1,0,0))).normalized()
        sel(ob); bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
        if side!='Left':
            b2=bmesh.new(); b2.from_mesh(me); bmesh.ops.reverse_faces(b2,faces=b2.faces[:]); b2.to_mesh(me); b2.free()
        attrs(me); wc=me.attributes['_WC']; wa=me.attributes['_WA']
        for i in range(len(me.vertices)): wc.data[i].vector=(cc.x,cc.z,-cc.y) if wheel else (0,0,0); wa.data[i].vector=(ax.x,ax.z,-ax.y) if wheel else (0,0,0)
        ca=me.color_attributes['Col']
        if ob.name.startswith('ShellBlend'):
            for i,v in enumerate(me.vertices):
                if v.co.z < -.006: ca.data[i].color=(13/16.,0,0,1)
        if cell:
            for dd in me.uv_layers.active.data:
                u,v=dd.uv; dd.uv=(.875,.13) if wheel else (.75+min(max(u,0),1)*.25*.996+.0005,.5+min(max(v,0),1)*.5*.996+.001)
        me.materials.clear(); ps.append(ob)
    sel(*ps); bpy.ops.object.join(); j=bpy.context.object; j.name=f'Skate_{side}_L{lod}'
    if cell:   # black inner liner: closes the see-through gaps between the shared shell's UV-island shards (add-on, shell untouched)
        ln=j.copy(); ln.data=j.data.copy(); bpy.context.collection.objects.link(ln); sel(ln)
        r_=ln.modifiers.new('r','REMESH'); r_.mode='VOXEL'; r_.voxel_size=.007; bpy.ops.object.modifier_apply(modifier='r')
        d_=ln.modifiers.new('d','DECIMATE'); d_.ratio=min(1,(700,450,200)[lod]/max(1,tri(ln))); bpy.ops.object.modifier_apply(modifier='d')
        b_=bmesh.new(); b_.from_mesh(ln.data); b_.normal_update()
        for v in b_.verts: v.co-=v.normal*.003
        b_.to_mesh(ln.data); b_.free()
        if not ln.data.uv_layers: ln.data.uv_layers.new(name=j.data.uv_layers.active.name)
        for dd in ln.data.uv_layers.active.data: dd.uv=(.875,.37)
        attrs(ln.data)
        for d in ln.data.attributes['_WC'].data: d.vector=(0,0,0)
        sel(j,ln); bpy.context.view_layer.objects.active=j; bpy.ops.object.join(); j=bpy.context.object
    zmin=min(v.co.z for v in j.data.vertices)
    for v in j.data.vertices: v.co.z-=zmin
    wc=j.data.attributes['_WC']
    for d in wc.data:
        if d.vector.length>0: d.vector=(d.vector[0],d.vector[1]-zmin,d.vector[2])
    return j
# probe skate top (L0) to choose the cut
pr=[skate(s,0,False) for s in ('Left','Right')]
TOP=min(max(v.co.z for v in p.data.vertices) for p in pr); print('SKATE_TOP',TOP)
# shell top at the leg (verts near the foot centre column): use 85th pct of shell z within 6cm of leg axis
for p in pr: bpy.data.objects.remove(p)
ZCUT=CFG['boot']; print('ZCUT',ZCUT)
# --- 2) strip Meshy skates at the boot top, then extend the leg/sock/pant hem down into the A-T shell (no gap, no Meshy boot remnant)
bm=bmesh.new(); bm.from_mesh(hi.data); bmesh.ops.remove_doubles(bm,verts=bm.verts[:],dist=.0001); kill=[v for v in bm.verts if v.co.z<ZCUT]; bmesh.ops.delete(bm,geom=kill,context='VERTS')
bnd=[e for e in bm.edges if e.is_boundary and all(v.co.z<ZCUT+.03 for v in e.verts)]
uvl_=bm.loops.layers.uv.active; CI=None
for nd in hi.data.materials[0].node_tree.nodes:
    if nd.type=='TEX_IMAGE' and nd.image.size[0]==8192: CI=nd.image
cw_,ch_=CI.size; CPX=np.empty(cw_*ch_*4,dtype=np.float32); CI.pixels.foreach_get(CPX); CPX=CPX.reshape(ch_,cw_,4); smp=[]
for e in bnd:
    for lo in e.link_loops:
        u,v=lo[uvl_].uv; smp.append(CPX[min(ch_-1,int(v*ch_)),min(cw_-1,int(u*cw_)),:3])
HEMC=np.median(np.array(smp),0); del CPX; print('HEM colour (srgb)',HEMC)
r=bmesh.ops.extrude_edge_only(bm,edges=bnd); nv=[g for g in r['geom'] if isinstance(g,bmesh.types.BMVert)]
for g in r['geom']:
    if isinstance(g,bmesh.types.BMFace): g.material_index=1
for v in nv:
    sd='Left' if v.co.x>0 else 'Right'; f=FOOT[sd]; v.co.z=TOP-.035; v.co.x=f['cx']+(v.co.x-f['cx'])*.9; v.co.y=f['cy']+(v.co.y-f['cy'])*.9
hm=bpy.data.materials.new('hem'); hm.use_nodes=True; hn=hm.node_tree; hb=hn.nodes['Principled BSDF']
lin=lambda c: c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
HEM_RGB=hn.nodes.new('ShaderNodeRGB'); HEM_RGB.outputs[0].default_value=(*[lin(float(c)) for c in HEMC],1)
HEM_ORM=hn.nodes.new('ShaderNodeRGB'); HEM_ORM.outputs[0].default_value=(1,.8,0,1)
HEM_EM=hn.nodes.new('ShaderNodeEmission'); hb.inputs['Base Color'].default_value=HEM_RGB.outputs[0].default_value
hi.data.materials.append(hm)
bm.to_mesh(hi.data); bm.free(); print('stripped verts',len(kill),'extruded hem verts',len(nv))
# hi material: find nodes
mat=hi.data.materials[0]; nt=mat.node_tree; bs=nt.nodes['Principled BSDF']; out=nt.nodes['Material Output']
def src(sock):
    for l in nt.links:
        if l.to_socket==sock: return l.from_node
COL=src(bs.inputs['Base Color']); MR=src(src(bs.inputs['Roughness']).inputs['Color'])
EM=nt.nodes.new('ShaderNodeEmission')
# --- 3) decal planes (front/back projected on hi)
bvh=BVHTree.FromObject(hi,bpy.context.evaluated_depsgraph_get())
DEC=[]
for dc in CFG['decals']:
    img=bpy.data.images.load(G+dc['img']); w,h=dc['w'],dc['h']; x0,z0=dc['x']-w/2,dc['z']-h/2; back=dc['side']=='back'
    me=bpy.data.meshes.new('decal'); b=bmesh.new(); uvl=b.loops.layers.uv.new('UVMap'); R=40; V={}
    for i in range(R+1):
        for j in range(R+1):
            x=x0+w*i/R; z=z0+h*j/R; o=Vector((x,1. if back else -1.,z)); d=Vector((0,-1 if back else 1,0))
            hit=bvh.ray_cast(o,d,3.)
            p=hit[0]-d*.004 if hit[0] else Vector((x,0,z))
            V[i,j]=(b.verts.new(p),((1-i/R) if back else i/R, j/R))
    for i in range(R):
        for j in range(R):
            q=[V[i,j],V[i+1,j],V[i+1,j+1],V[i,j+1]]
            f=b.faces.new([a[0] for a in q])
            for lo,a in zip(f.loops,q): lo[uvl].uv=a[1]
    b.to_mesh(me); b.free(); ob=bpy.data.objects.new('Decal_'+dc['img'],me); bpy.context.collection.objects.link(ob)
    dm=bpy.data.materials.new('dm'); dm.use_nodes=True; t=dm.node_tree; t.nodes.remove(t.nodes['Principled BSDF']); ti=t.nodes.new('ShaderNodeTexImage'); ti.image=img
    e=t.nodes.new('ShaderNodeEmission'); t.links.new(e.outputs[0],t.nodes['Material Output'].inputs['Surface']); me.materials.append(dm)
    DEC.append((ob,ti,e,t))
sc.render.engine='CYCLES'; sc.cycles.samples=1; sc.cycles.device='CPU'
bk=sc.render.bake; bk.use_selected_to_active=True; bk.margin=4
SKT={'col':'at-skate-meshy-1k.png','nrm':'at-skate-meshy-1k-normal.png','orm':'at-skate-meshy-1k-mr.png'}
SKD='/workspace/skyrydahs-characters/shared/at-skate/'
def bake_lod(lo,tag,RC,RN):
    sel(lo); bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.quads_convert_to_tris()
    while lo.data.uv_layers: bpy.ops.object.mode_set(mode='OBJECT'); lo.data.uv_layers.remove(lo.data.uv_layers[0]); bpy.ops.object.mode_set(mode='EDIT')
    lo.data.uv_layers.new(name='UVMap'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.0015,area_weight=0.)
    bpy.ops.object.mode_set(mode='OBJECT')
    for d in lo.data.uv_layers.active.data: u,v=d.uv; d.uv=(u*.75*.998,v)
    for p in lo.data.polygons: p.use_smooth=True
    I={}
    for k,Rr,nc in (('col',RC,0),('nrm',RN,1),('orm',RN,1)):
        im=bpy.data.images.new(f'{N}_{tag}_{k}',Rr,Rr,alpha=False); im.colorspace_settings.name='Non-Color' if nc else 'sRGB'
        if k=='nrm': im.generated_color=(.5,.5,1,1)
        I[k]=im
    lm=bpy.data.materials.new(f'{CFG["mat"]}_{tag}'); lm.use_nodes=True; lt=lm.node_tree; lb=lt.nodes['Principled BSDF']
    T={k:lt.nodes.new('ShaderNodeTexImage') for k in I}
    for k in I: T[k].image=I[k]
    lo.data.materials.clear(); lo.data.materials.append(lm)
    for p in lo.data.polygons: p.material_index=0
    def bake(k,typ,srcobs,ext,dist):
        for o in bpy.data.objects: o.select_set(False)
        for o in srcobs: o.select_set(True)
        lo.select_set(True); bpy.context.view_layer.objects.active=lo
        bk.cage_extrusion=ext; bk.max_ray_distance=dist
        for kk in T: T[kk].select=False
        lt.nodes.active=T[k]; T[k].select=True
        bpy.ops.object.bake(type=typ,normal_space='TANGENT') if typ=='NORMAL' else bpy.ops.object.bake(type=typ)
    HO=hn.nodes['Material Output']
    nt.links.new(bs.outputs[0],out.inputs['Surface']); hn.links.new(hb.outputs[0],HO.inputs['Surface']); bake('nrm','NORMAL',[hi],.015,.035)
    nt.links.new(COL.outputs[0],EM.inputs[0]); nt.links.new(EM.outputs[0],out.inputs['Surface']); hn.links.new(HEM_RGB.outputs[0],HEM_EM.inputs[0]); hn.links.new(HEM_EM.outputs[0],HO.inputs['Surface']); bake('col','EMIT',[hi],.015,.035)
    nt.links.new(MR.outputs[0],EM.inputs[0]); hn.links.new(HEM_ORM.outputs[0],HEM_EM.inputs[0]); bake('orm','EMIT',[hi],.015,.035)
    nt.links.new(bs.outputs[0],out.inputs['Surface']); hn.links.new(hb.outputs[0],HO.inputs['Surface'])
    def gp(im):
        a=np.empty(im.size[0]*im.size[1]*4,dtype=np.float32); im.pixels.foreach_get(a); return a.reshape(im.size[1],im.size[0],4)
    px={k:gp(I[k]) for k in I}
    px['orm'][...,0]=1.
    # decals: bake rgb + alpha with only the decal as source, composite
    for ob,ti,e,t in DEC:
        dd={}
        for mode in ('rgb','a'):
            t.links.new(ti.outputs['Color' if mode=='rgb' else 'Alpha'],e.inputs[0])
            tmp=bpy.data.images.new('tmp',RC,RC,alpha=False); tmp.generated_color=(0,0,0,1); tmp.colorspace_settings.name='sRGB' if mode=='rgb' else 'Non-Color'
            T['col'].image=tmp; bake('col','EMIT',[ob],.02,.04); T['col'].image=I['col']
            dd[mode]=gp(tmp); bpy.data.images.remove(tmp)
        a=dd['a'][...,:1]; px['col'][...,:3]=px['col'][...,:3]*(1-a)+dd['rgb'][...,:3]*a
        if RN!=RC:
            from PIL import Image as PI
            a2=np.array(PI.fromarray((a[...,0]*255).astype(np.uint8)).resize((RN,RN)),dtype=np.float32)[...,None]/255.
        else: a2=a
        px['orm'][...,1:2]=px['orm'][...,1:2]*(1-a2)+.7*a2; px['orm'][...,2:3]*=(1-a2)
        px['nrm'][...,:3]=px['nrm'][...,:3]*(1-a2)+np.array([.5,.5,1.])*a2
        print('decal',ob.name,'texels',int((a>.5).sum()))
    # skate texture into cell
    from PIL import Image as PI
    for k,f in SKT.items():
        Rr=px[k].shape[0]; cw,ch=Rr//4,Rr//2; s=np.array(PI.open(SKD+f).convert('RGBA').resize((cw,ch)),dtype=np.float32)/255.
        s=s[::-1]   # PIL top-down -> blender bottom-up
        if k=='orm':   # tame metal/rough at island borders (mirror slivers in the shared MR bake)
            s=s.copy(); s[...,0]=1.; s[...,1]=np.maximum(s[...,1],.4); s[...,2]=np.minimum(s[...,2],.5)
        if k=='col':   # standard skate in Oliver's colours: black shell, gold accents (cyan/red LEDs -> gold)
            rgb=s[...,:3]; mx=rgb.max(-1,keepdims=True); mn=rgb.min(-1,keepdims=True); sat=(mx-mn)/(mx+1e-4)
            lum=(.3*rgb[...,:1]+.59*rgb[...,1:2]+.11*rgb[...,2:3]); acc=np.clip((sat-.45)*3,0,1)*np.clip((mx-.35)*3,0,1)
            blk=np.clip(lum*.55,0,1)*np.array([1,1,1.05]); gold=np.array([1.,.843,0.])*np.clip(.55+mx,0,1)
            s[...,:3]=blk*(1-acc)+gold*acc
        px[k][int(Rr*.02):int(Rr*.24),Rr-cw+int(cw*.06):Rr-int(cw*.06),:3]={'col':np.array([1.,.80,.05]),'nrm':np.array([.5,.5,1.]),'orm':np.array([1.,.35,0.])}[k]   # gold wheel swatch
        px[k][int(Rr*.26):int(Rr*.48),Rr-cw+int(cw*.06):Rr-int(cw*.06),:3]={'col':np.array([.02,.02,.022]),'nrm':np.array([.5,.5,1.]),'orm':np.array([1.,.6,0.])}[k]   # black liner swatch
        px[k][Rr-ch:Rr,Rr-cw:Rr]=s
    for k in I:
        I[k].pixels.foreach_set(px[k].ravel()); I[k].filepath_raw=G+f'tex/{N}_{tag}_{k}.png'; I[k].file_format='PNG'; I[k].save(); I[k].pack()
    lt.links.new(T['col'].outputs[0],lb.inputs['Base Color'])
    sp=lt.nodes.new('ShaderNodeSeparateColor'); lt.links.new(T['orm'].outputs[0],sp.inputs[0]); lt.links.new(sp.outputs[1],lb.inputs['Roughness']); lt.links.new(sp.outputs[2],lb.inputs['Metallic'])
    nm=lt.nodes.new('ShaderNodeNormalMap'); lt.links.new(T['nrm'].outputs[0],nm.inputs['Color']); lt.links.new(nm.outputs[0],lb.inputs['Normal'])
    return lm
os.makedirs(G+'tex',exist_ok=True)
# --- 4) voxel base
base=hi.copy(); base.data=hi.data.copy(); bpy.context.collection.objects.link(base); 
sel(base); bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.remove_doubles(threshold=.0001); bpy.ops.mesh.delete_loose(); bpy.ops.object.mode_set(mode='OBJECT')
while base.data.uv_layers: base.data.uv_layers.remove(base.data.uv_layers[0])
print('BASE tris (welded hi)',tri(base))
OUT={}
for tag,tgt,RC,RN,slod in CFG['lods']:
    lo=base.copy(); lo.data=base.data.copy(); bpy.context.collection.objects.link(lo); lo.name=f'{CFG["prefix"]}_{tag}'
    sel(lo); md=lo.modifiers.new('d','DECIMATE'); md.ratio=min(1,tgt/tri(lo)); md.use_collapse_triangulate=True; bpy.ops.object.modifier_apply(modifier='d')
    lm=bake_lod(lo,tag,RC,RN); attrs(lo.data)
    sk=[skate(s,slod) for s in ('Left','Right')]
    for s_ in sk: s_.data.materials.append(lm)
    sel(lo,*sk); bpy.context.view_layer.objects.active=lo; bpy.ops.object.join(); lo=bpy.context.object; lo.data.name=lo.name
    print('LOD',tag,'tris',tri(lo)); OUT[tag]=lo.name
for ob,*_ in DEC: bpy.data.objects.remove(ob)
bpy.data.objects.remove(base); bpy.data.objects.remove(hi)
bpy.ops.wm.save_as_mainfile(filepath=G+N+'_lods.blend'); print('SAVED',OUT)
