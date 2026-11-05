import bpy,bmesh
o=bpy.data.objects['shell0']; bm=bmesh.new(); bm.from_mesh(o.data)
seen=set(); sizes=[]
for f0 in bm.faces:
  if f0.index in seen: continue
  st=[f0]; seen.add(f0.index); c=0
  while st:
    x=st.pop(); c+=1
    for e in x.edges:
      for g in e.link_faces:
        if g.index not in seen: seen.add(g.index); st.append(g)
  sizes.append(c)
sizes.sort(reverse=True); print('ISL',len(sizes),sizes[:5],sum(1 for s in sizes if s<20),'bnd',sum(1 for e in bm.edges if e.is_boundary),'nonman',sum(1 for e in bm.edges if not e.is_manifold))
