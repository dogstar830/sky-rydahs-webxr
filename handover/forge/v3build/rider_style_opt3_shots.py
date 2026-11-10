# Rydah Forge: Option 3 rider style before/after hero shots (1920x1080, dsf 1.5, ?tier=hd, FX on, seed=1, >=64 frames). Takes .testlock via caller.
import sys,time,json,os
from playwright.sync_api import sync_playwright
src=open('/workspace/v3build/dcsplit2.py').read(); HOOK=src.split('HOOK=r"""')[1].split('"""')[0]
OUT="/workspace/v3build/shots/hero/"; res={}
PL=os.environ.get("PLAYERS","caali,anika,ikki").split(",")
for who in PL:
 for tag,page,q in (("before","_rs_opt3.html",""),("after","_rs_opt3.html","&riderstyle=opt3")):
  with sync_playwright() as p:
    br=p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    pg=br.new_page(viewport={"width":1920,"height":1080},device_scale_factor=1.5); errs=[]; pg.on("pageerror",lambda e: errs.append(str(e)[:200]))
    pg.goto(f"http://localhost:8765/v3build/{page}?chars=/skyrydahs-characters/&tier=hd&seed=1&player={who}{q}&fx=1",timeout=240000); t0=time.time()
    while time.time()-t0<300:
        try:
            if pg.evaluate("typeof RIDERS!='undefined'&&RIDERS.ready&&GRIND.world"): break
        except Exception: pass
        time.sleep(.5)
    time.sleep(6); pg.keyboard.press("Enter"); time.sleep(2)
    pg.evaluate("garages.forEach(g=>g.gate&&(g.gate.dismissed=true));if(typeof GATE!='undefined'){GATE.uiOpen=false;gateUI()};window.__npcPassive=true;window.__npcFreeze=true"); pg.evaluate(HOOK)
    DAY=open("/workspace/v3build/sky_shots.py").read().split('DAY="""')[1].split('"""')[0]
    for v in ("night","day"):
        js="({rider:[-60,0,-30],cam:[-58.6,1.55,-27.2,-60,1.05,-30]})"
        if v=="day": pg.evaluate(DAY)
        pg.evaluate(f"window.__pin={js}"); f0=pg.evaluate("frame"); t1=time.time()
        while pg.evaluate("frame")-f0<64 and time.time()-t1<400: time.sleep(1)
        n=pg.evaluate("frame")-f0
        m=pg.evaluate("""(()=>{ renderer.info.autoReset=false; renderer.info.reset(); const t=performance.now(); let k=0; const c=[]; return new Promise(r=>{ (function L(){ c.push(renderer.info.render.calls); renderer.info.reset(); if(++k<30) requestAnimationFrame(L); else r({calls:Math.max(...c.slice(2)),ms:+((performance.now()-t)/30).toFixed(1),prog:renderer.info.programs.length,rs:window.RIDER_STYLE?RIDER_STYLE.stats:null,rsErr:window.RIDER_STYLE&&RIDER_STYLE.err,pbr:!!(window.PBR_WORLD&&PBR_WORLD.on),env:window.PBR_WORLD&&PBR_WORLD.ENV.cur}); })(); }); })()""")
        pg.screenshot(path=f"{OUT}rider_style_opt3_{who}_{v}_{tag}.png")
        # crew NPC: point camera at nearest NPC
        npc=None
        if who=="caali":
            npc=pg.evaluate("""(()=>{ const P=Ride.group.position; let b=null,d=1e9; for(const n of RIDERS.npcs){ const g=n&&(n.isObject3D?n:(n.holder||n.group||n.root)); if(!g) continue; const w=g.getWorldPosition(new THREE.Vector3()); const e=w.distanceTo(P); if(e<d){d=e;b=w;} } return b&&[b.x,b.y,b.z]; })()""")
            if npc:
                x,y,z=npc; pg.evaluate(f"window.__pin={{rider:[-60,0,-30],cam:[{x+1.6},{y+1.5},{z+2.6},{x},{y+1.0},{z}]}}"); time.sleep(1); f0=pg.evaluate("frame")
                while pg.evaluate("frame")-f0<64 and time.time()-t1<700: time.sleep(1)
                pg.screenshot(path=f"{OUT}rider_style_opt3_npc_{v}_{tag}.png")
        res[f"{who}_{v}_{tag}"]=dict(m,frames=n,errs=errs[:5],npc=npc); print(who,v,tag,res[f"{who}_{v}_{tag}"],flush=True)
    br.close()
json.dump(res,open("/workspace/v3build/perf/forge/rider_style_opt3"+("_npc" if PL==["caali"] else "")+".json","w"),indent=1)
