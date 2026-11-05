"""Hero-level face + hair kit shared by all riders (generalised from the Caali hero pass, code-e/src/build_rider.py).
hero_head(P): sculpted anime head, ears, nose, layered eyes (painted white/iris + sparkles), lashes, brows, mouth disc,
plus the 8 expression shape keys (EXPR). clump()/hair_cap(): clumped hair shells with the angel-ring UV mode.
P keys (all optional): jaw (taper, 0.42), chin (fwd, 0), width (x scale, 0.9), eye=dict(x,z,w,h,rot,iris,lash,flick,lower),
brow=dict(inner,mid,outer,thick), nose (1), mouth_w (1), lips (False), ear (1)."""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix
import rider_lib as RL
from rider_lib import finish, skin_obj, apply_all

EXPR = ['blink', 'smile', 'angry', 'surprised', 'sad', 'smirk', 'mouthOpen', 'focus']

def flat(name, pts, mat, loc, rot=(0,0,0), bone=None, th=0.008, plane='xz'):
    vs=[(a,0,b) if plane=='xz' else (a,b,0) for a,b in pts]
    me=bpy.data.meshes.new(name); me.from_pydata(vs,[],[list(range(len(vs)))]); o=bpy.data.objects.new(name,me)
    bpy.context.scene.collection.objects.link(o); bpy.context.view_layer.objects.active=o
    m=o.modifiers.new("s",'SOLIDIFY'); m.thickness=th; m.offset=0; apply_all(o)
    o.location=loc; o.rotation_euler=[math.radians(r) for r in rot]
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    return finish(o,mat,bone,False)

def stroke(a,b,w):
    a=Vector(a); b=Vector(b); d=(b-a).normalized(); n=Vector((-d.y,d.x))*w/2
    return [tuple(a+n),tuple(b+n),tuple(b-n),tuple(a-n)]

def pivot_rot(o, pivot, deg, axis='X'):
    pv=Vector(pivot); o.matrix_world = Matrix.Translation(pv) @ Matrix.Rotation(math.radians(deg),4,axis) @ Matrix.Translation(-pv) @ o.matrix_world
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active=o; bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)

def hero_head(P=None):
    P = P or {}; E = dict(x=0.037, z=1.655, w=1.15, h=0.56, rot=12, iris=0.92, lash=1.0, flick=1.0, lower=1.0); E.update(P.get('eye', {}))
    BR = dict(inner=1.684, mid=1.692, outer=1.69, thick=1.0); BR.update(P.get('brow', {}))
    jaw = P.get('jaw', 0.42); W = P.get('width', 0.9); FACE = []
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=22,radius=0.105,location=(0,0,1.66))
    hd=bpy.context.object; hd.name="head"
    G=lambda p,c,r: math.exp(-(p-c).length_squared/(r*r))
    ez=E['z']-1.66; ex=E['x']
    for vv in hd.data.vertices:
        p=vv.co; p.y*=1.05; p.x*=W
        if p.z<0:
            t=min(1,-p.z/0.105); p.x*=1-jaw*t*t; p.y*=1-0.15*t
            if p.y<0: p.y-=(0.015+P.get('chin',0))*t
            p.z*=1.12
        if p.y<-0.04:
            for s in (1,-1):
                p.y+=0.006*G(p,Vector((ex*s,-0.1,ez)),0.022)
                cb=G(p,Vector((0.06*s,-0.08,-0.032)),0.024); p.x+=s*0.004*cb*P.get('cheek',1); p.y-=0.002*cb
                p.y-=0.003*P.get('browridge',1)*G(p,Vector((0.036*s,-0.1,0.028)),0.018)
            nw=math.exp(-(p.x/0.0105)**2)*math.exp(-((p.z+0.024)/0.022)**2)
            p.y-=0.011*P.get('nose',1)*nw*max(0,min(1,(-p.z)/0.03+0.4))
            p.y+=0.0025*math.exp(-(p.x/0.022)**2)*math.exp(-((p.z+0.064)/0.0035)**2)
            p.y-=(0.0018+0.0012*P.get('lips',0))*math.exp(-(p.x/0.016)**2)*math.exp(-((p.z+0.071)/0.004)**2)
            p.y+=0.0012*math.exp(-(p.x/0.004)**2)*math.exp(-((p.z+0.052)/0.006)**2)
    finish(hd,'skin','head'); FACE.append((hd,'head',E['z']))
    for s in (1,-1):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=6,radius=0.025*P.get('ear',1),location=(0.092*s*W/0.9,0.01,1.65)); e=bpy.context.object
        e.scale=(0.4,0.8,1.1); bpy.ops.object.transform_apply(scale=True); finish(e,'skin','head')
    ns=P.get('nose',1)
    bpy.ops.mesh.primitive_cone_add(vertices=4,radius1=0.007*ns,radius2=0.0,depth=0.02*ns,location=(0,-0.112,1.63),rotation=(math.radians(-70),0,math.radians(45)))
    e=bpy.context.object; e.scale=(1,0.7,1); bpy.ops.object.transform_apply(scale=True); finish(e,'skin','head',True)
    zc=E['z']; L=E['lash']
    for s in (1,-1):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=14,ring_count=8,radius=0.025,location=(ex*s,-0.097,zc)); e=bpy.context.object
        e.scale=(E['w'],0.35,E['h']); e.rotation_euler=(0,0,math.radians(E['rot']*s)); bpy.ops.object.transform_apply(scale=True,rotation=True)
        finish(e,'eyes','head'); RL.PARTS[-1]['uv']='planar'; FACE.append((e,'eye',zc))
        ir=E['iris']
        bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=0.0145*ir,depth=0.0015,location=((ex-0.002)*s,-0.1062,zc-0.0005),rotation=(math.radians(90),0,0)); e=bpy.context.object
        e.scale=(0.95,1,min(1.0,E['h']/0.56)); bpy.ops.object.transform_apply(scale=True,rotation=True); finish(e,'iris','head'); RL.PARTS[-1]['uv']='planar'; FACE.append((e,'eye',zc))
        for (dx,dz,r) in ((-0.005,0.005,0.0036),(0.004,-0.005,0.0017)):
            bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=r*ir,depth=0.001,location=((ex-0.002)*s+dx*s,-0.1072,zc-0.0005+dz*E['h']/0.56),rotation=(math.radians(90),0,0))
            finish(bpy.context.object,'eyes','head',False); FACE.append((bpy.context.object,'eye',zc))
        hh=E['h']/0.56; dz=zc-1.655
        ul=skin_obj("upperLash",[(0.016*s,-0.1015,1.659+dz-0.004*(hh-1)),(0.03*s,-0.1052,1.6675+dz+0.008*(hh-1)),(0.047*s,-0.1025,1.668+dz+0.008*(hh-1)),(0.062*s,-0.0925,1.664+dz),(0.07*s,-0.088,1.664+dz+0.005*E['flick'])],
                    [(0,1),(1,2),(2,3),(3,4)],[(0.0022*L,)*2,(0.0034*L,)*2,(0.0036*L,)*2,(0.0028*L,)*2,(0.0012,0.0012)],0)
        finish(ul,'hair','head'); FACE.append((ul,'ulash',zc))
        lw=E['lower']
        ll=skin_obj("lowerLash",[(0.024*s,-0.1035,1.6425+dz),(0.042*s,-0.1015,1.643+dz),(0.056*s,-0.095,1.6465+dz)],[(0,1),(1,2)],[0.0009*lw,0.0012*lw,0.0008*lw],0)
        finish(ll,'hair','head'); FACE.append((ll,'llash',zc))
        T=BR['thick']
        br=skin_obj("brow",[(0.014*s,-0.1045,BR['inner']),(0.032*s,-0.1065,BR['mid']),(0.052*s,-0.101,BR['mid']+0.0035),(0.07*s,-0.089,BR['outer'])],[(0,1),(1,2),(2,3)],
                    [(0.0042*T,)*2,(0.0045*T,)*2,(0.0034*T,)*2,(0.0016*T,)*2],0)
        finish(br,'hair','head'); FACE.append((br,'brow',zc))
    n=18; MZ=1.596; mw=0.022*P.get('mouth_w',1)
    vs=[(0,-0.1085,MZ)]+[(mw*math.cos(2*math.pi*i/n),-0.1085+0.014*(math.cos(2*math.pi*i/n))**2,MZ+0.0014*math.sin(2*math.pi*i/n)) for i in range(n)]
    me=bpy.data.meshes.new("mouth"); me.from_pydata(vs,[],[(0,1+i,1+(i+1)%n) for i in range(n)]); mo=bpy.data.objects.new("mouth",me)
    bpy.context.scene.collection.objects.link(mo); finish(mo,'hair','head',False); FACE.append((mo,'mouth',zc))
    return FACE

def add_keys(o, kind, c=1.655, MZ=1.596):
    mw=o.matrix_world; inv=mw.inverted()
    if not o.data.shape_keys: o.shape_key_add(name="Basis", from_mix=False)
    lid=c-0.004
    for name in EXPR:
        k=o.shape_key_add(name=name, from_mix=False)
        for i,v in enumerate(o.data.vertices):
            w=mw@v.co; x,y,z=w.x,w.y,w.z; s=1 if x>=0 else -1; ax=abs(x)
            if kind=='eye':
                if name=='blink': z=lid+(z-lid)*0.06
                elif name=='smile': z=c-(c-z)*0.35 if z<c else c+(z-c)*0.85
                elif name=='angry': z=c+(z-c)*0.6 if z>c else z
                elif name=='surprised': x=x*1.0+(0.0)*s; z=c+(z-c)*1.18
                elif name=='sad': z=c+(z-c)*0.8 if z>c else z
                elif name=='smirk' and s<0: z=c-(c-z)*0.6 if z<c else z
                elif name=='focus': z=c+(z-c)*0.6 if z>c else c-(c-z)*0.75
            elif kind=='ulash':
                if name=='blink': z-=(z-(lid-0.002))*0.88
                elif name=='smile': z-=0.0015
                elif name in('angry','focus'): z-=(z-c)*0.4
                elif name=='surprised': z+=0.004
                elif name=='sad': z-=(z-c)*0.2
            elif kind=='llash':
                if name=='blink': z+=(lid-z)*0.6
                elif name=='smile': z+=0.006
                elif name=='focus': z+=0.0025
                elif name=='smirk' and s<0: z+=0.003
            elif kind=='brow':
                t=max(0,1-ax/0.072)
                if name=='blink': z-=0.002
                elif name=='smile': z+=0.003
                elif name=='angry': z-=0.009*t; x-=0.003*s*t
                elif name=='surprised': z+=0.009
                elif name=='sad': z+=0.008*t-0.002
                elif name=='smirk' and s>0: z+=0.005
                elif name=='focus': z-=0.004*t+0.001
            elif kind=='mouth':
                q=(x/0.022)**2
                if name=='smile': z+=0.0065*q-0.001; x*=1.1
                elif name=='angry': z-=0.004*q; x*=0.85
                elif name=='surprised': x*=0.5; z=MZ-0.002+(z-MZ)*7
                elif name=='sad': z-=0.005*q
                elif name=='smirk' and x<0: z+=0.007*q
                elif name=='mouthOpen': x*=0.82; z=MZ-0.004+(z-MZ)*9
                elif name=='focus': x*=0.88
            elif kind=='head':
                jaw=max(0,min(1,(1.604-z)/0.02)) if y<-0.02 else 0
                if name=='surprised': z-=0.004*jaw
                elif name=='mouthOpen': z-=0.008*jaw
                elif name=='smile':
                    cb=math.exp(-((ax-0.052)**2+(z-1.622)**2)/0.0004) if y<-0.06 else 0; z+=0.003*cb
            k.data[i].co=inv@Vector((x,y,z))

def add_expressions(FACE):
    for o,kind,c in FACE: add_keys(o,kind,c)

HC=Vector((0,0.015,1.675))
def clump(sdir, gdir, L, W, T=0.011, bend=Vector((0,0,-0.25)), segs=5, root_r=(0.095,0.105,0.1), mat='hair', bone='head'):
    sdir=sdir.normalized(); gdir=gdir.normalized(); root=HC+Vector((sdir.x*root_r[0],sdir.y*root_r[1],sdir.z*root_r[2]))
    pts=[root+gdir*L*t+bend*L*t*t for t in [i/segs for i in range(segs+1)]]
    verts=[]; faces=[]
    for i,p in enumerate(pts[:-1]):
        T_=(pts[i+1]-p).normalized(); rad=(p-HC).normalized()
        if abs(T_.dot(rad))>0.98: rad=Vector((0,1,0))
        Wd=T_.cross(rad).normalized(); Nd=Wd.cross(T_).normalized()
        f=(1-i/segs)**0.7; w=W*f; t=T*f
        verts+=[tuple(p+Wd*w),tuple(p+Nd*t),tuple(p-Wd*w),tuple(p-Nd*t*0.4)]
    verts.append(tuple(pts[-1])); tip=len(verts)-1
    for i in range(segs-1):
        a=4*i; b=4*(i+1)
        for j in range(4): faces.append((a+j,a+(j+1)%4,b+(j+1)%4,b+j))
    a=4*(segs-1)
    for j in range(4): faces.append((a+j,a+(j+1)%4,tip))
    me=bpy.data.meshes.new("clump"); me.from_pydata(verts,[],faces); o=bpy.data.objects.new("clump",me); bpy.context.scene.collection.objects.link(o)
    me.validate(); me.update(); finish(o,mat,bone,True); RL.PARTS[-1]['uv']='hair'; return o

def hair_cap(front_z=0.03, r=0.113):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=18,ring_count=11,radius=r,location=(0,0.014,1.677))
    cap=bpy.context.object; bm=bmesh.new(); bm.from_mesh(cap.data)
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if (v.co.y<-0.02 and v.co.z<front_z) or v.co.z<-0.075 or (v.co.y<0.03 and v.co.z<-0.01)],context='VERTS')
    bm.to_mesh(cap.data); bm.free(); cap.scale=(0.97,1.05,1); bpy.ops.object.transform_apply(scale=True); finish(cap,'hair','head'); RL.PARTS[-1]['uv']='hair'

def bangs(spec, W=0.032, T=0.011):
    """spec: list of (x, length, yaw)"""
    for x,L,yaw in spec: clump(Vector((x*5,-0.75,0.65)),Vector((yaw,-0.55,-0.85)),L,W,T,bend=Vector((0,-0.08,-0.2)))
