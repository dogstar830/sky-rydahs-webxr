// ===== GRAFFITI SYSTEM (graffiti.js, injected by patch_graffiti.py) =====
// S tag / M throw-up / L piece + heaven spots on pre-placed quads (walls, benches, billboards, rooftops, street asphalt).
// Xbox pad only (SR_PAD): X near a spot = start (can rattle), RS gesture chain with rhythm (S 1, M 3, L 5 gestures), B cancel.
// LT aim: uses the targeting reticle hit point (TGT.aim / TGT.spot) to pick a spot from range (S/M only) and to aim the mist.
// Draw calls: 4 paint InstancedMeshes (brick, metal, glass, asphalt; one ShaderMaterial program each) + 1 halo/glow InstancedMesh
// + 1 spray-icon InstancedMesh + 1 shared mist Points pool (256) = 7 total, independent of spot count.
// Turf bridge: extends the existing TURF object (turf_dash.js) and publishes it as window.TURF (see TURF API doc below).
// Heat: no heat system existed, so window.HEAT is a minimal one (see below).
const GRAF={ ready:false, spots:[], bySurf:{brick:[],metal:[],glass:[],asphalt:[]}, meshes:{}, cur:null, saved:null, night:null, forceNight:null,
  SIZES:{ S:{pts:1,gest:1,w:1.5,h:.85,heat:.35,lock:0}, M:{pts:3,gest:3,w:3.4,h:1.8,heat:.8,lock:0}, L:{pts:10,gest:5,w:6.4,h:3.2,heat:1.6,lock:120} },
  RANGE:4.6, AIM_RANGE:14, BEAT:.22, REVEAL_RATE:2.5, stats:{started:0,done:0,cancel:0,timeouts:0,perfect:0} };
// ---- 10 crew palettes (base, dark, light, accent, neon). Pulled at runtime from TURF.crews / CREWS (crews.js) when present.
// Volt and Rust Claw are not in crews.js yet -> fallback palettes defined here.
const GRAF_CREWS=[
  {id:"codee",   name:"Code : E",        src:"codee"},
  {id:"karasu",  name:"Kogarasumaru",    src:"karasu"},
  {id:"static",  name:"Static Angels",   src:"static"},
  {id:"behemoth",name:"Behemoth",        src:"behemoth"},
  {id:"anubis",  name:"Anubis",          src:"anubis"},
  {id:"forest",  name:"Sleeping Forest", src:"forest"},
  {id:"genesis", name:"Genesis",         src:"genesis"},
  {id:"ttt",     name:"Tool Toul To",    src:"ttt"},
  {id:"volt",    name:"Volt",            base:"#ff2fa0", accent:"#ffe600", neon:"#ff2fa0", fallback:true},
  {id:"rustclaw",name:"Rust Claw",       base:"#ff6a1a", accent:"#8b3a1a", dark:"#8b3a1a", neon:"#ff6a1a", fallback:true} ];
function grafPalette(){ const C=THREE.Color, out=[];
  for(const c of GRAF_CREWS){ let base=c.base, neon=c.neon, accent=c.accent;
    if(!base){ try{ const t=TURF.crews.find(q=>q.id===c.src); if(t) base=t.css; }catch(e){}
      try{ const k=(typeof CREWS!=="undefined")&&CREWS.find(q=>q.garage===c.src); if(k){ const d=k.defaults; neon="#"+new C(d.wheelGlow).getHexString(); accent="#"+new C(d.gold).getHexString(); if(!base) base="#"+new C(d.jacket).getHexString(); } }catch(e){} }
    base=base||"#cccccc"; neon=neon||base; accent=accent||"#ffffff";
    const b=new C(base), hsl={}; b.getHSL(hsl);
    out.push({id:c.id,name:c.name,fallback:!!c.fallback,css:base,base:b,dark:c.dark?new C(c.dark):new C().setHSL(hsl.h,hsl.s,hsl.l*.42),light:new C().setHSL(hsl.h,Math.min(1,hsl.s*.9),Math.min(.9,hsl.l*.45+.5)),accent:new C(accent),neon:new C(neon)}); }
  out.push({id:null,name:"Neutral",css:"#8a8a8a",base:new C(0x8a8a8a),dark:new C(0x3a3a3a),light:new C(0xcfcfcf),accent:new C(0xffffff),neon:new C(0x9a9a9a)});
  return out; }
function grafCrewIdx(id){ const i=GRAF_CREWS.findIndex(c=>c.id===id); return i<0?10:i; }
// ---- helpers
function grafHash(a,b){ const s=Math.sin(a*12.9898+b*78.233)*43758.5453; return s-Math.floor(s); }
function grafNight(){ if(GRAF.forceNight!=null) return !!GRAF.forceNight; try{ if(typeof FACADE!=="undefined"&&FACADE.uniforms.uDay.value>.5) return false; const b=scene.background; return !b||!b.isColor||(b.r+b.g+b.b)<.9; }catch(e){ return true; } }
function grafDistrictOf(x,z){ try{ for(const q of PALMA.districts){ const b=q.box; if(x>=b[0]&&x<=b[2]&&z>=b[1]&&z<=b[3]) return q.name; } }catch(e){} return null; }
function grafFree(x,z){ try{ if(typeof onLand==="function"&&!onLand(x,z)) return false; }catch(e){} for(const c of colliders){ if(c.off) continue; if(x>c.minX-.3&&x<c.maxX+.3&&z>c.minZ-.3&&z<c.maxZ+.3) return false; } return true; }
// ---- atlas: 10 crews x 3 sizes (+neutral row), 256x128 cells, 4 cols x 8 rows on 1024x1024.
// R = fill, G = outline, B = 3D shadow + shines, A = reveal order (stroke order + noise). Colours applied in the shader per crew.
function grafAtlas(){ const W=1024, CW=256, CH=128, cv=document.createElement("canvas"); cv.width=W; cv.height=W;
  const layer=(fn)=>{ const c=document.createElement("canvas"); c.width=W; c.height=W; const x=c.getContext("2d"); fn(x); return x.getImageData(0,0,W,W).data; };
  const cells=[]; GRAF_CREWS.forEach((c,ci)=>["S","M","L"].forEach((sz,si)=>cells.push({ci,sz,si,txt:c.name.replace(/[^A-Za-z]/g,"").toUpperCase().slice(0,sz==="S"?4:sz==="M"?6:8),seed:ci*3+si})));
  const draw=(x,mode)=>{ cells.forEach((c,k)=>{ const ox=(k%4)*CW, oy=((k/4)|0)*CH; x.save(); x.beginPath(); x.rect(ox,oy,CW,CH); x.clip(); x.translate(ox+CW/2,oy+CH*.48);
      const fs=c.sz==="S"?46:c.sz==="M"?54:58, wd=c.sz==="S"?"italic 900 ":"900 "; x.font=wd+fs+"px Impact, 'Arial Black', sans-serif"; x.textAlign="center"; x.textBaseline="middle";
      let tw=x.measureText(c.txt).width, sc=Math.min(1,(CW-30)/tw); x.scale(sc,c.sz==="S"?1:1.25); x.rotate(c.sz==="S"?-.12:-.05);
      x.lineJoin="round"; x.lineCap="round";
      if(mode==="fill"){ if(c.sz==="S"){ x.lineWidth=3; x.strokeStyle="#fff"; x.strokeText(c.txt,0,0); x.fillStyle="#fff"; x.fillText(c.txt,0,0); }
        else { x.lineWidth=c.sz==="L"?16:12; x.strokeStyle="#fff"; x.strokeText(c.txt,0,0); x.fillStyle="#fff"; x.fillText(c.txt,0,0); } }
      if(mode==="outline"&&c.sz!=="S"){ x.lineWidth=c.sz==="L"?26:20; x.strokeStyle="#fff"; x.strokeText(c.txt,0,0); x.globalCompositeOperation="destination-out"; x.lineWidth=c.sz==="L"?16:12; x.strokeText(c.txt,0,0); x.fillText(c.txt,0,0); x.globalCompositeOperation="source-over"; }
      if(mode==="outline"&&c.sz==="S"){ x.lineWidth=2; x.strokeStyle="#fff"; x.beginPath(); x.moveTo(-tw*.5,fs*.55); x.quadraticCurveTo(0,fs*.9,tw*.55,fs*.45); x.stroke(); }
      if(mode==="d3"&&c.sz!=="S"){ x.fillStyle="#fff"; for(let i=1;i<=7;i++){ x.globalAlpha=.9; x.fillText(c.txt,i*1.6,i*1.6); } x.globalAlpha=1; x.globalCompositeOperation="destination-out"; x.lineWidth=c.sz==="L"?26:20; x.strokeText(c.txt,0,0); x.globalCompositeOperation="source-over";
        if(c.sz==="L"){ x.fillStyle="#fff"; for(let i=0;i<14;i++){ const a=grafHash(c.seed,i)*tw-tw/2, b=grafHash(i,c.seed)*fs-fs/2; x.fillRect(a,b-1.5,7,3); x.fillRect(a+2,b-4,3,9); } } }
      if(mode==="d3"&&c.sz==="S"){ x.fillStyle="#fff"; for(let i=0;i<6;i++){ x.fillRect(-tw/2+grafHash(c.seed,i)*tw,-fs*.4+grafHash(i,c.seed)*fs*.8,3,3); } }
      if(mode==="bg"&&c.sz==="L"){ x.fillStyle="#fff"; x.beginPath(); for(let i=0;i<9;i++){ const a=(i/9-.5)*tw*.95, r=fs*(.55+grafHash(c.seed,i)*.35); x.moveTo(a+r,0); x.arc(a,(grafHash(i,3)-.5)*fs*.4,r,0,7); } x.fill(); }
      x.restore(); }); };
  const F=layer(x=>draw(x,"fill")), O=layer(x=>draw(x,"outline")), D=layer(x=>draw(x,"d3")), BG=layer(x=>draw(x,"bg"));
  const ctx=cv.getContext("2d"), img=ctx.createImageData(W,W), d=img.data;
  for(let y=0;y<W;y++) for(let x=0;x<W;x++){ const i=(y*W+x)*4, cx=x%CW;
    const order=(cx/CW)*.75+grafHash(Math.floor(x/9),Math.floor(y/9))*.25; // left->right stroke order + blotchy noise
    d[i]=F[i+3]; d[i+1]=O[i+3]; d[i+2]=D[i+3]; d[i+3]=Math.round(order*255); }
  ctx.putImageData(img,0,0); const t=new THREE.CanvasTexture(cv); t.premultiplyAlpha=false; t.generateMipmaps=true; t.minFilter=THREE.LinearMipmapLinearFilter; t.anisotropy=2; return t; }
function grafNoise(){ const N=64, a=new Uint8Array(N*N*4); for(let i=0;i<N*N;i++){ const v=Math.random()*255; a[i*4]=v; a[i*4+1]=Math.random()*255; a[i*4+2]=Math.random()*255; a[i*4+3]=255; }
  const t=new THREE.DataTexture(a,N,N,THREE.RGBAFormat); t.wrapS=t.wrapT=THREE.RepeatWrapping; t.magFilter=THREE.LinearFilter; t.needsUpdate=true; return t; }
// ---- paint shader: one ShaderMaterial per surface (define switch) -> 4 programs, 4 draw calls.
const GRAF_SURF={ brick:{id:0,cut:.35,por:.5,drip:.25}, metal:{id:1,cut:.15,por:.1,drip:1.}, glass:{id:2,cut:0,por:.2,drip:.6}, asphalt:{id:3,cut:0,por:.7,drip:0} };
function grafMaterial(surf,U){
  const vs=`attribute vec4 aA; attribute vec4 aB; attribute vec2 aSz; varying vec2 vUv; varying vec4 vA; varying vec4 vB; varying vec2 vSz; varying float vFog;
  void main(){ vUv=uv; vA=aA; vB=aB; vSz=aSz; vec4 mv=modelViewMatrix*instanceMatrix*vec4(position,1.); vFog=-mv.z; gl_Position=projectionMatrix*mv; }`;
  const fs=`#define SURF ${GRAF_SURF[surf].id}
  uniform sampler2D uAtlas, uNoise; uniform vec3 uBase[11]; uniform vec3 uDark[11]; uniform vec3 uLight[11]; uniform vec3 uAcc[11]; uniform vec3 uNeon[11];
  uniform float uTime, uNight, uCut, uPor, uDripK; uniform vec3 uFogC; uniform float uFogD;
  varying vec2 vUv; varying vec4 vA; varying vec4 vB; varying vec2 vSz; varying float vFog;
  vec3 pal(int k,int i){ if(k==0) return uBase[i]; if(k==1) return uDark[i]; if(k==2) return uLight[i]; if(k==3) return uAcc[i]; return uNeon[i]; }
  vec3 P(int k,float f){ int i=int(f+.5); for(int j=0;j<11;j++){ if(j==i) return pal(k,j); } return vec3(.5); }
  void main(){
    float crew=vA.x, old=vA.y, prog=vA.z, cell=vA.w, drip=vB.x, t0=vB.y, layers=vB.z, lock=vB.w;
    vec2 w=vUv*vSz;                                   // metres across the quad
    // tag art occupies v in [.2,1]; below is the drip / overspray zone
    vec2 tuv=vec2(vUv.x,(vUv.y-.2)/.8); float inArt=step(0.,tuv.y);
    float c=floor(cell+.5); vec2 cel=vec2(mod(c,4.),floor(c/4.)); vec2 auv=(cel+vec2(clamp(tuv.x,.004,.996),1.-clamp(tuv.y,.004,.996)))*vec2(.25,.125); auv.y=1.-auv.y;
    vec4 art=texture2D(uAtlas,auv)*inArt;
    float cOld=floor(lock+.5); vec2 celO=vec2(mod(cOld,4.),floor(cOld/4.)); vec2 auvO=(celO+vec2(clamp(tuv.x,.004,.996),1.-clamp(tuv.y,.004,.996)))*vec2(.25,.125); auvO.y=1.-auvO.y;
    vec4 artO=texture2D(uAtlas,auvO)*inArt;
    vec4 nz=texture2D(uNoise,w*.9), nz2=texture2D(uNoise,w*3.7);
    // ---- surface backing + coverage mask (mortar / seams skip)
    vec3 base; float cover=1., rough=.9, alphaBase=1.; float spec=0.;
  #if SURF==0
    vec2 bw=w/vec2(.24,.075); bw.x+=step(1.,mod(bw.y,2.))*.5; vec2 f=fract(bw); float mortar=1.-step(.07,f.x)*step(.12,f.y);
    float h=mix(1.,.0,mortar)*(.7+.3*nz.r); cover=smoothstep(uCut,uCut+.1,h); base=mix(vec3(.46,.2,.15),vec3(.6,.3,.22),nz.g)*(1.-mortar*.45);
  #elif SURF==1
    float rib=sin(w.x*3.14159*6.); float seam=step(.97,fract(w.x/1.2)); cover=1.-seam*.9; base=vec3(.42,.45,.5)*(.82+.18*rib)+nz2.r*.03; spec=pow(max(rib,0.),6.); rough=.35;
  #elif SURF==2
    base=vec3(.08,.13,.17); alphaBase=.35; float streak=smoothstep(.6,1.,texture2D(uNoise,vec2(w.x*2.,w.y*.08)).r); cover=.75+.25*streak; rough=.2;
  #else
    base=vec3(.1); alphaBase=0.; cover=1.-.6*smoothstep(.55,.8,texture2D(uNoise,vec2(w.x*.05,w.y*1.2)).g); // skate/tyre wear lines
  #endif
    float por=mix(1.,smoothstep(.15,.85,nz2.g),uPor);
    // ---- reveal: layers fill -> outline -> 3D -> highlights, each with stroke-order mask
    float order=art.a; float L=max(layers,1.);
    float pf=clamp(prog*L,0.,1.), po=clamp(prog*L-1.,0.,1.), p3=clamp(prog*L-2.,0.,1.), ph=clamp(prog*L-3.,0.,1.);
    if(L<1.5){ po=pf; p3=pf; ph=pf; } else if(L<3.5){ po=clamp(prog*L-1.,0.,1.); p3=clamp(prog*L-2.,0.,1.); ph=p3; }
    float rf=rv(pf,order), ro=rv(po,order), r3=rv(p3,order);
    float aF=art.r*rf, aO=art.g*ro, a3=art.b*r3, aH=art.b*step(.5,art.b)*rv(ph,order)*step(3.5,L);
    float aPaint=max(max(aF,aO),a3);
    vec3 cc=mix(P(0,crew)*(.9+.2*art.r),P(1,crew),aO); cc=mix(cc,P(1,crew)*.7,a3*(1.-aO)*(1.-aF)); cc=mix(cc,mix(P(2,crew),P(3,crew),.5),aH*(1.-aO));
    // shading: overspray halo (5-15% of stroke) on the art edges
    float halo=(1.-smoothstep(0.,.5,abs(art.r-.5)))*.12*rf*step(.01,1.-aPaint);
    // drips: columns below painted strokes, length = drip * surface factor, growing after the tag finishes
    float colId=floor(vUv.x*48.); float dh=grafH(colId,c); float dl=drip*uDripK*(.25+dh*.75)*clamp((uTime-t0)*.5,0.,1.)*step(.55,dh);
    float dripA=step(vUv.y,.24)*step(.24-dl*.24,vUv.y)*(1.-smoothstep(.35,.5,abs(fract(vUv.x*48.)-.5)))*step(.001,prog);
    // old owner's tag shows where the new one has not covered yet
    float aOld=max(artO.r,artO.g)*step(lock,50.)*(1.-step(.01,aPaint));
    vec3 oc=P(0,old);
    float a=clamp(aPaint*cover*por+halo*por+dripA*.9,0.,1.);
    vec3 pc=mix(cc,P(1,crew),dripA*.3);
  #if SURF==3
    pc=mix(pc,vec3(dot(pc,vec3(.33))),.35)*.8*(.85+.3*nz2.r); // asphalt: matte, darker, desaturated, grit
  #endif
    vec3 outc=mix(base,oc*(.8+.2*nz.r),aOld*cover*.85); outc=mix(outc,pc,a);
    // neon at night: emissive crew tint on paint (brick faces only, metal ribs streak, glass backlight)
    vec3 neon=P(4,crew)*uNight*a;
  #if SURF==0
    neon*=cover*.55;
  #elif SURF==1
    neon*=.35+spec*1.2; outc+=spec*(.05+uNight*.25)*mix(vec3(1.),P(4,crew),a);
  #elif SURF==2
    neon*=.9; outc+=P(4,crew)*a*.25*uNight;
  #else
    neon*=.12;
  #endif
    outc+=neon*.3;
    float alpha=max(alphaBase,a*(SURF==2?.7:1.))+aOld*cover*.85*(1.-alphaBase);
  #if SURF==3
    if(alpha<.5) discard; alpha=1.;
  #elif SURF!=2
    alpha=1.;
  #endif
    float fg=1.-exp(-uFogD*uFogD*vFog*vFog); outc=mix(outc,uFogC,clamp(fg,0.,1.));
    gl_FragColor=vec4(outc,alpha); }`;
  const fs2=fs.replace("void main(){","float grafH(float a,float b){ return fract(sin(a*12.9898+b*78.233)*43758.5453); }\n  float rv(float p,float o){ return step(.001,p)*(1.-smoothstep(p*1.08-.06,p*1.08,o)); }\n  void main(){");
  const m=new THREE.ShaderMaterial({ uniforms:Object.assign({},U,{ uCut:{value:GRAF_SURF[surf].cut}, uPor:{value:GRAF_SURF[surf].por}, uDripK:{value:GRAF_SURF[surf].drip} }), vertexShader:vs, fragmentShader:fs2,
    transparent:surf==="glass", depthWrite:surf!=="glass", polygonOffset:true, polygonOffsetFactor:-1, polygonOffsetUnits:-1, side:THREE.FrontSide });
  // asphalt uses discard (alphaTest-like); glass blends after opaques
  if(surf==="glass") m.renderOrder=2; return m; }
// ---- spot placement from world geometry (deterministic): building walls (M), rooftop billboards (L heaven), benches/low walls (S), street asphalt (S/M).
function grafPlace(){ const out=[], used=[]; let n=0; const far=(x,z,r)=>used.every(u=>Math.hypot(u[0]-x,u[1]-z)>r)&&TURF.spots.every(s=>Math.hypot(s.x-x,s.z-z)>2.6);
  const add=(o)=>{ o.id="g"+(n++); o.district=grafDistrictOf(o.x,o.z); if(!o.district) return; used.push([o.x,o.z]); out.push(o); };
  const faces=[]; if(typeof B!=="undefined"&&B.pos) B.pos.forEach((p,i)=>{ const [w,h,d]=B.size[i], by=(B.y&&typeof B.y[i]==="number")?B.y[i]:0;
    for(const [nx,nz,hw] of [[1,0,w/2],[-1,0,w/2],[0,1,d/2],[0,-1,d/2]]){ const len=nx?d:w, fx=p[0]+nx*(nx?w/2:0), fz=p[1]+nz*(nz?d/2:0);
      if(len<4) continue; if(!grafFree(fx+nx*2,fz+nz*2)) continue; faces.push({i,x:fx,z:fz,nx,nz,len,h,by,dist:grafDistrictOf(fx,fz)}); } });
  const byD={}; for(const f of faces){ if(!f.dist) continue; (byD[f.dist]=byD[f.dist]||[]).push(f); }
  let k=0; const surfCycle=["brick","metal","glass","brick","metal"];
  for(const dn of Object.keys(byD).sort()){ const L=byD[dn].sort((a,b)=>grafHash(a.x,a.z)-grafHash(b.x,b.z)); let nl=0, nm=0, ns=0, na=0;
    for(const f of L){ const tx=-f.nz, tz=f.nx;
      // L heaven spot: billboard on the roof edge of a mid-rise (reachable by grapple decks / ladders), facing the street
      if(nl<1&&f.h>=5.5&&f.h<=16&&f.len>=8&&far(f.x,f.z,6)){ add({size:"L",surf:k%2?"metal":"brick",x:f.x+f.nx*.07,z:f.z+f.nz*.07,y:f.by+f.h+1.75,nx:f.nx,nz:f.nz,roof:f.by+f.h,heaven:true,kind:k%2?"billboard":"rooftop"}); nl++; k++; continue; }
      if(nm<2&&f.len>=5&&far(f.x,f.z,5)){ const s=surfCycle[(k++)%surfCycle.length]; add({size:"M",surf:s,x:f.x+f.nx*.07+tx*(f.len*.2),z:f.z+f.nz*.07+tz*(f.len*.2),y:1.55,nx:f.nx,nz:f.nz,kind:s==="glass"?"storefront":s==="metal"?"shutter":"wall"}); nm++; continue; }
      if(ns<2&&far(f.x-tx*f.len*.3,f.z-tz*f.len*.3,4)){ add({size:"S",surf:ns%2?"metal":"brick",x:f.x+f.nx*.07-tx*f.len*.3,z:f.z+f.nz*.07-tz*f.len*.3,y:.9,nx:f.nx,nz:f.nz,kind:ns%2?"utility box":"bench wall"}); ns++; continue; }
      if(na<1){ const ax=f.x+f.nx*4.2, az=f.z+f.nz*4.2; if(grafFree(ax,az)&&far(ax,az,4)){ add({size:na?"S":"M",surf:"asphalt",x:ax,z:az,y:.035,nx:f.nx,nz:f.nz,ground:true,kind:"street"}); na++; continue; } } } }
  return out; }
// ---- build meshes
function grafInit(){ const PAL=GRAF.pal=grafPalette();
  GRAF.spots=grafPlace(); GRAF.flushed=(typeof turfFlush==='function')?turfFlush(GRAF.spots,s=>s.ground?null:s.y):[]; // same wall-penetration fix as legacy turf (x/z only, ids kept)
  const atlas=grafAtlas(), noise=grafNoise();
  const U={ uAtlas:{value:atlas}, uNoise:{value:noise}, uTime:{value:0}, uNight:{value:1}, uFogC:{value:new THREE.Color(0x000000)}, uFogD:{value:0},
    uBase:{value:PAL.map(p=>p.base)}, uDark:{value:PAL.map(p=>p.dark)}, uLight:{value:PAL.map(p=>p.light)}, uAcc:{value:PAL.map(p=>p.accent)}, uNeon:{value:PAL.map(p=>p.neon)} };
  GRAF.U=U; const m4=new THREE.Matrix4(), q=new THREE.Quaternion(), e=new THREE.Euler(), v=new THREE.Vector3(), s=new THREE.Vector3();
  for(const k in GRAF.bySurf) GRAF.bySurf[k]=[];
  GRAF.spots.forEach(sp=>{ GRAF.bySurf[sp.surf].push(sp); const Z=GRAF.SIZES[sp.size]; sp.w=Z.w; sp.h=Z.h*1.25; sp.owner=null; sp.old=null; sp.prog=0; sp.drip=0; sp.t0=-99; sp.lockUntil=0;
    sp.cellFor=crew=>grafCrewIdx(crew)*3+["S","M","L"].indexOf(sp.size); });
  for(const surf in GRAF.bySurf){ const L=GRAF.bySurf[surf], N=Math.max(1,L.length);
    const g=new THREE.InstancedBufferGeometry().copy(new THREE.PlaneGeometry(1,1)); g.instanceCount=L.length;
    const aA=new THREE.InstancedBufferAttribute(new Float32Array(N*4),4), aB=new THREE.InstancedBufferAttribute(new Float32Array(N*4),4), aSz=new THREE.InstancedBufferAttribute(new Float32Array(N*2),2);
    aA.setUsage(THREE.DynamicDrawUsage); aB.setUsage(THREE.DynamicDrawUsage); g.setAttribute("aA",aA); g.setAttribute("aB",aB); g.setAttribute("aSz",aSz);
    const mesh=new THREE.InstancedMesh(g,grafMaterial(surf,U),N); mesh.count=L.length; mesh.frustumCulled=false; mesh.renderOrder=surf==="glass"?3:1; mesh.name="graffiti_"+surf;
    L.forEach((sp,i)=>{ sp.mi=i; v.set(sp.x,sp.y,sp.z); if(sp.ground){ e.set(-Math.PI/2,0,Math.atan2(sp.nx,sp.nz)+Math.PI,"YXZ"); e.set(-Math.PI/2,0,0); q.setFromEuler(new THREE.Euler(-Math.PI/2,Math.atan2(sp.nx,sp.nz),0,"YXZ")); }
      else q.setFromEuler(e.set(0,Math.atan2(sp.nx,sp.nz),0)); s.set(sp.w,sp.h,1); m4.compose(v,q,s); mesh.setMatrixAt(i,m4); aSz.array[i*2]=sp.w; aSz.array[i*2+1]=sp.h; });
    GRAF.meshes[surf]={mesh,aA,aB}; scene.add(mesh); }
  // halo / night glow quads (one per spot, soft additive) + glass backlight floor pools: 1 draw call
  { const L=GRAF.spots, NG=L.length+GRAF.bySurf.glass.length, g=new THREE.InstancedBufferGeometry().copy(new THREE.PlaneGeometry(1,1)); g.instanceCount=NG;
    const aC=new THREE.InstancedBufferAttribute(new Float32Array(NG*4),4); aC.setUsage(THREE.DynamicDrawUsage); g.setAttribute("aC",aC);
    const mat=new THREE.ShaderMaterial({ uniforms:{uNight:U.uNight,uTime:U.uTime}, transparent:true, depthWrite:false, blending:THREE.AdditiveBlending,
      vertexShader:"attribute vec4 aC; varying vec2 vUv; varying vec4 vC; void main(){ vUv=uv; vC=aC; gl_Position=projectionMatrix*modelViewMatrix*instanceMatrix*vec4(position,1.); }",
      fragmentShader:"uniform float uNight,uTime; varying vec2 vUv; varying vec4 vC; void main(){ vec2 d=(vUv-.5)*2.; float r=dot(d,d); float a=exp(-r*2.6)*vC.a*uNight*(.85+.15*sin(uTime*2.+vC.r*9.)); if(a<.003) discard; gl_FragColor=vec4(vC.rgb*a,1.); }" });
    const mesh=new THREE.InstancedMesh(g,mat,NG); mesh.frustumCulled=false; mesh.renderOrder=4; mesh.name="graffiti_glow";
    L.forEach((sp,i)=>{ v.set(sp.x+sp.nx*(sp.ground?0:.12),sp.y+(sp.ground?.02:0),sp.z+sp.nz*(sp.ground?0:.12)); if(sp.ground) q.setFromEuler(new THREE.Euler(-Math.PI/2,0,0)); else q.setFromEuler(e.set(0,Math.atan2(sp.nx,sp.nz),0)); s.set(sp.w*1.5,sp.h*1.6,1); m4.compose(v,q,s); mesh.setMatrixAt(i,m4); sp.gi=i; });
    GRAF.bySurf.glass.forEach((sp,j)=>{ const i=L.length+j; v.set(sp.x+sp.nx*1.6,.03,sp.z+sp.nz*1.6); q.setFromEuler(new THREE.Euler(-Math.PI/2,0,0)); s.set(sp.w*1.2,2.6,1); m4.compose(v,q,s); mesh.setMatrixAt(i,m4); sp.gi2=i; });
    GRAF.glow={mesh,aC}; scene.add(mesh); }
  // spray-tag icons above each spot (can + mist puff), colour = owner, grey = neutral: 1 draw call
  { const c=document.createElement("canvas"); c.width=c.height=64; const x=c.getContext("2d"); x.fillStyle="#fff"; x.fillRect(22,22,18,34); x.fillRect(26,14,10,8); x.fillRect(29,8,4,6);
    for(let i=0;i<14;i++){ x.globalAlpha=.6; x.beginPath(); x.arc(44+Math.random()*14,8+Math.random()*12,1.5+Math.random()*2.5,0,7); x.fill(); } x.globalAlpha=1; x.strokeStyle="#000"; x.lineWidth=2; x.strokeRect(22,22,18,34);
    const tex=new THREE.CanvasTexture(c), N=GRAF.spots.length, g=new THREE.InstancedBufferGeometry().copy(new THREE.PlaneGeometry(.7,.7)); g.instanceCount=N;
    const aC=new THREE.InstancedBufferAttribute(new Float32Array(N*4),4); aC.setUsage(THREE.DynamicDrawUsage); g.setAttribute("aC",aC);
    const mat=new THREE.ShaderMaterial({ uniforms:{uMap:{value:tex},uTime:U.uTime}, transparent:false, alphaTest:.5,
      vertexShader:"attribute vec4 aC; varying vec2 vUv; varying vec4 vC; uniform float uTime; void main(){ vUv=uv; vC=aC; vec4 c=modelViewMatrix*instanceMatrix*vec4(0.,sin(uTime*2.+aC.w*7.)*.08,0.,1.); c.xy+=position.xy*(aC.w>0.?1.:0.); gl_Position=projectionMatrix*c; }",
      fragmentShader:"uniform sampler2D uMap; varying vec2 vUv; varying vec4 vC; void main(){ vec4 t=texture2D(uMap,vUv); if(t.a<.5) discard; gl_FragColor=vec4(vC.rgb*t.r+.04,1.); }" });
    const mesh=new THREE.InstancedMesh(g,mat,N); mesh.frustumCulled=false; mesh.name="graffiti_icons";
    GRAF.spots.forEach((sp,i)=>{ v.set(sp.x+sp.nx*.5,(sp.ground?1.4:sp.y+sp.h*.5+.5),sp.z+sp.nz*.5); m4.makeTranslation(v.x,v.y,v.z); mesh.setMatrixAt(i,m4); sp.ii=i; });
    GRAF.icons={mesh,aC}; scene.add(mesh); }
  // shared mist particle pool: 256 points, additive soft sprites, CPU ring buffer (<=64 per active can)
  { const N=256, g=new THREE.BufferGeometry(), pos=new Float32Array(N*3), col=new Float32Array(N*4);
    g.setAttribute("position",new THREE.BufferAttribute(pos,3).setUsage(THREE.DynamicDrawUsage)); g.setAttribute("aCol",new THREE.BufferAttribute(col,4).setUsage(THREE.DynamicDrawUsage));
    const mat=new THREE.ShaderMaterial({ transparent:true, depthWrite:false, blending:THREE.AdditiveBlending,
      vertexShader:"attribute vec4 aCol; varying vec4 vC; void main(){ vC=aCol; vec4 mv=modelViewMatrix*vec4(position,1.); gl_PointSize=clamp((90.+aCol.a*160.)/max(.5,-mv.z),1.,64.); gl_Position=projectionMatrix*mv; }",
      fragmentShader:"varying vec4 vC; void main(){ vec2 d=gl_PointCoord-.5; float a=smoothstep(.5,0.,length(d))*vC.a*.55; if(a<.01) discard; gl_FragColor=vec4(vC.rgb*a,1.); }" });
    const pts=new THREE.Points(g,mat); pts.frustumCulled=false; pts.renderOrder=5; pts.name="graffiti_mist";
    GRAF.mist={pts,pos,col,vel:new Float32Array(N*3),life:new Float32Array(N),max:new Float32Array(N),base:new Float32Array(N*3),n:N,i:0,alive:0,perCan:64}; scene.add(pts); }
  for(const sp of GRAF.spots) grafWrite(sp);
  grafTurfBridge(); GRAF.ready=true; }
function grafWrite(sp){ const M=GRAF.meshes[sp.surf]; if(!M) return; const i=sp.mi, A=M.aA.array, Bv=M.aB.array, crew=sp.paintFor!=null?sp.paintFor:sp.owner;
  const idx=grafCrewIdx(crew), oldIdx=sp.paintFor!=null?grafCrewIdx(sp.owner):10;
  // aA = (crew colour idx, old crew colour idx, reveal progress, atlas cell); aB = (drip, paint time, layers, old atlas cell or 99)
  const hasOld=sp.paintFor!=null&&sp.owner!=null;
  A[i*4]=idx; A[i*4+1]=hasOld?oldIdx:10; A[i*4+2]=crew==null?0:(sp.paintFor!=null?sp.prog:(sp.disp!=null?sp.disp:1)); A[i*4+3]=sp.cellFor(crew||GRAF_CREWS[0].id);
  Bv[i*4]=sp.drip; Bv[i*4+1]=sp.t0; Bv[i*4+2]={S:1,M:3,L:4}[sp.size]; Bv[i*4+3]=hasOld?sp.cellFor(sp.owner):99;
  M.aA.needsUpdate=M.aB.needsUpdate=true;
  const G=GRAF.glow; if(G){ const p=GRAF.pal[idx], on=crew!=null&&(sp.paintFor==null||sp.prog>.2); const set=(j,k)=>{ G.aC.array[j*4]=p.neon.r; G.aC.array[j*4+1]=p.neon.g; G.aC.array[j*4+2]=p.neon.b; G.aC.array[j*4+3]=on?k:0; };
    set(sp.gi,sp.surf==="asphalt"?.12:sp.size==="L"?.22:.18); if(sp.gi2!=null) set(sp.gi2,.55); G.aC.needsUpdate=true; }
  const I=GRAF.icons; if(I){ const p=GRAF.pal[grafCrewIdx(sp.owner)]; I.aC.array[sp.ii*4]=p.base.r; I.aC.array[sp.ii*4+1]=p.base.g; I.aC.array[sp.ii*4+2]=p.base.b; I.aC.array[sp.ii*4+3]=sp.owner===GRAF.me()?0:1+sp.ii*.01; I.aC.needsUpdate=true; } }
GRAF.me=()=>{ try{ return TURF.crews[TURF.me].id; }catch(e){ return "codee"; } };
// the old-tag art cell: shader reads vA.y as both colour index and (when <11) the cell row of that crew's same-size design
// ---- mist
function grafMist(from,to,crewIdx,n){ const M=GRAF.mist, p=GRAF.pal[crewIdx]; let alive=0; for(let i=0;i<M.n;i++) if(M.life[i]>0) alive++; M.alive=alive;
  for(let k=0;k<n;k++){ if(alive>=M.perCan*(GRAF.remote?2:1)) break; const i=M.i=(M.i+1)%M.n; alive++;
    const dx=to.x-from.x, dy=to.y-from.y, dz=to.z-from.z, L=Math.hypot(dx,dy,dz)||1, sp=4.5+Math.random()*2.5, cone=.22;
    M.pos[i*3]=from.x; M.pos[i*3+1]=from.y; M.pos[i*3+2]=from.z;
    M.vel[i*3]=dx/L*sp+(Math.random()-.5)*sp*cone; M.vel[i*3+1]=dy/L*sp+(Math.random()-.5)*sp*cone; M.vel[i*3+2]=dz/L*sp+(Math.random()-.5)*sp*cone;
    M.base[i*3]=p.base.r; M.base[i*3+1]=p.base.g; M.base[i*3+2]=p.base.b; M.life[i]=M.max[i]=.45+Math.random()*.3; } }
function grafMistUpdate(dt){ const M=GRAF.mist; let any=false; for(let i=0;i<M.n;i++){ if(M.life[i]<=0){ if(M.col[i*4+3]!==0){ M.col[i*4+3]=0; any=true; } continue; } any=true;
    M.life[i]-=dt; const k=Math.max(0,M.life[i]/M.max[i]); for(let a=0;a<3;a++){ M.vel[i*3+a]*=Math.exp(-dt*3.2); M.pos[i*3+a]+=M.vel[i*3+a]*dt; }
    M.pos[i*3+1]-=dt*.15; M.col[i*4]=M.base[i*3]; M.col[i*4+1]=M.base[i*3+1]; M.col[i*4+2]=M.base[i*3+2]; M.col[i*4+3]=k*(1-k)*4*.9; }
  if(any){ M.pts.geometry.attributes.position.needsUpdate=true; M.pts.geometry.attributes.aCol.needsUpdate=true; } M.pts.visible=any; }
// ---- procedural WebAudio: can rattle (ball bearing), hiss loop pitched by stick speed, cap pfft
function grafAC(){ try{ if(typeof gateAudio==="function"){ const a=gateAudio(); if(a) return a; } }catch(e){} try{ if(!GRAF.ac) GRAF.ac=new (window.AudioContext||window.webkitAudioContext)(); return GRAF.ac; }catch(e){ return null; } }
function grafNoiseBuf(ac){ if(GRAF.nb&&GRAF.nb.sampleRate===ac.sampleRate) return GRAF.nb; const n=ac.sampleRate, b=ac.createBuffer(1,n,n), d=b.getChannelData(0); for(let i=0;i<n;i++) d[i]=Math.random()*2-1; return GRAF.nb=b; }
function grafRattle(){ const ac=grafAC(); if(!ac) return; try{ const t=ac.currentTime; for(let i=0;i<9;i++){ const s=ac.createBufferSource(); s.buffer=grafNoiseBuf(ac); const f=ac.createBiquadFilter(); f.type="bandpass"; f.frequency.value=3200+Math.random()*1800; f.Q.value=9; const g=ac.createGain(); const ti=t+i*.055+Math.random()*.01;
      g.gain.setValueAtTime(0,ti); g.gain.linearRampToValueAtTime(.35,ti+.004); g.gain.exponentialRampToValueAtTime(.001,ti+.05); s.connect(f); f.connect(g); g.connect(ac.destination); s.start(ti,Math.random()*.5,.06); } GRAF.sfx=(GRAF.sfx||0)+1; }catch(e){} }
function grafHiss(level,speed){ const ac=grafAC(); if(!ac) return; try{ if(!GRAF.hiss){ const s=ac.createBufferSource(); s.buffer=grafNoiseBuf(ac); s.loop=true; const f=ac.createBiquadFilter(); f.type="bandpass"; f.Q.value=.8; f.frequency.value=5000; const g=ac.createGain(); g.gain.value=0; s.connect(f); f.connect(g); g.connect(ac.destination); s.start(); GRAF.hiss={s,f,g}; }
    const H=GRAF.hiss, t=ac.currentTime; H.g.gain.setTargetAtTime(level*.22,t,.03); H.f.frequency.setTargetAtTime(3800+speed*3200,t,.05); H.s.playbackRate.setTargetAtTime(.85+speed*.4,t,.05); }catch(e){} }
function grafPfft(){ const ac=grafAC(); if(!ac) return; try{ const t=ac.currentTime, s=ac.createBufferSource(); s.buffer=grafNoiseBuf(ac); const f=ac.createBiquadFilter(); f.type="highpass"; f.frequency.value=2500; const g=ac.createGain(); g.gain.setValueAtTime(.3,t); g.gain.exponentialRampToValueAtTime(.001,t+.18); s.connect(f); f.connect(g); g.connect(ac.destination); s.start(t,0,.2); GRAF.sfx=(GRAF.sfx||0)+1; }catch(e){} grafHiss(0,0); }
// ---- gestures: each is a sequence of 8-way RS directions (0=right,2=up,4=left,6=down); rhythm = BEAT seconds per step
const GRAF_GEST=[ {n:"FLICK →",d:[0]}, {n:"FLICK ↑",d:[2]}, {n:"HALF-CIRCLE ↻",d:[2,0,6]}, {n:"HALF-CIRCLE ↺",d:[2,4,6]}, {n:"ZIG",d:[4,0,4]}, {n:"FLICK ←",d:[4]}, {n:"SWOOP",d:[6,0,2]}, {n:"ARC ↷",d:[4,2,0]} ];
function grafPlan(sp){ const N=GRAF.SIZES[sp.size].gest, L=[]; for(let i=0;i<N;i++){ const h=grafHash(sp.x+i,sp.z-i*3); L.push(sp.size==="S"?GRAF_GEST[h<.5?0:1]:GRAF_GEST[2+Math.floor(h*6)%6]); } return L; }
function grafDir(x,y){ return ((Math.round(Math.atan2(-y,x)/(Math.PI/4))%8)+8)%8; }
// ---- spot selection: proximity (facing side), or LT reticle hit point from range
function grafAimPoint(){ try{ if(window.TGT&&TGT.aiming&&TGT.aim) return {x:TGT.aim.x,y:TGT.aim.y||1.5,z:TGT.aim.z,src:"reticle"}; }catch(e){} return null; }
function grafFind(){ const p=Ride.group.position, me=GRAF.me(); let best=null, bd=1e9; const aim=grafAimPoint();
  for(const sp of GRAF.spots){ if(sp.owner===me||sp.lockUntil>clock) continue; const dx=p.x-sp.x, dz=p.z-sp.z, d=Math.hypot(dx,dz);
    const front=sp.ground||dx*sp.nx+dz*sp.nz>-.2, dy=sp.heaven?Math.abs(p.y-sp.roof):0;
    if(d<=GRAF.RANGE+(sp.size==="L"?1.5:0)&&front&&dy<2.5&&d<bd){ bd=d; best=sp; } }
  if(!best&&aim){ const ay=Math.atan2(aim.x-p.x,aim.z-p.z), ad=(a,b)=>{ let d=(a-b)%(2*Math.PI); if(d>Math.PI) d-=2*Math.PI; if(d<-Math.PI) d+=2*Math.PI; return Math.abs(d); };
    for(const sp of GRAF.spots){ if(sp.owner===me||sp.size==="L"||sp.lockUntil>clock) continue; const dx=sp.x-p.x, dz=sp.z-p.z, dr=Math.hypot(dx,dz);
      if(dr>GRAF.AIM_RANGE||dr<1) continue; if(!sp.ground&&(p.x-sp.x)*sp.nx+(p.z-sp.z)*sp.nz<0) continue;
      const da=ad(Math.atan2(dx,dz),ay), tol=Math.atan2(sp.w*.6,dr)+.05; if(da<tol&&da<bd){ bd=da; best=sp; } } if(best) best._aimed=true; }
  return best; }
// ---- tag state machine
function grafStart(sp){ const me=GRAF.me(); GRAF.cur={sp,phase:"shake",t:0,plan:grafPlan(sp),gi:0,step:0,gt:0,score:0,perfect:0,drip:0,aimed:!!sp._aimed}; delete sp._aimed;
  sp.paintFor=me; sp.prog=0; sp.drip=0; GRAF.stats.started++; grafRattle(); grafWrite(sp); grafHud(); }
function grafCancel(why){ const C=GRAF.cur; if(!C) return; const sp=C.sp; delete sp.paintFor; sp.prog=0; grafWrite(sp); GRAF.cur=null; GRAF.stats.cancel++; if(why==="timeout") GRAF.stats.timeouts++; grafPfft(); grafHud(); GRAF.lastEvent="cancel:"+why;
  try{ flash(why==="timeout"?"PAINT DRIED":"TAG CANCELLED","#888"); }catch(e){} }
function grafComplete(){ const C=GRAF.cur, sp=C.sp, me=GRAF.me(), Z=GRAF.SIZES[sp.size]; const prev=sp.owner;
  sp.old=prev; sp.owner=me; delete sp.paintFor; sp.disp=Math.min(sp.prog,.999); sp.prog=1; sp.drip=Math.min(1,C.drip); sp.t0=clock; if(Z.lock) sp.lockUntil=clock+Z.lock; sp.tagT=Date.now();
  const burner=C.perfect===C.plan.length&&C.plan.length>=3, pts=Z.pts+(burner?Math.ceil(Z.pts*.5):0);
  GRAF.cur=null; GRAF.stats.done++; if(burner) GRAF.stats.perfect++; grafWrite(sp); grafPfft(); grafHud();
  try{ Stats.tags++; bumpChain(); if(typeof DASH!=="undefined") DASH.meter=Math.min(1,DASH.meter+(sp.size==="L"?.3:.12)); }catch(e){}
  try{ flash(burner?"BURNER!":sp.size==="L"?(sp.heaven?"HEAVEN SPOT!":"PIECE!"):sp.size==="M"?"THROW-UP":"TAGGED",GRAF.pal[grafCrewIdx(me)].css); }catch(e){}
  try{ SR_PAD.rumble(.4,.7,120); }catch(e){}
  // heat: night tags raise it, bigger + billboards more; day ~15%
  const night=grafNight(); HEAT.add(Z.heat*(sp.kind==="billboard"?1.5:1)*(night?1:.15),"tag:"+sp.size);
  grafTurfAdd(sp,me,prev,pts); GRAF.lastEvent="done:"+sp.id; }
function grafUpdateTag(dt){ const C=GRAF.cur; if(!C) return; const sp=C.sp, S=window.SR_PAD;
  if(!S||!S.active()){ grafCancel("pad"); return; }
  if(S.justPressed("B")){ grafCancel("B"); return; }
  const p=Ride.group.position, d=Math.hypot(p.x-sp.x,p.z-sp.z); if(d>(C.aimed?GRAF.AIM_RANGE:GRAF.RANGE)+2.5){ grafCancel("left"); return; }
  try{ Ride.speed*=Math.exp(-dt*6); }catch(e){}
  C.t+=dt; const rs=S.stick("right"), m=Math.hypot(rs.x,rs.y);
  if(C.phase==="shake"){ if(C.t>=.45){ C.phase="gesture"; C.gt=0; C.step=0; } grafHud(); return; }
  const G=C.plan[C.gi]; C.gt+=dt;
  if(m>.6){ const dir=grafDir(rs.x,rs.y), want=G.d[C.step], diff=Math.min((dir-want+8)%8,(want-dir+8)%8);
    if(diff<=(G.d.length===1?1:0)&&dir!==C.lastDir) C.step++; C.lastDir=dir; }
  else if(m<.25) C.lastDir=null;
  const spd=m>.25?Math.min(1,Math.hypot(rs.x-(C.prs?C.prs.x:0),rs.y-(C.prs?C.prs.y:0))/dt*.08):0; C.prs={x:rs.x,y:rs.y};
  grafHiss(m>.25?1:0,spd);
  if(m>.25&&frame%2===0){ const aim=C.aimed&&grafAimPoint(); const from={x:p.x+Math.sin(Ride.yaw)*.4,y:p.y+1.35,z:p.z+Math.cos(Ride.yaw)*.4};
    const to=aim?aim:{x:sp.x+(rs.x*.3)*(-sp.nz)*sp.w,y:sp.ground?.05:sp.y+rs.y*-.3*sp.h,z:sp.z+(rs.x*.3)*sp.nx*sp.w}; grafMist(from,to,grafCrewIdx(GRAF.me()),3); }
  const frac=(C.gi+Math.min(1,C.step/G.d.length))/C.plan.length; sp.prog+=(frac-sp.prog)*Math.min(1,dt*10); grafWrite(sp);
  if(C.step>=G.d.length){ // rhythm: ideal duration = steps x BEAT (+ reaction 0.25 s); too fast or too slow -> drips
    const ideal=G.d.length*GRAF.BEAT+.25, r=C.gt/ideal; let q=1; if(r<.45) q=.4; else if(r>2.6) q=.3; else if(r>1.7) q=.7;
    if(q===1) C.perfect++; C.drip+=(1-q)*.9+(sp.surf==="metal"?.15:0); C.score+=q; C.gi++; C.step=0; C.gt=0; C.lastDir=null; GRAF.lastGesture={q,r:+r.toFixed(2)};
    if(C.gi>=C.plan.length){ sp.prog=1; grafComplete(); return; } }
  else if(C.gt>4){ grafCancel("timeout"); return; }
  grafHud(); }
// ---- HUD prompt (desktop overlay; XR shows the paint reveal + mist + icon)
function grafHud(){ let el=document.getElementById("grafHud"); if(!el){ el=document.createElement("div"); el.id="grafHud"; el.className="hud"; el.style.cssText="position:fixed;left:50%;bottom:120px;transform:translateX(-50%);padding:8px 16px;background:rgba(8,8,10,.85);color:#fff;font:bold 15px Arial;letter-spacing:1px;border-left:4px solid #fff;display:none;z-index:15;text-align:center"; document.body.appendChild(el); }
  const C=GRAF.cur; if(!C){ el.style.display="none"; return; } const col=GRAF.pal[grafCrewIdx(GRAF.me())].css; el.style.display="block"; el.style.borderColor=col;
  if(C.phase==="shake"){ el.innerHTML=`SHAKE THE CAN… <span style="color:${col}">${{S:"TAG",M:"THROW-UP",L:C.sp.heaven?"HEAVEN PIECE":"PIECE"}[C.sp.size]}</span>`; return; }
  const G=C.plan[C.gi], ar=["→","↗","↑","↖","←","↙","↓","↘"]; el.innerHTML=`<span style="color:${col}">${C.gi+1}/${C.plan.length}</span> RS ${G.n} &nbsp; ${G.d.map((d,i)=>`<b style="opacity:${i<C.step?.35:1}">${ar[d]}</b>`).join(" ")} &nbsp;<small style="color:#aaa">B cancel</small>`; }
// ---- HEAT (no heat system existed in the build): window.HEAT
// HEAT = { level:Number 0..5 (float), stars:Int 0..5, max:5, lastReason:String, add(amount,reason), set(level), decay(dt), night():Bool,
//          subscribe(fn(HEAT,evt)) -> unsubscribe, onChange:fn|null }. Tags add heat (S .35, M .8, L 1.6, billboards x1.5); day = x0.15.
//          Decays .06/s after 8 s without new heat. At 3 stars cops would chase (police AI is a later assignment).
const HEAT=(function(){ const subs=new Set(); const H={ level:0, stars:0, max:5, lastReason:null, quiet:0, decayRate:.06, quietTime:8,
  add(a,why){ H.level=Math.max(0,Math.min(H.max,H.level+a)); H.lastReason=why||null; H.quiet=0; emit("add"); },
  set(v){ H.level=Math.max(0,Math.min(H.max,v)); emit("set"); }, night:grafNight,
  decay(dt){ H.quiet+=dt; if(H.quiet>H.quietTime&&H.level>0){ const s=H.stars; H.level=Math.max(0,H.level-H.decayRate*dt); if(Math.floor(H.level)!==s) emit("decay"); } },
  subscribe(fn){ subs.add(fn); return ()=>subs.delete(fn); }, onChange:null };
  function emit(evt){ H.stars=Math.floor(H.level+1e-6); try{ H.onChange&&H.onChange(H,evt); }catch(e){ console.warn("HEAT.onChange",e); } for(const f of subs){ try{ f(H,evt); }catch(e){ console.warn("HEAT sub",e); } } heatHud(); }
  function heatHud(){ let el=document.getElementById("heatHud"); if(!el){ el=document.createElement("div"); el.id="heatHud"; el.className="hud"; el.style.cssText="position:fixed;top:18px;right:220px;color:#ff3344;font:bold 18px Arial;letter-spacing:2px;text-shadow:0 0 6px #000;z-index:15"; document.body.appendChild(el); }
    el.textContent=H.level>0.05?"★".repeat(H.stars)+"☆".repeat(H.max-H.stars):""; }
  return H; })();
if(!window.HEAT) window.HEAT=HEAT;
// ---- TURF bridge: extend the existing TURF (turf_dash.js) instead of duplicating it, and publish it as window.TURF.
// window.TURF (same object the legacy turf code uses) gains:
//   TURF.api = 1
//   TURF.palette   : [{id,name,css,fallback}] the 10 real crews (Volt + Rust Claw are graffiti.js fallbacks)
//   TURF.districts : { [districtName]: { name, ids:[PALMA ids], boxes:[[x0,z0,x1,z1]], points:{crewId:n}, owner:crewId|null, ownerColor:css|null, threshold, spots:[spotIds] } }
//   TURF.tags      : [{ id, district, x, y, z, nx, nz, size:"S"|"M"|"L", surface, kind, heaven, crew:crewId|null, color:css, icon:"spray-can", t:ms }]
//                    (graffiti spots; legacy wall spots stay in TURF.spots and count 3 points each to their owner)
//   TURF.subscribe(fn(evt)) -> unsubscribe;  TURF.onChange = fn(evt) | null
//   evt = { type:"tag"|"flip", tag, district, crew, prevOwner, owner }
//   TURF.ownerOf(x,z) -> crewId|null ;  TURF.threshold = 12 (min points before a district can be owned)
function grafTurfBridge(){ const T=TURF; T.api=1; T.threshold=12; T.palette=GRAF.pal.slice(0,10).map(p=>({id:p.id,name:p.name,css:p.css,neon:"#"+p.neon.getHexString(),fallback:p.fallback}));
  const subs=T._subs=new Set(); T.subscribe=fn=>{ subs.add(fn); return ()=>subs.delete(fn); }; if(!("onChange" in T)) T.onChange=null;
  T._emit=evt=>{ try{ T.onChange&&T.onChange(evt); }catch(e){ console.warn("TURF.onChange",e); } for(const f of subs){ try{ f(evt); }catch(e){ console.warn("TURF sub",e); } } };
  T.districts={}; for(const q of PALMA.districts){ const D=T.districts[q.name]=T.districts[q.name]||{name:q.name,ids:[],boxes:[],points:{},owner:null,ownerColor:null,threshold:T.threshold,spots:[],tint:q.tint}; D.ids.push(q.id); D.boxes.push(q.box.slice()); }
  for(const sp of GRAF.spots) if(T.districts[sp.district]) T.districts[sp.district].spots.push(sp.id);
  T.tags=GRAF.spots.map(sp=>({id:sp.id,district:sp.district,x:+sp.x.toFixed(2),y:+sp.y.toFixed(2),z:+sp.z.toFixed(2),nx:sp.nx,nz:sp.nz,size:sp.size,surface:sp.surf,kind:sp.kind,heaven:!!sp.heaven,crew:null,color:"#8a8a8a",icon:"spray-can",t:0}));
  T.ownerOf=(x,z)=>{ const n=grafDistrictOf(x,z); return n&&T.districts[n]?T.districts[n].owner:null; };
  grafLoad(); grafRecount(true); }
function grafRecount(silent){ const T=TURF; for(const n in T.districts){ const D=T.districts[n]; D.points={}; }
  try{ for(const s of T.spots){ if(s.owner==null||s.owner<0) continue; const id=T.crews[s.owner].id, D=T.districts[s.d]; if(D) D.points[id]=(D.points[id]||0)+3; } }catch(e){}
  for(const sp of GRAF.spots){ if(!sp.owner) continue; const D=T.districts[sp.district]; if(D) D.points[sp.owner]=(D.points[sp.owner]||0)+(sp.pts||GRAF.SIZES[sp.size].pts); }
  const flips=[]; for(const n in T.districts){ const D=T.districts[n]; let best=null, bp=0, second=0; for(const c in D.points){ const v=D.points[c]; if(v>bp){ second=bp; bp=v; best=c; } else if(v>second) second=v; }
    let own=(best&&bp>=T.threshold&&bp>second)?best:(D.owner&&(D.points[D.owner]||0)>=T.threshold?D.owner:null);
    if(own!==D.owner){ flips.push({D,prev:D.owner,own}); D.owner=own; } D.ownerColor=own?(GRAF.pal[grafCrewIdx(own)]||{}).css||null:null; }
  if(!silent) for(const f of flips){ T._emit({type:"flip",district:f.D.name,prevOwner:f.prev,owner:f.own,crew:f.own}); if(f.own===GRAF.me()) try{ flash(f.D.name+" IS OURS",f.D.ownerColor); }catch(e){} }
  return flips; }
function grafTurfAdd(sp,crew,prev,pts){ const T=TURF; sp.pts=pts; const tg=T.tags.find(t=>t.id===sp.id); if(tg){ tg.crew=crew; tg.color=GRAF.pal[grafCrewIdx(crew)].css; tg.t=sp.tagT; }
  T._emit({type:"tag",tag:tg,district:sp.district,crew,prevOwner:prev}); grafRecount(false); grafSave(); try{ turfHUD(); }catch(e){} }
function grafSave(){ try{ const o={}; for(const sp of GRAF.spots) if(sp.owner) o[sp.id]=[sp.owner,sp.size,sp.tagT||0,sp.pts||0]; localStorage.setItem("skyrydahs.graffiti.v1",JSON.stringify({t:Date.now(),o})); }catch(e){} }
function grafLoad(){ let d=null; try{ d=JSON.parse(localStorage.getItem("skyrydahs.graffiti.v1")||"null"); }catch(e){} if(!d||!d.o) return;
  for(const sp of GRAF.spots){ const r=d.o[sp.id]; if(!r||r[1]!==sp.size) continue; sp.owner=r[0]; sp.tagT=r[2]; sp.pts=r[3]; sp.t0=-99; const tg=TURF.tags.find(t=>t.id===sp.id); if(tg){ tg.crew=sp.owner; tg.color=GRAF.pal[grafCrewIdx(sp.owner)].css; tg.t=sp.tagT; } grafWrite(sp); } }
window.TURF=TURF;
// ---- frame tick (called pre-render from animate)
const _grafV=new THREE.Vector3();
function grafTickCore(dt,xr){ if(!GRAF.ready){ if(TURF.ready&&typeof PALMA!=="undefined"&&colliders.length) try{ grafInit(); }catch(e){ console.warn("graffiti init failed",e); GRAF.ready=false; GRAF.fail=String(e); window.grafTick=null; } return; }
  const night=grafNight(); GRAF.night=night; const U=GRAF.U; U.uTime.value=clock; U.uNight.value+=((night?1:0)-U.uNight.value)*Math.min(1,dt*3);
  if(GRAF.glow&&!/[?&]nobatch=1/.test(location.search)) GRAF.glow.mesh.visible=U.uNight.value>.003; // DC proposal (Rydah Optimizer): glow/backlight shader discards every fragment when uNight~0, so skip its draw by day (-1 call); ?nobatch=1 keeps it always on
  try{ if(scene.fog){ U.uFogC.value.copy(scene.fog.color); U.uFogD.value=scene.fog.density||0; } }catch(e){}
  HEAT.decay(dt);
  if(window.wallKickCam) window.wallKickCam(dt,xr);  // wall-kick camera nudge (wallatk.js), pre-render, desktop only
  const S=window.SR_PAD, ride=State.mode==="ride", blocked=(window.PHONE&&PHONE.up)||(window.MAP&&MAP.open)||(typeof GATE!=="undefined"&&GATE.uiOpen)||(window.PAD&&(PAD.xNear==="pickup"||PAD.xNear==="gate"));
  if(GRAF.cur){ if(!ride) grafCancel("mode"); else grafUpdateTag(dt); }
  else if(S&&S.active()&&S.justPressed("X")){ const legacyAim=!!(window.TGT&&TGT.aiming&&TGT.spot); const sp=(ride&&!blocked&&!legacyAim)?grafFind():null; GRAF.lastX={ride,blocked:!!blocked,xNear:window.PAD&&PAD.xNear,spot:sp&&sp.id}; if(sp) grafStart(sp); }
  if(GRAF.cur&&window.PAD&&PAD.R&&PAD.R.rs) PAD.R.rs=[0,0,0]; // RS belongs to the gesture this frame (padTick/tgtTick run after us)
  if(!GRAF.cur) grafHiss(0,0);
  grafMistUpdate(dt);
  for(const sp of GRAF.spots) if(sp.disp!=null){ sp.disp+=dt*GRAF.REVEAL_RATE; if(sp.disp>=1) sp.disp=null; grafWrite(sp); }
  for(const sp of GRAF.spots) if(sp.lockUntil&&sp.lockUntil<clock&&sp._locked){ sp._locked=false; grafWrite(sp); } else if(sp.lockUntil>clock) sp._locked=true;
  if(GRAF.cur&&!xr) grafCam(dt); else GRAF.camK=Math.max(0,(GRAF.camK||0)-dt*4); }
// camera framing the wall while tagging (desktop only; restored at next poll like the targeting camera)
function grafCam(dt){ const sp=GRAF.cur.sp; if(GRAF.cur.aimed) return; GRAF.camK=Math.min(1,(GRAF.camK||0)+dt*4); const k=GRAF.camK*GRAF.camK*(3-2*GRAF.camK);
  if(!GRAF.saved) GRAF.saved={p:camera.position.clone(),q:camera.quaternion.clone()};
  const dist=sp.size==="L"?7.5:sp.size==="M"?5:3.2; const tx=-sp.nz, tz=sp.nx;
  if(sp.ground) _grafV.set(sp.x+sp.nx*3,3.2,sp.z+sp.nz*3); else _grafV.set(sp.x+sp.nx*dist+tx*1.2,sp.y+.6,sp.z+sp.nz*dist+tz*1.2);
  camera.position.lerp(_grafV,k); const q0=camera.quaternion.clone(); camera.lookAt(sp.x,sp.y,sp.z); const q1=camera.quaternion.clone(); camera.quaternion.copy(q0).slerp(q1,k); }
if(typeof poll==="function"){ const _gp=poll; poll=function(){ if(GRAF.saved){ camera.position.copy(GRAF.saved.p); camera.quaternion.copy(GRAF.saved.q); GRAF.saved=null; } return _gp.apply(this,arguments); }; }
// while tagging the right stick drives the gesture, not the camera / aim: zero RS for padTick + tgtTick
function grafWrapRS(name){ const f=window[name]; if(typeof f!=="function"||f._graf) return; const w=function(){ const R=window.PAD&&PAD.R; if(GRAF.cur&&R&&R.rs){ const rs=R.rs; R.rs=[0,0,0]; try{ return f.apply(this,arguments); } finally { R.rs=rs; } } return f.apply(this,arguments); }; w._graf=true; window[name]=w; }
// legacy hold-to-tag (turf_dash) stays on keyboard T/F; with a pad, X belongs to the gesture system
if(typeof turfUpdate==="function"){ const _gtu=turfUpdate; turfUpdate=function(dt){ if(GRAF.cur){ const t=Input.tag; Input.tag=false; try{ return _gtu(dt); } finally { Input.tag=t; } } return _gtu(dt); }; }
window.GRAF=GRAF; window.grafTick=function(dt,xr){ grafWrapRS("padTick"); grafWrapRS("tgtTick"); return grafTickCore(dt,xr); };
