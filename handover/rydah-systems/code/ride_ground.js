// ===== RIDE_GROUND (Rydah Systems, ride_ground.js via patch_ride_ground.py) =====
// Rider vertical position follows window.WORLD_GROUND(x,z,yHint) (Palma Builder, ground.js).
// Hooks from OUTSIDE (no core/ikki_skate edits), installed right after ground.js so they sit INSIDE grapple/aim/pad wrappers:
//   wallStep  : runs the existing wall-ride/air physics in a ground-relative frame (y -= ground, call, y += ground), so its
//               own "land at y<=0" / wall-stick height logic lands on the real surface. Post: land on higher surfaces, fall-through.
//   updateRide: after the core move (which lerps y to 0), replace the y with the ground follow (step-up <=0.35 m, small
//               step-downs stay grounded, larger drops -> WALL.air), slope accel/drag, surface friction, water/void respawn.
// Grinds (GRIND.on / internal rails), wall rides and grapple (GRAP.act/deck/airDeck) keep owning y.
// ?flatground=1 -> nothing installed (old y=0 behaviour). WORLD_GROUND null/missing -> ground 0 (old behaviour).
// Cost: <=2 WORLD_GROUND calls per frame (pre at old xz, post at new xz), 0 draws.
(function(){
  const FLAT=/[?&]flatground=1\b/.test(location.search);
  const FRIC={asphalt:1,concrete:1,wood:.97,metal:1.02,grass:.8,sand:.6};
  const STEP_UP=.35, STEP_DOWN=.4, SINK=.5, VOID_Y=-10, WATER_Y=-2.0, GRAV=13;
  const S={active:false, lastFrame:-1, surf:"concrete", groundY:0, normal:{x:0,y:1,z:0}, lastSafe:null, respawns:0, calls:0, frame:0, lastReason:""};
  const RG={}; for(const k of ["active","surf","groundY","normal","lastSafe","respawns","calls","lastReason","airT"]) Object.defineProperty(RG,k,{get:()=>k==="normal"?{...S.normal}:(k==="lastSafe"&&S.lastSafe?{...S.lastSafe}:S[k]),enumerable:true});
  S.airT=0;
  RG.friction=FRIC; RG.flat=FLAT; RG.version="1.2";
  window.RIDE_GROUND=RG;
  let preG=null, preX=0, preZ=0, safeA=null, safeB=null, safeT=0;
  function q(x,z,yh){ S.calls++; let g=null; try{ const W=window.WORLD_GROUND; if(typeof W==="function") g=W(x,z,yh); }catch(e){ if(!window.__rgErr) console.warn("ride_ground",e); window.__rgErr=e; g=null; }
    if(!g||!isFinite(g.y)) return {y:0,nx:0,ny:1,nz:0,surf:"concrete",none:true};
    return {y:g.y,nx:g.nx||0,ny:g.ny==null?1:g.ny,nz:g.nz||0,surf:FRIC[g.surf]!==undefined||g.surf==="water"?g.surf:"concrete"}; }
  function pub(g){ S.groundY=g.y; S.surf=g.surf; S.normal={x:g.nx,y:g.ny,z:g.nz}; }
  function others(){ return (typeof GRIND!=="undefined"&&GRIND.on)||(typeof GRAP!=="undefined"&&(GRAP.act||GRAP.deck||GRAP.airDeck)); }
  // ---- RIDER_RESET(reason): respawn at lastSafe, zero velocity, cancel grind / wall ride / grapple / air / attack ----
  function reset(why){ const R=Ride; if(!R||!R.group) return false; const p=R.group.position, s=safeA||safeB||{x:0,y:0,z:16};
    try{ if(typeof WALL!=="undefined"){ WALL.air=null; WALL.on=null; WALL.flipT=-1; WALL.chain=0; WALL.lastWall=null; } }catch(e){}
    try{ if(typeof GRIND!=="undefined"){ GRIND.on=null; GRIND.cd=Math.max(GRIND.cd||0,.5); GRIND.prevP=null; GRIND.ignore=null; } }catch(e){}
    try{ if(typeof GRAP!=="undefined"){ GRAP.act=null; GRAP.deck=null; GRAP.airDeck=false; if(GRAP.line) GRAP.line.visible=false; } }catch(e){}
    try{ if(typeof ATK!=="undefined"){ ATK.act=null; ATK.stun=0; } }catch(e){}
    try{ if(typeof DASH!=="undefined") DASH.t=0; }catch(e){}
    p.x=s.x; p.z=s.z; R.y=p.y=FLAT?0:s.y; R.speed=0; R.throttle=0; R.boost=0; R.grinding=false; R.group.rotation.x=0; R.group.rotation.z=0;
    S.airT=0; safeT=0; S.respawns++; S.lastReason=String(why||"script"); S.lastFrame=(typeof frame!=="undefined"?frame:0);
    try{ if(typeof flash==="function") flash(why==="menu"?"RIDER RESET":"BAIL! RESPAWN"); }catch(e){}
    return true; }
function swallow(){ if(S.swallow===(typeof frame!=="undefined"?frame:-9)&&typeof WALL!=="undefined"&&WALL.I){ WALL.I.jumpP=false; WALL.I.jump=false; } } // the A that picked RESET RIDER must not also hop
  window.RIDER_RESET=reset; RG.reset=reset;
  // robust install: each step in its own try/catch; if its target isn't there yet, retry every 250 ms for up to 10 s, then warn
  RG.installed={};
  function install(name,ready,fn){ let n=0; const go=()=>{ let ok=false; try{ ok=ready(); }catch(e){ ok=false; }
      if(ok){ try{ fn(); RG.installed[name]=true; }catch(e){ RG.installed[name]="error"; console.warn("ride_ground: install "+name+" failed",e); } return; }
      if(++n>40){ RG.installed[name]=false; console.warn("ride_ground: "+name+" not found after 10 s, not installed"); return; } setTimeout(go,250); };
    go(); }
  const isFn=n=>()=>typeof window[n]==="function"||(n==="wallStep"&&typeof wallStep==="function")||(n==="updateRide"&&typeof updateRide==="function");
  const respawn=reset;
  function safe(dt,g){ const p=Ride.group.position; if(g.surf==="water"||g.none) return; safeT+=dt;
    if(!safeB) safeB={x:p.x,y:g.y,z:p.z}; if(safeT>=.5){ safeT=0; safeA=safeB; safeB={x:p.x,y:g.y,z:p.z}; } S.lastSafe=safeA||safeB; }
  // air timer: >2 s airborne with no ground below (no data / water; flat mode: off the land) -> reset
  function airTick(dt,noGround){ if(typeof WALL!=="undefined"&&WALL.air&&!others()){ S.airT+=dt; if(S.airT>2&&noGround) { reset("air"); return true; } } else S.airT=0; return false; }
  // ---- pause menu: 'RESET RIDER' (after the main script has defined SCREENS / menuInput) ----
  install("menu",()=>typeof SCREENS!=="undefined"&&!!SCREENS.pause&&typeof menuInput==="function",function(){ const P=SCREENS.pause, o=P.opts;
    P.opts=()=>{ const a=o().slice(); if(a.indexOf("RESET RIDER")<0){ const i=a.indexOf("RESUME"); a.splice(i<0?0:i+1,0,"RESET RIDER"); } return a; }; P.h=Math.max(P.h,.95);
    const _mi=menuInput; menuInput=function(){ if(UI.screen==="pause"&&Input.pSelect&&SCREENS.pause.opts()[UI.sel]==="RESET RIDER"){ reset("menu"); resume(); S.swallow=(typeof frame!=="undefined"?frame:0); return; } return _mi(); };
    RG.menu=true; });
  if(FLAT){ // old y=0 physics untouched; only track lastSafe + fall-off for RIDER_RESET
    install("wallStep",isFn("wallStep"),function(){ const _ws=wallStep; wallStep=function(dt){ swallow(); const r=_ws(dt); try{ const p=Ride.group.position; airTick(dt,typeof onLand==="function"&&!onLand(p.x,p.z)); if(Ride.y<VOID_Y) reset("void"); }catch(e){} return r; }; });
    install("updateRide",isFn("updateRide"),function(){ const _ur=updateRide; updateRide=function(dt){ const r=_ur(dt); try{ if(!others()&&!Ride.grinding&&!(typeof WALL!=="undefined"&&(WALL.air||WALL.on))) safe(dt,{y:0,surf:"concrete"}); S.airT=0; }catch(e){} return r; }; });
    return; }
  function align(g){ const R=Ride; if(g.ny>.9995){ return; } // flat: leave rotation exactly as the core sets it
    const s=Math.sin(R.yaw), c=Math.cos(R.yaw), along=g.nx*s+g.nz*c, side=g.nx*c-g.nz*s, ny=Math.max(.2,g.ny);
    R.group.rotation.order="YXZ"; R.group.rotation.x=Math.atan2(along,ny); R.group.rotation.z=-Math.atan2(side,ny); }
  // ---- wallStep: ground-relative frame ----
  install("wallStep",isFn("wallStep"),function(){ const _ws=wallStep; wallStep=function(dt){
    swallow(); if(others()) return _ws(dt);
    const R=Ride, p=R.group.position; S.active=true;
    if(R.y<VOID_Y){ respawn("void"); return true; }
    const g0=q(p.x,p.z,R.y), off=g0.y; preG=g0; preX=p.x; preZ=p.z; const A0=WALL.air, W0=WALL.on;
    R.y-=off; p.y-=off; if(A0) A0.y-=off; if(W0) W0.y-=off;
    let r; try{ r=_ws(dt); } finally { R.y+=off; p.y+=off; if(WALL.air) WALL.air.y+=off; if(WALL.on) WALL.on.y+=off; }
    if(!r) return r;
    if(others()) return r;
    const g1=q(p.x,p.z,R.y); pub(g1); const A=WALL.air;
    if(A){ if(A.vy<=0&&R.y<g1.y){ A.y=g1.y; R.y=p.y=g1.y; } // crossed onto a higher surface: next step lands (A.y rel 0)
      if(A.vy<=0&&R.y<g1.y-SINK){ R.y=p.y=A.y=g1.y; } }
    else if(!WALL.on){ // just landed
      R.y=p.y=g1.y; if(g1.surf==="water") respawn("water"); }
    if(R.y<VOID_Y) respawn("void"); else if(!WALL.on&&g1.surf==="water"&&R.y<=g1.y+.05) respawn("water");
    else airTick(dt,g1.none||g1.surf==="water");
    return r; }; });
  // ---- updateRide: ground follow ----
  install("updateRide",isFn("updateRide"),function(){ const _ur=updateRide; updateRide=function(dt){
    if(others()){ return _ur(dt); }
    const R=Ride, p=R.group.position; S.active=true; S.frame++;
    const ox=p.x, oz=p.z, y0=R.y;
    const r=_ur(dt); const pg=preG; preG=null;
    if(others()) return r;
    if(y0<VOID_Y){ respawn("void"); return r; }
    if(R.grinding){ return r; } // core rail grind owns y (absolute rail height)
    if(typeof WALL!=="undefined"&&(WALL.air||WALL.on)) return r;
    let g=q(p.x,p.z,y0); const d=g.y-y0;
    if(d>STEP_UP){ // wall/ledge taller than a curb: block like a collider
      p.x=ox; p.z=oz; R.speed*=.6; g=(pg&&preX===ox&&preZ===oz)?pg:q(ox,oz,y0); }
    pub(g);
    const dd=g.y-y0;
    if(dd<-STEP_DOWN){ // edge: go airborne with the existing air physics
      R.y=p.y=y0; WALL.air={vx:Math.sin(R.yaw)*R.speed,vz:Math.cos(R.yaw)*R.speed,vy:0,y:y0,flip:false,t:0};
    } else {
      const y=Math.abs(dd)<.15?g.y:THREE.MathUtils.lerp(y0,g.y,.45); R.y=p.y=(y<g.y-SINK?g.y:y);
      // slope: gravity along velocity (downhill accel / uphill drag); 0 on flat normals
      const s=Math.sin(R.yaw), c=Math.cos(R.yaw), along=g.nx*s+g.nz*c; if(along) R.speed=Math.max(0,R.speed+9.8*along*dt);
      const m=FRIC[g.surf]!==undefined?FRIC[g.surf]:1; if(m!==1) R.speed=Math.max(0,R.speed*(1-(1-m)*2.5*dt));
      align(g);
      S.airT=0; if(g.surf==="water"||R.y<WATER_Y) respawn("water"); else safe(dt,g); }
    if(R.y<VOID_Y) respawn("void");
    return r; }; });
})();
