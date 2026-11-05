// ===== WORLD_PERF (world_perf.js, patch_world_perf.py): runtime draw-call pass over the finished world, no edits to other modules.
// Runs once after the static batcher (staticMerge) has finished. Touches render meshes only: colliders, grind splines (GRIND.S),
// wallride panels, rails, graffiti spots / TURF, gates and crew-base logic are data, never read or written here.
//  1. crew-base interiors (dressBase: 2 baked meshes per base, ~33k tris total) -> visible only within 45 m of that base
//  2. asphalt street planes (asphalt.js, one mesh per district) -> merged per shared material
//  3. static-batcher output (90 m tiles x material) -> re-merged into 270 m tiles x material (ink hulls stay on their DETM cull)
//  5. water streaks merged; 6. ink hull tiles drawn within 60 m (40 m quest); 7. details.js chunks packed per kind; ?tier=quest: far=fog+20, tiles beyond fog hidden
//  4. static canvas sign planes (FARCULL list) -> shared atlas pages, one mesh per page/state; originals swap back in within 28 m
// window.WORLD_PERF.stats holds before/after counts; ?noperf disables the pass.
const WORLD_PERF=(()=>{ const TILE=1e5; /* one merge tile city-wide (was 810): at the causeway every tile of a material was in view, so per-tile meshes only added draws; a merged mesh is 1 draw when any part is visible, so no view can rise */ const S={}; const st={}; const near=[]; const _cp=new THREE.Vector3();
  const names=g=>Object.keys(g.attributes).filter(k=>['position','normal','uv','color'].includes(k)).sort().join(',');
  function mergeList(L,mat){ // L: meshes (any transform, indexed or not) with identical attribute sets -> one world-space mesh
    const keys=names(L[0].geometry).split(','), A={}, size={}; keys.forEach(k=>{A[k]=[];size[k]=L[0].geometry.attributes[k].itemSize;});
    const v=new THREE.Vector3(), nm=new THREE.Matrix3();
    for(const o of L){ o.updateMatrixWorld(true); const g=o.geometry.index?o.geometry.toNonIndexed():o.geometry; nm.getNormalMatrix(o.matrixWorld);
      for(const k of keys){ const a=g.attributes[k], out=A[k];
        for(let i=0;i<a.count;i++){ if(k==='position'){ v.fromBufferAttribute(a,i).applyMatrix4(o.matrixWorld); out.push(v.x,v.y,v.z); }
          else if(k==='normal'){ v.fromBufferAttribute(a,i).applyMatrix3(nm).normalize(); out.push(v.x,v.y,v.z); }
          else for(let c=0;c<size[k];c++) out.push(a.array[i*size[k]+c]); } } }
    const geo=new THREE.BufferGeometry(); for(const k of keys) geo.setAttribute(k,new THREE.Float32BufferAttribute(A[k],size[k])); geo.computeBoundingSphere();
    const m=new THREE.Mesh(geo,mat); m.renderOrder=L[0].renderOrder; m.matrixAutoUpdate=false; m.userData.worldPerf=true; scene.add(m);
    for(const o of L) o.visible=false; return m; }

  // 4. sign atlas: static canvas-textured sign planes (the batcher's FARCULL list: signs, posters, billboards) are packed into
  // shared 2048 atlas pages (shelf packer, <=512 px wide cells) and drawn as ONE mesh per page+material state. LOD: within
  // NEAR m the original full-res sign is shown and its atlas quad is collapsed, so close-up quality is unchanged.
  const SIGN={ list:[], pages:[], NEAR:28, CAP:6, swaps:new Map(), made:0, freed:0, old:/[?&]oldsigns=1\b/.test(location.search) };
  function atlasSigns(){ if(typeof FARCULL==='undefined') return; const cands=[];
    for(const f of FARCULL){ const o=f.o, m=o.material, t=m&&m.map, g=o.geometry; if(!o.isMesh||!t||!t.image||!(t.image instanceof HTMLCanvasElement)||!m.isMeshBasicMaterial) continue;
      if(g.attributes.position.count!==4||!g.attributes.uv||t.repeat.x!==1||t.repeat.y!==1||t.offset.x!==0||t.offset.y!==0||m.vertexColors||m.opacity!==1||m.blending!==THREE.NormalBlending) continue;
      if(typeof tagTexs!=='undefined'&&tagTexs.includes(t)) continue;
      cands.push({f,o,m,t,ver:t.version,col:m.color.getHex()}); }
    // shelf pack, per state key
    const PW=2048, OLD=SIGN.old, MAXP=3;
    cands.sort((a,b)=>b.t.image.height/b.t.image.width-a.t.image.height/a.t.image.width);
    // memory cut: pick the largest cell width whose layout fits the budget (PW x PW + PW x 512, i.e. ~26.6 MB with mips; quest
    // the same). Dry-run shelf layout -> [pages, last page used height]. Falls back to the smallest width tried.
    const wpLay=(cw)=>{ let n=1,x=0,y=0,row=0; for(const it of cands){ const im=it.t.image, sc=Math.min(1,cw/im.width), w=Math.ceil(im.width*sc)+4, h=Math.ceil(im.height*sc)+4;
      if(x+w>PW){ x=0; y+=row; row=0; } if(y+h>PW){ n++; x=0; y=0; row=0; } x+=w; row=Math.max(row,h); } return [n,y+row]; };
    let CW=512; if(!OLD){ for(const cw of [384,320,288,256,224,192]){ CW=cw; const [n,u]=wpLay(cw); if(n<2||(n===2&&u<=512)) break; } SIGN.cw=CW; }
    let page=null; const newPage=()=>{ const c=document.createElement('canvas'); c.width=c.height=PW; const p={c,x:0,y:0,row:0,items:[],H:PW}; SIGN.pages.push(p); return p; };
    cands.sort((a,b)=>b.t.image.height/b.t.image.width-a.t.image.height/a.t.image.width);
    for(const it of cands){ const im=it.t.image, sc=Math.min(1,CW/im.width), w=Math.ceil(im.width*sc)+4, h=Math.ceil(im.height*sc)+4;
      if(!page) page=newPage(); if(page.x+w>PW){ page.x=0; page.y+=page.row; page.row=0; } if(page.y+h>PW){ if(SIGN.pages.length>=MAXP) break; page=newPage(); }
      page.c.getContext('2d').drawImage(im,page.x+2,page.y+2,w-4,h-4); it.rect=[page.x+2,page.y+2,w-4,h-4]; it.page=page; page.items.push(it); page.x+=w; page.row=Math.max(page.row,h); }
    if(!OLD) for(const p of SIGN.pages){ const used=p.y+p.row; let H=256; while(H<used) H*=2; if(H<PW){ const c=document.createElement('canvas'); c.width=PW; c.height=H; c.getContext('2d').drawImage(p.c,0,0); p.c.width=p.c.height=1; p.c=c; p.H=H; } }
    for(const p of SIGN.pages){ const tex=new THREE.CanvasTexture(p.c); tex.generateMipmaps=true; tex.minFilter=THREE.LinearMipmapLinearFilter; tex.anisotropy=4; p.tex=tex; const by=new Map();
      for(const it of p.items){ const m=it.m; const k=[m.side,m.transparent,m.depthWrite,m.depthTest,m.fog,m.alphaTest,it.col,it.o.renderOrder].join('|'); (by.get(k)||by.set(k,[]).get(k)).push(it); }
      for(const L of by.values()){ const m0=L[0].m, mat=new THREE.MeshBasicMaterial({map:tex,color:m0.color.clone(),transparent:m0.transparent,side:m0.side,depthWrite:m0.depthWrite,depthTest:m0.depthTest,fog:m0.fog,alphaTest:m0.alphaTest});
        const P=new Float32Array(L.length*18), U=new Float32Array(L.length*12), v=new THREE.Vector3();
        L.forEach((it,j)=>{ it.o.updateMatrixWorld(true); const g=it.o.geometry, pa=g.attributes.position, ua=g.attributes.uv, idx=g.index?Array.from(g.index.array):[0,1,2,0,2,3];
          const [rx,ry,rw,rh]=it.rect; idx.forEach((vi,q)=>{ v.fromBufferAttribute(pa,vi).applyMatrix4(it.o.matrixWorld); P.set([v.x,v.y,v.z],j*18+q*3);
            const u=ua.getX(vi), w=ua.getY(vi); U.set([(rx+.5+u*(rw-1))/PW, 1-(ry+.5+(1-w)*(rh-1))/p.H],j*12+q*2); }); it.base=P.slice(j*18,j*18+18); it.j=j; });
        const geo=new THREE.BufferGeometry(); geo.setAttribute('position',new THREE.BufferAttribute(P,3)); geo.setAttribute('uv',new THREE.BufferAttribute(U,2)); geo.computeBoundingSphere();
        const mesh=new THREE.Mesh(geo,mat); mesh.renderOrder=L[0].o.renderOrder; mesh.matrixAutoUpdate=false; mesh.frustumCulled=false; mesh.userData.worldPerf='signs'; scene.add(mesh);
        for(const it of L){ it.mesh=mesh; it.cen=it.f.cen; it.far=it.f.r; it.near=false; it.o.visible=false; if(!OLD) wpSignRelease(it); const i=FARCULL.indexOf(it.f); if(i>=0) FARCULL.splice(i,1); SIGN.list.push(it); } } }
    st.signs=[SIGN.list.length,SIGN.pages.length]; }
  // memory cut (default; ?oldsigns=1 = previous behaviour): the original sign texture is disposed after packing and detached
  // from the scene (kept only as it.m for change detection). A <=512 px source copy (1024x256 -> 512x128) is kept CPU-side; the
  // NEAR swap-in texture is regenerated from it on demand, LRU-capped at SIGN.CAP live, disposed when the rider leaves NEAR.
  function wpSignRelease(it){ const im=it.t.image, sc=Math.min(1,512/im.width); const c=document.createElement('canvas'); c.width=Math.max(1,Math.round(im.width*sc)); c.height=Math.max(1,Math.round(im.height*sc));
    c.getContext('2d').drawImage(im,0,0,c.width,c.height); it.src=c; it.t.dispose(); it.nm=it.m.clone(); it.nm.map=null; it.o.material=it.nm; }
  function wpSwapOn(it){ if(SIGN.swaps.has(it)){ SIGN.swaps.delete(it); SIGN.swaps.set(it,it.sw); return true; }
    if(SIGN.swaps.size>=SIGN.CAP) return false; // cap reached: this one keeps its atlas quad (still legible), takes a slot when one frees
    const t=new THREE.CanvasTexture(it.src); t.encoding=it.t.encoding; t.anisotropy=4; it.sw=t; it.nm.map=t; it.nm.needsUpdate=true; SIGN.swaps.set(it,t); SIGN.made++; return true; }
  function wpSwapOff(it){ const t=SIGN.swaps.get(it); if(!t) return; SIGN.swaps.delete(it); t.dispose(); it.sw=null; it.nm.map=null; it.nm.needsUpdate=true; SIGN.freed++; }
  function setQuad(it,on){ const a=it.mesh.geometry.attributes.position; if(on) a.array.set(it.base,it.j*18); else a.array.fill(it.base[0],it.j*18,it.j*18+18); a.needsUpdate=true; }
  let sf=0; function signTick(cp){ const N2=SIGN.NEAR*SIGN.NEAR; const check=(++sf%30)===0;
    for(const it of SIGN.list){ if(it.dead) continue;
      if(check&&(it.o.material!==(it.nm||it.m)||it.m.map!==it.t||it.t.version!==it.ver||it.m.color.getHex()!==it.col||!it.o.parent)){ it.dead=true; setQuad(it,false); if(it.nm){ wpSwapOff(it); it.o.material=it.m; it.t.needsUpdate=true; } FARCULL.push(it.f); continue; } // changed at runtime -> back to live mesh
      const d2=it.cen.distanceToSquared(cp), near=d2<N2, far=d2>it.far*it.far*1.6;
      if(it.nm){ const want=near&&wpSwapOn(it); if(!near) wpSwapOff(it); if(want!==it.near){ it.near=want; it.o.visible=want; setQuad(it,!want&&!it.hid); } }
      else if(near!==it.near){ it.near=near; it.o.visible=near; setQuad(it,!near&&!it.hid); }
      if(!it.near&&far!==!!it.hid){ it.hid=far; setQuad(it,!far); } /* it.near (not near): a capped swap-in keeps its atlas quad */ } }

  // tier: ?tier=quest | desktop; auto quest on a Quest UA or while an XR session runs. Desktop look unchanged.
  let INK=[]; const qp=new URLSearchParams(location.search).get('tier'); const TIERNAME=()=>qp||((/OculusBrowser|Quest/i.test(navigator.userAgent)||(typeof renderer!=='undefined'&&renderer.xr&&renderer.xr.isPresenting))?'quest':'desktop');
  let tierNow=null, far0=null; function applyTier(){ const t=TIERNAME(); if(t===tierNow) return; tierNow=t; const q=t==='quest';
    for(const d of INK) d.r=q?40:60;
    if(typeof camera!=='undefined'){ if(far0===null) far0=camera.far; camera.far=q?Math.min(far0,(scene.fog&&scene.fog.far||360)+20):far0; camera.updateProjectionMatrix(); }
    st.tier=t; }
  let tf=0; function tierCull(cp){ if(tierNow!=='quest'||!scene.fog) return; const F=scene.fog.far; // hide merged tiles wholly beyond the fog
    for(const o of scene.children){ if(!o.userData.worldPerf||o.userData.worldPerf==='signs') continue; const s=o.geometry.boundingSphere; if(!s) continue; o.visible=s.center.distanceTo(cp)-s.radius<F; } }

  // 7. details.js chunks (one InstancedMesh per kind per 90 m chunk, DETM-culled by chunk centre) -> one InstancedMesh per
  // kind+material; every 15 frames the visible chunks' instances are packed into it (same per-chunk radius rule, same look).
  const DG=[]; function packDetails(){ if(typeof DETM==='undefined') return; const by=new Map();
    for(const d of DETM){ const m=d.m; if(!m||!m.isInstancedMesh||m.parent!==scene) continue; const k=m.geometry.uuid+'|'+m.material.uuid+'|'+!!m.instanceColor; (by.get(k)||by.set(k,[]).get(k)).push(d); }
    for(const L of by.values()){ if(L.length<2) continue; let n=0; for(const d of L) n+=d.m.count; const m0=L[0].m;
      const im=new THREE.InstancedMesh(m0.geometry,m0.material,n); im.count=0; im.userData.worldPerf='details'; im.frustumCulled=false; if(m0.instanceColor) im.instanceColor=new THREE.InstancedBufferAttribute(new Float32Array(n*3),3);
      scene.add(im); for(const d of L){ d.m.visible=false; const i=DETM.indexOf(d); if(i>=0) DETM.splice(i,1); } DG.push({im,L,key:''}); }
    if(typeof camera!=='undefined'){ camera.getWorldPosition(_dj); detTick(_dj); } // filled at pack time, not 15 frames later
    st.details=[DG.reduce((a,g)=>a+g.L.length,0),DG.length]; }
  const DET_PAD=12; // pre-pack margin (m): chunks enter the packed set before they reach the visible radius -> no pop between 15-frame refills
  function detTick(cp){ for(const g of DG){ let n=0, key=''; for(const d of g.L){ const dx=d.cen.x-cp.x, dz=d.cen.z-cp.z, rr=d.r+DET_PAD; if(dx*dx+dz*dz<rr*rr){ key+=g.L.indexOf(d)+','; } }
      if(key===g.key) continue; g.key=key; const M=g.im.instanceMatrix.array, C=g.im.instanceColor&&g.im.instanceColor.array;
      for(const d of g.L){ const dx=d.cen.x-cp.x, dz=d.cen.z-cp.z, rr=d.r+DET_PAD; if(!(dx*dx+dz*dz<rr*rr)) continue; const c=d.m.count;
        M.set(d.m.instanceMatrix.array.subarray(0,c*16),n*16); if(C) C.set(d.m.instanceColor.array.subarray(0,c*3),n*3); n+=c; }
      g.im.count=n; g.im.visible=n>0; g.im.instanceMatrix.needsUpdate=true; if(C) g.im.instanceColor.needsUpdate=true; } }

  // 8. legacy turf tag rings (world.js tagSpots: 1 mesh each, material swapped purple->gold when tagged) -> 2 InstancedMeshes
  // that mirror each ring's current material every 15 frames. tagSpots data and the ring meshes themselves are untouched (hidden).
  const RING={list:[],ims:[]}; function packRings(){ if(typeof tagSpots==='undefined'||tagSpots.length<2) return; const g=tagSpots[0].m.geometry;
    const mats=[glow(C.purple,.8),glow(C.gold,.6)]; RING.ims=mats.map(m=>{ const im=new THREE.InstancedMesh(g,m,tagSpots.length); im.count=0; im.frustumCulled=false; im.userData.worldPerf='rings'; scene.add(im); return im; });
    RING.list=tagSpots.map(t=>t.m); for(const r of RING.list){ r.updateMatrixWorld(true); r.visible=false; } RING.key=''; st.rings=RING.list.length; }
  function ringTick(){ if(!RING.list.length) return; let key=''; for(const r of RING.list) key+=r.material===RING.ims[0].material?'0':r.material===RING.ims[1].material?'1':'x'; if(key===RING.key) return; RING.key=key;
    const n=[0,0]; RING.list.forEach((r,i)=>{ const k=key[i]; if(k==='x'){ r.visible=true; return; } r.visible=false; r.updateMatrixWorld(true); RING.ims[+k].setMatrixAt(n[+k]++,r.matrixWorld); });
    RING.ims.forEach((im,i)=>{ im.count=n[i]; im.instanceMatrix.needsUpdate=true; }); }
  // 9. mission beacon beams (world.js: one additive cylinder + own material each, same opacity animation) -> 1 vertex-coloured mesh
  const BEAM={src:null,mat:null}; function packBeams(){ const L=scene.children.filter(o=>o.isMesh&&o.visible&&o.geometry.type==='CylinderGeometry'&&o.geometry.parameters.height===40&&o.material.blending===THREE.AdditiveBlending&&!o.material.map);
    if(L.length<2) return; const mat=new THREE.MeshBasicMaterial({vertexColors:true,transparent:true,opacity:L[0].material.opacity,blending:THREE.AdditiveBlending,depthWrite:false});
    const tmp=L.map(o=>{ const g=o.geometry.index?o.geometry.toNonIndexed():o.geometry.clone(); const c=o.material.color, n=g.attributes.position.count, A=new Float32Array(n*3); for(let i=0;i<n;i++) A.set([c.r,c.g,c.b],i*3); g.setAttribute('color',new THREE.BufferAttribute(A,3)); const t=new THREE.Mesh(g,mat); o.updateMatrixWorld(true); t.matrixWorld.copy(o.matrixWorld); t.matrixAutoUpdate=false; t.updateMatrixWorld=()=>{}; return t; });
    mergeList(tmp,mat); for(const o of L) o.visible=false; BEAM.src=L[0].material; BEAM.mat=mat; st.beams=L.length; }

  // ---------- PASS 2 ----------
  // vertex-alpha basic material: per-vertex colour + aAlpha, so transparent glow pieces of different colour/opacity share one draw
  const _va={}; function vaMat(m){ const k=[m.blending,m.depthWrite,m.side,m.fog,m.depthTest].join('|'); if(_va[k]) return _va[k];
    const n=new THREE.MeshBasicMaterial({vertexColors:true,transparent:true,blending:m.blending,depthWrite:m.depthWrite,depthTest:m.depthTest,side:m.side,fog:m.fog});
    n.onBeforeCompile=sh=>{ sh.vertexShader='attribute float aAlpha; varying float vAA;\n'+sh.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\n vAA=aAlpha;');
      sh.fragmentShader='varying float vAA;\n'+sh.fragmentShader.replace('#include <color_fragment>','#include <color_fragment>\n diffuseColor.a*=vAA;'); };
    n.customProgramCacheKey=()=>'wp_va'; return _va[k]=n; }
  // merge with explicit per-vertex colour (+alpha); matrices from matrixWorld (or o.__mw override)
  function mergeColored(L,mat,alpha){ const v=new THREE.Vector3(), nm=new THREE.Matrix3(), P=[], N=[], C=[], A=[];
    for(const o of L){ const mw=o.matrixWorld; const g=o.geometry.index?o.geometry.toNonIndexed():o.geometry; nm.getNormalMatrix(mw); const pa=g.attributes.position, na=g.attributes.normal, gc=g.attributes.color;
      const col=o.material.color, op=o.material.opacity;
      for(let i=0;i<pa.count;i++){ v.fromBufferAttribute(pa,i).applyMatrix4(mw); P.push(v.x,v.y,v.z); if(na){ v.fromBufferAttribute(na,i).applyMatrix3(nm).normalize(); N.push(v.x,v.y,v.z); } else N.push(0,1,0);
        if(gc) C.push(gc.getX(i)*col.r,gc.getY(i)*col.g,gc.getZ(i)*col.b); else C.push(col.r,col.g,col.b); A.push(op); } }
    const geo=new THREE.BufferGeometry(); geo.setAttribute('position',new THREE.Float32BufferAttribute(P,3)); geo.setAttribute('normal',new THREE.Float32BufferAttribute(N,3)); geo.setAttribute('color',new THREE.Float32BufferAttribute(C,3));
    if(alpha) geo.setAttribute('aAlpha',new THREE.Float32BufferAttribute(A,1)); geo.computeBoundingSphere();
    const m=new THREE.Mesh(geo,mat); m.renderOrder=L[0].renderOrder; m.matrixAutoUpdate=false; m.userData.worldPerf='p2'; scene.add(m); for(const o of L) o.visible=false; return m; }
  // a) holo tower (world.js Terminal Plaza): 4 shells + beam share hm -> 1 mesh; 4 wireframe shells -> 1 wireframe mesh. Same group, still rotates.
  function packHolo(){ let done=0; scene.traverse(o=>{ if(!o.isGroup||o.children.length!==9) return; const sh=o.children.filter(c=>c.isMesh&&c.material.blending===THREE.AdditiveBlending), wf=o.children.filter(c=>c.isMesh&&c.material.wireframe);
      if(sh.length!==5||wf.length!==4||sh.some(c=>c.material!==sh[0].material)) return; o.updateMatrixWorld(true);
      for(const [L,mat] of [[sh,sh[0].material],[wf,wf[0].material]]){ const geos=L.map(c=>{ const g=c.geometry.clone(); c.updateMatrix(); g.applyMatrix4(c.matrix); return g; });
        let vo=0; const P=[], I=[]; for(const g of geos){ const pa=g.attributes.position; for(let i=0;i<pa.count;i++) P.push(pa.getX(i),pa.getY(i),pa.getZ(i)); for(const ix of g.index.array) I.push(ix+vo); vo+=pa.count; }
        const geo=new THREE.BufferGeometry(); geo.setAttribute('position',new THREE.Float32BufferAttribute(P,3)); geo.setIndex(I); geo.computeBoundingSphere(); const m=new THREE.Mesh(geo,mat); m.userData.worldPerf='holo'; o.add(m); for(const c of L) c.visible=false; }
      done++; }); st.holo=done; }
  // b) searchlight cones (world.js searchlight(): own material each, animated sway) -> 1 InstancedMesh with instanceColor, matrices copied per frame
  const SL={list:[],im:null}; function packSearch(){ const L=[]; scene.traverse(o=>{ if(o.isMesh&&o.geometry.type==='ConeGeometry'&&o.geometry.parameters.height===90&&o.material.blending===THREE.AdditiveBlending&&o.parent&&o.parent.isGroup&&o.visible) L.push(o); });
    if(L.length<2) return; const m0=L[0].material, mat=new THREE.MeshBasicMaterial({transparent:true,opacity:m0.opacity,depthWrite:false,blending:m0.blending,side:m0.side});
    const im=new THREE.InstancedMesh(L[0].geometry,mat,L.length); im.frustumCulled=false; im.userData.worldPerf='search'; const c=new THREE.Color(); L.forEach((o,i)=>im.setColorAt(i,c.copy(o.material.color))); scene.add(im);
    SL.list=L; SL.im=im; SL.src=L.map(o=>o.material); for(const o of L){ o.material=new THREE.MeshBasicMaterial({visible:false}); } st.search=L.length; }
  function searchTick(){ if(!SL.im) return; SL.list.forEach((o,i)=>{ o.updateMatrixWorld(true); SL.im.setMatrixAt(i,o.matrixWorld); }); SL.im.instanceMatrix.needsUpdate=true; }
  // c) static singletons + transparent glow tiles: snapshot now, merge after 2 s if matrix/visibility/colour/opacity never changed
  function singles(){ const ex=new Set([Ride.group,rig,typeof UI!=='undefined'?UI.mesh:null,...(typeof cans!=='undefined'?cans:[]),...(typeof tagSpots!=='undefined'?tagSpots.map(t=>t.m):[])]);
    const isEx=o=>{ for(let a=o;a;a=a.parent){ if(ex.has(a)||a.userData.noMerge) return true; } return false; };
    const outl=new Set(typeof outlines!=='undefined'?outlines:[]); const cand=[]; scene.updateMatrixWorld(true);
    scene.traverse(o=>{ if(!o.isMesh||o.isInstancedMesh||o.isSkinnedMesh||Array.isArray(o.material)||o.frustumCulled===false||o.renderOrder<0||outl.has(o)) return;
      const m=o.material; if(m.map||m.wireframe||m.vertexColors&&!o.userData.worldPerf||!(m.isMeshBasicMaterial||m.isMeshToonMaterial)||m.onBeforeCompile&&m.onBeforeCompile.toString().includes('aAlpha')) return;
if(o.userData.worldPerf&&o.userData.worldPerf!==true) return; for(let a=o;a;a=a.parent) if(!a.visible) return; if(isEx(o)) return;
      if(o.children.length) return; // meshes with ink hulls stay (their hulls are separate draws, culled by DETM)
      if(!m.transparent&&m.side!==THREE.FrontSide) return;
      cand.push([o,o.matrixWorld.clone(),m.color.getHex(),m.opacity,m]); });
    setTimeout(()=>{ scene.updateMatrixWorld(true); const ok=cand.filter(([o,mw,c,op,m])=>o.parent&&o.visible&&o.material===m&&o.matrixWorld.equals(mw)&&m.color.getHex()===c&&m.opacity===op);
      // animated-opacity materials are caught by the opacity check only if they changed in the window; also skip any material listed on an animated closure
      const by=new Map();
      for(const [o] of ok){ const m=o.material, g=o.geometry; if(!g.boundingSphere) g.computeBoundingSphere(); const c=g.boundingSphere.center.clone().applyMatrix4(o.matrixWorld);
        const T=Math.floor((c.x+5e4)/TILE)+'|'+Math.floor((c.z+5e4)/TILE); let k;
        if(m.transparent&&m.isMeshBasicMaterial) k='VA|'+[m.blending,m.depthWrite,m.side,m.fog].join(',')+'|'+o.renderOrder+'|'+T;
        else if(m.isMeshBasicMaterial) k='VB|'+m.fog+'|'+o.renderOrder+'|'+T;
        else if(m.isMeshToonMaterial&&!m.transparent&&typeof vcMat==='function') k='VT|'+mergeKey(m,{attributes:{}})+'|'+o.renderOrder+'|'+T;
        else continue; (by.get(k)||by.set(k,[]).get(k)).push(o); }
      let n=0,mm=0; for(const [k,L] of by){ if(L.length<2) continue; let mat; if(k[1]==='A') mat=vaMat(L[0].material); else if(k[1]==='B') mat=vcMat(L[0].material); else mat=vcMat(L[0].material);
        mergeColored(L,mat,k[1]==='A'); n+=L.length; mm++; }
      st.singles=[n,mm,cand.length]; },2000); }
  // 8. can pickups (world.js: ~85 cans, each a glow cylinder + ink hull child = 2 draws per visible can) -> 2 InstancedMeshes that
  // mirror every can the game itself shows (c.visible && !got) each frame. Originals stay in the scene for all game logic
  // (pickup, minimap, cull, bob/spin), only moved to layer 31 so the camera skips drawing them.
  const CANS={b:null,h:null};
  function wpCanPack(){ if(typeof cans==='undefined'||!cans.length) return; const c0=cans[0], h0=c0.children.find(k=>k.isMesh);
    const mk=(g,m)=>{ const im=new THREE.InstancedMesh(g,m,cans.length); im.count=0; im.frustumCulled=false; im.userData.worldPerf='cans'; im.instanceMatrix.setUsage(THREE.DynamicDrawUsage); scene.add(im); return im; };
    for(const c of cans){ if(c.geometry!==c0.geometry||c.material.color.getHex()!==c0.material.color.getHex()) return; } // only if they really are identical
    CANS.b=mk(c0.geometry,c0.material); if(h0) CANS.h=mk(h0.geometry,h0.material); CANS.hm=h0?h0.matrix.clone():null;
    for(const c of cans){ c.layers.set(31); c.traverse(k=>k.layers.set(31)); } st.cans=cans.length; }
  const _cm=new THREE.Matrix4();
  // Drawn set = exactly the cans the game shows (c.visible && !c.userData.got), rebuilt compactly every frame (82 cans), so a can
  // collected by the base game (pickup radius), pad.js:44 or anything else disappears the same frame; one that becomes visible
  // again reappears. Spin/bob (base loop: rotation.y, position.y) are mirrored from each can's own transform.
  // GPU upload only when a matrix or the count actually changed.
  function wpCanSet(im,i,mat){ const a=im.instanceMatrix.array, e=mat.elements, o=i*16; let d=false; for(let k=0;k<16;k++) if(a[o+k]!==e[k]){ a[o+k]=e[k]; d=true; } return d; }
  function wpCanTick(){ if(!CANS.b) return; let n=0, m=0, db=false, dh=false; for(const c of cans){ if(!c.visible||c.userData.got) continue; c.updateMatrix(); if(wpCanSet(CANS.b,n++,c.matrix)) db=true; const h=CANS.h&&c.children[0]; if(h&&h.isMesh){ h.updateMatrix(); if(wpCanSet(CANS.h,m++,_cm.multiplyMatrices(c.matrix,h.matrix))) dh=true; } } // bridge cans have no ink hull
    if(db||CANS.b.count!==n){ CANS.b.count=n; CANS.b.instanceMatrix.needsUpdate=true; } if(CANS.h&&(dh||CANS.h.count!==m)){ CANS.h.count=m; CANS.h.instanceMatrix.needsUpdate=true; } }
  window.CANS_SYNC=()=>wpCanTick(); window.CANS_HIDE=(c)=>{ if(!c) return; c.visible=false; c.userData.got=true; wpCanTick(); };
  // 9. static InstancedMesh pools (INST box/glow/cyl/cone + others; all frustumCulled=false because r128 bounds them by the unit
  // geometry): (a) pools sharing geometry+material are merged into one (same look, -1 draw each); (b) every pool gets a real
  // world bounding sphere (own geometry clone) so it is frustum-culled, and is hidden when wholly beyond fog far; (c) world_perf's
  // own dynamic IMs are hidden while count==0 (r128 still issues an empty instanced draw). Pools whose instanceMatrix changes at
  // runtime are re-bounded when their version moves. Gameplay data untouched (no colliders/splines/spots read or written here).
  const POOLS=[]; const _ps=new THREE.Vector3(), _pq=new THREE.Quaternion(), _pc=new THREE.Vector3(), _pm=new THREE.Matrix4();
  function wpPoolBound(P){ const im=P.im, a=im.instanceMatrix.array, g=im.geometry; if(!g.boundingSphere) g.computeBoundingSphere(); const r0=P.r0;
    let mnx=1e9,mny=1e9,mnz=1e9,mxx=-1e9,mxy=-1e9,mxz=-1e9,rs=0; for(let i=0;i<im.count;i++){ _pm.fromArray(a,i*16); _pm.decompose(_pc,_pq,_ps); const r=r0*Math.max(_ps.x,_ps.y,_ps.z);
      if(r===0) continue; rs=Math.max(rs,r); mnx=Math.min(mnx,_pc.x); mny=Math.min(mny,_pc.y); mnz=Math.min(mnz,_pc.z); mxx=Math.max(mxx,_pc.x); mxy=Math.max(mxy,_pc.y); mxz=Math.max(mxz,_pc.z); }
    if(mnx>mxx){ g.boundingSphere.center.set(0,-1e5,0); g.boundingSphere.radius=0; P.empty=true; } else { const c=g.boundingSphere.center.set((mnx+mxx)/2,(mny+mxy)/2,(mnz+mxz)/2); g.boundingSphere.radius=Math.hypot(mxx-mnx,mxy-mny,mxz-mnz)/2+rs; P.empty=false; }
    P.ver=im.instanceMatrix.version; P.cnt=im.count; }
  function wpPools(){ const L=scene.children.filter(o=>o.isInstancedMesh&&!o.userData.worldPerf&&o.frustumCulled===false&&o.visible&&!o.geometry.isInstancedBufferGeometry&&!(o.material.isShaderMaterial)&&o.matrixWorld.equals(new THREE.Matrix4()));
    // (a) merge same geometry+material+colour-mode
    const by=new Map(); for(const o of L){ const k=o.geometry.uuid+'|'+o.material.uuid+'|'+!!o.instanceColor; (by.get(k)||by.set(k,[]).get(k)).push(o); } let merged=0; const keep=[];
    for(const G of by.values()){ if(G.length===1){ keep.push(G[0]); continue; } const n=G.reduce((s,o)=>s+o.count,0), m0=G[0]; const im=new THREE.InstancedMesh(m0.geometry,m0.material,n); im.frustumCulled=false; im.renderOrder=m0.renderOrder;
      if(m0.instanceColor) im.instanceColor=new THREE.InstancedBufferAttribute(new Float32Array(n*3),3); let j=0; for(const o of G){ im.instanceMatrix.array.set(o.instanceMatrix.array.subarray(0,o.count*16),j*16); if(o.instanceColor) im.instanceColor.array.set(o.instanceColor.array.subarray(0,o.count*3),j*3); j+=o.count; o.visible=false; o.userData.wpMergedInto=im; }
      im.userData.wpPoolOf=G.length; scene.add(im); keep.push(im); merged+=G.length-1; }
    // (b) own geometry clone + real bounds
    for(const im of keep){ const g=im.geometry.clone(); g.computeBoundingSphere(); const r0=g.boundingSphere.center.length()+g.boundingSphere.radius; im.geometry=g; const P={im,r0}; wpPoolBound(P); im.frustumCulled=true; POOLS.push(P); }
    st.pools=[L.length,merged,POOLS.length]; }
  function wpPoolTick(cp){ const F=scene.fog?scene.fog.far:1e9; for(const P of POOLS){ const im=P.im; if(im.instanceMatrix.version!==P.ver||im.count!==P.cnt) wpPoolBound(P); const s=im.geometry.boundingSphere; im.visible=!P.empty&&(s.center.distanceTo(cp)-s.radius<F+20); }
    scene.children.forEach(o=>{ if(o.isInstancedMesh&&(o.userData.worldPerf==='details'||o.userData.worldPerf==='cans'||o.userData.worldPerf==='rings')) o.visible=o.count>0; }); }
  // 10. sea/shore overlays (flat transparent MeshBasic planes at sea level, not ours): (a) planes sharing one material (shore foam
  // bands etc.) are baked into ONE world-space mesh with that same material, so the base loop's opacity/offset animation keeps
  // working; (b) the two full-sea additive shimmer layers are drawn in ONE additive pass by a small shader that reads both original
  // materials every frame (map transform, colour, opacity, fog) -> identical sum. Mesh transforms are checked every 60 frames;
  // if a merged plane ever moves, that merge is undone. OFF by default; ?sea=1 enables.
  const SEA={groups:[],dual:null};
  // 11. same-material + same-geometry InstancedMesh pools (e.g. two box/glow pools built by different builders) -> one IM each.
  // Originals stay in the scene for their owners (moved to layer 31 so the camera skips them); the merged IM re-copies whenever an
  // original's instanceMatrix/instanceColor version, count or visibility changes (checked every 10 frames).
  const PM=[];
  function wpPoolMerge(){ const by=new Map(); for(const o of scene.children){ if(!o.isInstancedMesh||o.userData.worldPerf||Array.isArray(o.material)||o.layers.mask!==1||o.frustumCulled!==false) continue; /* city-wide pools only */ /* hidden ones too: owners toggle them by region */ const k=o.material.uuid+'|'+o.geometry.uuid+'|'+o.renderOrder+'|'+o.frustumCulled+'|'+(!!o.instanceColor); (by.get(k)||by.set(k,[]).get(k)).push(o); }
    for(const L of by.values()){ if(L.length<2) continue; const N=L.reduce((a,o)=>a+o.instanceMatrix.count,0); const im=new THREE.InstancedMesh(L[0].geometry,L[0].material,N); im.frustumCulled=L[0].frustumCulled; im.renderOrder=L[0].renderOrder; im.userData.worldPerf='pm';
      if(L[0].instanceColor) im.setColorAt(0,new THREE.Color(1,1,1)); scene.add(im); const g={im,L,sig:''}; PM.push(g); wpPoolMergeSync(g); for(const o of L) o.layers.set(31); }
    st.poolMerge=PM.map(g=>g.L.length); }
  function wpPoolMergeSync(g){ const sig=g.L.map(o=>o.instanceMatrix.version+':'+(o.instanceColor?o.instanceColor.version:0)+':'+o.count+':'+(o.visible?1:0)).join(','); if(sig===g.sig) return; g.sig=sig;
    const M=g.im.instanceMatrix.array, C=g.im.instanceColor&&g.im.instanceColor.array; let n=0; for(const o of g.L){ if(!o.visible) continue; const c=o.count; M.set(o.instanceMatrix.array.subarray(0,c*16),n*16); if(C&&o.instanceColor) C.set(o.instanceColor.array.subarray(0,c*3),n*3); n+=c; }
    g.im.count=n; g.im.visible=n>0; g.im.instanceMatrix.needsUpdate=true; if(C) g.im.instanceColor.needsUpdate=true; }
  /* opt-in: measured +3..5 world draws (merged sea is never frustum-culled) */ function wpSea(){ if(!/[?&]sea=1\b/.test(location.search)) return; const L=scene.children.filter(o=>o.isMesh&&o.visible&&!o.userData.worldPerf&&!o.children.length&&o.geometry.type==='PlaneGeometry'&&o.material.isMeshBasicMaterial&&o.material.transparent&&o.position.y<-1.5&&o.position.y>-3);
    const by=new Map(); for(const o of L) (by.get(o.material)||by.set(o.material,[]).get(o.material)).push(o);
    for(const [mat,G] of by){ if(G.length<2) continue; const geos=G.map(o=>{ o.updateMatrixWorld(true); const g=o.geometry.clone().applyMatrix4(o.matrixWorld); return g; });
      const P=[],U=[],I=[]; let base=0; for(const g of geos){ const ng=g.index?g:g; P.push(...g.attributes.position.array); U.push(...g.attributes.uv.array); for(const i of g.index.array) I.push(i+base); base+=g.attributes.position.count; }
      const geo=new THREE.BufferGeometry(); geo.setAttribute('position',new THREE.Float32BufferAttribute(P,3)); geo.setAttribute('uv',new THREE.Float32BufferAttribute(U,2)); geo.setIndex(I); geo.computeBoundingSphere();
      const m=new THREE.Mesh(geo,mat); m.renderOrder=G[0].renderOrder; m.matrixAutoUpdate=false; m.userData.worldPerf='sea'; scene.add(m); G.forEach(o=>o.visible=false);
      SEA.groups.push({m,G,snap:G.map(o=>o.matrixWorld.clone())}); }
    // dual additive full-sea layers
    const A=L.filter(o=>o.material.blending===THREE.AdditiveBlending&&o.material.map&&o.geometry.parameters.width>=1000&&o.visible);
    if(A.length===2&&A[0].geometry.parameters.width===A[1].geometry.parameters.width&&A[0].position.distanceTo(A[1].position)<.2){ const [a,b]=A, ma=a.material, mb=b.material;
      const U2=THREE.UniformsUtils.merge([THREE.UniformsLib.fog,{mA:{value:ma.map},mB:{value:mb.map},uA:{value:new THREE.Matrix3()},uB:{value:new THREE.Matrix3()},cA:{value:new THREE.Vector4()},cB:{value:new THREE.Vector4()}}]);
      U2.mA.value=ma.map; U2.mB.value=mb.map;
      const sm=new THREE.ShaderMaterial({uniforms:U2,fog:true,transparent:true,depthWrite:false,blending:THREE.CustomBlending,blendSrc:THREE.OneFactor,blendDst:THREE.OneFactor,blendEquation:THREE.AddEquation,
        vertexShader:'#include <fog_pars_vertex>\nuniform mat3 uA,uB; varying vec2 vA,vB; void main(){ vA=(uA*vec3(uv,1.)).xy; vB=(uB*vec3(uv,1.)).xy; vec4 mvPosition=modelViewMatrix*vec4(position,1.); gl_Position=projectionMatrix*mvPosition;\n#include <fog_vertex>\n}',
        fragmentShader:'#include <common>\n#include <fog_pars_fragment>\nuniform sampler2D mA,mB; uniform vec4 cA,cB; varying vec2 vA,vB; void main(){ vec4 ta=texture2D(mA,vA), tb=texture2D(mB,vB); vec3 ra=ta.rgb*cA.rgb, rb=tb.rgb*cB.rgb; float aa=ta.a*cA.a, ab=tb.a*cB.a;\n#ifdef USE_FOG\n #ifdef FOG_EXP2\n float ff=1.0-exp(-fogDensity*fogDensity*fogDepth*fogDepth);\n #else\n float ff=smoothstep(fogNear,fogFar,fogDepth);\n #endif\n ra=mix(ra,fogColor,ff); rb=mix(rb,fogColor,ff);\n#endif\n gl_FragColor=vec4(ra*aa+rb*ab,1.0); }'});
      const lin=c=>c; // MeshBasic in this build writes colours as-is (no output encoding change)
      const m=new THREE.Mesh(a.geometry,sm); m.position.copy(a.position); m.rotation.copy(a.rotation); m.scale.copy(a.scale); m.renderOrder=Math.max(a.renderOrder,b.renderOrder); m.frustumCulled=a.frustumCulled; m.userData.worldPerf='sea2';
      m.onBeforeRender=()=>{ for(const [o,mt,u,c] of [[a,ma,U2.uA,U2.cA],[b,mb,U2.uB,U2.cB]]){ const t=mt.map; if(t.matrixAutoUpdate) t.updateMatrix(); u.value.copy(t.matrix); c.value.set(mt.color.r,mt.color.g,mt.color.b,mt.visible&&o.userData.wpSeaOn!==false?mt.opacity:0); }
        U2.mA.value=ma.map; U2.mB.value=mb.map; };
      scene.add(m); a.visible=false; b.visible=false; SEA.dual={m,a,b,snap:[a.matrixWorld.clone(),b.matrixWorld.clone()]}; }
    st.sea=[SEA.groups.map(g=>g.G.length),!!SEA.dual]; }
  function wpSeaCheck(){ for(const g of SEA.groups){ if(g.undone) continue; if(g.G.some((o,i)=>{ o.updateMatrixWorld(); return !o.matrixWorld.equals(g.snap[i]); })){ g.undone=true; g.m.visible=false; g.G.forEach(o=>o.visible=true); } }
    const d=SEA.dual; if(d&&!d.undone){ d.a.updateMatrixWorld(); d.b.updateMatrixWorld(); if(!d.a.matrixWorld.equals(d.snap[0])||!d.b.matrixWorld.equals(d.snap[1])){ d.undone=true; d.m.visible=false; d.a.visible=d.b.visible=true; } } }
  function run(batchOut){ if(/[?&]noperf\b/.test(location.search)) return; st.start=performance.now();
    // 1. crew-base interiors
    if(typeof BASE_MATS!=='undefined'){ const mats=new Set(Object.values(BASE_MATS)); scene.traverse(o=>{ if(o.isMesh&&mats.has(o.material)){ if(!o.geometry.boundingSphere) o.geometry.computeBoundingSphere();
      o.updateMatrixWorld(true); near.push({o,c:o.geometry.boundingSphere.center.clone().applyMatrix4(o.matrixWorld),r:45}); } }); st.interiors=near.length; }
    // 2. asphalt per material
    if(typeof ASPH!=='undefined'&&ASPH.mats){ const mats=new Set(Object.values(ASPH.mats)), by=new Map();
      for(const o of scene.children) if(o.isMesh&&o.visible&&mats.has(o.material)&&!o.children.length){ const k=o.material.uuid+'|'+names(o.geometry); (by.get(k)||by.set(k,[]).get(k)).push(o); }
      let n=0,m=0; for(const L of by.values()){ if(L.length<2) continue; mergeList(L,L[0].material); n+=L.length; m++; } st.asphalt=[n,m]; }
    // 3. re-merge batcher tiles into 270 m tiles (skip ink hulls: they are distance-culled through DETM)
    { const by=new Map(), _p=new THREE.Vector3();
      for(const o of batchOut){ if(!o.isMesh||!o.visible||o.material===inkMat||o.parent!==scene) continue; const s=o.geometry.boundingSphere; if(!s) continue;
        const k=o.material.uuid+'|'+names(o.geometry)+'|'+Math.floor((s.center.x+5e4)/TILE)+'|'+Math.floor((s.center.z+5e4)/TILE)+'|'+o.renderOrder; (by.get(k)||by.set(k,[]).get(k)).push(o); }
      let n=0,m=0; for(const L of by.values()){ if(L.length<2) continue; mergeList(L,L[0].material); n+=L.length; m++; } st.batch=[n,m]; }

    // 5. water streaks (world.js createCity: 40 one-off glow planes, one per 90 m tile so the batcher never paired them) -> 1 mesh
    if(typeof _bmats!=='undefined'){ const wm=_bmats[0x1f5a8a+'_.5']||_bmats[0x1f5a8a+'_0.5']; if(wm){ const L=scene.children.filter(o=>o.isMesh&&o.visible&&o.material===wm&&!o.children.length&&o.geometry.type==='PlaneGeometry'); if(L.length>1){ mergeList(L,wm); st.streaks=L.length; } } }
    // 6. ink hull tiles drawn only up close (desktop 60 m, quest 40 m; were 95 m). Instanced detail hulls already cull at 50 m.
    if(typeof DETM!=='undefined'){ INK=DETM.filter(d=>d.m&&!d.m.isInstancedMesh&&d.m.material===inkMat); applyTier(); st.inkTiles=INK.length; }
    try{ packDetails(); }catch(e){ console.warn('world_perf details failed',e); }
    try{ wpCanPack(); }catch(e){ console.warn('world_perf cans failed',e); }
    try{ wpPools(); }catch(e){ console.warn('world_perf pools failed',e); }
    try{ wpSea(); }catch(e){ console.warn('world_perf sea failed',e); }
    try{ wpPoolMerge(); }catch(e){ console.warn('world_perf pool merge failed',e); }
    try{ packRings(); packBeams(); }catch(e){ console.warn('world_perf rings/beams failed',e); }
    try{ packHolo(); packSearch(); }catch(e){ console.warn('world_perf holo/search failed',e); }
    try{ atlasSigns(); }catch(e){ console.warn('world_perf atlas failed',e); }
    try{ singles(); }catch(e){ console.warn('world_perf singles failed',e); }
    st.ms=Math.round(performance.now()-st.start); WORLD_PERF.stats=st; }
  const _dj=new THREE.Vector3(1e9,0,0);
  function tick(){ if(typeof camera==='undefined') return; camera.getWorldPosition(_cp); wpCanTick(); if(SIGN.list.length) signTick(_cp); if((++tf%20)===0){ applyTier(); tierCull(_cp); } if((tf%10)===3||_dj.distanceToSquared(_cp)>64) wpPoolTick(_cp); if((tf%60)===11) wpSeaCheck(); if((tf%10)===5) for(const g of PM) wpPoolMergeSync(g); if(DG.length&&((tf%15)===0||_dj.distanceToSquared(_cp)>64)){ detTick(_cp); _dj.copy(_cp); } /* refill at once on camera moves > 8 m since last fill (respawn/teleport) */ if((tf%15)===7) ringTick(); if(BEAM.mat) BEAM.mat.opacity=BEAM.src.opacity; searchTick(); for(const n of near) n.o.visible=n.c.distanceToSquared(_cp)<n.r*n.r; }
  return { run, tick, stats:null, near, SIGN, detFill:(p)=>{ if(DG.length){ for(const g of DG) g.key=''; detTick(p); } } }; // detFill: probe/teleport hook
})();
// hook: capture what staticMerge creates, then run once it reports window.__merge
if(typeof staticMerge==='function'){ const _sm=staticMerge; staticMerge=function(){ const before=new Set(scene.children); _sm.apply(this,arguments);
  const iv=setInterval(()=>{ if(!window.__merge) return; clearInterval(iv); const out=scene.children.filter(o=>!before.has(o)&&o.isMesh&&o.matrixAutoUpdate===false);
    try{ WORLD_PERF.run(out); }catch(e){ console.warn('world_perf failed',e); } animated.push(WORLD_PERF.tick); },100); }; }
