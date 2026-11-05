import bpy,bmesh,sys
f=sys.argv[sys.argv.index('--')+1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=f)
for o in bpy.context.scene.objects:
  if o.type!='MESH': continue
  bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world)
  bnd=sum(1 for e in bm.edges if e.is_boundary); nm=sum(1 for e in bm.edges if not e.is_manifold and not e.is_boundary)
  # islands
  seen=set(); isl=0; sizes=[]
  for f0 in bm.faces:
    if f0.index in seen: continue
    isl+=1; st=[f0]; seen.add(f0.index); c=0
    while st:
      x=st.pop(); c+=1
      for e in x.edges:
        for g in e.link_faces:
          if g.index not in seen: seen.add(g.index); st.append(g)
    sizes.append(c)
  sizes.sort(reverse=True)
  # flipped: faces whose normal points toward bbox centre
  import mathutils
  cen=sum((v.co for v in bm.verts),mathutils.Vector())/max(1,len(bm.verts))
  inward=sum(1 for fa in bm.faces if fa.normal.dot(fa.calc_center_median()-cen)>0)
  # dup layer: verts within 1.5mm of another vertex not connected
  kd=mathutils.kdtree.KDTree(len(bm.verts))
  for v in bm.verts: kd.insert(v.co,v.index)
  kd.balance(); near=0
  for v in bm.verts:
    nb={e.other_vert(v).index for e in v.link_edges}
    for (co,i,dd) in kd.find_range(v.co,0.003):
      if i!=v.index and i not in nb: near+=1; break
  bb=[mathutils.Vector(c) for c in o.bound_box]
  print(f"OBJ {o.name} tris {sum(len(p.vertices)-2 for p in o.data.polygons)} verts {len(bm.verts)} boundaryE {bnd} nonmanifoldE {nm} islands {isl} top {sizes[:8]} inwardFaces {inward}/{len(bm.faces)} vertsNearUnlinked3mm {near} uvlayers {[u.name for u in o.data.uv_layers]}")
