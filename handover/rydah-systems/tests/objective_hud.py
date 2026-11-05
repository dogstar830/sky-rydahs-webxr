# OBJECTIVE HUD distance readout test (minimap_v2.js). Asserts on MINIMAP.state.obj + DOM #mm2o text. Run under .testlock.
# usage: python3 tests/objective_hud.py [--port 8765] [--page v3build/sky-rydahs-v3-ikki.html]
import sys,time,json,re
from playwright.sync_api import sync_playwright
port=sys.argv[sys.argv.index("--port")+1] if "--port" in sys.argv else "8765"
PAGE=sys.argv[sys.argv.index("--page")+1] if "--page" in sys.argv else "v3build/sky-rydahs-v3-ikki.html"
B=f"http://localhost:{port}/{PAGE}?chars=/skyrydahs-characters/"
res=[]
def check(n,ok,info): res.append((n,bool(ok))); print(("PASS " if ok else "FAIL ")+n,json.dumps(info))
def waitfor(pg,e,t=150):
    t0=time.time()
    while time.time()-t0<t:
        try:
            if pg.evaluate(e): return True
        except Exception: pass
        time.sleep(.3)
    return False
with sync_playwright() as p:
    br=p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"]); pg=br.new_page(viewport={"width":1280,"height":720})
    errs=[]; pg.on("pageerror",lambda e: errs.append(str(e)))
    pg.goto(B,timeout=180000); waitfor(pg,"typeof RIDERS!='undefined'&&RIDERS.ready"); time.sleep(2); pg.keyboard.press("Enter"); time.sleep(1)
    pg.evaluate("garages.forEach(g=>g.gate&&(g.gate.dismissed=true));if(typeof GATE!='undefined'){GATE.uiOpen=false;gateUI()};window.__npcPassive=true;window.__npcFreeze=true")
    check("format", pg.evaluate("[mm2Fmt(120),mm2Fmt(999.4),mm2Fmt(1234)].join('|')")=="120 m|999 m|1.2 km", pg.evaluate("[mm2Fmt(120),mm2Fmt(999.4),mm2Fmt(1234)]"))
    pg.evaluate("Ride.speed=0;Ride.throttle=0;const P=Ride.group.position;MAP.wp={x:P.x+120,z:P.z,name:'TEST POINT'}")
    def obj():
        f0=pg.evaluate("frame"); waitfor(pg,f"frame>{f0}+3",60); time.sleep(.5); return pg.evaluate("MINIMAP.state.obj")
    o=obj(); check("waypoint 120 m reads ~120 m", o and o["name"]=="TEST POINT" and 115<=o["dist"]<=125 and re.match(r"^1[12]\d m$",o["dtext"]), o)
    check("DOM objective panel shows name + distance", o and o["panel"] and "TEST POINT" in o["panel"] and o["dtext"] in o["panel"], o and o["panel"])
    pg.screenshot(path="/workspace/v3build/shots/objective_hud.png")
    pg.evaluate("Ride.speed=0;Ride.group.position.x+=40"); o2=obj()
    check("updates as rider moves (+40 m -> ~80 m)", o2 and 75<=o2["dist"]<=85 and o2["dtext"]!=o["dtext"], o2)
    pg.evaluate("const P=Ride.group.position;MAP.wp={x:P.x+1500,z:P.z,name:'FAR'}"); o3=obj()
    check("km switch above 1000 m", o3 and o3["dtext"].endswith(" km") and o3["dtext"].startswith("1.5"), o3)
    rim=pg.evaluate("MINIMAP.state.rim.find(r=>r.kind==='objective')"); check("far objective clamped to rim (label drawn there)", rim and rim["onRim"], rim)
    check("no page errors", not errs, errs[:3])
    br.close()
print(f"{sum(o for _,o in res)}/{len(res)} PASS")
