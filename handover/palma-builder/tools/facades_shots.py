# usage: python3 facades_shots.py <before|after> -> shots/facades_<tag>_{night,day}_{street,aerial}.png + draw calls/fps json
import sys,time,json
from playwright.sync_api import sync_playwright
tag=sys.argv[1]; D="/workspace/v3build/shots/facades_"
B="http://localhost:8765/v3build/sky-rydahs-v3-ikki.html?chars=/skyrydahs-characters/"
def waitfor(pg,e,t=150):
    t0=time.time()
    while time.time()-t0<t:
        if pg.evaluate(e): return True
        time.sleep(.2)
CALLS="""new Promise(res=>{renderer.info.autoReset=false;let n=0,mx=0;renderer.info.reset();function f(){mx=Math.max(mx,renderer.info.render.calls);renderer.info.reset();if(++n<8)requestAnimationFrame(f);else{renderer.info.autoReset=true;res(mx);}}requestAnimationFrame(f);})"""
FPS="new Promise(r=>{let n=0,t=performance.now();(function f(){if(++n<30)requestAnimationFrame(f);else r(Math.round(30000/(performance.now()-t)*10)/10)})()})"
DAY="""(()=>{scene.traverse(o=>{if(o.isHemisphereLight){o.intensity=.85;o.color.set(0xcfe0ff);o.groundColor.set(0x6a6470);}});
scene.fog.color.set(0xb8c8e0);_fogBase.set(0xb8c8e0);scene.background.set(0x9ab8e0);if(typeof FACADE!=='undefined')FACADE.setDay(1);})()"""
VIEWS={"street":"Ride.group.position.set(-60,0,-30);Ride.yaw=Math.PI;window.__camHook=()=>{camera.position.set(-59.2,1.7,-17);camera.lookAt(-60,6,-44);}",
 "street2":"Ride.group.position.set(236,0,190);window.__camHook=()=>{camera.position.set(236,1.8,194);camera.lookAt(228,7,176)}",
 "aerial":"Ride.group.position.set(0,0,60);window.__camHook=()=>{camera.position.set(0,40,120);camera.lookAt(0,0,0)}"}
out={}
with sync_playwright() as p:
    br=p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"]); pg=br.new_page(viewport={"width":1280,"height":720})
    errs=[]; pg.on("pageerror",lambda e: errs.append(str(e)))
    pg.goto(B,timeout=120000); waitfor(pg,"typeof RIDERS!='undefined'&&RIDERS.ready&&RIDERS.npcs.length>0"); time.sleep(3)
    pg.keyboard.press("Enter"); time.sleep(1.5)
    pg.evaluate("garages.forEach(g=>g.gate&&(g.gate.dismissed=true));if(typeof GATE!='undefined'){GATE.uiOpen=false;gateUI()};window.__npcPassive=true;window.__npcFreeze=true")
    for mode in ["night","day"]:
        if mode=="day": pg.evaluate(DAY); time.sleep(1)
        for v,js in VIEWS.items():
            pg.evaluate(js); time.sleep(2); pg.screenshot(path=D+f"{tag}_{mode}_{v}.png")
            out[f"calls_{mode}_{v}"]=pg.evaluate(CALLS); out[f"fps_{mode}_{v}"]=pg.evaluate(FPS)
    out["errors"]=errs[:5]; br.close()
print(json.dumps(out))
