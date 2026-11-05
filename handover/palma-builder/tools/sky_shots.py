# usage: python3 sky_shots.py <before|after> -> shots/sky_<tag>_{day,night}.png + draw calls
import sys,time,json
from playwright.sync_api import sync_playwright
tag=sys.argv[1]; B="http://localhost:8765/v3build/sky-rydahs-v3-ikki.html?chars=/skyrydahs-characters/"
def waitfor(pg,e,t=180):
    t0=time.time()
    while time.time()-t0<t:
        if pg.evaluate(e): return True
        time.sleep(.3)
CALLS="""new Promise(res=>{renderer.info.autoReset=false;let n=0,mx=0;renderer.info.reset();function f(){mx=Math.max(mx,renderer.info.render.calls);renderer.info.reset();if(++n<8)requestAnimationFrame(f);else{renderer.info.autoReset=true;res(mx);}}requestAnimationFrame(f);})"""
DAY="""(()=>{scene.traverse(o=>{if(o.isHemisphereLight){o.intensity=.85;o.color.set(0xcfe0ff);o.groundColor.set(0x6a6470);}});
scene.fog.color.set(0xb8c8e0);_fogBase.set(0xb8c8e0);scene.background.set(0x9ab8e0);if(typeof FACADE!=='undefined')FACADE.setDay(1);})()"""
out={}
with sync_playwright() as p:
    br=p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"]); pg=br.new_page(viewport={"width":1280,"height":720})
    errs=[]; pg.on("pageerror",lambda e: errs.append(str(e)))
    pg.goto(B,timeout=180000); waitfor(pg,"typeof RIDERS!='undefined'&&RIDERS.ready"); time.sleep(3)
    pg.keyboard.press("Enter"); time.sleep(1.5)
    pg.evaluate("garages.forEach(g=>g.gate&&(g.gate.dismissed=true));if(typeof GATE!='undefined'){GATE.uiOpen=false;gateUI()};window.__npcPassive=true;window.__npcFreeze=true")
    pg.evaluate("Ride.group.position.set(90,0,150);window.__camHook=()=>{camera.position.set(80,6,120);camera.lookAt(170,22,175)}")
    for mode in ["night","day"]:
        if mode=="day": pg.evaluate(DAY)
        time.sleep(2.5); pg.screenshot(path=f"/workspace/v3build/shots/sky_{tag}_{mode}.png"); out[mode]=pg.evaluate(CALLS)
        out["skyday_"+mode]=pg.evaluate("typeof SKY!='undefined'?SKY.day:null")
    out["errors"]=errs[:5]; br.close()
print(json.dumps(out))
