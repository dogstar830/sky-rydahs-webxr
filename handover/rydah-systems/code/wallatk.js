// ===== WALL RIDES + CREW ATTACKS (Air Gear turf battles) =====
// Wall ride: hit a wall face (collision boxes, same candidate-face filter as the turf spots) at speed and a shallow angle -> stick and
// ride along it with gravity drift. Hold JUMP = wall run (low drift), tap JUMP = kick-off, JUMP + back/side = wall flip, land on another
// wall while airborne = wall-to-wall chain. Attacks: 3 moves per crew rider. All FX go through ONE pooled dynamic mesh (+1 draw call,
// only while something is on screen) plus the existing particle pool. VR: rig only ever follows yaw + height, never roll/pitch.
// WALL-KICK CHAIN (Oliver 09:12 "Wall-kick chain up buildings to reach cables"): A/Space within KICK.win s of touching a kickable
// wall face (WALL_PANELS / wallPanel flag or any building facade collider, see wallFace) = up burst + outward push along the normal.
// up[n] * upScale with chain gravity KICK.g (instead of 13): 4.5/4/3.5/3/2.5 x2 -> ~4.5+3.6+2.7 m apex gain, street -> 9.5 m cables in 3-4 kicks.
// Max 5 kicks; chain resets only on landing or grind lock. After the limit / missed window A does nothing on the wall (no infinite climb).
// Feedback: pooled particles (emit) + dust ring from the existing ATK.fx pool (no new draw calls), desktop camera nudge (none in XR, never roll), trick popup.
const KICK={ win:.35, up:[4.5,4,3.5,3,2.5], upScale:2.0, g:9, out:4.2, along:.35, back:14, max:5, n:0, ct:-9, face:null, nudge:0, peakY:0, kicks:0, ignored:0 };
KICK.reach=.8; window.KICK=KICK;
const WALL={ on:null, air:null, chain:0, score:0, minSpeed:8.5, maxInto:.62, hold:false, flipT:-1, trail:[], lastWall:null };
const ATK_KEYS={ light:"J / LMB / Y / right B", heavy:"K / RMB / RT / left X", special:"L / LT / left Y" };
// move kinds: dash (lunge, hits along path), sweep (360 spin), cone (front arc), chain (arcs jump target to target), slam (charge + shockwave), dive (aerial dive kick + ring)
const MOVESETS={
  codee:{ who:"Caali (Code : E)", c1:0xffd700, c2:0x0a0a0a, moves:[
    {name:"Lightning Dash Strike",kind:"dash",r:1.8,knock:9,stun:.8,cd:1.2,fx:"bolt"},
    {name:"Chain Shock",kind:"chain",r:9,knock:4,stun:1.4,cd:3.5,fx:"bolt"},
    {name:"Thunder Drop",kind:"dive",r:3.4,knock:10,stun:1.2,cd:4,fx:"boltring"} ]},
  karasu:{ who:"Ikki (Kogarasumaru)", c1:0x00e5ff, c2:0x0b1a26, moves:[
    {name:"Wing-Sweep Kick",kind:"sweep",r:2.8,knock:8,stun:.8,cd:1.1,fx:"wing"},
    {name:"Crow Rush",kind:"cone",r:3.6,knock:10,stun:1,cd:2.6,fx:"wing2"},
    {name:"Raven Dive Kick",kind:"dive",r:3.4,knock:12,stun:1.3,cd:4,fx:"feather"} ]},
  static:{ who:"Static Angels", c1:0xaa00ff, c2:0x7fe9ff, moves:[
    {name:"Halo Slash",kind:"cone",r:3.4,knock:7,stun:.8,cd:1.2,fx:"halo"},
    {name:"Angel Wing Burst",kind:"sweep",r:3.2,knock:9,stun:1,cd:3,fx:"wing"},
    {name:"Static Fall",kind:"dive",r:3.6,knock:10,stun:1.4,cd:4,fx:"ring"} ]},
  behemoth:{ who:"Behemoth", c1:0xff6a00, c2:0x2a1608, moves:[
    {name:"Shoulder Slam",kind:"slam",r:2.6,knock:16,stun:1.2,cd:1.8,fx:"shock"},
    {name:"Horn Rush",kind:"dash",r:2,knock:14,stun:1,cd:3,fx:"horn"},
    {name:"Ground Pound",kind:"dive",r:4.2,knock:15,stun:1.5,cd:4.5,fx:"shock"} ]},
  anubis:{ who:"Anubis", c1:0x00bfa5, c2:0xffd28a, moves:[
    {name:"Jackal Fang",kind:"cone",r:3.2,knock:8,stun:.9,cd:1.2,fx:"fang"},
    {name:"Scales of Judgement",kind:"chain",r:8,knock:5,stun:1.6,cd:3.5,fx:"sand"},
    {name:"Ankh Dive",kind:"dive",r:3.4,knock:10,stun:1.2,cd:4,fx:"ring"} ]},
  forest:{ who:"Sleeping Forest", c1:0x7cb342, c2:0xd8ffd0, moves:[
    {name:"Root Sweep",kind:"sweep",r:3,knock:6,stun:1.1,cd:1.3,fx:"leaf"},
    {name:"Lullaby Leaves",kind:"chain",r:8,knock:3,stun:2.4,cd:4,fx:"leaf"},
    {name:"Canopy Drop",kind:"dive",r:3.6,knock:9,stun:1.4,cd:4,fx:"leafring"} ]},
  genesis:{ who:"Genesis", c1:0xff2bd6, c2:0xffd36a, moves:[
    {name:"Halo Kick",kind:"cone",r:3.2,knock:8,stun:.8,cd:1.2,fx:"halo"},
    {name:"Rebirth Spiral",kind:"sweep",r:3,knock:9,stun:1,cd:2.8,fx:"spiral"},
    {name:"Genesis Flare",kind:"slam",r:4,knock:12,stun:1.3,cd:4,fx:"shock"} ]},
  ttt:{ who:"Tool Toul To", c1:0xc0582b, c2:0xffb040, moves:[
    {name:"Wrench Spin",kind:"sweep",r:2.8,knock:8,stun:.9,cd:1.2,fx:"cross"},
    {name:"Rivet Burst",kind:"cone",r:4,knock:7,stun:1,cd:2.5,fx:"rivet"},
    {name:"Tool Drop",kind:"dive",r:3.4,knock:11,stun:1.2,cd:4,fx:"cross"} ]} };
// ===== COMBAT C1/C2 (Systems 10:50, Oliver via Ani): KH 3-hit chain on J/RB (light), hits 1-2 cancel on A/B, hit 3 = road finisher; sim-only hit-stop from CombatFX.emit ms * HITSTOP_SCALE
const CHAIN={ win:.6, minT:.16, n:0, last:-9, log:[], cancels:0, resets:0 };
const HITSTOP={ parse:q=>q==="full"?1:q==="off"?0:.5, att:0, log:[] }; HITSTOP.scale=HITSTOP.parse(new URLSearchParams(location.search).get("hitstop"));   // HITSTOP_SCALE .5 until Oliver tests on Quest
const CEV={ crew:null, pos:new THREE.Vector3(), dir:new THREE.Vector3(), rider:null, target:null, strength:1, hand:"right", fxName:null, side:null, fxCharge:undefined };
// CombatFX v3 attach points (Forge): kicks -> foot of the lead side, punches -> hand; KICK_KINDS by move kind
const FXKICK={dash:1,sweep:1,dive:1,slam:1}; function fxNameOf(A){ if(!A||!A.m) return null; const sd=A.side||(A.ch?((A.ch-1)%2?"L":"R"):"R"); return (FXKICK[A.m.kind]?"foot":"hand")+sd; }                     // ONE reused emit data object
function cfxEmit(evt,tgt,pos,dx,dz,str,A){ if(!window.CombatFX||!CombatFX.emit) return 0; const S=ATK.set; CEV.crew=S; CEV.rider=(typeof RIDERS!=="undefined"&&RIDERS.player)||Ride.group; A=A||ATK.act;
  CEV.fxName=fxNameOf(A); CEV.side=CEV.fxName?(CEV.fxName.slice(-1)==="L"?"Left":"Right"):null; CEV.fxCharge=A&&A.heavy?Math.min(1.5,A.charge||0):undefined; CEV.target=tgt||null; CEV.strength=str||1;
  if(pos) CEV.pos.copy(pos); else CEV.pos.copy(Ride.group.position).setY(1.1); CEV.dir.set(dx||Math.sin(Ride.yaw),0,dz||Math.cos(Ride.yaw)).normalize();
  let ms=0; try{ ms=+CombatFX.emit(evt,CEV)||0; }catch(e){ ATK.cfxErr=String(e); } (ATK.evLog=ATK.evLog||[]).push([evt,+clock.toFixed(2),ms]); if(ATK.evLog.length>60) ATK.evLog.shift(); return ms; }
// ===== COMBAT POSER BRIDGE (Systems 13:20; Rigger ikki_skate.js combat API, combat-anim-plan §8). OFF unless window.SR_COMBAT_POSES / ?combatposes=1 -> identical behaviour when off.
const CP={ unsub:[], u:null, log:[], rmMax:6, rmMaxXR:3, vMax:14, heldJ:0, floatMin:.25 };
CP.flag=()=>!!(window.SR_COMBAT_POSES||/[?&]combatposes=1(&|$)/.test(location.search));
CP.uOf=o=>{ for(const x of [o,o&&o.r,o&&o.root,o&&o.holder,o&&o.holder&&o.holder.children&&o.holder.children[0]]) if(x&&x.userData&&typeof x.userData.combatQuery==="function") return x.userData; return null; };
CP.player=()=>CP.flag()&&typeof RIDERS!=="undefined"?CP.uOf(RIDERS.player):null;
CP.bind=()=>{ const u=CP.player(); if(u===CP.u) return u; CP.teardown(); CP.u=u; if(!u||!u.onCombat) return u;
  CP.unsub.push(u.onCombat("onHitFrame",ev=>{ const A=ATK.act; CP.log.push(["hit",ev.move,ev.frame,+clock.toFixed(2)]); if(A&&A.pose&&!A.hitOpen){ A.hitOpen=true; A.hoT=A.t; A.hitSrc="onHitFrame"; A.hitPos=ev.pos||null; A.hfEv=ev; A.charge=Math.max(A.charge||0,Math.min(1,ev.charge||0)); } }));
  CP.unsub.push(u.onCombat("onCancelOpen",ev=>{ CP.log.push(["cancelOpen",ev.move,ev.frame,+clock.toFixed(2)]); }));
  CP.unsub.push(u.onCombat("onRecover",ev=>{ CP.log.push(["recover",ev.move,ev.frame,+clock.toFixed(2)]); })); return u; };
CP.teardown=()=>{ for(const f of CP.unsub) try{ f(); }catch(e){} CP.unsub.length=0; CP.u=null; };
CP.state=(u,n,o)=>{ CP.log.push(["setState",n,o&&(o.step!==undefined?o.step:o.move||o.kind),+clock.toFixed(2)]); try{ return u.setState(n,o); }catch(e){ ATK.cpErr=String(e); return false; } };
// start a posed chain/heavy hit: hits only open on onHitFrame (fallback: the old window D, then +0.1 s)
CP.atk=(A,o)=>{ const u=CP.bind(); if(!u) return; const C=ATK.commit, tg=C&&C.ref&&C.ref.holder?C.ref.holder:null; o.target=tg; if(o.side===undefined&&o.step!==undefined) o.side=o.step%2?"Left":"Right";
  if(o.side) A.side=o.side[0]; if(CP.state(u,"atk",o)!==false){ A.pose=true; A.hitOpen=false; A.D=({sweep:.42,cone:.5,dash:.4,slam:.55,chain:.45})[A.m.kind]||.45; A.rm=0; } };
CP.cancelOK=(A,kind)=>{ if(!A.pose) return kind==="chain"?A.t>=CHAIN.minT:true; const u=CP.u, q=u&&u.combatQuery&&u.combatQuery(); if(q&&u.combatState&&u.combatState()==="atk") return !!(q.cancelOpen&&q.cancelKinds.indexOf(kind)>=0); return A.t>=CHAIN.minT; };
CP.hitstop=(u,ms)=>{ if(u&&u.combatHitStop&&ms>0) try{ u.combatHitStop(ms); }catch(e){} };
CP.blocked=(x,z)=>typeof colliders!=="undefined"&&colliders.some(c=>!c.off&&x>c.minX-.35&&x<c.maxX+.35&&z>c.minZ-.35&&z<c.maxZ+.35);
CP.root=(A,dt)=>{ const u=CP.u, q=u&&u.combatQuery&&u.combatQuery(); if(!q||!q.root||!(q.root.fwdVel>0)) return; const xr=renderer.xr.isPresenting, cap=xr?CP.rmMaxXR:CP.rmMax;
  const v=Math.min(q.root.fwdVel,CP.vMax), d=Math.min(v*dt,Math.max(0,cap-A.rm)); if(d<=0) return; const p=Ride.group.position, nx=p.x+Math.sin(Ride.yaw)*d, nz=p.z+Math.cos(Ride.yaw)*d;
  if(CP.blocked(nx,nz)){ A.rmBlocked=true; return; } p.x=nx; p.z=nz; A.rm+=d; A.rmV=Math.max(A.rmV||0,v); /* no vertical root motion (XR comfort) */ };
addEventListener("pagehide",()=>CP.teardown());
const ATK={ set:null, cd:[0,0,0], act:null, fx:[], hits:0, npcPassive:false, stun:0, kv:new THREE.Vector2(), prevPad:{}, prevXR:{}, ctlPrev:[null,null], swingCd:0 };
// ---------- input (own edge detection; desktop / gamepad / VR) ----------
const WIN={ k:{}, p:{} };
addEventListener("keydown",e=>{ if(e.repeat) return; WIN.k[e.code]=true; WIN.p[e.code]=true; });
addEventListener("keyup",e=>{ WIN.k[e.code]=false; });
addEventListener("mousedown",e=>{ if(typeof State==="undefined"||State.mode!=="ride"||e.target.closest&&e.target.closest("#gatepad,button,.menu")) return; WIN.p[e.button===2?"MouseR":"MouseL"]=true; });
addEventListener("contextmenu",e=>{ if(typeof State!=="undefined"&&State.mode==="ride") e.preventDefault(); });
function wallInput(){ const I={jumpP:!!WIN.p.Space, jump:!!WIN.k.Space, a:[!!(WIN.p.KeyJ||WIN.p.MouseL),!!(WIN.p.KeyK||WIN.p.MouseR),!!WIN.p.KeyL],
    back:!!(WIN.k.KeyS||WIN.k.ArrowDown), side:(WIN.k.KeyA||WIN.k.ArrowLeft?-1:0)+(WIN.k.KeyD||WIN.k.ArrowRight?1:0), bP:!!WIN.p.KeyB }; WIN.p={};
  try{ if(window.SR_PAD&&SR_PAD.justPressed&&!renderer.xr.isPresenting&&SR_PAD.justPressed("B")) I.bP=true; }catch(e){}   // B = dodge/cancel (combat C1)
  const gp=(navigator.getGamepads?[...navigator.getGamepads()]:[]).find(Boolean), xr=renderer.xr.isPresenting;
  if(gp&&!xr){ const b=i=>!!(gp.buttons[i]&&gp.buttons[i].pressed), P=ATK.prevPad, e=i=>b(i)&&!P[i];
    if(e(0)) I.jumpP=true; if(b(0)) I.jump=true; if(e(3)) I.a[0]=true; if(e(7)) I.a[1]=true; if(e(6)) I.a[2]=true;
    const ly=gp.axes[1]||0, lx=gp.axes[0]||0; if(ly>.5) I.back=true; if(Math.abs(lx)>.5) I.side=Math.sign(lx); for(const i of [0,3,6,7]) P[i]=b(i); }
  const ses=xr&&renderer.xr.getSession(); if(ses){ for(const s of ses.inputSources){ const g=s.gamepad; if(!g) continue; const h=s.handedness, P=ATK.prevXR, b=i=>!!(g.buttons[i]&&g.buttons[i].pressed), e=i=>b(i)&&!P[h+i];
      if(h==="right"){ if(e(4)) I.jumpP=true; if(b(4)) I.jump=true; if(e(5)) I.a[0]=true; } else { if(e(4)) I.a[1]=true; if(e(5)) I.a[2]=true; }
      const ax=g.axes||[]; if((ax[3]||0)>.5&&h==="left") I.back=true; if(Math.abs(ax[2]||0)>.5&&h==="left") I.side=Math.sign(ax[2]); P[h+4]=b(4); P[h+5]=b(5); }
    // swing gesture: a fast controller swing (> 2.6 m/s) throws the light attack
    for(let i=0;i<2;i++){ const c=renderer.xr.getController(i); if(!c) continue; if(!c.parent) rig.add(c); c.updateMatrixWorld(); const w=new THREE.Vector3().setFromMatrixPosition(c.matrixWorld), pv=ATK.ctlPrev[i];
      if(pv&&ATK.swingCd<=0&&w.distanceTo(pv)/Math.max(.008,ATK.dtLast||.016)>2.6+Ride.speed){ I.a[0]=true; ATK.swingCd=.5; } ATK.ctlPrev[i]=w; } }
  return I; }
// ---------- candidate wall faces (same filter as the turf 'candidate wall faces': box faces 2.6..90 m long) ----------
function wallFace(c,x,z,r){ if(c.off) return null; const w=c.maxX-c.minX, d=c.maxZ-c.minZ; if(Math.max(w,d)<2.6||Math.max(w,d)>90) return null;
  if(!(x>c.minX-r&&x<c.maxX+r&&z>c.minZ-r&&z<c.maxZ+r)) return null; const dx1=x-(c.minX-r), dx2=(c.maxX+r)-x, dz1=z-(c.minZ-r), dz2=(c.maxZ+r)-z, m=Math.min(dx1,dx2,dz1,dz2);
  const f=m===dx1?{nx:-1,nz:0,len:d}:m===dx2?{nx:1,nz:0,len:d}:m===dz1?{nx:0,nz:-1,len:w}:{nx:0,nz:1,len:w}; if(f.len<2.6) return null; f.c=c; kickTag(f); return f; }
// Kick eligibility (Oliver 09:26): wallKick:true / WALL_PANELS always; facades unless noKick or (no flag) < 2.5 m tall. WALL_KICKS normals when present. All feature-detected.
function kickIdx(){ const L=window.WALL_KICKS; if(!Array.isArray(L)||!L.length) return null; if(KICK._wk!==L||KICK._wkn!==L.length){ KICK._wk=L; KICK._wkn=L.length; KICK._map=new Map(); for(const k of L){ const c=k&&(k.collider||(typeof k.colliderIndex==="number"?colliders[k.colliderIndex]:null)); if(c) KICK._map.set(c,k); } } return KICK._map; }
function kickHeight(c){ if(typeof c.maxY==="number") return c.maxY-(c.minY||0); if(typeof c.height==="number") return c.height; if(typeof c.h==="number") return c.h; const m=c.mesh; if(m&&m.geometry&&m.geometry.parameters&&m.geometry.parameters.height) return m.geometry.parameters.height*(m.scale?m.scale.y:1); return null; }
function kickTag(f){ const c=f.c, ud=(c.mesh&&c.mesh.userData)||c.userData||{}; const W=kickIdx(), k=W&&W.get(c);
  if(c.wallKick||ud.wallKick||k||c.wallPanel){ f.kick=true; f.src=k?"WALL_KICKS":(c.wallPanel?"WALL_PANELS":"wallKick"); }
  else if(c.noKick||ud.noKick){ f.kick=false; f.src="noKick"; }
  else { const h=kickHeight(c); f.kick=!(h!=null&&h<2.5); f.src=h==null?"facade?":"facade"; }
  f.name=(k&&k.name)||c.wallKickName||ud.name||c.wallPanelName||c.name||null;
  if(k&&k.normal){ const n=k.normal, nx=n.x!=null?n.x:n[0], nz=n.z!=null?n.z:n[2], l=Math.hypot(nx,nz); if(l>1e-6){ const ax=nx/l, az=nz/l; if(ax*f.nx+az*f.nz>0.2){ f.nx=ax; f.nz=az; } } } }
window.kickTag=kickTag;
// WALL RIDE panels: authored flag from blockout.js boWallPanels (collider.wallPanel + wallPanelName, window.WALL_PANELS).
// The 1.6x10 collider-size guess is only a fallback for builds without the flag.
function wallPanelTag(){ if(WALL.tagged) return; WALL.tagged=true;
  const L=Array.isArray(window.WALL_PANELS)?window.WALL_PANELS:null; if(L&&L.length){ for(const w of L) if(w&&w.collider){ w.collider.wallPanel=true; if(w.name&&!w.collider.wallPanelName) w.collider.wallPanelName=w.name; } WALL.panelSrc="WALL_PANELS"; return; }
  if(colliders.some(c=>c.wallPanel&&c.wallPanelName)){ WALL.panelSrc="flag"; return; }
  WALL.panelSrc="size-guess"; for(const c of colliders){ const w=c.maxX-c.minX, d=c.maxZ-c.minZ; if(Math.abs(w-1.6)<.01&&Math.abs(d-10)<.01) c.wallPanel=true; } }
function wallStick(f,dx,dz,sp,y,fromAir){ const R=Ride, p=R.group.position, dn=dx*f.nx+dz*f.nz; let tx=dx-f.nx*dn, tz=dz-f.nz*dn; const tl=Math.hypot(tx,tz)||1; tx/=tl; tz/=tl;
  const c=f.c; if(f.nx) p.x=(f.nx>0?c.maxX:c.minX)+f.nx*.45; else p.z=(f.nz>0?c.maxZ:c.minZ)+f.nz*.45;
  if(fromAir&&WALL.lastWall&&WALL.lastWall!==c){  /* Systems 08:20: coexists with the kick chain (KICK.n>0 gate broke wallride wall-to-wall: kick-off sets KICK.n) */  WALL.chain++; trickScore(250*WALL.chain,"WALL-TO-WALL x"+WALL.chain,.12); } else if(!fromAir) WALL.chain=0;
  WALL.on={f,tx,tz,sp:Math.max(sp*.97,WALL.minSpeed),y:Math.max(y,.05),y0:y,vy:fromAir?1.5:2.4+sp*.1,t:0,panel:!!c.wallPanel}; WALL.air=null; WALL.lastWall=c;
  if(!fromAir) trickScore(c.wallPanel?150:100,c.wallPanel?"WALL RIDE PANEL":"WALL RIDE",.05); for(let k=0;k<14;k++) emit({x:p.x-f.nx*.4,y:WALL.on.y+.2,z:p.z-f.nz*.4},k%2?0xffd27a:0xffffff,rnd(-3,3)+tx*4,rnd(1,4),rnd(-3,3)+tz*4,.4); }
function trickScore(pts,label,meter){ WALL.score+=pts; Stats.tricks=(Stats.tricks||0)+pts; if(typeof DASH!=="undefined") DASH.meter=Math.min(1,DASH.meter+(meter||0)); bumpChain(); if(label) flash(label+" +"+pts,atkSet().css); }
function wallLaunch(vx,vz,vy,flip){ const R=Ride, p=R.group.position; WALL.air={vx,vz,vy,y:R.y,flip:!!flip,t:0}; WALL.launches=(WALL.launches||0)+1; if(flip) WALL.flips=(WALL.flips||0)+1; WALL.on=null; if(flip) WALL.flipT=0; }
// returns true when it moved the rider this frame (updateRide is skipped)
function wallKick(f,R,p){ const n=KICK.n; if(f&&f.kick===false){ KICK.refused=(KICK.refused||0)+1; return false; } if(n>=KICK.max||clock-KICK.ct>KICK.win){ KICK.ignored++; return false; }
  const vy=KICK.up[n]*KICK.upScale, A=WALL.air, tx=-f.nz, tz=f.nx, hv=A?(A.vx*tx+A.vz*tz):0;
  wallLaunch(f.nx*KICK.out+tx*hv*KICK.along,f.nz*KICK.out+tz*hv*KICK.along,vy,false); WALL.air.kick=true; WALL.air.kf=f; WALL.air.y=Math.max(R.y,p.y);
  KICK.n=n+1; KICK.kicks++; KICK.ct=-9; KICK.nudge=.18; KICK.face=null; const sx=p.x-f.nx*.4, sz=p.z-f.nz*.4;
  for(let k=0;k<10;k++) emit({x:sx,y:WALL.air.y+.3,z:sz},k%2?0xd8d0c0:0xffffff,f.nx*rnd(.5,3)+tx*rnd(-2,2),rnd(-1,1.5),f.nz*rnd(.5,3)+tz*rnd(-2,2),.35);
  try{ ATK.fx.push({type:"ring",x:sx,z:sz,r:.9,t:0,life:.3,c1:0xffffff,c2:0xd8d0c0,shape:"ring"}); }catch(e){}
  trickScore(120+60*KICK.n,"WALL KICK x"+KICK.n,.06); return true; }
window.wallKickCam=function(dt,xr){ if(KICK.nudge<=0) return; if(!(xr&&renderer.xr.isPresenting)&&!window.__camHook) camera.position.y-=KICK.nudge*.25; KICK.nudge=Math.max(0,KICK.nudge-dt*1.2); };  // pitch-free vertical nudge only; skipped in VR
function wallStep(dt){ const R=Ride, p=R.group.position, I=WALL.I||{}; wallPanelTag(); if(ATK.stun>0){ ATK.stun-=dt; Input.mag=0; }
  if((!WALL.air&&!WALL.on)||R.grinding||(typeof GRIND!=="undefined"&&GRIND.on)){ KICK.n=0; KICK.face=null; }
  if(WALL.on){ KICK.ct=clock; KICK.face=WALL.on.f; }
  // ground: jump = hop (lets you reach walls airborne); detect shallow wall impacts at speed
  if(!WALL.on&&!WALL.air){ const dx=Math.sin(R.yaw), dz=Math.cos(R.yaw);
    if(I.jumpP&&State.mode==="ride"&&!(typeof GATE!=="undefined"&&GATE.uiOpen)){ wallLaunch(dx*R.speed,dz*R.speed,5.6,false); R.grinding=false; return true; }
    if(R.speed>=WALL.minSpeed&&!R.grinding){ const ahead=R.speed*dt+.2, nx=p.x+dx*ahead, nz=p.z+dz*ahead;
      for(const c of colliders){ const f=wallFace(c,nx,nz,.45); if(!f) continue; const into=-(dx*f.nx+dz*f.nz); if(into>0&&into<WALL.maxInto){ wallStick(f,dx,dz,R.speed,R.y,false); return true; } } }
    return false; }
  if(WALL.on){ const W=WALL.on, f=W.f, c=f.c; W.t+=dt; const hold=I.jump; W.vy-=(hold?2.6:8.5)*dt; if(W.g0===undefined){ let g=null; try{ g=typeof window.WORLD_GROUND==='function'?window.WORLD_GROUND(p.x+f.nx*.6,p.z+f.nz*.6,W.y):null; }catch(e){} W.g0=g&&Number.isFinite(g.y)?g.y:0; } const yc=Math.max(W.g0+6.5,W.y0||0);  // cap relative to real ground (seed-1 WORLD_GROUND) W.y=Math.min(yc,W.y+W.vy*dt); if(W.y>=yc) W.vy=Math.min(0,W.vy);
    W.sp=Math.max(0,W.sp-dt*(hold?.6:2.2)); p.x+=W.tx*W.sp*dt; p.z+=W.tz*W.sp*dt; R.y=W.y; p.y=W.y; R.speed=W.sp; R.yaw=Math.atan2(W.tx,W.tz); R.grinding=false;
    if(!(WALL.score>0)) WALL.score=0; WALL.ride=(WALL.ride||0)+dt; if(typeof DASH!=="undefined") DASH.meter=Math.min(1,DASH.meter+dt*(W.panel?.1:.07)); Stats.tricks=(Stats.tricks||0)+Math.round(dt*60);
    if(frame%2===0){ const sx=p.x-f.nx*.42, sz=p.z-f.nz*.42; for(let k=0;k<2;k++) emit({x:sx,y:W.y+.08,z:sz},k?0xffd27a:atkSet().c1,-W.tx*rnd(1,4)+f.nx*rnd(0,2),rnd(.5,3),-W.tz*rnd(1,4)+f.nz*rnd(0,2),.35); WALLSPARK++; }
    const off=f.nx?(p.z<c.minZ-.3||p.z>c.maxZ+.3):(p.x<c.minX-.3||p.x>c.maxX+.3);
    if(I.jumpP){ const into=Input.mag>0&&-(Math.sin(Input.yaw)*f.nx+Math.cos(Input.yaw)*f.nz)>.35, flip=(W.panel||!into)&&(I.back||I.side!==0);  /* 08:20: WALL RIDE panels keep jump+direction = flip */  /* Systems 01:55: stick pushed INTO the wall + A = wall-kick (one press, one action); flip needs back/side AWAY from it (holding left into the98_13 flipped out of the chain) */ if(!flip){ const r0=KICK.refused||0, n0=KICK.n, dct=clock-KICK.ct;
        if(wallKick(f,R,p)){ const A=WALL.air; const al=f.src==="WALL_KICKS"?KICK.along:.85; A.vx+=W.tx*W.sp*al; A.vz+=W.tz*W.sp*al; }
        else { /* Systems 09:52: refused/ignored wall-kick never eats the press on a wallride -> old plain kick-off (out + 0.85 along) */
          const why=(KICK.refused||0)>r0?"face kick:false ("+(f.src||"?")+")":n0>=KICK.max?"KICK.max":dct>KICK.win?"window ("+dct.toFixed(2)+" > "+KICK.win+")":"?";
          KICK.lastRefuse={why,src:f.src,n:n0,dct:+dct.toFixed(3),refused:KICK.refused||0,ignored:KICK.ignored,t:+clock.toFixed(2)}; KICK.fallbacks=(KICK.fallbacks||0)+1;
          wallLaunch(f.nx*6+W.tx*W.sp*.85,f.nz*6+W.tz*W.sp*.85,5.6,false); WALL.air.y=Math.max(R.y,p.y); }
        return true; }  /* Systems 01:40: kick off a wallride carries along-wall speed with KICK.along like the air kick (was .85: 7 m/s along the face shot the rider out of the 4 m alley after kick 1) */  // limit reached / window missed: A does nothing on the wall
      const kx=f.nx*6.2+W.tx*W.sp*.85, kz=f.nz*6.2+W.tz*W.sp*.85; wallLaunch(kx,kz,7.6,true); trickScore(400,"WALL FLIP",.15); return true; }
    if(off||W.sp<4||(W.y<=.02&&W.vy<0)||W.t>(hold?4.5:2.2)||!onLand(p.x,p.z)){ if(W.y>.15) wallLaunch(W.tx*W.sp+f.nx*1.5,W.tz*W.sp+f.nz*1.5,0,false); else { WALL.on=null; R.y=0; p.y=0; } }
    return true; }
  // airborne (hop, kick-off, flip, fall off a wall end)
  const A=WALL.air; A.t+=dt; A.vy-=(A.kick?KICK.g:13)*dt*(ATK.floatT>0?.25:1);  /* combat air hit float (flag-gated: floatT only set with combat poses) */
  if(A.kick&&A.kf&&A.t>.18){ const f=A.kf, o=A.vx*f.nx+A.vz*f.nz; if(!A.opp){ A.opp=colliders.some(c=>!c.off&&wallFace(c,p.x+f.nx*6,p.z+f.nz*6,1.2))?1:-1; } if(A.opp<0&&o>-KICK.out) { A.vx-=f.nx*KICK.back*dt; A.vz-=f.nz*KICK.back*dt; } }  // no facing wall: zig-zag back to the same wall
  if(A.kick) KICK.peakY=Math.max(KICK.peakY,A.y);
  if(I.jumpP&&KICK.face&&A.t>.05){ if(wallKick(KICK.face,R,p)) return true; } A.y+=A.vy*dt; const ox=p.x, oz=p.z; p.x+=A.vx*dt; p.z+=A.vz*dt; if(!onLand(p.x,p.z)){ p.x=ox; p.z=oz; A.vx*=-.3; A.vz*=-.3; }
  const hs=Math.hypot(A.vx,A.vz); if(hs>.5) R.yaw=Math.atan2(A.vx,A.vz);
  for(const c of colliders){ if(A.y>7&&!A.kick) break; const f=wallFace(c,p.x,p.z,.45), fk=f||wallFace(c,p.x,p.z,KICK.reach); if(fk&&A.t>.12&&fk.kick!==false){ KICK.ct=clock; KICK.face=fk; } /* kick contact reach > collision radius (hop drift left riders 0.46 m off) */ if(!f){ if(!c.off&&p.x>c.minX-.4&&p.x<c.maxX+.4&&p.z>c.minZ-.4&&p.z<c.maxZ+.4){ p.x=ox; p.z=oz; A.vx*=-.2; A.vz*=-.2; } continue; }
    const into=-(A.vx*f.nx+A.vz*f.nz)/(hs||1); if(into>0&&into<.85&&hs>5&&A.t>.12&&A.y>.15){ wallStick(f,A.vx/hs,A.vz/hs,hs,A.y,true); return true; }
    if(f.nx) p.x=(f.nx>0?c.maxX:c.minX)+f.nx*.46; else p.z=(f.nz>0?c.maxZ:c.minZ)+f.nz*.46; const vn=A.vx*f.nx+A.vz*f.nz; A.vx-=f.nx*vn*1.2; A.vz-=f.nz*vn*1.2; }
  if(A.y<=0){ A.y=0; R.speed=Math.min(hs,R.maxSpeed*1.5); WALL.air=null; if(A.flip) trickScore(150,"FLIP LANDED",.05); if(ATK.act&&ATK.act.m.kind==="dive") atkLand(); WALL.chain=0; WALL.lastWall=null; }
  R.y=A.y; p.y=A.y; return true; }
// ---------- attacks ----------
function atkSet(){ if(!ATK.set){ const q=new URLSearchParams(location.search).get("moves"); ATK.set=MOVESETS[q]?q:((typeof PLAYER_MODE!=="undefined"&&PLAYER_MODE==="ikki")?"karasu":"codee"); }
  const S=MOVESETS[ATK.set]; S.css=S.css||"#"+new THREE.Color(S.c1).getHexString(); return S; }
function atkTargets(){ const T=[]; for(const n of RIDERS.npcs) if(n.holder&&n.holder.visible) T.push(n); const k=RIDERS.ikkiNpc; if(k&&k.holder&&k.holder.visible){ k.g=k.g||garages.find(g=>g.crew==="karasu"); T.push(k); } return T; }
function atkStart(i,src){ const S=atkSet(), m=S.moves[i];
  if(i===0&&m&&State.mode==="ride"&&ATK.stun<=0){ if(clock-CHAIN.last>CHAIN.win&&CHAIN.n){ CHAIN.n=0; CHAIN.resets++; }
    const cur=ATK.act; if(CHAIN.n>0&&CHAIN.n<3&&(!cur||(cur.i===0&&!cur.heavy&&CP.cancelOK(cur,"chain")))){ return atkChainNext(S,m,cur); } }
  if(!m||ATK.cd[i]>0||ATK.act||ATK.stun>0||State.mode!=="ride"||(typeof GATE!=="undefined"&&GATE.uiOpen)) return false;
  ATK.cd[i]=m.cd; ATK._soft=null; const R=Ride, p=R.group.position;
  // soft lock-on: melee moves snap toward the nearest rider in front within reach (VR-friendly aim assist; rig still yaw-only)
  if(m.kind==="cone"||m.kind==="dash"||m.kind==="slam"){ let bt=null, bd=m.r+3; const fx=Math.sin(R.yaw), fz=Math.cos(R.yaw);
    for(const n of atkTargets()){ const q=n.holder.position, ddx=q.x-p.x, ddz=q.z-p.z, d=Math.hypot(ddx,ddz); if(d<bd&&(ddx*fx+ddz*fz)/(d||1)>-.2){ bd=d; bt=n; } }
    if(bt){ ATK._soft=bt; const q=bt.holder.position; R.yaw=Math.atan2(q.x-p.x,q.z-p.z); if(m.kind==="cone"){ ATK.lock=bt; if(bd>m.r*.6) R.speed=Math.max(R.speed,(bd-m.r*.5)*4); } } }
  const dx=Math.sin(R.yaw), dz=Math.cos(R.yaw); ATK.act={m,i,t:0,hit:new Set(),o:p.clone(),dx,dz,S,ch:i===0?1:0}; if(i===0){ CHAIN.n=1; CHAIN.last=clock; CHAIN.log.push([1,+clock.toFixed(2)]); }
  if(m.kind==="dash"){ R.speed=Math.max(R.speed,R.maxSpeed*1.5); if(WALL.air) { WALL.air.vx=dx*R.speed; WALL.air.vz=dz*R.speed; } }
  if(m.kind==="dive"){ if(!WALL.air&&!WALL.on){ let reach=2.4; for(const n of atkTargets()){ const q=n.holder.position, ddx=q.x-p.x, ddz=q.z-p.z, d=Math.hypot(ddx,ddz); if(d<7&&(ddx*dx+ddz*dz)/(d||1)>.5) reach=Math.min(reach,d); } wallLaunch(dx*reach/.95,dz*reach/.95,6.2,false); } else if(WALL.air){ WALL.air.vy=-9; WALL.air.vx=dx*14; WALL.air.vz=dz*14; } ATK.act.dive=true; }
  if(m.kind==="slam") R.speed=Math.max(R.speed,14);
  atkCommitStart(ATK.act); if(i===0&&CP.flag()) CP.atk(ATK.act,{step:0});  // lock-commit (Oliver via Ani 01:41): commit to the aimed target for the whole attack
  if(m.kind==="chain") atkChain(ATK.act);
  atkSfx(m); if(window.CombatFX) cfxEmit("attackStart",null,null,dx,dz,1); else gateHaptic&&gateHaptic(.5,40); $("atkhud")&&atkHUD(); return true; }
// next chain hit: same move, commit lock carried over (no re-pick: no target switching mid-chain), hit 3 = finisher (bigger knock, commits: no A/B cancel)
function atkChainNext(S,m,cur){ const R=Ride, p=R.group.position, C=ATK.commit; CHAIN.n++; CHAIN.last=clock; CHAIN.log.push([CHAIN.n,+clock.toFixed(2)]);
  const tg=C&&C.ref&&C.ref.holder?C.ref:null; if(tg){ const q=tg.holder.position; R.yaw=Math.atan2(q.x-p.x,q.z-p.z); }
  const dx=Math.sin(R.yaw), dz=Math.cos(R.yaw), fin=CHAIN.n===3, mm=fin?Object.assign({},m,{knock:m.knock*2.4,stun:m.stun*1.6,r:m.r*1.15,name:m.name+" FINISHER"}):m;
  ATK.act={m:mm,i:0,t:0,hit:new Set(),o:p.clone(),dx,dz,S,ch:CHAIN.n,fin}; if(tg&&mm.kind==="cone") ATK.lock=tg;
  if(mm.kind==="dash"){ R.speed=Math.max(R.speed,R.maxSpeed*1.5); } if(mm.kind==="slam") R.speed=Math.max(R.speed,14);
  if(C) C.act=ATK.act; else atkCommitStart(ATK.act); if(CP.flag()) CP.atk(ATK.act,{step:CHAIN.n-1}); if(mm.kind==="chain"&&!ATK.act.pose) atkChain(ATK.act);
  if(fin) ATK.cd[0]=m.cd+.35; atkSfx(mm); if(window.CombatFX) cfxEmit("attackStart",null,null,dx,dz,fin?1.4:1); else gateHaptic&&gateHaptic(.5,40); return true; }
// posed hit window: my radius/cone hit tests, opened by onHitFrame (or the fallback timer), root motion through collision
function cpStep(A,dt,rdt){ A.t+=dt; if(A.ch) CHAIN.last=clock;  /* posed hits run longer than the 0.6 s press window: the chain timeout counts from the end of the current hit */ const m=A.m, p=Ride.group.position, C=ATK.commit;
  if(A.heavy&&A.charging){ A.charge=Math.min(1,(A.charge||0)+dt); if(A.charge>=1){ A.charging=false; A.autoRel=true; try{ CP.u&&CP.u.combatRelease(); }catch(e){} CP.log.push(["release","auto",+clock.toFixed(2)]); } A.t=0; return; }
  if(C&&C.ref&&C.ref.holder&&!A.hit.has(C.ref)){ const q=C.ref.holder.position; Ride.yaw=Math.atan2(q.x-p.x,q.z-p.z); A.dx=Math.sin(Ride.yaw); A.dz=Math.cos(Ride.yaw); }
  CP.root(A,dt);
  if(!A.hitOpen&&A.t>=A.D+.1){ A.hitOpen=true; A.hoT=A.t; A.hitSrc="fallback"; }
  if(A.hitOpen) for(const n of atkTargets()){ const q=n.holder.position, ddx=q.x-p.x, ddz=q.z-p.z, d=Math.hypot(ddx,ddz); if(d<1.3||d<m.r+.4&&(ddx*A.dx+ddz*A.dz)/(d||1)>-.1) atkHit(A,n,ddx,ddz); }
  const holdJ=A.ch===1&&!A.heavy&&CP.heldJ>0&&CP.heldJ<.35;   // J still held: hit 1 may still turn into a heavy
  if(!holdJ&&(A.hitOpen&&A.t-A.hoT>=.12||A.t>A.D+.6)){ ATK.act=null; ATK.lock=null; } }
function cpHeavyInput(dt){ let held=!!(WIN.k&&WIN.k.KeyJ); try{ if(!held&&window.SR_PAD&&SR_PAD.pressed&&!renderer.xr.isPresenting) held=!!SR_PAD.pressed("Y"); }catch(e){}
  const A=ATK.act; if(held) CP.heldJ+=dt; else { if(A&&A.heavy&&A.charging){ A.charging=false; try{ CP.u&&CP.u.combatRelease(); }catch(e){} CP.log.push(["release","manual",+clock.toFixed(2)]); } CP.heldJ=0; return; }
  if(CP.heldJ>=.35&&A&&A.pose&&A.ch===1&&!A.heavy){ const m=A.m; A.heavy=true; A.hit=new Set(); A.charging=true; A.charge=0; A.ch=0; CHAIN.n=0; A.m=Object.assign({},m,{name:m.name+" HEAVY"}); A.hitOpen=false; A.t=0; A.D=.45;
    CP.state(CP.u,"atk",{move:"heavy",charge:true,target:ATK.commit&&ATK.commit.ref&&ATK.commit.ref.holder||null}); } }
function atkHit(A,n,dirx,dirz){ if(A.pose&&!A.hitOpen) return; if(A.hit.has(n)) return; A.hit.add(n); const m=A.m; ATK.hits++; n.hitN=(n.hitN||0)+1; n.lastKnock=m.knock;
  const l=Math.hypot(dirx,dirz)||1, kk=A.heavy?m.knock*2*(.5+.5*Math.min(1,A.charge||0)):m.knock; n.lastKnock=kk; (n.knockLog=n.knockLog||[]).push(kk); n.kv=new THREE.Vector2(dirx/l*kk,dirz/l*kk); n.stun=m.stun; n.stunMax=m.stun; n.off=n.off||new THREE.Vector3();
  const hp=n.holder.position; for(let k=0;k<18;k++) emit({x:hp.x,y:1.2,z:hp.z},k%3?A.S.c1:(A.S.c1===0x00e5ff?0x9ff6ff:0xffffff),rnd(-5,5),rnd(1,6),rnd(-5,5),.5);
  ATK.fx.push({type:"burst",x:hp.x,y:1.1,z:hp.z,t:0,life:.35,c1:A.S.c1,c2:A.S.c2});
  trickScore(120+Math.round(m.knock*10),"HIT! "+m.name.toUpperCase(),.06); atkTone("square",220,90,.12,.12);
  const evt=A.fin?"finisher":A.ch?"lightHit":(A.dive?"dive":"hit3"); _cfxP.set(hp.x,1.1,hp.z);
  if(window.CombatFX){ let ms;
    if(A.hfEv&&CombatFX.fromHitFrame&&!A.hfDone){ /* poses on: Rigger's hit frame drives the ONE spark (fromHitFrame, haptics off); my path adds the ONE haptic; no second emit */
      A.hfDone=true; const ev=A.hfEv; ev.fxCharge=A.heavy?Math.min(1.5,A.charge||0):undefined; ev.target=n.holder; if(!ev.fxName) ev.fxName=fxNameOf(A);
      try{ ms=+CombatFX.fromHitFrame(ev,evt,ATK.set)||0; }catch(e){ ATK.cfxErr=String(e); ms=0; } try{ if(window.SR_PAD&&SR_PAD.haptic) SR_PAD.haptic(evt,CEV); }catch(e){}
      (ATK.evLog=ATK.evLog||[]).push(["hf:"+evt,+clock.toFixed(2),ms]); }
    else ms=cfxEmit(evt,n,_cfxP,dirx,dirz,A.fin?1.8:1,A);
    ms*=HITSTOP.scale; if(ms>0&&A.pose){ CP.hitstop(CP.u,ms); CP.hitstop(CP.uOf(n),ms); } if(ms>0){ const s=ms/1000; n.hs=Math.max(n.hs||0,s); HITSTOP.att=Math.max(HITSTOP.att,s); HITSTOP.log.push([evt,ms,+clock.toFixed(2)]); if(HITSTOP.log.length>40) HITSTOP.log.shift(); } }
  else gateHaptic&&gateHaptic(.8,70);
  if(CP.flag()){ const vu=CP.uOf(n); if(vu&&vu.setState){ const d=new THREE.Vector3(dirx,0,dirz).normalize(); CP.state(vu,"react",{kind:A.fin||A.heavy?"knockdown":"light",dir:d}); n.reacted=(n.reacted||0)+1; }
    if(WALL.air){ ATK.floatT=Math.max(ATK.floatT||0,CP.floatMin); WALL.air.vy=Math.max(WALL.air.vy,0); ATK.floats=(ATK.floats||0)+1; } } }
const _cfxP=new THREE.Vector3();
function atkChain(A){ const p=Ride.group.position; let from=p.clone().setY(1.1), left=A.m.r, used=new Set();
  for(let k=0;k<3;k++){ let best=null, bd=k?6:A.m.r; for(const n of atkTargets()){ if(used.has(n)) continue; const d=n.holder.position.distanceTo(_atkV.copy(from).setY(0)); if(d<bd){ bd=d; best=n; } } if(!best) break;
    used.add(best); const to=best.holder.position.clone().setY(1.1); ATK.fx.push({type:A.m.fx==="bolt"?"bolt":"beam",a:from.clone(),b:to,t:0,life:.45,c1:A.S.c1,c2:A.S.c2}); atkHit(A,best,to.x-p.x,to.z-p.z); from=to; }
  if(!used.size) ATK.fx.push({type:"bolt",a:from.clone(),b:from.clone().add(new THREE.Vector3(A.dx*6,0,A.dz*6)),t:0,life:.3,c1:A.S.c1,c2:A.S.c2}); }
const _atkV=new THREE.Vector3();
function atkLand(){ const A=ATK.act; if(!A) return; const p=Ride.group.position; A.landed=true; ATK.fx.push({type:"ring",x:p.x,z:p.z,r:A.m.r,t:0,life:.5,c1:A.S.c1,c2:A.S.c2,shape:A.m.fx});
  for(const n of atkTargets()){ const q=n.holder.position, d=Math.hypot(q.x-p.x,q.z-p.z); if(d<A.m.r+(n===A.tgt?DIVE.landR:0)) atkHit(A,n,q.x-p.x,q.z-p.z); } }
// DIVE soft homing (Ani 09:39: dives missed MOVING targets). Lock the best target in front at dive start (or nearest within lockR in air),
// lead it by its measured velocity, and turn the horizontal air velocity toward the intercept at <= turn rad/s (speed eased, capped).
// Locked target gets +landR on the landing ring and airR for the mid-air contact hit. No new draws.
const DIVE={lockR:8, turn:5.5, maxSp:11, accel:22, lead:1, landR:1.2, airR:1.9}; window.DIVE=DIVE;
function diveHome(A,p,dt){ const W=WALL.air; if(!W||A.noHome) return;
  if(!A.tgt||!A.tgt.holder||!A.tgt.holder.visible){ let best=null,bs=-1e9; const hx=Math.sin(Ride.yaw), hz=Math.cos(Ride.yaw);
    for(const n of atkTargets()){ const q=n.holder.position, dx=q.x-p.x, dz=q.z-p.z, d=Math.hypot(dx,dz); if(d>DIVE.lockR) continue; const sc=(dx*hx+dz*hz)/(d||1)*2-d/DIVE.lockR; if(sc>bs){ bs=sc; best=n; } }
    A.tgt=best; if(best){ A.tq=best.holder.position.clone(); A.tv={x:0,z:0}; } if(!best) return; }
  const q=A.tgt.holder.position; if(dt>0&&A.tq){ const k=Math.min(1,dt*8); A.tv.x+=((q.x-A.tq.x)/dt-A.tv.x)*k; A.tv.z+=((q.z-A.tq.z)/dt-A.tv.z)*k; A.tq.copy(q); }
  // time to land from current height/vy under gravity 13 (ground = WALL.air.g0 when known)
  const g=13, y=W.y-(W.g0||0), vy=W.vy, tl=Math.max(.05,(vy+Math.sqrt(Math.max(0,vy*vy+2*g*Math.max(0,y))))/g)*DIVE.lead;
  const ix=q.x+A.tv.x*tl-p.x, iz=q.z+A.tv.z*tl-p.z, dist=Math.hypot(ix,iz); if(dist<1e-3) return;
  const want=Math.min(DIVE.maxSp,dist/tl), cur=Math.hypot(W.vx,W.vz);
  let ang=Math.atan2(W.vx,W.vz); const tgtAng=Math.atan2(ix,iz); let da=tgtAng-ang; da=Math.atan2(Math.sin(da),Math.cos(da));
  const mx=DIVE.turn*dt; ang+=Math.max(-mx,Math.min(mx,da)); const sp=cur+Math.max(-DIVE.accel*dt,Math.min(DIVE.accel*dt,want-cur));
  W.vx=Math.sin(ang)*sp; W.vz=Math.cos(ang)*sp; A.homed=(A.homed||0)+1; }
function atkUpdate(dt){ ATK.dtLast=dt; ATK.swingCd-=dt; for(let i=0;i<3;i++) ATK.cd[i]=Math.max(0,ATK.cd[i]-dt);
  const I=WALL.I||{a:[]}; if(State.mode==="ride") for(let i=0;i<3;i++) if(I.a[i]) atkStart(i,"in");
  const A=ATK.act, R=Ride, p=R.group.position;
  if(CHAIN.n&&!ATK.act&&clock-CHAIN.last>CHAIN.win){ CHAIN.n=0; CHAIN.resets++; }
  if(A&&A.ch&&A.ch<3&&(I.jumpP||I.bP)&&CP.cancelOK(A,I.jumpP?"jump":"dash")){ CHAIN.cancels++; CHAIN.cancelLog=[I.jumpP?"A":"B",A.ch,+clock.toFixed(2)]; ATK.act=null; ATK.lock=null; CHAIN.n=0; HITSTOP.att=0; if(I.bP&&window.CombatFX) cfxEmit("dodge",null,null,0,0,1); }
  let hsA=0; if(HITSTOP.att>0){ hsA=Math.min(HITSTOP.att,dt); HITSTOP.att-=hsA; }   // attacker hit-stop: freezes the ATTACK timeline/pose only (Ride movement keeps going)
  if(CP.flag()) cpHeavyInput(dt); if(ATK.floatT>0) ATK.floatT-=dt;
  if(A&&ATK.act===A&&A.pose){ cpStep(A,dt-hsA,dt); }
  else if(A&&ATK.act===A){ A.t+=dt-hsA; const m=A.m, S=A.S; atkCommitStep(A,dt);
    if(m.kind==="sweep"){ if(A.t<.05) ATK.fx.push({type:"arc",x:p.x,z:p.z,y:.9,r:m.r,a0:R.yaw,span:Math.PI*2,t:0,life:.42,c1:S.c1,c2:S.c2,shape:m.fx});
      for(const n of atkTargets()){ const q=n.holder.position, d=Math.hypot(q.x-p.x,q.z-p.z); if(d<m.r) atkHit(A,n,q.x-p.x,q.z-p.z); } if(A.t>.42) ATK.act=null; }
    else if(m.kind==="cone"){ const rep=m.fx==="wing2"?2:1; for(let k=0;k<rep;k++) if(A.t>=k*.18&&!A["s"+k]){ A["s"+k]=1; ATK.fx.push({type:"arc",x:p.x,z:p.z,y:1+k*.25,r:m.r,a0:R.yaw-1.1+(k?2.2:0),span:2.2*(k?-1:1),t:0,life:.32,c1:S.c1,c2:S.c2,shape:m.fx}); }
      if(ATK.lock&&!A.hit.has(ATK.lock)){ const q=ATK.lock.holder.position; R.yaw=Math.atan2(q.x-p.x,q.z-p.z); A.dx=Math.sin(R.yaw); A.dz=Math.cos(R.yaw); }
      for(const n of atkTargets()){ const q=n.holder.position, ddx=q.x-p.x, ddz=q.z-p.z, d=Math.hypot(ddx,ddz); if(d<1.3||d<m.r+.4&&(ddx*A.dx+ddz*A.dz)/(d||1)>-.1) atkHit(A,n,ddx,ddz); } if(A.t>.5){ ATK.act=null; ATK.lock=null; } }
    else if(m.kind==="dash"||m.kind==="slam"){ if(frame%2===0) ATK.fx.push({type:m.fx==="bolt"?"bolt":"beam",a:A.o.clone().setY(.9),b:p.clone().setY(.9),t:0,life:.3,c1:S.c1,c2:S.c2});
      const pp=A.pp||p; for(const n of atkTargets()){ const q=n.holder.position, sx=p.x-pp.x, sz=p.z-pp.z, L2=sx*sx+sz*sz, u=L2>1e-6?Math.max(0,Math.min(1,((q.x-pp.x)*sx+(q.z-pp.z)*sz)/L2)):1, d=Math.hypot(q.x-(pp.x+sx*u),q.z-(pp.z+sz*u)); if(d<m.r+.4) atkHit(A,n,q.x-p.x+A.dx,q.z-p.z+A.dz); }   /* Systems 13:52: swept along this frame's path (low fps tunnelled past the target) */
      A.pp=(A.pp||new THREE.Vector3()).copy(p);
      if(m.kind==="slam"&&A.t>.3&&!A.landed){ atkLand(); } if(A.t>(m.kind==="slam"?.55:.4)) ATK.act=null; }
    else if(m.kind==="chain"){ if(A.t>.45) ATK.act=null; }
    else if(m.kind==="dive"){ if(WALL.air&&!A.landed) diveHome(A,p,dt); /* soft homing dive (locked target, capped turn rate, lead) */ if(WALL.air&&WALL.air.vy<0) for(const n of atkTargets()){ const q=n.holder.position; if(Math.hypot(q.x-p.x,q.z-p.z)<(n===A.tgt?DIVE.airR:1.4)) atkHit(A,n,q.x-p.x+A.dx,q.z-p.z+A.dz); } if(A.landed&&A.t>.1||A.t>2.5){ if(!A.landed) atkLand(); ATK.act=null; } } }
  if(ATK.act&&ATK.act.m.kind==="dive"&&!WALL.air&&!ATK.act.landed&&ATK.act.t>.15) atkLand();
  const chainOpen=CHAIN.n>0&&CHAIN.n<3&&clock-CHAIN.last<=CHAIN.win;   // commit lock held across the whole chain
  if(ATK.commit&&(ATK.act?ATK.act!==ATK.commit.act:!chainOpen)) atkCommitEnd("done");
  // NPC reactions: knockback slide, stagger wobble, recover; NPCs fight back when you crowd them (turf battle)
  for(const n of [...RIDERS.npcs,RIDERS.ikkiNpc].filter(Boolean)){ if(!n.holder) continue; n.off=n.off||new THREE.Vector3(); n.acd=(n.acd||rnd(1,4))-dt;
    if(n.hs>0){ n.hs-=dt; n.ph=(n.ph||0)-dt; n.hsFrames=(n.hsFrames||0)+1; const hp=n.holder.position; if(n._last&&hp.equals(n._last)&&n._ap) hp.sub(n._ap); hp.add(n.off); (n._ap=n._ap||new THREE.Vector3()).copy(n.off); (n._last=n._last||new THREE.Vector3()).copy(hp); continue; }   // target hit-stop: anim phase + knockback/stun frozen
    if(n.kv){ n.off.x+=n.kv.x*dt; n.off.z+=n.kv.y*dt; n.kv.multiplyScalar(Math.max(0,1-dt*5)); if(n.kv.length()<.05) n.kv=null; }
    if(n.stun>0){ n.stun-=dt; const k=n.stun/(n.stunMax||1); n.holder.rotation.z=Math.sin(clock*18)*.35*k; n.holder.rotation.x=-.25*k; if(frame%3===0) ATK.fx.push({type:"stars",x:n.holder.position.x+n.off.x,z:n.holder.position.z+n.off.z,t:0,life:.12,c1:0xfff4a0}); }
    else { n.holder.rotation.z=n.holder.rotation.x=0; n.off.multiplyScalar(Math.max(0,1-dt*.8)); }
    const hp=n.holder.position; if(n._last&&hp.equals(n._last)&&n._ap) hp.sub(n._ap); hp.add(n.off); if(typeof WORLD_GROUND==="function"&&!(n.off.y>.02)){ const g=WORLD_GROUND(hp.x,hp.z,hp.y+.5); if(g&&Math.abs(g.y-hp.y)<1.5) hp.y=g.y; }  /* Systems 08:22: riders.js:135-136 roots NPCs at y 0; asphalt is 0.01 */ n._ap=(n._ap||new THREE.Vector3()).copy(n.off); n._last=(n._last||new THREE.Vector3()).copy(hp);
    if(!ATK.npcPassive&&!window.__npcPassive&&n.holder.visible&&!(n.stun>0)&&n.acd<=0&&State.mode==="ride"){ const q=n.holder.position, d=Math.hypot(q.x-p.x,q.z-p.z); if(d<3.2){ npcAttack(n); n.acd=rnd(4,7); } } }
  if(ATK.pk){ p.x+=ATK.pk.x*dt; p.z+=ATK.pk.y*dt; ATK.pk.multiplyScalar(Math.max(0,1-dt*5)); if(ATK.pk.length()<.1) ATK.pk=null; }
  // rider pose: wall lean (model only, VR rig never rolls), flip, attack spin
  const G=R.group; G.rotation.order="YXZ"; let rz=0, rx=0, ry=R.yaw;
  if(WALL.on){ const f=WALL.on.f, side=f.nx*Math.cos(R.yaw)-f.nz*Math.sin(R.yaw); rz=-side*.42; }
  if(WALL.flipT>=0){ WALL.flipT+=dt; rx=-Math.min(1,WALL.flipT/.75)*Math.PI*2; if(WALL.flipT>=.75||!WALL.air) WALL.flipT=-1; }
  if(ATK.act){ const k=ATK.act.m.kind; if(k==="sweep") ry+=Math.min(1,ATK.act.t/.38)*Math.PI*2; if(k==="slam"||k==="dash") rx=.35; if(k==="dive"&&WALL.air&&WALL.air.vy<0) rx=.6; }
  if(ATK.stun>0){ rz=Math.sin(clock*20)*.25; } G.rotation.set(rx,ry,rz);
  wallFX(dt); }
function npcAttack(n){ const crew=n.g&&n.g.crew||"karasu", S=MOVESETS[crew], m=S.moves[0], q=n.holder.position, p=Ride.group.position; const dx=p.x-q.x, dz=p.z-q.z, d=Math.hypot(dx,dz)||1;
  n.holder.rotation.y=Math.atan2(dx,dz); ATK.fx.push(m.kind==="sweep"?{type:"arc",x:q.x,z:q.z,y:.9,r:m.r,a0:0,span:Math.PI*2,t:0,life:.4,c1:S.c1,c2:S.c2,shape:m.fx}:
    m.kind==="cone"?{type:"arc",x:q.x,z:q.z,y:1,r:m.r,a0:Math.atan2(dx,dz)-1.1,span:2.2,t:0,life:.35,c1:S.c1,c2:S.c2,shape:m.fx}:{type:"beam",a:q.clone().setY(.9),b:p.clone().setY(.9),t:0,life:.3,c1:S.c1,c2:S.c2});
  ATK.lastNpc={crew,move:m.name,d:+d.toFixed(2),wall:!!WALL.on};
  if(d<m.r+.5&&!WALL.on){ ATK.pk=new THREE.Vector2(dx/d*m.knock*.7,dz/d*m.knock*.7); ATK.stun=.5; Ride.speed*=.3; ATK.playerHits=(ATK.playerHits||0)+1; if(CP.flag()){ const pu=CP.player(); if(pu&&pu.setState) CP.state(pu,"react",{kind:"light",dir:new THREE.Vector3(dx/d,0,dz/d)}); } flash("HIT BY "+S.who.toUpperCase(),"#"+new THREE.Color(S.c1).getHexString()); gateHaptic&&gateHaptic(1,120); atkTone("sawtooth",160,60,.2,.1); } }
// ---------- sound ----------
function atkTone(type,f0,f1,dur,vol){ if(typeof gateTone==="function") gateTone(type,f0,f1,dur,vol,3000); }
function atkSfx(m){ const k=m.fx; if(k==="bolt"||k==="boltring"){ atkTone("sawtooth",1800,200,.18,.08); atkTone("square",90,60,.2,.06); } else if(k==="shock"||k==="horn") atkTone("sine",120,40,.3,.3); else atkTone("triangle",900,300,.16,.08); }
// ---------- pooled FX: every ribbon / arc / bolt / ring / spark trail written into one dynamic mesh each frame ----------
const FXB={ maxQ:1800, mesh:null, n:0, pos:null, col:null, cam:new THREE.Vector3() };
function fxInit(){ const g=new THREE.BufferGeometry(); FXB.pos=new Float32Array(FXB.maxQ*6*3); FXB.col=new Float32Array(FXB.maxQ*6*3);
  g.setAttribute("position",new THREE.BufferAttribute(FXB.pos,3).setUsage(THREE.DynamicDrawUsage)); g.setAttribute("color",new THREE.BufferAttribute(FXB.col,3).setUsage(THREE.DynamicDrawUsage));
  const m=new THREE.MeshBasicMaterial({vertexColors:true,side:THREE.DoubleSide,depthWrite:false,fog:false}); m.toneMapped=false;
  FXB.mesh=new THREE.Mesh(g,m); FXB.mesh.frustumCulled=false; FXB.mesh.userData.noMerge=true; FXB.mesh.renderOrder=5; FXB.mesh.name="PooledFX"; scene.add(FXB.mesh); }
const _fa=new THREE.Vector3(), _fb=new THREE.Vector3(), _fs=new THREE.Vector3(), _fc=new THREE.Color();
function fxQuad(a,b,c,d,col){ if(FXB.n>=FXB.maxQ) return; const P=FXB.pos, C=FXB.col, o=FXB.n*18; const v=[a,b,c,a,c,d]; for(let i=0;i<6;i++){ P[o+i*3]=v[i].x; P[o+i*3+1]=v[i].y; P[o+i*3+2]=v[i].z; C[o+i*3]=col.r; C[o+i*3+1]=col.g; C[o+i*3+2]=col.b; } FXB.n++; }
// camera-facing ribbon through pts with width w(i)
function fxRibbon(pts,w,col,flatUp){ for(let i=0;i<pts.length-1;i++){ const a=pts[i], b=pts[i+1]; _fa.subVectors(b,a);
  if(flatUp) _fs.set(-_fa.z,0,_fa.x).normalize(); else { _fb.subVectors(FXB.cam,a); _fs.crossVectors(_fa,_fb).normalize(); }
  const wa=w(i), wb=w(i+1); fxQuad(a.clone().addScaledVector(_fs,wa),a.clone().addScaledVector(_fs,-wa),b.clone().addScaledVector(_fs,-wb),b.clone().addScaledVector(_fs,wb),col); } }
function fxBolt(a,b,seed,width,c1,c2){ const pts=[], n=9; let s=seed; const r=()=>(s=(s*16807)%2147483647)/2147483647-.5;
  for(let i=0;i<=n;i++){ const t=i/n, q=a.clone().lerp(b,t); if(i>0&&i<n){ q.x+=r()*.7; q.y+=r()*.6; q.z+=r()*.7; } pts.push(q); }
  fxRibbon(pts,()=>width*1.9,_fc.setHex(c2)); _fb.subVectors(FXB.cam,a).normalize().multiplyScalar(.03); fxRibbon(pts.map(q=>q.clone().add(_fb)),()=>width*.7,_fc.setHex(c1).lerp(_WHITE,.45)); } // white-hot core, neon falloff
const _WHITE=new THREE.Color(1,1,1);
function fxArc(F,k){ const pts=[], n=22, prog=Math.min(1,k*2.2), fade=1-Math.max(0,(k-.45)/.55), shp=F.shape;
  for(let i=0;i<=n;i++){ const a=F.a0+F.span*prog*(i/n); pts.push(new THREE.Vector3(F.x+Math.sin(a)*F.r*.85,F.y+(shp==="spiral"?i/n*1.2:Math.sin(i/n*Math.PI)*.15),F.z+Math.cos(a)*F.r*.85)); }
  const w=i=>(.08+.22*Math.sin(i/n*Math.PI))*fade; fxRibbon(pts,i=>w(i)*1.5,_fc.setHex(F.c2),true); fxRibbon(pts.map(q=>q.clone().setY(q.y+.02)),w,_fc.setHex(F.c1),true);
  if(shp==="wing"||shp==="wing2"||shp==="feather"||shp==="leaf"||shp==="cross"||shp==="fang"||shp==="rivet") for(let i=2;i<=n;i+=2){ const a=F.a0+F.span*prog*(i/n), ox=Math.sin(a), oz=Math.cos(a), r0=F.r*.85;
    const L=(shp==="wing"||shp==="wing2"?.9:.5)*fade, base=new THREE.Vector3(F.x+ox*r0,F.y,F.z+oz*r0), tip=base.clone().add(new THREE.Vector3(ox*L+Math.sin(a+1.4)*L*.5,.25*L,oz*L+Math.cos(a+1.4)*L*.5));
    const s=new THREE.Vector3(-oz,0,ox).multiplyScalar(shp==="cross"?.14*fade:.07*fade); fxQuad(base.clone().add(s),base.clone().sub(s),tip,tip.clone().addScaledVector(s,.3),_fc.setHex(i%4?F.c1:(F.c1===0x00e5ff?F.c2:0xffffff))); } }
function fxRing(F,k){ const pts=[], n=28, r=F.r*(.25+k), fade=1-k; for(let i=0;i<=n;i++){ const a=i/n*Math.PI*2; pts.push(new THREE.Vector3(F.x+Math.sin(a)*r,.08+(F.shape==="shock"?Math.abs(Math.sin(a*6))*.25*fade:0),F.z+Math.cos(a)*r)); }
  fxRibbon(pts,()=>.28*fade,_fc.setHex(F.c2),true); fxRibbon(pts.map(q=>q.clone().setY(q.y+.02)),()=>.13*fade,_fc.setHex(F.c1),true);
  if(F.shape==="boltring") for(let i=0;i<6;i++){ const a=i/6*Math.PI*2+k; fxBolt(new THREE.Vector3(F.x,.2,F.z),new THREE.Vector3(F.x+Math.sin(a)*r,.3,F.z+Math.cos(a)*r),(i+1)*977+((clock*20)|0),.05*fade+.01,F.c1,F.c2); } }
function wallFX(dt){ if(!FXB.mesh) fxInit(); FXB.n=0; (renderer.xr.isPresenting?renderer.xr.getCamera(camera):camera).getWorldPosition(FXB.cam);
  // wheel streaks while on a wall / airborne / dashing
  const R=Ride, p=R.group.position, act=WALL.on||WALL.air||(ATK.act&&ATK.act.m.kind==="dash")||DASH.t>0; const tr=WALL.trail;
  if(act){ const sx=Math.cos(R.yaw)*.16, sz=-Math.sin(R.yaw)*.16; tr.unshift([p.x+sx,p.y+.06,p.z+sz,p.x-sx,p.y+.06,p.z-sz]); } else tr.unshift(null); if(tr.length>22) tr.length=22;
  for(const side of [0,3]){ let run=[]; const flush=()=>{ if(run.length>1){ const L=run.length; fxRibbon(run,i=>.05*(1-i/L),_fc.setHex(atkSet().c1)); } run=[]; };
    for(const e of tr){ if(!e){ flush(); continue; } run.push(new THREE.Vector3(e[side],e[side+1],e[side+2])); } flush(); }
  for(let i=ATK.fx.length-1;i>=0;i--){ const F=ATK.fx[i]; F.t+=dt; const k=F.t/F.life; if(k>=1){ ATK.fx.splice(i,1); continue; }
    if(F.type==="bolt") fxBolt(F.a,F.b,7+((F.t*25)|0)*131+i,.07*(1-k)+.015,F.c1,F.c2);
    else if(F.type==="beam") fxRibbon([F.a,F.a.clone().lerp(F.b,.5).setY(F.a.y+.4),F.b],()=>.12*(1-k),_fc.setHex(F.c1));
    else if(F.type==="arc") fxArc(F,k);
    else if(F.type==="ring") fxRing(F,k);
    else if(F.type==="burst"){ for(let j=0;j<8;j++){ const a=j/8*Math.PI*2, L=.4+k*1.2; const c=new THREE.Vector3(F.x,F.y,F.z); fxRibbon([c.clone().add(new THREE.Vector3(Math.sin(a)*L*.4,Math.cos(a)*L*.4,0)),c.clone().add(new THREE.Vector3(Math.sin(a)*L,Math.cos(a)*L,0))],()=>.06*(1-k),_fc.setHex(j%2?F.c1:(F.c1===0x00e5ff?0x9ff6ff:0xffffff))); } }
    else if(F.type==="stars"){ for(let j=0;j<4;j++){ const a=clock*5+j*Math.PI/2, c=new THREE.Vector3(F.x+Math.sin(a)*.35,2.05,F.z+Math.cos(a)*.35); fxRibbon([c,c.clone().setY(c.y+.12)],()=>.06,_fc.setHex(F.c1)); } } }
  const g=FXB.mesh.geometry; g.setDrawRange(0,FXB.n*6); g.attributes.position.needsUpdate=g.attributes.color.needsUpdate=true; FXB.mesh.visible=FXB.n>0; }
// ---------- HUD ----------
function atkHUD(){ let d=$("atkhud"); if(!d){ const st=document.createElement("style"); st.textContent=`#atkhud{position:fixed;bottom:52px;left:130px;display:flex;gap:6px;font:bold 10px Arial;color:#fff;letter-spacing:1px;z-index:5}
  #atkhud div{position:relative;width:118px;padding:4px 6px;background:rgba(10,10,10,.8);border-left:3px solid var(--c);overflow:hidden} #atkhud i{position:absolute;left:0;bottom:0;height:3px;background:var(--c)} #atkhud s{text-decoration:none;color:#aaa;font-size:9px;display:block}
  #trk{position:fixed;bottom:22px;left:318px;font:bold 12px Arial;color:#fff;letter-spacing:2px;z-index:5}`; document.head.appendChild(st);
    d=document.createElement("div"); d.id="atkhud"; d.className="hud"; document.body.appendChild(d); const t=document.createElement("div"); t.id="trk"; t.className="hud"; document.body.appendChild(t); }
  const S=atkSet(), keys=["J","K","L"]; d.style.setProperty("--c",S.css); d.innerHTML=S.moves.map((m,i)=>`<div><s>${keys[i]} · ${["LIGHT","HEAVY","SPECIAL"][i]}</s>${m.name}<i style="width:${(100*(1-ATK.cd[i]/m.cd)).toFixed(0)}%"></i></div>`).join("");
  const on=State.mode==="ride"&&!$("stats").classList.contains("hidden"); d.style.display=$("trk").style.display=on?"flex":"none"; $("trk").textContent="TRICKS "+(Stats.tricks||0); }
function wallAtkPre(dt){ WALL.I=wallInput(); }
function wallAtkPost(dt){ try{ atkUpdate(dt); if(frame%6===0) atkHUD(); }catch(e){ if(!window.__atkErr) console.warn("atk",e); window.__atkErr=e; } }

// ---------- ATTACK LOCK-COMMIT (Oliver via Ani 01:41, Rydah Systems): "make the auto lock / aim assist target the attacked object or player after the attack is started".
// On attack start commit to ONE target: the LT/Q lock (target.js) > the melee soft-lock rider > best candidate in the forward cone by target.js's tgtPick rule
// (angle first in 1-degree bins, then distance; allies skipped; spots must face you). Candidates: riders/NPCs (atkTargets), active cops (HEAT.cops), taggable spots.
// Held for the whole attack: keep turning (ground) / homing (dive) at it. No switching. Breaks: attack ends, out of range (> COMMIT.range), line of sight blocked
// (collider box between), B / KeyB press, or a left-stick flick |dStick| > COMMIT.flick within COMMIT.flickT s. ATK.commit={target,kind,since,act,...}; ATK.commitLog keeps the last 8.
// Marker: target.js's DOM lock reticle (#retLock) projected onto the target -> 0 extra draw calls.
const COMMIT={cone:40*Math.PI/180, range:14, flick:.8, flickT:.15, turn:12}; window.COMMIT=COMMIT; ATK.commitLog=[]; ATK.stkH=[];
function cmPos(c){ const r=c.ref; if(c.kind==="enemy"&&r.holder) return {x:r.holder.position.x,z:r.holder.position.z,y:1.2}; if(c.kind==="cop") return {x:r.x,z:r.z,y:1.2}; return {x:c.x,z:c.z,y:c.y||2.4}; }
function cmCands(){ let L=[]; try{ L=typeof tgtCands==="function"?tgtCands():[]; }catch(e){ L=[]; } if(!L.length) for(const n of atkTargets()){ const q=n.holder.position; L.push({kind:"enemy",ref:n,x:q.x,z:q.z,y:1.2}); }
  try{ const H=window.HEAT; if(H&&Array.isArray(H.cops)){ const p=Ride.group.position; for(const c of H.cops) if(c&&c.active&&Math.hypot(c.x-p.x,c.z-p.z)<COMMIT.range) L.push({kind:"cop",ref:c,x:c.x,z:c.z,y:1.2}); } }catch(e){}
  return L; }
function cmPick(yaw){ const p=Ride.group.position; let best=null, bs=1e9; for(const c of cmCands()){ const dx=c.x-p.x, dz=c.z-p.z, d=Math.hypot(dx,dz); if(d>COMMIT.range||d<.3) continue;
    let a=Math.atan2(dx,dz)-yaw; a=Math.abs(Math.atan2(Math.sin(a),Math.cos(a))); if(a>COMMIT.cone) continue; const sc=Math.round(a/(Math.PI/180))*1000+d; if(sc<bs){ bs=sc; best=c; } } return best; }  // = tgtPick's spacing rule
function cmLOS(q){ const p=Ride.group.position, dx=q.x-p.x, dz=q.z-p.z, L=Math.hypot(dx,dz); if(L<1) return true; const ux=dx/L, uz=dz/L;
  for(const c of colliders){ if(c.off) continue; if(Math.max(c.maxX-c.minX,c.maxZ-c.minZ)>200) continue; const t1x=(c.minX-p.x)/ux, t2x=(c.maxX-p.x)/ux, t1z=(c.minZ-p.z)/uz, t2z=(c.maxZ-p.z)/uz;
    const t0=Math.max(Math.min(t1x,t2x),Math.min(t1z,t2z)), t1=Math.min(Math.max(t1x,t2x),Math.max(t1z,t2z)); if(t1>=t0&&t0>.5&&t0<L-.6) return false; } return true; }
function atkCommitStart(A){ const R=Ride, p=R.group.position; let c=null, src="cone";
  try{ if(typeof TGT!=="undefined"&&TGT.aiming&&TGT.lock){ c=TGT.lock; src="aim"; } }catch(e){}
  if(!c&&ATK._soft){ const q=ATK._soft.holder.position; c={kind:"enemy",ref:ATK._soft,x:q.x,z:q.z,y:1.2}; src="soft"; }
  if(!c){ c=cmPick(R.yaw); }
  ATK._soft=null; if(!c){ ATK.commit=null; return null; }
  if(c.kind==="spot"&&!c.ref.holder) c.shim={holder:{position:new THREE.Vector3(c.x,0,c.z),visible:true}};
  if(c.kind==="cop") c.shim={holder:{position:new THREE.Vector3(c.ref.x,0,c.ref.z),visible:true}};
  ATK.commit={target:c, ref:c.ref, kind:c.kind, since:clock, act:A, move:A.m.name, src, turns:0, broke:null};
  if(A.m.kind==="dive"){ A.tgt=c.kind==="enemy"?c.ref:c.shim; A.tq=A.tgt.holder.position.clone(); A.tv={x:0,z:0}; }   // dive homing follows the committed target only (tq/tv = diveHome's velocity estimate seed)
  if(A.m.kind==="cone"&&c.kind==="enemy") ATK.lock=c.ref;
  const q=cmPos(c); if(A.m.kind!=="dive"||!WALL.air){ R.yaw=Math.atan2(q.x-p.x,q.z-p.z); A.dx=Math.sin(R.yaw); A.dz=Math.cos(R.yaw); }
  return ATK.commit; }
function atkCommitEnd(why){ const C=ATK.commit; if(!C) return; C.broke=why; C.until=clock; ATK.commitLog.push({kind:C.kind,move:C.move,src:C.src,since:+C.since.toFixed(2),until:+clock.toFixed(2),why,turns:C.turns,id:C.ref&&C.ref.g?C.ref.g.crew:(C.ref&&C.ref.id)||null});
  if(ATK.commitLog.length>8) ATK.commitLog.shift(); const A=C.act; if(A&&why!=="done"){ A.noHome=true; if(ATK.lock===C.ref) ATK.lock=null; } ATK.commit=null; }
function cmBreakInput(){ let brk=!!(WIN.k&&WIN.k.KeyB&&!ATK._kbB); ATK._kbB=!!(WIN.k&&WIN.k.KeyB); let flick=false;
  const P=(typeof PAD!=="undefined")&&PAD.R;   // pad.js shared read (SR_PAD), no direct pad API reads here (patch_gamepad lint)
  if(P&&P.gp){ const b1=!!P.b(1); if(b1&&!ATK._gpB) brk=true; ATK._gpB=b1;
    const x=(P.ls&&P.ls[0])||0, y=(P.ls&&P.ls[1])||0, H=ATK.stkH; H.push([clock,x,y]); while(H.length&&clock-H[0][0]>COMMIT.flickT) H.shift();
    for(const h of H) if(Math.hypot(x-h[1],y-h[2])>COMMIT.flick){ flick=true; break; } }
  return brk?"B":flick?"flick":null; }
function atkCommitStep(A,dt){ const why=cmBreakInput(), C=ATK.commit; if(!C||C.act!==A) return; if(why){ atkCommitEnd(why); ATK.stkH.length=0; return; }
  const c=C.target, r=C.ref; if(c.kind==="enemy"&&!(r.holder&&r.holder.visible)) return atkCommitEnd("gone"); if(c.kind==="cop"&&!r.active) return atkCommitEnd("gone");
  const q=cmPos(c); if(c.shim) c.shim.holder.position.set(q.x,0,q.z); c.x=q.x; c.z=q.z; const R=Ride, p=R.group.position, d=Math.hypot(q.x-p.x,q.z-p.z);
  if(d>COMMIT.range) return atkCommitEnd("range"); if(!cmLOS(q)) return atkCommitEnd("los");
  if(A.m.kind==="dive"&&!A.tgt){ A.tgt=c.kind==="enemy"?r:c.shim; A.tq=A.tgt.holder.position.clone(); A.tv={x:0,z:0}; }   // diveHome keeps homing at it (no re-pick)
  else if(d>.25){ const want=Math.atan2(q.x-p.x,q.z-p.z); let da=want-R.yaw; da=Math.atan2(Math.sin(da),Math.cos(da)); const st=COMMIT.turn*dt; R.yaw+=Math.abs(da)<=st?da:Math.sign(da)*st; A.dx=Math.sin(R.yaw); A.dz=Math.cos(R.yaw); C.turns++; }
  if(c.kind!=="enemy"&&d<A.m.r&&!C.objHit){ C.objHit=true; ATK.objHits=(ATK.objHits||0)+1; r.atkHitN=(r.atkHitN||0)+1; } }
// marker: reuse target.js's DOM reticle, projected on the committed target (runs after tgtUpdate, which would otherwise hide it)
const _cmV=new THREE.Vector3();
function atkCommitMarker(){ const u=typeof TGT!=="undefined"&&TGT.ui; if(!u) return; const C=ATK.commit;
  if(!C){ if(ATK._mkOn){ u.style.left=u.style.top="50%"; ATK._mkOn=false; } ATK.markerShown=false; return; }
  const q=cmPos(C.target); _cmV.set(q.x,C.kind==="enemy"?1.4:q.y,q.z).project(camera); const on=_cmV.z<1&&Math.abs(_cmV.x)<1.2&&Math.abs(_cmV.y)<1.2;
  u.style.display=on?"block":u.style.display; u.style.left=((_cmV.x*.5+.5)*100).toFixed(2)+"%"; u.style.top=((-_cmV.y*.5+.5)*100).toFixed(2)+"%"; ATK._mkOn=true;
  const L=u.querySelector("#retLock"), D=u.querySelector("#retDot"); if(L&&on){ L.style.display=""; if(D) D.style.display="none"; } ATK.markerShown=on; }
(function cmHook(){ if(typeof tgtTick==="function"&&!tgtTick.__cm){ const o=tgtTick; tgtTick=function(dt){ o(dt); try{ atkCommitMarker(); }catch(e){} }; tgtTick.__cm=1; window.tgtTick=tgtTick; } else if(!(typeof tgtTick==="function")) setTimeout(cmHook,500); })();
window.atkCommitStart=atkCommitStart; window.atkCommitEnd=atkCommitEnd; window.cmPick=cmPick;
