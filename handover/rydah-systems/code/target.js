// ===== GTA V-style targeting (hold LT, or Q on keyboard): over-the-shoulder zoom, centre reticle, soft lock-on, free aim, aimed attacks + precise spray.
const TGT={ cone:15*Math.PI/180, minD:.75, stick:5*Math.PI/180, aiming:false, k:0, lock:null, spot:null, aim:null, yawOff:0, pitch:0, flickArmed:true, saved:null, ui:null, mk:null, prev:null, range:15, sprayR:4.6, key:false };
function tgtBuild(){ const u=document.createElement("div"); u.id="reticle"; u.className="hud"; u.style.cssText="position:fixed;left:50%;top:50%;width:44px;height:44px;margin:-22px 0 0 -22px;pointer-events:none;display:none;z-index:16";
  u.innerHTML='<svg viewBox="-22 -22 44 44" width="44" height="44"><g id="retDot"><circle r="3.2" fill="#fff" stroke="#000" stroke-width="1.2"/></g><g id="retLock" style="display:none" fill="none" stroke="#FF3344" stroke-width="3"><circle r="13"/><path d="M0 -20V-12M0 12V20M-20 0H-12M12 0H20"/><circle r="2.5" fill="#FF3344"/></g><g id="retSpray" style="display:none"><rect x="-6" y="-6" width="12" height="18" rx="3" fill="#FF2BD6" stroke="#000" stroke-width="1.4"/><rect x="-3" y="-11" width="6" height="5" fill="#FF2BD6" stroke="#000" stroke-width="1.2"/><circle cx="10" cy="-12" r="2" fill="#FF2BD6"/><circle cx="14" cy="-8" r="1.6" fill="#FF2BD6"/><circle cx="14" cy="-15" r="1.4" fill="#FF2BD6"/></g></svg>';
  document.body.appendChild(u); TGT.ui=u;
  const mk=new THREE.Mesh(new THREE.RingGeometry(.55,.72,24),new THREE.MeshBasicMaterial({color:0xFF3344,transparent:true,opacity:.9,depthTest:false,side:THREE.DoubleSide,fog:false})); mk.renderOrder=998; mk.visible=false; scene.add(mk); TGT.mk=mk;
  const c=document.createElement("canvas"); c.width=c.height=128; const x=c.getContext("2d"); for(let i=0;i<260;i++){ const a=Math.random()*7, r=Math.pow(Math.random(),.6)*56; x.fillStyle="rgba(255,255,255,"+(.25+Math.random()*.6).toFixed(2)+")"; x.beginPath(); x.arc(64+Math.cos(a)*r,64+Math.sin(a)*r*.6,1+Math.random()*2.4,0,7); x.fill(); }
  x.strokeStyle="rgba(255,255,255,.9)"; x.setLineDash([6,5]); x.lineWidth=3; x.strokeRect(6,22,116,84);
  const pv=new THREE.Mesh(new THREE.PlaneGeometry(2.4,1.2),new THREE.MeshBasicMaterial({map:new THREE.CanvasTexture(c),transparent:true,opacity:.85,depthWrite:false,color:0xFF2BD6,fog:false,side:THREE.DoubleSide,polygonOffset:true,polygonOffsetFactor:-4})); pv.visible=false; scene.add(pv); TGT.pv=pv; }
function tgtAlly(n){ try{ const me=TURF.crews[TURF.me]; const c=n.g&&n.g.crew; return !!(me&&c&&c===me.id); }catch(e){ return false; } }
function tgtCrewCol(n){ try{ return (n.g&&n.g.color)||"#FF3344"; }catch(e){ return "#FF3344"; } }
function tgtCands(){ const p=Ride.group.position, L=[]; try{ for(const n of atkTargets()){ if(tgtAlly(n)) continue; const q=n.holder.position; L.push({kind:"enemy",ref:n,x:q.x,z:q.z,y:1.2,col:tgtCrewCol(n)}); } }catch(e){}
  if(typeof TURF!=="undefined"&&TURF.ready) for(const s of TURF.spots){ if(s.owner===TURF.me) continue; if(Math.abs(s.x-p.x)>TGT.range||Math.abs(s.z-p.z)>TGT.range) continue; if((p.x-s.x)*s.nx+(p.z-s.z)*s.nz<0) continue; L.push({kind:"spot",ref:s,x:s.x,z:s.z,y:2.4,col:(TURF.crews[TURF.me]||{}).css||"#FF2BD6"}); }
  return L.filter(c=>{ const d=Math.hypot(c.x-p.x,c.z-p.z); return d<TGT.range&&d>=TGT.minD; }); }
function tgtDir(){ return Ride.yaw+TGT.yawOff; }
function tgtPick(dirYaw,cone,excl,side){ const p=Ride.group.position; let best=null, bs=1e9; for(const c of tgtCands()){ if(excl&&c.ref===excl.ref) continue; const dx=c.x-p.x, dz=c.z-p.z, d=Math.hypot(dx,dz), a=angDiff(Math.atan2(dx,dz),dirYaw);
    if(side){ if(Math.sign(-a)!==side||Math.abs(a)>1.6) continue; } else if(Math.abs(a)>cone) continue; const sc=Math.round(Math.abs(a)/(Math.PI/180))*1000+d; if(sc<bs){ bs=sc; best=c; } } return best; }
function tgtAcquire(dirYaw){ const p=Ride.group.position, cur=TGT.lock, n=tgtPick(dirYaw,TGT.cone);
  if(cur&&cur.kind==="enemy"){ const q=cur.ref.holder.position, d=Math.hypot(q.x-p.x,q.z-p.z), a=Math.abs(angDiff(Math.atan2(q.x-p.x,q.z-p.z),dirYaw));
    if(d>=TGT.minD&&d<TGT.range+3&&a<TGT.cone*1.6&&!tgtAlly(cur.ref)){ if(!n||n.ref===cur.ref) return cur; const an=Math.abs(angDiff(Math.atan2(n.x-p.x,n.z-p.z),dirYaw)); return an<a-TGT.stick?n:cur; } }
  return n&&n.kind==="enemy"?n:null; }
// free aim: 2D ray vs collider boxes -> wall hit point
function tgtRay(yaw){ const p=Ride.group.position, dx=Math.sin(yaw), dz=Math.cos(yaw); let tb=40, n=null; for(const c of colliders){ if(c.off) continue;
    const tx1=(c.minX-p.x)/dx, tx2=(c.maxX-p.x)/dx, tz1=(c.minZ-p.z)/dz, tz2=(c.maxZ-p.z)/dz, t0=Math.max(Math.min(tx1,tx2),Math.min(tz1,tz2)), t1=Math.min(Math.max(tx1,tx2),Math.max(tz1,tz2));
    if(t1>=t0&&t0>.3&&t0<tb){ tb=t0; n=(Math.min(tx1,tx2)>Math.min(tz1,tz2))?[-Math.sign(dx),0]:[0,-Math.sign(dz)]; } }
  return {x:p.x+dx*tb,z:p.z+dz*tb,y:1.5,hit:!!n,n}; }
function tgtUpdate(dt,R){ const on=State.mode==="ride"&&!renderer.xr.isPresenting&&!(window.PHONE&&PHONE.up)&&!(window.MAP&&MAP.open)&&!(window.GRAP&&GRAP.act)&&((PAD.lt||0)>0||TGT.key);
  if(!TGT.ui) tgtBuild(); if(on&&!TGT.aiming){ TGT.yawOff=0; TGT.pitch=0; TGT.lock=tgtAcquire(Ride.yaw); } if(!on){ TGT.lock=null; TGT.spot=null; }
  TGT.aiming=on; TGT.k=THREE.MathUtils.clamp(TGT.k+(on?dt:-dt)*7,0,1);
  if(on){ const rs=R&&R.gp?R.rs:[0,0,0];
    if(TGT.lock){ // fine aim around the lock; strong flick switches target
      if(Math.abs(rs[0])>.85&&TGT.flickArmed){ const n=tgtPick(tgtDir(),0,TGT.lock,Math.sign(-rs[0])); if(n){ TGT.lock=n; TGT.yawOff=0; } TGT.flickArmed=false; }
      if(Math.abs(rs[0])<.4) TGT.flickArmed=true;
      const L=TGT.lock, p=Ride.group.position; if(Math.hypot(L.ref.holder?L.ref.holder.position.x-p.x:L.x-p.x,L.ref.holder?L.ref.holder.position.z-p.z:L.z-p.z)>TGT.range+3) TGT.lock=null;
      else { if(L.ref.holder){ L.x=L.ref.holder.position.x; L.z=L.ref.holder.position.z; } const want=Math.atan2(L.x-p.x,L.z-p.z)-Ride.yaw; TGT.yawOff=angDiff(want,0)+rs[0]*-.12*(TGT.flickArmed?1:0); } }
    else { TGT.yawOff=THREE.MathUtils.clamp(TGT.yawOff-rs[0]*dt*1.8,-1.4,1.4); const n=tgtAcquire(tgtDir()); if(n) TGT.lock=n; }
    TGT.pitch=THREE.MathUtils.clamp(TGT.pitch+rs[1]*dt*.8,-.3,.4);
    // spot under reticle (locked spot or nearest spot within a tight cone)
    const sp=TGT.lock&&TGT.lock.kind==="spot"?TGT.lock:tgtPick(tgtDir(),.12); TGT.spot=sp&&sp.kind==="spot"?sp:null;
    TGT.aim=TGT.lock?{x:TGT.lock.x,z:TGT.lock.z,y:TGT.lock.y}:tgtRay(tgtDir()); }
  // UI
  const lockE=on&&TGT.lock&&TGT.lock.kind==="enemy", spray=on&&!lockE&&TGT.spot; TGT.ui.style.display=on?"block":"none";
  TGT.ui.querySelector("#retDot").style.display=on&&!lockE&&!spray?"":"none"; TGT.ui.querySelector("#retLock").style.display=lockE?"":"none"; TGT.ui.querySelector("#retSpray").style.display=spray?"":"none";
  TGT.mode=!on?"off":lockE?"lock":spray?"spray":"dot";
  const mk=TGT.mk; mk.visible=!!(on&&TGT.lock); if(mk.visible){ const L=TGT.lock; mk.material.color.set(L.col); mk.position.set(L.x,L.kind==="enemy"?2.3:L.y,L.z); mk.quaternion.copy(camera.quaternion); mk.scale.setScalar(1+.12*Math.sin(performance.now()/120)); }
  const pv=TGT.pv; pv.visible=!!(on&&TGT.spot); if(pv.visible){ const s=TGT.spot.ref, ok=Math.hypot(s.x-Ride.group.position.x,s.z-Ride.group.position.z)<=TGT.sprayR; pv.position.set(s.x+s.nx*.04,2.4,s.z+s.nz*.04); pv.rotation.set(0,Math.atan2(s.nx,s.nz),0); pv.material.color.set(ok?((TURF.crews[TURF.me]||{}).css||"#FF2BD6"):"#888888"); pv.material.opacity=ok?.85:.4; TGT.sprayOk=ok; } else TGT.sprayOk=false; }
// camera: over-the-shoulder + FOV zoom, applied pre-render, restored at next poll
function tgtCam(dt){ if(TGT.k<=0.001) return; if(!TGT.saved) TGT.saved={p:camera.position.clone(),q:camera.quaternion.clone(),fov:camera.fov};
  const p=Ride.group.position, y=tgtDir(), k=TGT.k*TGT.k*(3-2*TGT.k), fx=Math.sin(y), fz=Math.cos(y), rx=Math.cos(y), rz=-Math.sin(y);
  const sh=new THREE.Vector3(p.x-fx*2.3-rx*.75,p.y+1.75+TGT.pitch*-1.2,p.z-fz*2.3-rz*.75); camera.position.lerp(sh,k);
  const a=TGT.aim||{x:p.x+fx*10,z:p.z+fz*10,y:1.5}; const look=new THREE.Vector3(a.x,(a.y||1.5)+TGT.pitch*3,a.z); const q0=camera.quaternion.clone(); camera.lookAt(look); const q1=camera.quaternion.clone(); camera.quaternion.copy(q0).slerp(q1,k);
  camera.fov=TGT.saved.fov+(48-TGT.saved.fov)*k; camera.updateProjectionMatrix(); }
// rest FOV (Rydah Systems 17:58): the base camera eases the speed FOV 65+f*14 with a per-frame lerp(.1) (frame-rate dependent, .05 deadband, ~2 s tail),
// so after an LT release mid-lunge the FOV crept for seconds. Re-ease it here dt-based (rate 6/s) and snap within .01; the aim zoom builds on this live rest value.
function tgtRestFov(dt){ const sp=Ride.speed/Ride.maxSpeed, f=THREE.MathUtils.clamp((sp-.55)*2.2+(Ride.boost||0)*.5,0,1), want=65+f*14;
  let v=TGT.restFov==null?(TGT.saved?TGT.saved.fov:camera.fov):TGT.restFov; v=want+(v-want)*Math.exp(-Math.min(dt,.1)*6); if(Math.abs(v-want)<.01) v=want;
  TGT.fovWant=want; TGT.restFov=v; return v; }
function tgtTick(dt){ tgtUpdate(dt,PAD.R);
  if(State.mode==="ride"&&!renderer.xr.isPresenting&&!window.__overhead&&!window.__flyover){ const r=tgtRestFov(dt); if(TGT.saved) TGT.saved.fov=r; camera.fov=r; camera.updateProjectionMatrix(); } else TGT.restFov=null;
  tgtCam(dt); }
// restore camera at frame start (before game camera spring)
if(typeof poll==="function"){ const _pt=poll; poll=function(){ if(TGT.saved){ camera.position.copy(TGT.saved.p); camera.quaternion.copy(TGT.saved.q); camera.fov=TGT.saved.fov; camera.updateProjectionMatrix(); TGT.saved=null; } _pt(); }; }
// attacks go toward the locked / aimed target
if(typeof wallInput==="function"){ const _wt=wallInput; wallInput=function(){ const I=_wt(); if(TGT.aiming&&(I.a[0]||I.a[1]||I.a[2])){ Ride.yaw=tgtDir(); TGT.yawOff=TGT.lock?0:TGT.yawOff; TGT.lastAtkYaw=Ride.yaw; } return I; }; }
// spray only where the reticle points, and only on a valid (in-range, facing) spot
if(typeof turfUpdate==="function"){ const _tu=turfUpdate; turfUpdate=function(dt){ if(!TGT.aiming||!Input.tag) return _tu(dt);
  if(!TGT.spot||!TGT.sprayOk){ const t=Input.tag; Input.tag=false; try{ return _tu(dt); } finally { Input.tag=t; } }
  const all=TURF.spots; TURF.spots=[TGT.spot.ref]; try{ return _tu(dt); } finally { TURF.spots=all; } }; }
// aim slows turning (precision) while held
if(typeof updateRide==="function"){ const _ut=updateRide; updateRide=function(dt){ if(!TGT.aiming) return _ut(dt); const tr=Ride.turnRate; Ride.turnRate=tr*.5; try{ return _ut(dt); } finally { Ride.turnRate=tr; } }; }
addEventListener("keydown",e=>{ if(e.code==="KeyQ") TGT.key=true; }); addEventListener("keyup",e=>{ if(e.code==="KeyQ") TGT.key=false; });
window.TGT=TGT; window.tgtTick=tgtTick;
