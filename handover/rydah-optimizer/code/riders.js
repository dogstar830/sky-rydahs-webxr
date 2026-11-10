// ===== RIDERS: GLB crew riders (skyrydahs-characters). r128 port of shared/rider_loader.js (same GLB layout, slot palette,
// 3 draw calls/rider: toon body + inverted-hull outline + glow; LOD 0/14/32 m; setColor(slot,hex); update(camera,dt,boost01)).
// shared/rider_loader.js itself is an ES module for three r170 (three/addons, mergeGeometries, vMapUv, opaque_fragment, colorSpace),
// so it cannot run against this file's r128 global build; this port mirrors it 1:1 on r128 APIs (GLTFLoader r128 + BufferGeometryUtils r128).
const CHAR_BASE=(new URLSearchParams(location.search).get("chars"))||"skyrydahs-characters/";
const RSLOTS=['skin','hair','jacket','cloth','gold','metal','skate','eyes','iris','wheelGlow','glow2'], RROLES={primary:'jacket',secondary:'cloth',accent:'gold',trim:'skate',skin:'skin'};
const RBASE={skin:0xffd9c2,hair:0x23222f,jacket:0x2a2a30,cloth:0x34304a,gold:0xffd700,metal:0x8c93a3,skate:0x3a3a3e,eyes:0xffffff,iris:0xffc21a,wheelGlow:0xffd700,glow2:0xffd700,rim:0xffd700,shadow:0x5a4f9e,outline:0x07060c};
const RSPEC={hair:0,metal:1,gold:1,skate:.8}, RRIM={jacket:1,hair:.8,cloth:.6,skate:.9,skin:.35,metal:.6,gold:.4}, REMI={iris:.35,eyes:.1}, RHL={hair:.32,iris:1,eyes:.6,metal:.5};
function rResolve(def,crew){ const c=Object.assign({},RBASE,def), u=Object.assign({},crew); for(const r in RROLES) if(u[r]!==undefined&&u[RROLES[r]]===undefined) u[RROLES[r]]=u[r];
  if(crew.accent!==undefined) for(const k of ['gold','iris']) if(crew[k]===undefined) u[k]=crew.accent; return Object.assign(c,u); }
const RSLOT_GLSL=`#define NSLOTS ${RSLOTS.length}
 uniform vec3 uSlotColor[NSLOTS]; uniform float uSlotRim[NSLOTS]; uniform float uSlotSpec[NSLOTS]; uniform float uSlotEmi[NSLOTS]; uniform float uSlotHL[NSLOTS]; uniform float uPainted;
 int riderSlot(vec2 uv){ return int(clamp(floor(uv.x*float(NSLOTS)),0.,float(NSLOTS-1))); }`;
function rGrad(tones){ const v=tones===2?[95,255]:tones===4?[70,150,225,255]:[85,185,255]; const d=new Uint8Array(v.flatMap(x=>[x,x,x,255])); const t=new THREE.DataTexture(d,v.length,1,THREE.RGBAFormat); t.minFilter=t.magFilter=THREE.NearestFilter; t.generateMipmaps=false; t.needsUpdate=true; return t; }
function rToon(map,sh){ const m=new THREE.MeshToonMaterial({color:0xffffff,map,gradientMap:sh.gradientMap,skinning:true});
  m.onBeforeCompile=s=>{ Object.assign(s.uniforms,sh.slots,{uPainted:sh.painted,uRimColor:sh.rimColor,uShadowTint:sh.shadowTint,uLightDirV:sh.lightDirV});
    s.fragmentShader=s.fragmentShader.replace('#include <common>',`#include <common>\n${RSLOT_GLSL}\n uniform vec3 uRimColor; uniform vec3 uShadowTint; uniform vec3 uLightDirV;`)
     .replace('#include <map_fragment>',`#include <map_fragment>\n int sl=riderSlot(vUv); vec3 slc=uSlotColor[0]; float srim=0., sspec=0., semi=0., shl=0.;
       for(int i=0;i<NSLOTS;i++){ if(i==sl){ slc=uSlotColor[i]; srim=uSlotRim[i]; sspec=uSlotSpec[i]; semi=uSlotEmi[i]; shl=uSlotHL[i]; } }
       float hlMask=uPainted*smoothstep(.9,.98,texelColor.r);
       diffuseColor.rgb*=slc;`)
     .replace('#include <emissivemap_fragment>',`#include <emissivemap_fragment>\n totalEmissiveRadiance+=slc*semi;`)
     .replace('#include <tonemapping_fragment>',`{ vec3 Vd=normalize(vViewPosition); vec3 Nn=normalize(normal); float ndl=dot(Nn,uLightDirV);
        gl_FragColor.rgb*=mix(uShadowTint,vec3(1.),smoothstep(-.08,.22,ndl)); float fr=1.-clamp(dot(Nn,Vd),0.,1.);
        gl_FragColor.rgb+=uRimColor*smoothstep(.74,.8,fr)*smoothstep(.1,-.4,ndl-.25)*srim*.7;
        gl_FragColor.rgb+=vec3(1.,.97,.9)*step(.975,dot(Nn,normalize(uLightDirV+Vd)))*sspec*.8; gl_FragColor.rgb+=mix(vec3(1.),slc,.3)*hlMask*shl; }
       #include <tonemapping_fragment>`); };
  m.customProgramCacheKey=()=>'rider-toon-r128'; return m; }
function rGlowMat(map,sh){ const m=new THREE.MeshBasicMaterial({color:0xffffff,map,skinning:true});
  m.onBeforeCompile=s=>{ Object.assign(s.uniforms,sh.slots,{uGlow:sh.glow});
    s.fragmentShader=s.fragmentShader.replace('#include <common>',`#include <common>\n${RSLOT_GLSL}\n uniform float uGlow;`)
     .replace('#include <map_fragment>',`int sl=riderSlot(vUv); vec3 slc=uSlotColor[0]; for(int i=0;i<NSLOTS;i++){ if(i==sl) slc=uSlotColor[i]; } diffuseColor.rgb=slc*uGlow;`); };
  m.customProgramCacheKey=()=>'rider-glow-r128'; return m; }
function rOutline(c,sh){ return new THREE.ShaderMaterial({ side:THREE.BackSide, skinning:true, // opaque + discard (no stacked transparency on Quest)
  uniforms:{uThick:sh.outlineThick,uFar:sh.outlineFar,uColor:{value:new THREE.Color(c.outline)}},
  vertexShader:`#include <common>
    #include <skinning_pars_vertex>
    uniform float uThick; uniform float uFar; varying float vFade;
    void main(){
      #include <beginnormal_vertex>
      #include <skinbase_vertex>
      #include <skinnormal_vertex>
      #include <begin_vertex>
      #include <skinning_vertex>
      vec4 mvPosition=modelViewMatrix*vec4(transformed,1.); vec3 n=normalize(normalMatrix*objectNormal); float d=-mvPosition.z;
      mvPosition.xyz+=n*uThick*clamp(d,.6,5.); vFade=1.-smoothstep(uFar*.55,uFar,d); gl_Position=projectionMatrix*mvPosition; }`,
  fragmentShader:`uniform vec3 uColor; varying float vFade; void main(){ if(vFade<.5) discard; gl_FragColor=vec4(uColor,1.); }` }); }
function rMerge(meshes,mat){ const names=[]; for(const m of meshes) for(const n of Object.keys(m.morphTargetDictionary||{})) if(!names.includes(n)) names.push(n);
  const MP=[], MN=[];
  const geos=meshes.map(m=>{ const g=m.geometry.clone(); const cnt=g.attributes.position.count, dict=m.morphTargetDictionary||{}, src=m.geometry.morphAttributes;
    MP.push(names.map(n=>dict[n]!==undefined&&src.position&&src.position[dict[n]]?src.position[dict[n]]:null)); MN.push(names.map(n=>dict[n]!==undefined&&src.normal&&src.normal[dict[n]]?src.normal[dict[n]]:null)); g.morphAttributes={}; g.morphTargetsRelative=false; for(const k of Object.keys(g.attributes)) if(!['position','normal','uv','skinIndex','skinWeight'].includes(k)) g.deleteAttribute(k);
    if(g.attributes.skinIndex.array.constructor!==Uint16Array){ g.setAttribute('skinIndex',new THREE.Uint16BufferAttribute(Array.from(g.attributes.skinIndex.array),4)); }
    if(g.index&&g.index.array.constructor!==Uint32Array) g.setIndex(new THREE.Uint32BufferAttribute(Array.from(g.index.array),1)); return g; });
  const geo=THREE.BufferGeometryUtils.mergeBufferGeometries(geos,false); const ref=meshes[0]; const sm=new THREE.SkinnedMesh(geo,mat); sm.bind(ref.skeleton,ref.bindMatrix); sm.frustumCulled=false;
  if(names.length){ const pos=geo.attributes.position, nor=geo.attributes.normal, idx=[], dP=names.map(()=>[]), dN=names.map(()=>[]); let off=0;
    meshes.forEach((m,mi)=>{ const cnt=m.geometry.attributes.position.count; for(let i=0;i<cnt;i++){ let any=false; for(const a of MP[mi]) if(a&&(a.getX(i)||a.getY(i)||a.getZ(i))){ any=true; break; }
        if(!any) continue; idx.push(off+i); names.forEach((_,j)=>{ const a=MP[mi][j], b=MN[mi][j]; dP[j].push(a?a.getX(i):0,a?a.getY(i):0,a?a.getZ(i):0); dN[j].push(b?b.getX(i):0,b?b.getY(i):0,b?b.getZ(i):0); }); } off+=cnt; });
    const bP=new Float32Array(idx.length*3), bN=new Float32Array(idx.length*3); idx.forEach((v,k)=>{ for(let c=0;c<3;c++){ bP[k*3+c]=pos.array[v*3+c]; bN[k*3+c]=nor.array[v*3+c]; } }); const w=names.map(()=>0);
    sm.userData.expr={ names, weights:w, set(name,val){ const t=names.indexOf(name); if(t<0) return; w[t]=val; for(let k=0;k<idx.length;k++) for(let c=0;c<3;c++){ let p=bP[k*3+c], n=bN[k*3+c]; for(let j=0;j<w.length;j++) if(w[j]){ p+=dP[j][k*3+c]*w[j]; n+=dN[j][k*3+c]*w[j]; } pos.array[idx[k]*3+c]=p; nor.array[idx[k]*3+c]=n; } pos.needsUpdate=true; nor.needsUpdate=true; } }; }
  return sm; }
const _rGLTF={};
// patch_tex_share (step 4.2A, Rydah Optimizer proposal): textures with identical pixels across rider GLBs (the 512x128 crew atlas
// sha 75200a21b7cc is embedded in all 7 crew .quest.glb) are swapped for ONE shared THREE.Texture; duplicates are disposed.
// Only images <=512x512 px; GLBs in the folder of any WARDROBE_RIDERS entry flagged noTexShare:true are skipped (kept full quality). Textures only: materials are NOT merged, so per-crew colours/uniforms are untouched. ?notexshare=1 = old behaviour.
const _rTexShare=new Map(), _rTexOff=/[?&]notexshare=1/.test(location.search);
function _rTexKey(t){ const im=t&&t.image; if(!im||!im.width||im.width*im.height>262144) return null;
  if(t.isCompressedTexture){ const mm=t.mipmaps&&t.mipmaps[0]; if(!mm||!mm.data) return null; const d=mm.data; let h1=0x811c9dc5, h2=0; // KTX2 (?ktx2=1): hash transcoded level-0 bytes
    for(let i=0;i<d.length;i++){ h1=Math.imul(h1^d[i],16777619); h2=(h2+h1)|0; } return ['ktx2',im.width,im.height,t.format,t.mipmaps.length,t.flipY,t.encoding,t.wrapS,t.wrapT,(h1>>>0).toString(16),(h2>>>0).toString(16)].join('|'); }
  try{ const c=document.createElement('canvas'); c.width=im.width; c.height=im.height; const x=c.getContext('2d'); x.drawImage(im,0,0);
    const d=x.getImageData(0,0,c.width,c.height).data; let h1=0x811c9dc5, h2=0; for(let i=0;i<d.length;i+=4){ h1=Math.imul(h1^d[i]^(d[i+1]<<8)^(d[i+2]<<16)^(d[i+3]<<24),16777619); h2=(h2+h1)|0; }
    return [im.width,im.height,t.flipY,t.encoding,t.wrapS,t.wrapT,(h1>>>0).toString(16),(h2>>>0).toString(16)].join('|'); }catch(e){ return null; } }
window.__TEXSHARE={ms:0,textures:0,shared:0,savedBytes:0}; let _rTexLogT=0;
function rShareTextures(gltf){ if(_rTexOff) return gltf; const _t0=performance.now(), TS=window.__TEXSHARE; const SL=['map','emissiveMap','normalMap','roughnessMap','metalnessMap','aoMap','alphaMap'];
  gltf.scene.traverse(o=>{ if(!o.isMesh) return; for(const m of [].concat(o.material)) for(const s of SL){ const t=m[s]; if(!t||t.userData.rShared) continue;
    const k=_rTexKey(t); if(!k) continue; TS.textures++; const hit=_rTexShare.get(k); if(hit&&hit!==t){ m[s]=hit; m.needsUpdate=true; TS.shared++; TS.savedBytes+=t.isCompressedTexture?t.mipmaps.reduce((a,m)=>a+(m.data?m.data.byteLength:0),0):Math.round(t.image.width*t.image.height*4*1.33); t.dispose(); } else { t.userData.rShared=true; _rTexShare.set(k,t); } } });
  TS.ms+=performance.now()-_t0; clearTimeout(_rTexLogT); _rTexLogT=setTimeout(()=>{ if(!TS.logged){ TS.logged=true; console.log('[texshare]',JSON.stringify({ms:+TS.ms.toFixed(1),textures:TS.textures,shared:TS.shared,savedMB:+(TS.savedBytes/1048576).toFixed(2)})); } },3000);
  return gltf; }
function rNoTexShare(url){ if(typeof WARDROBE_RIDERS==='undefined') return false; return Object.values(WARDROBE_RIDERS).some(r=>r&&r.noTexShare&&r.url&&url.startsWith(r.url.slice(0,r.url.lastIndexOf('/')+1))); }
function rLoad(url){ return _rGLTF[url]||(_rGLTF[url]=new Promise((res,rej)=>new THREE.GLTFLoader().load(url,g=>res(rNoTexShare(url)?g:rShareTextures(g)),undefined,rej))); }
async function loadRiderR128(parent,url,crewColors,opts){ opts=opts||{}; const fp=!!opts.fp; const c=rResolve(opts.defaults||{},crewColors||{});
  const gltf=await rLoad(url); const root=fp||!opts.clone?gltf.scene:gltf.scene; // one instance per crew file
  const rim=Object.assign({},RRIM,opts.slotRim||{}), spec=Object.assign({},RSPEC,opts.slotSpec||{});
  const sh={ gradientMap:rGrad(opts.tones||3), painted:{value:0}, slots:{uSlotColor:{value:RSLOTS.map(s=>new THREE.Color(c[s]))},uSlotRim:{value:RSLOTS.map(s=>rim[s]??.5)},uSlotSpec:{value:RSLOTS.map(s=>spec[s]??0)},uSlotEmi:{value:RSLOTS.map(s=>REMI[s]??0)},uSlotHL:{value:RSLOTS.map(s=>RHL[s]??.3)}},
    rimColor:{value:new THREE.Color(c.rim)}, shadowTint:{value:new THREE.Color(c.shadow)}, lightDirV:{value:new THREE.Vector3(.4,.8,.5).normalize()}, glow:{value:1.3}, outlineThick:{value:.0022}, outlineFar:{value:40} };
  let map=null; const levels={}, att={}, glowPts=[], bones={};
  root.traverse(o=>{ if(o.isBone) bones[o.name]=o;
    if(o.isMesh){ if(!map&&o.material.map){ map=o.material.map; map.encoding=THREE.LinearEncoding; const big=map.image&&map.image.width>=512; map.magFilter=big?THREE.LinearFilter:THREE.NearestFilter; map.minFilter=THREE.LinearFilter; map.generateMipmaps=false; map.needsUpdate=true; }
      let m=o.name.match(/_LOD(\d)_(\w+)$/); if(!m&&fp){ const f=o.name.match(/_FP_(body|glow)$/); if(f) m=[null,'0',f[1]]; }
      if(m) (levels[m[1]]=levels[m[1]]||{body:[],glow:[]})[m[2]==='glow'?'glow':'body'].push(o); }
    else if(/_Att$/.test(o.name)) att[o.name.replace(/_Att$/,'')]=o; else if(/^GlowPt_/.test(o.name)) glowPts.push(o); });
  sh.painted.value=map&&map.image&&map.image.width>=512?1:0; const toonM=rToon(map,sh), glowM=rGlowMat(map,sh), olM=rOutline(c,sh); const lod=new THREE.LOD(); const dists=fp?[0]:(opts.lodDistances||[0,14,32]); let host=null;
  for(const li of Object.keys(levels).sort()){ const {body,glow}=levels[li]; host=host||body[0].parent; const g=new THREE.Group();
    const b=rMerge(body,toonM); g.add(b); const ol=new THREE.SkinnedMesh(b.geometry,olM); ol.bind(b.skeleton,b.bindMatrix); ol.frustumCulled=false; g.add(ol);
    if(glow.length) g.add(rMerge(glow,glowM)); for(const o of [...body,...glow]){ o.parent.remove(o); } lod.addLevel(g,dists[+li]??60*+li); }
  host.add(lod);
  const sprites=[]; if(opts.vr){ sh.glow.value=1; for(const p of glowPts){ const slot=/halo|visor|eyes/.test(p.name)?'glow2':'wheelGlow'; const s=new THREE.Sprite(new THREE.SpriteMaterial({map:TEX.glow,color:c[slot],blending:THREE.AdditiveBlending,depthWrite:false,transparent:true,opacity:.7})); const z=p.userData.glowSize??.12; s.scale.setScalar(z); s.userData.base=z; p.add(s); sprites.push(s); } }
  const wl=new THREE.Vector3(.5,1,.6).normalize(); const rest={}; for(const k in bones) rest[k]=bones[k].quaternion.clone();
  let exprs=[]; lod.traverse(o=>{ if(o.userData.expr) exprs=o.userData.expr.names; });
  Object.assign(root.userData,{ crew:opts.crewName, expressions:exprs, setExpression:(name,w)=>lod.traverse(o=>{ if(o.userData.expr) o.userData.expr.set(name,w===undefined?1:w); }), colors:c, shared:sh, lod, attachments:att, sprites, bones, rest, vr:!!opts.vr,
    setLightDir:v=>wl.copy(v).normalize(),
    setColor:(slot,hex)=>{ const k=RROLES[slot]??slot, i=RSLOTS.indexOf(k); if(i>=0) sh.slots.uSlotColor.value[i].set(hex); },
    update:(cam,dt,boost)=>{ boost=boost||0; sh.lightDirV.value.copy(wl).transformDirection(cam.matrixWorldInverse);
      if(opts.vr){ for(const s of sprites){ s.material.opacity=.55+.45*boost; s.scale.setScalar(s.userData.base*(1+.6*boost)); } } else sh.glow.value=1.3+boost*4; } });
  parent.add(root); return root; }
// procedural skate pose on the rig bones (GLBs ship without clips): stride, knee bend, crouch, arm swing, idle sway
const _rq=new THREE.Quaternion(), _re=new THREE.Euler();
function rPose(R,ph,stride,crouch,lean,armSw,t){ const B=R.userData.bones, S=R.userData.rest; const set=(n,x,y,z)=>{ n=n.replace('.',''); const b=B[n]; if(!b) return; b.quaternion.copy(S[n]).multiply(_rq.setFromEuler(_re.set(x,y||0,z||0))); };
  const sw=Math.sin(ph)*stride; set('thigh.L',-sw-crouch*.6); set('thigh.R',sw-crouch*.6); set('shin.L',crouch*1.1+Math.max(0,sw)*.7); set('shin.R',crouch*1.1+Math.max(0,-sw)*.7);
  set('foot.L',-crouch*.5); set('foot.R',-crouch*.5); set('spine',lean+crouch*.25,Math.sin(ph)*.08*stride,0); set('chest',Math.sin(t*1.6)*.02,0,0); set('head',-lean*.6,Math.sin(t*.4)*.25*(1-stride),0);
  set('upperarm.L',Math.sin(ph)*armSw+RARM[0],RARM[1],RARM[2]); set('upperarm.R',-Math.sin(ph)*armSw+RARM[0],-RARM[1],-RARM[2]); set('forearm.L',-.4); set('forearm.R',-.4); }
let RARM=[0,1.1,0];
const RIDERS={ player:null, fp:null, npcs:[], fail:false };
function initRiders(){
  const vr=false, need=["GLTFLoader","BufferGeometryUtils"];
  const L=["loaders/GLTFLoader.js","utils/BufferGeometryUtils.js"]; const bases=["vendor/three/examples/js/","https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/"]; let base=bases[0];
  const go=async()=>{ for(const cr of CREWS){ const col=new THREE.Color(cr.defaults.wheelGlow).getHex(); // canon: wheels glow crew colour
      try{ if(cr.garage==="codee"&&cr.dir==="caali"){ const r=await loadRiderR128(Ride.group,CHAR_BASE+cr.dir+"/"+cr.file+"-rider.glb",{wheelGlow:0xffd700},Object.assign({defaults:cr.defaults,crewName:cr.crew},cr.opts)); RIDERS.player=r;
          for(const ch of Ride.group.children) if(ch!==r&&ch!==Ride.aura) ch.visible=false; Ride.useGLB=true; continue; }
        const g=garages.find(q=>q.crew===cr.garage); if(!g) continue; const holder=new THREE.Group(); scene.add(holder);
        const r=await loadRiderR128(holder,CHAR_BASE+cr.dir+"/"+cr.file+"-rider.glb",{wheelGlow:new THREE.Color(g.color).getHex()},Object.assign({defaults:cr.defaults,crewName:cr.crew},cr.opts));
        RIDERS.npcs.push({r,holder,g,ph:Math.random()*6,mode:RIDERS.npcs.length%2}); }catch(e){ console.warn("rider load failed "+cr.dir+": "+(e&&e.message||e)); } }
    RIDERS.fail=RIDERS.fail||(!RIDERS.player&&"no-player"); RIDERS.ready=true; };
  const next=i=>{ if(i>=L.length){ go().catch(e=>{ RIDERS.fail="go:"+(e&&e.message||e); console.error("riders go() failed",e); }); return; } if(THREE[need[i]]||window[need[i]]){ next(i+1); return; } let bi=0; const tryBase=()=>{ const s=document.createElement("script"); s.src=bases[bi]+L[i]; s.onload=()=>{ base=bases[bi]; next(i+1); }; s.onerror=()=>{ if(bi+1<bases.length){ bi++; tryBase(); } else { RIDERS.fail="cdn:"+L[i]; console.warn("rider loader script failed "+L[i]); } }; document.head.appendChild(s); }; tryBase(); }; next(0);
}
async function riderEnterVR(){ if(!RIDERS.player) return; RIDERS.player.visible=false;
  if(!RIDERS.fp){ const cr=CREWS[0]; try{ RIDERS.fp=await loadRiderR128(Ride.group,CHAR_BASE+cr.dir+"/"+cr.file+"-fp.glb",{wheelGlow:new THREE.Color(cr.defaults.wheelGlow).getHex()},Object.assign({defaults:cr.defaults,crewName:cr.crew},cr.opts,{fp:true,vr:true})); }catch(e){ console.warn("fp load failed",e); } }
  if(RIDERS.fp) RIDERS.fp.visible=true; }
function riderExitVR(){ if(RIDERS.player) RIDERS.player.visible=true; if(RIDERS.fp) RIDERS.fp.visible=false; }
const _np=new THREE.Vector3();
function updateRiders(dt){ if(!RIDERS.ready&&!RIDERS.player) return; const cam=camera, R=Ride, sp=R.speed/R.maxSpeed;
  if(RIDERS.player){ const ph=clock*(4+sp*6); rPose(RIDERS.player,ph,R.grinding?0:.55*Math.min(1,sp*1.5),R.grinding?.35:.12+sp*.25,.18+sp*.25,.35*Math.min(1,sp*1.5),clock); RIDERS.player.userData.update(cam,dt,R.boost); }
  if(RIDERS.fp) RIDERS.fp.userData.update(cam,dt,R.boost);
  for(const n of RIDERS.npcs){ const [gx,gz]=n.g.pos, th=n.g.th, dx=Math.sin(th), dz=Math.cos(th); const cx=gx+dx*7, cz=gz+dz*7;
    _np.set(cx,0,cz); const d2=_np.distanceToSquared(cam.position); n.holder.visible=d2<70*70; if(!n.holder.visible) continue;   // distance-cull NPCs (Quest draw-call budget)
    if(n.gy===undefined){ let g=null; try{ g=typeof WORLD_GROUND==='function'?WORLD_GROUND(cx,cz,.5):null; }catch(e){} n.gy=g&&isFinite(g.y)&&Math.abs(g.y)<1.5?g.y:0; }   // Rigger: root NPCs on the rendered asphalt (0.01), once at spawn; 0 if WORLD_GROUND missing
    n.ph+=dt; if(n.mode===0){ const a=n.ph*.45; n.holder.position.set(cx+Math.cos(a)*3.2,n.gy,cz+Math.sin(a)*3.2); n.holder.rotation.y=-a; rPose(n.r,n.ph*5,.45,.2,.25,.3,clock); }   // looping carve
    else { n.holder.position.set(cx,n.gy,cz); n.holder.rotation.y=th+Math.sin(n.ph*.3)*.6; rPose(n.r,0,0,.05+Math.sin(n.ph*1.5)*.03,.02,0,clock+n.ph); }                              // idle sway
    n.r.userData.update(cam,dt,.2+.2*Math.sin(n.ph*2)); }
}
function riderFootPos(i,out){ const b=RIDERS.player&&RIDERS.player.userData.bones[i?'footR':'footL']; if(b){ b.getWorldPosition(out); out.y=Math.max(Ride.group.position.y+.05,out.y-.1); return true; } return false; }
