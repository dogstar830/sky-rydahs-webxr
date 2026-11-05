// ===== Palma City world map (View / M) + upper-right minimap. Shared icon set (icons.js), shared live data.
// World map: one CanvasTexture plane, redrawn (~10 Hz) only while open. Minimap: small DOM canvas, ~10 Hz, desktop only.
const MAP={ open:false, cv:null, tex:null, mesh:null, S:900, W:1600, cx:0, cz:0, zoom:1.6, cur:null, wp:null, dirty:true, beacon:null, locs:[], acc:0, mini:null, miniAcc:0, theme:null };
const MAPF='"Segoe UI","Helvetica Neue",Arial,sans-serif', MAPH='"Arial Black","Segoe UI",Arial,sans-serif';
function mapTheme(){ const t=window.__mapTheme||MAP.theme||((h=>h>=7&&h<19)(new Date().getHours())?"day":"night");
  return t==="day"?{t,bg:"#22344a",water:"#0f5a63",waterHi:"#1a7a84",land:"#3a4660",block:"#46526c",street:"#7a87a3",fill:.26,grid:"rgba(140,230,255,.07)",scan:"rgba(0,0,0,.06)"}
                  :{t,bg:"#070b14",water:"#062a33",waterHi:"#0a3a44",land:"#141a26",block:"#1a2131",street:"#36405a",fill:.2,grid:"rgba(46,230,214,.06)",scan:"rgba(0,0,0,.14)"}; }
function mapLocs(){ const L=[]; for(const d of PALMA.districts){ if(L.some(l=>l.name===d.name)) continue; const b=PALMA.districts.filter(q=>q.name===d.name).sort((p,q)=>(q.box[2]-q.box[0])*(q.box[3]-q.box[1])-(p.box[2]-p.box[0])*(p.box[3]-p.box[1]))[0].box; L.push({kind:"district",name:d.name,x:(b[0]+b[2])/2,z:(b[1]+b[3])/2,col:d.tint}); }
  for(const m of icMarkers()) if(m.kind!=="waypoint") L.push(m); for(const b of PALMA.bridges) L.push({kind:"bridge",name:b.name,x:(b.a[0]+b.b[0])/2,z:(b.a[1]+b.b[1])/2,col:b.css}); return L; }
function mapBuild(){ const c=document.createElement("canvas"); c.width=MAP.W; c.height=MAP.S; MAP.cv=c; MAP.tex=new THREE.CanvasTexture(c); MAP.tex.minFilter=THREE.LinearFilter; MAP.tex.generateMipmaps=false;
  MAP.mesh=new THREE.Mesh(new THREE.PlaneGeometry(1,1),new THREE.MeshBasicMaterial({map:MAP.tex,depthTest:false,depthWrite:false,fog:false})); MAP.mesh.renderOrder=999; MAP.mesh.frustumCulled=false; MAP.mesh.visible=false; scene.add(MAP.mesh);
  const bm=new THREE.Mesh(new THREE.CylinderGeometry(.35,.35,60,6,1,true),new THREE.MeshBasicMaterial({color:0x2EE6D6,transparent:true,opacity:.45,depthWrite:false,fog:false})); bm.position.y=30; bm.visible=false; scene.add(bm); MAP.beacon=bm; }

// ---- BLOCKOUT areas (Palma Builder blockout.js, read at runtime from BLOCKOUT.areas/land/cols/dashPath/ringPaths; nothing hardcoded). 2D canvas only.
function boMapData(){ const B=typeof BLOCKOUT!=="undefined"?BLOCKOUT:null; if(!B||!B.areas) return null; const A=B.areas;
  return { land:B.land||[], cont:(B.cols||[]).filter(c=>c.bo==="container"), beach:A.beach, port:A.port, tower:A.portside_tower, prec:A.gmen_precinct, dash:B.dashPath||null, ring:B.ringPaths||[],
    n:(B.land||[]).length+(B.dashPath?B.dashPath.length:0)+(B.ringPaths||[]).length+(A.gmen_precinct?1:0)+(A.portside_tower?1:0) }; }
function boRect(c,T,x0,z0,x1,z1){ const a=T(x0,z0), b=T(x1,z0), d=T(x1,z1), e=T(x0,z1); c.beginPath(); c.moveTo(a[0],a[1]); c.lineTo(b[0],b[1]); c.lineTo(d[0],d[1]); c.lineTo(e[0],e[1]); c.closePath(); }
function boLine(c,T,P){ c.beginPath(); P.forEach((p,i)=>{ const q=T(p[0],p[1]); i?c.lineTo(q[0],q[1]):c.moveTo(q[0],q[1]); }); }
// landmass: new walkable land (beach pad, port apron) with the island shore stroke, plus sand / container blocks
function boPaintLand(c,T,k,th,mini){ const D=boMapData(); if(!D) return; const day=th.t==="day";
  for(const b of D.land){ boRect(c,T,b[0],b[1],b[2],b[3]); if(!mini){ c.strokeStyle=th.waterHi; c.lineWidth=Math.max(2,6*k); c.stroke(); c.fillStyle=th.land; } else c.fillStyle=day?"rgba(40,56,80,.55)":"rgba(14,20,32,.6)"; c.fill(); }
  if(D.beach){ const b=D.beach.box; boRect(c,T,b[0],D.beach.boardwalk[1],b[2],b[3]); c.fillStyle=day?"rgba(237,232,220,.32)":"rgba(237,232,220,.14)"; c.fill(); }
  c.fillStyle=mini?(day?"rgba(150,170,200,.35)":"rgba(110,130,170,.3)"):th.block; for(const q of D.cont){ boRect(c,T,q.minX,q.minZ,q.maxX,q.maxZ); c.fill(); }
  for(const [a,col] of [[D.tower,"#FFD700"],[D.prec,"#3D7BFF"]]){ if(!a) continue; const w=Array.isArray(a.footprint)?a.footprint[0]:a.footprint, d=Array.isArray(a.footprint)?a.footprint[1]:a.footprint, [x,z]=a.centre;
    boRect(c,T,x-w/2,z-d/2,x+w/2,z+d/2); c.globalAlpha=mini?.55:.7; c.fillStyle=col; c.fill(); c.globalAlpha=1; c.strokeStyle=col; c.lineWidth=Math.max(1,1.2*k); c.stroke(); } }
// roads: beach boulevard + boardwalk, port quay edge, Heights Dash road, boulevard ring (yellow spine)
function boPaintRoads(c,T,k,th,mini,pass){ const D=boMapData(); if(!D) return; const day=th.t==="day"; c.save(); c.lineCap=c.lineJoin="round";
  const road=mini?(pass===0?(day?"rgba(120,200,255,.22)":"rgba(80,170,255,.2)"):(day?"rgba(190,235,255,.9)":"rgba(150,220,255,.85)")):th.street;
  const lw=(m,mm)=>Math.max(1,(mini?(pass===0?mm:1.6):m)*k);
  if(D.beach){ const b=D.beach.box, r=D.beach.road, zm=(r[0]+r[1])/2; boLine(c,T,[[b[0],zm],[b[2],zm]]); c.strokeStyle=road; c.lineWidth=lw(r[1]-r[0],r[1]-r[0]+4); c.stroke();
    const w=D.beach.boardwalk, zw=(w[0]+w[1])/2; boLine(c,T,[[b[0]+4,zw],[b[2]-4,zw]]); c.strokeStyle=mini&&pass?"rgba(255,214,160,.9)":"#9a7a56"; c.lineWidth=lw(w[1]-w[0],w[1]-w[0]+3); c.stroke(); }
  if(D.port){ const a=D.port.apron; boLine(c,T,[[a[0]+.4,a[1]],[a[0]+.4,a[3]]]); c.strokeStyle=mini&&!pass?"rgba(120,200,255,.2)":"#8a6a48"; c.lineWidth=lw(1.2,3); c.stroke();
    const cr=D.port.crane; if(cr&&!mini){ for(const x of cr.legs){ boLine(c,T,[[x,a[1]+1],[x,a[3]-1]]); c.strokeStyle="#9a9aa0"; c.lineWidth=Math.max(1,.6*k); c.stroke(); } boRect(c,T,cr.legs[0]-cr.outreach,cr.cz-2.2,cr.legs[1]+cr.backreach,cr.cz+2.2); c.fillStyle="#d84a2a"; c.globalAlpha=.8; c.fill(); c.globalAlpha=1; } }
  if(D.dash&&D.dash.length>1){ boLine(c,T,D.dash); c.strokeStyle=road; c.lineWidth=lw(7.3,11); c.stroke(); if(!mini||pass){ c.strokeStyle="#7CB342"; c.lineWidth=Math.max(1,(mini?.9:1.4)*k); c.setLineDash([6*k,6*k]); c.stroke(); c.setLineDash([]); } }
  for(const P of D.ring){ if(P.length<2) continue; if(!mini||pass){ boLine(c,T,P); c.strokeStyle="#FFD700"; c.globalAlpha=mini?.75:.85; c.lineWidth=Math.max(1,(mini?1.2:2)*k); c.stroke(); c.globalAlpha=1; } }
  c.restore(); }
// world-map area labels (small, district-label style)
function boPaintLabels(c,T,k){ const D=boMapData(); if(!D) return; const L=[]; if(D.beach){ const b=D.beach.box; L.push(["BEACH · BOARDWALK",(b[0]+b[2])/2,b[3]+8,"#FF2BD6"]); }
  if(D.port){ const a=D.port.apron; L.push(["PORT QUAY",(a[0]+a[2])/2,a[1]-6,"#d84a2a"]); } if(D.tower) L.push(["PORTSIDE TOWER",D.tower.centre[0],D.tower.centre[1]-D.tower.footprint/2-5,"#FFD700"]);
  if(D.dash&&D.dash.length) { const p=D.dash[Math.floor(D.dash.length/2)]; L.push(["HEIGHTS DASH",p[0],p[1]-10,"#7CB342"]); } if(D.ring[0]&&D.ring[0].length){ const p=D.ring[0][Math.floor(D.ring[0].length/2)]; L.push(["BOULEVARD RING",p[0]-30,p[1]+20,"#FFD700"]); }
  if(D.prec) L.push(["G-MEN PRECINCT",D.prec.centre[0],D.prec.centre[1]-D.prec.footprint[1]/2-5,"#3D7BFF"]);
  c.save(); c.textAlign="center"; c.font="900 "+Math.round(Math.max(14,Math.min(24,12*k)))+"px "+MAPH; for(const [t,x,z,col] of L){ const p=T(x,z); c.shadowColor="#000"; c.shadowBlur=6; c.fillStyle=col; c.fillText(t,p[0],p[1]); } c.restore(); }
// shared base-map painter: T(x,z)->[sx,sy], k = px per metre
function mapPaintBase(c,T,k,th,w,h){ c.fillStyle=th.water; c.fillRect(0,0,w,h);
  for(const i of PALMA.islands){ const a=T(i.box[0]-4,i.box[1]-4), b=T(i.box[2]+4,i.box[3]+4); c.beginPath(); c.moveTo(a[0],a[1]); const q=T(i.box[2]+4,i.box[1]-4), r=T(i.box[0]-4,i.box[3]+4); c.lineTo(q[0],q[1]); c.lineTo(b[0],b[1]); c.lineTo(r[0],r[1]); c.closePath(); c.strokeStyle=th.waterHi; c.lineWidth=Math.max(2,6*k); c.stroke(); c.fillStyle=th.land; c.fill(); }
  try{ boPaintLand(c,T,k,th,false); }catch(e){}
  for(const d of PALMA.districts){ const P=[[d.box[0],d.box[1]],[d.box[2],d.box[1]],[d.box[2],d.box[3]],[d.box[0],d.box[3]]].map(p=>T(p[0],p[1])); const poly=()=>{ c.beginPath(); P.forEach((p,i)=>i?c.lineTo(p[0],p[1]):c.moveTo(p[0],p[1])); c.closePath(); };
    poly(); c.globalAlpha=th.fill; c.fillStyle=d.tint; c.fill(); c.globalAlpha=1;
    const cell=26; c.strokeStyle=th.street; c.lineWidth=Math.max(1,2.2*k); c.beginPath();
    for(let x=d.box[0]+cell;x<d.box[2];x+=cell){ const a=T(x,d.box[1]+2), b=T(x,d.box[3]-2); c.moveTo(a[0],a[1]); c.lineTo(b[0],b[1]); }
    for(let z=d.box[1]+cell;z<d.box[3];z+=cell){ const a=T(d.box[0]+2,z), b=T(d.box[2]-2,z); c.moveTo(a[0],a[1]); c.lineTo(b[0],b[1]); } c.stroke();
    poly(); c.globalAlpha=.55; c.strokeStyle=d.tint; c.lineWidth=Math.max(1,1.2*k); c.stroke(); c.globalAlpha=1; }
  try{ boPaintRoads(c,T,k,th,false,1); }catch(e){}
  c.lineCap="round"; for(const br of PALMA.bridges){ const a=T(br.a[0],br.a[1]), b=T(br.b[0],br.b[1]); c.strokeStyle=th.block; c.lineWidth=Math.max(3,7.6*k); c.beginPath(); c.moveTo(a[0],a[1]); c.lineTo(b[0],b[1]); c.stroke(); c.strokeStyle=br.css; c.globalAlpha=.8; c.lineWidth=Math.max(1,1.4*k); c.stroke(); c.globalAlpha=1; }
  for(const t of icTags()){ const p=T(t.x,t.z); if(p[0]<-10||p[1]<-10||p[0]>w+10||p[1]>h+10) continue; c.fillStyle=t.col; c.globalAlpha=.8; c.beginPath(); c.arc(p[0],p[1],Math.max(1.5,1.1*k),0,7); c.fill(); c.globalAlpha=1; } }
function mapRoute(c,a,b,lw){ c.save(); c.setLineDash([lw*.2,lw*2.2]); c.lineCap="round"; c.strokeStyle="#2EE6D6"; c.shadowColor="#2EE6D6"; c.shadowBlur=lw*2; c.lineWidth=lw; c.beginPath(); c.moveTo(a[0],a[1]); c.lineTo(b[0],b[1]); c.stroke(); c.restore(); }
function mapPlayer(c,x,y,rot,s,label){ const t=performance.now()/1000, ph=(t*1.2)%1; c.save(); c.strokeStyle="rgba(232,177,42,"+(1-ph).toFixed(2)+")"; c.lineWidth=3; c.beginPath(); c.arc(x,y,s*(1.1+ph*1.6),0,7); c.stroke(); c.restore();
  icDraw(c,"player",x,y,s,{rot});
  if(label){ c.save(); c.font="900 "+Math.round(s*.85)+"px "+MAPH; const w=c.measureText("YOU").width+16, ty=y-s*2.1; c.fillStyle="#E8B12A"; icRR(c,x-w/2,ty-s*.62,w,s*1.0,6); c.fill(); c.fillStyle="#0B0B10"; c.textAlign="center"; c.fillText("YOU",x,ty+s*.24); c.restore(); } }
function mapW2S(x,z){ const k=MAP.S/720*MAP.zoom; return [MAP.W/2+(x-MAP.cx)*k, MAP.S/2+(z-MAP.cz)*k]; }
function mapDraw(){ const c=MAP.cv.getContext("2d"), S=MAP.S, W=MAP.W, th=mapTheme(), k=S/720*MAP.zoom; MAP.dirty=false;
  mapPaintBase(c,mapW2S,k,th,W,S);
  c.strokeStyle=th.grid; c.lineWidth=1; c.beginPath(); for(let g=-500;g<=500;g+=50){ let a=mapW2S(g,-500), b=mapW2S(g,500); c.moveTo(a[0],a[1]); c.lineTo(b[0],b[1]); a=mapW2S(-500,g); b=mapW2S(500,g); c.moveTo(a[0],a[1]); c.lineTo(b[0],b[1]); } c.stroke();
  c.textAlign="center"; const fs0=Math.round(20+8*Math.min(1.5,MAP.zoom));
  for(const l of MAP.locs){ if(l.kind!=="district") continue; const ds=PALMA.districts.filter(d=>d.name===l.name), bw=Math.max(...ds.map(d=>d.box[2]-d.box[0]))*k*.9; c.font="900 "+fs0+"px "+MAPH; const tw=c.measureText(l.name).width, fs=Math.max(12,Math.min(fs0,fs0*bw/tw)); const p=mapW2S(l.x,l.z); c.save(); c.font="900 "+Math.round(fs)+"px "+MAPH; c.shadowColor=l.col; c.shadowBlur=14; c.fillStyle=l.col; c.globalAlpha=.9; c.fillText(l.name,p[0],p[1]); c.shadowBlur=0; c.globalAlpha=.55; c.fillStyle="#fff"; c.fillText(l.name,p[0],p[1]); c.restore(); }
  try{ boPaintLabels(c,mapW2S,k); }catch(e){}
  const P=Ride.group.position, pp=mapW2S(P.x,P.z);
  if(MAP.wp) mapRoute(c,pp,mapW2S(MAP.wp.x,MAP.wp.z),6);
  const M=icMarkers(), R=Math.round(15+5*Math.min(2,MAP.zoom)); M.sort((a,b)=>(a.kind==="garage")-(b.kind==="garage")); for(const m of M){ const p=mapW2S(m.x,m.z); icDraw(c,m.kind,p[0],p[1],m.kind==="garage"?R*1.2:R,{col:m.col,crew:m.crew,dim:m.dim}); }
  if(MAP.cur){ const p=mapW2S(MAP.cur.x,MAP.cur.z), t=performance.now()/300; c.save(); c.strokeStyle="#fff"; c.lineWidth=3; c.setLineDash([10,6]); c.lineDashOffset=-t*6; icRR(c,p[0]-R*1.9,p[1]-R*1.9,R*3.8,R*3.8,12); c.stroke(); c.restore(); }
  try{ MAP.copsDrawn=[]; const Hh=window.HEAT; if(Hh&&Hh.cops) for(const q of Hh.cops){ const p=mapW2S(q.x,q.z), ang=Math.atan2(Math.cos(q.ry),Math.sin(q.ry)), s=R*(q.seeing?.75:.55); MAP.copsDrawn.push({id:q.id,x:p[0],y:p[1],ang,seeing:!!q.seeing});  // POLICE HEAT cops (read-only, north-up)
    c.save(); c.translate(p[0],p[1]); c.rotate(ang); c.fillStyle=q.seeing?"#FF2040":"#C8102E"; c.strokeStyle=q.seeing?"#fff":"rgba(0,0,0,.7)"; c.lineWidth=q.seeing?3:2; if(q.seeing){ c.shadowColor="#FF2040"; c.shadowBlur=14; }
    c.beginPath(); c.moveTo(s*1.4,0); c.lineTo(-s,-s*.85); c.lineTo(-s*.4,0); c.lineTo(-s,s*.85); c.closePath(); c.fill(); c.stroke(); c.restore(); } }catch(e){}
  mapPlayer(c,pp[0],pp[1],Math.PI-Ride.yaw,R*1.1,true);
  for(let y=0;y<S;y+=4){ c.fillStyle=th.scan; c.fillRect(0,y,W,1); }
  // header (glass) + selected name
  c.save(); c.fillStyle="rgba(8,12,22,.68)"; c.fillRect(0,0,W,78); c.fillStyle="#E8B12A"; c.fillRect(0,76,W,2);
  c.textAlign="left"; c.font="900 38px "+MAPH; c.fillStyle="#E8B12A"; c.shadowColor="#E8B12A"; c.shadowBlur=12; c.fillText("PALMA CITY",28,52); c.shadowBlur=0;
  c.textAlign="right"; c.font="800 30px "+MAPF; c.fillStyle=MAP.cur?"#FFFFFF":"#9AA6BC"; c.fillText(MAP.cur?MAP.cur.name:"D-PAD  SELECT A LOCATION",W-28,50); c.restore();
  // legend: glass card
  const LG=ICON.CAT, rowH=50, lw=430, lh=LG.length*rowH+70, lx=W-lw-24, ly=S-lh-70; c.save(); c.fillStyle="rgba(10,16,30,.62)"; c.strokeStyle="rgba(140,230,255,.35)"; c.lineWidth=2; icRR(c,lx,ly,lw,lh,18); c.fill(); c.stroke();
  c.fillStyle="#2EE6D6"; c.font="900 24px "+MAPH; c.textAlign="left"; c.fillText("LEGEND",lx+22,ly+40);
  LG.forEach(([kd,name,col],i)=>{ const y=ly+70+i*rowH+8; icDraw(c,kd,lx+42,y,17,{col,crew:"karasu"}); c.fillStyle="#F5F2E8"; c.font="700 23px "+MAPF; c.fillText(name,lx+80,y+8); }); c.restore();
  c.save(); c.fillStyle="rgba(8,12,22,.68)"; c.fillRect(0,S-56,W,56); c.fillStyle="#F5F2E8"; c.font="700 24px "+MAPF; c.textAlign="left";
  c.fillText("LS  PAN    RT/LT  ZOOM    D-PAD  SELECT    A  WAYPOINT    B / VIEW  CLOSE",28,S-19); c.restore();
  MAP.tex.needsUpdate=true; }
function mapSet(v){ if(!MAP.cv) mapBuild(); MAP.open=!!v; MAP.mesh.visible=MAP.open; if(MAP.open){ MAP.locs=mapLocs(); const p=Ride.group.position; MAP.cx=p.x; MAP.cz=p.z; MAP.zoom=1.6; MAP.cur=null; MAP.dirty=true; if(typeof PHONE!=="undefined"&&PHONE.up) phoneSet(false); }
  if(MAP.mini) MAP.mini.style.visibility=MAP.open?"hidden":""; }
function mapPick(dir){ const L=MAP.locs, o=MAP.cur||{x:MAP.cx,z:MAP.cz}; const v={up:[0,-1],down:[0,1],left:[-1,0],right:[1,0]}[dir]; let best=null, bs=1e9;
  for(const l of L){ if(l===MAP.cur) continue; const dx=l.x-o.x, dz=l.z-o.z, along=dx*v[0]+dz*v[1]; if(along<=1) continue; const side=Math.abs(dx*v[1]-dz*v[0]), sc=along+side*2; if(sc<bs){ bs=sc; best=l; } }
  if(best){ MAP.cur=best; MAP.cx=best.x; MAP.cz=best.z; MAP.dirty=true; } }
function mapWaypoint(){ const l=MAP.cur||{x:MAP.cx,z:MAP.cz,name:"MARKER"}; MAP.wp={x:l.x,z:l.z,name:l.name}; MAP.dirty=true; if(MAP.beacon){ MAP.beacon.position.set(l.x,30,l.z); MAP.beacon.visible=true; } try{ flash("WAYPOINT SET"); }catch(e){} }
function mapInput(R,dt){ if(R&&R.gp){ const [lx,ly,lm]=R.ls; if(lm>0){ MAP.cx+=lx*dt*260/MAP.zoom; MAP.cz+=ly*dt*260/MAP.zoom; MAP.cur=null; MAP.dirty=true; }
    const zi=R.v(7), zo=R.v(6); if(zi>.3||zo>.3){ MAP.zoom=THREE.MathUtils.clamp(MAP.zoom*Math.exp((zi-zo)*dt*1.8),.6,5); MAP.dirty=true; }
    if(R.e(12)) mapPick("up"); if(R.e(13)) mapPick("down"); if(R.e(14)) mapPick("left"); if(R.e(15)) mapPick("right"); if(R.e(0)) mapWaypoint(); if(R.e(1)||R.e(8)) mapSet(false); }
  MAP.cx=THREE.MathUtils.clamp(MAP.cx,-300,380); MAP.cz=THREE.MathUtils.clamp(MAP.cz,-420,240); }
addEventListener("keydown",e=>{ if(typeof State==="undefined"||State.mode!=="ride") return; const c=e.code;
  if(c==="KeyM"&&!e.repeat){ mapSet(!MAP.open); e.preventDefault(); e.stopImmediatePropagation(); return; }
  if(!MAP.open) return; const d={ArrowUp:"up",ArrowDown:"down",ArrowLeft:"left",ArrowRight:"right"}[c];
  if(d){ if(!e.repeat) mapPick(d); } else if(c==="Enter") mapWaypoint(); else if(c==="Escape"||c==="Backspace") mapSet(false); else if(c==="Equal") { MAP.zoom=Math.min(5,MAP.zoom*1.25); MAP.dirty=true; } else if(c==="Minus"){ MAP.zoom=Math.max(.6,MAP.zoom/1.25); MAP.dirty=true; } else return;
  e.preventDefault(); e.stopImmediatePropagation(); },{capture:true});
// ---- minimap (upper right, rotates with player, arrow fixed at centre, 10 Hz) ----
const MINI={ px:176, dpr:2, range:95 };
function miniBuild(){ const c=document.createElement("canvas"); c.id="skmini"; c.width=c.height=MINI.px*MINI.dpr; c.className="hud";
  c.style.cssText="position:fixed;top:14px;right:16px;width:"+MINI.px+"px;height:"+MINI.px+"px;z-index:20;pointer-events:none;border-radius:50%";
  document.body.appendChild(c); MAP.mini=c; const st=document.createElement("style");
  st.textContent="#minimap{display:none!important} #turf{top:"+(MINI.px+28)+"px!important}"; document.head.appendChild(st); }
function miniDraw(){ const cv=MAP.mini, c=cv.getContext("2d"), D=cv.width, C=D/2, Rr=C-6*MINI.dpr, th=mapTheme(), k=Rr/MINI.range, P=Ride.group.position, y=Ride.yaw;
  const fx=Math.sin(y), fz=Math.cos(y), a=-Math.PI/2-Math.atan2(fz,fx), ca=Math.cos(a), sa=Math.sin(a);
  const T=(x,z)=>{ const dx=(x-P.x)*k, dz=(z-P.z)*k; return [C+dx*ca-dz*sa, C+dx*sa+dz*ca]; };
  c.clearRect(0,0,D,D); c.save(); c.beginPath(); c.arc(C,C,Rr,0,7); c.clip(); mapPaintBase(c,T,k,th,D,D);
  for(let yy=0;yy<D;yy+=4) { c.fillStyle=th.scan; c.fillRect(0,yy,D,1); }
  if(MAP.wp){ const w=T(MAP.wp.x,MAP.wp.z); mapRoute(c,[C,C],w,3*MINI.dpr); } c.restore();
  const ir=11*MINI.dpr;
  for(const m of icMarkers()){ let [sx,sy]=T(m.x,m.z); const dx=sx-C, dy=sy-C, d=Math.hypot(dx,dy), lim=Rr-ir*.9; let edge=false;
    if(d>lim){ sx=C+dx/d*lim; sy=C+dy/d*lim; edge=true; }
    if(edge&&m.kind==="waypoint"){ const ang=Math.atan2(dy,dx); c.save(); c.translate(C+dx/d*(Rr-2*MINI.dpr),C+dy/d*(Rr-2*MINI.dpr)); c.rotate(ang); c.fillStyle="#2EE6D6"; c.shadowColor="#2EE6D6"; c.shadowBlur=10; c.beginPath(); c.moveTo(4*MINI.dpr,0); c.lineTo(-9*MINI.dpr,-8*MINI.dpr); c.lineTo(-9*MINI.dpr,8*MINI.dpr); c.closePath(); c.fill(); c.restore(); continue; }
    icDraw(c,m.kind,sx,sy,edge?ir*.72:ir,{col:m.col,crew:m.crew,dim:m.dim||edge}); }
  // rim + N marker
  c.save(); c.lineWidth=4*MINI.dpr; c.strokeStyle="#2EE6D6"; c.shadowColor="#2EE6D6"; c.shadowBlur=14; c.beginPath(); c.arc(C,C,Rr,0,7); c.stroke(); c.shadowBlur=0; c.lineWidth=1.5*MINI.dpr; c.strokeStyle="#05060C"; c.beginPath(); c.arc(C,C,Rr+2.6*MINI.dpr,0,7); c.stroke(); c.restore();
  const n=T(P.x,P.z-1e4), nd=Math.hypot(n[0]-C,n[1]-C), nx=C+(n[0]-C)/nd*Rr, ny=C+(n[1]-C)/nd*Rr; c.save(); c.fillStyle="#0D1020"; c.strokeStyle="#FFFFFF"; c.lineWidth=2*MINI.dpr; c.beginPath(); c.arc(nx,ny,9*MINI.dpr,0,7); c.fill(); c.stroke();
  c.fillStyle="#FFFFFF"; c.font="900 "+(11*MINI.dpr)+"px "+MAPH; c.textAlign="center"; c.textBaseline="middle"; c.fillText("N",nx,ny+.5*MINI.dpr); c.restore();
  mapPlayer(c,C,C,0,10*MINI.dpr,false); }
function mapTick(dt,xr){ if(xr&&!renderer.xr.isPresenting) xr=false;
  if(!xr&&State.mode==="ride"&&!(typeof MM2!=="undefined"&&!/minimap=old/.test(location.search))){ if(!MAP.mini) miniBuild(); MAP.mini.style.display=""; MINI_T: { MAP.miniAcc+=dt; if(MAP.miniAcc>=.1&&!MAP.open){ MAP.miniAcc=0; miniDraw(); } } }
  else if(MAP.mini) MAP.mini.style.display="none";
  if(!MAP.open||!MAP.mesh) return; if(State.mode!=="ride"){ mapSet(false); return; }
  MAP.acc+=dt; if(MAP.acc>=.1){ MAP.acc=0; MAP.dirty=true; } if(MAP.dirty) mapDraw();
  const m=MAP.mesh; let cam=camera; if(xr) cam=renderer.xr.getCamera(camera);
  const dist=xr?1.2:.5, h=xr?1.1:2*Math.tan(THREE.MathUtils.degToRad(camera.fov/2))*dist, asp=xr?16/9:Math.max(16/9,camera.aspect||16/9); m.scale.set(h*asp,h*(asp>16/9?asp/(16/9):1),1);
  cam.getWorldPosition(m.position); const q=new THREE.Quaternion(); cam.getWorldQuaternion(q); m.quaternion.copy(q); m.position.add(new THREE.Vector3(0,0,-dist).applyQuaternion(q)); }
window.MAP=MAP; window.mapSet=mapSet; window.mapTick=mapTick; window.miniDraw=miniDraw;
