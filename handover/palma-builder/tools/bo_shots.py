# python3 bo_shots.py <html> <before|after> -> shots/blockout_<tag>_<area>_<view>_<day|night>.png
import sys,time,json
from playwright.sync_api import sync_playwright
H,tag=sys.argv[1],sys.argv[2]; B=f"http://localhost:8765/v3build/{H}?chars=/skyrydahs-characters/&nofx&seed=1"
SEED="(()=>{ let _s=123456789; Math.random=()=>{ _s^=_s<<13; _s^=_s>>>17; _s^=_s<<5; return ((_s>>>0)%1e9)/1e9; }; })()"
DAY="""(()=>{scene.traverse(o=>{if(o.isHemisphereLight){o.intensity=.85;o.color.set(0xcfe0ff);o.groundColor.set(0x6a6470);}});
scene.fog.color.set(0xb8c8e0);_fogBase.set(0xb8c8e0);scene.background.set(0x9ab8e0);if(typeof FACADE!=='undefined')FACADE.setDay(1);if(typeof BRIDGES!=='undefined')BRIDGES.setDay(1);})()"""
V={"beach":[[245,70,275,245,0,212],[188,1.7,222.2,250,1.6,222.2]],
 "underpass":[[-80,45,-205,-112,0,-250],[-74,1.7,-222,-112,4,-250]],
 "port":[[-200,80,175,-285,0,110],[-238,1.7,34.9,-290,2,34.9]],
 "tower":[[140,90,240,54,50,134],[54,1.7,172,54,30,134]],
 "dash":[[40,140,-180,40,0,-275],[160,1.7,-262,100,1,-290]],
 "ring":[[60,90,90,60,0,10],[62,1.7,70,60,2,10]],
 "precinct":[[320,50,40,276,0,-9],[276,1.7,16,276,5,-9]],
 "forestsign":[[40,25,-235,40,5,-275],[40,2,-257,40,6.5,-275]]}
with sync_playwright() as p:
    br=p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"]); pg=br.new_page(viewport={"width":1280,"height":720})
    pg.add_init_script(SEED); pg.goto(B,timeout=180000); t0=time.time()
    while time.time()-t0<200:
        try:
            if pg.evaluate("typeof RIDERS!='undefined'&&RIDERS.ready&&window.GRAF&&GRAF.ready&&GRIND.world&&(typeof BLOCKOUT=='undefined'||BLOCKOUT.live)"): break
        except Exception: pass
        time.sleep(.5)
    time.sleep(3); pg.keyboard.press("Enter"); time.sleep(1.5)
    pg.evaluate("garages.forEach(g=>g.gate&&(g.gate.dismissed=true));if(typeof GATE!='undefined'){GATE.uiOpen=false;gateUI()};window.__npcPassive=true;window.__npcFreeze=true")
    for mode in ["night","day"]:
        if mode=="day": pg.evaluate(DAY)
        for a,vs in V.items():
            for vn,v in zip(["above","eye"],vs):
                pg.evaluate(f"(()=>{{GRIND.on=null;Ride.group.position.set({v[3]},0,{v[5]}+3);const V={v};window.__camHook=()=>{{camera.position.set(V[0],V[1],V[2]);camera.lookAt(V[3],V[4],V[5]);}};}})()")
                time.sleep(1.6); pg.screenshot(path=f"shots/blockout_{tag}_{a}_{vn}_{mode}.png")
    br.close(); print("done",tag)
