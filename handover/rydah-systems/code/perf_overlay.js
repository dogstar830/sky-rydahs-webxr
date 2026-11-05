// ===== ?perf=1 QUEST PERF OVERLAY (perf_overlay.js, Rydah Systems) — thin HUD on Rydah Optimizer's DC_METER (perf/drawcalls/dc_meter.js).
// Shows frame ms (last, rolling avg over 120 frames, p95), draw calls by the LOCKED metric = renderer.info.render.calls of the
// main scene render only (post-processing passes excluded, measured as call deltas around renderer.render(scene,…)), triangles,
// textures (renderer.info.memory.textures + est. MB of unique scene textures), and DC_METER's world/chars/fx split (1 Hz).
// Desktop: DOM panel (0 WebGL draws). WebXR: one head-locked CanvasTexture quad (1 draw, excluded from the shown count).
// Without ?perf nothing is created or hooked (0 draws, 0 cost). Coexists with ?fps (FPSO): FPSO's DOM box is hidden when ?perf is on.
(function(){
const on=/[?&]perf=1\b/.test(location.search); window.PERF={on};
if(!on) return;
const P=window.PERF; Object.assign(P,{ms:[],last:0,sceneCalls:0,sceneTris:0,frameCalls:0,frameTris:0,stat:null,acc:0,dcAcc:9,split:null,texMB:0,texN:0,dom:null,cv:null,tex:null,mesh:null});
// LOCKED metric: count only renderer.render(scene,…) (RenderPass or direct); composer/post quads use other scenes.
// Texture memory (Rydah Optimizer audit perf/texmem/audit.md): only GPU-uploaded textures (renderer.properties __webglTexture),
// incl. ShaderMaterial/RawShaderMaterial uniform textures (and arrays), dedup by uuid, real bytes/px per format, mips x1.33 only when present.
function texBpp(t){ const F=t.format, C=THREE; if(!t.isCompressedTexture) return (t.type===C.FloatType?16:t.type===C.HalfFloatType?8:1)*(F===C.RGBFormat?4:F===C.RedFormat||F===C.LuminanceFormat||F===C.AlphaFormat?1:F===C.RGFormat||F===C.LuminanceAlphaFormat?2:4);
  const n=(Object.keys(C).find(k=>C[k]===F&&/Format$/.test(k))||"");
  if(/RGB_ETC1|RGB_ETC2|RGB_S3TC_DXT1|RGBA_S3TC_DXT1|RGB_PVRTC_4|RGBA_PVRTC_4/.test(n)) return .5; if(/PVRTC_2/.test(n)) return .25;
  if(/RGBA_ETC2_EAC|RGBA_ASTC_4x4|RGBA_BPTC|DXT3|DXT5/.test(n)) return 1; const a=n.match(/ASTC_(\d+)x(\d+)/); if(a) return 16/(+a[1]*+a[2]); return 1; }
function texMem(){ const seen=new Map(); const add=t=>{ if(t&&t.isTexture&&!seen.has(t.uuid)) seen.set(t.uuid,t); };
  scene.traverse(o=>{ const ms=o.material?(Array.isArray(o.material)?o.material:[o.material]):[]; for(const m of ms){ if(!m) continue; for(const k in m) add(m[k]);
    if(m.uniforms) for(const k in m.uniforms){ const v=m.uniforms[k]&&m.uniforms[k].value; if(Array.isArray(v)) v.forEach(add); else add(v); } } });
  let b=0, up=0, sk=0; for(const t of seen.values()){ let gl=false; try{ gl=!!renderer.properties.get(t).__webglTexture; }catch(e){} if(!gl){ sk++; continue; } up++;
    const im=t.isCompressedTexture?(t.mipmaps&&t.mipmaps[0])||t.image:(t.image||{}); const w=im.width||im.videoWidth||0, h=im.height||im.videoHeight||0;
    const mip=t.isCompressedTexture?(t.mipmaps&&t.mipmaps.length>1):(t.generateMipmaps!==false&&t.minFilter!==THREE.LinearFilter&&t.minFilter!==THREE.NearestFilter)||(t.mipmaps&&t.mipmaps.length>1);
    b+=w*h*texBpp(t)*(mip?1.333:1); }
  P.texN=up; P.texSkipped=sk; P.texMB=b/1048576; return {mb:P.texMB,uploaded:up,skipped:sk,gl:renderer.info.memory.textures}; }
P.texMem=texMem;
function build(){ const _render=renderer.render.bind(renderer);  // hooked lazily (renderer exists by the first tick)
  renderer.render=function(s,c){ const i=renderer.info.render, c0=i.calls, t0=i.triangles; const r=_render(s,c); if(s===scene){ P.frameCalls+=i.calls-c0; P.frameTris+=i.triangles-t0; } return r; };
  const d=document.createElement("div"); d.id="perfOverlay"; d.className="hud";
  d.style.cssText="position:fixed;left:12px;bottom:12px;z-index:31;pointer-events:none;font:600 12px/1.35 Consolas,monospace;color:#F5F2E8;background:rgba(5,8,16,.8);padding:6px 9px;border-radius:8px;white-space:pre";
  document.body.appendChild(d); P.dom=d;
  const c=document.createElement("canvas"); c.width=320; c.height=176; P.cv=c; P.tex=new THREE.CanvasTexture(c); P.tex.minFilter=THREE.LinearFilter; P.tex.generateMipmaps=false;
  P.mesh=new THREE.Mesh(new THREE.PlaneGeometry(.2,.11),new THREE.MeshBasicMaterial({map:P.tex,transparent:true,depthTest:false,depthWrite:false,fog:false,toneMapped:false}));
  P.mesh.renderOrder=1001; P.mesh.position.set(.17,-.13,-.5); P.mesh.visible=false; P.mesh.name="perf_overlay_xr"; camera.add(P.mesh); }
function lines(){ const s=P.stat; if(!s) return ["PERF …"]; const sp=P.split;
  return [`frame ${s.ms.toFixed(1)} ms  avg ${s.avg.toFixed(1)}  p95 ${s.p95.toFixed(1)}  (${(1000/s.avg).toFixed(0)} fps)`,
    `draws ${s.calls}  (scene only, post-FX excluded) / 150`, `tris ${(s.tris/1000).toFixed(1)}k`,
    `textures ${s.texGL} GL · ~${P.texMB.toFixed(1)} MB (${P.texN} uploaded)`, sp?`DC_METER world ${sp.world} · chars ${sp.chars} · fx ${sp.fx}`:"DC_METER n/a"].concat(window.__TEXSHARE?[`texshare ${(+window.__TEXSHARE.ms||0).toFixed(1)} ms / ${((+window.__TEXSHARE.savedBytes||0)/1048576).toFixed(1)} MB saved`]:[]); }
function paintXR(){ const x=P.cv.getContext("2d"); x.clearRect(0,0,320,176); x.fillStyle="rgba(5,8,16,.82)"; x.fillRect(0,0,320,176);
  x.font="600 15px Consolas,monospace"; const L=lines(); L.forEach((l,i)=>{ x.fillStyle=i===1&&P.stat&&P.stat.calls>150?"#FF3344":"#F5F2E8"; x.fillText(l.slice(0,38),8,24+i*26); }); P.tex.needsUpdate=true; }
window.perfTick=function(dt,xr){ try{ if(!P.dom) build(); const now=performance.now(); if(P.last) { P.ms.push(now-P.last); if(P.ms.length>120) P.ms.shift(); } P.last=now;
  const inXR=!!(xr&&renderer.xr.isPresenting); P.mesh.visible=inXR; P.dom.style.display=inXR?"none":""; if(window.FPSO&&FPSO.dom) FPSO.dom.style.display="none";
  // previous frame's scene-only counts (this tick runs before this frame's render); own XR quad excluded
  P.sceneCalls=Math.max(0,P.frameCalls-(P.mesh.visible?1:0)); P.sceneTris=P.frameTris; P.frameCalls=0; P.frameTris=0;
  P.acc+=dt; P.dcAcc+=dt;
  if(P.dcAcc>=1){ P.dcAcc=0; try{ texMem(); if(window.DC_METER){ const e=DC_METER.estimate(); P.split={chars:e.cls.chars,fx:e.cls.fx,world:Math.max(0,P.sceneCalls-e.cls.chars-e.cls.fx)}; } }catch(e){} }
  if(P.acc<.25) return; P.acc=0; const a=P.ms.slice().sort((p,q)=>p-q), n=a.length; if(!n) return;
  P.stat={ms:P.ms[P.ms.length-1],avg:a.reduce((s,v)=>s+v,0)/n,p95:a[Math.min(n-1,Math.floor(n*.95))],calls:P.sceneCalls,tris:P.sceneTris,texGL:renderer.info.memory.textures};
  if(inXR) paintXR(); else P.dom.textContent=lines().join("\n"); }catch(e){ console.warn("perf overlay",e); window.perfTick=null; } };
})();
