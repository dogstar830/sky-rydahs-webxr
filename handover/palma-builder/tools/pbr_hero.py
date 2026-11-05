# Palma Builder: step-5 slice-1 hero before/after (1920x1080, dsf 1.5, ?tier=hd, FX on, seed=1, >=60 frames per view)
import sys,time
from playwright.sync_api import sync_playwright
src=open('/workspace/v3build/dcsplit2.py').read()
DAY=src.split('DAY="""')[1].split('"""')[0]; HOOK=src.split('HOOK=r"""')[1].split('"""')[0]; BRV=src.split('BRV="""')[1].split('"""')[0]
# causeway: dcsplit2's BRV parks the rider 30 m before the bridge end (water) -> bail -> respawn cut to the Sleeping Forest garage.
# Rider goes ON the deck (a + 25 m along the bridge, deck top 0.01) and is held there; the camera is teleported (pin) to the BRV side view.
CW="""((id)=>{const b=PALMA.bridges.find(q=>q.id===id),L=Math.hypot(b.b[0]-b.a[0],b.b[1]-b.a[1]),ux=(b.b[0]-b.a[0])/L,uz=(b.b[1]-b.a[1])/L,rx=b.a[0]+ux*60,rz=b.a[1]+uz*60;
 return {rider:[-60,0,-30],cam:[rx-ux*13,4.2,rz-uz*13,rx+ux*70,2,rz+uz*70]};})('causeway')"""  # 13:20: rider stays parked at the safe street spot (a rider pinned on the deck still triggered BAIL! RESPAWN and its respawn view); camera teleported alone. 12:40 fix: deck chase cam; the BRV side cam (40,9,-309) sat behind the Sleeping Forest garage
H=sys.argv[1]; V={"street":"({rider:[-60,0,-30],cam:[-59.2,1.7,-17,-60,6,-44]})","causeway":CW}
import os
for tag,q in [t for t in (("before",""),("after","&pbr=1")) if t[0] in os.environ.get("TAGS","before,after")]:
  with sync_playwright() as p:
    br=p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    pg=br.new_page(viewport={"width":1920,"height":1080},device_scale_factor=1.5); errs=[]; pg.on("pageerror",lambda e: errs.append(str(e)[:200]))
    pg.goto(f"http://localhost:8765/v3build/{H}?chars=/skyrydahs-characters/&tier=hd&seed=1{q}",timeout=240000); t0=time.time()
    while time.time()-t0<300:
        try:
            if pg.evaluate("typeof RIDERS!='undefined'&&RIDERS.ready&&GRIND.world"): break
        except Exception: pass
        time.sleep(.5)
    time.sleep(6); pg.keyboard.press("Enter"); time.sleep(2)
    pg.evaluate("garages.forEach(g=>g.gate&&(g.gate.dismissed=true));if(typeof GATE!='undefined'){GATE.uiOpen=false;gateUI()};window.__npcPassive=true;window.__npcFreeze=true"); pg.evaluate(HOOK)
    for tod in ("night","day"):
        if tod=="day": pg.evaluate(DAY)
        for v,js in [kv for kv in V.items() if kv[0] in os.environ.get('VIEWS','street,causeway')]:
            pg.evaluate(f"window.__pin={js}"); f0=pg.evaluate("frame"); t1=time.time()
            while pg.evaluate("frame")-f0<64 and time.time()-t1<400: time.sleep(1)
            n=pg.evaluate("frame")-f0; pos=pg.evaluate("[camera.getWorldPosition(new THREE.Vector3()).toArray().map(v=>Math.round(v)),Ride.group.position.toArray().map(v=>Math.round(v))]"); pg.screenshot(path=f"/workspace/v3build/shots/hero/pbr_{v}_{tod}_{tag}.png",timeout=180000); print(tag,tod,v,"frames",n,"cam/rider",pos,errs[:2],flush=True)
    br.close()
