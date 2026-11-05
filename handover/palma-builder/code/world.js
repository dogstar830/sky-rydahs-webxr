// ===== WORLD: PALMA CITY (3 islands, 3 grind bridges, 8 crew garages) =====
// Layout per "Palma City — Map Design Instructions" (Design Round 2). Origin = Terminal Plaza, +X east, +Z south.
const colliders=[], miniRects=[], rails=[], checkpoints=[], cans=[], tagSpots=[], animated=[];
const B={ pos:[], size:[], col:[], neon:[] };
function addBuilding(x,z,w,d,h,col,neon){
  B.pos.push([x,z]); B.size.push([w,h,d]); B.col.push(col); B.neon.push(neon);
  colliders.push({minX:x-w/2,maxX:x+w/2,minZ:z-d/2,maxZ:z+d/2});
  miniRects.push({x,z,w,d,c:"#"+new THREE.Color(col).offsetHSL(0,0,.12).getHexString()});
}
function rnd(a,b){ return a+Math.random()*(b-a); }
function pick(a){ return a[Math.floor(Math.random()*a.length)]; }
const PALMA={
  islands:[ {id:"west",box:[-240,-100,90,200]}, {id:"east",box:[170,-100,320,200]}, {id:"north",box:[-160,-320,240,-180]} ],
  districts:[
    {id:"portside",name:"PORTSIDE TERMINAL",box:[-70,-100,90,60],tint:"#FFD700",ground:0x1a1d2e},
    {id:"cove",name:"THE COVE",box:[-240,-100,-70,40],tint:"#AA00FF",ground:0x221a33},
    {id:"port",name:"INDUSTRIAL PORT",box:[-240,40,-70,200],tint:"#FF6A00",ground:0x1f1b1e},
    {id:"yard",name:"THE YARD",box:[-70,60,90,200],tint:"#C0582B",ground:0x24221c},
    {id:"the98",name:"THE 98",box:[170,-100,320,-20],tint:"#FFC83C",ground:0x1d1b24},
    {id:"drive",name:"THE DRIVE",box:[170,-20,320,90],tint:"#8CE6FF",ground:0x161c2c},
    {id:"strip",name:"THE STRIP",box:[170,90,320,200],tint:"#FF2BD6",ground:0x1e1226},
    {id:"heights",name:"THE HEIGHTS",box:[-160,-320,240,-180],tint:"#7CB342",ground:0x14261c},
  ],
  bridges:[
    {id:"causeway",name:"CAUSEWAY",a:[-20,-100],b:[40,-180],color:0xFFD700,css:"#FFD700"},
    {id:"shore",name:"SHORE BRIDGE",a:[90,150],b:[170,165],color:0xAA00FF,css:"#AA00FF"},
    {id:"b98",name:"98 BRIDGE",a:[240,-100],b:[200,-180],color:0x00E5FF,css:"#00E5FF"},
  ],
  garages:[
    {crew:"codee",name:"CODE : E",pos:[-36,-24],face:"E",color:"#FFD700",dark:0x141414},
    {crew:"karasu",name:"KOGARASUMARU",pos:[55,30],face:"W",color:"#00E5FF",dark:0x121010},
    {crew:"static",name:"STATIC ANGELS",pos:[-190,-30],face:"W",color:"#AA00FF",dark:0x1a1230},
    {crew:"behemoth",name:"BEHEMOTH",pos:[-190,150],face:"S",color:"#FF6A00",dark:0x151515},
    {crew:"anubis",name:"ANUBIS",pos:[-110,170],face:"E",color:"#00BFA5",dark:0x0f1a1a},
    {crew:"ttt",name:"TOOL TOUL TO",pos:[20,150],face:"N",color:"#C0582B",dark:0x2a2a2e},
    {crew:"genesis",name:"GENESIS",pos:[250,150],face:"N",color:"#FF2BD6",dark:0x1a0f1f},
    {crew:"forest",name:"SLEEPING FOREST",pos:[40,-260],face:"S",color:"#7CB342",dark:0xe8e8e0},
  ],
  missions:[ {type:"story",title:"SKYLINE GRIND",pos:[0,-46]}, {type:"crew",title:"STRIP RACE",pos:[240,110]}, {type:"side",title:"COVE TAGS",pos:[-150,-80]}, {type:"crew",title:"HEIGHTS DESCENT",pos:[120,-240]} ],
};
const MCOL={story:"#FFD700",crew:"#00E5FF",side:"#AA00FF"};
const FACE={E:Math.PI/2,W:-Math.PI/2,S:0,N:Math.PI};
function districtAt(x,z){ for(const d of PALMA.districts){ const b=d.box; if(x>=b[0]&&x<=b[2]&&z>=b[1]&&z<=b[3]) return d; } return null; }
// ---- land test: islands (+4 m shore) or bridge corridors ----
function segDist(px,pz,ax,az,bx,bz){ const vx=bx-ax,vz=bz-az,L2=vx*vx+vz*vz; const t=Math.max(-.15,Math.min(1.15,((px-ax)*vx+(pz-az)*vz)/L2)); return Math.hypot(px-(ax+vx*t),pz-(az+vz*t)); }
function onLand(x,z){
  for(const i of PALMA.islands){ const b=i.box; if(x>b[0]-4&&x<b[2]+4&&z>b[1]-4&&z<b[3]+4) return true; }
  for(const br of PALMA.bridges) if(segDist(x,z,br.a[0],br.a[1],br.b[0],br.b[1])<3.8) return true;
  return false;
}
// ---- generic instancing (keeps Quest draw calls low) ----
const INST={};
function inst(kind,x,y,z,sx,sy,sz,col,rx,ry,rz){ (INST[kind]=INST[kind]||[]).push([x,y,z,sx,sy,sz,col,rx||0,ry||0,rz||0]); }
function buildInstances(){
  const geos={ box:new THREE.BoxGeometry(1,1,1), glow:new THREE.BoxGeometry(1,1,1), cone:new THREE.ConeGeometry(.5,1,6), cyl:new THREE.CylinderGeometry(.5,.5,1,6), frond:new THREE.ConeGeometry(.5,1,4) };
  const m=new THREE.Matrix4(), q=new THREE.Quaternion(), e=new THREE.Euler(), c=new THREE.Color(), v=new THREE.Vector3(), s=new THREE.Vector3();
  for(const k in INST){ const L=INST[k], n=L.length, isGlow=k==="glow";
    const body=new THREE.InstancedMesh(geos[k], isGlow?new THREE.MeshBasicMaterial({color:0xffffff}):new THREE.MeshToonMaterial({color:0xffffff,gradientMap:gradMap}), n);
    const hull=isGlow?null:new THREE.InstancedMesh(geos[k],inkMat,n);
    L.forEach((p,i)=>{ q.setFromEuler(e.set(p[7],p[8],p[9])); m.compose(v.set(p[0],p[1],p[2]),q,s.set(p[3],p[4],p[5])); body.setMatrixAt(i,m); body.setColorAt(i,c.set(p[6]));
      if(hull){ const t=k==="frond"?.08:.22; m.compose(v,q,s.set(p[3]+t,p[4]+t,p[5]+t)); hull.setMatrixAt(i,m); } });
    scene.add(body); if(hull) scene.add(hull);
  }
}
function buildInstancedBuildings(){
  const n=B.pos.length, geo=new THREE.BoxGeometry(1,1,1); geo.translate(0,.5,0);
  const body=new THREE.InstancedMesh(geo,new THREE.MeshToonMaterial({color:0xffffff,gradientMap:gradMap}),n);
  const hull=new THREE.InstancedMesh(geo,inkMat,n);
  const bands=new THREE.InstancedMesh(geo,new THREE.MeshBasicMaterial({color:0xffffff}),n*3);
  const m=new THREE.Matrix4(), q=new THREE.Quaternion(), col=new THREE.Color();
  for(let i=0;i<n;i++){
    const [x,z]=B.pos[i], [w,h,d]=B.size[i];
    m.compose(new THREE.Vector3(x,0,z),q,new THREE.Vector3(w,h,d)); body.setMatrixAt(i,m); body.setColorAt(i,col.set(B.col[i]));
    m.compose(new THREE.Vector3(x,-.1,z),q,new THREE.Vector3(w+.4,h+.3,d+.4)); hull.setMatrixAt(i,m);
    const nc=col.set(B.neon[i]);
    m.compose(new THREE.Vector3(x,h-.3,z),q,new THREE.Vector3(w+.12,.3,d+.12)); bands.setMatrixAt(i*3,m); bands.setColorAt(i*3,nc);
    m.compose(new THREE.Vector3(x,h*.45,z),q,new THREE.Vector3(w+.08,.14,d+.08)); bands.setMatrixAt(i*3+1,m); bands.setColorAt(i*3+1,nc);
    m.compose(new THREE.Vector3(x,1.2,z),q,new THREE.Vector3(w+.06,.1,d+.06)); bands.setMatrixAt(i*3+2,m); bands.setColorAt(i*3+2,nc);
  }
  scene.add(body,hull,bands);
}
function addRail(x1,z1,x2,z2,h,col){
  const len=Math.hypot(x2-x1,z2-z1), ang=Math.atan2(x2-x1,z2-z1);
  const g=new THREE.Group(); g.position.set((x1+x2)/2,0,(z1+z2)/2); g.rotation.y=ang;
  const bar=new THREE.Mesh(new THREE.CylinderGeometry(.07,.07,len,6),toon(0xc0c0d0)); bar.rotation.x=Math.PI/2; bar.position.y=h; ink(bar,.03); g.add(bar);
  const gl=new THREE.Mesh(new THREE.BoxGeometry(.03,.03,len),glow(col||C.cyan)); gl.position.y=h-.09; g.add(gl);
  scene.add(g); rails.push({x1,z1,x2,z2,h});
  const n=Math.max(1,Math.floor(len/6)); for(let i=0;i<=n;i++){ const t=i/n; inst("box",x1+(x2-x1)*t,h/2,z1+(z2-z1)*t,.08,h,.08,0x666677); }
}
function bolt(x,y,z,ry,s){ const sh=new THREE.Shape(); sh.moveTo(0,1); sh.lineTo(-.45,0); sh.lineTo(-.05,0); sh.lineTo(-.3,-1); sh.lineTo(.45,.15); sh.lineTo(.05,.15); sh.lineTo(.3,1);
  const m=new THREE.Mesh(new THREE.ShapeGeometry(sh),glow(C.gold)); m.material.side=THREE.DoubleSide; m.scale.setScalar(s); m.position.set(x,y,z); m.rotation.y=ry; scene.add(m); return m; }
function flat(w,d,col,x,y,z,mat){ const m=new THREE.Mesh(new THREE.PlaneGeometry(w,d),mat||toon(col)); m.rotation.x=-Math.PI/2; m.position.set(x,y,z); scene.add(m); return m; }
function putSign(str,wid,css,x,y,z,ry,opt){ const s=sign(str,wid,css,opt); s.position.set(x,y,z); s.rotation.y=ry||0; scene.add(s); return s; }
function searchlight(x,y,z,col){
  const sl=new THREE.Mesh(new THREE.ConeGeometry(5,90,12,1,true), new THREE.MeshBasicMaterial({color:col||0x8fb8ff,transparent:true,opacity:.07,depthWrite:false,blending:THREE.AdditiveBlending,side:THREE.DoubleSide}));
  sl.geometry.translate(0,-45,0); const piv=new THREE.Group(); piv.position.set(x,y,z); sl.rotation.x=Math.PI; piv.add(sl); scene.add(piv);
  animated.push(t=>{ sl.rotation.z=Math.sin(t*.3+x)*.5; sl.rotation.x=Math.PI+Math.cos(t*.25+z)*.4; });
}

// ---- crew emblems (procedural canvas) ----
function emblemTex(crew,css){
  const c=document.createElement("canvas"); c.width=c.height=512; const x=c.getContext("2d");
  x.translate(256,256); x.fillStyle="#0A0A0A"; x.beginPath(); x.arc(0,0,240,0,7); x.fill();
  x.lineWidth=18; x.strokeStyle=css; x.shadowColor=css; x.shadowBlur=30; x.beginPath(); x.arc(0,0,222,0,7); x.stroke();
  x.fillStyle=css; x.strokeStyle=css; x.lineJoin="round"; x.lineCap="round";
  const wings=()=>{ for(const sd of [-1,1]){ x.save(); x.scale(sd,1); for(let k=0;k<4;k++){ x.beginPath(); x.moveTo(20,10); x.quadraticCurveTo(90+k*10,-90+k*30,180-k*14,-60+k*36); x.lineTo(40,30+k*6); x.fill(); } x.restore(); } };
  if(crew==="codee"){ x.shadowBlur=0; drawLogo(x,0,0,1.8); }
  else if(crew==="karasu"){ wings(); x.fillStyle="#000"; x.beginPath(); x.moveTo(0,-60); x.lineTo(40,40); x.lineTo(0,20); x.lineTo(-40,40); x.fill(); x.fillStyle=css; x.font='900 90px sans-serif'; x.textAlign="center"; x.fillText("小烏丸",0,170); }
  else if(crew==="static"){ wings(); x.lineWidth=16; x.strokeStyle="#00E5FF"; x.beginPath(); x.ellipse(0,-110,70,22,0,0,7); x.stroke(); }
  else if(crew==="behemoth"){ x.beginPath(); x.arc(0,-10,95,0,7); x.fill(); x.fillRect(-55,60,110,60); for(const sd of [-1,1]){ x.beginPath(); x.moveTo(sd*70,-70); x.quadraticCurveTo(sd*180,-120,sd*150,-200); x.quadraticCurveTo(sd*130,-110,sd*40,-95); x.fill(); }
    x.fillStyle="#000"; x.beginPath(); x.arc(-38,-10,24,0,7); x.arc(38,-10,24,0,7); x.fill(); x.fillRect(-40,80,14,40); x.fillRect(-7,80,14,40); x.fillRect(26,80,14,40); }
  else if(crew==="anubis"){ x.beginPath(); x.moveTo(-60,-180); x.lineTo(-20,-60); x.lineTo(20,-60); x.lineTo(60,-180); x.lineTo(80,-20); x.lineTo(150,60); x.lineTo(40,70); x.lineTo(0,160); x.lineTo(-40,70); x.lineTo(-80,-20); x.closePath(); x.fill(); x.fillStyle="#000"; x.beginPath(); x.moveTo(-50,0); x.lineTo(-15,10); x.lineTo(-45,20); x.fill(); x.beginPath(); x.moveTo(50,0); x.lineTo(15,10); x.lineTo(45,20); x.fill(); }
  else if(crew==="genesis"){ for(let k=0;k<3;k++){ x.lineWidth=26; x.beginPath(); x.moveTo(-150,-60+k*60); x.lineTo(0,20+k*60); x.lineTo(150,-60+k*60); x.stroke(); } x.fillStyle="#fff"; x.beginPath(); x.arc(0,-110,30,0,7); x.fill(); }
  else if(crew==="ttt"){ for(const r of [.7,-.7]){ x.save(); x.rotate(r); x.fillRect(-12,-150,24,280); x.fillRect(-60,-170,120,55); x.restore(); } }
  else if(crew==="forest"){ x.fillStyle="#FFD700"; x.strokeStyle="#FFD700"; x.fillRect(-16,0,32,160); x.lineWidth=14; for(const sd of [-1,1]){ x.beginPath(); x.moveTo(0,40); x.quadraticCurveTo(sd*60,0,sd*90,-40); x.stroke(); }
    x.beginPath(); x.arc(0,-60,110,0,7); x.arc(-90,-10,60,0,7); x.arc(90,-10,60,0,7); x.fill(); }
  return new THREE.CanvasTexture(c);
}
function emblem(crew,css,size,x,y,z,ry,parent){ const m=new THREE.Mesh(new THREE.PlaneGeometry(size,size),new THREE.MeshBasicMaterial({map:emblemTex(crew,css),transparent:true,side:THREE.DoubleSide})); m.position.set(x,y,z); m.rotation.y=ry||0; (parent||scene).add(m); return m; }

// ---- crew garage + attached clubhouse ----
const garages=[];
function createGarage(G){
  const th=FACE[G.face], [gx,gz]=G.pos, col=new THREE.Color(G.color).getHex();
  const g=new THREE.Group(); g.position.set(gx,0,gz); g.rotation.y=th; scene.add(g);
  const W=(lx,lz)=>[gx+lx*Math.cos(th)+lz*Math.sin(th), gz-lx*Math.sin(th)+lz*Math.cos(th)];
  const col2=(lx0,lx1,lz0,lz1)=>{ const a=W(lx0,lz0), b=W(lx1,lz1); colliders.push({minX:Math.min(a[0],b[0]),maxX:Math.max(a[0],b[0]),minZ:Math.min(a[1],b[1]),maxZ:Math.max(a[1],b[1])}); };
  const wall=G.dark, H=5.2;
  // floor
  const fl=new THREE.Mesh(new THREE.PlaneGeometry(12,10),toon(new THREE.Color(col).multiplyScalar(.18).getHex())); fl.rotation.x=-Math.PI/2; fl.position.set(0,.03,-5); g.add(fl);
  // walls: back, sides, front piers around a 7 m open bay
  box(12,H,.4,wall,0,H/2,-9.8,g,.06); box(.4,H,10,wall,-5.8,H/2,-5,g,.06); box(.4,H,10,wall,5.8,H/2,-5,g,.06);
  box(2.5,H,.4,wall,-4.75,H/2,-.2,g,.06); box(2.5,H,.4,wall,4.75,H/2,-.2,g,.06); box(12,1.4,.4,wall,0,H-.7,-.2,g,.06);
  box(12.4,.35,10.4,wall,0,H+.17,-5,g,.06); // roof
  col2(-6,6,-10,-9.6); col2(-6,-5.6,-10,0); col2(5.6,6,-10,0); col2(-6,-3.5,-.4,0); col2(3.5,6,-.4,0);
  // crew neon: bay frame, roof band, interior floor trim + ceiling strips
  box(.22,3.9,.25,col,-3.5,1.95,.05,g,0); box(.22,3.9,.25,col,3.5,1.95,.05,g,0); box(7.2,.22,.25,col,0,3.9,.05,g,0);
  box(12.5,.22,10.5,col,0,H+.4,-5,g,0);
  box(11.2,.06,.1,col,0,.06,-9.5,g,0); box(.1,.06,9.4,col,-5.5,.06,-5,g,0); box(.1,.06,9.4,col,5.5,.06,-5,g,0);
  for(const lz of [-3,-7]) box(8,.08,.3,0xffffff,0,H-.05,lz,g,0);
  // sign + emblem (outside, readable from distance) + emblem on back wall inside
  const sg=sign(G.name,10,G.color,{size:G.name.length>10?110:150,glow:40}); sg.position.set(0,H+1.8,.25); g.add(sg);
  emblem(G.crew,G.color,4.2,0,H+4.8,-1,0,g);
  emblem(G.crew,G.color,4,0,2.8,-9.55,0,g);
  // Air Treck rack (left wall) with 3 skate pairs
  box(.5,2.2,4,0x2a2a2a,-5.3,1.1,-5,g,.03);
  for(let k=0;k<3;k++){ box(.4,.3,.6,0x333333,-5.2,.8+k*.6,-6.3+k*1.3,g,.02); box(.42,.06,.62,col,-5.2,.66+k*.6,-6.3+k*1.3,g,0); }
  // checkpoint pad (local 0,-4) + dressing pad (local 4,-2)
  const cp=new THREE.Mesh(new THREE.CylinderGeometry(1.6,1.7,.12,32),glow(col,.55)); cp.position.set(0,.07,-4); g.add(cp);
  const cr=new THREE.Mesh(new THREE.RingGeometry(1.75,2,32),glow(C.gold)); cr.rotation.x=-Math.PI/2; cr.position.set(0,.15,-4); g.add(cr);
  const cs=sign("CHECKPOINT",2.6,"#FFD700",{size:150,glow:20}); cs.position.set(0,1.7,-4); g.add(cs); animated.push(t=>{ cs.position.y=1.7+Math.sin(t*2)*.1; });
  const dp=new THREE.Mesh(new THREE.CylinderGeometry(1,1.05,.1,24),glow(C.cyan,.5)); dp.position.set(3.6,.06,-2.2); g.add(dp);
  const ds=sign("DRESS",1.6,"#00E5FF",{size:170,glow:20}); ds.position.set(3.6,1.3,-2.2); g.add(ds);
  // attached clubhouse block behind the garage
  const ch=8.5; box(12,ch,6.4,wall,0,ch/2,-13.4,g,.08); col2(-6,6,-16.6,-10);
  box(12.1,.25,6.5,col,0,ch-.3,-13.4,g,0); box(12.1,.12,6.5,col,0,5.6,-13.4,g,0);
  for(const lx of [-4,0,4]){ const w=new THREE.Mesh(new THREE.PlaneGeometry(2.6,1.4),glow(new THREE.Color(col).lerp(new THREE.Color(0xffffff),.5).getHex(),.7)); w.position.set(lx,7,-16.65); w.rotation.y=Math.PI; g.add(w); }
  const cl=sign("CLUBHOUSE",5,G.color,{size:150,glow:20}); cl.position.set(0,7,-10.15); g.add(cl);
  const a=W(0,-8.3); miniRects.push({x:a[0],z:a[1],w:Math.abs(Math.sin(th))>.5?16.6:12,d:Math.abs(Math.sin(th))>.5?12:16.6,c:"#333"});
  const pc=W(0,-4), pdr=W(3.6,-2.2);
  garages.push(Object.assign({},G,{th,cp:pc,dress:pdr,inside:false,inDress:false,group:g}));
}

// ---- districts ----
function fillDistrict(d,o){
  const [x0,z0,x1,z1]=d.box, cell=o.cell||26;
  for(let x=x0+cell/2;x<x1-4;x+=cell) for(let z=z0+cell/2;z<z1-4;z+=cell){
    if(Math.random()>(o.density||.85)) continue;
    if(o.skip&&o.skip(x,z)) continue;
    if(garages.some(g=>Math.hypot(g.pos[0]-x,g.pos[1]-z)<24)) continue;
    if(PALMA.bridges.some(b=>Math.hypot(b.a[0]-x,b.a[1]-z)<22||Math.hypot(b.b[0]-x,b.b[1]-z)<22)) continue;
    const w=rnd(o.wmin||10,o.wmax||16), dd=rnd(o.wmin||10,o.wmax||16);
    addBuilding(x+rnd(-2,2),z+rnd(-2,2),w,dd,rnd(o.hmin,o.hmax),pick(o.cols),pick(o.neons));
    if(o.tags&&Math.random()<o.tags) tag(Math.floor(Math.random()*8),rnd(3,5),x,rnd(1.8,3.5),z+dd/2+2.05,0);
  }
  // street lines on cell boundaries
  for(let x=x0+cell;x<x1;x+=cell) inst("glow",x,.03,(z0+z1)/2,.18,.02,z1-z0-4,new THREE.Color(d.tint).multiplyScalar(.5).getHex());
  for(let z=z0+cell;z<z1;z+=cell) inst("glow",(x0+x1)/2,.03,z,x1-x0-4,.02,.18,new THREE.Color(d.tint).multiplyScalar(.5).getHex());
}
function palm(x,z){ const lean=rnd(-.15,.15), h=rnd(6,8.5); inst("cyl",x,h/2,z,.45,h,.45,0x4a3a3a,0,0,lean); const tx=x-Math.sin(lean)*h/2*1.0, ty=h;
  for(let k=0;k<6;k++){ const a=k*Math.PI/3; inst("frond",tx+Math.sin(a)*1.4,ty-.3,z+Math.cos(a)*1.4,.8,3.4,.18,0x1d6b4f,Math.cos(a)*1.9,0,-Math.sin(a)*1.9); } }
function tree(x,z,s,col){ s=s||1; inst("cyl",x,1.5*s,z,.5*s,3*s,.5*s,0x3b2a1e); inst("cone",x,4.5*s,z,4*s,5*s,4*s,col||pick([0x1d4a2a,0x23552f,0x1a3f26])); inst("cone",x,7*s,z,3*s,4*s,3*s,col||0x2a6a38); }

function createCity(){
  // sea
  const sea=flat(1600,1600,0,40,-2.5,-60,new THREE.MeshToonMaterial({color:0x07182e,gradientMap:gradMap}));
  for(let i=0;i<40;i++){ const w=flat(rnd(8,30),.25,0,rnd(-400,500),-2.45,rnd(-500,380),glow(0x1f5a8a,.5)); w.rotation.z=0; }
  // islands: cliff slabs + shore band
  for(const I of PALMA.islands){ const [x0,z0,x1,z1]=I.box, w=x1-x0+8, d=z1-z0+8;
    const cliff=box(w,10,d,I.id==="north"?0x23302a:0x2a2440,(x0+x1)/2,-5,(z0+z1)/2,null,.3);
    const shore=box(w+3,1.2,d+3,0x3a3550,(x0+x1)/2,-2.4,(z0+z1)/2,null,.1);
    // rocks along shore
    for(let k=0;k<30;k++){ const side=k%4, t=Math.random(); const rx=side<2?x0-4+t*w:(side===2?x0-5:x1+5), rz=side<2?(side?z0-5:z1+5):z0-4+t*d; inst("box",rx,-2,rz,rnd(3,7),rnd(2,5),rnd(3,7),0x2c2a3c,0,rnd(0,3),0); }
  }
  for(const d of PALMA.districts){ const [x0,z0,x1,z1]=d.box; flat(x1-x0,z1-z0,d.ground,(x0+x1)/2,.01,(z0+z1)/2);
    // district border neon
    const tc=new THREE.Color(d.tint).getHex(); inst("glow",(x0+x1)/2,.04,z0+.5,x1-x0-2,.03,.3,tc); inst("glow",(x0+x1)/2,.04,z1-.5,x1-x0-2,.03,.3,tc); inst("glow",x0+.5,.04,(z0+z1)/2,.3,.03,z1-z0-2,tc); inst("glow",x1-.5,.04,(z0+z1)/2,.3,.03,z1-z0-2,tc); }
  PALMA.garages.forEach(createGarage);
  const D=id=>PALMA.districts.find(d=>d.id===id);
  // PORTSIDE TERMINAL (gold + cyan on navy) -- plaza, terminal tower, police HQ
  createPlaza();
  fillDistrict(D("portside"),{hmin:14,hmax:40,cols:[C.deepBlue,0x26335c,C.concrete,C.cityPurple],neons:[C.gold,C.cyan,C.gold],skip:(x,z)=>Math.hypot(x,z)<36||Math.hypot(x,z+46)<16||Math.hypot(x-60,z+70)<20,tags:.3});
  // THE COVE (purple + cyan sunset) -- beach, palms, AQUA LUXE
  const cv=D("cove"); flat(34,140,0x6a5468,-223,.02,-30); flat(34,140,0x6a5468,-223,.02,-30);
  for(let z=-96;z<=36;z+=9){ palm(rnd(-232,-212),z+rnd(-2,2)); }
  for(let z=-90;z<=30;z+=16) palm(-178+rnd(-4,4),z);
  fillDistrict(cv,{hmin:6,hmax:16,cols:[0x3a3560,0x2c4a66,0x4a2f55],neons:[C.cyan,C.purple,C.pink],skip:(x,z)=>x<-200||Math.hypot(x+150,z+60)<16,density:.6});
  { const x=-150,z=-60; box(14,46,14,0x3d2f66,x,23,z,null,.12); colliders.push({minX:x-7,maxX:x+7,minZ:z-7,maxZ:z+7}); miniRects.push({x,z,w:14,d:14,c:"#6a4fa0"});
    for(let y=3;y<46;y+=3) inst("glow",x,y,z,14.15,.5,14.15,(y/3)%2?C.purple:C.cyan);
    const crown=new THREE.Mesh(new THREE.CylinderGeometry(4,7,5,8),glow(C.purple)); crown.position.set(x,48.5,z); scene.add(crown);
    putSign("AQUA LUXE",12,"#00E5FF",x-7.2,34,z,-Math.PI/2); putSign("HOTEL",7,"#AA00FF",x-7.2,29,z,-Math.PI/2); putSign("AQUA LUXE",12,"#00E5FF",x,34,z+7.2,0); }
  putSign("BEACH STRIP",14,"#00E5FF",-206,6,-90,-Math.PI/2);
  // INDUSTRIAL PORT (orange sodium + teal) -- containers, cranes, DOCK 7
  const ccols=[C.rust,C.teal,C.crane,0x2b4f7a,0x6b2a2a,0x00BFA5];
  for(let x=-228;x<-80;x+=18) for(let z=52;z<195;z+=14){
    if(garages.some(g=>Math.hypot(g.pos[0]-x,g.pos[1]-z)<22)||Math.random()<.3) continue;
    const st=1+Math.floor(Math.random()*3); for(let s=0;s<st;s++) inst("box",x,1.3+s*2.6,z,6.2,2.6,2.5,pick(ccols));
    colliders.push({minX:x-3.1,maxX:x+3.1,minZ:z-1.25,maxZ:z+1.25}); miniRects.push({x,z,w:6.2,d:2.5,c:"#7a3a2a"});
  }
  for(const [x,z] of [[-220,190],[-160,192],[-100,194],[-230,80]]) crane(x,z);
  putSign("DOCK 7",9,"#FF6A00",-190,9,154,0); putSign("INDUSTRIAL PORT",14,"#FF6A00",-150,7,44,Math.PI);
  // THE YARD (rust + steel) -- scrap stacks + scrap tower landmark
  for(let k=0;k<70;k++){ const x=rnd(-62,84), z=rnd(68,196); if(Math.hypot(x-20,z-155)<22||Math.hypot(x-90,z-150)<20) continue; const s=rnd(1.5,4);
    inst("box",x,s/2,z,s*rnd(1,2),s,s*rnd(1,2),pick([0x6b6b70,0x8a8a8f,0xC0582B,0xd4b000,0x4a4a50]),0,rnd(0,3),0); colliders.push({minX:x-s*.9,maxX:x+s*.9,minZ:z-s*.9,maxZ:z+s*.9}); miniRects.push({x,z,w:s*1.4,d:s*1.4,c:"#6a5040"}); }
  { const x=-30,z=110; for(const dx of [-3,3]) for(const dz of [-3,3]) box(.7,34,.7,0xd4b000,x+dx,17,z+dz,null,.06);
    for(let y=4;y<34;y+=6) box(7,.4,7,0x8a8a8f,x,y,z,null,.05); box(24,1.2,1.2,0xd4b000,x+8,34,z,null,.06); colliders.push({minX:x-3.5,maxX:x+3.5,minZ:z-3.5,maxZ:z+3.5}); miniRects.push({x,z,w:7,d:7,c:"#d4b000"});
    const hook=new THREE.Mesh(new THREE.SphereGeometry(.5,6,4),glow(0xff2020)); hook.position.set(x,35.5,z); scene.add(hook); putSign("THE YARD",12,"#C0582B",x,26,z+3.6,0); }
  // EAST ISLAND
  fillDistrict(D("the98"),{hmin:8,hmax:20,cols:[0x3a2e22,0x2e2a36,C.concrete],neons:[0xFFC83C,0xFFB000],density:.7});
  for(const [x,z] of [[195,-60],[245,-40],[295,-70],[270,-90]]){ const g=new THREE.Group(); g.position.set(x,0,z); box(.6,16,.6,0x333344,0,8,0,g,.03); box(14,6,.4,0x111118,0,19,0,g,.06);
    const t=sign("THE 98",13,"#FFC83C",{size:170,glow:40,bg:"#1a1206"}); t.position.set(0,19,.25); g.add(t); const t2=t.clone(); t2.position.z=-.25; t2.rotation.y=Math.PI; g.add(t2); scene.add(g); colliders.push({minX:x-.5,maxX:x+.5,minZ:z-.5,maxZ:z+.5}); }
  fillDistrict(D("drive"),{hmin:28,hmax:70,cols:[0x1b2a4a,0x22305a,0x2a3b66],neons:[0x8CE6FF,C.cyan],skip:(x,z)=>Math.hypot(x-245,z-35)<18,density:.8});
  { const x=245,z=35; box(16,96,16,0x203356,x,48,z,null,.14); box(9,14,9,0x2b4677,x,103,z,null,.1); colliders.push({minX:x-8,maxX:x+8,minZ:z-8,maxZ:z+8}); miniRects.push({x,z,w:16,d:16,c:"#4a6aa0"});
    for(let y=8;y<96;y+=8) inst("glow",x,y,z,16.15,.3,16.15,0x8CE6FF); putSign("THE DRIVE",14,"#8CE6FF",x,80,z+8.2,0); putSign("THE DRIVE",14,"#8CE6FF",x-8.2,80,z,-Math.PI/2); }
  // elevated road loop (visual only)
  for(const [ax,az,bx,bz] of [[180,-10,310,-10],[310,-10,310,80],[310,80,180,80],[180,80,180,-10]]){ const L=Math.hypot(bx-ax,bz-az); const m=box(Math.abs(bx-ax)+8,1,Math.abs(bz-az)+8,0x2a2d3a,(ax+bx)/2,12,(az+bz)/2,null,.1);
    inst("glow",(ax+bx)/2,12.55,(az+bz)/2,Math.abs(bx-ax)+8.1,.12,Math.abs(bz-az)+8.1,C.cyan); for(let t=0;t<=1;t+=20/L) inst("box",ax+(bx-ax)*t,6,az+(bz-az)*t,1.4,12,1.4,0x3a3d4a); }
  fillDistrict(D("strip"),{hmin:6,hmax:14,cols:[0x221433,0x2a1840,0x1a1a30],neons:[0xFF2BD6,C.cyan,C.purple],skip:(x,z)=>Math.hypot(x-290,z-120)<16||(x>235&&x<265&&z<140),density:.95,tags:.6,cell:22});
  { const x=290,z=120; box(14,58,14,0x2a1238,x,29,z,null,.12); colliders.push({minX:x-7,maxX:x+7,minZ:z-7,maxZ:z+7}); miniRects.push({x,z,w:14,d:14,c:"#8a2a80"});
    for(let y=4;y<58;y+=4) inst("glow",x,y,z,14.15,.4,14.15,(y/4)%2?0xFF2BD6:0xffffff); putSign("GENESIS",12,"#FF2BD6",x-7.2,46,z,-Math.PI/2); putSign("HOTEL",7,"#ffffff",x-7.2,41,z,-Math.PI/2); }
  createClubArch(250,104);
  // NORTH SHORE: THE HEIGHTS (moss + lantern gold) -- forest + great tree
  const hz=D("heights");
  for(let k=0;k<170;k++){ const x=rnd(-154,234), z=rnd(-314,-186); if(Math.hypot(x-40,z+262)<20||Math.abs(x-40+(z+180)*.0)<5&&z>-200||PALMA.bridges.some(b=>Math.hypot(b.b[0]-x,b.b[1]-z)<16)) continue;
    if(Math.abs(segDist(x,z,40,-180,40,-250))<6) continue; tree(x,z,rnd(.8,1.5)); colliders.push({minX:x-.8,maxX:x+.8,minZ:z-.8,maxZ:z+.8}); miniRects.push({x,z,w:3,d:3,c:"#2a5a34"}); }
  { const x=70,z=-290; box(4,38,4,0x4a3424,x,19,z,null,.12); colliders.push({minX:x-2,maxX:x+2,minZ:z-2,maxZ:z+2});
    for(const [dx,dy,dz,s] of [[0,40,0,14],[-7,33,3,9],[7,34,-2,9],[0,30,-7,8]]){ const c=new THREE.Mesh(new THREE.SphereGeometry(s,10,8),toon(0x2f7a3a)); c.position.set(x+dx,dy,z+dz); ink(c,.3); scene.add(c); }
    for(let k=0;k<14;k++){ const l=new THREE.Mesh(new THREE.SphereGeometry(.5,6,4),glow(C.gold)); l.position.set(x+rnd(-14,14),rnd(26,44),z+rnd(-14,14)); scene.add(l); } miniRects.push({x,z,w:20,d:20,c:"#3a7a40"}); }
  for(let z=-252;z<-186;z+=10) for(const sx of [-4,4]){ inst("box",40+sx,1,z,.25,2,.25,0x3b2a1e); const l=new THREE.Mesh(new THREE.SphereGeometry(.25,6,4),glow(C.gold)); l.position.set(40+sx,2.1,z); scene.add(l); }
  putSign("THE HEIGHTS",14,"#7CB342",40,6,-186,0);
  // bridges
  PALMA.bridges.forEach(createBridge);
  buildInstancedBuildings(); buildInstances();
  // street rails
  addRail(-24,-14,-24,14,.6,C.gold); addRail(24,-14,24,14,.6,C.gold); addRail(-60,-60,40,-60,.6,C.cyan); addRail(-200,-96,-200,30,.6,C.purple); addRail(200,100,200,190,.6,0xFF2BD6);
  addRail(-60,190,80,190,.6,0xC0582B); addRail(180,-30,310,-30,.6,0xFFC83C);
  // cans on land
  const canGeo=new THREE.CylinderGeometry(.13,.13,.36,8);
  for(let i=0;i<70;i++){ let x,z,ok=false; for(let t=0;t<20&&!ok;t++){ const I=pick(PALMA.islands).box; x=rnd(I[0]+4,I[2]-4); z=rnd(I[1]+4,I[3]-4); ok=!colliders.some(c=>x>c.minX-1&&x<c.maxX+1&&z>c.minZ-1&&z<c.maxZ+1); }
    if(!ok) continue; const m=new THREE.Mesh(canGeo,glow(C.cyan)); m.position.set(x,.6,z); ink(m,.03); scene.add(m); cans.push(m); }
  PALMA.bridges.forEach(b=>{ for(let t=.2;t<.9;t+=.2){ const m=new THREE.Mesh(canGeo,glow(C.cyan)); m.position.set(b.a[0]+(b.b[0]-b.a[0])*t,.6,b.a[1]+(b.b[1]-b.a[1])*t); scene.add(m); cans.push(m); } });
  // tag spots
  for(const p of [[12,-30],[-40,30],[-150,-20],[-120,100],[40,100],[220,-50],[230,130],[280,170],[0,-240]]){
    const r=new THREE.Mesh(new THREE.RingGeometry(1.2,1.6,24),glow(C.purple,.8)); r.rotation.x=-Math.PI/2; r.position.set(p[0],.05,p[1]); scene.add(r); tagSpots.push({m:r,x:p[0],z:p[1],done:false}); }
  // mission beacons (story gold / crew cyan / side purple)
  for(const M of PALMA.missions){ const col=new THREE.Color(MCOL[M.type]).getHex(); const b=new THREE.Mesh(new THREE.CylinderGeometry(.6,.6,40,8,1,true),new THREE.MeshBasicMaterial({color:col,transparent:true,opacity:.18,blending:THREE.AdditiveBlending,depthWrite:false}));
    b.position.set(M.pos[0],20,M.pos[1]); scene.add(b); }
}
function crane(x,z){ for(const dx of [-5,5]) for(const dz of [-3,3]) box(.7,24,.7,C.crane,x+dx,12,z+dz,null,.06);
  box(.9,1,30,C.crane,x-5,24,z-6,null,.06); box(.9,1,30,C.crane,x+5,24,z-6,null,.06); box(11,1,1,C.crane,x,24,z+3,null,.06); box(3,2,2,0xffb000,x,22.5,z-4,null,.05);
  const red=new THREE.Mesh(new THREE.SphereGeometry(.4,6,4),glow(0xff2020)); red.position.set(x,25.5,z-20); scene.add(red);
  for(const dx of [-5,5]) colliders.push({minX:x+dx-.5,maxX:x+dx+.5,minZ:z-3.5,maxZ:z+3.5}); miniRects.push({x,z,w:11,d:7,c:"#E0661C"}); }
function createClubArch(x,z){ box(1,10,1,0x1a1a2a,x-6.5,5,z,null,.06); box(1,10,1,0x1a1a2a,x+6.5,5,z,null,.06); box(14,1.8,1,0x1a1a2a,x,10,z,null,.06);
  box(.2,10,1.05,0xFF2BD6,x-6,5,z,null,0); box(.2,10,1.05,C.cyan,x+6,5,z,null,0);
  putSign("CLUB",8,"#FF2BD6",x,10,z+.55,0,{size:190,glow:50}); putSign("CLUB",8,"#00E5FF",x,10,z-.55,Math.PI,{size:190,glow:50});
  colliders.push({minX:x-7,maxX:x-6,minZ:z-.5,maxZ:z+.5},{minX:x+6,maxX:x+7,minZ:z-.5,maxZ:z+.5}); }
function createPlaza(){ // Terminal Plaza (0,0): cyan holo crystal tower, gold mission-launch ring, TERMINAL tower, GATE 07, ARRIVALS, Police HQ
  flat(1,1,0,0,0,0).visible=false;
  const plaza=new THREE.Mesh(new THREE.CircleGeometry(26,48),toon(0x2a2d3a)); plaza.rotation.x=-Math.PI/2; plaza.position.set(0,.025,0); scene.add(plaza);
  const rim=new THREE.Mesh(new THREE.RingGeometry(25.6,26,64),glow(C.gold,.8)); rim.rotation.x=-Math.PI/2; rim.position.set(0,.04,0); scene.add(rim);
  const ring=new THREE.Mesh(new THREE.RingGeometry(8.5,10,64),glow(C.gold,.9)); ring.rotation.x=-Math.PI/2; ring.position.set(0,.05,0); scene.add(ring);
  const rt=sign("TERMINAL PLAZA · MISSION LAUNCH",14,"#FFD700",{size:70,glow:10,stroke:6}); rt.rotation.x=-Math.PI/2; rt.position.set(0,.07,12.5); scene.add(rt);
  const tor=new THREE.Mesh(new THREE.TorusGeometry(3,.22,8,40),glow(C.gold)); tor.position.set(0,14,0); ink(tor,.06); scene.add(tor); animated.push(t=>tor.rotation.y=t*1.2);
  const tx=0,tz=-46; box(12,70,12,0x223055,tx,35,tz,null,.12); box(7,12,7,0x2b3c6a,tx,76,tz,null,.08); box(1,14,1,0x888899,tx,89,tz,null,.04);
  for(let y=6;y<70;y+=6) inst("glow",tx,y,tz,12.15,.2,12.15,C.cyan);
  colliders.push({minX:tx-6,maxX:tx+6,minZ:tz-6,maxZ:tz+6}); miniRects.push({x:tx,z:tz,w:12,d:12,c:"#3a5590"});
  putSign("TERMINAL",10,"#00E5FF",tx,4,tz+6.15,0,{size:160,glow:40});
  box(8,6,4,0x1c2440,-16,3,-34,null,.06); colliders.push({minX:-20,maxX:-12,minZ:-36,maxZ:-32}); putSign("GATE 07",6,"#FFD700",-16,4.5,-31.9,0);
  box(8,6,4,0x1c2440,16,3,-34,null,.06); colliders.push({minX:12,maxX:20,minZ:-36,maxZ:-32}); putSign("ARRIVALS",6,"#00E5FF",16,4.5,-31.9,0);
  // holo crystal on circular pad (cyan)
  const pad=new THREE.Mesh(new THREE.CylinderGeometry(5,5.4,.4,40),toon(0x1c1f2c)); pad.position.set(0,.2,0); ink(pad,.06); scene.add(pad);
  const pr=new THREE.Mesh(new THREE.RingGeometry(4.2,4.8,48),glow(C.cyan)); pr.rotation.x=-Math.PI/2; pr.position.set(0,.42,0); scene.add(pr);
  const hm=new THREE.MeshBasicMaterial({color:0x00E5FF,transparent:true,opacity:.35,blending:THREE.AdditiveBlending,depthWrite:false});
  const holo=new THREE.Group(); holo.position.set(0,.4,0); scene.add(holo);
  [[2.4,8],[1.8,6],[1.2,5],[.6,4]].reduce((y,[r,h])=>{ const c=new THREE.Mesh(new THREE.CylinderGeometry(r*.8,r,h,6,1,true),hm); c.position.y=y+h/2; holo.add(c);
    const w=new THREE.Mesh(new THREE.CylinderGeometry(r*.8,r,h,6,4,true),new THREE.MeshBasicMaterial({color:0x7ff4ff,wireframe:true,transparent:true,opacity:.5})); w.position.y=y+h/2; holo.add(w); return y+h; },0);
  const beam=new THREE.Mesh(new THREE.CylinderGeometry(.15,.6,80,8,1,true),hm); beam.position.y=50; holo.add(beam);
  animated.push(t=>{ holo.rotation.y=t*.4; hm.opacity=.28+Math.sin(t*3)*.08; });
  colliders.push({minX:-5,maxX:5,minZ:-5,maxZ:5});
  // Police HQ (60,-70) with searchlights
  box(22,16,16,0x1d2f6a,60,8,-70,null,.1); colliders.push({minX:49,maxX:71,minZ:-78,maxZ:-62}); miniRects.push({x:60,z:-70,w:22,d:16,c:"#3D7BFF"});
  box(22.2,.4,16.2,0x3D7BFF,60,16,-70,null,0); box(3,.6,1,0xff2020,56,16.6,-64,null,0); box(3,.6,1,0x2050ff,64,16.6,-64,null,0);
  putSign("POLICE HQ",10,"#3D7BFF",60,12,-61.85,0); searchlight(53,16.5,-72); searchlight(67,16.5,-72); searchlight(-30,0,-80,0xffe8a0); searchlight(30,0,40,0x8fb8ff);
  tag(0,5,-46.2,2.4,-21,-Math.PI/2);
}
function createBridge(b){
  const [ax,az]=b.a, [bx,bz]=b.b, L=Math.hypot(bx-ax,bz-az), ang=Math.atan2(bx-ax,bz-az), mx=(ax+bx)/2, mz=(az+bz)/2;
  const g=new THREE.Group(); g.position.set(mx,0,mz); g.rotation.y=ang; scene.add(g);
  box(8,.8,L+16,0x2a2d3a,0,-.39,0,g,.08);
  box(.25,.25,L+16,b.color,-4,.1,0,g,0); box(.25,.25,L+16,b.color,4,.1,0,g,0);
  box(.2,.02,L+10,b.color,0,.02,0,g,0);
  const ux=Math.sin(ang), uz=Math.cos(ang), px=uz, pz=-ux; // along / perpendicular
  for(let t=-L/2+10;t<L/2-5;t+=16) inst("box",mx+ux*t,-6,mz+uz*t,3,11,3,0x3a3d4a);
  for(const tt of [-L/2+4,L/2-4]) for(const s of [-1,1]){ const x=mx+ux*tt+px*s*5, z=mz+uz*tt+pz*s*5; inst("box",x,11,z,1.2,22,1.2,0x2a2d3a); inst("glow",x,11,z,1.3,20,.4,b.color); colliders.push({minX:x-.6,maxX:x+.6,minZ:z-.6,maxZ:z+.6}); }
  // cables: glowing lines from towers to mid
  for(const s of [-1,1]) for(const e of [-1,1]){ const len=Math.hypot(L/2-4,18); const c=new THREE.Mesh(new THREE.BoxGeometry(.08,.08,len),glow(b.color,.6)); c.position.set(s*5,13,e*(L/2-4)/2); c.rotation.x=e*Math.atan2(18,L/2-4)*-1; g.add(c); }
  // 2 grind rails, 3 m apart, 1.0 m high
  for(const s of [-1.5,1.5]) addRail(ax+px*s,az+pz*s,bx+px*s,bz+pz*s,1.0,b.color);
  const sg=sign(b.name,9,b.css,{size:150,glow:40}); sg.position.set(0,20,-L/2+4); sg.rotation.y=Math.PI; g.add(sg); const sg2=sg.clone(); sg2.position.z=L/2-4; sg2.rotation.y=0; g.add(sg2);
}
