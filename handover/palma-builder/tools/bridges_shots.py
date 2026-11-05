# usage: python3 bridges_shots.py <before|after> -> shots/bridges_<tag>_<bridge>_<view>.png (+ _night/_day), draw calls json, grind cable fingerprint
import sys,time,json,math
from playwright.sync_api import sync_playwright
tag=sys.argv[1]; D="/workspace/v3build/shots/bridges_"
B="http://localhost:8765/v3build/sky-rydahs-v3-ikki.html?chars=/skyrydahs-characters/"
def waitfor(pg,e,t=150):
    t0=time.time()
    while time.time()-t0<t:
        if pg.evaluate(e): return True
        time.sleep(.2)
CALLS="""new Promise(res=>{renderer.info.autoReset=false;let n=0,mx=0;renderer.info.reset();function f(){mx=Math.max(mx,renderer.info.render.calls);renderer.info.reset();if(++n<8)requestAnimationFrame(f);else{renderer.info.autoReset=true;res(mx);}}requestAnimationFrame(f);})"""
FPS="new Promise(r=>{let n=0,t=performance.now();(function f(){if(++n<30)requestAnimationFrame(f);else r(Math.round(30000/(performance.now()-t)*10)/10)})()})"
DAY="""(()=>{scene.traverse(o=>{if(o.isHemisphereLight){o.intensity=.85;o.color.set(0xcfe0ff);o.groundColor.set(0x6a6470);}});
scene.fog.color.set(0xb8c8e0);_fogBase.set(0xb8c8e0);scene.background.set(0x9ab8e0);if(typeof FACADE!=='undefined')FACADE.setDay(1);if(typeof BRIDGES!=='undefined')BRIDGES.setDay(1);})()"""
CAM="""((id,v)=>{const b=PALMA.bridges.find(q=>q.id===id),mx=(b.a[0]+b.b[0])/2,mz=(b.a[1]+b.b[1])/2,L=Math.hypot(b.b[0]-b.a[0],b.b[1]-b.a[1]),
 ux=(b.b[0]-b.a[0])/L,uz=(b.b[1]-b.a[1])/L,px=uz,pz=-ux; Ride.group.position.set(b.a[0]-ux*30,0,b.a[1]-uz*30);
 const V={above:[mx+px*L*.35-ux*L*.1,L*.45,mz+pz*L*.35-uz*L*.1, mx,0,mz], side:[mx+px*L*.75,6,mz+pz*L*.75, mx,6,mz],
  below:[mx+px*9+ux*L*.3,-2.1,mz+pz*9+uz*L*.3, mx-ux*L*.1,1.5,mz-uz*L*.1]}[v];
 window.__camHook=()=>{camera.position.set(V[0],V[1],V[2]);camera.lookAt(V[3],V[4],V[5]);};})"""
FP="""JSON.stringify(GRIND.S.filter(s=>s.kind==='main'||s.kind==='stay').map(s=>[s.kind,s.pts.length,...[s.pts[0],s.pts[s.pts.length-1]].map(p=>[+p.x.toFixed(3),+p.y.toFixed(3),+p.z.toFixed(3)])]))"""
out={}
with sync_playwright() as p:
    br=p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"]); pg=br.new_page(viewport={"width":1280,"height":720})
    errs=[]; pg.on("pageerror",lambda e: errs.append(str(e)))
    pg.goto(B,timeout=120000); waitfor(pg,"typeof RIDERS!='undefined'&&RIDERS.ready&&RIDERS.npcs.length>0"); time.sleep(3)
    pg.keyboard.press("Enter"); time.sleep(1.5)
    pg.evaluate("garages.forEach(g=>g.gate&&(g.gate.dismissed=true));if(typeof GATE!='undefined'){GATE.uiOpen=false;gateUI()};window.__npcPassive=true;window.__npcFreeze=true")
    fp=pg.evaluate(FP); open(f"/workspace/v3build/shots/bridges_{tag}_grind.json","w").write(fp)
    for mode in ["night","day"]:
        if mode=="day": pg.evaluate(DAY); time.sleep(1)
        for bid in ["causeway","shore","b98"]:
            for v in ["above","side","below"]:
                pg.evaluate(CAM+f"('{bid}','{v}')"); time.sleep(1.5); pg.screenshot(path=D+f"{tag}_{bid}_{v}_{mode}.png")
                out[f"calls_{mode}_{bid}_{v}"]=pg.evaluate(CALLS)
        out[f"fps_{mode}"]=pg.evaluate(FPS)
    out["errors"]=errs[:5]; out["grind_cables"]=len(json.loads(fp)); br.close()
print(json.dumps(out))
