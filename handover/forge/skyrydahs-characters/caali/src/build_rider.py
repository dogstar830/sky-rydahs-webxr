# Caali (crew Code : E) — HERO rider. Canon look = pack sheets 05 (full turnaround), 06 (head), 07 (gear detail).
# Shared pipeline: ../../shared/rider_lib.py  (painted atlas + baked normal map + 4 equal glowing wheels)
import sys; sys.path.insert(0, "/workspace/skyrydahs-characters/shared")
from rider_lib import *
import rider_lib as RL
CFG = {'name': 'code-e', 'out': '/workspace/skyrydahs-characters/code-e/', 'prefix': 'CodeE', 'glowpts': [],
       'painted': True, 'bake': True, 'wheels4': True}
init(CFG)
random.seed(7)
EXPR = ['blink', 'smile', 'angry', 'surprised', 'sad', 'smirk', 'mouthOpen', 'focus']
FACE = []   # (obj, kind)

def flat(name, pts, mat, loc, rot=(0,0,0), bone=None, th=0.008, plane='xz'):
    vs=[(a,0,b) if plane=='xz' else (a,b,0) for a,b in pts]
    me=bpy.data.meshes.new(name); me.from_pydata(vs,[],[list(range(len(vs)))]); o=bpy.data.objects.new(name,me)
    bpy.context.scene.collection.objects.link(o); bpy.context.view_layer.objects.active=o
    m=o.modifiers.new("s",'SOLIDIFY'); m.thickness=th; m.offset=0; apply_all(o)
    o.location=loc; o.rotation_euler=[math.radians(r) for r in rot]
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    return finish(o,mat,bone,False)
def stroke(a,b,w):
    a=Vector((a[0],a[1])); b=Vector((b[0],b[1])); d=(b-a).normalized(); n=Vector((-d.y,d.x))*w/2
    return [tuple(a+n),tuple(b+n),tuple(b-n),tuple(a-n)]
def sigil(cx, cy, cz, sc, facing, bone):
    """sheet 05 white dripping graffiti sigil (crossed strokes + crossbar + chevron + drips)"""
    S=[((-0.08,-0.08),(0.06,0.09),0.024),((0.08,-0.08),(-0.06,0.09),0.024),((-0.075,0.0),(0.075,0.005),0.016),
       ((-0.055,0.07),(0.0,0.115),0.016),((0.0,0.115),(0.055,0.07),0.016),
       ((-0.08,-0.08),(-0.082,-0.13),0.008),((0.08,-0.08),(0.079,-0.115),0.008),((0.02,0.0),(0.021,-0.06),0.007),((-0.04,0.0),(-0.04,-0.045),0.006)]
    for a,b,w in S:
        pts=stroke((a[0]*sc,a[1]*sc),(b[0]*sc,b[1]*sc),w*sc)
        if facing<0: pts=[(-x,z) for x,z in pts][::-1]
        flat("sigil",pts,'eyes',(cx,cy,cz),(0,0,0),bone,0.004)

module('body')
# legs / pelvis (baggy cargo pants, sheet 05 dark purple-grey)
for side in (1,-1):
    v=[(0.0,0,1.00),(0.10*side,0,0.97),(0.115*side,-0.01,0.78),(0.12*side,-0.02,0.58),(0.118*side,0,0.46),(0.112*side,0.0,0.39)]
    r=[(0.15,0.11),(0.10,0.10),(0.098,0.093),(0.08,0.078),(0.088,0.083),(0.078,0.078)]
    finish(skin_obj("pants",v,[(i,i+1) for i in range(len(v)-1)],r),'cloth')
# black tee under the open jacket (sheet 05)
finish(skin_obj("shirt",[(0,0,0.98),(0,0,1.15),(0,0,1.32),(0,0,1.45)],[(0,1),(1,2),(2,3)],[(0.13,0.09),(0.12,0.085),(0.15,0.095),(0.10,0.08)]),'jacket')

module('top')
# cropped black bomber, open front, purple sleeves (sheet 05 front/3-4), silver zips (06)
jv=[(0,0.005,1.02),(0,0.005,1.18),(0,0.005,1.34),(0,0.005,1.44),
    (0.2,0.005,1.42),(0.31,0.005,1.31),(0.42,0.005,1.20),(0.53,0.005,1.09),
    (-0.2,0.005,1.42),(-0.31,0.005,1.31),(-0.42,0.005,1.20),(-0.53,0.005,1.09)]
je=[(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(3,8),(8,9),(9,10),(10,11)]
jr=[(0.155,0.115),(0.145,0.105),(0.175,0.115),(0.12,0.09),(0.075,0.075),(0.07,0.07),(0.06,0.06),(0.062,0.062),
    (0.075,0.075),(0.07,0.07),(0.06,0.06),(0.062,0.062)]
jk=skin_obj("jacket",jv,je,jr)
bm=bmesh.new(); bm.from_mesh(jk.data)
bmesh.ops.delete(bm,geom=[f for f in bm.faces if (lambda c: c.y<-0.06 and abs(c.x)<0.045 and 1.0<c.z<1.47)(f.calc_center_median())],context='FACES')
bm.to_mesh(jk.data); bm.free()
sol=jk.modifiers.new("sol",'SOLIDIFY'); sol.thickness=0.012; apply_all(jk)
sl=dup(jk,"sleeves")
for o,keep in ((jk,lambda c: abs(c.x)<0.235),(sl,lambda c: abs(c.x)>=0.235)):
    bm=bmesh.new(); bm.from_mesh(o.data); bmesh.ops.delete(bm,geom=[f for f in bm.faces if not keep(f.calc_center_median())],context='FACES'); bm.to_mesh(o.data); bm.free()
finish(jk,'jacket'); finish(sl,'gold')
for k in range(3): ring("rib",(0,0.005,0.985+k*0.016),0.158,0.012,mat='gold',sc=(1,0.76,1))        # purple rib hem (05 back)
for s in (1,-1):
    ring("cuff",(0.555*s,0.005,1.065),0.064,0.04,rot=(0,math.radians(-45*s),0),mat='jacket')          # black rib cuffs
    ring("cuffStripe",(0.545*s,0.005,1.075),0.066,0.008,rot=(0,math.radians(-45*s),0),mat='gold')
# popped standing collar
bpy.ops.mesh.primitive_cone_add(vertices=16,radius1=0.085,radius2=0.12,depth=0.11,location=(0,0.01,1.50))
c=bpy.context.object; c.scale=(1,0.85,1); bpy.ops.object.transform_apply(scale=True)
bm=bmesh.new(); bm.from_mesh(c.data)
bmesh.ops.delete(bm,geom=[f for f in bm.faces if abs(f.normal.z)>0.9 or (f.calc_center_median().y<-0.07 and abs(f.calc_center_median().x)<0.03)],context='FACES')
bm.to_mesh(c.data); bm.free(); m=c.modifiers.new("s",'SOLIDIFY'); m.thickness=0.01; apply_all(c); finish(c,'jacket')
for s in (1,-1):
    cube((0.05*s,-0.116,1.24),(0.008,0.006,0.38),'metal',0)            # silver zipper tape (06)
    cube((0.105*s,-0.112,1.08),(0.075,0.02,0.07),'jacket',0.006)       # lower welt pocket
    cube((0.105*s,-0.124,1.11),(0.08,0.008,0.012),'gold',0.002)        # purple welt trim (05)
# left upper-arm zip pocket (05 3/4 + side)
cube((0.30,-0.045,1.33),(0.06,0.02,0.08),'jacket',0.006,None,(0,math.radians(-45),math.radians(-10)))
cube((0.302,-0.058,1.355),(0.05,0.006,0.008),'metal',0,None,(0,math.radians(-45),math.radians(-10)))

module('body')
finish(skin_obj("neck",[(0,0.01,1.42),(0,0.01,1.56)],[(0,1)],[0.045,0.042]),'skin','head')
for s in (1,-1):   # hands + black fingerless gloves with purple wrist strap (05)
    w=Vector((0.60*s,0,1.02)); d=Vector((0.70*s,0,0.92))-w
    finish(skin_obj("hand",[tuple(w),tuple(w+d*0.5),tuple(w+d)],[(0,1),(1,2)],[(0.032,0.022),(0.042,0.022),(0.03,0.02)]),'skin')
    finish(skin_obj("thumb",[tuple(w+d*0.2+Vector((0,-0.03,0))),tuple(w+d*0.55+Vector((0,-0.045,0)))],[(0,1)],[0.014,0.012]),'skin')
    ring("glove",tuple(w+d*0.3),0.046,0.075,rot=(0,math.radians(-45*s),0),mat='jacket')
    ring("gloveStrap",tuple(w+d*0.12),0.05,0.016,rot=(0,math.radians(-45*s),0),mat='gold')

# ================= HEAD: sculpted anime head =================
bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=22,radius=0.105,location=(0,0,1.66))
hd=bpy.context.object; hd.name="head"
G=lambda p,c,r: math.exp(-(p-c).length_squared/(r*r))
for vv in hd.data.vertices:
    p=vv.co; p.y*=1.05; p.x*=0.9
    if p.z<0:
        t=min(1,-p.z/0.105); p.x*=1-0.42*t*t; p.y*=1-0.15*t
        if p.y<0: p.y-=0.015*t
        p.z*=1.12
    if p.y<-0.04:
        for s in (1,-1):
            p.y+=0.006*G(p,Vector((0.037*s,-0.1,-0.005)),0.022)                  # eye sockets
            cb=G(p,Vector((0.06*s,-0.08,-0.032)),0.024); p.x+=s*0.004*cb; p.y-=0.002*cb   # cheekbones
            p.y-=0.003*G(p,Vector((0.036*s,-0.1,0.028)),0.018)                   # brow ridge
        nw=math.exp(-(p.x/0.0105)**2)*math.exp(-((p.z+0.024)/0.022)**2)
        p.y-=0.011*nw*max(0,min(1,(-0.0-p.z)/0.03+0.4))                          # nose bridge -> tip
        p.y+=0.0025*math.exp(-(p.x/0.022)**2)*math.exp(-((p.z+0.064)/0.0035)**2)   # mouth groove
        p.y-=0.0018*math.exp(-(p.x/0.016)**2)*math.exp(-((p.z+0.071)/0.004)**2)    # lower lip
        p.y+=0.0012*math.exp(-(p.x/0.004)**2)*math.exp(-((p.z+0.052)/0.006)**2)    # philtrum
finish(hd,'skin','head'); FACE.append((hd,'head'))
for s in (1,-1):   # ears (visible under the side hair, sheet 06)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=6,radius=0.025,location=(0.092*s,0.01,1.65)); e=bpy.context.object
    e.scale=(0.4,0.8,1.1); bpy.ops.object.transform_apply(scale=True); finish(e,'skin','head')
# nose tip wedge (small, anime)
bpy.ops.mesh.primitive_cone_add(vertices=4,radius1=0.007,radius2=0.0,depth=0.02,location=(0,-0.112,1.63),rotation=(math.radians(-70),0,math.radians(45)))
e=bpy.context.object; e.scale=(1,0.7,1); bpy.ops.object.transform_apply(scale=True); finish(e,'skin','head',True)
# layered eyes: white (painted lid shadow) + iris (painted gradient/pupil/catchlights) + highlight sparkles + lashes + brows
for s in (1,-1):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=14,ring_count=8,radius=0.025,location=(0.037*s,-0.097,1.655)); e=bpy.context.object
    e.scale=(1.15,0.35,0.56); e.rotation_euler=(0,0,math.radians(12*s)); bpy.ops.object.transform_apply(scale=True,rotation=True)
    finish(e,'eyes','head'); RL.PARTS[-1]['uv']='planar'; FACE.append((e,'eye'))
    bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=0.0145,depth=0.0015,location=(0.035*s,-0.1062,1.6545),rotation=(math.radians(90),0,0)); e=bpy.context.object
    e.scale=(0.92,1,1.0); bpy.ops.object.transform_apply(scale=True,rotation=True); finish(e,'iris','head'); RL.PARTS[-1]['uv']='planar'; FACE.append((e,'eye'))
    for (dx,dz,r) in ((-0.005,0.006,0.0038),(0.004,-0.006,0.0018)):
        bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=r,depth=0.001,location=(0.035*s+dx*s,-0.1072,1.653+dz),rotation=(math.radians(90),0,0))
        finish(bpy.context.object,'eyes','head',False); FACE.append((bpy.context.object,'eye'))
    ul=skin_obj("upperLash",[(0.016*s,-0.1015,1.659),(0.03*s,-0.1052,1.6675),(0.047*s,-0.1025,1.668),(0.062*s,-0.0925,1.664),(0.07*s,-0.088,1.669)],
                [(0,1),(1,2),(2,3),(3,4)],[(0.0022,0.0022),(0.0034,0.0034),(0.0036,0.0036),(0.0028,0.0028),(0.0012,0.0012)],0)
    finish(ul,'hair','head'); FACE.append((ul,'ulash'))
    ll=skin_obj("lowerLash",[(0.024*s,-0.1035,1.6425),(0.042*s,-0.1015,1.643),(0.056*s,-0.095,1.6465)],[(0,1),(1,2)],[0.0009,0.0012,0.0008],0)
    finish(ll,'hair','head'); FACE.append((ll,'llash'))
    br=skin_obj("brow",[(0.014*s,-0.1045,1.684),(0.032*s,-0.1065,1.692),(0.052*s,-0.101,1.6955),(0.07*s,-0.089,1.69)],[(0,1),(1,2),(2,3)],
                [(0.0042,0.0042),(0.0045,0.0045),(0.0034,0.0034),(0.0016,0.0016)],0)
    finish(br,'hair','head'); FACE.append((br,'brow'))
# mouth: one dark ellipse disc, morphs from a line (neutral, 06) to open shapes
n=18; MZ=1.596
vs=[(0,-0.1085,MZ)]+[(0.022*math.cos(2*math.pi*i/n),-0.1085+0.014*(math.cos(2*math.pi*i/n))**2,MZ+0.0014*math.sin(2*math.pi*i/n)) for i in range(n)]
me=bpy.data.meshes.new("mouth"); me.from_pydata(vs,[],[(0,1+i,1+(i+1)%n) for i in range(n)]); mo=bpy.data.objects.new("mouth",me)
bpy.context.scene.collection.objects.link(mo); finish(mo,'hair','head',False); FACE.append((mo,'mouth'))

def add_keys(o, kind):
    mw=o.matrix_world; inv=mw.inverted()
    if not o.data.shape_keys: o.shape_key_add(name="Basis", from_mix=False)
    for name in EXPR:
        k=o.shape_key_add(name=name, from_mix=False)
        for i,v in enumerate(o.data.vertices):
            w=mw@v.co; x,y,z=w.x,w.y,w.z; s=1 if x>=0 else -1; ax=abs(x)
            if kind=='eye':
                c=1.655
                if name=='blink': z=1.651+(z-1.651)*0.06
                elif name=='smile': z=c-(c-z)*0.35 if z<c else c+(z-c)*0.85
                elif name=='angry': z=c+(z-c)*0.6 if z>c else z
                elif name=='surprised': x=0.036*s+(x-0.036*s)*1.12; z=c+(z-c)*1.18
                elif name=='sad': z=c+(z-c)*0.8 if z>c else z
                elif name=='smirk' and s<0: z=c-(c-z)*0.6 if z<c else z
                elif name=='focus': z=c+(z-c)*0.6 if z>c else c-(c-z)*0.75
            elif kind=='ulash':
                if name=='blink': z-= (z-1.649)*0.88
                elif name=='smile': z-=0.0015
                elif name in('angry','focus'): z-=(z-1.655)*0.4
                elif name=='surprised': z+=0.004
                elif name=='sad': z-=(z-1.655)*0.2
            elif kind=='llash':
                if name=='blink': z+=(1.651-z)*0.6
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
for o,kind in FACE: add_keys(o,kind)

module('accessory','goggles')
# goggles on forehead (sheet 05: dark-metal frame, purple lenses; strap all round)
bpy.ops.mesh.primitive_torus_add(major_radius=0.124,minor_radius=0.008,major_segments=28,minor_segments=4,location=(0,0.012,1.735),rotation=(math.radians(-12),0,0))
g=bpy.context.object; g.scale=(0.95,1.06,1.6); bpy.ops.object.transform_apply(scale=True); finish(g,'jacket','head')
for s in (1,-1):
    bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=0.031,depth=0.02,location=(0.047*s,-0.113,1.757),rotation=(math.radians(62),0,math.radians(-22*s)))
    finish(bpy.context.object,'metal','head')
    bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=0.025,depth=0.022,location=(0.047*s,-0.1155,1.758),rotation=(math.radians(62),0,math.radians(-22*s)))
    finish(bpy.context.object,'gold','head')
cube((0,-0.122,1.758),(0.02,0.01,0.012),'metal',0,'head')

module('hair')
# black spiky hair: clumped shells (diamond cross-section, tapered, curved), angel-ring UV (sheet 06)
HC=Vector((0,0.015,1.675))
def clump(sdir, gdir, L, W, T=0.011, bend=Vector((0,0,-0.25)), segs=5):
    sdir=sdir.normalized(); gdir=gdir.normalized(); root=HC+Vector((sdir.x*0.095,sdir.y*0.105,sdir.z*0.1))
    pts=[root+gdir*L*t+bend*L*t*t for t in [i/segs for i in range(segs+1)]]
    verts=[]; faces=[]
    for i,p in enumerate(pts[:-1]):
        T_=(pts[i+1]-p).normalized(); rad=(p-HC).normalized(); Wd=T_.cross(rad).normalized(); Nd=Wd.cross(T_).normalized()
        f=(1-i/segs)**0.7; w=W*f; t=T*f
        verts+= [tuple(p+Wd*w), tuple(p+Nd*t), tuple(p-Wd*w), tuple(p-Nd*t*0.4)]
    verts.append(tuple(pts[-1])); tip=len(verts)-1
    for i in range(segs-1):
        a=4*i; b=4*(i+1)
        for j in range(4): faces.append((a+j,a+(j+1)%4,b+(j+1)%4,b+j))
    a=4*(segs-1)
    for j in range(4): faces.append((a+j,a+(j+1)%4,tip))
    me=bpy.data.meshes.new("clump"); me.from_pydata(verts,[],faces); o=bpy.data.objects.new("clump",me); bpy.context.scene.collection.objects.link(o)
    me.validate(); me.update(); finish(o,'hair','head',True); RL.PARTS[-1]['uv']='hair'
bpy.ops.mesh.primitive_uv_sphere_add(segments=18,ring_count=11,radius=0.113,location=(0,0.014,1.677))
cap=bpy.context.object; bm=bmesh.new(); bm.from_mesh(cap.data)
bmesh.ops.delete(bm,geom=[v for v in bm.verts if (v.co.y<-0.02 and v.co.z<0.03) or v.co.z<-0.075 or (v.co.y<0.03 and v.co.z<-0.01)],context='VERTS')
bm.to_mesh(cap.data); bm.free(); cap.scale=(0.97,1.05,1); bpy.ops.object.transform_apply(scale=True); finish(cap,'hair','head'); RL.PARTS[-1]['uv']='hair'
rnd=random.Random(11)
for i in range(15):   # crown: big messy spikes up/out
    az=2*math.pi*i/15+rnd.uniform(-0.2,0.2); el=math.radians(rnd.uniform(45,75))
    d=Vector((math.cos(el)*math.sin(az),-math.cos(el)*math.cos(az)*0.8+0.15,math.sin(el)))
    clump(d,d+Vector((0,0.1,0.35)),rnd.uniform(0.11,0.16),rnd.uniform(0.045,0.06),0.018,bend=Vector((0,0.05,-0.15)))
for i in range(15):   # sides/back: flaring out + down, nape spikes
    az=math.radians(rnd.uniform(70,290)); el=math.radians(rnd.uniform(-15,35))
    d=Vector((math.sin(az)*math.cos(el),-math.cos(az)*math.cos(el),math.sin(el)))
    clump(d,d*0.9+Vector((0,0.1,-0.45)),rnd.uniform(0.09,0.14),rnd.uniform(0.042,0.055),0.016,bend=Vector((0,0,-0.2)))
for x,L,yaw in ((-0.035,0.085,-0.25),(-0.012,0.1,0.05),(0.012,0.09,-0.1),(0.036,0.082,0.25),(0.06,0.075,0.45),(-0.06,0.075,-0.45),(0.0,0.05,0.0),(0.08,0.07,0.6),(-0.08,0.07,-0.6)):
    d=Vector((x*5,-0.75,0.65))   # bangs over the forehead, centre lock between the brows (06)
    clump(d,Vector((yaw,-0.55,-0.85)),L,0.032,0.011,bend=Vector((0,-0.08,-0.2)))
for s in (1,-1):   # temple locks in front of the ears
    clump(Vector((0.85*s,-0.35,0.35)),Vector((0.25*s,-0.2,-1)),0.085,0.03,0.011,bend=Vector((0,0,-0.1)))

module('accessory','scarf')
# purple scarf wrap with long tattered tails trailing back over the right shoulder (sheet 05)
bpy.ops.mesh.primitive_torus_add(major_radius=0.09,minor_radius=0.032,major_segments=18,minor_segments=6,location=(0,0.005,1.49))
o=bpy.context.object; o.scale=(1,0.92,0.85); bpy.ops.object.transform_apply(scale=True); finish(o,'gold','chest')
flat("scarfDrape",[(-0.05,0),(0.05,0),(0.03,-0.08),(0.0,-0.12),(-0.035,-0.07)],'gold',(0.005,-0.112,1.47),(8,0,0),'chest',0.01)
for dx,dz,L,ry in ((-0.075,1.48,1.0,8),(-0.115,1.46,0.8,-6)):
    pts=[(-0.032,0),(0.032,0),(0.036,-0.2*L),(0.018,-0.29*L),(0.004,-0.24*L),(-0.014,-0.31*L),(-0.036,-0.21*L)]
    flat("scarfTail",pts,'gold',(dx,0.142,dz),(0,ry,0),'chest',0.01)

module('accessory','emblem')
sigil(0.0,0.133,1.27,1.0,1,'chest')          # back: big white dripping sigil (05 back view)
sigil(0.1,-0.128,1.355,0.32,-1,'chest')      # chest: small sigil on the left chest (05 front)

module('body')
ring("belt",(0,0,0.99),0.155,0.035,mat='jacket',sc=(1,0.75,1))     # black belt
cube((0,-0.118,0.99),(0.05,0.012,0.035),'metal',0.004)             # silver buckle (05)
for s in (1,-1):
    cube((0.178*s,-0.01,0.74),(0.035,0.11,0.12),'cloth',0.01)            # bellows cargo pocket (05 side)
    cube((0.181*s,-0.01,0.80),(0.045,0.12,0.03),'cloth',0.006)           # flap
    cube((0.2*s,-0.01,0.80),(0.006,0.02,0.012),'metal',0)                 # snap
    ring("cinch",(0.112*s,0,0.41),0.084,0.03,mat='cloth')                # pants bunching over the boot cuff
# hanging purple straps with silver buckles (05 front + side, 07)
flat("strapF",[(-0.012,0),(0.012,0),(0.012,-0.36),(-0.012,-0.36)],'gold',(0.055,-0.122,0.97),(0,-6,0),None,0.004)
cube((0.07,-0.126,0.78),(0.03,0.006,0.02),'metal',0.002)
flat("strapF2",[(-0.012,0),(0.012,0),(0.012,-0.24),(-0.012,-0.24)],'gold',(-0.085,-0.12,0.97),(0,5,0),None,0.004)
flat("strapS",[(-0.012,0),(0.012,0),(0.012,-0.32),(-0.012,-0.32)],'gold',(-0.222,-0.02,0.94),(0,0,90),None,0.004)
cube((-0.224,-0.02,0.72),(0.006,0.03,0.02),'metal',0.002)

build_skates()
build_inventory()
finalize()
