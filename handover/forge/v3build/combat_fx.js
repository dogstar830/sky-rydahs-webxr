// ===== COMBAT_FX (combat_fx.js, Rydah Forge) — FF7R/KH-style attack FX, look only (no gameplay, no input) =====
// Injected by patch_combat_fx.py before </body>. Inert: builds its pools on the first frame (prewarmed, hidden = 0 draws) and
// draws nothing until Systems calls the API. Budget: max 3 draws while FX are live (0 idle):
//   1 = additive sprites (InstancedBufferGeometry, 1024 slots)   2 = additive ribbons (one merged dynamic BufferGeometry: slashes + bolts)
//   3 = "ink" sprites (normal blend, black/dark crew motifs: crow feathers, thorns, claw marks)     1 shared 512x512 procedural atlas (4x4 cells).
// No per-call allocation (typed-array pools, scratch vectors), no shader compiles mid-fight (compiled at init on a private scene).
// API (crew = id string like "codee"/"karasu"/"Code : E"/"Volt", a TURF.crews index, or {id}):
//   CombatFX.hit(pos, dir, crew, strength)           impact flash + star + ring + streak sparks + crew motif (strength ~0.3..2)
//   CombatFX.slash(riderObj, arc, crew)              swept crescent; arc={start:-110,end:110 (deg from forward), radius:1.2, height:1.0,
//                                                    tilt:0 (deg roll; 60=diagonal, 90=vertical kick), width:.45, dur:.22, dir:Vector3 fwd (else obj +Z)}
//   CombatFX.lightning(from, to, crew)               jagged flickering bolt + branch + end sparks (from/to: Vector3 or Object3D, followed)
//   CombatFX.stagger(target, phase)                  phase "pressured" (amber chevrons orbit) | "staggered" (shatter burst + gold orbit) | "off"
//   CombatFX.super(rider, crew)                      limit-break / finisher burst (rings, pillar, radial streaks, motif spiral, halo)
//   CombatFX.lockOn(target)                          reticle on target (null clears)
//   CombatFX.update(dt)                              only if CombatFX.manual=true (else auto-ticked from `animated`); pass hit-stop dt (0 = freeze)
//   CombatFX.timeScale, CombatFX.paused, CombatFX.stats, CombatFX.CREWS, CombatFX.clear()
(function(){
if(window.CombatFX) return;
const Q=location.search, OFF=/[?&]nocfx\b/.test(Q);
const CREWS={
  codee:   {name:"Code : E",       c1:0xffb000, c2:0xffd84a, ink:0x060606, motif:13, motif2:0,  inkMotif:13, inkN:3, bolt:true,  road:"Lightning Road: black + gold bolts"},
  karasu:  {name:"Kogarasumaru",   c1:0xff1020, c2:0xb00010, ink:0x070308, motif:3,  motif2:0,  inkMotif:3,  inkN:5, bolt:false, road:"Wing Road: black + red crow feathers"},
  static:  {name:"Static Angels",  c1:0xa040ff, c2:0x5ff4ff, ink:0,        motif:6,  motif2:0,  inkMotif:-1, inkN:0, bolt:false, road:"purple wings + cyan halo"},
  anubis:  {name:"Anubis",         c1:0x00d6b4, c2:0xffd889, ink:0,        motif:14, motif2:8,  inkMotif:-1, inkN:0, bolt:false, road:"teal ankh + sand-gold shards"},
  forest:  {name:"Sleeping Forest",c1:0x12a845, c2:0xe8ffe8, ink:0x0b3a1a, motif:4,  motif2:2,  inkMotif:5,  inkN:4, bolt:false, road:"Thorn Road: white + deep green leaves/thorns"},
  behemoth:{name:"Behemoth",       c1:0xff5a00, c2:0xff9a1a, ink:0x0a0604, motif:8,  motif2:0,  inkMotif:8,  inkN:5, bolt:false, road:"orange shock + black rock shards"},
  genesis: {name:"Genesis",        c1:0xff2bd6, c2:0xffd36a, ink:0,        motif:6,  motif2:0,  inkMotif:-1, inkN:0, bolt:false, road:"magenta + gold halo stars"},
  ttt:     {name:"Tool Toul To",   c1:0xd0602a, c2:0xb8bcc4, ink:0x3a3c40, motif:9,  motif2:8,  inkMotif:9,  inkN:3, bolt:false, road:"rust gears + gray rivets"},
  volt:    {name:"Volt",           c1:0xff2f78, c2:0xfff23a, ink:0,        motif:13, motif2:0,  inkMotif:-1, inkN:0, bolt:true,  road:"hot pink + yellow arcs"},
  rustclaw:{name:"Rust Claw",      c1:0xff6a10, c2:0xb8400c, ink:0x3a1406, motif:7,  motif2:8,  inkMotif:7,  inkN:3, bolt:false, road:"orange/rust claw marks"} };
const ALIAS={codee:"codee",codeе:"codee",code:"codee",codee_:"codee",caali:"codee",anika:"codee",karasu:"karasu",kogarasumaru:"karasu",ikki:"karasu",crow:"karasu",
  static:"static",staticangels:"static",anubis:"anubis",forest:"forest",sleepingforest:"forest",behemoth:"behemoth",genesis:"genesis",ttt:"ttt",tooltoulto:"ttt",
  volt:"volt",teamstorm:"volt",storm:"volt",rustclaw:"rustclaw",rust:"rustclaw"};
for(const k in CREWS){ const c=CREWS[k]; c.id=k; c.C1=new THREE.Color(c.c1); c.C2=new THREE.Color(c.c2); c.INK=new THREE.Color(c.ink); }
const _crewCache={};
function crewOf(c){ if(c&&c.C1) return c; let k=c;
  if(typeof c==="number"){ try{ k=TURF.crews[c].id; }catch(e){ k=""; } } else if(c&&typeof c==="object") k=c.id||c.crew||"";
  k=String(k||"").toLowerCase(); if(_crewCache[k]) return _crewCache[k];
  const n=k.replace(/[^a-z]/g,""); return (_crewCache[k]=CREWS[ALIAS[n]||n]||CREWS.codee); }
// ---------- atlas: 512x512, 4x4 cells of 128; R = shape mask, G = hot core mask ----------
const CELLS=["spark","ring","dot","feather","leaf","thorn","halo","claw","shard","gear","reticle","chevron","shatter","bolt","ankh","burst"];
function drawCell(x,i,core){ const k=core?1:0; x.fillStyle=x.strokeStyle="#fff"; x.lineCap="round"; x.lineJoin="miter";
  const P=(pts)=>{ x.beginPath(); x.moveTo(pts[0],pts[1]); for(let j=2;j<pts.length;j+=2) x.lineTo(pts[j],pts[j+1]); x.closePath(); x.fill(); };
  const sc=core?.55:1;
  switch(i){
  case 0: { const a=.95*sc,b=.1*sc; P([0,-a,b,-b,a,0,b,b,0,a,-b,b,-a,0,-b,-b]); break; }
  case 1: x.lineWidth=core?.05:.15; x.beginPath(); x.arc(0,0,.8,0,7); x.stroke(); break;
  case 2: { const g=x.createRadialGradient(0,0,0,0,0,core?.35:.95); g.addColorStop(0,"#fff"); g.addColorStop(core?.5:.25,"rgba(255,255,255,.8)"); g.addColorStop(1,"rgba(255,255,255,0)"); x.fillStyle=g; x.fillRect(-1,-1,2,2); break; }
  case 3: if(core){ x.lineWidth=.05; x.beginPath(); x.moveTo(0,.95); x.lineTo(0,-.7); x.stroke(); }
          else { x.beginPath(); x.moveTo(0,-.95); x.quadraticCurveTo(.42,-.3,.22,.55); x.lineTo(.08,.45); x.lineTo(.02,.95); x.lineTo(-.02,.95); x.lineTo(-.1,.3); x.lineTo(-.3,.38);
            x.quadraticCurveTo(-.4,-.25,0,-.95); x.fill(); x.globalCompositeOperation="destination-out"; x.lineWidth=.05; for(const y of [-.25,.05]){ x.beginPath(); x.moveTo(.35,y); x.lineTo(.05,y+.18); x.stroke(); } x.globalCompositeOperation="source-over"; } break;
  case 4: if(core){ x.lineWidth=.06; x.beginPath(); x.moveTo(0,.9); x.lineTo(0,-.75); x.stroke(); }
          else { x.beginPath(); x.moveTo(0,-.95); x.quadraticCurveTo(.62,-.2,0,.8); x.quadraticCurveTo(-.62,-.2,0,-.95); x.fill(); x.lineWidth=.06; x.beginPath(); x.moveTo(0,.75); x.lineTo(0,.98); x.stroke(); } break;
  case 5: x.beginPath(); x.moveTo(-.22*sc,.9); x.quadraticCurveTo(-.05,.0,.5*sc,-.95); x.quadraticCurveTo(.05*sc,.1,.22*sc,.9); x.closePath(); x.fill(); break;
  case 6: x.lineWidth=core?.04:.11; x.beginPath(); x.ellipse(0,0,.86,.32,0,0,7); x.stroke(); if(!core){ x.lineWidth=.04; x.beginPath(); x.ellipse(0,0,.66,.2,0,0,7); x.stroke(); } break;
  case 7: for(let j=-1;j<=1;j++){ const o=j*.34; x.beginPath(); x.moveTo(o-.25,-.92); x.quadraticCurveTo(o+.22*sc,0,o-.15,.92); x.quadraticCurveTo(o+(core?.04:.02),0,o-.25,-.92); x.fill(); } break;
  case 8: P([0,-.95*sc,.38*sc,-.1*sc,.12*sc,.9*sc,-.3*sc,.2*sc]); break;
  case 9: if(core){ x.lineWidth=.06; x.beginPath(); x.arc(0,0,.5,0,7); x.stroke(); } else { x.beginPath(); for(let j=0;j<16;j++){ const a=j/16*6.283, r=j%2?.62:.88; x.lineTo(Math.cos(a)*r,Math.sin(a)*r); x.lineTo(Math.cos(a+.39)*r,Math.sin(a+.39)*r); } x.closePath(); x.fill();
            x.globalCompositeOperation="destination-out"; x.beginPath(); x.arc(0,0,.3,0,7); x.fill(); x.globalCompositeOperation="source-over"; } break;
  case 10: x.lineWidth=core?.03:.08; for(let j=0;j<4;j++){ const a=j*1.5708+.25; x.beginPath(); x.arc(0,0,.72,a,a+1.07); x.stroke(); }
           for(let j=0;j<4;j++){ x.save(); x.rotate(j*1.5708); P([0,-.98,.1,-.78,-.1,-.78]); x.restore(); } if(!core){ x.beginPath(); x.arc(0,0,.07,0,7); x.fill(); } break;
  case 11: x.lineWidth=core?.07:.2; x.lineCap="butt"; x.beginPath(); x.moveTo(-.7,-.35); x.lineTo(0,.35); x.lineTo(.7,-.35); x.stroke(); break;
  case 12: x.lineWidth=core?.05:.14; for(let j=0;j<7;j++){ const a=j/7*6.283+.2; x.beginPath(); x.arc(0,0,.78+(j%2?.06:-.04),a,a+.72); x.stroke(); }
           if(!core) for(let j=0;j<7;j++){ const a=j/7*6.283+.1; x.save(); x.rotate(a); P([.62,0,.98,-.05,.98,.05]); x.restore(); } break;
  case 13: P([.15*sc,-.95,-.42*sc,.08,-.02*sc,.06,-.2*sc,.95,.45*sc,-.15,.05*sc,-.12]); break;
  case 14: x.lineWidth=core?.07:.18; x.lineCap="butt"; x.beginPath(); x.ellipse(0,-.5,.25,.32,0,0,7); x.stroke(); x.beginPath(); x.moveTo(0,-.18); x.lineTo(0,.95); x.moveTo(-.55,0); x.lineTo(.55,0); x.stroke(); break;
  case 15: for(let j=0;j<12;j++){ const a=j/12*6.283, r=(j%2?.6:.98)*sc, w=.07; x.save(); x.rotate(a); P([0,-r,w,-.15,0,0,-w,-.15]); x.restore(); } x.beginPath(); x.arc(0,0,.22*sc,0,7); x.fill(); break; } }
function makeAtlas(){ const S=512, C=128, mk=core=>{ const c=document.createElement("canvas"); c.width=c.height=S; const x=c.getContext("2d"); x.fillStyle="#000"; x.fillRect(0,0,S,S);
    for(let i=0;i<16;i++){ x.save(); x.translate((i%4)*C+C/2,((i/4)|0)*C+C/2); x.scale(C*.47,C*.47); drawCell(x,i,core); x.restore(); } return x.getImageData(0,0,S,S); };
  const A=mk(false), B=mk(true), out=document.createElement("canvas"); out.width=out.height=S; const ox=out.getContext("2d"), D=ox.createImageData(S,S);
  for(let p=0;p<S*S*4;p+=4){ D.data[p]=A.data[p]; D.data[p+1]=Math.min(A.data[p],B.data[p]); D.data[p+2]=0; D.data[p+3]=255; } ox.putImageData(D,0,0);
  const t=new THREE.CanvasTexture(out); t.generateMipmaps=true; t.minFilter=THREE.LinearMipmapLinearFilter; t.magFilter=THREE.LinearFilter; t.anisotropy=2; FX.atlasCanvas=out; return t; }
// ---------- sprite pools ----------
const VS=`attribute vec3 iPos; attribute vec3 iDir; attribute vec3 iCol; attribute vec4 iA; attribute vec2 iC;
varying vec2 vUv; varying vec3 vCol; varying float vA;
void main(){ vec2 c=position.xy; float s=iA.x, r=iA.y, cs=cos(r), sn=sin(r); vec2 rc=vec2(c.x*cs-c.y*sn,c.x*sn+c.y*cs);
  float cell=iC.x, col=mod(cell,4.), row=floor(cell/4.+.01); vUv=vec2((col+c.x+.5)/4.,1.-(row+1.)/4.+(c.y+.5)/4.); vCol=iCol; vA=iA.z; vec4 mv;
  if(iA.w<.5){ mv=viewMatrix*vec4(iPos,1.); mv.xy+=rc*s; }
  else if(iA.w<1.5){ vec3 n=normalize(iDir); vec3 t=normalize(abs(n.y)<.98?cross(n,vec3(0.,1.,0.)):cross(n,vec3(1.,0.,0.))); vec3 b=cross(n,t); mv=viewMatrix*vec4(iPos+(t*rc.x+b*rc.y)*s,1.); }
  else { mv=viewMatrix*vec4(iPos,1.); vec3 d=(viewMatrix*vec4(iDir,0.)).xyz; vec2 ax=length(d.xy)>1e-5?normalize(d.xy):vec2(1.,0.); vec2 pe=vec2(-ax.y,ax.x);
    vUv=vec2((col+c.y+.5)/4.,1.-(row+1.)/4.+(c.x+.5)/4.); mv.xy+=ax*(c.x-.35)*s*iC.y+pe*c.y*s; }
  gl_Position=projectionMatrix*mv; }`;
const FS_ADD=`uniform sampler2D map; uniform float uGain; uniform float uCap; uniform float uOcc; varying vec2 vUv; varying vec3 vCol; varying float vA;
void main(){ vec4 t=texture2D(map,vUv); float m=t.r; if(m*vA<.004) discard; float wh=step(2.9,vCol.r+vCol.g+vCol.b); vec3 hot=mix(vCol*1.35,vec3(1.),wh*.8);
  vec3 c=(vCol*m+hot*t.g*.6)*vA*uGain; float mx=max(c.r,max(c.g,c.b)); c*=min(1.,uCap/max(mx,1e-4));
  gl_FragColor=vec4(c,clamp(m*vA,0.,1.)*uOcc); }`;
const FS_INK=`uniform sampler2D map; varying vec2 vUv; varying vec3 vCol; varying float vA;
void main(){ float a=smoothstep(.38,.62,texture2D(map,vUv).r)*vA; if(a<.02) discard; gl_FragColor=vec4(vCol,a); }`;
function Pool(N,ink){ const p={N,live:0,cur:0}; const f=()=>new Float32Array(N);
  Object.assign(p,{px:f(),py:f(),pz:f(),vx:f(),vy:f(),vz:f(),dx:f(),dy:f(),dz:f(),life:f(),max:f(),s0:f(),s1:f(),rot:f(),rotv:f(),a0:f(),cr:f(),cg:f(),cb:f(),
    cell:f(),mode:f(),str:f(),grav:f(),drag:f(),ox:f(),oy:f(),oz:f(),orR:f(),orW:f(),orA:f(),vdir:f(),owner:new Int16Array(N),follow:new Array(N).fill(null)});
  const g=new THREE.InstancedBufferGeometry(); g.setAttribute("position",new THREE.BufferAttribute(new Float32Array([-.5,-.5,0,.5,-.5,0,.5,.5,0,-.5,.5,0]),3)); g.setIndex([0,1,2,0,2,3]);
  const ia=(k,name)=>{ const a=new THREE.InstancedBufferAttribute(new Float32Array(N*k),k); a.setUsage(THREE.DynamicDrawUsage); g.setAttribute(name,a); return a; };
  p.aPos=ia(3,"iPos"); p.aDir=ia(3,"iDir"); p.aCol=ia(3,"iCol"); p.aA=ia(4,"iA"); p.aC=ia(2,"iC"); g.instanceCount=0;
  const m=new THREE.ShaderMaterial({ vertexShader:VS, fragmentShader:ink?FS_INK:FS_ADD, uniforms:{map:{value:FX.atlas},uGain:{value:1.0},uCap:{value:.92},uOcc:{value:.75}}, transparent:true, depthWrite:false, depthTest:true,
    blending:ink?THREE.NormalBlending:THREE.CustomBlending, blendEquation:THREE.AddEquation, blendSrc:THREE.OneFactor, blendDst:THREE.OneMinusSrcAlphaFactor, fog:false, side:THREE.DoubleSide });
  const mesh=new THREE.Mesh(g,m); mesh.frustumCulled=false; mesh.renderOrder=ink?8990:9010; mesh.userData.noMerge=true; mesh.name=ink?"combatfx_ink":"combatfx_sprites"; mesh.visible=false;
  p.g=g; p.mesh=mesh; return p; }
// emit params (scratch, reset by e0) -> no allocation per spawn
const E={};
function e0(){ E.x=E.y=E.z=0; E.vx=E.vy=E.vz=0; E.dx=0; E.dy=1; E.dz=0; E.life=.2; E.s0=.3; E.s1=.3; E.rot=0; E.rotv=0; E.a=1; E.r=1; E.g=1; E.b=1; E.cell=0; E.mode=0; E.str=1;
  E.grav=0; E.drag=0; E.follow=null; E.ox=E.oy=E.oz=0; E.orR=0; E.orW=0; E.orA=0; E.vdir=0; E.owner=0; return E; }
function col(c){ E.r=c.r; E.g=c.g; E.b=c.b; return E; }
function put(p){ let i=-1; for(let k=0;k<p.N;k++){ const j=(p.cur+k)%p.N; if(p.life[j]<=0&&p.max[j]>=0){ i=j; break; } } if(i<0) i=p.cur; p.cur=(i+1)%p.N;
  p.px[i]=E.x; p.py[i]=E.y; p.pz[i]=E.z; p.vx[i]=E.vx; p.vy[i]=E.vy; p.vz[i]=E.vz; p.dx[i]=E.dx; p.dy[i]=E.dy; p.dz[i]=E.dz; p.life[i]=E.life>0?E.life:1; p.max[i]=E.life;
  p.s0[i]=E.s0; p.s1[i]=E.s1; p.rot[i]=E.rot; p.rotv[i]=E.rotv; p.a0[i]=E.a; p.cr[i]=E.r; p.cg[i]=E.g; p.cb[i]=E.b; p.cell[i]=E.cell; p.mode[i]=E.mode; p.str[i]=E.str;
  p.grav[i]=E.grav; p.drag[i]=E.drag; p.follow[i]=E.follow; p.ox[i]=E.ox; p.oy[i]=E.oy; p.oz[i]=E.oz; p.orR[i]=E.orR; p.orW[i]=E.orW; p.orA[i]=E.orA; p.vdir[i]=E.vdir; p.owner[i]=E.owner; return i; }
function under(i,k){ const a=FX.add, p=FX.ink; e0(); E.x=a.px[i];E.y=a.py[i];E.z=a.pz[i]; E.vx=a.vx[i];E.vy=a.vy[i];E.vz=a.vz[i]; E.dx=a.dx[i];E.dy=a.dy[i];E.dz=a.dz[i];
  E.life=a.max[i]; E.s0=a.s0[i]*(k||1.18); E.s1=a.s1[i]*(k||1.18); E.rot=a.rot[i]; E.rotv=a.rotv[i]; E.a=.8; E.r=a.cr[i]*.1; E.g=a.cg[i]*.1; E.b=a.cb[i]*.1; E.cell=a.cell[i]; E.mode=a.mode[i];
  E.grav=a.grav[i]; E.drag=a.drag[i]; E.follow=a.follow[i]; E.ox=a.ox[i]; E.oy=a.oy[i]; E.oz=a.oz[i]; E.orR=a.orR[i]; E.orW=a.orW[i]; E.orA=a.orA[i]; E.owner=a.owner[i]; return put(p); }
const putU=(k)=>under(put(FX.add),k);
const _v=new THREE.Vector3(), _w=new THREE.Vector3(), _u=new THREE.Vector3(), _cam=new THREE.Vector3(), _F=new THREE.Vector3(), _S=new THREE.Vector3(), UP=new THREE.Vector3(0,1,0);
function objOf(t){ if(!t) return null; if(t.holder&&t.holder.isObject3D) return t.holder; if(t.isObject3D) return t; if(t.group&&t.group.isObject3D) return t.group; return null; }
function posOf(t,out){ const o=objOf(t); if(o) return o.getWorldPosition(out); if(t&&t.isVector3) return out.copy(t); if(t&&t.x!==undefined) return out.set(t.x,t.y,t.z); return out.set(0,0,0); }
function tickPool(p,dt){ let k=0; const P=p.aPos.array,D=p.aDir.array,C=p.aCol.array,A=p.aA.array,CC=p.aC.array;
  for(let i=0;i<p.N;i++){ if(p.life[i]<=0) continue; const per=p.max[i]<0; if(!per){ p.life[i]-=dt; if(p.life[i]<=0){ p.follow[i]=null; continue; } }
    const t=per?0:1-p.life[i]/p.max[i]; let x,y,z;
    if(p.follow[i]){ posOf(p.follow[i],_v); p.orA[i]+=p.orW[i]*dt; x=_v.x+p.ox[i]+Math.cos(p.orA[i])*p.orR[i]; y=_v.y+p.oy[i]; z=_v.z+p.oz[i]+Math.sin(p.orA[i])*p.orR[i]; p.oy[i]+=p.vy[i]*dt; }
    else { const dr=Math.exp(-p.drag[i]*dt); p.vx[i]*=dr; p.vz[i]*=dr; p.vy[i]=p.vy[i]*dr-p.grav[i]*dt; p.px[i]+=p.vx[i]*dt; p.py[i]+=p.vy[i]*dt; p.pz[i]+=p.vz[i]*dt; x=p.px[i]; y=p.py[i]; z=p.pz[i];
      if(p.orW[i]){ p.orA[i]+=p.orW[i]*dt; } }
    p.rot[i]+=p.rotv[i]*dt; const e=1-(1-t)*(1-t)*(1-t); let s=p.s0[i]+(p.s1[i]-p.s0[i])*e, a=p.a0[i]*(t<.2?1:1-((t-.2)/.8)*((t-.2)/.8));
    if(per){ const q=.85+.15*Math.sin(FX.time*9+i); s*=q; }
    const b3=k*3; P[b3]=x; P[b3+1]=y; P[b3+2]=z;
    if(p.vdir[i]){ D[b3]=p.vx[i]; D[b3+1]=p.vy[i]; D[b3+2]=p.vz[i]; } else { D[b3]=p.dx[i]; D[b3+1]=p.dy[i]; D[b3+2]=p.dz[i]; }
    C[b3]=p.cr[i]; C[b3+1]=p.cg[i]; C[b3+2]=p.cb[i]; const b4=k*4; A[b4]=s; A[b4+1]=p.rot[i]; A[b4+2]=a; A[b4+3]=p.mode[i]; CC[k*2]=p.cell[i]; CC[k*2+1]=p.str[i]; k++; }
  p.live=k; p.g.instanceCount=k; p.mesh.visible=k>0; if(k){ for(const a of [p.aPos,p.aDir,p.aCol,p.aA,p.aC]){ a.needsUpdate=true; } } }
// ---------- ribbons (slash crescents + lightning), one merged dynamic geometry ----------
const RB={ MAX:24, SEG:28, rs:[], mesh:null };
function rbBuild(){ const S=RB.SEG, V=RB.MAX*S*2, g=new THREE.BufferGeometry();
  RB.pos=new Float32Array(V*3); RB.aux=new Float32Array(V*3); RB.col=new Float32Array(V*3);
  g.setAttribute("position",new THREE.BufferAttribute(RB.pos,3).setUsage(THREE.DynamicDrawUsage)); g.setAttribute("aux",new THREE.BufferAttribute(RB.aux,3).setUsage(THREE.DynamicDrawUsage));
  g.setAttribute("rcol",new THREE.BufferAttribute(RB.col,3).setUsage(THREE.DynamicDrawUsage));
  const I=[]; for(let r=0;r<RB.MAX;r++) for(let i=0;i<S-1;i++){ const a=(r*S+i)*2; I.push(a,a+1,a+2,a+1,a+3,a+2); } g.setIndex(I); g.setDrawRange(0,0);
  const m=new THREE.ShaderMaterial({ transparent:true, depthWrite:false, blending:THREE.CustomBlending, blendEquation:THREE.AddEquation, blendSrc:THREE.OneFactor, blendDst:THREE.OneMinusSrcAlphaFactor, side:THREE.DoubleSide, fog:false, uniforms:{uGain:{value:1.0}},
    vertexShader:`attribute vec3 aux; attribute vec3 rcol; varying vec3 vA; varying vec3 vC; void main(){ vA=aux; vC=rcol; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
    fragmentShader:`uniform float uGain; varying vec3 vA; varying vec3 vC; void main(){ float u=vA.x, v=vA.y, fade=vA.z; vec3 hot=vC*1.3; vec3 c;
      if(fade<0.){ float x=1.-abs(v*2.-1.); float m=step(.12,x); c=vC*m*1.1+hot*step(.62,x)*1.2; c*=(1.-u*u)*(-fade); }            // bolt: hard toon core
      else { float m=step(.03,v); c=vC*m*(.25+.75*v*v)+hot*step(.82,v)*(1.-u)*1.3; c*=fade*(1.-u)*(.4+.6*(1.-u)); }                  // slash: bright outer edge, inner falloff
      c*=uGain; float mx=max(c.r,max(c.g,c.b)); c*=min(1.,.85/max(mx,1e-4)); gl_FragColor=vec4(c,clamp(mx*1.6,0.,1.)*.75); }` });
  const mesh=new THREE.Mesh(g,m); mesh.frustumCulled=false; mesh.renderOrder=9005; mesh.userData.noMerge=true; mesh.name="combatfx_ribbons"; mesh.visible=false; RB.mesh=mesh;
  for(let i=0;i<RB.MAX;i++) RB.rs.push({att:null,n:0,samp:.2,on:false,kind:0,life:0,max:1,obj:null,c:new THREE.Color(),r:1,h:1,a0:0,a1:0,tilt:0,w:.4,F:new THREE.Vector3(),C:new THREE.Vector3(),
    A:new THREE.Vector3(),B:new THREE.Vector3(),fo:null,to:null,regen:0,seed:0,amp:.12,pts:new Float32Array(RB.SEG*3),wid:.06}); }
function rbGet(){ let best=RB.rs[0]; for(const r of RB.rs){ if(!r.on) return r; if(r.life<best.life) best=r; } return best; }
function rnd(s){ s=Math.sin(s*127.1+311.7)*43758.5453; return s-Math.floor(s); }
function boltPts(r){ const S=RB.SEG, P=r.pts; posOf(r.fo||r.A,_v); if(r.fo) r.A.copy(_v); posOf(r.to||r.B,_w); if(r.to) r.B.copy(_w);
  _v.copy(r.A); _w.copy(r.B); _u.subVectors(_w,_v); const L=_u.length()||1; _S.crossVectors(_u,UP); if(_S.lengthSq()<1e-6) _S.set(1,0,0); _S.normalize(); _F.crossVectors(_S,_u).normalize();
  let ox=0,oy=0; for(let i=0;i<S;i++){ const t=i/(S-1), env=Math.sin(Math.PI*t), sd=r.seed+i*1.7;
    if(i%3===0){ ox=(rnd(sd)-.5)*2*r.amp*L*env; oy=(rnd(sd+9.1)-.5)*2*r.amp*L*env; }
    P[i*3]=_v.x+_u.x*t+_S.x*ox+_F.x*oy; P[i*3+1]=_v.y+_u.y*t+_S.y*ox+_F.y*oy; P[i*3+2]=_v.z+_u.z*t+_S.z*ox+_F.z*oy; } }
function rbTick(dt){ const S=RB.SEG, Pp=RB.pos, Ax=RB.aux, Cc=RB.col; camera.getWorldPosition(_cam); let k=0;
  for(const r of RB.rs){ if(!r.on) continue; r.life-=dt; if(r.life<=0){ r.on=false; r.obj=r.fo=r.to=r.att=null; continue; } const t=1-r.life/r.max, base=k*S*2;
    if(r.kind===2){ r.regen-=dt; if(r.regen<=0){ r.regen=.034; r.seed+=1.37; boltPts(r); } const P=r.pts, fade=-(t<.3?1:1-(t-.3)/.7);
      for(let i=0;i<S;i++){ const j=Math.min(i+1,S-1), h=Math.max(i-1,0); const tx=P[j*3]-P[h*3], ty=P[j*3+1]-P[h*3+1], tz=P[j*3+2]-P[h*3+2], x=P[i*3],y=P[i*3+1],z=P[i*3+2];
        const vx=_cam.x-x,vy=_cam.y-y,vz=_cam.z-z; let nx=ty*vz-tz*vy, ny=tz*vx-tx*vz, nz=tx*vy-ty*vx; const nl=Math.hypot(nx,ny,nz)||1, w=r.wid*(.55+.45*Math.sin(Math.PI*i/(S-1)))/nl;
        nx*=w; ny*=w; nz*=w; const b=(base+i*2)*3; Pp[b]=x-nx;Pp[b+1]=y-ny;Pp[b+2]=z-nz;Pp[b+3]=x+nx;Pp[b+4]=y+ny;Pp[b+5]=z+nz;
        const u=Math.abs(i/(S-1)-.5)*1.2; Ax[b]=u;Ax[b+1]=0;Ax[b+2]=fade;Ax[b+3]=u;Ax[b+4]=1;Ax[b+5]=fade; Cc[b]=Cc[b+3]=r.c.r;Cc[b+1]=Cc[b+4]=r.c.g;Cc[b+2]=Cc[b+5]=r.c.b; } }
    else if(r.kind===3){ const P=r.pts; if(t<r.samp&&r.att){ r.att.getWorldPosition(_v); P.copyWithin(3,0,(S-1)*3); P[0]=_v.x;P[1]=_v.y;P[2]=_v.z; if(r.n<S) r.n++; }
      else { P.copyWithin(3,0,(S-1)*3); r.n=Math.max(1,r.n-2); }   // after sampling: tail catches the head
      const n=Math.max(2,r.n), fade=-(t<.5?1:1-(t-.5)/.5);
      for(let i=0;i<S;i++){ const q=Math.min(i,n-1), j=Math.min(q+1,n-1), h=Math.max(q-1,0); const x=P[q*3],y=P[q*3+1],z=P[q*3+2]; let tx=P[h*3]-P[j*3], ty=P[h*3+1]-P[j*3+1], tz=P[h*3+2]-P[j*3+2]; if(tx*tx+ty*ty+tz*tz<1e-10){ tx=1;ty=0;tz=0; }
        const vx=_cam.x-x,vy=_cam.y-y,vz=_cam.z-z; let nx=ty*vz-tz*vy, ny=tz*vx-tx*vz, nz=tx*vy-ty*vx; const nl=Math.hypot(nx,ny,nz)||1, u=q/(S-1), w=r.wid*(1-u)/nl;
        nx*=w; ny*=w; nz*=w; const b=(base+i*2)*3; Pp[b]=x-nx;Pp[b+1]=y-ny;Pp[b+2]=z-nz;Pp[b+3]=x+nx;Pp[b+4]=y+ny;Pp[b+5]=z+nz;
        Ax[b]=u;Ax[b+1]=0;Ax[b+2]=fade;Ax[b+3]=u;Ax[b+4]=1;Ax[b+5]=fade; Cc[b]=Cc[b+3]=r.c.r;Cc[b+1]=Cc[b+4]=r.c.g;Cc[b+2]=Cc[b+5]=r.c.b; }
      if(t<r.samp&&r.crew){ r.shed-=dt; if(r.shed<=0){ r.shed=.04; shedMotif(r.crew,P[0],P[1],P[2]); } } }
    else { if(r.obj){ posOf(r.obj,r.C); } const eo=x=>1-(1-x)*(1-x)*(1-x), ph=eo(Math.min(1,t/.55)), pt=eo(Math.max(0,(t-.18)/.82));
      const hd=r.a0+(r.a1-r.a0)*ph, tl=r.a0+(r.a1-r.a0)*pt; _F.copy(r.F); _S.crossVectors(_F,UP).normalize(); const ct=Math.cos(r.tilt), st=Math.sin(r.tilt);
      const sx=_S.x*ct, sy=st, sz=_S.z*ct; const fade=t<.6?1:1-(t-.6)/.4;
      for(let i=0;i<S;i++){ const u=i/(S-1), a=hd+(tl-hd)*u, ca=Math.cos(a), sa=Math.sin(a); const dx=_F.x*ca+sx*sa, dy=sy*sa, dz=_F.z*ca+sz*sa;
        const ri=r.r-r.w*(1-u*.85), ro=r.r+r.w*.18*(1-u), cx=r.C.x, cy=r.C.y+r.h, cz=r.C.z, b=(base+i*2)*3;
        Pp[b]=cx+dx*ri;Pp[b+1]=cy+dy*ri;Pp[b+2]=cz+dz*ri;Pp[b+3]=cx+dx*ro;Pp[b+4]=cy+dy*ro;Pp[b+5]=cz+dz*ro;
        Ax[b]=u;Ax[b+1]=0;Ax[b+2]=fade;Ax[b+3]=u;Ax[b+4]=1;Ax[b+5]=fade; Cc[b]=Cc[b+3]=r.c.r;Cc[b+1]=Cc[b+4]=r.c.g;Cc[b+2]=Cc[b+5]=r.c.b; }
      r._hx=r.C.x+(_F.x*Math.cos(hd)+sx*Math.sin(hd))*r.r; r._hy=r.C.y+r.h+sy*Math.sin(hd)*r.r; r._hz=r.C.z+(_F.z*Math.cos(hd)+sz*Math.sin(hd))*r.r;
      if(t<.55&&r.crew){ r.shed-=dt; if(r.shed<=0){ r.shed=.03; shedMotif(r.crew,r._hx,r._hy,r._hz); } } }
    if(++k>=RB.MAX) break; }
  const g=RB.mesh.geometry; g.setDrawRange(0,k*(S-1)*6); RB.mesh.visible=k>0; RB.live=k; if(k){ g.attributes.position.needsUpdate=g.attributes.aux.needsUpdate=g.attributes.rcol.needsUpdate=true; } }
// ---------- FX core ----------
const FX={ ready:false, time:0, timeScale:1, paused:false, manual:false, stats:{}, CREWS, crewOf, CELLS };
window.CombatFX=FX;
function init(){ if(FX.ready||OFF) return FX.ready; if(typeof scene==="undefined"||!scene||typeof camera==="undefined"||!camera||typeof renderer==="undefined"||!renderer) return false;
  FX.atlas=makeAtlas(); FX.add=Pool(1024,false); FX.ink=Pool(512,true); rbBuild();
  const tmp=new THREE.Scene(); for(const m of [FX.add.mesh,FX.ink.mesh,RB.mesh]){ m.visible=true; tmp.add(m); } FX.add.g.instanceCount=1; FX.ink.g.instanceCount=1;
  const t0=performance.now(); try{ renderer.compile(tmp,camera); }catch(e){ console.warn("CombatFX prewarm",e); } FX.stats.prewarmMs=Math.round(performance.now()-t0);
  for(const m of [FX.add.mesh,FX.ink.mesh,RB.mesh]){ tmp.remove(m); m.visible=false; scene.add(m); } FX.add.g.instanceCount=0; FX.ink.g.instanceCount=0;
  FX.ready=true; return true; }
let _last=0;
function update(dt){ if(!FX.ready&&!init()) return; if(FX.paused) dt=0; dt*=FX.timeScale; FX.time+=dt; tickPool(FX.add,dt); tickPool(FX.ink,dt); rbTick(dt); tickDemo(dt);
  if(FX.hide){ FX.add.mesh.visible=FX.ink.mesh.visible=RB.mesh.visible=false; }
  const s=FX.stats; s.sprites=FX.add.live; s.ink=FX.ink.live; s.ribbons=RB.live; s.draws=(FX.add.live?1:0)+(FX.ink.live?1:0)+(RB.live?1:0); }
FX.update=dt=>update(dt||0);
FX.clear=()=>{ for(const p of [FX.add,FX.ink]) if(p){ p.life.fill(0); p.max.fill(0); p.follow.fill(null); } for(const r of RB.rs) r.on=false; ST.forEach(s=>{ s.obj=null; }); LOCK.obj=null; };
function autoTick(){ const n=performance.now(), dt=_last?Math.min(.05,(n-_last)/1000):0; _last=n; if(!FX.manual) update(dt); }
if(typeof animated!=="undefined"&&animated.push) animated.push(autoTick); else { const loop=()=>{ autoTick(); requestAnimationFrame(loop); }; requestAnimationFrame(loop); }
const R=Math.random, TAU=6.2832;
function shedMotif(c,x,y,z){ e0(); col(R()<.5?c.C1:c.C2); E.x=x;E.y=y;E.z=z; E.vx=(R()-.5)*1.2;E.vy=R()*1.2;E.vz=(R()-.5)*1.2; E.cell=c.motif; E.life=.35+R()*.2; E.s0=.22; E.s1=.12; E.rot=R()*TAU; E.rotv=(R()-.5)*8; E.drag=2; E.grav=c.motif===3||c.motif===4?1.2:3; putU(1.25);
  if(c.inkMotif>=0&&R()<.5){ e0(); col(c.INK); E.x=x;E.y=y;E.z=z; E.vx=(R()-.5)*1.5;E.vy=R()*1.5;E.vz=(R()-.5)*1.5; E.cell=c.inkMotif; E.life=.45; E.s0=.26; E.s1=.2; E.rot=R()*TAU; E.rotv=(R()-.5)*6; E.drag=2; E.grav=1.5; put(FX.ink); } }
function sparks(c,x,y,z,dx,dy,dz,n,spd,len){ for(let i=0;i<n;i++){ e0(); col(i%3?c.C1:c.C2); let vx=dx+(R()-.5)*1.6, vy=dy+(R()-.5)*1.6, vz=dz+(R()-.5)*1.6; const l=Math.hypot(vx,vy,vz)||1, s=spd*(.5+R()*.8);
    E.x=x;E.y=y;E.z=z; E.vx=vx/l*s;E.vy=vy/l*s;E.vz=vz/l*s; E.mode=2; E.vdir=1; E.cell=2; E.str=len*(.7+R()*.6); E.s0=.07; E.s1=.03; E.life=.16+R()*.14; E.drag=7; E.grav=4; put(FX.add); } }
function motifBurst(c,x,y,z,n,spd){ for(let i=0;i<n;i++){ e0(); col(i%2?c.C1:c.C2); const a=R()*TAU, u=R()*2-1, s=spd*(.4+R()*.8), q=Math.sqrt(1-u*u);
    E.x=x;E.y=y;E.z=z; E.vx=Math.cos(a)*q*s; E.vy=u*s*.7+s*.3; E.vz=Math.sin(a)*q*s; E.cell=i%3===2?c.motif2:c.motif; E.life=.35+R()*.3; E.s0=.32; E.s1=.18; E.rot=R()*TAU; E.rotv=(R()-.5)*10; E.drag=3; E.grav=2; putU(1.25); }
  for(let i=0;i<c.inkN*(n>8?2:1);i++){ e0(); col(c.INK); const a=R()*TAU, s=spd*(.3+R()*.7); E.x=x;E.y=y;E.z=z; E.vx=Math.cos(a)*s; E.vy=R()*s; E.vz=Math.sin(a)*s;
    E.cell=c.inkMotif; E.life=.45+R()*.25; E.s0=.38; E.s1=.3; E.rot=R()*TAU; E.rotv=(R()-.5)*7; E.drag=3; E.grav=2.2; put(FX.ink); } }
// hit(pos, dir, crew, strength): ~0.25 s, frame-1 flash so it reads through hit-stop
FX.hit=function(pos,dir,crew,strength){ if(!FX.ready&&!init()) return; const c=crewOf(crew), k=Math.max(.2,Math.min(2.5,strength==null?1:strength)); posOf(pos,_u); const x=_u.x,y=_u.y,z=_u.z;
  let dx=0,dy=0,dz=0; if(dir){ dx=dir.x;dy=dir.y;dz=dir.z; const l=Math.hypot(dx,dy,dz)||1; dx/=l;dy/=l;dz/=l; }
  e0(); col(c.C1); E.x=x;E.y=y;E.z=z; E.cell=15; E.life=.09+.03*k; E.s0=.9*k; E.s1=1.4*k; E.rot=R()*TAU; E.a=1.2; put(FX.add);
  e0(); col(WHITE); E.x=x;E.y=y;E.z=z; E.cell=2; E.life=.045; E.s0=.22*k; E.s1=.25*k; put(FX.add);
  e0(); col(c.C1); E.x=x;E.y=y;E.z=z; E.cell=0; E.life=.14+.04*k; E.s0=1.1*k; E.s1=.4*k; E.rot=R()*.6-.3; putU();
  e0(); col(c.C1); E.x=x;E.y=y;E.z=z; E.cell=1; E.life=.2; E.s0=.25*k; E.s1=1.5*k; E.a=.9; putU();
  e0(); col(c.C1); E.x=x;E.y=y;E.z=z; E.cell=2; E.life=.12; E.s0=1.2*k; E.s1=1.5*k; E.a=.35; put(FX.add);
  if(c.bolt){ for(let i=0;i<3;i++){ e0(); col(i?c.C1:c.C2); E.x=x+(R()-.5)*.3*k;E.y=y+(R()-.5)*.3*k;E.z=z+(R()-.5)*.3*k; E.cell=13; E.life=.14; E.s0=.55*k; E.s1=.45*k; E.rot=R()*TAU; put(FX.add); } }
  sparks(c,x,y,z,dx*1.5,dy*1.5+.3,dz*1.5,Math.round(6+8*k),7+4*k,3.5); motifBurst(c,x,y,z,Math.round(3+3*k),3+1.5*k);
  if(c.inkMotif>=0){ e0(); col(c.INK); E.x=x;E.y=y;E.z=z; E.cell=c.inkMotif===13?13:c.inkMotif; E.life=.18; E.s0=.9*k; E.s1=1.1*k; E.rot=R()*TAU; E.a=.9; put(FX.ink); } };
// slash(riderObj, arc, crew): swept crescent (KH combo hit / kick arc)
FX.slash=function(rider,arc,crew){ if(!FX.ready&&!init()) return; const c=crewOf(crew), P=arc||{}, r=rbGet(), d2r=Math.PI/180; r.on=true; r.kind=1; r.crew=c; r.shed=0;
  r.obj=objOf(rider); posOf(rider,r.C); r.c.copy(c.C1); r.r=P.radius||1.2; r.h=P.height==null?1:P.height; r.w=P.width||.45; r.tilt=(P.tilt||0)*d2r;
  r.a0=(P.start==null?-110:P.start)*d2r; r.a1=(P.end==null?110:P.end)*d2r; r.max=r.life=P.dur||.24;
  if(P.dir) r.F.set(P.dir.x,0,P.dir.z); else if(r.obj){ r.obj.getWorldDirection(r.F); r.F.y=0; } else r.F.set(0,0,-1); if(r.F.lengthSq()<1e-6) r.F.set(0,0,-1); r.F.normalize();
  if(c.C2){ const r2=rbGet(); if(r2!==r){ r2.on=true; r2.kind=1; r2.crew=null; r2.obj=r.obj; r2.C.copy(r.C); r2.c.copy(c.C2); r2.r=r.r*.82; r2.h=r.h; r2.w=r.w*.5; r2.tilt=r.tilt; r2.a0=r.a0; r2.a1=r.a1; r2.max=r2.life=r.max*.85; r2.F.copy(r.F); } } };
// lightning(from, to, crew)
FX.lightning=function(from,to,crew){ if(!FX.ready&&!init()) return; const c=crewOf(crew); for(let b=0;b<3;b++){ const r=rbGet(); r.on=true; r.kind=2; r.max=r.life=b?.2:.3; r.regen=0; r.seed=R()*100;
    r.fo=b?null:(objOf(from)?from:null); r.to=b?null:(objOf(to)?to:null); posOf(from,r.A); posOf(to,r.B); r.c.copy(b===1?c.C2:c.C1); r.wid=b?.035:.075; r.amp=b?.2:.1;
    if(b){ _u.subVectors(r.B,r.A); const f=.35+R()*.3; r.A.addScaledVector(_u,b===1?f*.4:f*.6); r.B.copy(r.A).addScaledVector(_u,.35).add(_w.set((R()-.5)*1.2,(R()-.5)*1.2,(R()-.5)*1.2).multiplyScalar(_u.length()*.25)); }
    boltPts(r); }
  posOf(to,_v); sparks(c,_v.x,_v.y,_v.z,0,.5,0,8,6,3); e0(); col(c.C2); E.x=_v.x;E.y=_v.y;E.z=_v.z; E.cell=15; E.life=.12; E.s0=.8; E.s1=1.2; E.rot=R()*TAU; put(FX.add);
  posOf(from,_v); e0(); col(c.C1); E.x=_v.x;E.y=_v.y;E.z=_v.z; E.cell=0; E.life=.12; E.s0=.7; E.s1=.3; put(FX.add); };
// stagger(target, phase): FF7 Pressured -> Staggered readability
const ST=[]; for(let i=0;i<8;i++) ST.push({obj:null,phase:""});
const AMBER=new THREE.Color(0xffa21a), GOLD=new THREE.Color(0xffe27a), WHITE=new THREE.Color(0xffffff);
function releaseOwner(id){ for(const p of [FX.add,FX.ink]) for(let i=0;i<p.N;i++) if(p.owner[i]===id&&p.life[i]>0){ p.owner[i]=0; if(p.max[i]<0){ p.max[i]=.15; p.life[i]=.15; } } }
FX.stagger=function(target,phase,crew){ const cc=crew!=null?crewOf(crew):null, AM=cc?cc.C1:AMBER, GD=cc?cc.C2:GOLD; if(!FX.ready&&!init()) return; phase=phase||"staggered"; const o=objOf(target)||target; let si=ST.findIndex(s=>s.obj===o);
  if(phase==="off"){ if(si>=0){ releaseOwner(si+1); ST[si].obj=null; ST[si].phase=""; } return; }
  if(si<0){ si=ST.findIndex(s=>!s.obj); if(si<0){ si=0; releaseOwner(1); } ST[si].obj=o; ST[si].phase=""; } const s=ST[si]; if(s.phase===phase) return; releaseOwner(si+1); s.phase=phase;
  posOf(o,_v); const x=_v.x, y=_v.y, z=_v.z, H=1.1;
  if(phase==="pressured"){ for(let i=0;i<3;i++){ e0(); col(AM); E.follow=o; E.oy=H+.95; E.orR=.55; E.orW=2.4; E.orA=i*TAU/3; E.cell=11; E.life=-1; E.s0=E.s1=.34; E.owner=si+1; E.rot=Math.PI; putU(1.3); }
    e0(); col(AM); E.follow=o; E.oy=.06; E.mode=1; E.cell=12; E.life=-1; E.s0=E.s1=1.5; E.rotv=1.2; E.a=.6; E.owner=si+1; putU(1.08);
    e0(); col(AM); E.x=x;E.y=y+H;E.z=z; E.cell=1; E.life=.22; E.s0=.4; E.s1=1.8; put(FX.add); return; }
  // staggered: white frame-1 flash, gold shatter ring (billboard + ground), shards, then gold diamonds orbit until "off"
  e0(); col(GD); E.x=x;E.y=y+H;E.z=z; E.cell=15; E.life=.14; E.s0=1.4; E.s1=2.6; E.rot=R()*TAU; E.a=1.3; put(FX.add);
  e0(); col(GD); E.x=x;E.y=y+H;E.z=z; E.cell=12; E.life=.35; E.s0=.6; E.s1=3.0; E.rotv=2; putU(1.06);
  e0(); col(GD); E.x=x;E.y=y+.05;E.z=z; E.mode=1; E.cell=1; E.life=.4; E.s0=.5; E.s1=3.4; put(FX.add);
  for(let i=0;i<10;i++){ e0(); col(GD); const a=i/10*TAU; E.x=x;E.y=y+H;E.z=z; E.vx=Math.cos(a)*6; E.vy=2+R()*3; E.vz=Math.sin(a)*6; E.cell=8; E.life=.4; E.s0=.3; E.s1=.15; E.rot=R()*TAU; E.rotv=12; E.drag=4; E.grav=6; put(FX.add); }
  for(let i=0;i<4;i++){ e0(); col(GD); E.follow=o; E.oy=H+.85; E.orR=.5; E.orW=4; E.orA=i*TAU/4; E.cell=i%2?0:8; E.life=-1; E.s0=E.s1=.3; E.rotv=6; E.owner=si+1; put(FX.add); }
  e0(); col(GD); E.follow=o; E.oy=.06; E.mode=1; E.cell=12; E.life=-1; E.s0=E.s1=1.7; E.rotv=-2; E.a=.8; E.owner=si+1; put(FX.add); };
// super(rider, crew): KH finisher / Limit break burst (~0.9 s)
FX.super=function(rider,crew){ if(!FX.ready&&!init()) return; const c=crewOf(crew), o=objOf(rider); posOf(rider,_v); const x=_v.x,y=_v.y,z=_v.z;
  e0(); col(c.C1); E.x=x;E.y=y+1.1;E.z=z; E.cell=15; E.life=.16; E.s0=2; E.s1=4.5; E.rot=R()*TAU; E.a=1.2; put(FX.add);
  e0(); col(c.C2); E.x=x;E.y=y+1.1;E.z=z; E.cell=2; E.life=.5; E.s0=2.4; E.s1=4; E.a=.35; put(FX.add);
  e0(); col(c.C1); E.x=x;E.y=y+.05;E.z=z; E.mode=1; E.cell=1; E.life=.6; E.s0=.8; E.s1=7; put(FX.add);
  e0(); col(c.C2); E.x=x;E.y=y+.06;E.z=z; E.mode=1; E.cell=12; E.life=.8; E.s0=.6; E.s1=5; E.rotv=1.5; put(FX.add);
  e0(); col(c.C2); E.x=x;E.y=y+2.4;E.z=z; E.mode=1; E.cell=6; E.life=.9; E.s0=.6; E.s1=1.6; E.rotv=3; put(FX.add);
  for(let i=0;i<6;i++){ e0(); col(i%2?c.C1:c.C2); E.x=x+(R()-.5)*.6;E.y=y;E.z=z+(R()-.5)*.6; E.vy=10+R()*6; E.mode=2; E.vdir=1; E.cell=2; E.str=9; E.s0=.45; E.s1=.2; E.life=.45; E.drag=3; put(FX.add); }
  for(let i=0;i<20;i++){ e0(); col(i%2?c.C1:c.C2); const a=i/20*TAU; E.x=x;E.y=y+1;E.z=z; E.vx=Math.cos(a)*14;E.vy=(R()-.3)*3;E.vz=Math.sin(a)*14; E.mode=2; E.vdir=1; E.cell=2; E.str=5; E.s0=.14; E.s1=.06; E.life=.35; E.drag=5; put(FX.add); }
  for(let i=0;i<18;i++){ e0(); col(i%2?c.C1:c.C2); E.follow=o||null; if(!o){ E.x=x+Math.cos(i)*1.2; E.y=y+.3; E.z=z+Math.sin(i)*1.2; } E.oy=.2+i*.04; E.vy=2.2; E.orR=1.2+R()*.4; E.orW=7; E.orA=i/18*TAU*2;
    E.cell=i%3===2?c.motif2:c.motif; E.life=.8+R()*.2; E.s0=.42; E.s1=.2; E.rot=R()*TAU; E.rotv=6; put(FX.add); }
  motifBurst(c,x,y+1,z,8,6);
  if(c.bolt){ for(let i=0;i<4;i++){ const a=i/4*TAU+R(); _w.set(x+Math.cos(a)*3.2,y,z+Math.sin(a)*3.2); _u.set(x,y+3.5,z); FX.lightning(_u,_w,c); } } };
// lockOn(target): KH/FF7 reticle; null clears
const LOCK={obj:null};
FX.lockOn=function(target,crew){ const cc=crew!=null?crewOf(crew):null; if(!FX.ready&&!init()) return; const o=target?(objOf(target)||target):null; if(o===LOCK.obj&&cc===LOCK.c) return; releaseOwner(100); LOCK.c=cc; LOCK.obj=o; if(!o) return;
  e0(); col(cc?cc.C1:WHITE); E.follow=o; E.oy=1.05; E.cell=10; E.life=-1; E.s0=E.s1=.95; E.rotv=1.4; E.a=.9; E.owner=100; putU(1.1);
  e0(); if(cc) col(cc.C2); else { E.r=1; E.g=.25; E.b=.35; } E.follow=o; E.oy=1.05; E.cell=10; E.life=-1; E.s0=E.s1=1.25; E.rotv=-.7; E.a=.7; E.owner=100; putU(1.08);
  e0(); col(cc?cc.C1:AMBER); E.x=0; E.follow=o; E.oy=1.05; E.cell=1; E.life=.18; E.s0=2.4; E.s1=1.1; put(FX.add); };

// ---------- Rigger FX attach points (jackets.js srFXAttach): rider root userData.fx = {handL,handR,footL,footR,wheelL,wheelR} (empty Object3Ds on bones) ----------
// Lookup is cached per rider object (WeakMap); a miss is retried at most every 1 s (points are attached after the GLB loads). No allocation on a hit.
const WHEELS=['wheelL','wheelR'], ATT=new WeakMap(), FXN={handL:1,handR:1,footL:1,footR:1,wheelL:1,wheelR:1};
function fxMap(rider){ let o=objOf(rider); if(!o) return null; let e=ATT.get(o); const now=FX.time+performance.now()/1000;
  if(e&&(e.fx||now-e.t<1)) return e.fx; let fx=null;
  if(o.userData&&o.userData.fx) fx=o.userData.fx;
  else if(typeof RIDERS!=='undefined'&&RIDERS.player&&typeof Ride!=='undefined'&&o===Ride.group&&RIDERS.player.userData&&RIDERS.player.userData.fx) fx=RIDERS.player.userData.fx;
  else { for(const c of o.children){ if(c.userData&&c.userData.fx){ fx=c.userData.fx; break; } } }
  if(!e){ e={fx:null,t:0}; ATT.set(o,e); } e.fx=fx; e.t=now; return fx; }
// name from data: fxName ("footL"...), or data.fx when it is a name string; "foot"/"hand"/"wheel" alone -> side from data.side ("Left"/"Right") or L
function fxNameOf(d){ let n=d.fxName||(typeof d.fx==='string'?d.fx:null); if(!n) return null; if(FXN[n]) return n; const sd=d.side==='Right'?'R':'L'; return FXN[n+sd]?n+sd:null; }
FX.attach=function(rider,name){ const m=fxMap(rider); return m&&name&&m[name]||null; };
const chargeK=d=>{ const c=+d.fxCharge; return c>0?1+Math.min(1.5,c)*.6:1; };
// trail(attachObj, crew, opt): ribbon that samples an attach point's world path (kick from the wheel, punch from the hand)
FX.trail=function(att,crew,width,dur){ if(!FX.ready&&!init()) return; if(!att) return; const c=crewOf(crew), r=rbGet(); r.on=true; r.kind=3; r.att=att; r.crew=c; r.shed=0; r.n=0;
  r.c.copy(c.C1); r.wid=width||.09; r.max=r.life=dur||.34; r.samp=r.max*.65; att.getWorldPosition(_v); for(let i=0;i<RB.SEG;i++){ r.pts[i*3]=_v.x; r.pts[i*3+1]=_v.y; r.pts[i*3+2]=_v.z; } };
function attackTrail(d,c){ const m=fxMap(d.rider), n=fxNameOf(d); if(!m||!n||!m[n]) return false; const sd=n.slice(-1), k=chargeK(d);
  if(n[0]==='f'||n[0]==='w'){ const wh=m['wheel'+sd], ft=m['foot'+sd]; if(wh) FX.trail(wh,c,.11*k,.36); if(ft&&ft!==wh) FX.trail(ft,c._alt||(c._alt={C1:c.C2,C2:c.C1,INK:c.INK,motif:c.motif,motif2:c.motif2,inkMotif:-1,inkN:0}),.05*k,.3); }
  else FX.trail(m[n],c,.08*k,.3);
  return true; }
function hitAt(d,out){ const m=fxMap(d.rider), n=fxNameOf(d); if(m&&n&&m[n]){ const sd=n.slice(-1), o=(n[0]==='f'&&m['wheel'+sd])?m['wheel'+sd]:m[n]; return o.getWorldPosition(out); } return null; }
// Rigger onHitFrame adapter: CombatFX.fromHitFrame(ev, evtName='lightHit', crew) -> emit with ev.rider/fxName/fxCharge (ev.pos used when no attach point)
const _HF={}; FX.fromHitFrame=function(ev,evt,crew){ if(!ev) return 0; for(const k in _HF) _HF[k]=undefined; _HF.rider=ev.rider; _HF.fxName=ev.fxName; _HF.side=ev.side; _HF.fxCharge=ev.fxCharge; _HF.pos=ev.pos||null; _HF.target=ev.target||null; _HF.crew=crew; _HF.haptics=false; return FX.emit(evt||'lightHit',_HF); };
// ---------- single event entry: CombatFX.emit(evt, data) — same names as SR_PAD.haptic (gamepad.js HE table) ----------
// data (all optional, reuse one object per caller): {crew, pos, dir, rider, target, from, to, arc, strength, scale, hand, haptics}
// scale/hand are forwarded untouched to SR_PAD.haptic(evt,data) (its opts shape) unless data.haptics===false. Returns the sim hit-stop in ms.
// HIT-STOP is SIM-ONLY (Systems scales its sim dt); never the XR camera/head pose, no camera shake. CombatFX.update(dt) takes REAL dt
// (auto-tick already uses real frame time), so sparks/flashes keep moving through the freeze — that is what sells the hit.
const HITSTOP=FX.HITSTOP={attackStart:0,lightHit:40,hit3:70,finisher:110,dive:110,stagger:150,pressured:0,playerHit:0,dodge:0,lockOn:0,roadSuper:0};
const RED=new THREE.Color(0xff3040), _e1=new THREE.Vector3(), _e2=new THREE.Vector3(), _ARC={start:-110,end:110,radius:1.3,height:1,tilt:0,width:.45,dur:.22,dir:null};
function tpos(d,out){ if(d.rider&&(d.fxName||typeof d.fx==='string')&&hitAt(d,out)) return out; if(d.pos) return posOf(d.pos,out); if(d.target){ posOf(d.target,out); out.y+=1.1; return out; } if(d.rider){ posOf(d.rider,out); out.y+=1; return out; } return out.set(0,0,0); }
FX.emit=function(evt,d){ d=d||{}; const kq=chargeK(d); try{ if(d.haptics!==false&&window.SR_PAD&&SR_PAD.haptic) SR_PAD.haptic(evt,d); }catch(e){}
  if(!FX.ready&&!init()) return HITSTOP[evt]||0; const c=crewOf(d.crew), k=d.strength;
  switch(evt){
  case "attackStart": if(d.rider&&attackTrail(d,c)) break; if(d.rider){ const a=d.arc||_ARC; if(!d.arc) _ARC.dir=d.dir||null; FX.slash(d.rider,a,c); } break;
  case "lightHit": FX.hit(tpos(d,_e1),d.dir,c,(k==null?.7:k)*kq); break;
  case "hit3": FX.hit(tpos(d,_e1),d.dir,c,(k==null?1.15:k)*kq); break;
  case "finisher": tpos(d,_e1); FX.hit(_e1,d.dir,c,(k==null?1.8:k)*kq); if(c.bolt&&d.rider){ posOf(d.rider,_e2); _e2.y+=1.2; FX.lightning(_e2,_e1,c); }
    e0(); col(c.C1); E.x=_e1.x;E.y=_e1.y;E.z=_e1.z; E.cell=12; E.life=.3; E.s0=.6; E.s1=2.6; E.rotv=3; put(FX.add); break;
  case "dive": tpos(d,_e1); FX.hit(_e1,d.dir,c,(k==null?1.5:k)*kq); e0(); col(c.C1); E.x=_e1.x; E.y=(d.target?posOf(d.target,_e2).y:_e1.y-1)+.06; E.z=_e1.z; E.mode=1; E.cell=1; E.life=.4; E.s0=.4; E.s1=4; put(FX.add);
    e0(); col(c.C2); E.x=_e1.x; E.y=E.y; E.z=_e1.z; E.mode=1; E.cell=12; E.life=.45; E.s0=.4; E.s1=3; E.rotv=2; put(FX.add); break;
  case "stagger": FX.stagger(d.target,"staggered",d.crew); break;
  case "pressured": FX.stagger(d.target,"pressured",d.crew); break;
  case "playerHit": { tpos(d.rider&&!d.pos?{rider:d.rider}:d,_e1); e0(); col(RED); E.x=_e1.x;E.y=_e1.y;E.z=_e1.z; E.cell=15; E.life=.14; E.s0=1; E.s1=1.6; E.rot=R()*TAU; put(FX.add);
    sparks(c,_e1.x,_e1.y,_e1.z,0,.4,0,8,5,2.5); e0(); col(RED); E.x=_e1.x;E.y=_e1.y;E.z=_e1.z; E.cell=1; E.life=.2; E.s0=1.2; E.s1=.3; put(FX.add); break; }
  case "dodge": { const o=d.rider; if(!o) break; posOf(o,_e1); e0(); col(c.C2); E.x=_e1.x;E.y=_e1.y+.05;E.z=_e1.z; E.mode=1; E.cell=1; E.life=.25; E.s0=.4; E.s1=2.2; E.a=.7; put(FX.add);
    for(let i=0;i<5;i++){ e0(); col(i%2?c.C1:c.C2); E.x=_e1.x;E.y=_e1.y+.3+i*.3;E.z=_e1.z; E.cell=2; E.life=.22; E.s0=.9; E.s1=.5; E.a=.45; put(FX.add); } break; }
  case "lockOn": FX.lockOn(d.target||null,d.crew); break;
  case "roadSuper": { FX.super(d.rider||d.target,c); const m=fxMap(d.rider); if(m) for(const n of WHEELS) if(m[n]){ m[n].getWorldPosition(_e1); FX.hit(_e1,null,c,1.2*kq); FX.trail(m[n],c,.12,.6); } break; } }
  return HITSTOP[evt]||0; };
// ---------- ?fxdemo=1: every effect x every crew, looping near the player ----------
const DEMO={freeze:0,on:/[?&]fxdemo=1\b/.test(Q), auto:true, t:0, i:0, dummy:null, label:null, list:["slash","hit","lightning","pressured","staggered","super","lock"]};
FX.demo=DEMO; const CK=Object.keys(CREWS); DEMO.crews=CK;
function demoAnchor(){ const g=(typeof Ride!=="undefined"&&Ride.group)?Ride.group:null; if(!g) return false; if(!DEMO.dummy){ DEMO.dummy=new THREE.Object3D(); DEMO.dummy.name="fxdemo_target"; scene.add(DEMO.dummy);
    const P2=[]; for(let i=0;i<=8;i++){ const a=-Math.PI/2+i/8*Math.PI; P2.push(new THREE.Vector2(Math.cos(a)*.28,(a<0?.28:1.42)+Math.sin(a)*.28)); if(i===4) P2.push(new THREE.Vector2(.28,1.42)); }
    const cap=new THREE.Mesh(new THREE.LatheGeometry(P2,16),new THREE.MeshToonMaterial({color:0x23252f})); cap.name="fxdemo_standin"; cap.position.y=.05; DEMO.dummy.add(cap); DEMO.standin=cap; }
  g.getWorldPosition(_v); camera.getWorldDirection(_F); _F.y=0; if(_F.lengthSq()<1e-6) _F.set(0,0,-1); _F.normalize(); DEMO.fwd=(DEMO.fwd||new THREE.Vector3()).copy(_F);
  camera.getWorldPosition(_w); DEMO.dummy.position.set(_w.x,_v.y,_w.z).addScaledVector(_F,3.5).addScaledVector(_S.crossVectors(_F,UP).normalize(),.9); DEMO.dummy.updateMatrixWorld(); DEMO.rider=g; return true; }
const DD={crew:null,pos:null,dir:null,rider:null,target:null,arc:null,strength:null,haptics:false};
const DARC={start:-120,end:120,radius:1.5,height:1.0,tilt:0,width:.5,dur:.24,dir:null};
DEMO.fire=function(crew,kind){ if(!demoAnchor()) return false; const c=crewOf(crew), T=DEMO.dummy; DD.crew=c; DD.rider=DEMO.rider; DD.target=T; DD.dir=DEMO.fwd; DD.pos=null; DD.strength=null; DD.arc=null;
  let evt=kind; if(kind==="slash"){ evt="attackStart"; DD.rider=T; DARC.tilt=kindTilt++%2?35:-20; DARC.dir=DEMO.fwd; DD.arc=DARC; } else if(kind==="hit") evt="hit3"; else if(kind==="staggered") evt="stagger"; else if(kind==="super"){ FX.stagger(T,"off"); evt="roadSuper"; DD.rider=T; }
  else if(kind==="lightning"){ _u.copy(DEMO.rider.position); _u.y+=1.2; _v.copy(_w.copy(T.position)); _v.y+=1.0; FX.lightning(_u,_v,c); evt=""; } else if(kind==="lock"){ evt="lockOn"; DD.target=T; }
  const hs=evt?FX.emit(evt,DD):0; DEMO.freeze=Math.max(DEMO.freeze,hs/1000);
  if(DEMO.label){ DEMO.label.textContent="FXDEMO  "+c.name+"  ·  "+(evt||kind)+(hs?"  ·  HIT-STOP "+hs+" ms (sim only)":""); DEMO.label.style.borderColor="#"+c.C1.getHexString(); }
  return true; };
DEMO.freeze=0; DEMO.simT=0;
let kindTilt=0;
function tickDemo(dt){ if(!DEMO.on) return; if(typeof State!=="undefined"&&State.mode!=="ride") return;
  let sdt=dt; if(DEMO.freeze>0){ DEMO.freeze-=dt; sdt=0; } DEMO.simT+=sdt; if(DEMO.dummy&&DEMO.fwd){ demoAnchor(); DEMO.dummy.position.y+=.25*Math.sin(DEMO.simT*5); DEMO.dummy.position.addScaledVector(_S.crossVectors(DEMO.fwd,UP).normalize(),.6*Math.sin(DEMO.simT*2.3)); DEMO.dummy.updateMatrixWorld(); }
  if(!DEMO.auto) return;
  if(!DEMO.label){ const d=document.createElement("div"); d.id="fxdemoLabel"; d.style.cssText="position:fixed;left:50%;bottom:70px;transform:translateX(-50%);font:700 18px system-ui;color:#fff;background:rgba(10,8,20,.6);padding:6px 14px;border:2px solid #fff;border-radius:8px;z-index:50;pointer-events:none;letter-spacing:.05em"; document.body.appendChild(d); DEMO.label=d; }
  DEMO.t-=dt; if(DEMO.t>0) return; DEMO.t=.75; const n=DEMO.list.length, crew=CK[Math.floor(DEMO.i/n)%CK.length], kind=DEMO.list[DEMO.i%n]; DEMO.i++;
  if(kind==="lock"){ FX.lockOn(DEMO.dummy); setTimeout(()=>FX.lockOn(null),600); } else DEMO.fire(crew,kind); if(DEMO.i%n===0) FX.stagger(DEMO.dummy,"off"); }
})();
