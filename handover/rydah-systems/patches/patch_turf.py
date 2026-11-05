import os as _os; _SRC=_os.environ.get('SR_SRC','/workspace/v3build').rstrip('/')+'/'; _OUT=_os.environ.get('SR_HTML','/workspace/v3build/sky-rydahs-v3-ikki.html')  # Systems 10:25: SR_HTML / SR_SRC (default = old paths)
f=_OUT; src=open(f).read(); js=open(_SRC+'turf_dash.js').read()
def rep(o,n,cnt=1):
    global src; assert o in src,o[:70]; src=src.replace(o,n,cnt)
rep("// ===== LOOP =====",js+"\n// ===== LOOP =====")
# HUD
rep('<div id="flash" class="hud">CHECKPOINT</div>','''<div id="flash" class="hud">CHECKPOINT</div>
<div id="turf" class="hud hidden"></div><div id="welcome" class="hud"></div><div id="dashlines" class="hud"></div>
<div id="dash" class="hud hidden"><span>BOOST</span><div><i id="dashm"></i><b></b><b></b></div></div>''')
rep('  .hidden{display:none}','''  #turf{top:62px;right:18px;min-width:190px;padding:8px 10px;background:rgba(10,10,10,.82);border-left:4px solid #FFD700;color:#fff;font:bold 12px Arial;letter-spacing:1px}
  #turf .tn{font-size:13px;color:#ddd} #turf .tb{height:6px;background:#333;margin:5px 0} #turf .tb i{display:block;height:100%} #turf .tp{font-size:15px} #turf .tr{font-size:10px;color:#aaa;margin-top:2px}
  #welcome{top:110px;left:50%;transform:translateX(-50%);padding:10px 18px;background:rgba(10,10,10,.85);border:2px solid #FFD700;color:#fff;font:bold 16px Arial;opacity:0;pointer-events:none;white-space:nowrap}
  #dashlines{inset:0;opacity:0;pointer-events:none;background:repeating-conic-gradient(from 0deg at 50% 55%,rgba(255,255,255,.0) 0deg 3deg,rgba(255,255,255,.22) 3.4deg 3.8deg);-webkit-mask:radial-gradient(circle at 50% 55%,transparent 28%,#000 70%);mask:radial-gradient(circle at 50% 55%,transparent 28%,#000 70%)}
  #dash{bottom:22px;left:130px;color:#fff;font:bold 12px Arial;letter-spacing:2px;display:flex;gap:8px;align-items:center} #dash.hidden{display:none} #dash div{position:relative;width:180px;height:10px;background:#222;border:2px solid #000} #dash i{position:absolute;left:0;top:0;bottom:0;background:#FFD700}
  #dash b{position:absolute;top:0;bottom:0;width:2px;background:#000} #dash b:nth-of-type(1){left:33%} #dash b:nth-of-type(2){left:66%}
  .hidden{display:none}''')
# show/hide with HUD: find setHud
import re
m=re.search(r'function setHud\(on\)\{[^\n]*',src); assert m, "setHud"
line=m.group(0); new=line.replace("function setHud(on){","function setHud(on){ for(const id of ['turf','dash']){ const e=document.getElementById(id); if(e) e.classList.toggle('hidden',!on); }",1)
src=src.replace(line,new,1)
# input
rep("const Input={ mag:0, yaw:0, boost:false };","const Input={ mag:0, yaw:0, boost:false, tag:false, pDash:false }; let _dashPrev=false;")
rep("  Input.boost=!!(k.ShiftLeft||k.ShiftRight);","  Input.boost=!!(k.ShiftLeft||k.ShiftRight); Input.tag=!!(k.KeyT||k.KeyF);")
rep("Input.boost=Input.boost||b(5)||b(7); }","Input.boost=Input.boost||b(4); Input.tag=Input.tag||b(5)||b(2); }\n  const ses=renderer&&renderer.xr&&renderer.xr.getSession&&renderer.xr.getSession(); if(ses) for(const s of ses.inputSources){ const g=s.gamepad; if(!g) continue; if(g.buttons[0]&&g.buttons[0].pressed) Input.tag=true; if(g.buttons[1]&&g.buttons[1].pressed) Input.boost=true; }\n  Input.pDash=Input.boost&&!_dashPrev; _dashPrev=Input.boost;")
# ride: boost needs meter; dash raises top speed
rep("R.boost=THREE.MathUtils.lerp(R.boost,Input.boost&&Input.mag>0?1:0,dt*6);","R.boost=THREE.MathUtils.lerp(R.boost,(Input.boost&&Input.mag>0&&DASH.meter>0)||DASH.t>0?1:0,dt*6);")
rep("const top=R.maxSpeed*(1+R.boost*.45)","const top=R.maxSpeed*(1+R.boost*.45)*(DASH.t>0?1.35:1)")
# loop hooks
rep("  updateRiders(dt); districtMood(dt);","  if(!TURF.ready&&frame>3&&colliders.length) try{ turfInit(); }catch(e){ console.warn('turf init failed',e); TURF.ready=false; TURF.fail=1; }\n  updateRiders(dt); districtMood(dt); turfUpdate(dt); dashUpdate(dt);")
rep("if(frame%2===0) drawMinimap();","if(frame%2===0){ drawMinimap(); turfMinimap(); }")
rep("VRV.material.opacity=Math.min(.95,k*THREE.MathUtils.clamp((sp-.35)*1.6+Ride.boost*.3,0,1));","VRV.material.opacity=Math.min(.95,k*THREE.MathUtils.clamp((sp-.35)*1.6+Ride.boost*.3+DASH.fx*.5,0,1)); if(DASH.fx>.05&&k===0){ VRV.visible=xr; VRV.material.opacity=DASH.fx*.35; }")
# FX pass
rep("cmp.addPass(new THREE.ShaderPass(GradeShader));","cmp.addPass(new THREE.ShaderPass(GradeShader)); DASH.pass=new THREE.ShaderPass(DashShader); DASH.pass.enabled=false; cmp.addPass(DASH.pass);")
# hints
src=src.replace("Stick / WASD to skate · hold RB / Shift to boost","Stick / WASD to skate · Shift / LB boost dash · hold T / RB to tag walls")
src=src.replace("Grab cyan cans, roll over purple rings to bomb tags — chains raise top speed","Hold T / F / RB / X near a wall spot to tag it — take turf from rival crews")
# camera hook for tests
rep("  if(window.__fpcam&&!xr){","  if(window.__camHook&&!xr) window.__camHook();\n  if(window.__fpcam&&!xr){")
# district kits: replace the instanced building builder
import re
kits=open(_SRC+'kits.js').read()
a=src.index('function buildInstancedBuildings(){'); b=src.index('  body.count=ib; glass.count=ig; scene.add(body,glass,hull,bands);\n}',a); b=src.index('}',b+60)+1
src=src[:a]+kits+src[b:]
bases=open(_SRC+'bases.js').read()
rep("// ===== LOOP =====",bases+"\n// ===== LOOP =====")
rep("  garages.push(Object.assign({},G,{th,cp:pc,dress:pdr,inside:false,inDress:false,group:g}));","  if(!/nobase/.test(location.search)) try{ dressBase(G,g,W,col2,col); }catch(e){ console.warn('base dress failed '+G.crew,e); }\n  garages.push(Object.assign({},G,{th,cp:pc,dress:pdr,inside:false,inDress:false,group:g}));")

# staticMerge: colour-agnostic batching (bake material colour to vertex colours) + 90 m tiles
rep('const k=o.material.uuid+"|"+names+"|"+Math.floor(_p.x/60)+"|"+Math.floor(_p.z/60);','const k=mergeKey(o.material,g)+"|"+names+"|"+Math.floor(_p.x/90)+"|"+Math.floor(_p.z/90);')
rep("const names=k.split(\"|\")[1].split(\",\"); const arrs={}; names.forEach(n=>arrs[n]=[]); const nm=new THREE.Matrix3();","const names=k.split(\"|\")[1].split(\",\"); const arrs={}; names.forEach(n=>arrs[n]=[]); const nm=new THREE.Matrix3(); const vc=k.startsWith('VC'), CA=[];")
rep("for(const o of L){ const g=o.geometry.index?o.geometry.toNonIndexed():o.geometry; nm.getNormalMatrix(o.matrixWorld);","for(const o of L){ const g=o.geometry.index?o.geometry.toNonIndexed():o.geometry; nm.getNormalMatrix(o.matrixWorld); if(vc){ const c=o.material.color; for(let i=0;i<g.attributes.position.count;i++) CA.push(c.r,c.g,c.b); }")
rep("geo.computeBoundingSphere();\n      const m=new THREE.Mesh(geo,L[0].material);","if(vc) geo.setAttribute('color',new THREE.Float32BufferAttribute(CA,3)); geo.computeBoundingSphere();\n      const m=new THREE.Mesh(geo,vc?vcMat(L[0].material):L[0].material);")
rep("function staticMerge(){",r"""const _vcm={};
function mergeKey(m,g){ if(g.attributes.color||m.map||m.transparent||m.vertexColors||m===inkMat||!(m.isMeshToonMaterial||m.isMeshBasicMaterial)||m.side!==THREE.FrontSide) return m.uuid;
  return m.isMeshBasicMaterial?'VCB':'VCT'+JSON.stringify(m.userData.polish||null)+(m.emissive?m.emissive.getHex():0)+(m.gradientMap?m.gradientMap.uuid:''); }
function vcMat(m){ const k=mergeKey(m,{attributes:{}}); if(_vcm[k]) return _vcm[k];
  const n=m.isMeshBasicMaterial?new THREE.MeshBasicMaterial({vertexColors:true,fog:m.fog}):patchToon(new THREE.MeshToonMaterial({gradientMap:m.gradientMap,vertexColors:true,emissive:m.emissive?m.emissive.clone():undefined}),m.userData.polish);
  return _vcm[k]=n; }
function staticMerge(){""")

# crew jackets: shared emblem atlas + per-rider recolour/back patch
jk=open(_SRC+'jackets.js').read()
rep("// ===== LOOP =====",jk+"\n// ===== LOOP =====")
rep("  parent.add(root); return root; }\n// procedural skate pose","  if(!/nojacket/.test(location.search)) try{ crewJacket(root,opts.crewName,fp); }catch(e){ console.warn('jacket failed',e); }\n  parent.add(root); return root; }\n// procedural skate pose")
open(f,'w').write(src)
