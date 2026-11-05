// ===== MINIMAP_V2 : Watch Dogs-style tilted minimap + minimal direction markers (Sky Rydahs). ?minimap=old restores the old HUD.
// Static road grid pre-rendered once to a big canvas; per tick (20 Hz) one drawImage + route + icons into a small canvas.
// Desktop: canvas in a TOP-right DOM box (Oliver 18:39: minimap upper right; objective label under it, turf/rival panel #turf under that), tilted with a CSS 3D transform. VR: same canvas as CanvasTexture on a small quad in lower view.
const MM2={ on:!/[?&]minimap=old\b/.test(location.search), tilt:45, W:320, H:320, range:110, acc:0, hz:20,
  big:null, bx0:-360, bz0:-480, bspan:880, bpx:2048, cv:null, box:null, quad:null, tex:null, diam:null, sprite:null, arrows:[], theme:null,
  // GPS heading-up state: h = smoothed heading (Ride.yaw convention, forward=(sin h,cos h)); rot = canvas rotation so heading points up
  h:null, rot:0, cx:0, cz:0, lx:null, lz:null, vs:0, moving:false, vOn:1.5, vOff:.7, smooth:8, rim:[], nx:0, ny:0 };
window.__mmV2=MM2.on;
function mm2Crew(){ try{ const g=garages.find(g=>g.crew===lastCrew); if(g&&g.color) return g.color; }catch(e){} return "#E8B12A"; }
function mm2Obj(){ if(typeof MAP!=="undefined"&&MAP.wp) return {x:MAP.wp.x,z:MAP.wp.z,kind:"waypoint",name:MAP.wp.name};
  const P=Ride.group.position; let b=null,bd=1e18; for(const m of icMarkers()){ if(m.kind!=="job"&&!(m.kind==="gate"&&!m.dim)) continue; const d=(m.x-P.x)**2+(m.z-P.z)**2; if(d<bd){bd=d;b=m;} } return b; }
function mm2Fmt(d){ return d>=1000?(d/1000).toFixed(1)+" km":Math.round(d)+" m"; }
// OBJECTIVE readout: name + distance, refreshed at 5 Hz; shared by DOM panel, rim label, VR quad (canvas) and MINIMAP.state.obj
function mm2ObjText(ob,dt){ MM2.otAcc=(MM2.otAcc||0)+(dt||0); const key=ob?ob.name+"|"+ob.x+"|"+ob.z:""; if(MM2.ot&&MM2.otAcc<.2&&MM2.ot.key===key) return MM2.ot; MM2.otAcc=0;
  if(!ob){ MM2.ot=null; return null; } const P=Ride.group.position, d=Math.hypot(ob.x-P.x,ob.z-P.z), nm=String(ob.name||(ob.kind==="waypoint"?"WAYPOINT":"OBJECTIVE")).toUpperCase();
  MM2.ot={key:ob.name+"|"+ob.x+"|"+ob.z,name:nm,dist:d,dtext:mm2Fmt(d),text:nm+" · "+mm2Fmt(d)}; return MM2.ot; }
function mm2Wrap(a){ return Math.atan2(Math.sin(a),Math.cos(a)); }
// per-frame: velocity heading when moving (hysteresis), body yaw when stopped; wrap-safe exponential smoothing
function mm2Heading(dt){ const P=Ride.group.position; dt=Math.max(1e-4,Math.min(dt||0,.1));
  let tgt=Ride.yaw;
  if(MM2.lx!==null){ const dx=P.x-MM2.lx, dz=P.z-MM2.lz, d=Math.hypot(dx,dz);
    if(d<20){ const v=d/dt; MM2.vs+=(v-MM2.vs)*(1-Math.exp(-dt*10)); MM2.moving=MM2.moving?MM2.vs>MM2.vOff:MM2.vs>MM2.vOn;
      if(MM2.moving&&d>1e-4){ MM2.vh=Math.atan2(dx,dz); } } else { MM2.vs=0; MM2.moving=false; } }
  MM2.lx=P.x; MM2.lz=P.z; if(MM2.moving&&MM2.vh!==undefined) tgt=MM2.vh;
  if(MM2.h===null) MM2.h=tgt; else MM2.h=mm2Wrap(MM2.h+mm2Wrap(tgt-MM2.h)*(1-Math.exp(-dt*MM2.smooth)));
  MM2.rot=mm2Wrap(MM2.h+Math.PI); MM2.cx=P.x; MM2.cz=P.z; }
// world -> minimap canvas px (player fixed at centre, heading up)
function mm2W2S(x,z){ const k=MM2.H/MM2.range, cr=Math.cos(MM2.rot), sr=Math.sin(MM2.rot), dx=(x-MM2.cx)*k, dz=(z-MM2.cz)*k; return [MM2.W/2+dx*cr-dz*sr, MM2.H/2+dx*sr+dz*cr]; }
// clamp a canvas point to the circular rim; returns [x,y,onRim,ang]
function mm2Rim(p,R){ const C=MM2.W/2, dx=p[0]-C, dy=p[1]-MM2.H/2, d=Math.hypot(dx,dy)||1e-6, ang=Math.atan2(dy,dx); return d>R?[C+dx/d*R,MM2.H/2+dy/d*R,true,ang]:[p[0],p[1],false,ang]; }
// ---- static base: dark blocks, glowing light-blue/white streets. Built once per theme.
function mm2Base(){ const th=mapTheme(), bn=(typeof boMapData==="function"&&boMapData()||{n:0}).n; if(MM2.big&&MM2.theme===th.t&&MM2.boN===bn) return; MM2.theme=th.t; MM2.boN=bn;
  const c=MM2.big||document.createElement("canvas"); c.width=c.height=MM2.bpx; MM2.big=c; const g=c.getContext("2d"), k=MM2.bpx/MM2.bspan;
  const T=(x,z)=>[(x-MM2.bx0)*k,(z-MM2.bz0)*k]; g.clearRect(0,0,c.width,c.height);
  for(const i of PALMA.islands){ const a=T(i.box[0],i.box[1]), b=T(i.box[2],i.box[3]); g.fillStyle=th.t==="day"?"rgba(40,56,80,.55)":"rgba(14,20,32,.6)"; g.fillRect(a[0],a[1],b[0]-a[0],b[1]-a[1]); }
  try{ boPaintLand(g,T,k,th,true); }catch(e){}   // blockout land/containers/tower/precinct (map.js, BLOCKOUT runtime data)
  const day=th.t==="day", glow=day?"rgba(190,235,255,.9)":"rgba(150,220,255,.85)";
  for(const pass of [0,1]){ g.lineCap="round";
    for(const d of PALMA.districts){ const cell=26; g.beginPath();
      for(let x=d.box[0];x<=d.box[2]+.1;x+=cell){ const a=T(x,d.box[1]), b=T(x,d.box[3]); g.moveTo(a[0],a[1]); g.lineTo(b[0],b[1]); }
      for(let z=d.box[1];z<=d.box[3]+.1;z+=cell){ const a=T(d.box[0],z), b=T(d.box[2],z); g.moveTo(a[0],a[1]); g.lineTo(b[0],b[1]); }
      if(pass===0){ g.strokeStyle=day?"rgba(120,200,255,.22)":"rgba(80,170,255,.2)"; g.lineWidth=7*k; } else { g.strokeStyle=glow; g.lineWidth=1.6*k; } g.stroke(); }
    for(const br of PALMA.bridges){ const a=T(br.a[0],br.a[1]), b=T(br.b[0],br.b[1]); g.beginPath(); g.moveTo(a[0],a[1]); g.lineTo(b[0],b[1]);
      g.strokeStyle=pass?"rgba(255,255,255,.95)":"rgba(120,200,255,.25)"; g.lineWidth=(pass?2.2:9)*k; g.stroke(); }
    try{ boPaintRoads(g,T,k,th,true,pass); }catch(e){} } }
// ---- small white round POI icon (crew tint ring for garages/gates)
function mm2Icon(c,m,x,y,r,sy){ c.save(); c.translate(x,y); c.scale(1,sy); c.globalAlpha=m.dim?.45:1;
  c.fillStyle="rgba(8,12,20,.85)"; c.beginPath(); c.arc(0,0,r,0,7); c.fill(); c.lineWidth=r*.28; c.strokeStyle=(m.kind==="garage"||m.kind==="gate")?(m.col||"#fff"):"#fff"; c.stroke();
  c.fillStyle="#fff"; const s=r*.5; c.beginPath();
  if(m.kind==="job"){ c.moveTo(0,-s); c.lineTo(s,0); c.lineTo(0,s); c.lineTo(-s,0); }
  else if(m.kind==="shop"){ c.arc(0,0,s*.6,0,7); }
  else if(m.kind==="gate"){ c.rect(-s*.6,-s*.3,s*1.2,s*.9); }
  else if(m.kind==="pod"){ c.rect(-s*.25,-s*.8,s*.5,s*1.6); c.rect(-s*.8,-s*.25,s*1.6,s*.5); }
  else if(m.kind==="police"){ c.moveTo(0,-s); c.lineTo(s*.9,s*.7); c.lineTo(-s*.9,s*.7); }
  else if(m.kind==="garage"){ c.moveTo(0,-s); c.lineTo(s,0); c.lineTo(s*.6,s*.8); c.lineTo(-s*.6,s*.8); c.lineTo(-s,0); }
  else c.arc(0,0,s*.5,0,7); c.closePath(); c.fill(); c.restore(); }
function mm2Chevron(c,x,y,s,col){ c.save(); c.translate(x,y); c.shadowColor=col; c.shadowBlur=s*.9; c.fillStyle="#fff"; c.strokeStyle=col; c.lineWidth=s*.22; c.lineJoin="round";
  c.beginPath(); c.moveTo(0,-s); c.lineTo(s*.75,s*.75); c.lineTo(0,s*.35); c.lineTo(-s*.75,s*.75); c.closePath(); c.fill(); c.stroke(); c.restore(); }
// ---- per-tick map draw
function mm2Draw(){ mm2Base(); const cv=MM2.cv, c=cv.getContext("2d"), W=MM2.W, H=MM2.H, P={x:MM2.cx,z:MM2.cz}, col=mm2Crew();
  const px=W/2, py=H/2, k=H/MM2.range, sy=1/Math.cos(MM2.tilt*Math.PI/180), a=MM2.rot, RR=W/2-14;   // player fixed at centre, heading-up; icons counter-stretched for tilt
  const T=mm2W2S; MM2.rim=[];
  c.clearRect(0,0,W,H); const day=MM2.theme==="day"; c.fillStyle=day?"rgba(14,24,40,.62)":"rgba(4,8,16,.66)"; c.fillRect(0,0,W,H);
  c.save(); c.translate(px,py); c.rotate(a); const kb=MM2.bspan/MM2.bpx*k; c.scale(kb,kb); c.drawImage(MM2.big,((MM2.bx0-P.x)/MM2.bspan)*MM2.bpx,((MM2.bz0-P.z)/MM2.bspan)*MM2.bpx); c.restore();
  for(const t of icTags()){ const p=T(t.x,t.z); if(p[0]<0||p[1]<0||p[0]>W||p[1]>H) continue; c.fillStyle=t.col; c.globalAlpha=.75; c.fillRect(p[0]-2,p[1]-2,4,4); } c.globalAlpha=1;
  try{ for(const n of RIDERS.npcs){ const o=n.holder||n.g; if(!o||!o.position) continue; const p=T(o.position.x,o.position.z); if(p[0]<0||p[1]<0||p[0]>W||p[1]>H) continue; c.fillStyle="#FF3B5C"; c.beginPath(); c.arc(p[0],p[1],3.2,0,7); c.fill(); } }catch(e){}
  try{ const Hh=window.HEAT; if(Hh&&Hh.cops&&Hh.cops.length){ const chase=Hh.state&&Hh.state!=="idle", cone=(Hh.stars||0)<=1, PT=Hh.police&&Hh.police.types; MM2.cops=[];  // POLICE HEAT cops (Rydah Systems): 2D canvas only, 0 WebGL draws
    for(const q of Hh.cops){ let p=T(q.x,q.z); const f=T(q.x+Math.sin(q.ry),q.z+Math.cos(q.ry)), ang=Math.atan2(f[1]-p[1],f[0]-p[0]); const rp=mm2Rim(p,RR);
      if(rp[2]){ if(!chase) continue; p=rp; } MM2.cops.push({id:q.id,x:p[0],y:p[1],ang,onRim:!!rp[2],seeing:!!q.seeing});
      c.save(); c.translate(p[0],p[1]); c.rotate(ang);
      if(cone&&!rp[2]&&PT&&PT[q.type]){ const R=PT[q.type].sight*k, fv=PT[q.type].fov; c.fillStyle=q.seeing?"rgba(255,40,60,.28)":"rgba(255,40,60,.12)"; c.beginPath(); c.moveTo(0,0); c.arc(0,0,R,-fv,fv); c.closePath(); c.fill(); }
      const s=q.seeing?7:5; c.fillStyle=q.seeing?"#FF2040":"#C8102E"; c.strokeStyle=q.seeing?"#fff":"rgba(0,0,0,.6)"; c.lineWidth=q.seeing?2:1; if(q.seeing){ c.shadowColor="#FF2040"; c.shadowBlur=10; }
      c.beginPath(); c.moveTo(s*1.4,0); c.lineTo(-s,-s*.85); c.lineTo(-s*.4,0); c.lineTo(-s,s*.85); c.closePath(); c.fill(); c.stroke(); c.restore(); } } else MM2.cops=[]; }catch(e){}
  const ob=mm2Obj(); MM2.obj=ob;
  if(ob){ const w=T(ob.x,ob.z), m=T(ob.x,P.z); c.save(); c.lineCap=c.lineJoin="round"; c.strokeStyle=col; c.shadowColor=col; c.shadowBlur=12; c.lineWidth=5; c.beginPath(); c.moveTo(px,py); c.lineTo(m[0],m[1]); c.lineTo(w[0],w[1]); c.stroke(); c.shadowBlur=0; c.strokeStyle="rgba(255,255,255,.8)"; c.lineWidth=1.5; c.stroke(); c.restore(); }
  for(const m of icMarkers()){ if(m.kind==="waypoint") continue; let p=T(m.x,m.z); const rp=mm2Rim(p,RR); if(rp[2]){ if(m.kind!=="garage"&&m.kind!=="job") continue; p=rp; MM2.rim.push({kind:m.kind,x:p[0],y:p[1],ang:rp[3],onRim:true}); } mm2Icon(c,m,p[0],p[1],m.kind==="garage"?9:7,sy); }
  if(ob){ let [ox,oy]=T(ob.x,ob.z); const rp=mm2Rim([ox,oy],RR); ox=rp[0]; oy=rp[1]; MM2.rim.push({kind:"objective",x:ox,y:oy,ang:rp[3],onRim:rp[2]});
    if(rp[2]){ c.save(); c.translate(ox,oy); c.rotate(rp[3]); c.fillStyle=col; c.shadowColor=col; c.shadowBlur=10; c.beginPath(); c.moveTo(12,0); c.lineTo(-6,-8); c.lineTo(-6,8); c.closePath(); c.fill(); c.restore(); }
    c.save(); c.translate(ox,oy); c.scale(1,sy); c.fillStyle=col; c.shadowColor=col; c.shadowBlur=10; c.beginPath(); c.moveTo(0,-9); c.lineTo(9,0); c.lineTo(0,9); c.lineTo(-9,0); c.closePath(); c.fill(); c.fillStyle="#fff"; c.beginPath(); c.moveTo(0,-4); c.lineTo(4,0); c.lineTo(0,4); c.lineTo(-4,0); c.fill(); c.restore(); }
  { const ot=mm2ObjText(ob,MM2.dtLast||0); if(ot){ c.save();
      if(MM2.rim.length){ const r=MM2.rim[MM2.rim.length-1]; if(r.kind==="objective"&&r.onRim){ const lx=px+Math.cos(r.ang)*(RR-26), ly=py+Math.sin(r.ang)*(RR-26); c.translate(lx,ly); c.scale(1,sy); c.font="900 15px Arial"; c.textAlign="center"; c.textBaseline="middle"; const w=c.measureText(ot.dtext).width+10;
        c.fillStyle="rgba(8,12,20,.85)"; c.fillRect(-w/2,-10,w,20); c.fillStyle="#fff"; c.fillText(ot.dtext,0,1); c.setTransform(1,0,0,1,0,0); } }
      if(MM2.vr){ c.font="900 20px Arial"; c.textAlign="center"; c.textBaseline="middle"; const t=ot.name.length>18?ot.name.slice(0,17)+"…":ot.name, s2=t+"  "+ot.dtext, w=c.measureText(s2).width+16;
        c.fillStyle="rgba(8,12,20,.85)"; c.fillRect(W/2-w/2,H-34,w,26); c.fillStyle=col; c.fillText(t,W/2-c.measureText(ot.dtext).width/2-4,H-21); c.fillStyle="#fff"; c.textAlign="left"; c.fillText(ot.dtext,W/2+w/2-8-c.measureText(ot.dtext).width,H-21); }
      c.restore(); } }
  { const nx=px+Math.sin(a)*(RR+4), ny=py-Math.cos(a)*(RR+4); MM2.nx=nx; MM2.ny=ny; c.save(); c.translate(nx,ny); c.scale(1,sy); c.fillStyle="rgba(8,12,20,.85)"; c.beginPath(); c.arc(0,0,10,0,7); c.fill(); c.strokeStyle="#FF4D5E"; c.lineWidth=2; c.stroke();
    c.fillStyle="#fff"; c.font="900 13px Arial"; c.textAlign="center"; c.textBaseline="middle"; c.fillText("N",0,1); c.restore(); }
  c.save(); c.translate(0,0); mm2Chevron(c,px,py,11*Math.min(sy,1.4),"#E8B12A"); c.restore();
  if(MM2.tex) MM2.tex.needsUpdate=true; }
// ---- build: DOM (desktop) + quad (VR) + world diamond + edge arrows
function mm2Build(){ const cv=document.createElement("canvas"); cv.width=MM2.W; cv.height=MM2.H; MM2.cv=cv;
  const st=document.createElement("style"); st.textContent=`#skmini,#minimap{display:none!important}
#mm2{position:fixed;right:22px;top:26px;width:250px;height:230px;z-index:20;pointer-events:none;perspective:380px;perspective-origin:50% 0%}
#mm2 canvas{position:absolute;left:5px;top:-20px;width:240px;height:240px;transform:rotateX(${MM2.tilt}deg);transform-origin:50% 100%;
 -webkit-mask-image:radial-gradient(ellipse 62% 62% at 50% 50%,#000 45%,transparent 100%);mask-image:radial-gradient(ellipse 62% 62% at 50% 50%,#000 45%,transparent 100%)}
.mm2a{position:fixed;z-index:19;pointer-events:none;width:30px;height:30px;margin:-15px 0 0 -15px;display:none;filter:drop-shadow(0 0 3px rgba(0,0,0,.8))}
#mm2o{top:262px!important;bottom:auto!important}
#turf#turf{top:300px!important;right:22px!important}
#mm2d{position:fixed;z-index:19;pointer-events:none;width:26px;height:40px;margin:-40px 0 0 -13px;display:none;filter:drop-shadow(0 0 4px rgba(0,0,0,.7))}`;
  document.head.appendChild(st); const b=document.createElement("div"); b.id="mm2"; b.className="hud"; b.appendChild(cv); document.body.appendChild(b); MM2.box=b;
  const d=document.createElement("div"); d.id="mm2d"; d.innerHTML='<svg viewBox="0 0 26 40" width="26" height="40"><path d="M13 1 L25 13 L13 25 L1 13Z" fill="rgba(10,14,22,.55)" stroke="#fff" stroke-width="2"/><path d="M8 15 L13 9 L18 15" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/><path d="M13 27 L13 39" stroke="#fff" stroke-width="1.2" opacity=".6"/></svg><div id="mm2dd" style="font:700 10px Arial;color:#fff;text-align:center;margin-top:-4px;white-space:nowrap;margin-left:-20px;width:66px"></div>';
  document.body.appendChild(d); MM2.diam=d;
  const o=document.createElement("div"); o.id="mm2o"; o.style.cssText="position:fixed;right:22px;top:262px;z-index:20;pointer-events:none;font:900 15px Arial;color:#fff;background:rgba(8,12,20,.72);padding:4px 10px;border-radius:6px;border-left:3px solid #E8B12A;white-space:nowrap;display:none;text-shadow:0 1px 2px #000";
  o.innerHTML='<span id="mm2on"></span> <span id="mm2od" style="color:#E8B12A;margin-left:6px"></span>'; document.body.appendChild(o); MM2.opanel=o;
  for(let i=0;i<3;i++){ const e=document.createElement("div"); e.className="mm2a"; e.innerHTML='<svg viewBox="0 0 30 30" width="30" height="30"><path class="tri" d="M4 15 L14 9 L14 21Z" fill="#fff"/><circle cx="21" cy="15" r="5.5" fill="rgba(10,14,22,.7)" stroke="#fff" stroke-width="1.6"/><circle class="dot" cx="21" cy="15" r="2.2" fill="#fff"/></svg>'; document.body.appendChild(e); MM2.arrows.push(e); }
  // VR quad (lower view, tilted like a map plane) + world diamond sprite
  MM2.tex=new THREE.CanvasTexture(cv); MM2.tex.minFilter=THREE.LinearFilter; MM2.tex.generateMipmaps=false;
  const am=document.createElement("canvas"); am.width=am.height=128; const ag=am.getContext("2d"); ag.fillStyle="rgba(0,0,0,1)"; ag.fillRect(0,0,128,128);
  const gr=ag.createRadialGradient(64,64,30,64,64,64); gr.addColorStop(0,"#fff"); gr.addColorStop(1,"#000"); ag.fillStyle=gr; ag.fillRect(0,0,128,128);
  MM2.quad=new THREE.Mesh(new THREE.PlaneGeometry(.22,.22),new THREE.MeshBasicMaterial({map:MM2.tex,alphaMap:new THREE.CanvasTexture(am),transparent:true,depthTest:false,depthWrite:false,fog:false}));
  MM2.quad.renderOrder=998; MM2.quad.frustumCulled=false; MM2.quad.visible=false; scene.add(MM2.quad);
  const dc=document.createElement("canvas"); dc.width=dc.height=128; const g=dc.getContext("2d"); g.strokeStyle="#fff"; g.fillStyle="rgba(10,14,22,.55)"; g.lineWidth=7; g.beginPath(); g.moveTo(64,8); g.lineTo(120,64); g.lineTo(64,120); g.lineTo(8,64); g.closePath(); g.fill(); g.stroke(); g.lineWidth=9; g.lineCap=g.lineJoin="round"; g.beginPath(); g.moveTo(42,74); g.lineTo(64,50); g.lineTo(86,74); g.stroke();
  MM2.sprite=new THREE.Sprite(new THREE.SpriteMaterial({map:new THREE.CanvasTexture(dc),depthTest:false,depthWrite:false,fog:false,transparent:true})); MM2.sprite.renderOrder=997; MM2.sprite.visible=false; scene.add(MM2.sprite); }
const _mmV=new THREE.Vector3(), _mmQ=new THREE.Quaternion(), _mmE=new THREE.Vector3();
function mm2Indicators(xr,cam){ const P=Ride.group.position, ob=MM2.obj, W=innerWidth, H=innerHeight, col=mm2Crew();
  if(MAP.beacon) MAP.beacon.visible=false;   // replaced by the minimal diamond
  // world diamond (sprite in VR, DOM on desktop)
  if(ob){ const dist=Math.hypot(ob.x-P.x,ob.z-P.z); MM2.sprite.position.set(ob.x,6+Math.min(30,dist*.06),ob.z); const s=Math.max(1.2,dist*.035); MM2.sprite.scale.set(s,s,1); MM2.sprite.visible=xr; } else MM2.sprite.visible=false;
  const show=!xr&&ob; let used=0;
  const cand=[]; if(ob) cand.push({x:ob.x,z:ob.z,col,main:1}); if(!xr){ for(const m of icMarkers()){ if(m.kind!=="job"&&m.kind!=="garage") continue; if(ob&&m.x===ob.x&&m.z===ob.z) continue; cand.push({x:m.x,z:m.z,col:m.kind==="garage"?m.col:"#fff",d:(m.x-P.x)**2+(m.z-P.z)**2}); } }
  const rest=cand.filter(q=>!q.main).sort((a,b)=>a.d-b.d).slice(0,2), list=cand.filter(q=>q.main).concat(rest);
  MM2.diam.style.display="none";
  { const ot=MM2.ot; if(MM2.opanel){ if(ot&&!xr){ MM2.opanel.style.display="block"; MM2.opanel.style.borderLeftColor=col; document.getElementById("mm2on").textContent=ot.name; document.getElementById("mm2od").textContent=ot.dtext; } else MM2.opanel.style.display="none"; } }
  for(const t of list){ _mmV.set(t.x,P.y+4,t.z).project(cam); const behind=_mmV.z>1, sx=(_mmV.x*.5+.5)*W, sy=(-_mmV.y*.5+.5)*H;
    if(!xr&&!behind&&sx>30&&sx<W-30&&sy>30&&sy<H-30){ if(t.main){ const bb=MM2.box&&MM2.box.getBoundingClientRect(); if(bb&&sx>bb.left-14&&sx<bb.right+14&&sy>bb.top&&sy<bb.bottom+44) continue; MM2.diam.style.display="block"; MM2.diam.style.left=sx+"px"; MM2.diam.style.top=sy+"px"; document.getElementById("mm2dd").textContent=mm2Fmt(Math.hypot(t.x-P.x,t.z-P.z)); } continue; }
    if(xr||used>=3) continue; cam.getWorldPosition(_mmE); cam.getWorldQuaternion(_mmQ); _mmV.set(t.x-_mmE.x,0,t.z-_mmE.z).applyQuaternion(_mmQ.clone().invert()); const right=_mmV.x>0;
    const e=MM2.arrows[used++]; e.style.display="block"; e.style.left=(right?W-26:26)+"px"; e.style.top=(H*.5+(used-1)*34*(right?1:1)-17*(list.length>1)+"px");
    e.querySelector("svg").style.transform=right?"scaleX(-1)":""; e.querySelector(".dot").setAttribute("fill",t.col); e.querySelector(".tri").setAttribute("fill",t.main?col:"#fff"); }
  for(let i=used;i<3;i++) MM2.arrows[i].style.display="none"; }
function mm2Tick(dt,xr){ if(!MM2.on) return; if(xr&&!renderer.xr.isPresenting) xr=false;
  const ride=typeof State!=="undefined"&&State.mode==="ride"&&!(typeof MAP!=="undefined"&&MAP.open);
  if(!ride){ if(MM2.box){ MM2.box.style.display="none"; if(MM2.opanel) MM2.opanel.style.display="none"; MM2.quad.visible=MM2.sprite.visible=false; MM2.diam.style.display="none"; MM2.arrows.forEach(e=>e.style.display="none"); } return; }
  if(!MM2.cv) mm2Build(); MM2.box.style.display=xr?"none":"";
  MM2.vr=!!xr; MM2.dtLast=dt; mm2Heading(dt); mm2Draw(); MM2.acc+=dt; if(MM2.acc>=1/MM2.hz){ MM2.acc=0; let cam=camera; if(xr) cam=renderer.xr.getCamera(camera); mm2Indicators(xr,cam); }
  MM2.quad.visible=!!xr;
  if(xr){ const cam=renderer.xr.getCamera(camera); cam.getWorldPosition(_mmE); cam.getWorldQuaternion(_mmQ); const q=MM2.quad;
    // lower-right of view, 0.55 m out, tilted back ~40deg like a map plane (head-locked; cheap single quad)
    q.position.copy(_mmE).add(_mmV.set(.16,-.2,-.55).applyQuaternion(_mmQ)); q.quaternion.copy(_mmQ); q.rotateX(-MM2.tilt*Math.PI/180); } }
window.MM2=MM2; window.mm2Fmt=mm2Fmt; window.mm2Tick=mm2Tick;
// read-only debug state for tests (numbers, not pixels). heading uses Ride.yaw convention; rot = map canvas rotation (rad)
window.MINIMAP={ get state(){ return Object.freeze({heading:MM2.h,rot:MM2.rot,cx:MM2.cx,cz:MM2.cz,scale:MM2.H/MM2.range,moving:MM2.moving,speed:MM2.vs,n:[MM2.nx,MM2.ny],rim:MM2.rim.map(r=>Object.assign({},r)),cops:(MM2.cops||[]).map(r=>Object.assign({},r)),obj:MM2.ot?{name:MM2.ot.name,dist:MM2.ot.dist,text:MM2.ot.text,dtext:MM2.ot.dtext,panel:MM2.opanel?MM2.opanel.textContent.trim():null}:null,W:MM2.W,H:MM2.H}); }, w2s:(x,z)=>mm2W2S(x,z) };
