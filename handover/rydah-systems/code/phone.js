// ===== iLink phone (GTA V-style crew phone). Xbox pad: see pad.js (D-pad Up raise/lower, D-pad move, A select, B back). Desktop: Up/Tab raise · arrows move · Enter select · Backspace/Esc back. VR: left hand, Y/X raise, left stick move, left trigger select, B/Y back.
const PHONE={ up:false, t:0, app:"home", sel:0, dirty:true, acc:0, W:512, H:896, gold:"#E8B12A", cyan:"#2EE6D6",
  apps:[["Jobs","☰"],["Map","◈"],["Crew","✉"],["Hack","⌬"],["Stats","▮"],["Ping","◎"],["Snap","◐"],["Settings","⚙"],["Event","★"]],
  jobs:[{t:"Ride to a crew garage",d:false},{t:"Tag 3 walls",d:false},{t:"Collect 10 cans",d:false}],
  msgs:[{f:"CODEE",t:"Yo. Phone's live. Keep it on you."}], replies:null, rsel:0, offerSent:false, badge:{Crew:0,Jobs:0},
  hack:null, prevXR:{}, axLock:false, lastClock:"" };
const PH_CTRL=["XBOX PAD (Apex/CoD style)","LS move/steer   RS camera","L3 boost  A jump/wallride/grind pop","B back · slide/cancel grind","X action: pick up/gate/hold hack","D-LEFT grapple (at marked points)","RB melee: tap light · hold heavy","RT special  LB L-special  LT lock-on","Y trick  R3 crew  RT+Y ult","D-UP phone   D-DOWN ping","VIEW world map   MENU pause","MAP: LS pan RT/LT zoom D-pad","MAP: A waypoint  B/VIEW close","PHONE: D-pad move A ok B back","KEYS: WASD SPACE J K L SHIFT","KEYS: UP/TAB phone M map G grapple Q aim"];
function phoneBuild(){
  const cv=document.createElement("canvas"); cv.width=PHONE.W; cv.height=PHONE.H; PHONE.cv=cv; PHONE.cx=cv.getContext("2d");
  const tex=new THREE.CanvasTexture(cv); tex.anisotropy=4; PHONE.tex=tex;
  const g=new THREE.Group(); g.name="iLink";
  const M=c=>new THREE.MeshBasicMaterial({color:c,depthTest:false,depthWrite:false,toneMapped:false,fog:false});
  const edge=new THREE.Mesh(new THREE.BoxGeometry(.078,.142,.009),M(0xE8B12A)); edge.renderOrder=997;
  const body=new THREE.Mesh(new THREE.BoxGeometry(.074,.138,.011),M(0x050506)); body.renderOrder=998;
  const scr=new THREE.Mesh(new THREE.PlaneGeometry(.066,.1155),new THREE.MeshBasicMaterial({map:tex,depthTest:false,depthWrite:false,toneMapped:false,fog:false})); scr.position.z=.0061; scr.renderOrder=999;
  g.add(edge,body,scr); for(const m of g.children) m.frustumCulled=false; g.visible=false; scene.add(g); PHONE.g=g; return g;
}
function phRR(c,x,y,w,h,r){ c.beginPath(); c.moveTo(x+r,y); c.arcTo(x+w,y,x+w,y+h,r); c.arcTo(x+w,y+h,x,y+h,r); c.arcTo(x,y+h,x,y,r); c.arcTo(x,y,x+w,y,r); c.closePath(); }
function phTxt(c,s,x,y,sz,col,al,wt){ c.font=(wt||"600")+" "+sz+"px 'Segoe UI',Arial,sans-serif"; c.fillStyle=col||"#F5F2E8"; c.textAlign=al||"left"; c.fillText(s,x,y); }
function phWrap(c,s,x,y,w,lh,sz,col){ c.font="500 "+sz+"px 'Segoe UI',Arial,sans-serif"; const ws=s.split(" "); let ln="", n=0; for(const wd of ws){ const t=ln?ln+" "+wd:wd; if(c.measureText(t).width>w&&ln){ phTxt(c,ln,x,y+n*lh,sz,col,"left","500"); ln=wd; n++; } else ln=t; } phTxt(c,ln,x,y+n*lh,sz,col,"left","500"); return n+1; }
function phoneDraw(){
  const c=PHONE.cx, W=PHONE.W, H=PHONE.H, G=PHONE.gold; c.fillStyle="#0B0B0D"; c.fillRect(0,0,W,H);
  const d=new Date(), clk=String(d.getHours()).padStart(2,"0")+":"+String(d.getMinutes()).padStart(2,"0"); PHONE.lastClock=clk;
  let turf=0; try{ if(TURF.ready){ const own=Object.values(TURF.spots||{}); } }catch(e){}
  phTxt(c,"iLink",22,40,26,G,"left","800"); phTxt(c,clk,W/2,40,26,"#F5F2E8","center");
  for(let i=0;i<4;i++){ c.fillStyle=i<3?G:"#3a3628"; c.fillRect(W-110+i*14,38-8-i*6,9,8+i*6); } phTxt(c,"▮",W-30,40,22,PHONE.cyan,"center");
  c.fillStyle="#16161A"; c.fillRect(0,60,W,64); c.fillStyle=G; c.fillRect(0,121,W,3);
  const title=PHONE.app==="home"?PHONE.apps[PHONE.sel][0]:PHONE.app; phTxt(c,title.toUpperCase(),W/2,104,36,G,"center","800");
  const f=window["phApp_"+PHONE.app]; if(f) f(c,W,H,G); else phStub(c,W,H,G);
  c.fillStyle="#16161A"; c.fillRect(0,H-70,W,70); phTxt(c,"✓ SELECT",30,H-26,26,G,"left","700"); phTxt(c,"↩ BACK",W-30,H-26,26,"#FF4D3D","right","700");
  PHONE.tex.needsUpdate=true; PHONE.dirty=false;
}
window.phApp_home=(c,W,H,G)=>{ const s=150, ox=(W-3*s)/2, oy=160;
  PHONE.apps.forEach(([n,ic],i)=>{ const x=ox+(i%3)*s, y=oy+Math.floor(i/3)*(s+50), on=i===PHONE.sel, dim=n==="Hack"&&!phNearGate(60);
    phRR(c,x+10,y+10,s-20,s-20,22); c.fillStyle=on?G:"#16161A"; c.fill(); c.lineWidth=3; c.strokeStyle=on?"#FFD15C":"#2a2820"; c.stroke();
    phTxt(c,ic,x+s/2,y+s/2+26,70,on?"#0B0B0D":(dim?"#5a5648":G),"center","700"); phTxt(c,n,x+s/2,y+s+24,24,on?G:"#9A968C","center","600");
    const b=PHONE.badge[n]; if(b){ c.beginPath(); c.arc(x+s-22,y+22,18,0,7); c.fillStyle="#FF4D3D"; c.fill(); phTxt(c,String(b),x+s-22,y+31,24,"#fff","center","800"); } }); };
window.phApp_Jobs=(c,W,H,G)=>{ phJobsUpdate(); let y=180; PHONE.jobs.forEach((j,i)=>{ phRR(c,24,y-44,W-48,74,14); c.fillStyle=i===0&&!j.d?"#2a2410":"#16161A"; c.fill();
  phTxt(c,j.d?"✔":"◆",50,y+6,30,j.d?PHONE.cyan:G,"left","800"); phWrap(c,j.t,92,y+4,W-140,30,26,j.d?"#9A968C":"#F5F2E8"); y+=92; });
  if(PHONE.jobs.some(j=>j.m)) phTxt(c,"MISSION ACTIVE · open Hack near a gate",W/2,H-100,22,PHONE.cyan,"center"); };
window.phApp_Crew=(c,W,H,G)=>{ let y=160; const ms=PHONE.msgs.slice(-5);
  for(const m of ms){ const me=m.f==="ME", lines=Math.ceil(m.t.length/26), h=40+lines*30; phRR(c,me?110:24,y,W-134,h,16); c.fillStyle=me?"#3a2f0e":"#16161A"; c.fill();
    phTxt(c,m.f,me?W-40:44,y+28,20,me?G:PHONE.cyan,me?"right":"left","800"); phWrap(c,m.t,me?130:44,y+60,W-180,30,25,"#F5F2E8"); y+=h+22; }
  if(PHONE.replies){ let ry=H-90-PHONE.replies.length*62; PHONE.replies.forEach((r,i)=>{ phRR(c,40,ry,W-80,52,26); c.fillStyle=i===PHONE.rsel?G:"#16161A"; c.fill(); c.strokeStyle=G; c.lineWidth=2; c.stroke(); phTxt(c,r,W/2,ry+36,26,i===PHONE.rsel?"#0B0B0D":G,"center","700"); ry+=62; }); } };
window.phApp_Stats=(c,W,H,G)=>{ const S=typeof Stats!=="undefined"?Stats:{}, sp=typeof Ride!=="undefined"?Math.round(Ride.speed*2.2):0; PHONE.best=Math.max(PHONE.best||0,S.chain||1); PHONE.top=Math.max(PHONE.top||0,sp);
  [["TAGS",S.tags||0],["CANS",S.cans||0],["BEST CHAIN","x"+PHONE.best],["TOP SPEED",PHONE.top],["JOBS DONE",PHONE.jobs.filter(j=>j.d).length]].forEach(([k,v],i)=>{ const y=160+i*122; phRR(c,24,y,W-48,106,16); c.fillStyle="#16161A"; c.fill(); phTxt(c,k,48,y+42,24,"#9A968C"); phTxt(c,String(v),W-48,y+84,62,G,"right","800"); }); };
window.phApp_Settings=(c,W,H,G)=>{ phTxt(c,"CONTROLS",40,175,26,PHONE.cyan,"left","800"); PH_CTRL.forEach((s,i)=>{ phTxt(c,s,32,212+i*39,19,i%2?"#F5F2E8":G,"left","600"); }); };
window.phApp_Map=(c,W,H,G)=>{ const mm=document.getElementById("skmini")||document.getElementById("minimap"); phRR(c,24,150,W-48,W-48,16); c.fillStyle="#101014"; c.fill(); c.save(); c.clip();
  if(mm&&mm.width) c.drawImage(mm,24,150,W-48,W-48); else { c.strokeStyle="#2a2820"; for(let i=0;i<10;i++){ c.beginPath(); c.moveTo(24+i*46,150); c.lineTo(24+i*46,150+W-48); c.stroke(); } } c.restore();
  c.beginPath(); c.arc(W/2,150+(W-48)/2,12,0,7); c.fillStyle=G; c.fill(); c.strokeStyle="#0B0B0D"; c.lineWidth=3; c.stroke(); phTxt(c,"YOU",W/2,150+(W-48)/2-22,20,G,"center","800"); phTxt(c,"VIEW / M  full Palma City map",W/2,H-110,22,"#9A968C","center"); };
function phStub(c,W,H,G){ phTxt(c,PHONE.apps.find(a=>a[0]===PHONE.app)[1],W/2,400,140,G,"center"); phTxt(c,"COMING SOON",W/2,500,32,"#9A968C","center","800"); }
window.phApp_Hack=(c,W,H,G)=>{ const h=PHONE.hack; const cx=W/2, cy=470, R=170;
  if(!h){ phTxt(c,phNearGate(60)?"Gate in range":"No gate in range",cx,cy,30,phNearGate(60)?PHONE.cyan:"#9A968C","center","700"); return; }
  for(let i=0;i<8;i++){ const a0=(i/8)*Math.PI*2-Math.PI/2+.05, a1=a0+Math.PI*2/8-.1; // outer fixed targets
    c.beginPath(); c.arc(cx,cy,R+34,a0,a1); c.lineWidth=10; c.strokeStyle=h.target.includes(i)?PHONE.cyan:"#22222a"; c.stroke();
    const j=((i-h.rot)%8+8)%8; c.beginPath(); c.arc(cx,cy,R,a0,a1); c.lineWidth=36; c.strokeStyle=h.segs.includes(j)?G:"#1d1d22"; c.stroke(); }
  const tl=Math.max(0,h.time), fr=tl/h.max; c.fillStyle="#16161A"; c.fillRect(40,170,W-80,16); c.fillStyle=fr<.3?"#FF4D3D":G; c.fillRect(40,170,(W-80)*fr,16);
  phTxt(c,h.state==="ok"?"ACCESS GRANTED":h.state==="fail"?"TRACE DETECTED":tl.toFixed(1)+"s",cx,cy+14,h.state?34:46,h.state==="ok"?PHONE.cyan:h.state==="fail"?"#FF4D3D":"#F5F2E8","center","800");
  phTxt(c,h.state==="fail"?"ENTER to retry":h.state==="ok"?"Gate opening…":"◀ ▶ spin ring · line up gold",cx,H-110,24,"#9A968C","center"); };
function phNearGate(r){ if(typeof garages==="undefined") return null; const p=Ride.group.position; let best=null, bd=r*r; for(const g of garages){ if(!g.gate) continue; const dx=g.cp[0]-p.x, dz=g.cp[1]-p.z, d=dx*dx+dz*dz; if(d<bd){ bd=d; best=g; } } return best; }
function phHackStart(){ const segs=[0,1,4], rot=2+Math.floor(Math.random()*5); PHONE.hack={segs,target:segs.slice(),rot,time:15,max:15,state:null}; }
function phHackCheck(){ const h=PHONE.hack; if(!h||h.state) return; if(h.rot%8===0){ h.state="ok"; phHackWin(); } }
function phHackWin(){ const g=phNearGate(1e4); PHONE.lastGate=g?g.crew:null; if(g&&g.gate&&typeof gateOpenNow==="function"){ g.gate.dismissed=true; gateOpenNow(g.gate); }
  for(const j of PHONE.jobs) if(j.m) j.d=true; try{ GATE_SFX.ok(); }catch(e){} phBuzz(.8,120); }
function phJobsUpdate(){ const S=typeof Stats!=="undefined"?Stats:{}; PHONE.jobs[1].d=PHONE.jobs[1].d||(S.tags||0)>=3; PHONE.jobs[2].d=PHONE.jobs[2].d||(S.cans||0)>=10; try{ PHONE.jobs[0].d=PHONE.jobs[0].d||lastCrew; }catch(e){} }
function phOffer(){ if(PHONE.offerSent) return; PHONE.offerSent=true; PHONE.msgs.push({f:"CODEE",t:"Karasu left a gate on cheap locks. Crack it with Hack and the turf's ours. You in?"}); PHONE.replies=["Accept","Who's backing me?","Not now"]; PHONE.rsel=0; PHONE.badge.Crew=1; phBuzz(.5,60); setTimeout(()=>phBuzz(.5,60),140); PHONE.dirty=true; }
function phReply(i){ const r=PHONE.replies[i]; PHONE.msgs.push({f:"ME",t:r});
  if(r==="Accept"){ PHONE.jobs.unshift({t:"Mission: hack the nearest crew gate",d:false,m:true}); PHONE.badge.Jobs=1; PHONE.msgs.push({f:"CODEE",t:"Locked in. It's on your Jobs list."}); PHONE.replies=null; PHONE.accepted=true; }
  else if(r==="Not now"){ PHONE.msgs.push({f:"CODEE",t:"Offer stands. Ping me."}); PHONE.replies=["Accept","Not now"]; }
  else { PHONE.msgs.push({f:"CODEE",t:"Whole crew's on comms. Just get the gate."}); PHONE.replies=["Accept","Not now"]; } PHONE.rsel=0; }
function phBuzz(s,ms){ try{ const ses=renderer.xr.getSession&&renderer.xr.getSession(); if(ses) for(const src of ses.inputSources) if(src.handedness==="left"&&src.gamepad&&src.gamepad.hapticActuators&&src.gamepad.hapticActuators[0]) src.gamepad.hapticActuators[0].pulse(s,ms); }catch(e){} }
function phoneSet(v){ PHONE.up=!!v; PHONE.dirty=true; if(PHONE.up&&!PHONE.offerSent) setTimeout(phOffer,2500); }
function phoneNav(a){ if(!PHONE.up) return; PHONE.dirty=true; const ap=PHONE.app;
  if(a==="back"){ if(ap==="home") phoneSet(false); else { if(ap==="Hack") PHONE.hack=null; PHONE.app="home"; } return; }
  if(ap==="home"){ const s=PHONE.sel; if(a==="left") PHONE.sel=(s+8)%9; if(a==="right") PHONE.sel=(s+1)%9; if(a==="up") PHONE.sel=(s+6)%9; if(a==="down") PHONE.sel=(s+3)%9;
    if(a==="select"){ PHONE.app=PHONE.apps[s][0]; PHONE.badge[PHONE.app]=0; if(PHONE.app==="Hack") phHackStart(); } return; }
  if(ap==="Crew"&&PHONE.replies){ const n=PHONE.replies.length; if(a==="up") PHONE.rsel=(PHONE.rsel+n-1)%n; if(a==="down") PHONE.rsel=(PHONE.rsel+1)%n; if(a==="select") phReply(PHONE.rsel); return; }
  if(ap==="Hack"){ const h=PHONE.hack; if(!h) return; if(h.state==="fail"&&a==="select"){ phHackStart(); return; } if(h.state) return;
    if(a==="left") h.rot=(h.rot+7)%8; if(a==="right") h.rot=(h.rot+1)%8; phHackCheck(); return; } }
window.phoneNav=phoneNav; window.phoneSet=phoneSet;
addEventListener("keydown",e=>{ if(typeof State==="undefined"||State.mode==="menu") return; const c=e.code;
  if(c==="Tab"){ e.preventDefault(); e.stopImmediatePropagation(); if(!e.repeat) phoneSet(!PHONE.up); return; }
  if(!PHONE.up){ if(c==="ArrowUp"&&State.mode==="ride"){ e.preventDefault(); e.stopImmediatePropagation(); if(!e.repeat) phoneSet(true); } return; }
  const m={ArrowUp:"up",ArrowDown:"down",ArrowLeft:"left",ArrowRight:"right",Enter:"select",NumpadEnter:"select",Backspace:"back",Escape:"back"}[c];
  if(m){ e.preventDefault(); e.stopImmediatePropagation(); if(!e.repeat) phoneNav(m); } },{capture:true});
function phXRInput(ses){ const P=PHONE.prevXR; let L=null, R=null; for(const s of ses.inputSources){ if(!s.gamepad) continue; if(s.handedness==="left") L=s; else if(s.handedness==="right") R=s; }
  const e=(src,h,i)=>{ const b=!!(src&&src.gamepad.buttons[i]&&src.gamepad.buttons[i].pressed), r=b&&!P[h+i]; P[h+i]=b; return r; };
  const lx=e(L,"l",4), ly=e(L,"l",5), lt=e(L,"l",0), rb=e(R,"r",5);
  if(!PHONE.up){ if(lx||ly) phoneSet(true); return; }
  if(ly||rb) phoneNav("back"); else if(lx) phoneSet(false); if(lt) phoneNav("select");
  const ax=L?L.gamepad.axes:[], x=ax[2]||0, y=ax[3]||0; if(Math.hypot(x,y)<.35) PHONE.axLock=false; else if(!PHONE.axLock&&Math.hypot(x,y)>.7){ PHONE.axLock=true; phoneNav(Math.abs(x)>Math.abs(y)?(x>0?"right":"left"):(y>0?"down":"up")); phBuzz(.15,15); } }
// While the phone is up in VR, its buttons/stick feed the phone, not attacks/tag (attack + gate logic untouched).
if(typeof wallInput==="function"){ const _wi=wallInput; wallInput=function(){ const I=_wi(); if(renderer.xr.isPresenting&&(PHONE.up||PHONE.xrEdge)){ I.a[1]=I.a[2]=false; if(PHONE.up){ I.a[0]=false; I.back=false; I.side=0; } } return I; }; }
if(typeof poll==="function"){ const _po=poll; poll=function(){ _po(); if(PHONE.up&&renderer.xr.isPresenting) Input.tag=false; }; }
const _phV=new THREE.Vector3(), _phQ=new THREE.Quaternion(), _phE=new THREE.Euler();
function phoneTick(dt,xr){ if(!PHONE.g) phoneBuild(); const g=PHONE.g;
  PHONE.xrEdge=false; const ses=xr&&renderer.xr.getSession(); if(ses){ const was=PHONE.up; phXRInput(ses); PHONE.xrEdge=was!==PHONE.up; }
  PHONE.t=THREE.MathUtils.clamp(PHONE.t+(PHONE.up?dt:-dt)*5,0,1); const k=PHONE.t*PHONE.t*(3-2*PHONE.t); g.visible=PHONE.t>.001;
  if(!g.visible){ return; }
  if(PHONE.hack&&!PHONE.hack.state){ PHONE.hack.time-=dt; if(PHONE.hack.time<=0){ PHONE.hack.state="fail"; } PHONE.dirty=true; }
  PHONE.acc+=dt; if(PHONE.acc>=1/30){ PHONE.acc=0; const d=new Date(); if(String(d.getMinutes()).padStart(2,"0")!==PHONE.lastClock.slice(3)) PHONE.dirty=true; if(PHONE.dirty) phoneDraw(); }
  if(xr){ let ctl=null; const srcs=ses?[...ses.inputSources]:[]; const li=srcs.findIndex(s=>s.handedness==="left"); if(li>=0){ ctl=renderer.xr.getController(li); if(!ctl.parent&&typeof rig!=="undefined") rig.add(ctl); }
    if(ctl&&g.parent!==ctl){ ctl.add(g); } if(ctl){ g.scale.setScalar(1); g.position.set(.01,.03-.04*(1-k),-.06); g.rotation.set(-.6+.35*k,.35,0); } return; }
  if(g.parent!==scene) scene.add(g);
  const asp=camera.aspect||1.78, hh=Math.tan(THREE.MathUtils.degToRad(camera.fov/2))*.5; g.scale.setScalar(hh*1.55/.14*.5);
  _phV.set(hh*asp*.40,-hh*(.45+.9*(1-k)),-.5).applyQuaternion(camera.quaternion).add(camera.position); g.position.copy(_phV);
  g.quaternion.copy(camera.quaternion); _phQ.setFromEuler(_phE.set(.12,-.32,.1)); g.quaternion.multiply(_phQ); }
window.phoneTick=phoneTick; window.PHONE=PHONE;
