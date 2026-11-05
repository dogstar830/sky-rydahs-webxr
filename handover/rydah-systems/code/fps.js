// ===== ?fps performance overlay: FPS (1 s avg + min), frame ms, draw calls, triangles. Desktop: DOM canvas bottom-right. WebXR: head-locked panel (tiny CanvasTexture, ~4 Hz).
const FPSO={ on:/[?&]fps\b/.test(location.search), cv:null, tex:null, mesh:null, dom:null, acc:0, frames:[], last:0, calls:0, tris:0 };
function fpsBuild(){ const c=document.createElement("canvas"); c.width=256; c.height=96; FPSO.cv=c;
  c.id="fpsOverlay"; c.style.cssText="position:fixed;right:12px;bottom:12px;width:192px;height:72px;z-index:30;pointer-events:none;border-radius:8px"; document.body.appendChild(c); FPSO.dom=c;
  const c2=document.createElement("canvas"); c2.width=256; c2.height=96; FPSO.cv2=c2; FPSO.tex=new THREE.CanvasTexture(c2); FPSO.tex.minFilter=THREE.LinearFilter; FPSO.tex.generateMipmaps=false;
  FPSO.mesh=new THREE.Mesh(new THREE.PlaneGeometry(.16,.06),new THREE.MeshBasicMaterial({map:FPSO.tex,transparent:true,depthTest:false,depthWrite:false,fog:false})); FPSO.mesh.renderOrder=1000; FPSO.mesh.position.set(-.17,-.15,-.5); FPSO.mesh.visible=false; camera.add(FPSO.mesh);
  renderer.info.autoReset=false; }
function fpsPaint(c,t){ const x=c.getContext("2d"); x.clearRect(0,0,256,96); x.fillStyle="rgba(5,8,16,.78)"; x.beginPath(); x.moveTo(10,0); x.arcTo(256,0,256,96,10); x.arcTo(256,96,0,96,10); x.arcTo(0,96,0,0,10); x.arcTo(0,0,256,0,10); x.fill();
  x.font="800 26px 'Segoe UI',Arial,sans-serif"; x.fillStyle=t.avg>=70?"#7CFFB2":t.avg>=50?"#FFD700":"#FF3344"; x.fillText(t.avg.toFixed(0)+" FPS",12,32); x.font="600 18px 'Segoe UI',Arial,sans-serif"; x.fillStyle="#F5F2E8";
  x.fillText("min "+t.min.toFixed(0)+" · "+t.ms.toFixed(1)+" ms",128,30); x.fillText("calls "+t.calls+"   tris "+(t.tris>=1e3?(t.tris/1e3).toFixed(1)+"k":t.tris),12,70); }
function fpsTick(dt,xr){ if(!FPSO.on) return; if(!FPSO.cv) fpsBuild(); const now=performance.now();
  // renderer.info accumulates (autoReset off) across composer passes; sample then reset once per frame
  FPSO.calls=renderer.info.render.calls; FPSO.tris=renderer.info.render.triangles; renderer.info.reset();
  if(FPSO.last){ FPSO.frames.push([now,now-FPSO.last]); } FPSO.last=now; while(FPSO.frames.length&&FPSO.frames[0][0]<now-1000) FPSO.frames.shift();
  FPSO.acc+=dt; const inXR=!!(xr&&renderer.xr.isPresenting); FPSO.mesh.visible=inXR; FPSO.dom.style.display=inXR?"none":"";
  if(FPSO.acc<.25) return; FPSO.acc=0; const F=FPSO.frames, n=F.length; if(!n) return; const ms=F.reduce((a,f)=>a+f[1],0)/n, mx=Math.max(...F.map(f=>f[1]));
  const t={avg:1000/ms,min:1000/mx,ms,calls:FPSO.calls,tris:FPSO.tris}; FPSO.stat=t; if(inXR){ fpsPaint(FPSO.cv2,t); FPSO.tex.needsUpdate=true; } else fpsPaint(FPSO.cv,t); }
window.FPSO=FPSO; window.fpsTick=fpsTick;
