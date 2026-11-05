// ===== POLE GRIND: spiral climb + double-helix light ribbon (Rydah Systems, Oliver ref3-pole-grind 2026-10-30; Optimizer spec perf/anika-fx-budget.md §4b) =====
// Runs after grind.js (patch_polegrind.py). Gameplay: on a vertical pole spline (grindPole -> s.vert, kind pole|lamp; palm trunks excluded) the rider orbits the
// pole axis while grind.js moves them up the arc (spiral climb). Root placement + spin around poleAxis are here; yaw only (no roll/pitch, no camera roll in VR).
// Rigger hook: RIDERS.player.userData.setState('polegrind',{variant:'climb'|'top',poleAxis,side}) on entry / at the top, setState(null) on exit.
// Timing = Rigger's state: entry .30 s fade-in, 1.6 s hold loop, .25 s exit fade-out. Top: 'top' pose for PG.TOP_HOLD s, then pop onto the nearest
// cable/crossarm within PG.POP_R (chains into the cable grind) or launch. FX: 1 static double-helix mesh (1.5 turns, additive, vertex-shader scroll,
// 1 draw, only visible while k>0) + wheel sparks from grind.js's spark pool (0 draws). Debug/test state: window.PG.
const PG={ on:false, s:null, ang:0, dirA:1, k:0, ph:"off", t:0, holdT:0, ENTER:.30, HOLD:1.6, EXIT:.25, TOP_HOLD:.35, POP_R:5, OMEGA_MAX:7, CLIMB:6, BAND:3.2, R:.85,
  topT:-1, tl:[], stateLog:[], stats:{entries:0,tops:0,cablePops:0,launches:0,exits:0}, mesh:null };
window.PG=PG;
function pgState(name,o){ PG.stateLog.push([+clock.toFixed(2),name,o&&o.variant||null]); if(PG.stateLog.length>40) PG.stateLog.shift();
  try{ const u=typeof RIDERS!=="undefined"&&RIDERS.player&&RIDERS.player.userData; if(u&&typeof u.setState==="function") u.setState(name,o); }catch(e){ PG.stateErr=String(e); } }
function pgIsPole(s){ return !!(s&&s.vert&&(s.kind==="pole"||s.kind==="lamp")); }
function pgTl(ev){ PG.tl.push([ev,+clock.toFixed(3),+PG.k.toFixed(3)]); if(PG.tl.length>40) PG.tl.shift(); }
// ---- helix mesh (static geometry, all motion in the vertex shader). Bold pass (Oliver ref3, 04:27): strands ~2.7x wider, white-orange core -> violet ->
// electric-blue fringe across each strand, HDR-ish brightness (blooms at night), radius wraps the rider's orbit, full height pole base -> above the rider,
// small loop flourishes. Debris = 1 Points draw (GPU-animated rock chips orbiting/rising). Delta while pole grinding = 2, idle = 0. XR: intensity x0.55.
function pgBuild(){ const segs=200, P=[], I=[]; for(let s=0;s<2;s++) for(let i=0;i<=segs;i++){ const u=i/segs; P.push(u,0,s,u,1,s); }
  for(let s=0;s<2;s++) for(let i=0;i<segs;i++){ const a=(s*(segs+1)+i)*2; I.push(a,a+1,a+2,a+1,a+3,a+2); }
  const g=new THREE.BufferGeometry(); g.setAttribute("position",new THREE.Float32BufferAttribute(P,3)); g.setIndex(I);
  const m=new THREE.ShaderMaterial({ transparent:true, depthWrite:false, blending:THREE.AdditiveBlending, side:THREE.DoubleSide, fog:false,
    uniforms:{ uT:{value:0}, uSpin:{value:0}, uR:{value:PG.R}, uH:{value:6}, uTurns:{value:3}, uW:{value:.3}, uK:{value:0}, uHead:{value:.5}, uGain:{value:1.5} },
    vertexShader:`uniform float uT,uSpin,uR,uH,uTurns,uW,uHead; varying vec2 vUv; varying float vS; varying float vF;
      void main(){ float u=position.x, v=position.y, s=position.z; vUv=vec2(u,v); vS=s;
        float a=6.2832*(u*uTurns+s*.5)+uSpin;
        float r=uR*(.9+.1*sin(u*uTurns*3.+uT*3.9))+.12*sin(u*uTurns*12.566+s*3.14)*smoothstep(.2,.9,sin(u*uTurns*2.+uT));   // breathing + small loop flourishes
        vec3 n=vec3(cos(a),0.,sin(a)); float lift=.1*sin(u*uTurns*12.566+s*3.14);
        vec3 p=vec3(n.x*r,u*uH+lift,n.z*r)+vec3(0.,(v-.5)*uW,0.)+n*(v-.5)*uW*.35;
        vec3 ax=(modelMatrix*vec4(0.,p.y,0.,1.)).xyz, tc=cameraPosition-ax; tc.y=0.; float fr=dot(n,normalize(tc+1e-4));   // >0: strand is between camera and pole
        float nearRider=1.-smoothstep(.9,2.,abs(u*uH-(uHead*uH-1.0)));            // rider's body band
        vF=(1.-.8*smoothstep(.1,.6,fr)*nearRider)*mix(1.,.4,smoothstep(0.,.6,-fr));   // far side dimmed: caps overlap glow
        gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.); }`,
    fragmentShader:`uniform float uT,uK,uHead,uGain; varying vec2 vUv; varying float vS; varying float vF;
      void main(){ float x=abs(vUv.y*2.-1.);                                   // 0 = strand centre, 1 = edge
        float ends=smoothstep(0.,.04,vUv.x)*smoothstep(uHead+.12,uHead-.02,vUv.x); // base -> just above the rider
        float streak=.7+.3*sin(vUv.x*90.-uT*6.2832/1.6*4.);                     // light runs up the strand, loops once per 1.6 s
        vec3 white=vec3(1.,.93,.8), orange=vec3(1.,.42,.06), violet=vec3(.62,.18,1.), blue=mix(vec3(.2,.55,1.),vec3(.35,.4,1.),vS);
        vec3 c=x<.12?mix(white,orange,x/.12):x<.55?orange:x<.78?mix(orange,violet,(x-.55)/.23):mix(violet,blue,(x-.78)/.22);
        float a=uK*ends*streak*(1.-smoothstep(.8,1.,x))*(x<.12?1.15:1.)*vF;
        gl_FragColor=vec4(c*a*uGain,1.); }` });
  const mesh=new THREE.Mesh(g,m); mesh.frustumCulled=false; mesh.renderOrder=9001; mesh.visible=false; mesh.userData.noMerge=true; mesh.name="pg_helix"; scene.add(mesh); PG.mesh=mesh;
  // debris: 64 rock chips, all motion in the vertex shader (orbit + slow rise + tumble flicker), normal blending, dark rock with a warm rim from the helix
  const N=110, D=new Float32Array(N*3); for(let i=0;i<N;i++){ D[i*3]=Math.random(); D[i*3+1]=Math.random(); D[i*3+2]=Math.random(); }
  const dg=new THREE.BufferGeometry(); dg.setAttribute("position",new THREE.BufferAttribute(D,3));
  const dm=new THREE.ShaderMaterial({ transparent:true, depthWrite:false, fog:false, uniforms:{ uT:{value:0}, uH:{value:6}, uK:{value:0}, uPx:{value:innerHeight} },
    vertexShader:`uniform float uT,uH,uPx; varying float vA; varying float vR;
      void main(){ float a=position.x*6.2832+uT*(.15+position.z*.25), rr=1.4+position.y*3.2, y=fract(position.z+uT*.04)*(uH+2.)-.5;
        vec4 mv=modelViewMatrix*vec4(cos(a)*rr,y,sin(a)*rr,1.); gl_Position=projectionMatrix*mv; vA=smoothstep(0.,.15,fract(position.z+uT*.04))*smoothstep(1.,.8,fract(position.z+uT*.04)); vR=position.y;
        gl_PointSize=clamp((15.+position.z*25.)*uPx/900./max(1.,-mv.z)*4.,3.,56.); }`,
    fragmentShader:`uniform float uK; varying float vA; varying float vR; void main(){ vec2 q=gl_PointCoord*2.-1.;
        float ang=atan(q.y,q.x), e=.62+.18*sin(ang*3.+vR*20.)+.12*sin(ang*5.+vR*37.); float d=length(q)/e; if(d>1.) discard;   // irregular chunk silhouette
        float face=floor((ang+3.1416)/1.2566+vR*5.); float lit=.55+.45*fract(sin(face*12.9+vR*78.)*437.5)*(.6-.4*q.y);               // faceted, top-lit
        vec3 rock=mix(vec3(.2,.16,.13),vec3(.42,.34,.27),vR)*lit, rim=vec3(1.,.55,.25)*smoothstep(.75,1.,d)*.7; gl_FragColor=vec4(rock+rim,uK*vA); }` });
  const deb=new THREE.Points(dg,dm); deb.frustumCulled=false; deb.renderOrder=9000; deb.visible=false; deb.userData.noMerge=true; deb.name="pg_debris"; scene.add(deb); PG.deb=deb; }
// ---- gameplay ----
function pgEnter(O){ const s=O.s; PG.on=true; PG.s=s; PG.ang=Math.atan2(O.off.z,O.off.x); PG.dirA=Math.random()<.5?1:-1; PG.ph="enter"; PG.t=0; PG.topT=-1; PG.stats.entries++; pgTl("enter");
  PG.axis=new THREE.Vector3(0,1,0); PG.base=s.pts[0].clone(); pgState("polegrind",{variant:"climb",poleAxis:PG.axis,side:PG.dirA>0?"Left":"Right"}); }
function pgLeave(why){ if(!PG.on) return; PG.on=false; PG.s=null; PG.ph="exit"; PG.t=0; PG.stats.exits++; PG.lastExit=why; pgTl("exit:"+why); pgState(null); }
function pgPlace(O,dt){ const R=Ride, p=R.group.position, s=O.s, r=Math.hypot(O.off.x,O.off.z)||(s.r+.12);
  const w=Math.min(PG.OMEGA_MAX,(Math.abs(O.v)*.9)/Math.max(.3,r)); PG.ang+=PG.dirA*w*dt;           // tangential ~0.9 x grind speed -> ~45 deg helix
  O.off.set(Math.cos(PG.ang)*r,0,Math.sin(PG.ang)*r); grindAt(s,O.arc,_grv,_grt); p.set(_grv.x+O.off.x,_grv.y,_grv.z+O.off.z); R.y=p.y;
  const tx=-Math.sin(PG.ang)*PG.dirA, tz=Math.cos(PG.ang)*PG.dirA; R.yaw=Math.atan2(tx,tz); R.group.rotation.y=R.yaw;      // face along the orbit; yaw only
  if(frame%2===0&&GRIND.spk){ const cx=Math.cos(R.yaw), cz=-Math.sin(R.yaw), C=[0xffb050,0xfff0d0,0x9a5cff,0x4f9bff];
    for(const sd of [-1,1]) grindSpark(p.x+cx*.11*sd,p.y+.03,p.z+cz*.11*sd,C[(Math.random()*4)|0],-tx*2+O.off.x*3+(Math.random()-.5),Math.random()*1.5,-tz*2+O.off.z*3+(Math.random()-.5),.3,8); } }
function pgTop(dt){ const G=GRIND, O=G.on, R=Ride, p=R.group.position; if(PG.topT<0){ PG.topT=0; PG.ph="top"; PG.stats.tops++; pgTl("top"); O.arc=O.s.L-.02; grindAt(O.s,O.arc,_grv); p.set(_grv.x+O.off.x,_grv.y,_grv.z+O.off.z); R.y=p.y;
    pgState("polegrind",{variant:"top",poleAxis:PG.axis,side:PG.dirA>0?"Left":"Right"}); }
  PG.topT+=dt; R.speed=O.v=Math.max(O.v,6); if(PG.topT<PG.TOP_HOLD) return true;
  // pop: nearest cable / crossarm (not vertical) within POP_R of the pole top -> chain into its grind; else launch off the top
  const top=new THREE.Vector3(p.x,p.y,p.z); let best=null; for(const n of grindAll(top,PG.POP_R)){ if(n.s.vert||n.s===O.s) continue; if(Math.abs(n.q.y-top.y)>2.5) continue; if(!best||n.d<best.d) best=n; }
  const v=Math.max(7,O.v); PG.popTo=best?{id:best.s.id,mat:best.s.mat,d:+best.d.toFixed(2)}:null;
  if(best){ G.on=null; R.grinding=false; pgLeave("pop"); PG.stats.cablePops++; const fx=Math.sin(R.yaw), fz=Math.cos(R.yaw), dir=(best.tan.x*fx+best.tan.z*fz)>=0?1:-1;
    p.set(best.q.x,best.q.y+best.s.r+.02,best.q.z); R.y=p.y; grindLock(best.s,best.arc,dir,v,1); trickScore&&trickScore(300,"POLE POP",.1); }
  else { pgLeave("launch"); PG.stats.launches++; grindExit("jump"); if(WALL.air){ WALL.air.vy=Math.max(WALL.air.vy,6); } }
  return true; }
if(typeof grindStep==="function"){ const _pgStep=grindStep; grindStep=function(dt){ const G=GRIND;
    if(G.on&&pgIsPole(G.on.s)){ const O=G.on; if(!PG.on||PG.s!==O.s) pgEnter(O);
      if(PG.topT>=0||(O.dir>0&&O.arc+O.v*dt>=O.s.L-.05)){ G.I=grindInput(); if(G.I.jump||G.I.drop){ pgLeave(G.I.jump?"jump":"drop"); return _pgStep(dt); } try{ return pgTop(dt); }catch(e){ PG.err=String(e); } } }
    if(G.on&&pgIsPole(G.on.s)&&G.on.dir>0&&PG.topT<0) G.on.v+=PG.CLIMB*dt;   // A-T wheel drive up the pole: offsets most of gravity+bark drag (net ~-5 m/s^2) so a dash entry reaches a 10 m top
    const r=_pgStep(dt);
    if(G.on&&pgIsPole(G.on.s)&&PG.on&&PG.topT<0) pgPlace(G.on,dt); else if(PG.on&&(!G.on||G.on.s!==PG.s)) pgLeave(G.on?"switch":"exit");
    return r; }; }
// ---- FX timing (entry .30 / hold loop 1.6 / exit .25), runs every frame before render ----
function pgFX(dt,xr){ if(!PG.mesh) pgBuild(); const M=PG.mesh, U=M.material.uniforms; PG.t+=dt;
  if(PG.on){ if(PG.ph==="enter"){ PG.k=Math.min(1,PG.t/PG.ENTER); if(PG.k>=1){ PG.ph=PG.topT>=0?"top":"hold"; PG.holdT=0; pgTl("hold"); } } else { PG.k=1; PG.holdT+=dt; } }
  else if(PG.ph==="exit"){ PG.k=Math.max(0,PG.k-dt/PG.EXIT); if(PG.k<=0){ PG.ph="off"; pgTl("hidden"); } }
  M.visible=PG.deb.visible=PG.k>0; if(!M.visible) return; const p=Ride.group.position, b=PG.base||p;
  if(PG.on){ M.position.set(b.x,b.y,b.z); PG.deb.position.set(b.x,b.y,b.z); } M.rotation.set(0,0,0);   // pole axis is world-vertical: no roll/pitch
  const H=Math.max(2.5,p.y-M.position.y+1.8); PG.H=H;                 // full height: pole base -> 1.8 m above the rider's feet
  U.uH.value=H; U.uTurns.value=H*.42; U.uHead.value=(p.y-M.position.y+1.6)/H; U.uR.value=PG.R;
  U.uK.value=PG.k*(xr?.55:1); U.uGain.value=xr?1.0:1.5; U.uT.value=(PG.holdT%PG.HOLD); U.uSpin.value=-PG.ang*.5+clock*1.2*PG.dirA;
  const DU=PG.deb.material.uniforms; DU.uT.value=clock; DU.uH.value=H; DU.uK.value=PG.k*(xr?.7:1); DU.uPx.value=innerHeight; }
// ---- runtime vortex gate (same rule as patches_proposed/grind_vortex_gate.diff; inert once that diff lands, which defines GRIND.VORTEX_XR_CAP) ----
function pgVortexGate(xr){ const G=GRIND; if(!G.vortex||G.VORTEX_XR_CAP!==undefined) return; const cap=!G.on?0:xr?(PG.k>.02?0:.3):1;
  if(G.vk>cap){ G.vk=cap; G.vortex.material.uniforms.uK.value=cap; } G.vortex.visible=G.vk>.02; }
if(typeof grindTick==="function"){ const _pgTick=grindTick; grindTick=function(dt,xr){ _pgTick(dt,xr); try{ pgFX(dt,xr); pgVortexGate(xr); if(window.trailsTick) trailsTick(dt,xr); }catch(e){ if(!PG.fxErr) console.warn("polegrind fx",e); PG.fxErr=String(e); } }; }
