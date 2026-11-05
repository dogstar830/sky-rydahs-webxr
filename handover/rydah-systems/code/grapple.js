// ===== Grapple (Y): cable up to marked grapple points on crew-house roof catwalks, rooftops and billboard decks.
const GRAP={ pts:[], act:null, deck:null, airDeck:false, target:null, line:null, prompt:null, mk:null, built:false, ac:null, range:11 };
function grapBuild(){ if(GRAP.built) return; GRAP.built=true; const P=GRAP.pts;
  const add=(name,kind,ax,az,nx,nz,y,deck)=>P.push({name,kind,x:ax,z:az,y,lx:ax-nx*2.2,lz:az-nz*2.2,deck});
  // crew-house roof catwalks (garage walls H=5.2; local box x±5.8, z -9.8..-0.2; front faces local +z)
  const decks=[];
  for(const g of (typeof garages!=="undefined"?garages:[])){ if(!g.group) continue; const th=g.th, gx=g.pos[0], gz=g.pos[1];
    const W=(lx,lz)=>[gx+lx*Math.cos(th)+lz*Math.sin(th), gz-lx*Math.sin(th)+lz*Math.cos(th)];
    const c=[W(-5.8,-9.8),W(5.8,-.2)], d={minX:Math.min(c[0][0],c[1][0]),maxX:Math.max(c[0][0],c[1][0]),minZ:Math.min(c[0][1],c[1][1]),maxZ:Math.max(c[0][1],c[1][1]),y:5.4};
    const side=W(6.6,-5), n=[Math.sin(th+Math.PI/2),Math.cos(th+Math.PI/2)]; // anchor on the +x side wall top
    const a=W(5.9,-5); add(g.name+" CATWALK","catwalk",a[0],a[1],n[0],n[1],d.y,d); decks.push([d,g.color]); }
  // rooftops + billboard decks: low/mid buildings with roomy roofs
  if(typeof B!=="undefined"&&B.pos&&B.pos.length){ const cand=[]; B.pos.forEach((p,i)=>{ const [w,h,dd]=B.size[i]; if(h<5.5||h>11||w<7||dd<7) return; const dist=typeof districtAt==="function"?districtAt(p[0],p[1]):null; cand.push({i,x:p[0],z:p[1],w,h,d:dd,dist:dist&&dist.id}); });
    const pick=(f,n,kind,label)=>{ const used=new Set(); for(const c of cand.filter(f)){ if(used.size>=n) break; const k=c.dist+":"+Math.round(c.x/60)+":"+Math.round(c.z/60); if(used.has(k)) continue; used.add(k);
        const d={minX:c.x-c.w/2,maxX:c.x+c.w/2,minZ:c.z-c.d/2,maxZ:c.z+c.d/2,y:c.h+.05}; add(label,kind,c.x,c.z+c.d/2+.1,0,1,d.y,d); decks.push([d,kind==="billboard"?"#FFC83C":"#2EE6D6"]); c.used=true; } };
    pick(c=>c.dist==="the98",4,"billboard","BILLBOARD DECK"); pick(c=>c.dist&&c.dist!=="the98"&&!c.used,8,"rooftop","ROOFTOP"); }
  // markers: one instanced glow ring per point + one instanced beam (2 draw calls); thin deck edge trims (1)
  const n=P.length; if(!n) return;
  const ring=new THREE.InstancedMesh(new THREE.TorusGeometry(.55,.09,6,16),new THREE.MeshBasicMaterial({color:0xE8B12A,fog:false}),n);
  const beam=new THREE.InstancedMesh(new THREE.CylinderGeometry(.05,.05,1,5,1,true),new THREE.MeshBasicMaterial({color:0xE8B12A,transparent:true,opacity:.55,depthWrite:false,fog:false}),n);
  const m=new THREE.Matrix4(), q=new THREE.Quaternion(), e=new THREE.Euler(), v=new THREE.Vector3(), s=new THREE.Vector3();
  P.forEach((p,i)=>{ q.setFromEuler(e.set(Math.PI/2,0,0)); m.compose(v.set(p.x,p.y+.15,p.z),q,s.set(1,1,1)); ring.setMatrixAt(i,m); q.identity(); m.compose(v.set(p.x,p.y/2,p.z),q,s.set(1,p.y,1)); beam.setMatrixAt(i,m); });
  scene.add(ring); scene.add(beam); GRAP.mk=ring;
  const trim=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),new THREE.MeshBasicMaterial({color:0xffffff,fog:false}),decks.length); const col=new THREE.Color();
  decks.forEach(([d,c],i)=>{ m.compose(v.set((d.minX+d.maxX)/2,d.y-.08,(d.minZ+d.maxZ)/2),q.identity(),s.set(d.maxX-d.minX,.16,d.maxZ-d.minZ)); trim.setMatrixAt(i,m); trim.setColorAt(i,col.set(c).multiplyScalar(.35)); }); scene.add(trim);
  const lg=new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(),new THREE.Vector3()]); GRAP.line=new THREE.Line(lg,new THREE.LineBasicMaterial({color:0x2EE6D6})); GRAP.line.visible=false; GRAP.line.frustumCulled=false; scene.add(GRAP.line);
  const pr=document.createElement("div"); pr.id="grapPrompt"; pr.className="hud"; pr.style.cssText="position:fixed;left:50%;top:64%;transform:translateX(-50%);padding:8px 16px;background:rgba(10,16,30,.72);border:2px solid #E8B12A;border-radius:14px;color:#fff;font:800 18px 'Segoe UI',Arial,sans-serif;letter-spacing:2px;display:none;pointer-events:none;z-index:15";
  pr.innerHTML='<span style="display:inline-block;width:26px;height:26px;line-height:26px;border-radius:50%;background:#E8B12A;color:#111;text-align:center;margin-right:10px;font-size:13px">&#9664;</span><span id="grapName">GRAPPLE</span>'; document.body.appendChild(pr); GRAP.prompt=pr; }
function grapFind(){ const R=Ride, p=R.group.position, fx=Math.sin(R.yaw), fz=Math.cos(R.yaw); let best=null, bs=1e9; const cy=R.y||0;
  for(const g of GRAP.pts){ if(cy>=g.y-.5) continue; const dx=g.x-p.x, dz=g.z-p.z, d=Math.hypot(dx,dz); if(d>GRAP.range||d<.4) continue; const dot=(dx*fx+dz*fz)/d; if(dot<.7) continue; const sc=d*(2-dot); if(sc<bs){ bs=sc; best=g; } }
  return best; }
function grapWhoosh(){ try{ const A=GRAP.ac||(GRAP.ac=new (window.AudioContext||window.webkitAudioContext)()); const n=A.sampleRate*.5, b=A.createBuffer(1,n,A.sampleRate), d=b.getChannelData(0); for(let i=0;i<n;i++) d[i]=(Math.random()*2-1)*Math.sin(Math.PI*i/n);
  const s=A.createBufferSource(); s.buffer=b; const f=A.createBiquadFilter(); f.type="bandpass"; f.Q.value=1.4; f.frequency.setValueAtTime(400,A.currentTime); f.frequency.exponentialRampToValueAtTime(2600,A.currentTime+.45); const g=A.createGain(); g.gain.value=.35; s.connect(f); f.connect(g); g.connect(A.destination); s.start(); }catch(e){} }
function grapStart(g){ const R=Ride, p=R.group.position; const d=Math.hypot(g.x-p.x,g.z-p.z,g.y-(R.y||0)); GRAP.act={g,t:0,dur:THREE.MathUtils.clamp(.55+d*.04,.6,1.0),x0:p.x,z0:p.z,y0:R.y||0};
  WALL.on=null; WALL.air=null; GRAP.deck=null; if(typeof GRIND!=="undefined"){ GRIND.on=null; GRIND.cd=Math.max(GRIND.cd||0,1.2); } R.grinding=false; R.speed=0; GRAP.line.visible=true; grapWhoosh(); try{ flash("GRAPPLE"); }catch(e){} GRAP.count=(GRAP.count||0)+1; }
function grapStep(dt){ const A=GRAP.act, R=Ride, p=R.group.position, g=A.g; A.t+=dt; const u=Math.min(1,A.t/A.dur), k=u*u*(3-2*u);
  const lift=Math.min(1,k*1.25); p.x=THREE.MathUtils.lerp(A.x0,g.x,Math.min(1,k*1.1)); p.z=THREE.MathUtils.lerp(A.z0,g.z,Math.min(1,k*1.1)); const y=THREE.MathUtils.lerp(A.y0,g.y+.6,lift)+Math.sin(u*Math.PI)*.4; R.y=y; p.y=y;
  if(u>=.85){ const w=(u-.85)/.15; p.x=THREE.MathUtils.lerp(g.x,g.lx,w); p.z=THREE.MathUtils.lerp(g.z,g.lz,w); R.y=p.y=g.y; }
  R.yaw=Math.atan2(g.lx-A.x0,g.lz-A.z0); const L=GRAP.line.geometry.attributes.position; L.setXYZ(0,p.x,p.y+1.3,p.z); L.setXYZ(1,g.x,g.y+.15,g.z); L.needsUpdate=true;
  if(typeof emit==="function"&&Math.random()<.6) emit({x:p.x,y:p.y+.8,z:p.z},0x2EE6D6,(Math.random()-.5)*2,-2,(Math.random()-.5)*2,.25);
  if(u>=1){ GRAP.act=null; GRAP.line.visible=false; GRAP.deck=g.deck; R.y=p.y=g.y; R.speed=2; try{ trickScore(120,"GRAPPLE UP",.04); }catch(e){} } }
function grapInDeck(d,x,z){ return d&&x>=d.minX-.2&&x<=d.maxX+.2&&z>=d.minZ-.2&&z<=d.maxZ+.2; }
// hooks: wallStep (airborne/deck), updateRide (deck walking), speed lines, input
if(typeof wallStep==="function"){ const _ws=wallStep; wallStep=function(dt){ if(!GRAP.built) grapBuild(); if(GRAP.act){ grapStep(dt); return true; }
  const deckAir=(GRAP.airDeck&&WALL.air)||GRAP.deck; let saved=null; if(deckAir){ saved=colliders.splice(0); }
  let r; try{ r=_ws(dt); } finally { if(saved) colliders.push(...saved); }
  const A=WALL.air, p=Ride.group.position;
  if(A&&GRAP.airDeck){ const d=GRAP.airDeck; if(A.vy<0&&A.y<=d.y&&A.y>d.y-1.2&&grapInDeck(d,p.x,p.z)){ WALL.air=null; GRAP.deck=d; GRAP.airDeck=false; Ride.y=p.y=d.y; Ride.speed=Math.hypot(A.vx,A.vz); r=true; } }
  if(!WALL.air) GRAP.airDeck=GRAP.deck?false:GRAP.airDeck;
  if(GRAP.deck&&WALL.air){ GRAP.airDeck=GRAP.deck; GRAP.deck=null; }
  return r; }; }
if(typeof updateRide==="function"){ const _ur2=updateRide; updateRide=function(dt){ const d=GRAP.deck; if(!d) return _ur2(dt);
  const saved=colliders.splice(0); try{ _ur2(dt); } finally { colliders.push(...saved); }
  const p=Ride.group.position; Ride.y=p.y=d.y;
  if(!grapInDeck(d,p.x,p.z)){ GRAP.deck=null; GRAP.airDeck=false; wallLaunch(Math.sin(Ride.yaw)*Ride.speed,Math.cos(Ride.yaw)*Ride.speed,1.5,false); WALL.air.y=d.y; } }; }
if(typeof updateSpeedLines==="function"){ const _sl=updateSpeedLines; updateSpeedLines=function(dt,f){ return _sl(dt,GRAP.act?1:f); }; }
function grapTick(){ if(!GRAP.built||!GRAP.prompt) return; const ok=State.mode==="ride"&&!renderer.xr.isPresenting&&!GRAP.act&&!(window.PHONE&&PHONE.up)&&!(window.MAP&&MAP.open);
  GRAP.target=ok?grapFind():null; GRAP.prompt.style.display=GRAP.target?"block":"none"; if(GRAP.target) document.getElementById("grapName").textContent="GRAPPLE · "+GRAP.target.name;
  if(GRAP.mk){ GRAP.mk.material.color.setHSL(.11,1,.5+.15*Math.sin(performance.now()/200)); } }
addEventListener("keydown",e=>{ if(e.code==="KeyG"&&!e.repeat&&State.mode==="ride"&&GRAP.target&&!GRAP.act){ grapStart(GRAP.target); e.preventDefault(); } });
window.GRAP=GRAP; window.grapStart=grapStart; window.grapTick=grapTick; window.grapFind=grapFind;
