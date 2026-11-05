// ===== Sky Rydahs shared map icon set (Air Gear motifs). Used by BOTH the world map and the minimap. Procedural canvas, no text.
const ICON={ dark:"#0D1020", ink:"#05060C",
  CAT:[["garage","CREW GARAGE / BASE","#FFD700"],["gate","CREW GATE (LOCKED)","#00E5FF"],["job","JOB / MISSION","#FFC83A"],["shop","A·T PARTS SHOP","#8CE6FF"],["pod","SAVE POD (CHECKPOINT)","#7CFFB2"],["tag","TURF TAG","#FF2BD6"],["police","POLICE HEAT","#FF3344"],["waypoint","WAYPOINT","#2EE6D6"],["player","YOU (A·T)","#E8B12A"]],
  col(k){ const c=ICON.CAT.find(c=>c[0]===k); return c?c[2]:"#fff"; } };
function icRR(c,x,y,w,h,r){ c.beginPath(); c.moveTo(x+r,y); c.arcTo(x+w,y,x+w,y+h,r); c.arcTo(x+w,y+h,x,y+h,r); c.arcTo(x,y+h,x,y,r); c.arcTo(x,y,x+w,y,r); c.closePath(); }
function icWing(c,s,sd){ c.save(); c.scale(sd,1); c.beginPath(); c.moveTo(.1*s,.1*s); c.quadraticCurveTo(.55*s,-.55*s,1.05*s,-.45*s); c.lineTo(.62*s,-.18*s); c.lineTo(.9*s,-.12*s); c.lineTo(.52*s,.05*s); c.lineTo(.72*s,.12*s); c.lineTo(.3*s,.26*s); c.closePath(); c.fill(); c.stroke(); c.restore(); }
// crew emblem silhouettes (simplified, procedural)
function icCrew(c,crew,s,col){ c.fillStyle=col; c.strokeStyle=col; c.lineWidth=Math.max(1.5,s*.12); c.lineJoin="round"; c.lineCap="round";
  if(crew==="karasu"){ c.strokeStyle=ICON.ink; c.lineWidth=Math.max(1,s*.06); icWing(c,s*.9,1); icWing(c,s*.9,-1); c.beginPath(); c.moveTo(0,-.45*s); c.lineTo(.22*s,.2*s); c.lineTo(0,.5*s); c.lineTo(-.22*s,.2*s); c.closePath(); c.fill(); }
  else if(crew==="static"){ c.strokeStyle=ICON.ink; c.lineWidth=Math.max(1,s*.06); icWing(c,s*.8,1); icWing(c,s*.8,-1); c.strokeStyle=col; c.lineWidth=Math.max(1.5,s*.12); c.beginPath(); c.ellipse(0,-.52*s,.36*s,.12*s,0,0,7); c.stroke(); }
  else if(crew==="behemoth"){ c.beginPath(); c.arc(0,-.05*s,.42*s,0,7); c.fill(); c.fillRect(-.24*s,.25*s,.48*s,.25*s); c.fillStyle=ICON.dark; c.beginPath(); c.arc(-.16*s,-.05*s,.11*s,0,7); c.arc(.16*s,-.05*s,.11*s,0,7); c.fill(); for(const sd of[-1,1]){ c.beginPath(); c.moveTo(sd*.3*s,-.35*s); c.quadraticCurveTo(sd*.75*s,-.55*s,sd*.6*s,-.05*s); c.stroke(); } }
  else if(crew==="anubis"){ c.beginPath(); c.moveTo(-.28*s,-.62*s); c.lineTo(-.1*s,-.2*s); c.lineTo(.1*s,-.2*s); c.lineTo(.28*s,-.62*s); c.lineTo(.36*s,-.05*s); c.lineTo(.62*s,.25*s); c.lineTo(.18*s,.3*s); c.lineTo(0,.6*s); c.lineTo(-.18*s,.3*s); c.lineTo(-.36*s,-.05*s); c.closePath(); c.fill(); }
  else if(crew==="genesis"){ for(let k=0;k<3;k++){ c.beginPath(); c.moveTo(-.55*s,(-.4+k*.3)*s); c.lineTo(0,(-.1+k*.3)*s); c.lineTo(.55*s,(-.4+k*.3)*s); c.stroke(); } }
  else if(crew==="ttt"){ for(const r of[.7,-.7]){ c.save(); c.rotate(r); c.fillRect(-.07*s,-.55*s,.14*s,1.05*s); c.fillRect(-.24*s,-.62*s,.48*s,.2*s); c.restore(); } }
  else if(crew==="forest"){ c.fillRect(-.07*s,0,.14*s,.6*s); for(const sd of[-1,1]){ c.beginPath(); c.moveTo(0,.15*s); c.quadraticCurveTo(sd*.55*s,0,sd*.45*s,-.45*s); c.quadraticCurveTo(sd*.1*s,-.3*s,0,.15*s); c.fill(); } c.beginPath(); c.moveTo(0,-.62*s); c.quadraticCurveTo(.2*s,-.3*s,0,-.05*s); c.quadraticCurveTo(-.2*s,-.3*s,0,-.62*s); c.fill(); }
  else { /* codee: wheel-E chevron */ c.beginPath(); c.arc(0,0,.5*s,0,7); c.stroke(); for(let k=-1;k<=1;k++){ c.fillRect(-.22*s,(k*.24-.05)*s,.5*s,.1*s); } c.fillRect(-.26*s,-.34*s,.1*s,.68*s); } }
// one badge: rounded dark plate + neon rim + glow, symbol inside. kind, x,y centre, r radius, o:{col,crew,dim}
function icDraw(c,kind,x,y,r,o){ o=o||{}; const col=o.col||ICON.col(kind); c.save(); c.translate(x,y); if(o.dim) c.globalAlpha*=.45;
  if(kind==="player"){ const s=r; c.rotate(o.rot||0); c.shadowColor=col; c.shadowBlur=s*.8; c.fillStyle=col; c.strokeStyle=ICON.ink; c.lineWidth=Math.max(1.5,s*.1);
    icWing(c,s*.85,1); icWing(c,s*.85,-1); c.beginPath(); c.moveTo(0,-1.05*s); c.lineTo(.42*s,.55*s); c.lineTo(0,.3*s); c.lineTo(-.42*s,.55*s); c.closePath(); c.fill(); c.stroke();
    c.shadowBlur=0; c.fillStyle=ICON.ink; c.beginPath(); c.arc(-.22*s,.62*s,.12*s,0,7); c.arc(.22*s,.62*s,.12*s,0,7); c.fill(); c.restore(); return; }
  const w=r*2, rr=r*.42; c.shadowColor=col; c.shadowBlur=r*.7; icRR(c,-r,-r,w,w,rr); c.fillStyle=ICON.dark; c.fill(); c.lineWidth=Math.max(1.5,r*.16); c.strokeStyle=col; c.stroke(); c.shadowBlur=0;
  c.lineWidth=Math.max(1,r*.07); c.strokeStyle=ICON.ink; icRR(c,-r-c.lineWidth*1.5,-r-c.lineWidth*1.5,w+c.lineWidth*3,w+c.lineWidth*3,rr*1.2); c.stroke();
  const s=r*.8; c.fillStyle=col; c.strokeStyle=col; c.lineJoin="round"; c.lineCap="round"; c.lineWidth=Math.max(1.5,s*.14);
  if(kind==="garage") icCrew(c,o.crew,s,col);
  else if(kind==="gate"){ c.beginPath(); c.arc(0,-.2*s,.32*s,Math.PI,0); c.stroke(); icRR(c,-.5*s,-.2*s,s,.75*s,.12*s); c.fill(); c.fillStyle=ICON.dark; c.beginPath(); c.moveTo(.08*s,-.12*s); c.lineTo(-.18*s,.22*s); c.lineTo(0,.22*s); c.lineTo(-.1*s,.5*s); c.lineTo(.2*s,.12*s); c.lineTo(.02*s,.12*s); c.closePath(); c.fill(); }
  else if(kind==="job"){ c.beginPath(); c.moveTo(-.6*s,.35*s); c.lineTo(-.6*s,-.35*s); c.lineTo(-.3*s,0); c.lineTo(0,-.55*s); c.lineTo(.3*s,0); c.lineTo(.6*s,-.35*s); c.lineTo(.6*s,.35*s); c.closePath(); c.fill(); c.fillRect(-.6*s,.45*s,1.2*s,.14*s); c.fillStyle=ICON.dark; c.beginPath(); c.arc(0,.12*s,.12*s,0,7); c.fill(); }
  else if(kind==="shop"){ c.beginPath(); for(let i=0;i<16;i++){ const a=i*Math.PI/8, q=i%2?.48*s:.62*s; c.lineTo(Math.cos(a)*q,Math.sin(a)*q); } c.closePath(); c.fill(); c.fillStyle=ICON.dark; c.beginPath(); c.arc(0,0,.3*s,0,7); c.fill(); c.fillStyle=col; c.beginPath(); c.arc(0,0,.1*s,0,7); c.fill(); for(let k=0;k<3;k++){ c.save(); c.rotate(k*2.094); c.fillRect(-.04*s,-.3*s,.08*s,.22*s); c.restore(); } }
  else if(kind==="pod"){ c.save(); c.rotate(-.6); icRR(c,-.3*s,-.62*s,.6*s,1.24*s,.3*s); c.stroke(); c.beginPath(); c.moveTo(-.3*s,0); c.lineTo(.3*s,0); c.stroke(); icRR(c,-.3*s,-.62*s,.6*s,.62*s,.3*s); c.globalAlpha*=.6; c.fill(); c.restore(); }
  else if(kind==="tag"){ icRR(c,-.22*s,-.2*s,.44*s,.78*s,.08*s); c.fill(); c.fillRect(-.08*s,-.36*s,.16*s,.16*s); c.beginPath(); for(const [dx,dy,rd] of [[.36,-.42,.07],[.5,-.3,.05],[.5,-.52,.05],[.62,-.4,.04]]){ c.moveTo(dx*s+rd*s,dy*s); c.arc(dx*s,dy*s,rd*s,0,7); } c.fill(); c.fillStyle=ICON.dark; c.fillRect(-.22*s,.05*s,.44*s,.1*s); }
  else if(kind==="police"){ c.beginPath(); c.moveTo(-.4*s,.3*s); c.lineTo(-.4*s,-.05*s); c.arc(0,-.05*s,.4*s,Math.PI,0); c.lineTo(.4*s,.3*s); c.closePath(); c.fill(); c.fillRect(-.55*s,.35*s,1.1*s,.18*s); c.lineWidth=Math.max(1,s*.1); for(const a of [-2.4,-1.57,-.74]){ c.beginPath(); c.moveTo(Math.cos(a)*.55*s,-.05*s+Math.sin(a)*.55*s); c.lineTo(Math.cos(a)*.75*s,-.05*s+Math.sin(a)*.75*s); c.stroke(); } }
  else if(kind==="waypoint"){ c.beginPath(); c.arc(0,-.15*s,.38*s,Math.PI*.85,Math.PI*.15); c.lineTo(0,.62*s); c.closePath(); c.fill(); c.fillStyle=ICON.dark; c.beginPath(); c.arc(0,-.15*s,.15*s,0,7); c.fill(); }
  c.restore(); }
// live marker list from the actual world data (same for both maps)
function icMarkers(){ const M=[]; const GR=typeof garages!=="undefined"&&garages.length?garages:PALMA.garages;
  for(const g of GR){ M.push({kind:"garage",x:g.pos[0],z:g.pos[1],col:g.color,crew:g.crew,name:g.name+" GARAGE"});
    if(g.gate&&g.cp){ const open=g.gate.state&&g.gate.state!=="closed"; M.push({kind:"gate",x:g.cp[0],z:g.cp[1],col:g.color,crew:g.crew,name:g.name+(open?" GATE (OPEN)":" GATE"),dim:open}); } }
  for(const m of PALMA.missions) M.push({kind:"job",x:m.pos[0],z:m.pos[1],col:(typeof MCOL!=="undefined"&&MCOL[m.type])||ICON.col("job"),name:m.title});
  const sh=PALMA.shops||[{name:"A·T PARTS · CODE : E",pos:[(PALMA.garages.find(g=>g.crew==="codee")||{pos:[0,0]}).pos[0]+3,(PALMA.garages.find(g=>g.crew==="codee")||{pos:[0,0]}).pos[1]+12]}];
  for(const s of sh) M.push({kind:"shop",x:s.pos[0],z:s.pos[1],name:s.name});
  try{ const g=GR.find(g=>g.crew===lastCrew); if(g) M.push({kind:"pod",x:g.pos[0]-8,z:g.pos[1]+8,name:"SAVE POD · "+g.name}); }catch(e){}
  for(const p of (PALMA.pods||[])) M.push({kind:"pod",x:p.pos[0],z:p.pos[1],name:p.name||"SAVE POD"});
  // POLICE: G-Men precinct (blockout.js runtime BLOCKOUT.areas.gmen_precinct) is the main HQ; old Portside North spot (60,-70) = substation
  { const gp=(typeof BLOCKOUT!=="undefined"&&BLOCKOUT.areas&&BLOCKOUT.areas.gmen_precinct)||null;
    if(gp){ M.push({kind:"police",x:gp.centre[0],z:gp.centre[1],name:"G-MEN PRECINCT · POLICE HQ",hq:true}); M.push({kind:"police",x:60,z:-70,name:"G-MEN SUBSTATION · PORTSIDE N",dim:true}); }
    else M.push({kind:"police",x:60,z:-70,name:"POLICE HQ · HEAT"}); }
  if(typeof MAP!=="undefined"&&MAP.wp) M.push({kind:"waypoint",x:MAP.wp.x,z:MAP.wp.z,name:"WAYPOINT · "+MAP.wp.name});
  return M; }
function icTags(){ const T=[]; if(typeof TURF!=="undefined"&&TURF.spots) for(const s of TURF.spots){ let col="#5a5f70"; try{ const cr=s.owner>=0?TURF.crews[s.owner]:null; if(cr) col=cr.css||cr.color||col; }catch(e){} T.push({x:s.x,z:s.z,col}); } return T; }
window.ICON=ICON; window.icDraw=icDraw; window.icMarkers=icMarkers;
