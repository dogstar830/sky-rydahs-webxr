# Rydah Forge: CombatFX hero shots + draw-call measure. Oliver standard: 1920x1080 @1.5, ?tier=hd, FX on, >=60 frames before capture.
from playwright.sync_api import sync_playwright
import time,json,sys
BASE="http://localhost:8765/v3build"; PAGE=sys.argv[1] if len(sys.argv)>1 else "fxdemo_scratch.html"; OUT="/workspace/v3build/shots/hero/"
CREWS=sys.argv[2].split(",") if len(sys.argv)>2 and sys.argv[2] else ["codee","karasu","static","anubis","forest","behemoth","genesis","ttt","volt","rustclaw"]; SKIPX=len(sys.argv)>3
with sync_playwright() as p:
    b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    pg=b.new_page(viewport={"width":1920,"height":1080},device_scale_factor=1.5); pg.set_default_timeout(240000); errs=[]
    pg.on("pageerror",lambda e: errs.append(str(e))); ev=pg.evaluate
    pg.goto(BASE+"/"+PAGE+"?chars=/skyrydahs-characters/&tier=hd&seed=1&fxdemo=1",timeout=300000)
    t0=time.time()
    while time.time()-t0<240 and not ev("typeof RIDERS!='undefined'&&RIDERS.ready&&TURF.ready"): time.sleep(1)
    for k in range(10):
        if ev("State.mode")=="ride": break
        pg.keyboard.press("Enter"); t1=time.time()
        while ev("State.mode")!="ride" and time.time()-t1<15: time.sleep(.3)
    ev("try{garages.forEach(g=>g.gate&&(g.gate.dismissed=true));GATE.uiOpen=false;gateUI&&gateUI()}catch(e){}")
    ev("CombatFX.demo.auto=false")
    while ev("frame")<60 and time.time()-t0<400: time.sleep(.3)
    def frames(n):
        f0=ev("frame")
        while ev("frame")<f0+n: time.sleep(.1)
    def calls(): frames(2); return ev("(()=>{const i=renderer.info;i.autoReset=false;i.reset();renderer.render(scene,camera);const sc=i.render.calls;i.autoReset=true;return {sceneCalls:sc,calls:renderer.info.render.calls,tris:renderer.info.render.triangles,tex:renderer.info.memory.textures,prog:(renderer.info.programs||[]).length,fx:Object.assign({},CombatFX.stats)}})()")
    ev("CombatFX.clear()"); frames(3); ev("CombatFX.paused=true"); base=calls(); pg.screenshot(path="/workspace/v3build/perf/forge/cfx_base.png"); ev("CombatFX.paused=false"); print("BASE",base,flush=True)
    res={"base":base,"shots":[]}
    def shoot(crew,kinds,name,adv=2):
        ev("CombatFX.clear();CombatFX.paused=false")
        for k in kinds: ev(f"CombatFX.demo.fire('{crew}','{k}')")
        frames(adv); ev("CombatFX.paused=true"); frames(1)
        st=calls(); pg.screenshot(path=OUT+name); ev("CombatFX.hide=true"); frames(1); pg.screenshot(path="/workspace/v3build/perf/forge/cfx_base_"+name); ev("CombatFX.hide=false"); st["shot"]=name; res["shots"].append(st); print(name,st,flush=True); ev("CombatFX.paused=false")
    for c in CREWS:
        shoot(c,["pressured","slash","lightning","lock","hit"],f"combat_fx_{c}.png",4)
    if not SKIPX: shoot("codee",["super"],"combat_fx_super_codee.png",3)
    if not SKIPX: shoot("karasu",["super"],"combat_fx_super_karasu.png",3)
    if not SKIPX: shoot("forest",["pressured","slash"],"combat_fx_pressured_forest.png",3)
    print("errors",errs[:5]); res["errors"]=errs[:5]; json.dump(res,open("/workspace/v3build/perf/forge/combat-fx-shots.json","w"),indent=1); b.close()
