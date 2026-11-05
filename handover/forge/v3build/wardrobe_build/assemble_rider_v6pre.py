# Bakes a wardrobe loadout into ONE skinned mesh per LOD (single material, one 2048x3072 atlas for base/normal/MR) so a full
# rider costs 1 draw call, exactly like ikki-meshy-skate.glb. Every vertex keeps _SLOT (slot index+1, body=0) and the body keeps _BM
# (bitmask of slots that cover it) so the JS wardrobe API can hide/replace baked pieces at runtime without a rebuild.
# usage: blender -b -P assemble_rider.py -- <outfit.json> <out.glb> <MeshName>
import bpy, bmesh, math, json, sys, os, numpy as np
from mathutils import Vector, Matrix
A=sys.argv[sys.argv.index('--')+1:]; OUTFIT=json.load(open(A[0])); OUTF=A[1]; NAME=A[2]
WD=os.environ.get('WD','/workspace/skyrydahs-characters/wardrobe/'); CELL=int(os.environ.get('CELL','1024')); SL=json.load(open(WD+'slots.json')); SLOTS=SL['slots']
bpy.ops.wm.read_factory_settings(use_empty=True)
def imp(fn):
    before=set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=fn); return [o for o in bpy.data.objects if o not in before]
new=imp(WD+'body/base.glb'); arm=[o for o in new if o.type=='ARMATURE'][0]
def lods_of(objs):
    L={}
    for o in objs:
        import re; mm=re.search(r'_LOD(\d)',o.name)
        if o.type=='MESH' and mm: L[int(mm.group(1))]=o
        elif o.type=='MESH': print('skip mesh',o.name); bpy.data.objects.remove(o)
    return L
parts={'body':lods_of(new)}
for slot,item in OUTFIT.items():
    if slot=='skates' or not item: continue
    ob=imp(WD+f'{slot}/{item}.glb'); a2=[o for o in ob if o.type=='ARMATURE'][0]; L=lods_of(ob)
    for o in L.values():
        mw=o.matrix_world.copy(); o.parent=arm; o.matrix_world=mw
        for m in o.modifiers:
            if m.type=='ARMATURE': m.object=arm
    bpy.data.objects.remove(a2); parts[slot]=L
# reference full body for skate foot frames (same as build_lod_v3)
ref=imp('/workspace/skyrydahs-characters/meshy/ikki-meshy-rigged.glb'); rarm=[o for o in ref if o.type=='ARMATURE'][0]; body=[o for o in ref if o.type=='MESH' and o.parent==rarm][0]
B=lambda n: rarm.data.bones['mixamorig:'+n]; W=lambda v: rarm.matrix_world@v
MODULE='/workspace/skyrydahs-characters/shared/at-skate/at-skate-meshy.blend'
def foot_frame(side):
    foot=B(side+'Foot'); toe=B(side+'ToeBase'); h=W(foot.head_local); t=W(toe.head_local)
    d=Vector((t.x-h.x,t.y-h.y,0)).normalized(); ang=math.atan2(d.x,-d.y)
    ids={body.vertex_groups['mixamorig:'+side+'Foot'].index,body.vertex_groups['mixamorig:'+side+'ToeBase'].index}
    pts=[body.matrix_world@v.co for v in body.data.vertices if (body.matrix_world@v.co).z<.11 and any(g.group in ids and g.weight>.4 for g in v.groups)]
    R=Matrix.Rotation(ang,3,'Z'); loc=[R.inverted()@p for p in pts]
    ys=sorted(p.y for p in loc); xs=sorted(p.x for p in loc); ys=ys[int(len(ys)*.02):int(len(ys)*.98)]; zs=[p.z for p in pts]
    L=max(ys)-min(ys); cy=(max(ys)+min(ys))/2; cx=(max(xs)+min(xs))/2; c=R@Vector((cx,cy,0)); return ang,Vector((c.x,c.y,min(zs))),L
def sel(*obs):
    bpy.ops.object.select_all(action='DESELECT')
    for o in obs: o.select_set(True)
    bpy.context.view_layer.objects.active=obs[0]
def skate(side,lod):
    with bpy.data.libraries.load(MODULE) as (src,dst): dst.objects=[n for n in src.objects if n.endswith(f'_L{lod}')]
    ang,o,L=foot_frame(side); k=max(1.,L/.30)
    M=Matrix.Translation(o)@Matrix.Rotation(ang,4,'Z')@Matrix.Diagonal(((k if side=='Left' else -k),k,k,1))@Matrix.Translation((0,-.02,0))
    ps=[]
    for ob in dst.objects:
        bpy.context.collection.objects.link(ob); ob.parent=None; ob.matrix_world=M@ob.matrix_basis
        me=ob.data=ob.data.copy(); wheel=ob.name.startswith('Wheel'); c=ob.matrix_world.to_translation(); ax=(ob.matrix_world.to_3x3()@Vector((1,0,0))).normalized()
        sel(ob); bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
        if side!='Left':
            bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.reverse_faces(bm,faces=bm.faces[:]); bm.to_mesh(me); bm.free()
        wc=me.attributes.new('_WC','FLOAT_VECTOR','POINT'); wa=me.attributes.new('_WA','FLOAT_VECTOR','POINT')
        for i in range(len(me.vertices)): wc.data[i].vector=(c.x,c.z,-c.y) if wheel else (0,0,0); wa.data[i].vector=(ax.x,ax.z,-ax.y) if wheel else (0,0,0)
        if ob.name.startswith('ShellBlend'):
            ca=me.color_attributes.get('Col')
            for i,v in enumerate(me.vertices):
                if v.co.z-o.z < -.006: ca.data[i].color=(13/16.,0,0,1)
            gF=ob.vertex_groups.new(name='mixamorig:'+side+'Foot'); gL=ob.vertex_groups.new(name='mixamorig:'+side+'Leg')
            for v in me.vertices:
                h=v.co.z-o.z; t=min(1,max(0,(h-.17)/(.32-.17))); t=t*t*(3-2*t)
                if t<1: gF.add([v.index],1-t,'REPLACE')
                if t>0: gL.add([v.index],t,'REPLACE')
        else:
            vg=ob.vertex_groups.new(name='mixamorig:'+side+('Leg' if ob.name.startswith('Cuff') else 'Foot')); vg.add(list(range(len(me.vertices))),1.,'REPLACE')
        ps.append(ob)
    sel(*ps); bpy.ops.object.join(); j=bpy.context.object; j.parent=arm; am=j.modifiers.new('Armature','ARMATURE'); am.object=arm; return j
# ---------------- atlas ----------------
AW=AH=4*CELL   # one atlas, one material, one draw call; 4x4 grid of CELLxCELL cells (quest 1024 -> 4096^2, hd 1536 -> 6144^2)
_L={'skates':(0,0,1,1),'body':(1,0,1,1),'hair':(2,0,1,1),'gloves':(3,0,.5,.5),'neck':(3.5,0,.5,.5),'accessory':(3,.5,.5,.5),
    'head':(0,1,2,2),'jacket':(2,1,2,1),'pants':(2,2,2,1),'top':(0,3,2,1)}
TILES={k:(int(x*CELL),int(y*CELL),int(w*CELL),int(h*CELL)) for k,(x,y,w,h) in _L.items()}
ATL={k:np.zeros((AH,AW,4),np.float32) for k in ('c','n','mr')}; ATL['n'][...]=(.5,.5,1,1); ATL['mr'][...]=(0,.8,0,1); ATL['c'][...,3]=1
def imgs_of(o):
    mat=o.data.materials[0]; nt=mat.node_tree; bs=[n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'][0]; out={}
    def up(sock):
        if not sock.links: return None
        n=sock.links[0].from_node
        while n.type!='TEX_IMAGE':
            ins=[i for i in n.inputs if i.links]
            if not ins: return None
            n=ins[0].links[0].from_node
        return n.image
    out['c']=up(bs.inputs['Base Color']); out['n']=up(bs.inputs['Normal']); out['mr']=up(bs.inputs['Roughness']) or up(bs.inputs['Metallic'])
    return out,bs
def paste(key,img,tile,fill=None):
    x,y,w,h=tile
    if img is None:
        ATL[key][y:y+h,x:x+w]=fill; return
    im=img.copy(); im.scale(w,h); px=np.array(im.pixels[:],np.float32).reshape(h,w,4); bpy.data.images.remove(im); ATL[key][y:y+h,x:x+w]=px
# skate tile straight from Ikki's atlas (bottom-left 1024 in blender pixel order) -> same Meshy AT textures
for key,fn in (('c','ikki_atlas.png'),('n','ikki_atlas_n.png'),('mr','ikki_atlas_mr.png')):
    im=bpy.data.images.load('/workspace/v3build/ikki_v3/'+fn); im.colorspace_settings.name='Non-Color'; px=np.array(im.pixels[:],np.float32).reshape(im.size[1],im.size[0],im.channels if im.channels==4 else 4)
    tile=bpy.data.images.new('t',1024,1024,alpha=True,float_buffer=True); tile.pixels.foreach_set(px[0:1024,0:1024].ravel()); tile.scale(CELL,CELL); ATL[key][0:CELL,0:CELL]=np.array(tile.pixels[:],np.float32).reshape(CELL,CELL,4)
for slot,L in parts.items():
    tile=TILES[slot]; I,bs=imgs_of(L[0])
    for im in I.values():
        if im: im.colorspace_settings.name='Non-Color'   # copy raw values
    rough=bs.inputs['Roughness'].default_value; met=bs.inputs['Metallic'].default_value
    paste('c',I['c'],tile,(*bs.inputs['Base Color'].default_value[:3],1)); paste('n',I['n'] if os.environ.get('ITEM_NORMALS')=='1' else None,tile,(.5,.5,1,1))   # Meshy normal maps came out scrambled in the atlas (faceted face); flat until a proper bake; paste('mr',I['mr'],tile,(0,rough,met,1))
    if I['mr'] is None: pass
    elif slot in ('hair','top','pants','jacket','gloves','body'):   # cloth/skin: never chrome (Meshy MR often reads metallic)
        x,y,w,h=tile; ATL['mr'][y:y+h,x:x+w,2]*=.15
def mkimg(key,name,colour):
    im=bpy.data.images.new(name,AW,AH,alpha=False,float_buffer=False); im.pixels.foreach_set(ATL[key].ravel()); 
    if not colour: im.colorspace_settings.name='Non-Color'
    return im
AC=mkimg('c',NAME+'_atlas',True); AN=mkimg('n',NAME+'_atlas_n',False); AM_=mkimg('mr',NAME+'_atlas_mr',False)
MAT=bpy.data.materials.new(NAME+'Atlas'); MAT.use_nodes=True; nt=MAT.node_tree; bs=nt.nodes['Principled BSDF']
t=nt.nodes.new('ShaderNodeTexImage'); t.image=AC; nt.links.new(t.outputs['Color'],bs.inputs['Base Color'])
t=nt.nodes.new('ShaderNodeTexImage'); t.image=AN; nm=nt.nodes.new('ShaderNodeNormalMap'); nt.links.new(t.outputs['Color'],nm.inputs['Color']); nt.links.new(nm.outputs['Normal'],bs.inputs['Normal'])
t=nt.nodes.new('ShaderNodeTexImage'); t.image=AM_; sp=nt.nodes.new('ShaderNodeSeparateColor'); nt.links.new(t.outputs['Color'],sp.inputs['Color']); nt.links.new(sp.outputs['Green'],bs.inputs['Roughness']); nt.links.new(sp.outputs['Blue'],bs.inputs['Metallic'])
def prep(o,slot):
    me=o.data; x,y,sw,sh=TILES[slot]
    uv=me.uv_layers.active
    if uv is None: uv=me.uv_layers.new()
    for d in uv.data:
        u,v=d.uv; u=min(max(u,0),1); v=min(max(v,0),1); d.uv=((x+u*sw*.998+sw*.001)/AW,(y+v*sh*.998+sh*.001)/AH)
    for n in list(me.uv_layers):
        if n!=uv: me.uv_layers.remove(n)
    if 'Col' not in me.color_attributes:
        ca=me.color_attributes.new('Col','FLOAT_COLOR','POINT')
        for d in ca.data: d.color=(0,0,0,1)
    me.color_attributes.active_color=me.color_attributes['Col']
    for nm in ('_WC','_WA'):
        if nm not in me.attributes: me.attributes.new(nm,'FLOAT_VECTOR','POINT')
    if '_BM' not in me.attributes: me.attributes.new('_BM','FLOAT','POINT')
    at=me.attributes.get('_SLOT') or me.attributes.new('_SLOT','FLOAT','POINT'); at.data.foreach_set('value',[float(0 if slot=='body' else SLOTS.index(slot)+1)]*len(me.vertices))
    me.materials.clear(); me.materials.append(MAT)
    if slot!='skates':
        for poly in me.polygons: poly.use_smooth=True
        sel(o); bpy.ops.mesh.customdata_custom_splitnormals_clear() if me.has_custom_normals else None
out=[]
for li in range(3):
    obs=[]
    for slot,L in parts.items(): prep(L[li],slot); obs.append(L[li])
    if OUTFIT.get('skates'):
        for side in ('Left','Right'): s_=skate(side,li); prep(s_,'skates'); obs.append(s_)
    sel(obs[0],*obs[1:]); bpy.context.view_layer.objects.active=obs[0]; bpy.ops.object.join(); j=bpy.context.object
    j.name=f'{NAME}_LOD{li}'; j.data.name=j.name; print('LOD',li,'tris',sum(len(p.vertices)-2 for p in j.data.polygons)); out.append(j)
for o in ref: 
    if o.name in bpy.data.objects: bpy.data.objects.remove(o)
sel(arm,*out)
bpy.ops.export_scene.gltf(filepath=OUTF,export_format='GLB',use_selection=True,export_animations=False,export_vertex_color='ACTIVE',export_image_format='WEBP',export_image_quality=82,export_yup=True,export_skins=True,export_morph=False,export_attributes=True)
print('EXPORT',OUTF,os.path.getsize(OUTF)//1024,'KB')
