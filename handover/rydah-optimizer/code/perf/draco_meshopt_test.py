from playwright.sync_api import sync_playwright
import time,json,sys
O="/workspace/v3build/perf/shots/draco-meshopt/"
BUILT="http://localhost:8793/v3build/sky-rydahs-v3-ikki.html?chars=/skyrydahs-characters/&"
PWA="http://localhost:8793/sky-rydahs-pwa/site/index.html?"
RUNS=[("built_ikki",BUILT+"player=ikki"),("built_ikki_orig",BUILT+"player=ikki&ikki=orig"),("built_caali",BUILT+"player=caali&tier=quest"),
      ("pwa_ikki",PWA+"player=ikki"),("pwa_ikki_orig",PWA+"player=ikki&ikki=orig"),("pwa_caali",PWA+"player=caali&tier=quest")]
if len(sys.argv)>1: RUNS=[r for r in RUNS if r[0] in sys.argv[1:]]
CAMS=[("body",0,2.6,1.1,.9),("face",0,.75,1.62,1.55),("skates",.6,1.0,.35,.1)]
INFO="""(()=>{const out={};const one=P=>{if(!P)return null;let m=0,sk=0,vis=0,tris=0;P.traverse(o=>{if(o.isMesh){m++;if(o.isSkinnedMesh)sk++;let v=true,q=o;while(q){if(!q.visible)v=false;q=q.parent}if(v)vis++;const g=o.geometry;tris+=(g.index?g.index.count:g.attributes.position.count)/3}});return{meshes:m,skinned:sk,visible:vis,tris:Math.round(tris),wardrobe:!!P.userData.wardrobe,ikki:!!P.userData.setState}};
out.player=one(RIDERS.player);out.npcs=(RIDERS.npcs||[]).length;out.ikkiNpc=[];scene.traverse(o=>{if(o.userData&&o.userData.setState&&o!==RIDERS.player)out.ikkiNpc.push(one(o))});
out.wrap=!!window.SR_GLTF_WRAP;out.draco=!!window.SR_DRACO;out.meshopt=!!window.MeshoptDecoder;const L=new THREE.GLTFLoader();out.loaderHas={draco:!!L.dracoLoader,meshopt:!!L.meshoptDecoder};return out})()"""
res={}
with sync_playwright() as p:
  b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
  for tag,url in RUNS:
    ctx=b.new_context(viewport={"width":1000,"height":800}); pg=ctx.new_page(); pg.set_default_timeout(150000)
    errs=[];warns=[];net=[];failed=[]
    pg.on("console",lambda m:(errs if m.type=="error" else warns).append(m.text) if m.type in("error","warning") else None)
    pg.on("pageerror",lambda e:errs.append("PAGEERROR "+str(e)))
    pg.on("response",lambda r:net.append((r.status,r.url)))
    pg.on("requestfailed",lambda r:failed.append(r.url))
    t0=time.time(); pg.goto(url,timeout=120000)
    for i in range(170):
      if pg.evaluate("typeof RIDERS!='undefined'&&RIDERS.ready"): break
      time.sleep(1)
    r={"ready_s":round(time.time()-t0,1)}; time.sleep(3)
    for k in range(6):
      if pg.evaluate("State.mode")=="ride": break
      pg.keyboard.press("Enter"); time.sleep(2)
    r["info"]=pg.evaluate(INFO)
    pg.evaluate("window.__hideIkkiNpc=true; Ride.group.position.set(-6,0,40); Ride.yaw=Math.PI; Ride.speed=0; RIDERS.player&&RIDERS.player.userData.setState&&RIDERS.player.userData.setState('idle')")
    for nm,ang,d,cy,ly in CAMS:
      pg.evaluate(f"(()=>{{const p=Ride.group.position;window.__camHook=()=>{{Ride.group.position.set(-6,0,40);const y=Ride.yaw+{ang};camera.position.set(p.x+Math.sin(y)*{d},{cy},p.z+Math.cos(y)*{d});camera.lookAt(p.x,{ly},p.z)}}}})()"); time.sleep(1.5); pg.screenshot(path=O+f"{tag}_{nm}.png")
    if "pwa" in tag:
      time.sleep(4)
      r["sw"]=pg.evaluate("""(async()=>{const reg=await navigator.serviceWorker.getRegistration();const ks=await caches.keys();let c=[];for(const k of ks){const ca=await caches.open(k);c=c.concat((await ca.keys()).map(q=>q.url))}
        const need=['libs/draco/DRACOLoader.js','libs/draco/draco_wasm_wrapper.js','libs/draco/draco_decoder.wasm','libs/draco/draco_decoder.js','vendor/three/examples/js/libs/meshopt_decoder.js','ikki-meshy-skate.quest-draco.glb'];
        return {registered:!!reg,active:!!(reg&&reg.active),caches:ks,cached:c.length,missing:need.filter(n=>!c.some(u=>u.includes(n)))}})()""")
    keys=["quest-draco.glb","ikki-meshy-skate.glb","caali-g.glb","DRACOLoader.js","draco_wasm_wrapper","draco_decoder.wasm","draco_decoder.js","meshopt_decoder","GLTFLoader.js"]
    r["net"]={k:sorted({s for s,u in net if k in u}) for k in keys}
    r["errors"]=errs; r["error_count"]=len(errs); r["warnings"]=[w[:160] for w in warns][:8]; r["failed"]=failed[:10]; r["http_errors"]=[(s,u) for s,u in net if s>=400][:10]
    res[tag]=r; print(tag,json.dumps(r)); sys.stdout.flush(); ctx.close()
  b.close()
json.dump(res,open("/workspace/v3build/perf/results-draco-meshopt-"+"_".join(sys.argv[1:] or ["all"])+".json","w"),indent=1)
