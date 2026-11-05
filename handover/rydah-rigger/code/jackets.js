// ===== CREW JACKETS: one brand per crew. Jacket slot = crew colour, accent/trim = darker shade (Code : E = black + gold),
// back patch = crew emblem (same emblemTex() art as garage murals / turf tags) from ONE shared 1024x512 atlas -> +1 draw call per rider.
const JACKET_ORDER=["codee","karasu","static","behemoth","anubis","forest","genesis","ttt"];
const JACKET={ atlas:null, mat:null, geo:{} };
// CREW_JACKET (Oliver's crew boards: skyrydahs-ref/meshy-prompts-crews.md + visual-pack PROMPT; brief wins over jacket-colorways.json):
//  main = bomber body, trim = accent/hardware slot, panel = second jacket colour, mode: 0 none, 1 sleeves (arms past the shoulder joint), 2 side panels + shoulder yoke
//  glow = Air Treck wheel/LED glow on the shared Meshy skate. css = garage/emblem colour (unchanged: patch art + garage signs).
const CREW_JACKET={
  codee:   {main:0x141414,trim:0xffd700,panel:0x141414,mode:0,glow:0xffd700},   // Code : E black + gold
  karasu:  {main:0x07090b,trim:0x00e5ff,panel:0x00e5ff,mode:2,glow:0x00e5ff},   // black bomber, cyan panels (cyan + black only, no red)
  static:  {main:0xaa00ff,trim:0x00e5ff,panel:0xaa00ff,mode:0,glow:0x00e5ff},   // violet purple + electric cyan
  anubis:  {main:0x0a3d3a,trim:0xb08d57,panel:0x0a3d3a,mode:0,glow:0x18d6c4},   // deep teal + antique gold hardware
  forest:  {main:0xeef2ec,trim:0x1f5e36,panel:0x1f5e36,mode:2,glow:0x2ecc71},   // off-white bomber, forest-green panels
  behemoth:{main:0x0e0b09,trim:0xff6a00,panel:0xff6a00,mode:1,glow:0xff6a00},   // matte black bomber, blaze-orange sleeves
  genesis: {main:0xd1178f,trim:0xffc94a,panel:0xd1178f,mode:0,glow:0xff1fd1},   // magenta + gold trim/piping
  ttt:     {main:0x5b5f63,trim:0xb7472a,panel:0xb7472a,mode:2,glow:0xff5a2a} }; // steel gray bomber, rust-red panels
function crewBrand(id){ const g=(PALMA.garages||[]).find(q=>q.crew===id); const css=id==="codee"?"#FFD700":id==="forest"?"#e9efe6":(g?g.color:"#ffffff"); const c=new THREE.Color(css), J=CREW_JACKET[id];
  if(J) return Object.assign({css,cuff:new THREE.Color(J.main).multiplyScalar(.7).getHex()},J);
  return {css,main:c.getHex(),trim:c.clone().multiplyScalar(.32).getHex(),cuff:c.clone().multiplyScalar(.55).getHex(),panel:c.getHex(),mode:0,glow:c.getHex()}; }
// two-tone jacket: rest-pose (bind space) mask on the toon jacket slot -> panel colour; no mesh change, 0 extra draw calls
function crewJacketPanels(r,B){ const U=r.userData, bn=U.bones||{}, w=n=>bn[n]?bn[n].getWorldPosition(new THREE.Vector3()).applyMatrix4(new THREE.Matrix4().copy(r.matrixWorld).invert()):null;
  const ua=w('upperarm.L')||w('shoulder.L'), nk=w('neck'); if(!ua||!nk||!B.mode) return;
  const sx=Math.abs(ua.x), uni={uJkPanel:{value:new THREE.Color(B.panel)},uJkMode:{value:B.mode},uJkShX:{value:sx},uJkPX:{value:sx*.55},uJkYoke:{value:nk.y-.13}};
  (U.lod||r).traverse(o=>{ if(!o.isMesh||!o.material||!o.material.customProgramCacheKey||o.material.customProgramCacheKey()!=='rider-toon-r128') return; const m=o.material, ob=m.onBeforeCompile;
    if(m.userData.jk) return; m.userData.jk=1;
    m.onBeforeCompile=s=>{ ob(s); Object.assign(s.uniforms,uni);
      s.vertexShader=s.vertexShader.replace('#include <common>','#include <common>\n varying vec3 vRestP;').replace('#include <begin_vertex>','#include <begin_vertex>\n vRestP=position;');
      s.fragmentShader=s.fragmentShader.replace('#include <common>','#include <common>\n varying vec3 vRestP; uniform vec3 uJkPanel; uniform float uJkMode; uniform float uJkShX; uniform float uJkPX; uniform float uJkYoke;')
        .replace('diffuseColor.rgb*=slc;',`float jax=abs(vRestP.x), jsl=step(uJkShX,jax), jkm=0.;
         if(sl==2&&uJkMode>.5){ jkm=uJkMode<1.5?jsl:max(step(uJkPX,jax),step(uJkYoke,vRestP.y))*(1.-jsl); }
         diffuseColor.rgb*=mix(slc,uJkPanel,jkm);`); };
    m.customProgramCacheKey=()=>'rider-toon-r128-jk'; m.needsUpdate=true; }); }
// ===== shared black-shell Meshy Air Treck for crew NPC riders (skyrydahs-characters/wardrobe/skates/at-skate-meshy.glb, READ-only)
// One source GLB + one texture set for everyone; per rider: 1 SkinnedMesh per LOD level (both feet, rigid-weighted to foot.L/foot.R),
// 1 material clone per rider of ONE base material (same onBeforeCompile + cache key = one program; crew colours are per-clone uniforms). Toon skate parts are dropped before rMerge; their toon wheel glow is cut.
const SR_SKATE={ url:()=>CHAR_BASE+'wardrobe/skates/at-skate-meshy.v2.glb', tex:()=>CHAR_BASE+'shared/at-skate/at-skate-meshy-v2-1k', on:()=>new URLSearchParams(location.search).get('crewskate')!=='toon', src:null, mat:null };
// A-T crew colours (character-bible.md §1 "A-T: paint, frame, wheel, glow"; at-standard-spec §3). Keyed by garage id.
const SR_AT_LOADOUT={ codee:{paint:0x0b0b0d,frame:0xc9a227,wheel:0x1c1c20,glow:0xffd700}, karasu:{paint:0x07090b,frame:0x07090b,wheel:0x0b1418,glow:0x00e5ff},
  anubis:{paint:0x0a3d3a,frame:0xc9a75a,wheel:0x031413,glow:0x18d6c4}, static:{paint:0x0b0b0d,frame:0x9b4dff,wheel:0x3a1670,glow:0x00e5ff},
  forest:{paint:0x0b0b0d,frame:0x1f5e36,wheel:0xeef2ec,glow:0x2ecc71}, behemoth:{paint:0x0e0b09,frame:0x2b2b2b,wheel:0x0e0b09,glow:0xff6a00},
  genesis:{paint:0x0b0b0d,frame:0xffc94a,wheel:0x14031a,glow:0xff1fd1}, ttt:{paint:0x0b0b0d,frame:0x5b5f63,wheel:0x2e3033,glow:0xff5a2a} };
// Slot mask (Optimizer convention): R = primary (paint, shell), G = secondary (frame, chassis rails below FRAME_Y), B = wheel+glow (wheels); emissive glow = the
// texture's neon texels (LED strips / rims, any region). Spec has 4 slots on 3 channels -> wheel and glow share B; the wheel tint gets its own uniform uCrewWheel.
const SR_AT_FRAME_Y=-0.02;
// r128 mergeBufferGeometries rejects InterleavedBufferAttribute: copy each into a tight BufferAttribute (keeps normalized flag). Guard from Forge 05:28.
function srDeinterleave(g){ for(const k of Object.keys(g.attributes)){ const a=g.attributes[k]; if(!a.isInterleavedBufferAttribute) continue;
  const n=a.count,s=a.itemSize,out=new a.array.constructor(n*s); for(let i=0;i<n;i++) for(let c=0;c<s;c++) out[i*s+c]=a.data.array[i*a.data.stride+a.offset+c];
  g.setAttribute(k,new THREE.BufferAttribute(out,s,a.normalized)); } return g; }
// A-T skate scale (Forge at-skate-v2.md, 2 big wheels ruling 2026-10-30). Revert = set SR_SKATE_SCALE=1 (lift follows). Pivot = ankle pivot in skate mesh space.
const SR_SKATE_SCALE=1.25, SR_SKATE_PIVOT=new THREE.Vector3(0,0.12,-0.06);
const SR_SKATE_LIFT=0.0532;   // merged-path rider lift (m) at SR_SKATE_SCALE; doc nominal +0.059, set from the sandbox bind-pose wheel-bottom measurement
// per-side skate offset (applied to the skate verts, not the rider): shared rider-skeleton bind has RightFoot 10.53 mm above LeftFoot (Caali G A-pose), so one rider lift leaves the R wheels off the floor
const SR_SKATE_SIDE_DY={L:0,R:-0.0105};   // R = -(bind-floor gap of the R half at 1.25x), sandbox-measured 10.5 mm
const srSkateLift=()=>SR_SKATE_SCALE===1?0:SR_SKATE_LIFT;
function srScaleAbout(attr,c,s){ if(!attr) return; for(let k=0;k<attr.count;k++) attr.setXYZ(k,c.x+s*(attr.getX(k)-c.x),c.y+s*(attr.getY(k)-c.y),c.z+s*(attr.getZ(k)-c.z)); attr.needsUpdate=true; }
// lift a rider so scaled wheels meet the floor: insert one Group above the top bone (game moves the root, anims move Hips; neither touches this) -> no extra draws
function srRiderLift(skel,dy){ if(!dy) return; let t=skel.bones[0]; while(t.parent&&t.parent.isBone) t=t.parent; const P=t.parent; if(!P||P.userData.atLiftGrp) return; if(P.name==='SR_AT_Lift'){ return; }
  const L=new THREE.Group(); L.name='SR_AT_Lift'; L.userData.atLiftGrp=true; L.position.y=dy; P.add(L); for(const c of P.children.filter(c=>c.isBone)) L.add(c); P.userData.atLiftGrp=L; }
// Draco (skate v2 GLBs are Draco): guarded so a missing window.SR_DRACO only warns
function srSkateLoader(){ const L=new THREE.GLTFLoader(); if(window.SR_DRACO) L.setDRACOLoader(window.SR_DRACO); else console.warn('crew skate: window.SR_DRACO undefined, Draco skate GLBs will fail to decode'); return L; }
function srSkateSource(){ if(SR_SKATE.src) return SR_SKATE.src; return SR_SKATE.src=(async()=>{ const g=await new Promise((res,rej)=>srSkateLoader().load(SR_SKATE.url(),res,undefined,rej));
    const lv=[]; g.scene.updateMatrixWorld(true);
    for(let i=0;i<3;i++){ const parts=[]; g.scene.traverse(o=>{ if(o.isMesh&&new RegExp('_L'+i+'$').test(o.name)){ const q=srDeinterleave(o.geometry.clone()), wh=/Wheel/.test(o.name), p=q.attributes.position, mk=new Float32Array(p.count*3);
          for(let k=0;k<p.count;k++){ const y=p.getY(k); mk[k*3]=wh?0:(y<SR_AT_FRAME_Y?0:1); mk[k*3+1]=wh?0:(y<SR_AT_FRAME_Y?1:0); mk[k*3+2]=wh?1:0; }
          q.setAttribute('atMask',new THREE.BufferAttribute(mk,3)); q.applyMatrix4(o.matrixWorld);
          for(const k of Object.keys(q.attributes)) if(!['position','normal','uv','atMask'].includes(k)) q.deleteAttribute(k); if(q.index&&q.index.array.constructor!==Uint32Array) q.setIndex(new THREE.Uint32BufferAttribute(Array.from(q.index.array),1)); parts.push(q); } });
      if(parts.length){ lv[i]=THREE.BufferGeometryUtils.mergeBufferGeometries(parts,false); srScaleAbout(lv[i].attributes.position,SR_SKATE_PIVOT,SR_SKATE_SCALE); } }
    SR_SKATE.sockets={}; g.scene.traverse(o=>{ if(/^[LR]?_?at_/.test(o.name)||/_at_/.test(o.name)){ const w=o.getWorldPosition(new THREE.Vector3()); SR_SKATE.sockets[o.name]=w.sub(SR_SKATE_PIVOT).multiplyScalar(SR_SKATE_SCALE).add(SR_SKATE_PIVOT); } });   // sockets, mesh space, scaled about the pivot
    // Optimizer KTX2 (perf/ktx2/jackets_skate_ktx2.proposed.diff, merged by Rigger): ?ktx2=1 gate + loader ready -> shared/at-skate/ktx2/*.ktx2 (albedo ETC1S, mr/normal UASTC), PNG fallback on error.
    // r128 KTX2Loader does not set encoding -> albedo sRGB, -mr/-normal Linear set here. ?atktx2bad=1 forces a bad URL to test the fallback.
    const tl=new THREE.TextureLoader(), K2=(window.SR_KTX2&&window.SR_KTX2.on&&typeof window.SR_KTX2.loader==='function')?window.SR_KTX2.loader():null;
    const swap=(ph,t)=>{ for(const m of (SR_SKATE.mats||[])) for(const sl of ['map','normalMap','roughnessMap','metalnessMap']) if(m[sl]===ph){ m[sl]=t; m.needsUpdate=true; } };
    const png=(k,enc)=>{ const t=tl.load(SR_SKATE.tex()+k+'.png'); t.flipY=false; t.encoding=enc; t.anisotropy=4; return t; };
    const KT={}, T=k=>{ if(KT[k]) return KT[k]; const enc=k===''?THREE.sRGBEncoding:THREE.LinearEncoding;   /* albedo sRGB; -mr/-normal stay Linear */
      if(!K2) return KT[k]=png(k,enc);
      const ph=new THREE.Texture(); ph.flipY=false; ph.encoding=enc; const u=SR_SKATE.tex().replace(/at-skate-meshy-v2-1k$/,/atktx2bad=1/.test(location.search)?'ktx2-missing/at-skate-meshy-v2-1k':'ktx2/at-skate-meshy-v2-1k')+k+'.ktx2';
      K2.load(u,t=>{ t.flipY=false; t.encoding=enc; t.anisotropy=4; swap(ph,t); KT[k]=t; SR_SKATE.texSrc='ktx2'; },undefined,e=>{ console.warn('skate ktx2 failed, png',u,e&&e.message||e); const t=png(k,enc); swap(ph,t); KT[k]=t; SR_SKATE.texSrc='png-fallback'; });
      return KT[k]=ph; };
    const mat=new THREE.MeshStandardMaterial({map:T(''),normalMap:T('-normal'),roughnessMap:T('-mr'),metalnessMap:T('-mr'),roughness:1,metalness:1,skinning:true,envMap:typeof ikkiEnv==='function'?ikkiEnv():null,envMapIntensity:1.1});
    SR_SKATE.mats=[mat]; mat.userData.crew={uCrewPrimary:{value:new THREE.Color(0x0b0b0d)},uCrewSecondary:{value:new THREE.Color(0x0b0b0d)},uCrewWheel:{value:new THREE.Color(0x1c1c20)},uCrewGlow:{value:new THREE.Color(0xffffff)},uGlowStrength:{value:1.8}};
    SR_SKATE.obc=function(s){ Object.assign(s.uniforms,this.userData.crew);   // `this` = the material being compiled -> each clone binds ITS OWN uniform objects
      s.vertexShader=s.vertexShader.replace('#include <common>','#include <common>\n attribute vec3 atMask; varying vec3 vAtMask;').replace('#include <begin_vertex>','#include <begin_vertex>\n vAtMask=atMask;');
      s.fragmentShader=s.fragmentShader.replace('#include <common>','#include <common>\n uniform vec3 uCrewPrimary, uCrewSecondary, uCrewWheel, uCrewGlow; uniform float uGlowStrength; varying vec3 vAtMask; float atGm;')
      .replace('#include <map_fragment>',`#include <map_fragment>
        { vec3 t=diffuseColor.rgb; float cy=smoothstep(.1,.28,min(t.g,t.b)-t.r)*smoothstep(.25,.5,max(t.g,t.b)), rd=smoothstep(.12,.3,t.r-max(t.g,t.b))*smoothstep(.22,.45,t.r);
          atGm=max(cy,rd); float det=clamp(dot(t,vec3(.3333))/.10,0.,1.6);   // texture detail normalised to the atlas median luma (0.10) -> slot hex comes out exact on mid texels
          vec3 slot=vAtMask.r*uCrewPrimary+vAtMask.g*uCrewSecondary+vAtMask.b*uCrewWheel; diffuseColor.rgb=mix(slot*det,vec3(.02),atGm*.9);
          float au=smoothstep(.25,.4,t.r-t.b)*smoothstep(.55,.7,t.r)*(1.-atGm); diffuseColor.rgb=mix(diffuseColor.rgb,t,au); }   // Forge v2 gold hubs: texel-hue gold stays gold, rims keep uCrewWheel`)
      .replace('#include <emissivemap_fragment>','#include <emissivemap_fragment>\n totalEmissiveRadiance+=uCrewGlow*atGm*uGlowStrength;'); };   // in-shader emissive, no bloom (Quest)
    mat.onBeforeCompile=SR_SKATE.obc; mat.customProgramCacheKey=()=>'crew-at-skate-m1-v2hub'; SR_SKATE.mat=mat; return {lv,mat}; })(); }
// one clone of the ONE base material per rider: same onBeforeCompile fn + cache key -> one compiled program for every crew; colours are per-clone uniforms
function srSkateMaterial(base,lo){ const m=base.clone(); (SR_SKATE.mats=SR_SKATE.mats||[]).push(m); m.userData={crew:{uCrewPrimary:{value:new THREE.Color(lo.paint)},uCrewSecondary:{value:new THREE.Color(lo.frame)},uCrewWheel:{value:new THREE.Color(lo.wheel)},uCrewGlow:{value:new THREE.Color(lo.glow)},uGlowStrength:{value:1.8}}};
  m.onBeforeCompile=SR_SKATE.obc; m.customProgramCacheKey=base.customProgramCacheKey; m.name='M1_at_skate'; return m; }
// NPC default (Forge 19-bone crews): halves of at-skate-meshy.merged.glb (already mirrored, COLOR_0 mask), moved into AT-root space (ankle pivot origin)
// and fitted per foot like the legacy path -> still ONE SkinnedMesh for both feet. ?atskate=legacy = the old single-skate fit.
function srSkateHalves(){ if(SR_SKATE.halves) return SR_SKATE.halves; return SR_SKATE.halves=(async()=>{
    const g=await new Promise((res,rej)=>srSkateLoader().load(CHAR_BASE+'wardrobe/skates/at-skate-meshy.merged.v2.glb',res,undefined,rej)); g.scene.updateMatrixWorld(true);
    const rootP=s=>{ const o=g.scene.getObjectByName(s+'_AT_Root'); if(!o) throw new Error('merged skate: no '+s+'_AT_Root'); return o.getWorldPosition(new THREE.Vector3()); }, RP={L:rootP('L'),R:rootP('R')}, lv=[];
    g.scene.traverse(o=>{ if(!o.isSkinnedMesh) return; const m=o.name.match(/LOD(\d)/); if(!m) return; const G=srDeinterleave(o.geometry.clone()), si=G.attributes.skinIndex, n=si.count, ix=G.index.array, col=G.attributes.color;
      const out={}; for(const [side,j] of [['L',0],['R',1]]){ const keep=[]; for(let v=0;v<n;v++) if(si.getX(v)===j) keep.push(v); const remap=new Int32Array(n).fill(-1); keep.forEach((v,k)=>remap[v]=k);
        const geo=new THREE.BufferGeometry(), A=(name,src,sz)=>{ const a=new Float32Array(keep.length*sz); const ar=src.isInterleavedBufferAttribute?src.data.array:src.array, div=src.normalized&&ar instanceof Uint8Array?255:src.normalized&&ar instanceof Uint16Array?65535:1;   // r128 getX does not denormalise
          const gt=['getX','getY','getZ','getW']; keep.forEach((v,k)=>{ for(let c=0;c<sz;c++) a[k*sz+c]=src[gt[c]](v)/div; }); /* getX..W: works for interleaved (gltf-transform) buffers too */ geo.setAttribute(name,new THREE.BufferAttribute(a,sz)); };
        A('position',G.attributes.position,3); A('normal',G.attributes.normal,3); A('uv',G.attributes.uv,2); if(col) A('atMask',col,3);
        const p=geo.attributes.position; for(let k=0;k<p.count;k++) p.setXYZ(k,p.getX(k)-RP[side].x,p.getY(k)-RP[side].y,p.getZ(k)-RP[side].z);   // bind world -> AT-root space
        const I=[]; for(let t=0;t<ix.length;t+=3) if(remap[ix[t]]>=0) I.push(remap[ix[t]],remap[ix[t+1]],remap[ix[t+2]]); geo.setIndex(new THREE.Uint32BufferAttribute(I,1)); out[side]=geo; }
      lv[+m[1]]=out; });
    if(!lv[0]) throw new Error('merged skate: no LOD0'); return lv; })(); }
async function crewSkates(root,glowHex,crewId){ const U=root.userData, toon=U._toonSk||[]; if(!toon.length||!U.lod) return;
  let S, HV=null; try{ S=await srSkateSource(); }catch(e){ console.warn('crew skate: source failed, keeping toon skates',e); return; }
  if(SR_SKATE.mode()==='fit') try{ HV=await srSkateHalves(); }catch(e){ console.warn('crew skate: merged.glb failed, using the legacy fit',e); HV=null; }   // toon parts stay unmerged as a fallback
  const box=(geos,sgn)=>{ const b=new THREE.Box3(), v=new THREE.Vector3(); for(const g of geos){ const p=g.attributes.position; for(let i=0;i<p.count;i++){ v.fromBufferAttribute(p,i); if(v.x*sgn>0) b.expandByPoint(v); } } return b; };
  const t0=toon.filter(o=>/_LOD0_/.test(o.name)).map(o=>o.geometry), tb={L:box(t0,1),R:box(t0,-1)}, sb=new THREE.Box3().setFromBufferAttribute(S.lv[0].attributes.position), ss=sb.getSize(new THREE.Vector3()), sc=sb.getCenter(new THREE.Vector3());
  const top=Math.max(tb.L.max.y,tb.R.max.y);
  const lo=Object.assign({paint:0x0b0b0d,frame:0x2b2b2b,wheel:0x1c1c20},SR_AT_LOADOUT[crewId]||{}); if(glowHex!==undefined&&!SR_AT_LOADOUT[crewId]) lo.glow=glowHex; if(lo.glow===undefined) lo.glow=0xffffff;
  const mat=srSkateMaterial(S.mat,lo);
  let MS=null, MF=null; if(SR_SKATE.merged()) try{ MS=await srSkateMergedSrc(); let b0=null; U.lod.levels[0].object.children.forEach(o=>{ if(!b0&&o.isSkinnedMesh&&/^rider-toon/.test((o.material.customProgramCacheKey&&o.material.customProgramCacheKey())||'')) b0=o; });
    if(!b0) throw new Error('no LOD0 toon body'); MF=srSkateRiderFit(root,b0,MS); }catch(e){ console.warn('crew skate: v2 merged failed, using the fit path',e); MS=MF=null; }   // default = v2 merged; ?atskate=fit|legacy = old fits
  U.lod.levels.forEach((L,li)=>{ const grp=L.object; let body=null, glow=null; grp.children.forEach(o=>{ if(!o.isSkinnedMesh) return; const k=o.material.customProgramCacheKey&&o.material.customProgramCacheKey(); if(/^rider-toon/.test(k||'')&&!body) body=o; if(k==='rider-glow-r128') glow=o; });
    if(!body) return; const bones=body.skeleton.bones, bi=n=>Math.max(0,bones.findIndex(b=>b.name===n||b.name.replace(/[.:]/g,'')===n.replace(/[.:]/g,'')));
    if(glow&&glow.geometry.index){ const p=glow.geometry.attributes.position, ix=glow.geometry.index.array, keep=[];   // drop the toon wheel-glow tris (they sat on the old skates)
      for(let i=0;i<ix.length;i+=3){ if(Math.max(p.getY(ix[i]),p.getY(ix[i+1]),p.getY(ix[i+2]))>top+.02) keep.push(ix[i],ix[i+1],ix[i+2]); } glow.geometry.setIndex(keep); }
    if(MF){ grp.add(srSkateMergedMesh(MS,MF,body,li,mat)); if(li===0) srRiderLiftRL(root,body.skeleton,MF.lift); return; }
    const src=S.lv[Math.min(li,S.lv.length-1)]; if(!src) return; const halves=[], hv=HV&&HV[Math.min(li,HV.length-1)];
    for(const [side,bn] of [['L','foot.L'],['R','foot.R']]){ const b=tb[side]; if(b.isEmpty()) continue; const sz=b.getSize(new THREE.Vector3()), c=b.getCenter(new THREE.Vector3()), k=sz.z/ss.z*SR_SKATE_SCALE, ky=Math.max(k,(top+.012-b.min.y)/ss.y*SR_SKATE_SCALE), aY=new THREE.Matrix4().copy(body.skeleton.boneInverses[bi(bn)]).invert().elements[13], drop=(SR_SKATE_SCALE-1)*Math.max(0,aY-b.min.y);   // s about the ankle = bottom-anchored s, minus drop; rider lifted by drop   // length from the old skate, height up to the old boot top so the shin never shows a gap
      let g; if(hv&&hv[side]){ g=hv[side].clone(); const hb=new THREE.Box3().setFromBufferAttribute(g.attributes.position), hs=hb.getSize(new THREE.Vector3()), hc=hb.getCenter(new THREE.Vector3()), hk=sz.z/hs.z*SR_SKATE_SCALE, hky=Math.max(hk,(top+.012-b.min.y)/hs.y*SR_SKATE_SCALE);
        g.translate(-hc.x,-hb.min.y,-hc.z); g.scale(hk,hky,hk); }   // merged half: already mirrored + COLOR_0 mask (atMask), same fit as legacy
      else { g=src.clone(); g.translate(-sc.x,-sb.min.y,-sc.z); g.scale(k,ky,k); if(side==='R'){ g.scale(-1,1,1); const ix=g.index.array; for(let q=0;q<ix.length;q+=3){ const t=ix[q+1]; ix[q+1]=ix[q+2]; ix[q+2]=t; } } }   // legacy: R = mirror (outer side faces out, spec §2)
      g.translate(c.x,b.min.y-drop,c.z); if(li===0&&side==='L') srRiderLift(body.skeleton,drop); const n=g.attributes.position.count, j=bi(bn);
      g.setAttribute('skinIndex',new THREE.Uint16BufferAttribute(new Uint16Array(n*4).map((_,q)=>q%4?0:j),4)); g.setAttribute('skinWeight',new THREE.Float32BufferAttribute(new Float32Array(n*4).map((_,q)=>q%4?0:1),4)); halves.push(g); }
    if(!halves.length) return; const sm=new THREE.SkinnedMesh(THREE.BufferGeometryUtils.mergeBufferGeometries(halves,false),mat); sm.bind(body.skeleton,body.bindMatrix); sm.frustumCulled=false; sm.name='CrewATSkate_LOD'+li; sm.userData.noMerge=true; grp.add(sm); });
  for(const o of toon) if(o.parent) o.parent.remove(o); U._toonSk=null; U.atSkate=mat; if(MF){ U.atSkateFit={u:+MF.u.toFixed(4),lift:+MF.lift.toFixed(4),dyR:+MF.dy[1].toFixed(4),ground:+MF.ground.toFixed(4),shared:MF.shared}; U.atSockets=srSkateSockets(MS,MF); }
  U.setLoadout=U.setLoadout||function(o){ const C=mat.userData.crew; if(o.paint!==undefined) C.uCrewPrimary.value.set(o.paint); if(o.frame!==undefined) C.uCrewSecondary.value.set(o.frame); if(o.wheel!==undefined) C.uCrewWheel.value.set(o.wheel); if(o.glow!==undefined) C.uCrewGlow.value.set(o.glow); }; }
// ===== v2 merged skate on EVERY rider (Rydah Rigger 2026-10-30): player/Ikki (loadIkki) + crew NPCs (crewSkates) =====
// One SkinnedMesh per rider LOD (1 draw), rigid to the rider's own foot bones. Built in ROOT-LOCAL rest space:
//   p_rl = foot_rl[side] + u*SR_SKATE_SCALE*(p_shared - AT_Root_shared[side]) (+ R side offset), u = rider hips-foot / shared hips-foot.
// Lift (one value per rider, Group above the top bone) puts the L wheels on the rider's own ground (root parent origin);
// the per-side offset puts the R wheels there too. Shared skeleton -> lift 0.0532 / R -0.0105 (= SR_SKATE_LIFT / SR_SKATE_SIDE_DY).
// ?atskate=fit -> old fitted halves, ?atskate=legacy -> old single-skate fit (crews); ?atskate=off -> no v2 on loadIkki riders.
SR_SKATE.mode=()=>{ const q=new URLSearchParams(location.search).get('atskate'); return q==='legacy'||q==='fit'||q==='off'?q:'merged'; };
SR_SKATE.legacy=()=>SR_SKATE.mode()==='legacy';
SR_SKATE.merged=()=>SR_SKATE.mode()==='merged';
const SR_SHARED_HIPFOOT=0.7837;   // rider-skeleton.bones.json: |Hips - LeftFoot| at bind
function srSkateMergedSrc(){ return SR_SKATE.msrc||(SR_SKATE.msrc=new Promise((res,rej)=>srSkateLoader().load(CHAR_BASE+'wardrobe/skates/at-skate-meshy.merged.v2.glb',res,undefined,rej)).then(g=>{ g.scene.updateMatrixWorld(true);
  const RT=['L','R'].map(s=>{ const o=g.scene.getObjectByName(s+'_AT_Root'); if(!o) throw new Error('merged skate: no '+s+'_AT_Root'); return o.getWorldPosition(new THREE.Vector3()); });
  const sockets=[]; g.scene.traverse(o=>{ if(/^[LR]_at_/.test(o.name)){ const s=o.name[0]==='L'?0:1; sockets.push({name:o.name,s,off:o.getWorldPosition(new THREE.Vector3()).sub(RT[s])}); } });
  const lv=[]; g.scene.traverse(o=>{ if(!o.isSkinnedMesh) return; const m=o.name.match(/LOD(\d)/); if(!m) return; const G=srDeinterleave(o.geometry.clone()); G.applyMatrix4(o.matrixWorld);
    const si=G.attributes.skinIndex, n=si.count, side=new Uint8Array(n), minY=[1e9,1e9]; for(let k=0;k<n;k++){ side[k]=si.getX(k)===0?0:1; minY[side[k]]=Math.min(minY[side[k]],G.attributes.position.getY(k)); }
    const c=G.attributes.color; if(c){ const ca=c.isInterleavedBufferAttribute?c.data.array:c.array, dv=c.normalized&&ca instanceof Uint8Array?255:c.normalized&&ca instanceof Uint16Array?65535:1, mk=new Float32Array(n*3);
      for(let k=0;k<n;k++){ mk[k*3]=c.getX(k)/dv; mk[k*3+1]=c.getY(k)/dv; mk[k*3+2]=c.getZ(k)/dv; } G.setAttribute('atMask',new THREE.BufferAttribute(mk,3)); }
    for(const k of Object.keys(G.attributes)) if(!['position','normal','uv','atMask','_wc'].includes(k)) G.deleteAttribute(k);
    lv[+m[1]]={G,side,minY}; });
  if(!lv[0]) throw new Error('merged skate: no LOD0');
  const wheels=[], W=lv[0].G.attributes._wc, P0=lv[0].G.attributes.position, MK=lv[0].G.attributes.atMask; if(W&&MK){ const map=new Map();
    for(let k=0;k<W.count;k++){ if(MK.getZ(k)<.5) continue; const x=W.getX(k),y=W.getY(k),z=W.getZ(k); if(!x&&!y&&!z) continue; const s=lv[0].side[k]; if(Math.abs(x-RT[s].x)>.05) continue;   // wheel geometry only (B mask), on its own foot
      const key=x.toFixed(4)+','+y.toFixed(4)+','+z.toFixed(4); let e=map.get(key); if(!e) map.set(key,e={s,bb:new THREE.Box3(),n:0}); e.n++; e.bb.expandByPoint(new THREE.Vector3(P0.getX(k),P0.getY(k),P0.getZ(k))); }   // _WC = cluster id only (not trusted as a centre)
    for(const e of map.values()){ if(e.n<50) continue; const sz=e.bb.getSize(new THREE.Vector3()); wheels.push({s:e.s,c:e.bb.getCenter(new THREE.Vector3()),r:Math.max(sz.y,sz.z)/2}); } }
  return {lv,RT,sockets,wheels}; })); }
// ===== Rigger 14:4x: FX attach points (Forge): empty Object3D children srFX_handL/R, srFX_footL/R, srFX_wheelL/R. No meshes, no draws.
// hands on the hand bones (19-bone crews have none -> on the forearm, offset to the wrist by the forearm's own rest length); feet on the foot bones;
// wheel = bottom of the FRONT wheel of each skate (+z = rider forward), measured on the CPU-skinned LOD0 skate verts at rest (already 1.25x scaled)
// and parented to the foot bone (skate is rigid to the foot) -> follows bone and scale. U.fx = {handL:obj,...}; U.fxPos(name) -> world Vector3.
const SR_FX_NAMES=['handL','handR','footL','footR','wheelL','wheelR'];
function srFXAttach(R){ const U=R&&R.userData; if(!U||U.fx) return U&&U.fx; const bones={}; R.traverse(o=>{ if(o.isBone) bones[srBoneKey(o)]=o; }); const pick=(...k)=>{ for(const n of k) if(bones[n]) return bones[n]; return null; };
  const fx={}, rest=U.rest&&U.bones, keep=[]; if(rest) for(const k in U.bones) if(U.rest[k]){ keep.push([U.bones[k],U.bones[k].quaternion.clone()]); U.bones[k].quaternion.copy(U.rest[k]); }
  R.updateMatrixWorld(true);
  const add=(name,bone,pos)=>{ if(!bone) return; const o=new THREE.Object3D(); o.name='srFX_'+name; if(pos) o.position.copy(pos); bone.add(o); fx[name]=o; };
  ['L','R'].forEach((s,i)=>{ const side=i?'right':'left'; const h=pick(side+'hand','hand'+s.toLowerCase()); if(h) add('hand'+s,h);
    else { const fa=pick(side+'forearm','forearm'+s.toLowerCase()); if(fa){ const ch=fa.children.find(c=>c.isBone); add('hand'+s,fa,ch?ch.position.clone():(pick('upperarm'+s.toLowerCase(),side+'arm')?fa.position.clone():null)); } }
    add('foot'+s,pick(side+'foot','foot'+s.toLowerCase())); });
  // front wheel bottom per side
  const FT=[fx.footL&&fx.footL.parent,fx.footR&&fx.footR.parent], fp=FT.map(b=>b?b.getWorldPosition(new THREE.Vector3()):null), inv=new THREE.Matrix4().copy(R.matrixWorld).invert(), pts=[[],[]], v=new THREE.Vector3();
  if(fp[0]&&fp[1]) (U.lod&&U.lod.levels&&U.lod.levels[0]?U.lod.levels[0].object:R).traverse(o=>{ if(!o.isMesh||!/ATSkate|skate/i.test(o.name)) return; if(o.isSkinnedMesh) o.skeleton.update(); const P=o.geometry.attributes.position;
    for(let j=0;j<P.count;j+=2){ v.fromBufferAttribute(P,j); if(o.isSkinnedMesh) o.boneTransform(j,v); v.applyMatrix4(o.matrixWorld); const s=v.distanceToSquared(fp[0])<=v.distanceToSquared(fp[1])?0:1; pts[s].push(v.clone().applyMatrix4(inv)); } });
  pts.forEach((A,s)=>{ if(!A.length||!FT[s]) return; let mnY=1e9,mxZ=-1e9; for(const p of A) mnY=Math.min(mnY,p.y); const band=A.filter(p=>p.y<mnY+.03); for(const p of band) mxZ=Math.max(mxZ,p.z);
    const fr=band.filter(p=>p.z>mxZ-.035), c=new THREE.Vector3(); fr.forEach(p=>c.add(p)); c.multiplyScalar(1/fr.length); c.y=mnY; c.applyMatrix4(R.matrixWorld); add('wheel'+'LR'[s],FT[s],FT[s].worldToLocal(c)); });
  for(const [b,q] of keep) b.quaternion.copy(q); R.updateMatrixWorld(true);
  U.fx=fx; U.fxPos=n=>fx[n]?fx[n].getWorldPosition(new THREE.Vector3()):null; U.fxAll=()=>{ const o={}; for(const n of SR_FX_NAMES) if(fx[n]) o[n]=fx[n].getWorldPosition(new THREE.Vector3()).toArray(); return o; }; return fx; }
window.srFXAttach=srFXAttach;
function srBoneKey(b){ return b.name.replace(/^mixamorig:?/,'').replace(/[._:\s-]/g,'').toLowerCase(); }
function srFootIdx(bones,s){ const want=s?['rightfoot','footr','rfoot']:['leftfoot','footl','lfoot']; return bones.findIndex(b=>want.includes(srBoneKey(b))); }
// rest fit for one rider (call while the rig is in its load/rest pose): foot frames, unit scale, ground, lift, per-side offset
function srSkateRiderFit(root,body,MS){ root.updateMatrixWorld(true); const sk=body.skeleton, B=sk.bones, rinv=new THREE.Matrix4().copy(root.matrixWorld).invert();
  const j=[srFootIdx(B,0),srFootIdx(B,1)]; if(j[0]<0||j[1]<0) throw new Error('rider has no Left/Right foot bones');
  const rl=b=>new THREE.Matrix4().multiplyMatrices(rinv,b.matrixWorld), foot=j.map(i=>new THREE.Vector3().setFromMatrixPosition(rl(B[i])));
  const hi=B.findIndex(b=>/^(hips|pelvis)$/.test(srBoneKey(b))); const u=hi>=0?new THREE.Vector3().setFromMatrixPosition(rl(B[hi])).distanceTo(foot[0])/SR_SHARED_HIPFOOT:1;
  const ground=root.worldToLocal((root.parent||root).localToWorld(new THREE.Vector3())).y, k=u*SR_SKATE_SCALE, L0=MS.lv[0];
  const bot=[0,1].map(s=>foot[s].y+k*(L0.minY[s]-MS.RT[s].y)), lift=ground-bot[0], dyR=bot[0]-bot[1];
  // mesh-space map per side: p_mesh = inv(bindMatrix) * Bbind_j * inv(Brest_rl_j) * p_rl
  const bmi=new THREE.Matrix4().copy(body.bindMatrix).invert(), M=j.map(i=>new THREE.Matrix4().multiplyMatrices(bmi,new THREE.Matrix4().copy(sk.boneInverses[i]).invert()).multiply(rl(B[i]).invert()));
  const shared=Math.abs(u-1)<.02&&Math.abs(foot[0].y-0.21284)<.002&&Math.abs(foot[1].y-0.22337)<.002;
  const liftBind=-bot[0];   // SR_SKATE_LIFT is defined against the bind origin (root y 0). 'lift' is against the parent origin, so loadIkki riders (root at deck IKKI_DECK_REST*s) read lift = SR_SKATE_LIFT - deck (-0.0987 = 0.0532 - 0.1519): not an error
  if(shared&&(Math.abs(liftBind-SR_SKATE_LIFT)>.001||Math.abs(dyR-SR_SKATE_SIDE_DY.R)>.001)) console.warn('crew skate: shared-skeleton rider lift/side differ from SR_SKATE_LIFT/SR_SKATE_SIDE_DY',liftBind,dyR,'(parent-ground lift',lift,')');
  return {j,foot,u,k,ground,lift,dy:[0,dyR],M,shared}; }
function srSkateMergedMesh(MS,F,body,li,mat){ const L=MS.lv[Math.min(li,MS.lv.length-1)], G=L.G.clone(), P=G.attributes.position, N=G.attributes.normal, W=G.attributes._wc, n=P.count, v=new THREE.Vector3();
  const nm=F.M.map(m=>new THREE.Matrix3().setFromMatrix4(m));
  for(let q=0;q<n;q++){ const s=L.side[q], R=MS.RT[s], f=F.foot[s];
    v.fromBufferAttribute(P,q).sub(R).multiplyScalar(F.k).add(f); v.y+=F.dy[s]; v.applyMatrix4(F.M[s]); P.setXYZ(q,v.x,v.y,v.z);
    if(N){ v.fromBufferAttribute(N,q).applyMatrix3(nm[s]).normalize(); N.setXYZ(q,v.x,v.y,v.z); }
    if(W&&(W.getX(q)||W.getY(q)||W.getZ(q))){ v.fromBufferAttribute(W,q).sub(R).multiplyScalar(F.k).add(f); v.y+=F.dy[s]; v.applyMatrix4(F.M[s]); W.setXYZ(q,v.x,v.y,v.z); } }
  const si=new Uint16Array(n*4), sw=new Float32Array(n*4); for(let q=0;q<n;q++){ si[q*4]=F.j[L.side[q]]; sw[q*4]=1; }
  G.setAttribute('skinIndex',new THREE.Uint16BufferAttribute(si,4)); G.setAttribute('skinWeight',new THREE.Float32BufferAttribute(sw,4)); G.computeBoundingBox(); G.computeBoundingSphere();
  const sm=new THREE.SkinnedMesh(G,mat); sm.name='ATSkateV2_LOD'+li; sm.frustumCulled=false; sm.userData.noMerge=true; sm.bind(body.skeleton,body.bindMatrix); return sm; }
// lift the whole rider by dy (root-local units): one Group above the top bone, converted into that parent's space
function srRiderLiftRL(root,skel,dy){ if(!dy) return 0; let t=skel.bones[0]; while(t.parent&&t.parent.isBone) t=t.parent; const P=t.parent; if(!P||P.userData.atLiftGrp) return 0;
  root.updateMatrixWorld(true); const Prl=new THREE.Matrix4().copy(root.matrixWorld).invert().multiply(P.matrixWorld), v=new THREE.Vector3(0,dy,0).applyMatrix3(new THREE.Matrix3().setFromMatrix4(Prl).invert());
  const G=new THREE.Group(); G.name='SR_AT_Lift'; G.position.copy(v); P.add(G); for(const c of P.children.filter(c=>c.isBone)) G.add(c); P.userData.atLiftGrp=G; G.updateMatrixWorld(true); return dy; }
function srSkateSockets(MS,F){ const o={}; for(const s of MS.sockets){ const p=s.off.clone().multiplyScalar(F.k).add(F.foot[s.s]); p.y+=F.dy[s.s]+F.lift; o[s.name]=p; } return o; }   // root-local rest positions
// attach to a list of [levelGroup, bodyMesh] pairs; returns {mat,fit}
async function srSkateAttach(root,pairs,lo,matIn,liftMode){ const S=await srSkateSource(), MS=await srSkateMergedSrc(); const mat=matIn||srSkateMaterial(S.mat,lo);
  const F=srSkateRiderFit(root,pairs[0][1],MS); pairs.forEach(([grp,body],li)=>grp.add(srSkateMergedMesh(MS,F,body,li,mat)));
  if(liftMode==='root'){ root.position.y+=F.lift*root.scale.y; root.updateMatrixWorld(true); }   // loadIkki poser pins the feet to the rest deck relative to the root each frame -> move the root
  else srRiderLiftRL(root,pairs[0][1].skeleton,F.lift); const U=root.userData; U.atSkate=mat; U.atSkateFit={u:+F.u.toFixed(4),lift:+F.lift.toFixed(4),dyR:+F.dy[1].toFixed(4),ground:+F.ground.toFixed(4),shared:F.shared}; U.atSockets=srSkateSockets(MS,F); return {mat,fit:F}; }
// API kept: srSkateMerged(body,lo) on a body already in a rider root
async function srSkateMerged(body,lo){ let root=body; while(root.parent&&!root.parent.isScene) root=root.parent; const r=await srSkateAttach(root,[[body.parent,body]],lo); const meshes=[]; body.parent.traverse(o=>{ if(/^ATSkateV2_LOD/.test(o.name)) meshes.push(o); }); return {meshes,mat:r.mat,sockets:root.userData.atSockets,lift:r.fit.lift}; }
// baked skate on loadIkki bodies (sid 11-13 in COLOR_0.r*16): discard in the body's own material; no-op when no such verts (Anika, Caali v2)
// Caali G v2 / Anika ship without the wardrobe _slot/_bm attributes. patch_wardrobe's body shader declares them; an unbound attribute reads a stale/undefined
// generic value -> random vHide discards. Give such meshes zero-filled u8 attributes (_slot 0 = not a swappable piece, _bm 0 = no cover bits) -> vHide=0, atlas colours untouched.
function srWardrobeAttrGuard(root){ const miss=[]; root.traverse(m=>{ if(!m.isMesh||!m.geometry||!m.geometry.attributes.position) return; const G=m.geometry, n=G.attributes.position.count;
  for(const k of ['_slot','_bm']) if(!G.attributes[k]){ G.setAttribute(k,new THREE.BufferAttribute(new Uint8Array(n),1)); miss.push(m.name+'.'+k); } });
  if(miss.length) console.info('[rigger] wardrobe attrs missing -> zero guard (no piece hide / skin cover on this rider):',miss.join(',')); root.userData.atNoWardrobeAttrs=miss; }
function srSidSet(m){ for(const k of ['color','color_1']){ const c=m.geometry.attributes[k]; if(!c) continue; const ar=c.isInterleavedBufferAttribute?c.data.array:c.array, dv=c.normalized&&ar instanceof Uint8Array?255:c.normalized&&ar instanceof Uint16Array?65535:1;
    for(let i=0;i<c.count;i++){ const sid=Math.floor(c.getX(i)/dv*16+.5); if(sid>=11&&sid<=13) return k; } } return null; }   // COLOR_0 -> 'color', COLOR_1 -> 'color_1' (r128 GLTFLoader names)
function srHasBakedSkate(m){ const k=srSidSet(m); m.userData.atSidSet=k; return !!k; }
// LOD1/2 baked skate (rule b): tint sid 11-13 toward the v2 shell so the ~9 m LOD switch doesn't pop. Shares the v2 skate's crew uniforms (no new textures/draws).
// Shell = v2 1k albedo dark-shell median #122134 (sRGB) lit by crew primary; frame = same x crew secondary; wheels = uCrewWheel rim + v2 gold hub #CCB01A (albedo gold median) 35%.
const SR_SKATE_TINT={shell:0x122134, gold:0xccb01a, hub:.35, mode:1};   // mode 0 crew-lit, 1 flat, 2 crew clamped (?attint=crew|flat|clamp)
function srTintBakedSkate(root,skMat){ const C=skMat&&skMat.userData&&skMat.userData.crew; if(!C||/notint=1/.test(location.search)) return;
  const U={uAtShell:{value:new THREE.Color(SR_SKATE_TINT.shell)},uAtGold:{value:new THREE.Color(SR_SKATE_TINT.gold)},uAtP:C.uCrewPrimary,uAtS:C.uCrewSecondary,uAtW:C.uCrewWheel,uAtEmi:{value:/attintemi=1/.test(location.search)?1:.1},uAtMode:{value:({crew:0,flat:1,clamp:2})[(location.search.match(/attint=(\w+)/)||[])[1]]??SR_SKATE_TINT.mode}};
  root.traverse(m=>{ if(!m.isSkinnedMesh||!m.material||m.material.userData.atTint) return; const mt=m.material, ob=mt.onBeforeCompile, ck=mt.customProgramCacheKey; mt.userData.atTint=U;
    mt.onBeforeCompile=function(s,r){ if(ob) ob.call(this,s,r); if(!/float atShellM/.test(s.fragmentShader)) return; Object.assign(s.uniforms,this.userData.atTint);
      s.fragmentShader=s.fragmentShader.replace('#include <common>','#include <common>\n uniform vec3 uAtShell, uAtGold, uAtP, uAtS, uAtW; uniform float uAtMode; uniform float uAtEmi;').replace('#include <roughnessmap_fragment>',
        'if(atSk>.5&&sid<13.5){ float atL=clamp(dot(atT,vec3(.3,.59,.11))*2.2,.5,1.4); vec3 atC=sid==13.?uAtS:uAtP; vec3 sh=uAtMode<.5?uAtShell*(.6+.8*atC):uAtMode<1.5?uAtShell:uAtShell*(.8+.4*min(atC,vec3(.35)));\n diffuseColor.rgb=sid==12.?mix(uAtW,uAtGold,'+SR_SKATE_TINT.hub.toFixed(2)+')*atL:mix(sh*atL,diffuseColor.rgb,atGlowM); }   // rigger LOD tint\n#include <roughnessmap_fragment>').replace('#include <lights_fragment_begin>','#include <lights_fragment_begin>\n if(atSk>.5&&sid<13.5) totalEmissiveRadiance*=uAtEmi;   // rigger LOD tint: baked neon glow down (v2 has no cyan emissive)'); };
    mt.customProgramCacheKey=function(){ return (ck?ck.call(this):'')+'|attint'; }; mt.needsUpdate=true; }); }
function srHideBakedSkate(root){ root.traverse(m=>{ if(!m.isSkinnedMesh||!m.material||m.material.userData.atHide||!m.geometry.attributes.color) return; const mt=m.material, ob=mt.onBeforeCompile, ck=mt.customProgramCacheKey;
  mt.userData.atHide={value:1}; mt.onBeforeCompile=function(s,r){ if(ob) ob.call(this,s,r); s.uniforms.uAtHideBaked=this.userData.atHide; const c1=this.userData.atSidSet==='color_1'; if(!c1&&!/varying vec3 vFlag/.test(s.fragmentShader)) return;
    if(c1) s.vertexShader=s.vertexShader.replace('#include <common>','#include <common>\n attribute vec3 color_1; varying float vAtSid1;').replace('#include <begin_vertex>','#include <begin_vertex>\n vAtSid1=color_1.r;');
    s.fragmentShader=(c1?s.fragmentShader.replace('#include <common>','#include <common>\n varying float vAtSid1;'):s.fragmentShader).replace('#include <common>','#include <common>\n #define ATSID '+(c1?'vAtSid1':'vFlag.r'));
    s.fragmentShader=s.fragmentShader.replace('#include <common>','#include <common>\n uniform float uAtHideBaked;').replace('#include <clipping_planes_fragment>','if(uAtHideBaked>.5&&abs(floor(ATSID*16.+.5)-12.)<1.5) discard;   // v2 skate replaces the baked one\n#include <clipping_planes_fragment>'); };
  mt.userData.atSidSet=m.userData.atSidSet||srSidSet(m); mt.customProgramCacheKey=function(){ return (ck?ck.call(this):'')+'|athide'+(this.userData.atSidSet==='color_1'?'1':''); }; mt.needsUpdate=true; }); }
// loadIkki riders: the poser pitches the feet (idle crouch) -> a wheel dips ~13 mm. Each frame after the poser: lowest wheel bottom
// (wheel centre on its foot bone - radius) vs the rider's own ground (parent origin); root y corrected, clamped to +-SR_SKATE_CONTACT_MAX.
const SR_SKATE_CONTACT_MAX=0.03;
function srSkateContacts(root,body,MS,F){ root.updateMatrixWorld(true); const rinv=new THREE.Matrix4().copy(root.matrixWorld).invert(), B=body.skeleton.bones;
  return MS.wheels.map(w=>{ const b=B[F.j[w.s]], p=w.c.clone().sub(MS.RT[w.s]).multiplyScalar(F.k).add(F.foot[w.s]); p.y+=F.dy[w.s];
    const q=p.applyMatrix4(new THREE.Matrix4().multiplyMatrices(rinv,b.matrixWorld).invert()); return {b,q,r:w.r*F.k}; }); }
// grounded = poser state idle/stride/tuck (ikki_skate stateName) and, for the player, no wall ride / air / grind / airtime
function srSkateGrounded(root){ const U=root.userData, st=typeof U.stateName==='function'?U.stateName():U.stateName; if(st&&!/^(idle|stride|tuck|kick)$/.test(st)) return false;
  if(typeof RIDERS!=='undefined'&&RIDERS.player===root){ if(typeof WALL!=='undefined'&&(WALL.air||WALL.on)) return false; if(typeof GRIND!=='undefined'&&GRIND.on) return false; if(window.RIDE_GROUND&&RIDE_GROUND.airT>0) return false; }
  return true; }
function srSkateGround(root){ const U=root.userData, C=U.atContact, P=root.parent; if(!C||!C.length||!P) return; const v=srSkateGround.v||(srSkateGround.v=new THREE.Vector3());
  const sc=new THREE.Vector3().setFromMatrixScale(root.matrixWorld).y; let mn=Infinity; for(const c of C){ v.copy(c.q).applyMatrix4(c.b.matrixWorld); mn=Math.min(mn,v.y-c.r*sc); }
  const now=performance.now(), dt=Math.min(.1,Math.max(0,(now-(U.atT||now))/1000)); U.atT=now;
  const gy=P.matrixWorld.elements[13], ps=new THREE.Vector3().setFromMatrixScale(P.matrixWorld).y||1;
  const o=srSkateGrounded(root)?THREE.MathUtils.clamp((U.atCorr||0)-(mn-gy)/ps,-SR_SKATE_CONTACT_MAX,SR_SKATE_CONTACT_MAX):(U.atCorr||0)*Math.exp(-dt/.05);   // airborne/trick: ease to 0 (~0.15 s to 95%), no dip
  if(Math.abs(o-(U.atCorr||0))<1e-5) return; root.position.y=U.atBaseY+o; U.atCorr=o; root.updateMatrixWorld(true); }
// player / Ikki: wrap loadIkki (riders call it at runtime, after this script ran)
if(typeof loadIkki==='function'&&!window.__srIkkiWrap){ window.__srIkkiWrap=true; const _loadIkki=loadIkki;
  loadIkki=async function(parent,refH,fresh,opt){ const r=await _loadIkki.apply(this,arguments); if(!SR_SKATE.on()||SR_SKATE.mode()==='off') return r;
    try{ const lod=r.userData.lod, pairs=[]; (lod&&lod.levels||[]).forEach(L=>{ let b=null; L.object.traverse(o=>{ if(o.isSkinnedMesh&&!b&&!/^ATSkate/.test(o.name)) b=o; }); if(b) pairs.push([L.object,b]); });
      if(!pairs.length) throw new Error('no LOD bodies');
      // Optimizer ruling (b): baked-skate riders -> v2 on LOD0 only (own material clone with the sid 11-13 discard); LOD1/2 keep the baked skate (1 draw).
      // Stripped riders (no sid 11-13 verts: Anika, Caali v2) -> v2 on every LOD.
      const baked=srHasBakedSkate(pairs[0][1]); if(baked){ const b0=pairs[0][1], m0=b0.material.clone(); m0.onBeforeCompile=b0.material.onBeforeCompile; m0.customProgramCacheKey=b0.material.customProgramCacheKey; m0.userData={}; b0.material=m0; pairs.length=1; }
      r.userData.atSkateLODs=baked?'LOD0 (baked kept on LOD1/2)':'all';
      const lo=Object.assign({paint:0x0b0b0d,frame:0x2b2b2b,wheel:0x1c1c20,glow:0xffd700},SR_AT_LOADOUT[(opt&&opt.crew)||'codee']||{});
      srWardrobeAttrGuard(r); const {mat,fit}=await srSkateAttach(r,pairs,lo,null,'root'); srHideBakedSkate(baked?pairs[0][1]:r); if(baked&&r.userData.lod) r.userData.lod.levels.slice(1).forEach(l=>srTintBakedSkate(l.object,mat)); const U=r.userData, prev=U.setLoadout;
      U.atContact=srSkateContacts(r,pairs[0][1],await srSkateMergedSrc(),fit); try{ srFXAttach(r); }catch(e){ console.warn('srFX attach',e); } U.atBaseY=r.position.y; U.atCorr=0;
      for(const k of ['drive','update']) if(typeof U[k]==='function'){ const f=U[k]; U[k]=function(){ const o=f.apply(this,arguments); srSkateGround(r); return o; }; }
      U.setLoadout=function(o){ if(prev) prev.call(this,o); const C=mat.userData.crew; if(o.paint!==undefined) C.uCrewPrimary.value.set(o.paint); if(o.frame!==undefined) C.uCrewSecondary.value.set(o.frame); if(o.wheel!==undefined) C.uCrewWheel.value.set(o.wheel); if(o.glow!==undefined) C.uCrewGlow.value.set(o.glow); };
    }catch(e){ console.warn('v2 skate on loadIkki rider failed, keeping the baked skate',e); }
    return r; }; }
// bespoke back patches for crews with reference art (base-refs/): origin = cell centre, radius ~120 px. Original shapes, not traced.
const JACKET_LOGOS={
  karasu(x,css){ // crow head in a broken brush circle
    x.fillStyle="#08080a"; x.beginPath(); x.arc(0,0,122,0,7); x.fill();
    x.strokeStyle=css; x.lineCap="round"; for(let k=0;k<5;k++){ x.lineWidth=16-k*2.5; x.globalAlpha=1-k*.12; x.beginPath(); x.arc(k*1.5,-k,100-k*3,-1.2+k*.08,Math.PI*1.55-k*.15); x.stroke(); } x.globalAlpha=1;
    x.fillStyle=css; x.beginPath(); x.moveTo(-70,60); x.quadraticCurveTo(-78,-10,-40,-50); x.quadraticCurveTo(0,-82,38,-52); x.lineTo(92,-30); x.lineTo(40,-18); x.quadraticCurveTo(30,20,48,58);
    x.lineTo(20,40); x.lineTo(10,66); x.lineTo(-12,42); x.lineTo(-30,70); x.lineTo(-44,46); x.closePath(); x.fill(); // head + beak + ruffled neck
    x.fillStyle="#08080a"; x.beginPath(); x.moveTo(38,-52); x.lineTo(92,-30); x.lineTo(40,-34); x.fill(); x.beginPath(); x.arc(8,-38,9,0,7); x.fill(); x.fillStyle=css; x.beginPath(); x.arc(10,-40,3,0,7); x.fill(); },
  forest(x,css){ // tree whose canopy is a sleeping face in profile
    x.fillStyle="#0d2418"; x.beginPath(); x.arc(0,0,122,0,7); x.fill(); x.strokeStyle=css; x.lineWidth=6; x.beginPath(); x.arc(0,0,112,0,7); x.stroke();
    x.fillStyle=css; for(const [a,b,r] of [[-50,-40,38],[-10,-62,44],[38,-50,40],[60,-12,32],[-62,0,30],[22,-14,36],[-24,-18,36]]){ x.beginPath(); x.arc(a,b,r,0,7); x.fill(); }
    x.beginPath(); x.moveTo(-12,0); x.quadraticCurveTo(-6,50,-30,92); x.lineTo(34,92); x.quadraticCurveTo(10,50,14,0); x.fill(); // trunk
    for(const sd of [-1,1]){ x.beginPath(); x.moveTo(0,90); x.quadraticCurveTo(sd*30,96,sd*56,104); x.lineTo(sd*20,98); x.fill(); }
    x.strokeStyle="#0d2418"; x.lineWidth=5; x.lineCap="round"; x.beginPath(); x.moveTo(14,-60); x.quadraticCurveTo(30,-50,24,-36); x.lineTo(34,-26); x.lineTo(24,-22); x.quadraticCurveTo(30,-10,20,-2); x.stroke(); // face profile
    x.beginPath(); x.arc(4,-40,8,.2,Math.PI-.2); x.stroke(); }, // closed eye
  behemoth(x,css){ // horned demon skull
    x.fillStyle="#140c06"; x.beginPath(); x.arc(0,0,122,0,7); x.fill(); x.fillStyle=css;
    for(const sd of [-1,1]){ x.beginPath(); x.moveTo(sd*40,-46); x.quadraticCurveTo(sd*112,-60,sd*96,-118); x.quadraticCurveTo(sd*84,-74,sd*28,-70); x.fill(); }
    x.beginPath(); x.moveTo(-58,-56); x.quadraticCurveTo(0,-90,58,-56); x.lineTo(66,8); x.lineTo(40,40); x.lineTo(34,92); x.lineTo(-34,92); x.lineTo(-40,40); x.lineTo(-66,8); x.closePath(); x.fill();
    x.fillStyle="#140c06"; for(const sd of [-1,1]){ x.beginPath(); x.moveTo(sd*12,-8); x.lineTo(sd*52,-26); x.lineTo(sd*44,10); x.closePath(); x.fill(); }
    x.beginPath(); x.moveTo(0,18); x.lineTo(-10,40); x.lineTo(10,40); x.fill(); for(let k=-2;k<=2;k++) x.fillRect(k*14-4,60,8,30); },
  static(x,css){ // spread wings under a halo
    x.fillStyle="#0c0616"; x.beginPath(); x.arc(0,0,122,0,7); x.fill(); x.fillStyle=css; x.strokeStyle="#7fe9ff"; x.lineCap="round";
    for(const sd of [-1,1]){ x.save(); x.scale(sd,1); for(let k=0;k<4;k++){ x.beginPath(); x.moveTo(8,30); x.quadraticCurveTo(40+k*6,-40+k*22,104-k*8,-34+k*26); x.quadraticCurveTo(60,8+k*10,10,44); x.fill(); } x.restore(); }
    x.lineWidth=9; x.beginPath(); x.ellipse(0,-70,42,12,0,0,7); x.stroke(); x.fillStyle="#fff"; x.beginPath(); x.arc(0,40,9,0,7); x.fill(); }
};
function jacketAtlas(){ if(JACKET.atlas) return JACKET.atlas;
  const cv=document.createElement("canvas"); cv.width=1024; cv.height=512; const x=cv.getContext("2d");
  JACKET_ORDER.forEach((id,i)=>{ const cx=(i%4)*256+128, cy=(i>>2)*256+128;
    if(JACKET_LOGOS[id]){ x.save(); x.translate(cx,cy); JACKET_LOGOS[id](x,crewBrand(id).css); x.restore(); }
    else { const e=emblemTex(id,crewBrand(id).css).image; x.drawImage(e,cx-124,cy-124,248,248); } });
  const t=new THREE.CanvasTexture(cv); t.anisotropy=4; JACKET.atlas=t;
  JACKET.mat=new THREE.MeshBasicMaterial({map:t,alphaTest:.5,side:THREE.DoubleSide}); JACKET.mat.toneMapped=false; return t; }
function jacketDecalGeo(id){ if(JACKET.geo[id]) return JACKET.geo[id]; const i=Math.max(0,JACKET_ORDER.indexOf(id)), u0=(i%4)/4, v1=1-(i>>2)/2, v0=v1-.5;
  const g=new THREE.PlaneGeometry(1,1), uv=g.attributes.uv; for(let k=0;k<uv.count;k++) uv.setXY(k,u0+uv.getX(k)*.25,v0+uv.getY(k)*.5); uv.needsUpdate=true; return JACKET.geo[id]=g; }
function jacketDecal(id,size){ jacketAtlas(); const m=new THREE.Mesh(jacketDecalGeo(id),JACKET.mat); m.scale.setScalar(size); m.userData.noMerge=true; m.name="CrewPatch_"+id; m.renderOrder=2; return m; }
const JACKET_FIT={ back:.15, up:.03, size:.24 }; // tuned against crew GLBs (metres, before rider scale); ?patch=back,up,size overrides
{ const q=new URLSearchParams(location.search).get("patch"); if(q){ const [a,b,c]=q.split(",").map(Number); Object.assign(JACKET_FIT,{back:a,up:b,size:c}); } }
function crewJacket(r,crewName,fp){ if(typeof srDetailInstall==='function') srDetailInstall(r); const cr=CREWS.find(c=>c.crew===crewName); if(!cr||!r||!r.userData.setColor) return; const id=cr.garage, B=crewBrand(id), U=r.userData;
  U.setColor("jacket",B.main); U.setColor("gold",B.trim); if(B.glow!==undefined) U.setColor("wheelGlow",B.glow); U.brand=Object.assign({id},B); crewJacketPanels(r,B); if(fp) return;
  const bone=U.bones.chest||U.bones.spine; if(!bone) return; r.updateMatrixWorld(true);
  // place the patch in rider space (behind the chest, facing backwards), then re-express in the chest bone's space so it follows the pose
  const bb=new THREE.Box3().setFromObject(r), ws=new THREE.Vector3(); r.getWorldScale(ws); const bp=new THREE.Vector3(); bone.getWorldPosition(bp);
  const inv=new THREE.Matrix4().copy(r.matrixWorld).invert(), lp=bp.clone().applyMatrix4(inv); const back=U.backSign||-1; // rider faces +Z
  const d=jacketDecal(id,1); const world=new THREE.Object3D(); r.add(world); world.position.set(0,lp.y+JACKET_FIT.up,lp.z+back*JACKET_FIT.back); world.rotation.y=back<0?Math.PI:0; world.updateMatrixWorld(true);
  const m=new THREE.Matrix4().copy(bone.matrixWorld).invert().multiply(world.matrixWorld); r.remove(world); bone.add(d); m.decompose(d.position,d.quaternion,d.scale); d.scale.multiplyScalar(JACKET_FIT.size);
  U.patch=d; }
// Caali G back patch (gold phoenix + lightning, black/gold, from caali-g-turnaround.jpg; gen_caali_g_emblem.py). Caali G only; other crews keep the JACKET atlas.
const SR_CG_PATCH={url:CHAR_BASE+'shared/crew-logos/caali-g-patch-noshadow.png', mat:null};
function srCaaliGPatch(){ if(!SR_CG_PATCH.mat){ const t=new THREE.TextureLoader().load(SR_CG_PATCH.url); t.encoding=THREE.sRGBEncoding; t.anisotropy=4;
    SR_CG_PATCH.mat=new THREE.MeshBasicMaterial({map:t,alphaTest:.5,side:THREE.DoubleSide}); SR_CG_PATCH.mat.toneMapped=false; }
  const m=new THREE.Mesh(new THREE.PlaneGeometry(1,1),SR_CG_PATCH.mat); m.userData.noMerge=true; m.name="CrewPatch_caali-g"; m.renderOrder=2; return m; }
// ===== per-rider detail toggle (for Rydah Optimizer's sorter in riders.js): root.userData.setDetail('full'|'lite'), alias root.setDetail =====
// full = current passes. lite = body + skate only: hides the inverted-hull outline, the separate glow/rim mesh (rider-glow-r128), VR glow sprites,
// the back-patch decal and the Ikki-poser ground contact. The skate's own emissive glow (uGlowStrength) stays on.
// Visibility flips only: no material changes, no recompiles, no new programs. Idempotent; default 'full'.
function srDetailParts(root){ const out=[]; root.traverse(o=>{ if(o===root) return; const m=o.material, k=m&&m.customProgramCacheKey&&m.customProgramCacheKey();
    const outline=o.isMesh&&m&&m.isShaderMaterial&&m.side===THREE.BackSide&&m.uniforms&&m.uniforms.uThick, glow=k==='rider-glow-r128', patch=/^CrewPatch_/.test(o.name||'');
    if(outline||glow||patch||o.isSprite) out.push(o); }); return out; }
function srSetDetail(root,mode){ const U=root.userData; mode=mode==='lite'?'lite':'full'; if(U.detail===mode&&U._detailParts) return mode;
  if(mode==='lite'){ U._detailParts=srDetailParts(root); for(const o of U._detailParts) o.visible=false; }
  else { for(const o of (U._detailParts||[])) o.visible=true; U._detailParts=U._detailParts||[]; }
  if(U.ground) U.ground.visible=mode==='full';   // Ikki-poser contact shadow; its update() also honours U.detail
  U.detail=mode; return mode; }
function srDetailInstall(root){ const U=root.userData; if(U.setDetail) return; U.detail=U.detail||'full'; U.setDetail=m=>srSetDetail(root,m); root.setDetail=U.setDetail; U.getDetail=()=>U.detail; }
// ===== crew NPC glow parts folded into the body draw (Optimizer: no separate glow mesh on NPCs, both tiers). ?npcglow=mesh = old separate glow pass.
// The toon glow parts are NOT only wheels: per crew 72-288 LOD0 glow verts sit above the skates (eyes/visor/halo/piping, slots wheelGlow+glow2, up to 1.96 m).
// So instead of deleting them they join the toon body (same draw) with uSlotEmi = SR_GLOW_EMI on those two slots (unlit glow ~ slot colour x 1.3 like rGlowMat);
// the toon wheel-glow tris that sat on the retired skates (all verts below the old skate top 0.419 + .02) are cut. Lost vs the old pass: the boost pulse on body glow.
const SR_GLOW_EMI=1.3, SR_GLOW_CUT_Y=.439;
function srGlowToBody(root,o){ if(new URLSearchParams(location.search).get('npcglow')==='mesh'||!o.geometry||!o.geometry.attributes.position) return false;
  const g=o.geometry, p=g.attributes.position, ix=g.index?g.index.array:null, keep=[]; const n=ix?ix.length:p.count;
  if(typeof SR_SKATE!=='undefined'&&SR_SKATE.on()) for(let i=0;i<n;i+=3){ const a=ix?ix[i]:i, b=ix?ix[i+1]:i+1, c=ix?ix[i+2]:i+2; if(Math.max(p.getY(a),p.getY(b),p.getY(c))>SR_GLOW_CUT_Y) keep.push(a,b,c); }
  else for(let i=0;i<n;i++) keep.push(ix?ix[i]:i);
  g.setIndex(keep); root.userData._glowMerged=true; return true; }
// ===== Rigger 10:5x: crew 19-bone path (rPose) planted-wheel contact =====
// rPose (base html) has no foot pin: the carve swings thigh/shin, so the lower skate lifts or sinks (npc6 -7.3..+16 mm). After rPose:
// (1) plant: level the planted foot back to its rest sole axis (weight 1 at <=1 cm above the lower foot, 0 at >=4 cm), capped at 50 deg (RIDER_JOINT_LIMITS.Foot plantar)
//     and slewed at 720 deg/s (10 deg/frame @72 fps), same as ikki_skate.js plant();
// (2) contact nudge: root y so the lower foot joint sits at its rest height above the holder (skate is rigid to the foot -> wheel on the asphalt),
//     clamped to SR_SKATE_CONTACT_MAX (30 mm), eased (tau 50 ms). Crews are always grounded. ?noplant=1 disables both.
const _cpY=new THREE.Vector3(0,1,0), _cpA=new THREE.Vector3(), _cpQ=new THREE.Quaternion(), _cpH=new THREE.Quaternion(), _cpP=new THREE.Quaternion(), _cpD=new THREE.Quaternion();
function srCrewPlant(R){ const U=R.userData, B=U&&U.bones, H=R.parent; if(!B||U.ikki||!H||/noplant=1/.test(location.search)) return; const F=[B.footL,B.footR]; if(!F[0]||!F[1]) return;
  const hy=b=>{ b.getWorldPosition(_cpA); return H.worldToLocal(_cpA).y; };
  if(!U.cp){ const S=U.rest, keep={}; for(const k in B) if(S[k]){ keep[k]=B[k].quaternion.clone(); B[k].quaternion.copy(S[k]); } const y0=R.position.y; H.updateWorldMatrix(true,true); H.getWorldQuaternion(_cpH).invert();   // full chain refresh: the holder's matrixWorld can be a frame stale (y 0 before wallatk/spawn y) -> +1 cm in the contact reference
    // target = rest foot-joint height above the skate's lowest wheel (rest pose, CPU-skinned LOD0 skate verts): lower foot joint at that height -> wheel on the holder ground (y 0)
    let mn=1e9; const v=new THREE.Vector3(); (U.lod&&U.lod.levels[0]?U.lod.levels[0].object:R).traverse(o=>{ if(!o.isMesh||!/ATSkate|skate/i.test(o.name)) return; if(o.isSkinnedMesh) o.skeleton.update();   /* boneTransform reads boneMatrices: refresh for the rest pose */ const P=o.geometry.attributes.position; for(let j=0;j<P.count;j+=3){ v.fromBufferAttribute(P,j); if(o.isSkinnedMesh) o.boneTransform(j,v); v.applyMatrix4(o.matrixWorld); H.worldToLocal(v); if(v.y<mn) mn=v.y; } });
    const jl=Math.min(hy(F[0]),hy(F[1]));
    U.cp={ y0, up:F.map(f=>_cpY.clone().applyQuaternion(f.getWorldQuaternion(new THREE.Quaternion()).premultiply(_cpH).invert())), low:mn<1e8?jl-mn:jl, a:[0,0], corr:0, t:performance.now() };
    for(const k in keep) B[k].quaternion.copy(keep[k]); }
  const C=U.cp, now=performance.now(), dt=Math.min(.1,Math.max(1e-4,(now-C.t)/1000)); C.t=now; R.position.y=C.y0+(U.crDrop||0); R.updateMatrixWorld(true); H.getWorldQuaternion(_cpH).invert();   // crDrop: combat knockdown root drop (srCrewCombatPose), 0 otherwise
  const ys=F.map(hy), lo=Math.min(ys[0],ys[1]), mx=720*Math.PI/180*dt, cap=50*Math.PI/180;
  F.forEach((f,s)=>{ const w=1-THREE.MathUtils.smoothstep(ys[s]-lo,.01,.04); f.getWorldQuaternion(_cpQ).premultiply(_cpH); _cpA.copy(C.up[s]).applyQuaternion(_cpQ).normalize();
    _cpD.setFromUnitVectors(_cpA,_cpY); const ang=2*Math.acos(Math.min(1,Math.abs(_cpD.w))), want=Math.min(ang,cap)*w; C.a[s]+=THREE.MathUtils.clamp(want-C.a[s],-mx,mx);
    if(ang<1e-5||C.a[s]<1e-5) return; _cpD.copy(_cpP.identity().slerp(_cpD,C.a[s]/ang)); f.parent.getWorldQuaternion(_cpP).premultiply(_cpH); f.quaternion.copy(_cpP.invert().multiply(_cpD.multiply(_cpQ))); });
  R.updateMatrixWorld(true); const lo2=Math.min(hy(F[0]),hy(F[1])), M=typeof SR_SKATE_CONTACT_MAX!=='undefined'?SR_SKATE_CONTACT_MAX:.03, pin=THREE.MathUtils.clamp(C.low-lo2,-.15,.15);   // holder-local: the holder itself sits on WORLD_GROUND (riders spawn y via patch_crew_quest, and wallatk when on), so ground = holder y 0. A ground term here double-counts when wallatk moves the holder after rPose.
  // (3) pose pin, like the ikki_skate poser's hips pin: rPose bends both knees in the carve without dropping the hips (both feet rise up to ~45 mm),
  // so the lower foot is pinned to its contact height directly (pose step, |pin|<=15 cm sanity). The eased nudge is then only the residual, still clamped to SR_SKATE_CONTACT_MAX.
  C.corr+=(0-C.corr)*(1-Math.exp(-dt/.05)); C.corr=THREE.MathUtils.clamp(C.corr,-M,M); R.position.y=C.y0+(U.crDrop||0)+pin+C.corr;
  // one-time calibration on the 5th posed frame: measure the real lowest wheel (fresh skeleton, CPU skin) in this same frame and fold the residual into the
  // contact reference. The rest-pose scan can be ~1 cm off when the holder/skeleton matrices at load were a frame stale (npc6 +10 / npc3 -10 mm).
  if(!C.cal&&(C.n=(C.n||0)+1)>=5){ C.cal=1; R.updateMatrixWorld(true); let mn=1e9; const v=new THREE.Vector3(); (U.lod&&U.lod.levels[0]?U.lod.levels[0].object:R).traverse(o=>{ if(!o.isMesh||!/ATSkate|skate/i.test(o.name)) return; if(o.isSkinnedMesh) o.skeleton.update(); const P=o.geometry.attributes.position; for(let j=0;j<P.count;j+=2){ v.fromBufferAttribute(P,j); if(o.isSkinnedMesh) o.boneTransform(j,v); v.applyMatrix4(o.matrixWorld); H.worldToLocal(v); if(v.y<mn) mn=v.y; } });
    if(mn<1e8&&Math.abs(mn)<.05){ C.low-=mn; R.position.y-=mn; C.calMm=+(mn*1000).toFixed(1); } } }
// ===== Rigger 13:4x: crew 19-bone path (rPose) combat reacts, FLAG-GATED like the loadIkki poser (window.SR_COMBAT_POSES / ?combatposes=1) =====
// Additive Euler (radians, rig-local axes exactly as rPose uses them: spine/chest/head x+ = forward, thigh x- = hip flex, shin x+ = knee, forearm x- = elbow)
// applied AFTER rPose and BEFORE srCrewPlant (feet-on-ground unchanged). Authored for a hit from the front; hit from behind flips spine/chest/head pitch,
// the lateral lean follows dir. LOD (Systems): full < 12 m, key poses only 12-30 m (snap to the last key, no blend), none > 30 m or offscreen (clock still
// runs, events still fire). No meshes, no draws. API on crew riders: setState('react',{kind,dir}), combatHitStop(ms), combatQuery(), combatState(), onCombat(type,fn).
const SR_CREW_REACT=(()=>{ const Z={spine:[0,0,0],chest:[0,0,0],head:[0,0,0],upperarmL:[0,0,0],upperarmR:[0,0,0],forearmL:[0,0,0],forearmR:[0,0,0]};
  const LT={spine:[-.16,0,.12],chest:[-.1,0,.08],head:[-.3,0,.12],upperarmL:[-.45,0,0],upperarmR:[-.45,0,0],forearmL:[-.7,0,0],forearmR:[-.7,0,0]};
  const KZ=Object.assign({},Z,{thighL:[0,0,0],thighR:[0,0,0],shinL:[0,0,0],shinR:[0,0,0]}),
        KC={spine:[.45,0,0],chest:[.4,0,0],head:[.3,0,0],upperarmL:[-1.2,0,0],upperarmR:[-1.2,0,0],forearmL:[-1.6,0,0],forearmR:[-1.6,0,0],thighL:[-1.5,0,0],thighR:[-1.5,0,0],shinL:[1.9,0,0],shinR:[1.9,0,0]},
        KF={spine:[-.16,0,0],chest:[-.15,0,0],head:[-.3,0,0],upperarmL:[-.6,0,.3],upperarmR:[-.6,0,-.3],forearmL:[-.4,0,0],forearmR:[-.4,0,0],thighL:[-.5,0,0],thighR:[-.9,0,0],shinL:[.6,0,0],shinR:[1.0,0,0]},
        KU={spine:[.45,0,0],chest:[.3,0,0],head:[-.1,0,0],upperarmL:[-.5,0,0],upperarmR:[-.5,0,0],forearmL:[-.9,0,0],forearmR:[-.9,0,0],thighL:[-1.6,0,0],thighR:[-1.3,0,0],shinL:[2.0,0,0],shinR:[1.8,0,0]};
  return { react_light:{A:2,X:2,R:10,dirFlip:true,keys:[[0,LT],[4,LT],[14,Z]]}, knockdown:{A:6,X:40,R:24,dirFlip:false,keys:[[0,KF],[6,KC],[46,KC],[58,KU],[70,KZ]]} }; })();
const SR_CREW_REACT_KIND={ light:'react_light', heavy:'react_light', knockdown:'knockdown' };   // heavy -> light on crews until a 19-bone heavy is authored
const _crQ=new THREE.Quaternion(), _crE=new THREE.Euler(), _crV=new THREE.Vector3(), _crI=new THREE.Quaternion();
function srCrewCombatOn(){ return typeof riderCombatOn==='function'?riderCombatOn():!!(window.SR_COMBAT_POSES||/[?&]combatposes=1(&|$)/.test(location.search)); }
function srCrewCombatInstall(R){ const U=R&&R.userData; if(!U||U.ikki||!U.bones||U.crCombat) return; try{ srFXAttach(R); }catch(e){ console.warn('srFX attach (crew)',e); } const CB={onHitFrame:[],onCancelOpen:[],onCancelClose:[],onRecover:[]}, prevSet=U.setState;
  const C=U.crCombat={ S:null, prev:{}, tail:0, lastClock:null, lod:'full', log:[], slewMax:0, over:0 };
  const emit=(type,ev)=>{ C.log.push([type,ev.move,ev.frame]); if(C.log.length>32) C.log.shift(); const h=U.combatEvents&&U.combatEvents[type]; for(const f of [h,...CB[type]]) if(typeof f==='function') try{ f(ev); }catch(e){ console.warn('crew combat '+type,e); } };
  const ev=(type,f,x)=>Object.assign({type,rider:R,riderId:U.crew||U.name||'crew',move:C.S.name,kind:'react',step:-1,side:C.S.side,frame:f,t:f/72,target:null},x||{});
  C.start=o=>{ if(!srCrewCombatOn()) return false; o=o||{}; const name=SR_CREW_REACT_KIND[o.kind]||(SR_CREW_REACT[o.kind]&&o.kind)||'react_light', m=SR_CREW_REACT[name];
    let fb=1, side='Left'; if(o.dir&&o.dir.isVector3){ const lq=R.getWorldQuaternion(new THREE.Quaternion()).invert(), l=o.dir.clone().applyQuaternion(lq); fb=l.z>0?-1:1; side=l.x>=0?'Left':'Right'; }
    if(!C.S&&C.tail<=0) C.prev={};   // fresh slew reference (no stale pose from an earlier react)
    if(C.S&&!C.S.done) emit('onRecover',ev('onRecover',C.S.f,{interrupted:true,by:name}));
    C.S={name,m,fb,side,t:0,f:-1,done:false,stop:0,end:m.A+m.X+m.R,w0:C.S&&!C.S.done?C.S.w:0,w:0}; return true; };
  C.step=dt=>{ const S=C.S; if(!S) return; if(S.stop>0){ S.stop-=dt; if(S.stop>0) dt=0; else { dt=-S.stop; S.stop=0; } } S.t+=dt; const f=Math.floor(S.t*72+1e-6), m=S.m;
    for(let k=S.f+1;k<=f&&!S.done;k++) if(k===S.end){ S.done=true; emit('onRecover',ev('onRecover',k,{interrupted:false})); }
    S.f=Math.max(S.f,f); const ff=S.t*72, sm=(a,b,x)=>{ const t=Math.min(1,Math.max(0,(x-a)/(b-a))); return t*t*(3-2*t); };
    S.w=S.done?0:Math.min(S.w0+(1-S.w0)*sm(0,Math.max(2,m.A),ff),1-sm(m.A+m.X+m.R*.5,S.end,ff)); if(S.done){ C.S=null; C.tail=.3; } };
  C.sample=keysOnly=>{ const S=C.S, K=S.m.keys, ff=S.t*72; let i=0; while(i<K.length-2&&ff>K[i+1][0]) i++; const a=K[i], b=K[i+1];
    const u=keysOnly?(ff>=b[0]?1:0):Math.min(1,Math.max(0,(ff-a[0])/Math.max(1e-6,b[0]-a[0]))), e=u*u*(3-2*u), out={};
    for(const n in b[1]){ const p=a[1][n]||b[1][n], q=b[1][n]; const v=[0,1,2].map(j=>p[j]+(q[j]-p[j])*e); if(/^(spine|chest|head)$/.test(n)){ if(S.m.dirFlip&&S.fb<0) v[0]=-v[0]*.75; if(S.side==='Right') v[2]=-v[2]; } out[n]=v; } return out; };
  U.setState=function(n,o){ if(n==='react') return C.start(o); return typeof prevSet==='function'?prevSet.apply(this,arguments):false; };
  U.combatEvents={ onHitFrame:null, onCancelOpen:null, onCancelClose:null, onRecover:null };
  U.onCombat=(type,fn)=>{ if(!CB[type]||typeof fn!=='function') return ()=>{}; CB[type].push(fn); return ()=>{ const i=CB[type].indexOf(fn); if(i>=0) CB[type].splice(i,1); }; };
  U.combatHitStop=ms=>{ if(!C.S) return false; C.S.stop=Math.max(C.S.stop,(+ms||0)/1000); return true; };
  U.combatState=()=>C.S&&!C.S.done?'react':null; U.combatOn=srCrewCombatOn; U.combatStep=dt=>C.step(dt);
  U.combatQuery=()=>{ const S=C.S; if(!S) return null; const m=S.m, f=S.f; return { kind:'react', move:S.name, step:-1, side:S.side, frame:f, phase:f<m.A?'A':f<m.A+m.X?'X':'R', charge:0, hitStop:S.stop,
    frames:{a:m.A,x:m.X,r:m.R,end:S.end,hit:[],cancel:null}, cancelOpen:false, cancelKinds:[], root:{fwdVel:0,up:0,total:0,applied:false}, weight:S.w, target:null, plant:'both', mask:'full', lod:C.lod, fx:U.fxAll?U.fxAll():{} }; }; }
window.srCrewCombatInstall=srCrewCombatInstall;
// per rPose call: advance the clock (game clock delta; manual via combatStep when window.__crewCombatManual), LOD, additive overlay, 720 deg/s slew
function srCrewCombatPose(R){ const U=R.userData; if(!U||U.ikki||!U.bones) return; if(!U.crCombat) srCrewCombatInstall(R); const C=U.crCombat; if(!C||(!C.S&&C.tail<=0)) return;
  const gc=typeof clock!=='undefined'?clock:performance.now()/1000, dt=C.lastClock===null?0:Math.min(.1,Math.max(0,gc-C.lastClock)); C.lastClock=gc;
  if(!window.__crewCombatManual) C.step(dt); const sdt=window.__crewCombatManual?(C.mdt||1/72):Math.max(dt,1e-4); C.tail=Math.max(0,C.tail-sdt);
  let lod='full'; if(typeof camera!=='undefined'){ R.getWorldPosition(_crV); const d=_crV.distanceTo(camera.position); _crV.project(camera); lod=(d>30||_crV.z>1||Math.abs(_crV.x)>1.15||Math.abs(_crV.y)>1.15)?'off':d>12?'keys':'full'; } C.lod=lod;
  const B=U.bones; if(C.S&&lod!=='off'&&C.S.w>1e-3){ const O=C.sample(lod==='keys'), w=C.S.w; for(const n in O){ const b=B[n]; if(!b) continue; const v=O[n]; _crQ.setFromEuler(_crE.set(v[0]*w,v[1]*w,v[2]*w)); b.quaternion.multiply(_crQ); } }
  if(lod==='full'){ const mx=720*Math.PI/180*sdt; for(const n in SR_CREW_REACT.knockdown.keys[1][1]){ const b=B[n]; if(!b) continue; const q=C.prev[n]; if(q){ const d=2*Math.acos(Math.min(1,Math.abs(q.dot(b.quaternion)))); if(d>mx) q.slerp(b.quaternion,mx/d); else q.copy(b.quaternion); b.quaternion.copy(q); C.slewMax=Math.max(C.slewMax,Math.min(d,mx)/sdt*180/Math.PI); } else C.prev[n]=b.quaternion.clone(); } }
  else C.prev={};
  // knockdown crouch: drop the root so the lower foot joint stays at its contact height (srCrewPlant's own nudge is capped at 30 mm); 0 when idle
  U.crDrop=0; const P=U.cp, H=R.parent; if(P&&H&&C.S&&lod!=='off'&&C.S.w>1e-3){ R.position.y=P.y0; R.updateMatrixWorld(true); const lo=Math.min(H.worldToLocal(B.footL.getWorldPosition(_crV)).y,H.worldToLocal(B.footR.getWorldPosition(_crV)).y); U.crDrop=Math.min(0,P.low-lo); } }
if(typeof rPose==='function'&&!window.__srRPoseWrap){ window.__srRPoseWrap=true; const _rp=rPose; rPose=function(R){ _rp.apply(this,arguments); try{ srCrewCombatPose(R); }catch(e){ if(!window.__srCCerr){ window.__srCCerr=1; console.warn('crew combat',e); } } try{ srCrewPlant(R); }catch(e){ if(!window.__srCPerr){ window.__srCPerr=1; console.warn('crew plant',e); } } }; }
