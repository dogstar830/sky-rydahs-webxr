# Rydah Forge 2026-10-30: edit Rigger's rigged GLBs in place (skin weights kept):
#  1) strip baked A-T skate (UV cell u>=.75), cap leg hems  2) Anika: split braids from top, refill, braid verts -> braid bones + Head only
#  3) optional Right-arm forearm shortening (Caali) with matching Hand-chain joint shift (per-rider IBM), weights kept.
import sys,os,json,struct,io,numpy as np
sys.path.insert(0,'/workspace/forge_kit/gr8/fix'); from glbio import *
from PIL import Image
src,dst,colsrc=sys.argv[1:4]; ARMFIX=json.loads(sys.argv[4]) if len(sys.argv)>4 else {}
j,b=load(src); sk=j['skins'][0]; JN=[j['nodes'][i]['name'] for i in sk['joints']]
IBM=acc(j,b,sk['inverseBindMatrices']).reshape(-1,4,4).transpose(0,2,1); JP=np.array([np.linalg.inv(m)[:3,3] for m in IBM])
jid=lambda n: JN.index(n)
# colour atlases (webp main file) by image name
jc,bc=load(colsrc); COL={}
for im in jc['images']:
    if im['name'].endswith('_col'):
        v=jc['bufferViews'][im['bufferView']]; COL[im['name']]=np.asarray(Image.open(io.BytesIO(bytes(bc[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']]))).convert('RGB'),dtype=np.float32)/255.
IDX=set(); NEW={}  # accessor id -> array
LOG={}
BRAID=[i for i,n in enumerate(JN) if n.startswith('Anika_Braid')]
def chain_pts(side):
    ids=[jid(f'Anika_Braid{side}_0{k}') for k in range(1,6)]; return JP[ids],ids
def seg_dist(p,pts):
    d=np.full(len(p),9.)
    for a,c in zip(pts[:-1],pts[1:]):
        ab=c-a; t=np.clip(((p-a)@ab)/(ab@ab),0,1); d=np.minimum(d,np.linalg.norm(p-(a+t[:,None]*ab),axis=1))
    return d
def renorm(Jw,Ww,allowed,fallback):
    m=np.isin(Jw,allowed); Ww=Ww*m; s=Ww.sum(1)
    z=s<1e-4; Ww[z]=0; Ww[z,0]=1; Jw[z,0]=fallback[z] if hasattr(fallback,'__len__') else fallback; s=Ww.sum(1)
    return Jw,(Ww/s[:,None]).astype(np.float32)
def weld(P):
    k=np.round(P[:,:3]/2e-4).astype(np.int64)
    if P.shape[1]>3: k=np.c_[k,P[:,3].astype(np.int64)]
    _,first,inv=np.unique(k,axis=0,return_index=True,return_inverse=True)
    return first[inv.ravel()]
def boundary(F,P=None):
    if P is not None: F=weld(P)[F]
    from collections import Counter
    e=np.concatenate([F[:,[0,1]],F[:,[1,2]],F[:,[2,0]]]); key=np.sort(e,1); c=Counter(map(tuple,key))
    return np.array([x for x,k in zip(e,map(tuple,key)) if c[k]==1])
def loops(E):
    # group directed boundary edges into connected components
    par={}
    def f(x):
        while par.get(x,x)!=x: x=par[x]
        return x
    for a,c in E: par.setdefault(a,a); par.setdefault(c,c); ra,rc=f(a),f(c); 
    for a,c in E:
        ra,rc=f(a),f(c)
        if ra!=rc: par[ra]=rc
    g={}
    for a,c in E: g.setdefault(f(a),[]).append((a,c))
    return list(g.values())
for mi,m in enumerate(j['meshes']):
    for p in m['primitives']:
        A={k:acc(j,b,v) for k,v in p['attributes'].items()}; F=acc(j,b,p['indices']).reshape(-1,3).astype(np.int64)
        P=A['POSITION']; UV=A['TEXCOORD_0']; n0=len(P)
        lg={'tris_in':len(F)}; A['_TAG']=np.zeros(len(P),np.float32)
        # 1) skate strip
        if 'COLOR_1' in A and os.environ.get('SKATE')=='c1':   # Akito: baked skate flagged sid 11-13 in COLOR_1.r*16 (not COLOR_0)
            sid=np.floor(A['COLOR_1'][:,0]*16+.5); sk_f=(sid[F]>=10.5).all(1)
        else: sk_f=(UV[F][:,:,0]>=.75).all(1)
        F=F[~sk_f]; lg['skate_tris_removed']=int(sk_f.sum())
        # 2) braid split (Anika)
        if BRAID and 'Anika' in m['name']:
            mat=j['materials'][p['material']]['name']; tag=mat.replace('AnikaAtlas_','anika_'); C=COL.get(tag+'_col')
            fc=F.mean(1); cuv=UV[F].mean(1); H_,W_=C.shape[:2]
            px=C[np.clip(((cuv[:,1])*H_).astype(int),0,H_-1),np.clip((cuv[:,0]*W_).astype(int),0,W_-1)]
            blonde=(px[:,2]<0.82*px[:,1])&(px[:,1]>0.55*px[:,0])   # ash-blonde hair texel (pink top / skin have B>=G)
            cen=P[F].mean(1); isb=np.zeros(len(F),bool); side=np.zeros(len(F),int)
            for si,sd in enumerate('LR'):
                pts,_=chain_pts(sd); tail=pts[-1]+(pts[-1]-pts[-2]); pts=np.vstack([pts,tail])
                d=seg_dist(cen,pts); hit=blonde&(d<.045)&(cen[:,1]<1.20); isb|=hit; side[hit]=si
            lg['braid_tris']=int(isb.sum())
            bv=np.unique(F[isb]); tv=np.unique(F[~isb]); shared=np.intersect1d(bv,tv)
            # duplicate shared verts for the braid faces
            remap=np.arange(len(P)); new=len(P)+np.arange(len(shared)); remap[shared]=new
            for k in A: A[k]=np.concatenate([A[k],A[k][shared]])
            A['_TAG'][len(P):]=1; Fb=F[isb].copy(); Fb=remap[Fb]; Ft=F[~isb]; P=A['POSITION']; UV=A['TEXCOORD_0']
            J_,W__=A['JOINTS_0'].astype(np.int64),A['WEIGHTS_0'].astype(np.float32)
            bset=np.unique(Fb); allowed=BRAID+[jid('mixamorig:Head')]
            # fallback = nearest braid bone by position
            bp=JP[BRAID]; nb=np.array(BRAID)[np.argmin(np.linalg.norm(P[bset][:,None]-bp[None],axis=2),1)]
            J_[bset],W__[bset]=renorm(J_[bset],W__[bset],allowed,nb)
            tset=np.unique(Ft); nbr=[jid('mixamorig:'+n) for n in ('Spine2','Neck','LeftShoulder','RightShoulder')]
            nt=np.array(nbr)[np.argmin(np.linalg.norm(P[tset][:,None]-JP[nbr][None],axis=2),1)]
            notb=[i for i in range(len(JN)) if i not in BRAID]; J_[tset],W__[tset]=renorm(J_[tset],W__[tset],notb,nt)
            lg['shared_split_verts']=int(len(shared)); lg['top_verts_braid_weight_stripped']=int((np.isin(acc(j,b,p['attributes']['JOINTS_0'])[tset[tset<n0]],BRAID)&(acc(j,b,p['attributes']['WEIGHTS_0'])[tset[tset<n0]]>0)).any(1).sum())
            A['JOINTS_0']=J_.astype(A['JOINTS_0'].dtype); A['WEIGHTS_0']=W__
            # fill the contact holes on both sides (fan from loop centroid), only loops that touch split verts
            sh=set(shared.tolist())|set(new.tolist()); fills=[]
            for FF,label in ((Ft,'top'),(Fb,'braid')):
                E=boundary(FF,np.c_[A['POSITION'],A['_TAG']]); E=E[[ (a in sh or c in sh) for a,c in E]] if len(E) else E
                for lp in loops(E):
                    vs=np.unique(np.array(lp).ravel()); c=len(A['POSITION'])
                    cen_=A['POSITION'][vs].mean(0); near=vs[np.argmin(np.linalg.norm(A['POSITION'][vs]-cen_,axis=1))]
                    for k in A: A[k]=np.concatenate([A[k],A[k][near:near+1]])
                    A['POSITION'][c]=cen_
                    ww=np.zeros(len(JN)); 
                    for v in vs:
                        for jj,wt in zip(A['JOINTS_0'][v],A['WEIGHTS_0'][v]): ww[jj]+=wt
                    top=np.argsort(-ww)[:4]; A['JOINTS_0'][c]=top; A['WEIGHTS_0'][c]=(ww[top]/ww[top].sum()).astype(np.float32)
                    for a_,c_ in lp: fills.append((c_,a_,c))
                lg[f'{label}_holes_filled']=len(loops(E)) if len(E) else 0
            F=np.vstack([Ft,Fb,np.array(fills,dtype=np.int64).reshape(-1,3)])
        # 3) hem caps: boundary loops low on the legs
        ank=min(JP[jid('mixamorig:LeftFoot')][1],JP[jid('mixamorig:RightFoot')][1])
        E=boundary(F,np.c_[A['POSITION'],A['_TAG']]); Pp=A['POSITION']; caps=[]; info=[]
        for lp in loops(E):
            vs=np.unique(np.array(lp).ravel())
            if Pp[vs][:,1].max()>ank+.17 or len(vs)<4: continue
            c=len(A['POSITION']); cen_=A['POSITION'][vs].mean(0); near=vs[0]
            for k in A: A[k]=np.concatenate([A[k],A[k][near:near+1]])
            A['POSITION'][c]=cen_; A['NORMAL'][c]=(0,-1,0)
            if '_WC' in A: A['_WC'][c]=0
            for a_,c_ in lp: caps.append((c_,a_,c))
            sd='Left' if cen_[0]>0 else 'Right'; pv=JP[jid('mixamorig:'+sd+'Foot')]
            info.append(dict(side=sd,verts=int(len(vs)),cap_y=round(float(cen_[1]),3),ring_bottom=round(float(Pp[vs][:,1].min()),3),ankle_pivot=[round(float(x),3) for x in pv],dxz=round(float(np.hypot(cen_[0]-pv[0],cen_[2]-pv[2])),3),above_pivot=round(float(cen_[1]-pv[1]),3)))
        if caps: F=np.vstack([F,np.array(caps,dtype=np.int64)])
        lg['hem_caps']=info
        # 4) right-arm fix (shorten forearm along the arm axis), same delta for the Hand chain joints below
        if ARMFIX:
            for sd,dl in ARMFIX.items():
                E_,Hj=JP[jid(f'mixamorig:{sd}ForeArm')],JP[jid(f'mixamorig:{sd}Hand')]; ax=(E_-Hj)/np.linalg.norm(E_-Hj); L=np.linalg.norm(E_-Hj)
                hand=[i for i,n in enumerate(JN) if n.startswith(f'mixamorig:{sd}Hand')]; fore=[jid(f'mixamorig:{sd}ForeArm'),jid(f'mixamorig:{sd}ForeArmTwist')]
                Jw,Ww=A['JOINTS_0'].astype(int),A['WEIGHTS_0']; wh=(Ww*np.isin(Jw,hand)).sum(1); wf=(Ww*np.isin(Jw,fore)).sum(1)
                s=np.clip(((E_-A['POSITION'])@ax)/L,0,1); A['POSITION']+= (ax*dl)[None]*(wh+wf*s)[:,None]
                lg[f'armfix_{sd}']=dict(delta=dl,verts_moved=int(((wh+wf*s)>1e-3).sum()))
        if BRAID and 'Anika' in m['name']:   # final purity pass (hole-fill centroids): braid-dominant -> braid+Head only, else no braid
            Jw,Ww=A['JOINTS_0'].astype(np.int64),A['WEIGHTS_0'].astype(np.float32); hd=jid('mixamorig:Head')
            bw=(Ww*np.isin(Jw,BRAID)).sum(1); mixd=(bw>0)&((Ww*~np.isin(Jw,BRAID+[hd])).sum(1)>1e-4)
            bd=mixd&(bw>=.5); td=mixd&(bw<.5)
            if bd.any(): Jw[bd],Ww[bd]=renorm(Jw[bd],Ww[bd],BRAID+[hd],hd)
            if td.any(): Jw[td],Ww[td]=renorm(Jw[td],Ww[td],[i for i in range(len(JN)) if i not in BRAID],jid('mixamorig:Neck'))
            A['JOINTS_0']=Jw.astype(A['JOINTS_0'].dtype); A['WEIGHTS_0']=Ww; lg['purity_fixed']=int(mixd.sum())
        # compact
        used=np.unique(F); rm=-np.ones(len(A['POSITION']),np.int64); rm[used]=np.arange(len(used)); F=rm[F]
        for k in A: A[k]=A[k][used]
        lg['tris_out']=len(F); lg['verts_out']=len(used); LOG[m['name']]=lg
        for k,v in p['attributes'].items():
            ac=j['accessors'][v]; dt=CT[ac['componentType']]
            NEW[v]=(np.round(np.clip(A[k],0,1)*np.iinfo(dt).max).astype(dt) if ac.get('normalized') and dt!=np.float32 else A[k].astype(dt))
        IDX.add(p['indices']); NEW[p['indices']]=F.ravel().astype(np.uint32 if len(used)>65535 or j['accessors'][p['indices']]['componentType']==5125 else np.uint16)
# per-rider Hand-chain joint shift (bind) -> IBM update; node translation of <sd>Hand
if ARMFIX:
    I2=IBM.copy()
    for sd,dl in ARMFIX.items():
        E_,Hj=JP[jid(f'mixamorig:{sd}ForeArm')],JP[jid(f'mixamorig:{sd}Hand')]; ax=(E_-Hj)/np.linalg.norm(E_-Hj); d=ax*dl
        for i,n in enumerate(JN):
            if n.startswith(f'mixamorig:{sd}Hand'):
                T=np.eye(4); T[:3,3]=-d; I2[i]=IBM[i]@T
        hn=j['nodes'][sk['joints'][jid(f'mixamorig:{sd}Hand')]]; Wd=worlds(j); par=[i for i,nn in enumerate(j['nodes']) if sk['joints'][jid(f'mixamorig:{sd}Hand')] in nn.get('children',[])][0]
        Rl=np.linalg.inv(Wd[par][:3,:3]); hn['translation']=list(np.array(hn.get('translation',[0,0,0]))+Rl@d)
        LOG[f'joint_{sd}Hand_shift']=[round(float(x),4) for x in d]
    NEW[sk['inverseBindMatrices']]=I2.transpose(0,2,1).reshape(-1,16).astype(np.float32)
# rebuild binary: keep referenced views, replace modified accessors
nb=bytearray(); views=[]
def put(data,target=None):
    while len(nb)%4: nb.append(0)
    o=len(nb); nb.extend(data); v={'buffer':0,'byteOffset':o,'byteLength':len(data)}
    if target: v['target']=target
    views.append(v); return len(views)-1
vmap={}
for ai,a in enumerate(j['accessors']):
    if ai in NEW:
        arr=NEW[ai]; a['count']=int(arr.shape[0]) if arr.ndim>1 else int(len(arr))
        if ai in IDX: a['componentType']=5125 if arr.dtype==np.uint32 else 5123
        tgt=j['bufferViews'][a['bufferView']].get('target'); a['bufferView']=put(np.ascontiguousarray(arr).tobytes(),tgt); a.pop('byteOffset',None)
        if 'min' in a and arr.ndim>1 and arr.dtype==np.float32: a['min']=[float(x) for x in arr.min(0)]; a['max']=[float(x) for x in arr.max(0)]
        elif 'min' in a and arr.ndim==1 and ai not in IDX: a['min']=[float(arr.min())]; a['max']=[float(arr.max())]
    elif 'bufferView' in a:
        ov=a['bufferView']
        if ov not in vmap:
            v=j['bufferViews'][ov]; o=v.get('byteOffset',0); vmap[ov]=put(bytes(b[o:o+v['byteLength']]),v.get('target'))
            if 'byteStride' in v: views[vmap[ov]]['byteStride']=v['byteStride']
        a['bufferView']=vmap[ov]
for im in j.get('images',[]):
    if 'bufferView' in im:
        ov=im['bufferView']
        if ov not in vmap:
            v=j['bufferViews'][ov]; o=v.get('byteOffset',0); vmap[ov]=put(bytes(b[o:o+v['byteLength']]))
        im['bufferView']=vmap[ov]
while len(nb)%4: nb.append(0)
j['bufferViews']=views; j['buffers']=[{'byteLength':len(nb)}]
js=json.dumps(j,separators=(',',':')).encode(); js+=b' '*((4-len(js)%4)%4)
open(dst,'wb').write(b'glTF'+struct.pack('<II',2,12+8+len(js)+8+len(nb))+struct.pack('<I',len(js))+b'JSON'+js+struct.pack('<I',len(nb))+b'BIN\x00'+bytes(nb))
print(json.dumps(LOG))
