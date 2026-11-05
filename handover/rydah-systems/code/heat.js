// ===== POLICE HEAT v1 (heat.js, Rydah Systems) — Windstorm G-Men ladder ★0–★3, hooks for ★4–5 =====
// Injected right after graffiti.js by patch_graffiti.py; extends window.HEAT (graffiti.js) without changing its old API.
// Ladder: ★0 foot patrols with sight cones · ★1 patrols follow (no force) · ★2 + bike cops, foot cordon · ★3 + G-Men on A-T,
// 60 s reinforcement timer (freezes in cooldown). Escape = no cop sees you -> cooldown; hiding spots (crew garages, under bridges,
// standing still) speed it up. BUSTED after 3 s pinned or 3 knockdowns -> unbanked parts/turf lost. Bank at your crew HQ.
// Night x2 on police heat gain and on pay. Draws: 3 InstancedMesh (bodies, cones, light bars), pool of 6.
(function(){
if(typeof HEAT==="undefined"||!window.HEAT) return;
const H=window.HEAT, V3=THREE.Vector3;
const P=H.police={ v1MaxLevel:3.999, pool:6, cullR:150, spawnR:[55,85], pinR:1.7, pinSlow:2.0, pinTime:3, knockMax:3, knockR:1.3, knockCD:2.5,
  reinforceT:60, coolBase:8, coolPerStar:3, hideMult:2.5, stillMult:1.5, gainPerSec:.025,
  types:{ patrol:{speed:6, sight:26, fov:.62, col:0x22336e, name:"patrol"}, bike:{speed:13, sight:34, fov:.7, col:0x2a2a40, name:"bike cop"},
          gmen:{speed:16, sight:42, fov:.85, col:0x111114, name:"G-Men"} },
  ladder:[ {patrol:2}, {patrol:3}, {patrol:2,bike:2}, {patrol:1,bike:2,gmen:2} ] };
// ---- API additions (old HEAT fields untouched)
H.api=2; H.state="idle";            // "idle" | "pursuit" | "cooldown"
H.cops=[];                          // [{id,type,x,y,z,ry,seeing,active}] for minimap / world map (read-only)
H.cooldown=0; H.cooldownMax=0; H.reinforce=null; H.pinned=0; H.knockdowns=0; H.busts=0; H.escapes=0;
H.atRisk={ parts:0, turf:[] }; H.banked={ parts:0, turf:0 }; H.seen=false; H.hiding=null;
H.hooks={ tier4:null, tier5:null, onBust:null, onEscape:null, onBank:null, onReinforce:null }; // ★4 Black Rain + rail spikes, ★5 Kaito + heli
H.payMult=()=>H.night()?2:1;
H.gain=(a,why)=>H.add(a*(H.night()?2:1),why);                       // police-side heat: night doubles
H.addParts=n=>{ H.atRisk.parts+=Math.round(n*H.payMult()); return H.atRisk.parts; };   // pay: night doubles
H.knockdown=why=>{ H.knockdowns++; emitP("knockdown"); if(H.knockdowns>=P.knockMax) H.bust("knockdowns"); };
H.bust=why=>{ const lost={parts:H.atRisk.parts,turf:H.atRisk.turf.slice()}; H.busts++; H.lastBust={why,lost,t:Date.now()};
  for(const t of lost.turf){ try{ const sp=GRAF.spots.find(s=>s.id===t.id); if(sp&&sp.owner===t.crew){ sp.owner=t.prev||null; sp.pts=0; grafWrite(sp); } }catch(e){} }
  try{ if(lost.turf.length){ grafRecount(false); grafSave(); } }catch(e){}
  H.atRisk={parts:0,turf:[]}; endPursuit("busted"); H.set(0); try{ flash("BUSTED","#ff3344"); }catch(e){} hk("onBust",lost); emitP("bust"); };
H.bank=()=>{ if(H.state==="pursuit") return false; const g=myGarage(); const p=pp(); if(!g||Math.hypot(p.x-g.pos[0],p.z-g.pos[1])>14) return false;
  const b={parts:H.atRisk.parts,turf:H.atRisk.turf.length}; H.banked.parts+=b.parts; H.banked.turf+=b.turf; H.atRisk={parts:0,turf:[]};
  if(b.parts||b.turf) try{ flash("BANKED","#7CFFB2"); }catch(e){} hk("onBank",b); emitP("bank"); return b; };
H.step=dt=>{ while(dt>1e-9){ const d=Math.min(dt,.25); tick(d,true); dt-=d; } };           // test/time stub: advance police sim by dt seconds (works while H.freeze=true)
H.freeze=false; H.playerOverride=null; // tests: {x,y,z,speed}
H.spawnCop=(type,x,z,ry)=>spawn(type,x,z,ry);
H.clearCops=()=>{ for(const c of cops) c.active=false; sync(); };
H.policeHud=true; P._los=(ax,az,bx,bz)=>segBlocked(ax,az,bx,bz); P._hiding=p=>hidingAt(p);
// ---- internals
const cops=[]; let mBody=null, mCone=null, mBar=null, ready=false, nid=1, blink=0;
const hk=(n,a)=>{ try{ H.hooks[n]&&H.hooks[n](a,H); }catch(e){ console.warn("HEAT hook "+n,e); } };
function emitP(evt){ try{ H.onChange&&H.onChange(H,"police:"+evt); }catch(e){} }
function pp(){ const o=H.playerOverride; if(o) return {x:o.x,y:o.y||0,z:o.z,speed:o.speed||0}; const g=Ride.group; return g?{x:g.position.x,y:g.position.y,z:g.position.z,speed:Math.abs(Ride.speed||0)}:{x:0,y:0,z:0,speed:0}; }
function myGarage(){ try{ const me=GRAF.me(); return PALMA.garages.find(g=>g.crew===me)||null; }catch(e){ return null; } }
function mergeParts(parts){ // [[geom, hexColor, x,y,z]] -> one non-indexed BufferGeometry with vertex colours
  const pos=[],nor=[],col=[]; for(const [g0,c,x,y,z] of parts){ const g=g0.index?g0.toNonIndexed():g0; g.translate(x,y,z); g.computeVertexNormals(); const C=new THREE.Color(c);
    const a=g.attributes.position.array, n=g.attributes.normal.array; for(let i=0;i<a.length;i++){ pos.push(a[i]); nor.push(n[i]); } for(let i=0;i<a.length/3;i++) col.push(C.r,C.g,C.b); }
  const G=new THREE.BufferGeometry(); G.setAttribute("position",new THREE.Float32BufferAttribute(pos,3)); G.setAttribute("normal",new THREE.Float32BufferAttribute(nor,3)); G.setAttribute("color",new THREE.Float32BufferAttribute(col,3)); return G; }
function build(){ const B=(w,h,d)=>new THREE.BoxGeometry(w,h,d);
  const body=mergeParts([[B(.5,.8,.3),0xffffff,0,1.2,0],[B(.2,.75,.22),0x9aa0b0,-.13,.42,0],[B(.2,.75,.22),0x9aa0b0,.13,.42,0],[B(.26,.28,.26),0xd8b090,0,1.78,0],
    [B(.32,.14,.34),0x101010,0,1.96,0],[B(.14,.55,.14),0xffffff,-.33,1.2,0],[B(.14,.55,.14),0xffffff,.33,1.2,0],[B(.28,.1,.4),0x00e5ff,-.13,.05,0],[B(.28,.1,.4),0x00e5ff,.13,.05,0]]);
  const mat=new THREE.MeshLambertMaterial({vertexColors:true}); mBody=new THREE.InstancedMesh(body,mat,P.pool);
  const cg=new THREE.ConeGeometry(1,1,16,1,true); cg.translate(0,-.5,0); cg.rotateX(-Math.PI/2); // apex at origin, opens along +z
  // subtle ground fan: red only, alpha fades with distance from the cop (apex) and toward the fan edges; no depth write
  const coneMat=new THREE.ShaderMaterial({transparent:true,depthWrite:false,side:THREE.DoubleSide,
    vertexShader:"varying vec3 vL; void main(){ vL=position; gl_Position=projectionMatrix*modelViewMatrix*instanceMatrix*vec4(position,1.); }",
    fragmentShader:"varying vec3 vL; void main(){ float r=clamp(vL.z,0.,1.); float a=.10*(1.-r)*(1.-r)+.05*smoothstep(.9,.97,r)*(1.-smoothstep(.97,1.,r)); gl_FragColor=vec4(1.,.13,.18,a); }"});
  mCone=new THREE.InstancedMesh(cg,coneMat,P.pool);
  mBar=new THREE.InstancedMesh(B(.34,.07,.1),new THREE.MeshBasicMaterial({color:0xffffff}),P.pool);
  for(const m of [mBody,mCone,mBar]){ m.count=0; m.frustumCulled=false; m.instanceMatrix.setUsage(THREE.DynamicDrawUsage); m.name="heat_cops"; scene.add(m); }
  for(let i=0;i<P.pool;i++){ mBody.setColorAt(i,new THREE.Color(0xffffff)); mBar.setColorAt(i,new THREE.Color(0xff0000)); }
  for(let i=0;i<P.pool;i++) cops.push({id:0,type:"patrol",x:0,y:0,z:0,ry:0,active:false,seeing:false,tackleCD:0,wander:Math.random()*6.28,home:null});
  ready=true; }
function spawn(type,x,z,ry){ if(!ready) build(); let c=cops.find(c=>!c.active); if(!c) return null;
  if(x==null){ const p=pp(); for(let t=0;t<12;t++){ const a=Math.random()*6.283, r=P.spawnR[0]+Math.random()*(P.spawnR[1]-P.spawnR[0]); x=p.x+Math.cos(a)*r; z=p.z+Math.sin(a)*r; if(!inCol(x,z)) break; } }
  Object.assign(c,{id:nid++,type,x,y:0,z,ry:ry!=null?ry:Math.random()*6.283,active:true,seeing:false,tackleCD:1,home:[x,z]}); sync(); return c.id; }
function inCol(x,z){ try{ for(const c of colliders) if(x>c.minX&&x<c.maxX&&z>c.minZ&&z<c.maxZ) return true; }catch(e){} return false; }
function segBlocked(ax,az,bx,bz){ let n=0; try{ for(const c of colliders){ if(Math.max(ax,bx)<c.minX||Math.min(ax,bx)>c.maxX||Math.max(az,bz)<c.minZ||Math.min(az,bz)>c.maxZ) continue;
  let t0=0,t1=1; const dx=bx-ax, dz=bz-az; for(const [p,q] of [[-dx,ax-c.minX],[dx,c.maxX-ax],[-dz,az-c.minZ],[dz,c.maxZ-az]]){ if(p===0){ if(q<0){ t0=2; break; } } else { const r=q/p; if(p<0){ if(r>t1){t0=2;break;} if(r>t0) t0=r; } else { if(r<t0){t0=2;break;} if(r<t1) t1=r; } } }
  if(t0<=t1&&t1>.02&&t0<.98) return true; if(++n>4000) break; } }catch(e){} return false; }
function sees(c,p){ const T=P.types[c.type], dx=p.x-c.x, dz=p.z-c.z, d=Math.hypot(dx,dz); const chase=H.state!=="idle";
  const range=T.sight*(chase?1.25:1)*(H.night()?.8:1); if(d>range) return false;
  if(p.y>6&&c.type!=="gmen"&&d>12) return false;            // rooftops: only A-T G-Men follow you up there
  if(!chase||d>8){ let a=Math.atan2(dx,dz)-c.ry; a=Math.atan2(Math.sin(a),Math.cos(a)); if(Math.abs(a)>(chase?T.fov*1.6:T.fov)) return false; }
  return !segBlocked(c.x,c.z,p.x,p.z); }
function hidingAt(p){ const g=myGarage(); if(g&&Math.hypot(p.x-g.pos[0],p.z-g.pos[1])<12) return "crew HQ";
  try{ for(const g2 of PALMA.garages) if(Math.hypot(p.x-g2.pos[0],p.z-g2.pos[1])<9) return "garage"; }catch(e){}
  try{ for(const b of PALMA.bridges){ const ax=b.a[0],az=b.a[1],bx=b.b[0],bz=b.b[1], L2=(bx-ax)**2+(bz-az)**2||1; let t=((p.x-ax)*(bx-ax)+(p.z-az)*(bz-az))/L2; if(t<.1||t>.9) continue;
    if(Math.hypot(p.x-(ax+t*(bx-ax)),p.z-(az+t*(bz-az)))<5&&p.y<2) return "under bridge"; } }catch(e){}
  if(p.speed<.5) return "still"; return null; }
function want(){ const s=Math.min(3,H.stars), L=Object.assign({},P.ladder[s]); if(s>=3&&H._extraG) L.gmen=(L.gmen||0)+H._extraG; return L; }
function endPursuit(why){ H.state="idle"; H.cooldown=0; H.pinned=0; H.reinforce=null; H._extraG=0; H.knockdowns=0; if(why==="escaped"){ H.escapes++; hk("onEscape",{stars:H.stars}); emitP("escape"); try{ flash("ESCAPED","#2EE6D6"); }catch(e){} } }
function tick(dt,manual){ if(H.freeze&&!manual) return; if(!ready){ if(typeof scene==="undefined"||!Ride.group) return; build(); }
  dt=Math.min(dt,.25); const p=pp(); blink+=dt;
  // ★4–5 out of scope: cap at ★3 unless a tier hook is installed
  if(H.level>P.v1MaxLevel&&!H.hooks.tier4) H.set(P.v1MaxLevel); else if(H.stars>=4) hk(H.stars>=5&&H.hooks.tier5?"tier5":"tier4",{dt,p});
  // roster: despawn far / surplus, spawn missing (pool max 6)
  const L=want(); let n=0; for(const c of cops) if(c.active){ n++; if(Math.hypot(c.x-p.x,c.z-p.z)>P.cullR) c.active=false; }
  for(const t in P.types){ let have=cops.filter(c=>c.active&&c.type===t).length; const w=L[t]||0;
    for(const c of cops) if(have>w&&c.active&&c.type===t&&!c.seeing){ c.active=false; have--; }
    while(have<w&&cops.some(c=>!c.active)){ spawn(t); have++; } }
  // perception + movement
  let anySee=false; for(const c of cops){ if(!c.active) continue; const T=P.types[c.type]; c.tackleCD-=dt;
    c.seeing=sees(c,p); if(c.seeing) anySee=true;
    const dx=p.x-c.x, dz=p.z-c.z, d=Math.hypot(dx,dz)||1;
    if(H.state!=="idle"&&(c.seeing||H.state==="pursuit")){ const sp=T.speed*(H.stars>=1?1:0)*(c.type==="patrol"&&H.stars===1?.8:1);
      const stop=c.type==="patrol"&&H.stars<2?6:.9; if(d>stop){ const k=Math.min(d-stop,sp*dt)/d; c.x+=dx*k; c.z+=dz*k; } c.ry=Math.atan2(dx,dz);
      if(c.type==="gmen") c.y+=(p.y-c.y)*Math.min(1,dt*3); else c.y=0;
      if(H.stars>=2&&c.type!=="patrol"&&d<P.knockR&&c.tackleCD<=0&&p.speed>P.pinSlow){ c.tackleCD=P.knockCD; H.knockdown(c.type); if(H.state==="idle") return; } }
    else { c.wander+=dt*.3; c.ry+=Math.sin(c.wander)*dt*.6; const nx=c.x+Math.sin(c.ry)*1.4*dt, nz=c.z+Math.cos(c.ry)*1.4*dt; if(!inCol(nx,nz)&&Math.hypot(nx-c.home[0],nz-c.home[1])<15){ c.x=nx; c.z=nz; } else c.ry+=Math.PI*.5; c.y=0; } }
  H.seen=anySee;
  // pursuit state machine
  if(anySee&&H.stars>=1){ if(H.state!=="pursuit"){ H.state="pursuit"; emitP("pursuit"); } H.cooldown=0; H.quiet=0;
    H.level=Math.min(P.v1MaxLevel>H.level?P.v1MaxLevel:H.level, H.level+P.gainPerSec*dt*(H.night()?2:1)); const s0=H.stars; H.stars=Math.floor(H.level+1e-6); if(H.stars!==s0) H.set(H.level); }
  else if(anySee&&H.stars===0&&window.GRAF&&GRAF.cur){ H.gain(1,"spotted tagging"); }
  else if(H.state==="pursuit"&&!anySee){ H.state="cooldown"; H.cooldownMax=P.coolBase+P.coolPerStar*H.stars; H.cooldown=0; emitP("cooldown"); }
  if(H.state==="cooldown"){ H.quiet=0; H.hiding=hidingAt(p); const m=H.hiding==="still"?P.stillMult:H.hiding?P.hideMult:1; H.cooldown+=dt*m; if(H.cooldown>=H.cooldownMax) endPursuit("escaped"); }
  else H.hiding=null;
  // ★3 reinforcements: 60 s countdown, frozen during cooldown
  if(H.stars>=3&&H.state!=="idle"){ if(H.reinforce==null) H.reinforce=P.reinforceT; if(H.state==="pursuit") H.reinforce-=dt;
    if(H.reinforce<=0){ H._extraG=Math.min(P.pool-5,(H._extraG||0)+1); H.reinforce=P.reinforceT; hk("onReinforce",{extra:H._extraG}); emitP("reinforce"); if(H.hooks.tier4) H.gain(1,"reinforcements"); } }
  else if(H.stars<3) H.reinforce=null;
  // busted: pinned 3 s (cop within reach, you nearly stopped)
  if(H.state==="pursuit"){ const near=cops.some(c=>c.active&&Math.hypot(c.x-p.x,c.z-p.z)<P.pinR); if(near&&p.speed<P.pinSlow) H.pinned+=dt; else H.pinned=Math.max(0,H.pinned-dt*2); if(H.pinned>=P.pinTime) H.bust("pinned"); } else H.pinned=0;
  sync(); hud(); }
const _m=new THREE.Matrix4(), _q=new THREE.Quaternion(), _s=new V3(), _p=new V3(), _e=new THREE.Euler(), _c=new THREE.Color();
function sync(){ if(!ready) return; let i=0; H.cops.length=0; const showCones=H.stars<=1;
  for(const c of cops){ if(!c.active) continue; H.cops.push({id:c.id,type:c.type,x:+c.x.toFixed(2),y:+c.y.toFixed(2),z:+c.z.toFixed(2),ry:+c.ry.toFixed(3),seeing:c.seeing});
    _q.setFromEuler(_e.set(0,c.ry,0)); _m.compose(_p.set(c.x,c.y,c.z),_q,_s.set(1,1,1)); mBody.setMatrixAt(i,_m); mBody.setColorAt(i,_c.set(P.types[c.type].col).lerp(_c.clone().set(0xffffff),.55));
    _m.compose(_p.set(c.x,c.y+2.12,c.z),_q,_s.set(1,1,1)); mBar.setMatrixAt(i,_m); mBar.setColorAt(i,_c.set((Math.floor(blink*4)+i)%2?0xff1030:0x2050ff));
    const T=P.types[c.type], R=(showCones||(H.state==="cooldown"&&!c.seeing))?T.sight:0.001, w=Math.tan(T.fov)*R; _m.compose(_p.set(c.x,c.y+.08,c.z),_q,_s.set(w,.02,R)); mCone.setMatrixAt(i,_m); i++; }
  for(const m of [mBody,mCone,mBar]){ m.count=i; m.instanceMatrix.needsUpdate=true; if(m.instanceColor) m.instanceColor.needsUpdate=true; } mCone.visible=(showCones||H.state==="cooldown")&&i>0; mBody.visible=mBar.visible=i>0; }
function hud(){ if(!H.policeHud) return; let el=document.getElementById("heatPolice"); if(!el){ el=document.createElement("div"); el.id="heatPolice"; el.className="hud"; el.style.cssText="position:fixed;top:42px;right:220px;color:#fff;font:bold 13px Arial;text-shadow:0 0 5px #000;z-index:15;text-align:right"; document.body.appendChild(el); }
  let s=""; if(H.state==="pursuit") s=`<span style="color:#ff3344">PURSUIT</span>`+(H.pinned>.05?` <span style="color:#ff3344">BUST ${"▮".repeat(Math.ceil(H.pinned/P.pinTime*6))}</span>`:"");
  else if(H.state==="cooldown") s=`<span style="color:#4fa8ff">COOLDOWN ${"▮".repeat(Math.ceil(H.cooldown/H.cooldownMax*8))}${"▯".repeat(8-Math.ceil(H.cooldown/H.cooldownMax*8))}</span>${H.hiding?" · "+H.hiding.toUpperCase():""}`;
  if(H.reinforce!=null&&H.state!=="idle") s+=`<br>G-MEN BACKUP ${Math.ceil(H.reinforce)}s`; if(H.knockdowns) s+=`<br>KNOCKDOWNS ${H.knockdowns}/3`;
  if(H.atRisk.parts||H.atRisk.turf.length) s+=`<br><span style="color:#ffc83c">AT RISK: ${H.atRisk.parts} parts · ${H.atRisk.turf.length} tags</span>`; el.innerHTML=s; }
// unbanked turf: my crew's new tags are at risk until banked
try{ TURF.subscribe(e=>{ if(e.type==="tag"&&e.tag&&e.crew===GRAF.me()) H.atRisk.turf.push({id:e.tag.id,crew:e.crew,prev:e.prevOwner||null}); }); }catch(e){}
window.heatTick=function(dt,xr){ try{ if(window.GRAF&&GRAF.ready) tick(dt,false); }catch(e){ console.warn("heat tick",e); window.heatTick=null; } };
})();
