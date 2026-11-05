# usage: python3 dcavg.py <html> <extra-query> <tag> : 3 fresh loads, seeded Math.random, &nofx, wait 6 s, DC_PROBE.run per view (day) -> averages
import sys,time,json,re
from playwright.sync_api import sync_playwright
H,Q,tag=sys.argv[1],sys.argv[2],sys.argv[3]; B=f"http://localhost:8765/v3build/{H}?chars=/skyrydahs-characters/&nofx{Q}"
SEED="(()=>{ let _s=123456789; Math.random=()=>{ _s^=_s<<13; _s^=_s>>>17; _s^=_s<<5; return ((_s>>>0)%1e9)/1e9; }; })()"
DAY="""(()=>{scene.traverse(o=>{if(o.isHemisphereLight){o.intensity=.85;o.color.set(0xcfe0ff);o.groundColor.set(0x6a6470);}});
scene.fog.color.set(0xb8c8e0);_fogBase.set(0xb8c8e0);scene.background.set(0x9ab8e0);if(typeof FACADE!=='undefined')FACADE.setDay(1);if(typeof BRIDGES!=='undefined')BRIDGES.setDay(1);})()"""
BR="""((id)=>{GRIND.on=null;const b=PALMA.bridges.find(q=>q.id===id),mx=(b.a[0]+b.b[0])/2,mz=(b.a[1]+b.b[1])/2,L=Math.hypot(b.b[0]-b.a[0],b.b[1]-b.a[1]),
 ux=(b.b[0]-b.a[0])/L,uz=(b.b[1]-b.a[1])/L,px=uz,pz=-ux; Ride.group.position.set(b.a[0]-ux*30,0,b.a[1]-uz*30);
 const V=[mx-px*L*.6+ux*L*.2,9,mz-pz*L*.6+uz*L*.2, mx,6,mz]; window.__camHook=()=>{camera.position.set(V[0],V[1],V[2]);camera.lookAt(V[3],V[4],V[5]);};})"""
V=[("causeway_west_day",BR+"('causeway')"),("b98_day",BR+"('b98')"),("aerial_day","GRIND.on=null;Ride.group.position.set(0,0,60);window.__camHook=()=>{camera.position.set(0,40,120);camera.lookAt(0,0,0)}"),
   ("street_day","GRIND.on=null;Ride.group.position.set(-60,0,-30);Ride.yaw=Math.PI;window.__camHook=()=>{camera.position.set(-59.2,1.7,-17);camera.lookAt(-60,6,-44);}")]
SPLIT="""(()=>{ const fr=new THREE.Frustum(); camera.updateMatrixWorld(true); fr.setFromProjectionMatrix(new THREE.Matrix4().multiplyMatrices(camera.projectionMatrix,camera.matrixWorldInverse));
 const C={world:0,chars:0,hud:0,fx:0}, top={}; const charRoot=o=>{ let a=o; while(a){ if(a.isSkinnedMesh||a===Ride.group||(a.userData&&(a.userData.npc||a.userData.rider))) return true; a=a.parent; } return false; };
 const skTop=new Set(); scene.traverse(o=>{ if(o.isSkinnedMesh){ let a=o; while(a.parent&&a.parent!==scene) a=a.parent; skTop.add(a); } });
 scene.traverseVisible(o=>{ if(!(o.isMesh||o.isLine||o.isPoints||o.isSprite)) return; if(o.frustumCulled!==false&&(o.isSprite?!fr.intersectsSprite(o):(o.geometry&&!fr.intersectsObject(o)))) return;
  if(o.isInstancedMesh&&o.count===0) return; const n=Array.isArray(o.material)?Math.max(1,(o.geometry.groups||[]).length):1;
  let a=o; while(a.parent&&a.parent!==scene&&a.parent!==camera) a=a.parent; let k;
  if(a.parent===camera||o.layers.mask===0) k="hud"; else if(skTop.has(a)||charRoot(o)) k="chars"; else if(o.isPoints||o.isSprite||(o.material&&o.material.blending===THREE.AdditiveBlending&&!o.userData.worldPerf&&!o.matrixAutoUpdate===false)) k="fx"; else k="world";
  C[k]+=n; if(k==="world"){ const t=(o.userData.worldPerf?"wp:"+o.userData.worldPerf:"")||o.name||(o.isInstancedMesh?"inst:"+(o.geometry.type):(o.matrixAutoUpdate===false?"merged":o.geometry&&o.geometry.type)); top[t]=(top[t]||0)+n; } });
 return {C,top:Object.entries(top).sort((a,b)=>b[1]-a[1]).slice(0,10)}; })()"""
R={}
with sync_playwright() as p:
    br=p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    for run in range(int(__import__("os").environ.get("RUNS","3"))):
        pg=br.new_page(viewport={"width":1280,"height":720}); errs=[]; pg.on("pageerror",lambda e: errs.append(str(e)[:200]))
        pg.add_init_script(SEED); pg.goto(B,timeout=180000); t0=time.time()
        while time.time()-t0<200:
            try:
                if pg.evaluate("typeof RIDERS!='undefined'&&RIDERS.ready&&window.GRAF&&GRAF.ready&&GRIND.world"): break
            except Exception: pass
            time.sleep(.5)
        time.sleep(6); pg.keyboard.press("Enter"); time.sleep(1.5)
        pg.evaluate("garages.forEach(g=>g.gate&&(g.gate.dismissed=true));if(typeof GATE!='undefined'){GATE.uiOpen=false;gateUI()};window.__npcPassive=true;window.__npcFreeze=true")
        pg.evaluate("new Promise(r=>{const s=document.createElement('script');s.src='perf/drawcalls/dc_probe.js';s.onload=r;document.head.appendChild(s);})"); pg.evaluate(DAY)
        for lab,js in V:
            pg.evaluate(js); time.sleep(2.5)
            r=pg.evaluate(f"(()=>{{ DC_PROBE.run('{lab}'); const s=DC_PROBE.last.sum; return [s.renderer_calls,s.estDraws,s.inkHullDraws]; }})()")+[pg.evaluate(SPLIT)]
            R.setdefault(lab,[]).append(r)
            if run==0: pg.screenshot(path=f"/workspace/v3build/shots/dcsplit_{tag}_{lab}.png")
        R.setdefault("errors",[]).extend(errs[:3]); R.setdefault("wp",[]).append(pg.evaluate("typeof WORLD_PERF!='undefined'?WORLD_PERF.stats:null")); pg.close()
    br.close()
out={k:(v if k in("errors","wp") else {"runs":v,"avg_calls":round(sum(x[0] for x in v)/len(v),1),"avg_est":round(sum(x[1] for x in v)/len(v),1),"split":{c:round(sum(x[3]["C"][c] for x in v)/len(v),1) for c in ("world","chars","hud","fx")},"top":v[0][3]["top"]}) for k,v in R.items()}
json.dump(out,open(f"/workspace/v3build/shots/dcsplit_{tag}.json","w"),indent=1); print(json.dumps({k:([v["avg_calls"],v["split"]] if isinstance(v,dict) else v) for k,v in out.items() if k!="wp"}))
