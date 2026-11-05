// ===== PBR WORLD (Palma Builder, pbr_world.js via patch_pbr_world.py; realism step 5 slice 1). DEFAULT ON (10/30); ?toon=1 or ?pbr=0 forces the old toon look; ?pbr=1 = no-op.
// Default path: this IIFE returns before touching anything (no textures, no listeners, no material changes).
// Slice 1: ground atlas page G (2x2: asphalt031 | concrete034 / ground080 sand | planks037A) on district asphalt, sidewalks/curbs, Cove sand,
// blockout sand pad + boardwalk deck (per-instance by instanceColor, inside the shared INST box pool); facade detail page F (plaster | bricks105)
// on the FACADE shader (stucco + brick only); one Portside env cube (baked offline by pbr_env_bake.py, PMREM at load) on world PBR + facade glass;
// ACES filmic tonemapping + PBR fog ranges. Projection: world-space planar / dominant-axis (triplanar-lite) UVs, explicit gradients (no mip seams).
// Texture convention (perf/texmem/audit.md §5): KTX2 colour ETC1S sRGB, ORM R=AO G=rough B=metal linear ETC1S, normals +Y UASTC; KTX2 pre-flipped, flipY off.
// Albedo scale k calibrated 10/30 against the toon look (legacy lights give ~2x on Standard diffuse). Colour space: the game renders with outputEncoding Linear and display-referred colours, so albedo is sampled as stored (encoding Linear) to match.
const PBR_WORLD=(()=>{ const Q=location.search, on=!/[?&]toon=1(&|$)/.test(Q)&&!/[?&]pbr=0(&|$)/.test(Q); if(!on) return {on:false}; /* DEFAULT ON since 10/30 (Ani); ?toon=1 or ?pbr=0 = old toon look; ?pbr=1 kept as no-op */
  const S={on:true,stats:{},warn:[]}, K2=window.SR_KTX2&&window.SR_KTX2.on, BASE='assets/pbr/';
  // ---- textures (jpg default; ?ktx2=1 -> SR_KTX2.loader, swap in place, jpg fallback)
  const U={ gA:{value:null}, gN:{value:null}, gO:{value:null}, fA:{value:null}, fN:{value:null} };
  function jpg(n,u){ const t=new THREE.TextureLoader().load(BASE+n+'.jpg'); t.wrapS=t.wrapT=THREE.ClampToEdgeWrapping; t.anisotropy=8; t.generateMipmaps=true; t.minFilter=THREE.LinearMipmapLinearFilter; U[u].value=t; return t; }
  function tex(n,u){ jpg(n,u); if(!K2) return; let tries=0; const go=()=>{ try{ const L=typeof window.SR_KTX2.loader==='function'&&window.SR_KTX2.loader(); if(!L){ if(++tries>300){ S.warn.push('ktx2 no loader '+n); return; } return requestAnimationFrame(go); }
      L.load(BASE+n+'.ktx2',c=>{ c.wrapS=c.wrapT=THREE.ClampToEdgeWrapping; c.anisotropy=8; c.minFilter=THREE.LinearMipmapLinearFilter; c.generateMipmaps=false; c.flipY=false; c.encoding=THREE.LinearEncoding; c.needsUpdate=true; U[u].value=c; S.stats['ktx2_'+n]=1; },undefined,e=>{ S.warn.push('ktx2 fallback jpg '+n); }); }catch(e){ S.warn.push('ktx2 err '+n); } }; requestAnimationFrame(go); }
  // ---- env: 6x1 strip (px,nx,py,ny,pz,nz) -> CubeTexture (facade samplerCube) + PMREM (world PBR)
  const ENV={day:null,night:null,cube:{day:null,night:null},cur:null};
  function envLoad(tag){ const im=new Image(); im.onload=()=>{ const s=im.height, faces=[]; for(let f=0;f<6;f++){ const c=document.createElement('canvas'); c.width=c.height=s; c.getContext('2d').drawImage(im,f*s,0,s,s,0,0,s,s); faces.push(c); }
      const ct=new THREE.CubeTexture(faces); ct.needsUpdate=true; ENV.cube[tag]=ct; try{ const pm=new THREE.PMREMGenerator(renderer); ENV[tag]=pm.fromCubemap(ct).texture; pm.dispose(); }catch(e){ S.warn.push('pmrem '+e); } S.stats['env_'+tag]=s; }; im.src=BASE+'env_portside_'+tag+'.png'; }
  // ---- shared shader injection (works on MeshStandardMaterial and MeshToonMaterial chunk names, r128)
  const VPARS=`varying vec3 vPbrW; varying vec3 vPbrN;`;
  const VMAIN=`{ vec4 pw=vec4(transformed,1.); vec3 pn=objectNormal;
    #ifdef USE_INSTANCING
      pw=instanceMatrix*pw; pn=mat3(instanceMatrix)*pn;
    #endif
    pw=modelMatrix*pw; vPbrW=pw.xyz; vPbrN=normalize(mat3(modelMatrix)*pn); }`;
  const FPARS=`varying vec3 vPbrW; varying vec3 vPbrN; uniform sampler2D pbrA, pbrN, pbrO; uniform vec4 pbrT; uniform vec3 pbrTint; uniform float pbrK, pbrNS, pbrWet, pbrAsph, pbrCA; uniform sampler2D pbrAO; uniform vec4 pbrAOB;
    // pbrT: tile col,row (page 2x2), metres per tile, mode (0 = whole material, 1 = per-instance: sand/wood instanceColor match)
    /* slice 2: z = 1 -> divide by vColor (sand/wood take the texture colour); 0 -> keep instance tint (concrete/steel) */
    vec3 pbrTile(vec3 c){ if(pbrT.w<.5) return vec3(pbrT.xy,0.); if(length(c-vec3(.929,.910,.863))<.03) return vec3(0.,1.,1.); if(length(c-vec3(.541,.416,.282))<.03) return vec3(1.,1.,1.);
      if(length(c-vec3(.165,.176,.227))<.02) return vec3(0.,0.,2.); /* z=2: neutral grey (drop the navy vertex tint) */ /* bridge deck 0x2a2d3a (merged vertex colour) -> asphalt */
      if(pbrT.w>1.5||length(c-vec3(.522,.518,.498))<.03||length(c-vec3(.455,.451,.431))<.03||length(c-vec3(.608,.596,.565))<.03) return vec3(1.,0.,0.); return vec3(-1.); }
    float pbrN2(vec2 p){ vec2 i=floor(p), f=fract(p); f=f*f*(3.-2.*f); float a=fract(sin(dot(i,vec2(127.1,311.7)))*43758.5), b=fract(sin(dot(i+vec2(1.,0.),vec2(127.1,311.7)))*43758.5), c=fract(sin(dot(i+vec2(0.,1.),vec2(127.1,311.7)))*43758.5), d=fract(sin(dot(i+1.,vec2(127.1,311.7)))*43758.5); return mix(mix(a,b,f.x),mix(c,d,f.x),f.y); }`;
  const FMAP=`vec3 pAlb=vec3(1.), pNrm=vec3(.5,.5,1.), pORM=vec3(1.,1.,0.); float pM=0., pWetM=0., pAOg=1.; vec3 pT=vec3(1.,0.,0.), pB=vec3(0.,0.,-1.), pWN=normalize(vPbrN);
    {
    #if defined(USE_INSTANCING_COLOR) || defined(USE_COLOR)
      vec3 tl=pbrTile(vColor);
    #else
      vec3 tl=pbrTile(vec3(0.));
    #endif
      if(tl.x>-.5){ pM=1.; vec3 an=abs(pWN); vec2 puv;
        if(an.y>=an.x&&an.y>=an.z){ puv=vec2(vPbrW.x,-vPbrW.z); }
        else if(an.x>an.z){ puv=vec2(-vPbrW.z*sign(pWN.x),vPbrW.y); pT=vec3(0.,0.,-sign(pWN.x)); pB=vec3(0.,1.,0.); }
        else { puv=vec2(vPbrW.x*sign(pWN.z),vPbrW.y); pT=vec3(sign(pWN.z),0.,0.); pB=vec3(0.,1.,0.); }
        vec2 tuv=puv/pbrT.z; const float PAD=.008; vec2 SC=vec2(.5)*(1.-2.*PAD);
        vec2 auv=(vec2(tl.x,1.-tl.y)+PAD+fract(tuv)*(1.-2.*PAD))*.5; vec2 gx=dFdx(tuv)*SC, gy=dFdy(tuv)*SC;
        pAlb=texture2DGradEXT(pbrA,auv,gx,gy).rgb; pNrm=texture2DGradEXT(pbrN,auv,gx,gy).rgb; pORM=texture2DGradEXT(pbrO,auv,gx,gy).rgb;
        vec3 alb=pAlb*pbrTint*pbrK;
    #if defined(USE_INSTANCING_COLOR) || defined(USE_COLOR)
        if(tl.z>1.5) alb*=.42;
        if(tl.z>.5) alb/=max(vColor,vec3(.05)); /* color_fragment multiplies vColor back in */
        else if(pbrT.w>.5) alb*=(tl.x<.5&&tl.y<.5)?.9:1.6; /* tinted concrete/steel x1.6 (vColor ~.5 multiplies in); merged toon bridge deck (asphalt) kept dark */
    #endif
        if(an.y>.5&&vPbrW.y<.4){ /* ground: runtime-baked top-down AO mask (walls + kerbs), gutter damp, asphalt macro */
          vec2 m=(vPbrW.xz-pbrAOB.xy)/pbrAOB.zw; float occ=(m.x>0.&&m.x<1.&&m.y>0.&&m.y<1.)?texture2D(pbrAO,m).r:0.; pAOg=1.-.8*occ;
          if(pbrAsph>.5||(pbrT.w>.5&&tl.x<.5&&tl.y<.5)){ float mac=pbrN2(vPbrW.xz/9.)*.6+pbrN2(vPbrW.xz/2.7)*.4; float l=dot(alb,vec3(.33)); alb=max(vec3(0.),(alb-l)*1.7+l); /* contrast back */
            alb*=mix(.42,1.42,smoothstep(.28,.78,mac)); float wear=max(pbrN2(vec2(vPbrW.x*.7,vPbrW.z/22.)),pbrN2(vec2(vPbrW.x/22.,vPbrW.z*.7))); alb*=1.+.5*smoothstep(.6,.9,wear)-.04; /* lane wear streaks */                                   /* patched / sun-bleached macro */
            float crack=smoothstep(.46,.78,1.-pNrm.b); alb*=1.-crack;                    /* cracks from the tile's normal relief */
            pWetM=clamp(smoothstep(.15,.5,occ)+smoothstep(.62,.78,1.-mac)*.8,0.,1.); alb*=mix(1.,.45,pWetM*mix(.5,1.,pbrWet)); } }
        if(an.y<.5) pAOg=mix(1.-.4*pbrCA,1.,smoothstep(0.,1.2,vPbrW.y));              /* contact AO at wall / prop bases */
        diffuseColor.rgb=alb*pAOg; } }`;
  const FNRM=`#include <normal_fragment_maps>
    if(pM>.5){ vec2 nxy=(pNrm.xy*2.-1.)*pbrNS; vec3 pn=normalize(pT*nxy.x+pB*nxy.y+pWN*sqrt(max(.05,1.-dot(nxy,nxy)))); normal=normalize((viewMatrix*vec4(pn,0.)).xyz); }`;
  const FROUGH=`float roughnessFactor = roughness; if(pM>.5) roughnessFactor*=pORM.g; roughnessFactor=mix(roughnessFactor,.2,pWetM*pbrWet);`, FMETAL=`float metalnessFactor = metalness; if(pM>.5) metalnessFactor*=pORM.b;`;
  // Bloom guard: setupFX's UnrealBloomPass high-pass (threshold .68, smoothWidth .01) is a near-binary cut on 8-bit composer targets; a large
  // ACES-mapped PBR ground area just over .68 gets ~1.8x its colour added back (5 mips x factors 3.0 x strength .6) -> white street. Diffuse world
  // surfaces must never bloom, so the final (post-fog) luminance is soft-capped below the threshold. Emissive/neon are separate materials (untouched).
  /* slice 3: soft shoulder only above .5 (asymptote .66 < bloom .68); darks + midtones untouched */
  const FCAP=`float pbrL=dot(gl_FragColor.rgb,vec3(.2126,.7152,.0722)); if(pbrL>.5) gl_FragColor.rgb*=(.5+.16*(1.-exp(-(pbrL-.5)/.16)))/pbrL;
    #include <dithering_fragment>`;
  const FAO=`#include <aomap_fragment>
    if(pM>.5){ reflectedLight.indirectDiffuse*=pORM.r*pAOg; reflectedLight.indirectSpecular*=pORM.r*mix(pAOg,1.,pWetM*pbrWet); reflectedLight.directDiffuse*=mix(1.,pAOg,.6); }`;
  function inject(mat,o){ const prev=mat.onBeforeCompile, uni={ pbrA:U.gA, pbrN:U.gN, pbrO:U.gO, pbrT:{value:new THREE.Vector4(o.tile[0],o.tile[1],o.m,o.mode||0)}, pbrTint:{value:new THREE.Color(o.tint==null?0xffffff:o.tint)}, pbrK:{value:o.k||1}, pbrNS:{value:o.ns||1}, pbrWet:WET, pbrAsph:{value:o.asph?1:0}, pbrCA:{value:o.ca==null?1:o.ca}, pbrAO:AOT, pbrAOB:AOB };
    mat.onBeforeCompile=function(sh,r){ if(prev) prev.call(this,sh,r); Object.assign(sh.uniforms,uni);
      sh.vertexShader=VPARS+'\n'+sh.vertexShader.replace('#include <project_vertex>','#include <project_vertex>\n'+VMAIN);
      let f=FPARS+'\n'+sh.fragmentShader.replace('#include <map_fragment>','#include <map_fragment>\n'+FMAP).replace('#include <normal_fragment_maps>',FNRM).replace('#include <aomap_fragment>',FAO).replace('#include <dithering_fragment>',FCAP);
      f=f.replace('#include <roughnessmap_fragment>',FROUGH).replace('#include <metalnessmap_fragment>',FMETAL); sh.fragmentShader=f; };
    const pk=mat.customProgramCacheKey; mat.customProgramCacheKey=function(){ return (pk?pk.call(this):'')+'|pbrW'+(o.mode||0); }; mat.needsUpdate=true; mat.userData.pbrWorld=o.id; return mat; }
  function std(o){ const m=new THREE.MeshStandardMaterial({color:0xffffff,roughness:o.rough==null?1:o.rough,metalness:o.metal==null?1:o.metal,envMap:ENV.night,envMapIntensity:o.env||1});
    m.userData.pbrEnv=1; S.mats.push(m); return inject(m,o); }
  S.mats=[];
  // ---- slice 2: runtime-baked top-down AO mask (1024^2 L8, ~1.4 MB w/ mips): building colliders (occluders) + kerbs, blurred
  const WET={value:1}, AOT={value:null}, AOB={value:new THREE.Vector4(-440,-480,880,820)};
  function bakeAO(){ const N=1024, b=AOB.value, cv=document.createElement('canvas'); cv.width=cv.height=N; const x=cv.getContext('2d'); x.fillStyle='#000'; x.fillRect(0,0,N,N);
    const R=(x0,z0,x1,z1,a)=>{ x.fillStyle='rgba(255,255,255,'+a+')'; x.fillRect((x0-b.x)/b.z*N,(z0-b.y)/b.w*N,(x1-x0)/b.z*N,(z1-z0)/b.w*N); };
    let nc=0, nw=0; x.filter='blur(3px)';
    for(const c of (typeof colliders!=='undefined'?colliders:[])){ if(!c||c.maxX<-1e5||'off' in c) continue; const w=c.maxX-c.minX, d=c.maxZ-c.minZ; if(w<.6&&d<.6) continue; R(c.minX-1.2,c.minZ-1.2,c.maxX+1.2,c.maxZ+1.2,.9); nc++; }
    x.filter='blur(1.2px)';
    if(typeof DET!=='undefined') for(const k in DET){ if(k.split('|')[0]!=='walk') continue; for(const p of DET[k]){ R(p[0]-p[3]/2-.5,p[2]-p[5]/2-.5,p[0]+p[3]/2+.5,p[2]+p[5]/2+.5,.35); nw++; } }
    const px=x.getImageData(0,0,N,N).data, L=new Uint8Array(N*N); for(let i=0;i<N*N;i++) L[i]=px[i*4];
    const t=new THREE.DataTexture(L,N,N,THREE.LuminanceFormat); t.flipY=false; t.generateMipmaps=true; t.minFilter=THREE.LinearMipmapLinearFilter; t.magFilter=THREE.LinearFilter; t.needsUpdate=true; AOT.value=t; S.stats.ao={colliders:nc,kerbs:nw,px:N}; }
  // ---- conversion: after WORLD_PERF.run (merges done); swaps by material identity, so merge keys / draw counts are unchanged
  function convert(){ const T0=performance.now(), map=new Map(), st=S.stats; st.conv={}; try{ bakeAO(); }catch(e){ S.warn.push('ao '+e); }
    const swap=(old,mk,id)=>{ if(!map.has(old)) map.set(old,mk()); st.conv[id]=(st.conv[id]||0)+1; return map.get(old); };
    const asph=new Set(Object.values((typeof ASPH!=='undefined'&&ASPH.mats)||{}));
    const walkMap=typeof TEX!=='undefined'?TEX.walk:null, sandMap=typeof TEX!=='undefined'?TEX.sand:null;
    scene.traverse(o=>{ if(!o.isMesh||!o.material||Array.isArray(o.material)) return; const m=o.material;
      if(asph.has(m)) o.material=swap(m,()=>std({id:'asphalt',asph:1,tile:[0,0],m:6,tint:m.color.getHex(),k:.2,rough:1,metal:1,env:.9,ns:1.1}),'asphalt');
      else if(walkMap&&m.map===walkMap) o.material=swap(m,()=>std({id:'walk',tile:[1,0],m:3,k:.6,rough:1,metal:1,env:.8}),'walk');
      else if(sandMap&&m.map===sandMap) o.material=swap(m,()=>std({id:'sand_cove',tile:[0,1],m:4,tint:0xEDE8DC,k:.7,rough:1,metal:1,env:.6}),'sand_cove');
      else if(o.isInstancedMesh&&o.instanceColor&&m.isMeshToonMaterial&&!m.userData.pbrWorld){
        const a=o.instanceColor.array; let hit=0; for(let i=0;i<a.length;i+=3){ const r=a[i],g=a[i+1],b=a[i+2]; if((Math.abs(r-.929)<.01&&Math.abs(g-.910)<.01&&Math.abs(b-.863)<.01)||(Math.abs(r-.541)<.01&&Math.abs(g-.416)<.01&&Math.abs(b-.282)<.01)){ hit++; } }
        if(hit){ inject(m,{id:'box_sand_wood',tile:[0,0],m:3,mode:1,k:.6}); st.conv.box_sand_wood_instances=(st.conv.box_sand_wood_instances||0)+hit; } } });
    // bridges (slice 2): bridges.js fine InstancedMesh (mode 2 = every instance concrete-textured, instance tint kept),
    // createBridge deck (0x2a2d3a -> asphalt tile), parapets/joints/piers (concrete tile); toon materials swapped by identity (merge keys unchanged)
    if(typeof BRIDGES!=='undefined') for(const r of BRIDGES.list||[]) for(const im of r.meshes||[]){ if(im.userData.glow||im.material.userData.pbrWorld) continue;
      im.material=swap(im.material,()=>std({id:'bridge_fine',tile:[1,0],m:3,mode:2,k:.9,rough:1,metal:1,env:.9}),'bridge_fine'); }
    const BC={0x2a2d3a:{id:'bridge_deck',asph:1,tile:[0,0],m:6,tint:0x8a8f9c,k:.42,env:1.2},0x9b9890:{id:'bridge_parapet',tile:[1,0],m:3,tint:0x9b9890,k:.75,env:.8},0x6a6e78:{id:'bridge_joint',tile:[1,0],m:2,tint:0x6a6e78,k:.7,env:.8},
      0x85847f:{id:'bridge_conc',tile:[1,0],m:3,tint:0x85847f,k:.75,env:.8},0x74736e:{id:'bridge_conc2',tile:[1,0],m:3,tint:0x74736e,k:.75,env:.8}};
    scene.traverse(o=>{ const m=o.material; if(!o.isMesh||o.isInstancedMesh||!m||Array.isArray(m)||!m.isMeshToonMaterial||m.map||m.userData.pbrWorld) return; const c=BC[m.color.getHex()]; if(!c) return;
      o.material=swap(m,()=>std(Object.assign({rough:1,metal:1},c)),c.id); });
    // merged vertex-colour toon meshes (world_perf / staticMerge): bridge deck + parapet/joint/pier concrete live here after merging
    const VC=[[.165,.176,.227],[.522,.518,.498],[.455,.451,.431],[.608,.596,.565],[.416,.431,.471]];
    scene.traverse(o=>{ const m=o.material; if(!o.isMesh||o.isInstancedMesh||!m||Array.isArray(m)||!m.isMeshToonMaterial||!m.vertexColors||m.userData.pbrWorld) return; const ca=o.geometry&&o.geometry.attributes.color; if(!ca) return;
      const a=ca.array, st2=ca.itemSize; let hit=0; for(let i=0;i<a.length;i+=st2*3){ for(const v of VC) if(Math.abs(a[i]-v[0])<.012&&Math.abs(a[i+1]-v[1])<.012&&Math.abs(a[i+2]-v[2])<.012){ hit++; break; } }
      if(hit){ inject(m,{id:'merged_bridge_conc',tile:[0,0],m:4,mode:1,k:.6}); st.conv.merged_vc_tris=(st.conv.merged_vc_tris||0)+hit; } });
    // slice 4 (1): split bridge-deck triangles (vertex colour 0x2a2d3a, y<.05) out of the merged toon meshes into their own Mesh with a
    // dedicated MeshStandardMaterial (asphalt tile). Removed tris are collapsed in the source (degenerate), so geometry/draws there are unchanged.
    { const deckM=std({id:'bridge_deck_split',asph:1,tile:[0,0],m:6,tint:0xb0a898,k:.26,rough:1,metal:1,env:.9}); let nd=0, nmesh=0; const P=[], N=[], nm3=new THREE.Matrix3(), wn=new THREE.Vector3(); let lmask=null; /* 10/30 19:50: all deck tris merged (world space) into ONE mesh = 1 draw (was 4) */
      scene.traverse(o=>{ const m=o.material; if(!o.isMesh||o.isInstancedMesh||!m||Array.isArray(m)||!m.isMeshToonMaterial||!m.vertexColors||o.userData.pbrDeckSrc) return;
        let g=o.geometry; const ca=g.attributes.color, pa=g.attributes.position; if(!ca||!pa) return; o.updateMatrixWorld(true);
        const idx=g.index, n=idx?idx.count:pa.count, I=k=>idx?idx.getX(k):k, isD=v=>Math.abs(ca.getX(v)-.165)<.012&&Math.abs(ca.getY(v)-.176)<.012&&Math.abs(ca.getZ(v)-.227)<.012;
        const na=g.attributes.normal, wv=new THREE.Vector3(); nm3.getNormalMatrix(o.matrixWorld); let hit=0;
        for(let t=0;t<n;t+=3){ const a=I(t),b=I(t+1),c=I(t+2); if(!(isD(a)&&isD(b)&&isD(c))) continue; let ok=true; for(const v of [a,b,c]){ wv.fromBufferAttribute(pa,v).applyMatrix4(o.matrixWorld); if(wv.y>.05||wv.y<-.05) ok=false; } if(!ok) continue;
          for(const v of [a,b,c]){ wv.fromBufferAttribute(pa,v).applyMatrix4(o.matrixWorld); P.push(wv.x,wv.y,wv.z); if(na){ wn.fromBufferAttribute(na,v).applyMatrix3(nm3).normalize(); N.push(wn.x,wn.y,wn.z); } else N.push(0,1,0); }
          if(idx){ idx.setX(t+1,a); idx.setX(t+2,a); } else { for(const v of [b,c]) pa.setXYZ(v,pa.getX(a),pa.getY(a),pa.getZ(a)); } hit++; }
        if(!hit) return; if(idx) idx.needsUpdate=true; else pa.needsUpdate=true; o.userData.pbrDeckSrc=1;
        if(lmask===null) lmask=o.layers.mask; nd+=hit; nmesh++; });
      if(P.length){ const ng=new THREE.BufferGeometry(); ng.setAttribute('position',new THREE.Float32BufferAttribute(P,3)); ng.setAttribute('normal',new THREE.Float32BufferAttribute(N,3)); ng.computeBoundingSphere();
        const dm=new THREE.Mesh(ng,deckM); dm.matrixAutoUpdate=false; dm.updateMatrix(); dm.layers.mask=lmask; dm.name='pbr_bridge_deck'; scene.add(dm); dm.updateMatrixWorld(true); }
      st.conv.deck_src_meshes=nmesh; nmesh=P.length?1:0; st.conv.deck_split_tris=nd; st.conv.deck_split_meshes=nmesh; }
    // facades: page F detail on stucco (6) + brick (0), env cube, ACES chunk (ShaderMaterial has no tonemapping include)
    scene.traverse(o=>{ const m=o.material; if(!o.isMesh||!m||!m.isShaderMaterial||!m.uniforms||!m.uniforms.uFA||m.userData.pbrWorld) return; m.userData.pbrWorld='facade';
      m.uniforms.pbrFA=U.fA; m.uniforms.pbrFN=U.fN;
      let f=m.fragmentShader; const a='vec3 alb=texture2DGradEXT(uFA,auv,gx,gy).rgb; vec3 nr=texture2DGradEXT(uFN,auv,gx,gy).rgb;';
      if(f.indexOf(a)<0){ S.warn.push('facade anchor'); return; }
      f=f.replace('uniform sampler2D uFA, uFN;','uniform sampler2D uFA, uFN, pbrFA, pbrFN;').replace(a,a+`
        if(fm==6||fm==0){ vec2 duv=fract(tuv*.5); vec2 dsc=vec2(.5,1.)*(1.-2.*PAD); vec2 dv=(vec2(fm==0?1.:0.,0.)+PAD+duv*(1.-2.*PAD))*vec2(.5,1.); vec2 dgx=dFdx(tuv*.5)*dsc, dgy=dFdy(tuv*.5)*dsc;
          vec3 da=texture2DGradEXT(pbrFA,dv,dgx,dgy).rgb; vec3 dn=texture2DGradEXT(pbrFN,dv,dgx,dgy).rgb; float dl=dot(da,vec3(.3,.59,.11));
          alb*=mix(1.,clamp(dl/.45,.6,1.4),.45); nr.xy=mix(nr.xy,dn.xy,.4); }`);
      { const a2='vec3 o=mix(col*.92+emi*.62,avg,aa*.85);'; if(f.indexOf(a2)>=0) f=f.replace(a2,'emi*=mix(1.,.38,uDay); /* pbr: day-only window/door emissive cut, night unchanged */ { float cl=dot(col,vec3(.2126,.7152,.0722)); if(cl>.45) col*=(.45+.2*(1.-exp(-(cl-.45)/.2)))/cl; float al=dot(avg,vec3(.2126,.7152,.0722)); if(al>.45) avg*=(.45+.2*(1.-exp(-(al-.45)/.2)))/al; } /* pbr: glass/panel shoulder, emi untouched */\n        '+a2); else S.warn.push('facade shoulder anchor'); }
      f=f.replace(/gl_FragColor=vec4\(o,1\.\);(\s*)#include <fog_fragment>/,'gl_FragColor=vec4(o,1.);$1#include <tonemapping_fragment>$1#include <fog_fragment>$1if(dot(emi,vec3(.333))<.05||uDay>.5){ float pbrL=dot(gl_FragColor.rgb,vec3(.2126,.7152,.0722)); if(pbrL>.5) gl_FragColor.rgb*=(.5+.16*(1.-exp(-(pbrL-.5)/.16)))/pbrL; } /* pbr bloom guard, post tonemap+fog, non-emissive only */');
      m.fragmentShader=f; m.needsUpdate=true; st.conv.facade=(st.conv.facade||0)+1; });
    // neon / glow MeshBasic stays saturated (skip ACES shoulder)
    let nb=0; scene.traverse(o=>{ const m=o.material; if(o.isMesh&&m&&!Array.isArray(m)&&m.isMeshBasicMaterial&&m.toneMapped!==false&&(m.blending===THREE.AdditiveBlending||(m.color&&m.color.getHSL({}).s>.5))){ m.toneMapped=false; m.needsUpdate=true; nb++; } }); st.neonNoTM=nb;
    st.ms=+(performance.now()-T0).toFixed(1); }
  // ---- grade + fog (PBR path only)
  const GR={ exp:{night:1.1,day:1.0}, fog:{night:[60,360],day:[90,400]} };
  function dayV(){ try{ return typeof FACADE!=='undefined'?FACADE.uniforms.uDay.value:0; }catch(e){ return 0; } }
  function tick(){ const dv=dayV(), d=dv>.5?'day':'night'; WET.value=1.-.85*dv;
    /* day bloom tweaks removed 10/31: replaced by FXBLOOM in patch_xr_fxmem.py (Optimizer) */
    if(renderer){ renderer.toneMapping=THREE.ACESFilmicToneMapping; renderer.toneMappingExposure=GR.exp[d]; }
    if(scene&&scene.fog&&scene.fog.isFog){ scene.fog.near=GR.fog[d][0]; scene.fog.far=GR.fog[d][1]; }
    if(ENV.cur!==d&&ENV[d]){ ENV.cur=d; for(const m of S.mats){ m.envMap=ENV[d]; m.needsUpdate=true; } if(typeof FACADE!=='undefined'&&ENV.cube[d]) FACADE.uniforms.uEnv.value=ENV.cube[d]; } }
  function boot(){ tex('pbrG_albedo','gA'); tex('pbrG_nrm','gN'); tex('pbrG_orm','gO'); tex('pbrF_albedo','fA'); tex('pbrF_nrm','fN'); envLoad('day'); envLoad('night'); }
  S.install=function(){ if(typeof WORLD_PERF==='undefined'||!WORLD_PERF.run){ S.warn.push('no WORLD_PERF.run; converting on first tick'); return false; }
    const r0=WORLD_PERF.run; WORLD_PERF.run=function(){ const v=r0.apply(this,arguments); try{ convert(); }catch(e){ console.warn('pbr_world convert failed',e); S.warn.push('convert '+e); } return v; }; return true; };
  S.boot=boot; S.tick=tick; S.convert=convert; S.U=U; S.ENV=ENV; S.GR=GR; return S; })();
if(PBR_WORLD.on){ PBR_WORLD.boot(); const _pbrInstalled=PBR_WORLD.install(); let _pbrDone=_pbrInstalled; (function pbrLoop(){ try{ if(!_pbrDone&&typeof scene!=='undefined'&&scene&&scene.children.length>50){ _pbrDone=true; PBR_WORLD.convert(); } if(typeof renderer!=='undefined'&&renderer) PBR_WORLD.tick(); }catch(e){} requestAnimationFrame(pbrLoop); })(); }
window.PBR_WORLD=PBR_WORLD;
