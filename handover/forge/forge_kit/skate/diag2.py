import bpy,bmesh,sys,mathutils
f=sys.argv[sys.argv.index('--')+1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=f)
for o in bpy.context.scene.objects:
  if o.type!='MESH' or not o.name.endswith('L0') and 'mesh0' not in o.name: continue
  for d in (1e-6,0.0005,0.001,0.002,0.004):
    bm=bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=d/max(o.matrix_world.to_scale()))
    bnd=sum(1 for e in bm.edges if e.is_boundary); nm=sum(1 for e in bm.edges if not e.is_manifold and not e.is_boundary)
    seen=set(); isl=0
    for f0 in bm.faces:
      if f0.index in seen: continue
      isl+=1; st=[f0]; seen.add(f0.index)
      while st:
        x=st.pop()
        for e in x.edges:
          for g in e.link_faces:
            if g.index not in seen: seen.add(g.index); st.append(g)
    # inconsistent winding: manifold edges where both faces traverse edge same direction
    bad=0
    for e in bm.edges:
      if len(e.link_faces)==2:
        a,b=e.link_faces
        def dirn(fc):
          vs=list(fc.verts); i=vs.index(e.verts[0]); return vs[(i+1)%len(vs)]==e.verts[1]
        if dirn(a)==dirn(b): bad+=1
    print(f"OBJ {o.name} weld{d*1000:.1f}mm verts {len(bm.verts)} boundaryE {bnd} nonmanE {nm} islands {isl} windingFlipEdges {bad}")
    bm.free()
