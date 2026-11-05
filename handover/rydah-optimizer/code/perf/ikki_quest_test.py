from playwright.sync_api import sync_playwright
import time,json,sys
B="http://localhost:8793/v3build/perf/sky-rydahs-v3-ikki-quest.html?chars=/skyrydahs-characters/&player=ikki&ikki=/skyrydahs-characters/meshy/"
V=[sys.argv[1]]
O="/workspace/v3build/perf/shots/"; res={}
CAMS=[("body",0,2.6,1.1,.9),("face",0,.75,1.62,1.55),("face34",.75,.75,1.62,1.55),("skates",.6,1.0,.35,.1)]
with sync_playwright() as p:
  b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
  for v in V:
    tag=v.replace("ikki-meshy-skate","").replace(".glb","").strip(".") or "orig"
    pg=b.new_page(viewport={"width":1000,"height":800}); pg.set_default_timeout(150000); errs=[]
    pg.on("console",lambda m: errs.append(m.text) if m.type in("error","warning") else None); pg.on("pageerror",lambda e: errs.append("PAGEERROR "+str(e)))
    t0=time.time(); pg.goto(B+v,timeout=120000)
    for i in range(150):
      if pg.evaluate("typeof RIDERS!='undefined'&&RIDERS.ready"): break
      time.sleep(1)
    load=time.time()-t0; time.sleep(3)
    for k in range(6):
      if pg.evaluate("State.mode")=="ride": break
      pg.keyboard.press("Enter"); time.sleep(2)
    r={"load_s_to_ready":round(load,1)}
    r["errors_at_ready"]=[e[:200] for e in errs if "ikki" in e.lower() or "draco" in e.lower() or "PAGEERROR" in e][:6]; json.dump(r,open(f"/workspace/v3build/perf/results-{tag}.partial.json","w"))
    r["ikki"]=pg.evaluate("""(()=>{let tris=[],mats=new Set(),tex=new Set(),sk=0,name='';const P=RIDERS.player;if(!P)return null;P.traverse(o=>{if(o.isMesh){const g=o.geometry;tris.push([o.name,(g.index?g.index.count:g.attributes.position.count)/3]);if(o.isSkinnedMesh)sk++;const m=o.material;(Array.isArray(m)?m:[m]).forEach(mm=>{mats.add(mm.uuid);for(const k in mm){const t=mm[k];if(t&&t.isTexture&&t.image)tex.add(k+':'+t.image.width+'x'+t.image.height)}; if(mm.uniforms)for(const k in mm.uniforms){const t=mm.uniforms[k].value;if(t&&t.isTexture&&t.image)tex.add(k+':'+t.image.width+'x'+t.image.height)}})}});return {meshes:tris,skinned:sk,materials:mats.size,textures:[...tex],isIkki:!!P.userData.setState}})()""")
    pg.evaluate("window.__hideIkkiNpc=true; Ride.group.position.set(-6,0,40); Ride.yaw=Math.PI; Ride.speed=0; RIDERS.player.userData.setState&&RIDERS.player.userData.setState('idle')")
    for nm,ang,d,cy,ly in CAMS:
      pg.evaluate(f"(()=>{{const p=Ride.group.position;window.__camHook=()=>{{Ride.group.position.set(-6,0,40);const y=Ride.yaw+{ang};camera.position.set(p.x+Math.sin(y)*{d},{cy},p.z+Math.cos(y)*{d});camera.lookAt(p.x,{ly},p.z)}}}})()"); time.sleep(1.5); pg.screenshot(path=O+f"{tag}_{nm}.png")
      if nm=="body":
        r["renderer_info_body_view"]=pg.evaluate("({calls:renderer.info.render.calls,triangles:renderer.info.render.triangles,textures:renderer.info.memory.textures,geometries:renderer.info.memory.geometries,programs:renderer.info.programs.length})")
    pg.set_viewport_size({"width":1832,"height":1920}); time.sleep(2)
    r["frame_ms_1832x1920_body_view_10frames"]=pg.evaluate("new Promise(res=>{let n=0,t0=performance.now();function f(){if(++n<10)requestAnimationFrame(f);else res((performance.now()-t0)/10)}requestAnimationFrame(f)})")
    pass
    res[tag]=r; print(tag,json.dumps(r)); sys.stdout.flush(); pg.close()
  b.close()
json.dump(res,open(f"/workspace/v3build/perf/results-{tag}.json","w"),indent=1)
