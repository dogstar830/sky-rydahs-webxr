// ===== Xbox / Standard Gamepad layer (Apex/CoD-style, adapted for skating). Keyboard stays as fallback. XR untouched.
const PAD={ prev:{}, dz:{ls:.18,rs:.2,trig:.3}, cam:{yaw:0,pitch:0,saved:null}, lt:0, crouch:0, slideScored:false, trickCd:0, ultCd:0, xHold:0, edge:false, last:null };
function padGet(){ try{ return (navigator.getGamepads?[...navigator.getGamepads()]:[]).find(Boolean)||null; }catch(e){ return null; } }
function padStick(x,y,dz){ const m=Math.hypot(x,y); if(m<dz) return [0,0,0]; const k=Math.min(1,(m-dz)/(1-dz))/m; return [x*k,y*k,Math.min(1,(m-dz)/(1-dz))]; }
function padNoPad(fn){ const own=Object.prototype.hasOwnProperty.call(navigator,"getGamepads"), real=navigator.getGamepads; try{ navigator.getGamepads=()=>[]; return fn(); } finally { if(own) navigator.getGamepads=real; else delete navigator.getGamepads; } }
function padFlash(t){ try{ flash(t); }catch(e){} }
function padNearSpot(r){ if(typeof TURF==="undefined"||!TURF.spots) return null; const p=Ride.group.position; for(const s of TURF.spots){ if(Math.hypot(p.x-s.x,p.z-s.z)<r) return s; } return null; }
function padRead(){ const gp=padGet(); const P=PAD.prev, C={};
  const b=i=>!!(gp&&gp.buttons[i]&&(gp.buttons[i].pressed||gp.buttons[i].value>PAD.dz.trig)), v=i=>gp&&gp.buttons[i]?(gp.buttons[i].value||(gp.buttons[i].pressed?1:0)):0;
  for(let i=0;i<17;i++){ C[i]=b(i); } const e=i=>C[i]&&!P[i]; const ax=gp?gp.axes||[]:[];
  const r={gp, b:i=>C[i], e, v, ls:padStick(ax[0]||0,ax[1]||0,PAD.dz.ls), rs:padStick(ax[2]||0,ax[3]||0,PAD.dz.rs)}; PAD.cur=C; return r; }
function padCommit(){ PAD.prev=Object.assign({},PAD.cur||{}); }
// Phone: D-pad Up raise/lower (edge), D-pad navigates, A select, B back; View opens Map app.
function phPadInput(R){ if(!R.gp||typeof State==="undefined"||State.mode==="menu") return;
  if(!PHONE.up){ if(State.mode!=="ride") return; if(R.e(12)) phoneSet(true); return; }
  if(R.e(12)){ if(PHONE.app==="home"&&PHONE.sel<3) phoneSet(false); else phoneNav("up"); }
  if(R.e(13)) phoneNav("down"); if(R.e(14)) phoneNav("left"); if(R.e(15)) phoneNav("right"); if(R.e(0)) phoneNav("select"); if(R.e(1)) phoneNav("back");
  if(R.e(8)){ phoneSet(false); if(window.mapSet) mapSet(true); } }
window.phPadInput=phPadInput;
// poll(): run the original without the pad (so its old pad mapping is ignored), then apply ours.
if(typeof poll==="function"){ const _po=poll; poll=function(){
  if(PAD.cam.saved){ camera.position.copy(PAD.cam.saved.p); camera.quaternion.copy(PAD.cam.saved.q); PAD.cam.saved=null; }
  const nw=performance.now(); PAD.dt=Math.min(.1,(nw-(PAD.tPrev||nw))/1000)||1/60; PAD.tPrev=nw;
  padNoPad(_po); const R=padRead(); PAD.R=R; PAD.edge=false;
  if(!R.gp||renderer.xr.isPresenting){ padCommit(); return; }
  const ride=State.mode==="ride", ui=typeof GATE!=="undefined"&&GATE.uiOpen;
  // menus / pause: D-pad or LS navigates, A select, B back, Menu start
  const nav={up:R.e(12),down:R.e(13),left:R.e(14),right:R.e(15),select:R.e(0),back:R.e(1),start:R.e(9)};
  if(!ride){ for(const n in nav) if(nav[n]) Input["p"+n[0].toUpperCase()+n.slice(1)]=true; padCommit(); return; }
  if(nav.start) Input.pStart=true;
  if(window.MAP&&MAP.open){ mapInput(R,1/60); Input.mag=0; Input.boost=false; Input.tag=false; PAD.edge=true; PAD.lt=0; PAD.crouch=0; padCommit(); return; }
  if(R.e(8)&&!PHONE.up){ mapSet(true); PAD.edge=true; Input.mag=0; padCommit(); return; }
  const was=PHONE.up; phPadInput(R); PAD.edge=was!==PHONE.up;
  // LS move/steer (deadzone, rescaled)
  const [lx,ly,lm]=R.ls; if(lm>0){ Input.mag=lm; Input.yaw=Math.atan2(lx,-ly); }
  // L3 boost (edge = dash)
  if(R.b(10)){ Input.boost=true; if(R.e(10)) Input.pDash=true; }
  PAD.lt=R.v(6)>PAD.dz.trig?R.v(6):0; PAD.crouch=(!PHONE.up&&R.b(1))?PAD.crouch+PAD.dt:0;
  if(!PHONE.up&&!PAD.edge&&!ui){
    // X = action: pick up (cans), doors/gates (tap re-opens the gate panel), hold-to-hack (0.5 s, via iLink Hack), turf tag spots (hold). No melee.
    PAD.xNear=null; if(R.b(2)){ const p=Ride.group.position, g=typeof phNearGate==="function"?phNearGate(8):null, s=padNearSpot(5);
      let can=null; try{ for(const c of cans) if(c.visible&&!c.userData.got&&Math.hypot(c.position.x-p.x,c.position.z-p.z)<3.5){ can=c; break; } }catch(e){}
      PAD.xNear=can?"pickup":g?"gate":s?"spot":null;
      if(can&&R.e(2)){ can.visible=false; can.userData.got=true; Stats.cans++; try{ bumpChain(); }catch(e){} PAD.last="pickup"; }
      else if(g){ if(R.e(2)&&g.gate&&g.gate.state==="closed"){ g.gate.dismissed=false; PAD.last="gate"; } PAD.xHold+=PAD.dt||1/60; if(PAD.xHold>.5){ PAD.xHold=0; phoneSet(true); PHONE.app="Hack"; phHackStart(); PAD.edge=true; PAD.last="hack"; } }
      else if(s) Input.tag=true; } else PAD.xHold=0;
    if(R.e(1)&&Ride.grinding){ Ride.grinding=false; PAD.last="cancelgrind"; }
    // D-pad LEFT = grapple to a marked point in range & in view (Oliver 2026-10-30: LB is the L special only); never in UI (menus/pause return above, gate keypad, map, phone)
    if(R.e(14)&&ride&&!ui&&!PAD.edge&&!(window.PHONE&&PHONE.up)&&!(window.MAP&&MAP.open)&&window.GRAP&&GRAP.target&&!GRAP.act){ grapStart(GRAP.target); PAD.last="grapple"; }
    if(R.e(13)){ PAD.ping=Ride.group.position.clone(); padFlash("PING"); try{ PHONE.badge.Map=1; PHONE.dirty=true; }catch(e){} }
    // Y = trick/ability, R3 = crew move, RT+Y = crew ultimate
    const rb=R.b(3), lb=R.b(7);
    if(rb&&lb&&(R.e(3)||R.e(7))&&PAD.ultCd<=0&&typeof DASH!=="undefined"&&DASH.meter>=.99){ DASH.meter=0; DASH.t=1.5; Ride.speed=Math.max(Ride.speed+14,Ride.maxSpeed*1.6); PAD.ultCd=1; trickScore(800,"CREW ULTIMATE",0); PAD.last="ult"; }
    else if(R.e(3)&&!lb&&PAD.trickCd<=0){ PAD.trickCd=.6; const A=typeof WALL!=="undefined"&&WALL.air; if(A){ A.flip=true; trickScore(200,"AIR SPIN",.06); } else trickScore(60,"SHOVE-IT",.03); PAD.last="trick"; }
    else if(R.e(11)&&typeof DASH!=="undefined"&&DASH.meter>=.33&&DASH.t<=0){ Input.pDash=true; Input.boost=true; PAD.last="crew"; padFlash("CREW MOVE"); } }
  padCommit(); }; }
// wallInput(): A jump/wall ride, X quick melee (when nothing to interact with), R3 kick = light, Y heavy, RT special; LS back/side for wall flips.
if(typeof wallInput==="function"){ const _wi=wallInput; wallInput=function(){ const I=padNoPad(_wi), R=PAD.R; if(!R||!R.gp||renderer.xr.isPresenting) return I;
  if(PHONE.up||PAD.edge||(window.MAP&&MAP.open)||(typeof GATE!=="undefined"&&GATE.uiOpen)) return I;
  if(R.e(0)) I.jumpP=true; if(R.b(0)) I.jump=true;
  // RB melee: tap = light/combo, hold >=0.35 s then release = charged heavy. RT = special (RT+Y = ultimate instead).
  if(R.e(7)&&!R.b(3)) I.a[2]=true;
  if(R.e(4)) I.a[2]=true;  // LB = L special (Oliver 2026-10-30; legacy wallInput LB mapping runs muted, so it must live here)
  if(R.b(5)){ if(R.e(5)||PAD.rtS==null){ PAD.rtS=performance.now(); PAD.rtN=0; } PAD.rtN++; PAD.rtT=(performance.now()-PAD.rtS)/1000; PAD.charging=PAD.rtT>=.35&&PAD.rtN>=3; }
  else if(PAD.rtT!=null){ if(PAD.rtT>=.35&&PAD.rtN>=3) I.a[1]=true; else I.a[0]=true; PAD.rtT=null; PAD.rtS=null; PAD.charging=false; }
  const [lx,ly]=R.ls; if(ly>.5) I.back=true; if(Math.abs(lx)>.5) I.side=Math.sign(lx); return I; }; }
// updateRide(): LT aim (slower, precise turning, auto-face nearest NPC within 12m), B slide/power slide/low grind.
if(typeof updateRide==="function"){ const _ur=updateRide; updateRide=function(dt){ const R=Ride, tr=R.turnRate, dr=R.drag;
  PAD.trickCd-=dt; PAD.ultCd-=dt;
  if(PAD.crouch>0){ R.drag=dr*.35; R.turnRate=tr*1.7; if(PAD.crouch>.4&&!PAD.slideScored&&R.speed>5){ PAD.slideScored=true; trickScore(R.grinding?200:100,R.grinding?"LOW GRIND":"POWER SLIDE",.04); } } else PAD.slideScored=false;
  try{ _ur(dt); } finally { R.turnRate=tr; R.drag=dr; } }; }
function padLockTarget(r){ const p=Ride.group.position; let best=null, bd=r*r; const L=[]; try{ if(typeof RIDERS!=="undefined"&&RIDERS.npcs) for(const n of RIDERS.npcs){ const o=n.holder||n.r; if(o&&o.position) L.push(o.position); } }catch(e){}
  for(const q of L){ const d=(q.x-p.x)**2+(q.z-p.z)**2; if(d<bd&&d>.01){ bd=d; best=q; } } return best; }
// RS camera orbit around the rider (applied just before render, restored next poll so the follow spring is unaffected).
const _padV=new THREE.Vector3(), _padT=new THREE.Vector3();
function padTick(dt,xr){ const R=PAD.R; if(xr||State.mode!=="ride"||(window.MAP&&MAP.open)) { PAD.cam.yaw=PAD.cam.pitch=0; return; }
  const [rx,ry,rm]=R&&R.gp?R.rs:[0,0,0]; if(rm>0&&PAD.lt<=0){ PAD.cam.yaw=THREE.MathUtils.clamp(PAD.cam.yaw-rx*dt*2.6,-Math.PI,Math.PI); PAD.cam.pitch=THREE.MathUtils.clamp(PAD.cam.pitch+ry*dt*1.6,-.35,.6); }
  else { const k=Math.exp(-dt*(PAD.lt>0?12:2.5)); PAD.cam.yaw*=k; PAD.cam.pitch*=k; }
  if(Math.abs(PAD.cam.yaw)<1e-3&&Math.abs(PAD.cam.pitch)<1e-3) return;
  PAD.cam.saved={p:camera.position.clone(),q:camera.quaternion.clone()};
  const t=_padT.copy(Ride.group.position); t.y+=1.4; _padV.copy(camera.position).sub(t); _padV.applyAxisAngle(THREE.Object3D.DefaultUp,PAD.cam.yaw); _padV.y+=PAD.cam.pitch*3;
  camera.position.copy(t).add(_padV); camera.lookAt(t); }
window.PAD=PAD; window.padTick=padTick;
// ---- camera-relative move (Rydah Systems 12:4x EDT): LS / WASD were WORLD-absolute (LS up = +z), so with the follow cam behind a rider
// spawned at yaw pi the rider went the opposite way of camera-forward (smoke CORE dot -0.9). Heading = cameraYaw - stickAngle, where cameraYaw is
// the RENDERED camera (follow cam + RS orbit PAD.cam.yaw), latched when the stick engages (and re-latched on RS input), so a held
// stick keeps a straight line instead of chasing the follow cam. Convention: heading yaw = atan2(dx,dz) (Ride moves +sin/+cos).
// ?worldstick=1 = old absolute behaviour.
if(typeof poll==="function"&&!/[?&]worldstick=1\b/.test(location.search)){ const _pc=poll; const CR={ref:null,raw:0,on:false}; PAD.camRel=CR;
  const _f=new THREE.Vector3();
  poll=function(){ const r=_pc.apply(this,arguments); if(window.__worldStick) return r;  // test escape: world-absolute steering (tests set window.__worldStick=true)
    try{ const ride=State.mode==="ride"&&!(window.MAP&&MAP.open)&&!(renderer.xr&&renderer.xr.isPresenting);
      if(!ride||!(Input.mag>0)){ CR.on=false; CR.ref=null; CR.pivot=false; CR.brake=false; return r; }
      const rs=PAD.R&&PAD.R.gp&&PAD.R.rs&&PAD.R.rs[2]>0;
      if(!CR.on||rs||CR.ref===null){ camera.getWorldDirection(_f); CR.ref=Math.atan2(_f.x,_f.z)+((PAD.cam&&PAD.cam.yaw)||0); }
      CR.on=true; CR.raw=Input.yaw; Input.yaw=Math.atan2(Math.sin(CR.ref-CR.raw),Math.cos(CR.ref-CR.raw));
      // brake (genre standard): stick/S pointing >135 deg away from the current travel direction while rolling on the ground = slow down, don't U-turn
      const off=Math.abs(Math.atan2(Math.sin(Input.yaw-Ride.yaw),Math.cos(Input.yaw-Ride.yaw)));
      const free=!(typeof WALL!=="undefined"&&(WALL.air||WALL.on))&&!(window.GRIND&&GRIND.on)&&!Ride.grinding;
      // hysteresis: once slowed below 1.5 m/s on a reverse, PIVOT (no re-brake) until the stick is released or the rider faces within 135 deg,
      // and swing the body round at 8 rad/s, so a full reverse = brake -> turn -> accelerate the new way (never pinned at the threshold)
      const dt=Math.min(.1,PAD.dt||1/60);
      if(off<=2.356||!free) CR.pivot=false;
      CR.brake=free&&!CR.pivot&&Ride.speed>1.5&&off>2.356;
      if(CR.brake){ Ride.speed=Math.max(0,Ride.speed-16*Input.mag*dt); Input.mag=0; Input.boost=false; CR.nBrake=(CR.nBrake||0)+1; if(Ride.speed<=1.5) CR.pivot=true; }
      else if(free&&off>2.356&&Ride.speed<=1.5) CR.pivot=true;
      if(CR.pivot&&free){ const d=Math.atan2(Math.sin(Input.yaw-Ride.yaw),Math.cos(Input.yaw-Ride.yaw)), st=8*dt; Ride.yaw+=Math.abs(d)<=st?d:Math.sign(d)*st; }
    }catch(e){ if(!window.__crErr) console.warn("camrel",e); window.__crErr=e; }
    return r; }; }
