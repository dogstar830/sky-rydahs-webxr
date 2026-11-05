// ===== CREW TURF TAGGING (JSRF-style) + BOOST DASH =====
// Tags: one InstancedMesh (1 draw call) sampling a 2048x512 canvas graffiti atlas (8 crews x [single, big-L, big-M, big-R]).
// Ownership persists in localStorage; rivals retake a few spots based on time away. Dash: meter, burst, post blur/ripple, crew streak ribbons.
const TURF={ ready:false, spots:[], pieces:[], crews:[], dist:{}, mesh:null, key:"skyrydahs.turf.v1", saveT:0, cur:null, sprayT:0, welcomeT:0 };
const TQ=new URLSearchParams(location.search);
function turfCrews(){ const names={codee:"CODE:E",karasu:"KARASU",static:"STATIC",behemoth:"BEHEMOTH",anubis:"ANUBIS",forest:"FOREST",genesis:"GENESIS",ttt:"TTT"};
  const full={codee:"Code : E",karasu:"Kogarasumaru",static:"Static Angels",behemoth:"Behemoth",anubis:"Anubis",forest:"Sleeping Forest",genesis:"Genesis",ttt:"Tool Toul To"};
  return PALMA.garages.slice(0,8).map(g=>({id:g.crew,css:g.crew==="codee"?"#FFD700":g.color,hex:g.crew==="codee"?0xffd700:new THREE.Color(g.color).getHex(),tag:names[g.crew]||g.name,name:full[g.crew]||g.name,pos:g.pos})); }
function turfPlayerCrew(){ return TURF.crews.findIndex(c=>c.id===(PLAYER_MODE==="ikki"?"karasu":"codee")); }
function turfEmblem(x,id,cx,cy,r,col){ x.save(); x.translate(cx,cy); x.lineJoin="round"; x.fillStyle="#0a0a0a"; x.strokeStyle="#0a0a0a"; x.lineWidth=10;
  const path=()=>{ x.beginPath(); if(id==="karasu"){ const k=r/32; x.moveTo(0,-6*k); x.quadraticCurveTo(-14*k,-18*k,-30*k,-10*k); x.quadraticCurveTo(-18*k,-6*k,-12*k,2*k); x.lineTo(-6*k,0); x.lineTo(-4*k,16*k); x.lineTo(0,12*k); x.lineTo(4*k,16*k); x.lineTo(6*k,0); x.lineTo(12*k,2*k); x.quadraticCurveTo(18*k,-6*k,30*k,-10*k); x.quadraticCurveTo(14*k,-18*k,0,-6*k); }
    else { const n=id==="codee"?6:id==="static"?5:id==="anubis"?3:id==="behemoth"?4:id==="genesis"?8:id==="forest"?7:4; for(let i=0;i<n;i++){ const a=i/n*Math.PI*2-Math.PI/2; x.lineTo(Math.cos(a)*r,Math.sin(a)*r); } x.closePath(); } };
  path(); x.stroke(); x.fillStyle=col; path(); x.fill();
  if(id!=="karasu"){ x.fillStyle="#0a0a0a"; x.font=`900 ${r*1.1|0}px Impact,Arial Black,sans-serif`; x.textAlign="center"; x.textBaseline="middle"; x.fillText(id==="codee"?"E":id[0].toUpperCase(),0,r*.08); }
  x.restore(); }
function turfPiece(x,c,text,X,Y,W,H,emblem){ // stylised wildstyle-ish bubble letters: drop shadow, black outline, crew fill + gradient, white shine, drips
  x.save(); x.beginPath(); x.rect(X,Y,W,H); x.clip(); const fs=Math.min(H*.78,W/(text.length*.62)); x.font=`900 ${fs|0}px Impact,"Arial Black",sans-serif`; x.textAlign="center"; x.textBaseline="middle";
  const cx=X+W/2+(emblem?H*.32:0), cy=Y+H*.52; x.save(); x.translate(cx,cy); x.transform(1,0,-.18,1,0,0); x.rotate(-.05);
  x.lineJoin="round"; x.strokeStyle="#000"; x.lineWidth=fs*.32; x.strokeText(text,6,8); x.lineWidth=fs*.2; x.strokeStyle="#0a0a0a"; x.strokeText(text,0,0);
  const gr=x.createLinearGradient(0,-fs/2,0,fs/2); gr.addColorStop(0,"#fff"); gr.addColorStop(.18,c.css); gr.addColorStop(.75,c.css); gr.addColorStop(1,"#000"); x.fillStyle=gr; x.fillText(text,0,0);
  x.globalAlpha=.85; x.fillStyle="#fff"; x.fillText(text.replace(/./g,m=>m),-fs*.03,-fs*.05); x.globalCompositeOperation="source-atop"; x.fillStyle=c.css; x.fillText(text,0,fs*.02); x.restore(); x.restore();
  x.save(); x.fillStyle=c.css; for(let i=0;i<6;i++){ const dx=X+W*(.12+.76*((i*37%11)/11)), l=H*(.08+.12*((i*53%7)/7)); x.fillRect(dx,cy+fs*.32,3,l); x.beginPath(); x.arc(dx+1.5,cy+fs*.32+l,3,0,7); x.fill(); } x.restore();
  if(emblem) turfEmblem(x,c.id,X+H*.42,Y+H*.5,H*.3,c.css); }
function turfAtlas(){ const T=256, Hh=128, cv=document.createElement("canvas"); cv.width=8*T; cv.height=4*Hh; const x=cv.getContext("2d");
  TURF.crews.forEach((c,i)=>{ turfPiece(x,c,c.tag.length>6?c.tag.slice(0,6):c.tag,i*T,0,T,Hh,true);                 // row 0: single tag w/ emblem
    const w=document.createElement("canvas"); w.width=3*T; w.height=Hh; const y=w.getContext("2d"); turfPiece(y,c,c.tag,0,0,3*T,Hh,true); // rows 1-3: big piece sliced L/M/R
    for(let s=0;s<3;s++) x.drawImage(w,s*T,0,T,Hh,i*T,(1+s)*Hh,T,Hh); });
  const t=new THREE.CanvasTexture(cv); t.anisotropy=4; return t; }
function turfDistrict(x,z){ for(const q of PALMA.districts){ const b=q.box; if(x>=b[0]&&x<=b[2]&&z>=b[1]&&z<=b[3]) return q; } return null; }
function turfInside(x,z){ for(const c of colliders) if(x>c.minX-.3&&x<c.maxX+.3&&z>c.minZ-.3&&z<c.maxZ+.3) return true; return false; }
// Flush wall spots onto the VISIBLE wall face (+2 cm along the normal). Collider boxes can sit inside the rendered wall
// (e.g. crew-base annex back walls), which buried tiles ("ST FORES"). Raycasts from 3 m out along -normal at the tile height
// against opaque scene meshes near the spot; moves x/z only (ids, owners and localStorage keys unchanged). Returns the moved list.
function turfFlush(spots,yOf){ const moved=[]; try{ const rc=new THREE.Raycaster(), o=new THREE.Vector3(), d=new THREE.Vector3(), sph=new THREE.Sphere(), cand=[];
  scene.updateMatrixWorld(true); const skip=new Set(); try{ if(Ride.group) Ride.group.traverse(x=>skip.add(x)); }catch(e){}
  scene.traverse(m=>{ if(!(m.isMesh)||!m.visible||skip.has(m)||!m.geometry) return; const ms=Array.isArray(m.material)?m.material:[m.material]; if(ms.some(q=>!q||q.transparent||q.side===THREE.BackSide)) return; if(/graffiti|turf|heat_cops|perf/i.test(m.name||"")) return;
    if(!m.geometry.boundingSphere) m.geometry.computeBoundingSphere(); cand.push(m); });
  // 3 rays across the tile width (centre, ±1.1 m along the wall): the most-outward wall hit wins, so a tile can't stay partly inside.
  // Hits more than 0.6 m in front of the spot are props/poles/benches, not the wall: ignored (keeps tiles from floating out).
  for(const sp of spots){ const y=yOf(sp); if(y==null) continue; const tx=-sp.nz, tz=sp.nx; let best=null;
    for(const off of [0,-1.1,1.1]){ o.set(sp.x+sp.nx*3+tx*off,y,sp.z+sp.nz*3+tz*off); d.set(-sp.nx,0,-sp.nz); rc.set(o,d); rc.near=0; rc.far=3.6;
      const near=cand.filter(m=>{ if(m.isInstancedMesh) return true; sph.copy(m.geometry.boundingSphere).applyMatrix4(m.matrixWorld); return sph.distanceToPoint(o)<5; });
      const h=rc.intersectObjects(near,false).filter(h=>(!h.face||Math.abs(h.face.normal.y)<.7)&&h.distance>=2.4)[0]; if(h&&(!best||h.distance<best)) best=h.distance; }
    if(best==null) continue; const t=best;
    if(t<2.985||t>3.05){ const ox=sp.x, oz=sp.z, k=3-t+.02; sp.x+=sp.nx*k; sp.z+=sp.nz*k; moved.push({id:sp.id,from:[+ox.toFixed(2),+oz.toFixed(2)],to:[+sp.x.toFixed(2),+sp.z.toFixed(2)],d:+(3-t).toFixed(3)}); } } }catch(e){ console.warn("turfFlush",e); } return moved; }
function turfInit(){ TURF.crews=turfCrews(); TURF.me=turfPlayerCrew(); const me=TURF.me;
  // candidate wall faces from building/billboard/pylon collision boxes
  const faces=[]; for(const c of colliders){ const w=c.maxX-c.minX, d=c.maxZ-c.minZ; if(Math.max(w,d)<2.6||Math.max(w,d)>90) continue;
    for(const [nx,nz,len,px,pz] of [[1,0,d,c.maxX,(c.minZ+c.maxZ)/2],[-1,0,d,c.minX,(c.minZ+c.maxZ)/2],[0,1,w,(c.minX+c.maxX)/2,c.maxZ],[0,-1,w,(c.minX+c.maxX)/2,c.minZ]]){
      if(len<2.6) continue; const ox=px+nx*1.6, oz=pz+nz*1.6; if(!onLand(ox,oz)||turfInside(ox,oz)) continue; const q=turfDistrict(px,pz); if(!q) continue; faces.push({c,nx,nz,len,px,pz,q,key:q.name}); } }
  let seed=1337; const rr=()=>(seed=(seed*16807)%2147483647)/2147483647; // deterministic pick order -> stable spot ids per district
  const byD={}; for(const f of faces) (byD[f.key]=byD[f.key]||[]).push(f);
  let inst=[];
  for(const key of Object.keys(byD).sort()){ const L=byD[key].sort((a,b)=>(a.px-b.px)||(a.pz-b.pz)); const q=L[0].q; const ctr=[(q.box[0]+q.box[2])/2,(q.box[1]+q.box[3])/2];
    let rival=0, bd=1e9; TURF.crews.forEach((c,i)=>{ if(i===me) return; const dd=Math.hypot(c.pos[0]-ctr[0],c.pos[1]-ctr[1]); if(dd<bd){ bd=dd; rival=i; } });
    const D=TURF.dist[key]={key,name:key,rival,spots:[],box:q.box}; const used=[]; const far=(x,z)=>used.every(u=>Math.hypot(u[0]-x,u[1]-z)>9);
    const want=6+((key.length*7)%5); // 6-10 per district
    // one big piece (3 adjacent segments) on the longest free face
    const big=L.filter(f=>f.len>=9).sort((a,b)=>b.len-a.len)[0];
    if(big){ const pc={id:TURF.pieces.length,segs:[],d:key}; TURF.pieces.push(pc); const tx=-big.nz, tz=big.nx; for(let s=0;s<3;s++){ const o=(s-1)*2.45; const sp={id:key+"#"+D.spots.length,d:key,x:big.px+tx*o+big.nx*.06,z:big.pz+tz*o+big.nz*.06,nx:big.nx,nz:big.nz,piece:pc,seg:s,owner:rr()<.75?rival:-1,prog:1}; pc.segs.push(sp); D.spots.push(sp); }
      for(let s=1;s<3;s++) pc.segs[s].owner=pc.segs[0].owner; used.push([big.px,big.pz]); }
    const pool=L.slice(); for(let i=pool.length-1;i>0;i--){ const j=(rr()*(i+1))|0; [pool[i],pool[j]]=[pool[j],pool[i]]; }
    for(const f of pool){ if(D.spots.length>=want) break; if(!far(f.px,f.pz)) continue; used.push([f.px,f.pz]); D.spots.push({id:key+"#"+D.spots.length,d:key,x:f.px+f.nx*.06,z:f.pz+f.nz*.06,nx:f.nx,nz:f.nz,owner:rr()<.6?rival:-1,prog:1}); }
    TURF.spots.push(...D.spots); }
  TURF.flushed=turfFlush(TURF.spots,s=>s.piece?2.6:2.2);
  // instanced decal mesh
  const N=TURF.spots.length, geo=new THREE.InstancedBufferGeometry().copy(new THREE.PlaneGeometry(2.4,1.2)); geo.instanceCount=N;
  const aOld=new THREE.InstancedBufferAttribute(new Float32Array(N),1), aNew=new THREE.InstancedBufferAttribute(new Float32Array(N),1), aProg=new THREE.InstancedBufferAttribute(new Float32Array(N),1);
  aOld.setUsage(THREE.DynamicDrawUsage); aNew.setUsage(THREE.DynamicDrawUsage); aProg.setUsage(THREE.DynamicDrawUsage); geo.setAttribute("aOld",aOld); geo.setAttribute("aNew",aNew); geo.setAttribute("aProg",aProg);
  const mat=new THREE.ShaderMaterial({ transparent:false, fog:true, side:THREE.DoubleSide, polygonOffset:true, polygonOffsetFactor:-2, polygonOffsetUnits:-2,
    uniforms:Object.assign({map:{value:turfAtlas()},uTime:TOONU.uTime},THREE.UniformsLib.fog),
    vertexShader:`attribute float aOld; attribute float aNew; attribute float aProg; varying vec2 vUv; varying float vOld,vNew,vProg;
      #include <fog_pars_vertex>
      void main(){ vUv=uv; vOld=aOld; vNew=aNew; vProg=aProg; vec4 mvPosition=modelViewMatrix*instanceMatrix*vec4(position,1.); gl_Position=projectionMatrix*mvPosition;
      #include <fog_vertex>
      }`,
    fragmentShader:`uniform sampler2D map; uniform float uTime; varying vec2 vUv; varying float vOld,vNew,vProg;
      #include <fog_pars_fragment>
      float h(vec2 p){ return fract(sin(dot(p,vec2(12.9898,78.233)))*43758.5453); }
      vec4 tile(float t){ if(t<0.) return vec4(0.); float c=mod(t,8.), r=floor(t/8.); return texture2D(map,vec2((c+vUv.x)/8.,1.-(r+1.-vUv.y)/4.)); }
      void main(){ float n=h(floor(vUv*vec2(48.,24.))); float rev=step(vUv.x+n*.18,vProg*1.2); vec4 a=tile(vOld), b=tile(vNew); vec4 c=mix(a,b,rev);
        if(vProg<1.&&vProg>0.&&abs(vUv.x+n*.18-vProg*1.2)<.04) c=vec4(b.rgb*1.6+.2,1.); if(c.a<.5) discard; gl_FragColor=vec4(c.rgb*1.15,1.);
        #include <fog_fragment>
      }` });
  const mesh=new THREE.InstancedMesh(geo,mat,N); mesh.frustumCulled=false; mesh.userData.noMerge=true; const m4=new THREE.Matrix4(), q4=new THREE.Quaternion(), e=new THREE.Euler(), s1=new THREE.Vector3(1,1,1), p=new THREE.Vector3();
  TURF.spots.forEach((s,i)=>{ s.i=i; s.y=s.piece?2.6:2.2; p.set(s.x,s.y,s.z); q4.setFromEuler(e.set(0,Math.atan2(s.nx,s.nz),0)); m4.compose(p,q4,s1); mesh.setMatrixAt(i,m4); });
  TURF.mesh=mesh; TURF.attr={aOld,aNew,aProg}; scene.add(mesh);
  turfLoad(); TURF.spots.forEach(turfPaint); TURF.ready=true; turfHUD(); }
function turfTile(s,owner){ return owner<0?-1:(s.piece?owner+8*(1+s.seg):owner); }
function turfPaint(s){ const A=TURF.attr; A.aOld.array[s.i]=turfTile(s,s.prevOwner??s.owner); A.aNew.array[s.i]=turfTile(s,s.sprayFor??s.owner); A.aProg.array[s.i]=s.sprayFor!==undefined?s.prog:1; A.aOld.needsUpdate=A.aNew.needsUpdate=A.aProg.needsUpdate=true; }
function turfSave(){ try{ const own={}; for(const s of TURF.spots) own[s.id]=s.owner>=0?TURF.crews[s.owner].id:null; localStorage.setItem(TURF.key,JSON.stringify({t:Date.now(),own})); }catch(e){} }
function turfLoad(){ let d=null; try{ d=JSON.parse(localStorage.getItem(TURF.key)||"null"); }catch(e){} if(!d||!d.own) return;
  const idx=id=>TURF.crews.findIndex(c=>c.id===id); for(const s of TURF.spots) if(s.id in d.own) s.owner=d.own[s.id]?idx(d.own[s.id]):-1;
  const away=(TQ.get("turfAway")!==null?+TQ.get("turfAway"):(Date.now()-d.t)/60000); // minutes away (?turfAway=N simulates)
  const k=Math.min(3,Math.floor(away/30)); if(k<=0) return; const lost=[];
  for(const key in TURF.dist){ const D=TURF.dist[key], mine=D.spots.filter(s=>s.owner===TURF.me); const n=Math.min(k,mine.length); for(let i=0;i<n;i++) mine[mine.length-1-i].owner=D.rival; if(n) lost.push([n,D]); }
  if(lost.length){ lost.sort((a,b)=>b[0]-a[0]); const [n,D]=lost[0]; const tc=s=>s.toLowerCase().replace(/(^|[\s·])(\w)/g,(m,a,b)=>a+b.toUpperCase());
    const more=lost.slice(1).reduce((a,b)=>a+b[0],0); TURF.welcome=`Welcome back — ${TURF.crews[D.rival].name} took ${n} spot${n>1?"s":""} in ${tc(D.name)}`+(more?` · rivals took ${more} more elsewhere`:""); TURF.welcomeT=6; } turfSave(); }
function turfPct(D){ return D.spots.length?Math.round(100*D.spots.filter(s=>s.owner===TURF.me).length/D.spots.length):0; }
function turfHUD(){ const el=$("turf"); if(!el||!TURF.ready) return; const q=turfDistrict(Ride.group.position.x,Ride.group.position.z), D=q&&TURF.dist[q.name], me=TURF.crews[TURF.me];
  const all=TURF.spots.length, mine=TURF.spots.filter(s=>s.owner===TURF.me).length;
  el.innerHTML=D?`<div class="tn">${D.name}</div><div class="tb"><i style="width:${turfPct(D)}%;background:${me.css}"></i></div><div class="tp" style="color:${me.css}">${me.name.toUpperCase()} ${turfPct(D)}%</div><div class="tr">RIVAL · <span style="color:${TURF.crews[D.rival].css}">${TURF.crews[D.rival].name.toUpperCase()}</span> ${Math.round(100*D.spots.filter(s=>s.owner===D.rival).length/D.spots.length)}%</div>`
    :`<div class="tn">PALMA CITY</div><div class="tp" style="color:${me.css}">TURF ${Math.round(100*mine/all)}%</div>`; }
function turfUpdate(dt){ if(!TURF.ready) return; const p=Ride.group.position, me=TURF.me; let best=null, bd=4.6;
  if(State.mode==="ride"&&Input.tag){ for(const s of TURF.spots){ if(s.owner===me) continue; const dx=p.x-s.x, dz=p.z-s.z, d=Math.hypot(dx,dz); if(d>bd||dx*s.nx+dz*s.nz<0) continue;
      if(s.piece&&s.seg>0&&s.piece.segs[s.seg-1].owner!==me) continue; best=s; bd=d; } }
  if(best){ if(best.sprayFor===undefined){ best.prevOwner=best.owner; best.sprayFor=me; best.prog=0; }
    best.prog=Math.min(1,best.prog+dt/(best.piece?.3:.4)); TURF.sprayT=.15;
    if(frame%2===0){ const c=TURF.crews[me].hex; for(let k=0;k<3;k++){ _v.set(p.x,1.3,p.z); emit(_v,c,(best.x-p.x)*1.4+rnd(-.6,.6),(best.y-1.3)*1.4+rnd(-.3,.6),(best.z-p.z)*1.4+rnd(-.6,.6),.45); } }
    if(best.prog>=1){ best.owner=me; delete best.sprayFor; delete best.prevOwner; Stats.tags++; bumpChain(); DASH.meter=Math.min(1,DASH.meter+.12); TURF.dirty=true;
      if(best.piece&&best.seg===2&&best.piece.segs.every(s=>s.owner===me)){ flash("BIG PIECE!",TURF.crews[me].css); DASH.meter=Math.min(1,DASH.meter+.25); } else flash(best.piece?"PIECE "+(best.seg+1)+"/3":"TAGGED",TURF.crews[me].css); turfHUD(); }
    turfPaint(best); }
  if(TURF.dirty&&(TURF.saveT-=dt)<=0){ turfSave(); TURF.dirty=false; TURF.saveT=1; }
  if(frame%20===0) turfHUD();
  const w=$("welcome"); if(TURF.welcomeT>0&&State.mode==="ride"){ TURF.welcomeT-=dt; w.textContent=TURF.welcome; w.style.opacity=Math.min(1,TURF.welcomeT); } else if(w) w.style.opacity=0; }
function turfMinimap(){ if(!TURF.ready) return; const x=mm, S=180, sc=S/170, p=Ride.group.position;
  for(const s of TURF.spots){ const X=S/2+(s.x-p.x)*sc, Y=S/2+(s.z-p.z)*sc; if(X<2||Y<2||X>S-2||Y>S-2) continue; x.fillStyle=s.owner<0?"#555":TURF.crews[s.owner].css; x.fillRect(X-2,Y-2,4,4); if(s.owner===TURF.me){ x.strokeStyle="#fff"; x.lineWidth=1; x.strokeRect(X-2.5,Y-2.5,5,5); } }
  const q=turfDistrict(p.x,p.z), D=q&&TURF.dist[q.name]; if(D){ const pc=turfPct(D); x.fillStyle="rgba(0,0,0,.65)"; x.fillRect(0,S-18,S,18); x.fillStyle=TURF.crews[TURF.me].css; x.fillRect(0,S-3,S*pc/100,3); x.font="bold 11px Arial"; x.fillText(D.name.slice(0,20)+"  "+pc+"%",5,S-6); } }

// ---- BOOST DASH ----
const DASH={ meter:.5, t:0, rip:9, fx:0, pass:null, trail:null, hist:[] };
const DashShader={ uniforms:{tDiffuse:{value:null},uBlur:{value:0},uRip:{value:9},uRipA:{value:0},uC:{value:new THREE.Vector2(.5,.55)},uTint:{value:new THREE.Color(0xffd700)}},
  vertexShader:`varying vec2 vUv; void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
  fragmentShader:`uniform sampler2D tDiffuse; uniform float uBlur,uRip,uRipA; uniform vec2 uC; uniform vec3 uTint; varying vec2 vUv;
    void main(){ vec2 d=vUv-uC; float r=length(d); vec2 dir=r>0.?d/r:vec2(0.);
      float ring=exp(-pow((r-uRip)*14.,2.))*uRipA; vec2 uv=vUv-dir*ring*.035;                       // shockwave ripple
      vec3 c=vec3(0.); float k=uBlur*smoothstep(.08,.6,r); for(int i=0;i<10;i++){ c+=texture2D(tDiffuse,uv-d*k*float(i)*.012).rgb; } c/=10.; // radial blur
      c+=uTint*ring*.35; gl_FragColor=vec4(c,1.); }` };
function dashInit(){ const N=24, g=new THREE.BufferGeometry(); g.setAttribute("position",new THREE.BufferAttribute(new Float32Array(2*N*2*3),3).setUsage(THREE.DynamicDrawUsage)); const a=new Float32Array(2*N*2);
  const idx=[]; for(let r=0;r<2;r++) for(let i=0;i<N-1;i++){ const o=r*N*2+i*2; idx.push(o,o+1,o+2,o+1,o+3,o+2); } g.setIndex(idx);
  for(let r=0;r<2;r++) for(let i=0;i<N;i++){ a[r*N*2+i*2]=a[r*N*2+i*2+1]=1-i/(N-1); } g.setAttribute("aA",new THREE.BufferAttribute(a,1));
  const m=new THREE.ShaderMaterial({ transparent:true, depthWrite:false, blending:THREE.AdditiveBlending, side:THREE.DoubleSide, uniforms:{uC:{value:new THREE.Color(0xffd700)},uK:{value:0}},
    vertexShader:`attribute float aA; varying float vA; void main(){ vA=aA; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
    fragmentShader:`uniform vec3 uC; uniform float uK; varying float vA; void main(){ gl_FragColor=vec4(uC*vA*vA*uK*1.6,1.); }` });
  const mesh=new THREE.Mesh(g,m); mesh.frustumCulled=false; mesh.visible=false; mesh.userData.noMerge=true; scene.add(mesh); DASH.trail=mesh; DASH.N=N; }
function dashUpdate(dt){ if(!DASH.trail) dashInit(); const R=Ride, xr=renderer.xr.isPresenting, col=TURF.ready?TURF.crews[TURF.me].hex:0xffd700;
  if(R.grinding) DASH.meter=Math.min(1,DASH.meter+dt*.16); if(Stats.cans!==DASH.cans){ if(DASH.cans!==undefined) DASH.meter=Math.min(1,DASH.meter+.06); DASH.cans=Stats.cans; }
  if(State.mode==="ride"&&Input.pDash&&DASH.meter>=.33&&DASH.t<=0){ DASH.meter-=.33; DASH.t=.75; DASH.rip=0; R.speed=Math.max(R.speed+10,R.maxSpeed*1.45); flash("BOOST DASH",TURF.ready?TURF.crews[TURF.me].css:"#FFD700"); }
  if(Input.boost&&DASH.t<=0&&Input.mag>0) DASH.meter=Math.max(0,DASH.meter-dt*.12);
  DASH.t=Math.max(0,DASH.t-dt); DASH.rip+=dt*1.6; DASH.fx=THREE.MathUtils.lerp(DASH.fx,DASH.t>0?1:0,1-Math.exp(-dt*(DASH.t>0?14:3)));
  // post pass: radial blur + ripple (2D only — never in XR)
  if(DASH.pass){ const on=!xr&&(DASH.fx>.02||DASH.rip<.9); DASH.pass.enabled=on; const u=DASH.pass.uniforms; u.uBlur.value=DASH.fx; u.uRip.value=DASH.rip; u.uRipA.value=Math.max(0,1-DASH.rip/.9); u.uTint.value.setHex(col); }
  const dl=$("dashlines"); if(dl) dl.style.opacity=xr?0:DASH.fx*.9;
  const dm=$("dashm"); if(dm){ dm.style.width=(DASH.meter*100).toFixed(0)+"%"; dm.style.background=TURF.ready?TURF.crews[TURF.me].css:"#FFD700"; }
  // world-space crew streak ribbons (also in VR)
  const T=DASH.trail, N=DASH.N, p=R.group.position, sx=Math.cos(R.yaw), sz=-Math.sin(R.yaw); DASH.hist.unshift([p.x,p.y,p.z]); if(DASH.hist.length>N) DASH.hist.length=N;
  T.visible=DASH.fx>.02&&!window.TRAILS; T.material.uniforms.uK.value=DASH.fx; T.material.uniforms.uC.value.setHex(col);
  if(T.visible){ const A=T.geometry.attributes.position.array; for(let r=0;r<2;r++){ const side=r?.28:-.28; for(let i=0;i<N;i++){ const h=DASH.hist[Math.min(i,DASH.hist.length-1)], o=(r*N*2+i*2)*3, w=.07*(1-i/N);
        const bx=h[0]+sx*side, bz=h[2]+sz*side, by=h[1]+.95+(r?.1:0); A[o]=bx; A[o+1]=by+w; A[o+2]=bz; A[o+3]=bx; A[o+4]=by-w; A[o+5]=bz; } } T.geometry.attributes.position.needsUpdate=true; } }
