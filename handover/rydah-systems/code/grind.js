// ===== LOCKED-IN GRIND (JSR / BRC / Air Gear style) =====
// Every rail, telephone/power cable, bridge cable, pole and palm trunk is a spline. Land on/near one (air) or skate into a low one -> snap + lock,
// ride it to the end, pop off with your momentum. A = jump off (pops up), B = drop off (keeps momentum), L3 = kick, LS = lean/balance.
// Physics: grip loss on contact (entry speed + angle), material drag (steel < cable < bark), gravity along slope (up/down cables, up trunks).
// Rendering: cables/bridge cables are merged tubes (1 draw call per material), poles are 2 global InstancedMeshes (wood / galvanised),
// sparks = 1 pooled Points (cap 160), trail = 1 ribbon, vortex focus = 1 clip-space quad. All extras hidden when idle.
const GRIND={ S:[], grid:new Map(), cell:6, on:null, cd:0, ignore:null, ignoreT:0, stats:{locks:0,ends:0,jumps:0,drops:0,kicks:0}, bob:0, hudT:0,
  MAT:{ steel:{mu:.35,k:.010,snap:1.25,col:[0xffe6a0,0xffffff,0xffb040],label:"RAIL GRIND"},
        cable:{mu:.75,k:.022,snap:1.5, col:[0xffd27a,0xffffff,0x7fe9ff],label:"CABLE GRIND"},
        bark: {mu:1.25,k:.030,snap:1.0, col:[0x8a5a2b,0xc8a070,0x5fae4a,0xffd27a],label:"PALM GRIND"} },
  poles:{wood:[],galv:[]}, tubes:{cable:[],steel:[],hanger:[]}, keyPrev:{} };
const _grw=new THREE.Vector3(), _grv=new THREE.Vector3(), _grt=new THREE.Vector3(), _grq=new THREE.Vector3();
addEventListener("keydown",e=>{ if(!e.repeat) GRIND.keyPrev[e.code]=true; });
// ---------- spline registry ----------
function grindAdd(pts,mat,r,opt){ opt=opt||{}; const P=pts.map(a=>a.isVector3?a.clone():new THREE.Vector3(a[0],a[1],a[2])); const cum=[0];
  for(let i=1;i<P.length;i++) cum.push(cum[i-1]+P[i].distanceTo(P[i-1])); const s={pts:P,cum,L:cum[cum.length-1],mat,r:r||.1,id:GRIND.S.length,vert:!!opt.vert,kind:opt.kind||mat};
  if(s.L>.5) GRIND.S.push(s); return s; }
function grindGridBuild(){ const G=GRIND.grid, c=GRIND.cell; G.clear();
  for(const s of GRIND.S) for(let i=0;i<s.pts.length-1;i++){ const a=s.pts[i], b=s.pts[i+1];
    for(let x=Math.floor(Math.min(a.x,b.x)/c)-1;x<=Math.floor(Math.max(a.x,b.x)/c)+1;x++) for(let z=Math.floor(Math.min(a.z,b.z)/c)-1;z<=Math.floor(Math.max(a.z,b.z)/c)+1;z++){ const k=x+"|"+z; let L=G.get(k); if(!L) G.set(k,L=[]); L.push([s,i]); } }
  GRIND.built=true; }
// closest point on spline segments near p (3D); returns {s,i,t,d,dh,q,arc}
function grindNear(p,maxD,filter){ const c=GRIND.cell, k=Math.floor(p.x/c)+"|"+Math.floor(p.z/c), L=GRIND.grid.get(k); if(!L) return null; let best=null;
  for(const [s,i] of L){ if(filter&&!filter(s)) continue; const a=s.pts[i], b=s.pts[i+1]; _grt.subVectors(b,a); const l2=_grt.lengthSq(); let t=l2>0?_grw.subVectors(p,a).dot(_grt)/l2:0; t=Math.max(0,Math.min(1,t));
    _grq.copy(a).addScaledVector(_grt,t); const d=_grq.distanceTo(p); if(d<maxD&&(!best||d<best.d)) best={s,i,t,d,dh:Math.hypot(_grq.x-p.x,_grq.z-p.z),q:_grq.clone(),arc:s.cum[i]+t*(s.cum[i+1]-s.cum[i])}; }
  return best; }
function grindAt(s,arc,out,tan){ arc=Math.max(0,Math.min(s.L,arc)); let i=0; while(i<s.cum.length-2&&s.cum[i+1]<arc) i++; const a=s.pts[i], b=s.pts[i+1], l=(s.cum[i+1]-s.cum[i])||1, t=(arc-s.cum[i])/l;
  out.copy(a).lerp(b,t); if(tan) tan.subVectors(b,a).normalize(); return out; }
// ---------- world hooks (called from patched builders) ----------
function grindWire(a,b,sag){ const n=10, P=[]; for(let i=0;i<=n;i++){ const t=i/n; P.push([a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t-4*sag*t*(1-t),a[2]+(b[2]-a[2])*t]); }
  const s=grindAdd(P,"cable",.09); GRIND.tubes.cable.push(s); }
function grindPole(x,z,h,r,kind){ GRIND.poles[kind].push([x,z,h,r]); const s=grindAdd([[x,.2,z],[x,h*.5,z],[x,h-.15,z]],"steel",r,{vert:true,kind:kind==="wood"?"pole":"lamp"}); if(kind==="wood"){ s.mat="bark"; s.kind="pole"; } }
function grindTrunk(x0,z0,x1,y1,z1,r,spiral){ const P=[], n=12; for(let i=0;i<=n;i++){ const t=i/n, a=t*Math.PI*spiral; P.push([x0+(x1-x0)*t+Math.sin(a)*.04,(y1)*t+.15,z0+(z1-z0)*t+Math.cos(a)*.04]); }
  grindAdd(P,"bark",r,{vert:true,kind:"trunk"}); }
function grindFrond(tx,ty,tz,a,len){ const P=[]; for(let i=0;i<=4;i++){ const t=i/4; P.push([tx+Math.sin(a)*len*t,ty+.25-1.8*t*t,tz+Math.cos(a)*len*t]); } grindAdd(P,"bark",.08,{kind:"frond"}); }
function grindRails(){ if(GRIND.railsDone||typeof rails==="undefined") return; GRIND.railsDone=true; for(const r of rails) grindAdd([[r.x1,r.h,r.z1],[r.x2,r.h,r.z2]],"steel",.09,{kind:"rail"}); }
// bridge LineSegments (group-local) -> world splines: chain consecutive segments; vertical hangers render only
function grindBridgeSeg(seg,g,b){ g.updateMatrixWorld(true); const W=[]; for(let i=0;i<seg.length;i+=3) W.push(new THREE.Vector3(seg[i],seg[i+1],seg[i+2]).applyMatrix4(g.matrixWorld));
  const chains=[], open=new Map(), K=v=>v.x.toFixed(2)+","+v.y.toFixed(2)+","+v.z.toFixed(2);
  for(let i=0;i<W.length;i+=2){ const a=W[i], b=W[i+1], dy=Math.abs(b.y-a.y), l=a.distanceTo(b);
    if(dy/l>.97){ GRIND.tubes.hanger.push({pts:[a,b],r:.05}); continue; }
    const c=open.get(K(a)); if(c){ open.delete(K(a)); c.push(b); open.set(K(b),c); } else { const n=[a,b]; chains.push(n); open.set(K(b),n); } }
  for(const c of chains){ const main=c.length>4; const s=grindAdd(c,"steel",main?.22:.12,{kind:main?"main":"stay"}); GRIND.tubes.steel.push(s); } }
function grindZip(a,b){ const P=[]; for(let i=0;i<=16;i++){ const t=i/16; P.push([a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t-3*t*(1-t),a[2]+(b[2]-a[2])*t]); } GRIND.tubes.steel.push(grindAdd(P,"steel",.12,{kind:"zip"})); }
// ---------- textures (canvas, generated once; refs: skyrydahs-ref/grind/*) ----------
function grindCanvas(n,fn){ const c=document.createElement("canvas"); c.width=c.height=n; fn(c.getContext("2d"),n); return c; }
function grindNormalFromHeight(hc,str){ const n=hc.width, src=hc.getContext("2d").getImageData(0,0,n,n).data, out=document.createElement("canvas"); out.width=out.height=n; const o=out.getContext("2d"), im=o.createImageData(n,n);
  const h=(x,y)=>src[(((y+n)%n)*n+((x+n)%n))*4]/255; for(let y=0;y<n;y++) for(let x=0;x<n;x++){ const dx=(h(x+1,y)-h(x-1,y))*str, dy=(h(x,y+1)-h(x,y-1))*str, l=Math.hypot(dx,dy,1), j=(y*n+x)*4;
    im.data[j]=(-dx/l*.5+.5)*255; im.data[j+1]=(-dy/l*.5+.5)*255; im.data[j+2]=(1/l*.5+.5)*255; im.data[j+3]=255; } o.putImageData(im,0,0); return out; }
function grindTex(c,rx,ry){ const t=new THREE.CanvasTexture(c); t.wrapS=t.wrapT=THREE.RepeatWrapping; t.repeat.set(rx||1,ry||1); t.anisotropy=4; return t; }
function grindMats(){ if(GRIND.mats) return GRIND.mats; const R=(a,b)=>a+Math.random()*(b-a);
  // weathered creosote/CCA wood pole: vertical grain, checks (cracks), grey sun-bleach  (ref: ambientCG WoodSiding011 / Bark012)
  const wood=grindCanvas(256,(x,n)=>{ x.fillStyle="#5b4632"; x.fillRect(0,0,n,n); for(let i=0;i<260;i++){ const px=Math.random()*n, w=R(.5,3); x.fillStyle=`rgba(${Math.random()<.5?"150,135,115":"40,30,22"},${R(.15,.45)})`; x.fillRect(px,0,w,n); }
    for(let i=0;i<14;i++){ const px=Math.random()*n, y=Math.random()*n; x.fillStyle="rgba(20,14,10,.85)"; x.fillRect(px,y,R(1,2.2),R(30,120)); } const g=x.createLinearGradient(0,0,n,0); g.addColorStop(0,"rgba(160,160,155,.18)"); g.addColorStop(.5,"rgba(0,0,0,0)"); g.addColorStop(1,"rgba(160,160,155,.18)"); x.fillStyle=g; x.fillRect(0,0,n,n); });
  // galvanised steel: zinc spangle mottling + light streaking (ref: ambientCG Metal046B)
  const galv=grindCanvas(256,(x,n)=>{ x.fillStyle="#8d9399"; x.fillRect(0,0,n,n); for(let i=0;i<900;i++){ const v=R(110,190)|0; x.fillStyle=`rgba(${v},${v+3},${v+6},.35)`; x.beginPath(); x.arc(Math.random()*n,Math.random()*n,R(2,9),0,7); x.fill(); }
    for(let i=0;i<40;i++){ x.fillStyle="rgba(70,62,50,.18)"; x.fillRect(Math.random()*n,Math.random()*n,R(1,3),R(20,90)); } });
  // helical wire-strand height -> normal (7-wire strand lay ~ 45 deg); tube UVs: u=around, v=length/(2pi r) so the helix keeps its pitch on every cable
  const helixH=grindCanvas(128,(x,n)=>{ for(let y=0;y<n;y++) for(let i=0;i<n;i++){ const ph=((i+y)/n*7)%1, v=Math.pow(Math.sin(ph*Math.PI),.6)*255|0; x.fillStyle=`rgb(${v},${v},${v})`; x.fillRect(i,y,1,1); } });
  // rubber insulation: fine extrusion lines + scuffs
  const rubH=grindCanvas(64,(x,n)=>{ x.fillStyle="#808080"; x.fillRect(0,0,n,n); for(let i=0;i<n;i+=3){ x.fillStyle=`rgba(${Math.random()<.5?255:0},${Math.random()<.5?255:0},${Math.random()<.5?255:0},.08)`; x.fillRect(i,0,1,n); } });
  const M={ wood:new THREE.MeshStandardMaterial({color:0xb8a690,map:grindTex(wood,1,3),roughness:.92,metalness:0}),
    galv:new THREE.MeshStandardMaterial({color:0xd0d6dc,map:grindTex(galv,1,4),roughness:.48,metalness:.75}),
    cable:new THREE.MeshStandardMaterial({color:0x121216,roughness:.38,metalness:0,normalMap:grindTex(grindNormalFromHeight(rubH,1.2),1,1),normalScale:new THREE.Vector2(.35,.35)}),
    steel:new THREE.MeshStandardMaterial({color:0xaab2bc,roughness:.32,metalness:.9,normalMap:grindTex(grindNormalFromHeight(helixH,3),1,1),normalScale:new THREE.Vector2(1,1)}) };
  M.cable.emissive=new THREE.Color(0x05060a); M.steel.emissive=new THREE.Color(0x0c0e14); return GRIND.mats=M; }
// merged tube builder: one BufferGeometry per material (shared material, 1 draw call)
function grindTubes(list,mat,radial){ if(!list.length) return null; const pos=[], nor=[], uv=[], idx=[]; const up=new THREE.Vector3(0,1,0), T=new THREE.Vector3(), N=new THREE.Vector3(), B=new THREE.Vector3(), v=new THREE.Vector3();
  for(const s of list){ const P=s.pts, r=s.r; let len=0; for(let i=0;i<P.length;i++){ if(i>0) len+=P[i].distanceTo(P[i-1]); T.subVectors(P[Math.min(i+1,P.length-1)],P[Math.max(i-1,0)]).normalize();
      N.crossVectors(T,Math.abs(T.y)>.9?v.set(1,0,0):up).normalize(); B.crossVectors(T,N); const base=pos.length/3;
      for(let k=0;k<=radial;k++){ const a=k/radial*Math.PI*2, cx=Math.cos(a), sy=Math.sin(a); const nx=N.x*cx+B.x*sy, ny=N.y*cx+B.y*sy, nz=N.z*cx+B.z*sy;
        pos.push(P[i].x+nx*r,P[i].y+ny*r,P[i].z+nz*r); nor.push(nx,ny,nz); uv.push(k/radial,len/(Math.PI*2*r)); }
      if(i>0){ const b0=base-(radial+1); for(let k=0;k<radial;k++) idx.push(b0+k,base+k,b0+k+1, b0+k+1,base+k,base+k+1); } } }
  const g=new THREE.BufferGeometry(); g.setAttribute("position",new THREE.Float32BufferAttribute(pos,3)); g.setAttribute("normal",new THREE.Float32BufferAttribute(nor,3)); g.setAttribute("uv",new THREE.Float32BufferAttribute(uv,2)); g.setIndex(idx);
  g.computeBoundingSphere(); const m=new THREE.Mesh(g,mat); m.matrixAutoUpdate=false; m.userData.grind=true; scene.add(m); return m; }
function grindBuildCables(){ const M=grindMats(); GRIND.meshCable=grindTubes(GRIND.tubes.cable,M.cable,6); }
function grindBuildWorld(){ if(GRIND.world) return; GRIND.world=true; const M=grindMats();
  grindRails(); grindBuildCables.done||0; GRIND.meshSteel=grindTubes(GRIND.tubes.steel.concat(GRIND.tubes.hanger),M.steel,8);
  const mk=(L,mat)=>{ if(!L.length) return; const g=new THREE.CylinderGeometry(.85,1,1,10,1,true); const im=new THREE.InstancedMesh(g,mat,L.length); const m=new THREE.Matrix4(), q=new THREE.Quaternion(), s=new THREE.Vector3(), v=new THREE.Vector3();
    L.forEach((p,i)=>{ m.compose(v.set(p[0],p[2]/2,p[1]),q,s.set(p[3],p[2],p[3])); im.setMatrixAt(i,m); }); im.userData.grind=true; scene.add(im); return im; };
  GRIND.meshWood=mk(GRIND.poles.wood,M.wood); GRIND.meshGalv=mk(GRIND.poles.galv,M.galv); grindGridBuild(); grindFX(); }
// ---------- FX: spark pool, trail ribbon, vortex quad, audio ----------
function grindFX(){ const SP={n:160,i:0}; SP.pos=new Float32Array(SP.n*3).fill(-999); SP.col=new Float32Array(SP.n*3); SP.vel=new Float32Array(SP.n*3); SP.life=new Float32Array(SP.n); SP.base=new Float32Array(SP.n*3); SP.grav=new Float32Array(SP.n);
  const g=new THREE.BufferGeometry(); g.setAttribute("position",new THREE.BufferAttribute(SP.pos,3)); g.setAttribute("color",new THREE.BufferAttribute(SP.col,3));
  SP.pts=new THREE.Points(g,new THREE.PointsMaterial({size:.09,vertexColors:true,transparent:true,blending:THREE.AdditiveBlending,depthWrite:false})); SP.pts.frustumCulled=false; SP.pts.visible=false; scene.add(SP.pts);
  SP.alive=()=>{ let n=0; for(let i=0;i<SP.n;i++) if(SP.life[i]>0) n++; return n; }; GRIND.spk=SP;
  const TN=28, tg=new THREE.BufferGeometry(); GRIND.trail={n:TN,pts:[],pos:new Float32Array(TN*2*3),col:new Float32Array(TN*2*3)};
  tg.setAttribute("position",new THREE.BufferAttribute(GRIND.trail.pos,3)); tg.setAttribute("color",new THREE.BufferAttribute(GRIND.trail.col,3)); const ix=[]; for(let i=0;i<TN-1;i++){ const a=i*2; ix.push(a,a+1,a+2,a+1,a+3,a+2); } tg.setIndex(ix);
  GRIND.trail.mesh=new THREE.Mesh(tg,new THREE.MeshBasicMaterial({vertexColors:true,transparent:true,blending:THREE.AdditiveBlending,depthWrite:false,side:THREE.DoubleSide})); GRIND.trail.mesh.frustumCulled=false; GRIND.trail.mesh.visible=false; scene.add(GRIND.trail.mesh);
  // vortex focus: clip-space quad (no matrices) -> radial speed streaks + tunnel vignette centred slightly above screen centre; per-eye safe in XR
  const vm=new THREE.ShaderMaterial({transparent:true,depthTest:false,depthWrite:false,uniforms:{uK:{value:0},uT:{value:0},uA:{value:16/9},uXR:{value:0},uC:{value:new THREE.Color(0x9ff4ff)}},
    vertexShader:"varying vec2 vUv; void main(){ vUv=uv; gl_Position=vec4(position.xy*2.0,0.0,1.0); }",
    fragmentShader:`uniform float uK,uT,uA,uXR; uniform vec3 uC; varying vec2 vUv;
      void main(){ vec2 d=vUv*2.0-1.0; d.y-=.08; d.x*=uA; float r=length(d), a=atan(d.y,d.x); float id=floor((a+3.14159)/6.28318*140.0); float h=fract(sin(id*12.9898)*43758.5453);
        float run=fract(h*9.1-uT*(1.6+h*2.4)-r*.35); float st=smoothstep(.72,1.0,h)*smoothstep(.45,1.25,r)*smoothstep(.0,.25,run)*smoothstep(.75,.35,run)*(1.0-uXR);
        float vig=smoothstep(.55,1.55,r); float al=clamp(st*uK*.9+vig*uK*.6,0.0,.8); gl_FragColor=vec4(mix(vec3(.0,.01,.03),uC,st/(st+vig*.6+.001)),al); }`});
  GRIND.vortex=new THREE.Mesh(new THREE.PlaneGeometry(1,1),vm); GRIND.vortex.frustumCulled=false; GRIND.vortex.renderOrder=9990; GRIND.vortex.visible=false; scene.add(GRIND.vortex); }
function grindSpark(x,y,z,col,vx,vy,vz,life,grav){ const S=GRIND.spk, i=S.i=(S.i+1)%S.n, c=_grcol.set(col); S.pos[i*3]=x; S.pos[i*3+1]=y; S.pos[i*3+2]=z; S.vel[i*3]=vx; S.vel[i*3+1]=vy; S.vel[i*3+2]=vz; S.base[i*3]=c.r; S.base[i*3+1]=c.g; S.base[i*3+2]=c.b; S.life[i]=life; S.grav[i]=grav; }
const _grcol=new THREE.Color();
function grindNight(){ const b=scene.background; return !b||!b.isColor||(b.r+b.g+b.b)<.9; }
function grindAudio(on,v){ try{ if(on&&!GRIND.au){ const ac=typeof gateAudio==="function"?gateAudio():null; if(!ac) return; const n=ac.sampleRate, buf=ac.createBuffer(1,n,n), d=buf.getChannelData(0); for(let i=0;i<n;i++) d[i]=Math.random()*2-1;
      const src=ac.createBufferSource(); src.buffer=buf; src.loop=true; const bp=ac.createBiquadFilter(); bp.type="bandpass"; bp.Q.value=2.2; const gn=ac.createGain(); gn.gain.value=0; src.connect(bp); bp.connect(gn); gn.connect(ac.destination); src.start(); GRIND.au={ac,src,bp,gn}; }
    const A=GRIND.au; if(!A) return; const t=A.ac.currentTime; A.gn.gain.setTargetAtTime(on?Math.min(.16,.04+v*.006):0,t,.05); A.bp.frequency.setTargetAtTime(900+v*160,t,.05); A.src.playbackRate.setTargetAtTime(.7+Math.min(1.2,v/22),t,.08); }catch(e){} }
function grindRumble(strong,weak,ms){ try{ for(const gp of (navigator.getGamepads?[...navigator.getGamepads()]:[])) if(gp&&gp.vibrationActuator&&gp.vibrationActuator.playEffect){ gp.vibrationActuator.playEffect("dual-rumble",{duration:ms,strongMagnitude:strong,weakMagnitude:weak}); GRIND.rumbles=(GRIND.rumbles||0)+1; } }catch(e){} }
// ---------- input ----------
function grindInput(){ const I=WALL.I||{}, R=typeof PAD!=="undefined"?PAD.R:null, gp=R&&R.gp&&!renderer.xr.isPresenting, K=GRIND.keyPrev; GRIND.keyPrev={};
  const blocked=(typeof PHONE!=="undefined"&&PHONE.up)||(window.MAP&&MAP.open)||(typeof GATE!=="undefined"&&GATE.uiOpen);
  let lean=I.side||0; if(gp&&R.ls[2]>0) lean=R.ls[0]; const xr=renderer.xr.isPresenting&&renderer.xr.getSession();
  let drop=!blocked&&(!!K.KeyC||(gp&&R.e(1))), kick=!blocked&&(!!K.ShiftLeft||!!K.ShiftRight||(gp&&R.e(10)));
  if(xr) for(const s of xr.inputSources){ const g=s.gamepad; if(g&&s.handedness==="left"&&g.buttons[3]&&g.buttons[3].pressed&&!GRIND.xrStick){ kick=true; } GRIND.xrStick=!!(g&&s.handedness==="left"&&g.buttons[3]&&g.buttons[3].pressed); }
  return { jump:!blocked&&!!I.jumpP, drop, kick, lean }; }
// ---------- lock / ride / exit ----------
function grindLock(s,arc,dir,v,align){ const R=Ride, M=GRIND.MAT[s.mat]; const ent=v; const loss=.03+.06*Math.min(1,ent/24)+.16*(1-Math.min(1,align));
  GRIND.on={s,arc,dir,v:Math.max(s.vert?4:3,v*(1-loss)),bal:0,t:0,grip:.18,ent,loss,nightK:0,off:new THREE.Vector3()}; GRIND.stats.locks++; WALL.air=null; WALL.on=null; R.grinding=true;
  if(s.vert){ grindAt(s,arc,_grv); const p=R.group.position; GRIND.on.off.set(p.x-_grv.x,0,p.z-_grv.z); if(GRIND.on.off.lengthSq()<1e-4) GRIND.on.off.set(Math.sin(R.yaw),0,Math.cos(R.yaw)).multiplyScalar(-1); GRIND.on.off.normalize().multiplyScalar(s.r+.12); }
  trickScore(s.kind==="trunk"?150:100,s.kind==="trunk"||s.kind==="pole"||s.kind==="lamp"?"POLE CLIMB":M.label,.05); grindRumble(.55,.35,90);
  const p=R.group.position; for(let k=0;k<18;k++) grindSpark(p.x,p.y+.05,p.z,M.col[k%M.col.length],(Math.random()-.5)*5,Math.random()*4,(Math.random()-.5)*5,.45,9); GRIND.spk.pts.visible=true; }
function grindExit(kind){ const G=GRIND, O=G.on; if(!O) return; const s=O.s; grindAt(s,O.arc,_grv,_grt); _grt.multiplyScalar(O.dir); const v=O.v;
  let vx=_grt.x*v, vz=_grt.z*v, vy=_grt.y*v; if(s.vert&&kind!=="drop"){ vx+=O.off.x*8; vz+=O.off.z*8; }   // trunk/pole top: kick off outward
  if(kind==="jump"){ vy=Math.max(vy,0)+6.5; G.stats.jumps++; trickScore(120,"GRIND POP",.05); }
  else if(kind==="drop"){ vy=Math.min(vy,0); G.stats.drops++; }
  else { vy=Math.max(vy,0)+3.2; G.stats.ends++; trickScore(80,"RAIL END",.03); }
  G.lastExit={kind,v,vx,vy,vz,h:Math.hypot(vx,vz)}; G.on=null; G.ignore=s; G.ignoreT=.45; G.cd=kind==="end"?.12:.4; G.cdSet=G.cd; Ride.grinding=false;
  if(typeof wallLaunch==="function"){ Ride.y=Ride.group.position.y; wallLaunch(vx,vz,vy,false); WALL.air.y=Ride.y; WALL.air.t=.2; } grindRumble(.25,.5,60); }
// all candidates near p (best segment per spline), within maxD (3D)
function grindAll(p,maxD){ const c=GRIND.cell, L=GRIND.grid.get(Math.floor(p.x/c)+"|"+Math.floor(p.z/c)); if(!L) return []; const by=new Map();
  for(const [s,i] of L){ if(s.kind==="npc"||s.rider) continue; const a=s.pts[i], b=s.pts[i+1]; _grt.subVectors(b,a); const l2=_grt.lengthSq(); let t=l2>0?_grw.subVectors(p,a).dot(_grt)/l2:0; t=Math.max(0,Math.min(1,t));
    _grq.copy(a).addScaledVector(_grt,t); const d=_grq.distanceTo(p); if(d>maxD) continue; const o=by.get(s); if(o&&o.d<=d) continue;
    by.set(s,{s,i,t,d,dh:Math.hypot(_grq.x-p.x,_grq.z-p.z),q:_grq.clone(),tan:_grt.clone().normalize(),arc:s.cum[i]+t*(s.cum[i+1]-s.cum[i])}); }
  return [...by.values()]; }
GRIND.GROUND_SNAP={steel:.6,cable:.8,bark:.5}; GRIND.VORTEX_XR_CAP=.3; /* XR cap for the full-screen vortex focus (0 = off in XR) */ GRIND.HEADON=Math.cos(20*Math.PI/180);
// lock rules: airborne + falling = full snap radius; rising or grounded = tight radius. Poles/trunks: air press-in or head-on (<=20 deg) skate-in at speed.
// several candidates -> best aligned with velocity (70%) + view direction (30%), small distance penalty. 0.4 s global cooldown after jump/drop.
function grindTryLock(dt){ const R=Ride, p=R.group.position, G=GRIND, A=WALL.air; const prev=G.prevP||p.clone(); G.prevP=p.clone(); if(G.cd>0) return false;
  const vx=A?A.vx:Math.sin(R.yaw)*R.speed, vz=A?A.vz:Math.cos(R.yaw)*R.speed, vy=A?A.vy:0, hs=Math.hypot(vx,vz), vl=Math.hypot(hs,vy)||1;
  if(!A&&(WALL.on||R.speed<5)) return false; if(A&&A.t<.08&&!(A.vy<0)) return false;
  const falling=!!A&&vy<=.5, apex=!!A&&Math.abs(vy)<1.5, fy=A?A.y:R.y; /* apex (wall-kick/hop top, |vy|<1.5): full snap radius + reach a cable up to 1.5 m above the feet */ camera.getWorldDirection(_grw); const cx=_grw.x, cz=_grw.z, cl=Math.hypot(cx,cz)||1;
  _grv.set(p.x,fy+(A?0:.3),p.z); const C=grindAll(_grv,1.6); let best=null;
  for(const n of C){ const s=n.s, M=G.MAT[s.mat]; if(s===G.ignore&&G.ignoreT>0) continue;
    if(s.vert){ // pole / trunk: never on a glancing pass. head-on: heading within 20 deg of the pole centre, swept so fast frames can't skip it
      const tx=n.q.x-p.x, tz=n.q.z-p.z, l=Math.hypot(tx,tz)||1, head=(tx*vx+tz*vz)/(l*(hs||1));
      const ax=n.q.x-prev.x, az=n.q.z-prev.z, mx=p.x-prev.x, mz=p.z-prev.z, ml2=mx*mx+mz*mz, u=ml2>0?Math.max(0,Math.min(1,(ax*mx+az*mz)/ml2)):1, sweep=Math.hypot(prev.x+mx*u-n.q.x,prev.z+mz*u-n.q.z);
      const r=ml2<Math.pow(hs*.12+.6,2)?Math.min(n.dh,sweep):n.dh; if(A){ if(!(head>.5&&r<(falling?M.snap*.6:G.GROUND_SNAP[s.mat])+s.r)) continue; }
      else { const h2=ml2>0?((n.q.x-prev.x)*mx+(n.q.z-prev.z)*mz)/(Math.hypot(n.q.x-prev.x,n.q.z-prev.z)*Math.sqrt(ml2)||1):head; if(Math.max(head,h2)<G.HEADON||r>G.GROUND_SNAP[s.mat]+s.r||R.speed<5) continue; }
      const sc=1+Math.max(head,0)-r*.2; if(!best||sc>best.sc) best={n,sc,dir:1,align:.8}; continue; }
    const rad=(falling||apex)?M.snap:G.GROUND_SNAP[s.mat]; if(n.d>rad) continue; if(A&&n.q.y>fy+(apex?1.5:.9)) continue; if(!A&&(n.q.y>1.45||n.dh>rad)) continue;
    const T=n.tan, dv=(vx*T.x+vy*T.y+vz*T.z)/vl, th=Math.hypot(T.x,T.z)||1, dc=(cx*T.x+cz*T.z)/(cl*th);
    if(!A&&Math.abs(dv)<.25) continue; const sc=.7*Math.abs(dv)+.3*Math.abs(dc)-.25*n.d/rad; if(!best||sc>best.sc) best={n,sc,dir:dv>=0?1:-1,align:Math.abs(dv)+(A?.2:0)}; }
  if(!best) return false; const n=best.n; G.lastPick={kind:n.s.kind,id:n.s.id,sc:best.sc,cands:C.length};
  const v=n.s.vert?Math.max(hs*.85,Math.abs(vy)*.5):Math.max(hs*Math.max(.45,Math.abs(best.align>1?1:best.align)),Math.abs(vy)*.5);
  grindLock(n.s,n.arc,best.dir,A?v:(n.s.vert?R.speed*.85:R.speed),Math.min(1,best.align)); return true; }
function grindRide(dt){ const R=Ride, p=R.group.position, G=GRIND, O=G.on, s=O.s, M=G.MAT[s.mat], I=G.I; O.t+=dt;
  if(I.jump){ grindExit("jump"); return; } if(I.drop){ grindExit("drop"); return; }
  grindAt(s,O.arc,_grv,_grt); const ty=_grt.y*O.dir;
  if(I.kick){ O.v+=4.5; G.stats.kicks++; grindRumble(.4,.2,80); for(let k=0;k<10;k++) grindSpark(p.x,p.y,p.z,0x7fe9ff,(Math.random()-.5)*3,Math.random()*2,(Math.random()-.5)*3,.35,6); }
  if(Input&&Input.boost&&typeof DASH!=="undefined"&&DASH.t>0) O.v+=dt*3;
  // grip moment (first ~0.18 s: extra bite), gravity along slope, material drag (coulomb + air)
  const grip=O.t<O.grip?2.2:0; O.v+=(-9.8*ty-M.mu-grip-M.k*O.v*O.v)*dt; O.v=Math.min(O.v,42);
  // balance: LS leans; drift grows with speed and on cables; off-balance bleeds speed (no bail)
  const drift=(Math.sin(O.t*1.9+s.id)*.5+Math.sin(O.t*3.7)*.25)*(s.mat==="cable"?1.3:.8)*Math.min(1.5,O.v/14);
  O.bal=Math.max(-1,Math.min(1,O.bal+(drift-I.lean*1.6)*dt)); if(Math.abs(O.bal)>.95) O.v-=dt*3;
  if(O.v<0){ if(s.vert||O.v<-.5){ O.dir*=-1; O.v=-O.v; } else O.v=0; }
  if(!s.vert&&O.v<.8&&O.t>.4){ grindExit("drop"); return; }
  O.arc+=O.dir*O.v*dt; if(O.arc<=0||O.arc>=s.L){ O.arc=Math.max(0,Math.min(s.L,O.arc)); grindExit("end"); return; }
  grindAt(s,O.arc,_grv,_grt); const tx=_grt.x*O.dir, tz=_grt.z*O.dir;
  if(s.vert){ p.set(_grv.x+O.off.x,_grv.y,_grv.z+O.off.z); } else { const th=Math.hypot(tx,tz)||1; p.set(_grv.x+(tz/th)*O.bal*.06,_grv.y+s.r+.02,_grv.z-(tx/th)*O.bal*.06); }
  R.y=p.y; R.speed=O.v; if(Math.hypot(tx,tz)>.2) R.yaw=Math.atan2(tx,tz); else if(s.vert) R.yaw=Math.atan2(-O.off.x,-O.off.z); R.group.rotation.y=R.yaw; R.grinding=true;
  Stats.tricks=(Stats.tricks||0)+Math.round(dt*40); if(typeof DASH!=="undefined") DASH.meter=Math.min(1,DASH.meter+dt*.12); if(typeof chainT!=="undefined") chainT=Math.max(chainT,1.5);
  // sparks from both skates + contact (bark: chips + leaves mixed in), scaled by speed, brighter at night
  const night=grindNight(), k=Math.min(1,O.v/20), n=Math.round(1+k*4), cols=M.col, hot=night?1:.65;
  for(let j=0;j<n;j++){ const side=j%2?1:-1, c=cols[(Math.random()*cols.length)|0], bark=s.mat==="bark";
    grindSpark(p.x+Math.cos(R.yaw)*.1*side,p.y+.02,p.z-Math.sin(R.yaw)*.1*side,bark&&Math.random()<.5?c:(night?0xfff0b0:c),-tx*O.v*.25+(Math.random()-.5)*2.5,Math.random()*2.5*(bark?.6:1)+.3,-tz*O.v*.25+(Math.random()-.5)*2.5,(bark?.6:.35)*(.6+k*.6),bark?3:10);
    if(night||!bark) G.spk.pts.material.size=.07+k*.06*(night?1.3:1); }
  G.spk.pts.material.opacity=hot; G.spk.pts.visible=true;
  if(frame%6===0) grindRumble(.12+k*.25,.25+k*.35,110);
  O.bob=Math.sin(O.t*(10+O.v*.6))*.022*k+(O.t<.15?-.05*(1-O.t/.15):0); }
function grindUpdateFX(dt,xr){ const G=GRIND, S=G.spk; if(!S) return; let any=false;
  for(let i=0;i<S.n;i++){ if(S.life[i]<=0){ S.col[i*3]=S.col[i*3+1]=S.col[i*3+2]=0; continue; } any=true; S.life[i]-=dt; const k=Math.max(0,S.life[i]); S.vel[i*3+1]-=S.grav[i]*dt;
    for(let a=0;a<3;a++){ S.pos[i*3+a]+=S.vel[i*3+a]*dt; S.col[i*3+a]=S.base[i*3+a]*Math.min(1,k*3); } }
  S.pts.visible=any; if(any){ S.pts.geometry.attributes.position.needsUpdate=true; S.pts.geometry.attributes.color.needsUpdate=true; }
  // trail ribbon from the contact point
  const T=G.trail, p=Ride.group.position; if(G.on) T.pts.unshift([p.x,p.y+.04,p.z,Math.sin(Ride.yaw),Math.cos(Ride.yaw)]); else if(T.pts.length) T.pts.pop(); if(G.on&&T.pts.length>T.n) T.pts.pop(); if(!G.on&&T.pts.length) T.pts.pop();
  T.mesh.visible=T.pts.length>1; if(T.mesh.visible){ const c=G.on&&G.on.s.mat==="bark"?[1,.75,.35]:[.55,.95,1]; for(let i=0;i<T.n;i++){ const q=T.pts[Math.min(i,T.pts.length-1)], w=.07*(1-i/T.n), f=(1-i/T.n)*(i<T.pts.length?1:0);
      T.pos.set([q[0]-q[4]*w,q[1],q[2]+q[3]*w,q[0]+q[4]*w,q[1],q[2]-q[3]*w],i*6); T.col.set([c[0]*f,c[1]*f,c[2]*f,c[0]*f,c[1]*f,c[2]*f],i*6); }
    T.mesh.geometry.attributes.position.needsUpdate=true; T.mesh.geometry.attributes.color.needsUpdate=true; }
  // vortex focus strength: ONLY while actually grinding (was also x0.45 off-grind above 7 m/s); XR: capped at 0.3 (full-screen fill per eye on Quest)
  // and off while the pole-grind helix shows (PG.k, polegrind.js) so the two additive layers never stack in the headset
  const V=G.vortex.material.uniforms, sp=Ride.speed, cap=xr?((window.PG&&PG.k>.02)?0:G.VORTEX_XR_CAP):1, want=State.mode==="ride"&&G.on?Math.min(cap,Math.max(0,Math.min(1,(sp-7)/18))):0; G.vk=(G.vk||0)+(want-(G.vk||0))*Math.min(1,dt*5);
  V.uK.value=G.vk; V.uT.value=clock; V.uXR.value=xr?1:0; V.uA.value=innerWidth/innerHeight; G.vortex.visible=G.vk>.02;
  grindAudio(!!G.on,G.on?G.on.v:0); }
function grindHUD(){ let d=document.getElementById("grindbal"); if(!d){ d=document.createElement("div"); d.id="grindbal"; d.className="hud"; d.style.cssText="position:fixed;left:50%;top:58%;width:120px;height:6px;margin-left:-60px;background:rgba(0,0,0,.35);border:1px solid rgba(127,233,255,.6);border-radius:3px;z-index:6;display:none";
    d.innerHTML='<i style="position:absolute;top:-3px;width:4px;height:12px;background:#7fe9ff;left:58px"></i>'; document.body.appendChild(d); }
  const O=GRIND.on; d.style.display=O&&!renderer.xr.isPresenting?"block":"none"; if(O){ d.firstChild.style.left=(58+O.bal*58)+"px"; d.firstChild.style.background=Math.abs(O.bal)>.8?"#ff4a6a":"#7fe9ff"; } }
function grindCtrlText(){ if(GRIND.ctrlDone||typeof PH_CTRL==="undefined") return; GRIND.ctrlDone=true; for(let i=0;i<PH_CTRL.length;i++){
    if(/^B /.test(PH_CTRL[i])) PH_CTRL[i]="B back · slide · rail: DROP OFF"; if(/^KEYS: WASD/.test(PH_CTRL[i])&&!/ C /.test(PH_CTRL[i])) PH_CTRL[i]=PH_CTRL[i].replace("SPACE","SPACE C(drop)"); if(/^L3/.test(PH_CTRL[i])) PH_CTRL[i]="L3 boost/grind kick  A jump·rail POP"; }
  if(!PH_CTRL.some(s=>/GRIND/.test(s))){ const j=PH_CTRL.findIndex(s=>/^LT/.test(s)); PH_CTRL.splice(j<0?PH_CTRL.length:j,0,"GRIND auto-locks on landing · LS lean"); } if(typeof PHONE!=="undefined") PHONE.dirty=true; }
// main hook: returns true when it moved the rider (wallStep + updateRide skipped)
function grindStep(dt){ const G=GRIND, R=Ride; if(!G.world) grindBuildWorld(); grindCtrlText(); G.cd-=dt; G.ignoreT-=dt; G.I=grindInput();
  if(G.on){ grindRide(dt); return !!G.on||true; }
  if(State.mode==="ride"&&grindTryLock(dt)){ grindRide(0); return true; } return false; }
function grindTick(dt,xr){ try{ if(!GRIND.world&&typeof rails!=="undefined"&&rails.length) grindBuildWorld(); grindUpdateFX(dt,xr); if(frame%3===0) grindHUD(); const O=GRIND.on; if(O&&!xr&&!window.__camHook){ camera.position.y+=O.bob||0; } }catch(e){ if(!window.__grindFxErr) console.warn("grind fx",e); window.__grindFxErr=e; } }
window.GRIND=GRIND;
