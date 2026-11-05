// ===== TRAILS: one pooled additive ring-buffer ribbon for ALL wheel light trails + the turf_dash.js dash streaks (Rydah Systems; Optimizer spec §4a) =====
// 1 mesh / 1 draw (drawRange = live trails only), MAXT trail slots x SEG points, rewritten per frame. Trails: player 2 skates, NPC riders within TR.NPC_R m
// (nearest first, 2 per rider), dash streaks (2) while DASH.fx > .02 (turf_dash.js hides its own ribbon when TRAILS exists). Camera-facing width, tapered tail,
// gold core -> pink/cyan/violet fringe (ref1 night FX). No textures. Debug/test: window.TRAILS.
const TR={ SEG:24, MAXT:8, NPC_R:12, mesh:null, slots:[], live:0, stats:{player:0,npc:0,dash:0}, minSp:3.5 };
window.TRAILS=TR;
function trBuild(){ const S=TR.SEG, T=TR.MAXT, V=T*S*2, g=new THREE.BufferGeometry();
  TR.pos=new Float32Array(V*3); TR.aux=new Float32Array(V*2); TR.col=new Float32Array(V*3);
  g.setAttribute("position",new THREE.BufferAttribute(TR.pos,3).setUsage(THREE.DynamicDrawUsage)); g.setAttribute("aux",new THREE.BufferAttribute(TR.aux,2).setUsage(THREE.DynamicDrawUsage));
  g.setAttribute("tcol",new THREE.BufferAttribute(TR.col,3).setUsage(THREE.DynamicDrawUsage));
  const I=[]; for(let t=0;t<T;t++) for(let i=0;i<S-1;i++){ const a=(t*S+i)*2; I.push(a,a+1,a+2,a+1,a+3,a+2); } g.setIndex(I); g.setDrawRange(0,0);
  const m=new THREE.ShaderMaterial({ transparent:true, depthWrite:false, blending:THREE.AdditiveBlending, side:THREE.DoubleSide, fog:false, uniforms:{ uCore:{value:new THREE.Color(0xffd27a)} },
    vertexShader:`attribute vec2 aux; attribute vec3 tcol; varying vec2 vA; varying vec3 vC; void main(){ vA=aux; vC=tcol; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
    fragmentShader:`uniform vec3 uCore; varying vec2 vA; varying vec3 vC; void main(){ float x=1.-abs(vA.y*2.-1.), a=1.-vA.x; a*=a; vec3 c=mix(vC,uCore,smoothstep(.45,1.,x)); gl_FragColor=vec4(c*x*a*1.4,1.); }` });
  const mesh=new THREE.Mesh(g,m); mesh.frustumCulled=false; mesh.renderOrder=9000; mesh.userData.noMerge=true; mesh.name="trails_ring"; mesh.visible=false; scene.add(mesh); TR.mesh=mesh; }
// slot = {key, hist: Float32Array(SEG*3) ring, n, head, w, col:[r,g,b], seen}
function trSlot(key,col,w){ let s=TR.slots.find(q=>q.key===key); if(!s){ if(TR.slots.length>=TR.MAXT){ const old=TR.slots.reduce((a,b)=>a.seen<b.seen?a:b); TR.slots.splice(TR.slots.indexOf(old),1); }
    s={key,hist:new Float32Array(TR.SEG*3),n:0,head:0,w,col}; TR.slots.push(s); } s.col=col; s.w=w; s.seen=frame; return s; }
function trPush(s,x,y,z){ const H=s.hist, h=s.head; if(s.n>0){ const o=((h-1+TR.SEG)%TR.SEG)*3; if(Math.hypot(H[o]-x,H[o+1]-y,H[o+2]-z)<.06) { H[o]=x;H[o+1]=y;H[o+2]=z; return; } }
  H[h*3]=x; H[h*3+1]=y; H[h*3+2]=z; s.head=(h+1)%TR.SEG; s.n=Math.min(TR.SEG,s.n+1); }
const _trC=new THREE.Color();
function trWheels(key,x,y,z,yaw,col,w){ const cx=Math.cos(yaw), cz=-Math.sin(yaw); for(const sd of [-1,1]) trPush(trSlot(key+(sd<0?"L":"R"),col,w),x+cx*.12*sd,y+.05,z+cz*.12*sd); }
function trailsTick(dt,xr){ if(!TR.mesh) trBuild(); const R=Ride, p=R.group.position; TR.stats={player:0,npc:0,dash:0};
  const crew=(typeof TURF!=="undefined"&&TURF.ready&&TURF.crews[TURF.me])?TURF.crews[TURF.me].hex:0xff4fd8;
  if(State.mode==="ride"&&(R.speed>TR.minSp||R.grinding||WALL.air)){ _trC.setHex(crew); trWheels("p",p.x,R.y||p.y,p.z,R.yaw,[_trC.r,_trC.g,_trC.b],.06); TR.stats.player=2; }
  // NPC riders within NPC_R (nearest 2 riders -> 4 trails), only while they move
  try{ const L=[]; for(const n of atkTargets()){ const q=n.holder.position, d=Math.hypot(q.x-p.x,q.z-p.z); if(d>TR.NPC_R) continue; const lp=n._trLast; const sp=lp?Math.hypot(q.x-lp.x,q.z-lp.z)/Math.max(dt,1e-3):0;
      n._trLast=(n._trLast||new THREE.Vector3()).copy(q); if(sp>.8) L.push([d,n]); }
    L.sort((a,b)=>a[0]-b[0]); for(const [d,n] of L.slice(0,2)){ const q=n.holder.position, c=_trC.set((n.g&&n.g.color)||"#7fe9ff"); trWheels("n"+(n.g?n.g.crew:n.id),q.x,q.y,q.z,n.holder.rotation.y,[c.r,c.g,c.b],.05); TR.stats.npc+=2; } }catch(e){}
  // dash streaks (turf_dash.js history), absorbed here
  if(typeof DASH!=="undefined"&&DASH.fx>.02&&DASH.hist&&DASH.hist.length){ _trC.setHex(crew); const h=DASH.hist[0], sx=Math.cos(R.yaw), sz=-Math.sin(R.yaw);
    for(let r=0;r<2;r++){ const side=r?.28:-.28; trPush(trSlot("d"+r,[_trC.r*DASH.fx,_trC.g*DASH.fx,_trC.b*DASH.fx],.07),h[0]+sx*side,h[1]+.95+(r?.1:0),h[2]+sz*side); } TR.stats.dash=2; }
  // drop slots not updated this frame (they fade by aging out over a few frames)
  for(const s of TR.slots) if(s.seen!==frame){ s.n=Math.max(0,s.n-3); }
  TR.slots=TR.slots.filter(s=>s.n>1||s.seen===frame);
  // write geometry: live slots packed into the first k slots
  const S=TR.SEG, P=TR.pos, A=TR.aux, C=TR.col, cam=camera.position; let k=0;
  for(const s of TR.slots){ if(s.n<2) continue; const H=s.hist; for(let i=0;i<S;i++){ const j=Math.min(i,s.n-1), o=((s.head-1-j+S*2)%S)*3, o2=((s.head-1-Math.min(j+1,s.n-1)+S*2)%S)*3;
      const x=H[o],y=H[o+1],z=H[o+2]; let tx=x-H[o2],ty=y-H[o2+1],tz=z-H[o2+2]; if(tx*tx+ty*ty+tz*tz<1e-8){ tx=1;ty=0;tz=0; }
      const vx=cam.x-x, vy=cam.y-y, vz=cam.z-z; let nx=ty*vz-tz*vy, ny=tz*vx-tx*vz, nz=tx*vy-ty*vx; const nl=Math.hypot(nx,ny,nz)||1, dist=Math.hypot(vx,vy,vz);
      const age=j/(S-1), w=s.w*(1-age)*Math.max(.4,Math.min(1,dist/2)); nx*=w/nl; ny*=w/nl; nz*=w/nl;
      const b=(k*S+i)*2; P.set([x-nx,y-ny,z-nz,x+nx,y+ny,z+nz],b*3); A.set([age,0,age,1],b*2); C.set([...s.col,...s.col],b*3); }
    if(++k>=TR.MAXT) break; }
  TR.live=k; const g=TR.mesh.geometry; g.setDrawRange(0,k*(S-1)*6); TR.mesh.visible=k>0;
  if(k){ g.attributes.position.needsUpdate=true; g.attributes.aux.needsUpdate=true; g.attributes.tcol.needsUpdate=true; } }
window.trailsTick=trailsTick;
