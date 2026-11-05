// ===== FACADES (CC0 ambientCG material atlas on the single instanced building shader) =====
// 8 materials in one 2048x1024 atlas (albedo) + one (normal xy | roughness). Sampled with world-space box UVs in buildInstancedBuildings'
// ShaderMaterial -> zero new meshes, zero new draw calls. Materials: 0 brick 1 precast 2 board-formed 3 brushed steel 4 marble 5 travertine 6 stucco 7 corrugated alu.
const FACADE=(()=>{ const K2=window.SR_KTX2&&window.SR_KTX2.on; // ?ktx2=1 (patch_draco ktx2 gate; Rydah Optimizer step4): pre-flipped KTX2 copies, ETC1S albedo + UASTC nr; jpg fallback on error or no loader after ~300 frames
  const swapU=(t,c)=>{ for(const u of Object.values(FACADE.uniforms)) if(u&&u.value===t) u.value=c; };
  const ldK=(s,k)=>{ const t=new THREE.Texture(); let tries=0; // placeholder (no image, never uploads); swapped in place below. r128 Texture has NO userData: don't touch it
    const fb=e=>{ console.warn('[facade ktx2] fallback jpg',k,e||'no SR_KTX2 loader'); swapU(t,ld(s)); };
    const go=()=>{ try{ const L=typeof window.SR_KTX2.loader==='function'&&window.SR_KTX2.loader(); if(!L){ if(++tries>300) return fb(); return requestAnimationFrame(go); }
      L.load('assets/world_ktx2/'+k+'.ktx2',c=>{ c.wrapS=c.wrapT=THREE.ClampToEdgeWrapping; c.anisotropy=4; c.minFilter=THREE.LinearMipmapLinearFilter; c.generateMipmaps=false; c.flipY=false; swapU(t,c); },undefined,fb); }catch(e){ fb(e); } };
    requestAnimationFrame(go); return t; };
  const ld=(s,k)=>{ if(K2&&k){ try{ return ldK(s,k); }catch(e){ console.warn('[facade ktx2] init failed, jpg',k,e); } } const t=new THREE.TextureLoader().load(s); t.wrapS=t.wrapT=THREE.ClampToEdgeWrapping; t.anisotropy=4; t.generateMipmaps=true; t.minFilter=THREE.LinearMipmapLinearFilter; return t; };
  // per material: tile col,row | metres per tile | tint amount (1 = take building colour, e.g. pastel stucco)
  const T=[[0,0,1.8,.16],[1,0,3.0,.14],[2,0,2.4,.12],[3,0,1.2,.10],[0,1,2.0,.06],[1,1,2.4,.10],[2,1,3.0,1.0],[3,1,1.6,.35]];
  const W={ // district kit -> material weights [brick,precast,board,steel,marble,trav,stucco,corr]
    0:[.05,0,0,0,.15,.10,.70,0],      // cove beach deco: pastel stucco, marble/travertine hotels
    1:[0,.35,.10,.45,.10,0,0,0],      // portside terminal: steel+glass, precast
    2:[.45,.05,.10,0,0,0,0,.40],      // yard warehouses: brick, corrugated alu
    3:[.35,.20,.10,0,0,0,.35,0],      // neon strip
    4:[0,.30,0,.20,.20,.15,.15,0],    // bayfront condos: precast, marble, travertine
    5:[.30,.25,.20,.15,.10,0,0,0],    // billboard mile
    6:[.50,0,.30,0,0,.20,0,0] };      // north shore
  const h=(x,z)=>{ const s=Math.sin(x*12.9898+z*78.233)*43758.5453; return s-Math.floor(s); };
  const pick=(k,hgt,x,z)=>{ let w=W[k]||W[1]; if(hgt>30&&(k===4||k===5)) w=[0,.3,0,.5,.2,0,0,0]; // towers -> curtain wall / precast / marble
    let r=h(x,z), a=0; for(let i=0;i<8;i++){ a+=w[i]; if(r<a) return i; } return 1; };
  const uniforms={ uFA:{value:ld('__FACADE_ALB__','facade_albedo')}, uFN:{value:ld('__FACADE_NR__','facade_nr')}, uFT:{value:T.map(t=>new THREE.Vector4(t[0],1-t[1],t[2],t[3]))},
    uEnv:{value:(typeof ikkiEnv==='function')?ikkiEnv():null}, uDay:{value:0} };
  return { uniforms, pick, setDay(v){ uniforms.uDay.value=v; } }; })();
