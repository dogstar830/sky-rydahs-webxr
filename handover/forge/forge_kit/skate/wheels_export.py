import bpy,bmesh,math,numpy as np
from mathutils import Vector
G='/workspace/forge_kit/skate/'
V0=72/1024
def cell(k): return ((k+.5)/4, (V0*0.5))  # blender uv (v up); strip is v in [0,V0]
WH={'F':((0,-0.0895,-0.0425),0.0725),'R':((0,0.1715,-0.0485),0.0685)}
XC=0.006; WD=0.050
def lathe(bm,prof,N,uvk):
  # prof: list of (r,x,cellidx) ; revolve around X
  rings=[]
  for (r,x,_) in prof:
    rings.append([bm.verts.new((x,r*math.cos(2*math.pi*i/N),r*math.sin(2*math.pi*i/N))) for i in range(N)])
  for j in range(len(prof)-1):
    k=prof[j][2]
    for i in range(N):
      a,b,c,d=rings[j][i],rings[j][(i+1)%N],rings[j+1][(i+1)%N],rings[j+1][i]
      try: f=bm.faces.new((a,b,c,d)); f[uvk]=k
      except ValueError: pass
def build_wheel(r,N,spokes,name):
  bm=bmesh.new(); kl=bm.faces.layers.int.new('cell')
  w=WD/2
  prof=[(r-0.020,-w+0.004,2),(r-0.016,-w,0),(r-0.005,-w,0),(r,-w+0.008,0),(r,w-0.008,0),(r-0.005,w,0),(r-0.016,w,2),(r-0.020,w-0.004,1),(r-0.026,w-0.006,1),(r-0.026,-w+0.006,1),(r-0.020,-w+0.004,1)]
  if not spokes: prof=[(r-0.022,-w,2),(r,-w+0.008,0),(r,w-0.008,0),(r-0.022,w,2)]
  lathe(bm,prof,N,kl)
  if spokes:
    for s in range(spokes):
      a=2*math.pi*s/spokes
      for side in (-1,1):
        L=r-0.026-0.012; cx=side*(w-0.012)
        mid=0.012+L/2
        v=bmesh.ops.create_cube(bm,size=1)['verts']
        for vv in v:
          vv.co=Vector((vv.co.x*0.006+cx, vv.co.y*L, vv.co.z*0.008))
          vv.co.y+=mid
          y,z=vv.co.y,vv.co.z; vv.co.y=y*math.cos(a)-z*math.sin(a); vv.co.z=y*math.sin(a)+z*math.cos(a)
        for f in {f for vv in v for f in vv.link_faces}: f[kl]=1
    # hub caps + axle
    for side in (-1,1):
      res=bmesh.ops.create_cone(bm,cap_ends=True,segments=max(8,N//2),radius1=0.016,radius2=0.012,depth=0.012)
      for vv in res['verts']:
        x,y,z=vv.co; vv.co=Vector((z*side+side*(w-0.010),y,x))
      for f in {f for vv in res['verts'] for f in vv.link_faces}: f[kl]=1
    res=bmesh.ops.create_cone(bm,cap_ends=False,segments=max(8,N//2),radius1=0.007,radius2=0.007,depth=2*w-0.01)
    for vv in res['verts']: x,y,z=vv.co; vv.co=Vector((z,y,x))
    for f in {f for vv in res['verts'] for f in vv.link_faces}: f[kl]=0
  else:
    for side in (-1,1):
      res=bmesh.ops.create_circle(bm,cap_ends=True,segments=N,radius=r-0.022)
      for vv in res['verts']: x,y,z=vv.co; vv.co=Vector((side*w,x,y))
      for f in {f for vv in res['verts'] for f in vv.link_faces}: f[kl]=1
  bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
  for v in bm.verts: v.co.x+=XC
  me=bpy.data.meshes.new(name); bm.to_mesh(me); o=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(o)
  uv=me.uv_layers.new(name='UVMap'); cl=me.attributes['cell'].data
  for p in me.polygons:
    for li in p.loop_indices: uv.data[li].uv=cell(cl[p.index].value)
  for p in me.polygons: p.use_smooth=False
  return o
LOD={0:(32,5),1:(12,5),2:(8,0)}
def dump(o,local_off):
  me=o.data; me.calc_loop_triangles()
  try: me.calc_normals_split()
  except Exception: pass
  uvl=me.uv_layers[0].data; keys={}; P=[];Nn=[];U=[];I=[]
  for lt in me.loop_triangles:
    tri=[]
    for li,vi in zip(lt.loops,lt.vertices):
      co=me.vertices[vi].co; n=me.loops[li].normal if lt.use_smooth or True else lt.normal
      if not me.polygons[lt.polygon_index].use_smooth: n=lt.normal
      uv=uvl[li].uv
      k=(vi,round(uv[0],5),round(uv[1],5),round(n[0],3),round(n[1],3),round(n[2],3))
      if k not in keys:
        keys[k]=len(P); c=co-Vector(local_off); P.append((c.x,c.z,-c.y)); Nn.append((n[0],n[2],-n[1])); U.append((uv[0],1-uv[1]))
      tri.append(keys[k])
    I.append(tri)
  return dict(P=np.array(P,np.float32),N=np.array(Nn,np.float32),U=np.array(U,np.float32),I=np.array(I,np.uint32))
out={}
for i in range(3):
  sh=bpy.data.objects['shell%d'%i]
  for k,v in dump(sh,(0,0,0)).items(): out['shell%d_%s'%(i,k)]=v
  for wn,(c,r) in WH.items():
    o=build_wheel(r,*LOD[i],'Wheel_%s_L%d'%(wn,i))
    for k,v in dump(o,(0,0,0)).items(): out['wheel%s%d_%s'%(wn,i,k)]=v
    print('TRIS',i,wn,len(out['wheel%s%d_I'%(wn,i)]))
  print('TRIS shell',i,len(out['shell%d_I'%i]))
np.savez(G+'skate_v2_geo.npz',**out)
bpy.ops.wm.save_as_mainfile(filepath=G+'skate_v2_work2.blend')
