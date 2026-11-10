// ===== CREWHOUSE KIT (Palma Builder): one shared, parameterised crew garage interior =====
// Upstairs = exact Kogarasumaru ref (pod loft); downstairs = A-T tuning bay. ONE kit instance (shared geometry, materials, atlas)
// is re-parented into whichever garage the camera is near; per-crew colour via uniforms/instanceColor, logos via one logo atlas page.
// Old dressBase interiors stay as the far LOD and are hidden while the kit is active in that garage. No skateboards anywhere.
(function(){
const KIT_LOGO_SLOT={codee:0,karasu:1,static:2,behemoth:3,anubis:4,ttt:5,genesis:6,forest:7,volt:8,rustclaw:9}; // volt=shared/crew-logos/volt.png slot8; rustclaw=rust-claw.png slot9 (packed 2026-11-05)
// per-crew theme: c1 = neon (crews.js defaults.wheelGlow), c2 = accent (crews.js defaults.gold), name = world.js PALMA.garages name
function kitTheme(gid){ const G=(PALMA.garages||[]).find(q=>q.crew===gid)||{name:gid,color:"#00E5FF"};
  // CREWS = playable; CREW_RIVALS = Volt/Rust Claw (Systems, kept out of CREWS on purpose). Same defaults.wheelGlow/gold keys.
  const cr=(typeof CREWS!=='undefined'?CREWS:[]).find(q=>q.garage===gid)||(typeof CREW_RIVALS!=='undefined'&&CREW_RIVALS.find(q=>q.garage===gid));
  const d=cr&&cr.defaults||{}; const T={id:gid,name:G.name,c1:d.wheelGlow!=null?d.wheelGlow:new THREE.Color(G.color).getHex(),c2:d.gold!=null?d.gold:0xb040ff,logo:KIT_LOGO_SLOT[gid]||0,
    sign:"AirTrecks",poster:G.name+" CREW",bay:[G.name,"GARAGE BAY 01","A-T TUNING & OPS"],street:"PALMA CITY"};
  if(gid==="karasu") Object.assign(T,{c1:0x00e5ff,c2:0x9a3cff,sign:"AirTrecks",poster:"KARASU CREW",bay:["KOGARASUMARU","GARAGE BAY 01","A-T TUNING & OPS"]}); // locked ref palette, purple accents downstairs
  return Object.assign(T,(window.KIT_THEME_OVERRIDE||{})[gid]||{}); }
window.kitTheme=kitTheme; window.KOG_THEME=null;

// ---------- atlas (2048², mips) ----------
const AT=document.createElement('canvas'); AT.width=AT.height=2048; const ax=AT.getContext('2d'); const kitAtlasTex=new THREE.CanvasTexture(AT);
kitAtlasTex.encoding=THREE.sRGBEncoding; kitAtlasTex.anisotropy=4;
const CELLS={}; { let x=0,y=0,rowH=0; const add=(n,w,h)=>{ if(x+w>2048){ x=0; y+=rowH; rowH=0; } CELLS[n]={x,y,w,h}; x+=w; rowH=Math.max(rowH,h); };
  add('city',1024,384); add('tv',512,288); add('map',512,288);
  add('street',512,448); add('rug1',512,384); add('decal',448,448); add('signbig',512,192);
  add('racers',256,448); add('nosleep',256,384); add('club',256,256); add('crewp',256,384); add('banner',256,256); add('side',256,448); add('fridge',256,448); add('lockers',256,384);
  add('rug2',384,256); add('mq1',384,96); add('mq2',384,96); add('ops',384,96); add('bay2',384,192); add('airt',512,128);
  add('scr1',256,256); add('scr2',256,256); add('laptop',256,160); add('labels',512,256); add('jacket',192,256); add('snacks',256,128); add('chips',128,128); add('pillow',128,128); add('can',128,128); add('paper',128,128); add('sky',128,128); add('rugfloor',256,256);
  for(let i=1;i<=6;i++) add('pod'+i,128,64); add('black',64,64); }
const LOGO=new Image(); let logoReady=false; LOGO.onload=()=>{ logoReady=true; if(KIT.theme) kitDrawAtlas(KIT.theme); }; LOGO.src='assets/kit/kit_logos.png';
const css=h=>'#'+new THREE.Color(h).getHexString();
function nt(t,x,y,size,col,o){ o=o||{}; ax.save(); ax.font=(o.w||'900')+' '+size+'px '+(o.f||'Impact, "Arial Black", sans-serif'); ax.textAlign=o.a||'center'; ax.textBaseline='middle';
  ax.shadowColor=col; ax.shadowBlur=o.glow==null?size*.35:o.glow; ax.fillStyle=o.fill||col; ax.fillText(t,x,y); if(o.glow!==0){ ax.shadowBlur*=.4; ax.fillText(t,x,y);} ax.restore(); }
function cell(n,bg){ const c=CELLS[n]; ax.save(); ax.beginPath(); ax.rect(c.x,c.y,c.w,c.h); ax.clip(); if(bg){ ax.fillStyle=bg; ax.fillRect(c.x,c.y,c.w,c.h); } return c; }
function logo(T,x,y,s){ if(!logoReady) return; const i=T.logo; ax.drawImage(LOGO,(i%4)*256,((i/4)|0)*256,256,256,x-s/2,y-s/2,s,s); }
let seedA=7; const ra=()=>(seedA=(seedA*16807)%2147483647)/2147483647;
function stickers(c,n,C1){ const cols=[C1,'#ffffff','#ff3b6b','#ffd23a','#9a3cff','#111']; for(let i=0;i<n;i++){ ax.save(); ax.translate(c.x+ra()*c.w,c.y+ra()*c.h); ax.rotate((ra()-.5)*.8); const w=14+ra()*34,h=10+ra()*24; ax.fillStyle=cols[i%6]; ax.fillRect(-w/2,-h/2,w,h); ax.fillStyle=i%6===1?'#111':'#fff'; ax.font='bold 9px sans-serif'; ax.fillText(['A-T','RYD','2099','KRS','NO SLP','★'][i%6],-w/2+2,2); ax.restore(); } }
function skyline(c,C1,dense){ const g=ax.createLinearGradient(0,c.y,0,c.y+c.h); g.addColorStop(0,'#030612'); g.addColorStop(.7,'#0a1630'); g.addColorStop(1,'#0d2340'); ax.fillStyle=g; ax.fillRect(c.x,c.y,c.w,c.h);
  for(let L=0;L<2;L++) for(let x=c.x;x<c.x+c.w;){ const w=20+ra()*(L?60:40), h=c.h*(L?.35+ra()*.55:.5+ra()*.45); const top=c.y+c.h-h; ax.fillStyle=L?'#0b1222':'#121b30'; ax.fillRect(x,top,w-3,h);
    for(let wy=top+6;wy<c.y+c.h-4;wy+=7) for(let wx=x+3;wx<x+w-6;wx+=6) if(ra()<(dense||.35)){ ax.fillStyle=ra()<.7?'rgba(160,220,255,.75)':(ra()<.5?C1:'rgba(255,200,120,.7)'); ax.fillRect(wx,wy,3,3); } x+=w; } }
function kitDrawAtlas(T){ seedA=7; const C1=css(T.c1), C2=css(T.c2); ax.clearRect(0,0,2048,2048); ax.fillStyle='#050608'; ax.fillRect(0,0,2048,2048);
  let c=cell('city'); skyline(c,C1,.75); { const g=ax.createRadialGradient(c.x+c.w*.5,c.y+c.h,10,c.x+c.w*.5,c.y+c.h,c.w*.6); g.addColorStop(0,'rgba(80,200,255,.35)'); g.addColorStop(1,'rgba(0,0,0,0)'); ax.fillStyle=g; ax.fillRect(c.x,c.y,c.w,c.h); } ax.fillStyle='rgba(0,0,0,.9)'; for(let k=1;k<6;k++) ax.fillRect(c.x+k*c.w/6-2,c.y,4,c.h); ax.fillRect(c.x,c.y+c.h*.5-3,c.w,6); ax.restore();
  c=cell('tv','#020409'); { const cx=c.x+c.w/2, hy=c.y+c.h*.42; skyline({x:c.x,y:c.y,w:c.w,h:c.h*.42},C1,.5); ax.fillStyle='#04121a'; ax.beginPath(); ax.moveTo(c.x,c.y+c.h); ax.lineTo(cx-8,hy); ax.lineTo(cx+8,hy); ax.lineTo(c.x+c.w,c.y+c.h); ax.fill();
    ax.strokeStyle=C1; ax.shadowColor=C1; ax.shadowBlur=12; ax.lineWidth=4; for(const s of [-1,1]){ ax.beginPath(); ax.moveTo(cx+s*8,hy); ax.lineTo(cx+s*c.w*.5,c.y+c.h); ax.stroke(); }
    ax.setLineDash([16,14]); ax.lineWidth=3; ax.beginPath(); ax.moveTo(cx,hy); ax.lineTo(cx,c.y+c.h); ax.stroke(); ax.setLineDash([]);
    for(let k=0;k<6;k++){ const t=k/6, yy=hy+(c.h*.58)*t*t; ax.globalAlpha=.6; ax.fillStyle=C1; ax.fillRect(cx-c.w*.45*t-20,yy,10,4); ax.fillRect(cx+c.w*.45*t+10,yy,10,4); } ax.globalAlpha=1;
    ax.shadowBlur=0; ax.fillStyle='#0b0d12'; ax.beginPath(); ax.ellipse(cx,c.y+c.h+10,170,70,0,Math.PI,0); ax.fill(); ax.strokeStyle=C1; ax.lineWidth=3; ax.stroke(); ax.beginPath(); ax.arc(cx,c.y+c.h-26,26,0,7); ax.stroke();
    nt('2:13.48',c.x+60,c.y+20,18,C1,{a:'left'}); nt('POS 1/8',c.x+c.w-60,c.y+20,18,C1); nt('312 km/h',c.x+c.w-70,c.y+c.h-20,20,'#fff'); ax.restore(); }
  c=cell('map','#02070c'); ax.strokeStyle=C1; ax.globalAlpha=.35; ax.lineWidth=1; for(let k=0;k<20;k++){ ax.beginPath(); ax.moveTo(c.x+ra()*c.w,c.y); ax.lineTo(c.x+ra()*c.w,c.y+c.h); ax.stroke(); ax.beginPath(); ax.moveTo(c.x,c.y+ra()*c.h); ax.lineTo(c.x+c.w,c.y+ra()*c.h); ax.stroke(); }
    ax.globalAlpha=1; ax.lineWidth=4; ax.shadowColor=C1; ax.shadowBlur=10; ax.beginPath(); ax.moveTo(c.x+40,c.y+220); for(let k=0;k<8;k++) ax.lineTo(c.x+60+k*55,c.y+60+ra()*180); ax.stroke(); ax.strokeStyle=C2; ax.beginPath(); ax.moveTo(c.x+30,c.y+60); ax.bezierCurveTo(c.x+200,c.y+300,c.x+300,c.y,c.x+480,c.y+200); ax.stroke();
    for(let k=0;k<7;k++){ ax.fillStyle=k%2?C2:'#fff'; ax.beginPath(); ax.arc(c.x+40+ra()*430,c.y+30+ra()*230,6,0,7); ax.fill(); } nt('PALMA CITY // CREW TURF',c.x+130,c.y+18,16,C1,{a:'left'}); ax.restore();
  c=cell('street'); skyline(c,C2,.4); ax.fillStyle='#0b0f18'; ax.fillRect(c.x,c.y+c.h*.72,c.w,c.h*.28); ax.fillStyle=C2; ax.globalAlpha=.25; ax.fillRect(c.x,c.y+c.h*.74,c.w,8); ax.globalAlpha=1;
    nt(T.street,c.x+c.w/2,c.y+c.h*.52,64,C2); nt('OCEAN BLVD',c.x+c.w/2,c.y+c.h*.62,30,C1); ax.restore();
  c=cell('rug1','#06080a'); ax.strokeStyle=C1; ax.shadowColor=C1; ax.shadowBlur=6; for(const [i,lw] of [[14,8],[34,4],[50,3]]){ ax.lineWidth=lw; ax.strokeRect(c.x+i,c.y+i,c.w-2*i,c.h-2*i); }
    ax.fillStyle=C1; for(const s of [-1,1]) for(let k=0;k<9;k++){ ax.save(); ax.translate(c.x+c.w/2,c.y+c.h/2+s*110); ax.rotate((k-4)*.28+(s<0?Math.PI:0)); ax.beginPath(); ax.moveTo(-6,0); ax.lineTo(0,-90); ax.lineTo(6,0); ax.fill(); ax.restore(); } ax.restore();
  c=cell('rug2','#05080a'); ax.globalAlpha=.85; for(let k=0;k<140;k++){ ax.fillStyle=k%3?C1:'#0d2a30'; ax.save(); ax.translate(c.x+ra()*c.w,c.y+ra()*c.h); ax.rotate(ra()*3); ax.fillRect(-12,-3,24,6); ax.restore(); } ax.globalAlpha=1; ax.strokeStyle=C1; ax.lineWidth=6; ax.strokeRect(c.x+6,c.y+6,c.w-12,c.h-12); ax.restore();
  c=cell('rugfloor','#05070a'); ax.strokeStyle=C1; ax.lineWidth=5; ax.strokeRect(c.x+10,c.y+10,c.w-20,c.h-20); logo(T,c.x+128,c.y+128,200); ax.restore();
  c=cell('decal'); ax.clearRect(c.x,c.y,c.w,c.h); ax.fillStyle='#0a0b0d'; ax.fillRect(c.x,c.y,c.w,c.h); ax.globalAlpha=.85; logo(T,c.x+c.w/2,c.y+c.h/2,420); ax.globalAlpha=1; ax.restore();
  c=cell('signbig','#0a0a0c'); ax.strokeStyle=C1; ax.lineWidth=6; ax.strokeRect(c.x+6,c.y+6,c.w-12,c.h-12); logo(T,c.x+80,c.y+96,140); nt(T.bay[0],c.x+300,c.y+52,T.bay[0].length>12?40:56,C1); nt(T.bay[1],c.x+300,c.y+108,30,'#fff',{glow:6}); nt(T.bay[2],c.x+300,c.y+152,30,C2); ax.restore();
  c=cell('racers','#07090c'); nt("RACER'S",c.x+128,c.y+90,62,C1); nt("MEET",c.x+128,c.y+165,70,C1); nt("-",c.x+128,c.y+225,60,C1); nt("2099",c.x+128,c.y+300,74,C1); stickers({x:c.x,y:c.y+390,w:256,h:56},6,C1); ax.restore();
  c=cell('nosleep','#0c0d0f'); ax.strokeStyle='#ddd'; ax.lineWidth=3; ax.strokeRect(c.x+8,c.y+8,240,368); nt("RACER'S",c.x+128,c.y+60,44,'#f2f2f2',{glow:0}); nt("MEET",c.x+128,c.y+112,48,'#f2f2f2',{glow:0}); nt("NO SLEEP",c.x+128,c.y+172,42,C1,{glow:0}); nt("MEET",c.x+128,c.y+226,46,'#f2f2f2',{glow:0}); nt("TONIGHT",c.x+128,c.y+290,42,'#f2f2f2',{glow:0}); ax.restore();
  c=cell('club','#08090b'); nt("NO SLEEP",c.x+128,c.y+90,46,'#f0f0f0',{glow:0,f:'"Brush Script MT", cursive'}); nt("CLUB",c.x+128,c.y+160,60,C1); ax.restore();
  c=cell('crewp','#c8a26a'); ax.fillStyle='#1b140c'; ax.fillRect(c.x+14,c.y+14,228,356); logo(T,c.x+128,c.y+150,200); nt(T.poster,c.x+128,c.y+300,T.poster.length>12?24:34,'#f4d9a0',{glow:0}); ax.restore();
  c=cell('banner','#0c0c0e'); logo(T,c.x+128,c.y+90,150); nt("RACER'S MEET",c.x+128,c.y+190,30,'#eee',{glow:0}); nt("TONIGHT",c.x+128,c.y+228,30,C1); ax.restore();
  c=cell('side','#0b0c0e'); for(let k=0;k<26;k++){ ax.strokeStyle=k%4?'#cfd3d8':C1; ax.lineWidth=2+ra()*5; ax.beginPath(); ax.moveTo(c.x+ra()*256,c.y+ra()*512); ax.quadraticCurveTo(c.x+ra()*256,c.y+ra()*512,c.x+ra()*256,c.y+ra()*512); ax.stroke(); } nt("NO SLEEP",c.x+128,c.y+380,40,'#fff',{glow:0,f:'"Brush Script MT", cursive'}); nt("CLUB",c.x+128,c.y+430,40,C1); nt("AT",c.x+128,c.y+120,90,C1); ax.restore();
  c=cell('fridge','#9aa1a8'); { const g=ax.createLinearGradient(c.x,0,c.x+c.w,0); g.addColorStop(0,'#6d747b'); g.addColorStop(.5,'#b7bec4'); g.addColorStop(1,'#5f666c'); ax.fillStyle=g; ax.fillRect(c.x,c.y,c.w,c.h); } ax.fillStyle='#222'; ax.fillRect(c.x,c.y+180,c.w,5); stickers({x:c.x+10,y:c.y+20,w:236,h:470},22,C1); ax.fillStyle='#e00'; ax.fillRect(c.x+120,c.y+60,110,48); nt('COLA',c.x+175,c.y+84,38,'#fff',{glow:0}); nt('COLA',c.x+128,c.y+300,50,C1); ax.restore();
  c=cell('lockers','#2a2f36'); for(let k=0;k<3;k++){ ax.strokeStyle='#050505'; ax.lineWidth=4; ax.strokeRect(c.x+k*85+2,c.y+2,82,380); for(let v=0;v<6;v++) ax.fillRect(c.x+k*85+20,c.y+20+v*8,40,3); } stickers(c,110,C1); ax.restore();
  c=cell('mq1','#04070a'); nt('STREET RACE',c.x+192,c.y+32,50,C1,{glow:6}); nt('2099',c.x+192,c.y+76,40,'#ffffff',{glow:4}); ax.restore();
  c=cell('mq2','#04070a'); nt('NEO-PUCK',c.x+192,c.y+50,52,C1); ax.restore();
  c=cell('ops','#04070a'); nt('OPS / LOGISTICS',c.x+192,c.y+48,44,C1); ax.restore();
  c=cell('bay2','#0d0f12'); ax.strokeStyle='#888'; ax.lineWidth=3; ax.strokeRect(c.x+6,c.y+6,c.w-12,c.h-12); nt('BAY 02',c.x+192,c.y+66,56,'#e8e8e8',{glow:0}); nt('GEAR STORAGE',c.x+192,c.y+132,40,C1,{glow:4}); ax.restore();
  c=cell('airt','#030507'); nt(T.sign,c.x+256,c.y+64,80,C1,{f:'"Arial Black", sans-serif'}); ax.restore();
  for(const [n,hue] of [['scr1',0],['scr2',1]]){ c=cell(n,'#020810'); if(!hue){ skyline({x:c.x,y:c.y,w:256,h:120},C1,.5); ax.strokeStyle=C1; ax.lineWidth=3; ax.beginPath(); ax.moveTo(c.x,c.y+256); ax.lineTo(c.x+120,c.y+120); ax.lineTo(c.x+136,c.y+120); ax.lineTo(c.x+256,c.y+256); ax.stroke(); }
    else { ax.strokeStyle=C1; ax.lineWidth=4; ax.strokeRect(c.x+20,c.y+30,216,196); ax.beginPath(); ax.moveTo(c.x+128,c.y+30); ax.lineTo(c.x+128,c.y+226); ax.stroke(); ax.beginPath(); ax.arc(c.x+128,c.y+128,30,0,7); ax.stroke(); ax.fillStyle='#fff'; ax.beginPath(); ax.arc(c.x+90,c.y+100,9,0,7); ax.fill(); } ax.restore(); }
  c=cell('laptop','#0d4656'); ax.fillStyle='#1b7f96'; ax.fillRect(c.x,c.y,256,24); ax.strokeStyle='#e8fdff'; ax.lineWidth=3; for(let k=0;k<6;k++) ax.strokeRect(c.x+10+k*40,c.y+30+((k*37)%60),34,60); ax.beginPath(); ax.arc(c.x+128,c.y+80,40,0,7); ax.stroke(); nt('A-T DIAG',c.x+60,c.y+13,18,'#ffffff'); ax.restore();
  c=cell('labels','#c09a5e'); { const L=[['A-T CORE','BATTERY'],['110MM','WHEELS'],['FRAME KITS',''],['HELMETS',''],['GLOW TAIL',''],['A-T BATTERY','PACKS'],['FRAGILE',''],['T-REX','PARTS']]; L.forEach((s,i)=>{ const x=c.x+(i%4)*128, y=c.y+((i/4)|0)*128; ax.fillStyle=i%2?'#151719':'#b88c50'; ax.fillRect(x+4,y+4,120,120); ax.fillStyle=i%2?'#e8e8e8':'#1a1208'; ax.font='bold 17px sans-serif'; ax.textAlign='center'; ax.fillText(s[0],x+64,y+56); ax.fillText(s[1],x+64,y+80); ax.fillStyle=C1; ax.fillRect(x+20,y+96,88,5); }); } ax.restore();
  c=cell('jacket','#0b0b0d'); ax.fillStyle='#16171a'; ax.beginPath(); ax.moveTo(c.x+30,c.y+20); ax.lineTo(c.x+162,c.y+20); ax.lineTo(c.x+190,c.y+250); ax.lineTo(c.x+2,c.y+250); ax.fill(); logo(T,c.x+96,c.y+110,120); ax.fillStyle=C1; ax.fillRect(c.x+10,c.y+236,172,6); ax.restore();
  c=cell('snacks','#101215'); for(let k=0;k<10;k++){ ax.fillStyle=['#e8b030','#d84040','#30a0e0','#f0f0f0','#40c060'][k%5]; ax.fillRect(c.x+4+k*25,c.y+30+(k%3)*6,21,90); } ax.restore();
  c=cell('paper','#e9e7df'); ax.fillStyle='#9aa'; for(let k=0;k<9;k++) ax.fillRect(c.x+12,c.y+16+k*12,80+ra()*30,3); ax.restore();
  c=cell('sky','#0b1a33'); for(let k=0;k<40;k++){ ax.fillStyle='rgba(200,220,255,'+ra()+')'; ax.fillRect(c.x+ra()*128,c.y+ra()*128,2,2); } ax.restore();
  for(let i=1;i<=6;i++){ c=cell('pod'+i,'#05080b'); ax.strokeStyle=C1; ax.lineWidth=3; ax.strokeRect(c.x+3,c.y+3,122,58); nt('POD 0'+i,c.x+64,c.y+32,30,C1); ax.restore(); }
  c=cell('black','#030303'); ax.restore();
  c=cell('chips','#22262c'); ax.fillStyle='#0b0d10'; ax.fillRect(c.x,c.y+40,128,48); nt('CHIPS',c.x+64,c.y+64,30,C1,{glow:2}); ax.fillStyle='#e0a040'; ax.beginPath(); ax.arc(c.x+64,c.y+105,14,0,7); ax.fill(); ax.restore();
  c=cell('pillow','#0b2a30'); ax.strokeStyle=C1; ax.lineWidth=5; ax.strokeRect(c.x+10,c.y+10,108,108); for(let k=0;k<6;k++){ ax.beginPath(); ax.moveTo(c.x+20+k*16,c.y+20); ax.lineTo(c.x+20+k*16,c.y+108); ax.globalAlpha=.4; ax.stroke(); ax.globalAlpha=1; } ax.restore();
  c=cell('can','#8a9096'); ax.fillStyle='#15181c'; ax.fillRect(c.x,c.y+30,128,68); nt('KRS',c.x+64,c.y+64,34,C1,{glow:2}); ax.fillStyle=C1; ax.fillRect(c.x,c.y+100,128,6); ax.restore();
  kitAtlasTex.needsUpdate=true; }

// ---------- shared materials (MeshStandardMaterial PBR + emissive neon) ----------
const TL=new THREE.TextureLoader(); const K2=window.SR_KTX2&&window.SR_KTX2.on; // ?ktx2=1 (Rydah Optimizer step4): assets/world_ktx2/<n>.ktx2 (512, pre-flipped, ETC1S colour/rough, UASTC normal); falls back to the jpg on any failure
const txJ=(n,srgb)=>{ const t=TL.load('assets/kit/'+n+'.jpg'); t.wrapS=t.wrapT=THREE.RepeatWrapping; if(srgb) t.encoding=THREE.sRGBEncoding; t.anisotropy=4; return t; };
const txSwap=(from,to)=>{ for(const m of Object.values(typeof MAT!=='undefined'?MAT:{})) for(const sl of ['map','normalMap','roughnessMap']) if(m&&m[sl]===from){ m[sl]=to; m.needsUpdate=true; } };
const txNow=(n,srgb)=>{ if(!K2) return txJ(n,srgb); const t=new THREE.Texture(); let tries=0;
  const swap=c=>{ for(const m of Object.values(typeof MAT!=='undefined'?MAT:{})) for(const sl of ['map','normalMap','roughnessMap']) if(m&&m[sl]===t){ m[sl]=c; m.needsUpdate=true; } };
  const fb=()=>swap(txJ(n,srgb));
  const go=()=>{ try{ const L=typeof window.SR_KTX2.loader==='function'&&window.SR_KTX2.loader(); if(!L){ if(++tries>300) return fb(); return requestAnimationFrame(go); }
    L.load('assets/world_ktx2/'+n+'.ktx2',c=>{ c.wrapS=c.wrapT=THREE.RepeatWrapping; if(srgb) c.encoding=THREE.sRGBEncoding; c.anisotropy=4; c.flipY=false; swap(c); },undefined,fb); }catch(e){ console.warn('[kit ktx2] fallback jpg',n,e); fb(); } };
  go(); return t; };
// lazy: MAT gets placeholders at spawn; the real jpg/ktx2 loads run on first approach (kitLazy)
const KIT_DEFER=[]; const tx=(n,srgb)=>{ const t=new THREE.Texture(); KIT_DEFER.push(()=>{ let r; try{ r=txNow(n,srgb); }catch(e){ console.warn('[kit ktx2] init failed, jpg',n,e); r=txJ(n,srgb); } txSwap(t,r); }); return t; };
const U={uC1:{value:new THREE.Color(0x00e5ff)},uC2:{value:new THREE.Color(0x9a3cff)},uKL:{value:Array.from({length:8},()=>new THREE.Vector3(0,-999,0))},uKC:{value:Array.from({length:8},()=>new THREE.Color(0))}};
// fake neon fill lights (8 world-space points, no scene lights added -> no program churn for the rest of the world); r128 chunk names only
function kitify(m,isBasic){ m.onBeforeCompile=s=>{ Object.assign(s.uniforms,U);
  s.vertexShader='attribute vec2 kt;\nvarying vec2 vKt;\nvarying vec3 vKW;\nvarying vec3 vKN;\n'+s.vertexShader.replace('#include <project_vertex>',`#include <project_vertex>
  vKt=kt; vec4 kw=vec4(transformed,1.0); vec3 kn=normal;
  #ifdef USE_INSTANCING
  kw=instanceMatrix*kw; kn=mat3(instanceMatrix)*kn;
  #endif
  kw=modelMatrix*kw; vKW=kw.xyz; vKN=normalize(mat3(modelMatrix)*kn);`);
  s.fragmentShader='uniform vec3 uC1;\nuniform vec3 uC2;\nuniform vec3 uKL[8];\nuniform vec3 uKC[8];\nvarying vec2 vKt;\nvarying vec3 vKW;\nvarying vec3 vKN;\n'+s.fragmentShader.replace('#include <color_fragment>',`#include <color_fragment>
  diffuseColor.rgb=mix(diffuseColor.rgb,uC1*${isBasic?'1.0':'0.9'},clamp(vKt.x,0.0,1.0)); diffuseColor.rgb=mix(diffuseColor.rgb,uC2,clamp(vKt.y,0.0,1.0));`)
  +(isBasic?'':'').replace('','');
  if(!isBasic) s.fragmentShader=s.fragmentShader.replace('#include <emissivemap_fragment>',`#include <emissivemap_fragment>
  { vec3 kacc=vec3(0.0); for(int i=0;i<8;i++){ vec3 d=uKL[i]-vKW; float l2=dot(d,d); kacc+=uKC[i]*(0.25+0.75*max(dot(normalize(vKN),d*inversesqrt(l2+1e-4)),0.0))/(1.0+l2*0.35); }
    totalEmissiveRadiance+=diffuseColor.rgb*(kacc*1.2+vec3(0.42,0.37,0.30)); }`); };
  m.customProgramCacheKey=()=>'kit'+(isBasic?'b':'s'); return m; }
const pm=(n,o)=>kitify(new THREE.MeshStandardMaterial(o),false);
const MAT={
  conc:pm('conc',{map:tx('Concrete034_Color',1),normalMap:tx('Concrete034_NormalGL'),roughnessMap:tx('Concrete034_Roughness'),roughness:1,metalness:0,color:0x6a6e74,vertexColors:true}),
  wet:pm('wet',{map:tx('Concrete046_Color',1),normalMap:tx('Concrete046_NormalGL'),roughnessMap:tx('Concrete046_Roughness'),roughness:.32,metalness:.15,color:0x4a4f56,vertexColors:true,normalScale:new THREE.Vector2(.5,.5)}),
  metal:pm('metal',{map:tx('PaintedMetal004_Color',1),normalMap:tx('PaintedMetal004_NormalGL'),roughnessMap:tx('PaintedMetal004_Roughness'),roughness:.8,metalness:.55,color:0xffffff,vertexColors:true}),
  soft:pm('soft',{roughness:.88,metalness:0,color:0xffffff,vertexColors:true}),
  neon:kitify(new THREE.MeshBasicMaterial({color:0xffffff,vertexColors:true,toneMapped:false}),true),
  atlas:kitify(new THREE.MeshBasicMaterial({map:kitAtlasTex,color:0xffffff,vertexColors:true,toneMapped:false}),true),
  inst:pm('inst',{roughness:.45,metalness:.3,color:0xffffff}) };
MAT.wet.envMapIntensity=1; MAT.wet.metalness=.05;
// metal tint: painted-metal albedo is light grey -> vertex colour darkens to black/charcoal

// ---------- builder: per-material merged buckets ----------
function Bk(){ return {p:[],n:[],u:[],c:[],k:[]}; }
function mkB(){ return {conc:Bk(),wet:Bk(),metal:Bk(),soft:Bk(),neon:Bk(),atlas:Bk()}; }
const _v=new THREE.Vector3(), _m=new THREE.Matrix4(), _q=new THREE.Quaternion(), _e=new THREE.Euler(), _s=new THREE.Vector3(), _nm=new THREE.Matrix3();
let OFS=null, KPROP=null, KM=null, LANEF=false; const PROPR={}; const KIT_LANE={outer:[-5.2,3.8,-.4,7.9],island:[-2.2,.8,2.6,4.9],stair:[.2,1.2,-6.9,-.4]};
function inLane(x,z){ const o=KIT_LANE.outer,i=KIT_LANE.island,s=KIT_LANE.stair; return (x>o[0]&&x<o[1]&&z>o[2]&&z<o[3]&&!(x>i[0]&&x<i[1]&&z>i[2]&&z<i[3]))||(x>s[0]&&x<s[1]&&z>s[2]&&z<s[3]); }
function put(B,mat,geo,pos,rot,scl,col,kt,uv){ if(LANEF&&pos[1]<.4&&inLane(pos[0],pos[2])) return; if(KPROP){ const r=(PROPR[KPROP]=PROPR[KPROP]||{}); const bb=B[mat]; if(!r[mat]) r[mat]=[bb.p.length/3,bb.p.length/3]; } if(OFS) pos=[pos[0]+OFS[0],pos[1],pos[2]+OFS[1]]; const b=B[mat]; const g=geo.index?geo.toNonIndexed():geo; _e.set(rot?rot[0]:0,rot?rot[1]:0,rot?rot[2]:0); _q.setFromEuler(_e); _s.set(1,1,1); if(scl) _s.set(scl[0],scl[1],scl[2]);
  _m.compose(_v.set(pos[0],pos[1],pos[2]),_q,_s); if(KM) _m.premultiply(KM); _nm.getNormalMatrix(_m); const P=g.attributes.position,N=g.attributes.normal,UV=g.attributes.uv; const c=new THREE.Color(col==null?0xffffff:col); const tri=(mat==='conc'||mat==='wet'||mat==='metal');
  const sc=mat==='metal'?1:2.4; for(let i=0;i<P.count;i++){ const v=new THREE.Vector3().fromBufferAttribute(P,i).applyMatrix4(_m), n=new THREE.Vector3().fromBufferAttribute(N,i).applyMatrix3(_nm).normalize();
    b.p.push(v.x,v.y,v.z); b.n.push(n.x,n.y,n.z); b.c.push(c.r,c.g,c.b); b.k.push(kt?kt[0]:0,kt?kt[1]:0);
    if(uv){ const C=CELLS[uv], uu=UV.getX(i), vv=UV.getY(i); b.u.push((C.x+uu*C.w)/2048,1-(C.y+(1-vv)*C.h)/2048); }
    else if(tri){ const ax_=Math.abs(n.x),ay=Math.abs(n.y),az=Math.abs(n.z); b.u.push(ax_>ay&&ax_>az?v.z/sc:v.x/sc, ay>=ax_&&ay>=az?v.z/sc:v.y/sc); }
    else b.u.push(UV?UV.getX(i):0,UV?UV.getY(i):0); } if(KPROP) PROPR[KPROP][mat][1]=b.p.length/3; }
function flush(B,parent,tag){ for(const k in B){ const b=B[k]; if(!b.p.length) continue; const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.Float32BufferAttribute(b.p,3)); g.setAttribute('normal',new THREE.Float32BufferAttribute(b.n,3));
  g.setAttribute('uv',new THREE.Float32BufferAttribute(b.u,2)); g.setAttribute('color',new THREE.Float32BufferAttribute(b.c,3)); g.setAttribute('kt',new THREE.Float32BufferAttribute(b.k,2)); if(k==='conc'||k==='wet'||k==='metal'){ g.computeTangents&&0; }
  const m=new THREE.Mesh(g,MAT[k]); m.name='kit_'+tag+'_'+k; m.userData.noMerge=true; m.userData.mod='kit'; m.frustumCulled=false; parent.add(m); } }
const GB=new THREE.BoxGeometry(1,1,1), GP=new THREE.PlaneGeometry(1,1), GC=new THREE.CylinderGeometry(.5,.5,1,14), GC6=new THREE.CylinderGeometry(.5,.5,1,6), GS=new THREE.SphereGeometry(.5,14,10);
const CK=[1,0], AK=[0,1];
// shorthand: box(B,mat,w,h,d,x,y,z,col,kt,rot)
const bx=(B,m,w,h,d,x,y,z,col,kt,rot)=>put(B,m,GB,[x,y,z],rot,[w,h,d],col,kt);
const pl=(B,uv,w,h,x,y,z,rot,col)=>put(B,'atlas',GP,[x,y,z],rot,[w,h,1],col==null?0xffffff:col,null,uv);
const neon=(B,w,h,d,x,y,z,kt,col,rot)=>put(B,'neon',GB,[x,y,z],rot,[w,h,d],col==null?0xffffff:col,kt||CK);
const cy=(B,m,r,h,x,y,z,col,rot,kt,seg)=>put(B,m,seg===6?GC6:GC,[x,y,z],rot,[r*2,h,r*2],col,kt);
const BLK=0x16181c, CHAR=0x2a2d33, STEEL=0x3a3e45, H2=Math.PI/2;

// ---------- instanced pools ----------
function pool(geo,n,name){ const m=new THREE.InstancedMesh(geo,MAT.inst,n); m.name='kit_'+name; m.userData.noMerge=true; m.userData.mod='kit'; m.frustumCulled=false; m.count=0; m.instanceColor=new THREE.InstancedBufferAttribute(new Float32Array(n*3),3);
  geo.setAttribute('kt',new THREE.InstancedBufferAttribute(new Float32Array(n*2),2)); m._kt=geo.attributes.kt; return m; }
let CURB=null; const PROPI={}; function addI(P,pos,rot,scl,col,kt){ if(LANEF&&pos[1]<.4&&inLane(pos[0],pos[2])) return -1; if(P.name==='kit_cans'&&CURB){ put(CURB,'metal',P.geometry,pos,rot,scl,col,kt); return -1; } if(OFS) pos=[pos[0]+OFS[0],pos[1],pos[2]+OFS[1]]; const i=P.count++; _e.set(rot?rot[0]:0,rot?rot[1]:0,rot?rot[2]:0); _q.setFromEuler(_e); _m.compose(_v.set(pos[0],pos[1],pos[2]),_q,_s.set(scl[0],scl[1],scl[2])); if(KM) _m.premultiply(KM); P.setMatrixAt(i,_m); P.setColorAt(i,new THREE.Color(col)); P._kt.setXY(i,kt?kt[0]:0,kt?kt[1]:0); if(KPROP) (PROPI[KPROP]=PROPI[KPROP]||[]).push([P,i]); return i; }
// pod shell geometry: open-front capsule (cylinder + rear dome), axis +z
const podGeo=(()=>{ const B=mkB(); put(B,'soft',new THREE.CylinderGeometry(.85,.85,1.9,28,1,true),[0,0,0],[H2,0,0],[1,1,1]); put(B,'soft',new THREE.SphereGeometry(.85,28,12,0,Math.PI*2,0,Math.PI/2),[0,0,-.95],[-H2,0,0],[1,1,1]);
  const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.Float32BufferAttribute(B.soft.p,3)); g.setAttribute('normal',new THREE.Float32BufferAttribute(B.soft.n,3)); g.setAttribute('uv',new THREE.Float32BufferAttribute(B.soft.u,2)); return g; })();
MAT.inst.side=THREE.DoubleSide;

const KIT={theme:null,g:null,root:null,up:null,down:null,pools:{},drones:[],skates:null};
window.KIT=KIT; const KIT_UPY=13.0; // loft floor sits above the clubhouse block roof (8.5 m) so the old shell never pokes into the room

function buildUp(){ const R=new THREE.Group(); R.name='kit_up'; const B=mkB(); CURB=B; const P={}; KIT.pools.up=P;
  P.pod=pool(podGeo,6,'pods'); P.can=pool(new THREE.CylinderGeometry(.033,.033,.12,8),90,'cans'); P.clut=pool(new THREE.BoxGeometry(1,1,1),200,'clutter'); KIT.upCol=[]; P.drone=pool(new THREE.BoxGeometry(1,1,1),24,'drones');
  const WX=6, D=8, H=6.2, CW=3.2;
  // shell: concrete floor/walls/ceiling (inward), window wall opening on +x under the catwalk
  bx(B,'wet',12,.2,16,0,-.1,0,0x3a3e44); bx(B,'conc',12,.2,16,0,H+.1,0,0x1a1b1e);
  bx(B,'conc',.2,H,16,-WX-.1,H/2,0,0x6a6d72); bx(B,'conc',12,H,.2,0,H/2,-D-.1,0x5c5f64); bx(B,'conc',12,H,.2,0,H/2,D+.1,0x5c5f64);
  bx(B,'conc',.2,H-3.2,16,WX+.1,3.2+(H-3.2)/2,0,0x5c5f64); bx(B,'conc',.2,.4,16,WX+.1,.2,0,0x5c5f64); bx(B,'conc',.2,3.2,1.5,WX+.1,1.6,7.25,0x5c5f64); bx(B,'conc',.2,3.2,1.5,WX+.1,1.6,-7.25,0x5c5f64);
  pl(B,'city',13,2.85,WX+.05,1.78,0,[0,-H2,0]); for(let z=-6.5;z<=6.5;z+=1.625) bx(B,'metal',.1,2.85,.06,WX-.02,1.78,z,BLK); bx(B,'metal',.1,.06,13,WX-.02,1.78,0,BLK); neon(B,.04,.03,13,WX-.08,.36,0); neon(B,.04,.03,13,WX-.08,3.12,0); // window mullions
  // concrete pillars
  for(const [x,z] of [[-3.6,-6.1],[1.5,-6.1],[3.8,-4.4]]) bx(B,'conc',.5,H,.5,x,H/2,z,0x4e5156);
  // ceiling: black pipes, ducts, beams, hanging cables, cyan strip lights
  for(const x of [-4.5,-1.5,1.5,4.5]) bx(B,'metal',.25,.4,16,x,H-.25,0,BLK);
  for(const [x,y,r] of [[-3,6.55,.12],[-2.6,6.55,.08],[.2,6.4,.3],[2.6,6.6,.1],[3,6.6,.06]]) cy(B,'metal',r,16,x,y,0,0x0d0e10,[H2,0,0]);
  bx(B,'metal',1.1,.7,16,-.9,6.45,0,0x18191c); for(let z=-7;z<8;z+=2) bx(B,'metal',1.16,.76,.08,-.9,6.45,z,0x101113);
  for(let i=0;i<14;i++){ const x=-5+((i*37)%100)/10, z=-7+((i*53)%140)/10, L=.6+((i*7)%10)/8; cy(B,'metal',.012,L,x,H-L/2-.1,z,0x050505); }
  for(const [x,z,L] of [[-4,0,10],[0.9,-1,12],[2.4,0,14],[-2.5,4,6]]) neon(B,.08,.04,L,x,H-.55,z);
  // catwalk BACK-LEFT (open pods) + catwalk RIGHT (closed pods), painted metal decks, rails, under-deck neon
  bx(B,'metal',7.6,.14,2.2,-2.2,CW,-6.9,STEEL); bx(B,'metal',7.6,.25,.12,-2.2,CW-.15,-5.82,BLK); neon(B,7.2,.04,.06,-2.2,CW-.3,-5.85);
  bx(B,'metal',2.2,.14,16,4.9,CW,0,STEEL); bx(B,'metal',.12,.25,16,3.82,CW-.15,0,BLK); neon(B,.06,.04,15.4,3.85,CW-.3,0); neon(B,.06,.04,7,-2.2+0,CW-.3,-7.9);
  for(let x=-5.8;x<=1.4;x+=.6) bx(B,'metal',.04,1,.04,x,CW+.5,-5.82,BLK); bx(B,'metal',7.6,.05,.05,-2.2,CW+1,-5.82,BLK); bx(B,'metal',7.6,.04,.04,-2.2,CW+.55,-5.82,BLK);
  for(let z=-5.4;z<=7.8;z+=.6) bx(B,'metal',.04,1,.04,3.82,CW+.5,z,BLK); bx(B,'metal',.05,.05,13.4,3.82,CW+1,1.1,BLK); bx(B,'metal',.04,.04,13.4,3.82,CW+.55,1.1,BLK);
  for(const [x,z] of [[-5.6,-5.9],[3.85,6.5],[3.85,2.0]]){ bx(B,'metal',.06,CW,.06,x,CW/2,z,BLK); KIT.upCol.push([x-.08,x+.08,z-.08,z+.08]); } // catwalk support posts + footprint colliders (Nov 9 close-out: skater can't pass through)
  // stair: steel stringers + treads with cyan nosing, up to the right catwalk
  { const x0=1.2,x1=3.8, z=-6.9, n=14; for(const dz of [-.5,.5]) bx(B,'metal',Math.hypot(x1-x0,CW)+.2,.12,.06,(x0+x1)/2,CW/2,z+dz,BLK,null,[0,0,Math.atan2(CW,x1-x0)]);
    for(let i=0;i<n;i++){ const t=(i+.5)/n; bx(B,'metal',.22,.04,.95,x0+t*(x1-x0),t*CW,z,STEEL); neon(B,.03,.03,.95,x0+t*(x1-x0)-.11,t*CW+.02,z); }
    bx(B,'metal',Math.hypot(x1-x0,CW)+.2,.04,.04,(x0+x1)/2,CW/2+.9,z+.5,BLK,null,[0,0,Math.atan2(CW,x1-x0)]); neon(B,Math.hypot(x1-x0,CW),.03,.03,(x0+x1)/2,CW/2+.92,z+.5,CK,null,[0,0,Math.atan2(CW,x1-x0)]); }
  // OPEN pods (3) on the back catwalk: white shells, cyan glowing interiors, bedding, doors swung open
  KPROP='podx'; [-4.55,-2.2,.15].forEach((x,i)=>{ addI(P.pod,[x,CW+1.15,-6.95],[0,0,0],[1.25,1.25,1.0],0x8a9299); neon(B,1.6,1.6,.02,x,CW+1.15,-7.75,[.32,0],0x0c2a30); put(B,'neon',new THREE.TorusGeometry(1.0,.04,8,32),[x,CW+1.15,-5.98],null,[1,1,1],0xffffff,CK); put(B,'soft',new THREE.TorusGeometry(1.1,.11,10,36),[x,CW+1.15,-6.0],null,[1,1,1],0xc8cdd2);
    put(B,'neon',new THREE.CylinderGeometry(.82,.82,1.7,24,1,true,Math.PI*.6,Math.PI*.8),[x,CW+1.15,-6.95],[H2,0,0],[1.25,1,1.25],0x0a2a30,[.38,0]); // inner glow lining (lower half)
    bx(B,'soft',1.1,.22,1.6,x,CW+.38,-6.95,0x8fa8b0,[.15,0]); bx(B,'soft',.5,.14,.3,x-.25,CW+.55,-7.55,0x9aa4aa); put(B,'soft',GS,[x+.4,CW+.42,-6.5],null,[.7,.2,.5],0xe0f8ff);
    put(B,'soft',new THREE.CylinderGeometry(1.07,1.07,.08,28,1,false),[x+1.12,CW+1.15,-5.45],[0,.2,H2],[1,1,1.05],0x5f666c); neon(B,.03,1.9,.03,x+1.07,CW+1.15,-5.85,CK,0xffffff); });
  // CLOSED pods (3) on the right catwalk: black shells, cyan rims, POD labels
  [-5.4,-2.8,-.2].forEach((z,i)=>{ addI(P.pod,[5.0,CW+1.15,z],[0,-H2,0],[1.25,1.25,1.0],0x0c0d10); put(B,'metal',new THREE.CylinderGeometry(1.02,1.02,.06,28),[4.07,CW+1.15,z],[0,0,H2],[1,1,1],0x0e0f12);
    put(B,'neon',new THREE.TorusGeometry(1.07,.06,8,32),[4.05,CW+1.15,z],[0,H2,0],[1,1,1],0xffffff,CK); neon(B,.02,1.8,.02,4.03,CW+1.15,z,CK); }); KPROP=null;
  [-5.4,-2.8,-.2].forEach((z,i)=>{ pl(B,'pod'+(i+4),.44,.22,2.55,CW+1.75,z+.3,[0,-H2,0]); pl(B,'pod'+(i+4),.36,.18,2.55,CW+.5,z-.3,[0,-H2,0]); });
  [1,2,3].forEach(i=>pl(B,'pod'+i,.36,.18,[-4.75,-2.25,.25][i-1]-.1,CW+2.15,-4.6,null));
  KPROP='tv'; // wall TV (racing game): Nov 9 close-out moved from the back wall (half-blocked behind couch/catwalk in the upstairs hero camera) to the FRONT wall, facing the 2nd couch; wall-mounted only (front strip is skate lane: no console, no floor footprint)
  bx(B,'metal',2.65,1.55,.1,-.7,1.42,7.93,0x050505); pl(B,'tv',2.53,1.43,-.7,1.42,7.87,[0,Math.PI,0]); neon(B,2.65,.03,.03,-.7,.62,7.86);
  // plant by the TV
  cy(B,'soft',.18,.4,-4.4,.2,-7.4,0x111111); for(let k=0;k<7;k++) put(B,'soft',GB,[-4.4+Math.sin(k)*.15,.75+k*.06,-7.4+Math.cos(k)*.15],[k*.6,k,0],[.05,.6,.18],0x1e4a2a);
  KPROP='lockers'; // sticker-covered locker bank
  bx(B,'metal',1.35,2.05,.5,.35,1.03,-7.7,0x1c1e22); pl(B,'lockers',1.3,2.0,.35,1.03,-7.44,null); for(let i=0;i<4;i++) addI(P.clut,[-.1+i*.3,2.15,-7.7],null,[.14,.2,.14],[0xffd23a,0xd84040,0xffffff,0x30a0e0][i]);
  KPROP=null; // skate shelf + helmet rack under the stair
  bx(B,'metal',1.8,.05,.45,2.6,.5,-7.55,STEEL); bx(B,'metal',1.8,.05,.45,2.6,1.0,-7.55,STEEL); for(const x of [1.75,3.45]) bx(B,'metal',.04,1.1,.45,x,.55,-7.55,BLK); neon(B,1.7,.02,.02,2.6,.98,-7.33);
  for(let i=0;i<4;i++) put(B,'metal',GS,[1.95+i*.42,.63,-7.5],[0,0,0],[.32,.26,.36],i%2?0x15171a:0x2a2d32);
  // AirTrecks sign + cable to it
  bx(B,'metal',2.4,.66,.06,4.65,2.45,-7.95,0x030405); pl(B,'airt',2.35,.6,4.65,2.45,-7.91,null); for(const dy of [-.33,.33]) neon(B,2.4,.03,.03,4.65,2.45+dy,-7.9);
  // A-T skate wall display on the pillar (hooks); skates placed later from the shared GLB
  bx(B,'metal',.06,2.2,.7,3.52,1.6,-4.4,0x111214); for(let i=0;i<4;i++){ bx(B,'metal',.25,.025,.025,3.4,1.0+i*.5,-4.4,STEEL); neon(B,.02,.02,.6,3.5,.78+i*.5,-4.4); }
  pl(B,'crewp',.45,.65,3.52,2.75,-4.15,[0,-H2,0]); // little poster on pillar
  KM=new THREE.Matrix4().makeTranslation(-5.05,0,-1.9).multiply(new THREE.Matrix4().makeRotationY(-.45)).multiply(new THREE.Matrix4().makeTranslation(5.35,0,-3.3)); // arcade cabinets (left): STREET RACE 2099 + NEO-PUCK, graffiti sides
  [[-5.35,3.9,'mq1','scr1'],[-5.35,2.75,'mq2','scr2']].forEach(([x,z,mq,sc])=>{ const r=[0,H2,0];
    bx(B,'metal',.85,1.05,.9,x,.52,z,0x0b0c0e); bx(B,'metal',.6,.75,.9,x-.12,1.42,z,0x0b0c0e); bx(B,'metal',.4,.12,.9,x+.22,1.05,z,0x111216,null,[0,0,-.25]); bx(B,'metal',.25,.3,.9,x-.2,1.95,z,0x0b0c0e);
    pl(B,sc,.7,.55,x+.2,1.45,z,[0,H2,-.25]); pl(B,mq,.9,.3,x+.14,1.97,z,r); neon(B,.9,.02,.02,x+.3,1.82,z,CK,0xffffff,r); neon(B,.02,1.9,.02,x+.43,1.0,z+.46); neon(B,.02,1.9,.02,x+.43,1.0,z-.46);
    pl(B,'side',.85,1.9,x,1.0,z+.46,null); put(B,'neon',GS,[x+.33,1.13,z+.15],null,[.06,.06,.06],0xffffff,[0,1]); put(B,'neon',GS,[x+.33,1.13,z-.1],null,[.06,.06,.06],0xff3b6b);
    for(let k=0;k<2;k++) addI(P.can,[x+.3,1.18,z-.3+k*.08],null,[1,1,1],k?0x2a8a9a:0xb8bcc0);
    { const xs=[],zs=[]; for(const [dx,dz] of [[-.45,-.46],[.45,-.46],[-.45,.46],[.45,.46]]){ const v=new THREE.Vector3(x+dx,0,z+dz).applyMatrix4(KM); xs.push(v.x); zs.push(v.z); } KIT.upCol.push([Math.min(...xs),Math.max(...xs),Math.min(...zs),Math.max(...zs)]); } });
  KM=null; // left wall posters + signs
  pl(B,'racers',.95,1.66,-5.97,4.55,-4.6,[0,H2,0]); pl(B,'nosleep',.62,.93,-5.97,2.75,-3.3,[0,H2,0]); pl(B,'crewp',.6,.9,-5.97,2.4,-2.1,[0,H2,0]); pl(B,'club',.7,.7,-5.97,2.5,2.6,[0,H2,0]);
  pl(B,'banner',.75,.75,.95,2.65,-5.76,null); bx(B,'metal',.01,.6,.01,.95,3.0,-5.78,0x050505);
  put(B,'metal',new THREE.TorusGeometry(.12,.03,6,14,Math.PI),[-5.9,2.2,2.0],[0,H2,0],[1,1,1],0x111111); // headphones on wall hook
  KPROP='couch'; // black sectional couch + cyan cushions, headset, jacket, chip bag
  bx(B,'soft',4,.42,1.0,-1.6,.21,-3.0,0x26292f); bx(B,'soft',4,.6,.25,-1.6,.6,-3.42,0x26292f); bx(B,'soft',.9,.42,1.8,.85,.21,-2.6,0x26292f); bx(B,'soft',.25,.3,1.0,-3.7,.5,-3.0,0x26292f);
  for(let i=0;i<3;i++) bx(B,'soft',1.25,.12,.9,-3.0+i*1.3,.48,-2.98,i===1?0xffffff:0x30343b,i===1?[.75,0]:null);
  bx(B,'soft',.85,.12,1.0,.85,.48,-2.3,0x30343b); for(const x of [-2.4,-.6]) bx(B,'soft',.55,.45,.18,x,.8,-3.25,0xffffff,[.8,0],[-.25,0,0]);
  put(B,'soft',new THREE.TorusGeometry(.13,.03,6,14,Math.PI),[-3.0,.66,-2.8],[0,0,0],[1,1,1],0x0a0a0a); put(B,'soft',GS,[-3.13,.56,-2.8],null,[.08,.12,.12],0x0a0a0a); put(B,'soft',GS,[-2.87,.56,-2.8],null,[.08,.12,.12],0x0a0a0a);
  put(B,'soft',GB,[-1.6,.82,-3.2],[-.3,.1,.05],[.8,.55,.25],0x1a1b1f); bx(B,'soft',.25,.08,.6,-1.95,.6,-3.0,0x1a1b1f,null,[0,.4,0]); // jacket draped
  addI(P.clut,[-2.3,.57,-2.7],[0,.4,.1],[.26,.05,.34],0xc08030);
  for(let i=0;i<3;i++){ bx(B,'soft',1.2,.45,.2,-3.0+i*1.3,.78,-3.27,0x1e2126,null,[-.15,0,0]); bx(B,'soft',1.28,.02,.04,-3.0+i*1.3,.55,-2.53,0x3a3f46); }
  for(const x of [-3.65,-2.35,-1.05,.25]) bx(B,'soft',.03,.14,.92,x,.48,-2.98,0x050505);
  neon(B,4.6,.02,.02,-1.4,.02,-2.48,[.5,0],0x0a2a30); neon(B,.02,.02,1.8,1.32,.02,-2.6,[.5,0],0x0a2a30); bx(B,'soft',.85,.02,.04,.85,.55,-1.68,0x3a3f46);
  KPROP=null; // coffee table (controller, mug, remote) + under-glow
  bx(B,'metal',1.6,.08,.9,-1.4,.42,-1.0,0x3a3f47); bx(B,'metal',1.5,.012,.8,-1.4,.465,-1.0,0x23272d); for(const [w,d,ox,oz] of [[1.62,.02,0,.45],[1.62,.02,0,-.45],[.02,.92,.8,0],[.02,.92,-.8,0]]) neon(B,w,.015,d,-1.4+ox,.43,-1.0+oz,[.6,0],0x0a2a30); bx(B,'metal',1.4,.34,.7,-1.4,.2,-1.0,0x101114); neon(B,1.4,.02,.7,-1.4,.03,-1.0,CK,0x7fdfff);
  put(B,'soft',GB,[-1.75,.48,-.95],[0,.3,0],[.22,.04,.13],0x111111); put(B,'soft',GS,[-1.84,.48,-.98],null,[.09,.05,.09],0x111111); put(B,'soft',GS,[-1.66,.48,-.92],null,[.09,.05,.09],0x111111);
  cy(B,'soft',.05,.11,-1.15,.51,-1.15,0x1a1a1a); bx(B,'soft',.05,.025,.2,-.9,.475,-.9,0x050505,null,[0,-.5,0]);
  // rugs (decals)
  pl(B,'rug1',4.6,3.4,-1.4,.012,-1.1,[-H2,0,0]); pl(B,'rug2',3.0,1.9,2.4,.012,-2.6,[-H2,0,0]);
  // day-bed by the window + blanket + pillows on floor
  bx(B,'soft',2.0,.4,.9,3.1,.2,-2.7,0x141518); bx(B,'soft',.6,.2,.4,2.4,.5,-2.95,0xffffff,[.8,0]); put(B,'soft',GB,[3.0,.44,-2.6],[0,.2,.08],[1.1,.06,.8],0x8a8f96);
  LANEF=true; for(const [x,z] of [[1.6,-.6],[2.0,.3],[-3.6,-.2],[.6,1.2]]) put(B,'soft',GS,[x,.07,z],null,[.34,.12,.28],0xffffff,[.75,0]); put(B,'soft',GB,[-.3,.04,-.2],[0,.6,0],[.9,.05,.6],0x3a3f46); for(const [x,z,c] of [[-2.9,1.2,0x2a2e34],[.9,.2,0x1d6f7d],[-.2,2.4,0x111316]]) addI(P.clut,[x,.04,z],[0,x,.1],[.28,.06,.34],c);
  LANEF=false; KPROP='kitchen'; OFS=[0,1.6]; // kitchenette (under right catwalk, by windows): counter, microwave, kettle, cola fridge, snack shelf, chopsticks cup
  bx(B,'metal',.7,.9,2.6,5.6,.45,2.7,0x101114); pl(B,'lockers',2.5,.85,5.24,.45,2.7,[0,-H2,0],0x9fa6ad); bx(B,'metal',.72,.05,2.62,5.6,.92,2.7,0x2a2d32); neon(B,.02,.02,2.6,5.24,.9,2.7);
  bx(B,'metal',.4,.3,.55,5.55,1.1,1.9,0x1a1c20); pl(B,'black',.35,.2,5.34,1.1,1.85,[0,-H2,0],0x0b2a33); put(B,'metal',GC,[5.55,1.06,2.7],null,[.16,.22,.16],0xc9ced3); cy(B,'soft',.06,.13,5.5,1.0,3.5,0x101010); for(let k=0;k<6;k++) cy(B,'soft',.006,.3,5.5+(k%3)*.01-.01,1.15,3.5+((k/3)|0)*.012,0xc8a060,[.05*(k-3),0,.06*(k%3-1)]);
  put(B,'soft',GS,[5.5,1.0,3.05],null,[.28,.1,.28],0x8a6040);
  bx(B,'metal',.4,.04,2.0,5.75,2.0,2.3,STEEL); pl(B,'snacks',1.8,.38,5.56,2.2,2.3,[0,-H2,0]); neon(B,.02,.02,2.0,5.55,1.97,2.3);
  bx(B,'metal',.7,2.05,.75,5.6,1.03,4.45,0x8f969c); pl(B,'fridge',.74,2.0,5.24,1.03,4.45,[0,-H2,0]);
  KPROP='desk'; OFS=[-3.3,-3.5]; // study desk (front right): laptop, notebooks, markers, sticky notes, cans under it
  bx(B,'metal',2.4,.06,1.0,3.4,.8,5.6,0x5a4630); for(const [x,z] of [[2.3,5.2],[4.5,5.2],[2.3,6.0],[4.5,6.0]]) bx(B,'metal',.05,.8,.05,x,.4,z,BLK); bx(B,'metal',2.3,.04,.9,3.4,.25,5.6,BLK);
  bx(B,'metal',.4,.02,.3,4.1,.84,5.55,0x22252a); pl(B,'laptop',.56,.36,4.0,1.03,5.36,[-.22,0,0]); bx(B,'metal',.58,.38,.015,4.0,1.03,5.35,0x22252a,null,[-.22,0,0]); bx(B,'metal',.56,.02,.38,4.0,.84,5.6,0x22252a); cy(B,'soft',.045,.11,4.55,.89,5.45,0xe8eef0); cy(B,'neon',.047,.015,4.55,.92,5.45,0xffffff,null,CK); put(B,'metal',new THREE.TorusGeometry(.1,.022,6,16,Math.PI),[2.45,.86,5.95],[H2,0,.4],[1,1,1],0x15171a); bx(B,'metal',.08,.01,.15,3.75,.835,5.85,0x0a0a0c); pl(B,'laptop',.07,.13,3.75,.842,5.85,[-H2,0,.2]); cy(B,'metal',.035,.12,4.75,.89,5.75,0x8a9096); cy(B,'metal',.06,.02,2.25,.84,5.35,0x15171a); bx(B,'metal',.02,.4,.02,2.25,1.04,5.35,0x15171a,null,[0,0,.3]); bx(B,'neon',.14,.03,.08,2.33,1.24,5.35,0xffffff,CK);
  for(let i=0;i<5;i++) bx(B,'soft',.3,.03,.22,2.6+(i%2)*.05,.85+i*.03,5.4,[0xe8e8e8,0x30a0e0,0xe8e8e8,0x111111,0xf0f0f0][i]); pl(B,'paper',.42,.32,3.0,.835,5.75,[-H2,0,.15]); pl(B,'paper',.42,.32,3.44,.836,5.78,[-H2,0,-.1]); pl(B,'paper',.3,.3,2.6,.837,5.85,[-H2,0,.4]);
  for(let i=0;i<8;i++) addI(P.clut,[2.8+i*.13,.835,5.15+(i%3)*.1],[0,i,0],[.07,.005,.07],[0xff6aa8,0xffe04a,0x6affb0,0xff6aa8][i%4]); for(let i=0;i<5;i++) addI(P.clut,[3.6+i*.05,.84,5.9],[0,0,H2],[.012,.12,.012],[0xd84040,0x30a0e0,0x40c060,0x111111,0xffd23a][i]);
  for(let i=0;i<6;i++) addI(P.can,[2.5+i*.16,.06,5.5+(i%2)*.2],[0,0,0],[1.4,1.4,1.4],i%2?0x15171a:0xc0c4c8,i%3===0?CK:null);
  KPROP=null; OFS=null;
  LANEF=true; { let sd=11; const r2=()=>(sd=(sd*16807)%2147483647)/2147483647; const GCAN=new THREE.CylinderGeometry(.033,.033,.12,10), GPIL=new THREE.SphereGeometry(.5,12,8);
    for(let i=0;i<46;i++){ const x=-4.6+r2()*8.6, z=-3.9+r2()*6.4; if(Math.abs(x+1.4)<.85&&Math.abs(z+1)<.5) continue; const lie=r2()<.6; put(B,'atlas',GCAN,[x,lie?.033:.06,z],lie?[H2,r2()*6,0]:[0,r2()*6,0],[1,1,1],0xffffff,null,'can'); }
    for(let i=0;i<10;i++){ const x=-4+r2()*7.5, z=-3.5+r2()*5.8; put(B,'atlas',GB,[x,.03,z],[0,r2()*6,.15],[.26,.05,.34],0xffffff,null,'chips'); }
    for(const [x,y,z,s] of [[-3.2,.62,-2.75,.42],[-2.0,.62,-2.75,.42],[.7,.62,-2.0,.4],[3.5,.5,-2.9,.4],[1.6,.09,-.6,.5],[2.0,.09,.3,.5],[-3.6,.09,-.2,.5],[.6,.09,1.2,.45]]) put(B,'atlas',GPIL,[x,y,z],[.3,x,0],[s,s*.38,s*.8],0xffffff,null,'pillow'); }
  // lived-in clutter: cans, chip bags, sneakers, papers
  for(let i=0;i<30;i++){ const a=i*2.39, r=1.2+((i*7)%10)/3; addI(P.can,[-1+Math.cos(a)*r,.03,1+Math.sin(a)*r*1.2],[H2,a,0],[1,1,1],[0xb8bcc0,0x15171a,0x2a8a9a][i%3],i%4===0?CK:null); }
  for(let i=0;i<24;i++){ const x=-4.5+((i*31)%90)/10, z=-1.5+((i*17)%60)/10; addI(P.clut,[x,.004,z],[0,i,0],[.18,.004,.24],i%5?0xb8bcc0:0x5fd8ee); }
  addI(P.clut,[-.6,.04,-1.9],[0,.8,.1],[.3,.06,.36],0x2a2e34); addI(P.clut,[1.1,.04,1.6],[0,-.4,.1],[.28,.06,.34],0x1d6f7d);
  for(const [x,z,r] of [[2.0,.9,.3],[2.25,1.0,.1]]) { addI(P.clut,[x,.06,z],[0,r,0],[.12,.12,.3],0x0a0a0a); addI(P.clut,[x,.015,z],[0,r,0],[.13,.03,.31],0xffffff); }
  LANEF=false;
  // ===== pass 8 (Oliver: "add more furniture but still give room to skate around like a loft") =====
  // 3 m skate lane = rectangular ring around the front island: outer x -5.2..3.8, z -0.4..7.9; island x -2.2..0.8, z 2.6..4.9. Stair-foot corridor x 0.2..1.2, z -6.9..-0.4 kept clear.
  // furniture lives around the edges + in islands; every standing piece registers a footprint collider (up-local) in KIT.upCol; rugs/decals get none.
  { const col=(x0,x1,z0,z1)=>KIT.upCol.push([x0,x1,z0,z1]); const W1=0x7a5232, W2=0x9a7048, LEA=0x5a3e30, FAB=0x7a6a55, WARM=0xffb057, RAW=[0,0];
    const bulbs=(x0,z0,x1,z1,y,sag,n)=>{ for(let i=0;i<=n;i++){ const t=i/n, yy=y-sag*4*t*(1-t); put(B,'neon',GS,[x0+(x1-x0)*t,yy,z0+(z1-z0)*t],null,[.07,.09,.07],WARM,RAW); if(i<n) put(B,'metal',GB,[x0+(x1-x0)*(t+.5/n),yy-.01,z0+(z1-z0)*(t+.5/n)],[0,Math.atan2(x1-x0,z1-z0),0],[.01,.01,Math.hypot(x1-x0,z1-z0)/n],0x111111); } };
    // -- island: rug + (2nd Forge couch instance, see KIT_PROP_FIT.couch.inst) + floor lamp, throw pillows
    pl(B,'rug2',3.0,2.3,-.7,.013,3.75,[-H2,0,0]); col(-2.0,.6,2.65,4.85);
    cy(B,'metal',.12,.04,-2.08,.02,4.7,0x111111); cy(B,'metal',.015,1.5,-2.08,.77,4.7,0x111111); put(B,'neon',GC,[-2.08,1.6,4.7],null,[.32,.28,.32],WARM,RAW); col(-2.2,-1.96,4.58,4.82);
    // -- lounge: armchair, side table, extra floor cushions (back-left zone, off the lane)
    bx(B,'soft',.9,.42,.85,-4.3,.21,-3.2,LEA); bx(B,'soft',.9,.5,.18,-4.3,.65,-3.55,LEA); bx(B,'soft',.16,.25,.85,-4.7,.55,-3.2,LEA); bx(B,'soft',.16,.25,.85,-3.9,.55,-3.2,LEA); bx(B,'soft',.62,.1,.6,-4.3,.47,-3.15,FAB); col(-4.78,-3.82,-3.65,-2.75);
    pl(B,'rug1',1.8,1.6,-4.3,.012,-3.3,[-H2,0,.3]);
    cy(B,'metal',.3,.04,-3.35,.55,-1.75,W1); cy(B,'metal',.03,.53,-3.35,.27,-1.75,0x111111); cy(B,'metal',.18,.02,-3.35,.01,-1.75,0x111111); col(-3.65,-3.05,-2.05,-1.45);
    // -- beanbags (back-right, between daybed and lane; stair corridor stays clear)
    for(const [x,z,c] of [[2.5,-1.3,0x3a3f46],[3.4,-1.15,0x6b4a2e]]){ put(B,'soft',GS,[x,.26,z],[0,x,0],[.9,.55,.9],c); col(x-.45,x+.45,z-.45,z+.45); }
    // -- workout corner: punching bag + bench + mat + kettlebells (back-left)
    cy(B,'soft',.25,1.1,-4.8,1.35,-4.6,0x8a1f1f); cy(B,'metal',.26,.06,-4.8,1.92,-4.6,0x111111); cy(B,'metal',.01,4.2,-4.8,4.0,-4.6,0x333333); col(-5.05,-4.55,-4.85,-4.35);
    bx(B,'soft',.35,.08,1.2,-5.3,.45,-5.75,LEA); for(const z of [-6.2,-5.3]) bx(B,'metal',.3,.42,.06,-5.3,.21,z,0x111111); col(-5.5,-5.1,-6.4,-5.1);
    pl(B,'black',1.2,1.9,-4.9,.011,-5.2,[-H2,0,0],0x1a1a1a); for(const [x,z] of [[-5.75,-4.0],[-5.75,-3.75]]){ put(B,'metal',GS,[x,.1,z],null,[.18,.18,.18],0x101010); } col(-5.95,-5.55,-4.15,-3.6);
    // -- vending machine (right strip, faces the room) with warm glow
    bx(B,'metal',.8,1.95,.95,5.55,.98,-1.5,0x7a1e22); pl(B,'snacks',.85,1.2,5.14,1.15,-1.5,[0,-H2,0]); put(B,'neon',GB,[5.14,1.85,-1.5],[0,-H2,0],[.85,.12,.02],WARM,RAW); neon(B,.02,1.9,.02,5.14,.98,-1.98); col(5.15,5.95,-1.98,-1.02);
    // -- desk chair (Forge desk moves to the right strip)
    cy(B,'metal',.22,.06,4.3,.46,.5,0x15171a); cy(B,'metal',.03,.42,4.3,.22,.5,0x111111); bx(B,'soft',.06,.5,.42,4.08,.72,.5,0x15171a); col(4.06,4.54,.26,.74);
    // -- kitchen stools
    for(const z of [4.55,5.45]){ cy(B,'metal',.19,.05,4.55,.72,z,W2); cy(B,'metal',.02,.7,4.55,.36,z,0x111111); cy(B,'metal',.15,.02,4.55,.01,z,0x111111); col(4.35,4.75,z-.2,z+.2); }
    // -- crates (right-front corner) with stuff on top
    for(const [x,y,z,s] of [[5.3,.3,7.1,.6],[5.3,.9,7.1,.6],[4.6,.25,7.4,.5],[5.35,.3,6.45,.6]]){ bx(B,'metal',s,s,s,x,y,z,W1); bx(B,'metal',s+.01,.05,s+.01,x,y+s*.3,z,W2); } col(4.3,5.65,6.13,7.7);
    put(B,'atlas',GB,[5.3,1.24,7.05],[0,.4,0],[.26,.05,.34],0xffffff,null,'chips'); put(B,'soft',new THREE.TorusGeometry(.1,.022,6,16,Math.PI),[5.2,1.25,7.25],[0,.6,0],[1,1,1],0x15171a);
    // -- jacket rack (left strip): posts, rail, jackets + caps
    for(const z of [1.0,2.6]) bx(B,'metal',.04,1.7,.04,-5.65,.85,z,0x111111); bx(B,'metal',.03,.03,1.65,-5.65,1.68,1.8,STEEL); bx(B,'metal',.5,.03,1.7,-5.65,.02,1.8,0x111111);
    [0x15171a,0x2a2d33,0x5a1e1e,0x15171a,0x3b4a3a].forEach((c,i)=>{ put(B,'soft',GB,[-5.65,1.25,1.15+i*.32],[0,0,.04*(i-2)],[.42,.8,.12],c); bx(B,'soft',.08,.06,.12,-5.65,1.62,1.15+i*.32,0x050505); });
    neon(B,.02,.02,1.6,-5.4,1.7,1.8); col(-5.95,-5.35,.95,2.65);
    // -- plants
    for(const [x,z,s] of [[-5.55,-6.9,1.2],[5.5,-3.7,1.0],[-5.65,3.6,.9],[-5.65,7.65,.7]]){ cy(B,'soft',.2*s,.42*s,x,.21*s,z,0x2a2420); for(let k=0;k<9;k++) put(B,'soft',GB,[x+Math.sin(k*1.7)*.16*s,(.6+k*.07)*s,z+Math.cos(k*1.7)*.16*s],[k*.5,k*1.3,.3],[.05,.55*s,.2*s],k%2?0x2e6a34:0x1f4a26); col(x-.25*s,x+.25*s,z-.25*s,z+.25*s); }
    // -- gear + A-T skate wall on the back wall (between TV and stair): pegboard, shelf, helmets, skates (KIT.skateSpots)
    bx(B,'metal',1.6,1.9,.05,.15,1.6,-7.97,0x2a2420); for(let i=0;i<8;i++) for(let j=0;j<9;j++) bx(B,'metal',.02,.02,.01,-.55+i*.2,.75+j*.2,-7.94,0x0a0a0a);
    bx(B,'metal',1.5,.04,.3,.15,.95,-7.8,W2); for(let i=0;i<3;i++) put(B,'metal',GS,[-.35+i*.5,1.12,-7.8],null,[.3,.24,.34],[0x15171a,WARM,0x2a2d33][i]); neon(B,1.5,.02,.02,.15,2.58,-7.92); col(-.7,1.0,-8,-7.6);
    // -- wall shelves (front wall, above head height: no colliders) with books, cans, figures + warm under-glow
    for(const [x0,y] of [[-4.6,1.9],[-1.2,2.3],[1.6,1.9]]){ bx(B,'metal',2.2,.05,.3,x0+1.1,y,7.83,W2); put(B,'neon',GB,[x0+1.1,y-.04,7.75],null,[2.1,.015,.02],WARM,RAW);
      for(let k=0;k<9;k++) bx(B,'soft',.05+(k%3)*.02,.22+(k%4)*.04,.2,x0+.15+k*.11,y+.14+(k%4)*.02,7.83,[0x8a3a2a,0x2a4a6a,0xd8c8a0,0x3a3a3a,0x6a5a2a][k%5]); put(B,'atlas',new THREE.CylinderGeometry(.033,.033,.12,10),[x0+1.5,y+.09,7.8],null,[1,1,1],0xffffff,null,'can'); put(B,'soft',GS,[x0+1.9,y+.12,7.8],null,[.14,.2,.14],0xffffff,[.75,0]); }
    // -- posters + stickers on the front and back-left walls
    pl(B,'club',1.0,1.0,-3.0,3.0,7.88,[0,Math.PI,0]); pl(B,'crewp',.8,1.2,.5,3.4,7.88,[0,Math.PI,0]); pl(B,'nosleep',.7,1.0,2.8,3.3,7.88,[0,Math.PI,0]); pl(B,'banner',.8,.8,-5.2,3.1,7.88,[0,Math.PI,0]);
    pl(B,'crewp',.6,.9,-5.97,2.3,-5.6,[0,H2,0]); pl(B,'club',.6,.6,-5.97,2.6,5.9,[0,H2,0]);
    // -- string lights: front wall, over the lounge, over the island (high; skate-safe)
    bulbs(-5.6,7.7,3.6,7.7,3.6,.35,26); bulbs(-5.6,-1.0,3.6,-1.0,4.9,.5,24); bulbs(-3.0,1.6,1.6,6.6,4.7,.4,18); bulbs(-5.9,-7.0,-5.9,6.5,3.0,.3,30);
    // -- surface clutter: magazines, controllers, cans, headphones on coffee table / couch / side table / beanbags
    for(const [x,y,z,r,c] of [[-1.05,.475,-.85,.4,0xd84040],[-1.2,.48,-.82,.9,0x2a6a9a],[-3.35,.575,-1.75,.2,0xe8e0c8],[-.5,.5,3.2,1.2,0xd8c040]]) addI(P.clut,[x,y,z],[0,r,0],[.22,.01,.3],c);
    for(const [x,y,z] of [[-1.7,.5,-1.25],[-.5,.62,3.4],[2.5,.56,-1.25],[-3.3,.6,-1.85]]){ put(B,'soft',GB,[x,y,z],[0,x,0],[.16,.035,.1],0x111111); put(B,'neon',GS,[x+.03,y+.02,z],null,[.02,.01,.02],0xffffff); }
    for(const [x,y,z] of [[-1.0,.53,-1.25],[-3.25,.63,-1.65],[-3.45,.63,-1.7],[3.35,.58,-1.0]]) put(B,'atlas',new THREE.CylinderGeometry(.033,.033,.12,10),[x,y,z],null,[1,1,1],0xffffff,null,'can');
    put(B,'soft',new THREE.TorusGeometry(.12,.026,6,16,Math.PI),[3.3,.56,-1.25],[H2,0,.5],[1,1,1],0x15171a); put(B,'atlas',GB,[-3.3,.6,-1.62],[0,1,0],[.22,.05,.3],0xffffff,null,'chips');
  }
  for(const c of [[-2.96,.16,-4.17,-1.53],[-2.2,-.6,-1.45,-.55],[2.1,4.1,-3.15,-2.25],[5.0,6.0,3.9,6.1],[4.6,5.3,-.28,1.28],[-6.0,-5.3,4.51,7.29],[-3.85,-3.35,-6.35,-5.85],[1.25,1.75,-6.35,-5.85],[3.55,4.05,-4.65,-4.15]]) KIT.upCol.push(c); // couch, coffee table, daybed, kitchen, desk, lockers, pillars
  // drones: top centre + small one by the window (instanced pool, bob in tick)
  const drone=(x,y,z,s)=>{ const k=KIT.drones.length; const ids=[]; ids.push(addI(P.drone,[x,y,z],null,[.35*s,.1*s,.35*s],0x111214)); for(const [dx,dz] of [[-1,-1],[1,-1],[-1,1],[1,1]]){ ids.push(addI(P.drone,[x+dx*.32*s,y+.02,z+dz*.32*s],null,[.22*s,.015*s,.22*s],0x2a2d32)); }
    ids.push(addI(P.drone,[x,y-.06*s,z+.12*s],null,[.08*s,.05*s,.05*s],0xffffff,CK)); KIT.drones.push({ids,y,s,ph:k*1.7}); };
  drone(-.6,4.6,-4.2,2.2); drone(3.0,2.7,-.8,1.3); cy(B,'metal',.008,1.2,-.6,5.6,-4.2,0x050505);
  P.pod.instanceMatrix.needsUpdate=true; delete P.can; CURB=null; flush(B,R,'up'); R.userData.propR=Object.assign({},PROPR); for(const k in P) R.add(P[k]);
  // lights (room-space -> kit uniforms): pods glow, TV, window, stair, kitchen, couch
  R.userData.lights=[[-2.2,4.4,-5.2,.8],[-2.5,1.8,-6.4,.9],[3.6,4.4,-2.8,1.0],[-1.0,3.6,-.8,-1.1],[-1.4,.6,-1.2,.8],[5.2,1.8,-1.0,.9],[-4.4,2.0,-1.6,.8],[-.7,3.4,4.2,-1.2]];
  return R; }

function buildDown(){ const R=new THREE.Group(); R.name='kit_down'; const B=mkB(); CURB=B; const P={}; KIT.pools.down=P;
  P.box=pool(new THREE.BoxGeometry(1,1,1),320,'dbox'); P.cyl=pool(new THREE.CylinderGeometry(.5,.5,1,12),220,'dcyl');
  const X0=-5.5,X1=5.5,Z0=-9.5,Z1=-.3,H=5.2,MZ=2.6;
  bx(B,'wet',11,.1,9.2,0,.0,-4.9,0x5a5f66); // wet reflective floor
  bx(B,'conc',.1,H,9.2,X0-.05,H/2,-4.9,0x6a6d72); bx(B,'conc',.1,H,9.2,X1+.05,H/2,-4.9,0x60636a); bx(B,'conc',11,H,.1,0,H/2,Z0+.05,0x5c5f64); bx(B,'conc',11,.1,9.2,0,H-.05,-4.9,0x1b1c1f);
  for(const z of [-2.5,-5,-7.5]) bx(B,'metal',11,.35,.2,0,H-.3,z,BLK); for(const x of [-2.5,1.5]) bx(B,'metal',.25,.3,9,x,H-.55,-4.9,BLK);
  // skylights + neon strips (crew + accent), fake wet reflections of strips
  for(const z of [-2.5,-5,-7.5]){ pl(B,'sky',1.4,1.1,-.5,H-.11,z+1.2,[H2,0,0]); }
  for(const [x,z,L,k] of [[-3.6,-5,7,CK],[3.0,-5,7,AK],[.5,-3,4,[.4,0]]]){ neon(B,.08,.04,L,x,H-.75,z,k); neon(B,.18,.002,L*.9,x,.022,z,k,0x404040); }
  // roll-up door (left wall) to bay 02 gear storage, with night street + PALMA CITY card
  pl(B,'street',2.6,2.4,X0+.01,1.2,-2.4,[0,H2,0]); bx(B,'metal',.15,.25,2.9,X0+.1,2.55,-2.4,0x2a2d33); for(let i=0;i<7;i++) bx(B,'metal',.05,.1,2.7,X0+.08,2.0+i*.06,-2.4,0x3c4048);
  for(const dz of [-1.4,1.4]) bx(B,'metal',.15,2.7,.12,X0+.1,1.35,-2.4+dz,0x2a2d33); pl(B,'bay2',1.6,.8,X0+.03,3.1,-2.4,[0,H2,0]); pl(B,'decal',.7,.7,X0+.12,2.25,-2.4,[0,H2,0]);
  // big crew sign (KIT_THEME) over the door
  bx(B,'metal',.08,1.25,3.3,X0+.06,4.25,-4.6,0x050505); pl(B,'signbig',3.2,1.2,X0+.11,4.25,-4.6,[0,H2,0]);
  // mezzanine catwalk (back) with OPS / LOGISTICS glass office (left) + crates, steel stair, second flight up to the pod loft hatch
  bx(B,'metal',11,.14,2.3,0,MZ,-8.35,STEEL); bx(B,'metal',11,.25,.12,0,MZ-.15,-7.2,BLK); neon(B,10.8,.04,.06,0,MZ-.3,-7.22,AK); neon(B,10.8,.03,.03,0,MZ+1.0,-7.2,CK);
  for(let x=-5.4;x<=5.4;x+=.55) bx(B,'metal',.04,1,.04,x,MZ+.5,-7.2,BLK);
  for(const x of [-5.3,-1.5,2.2,5.3]) bx(B,'metal',.12,MZ,.12,x,MZ/2,-7.25,BLK);
  // office glass box
  bx(B,'metal',3.2,.08,2.1,-3.8,MZ+1.9,-8.4,BLK); for(const x of [-5.35,-2.25]) bx(B,'metal',.06,1.9,2.1,x,MZ+.95,-8.4,BLK); bx(B,'metal',3.2,1.9,.04,-3.8,MZ+.95,-7.4,0x0e2a33);
  neon(B,3.1,.02,1.9,-3.8,MZ+1.84,-8.4,CK,0x6fdfff); bx(B,'metal',1.2,.05,.5,-4.4,MZ+.75,-9.1,STEEL); pl(B,'map',.8,.45,-4.3,MZ+1.3,-9.38,null); pl(B,'ops',1.5,.38,-3.8,MZ+2.15,-7.36,null);
  for(let i=0;i<9;i++) addI(P.box,[.2+(i%5)*.95,MZ+.32+((i/5)|0)*.6,-8.7-(i%2)*.4],[0,(i%3)*.2,0],[.75,.6,.6],i%3?0xb88c50:0x16181b,i%3===0?[0,.05]:null);
  { const x=-1.0, z0=-4.4, z1=-7.2, n=12; for(const dx of [-.45,.45]) bx(B,'metal',.06,.12,Math.hypot(z1-z0,MZ)+.2,x+dx,MZ/2,(z0+z1)/2,BLK,null,[Math.atan2(MZ,-(z1-z0))*-1+0,0,0].map((v,i)=>i===0?Math.atan2(MZ,z0-z1):0));
    for(let i=0;i<n;i++){ const t=(i+.5)/n; bx(B,'metal',.9,.04,.22,x,t*MZ,z0+t*(z1-z0),STEEL); neon(B,.9,.02,.02,x,t*MZ+.02,z0+t*(z1-z0)+.11); } }
  { const x=4.6, z0=-7.6, z1=-9.4; for(let i=0;i<8;i++){ const t=(i+.5)/8; bx(B,'metal',.8,.04,.2,x,MZ+t*(H-MZ),z0+t*(z1-z0)+0,STEEL); neon(B,.8,.02,.02,x,MZ+t*(H-MZ)+.02,z0+t*(z1-z0)); } neon(B,1,.03,1.2,x,H-.07,-9.0,CK); }
  // shelving wall (under the mezzanine): helmets, wheels, A-T core batteries, frame kits; atlas box labels
  for(let s=0;s<4;s++) bx(B,'metal',6.2,.04,.6,2.1,.35+s*.55,-9.15,STEEL); for(let x=-1;x<=5.2;x+=1.55) bx(B,'metal',.05,2.3,.6,x,1.15,-9.15,BLK); neon(B,6.1,.02,.02,2.1,2.32,-8.86,CK);
  for(let s=0;s<4;s++) for(let k=0;k<20;k++){ const x=-.8+k*.31, y=.37+s*.55, z=-9.1; const t=(s+k)%4;
    if(t===0) addI(P.cyl,[x,y+.14,z],[0,0,H2],[.24,.07,.24],0x111111,[.6,0]); else if(t===1) addI(P.box,[x,y+.12,z],null,[.22,.24,.26],0x15171a,[0,.25]);
    else if(t===2) addI(P.cyl,[x,y+.16,z],null,[.3,.3,.3],0x0f1013); else addI(P.box,[x,y+.13,z],null,[.45,.26,.4],0xb88c50); }
  for(let i=0;i<4;i++){ const C=CELLS.labels; put(B,'atlas',GP,[-.4+i*1.6,2.62+.3,-8.0],null,[.55,.4,1],0xffffff,null,'labels'); }
  // relabel those 4 crate faces with individual label tiles
  { const b=B.atlas; const n=6*4*0; }
  for(let s=0;s<3;s++){ bx(B,'metal',7.4,.04,.5,1.6,2.75+.5+s*.6,-9.25,STEEL); for(let k=0;k<16;k++) addI(P.box,[-1.8+k*.45,2.75+.5+s*.6+.17,-9.25],null,[.38,.3,.36],(k+s)%3?0xb88c50:0x16181b,(k+s)%5?null:[0,.12]); }
  for(let s=0;s<4;s++) pl(B,'labels',6.0,.12,2.1,.3+s*.55,-8.84,null); // box-label strips on shelf fronts
  // A-T skates on lit display plinths (2 rows x 3), trims glow crew colour
  KIT.plinths=[]; for(const z of [-3.5,-4.7,-5.9]) for(const x of [1.95,2.85,3.75,4.65]){ bx(B,'metal',.62,.42,.62,x,.21,z,0x0c0d10); for(const [w,d,ox,oz] of [[.64,.03,0,.3],[.64,.03,0,-.3],[.03,.64,.3,0],[.03,.64,-.3,0]]) neon(B,w,.03,d,x+ox,.43,z+oz,CK); bx(B,'metal',.58,.02,.58,x,.425,z,0x1a1c20); neon(B,.66,.02,.66,x,.03,z,AK); KIT.plinths.push([x,.44,z]); }
  // tuning workbench + tools (left wall)
  bx(B,'metal',.8,.08,2.4,-5.05,.92,-5.6,0x3a3020); bx(B,'metal',.75,.8,2.3,-5.07,.45,-5.6,0x16181b); bx(B,'metal',.05,1.2,2.4,-5.45,1.6,-5.6,0x24262b); neon(B,.02,.02,2.3,-5.4,2.22,-5.6,CK);
  for(let i=0;i<9;i++) bx(B,'metal',.02,.05+(i%3)*.1,.04,-5.41,1.5+(i%3)*.2,-6.6+i*.25,0x8a8f99); addI(P.box,[-4.95,1.05,-5.0],[0,.3,0],[.3,.18,.45],0xd02020); addI(P.cyl,[-5.0,1.0,-6.1],[0,0,H2],[.24,.06,.24],0x111111,[.6,0]); addI(P.box,[-4.9,1.0,-6.4],[0,0,0],[.25,.12,.18],0x15171a,[0,.3]);
  // hanging crew jacket rack (atlas jackets with logo)
  bx(B,'metal',2.2,.04,.04,-.6,2.15,-8.85,STEEL); for(let i=0;i<5;i++) pl(B,'jacket',.5,.7,-1.5+i*.45,1.78,-8.8+(i%2)*.03,[0,(i%2)*.15,0]);
  // wall city-map screen (right wall)
  bx(B,'metal',.08,1.4,2.5,X1-.04,2.4,-4.6,0x050505); pl(B,'map',2.35,1.25,X1-.09,2.4,-4.6,[0,-H2,0]);
  // forklift (near bay entrance) + battery-pack crates
  bx(B,'metal',1.0,.7,1.4,-4.0,.45,-1.5,0x1b1d22); bx(B,'metal',.9,.06,1.2,-4.0,2.0,-1.6,0x111214); for(const [dx,dz] of [[-.45,-.6],[.45,-.6]]) bx(B,'metal',.05,2.0,.05,-4.0+dx,1.0,-1.5+dz,0x111214);
  bx(B,'metal',.12,2.2,.5,-4.0,1.1,-.75,0x2a2d33); for(const dx of [-.25,.25]) bx(B,'metal',.1,.04,.9,-4.0+dx,.1,-.35,0x2a2d33); neon(B,1.0,.03,.03,-4.0,.82,-2.2,AK);
  for(const [dx,dz] of [[-.5,-.4],[.5,-.4],[-.5,.4],[.5,.4]]) addI(P.cyl,[-4.0+dx,.16,-1.5+dz],[0,0,H2],[.32,.15,.32],0x0a0a0a);
  for(let i=0;i<6;i++) addI(P.box,[-2.6+(i%3)*.62,.22+((i/3)|0)*.44,-.9],null,[.58,.42,.5],0x16181b,i%2?null:[0,.06]);
  pl(B,'labels',.55,.27,-2.6,.3,-.64,null,0xffffff);
  // crew floor decal
  pl(B,'rugfloor',1.6,1.6,-2.6,.012,-6.0,[-H2,0,0]);
  delete P.can; for(const k in P){ P[k].instanceMatrix.needsUpdate=true; } CURB=null; flush(B,R,'down'); for(const k in P) R.add(P[k]);
  R.userData.lights=[[0,4.2,-4,1.0],[3.2,1.4,-5.1,.9],[-4.6,2.2,-5.6,.6],[-4.3,1.8,-2.4,.6],[2.1,2.0,-7.8,.8],[-3.8,3.6,-8.0,.6],[4.6,2.4,-4.6,.6],[-1,1.5,-6,.5]];
  return R; }

// ---------- skates (shared black-shell Meshy A-T, cyan/crew tint, instanced) ----------
KIT.skateSpots={ up:[[-5.5,.32,-.45,0,-0.35],[-5.55,.32,-.95,0,-0.3],[-5.6,.32,3.2,0,-.35],[1.7,.32,-2.2,1.2,0],[-.35,1.3,-7.8,0,0],[.15,1.3,-7.8,0,0],[.65,1.3,-7.8,0,0],[-.1,1.9,-7.8,0,0],[.4,1.9,-7.8,0,0],[3.43,1.05,-4.4,H2,0],[3.43,1.55,-4.4,H2,0],[3.43,2.05,-4.4,H2,0],[2.2,.72,-7.5,0,0]], down:null };
async function kitSkates(){ try{ const url=(typeof SR_SKATE!=='undefined'&&SR_SKATE.url)?SR_SKATE.url():(typeof CHAR_BASE!=='undefined'?CHAR_BASE:'skyrydahs-characters/')+'wardrobe/skates/at-skate-meshy.glb'; // same base + file as the rider skates (SR_SKATE)
  const L=new THREE.GLTFLoader(); { const dl=kitDraco(); if(dl) L.setDRACOLoader(dl); } if(window.MeshoptDecoder&&L.setMeshoptDecoder) L.setMeshoptDecoder(window.MeshoptDecoder); let g=null; try{ g=await new Promise((res,rej)=>L.load(url,res,undefined,rej)); }catch(e){ g=null; }
  let src=null; if(!g) g={scene:kitStandInSkate()}; g.scene.traverse(o=>{ if(o.isMesh&&(!src||/LOD1/.test(o.name))) src=o; }); if(!src) throw new Error('no skate mesh');
  KIT.skateSrc=g.parser?'glb':'standin'; const geo=src.geometry.clone(); geo.computeBoundingBox(); const bb=geo.boundingBox, s=.3/(bb.max.y-bb.min.y||1); geo.translate(-(bb.min.x+bb.max.x)/2,-bb.min.y,-(bb.min.z+bb.max.z)/2); geo.scale(s,s,s);
  const m0=src.material; const mat=kitify(new THREE.MeshStandardMaterial({map:m0.map||null,normalMap:m0.normalMap||null,color:0x2a2d33,roughness:.45,metalness:.35,emissive:0x00e5ff,emissiveIntensity:.0,emissiveMap:null}),false);
  mat.emissiveIntensity=1; mat.emissive.set(0x00e5ff).multiplyScalar(.12);
  geo.setAttribute('kt',new THREE.InstancedBufferAttribute(new Float32Array(32*2),2));
  const mk=(n,name)=>{ const m=new THREE.InstancedMesh(geo,mat,n); m.name='kit_'+name; m.userData.noMerge=true; m.userData.mod='kit'; m.frustumCulled=false; m.count=n; return m; };
  const up=mk(KIT.skateSpots.up.length,'skates_up'), dn=mk(KIT.plinths.length,'skates_down');
  const place=(M,spots)=>{ let i=0; for(const [x,y,z,ry,lean] of spots) for(const side of [0]){ _e.set(0,ry,lean||0); _q.setFromEuler(_e); const o=new THREE.Vector3(0,0,0); _m.compose(_v.set(x+o.x,y,z+o.z),_q,_s.set(1,1,1)); M.setMatrixAt(i++,_m); } M.instanceMatrix.needsUpdate=true; };
  place(up,KIT.skateSpots.up); { let i=0; for(const p of KIT.plinths){ _e.set(0,-.6,0); _q.setFromEuler(_e); _m.compose(_v.set(p[0],p[1],p[2]),_q,_s.set(1.7,1.7,1.7)); dn.setMatrixAt(i++,_m); } dn.instanceMatrix.needsUpdate=true; } KIT.up.add(up); KIT.down.add(dn); KIT.skates={up,dn,mat};
  }catch(e){ console.warn('kit skates failed',e); } }

// procedural stand-in pair (black shell boot, frame, 4 wheels each) used only if the shared skate GLB is unavailable
function kitStandInSkate(){ const B=mkB(); for(const sx of [-.11,.11]){ bx(B,'soft',.11,.16,.26,sx,.17,.0,0x15171a); bx(B,'soft',.12,.14,.14,sx,.3,-.04,0x15171a); bx(B,'soft',.03,.05,.3,sx,.06,0,0x2a2d33);
  for(let k=0;k<4;k++) cy(B,'soft',.035,.028,sx,.035,-.11+k*.075,0x00e5ff,[0,0,H2]); }
  const b=B.soft, g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.Float32BufferAttribute(b.p,3)); g.setAttribute('normal',new THREE.Float32BufferAttribute(b.n,3)); g.setAttribute('uv',new THREE.Float32BufferAttribute(b.u,2));
  const sc=new THREE.Group(); const m=new THREE.Mesh(g,new THREE.MeshStandardMaterial({color:0x2a2d33})); m.name='ATSkate_LOD1'; sc.add(m); return sc; }
// Nov 9: the loader-fail HUD's wasm probe can set window.SR_DRACO to a plain {failed,mime} object before any real loader exists;
// passing that to setDRACOLoader threw 'this.dracoLoader.preload is not a function' and every kit GLB fell back to procedural. Use SR_DRACO only if it is a real DRACOLoader.
function kitDraco(){ const d=window.SR_DRACO; if(d&&typeof d.preload==='function') return d; if(!THREE.DRACOLoader) return null; if(!KIT.draco){ KIT.draco=new THREE.DRACOLoader(); KIT.draco.setDecoderPath('libs/draco/'); if(!d) window.SR_DRACO=KIT.draco; } return KIT.draco; }
// ---------- Meshy prop swap: props/kit/manifest.json lists available <name>.glb; missing -> procedural stays (no 404s) ----------
const KIT_PROP_FIT={ tv:{c:[-.7,.7,7.95],k:1.6,ry:Math.PI}, /* Nov 9: front wall, out of the upstairs hero camera, under the middle shelf (y 2.3) */ lockers:{c:[-6.0,0,5.9],k:1,ry:H2}, couch:{c:[-1.4,0,-2.85],k:1.2,ry:0,inst:[[-1.4,-2.85,0,1.2],[-.7,3.75,Math.PI,1.0]]},
  kitchen:{c:[5.5,0,5.0],k:1,ry:-H2}, desk:{c:[4.95,0,.5],k:1.3,ry:H2} }; // lockers: 2-row unit pushed into the back wall so only the front row shows
async function kitProp(name,fallbackFn){ try{ const m=KIT.manifest||(KIT.manifest=await fetch('props/kit/manifest.json').then(r=>r.ok?r.json():{props:[]}).catch(()=>({props:[]})));
  if(!(m.props||[]).includes(name)) return fallbackFn&&fallbackFn();
  const L=new THREE.GLTFLoader(); { const dl=kitDraco(); if(dl) L.setDRACOLoader(dl); } if(window.MeshoptDecoder&&L.setMeshoptDecoder) L.setMeshoptDecoder(window.MeshoptDecoder); const g=await new Promise((res,rej)=>L.load('props/kit/'+name+'.glb',res,undefined,rej)); return g.scene; }catch(e){ return fallbackFn&&fallbackFn(); } }
function kitFit(obj,F){ if(F.k){ const h=new THREE.Group(); h.add(obj); h.scale.setScalar(F.k); h.rotation.y=F.ry; h.position.set(F.c[0],F.c[1],F.c[2]); h.traverse(o=>{ o.layers.enable(KIT_LAYER); if(o.isMesh){ o.userData.noMerge=true; o.userData.mod='kit'; o.frustumCulled=false; } }); h.name='kit_prop'; return h; } const box=new THREE.Box3().setFromObject(obj), sz=box.getSize(new THREE.Vector3()), ctr=box.getCenter(new THREE.Vector3()); const w=Math.abs(F.ry)>.1?[F.s[2],F.s[1],F.s[0]]:F.s;
  const k=Math.min(w[0]/(sz.x||1),w[1]/(sz.y||1),w[2]/(sz.z||1)); const h=new THREE.Group(); obj.position.sub(ctr); h.add(obj); h.scale.setScalar(k); h.rotation.y=F.ry; h.position.set(F.c[0],F.c[1],F.c[2]);
  h.traverse(o=>{ if(o.isMesh){ o.userData.noMerge=true; o.frustumCulled=false; } }); h.name='kit_prop'; return h; }
async function kitSwapProps(){ const R=KIT.up; await kitProp('_',null); const names=((KIT.manifest&&KIT.manifest.props)||[]).map(p=>typeof p==='string'?p:p.name); for(const name of names){ if(!KIT_PROP_FIT[name]) continue; const sc=await kitProp(name,null); if(!sc) continue; kitPropMat(name,sc); const FI=KIT_PROP_FIT[name]; if(FI.inst){ const {geo,mat}=kitGlbGeo(sc); const M=new THREE.InstancedMesh(geo,mat,FI.inst.length); M.name='kit_prop_'+name; M.userData.noMerge=true; M.userData.mod='kit'; M.frustumCulled=false; M.layers.enable(KIT_LAYER); FI.inst.forEach(([x,z,r,k],i)=>{ _e.set(0,r,0); _q.setFromEuler(_e); _m.compose(_v.set(x,0,z),_q,_s.set(k,k,k)); M.setMatrixAt(i,_m); }); R.add(M); } else R.add(kitFit(sc,FI)); for(const [P,i] of (PROPI[name]||[])){ _m.makeScale(0,0,0); P.setMatrixAt(i,_m); P.instanceMatrix.needsUpdate=true; }
    const pr=R.userData.propR[name]||{}; for(const k in pr){ const mesh=R.children.find(o=>o.name==='kit_up_'+k); if(!mesh) continue; const P=mesh.geometry.attributes.position; for(let i=pr[k][0];i<pr[k][1];i++) P.setXYZ(i,0,-50,0); P.needsUpdate=true; } }
  await kitPodGlb(); await kitDroneGlb(); }
// Rydah Forge pod.glb / drone.glb: Y-up metres, origin floor centre, one material, white emissive -> crew colour (capped so pods don't bloom)
const KIT_PS=1.45, KIT_PODS=[[-4.75,-6.25,0,1],[-2.25,-6.25,0,1],[.25,-6.25,0,1],[4.25,-5.4,-Math.PI/2+.55,0],[4.25,-2.8,-Math.PI/2+.55,0],[4.25,-.2,-Math.PI/2+.55,0]]; // up-local x,z,ry,open
window.KIT_POD_FOOT=KIT_PODS.map(([x,z,r])=>r?{minX:x-1.11*KIT_PS,maxX:x+1.27*KIT_PS,minZ:z-.65*KIT_PS,maxZ:z+.65*KIT_PS}:{minX:x-.65*KIT_PS,maxX:x+.94*KIT_PS,minZ:z-1.27*KIT_PS,maxZ:z+1.11*KIT_PS}); // door-open bounds X -0.65..0.94
function kitGlbGeo(sc,filter){ const gs=[]; sc.updateMatrixWorld(true); let mat=null; sc.traverse(o=>{ if(o.isMesh&&(!filter||filter(o))){ const g=o.geometry.clone(); g.applyMatrix4(o.matrixWorld); for(const k of Object.keys(g.attributes)) if(!/^(position|normal|uv)$/.test(k)) g.deleteAttribute(k); gs.push(g); mat=mat||o.material; } });
  return {geo:gs.length===1?gs[0]:(gs.length?THREE.BufferGeometryUtils.mergeBufferGeometries(gs):null),mat}; }
// per-prop material hookups (each GLB loads once; the kit is reparented per garage, so materials are shared by all garages)
function kitPropMat(name,sc){ sc.traverse(o=>{ if(!o.isMesh) return; const m=o.material; if(kitEnv()){ m.envMap=KIT.env; m.envMapIntensity=.6; }
  const tint=name==='couch'?' { float l=dot(diffuseColor.rgb,vec3(.333)); diffuseColor.rgb=mix(diffuseColor.rgb,uC1*(.35+.65*l),smoothstep(.5,.75,l)); }':''; // couch: near-white cushions -> crew colour
  m.onBeforeCompile=sh=>{ sh.uniforms.uC1=U.uC1; sh.fragmentShader='uniform vec3 uC1;\n'+sh.fragmentShader.replace('#include <map_fragment>','#include <map_fragment>\n'+tint).replace('#include <emissivemap_fragment>','#include <emissivemap_fragment>\n totalEmissiveRadiance+=diffuseColor.rgb*vec3(0.30,0.30,0.29);'); }; m.customProgramCacheKey=()=>'kitprop_'+name; // same warm interior fill as the kit
  if(name==='desk'){ KIT.deskMat=m; m.emissive.set(KIT.theme?KIT.theme.c1:'#19e6ff').lerp(new THREE.Color(1,1,1),.35); m.emissiveIntensity=2.2; } // only the laptop screen is emissive
  if(name==='tv'&&(o.name==='screen'||m.name==='screen')){ const c=document.createElement('canvas'); c.width=512; c.height=288; KIT.tvCanvas=c; kitTvTex(); const t=new THREE.CanvasTexture(c); t.encoding=THREE.sRGBEncoding; KIT.tvTex=t; m.map=t; m.emissiveMap=t; m.color.set(0xffffff); m.emissive.set(0xffffff); m.emissiveIntensity=.6; m.toneMapped=true; }
  m.needsUpdate=true; }); }
function kitTvTex(){ const c=KIT.tvCanvas; if(!c||!CELLS.tv) return; const r=CELLS.tv, g2=c.getContext("2d"); g2.setTransform(1,0,0,-1,0,288); g2.drawImage(AT,r.x,r.y,r.w,r.h,0,0,512,288); /* Nov 9: was (-1,0,0,-1) -> HUD text on the GLB screen read mirrored; v-flip only */ if(KIT.tvTex) KIT.tvTex.needsUpdate=true; }
// small PMREM of a garage-like interior, applied ONLY to kit gloss materials (pods, drones, skates) — never scene.environment
function kitEnv(){ if(KIT.env!==undefined) return KIT.env; try{ const r=window.renderer||(typeof renderer!=='undefined'?renderer:null); if(!r||!THREE.PMREMGenerator){ return KIT.env=null; }
  const sc=new THREE.Scene(), bm=c=>new THREE.MeshBasicMaterial({color:c,side:THREE.BackSide}); const room=new THREE.Mesh(new THREE.BoxGeometry(12,6,16),bm(0x15181c)); sc.add(room);
  const strip=(w,h,d,x,y,z,c)=>{ const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),new THREE.MeshBasicMaterial({color:c})); m.position.set(x,y,z); sc.add(m); };
  for(const z of [-5,-1.5,2,5.5]) strip(9,.08,.15,0,2.9,z,0xd8f4ff); strip(.1,.1,14,-5.9,1,0,0x19c8e0); strip(.1,.1,14,5.9,1,0,0x19c8e0); strip(10,3,.1,0,1.5,-7.9,0x1a3a48); strip(3,1.6,.1,-2,1.6,7.9,0x6a7a88);
  const g=new THREE.PMREMGenerator(r); KIT.env=g.fromScene(sc,.02).texture; g.dispose(); sc.traverse(o=>{ if(o.geometry) o.geometry.dispose(); }); }catch(e){ KIT.env=null; } return KIT.env; }
function kitGlbMat(m){ m=m.clone(); const env=kitEnv(); if(env){ m.envMap=env; m.envMapIntensity=.9; m.needsUpdate=true; } m.emissive.set(KIT.theme?KIT.theme.c1:'#19e6ff'); m.emissiveIntensity=.45; (KIT.glbMats=KIT.glbMats||[]).push(m); return m; }
function kitAdopt(M,old,name){ M.name=name; M.userData=Object.assign({},old.userData); M.layers.mask=old.layers.mask; M.frustumCulled=false; return M; }
async function kitPodGlb(){ const sc=await kitProp('pod',null); if(!sc) return; const R=KIT.up, old=KIT.pools.up.pod; const {geo,mat}=kitGlbGeo(sc); if(!geo) return;
  const pm=kitGlbMat(mat); pm.envMapIntensity=1.1; KIT.podMat=pm;
  // lavender cast = world HemisphereLight 0x5a4a9a on a white shell; add a neutral-warm interior fill on the pod material only
  pm.onBeforeCompile=sh=>{ sh.fragmentShader=sh.fragmentShader.replace('#include <emissivemap_fragment>','#include <emissivemap_fragment>\n totalEmissiveRadiance+=diffuseColor.rgb*vec3(0.30,0.31,0.30);'); }; pm.customProgramCacheKey=()=>'kitpod'; pm.color.setRGB(1.0,1.0,.86); // shell albedo/roughness come from Forge's GLB (no kit override); one material shared by open + closed pods, all garages
  const names=((KIT.manifest&&KIT.manifest.props)||[]).map(p=>typeof p==='string'?p:p.name); let gc=null; if(names.includes('pod_closed')){ const sc2=await kitProp('pod_closed',null); if(sc2) gc=kitGlbGeo(sc2).geo; }
  const open=KIT_PODS.filter(p=>p[3]||!gc), shut=gc?KIT_PODS.filter(p=>!p[3]):[];
  const place=(M,list)=>list.forEach(([x,z,r,op],i)=>{ const tint=op?0xffffff:0x4a4e55; /* reference: closed pods charcoal, open pods white */ _e.set(0,r,0); _q.setFromEuler(_e); _m.compose(_v.set(x,3.2,z),_q,_s.set(KIT_PS,KIT_PS,KIT_PS)); M.setMatrixAt(i,_m); M.setColorAt(i,new THREE.Color(tint)); });
  const M=kitAdopt(new THREE.InstancedMesh(geo,pm,open.length),old,'kit_pods'); place(M,open); R.remove(old); R.add(M); KIT.pools.up.pod=M;
  if(gc){ const MC=kitAdopt(new THREE.InstancedMesh(gc,pm,shut.length),old,'kit_pods_closed'); place(MC,shut); R.add(MC); KIT.pools.up.podClosed=MC; }
  const pr=R.userData.propR.podx||{}; for(const k in pr){ const mesh=R.children.find(o=>o.name==='kit_up_'+k); if(!mesh) continue; const P=mesh.geometry.attributes.position; for(let i=pr[k][0];i<pr[k][1];i++) P.setXYZ(i,0,-50,0); P.needsUpdate=true; } }
async function kitDroneGlb(){ const sc=await kitProp('drone',null); if(!sc) return; const R=KIT.up, old=KIT.pools.up.drone; const isR=o=>/^rotor_/.test(o.name);
  const body=kitGlbGeo(sc,o=>!isR(o)); const rg=sc.getObjectByName('rotor_FL').geometry.clone(); for(const k of Object.keys(rg.attributes)) if(!/^(position|normal|uv)$/.test(k)) rg.deleteAttribute(k);
  const hubs=['rotor_FL','rotor_FR','rotor_BL','rotor_BR'].map(n=>sc.getObjectByName(n).position.clone()); const mat=kitGlbMat(body.mat); const N=KIT.drones.length;
  const MB=kitAdopt(new THREE.InstancedMesh(body.geo,mat,N),old,'kit_drones'), MR=kitAdopt(new THREE.InstancedMesh(rg,mat,N*4),old,'kit_rotors');
  KIT.drones.forEach(d=>{ old.getMatrixAt(d.ids[0],_m); _m.decompose(_v,_q,_s); d.k=d.s*3.0; d.pos=_v.clone(); d.pos.y-=.14*d.k; });
  R.remove(old); R.add(MB,MR); KIT.glbDrone={MB,MR,hubs}; kitDronePose(0); }
function kitDronePose(t){ const D=KIT.glbDrone; if(!D) return; KIT.drones.forEach((d,k)=>{ const dy=Math.sin(t*1.6+d.ph)*.06; _q.set(0,0,0,1); _m.compose(_v.copy(d.pos).setY(d.pos.y+dy),_q,_s.set(d.k,d.k,d.k)); D.MB.setMatrixAt(k,_m);
    D.hubs.forEach((h,j)=>{ _e.set(0,t*40+j*.8,0); _q.setFromEuler(_e); _m.compose(_v.copy(h).multiplyScalar(d.k).add(d.pos).setY(d.pos.y+dy+h.y*d.k),_q,_s.set(d.k,d.k,d.k)); D.MR.setMatrixAt(k*4+j,_m); }); });
  D.MB.instanceMatrix.needsUpdate=true; D.MR.instanceMatrix.needsUpdate=true; }
// ---------- exterior hiding while inside: camera layer 5 = kit-keep set (garage group, rider, HUD, lights; downstairs also the street in front of the bay) ----------
const KIT_LAYER=5; let kitHide=null;
function kitTagKeep(G,mode){ const inv=new THREE.Matrix4().copy(G.group.matrixWorld).invert(), v=new THREE.Vector3(); const keepTree=new Set([G.group,Ride.group,camera]);
  scene.traverse(o=>{ if(!(o.isMesh||o.isLight||o.isSprite||o.isPoints||o.isLine)) return; let keep=o.isLight&&(o.isHemisphereLight||o.isAmbientLight); if(!keep) for(let a=o;a;a=a.parent) if(keepTree.has(a)){ keep=true; break; } let npc=false; for(let a=o;a;a=a.parent) if(a.userData&&(a.userData.npc||a.userData.rider)&&a!==Ride.group){ npc=true; break; } if(npc){ o.layers.disable(KIT_LAYER); return; } // roaming NPC riders never draw inside
    if(!keep&&mode==='down'){ if(o.isInstancedMesh||!o.geometry) keep=true; else { if(!o.geometry.boundingSphere) o.geometry.computeBoundingSphere(); const bs=o.geometry.boundingSphere; v.copy(bs.center).applyMatrix4(o.matrixWorld).applyMatrix4(inv); const r=bs.radius*o.matrixWorld.getMaxScaleOnAxis(); keep=r>60||v.z+r>-1; } }
    if(keep) o.layers.enable(KIT_LAYER); else o.layers.disable(KIT_LAYER); }); }
function kitCams(on){ const cs=[camera]; if(renderer.xr&&renderer.xr.isPresenting){ const v=renderer.xr.getCamera(camera); cs.push(v); if(v.cameras) cs.push(...v.cameras); }
  for(const c of cs){ if(on){ c.layers.disable(0); c.layers.enable(KIT_LAYER); } else { c.layers.enable(0); c.layers.disable(KIT_LAYER); } } }
function kitExterior(G,inside,mode){ const key=inside?G.crew+mode:null; if(key===kitHide){ if(key&&(++KIT.tagT%30)===0) Ride.group.traverse(o=>o.layers.enable(KIT_LAYER)); if(key) kitCams(true); return; }
  kitHide=key; if(window.KIT_NOHIDE||!key){ kitCams(false); return; } kitTagKeep(G,mode); kitCams(true); }
KIT.tagT=0;
// ---------- apply to a garage ----------
function kitApply(G){ const T=kitTheme(G.crew); KIT.theme=T; if(G.crew==='karasu') window.KOG_THEME=T; U.uC1.value.set(T.c1); U.uC2.value.set(T.c2); kitDrawAtlas(T); if(KIT.skates) KIT.skates.mat.emissive.set(T.c1).multiplyScalar(.12); if(KIT.skates&&kitEnv()&&KIT.skates.mat.envMap!==KIT.env){ KIT.skates.mat.envMap=KIT.env; KIT.skates.mat.envMapIntensity=.7; KIT.skates.mat.needsUpdate=true; } (KIT.glbMats||[]).forEach(m=>m.emissive.set(T.c1)); if(KIT.deskMat) KIT.deskMat.emissive.set(T.c1).lerp(new THREE.Color(1,1,1),.35); kitTvTex();
  if(KIT.g&&KIT.g.group) KIT.oldMeshes.forEach(m=>m.visible=true);
  KIT.g=G; G.group.add(KIT.root); KIT.oldMeshes=G.group.children.filter(o=>{ if(!o.isMesh||o===KIT.root||!o.geometry) return false; if(!o.geometry.boundingBox) o.geometry.computeBoundingBox(); const b=o.geometry.boundingBox.clone().applyMatrix4(o.matrix); return b.min.x>-5.7&&b.max.x<5.7&&b.min.z>-9.7&&b.max.z<-.3&&b.max.y<5.3&&!(Math.abs(b.min.x)<2.2&&b.min.z>-6.5&&b.max.z<-1.5&&b.max.y<2.3); }); KIT.oldMeshes.forEach(m=>m.visible=false);
  KIT.root.updateMatrixWorld(true); kitLights(); }
function kitLights(){ let i=0; for(const R of [KIT.up.visible&&!KIT.down.visible?KIT.up:KIT.down]) for(const [x,y,z,w] of R.userData.lights){ if(i>=8) break; const v=new THREE.Vector3(x,y,z).applyMatrix4(R.matrixWorld); U.uKL.value[i].copy(v); if(w<0) U.uKC.value[i].setRGB(1,.62,.32).multiplyScalar(-w*2.0); else U.uKC.value[i].copy(U.uC1.value).lerp(new THREE.Color(0xffffff),.45).multiplyScalar(w*2.0); i++; } }
function kitBuild(){ const root=new THREE.Group(); root.name='kit_root'; root.userData.noMerge=true; root.userData.mod='kit';
  KIT.down=buildDown(); KIT.up=buildUp(); KIT.up.position.set(0,KIT_UPY,-8.35); root.add(KIT.down,KIT.up); KIT.root=root; KIT.oldMeshes=[];
  // colliders for downstairs props, added in every garage footprint (same layout everywhere)
  for(const G of garages){ const th=G.th, [gx,gz]=G.pos; const W=(lx,lz)=>[gx+lx*Math.cos(th)+lz*Math.sin(th), gz-lx*Math.sin(th)+lz*Math.cos(th)];
    const c2=(a0,a1,b0,b1,fl)=>{ const a=W(a0,b0), b=W(a1,b1); colliders.push({minX:Math.min(a[0],b[0]),maxX:Math.max(a[0],b[0]),minZ:Math.min(a[1],b[1]),maxZ:Math.max(a[1],b[1]),kit:1,fl:fl||'down',g:G,off:fl==='up'}); };
    for(const [x0,x1,z0,z1] of KIT.upCol) c2(x0,x1,z0-8.35,z1-8.35,'up');
    for(const z of [-3.5,-4.7,-5.9]) c2(1.6,5.0,z-.32,z+.32); c2(-5.5,-4.6,-6.8,-4.4); c2(-4.55,-3.45,-2.3,-.2); c2(-2.95,-.95,-1.2,-.6); c2(-1.0,5.5,-9.5,-8.8); c2(-1.5,-.5,-7.2,-6.2); }
  }
window.KIT_GROUND=function(x,z,yHint){ const G=KIT.g; if(!G) return null; const th=G.th, dx=x-G.pos[0], dz=z-G.pos[1]; const lx=dx*Math.cos(th)-dz*Math.sin(th), lz=dx*Math.sin(th)+dz*Math.cos(th); yHint=yHint||0;
  const S=[]; if(lx>-5.5&&lx<5.5&&lz>-9.5&&lz<-.3){ S.push({y:0,surf:'floor'}); if(lz<-7.2) S.push({y:2.6,surf:'mezz'}); if(Math.abs(lx+1)<.45&&lz<-4.4&&lz>-7.2){ const t=(-4.4-lz)/2.8; S.push({y:t*2.6,surf:'stair',n:[0,.73,.68]}); } }
  const rz=lz+8.35; if(lx>-6&&lx<6&&rz>-8&&rz<8){ S.push({y:KIT_UPY,surf:'loft'}); const pod=KIT.pools.up.pod.name==='kit_pods'?KIT_POD_FOOT.find(f=>lx>f.minX&&lx<f.maxX&&rz>f.minZ&&rz<f.maxZ):null; if(pod) S.push({y:KIT_UPY+3.2+1.4*KIT_PS,surf:'pod'}); else if((lx<1.6&&rz<-5.8)||lx>3.8) S.push({y:KIT_UPY+3.2,surf:'catwalk'}); if(lx>1.2&&lx<3.8&&Math.abs(rz+6.9)<.5){ S.push({y:KIT_UPY+(lx-1.2)/2.6*3.2,surf:'stair',n:[-.78,.63,0]}); } }
  if(!S.length) return null; let best=S[0]; for(const s of S) if(s.y<=yHint+.6&&s.y>=best.y) best=s; const n=best.n||[0,1,0]; return {y:best.y,nx:n[0],ny:n[1],nz:n[2],surf:best.surf}; };
window.KOG_GROUND=(x,z,y)=>KIT.g&&KIT.g.crew==='karasu'?KIT_GROUND(x,z,y):null;
const KIT_R=14, _kc=new THREE.Vector3(); // player within 14 m of the garage+loft footprint centre (local 0,-8): inside or at the door
function kitColGate(G){ const up=!!(G&&(KIT.up.visible||window.KIT_FLOOR==='up')); if(KIT._cg===(up?G:null)) return; KIT._cg=up?G:null; for(const c of colliders){ if(!c.kit||!c.fl) continue; c.off=c.fl==='up'?!(up&&c.g===G):(up&&c.g===G); }
  // ground-level world colliders have no height; while the rider is on the loft (13 m up) the ones under the loft footprint are switched off, and restored on leaving
  for(const c of colliders) if(c._ko){ c.off=c._ko.prev; delete c._ko; }
  if(up){ const xs=[],zs=[]; for(const [x,z] of [[-6,-16.35],[6,-16.35],[-6,-.35],[6,-.35]]){ const v=G.group.localToWorld(new THREE.Vector3(x,0,z)); xs.push(v.x); zs.push(v.z); } const a0=Math.min(...xs),a1=Math.max(...xs),b0=Math.min(...zs),b1=Math.max(...zs);
    for(const c of colliders){ if(c.kit||c.off) continue; if(c.maxX>a0&&c.minX<a1&&c.maxZ>b0&&c.minZ<b1){ c._ko={prev:!!c.off}; c.off=true; } } } }
window.kitColGate=kitColGate; window.KIT_LANE=KIT_LANE;
// textures + GLBs (skates, Forge props) load on first approach within ~40 m of any garage, not at spawn
const KIT_LAZY_R=40; function kitLazy(){ KIT.lazy=true; KIT.lazyT=performance.now(); try{ KIT_DEFER.splice(0).forEach(f=>f()); }catch(e){ console.warn('kit tex',e); } kitSkates(); kitSwapProps().then(()=>{ KIT.propsReady=true; }); }
function kitTick(){ if(!KIT.root) return; const cam=(renderer.xr&&renderer.xr.isPresenting)?renderer.xr.getCamera(camera):camera; const p=new THREE.Vector3(); cam.getWorldPosition(p); const pp=(typeof Ride!=='undefined'&&Ride.group)?Ride.group.position:p; // gate on the PLAYER, floor choice on camera height
  let best=null,bd=1e9; for(const G of garages){ const c=G.group.localToWorld(_kc.set(0,0,-8)); const d=Math.hypot(c.x-pp.x,c.z-pp.z); if(d<bd){ bd=d; best=G; } } if(window.KIT_FORCE) best=garages.find(g=>g.crew===window.KIT_FORCE)||best,bd=0;
  if(!KIT.lazy&&(bd<KIT_LAZY_R||window.KIT_FORCE)) kitLazy(); kitColGate(bd<KIT_R?best:null); const on=bd<KIT_R; KIT.root.visible=on; if(!on) kitExterior(null,false); if(on&&best!==KIT.g) kitApply(best); if(!on){ if(KIT.oldMeshes) KIT.oldMeshes.forEach(m=>m.visible=true); KIT.g=null; return; }
  const ly=p.y, wasUp=KIT.up.visible; KIT.up.visible=ly-(KIT.g?0:0)>KIT_UPY-1.5||window.KIT_FLOOR==='up'; KIT.down.visible=!KIT.up.visible||window.KIT_FLOOR==='both'; if(wasUp!==KIT.up.visible) kitLights(); { const inv=new THREE.Matrix4().copy(best.group.matrixWorld).invert(); const lp=new THREE.Vector3(pp.x,0,pp.z).applyMatrix4(inv); const inside=lp.x>-6&&lp.x<6&&lp.z>-17&&lp.z<-.2; KIT.inside=inside; kitExterior(best,inside,KIT.up.visible?'up':'down'); } 
  const t=(performance.now()-(KIT.t0||(KIT.t0=performance.now())))/1000, P=KIT.pools.up.drone; if(KIT.up.visible&&KIT.glbDrone) kitDronePose(t); else if(KIT.up.visible){ for(const d of KIT.drones){ const dy=Math.sin(t*1.6+d.ph)*.06; for(const i of d.ids){ P.getMatrixAt(i,_m); _m.elements[13]+= dy-(d._dy||0); P.setMatrixAt(i,_m); } d._dy=dy; } P.instanceMatrix.needsUpdate=true; } }

// ---------- per-crew EXTERIOR variants (Palma only; Volt charging plaza / Rust Claw salvage shed) ----------
// Budget: <=~6 draws each via shared mats + mergeBufferGeometries / InstancedMesh. No cars/bikes/boards.
const KIT_EXT={ mats:null, done:Object.create(null) };
function kitExtMats(){ if(KIT_EXT.mats) return KIT_EXT.mats;
  const M={};
  M.steel=new THREE.MeshStandardMaterial({color:0x6a7078,roughness:.55,metalness:.7});
  M.dark=new THREE.MeshStandardMaterial({color:0x1c1e22,roughness:.6,metalness:.45}); // Volt canopy underside composite; shared
  M.glass=new THREE.MeshStandardMaterial({color:0x88c8e8,roughness:.15,metalness:.2,transparent:true,opacity:.45,depthWrite:false});
  M.corr=new THREE.MeshStandardMaterial({color:0x7a4a2a,roughness:.85,metalness:.55});
  M.corr2=new THREE.MeshStandardMaterial({color:0x5a5e64,roughness:.7,metalness:.65});
  M.wood=new THREE.MeshStandardMaterial({color:0x5a4030,roughness:.95,metalness:0});
  M.buoy=new THREE.MeshStandardMaterial({color:0xd45020,roughness:.55,metalness:.1});
  M.chain=new THREE.MeshStandardMaterial({color:0x3a3c40,roughness:.6,metalness:.8});
  M.boll=new THREE.MeshStandardMaterial({color:0x2a2e34,roughness:.45,metalness:.75});
  KIT_EXT.mats=M; return M; }
function kitExtNeon(col){ const m=new THREE.MeshBasicMaterial({color:col}); m.toneMapped=false; return m; }
function kitExtBox(w,h,d,x,y,z,rx,ry,rz){ const g=new THREE.BoxGeometry(w,h,d); if(rx||ry||rz){ g.rotateX(rx||0); g.rotateY(ry||0); g.rotateZ(rz||0); } g.translate(x,y,z); return g; }
function kitExtCyl(rt,rb,h,x,y,z,seg){ const g=new THREE.CylinderGeometry(rt,rb,h,seg||8); g.translate(x,y,z); return g; }
function kitExtMerge(geos,mat,parent,name){ const ok=geos.filter(Boolean); if(!ok.length) return null;
  const g=THREE.BufferGeometryUtils.mergeBufferGeometries(ok,false); if(!g) return null;
  const m=new THREE.Mesh(g,mat); m.name=name||'kit_ext'; m.userData.noMerge=true; m.userData.mod='kit_ext'; m.frustumCulled=true; parent.add(m); return m; }
function kitExtPushCol(G,boxes){ const th=G.th,[gx,gz]=G.pos; const W=(lx,lz)=>[gx+lx*Math.cos(th)+lz*Math.sin(th), gz-lx*Math.sin(th)+lz*Math.cos(th)];
  for(const [a0,a1,b0,b1] of boxes){ const a=W(a0,b0), b=W(a1,b1); colliders.push({minX:Math.min(a[0],b[0]),maxX:Math.max(a[0],b[0]),minZ:Math.min(a[1],b[1]),maxZ:Math.max(a[1],b[1]),kit_ext:1,g:G}); } }
function kitExtVolt(G){ // EV charging plaza: canopy + glass kiosk + bollards + neon (target ~6 draws)
  // Canopy underside clearance >=3.5 m (deck y=3.85, th=.18 -> underside 3.76). No footprint AABB (2D colliders would block under-pass); posts+kiosk+bollards already collide. Thin deck is non-walkable (no ground height).
  // Ani 14:00: underside was a blown-out 0xffe600 MeshBasic slab — dark PBR deck + thin tone-mapped emissive strips only.
  const M=kitExtMats(), root=new THREE.Group(); root.name='kit_ext_volt'; root.userData.noMerge=true; G.group.add(root);
  const th=kitTheme(G.crew), c1=new THREE.Color(th.c1), accent=new THREE.Color(th.c2);
  // neon1: moderate emissive strips (NOT MeshBasic / toneMapped:false — that bloom-clipped as a yellow sheet)
  const neon1=new THREE.MeshStandardMaterial({color:0x14140c,emissive:c1.getHex(),emissiveIntensity:1.15,roughness:.35,metalness:.15,toneMapped:true});
  const neon2=kitExtNeon(accent.getHex());
  // draw 1: dark body — canopy deck (underside reads as dark metal) + kiosk shell + underside panel grooves
  kitExtMerge([kitExtBox(10.5,.18,6.2,0,3.85,5.2), kitExtBox(2.2,2.6,2.0,-5.2,1.3,6.5),
    kitExtBox(10.0,.015,.035,0,3.745,3.55),kitExtBox(10.0,.015,.035,0,3.745,5.2),kitExtBox(10.0,.015,.035,0,3.745,6.85),
    kitExtBox(.035,.015,5.6,-3.3,3.745,5.2),kitExtBox(.035,.015,5.6,3.3,3.745,5.2)], M.dark, root, 'kit_ext_volt_dark');
  // draw 2: steel (canopy posts + kiosk roof) — posts h=3.76 @ cy=1.88 reach deck underside
  kitExtMerge([kitExtCyl(.09,.11,3.76,-4.6,1.88,3.0),kitExtCyl(.09,.11,3.76,-4.6,1.88,7.2),kitExtCyl(.09,.11,3.76,4.6,1.88,3.0),kitExtCyl(.09,.11,3.76,4.6,1.88,7.2),kitExtBox(2.3,.12,2.1,-5.2,2.66,6.5)], M.steel, root, 'kit_ext_volt_steel');
  // draw 3: yellow emissive accents only — thin perimeter + cross strips + yard strip (no full-slab)
  kitExtMerge([kitExtBox(10.55,.03,.05,0,3.74,2.15),kitExtBox(10.55,.03,.05,0,3.74,8.25),
    kitExtBox(.05,.03,6.15,-5.22,3.74,5.2),kitExtBox(.05,.03,6.15,5.22,3.74,5.2),
    kitExtBox(9.6,.025,.045,0,3.735,3.4),kitExtBox(9.6,.025,.045,0,3.735,5.2),kitExtBox(9.6,.025,.045,0,3.735,7.0),
    kitExtBox(9.5,.03,.2,0,.04,8.2)], neon1, root, 'kit_ext_volt_neon1');
  // draw 4: neon accent (kiosk bar + 4 cable arms as boxes)
  kitExtMerge([kitExtBox(1.6,.18,.06,-5.2,2.4,7.55),kitExtBox(.06,1.4,.06,-2.2,2.7,4.2),kitExtBox(.06,1.4,.06,-.4,2.7,4.2),kitExtBox(.06,1.4,.06,1.4,2.7,4.2),kitExtBox(.06,1.4,.06,3.2,2.7,4.2)], neon2, root, 'kit_ext_volt_neon2');
  // draw 5: glass kiosk pane
  kitExtMerge([kitExtBox(1.9,1.6,.06,-5.2,1.5,7.52)], M.glass, root, 'kit_ext_volt_glass');
  // draw 6: bollards InstancedMesh
  const bGeo=new THREE.CylinderGeometry(.18,.22,1.15,10); const boll=new THREE.InstancedMesh(bGeo,M.boll,4); boll.name='kit_ext_volt_bollards'; boll.userData.noMerge=true; boll.userData.mod='kit_ext';
  const _m=new THREE.Matrix4(),_q=new THREE.Quaternion(),_s=new THREE.Vector3(1,1,1),_p=new THREE.Vector3();
  [[-2.2,4.2],[-.4,4.2],[1.4,4.2],[3.2,4.2]].forEach((xz,i)=>{ _p.set(xz[0],.58,xz[1]); _m.compose(_p,_q,_s); boll.setMatrixAt(i,_m); });
  root.add(boll);
  // kiosk + bollard row only (canopy footprint intentionally NOT an xz collider — would block the 3.76 m under-pass)
  kitExtPushCol(G,[[-6.3,-4.1,5.5,7.6],[-2.5,3.5,3.9,4.6]]);
  G.extVariant=root; return root; }
function kitExtRustClaw(G){ // corrugated salvage shed + marina salvage (target ~6 draws)
  const M=kitExtMats(), root=new THREE.Group(); root.name='kit_ext_rustclaw'; root.userData.noMerge=true; G.group.add(root);
  const th=kitTheme(G.crew), c1=new THREE.Color(th.c1); const neon1=kitExtNeon(c1.getHex());
  const _m=new THREE.Matrix4(),_q=new THREE.Quaternion(),_s=new THREE.Vector3(1,1,1),_p=new THREE.Vector3();
  // draw 1: corrugated panels (InstancedMesh)
  const panelGeo=new THREE.BoxGeometry(2.4,4.6,.08); const panels=new THREE.InstancedMesh(panelGeo,M.corr,6); panels.name='kit_ext_rc_panels'; panels.userData.noMerge=true; panels.userData.mod='kit_ext';
  [[-4.75,2.3,.05,0],[4.75,2.3,.05,0],[-5.85,2.3,-2.5,1],[-5.85,2.3,-6.5,1],[5.85,2.3,-2.5,1],[5.85,2.3,-6.5,1]].forEach((p,i)=>{
    _p.set(p[0],p[1],p[2]); if(p[3]) _q.setFromAxisAngle(new THREE.Vector3(0,1,0),Math.PI/2); else _q.identity(); _m.compose(_p,_q,_s.set(1,1,1)); panels.setMatrixAt(i,_m); });
  root.add(panels);
  // draw 2: galvanized strips + crane boom/mast/hook (steel+chain merged as steel-ish)
  kitExtMerge([kitExtBox(2.4,.12,.1,-4.75,4.4,.1),kitExtBox(2.4,.12,.1,4.75,4.4,.1),kitExtBox(2.4,.12,.1,-4.75,.3,.1),kitExtBox(2.4,.12,.1,4.75,.3,.1),
    kitExtBox(.12,.12,4.5,3.2,5.8,2.0,0,.2,-.35),kitExtBox(.25,.8,.25,3.2,4.6,.2),kitExtCyl(.04,.04,1.2,4.6,4.9,3.6,6)], M.steel, root, 'kit_ext_rc_steel');
  // draw 3: wood crates IM
  const crateGeo=new THREE.BoxGeometry(1.1,.7,.9); const crates=new THREE.InstancedMesh(crateGeo,M.wood,5); crates.name='kit_ext_rc_crates'; crates.userData.noMerge=true; crates.userData.mod='kit_ext';
  [[-5.2,.35,5.5],[-5.2,1.05,5.5],[-3.8,.35,6.2],[4.6,.35,5.8],[5.0,1.05,5.8]].forEach((p,i)=>{ _p.set(p[0],p[1],p[2]); _q.setFromAxisAngle(new THREE.Vector3(0,1,0),(i%3)*.4); _m.compose(_p,_q,_s.set(1,1,1)); crates.setMatrixAt(i,_m); });
  root.add(crates);
  // draw 4: hull plates IM (reuse corr)
  const plateGeo=new THREE.BoxGeometry(1.8,.08,1.1); const plates=new THREE.InstancedMesh(plateGeo,M.corr2,4); plates.name='kit_ext_rc_plates'; plates.userData.noMerge=true; plates.userData.mod='kit_ext';
  [[5.0,.9,3.8],[5.2,1.5,3.5],[-5.4,.8,3.6],[-5.0,1.4,3.2]].forEach((p,i)=>{ _p.set(p[0],p[1],p[2]); _q.setFromEuler(new THREE.Euler(.2,(i%2?1:-1)*.5,.15)); _m.compose(_p,_q,_s.set(1,1,1)); plates.setMatrixAt(i,_m); });
  root.add(plates);
  // draw 5: buoys IM
  const buoyGeo=new THREE.SphereGeometry(.35,10,8); const buoys=new THREE.InstancedMesh(buoyGeo,M.buoy,4); buoys.name='kit_ext_rc_buoys'; buoys.userData.noMerge=true; buoys.userData.mod='kit_ext';
  [[-4.2,.4,7.0],[-3.5,.4,7.3],[4.0,.4,7.1],[4.8,.55,6.6]].forEach((p,i)=>{ _p.set(p[0],p[1],p[2]); _q.identity(); _m.compose(_p,_q,_s.set(1,1,1)); buoys.setMatrixAt(i,_m); });
  root.add(buoys);
  // draw 6: neon bar + yard pad + hook torus (neon + dark + chain) — keep to 1 neon mesh; pad on dark; hook as chain single
  kitExtMerge([kitExtBox(3.2,.22,.06,0,4.9,.35)], neon1, root, 'kit_ext_rc_neon');
  // hook torus can't easily merge with boxes of different type into same draw with different mat — add as part of steel already? Add separate chain mesh would be draw 7.
  // Fold hook into steel draw by approximating with small boxes already in steel merge; skip torus to hold budget.
  kitExtPushCol(G,[[-5.8,-3.2,5.0,7.4],[3.4,5.8,5.2,7.2],[2.8,3.8,0,.6]]);
  G.extVariant=root; return root; }
function kitPaintEmblem(crew,css){ // black disc + neon ring + kit_logos atlas slot (matches world.js emblemTex frame)
  const c=document.createElement('canvas'); c.width=c.height=512; const x=c.getContext('2d');
  x.translate(256,256); x.fillStyle='#0A0A0A'; x.beginPath(); x.arc(0,0,240,0,7); x.fill();
  x.lineWidth=18; x.strokeStyle=css; x.shadowColor=css; x.shadowBlur=30; x.beginPath(); x.arc(0,0,222,0,7); x.stroke();
  const i=KIT_LOGO_SLOT[crew]; if(logoReady&&i!=null){ x.shadowBlur=0; x.drawImage(LOGO,(i%4)*256,((i/4)|0)*256,256,256,-180,-180,360,360); }
  const t=new THREE.CanvasTexture(c); t.needsUpdate=true; return t; }
function kitFixEmblems(){ // exterior emblem discs for volt/rustclaw were empty (emblemTex has no branch). world_perf atlasSigns may already have baked the empty disc — pull those entries out and show live meshes with kit_logos. Karasu/others untouched.
  if(!logoReady){ if(!kitFixEmblems._w){ kitFixEmblems._w=1; LOGO.addEventListener('load',kitFixEmblems); } return; }
  if(typeof garages==='undefined') return;
  // retry until world_perf atlas has run (SIGN.list) so we can detach; also fine if atlas never packs them
  const fixed=[];
  for(const G of garages){ if(G.crew!=='volt'&&G.crew!=='rustclaw') continue;
    const tex=G._emblemTex||(G._emblemTex=kitPaintEmblem(G.crew,G.color||'#fff'));
    G.group.traverse(o=>{ if(!o.isMesh||!o.material) return;
      if(!(o.geometry&&o.geometry.type==='PlaneGeometry')) return;
      if(Math.abs(o.position.y-10)>0.2) return; // exterior emblem @ H+4.8
      if(!o.userData.kitEmblem){ o.userData.kitEmblem=1; o.userData.noMerge=true;
        o.material=new THREE.MeshBasicMaterial({map:tex,transparent:true,side:THREE.DoubleSide,depthWrite:false,toneMapped:false}); }
      else if(o.material&&o.material.map!==tex){ o.material.map=tex; o.material.needsUpdate=true; }
      o.visible=true; fixed.push(o); });
    G._emblemFixed=1; }
  try{ const S=(typeof WORLD_PERF!=='undefined'&&WORLD_PERF.SIGN)||(typeof SIGN!=='undefined'?SIGN:null);
    if(S&&S.list&&fixed.length){ for(let i=S.list.length-1;i>=0;i--){ const it=S.list[i]; if(!it||!it.o||!fixed.includes(it.o)) continue;
      try{ const a=it.mesh.geometry.attributes.position; a.array.fill(it.base[0],it.j*18,it.j*18+18); a.needsUpdate=true; }catch(e){}
      if(it.sw&&S.swaps){ try{ it.sw.dispose(); S.swaps.delete(it); }catch(e){} }
      it.o.visible=true; it.dead=true; S.list.splice(i,1);
      if(typeof FARCULL!=='undefined') FARCULL.push({o:it.o,cen:it.cen||it.o.getWorldPosition(new THREE.Vector3()),r:it.far||95}); } }
  }catch(e){ console.warn('kitFixEmblems SIGN detach',e); }
  window.KIT_EMBLEM_FIXED=true;
  // world_perf may atlas after us (staticMerge +2.5s); re-run once more to catch late packing
  if(!kitFixEmblems._again){ kitFixEmblems._again=1; setTimeout(kitFixEmblems,3500); } }
function kitExtVariant(G){ if(!G||KIT_EXT.done[G.crew]) return; KIT_EXT.done[G.crew]=1;
  try{ if(G.crew==='volt') kitExtVolt(G); else if(G.crew==='rustclaw') kitExtRustClaw(G); }catch(e){ console.warn('kitExtVariant '+G.crew,e); } }
function kitExtAll(){ if(typeof garages==='undefined'||!garages.length) return; if(!(THREE.BufferGeometryUtils&&THREE.BufferGeometryUtils.mergeBufferGeometries)) return setTimeout(kitExtAll,250); for(const G of garages) kitExtVariant(G); }
window.kitExtVariant=kitExtVariant; window.kitExtAll=kitExtAll; window.kitExtVolt=kitExtVolt; window.kitExtRustClaw=kitExtRustClaw; window.kitFixEmblems=kitFixEmblems;
function kitInit(){ if(typeof garages==='undefined'||!garages.length||typeof scene==='undefined'||!THREE.GLTFLoader||typeof animated==='undefined'){ return setTimeout(kitInit,300); }
  if(/nokit/.test(location.search)) return; try{ kitExtAll(); kitBuild(); kitFixEmblems(); animated.push(kitTick); window.KIT_READY=true; }catch(e){ console.warn('crewhouse kit failed',e); } }
setTimeout(kitInit,0);
})();
