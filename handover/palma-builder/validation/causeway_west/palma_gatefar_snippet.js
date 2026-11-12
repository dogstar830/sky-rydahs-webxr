  // 14. far gate decor (gates.js moving-part meshes Gate_toon_*/Gate_glow_* + lightbox CrewPatch_* under garage groups; Palma Nov 12, causeway_west budget):
  // beyond GF.R m (fog 70..360, ~90% fogged) moved to layer 29 so the camera skips them; gates.js keeps full control of .visible. ?gatefar=0 disables.
  const GF={list:[],R:250,H:15}; function packGateFar(){ if(/[?&]gatefar=0\b/.test(location.search)||typeof garages==='undefined') return;
    for(const G of garages){ if(!G.group) continue; G.group.traverse(o=>{ if((o.isMesh)&&/^(Gate_(toon|glow)_|CrewPatch_)/.test(o.name||'')){ if(!o.geometry.boundingSphere) o.geometry.computeBoundingSphere(); GF.list.push({o,far:false,mask:o.layers.mask}); } }); }
    st.gateFar=GF.list.length; }
  const _gfp=new THREE.Vector3(); function gateFarTick(cp){ for(const g of GF.list){ g.o.getWorldPosition(_gfp); const d=_gfp.distanceTo(cp); const f=g.far?d>GF.R-GF.H:d>GF.R;
    if(f!==g.far){ g.far=f; if(f){ g.mask=g.o.layers.mask; g.o.layers.set(29); } else g.o.layers.mask=g.mask; } } }
