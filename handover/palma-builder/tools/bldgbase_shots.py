# Palma Builder 10/30: building-base before/after. hero standard (1920x1080, dsf 1.5, tier hd, FX on, seed 1, >=60 frames). usage: python3 bldgbase_shots.py <html> <tag>
# Day = game's own day signals (FACADE.uniforms.uDay via the global const FACADE, scene.background, BRIDGES), verified by reading FACADE.uniforms.uDay + SKY.day before each shot.
import sys,time,json
from playwright.sync_api import sync_playwright
H,tag=sys.argv[1],sys.argv[2]
src=open('/workspace/v3build/dcsplit2.py').read(); HOOK=src.split('HOOK=r"""')[1].split('"""')[0]
DAY="""(()=>{scene.traverse(o=>{if(o.isHemisphereLight){o.intensity=.85;o.color.set(0xcfe0ff);o.groundColor.set(0x6a6470);}});
scene.fog.color.set(0xb8c8e0);_fogBase.set(0xb8c8e0);scene.background.set(0x9ab8e0);if(typeof FACADE!=='undefined')FACADE.setDay(1);if(typeof BRIDGES!=='undefined')BRIDGES.setDay(1);})()"""
CLOSE="""(()=>{ let best=null; for(let i=0;i<B.pos.length;i++){ const [x,z]=B.pos[i],[w,h,d]=B.size[i]; if((B.y&&B.y[i])||h<8) continue;
  for(const [nx,nz,fx,fz,W] of [[1,0,x+w/2,z,d],[-1,0,x-w/2,z,d],[0,1,x,z+d/2,w],[0,-1,x,z-d/2,w]]){ if(W<9) continue; const cx=fx+nx*7, cz=fz+nz*7, dd=Math.hypot(cx+60,cz+30);
    if(onLand(cx,cz)&&!colliders.some(c=>cx>c.minX-1&&cx<c.maxX+1&&cz>c.minZ-1&&cz<c.maxZ+1)&&(!best||dd<best.dd)) best={dd,cam:[cx-nz*1.5,1.7,cz+nx*1.5,fx,1.9,fz],i}; } }
  return {rider:[-60,0,-30],cam:best.cam}; })()"""
V={"street":"({rider:[-60,0,-30],cam:[-59.2,1.7,-17,-60,6,-44]})","close":CLOSE}
with sync_playwright() as p:
    br=p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    pg=br.new_page(viewport={"width":1920,"height":1080},device_scale_factor=1.5); errs=[]; cons=[]
    pg.on("pageerror",lambda e: errs.append(str(e)[:200])); pg.on("console",lambda m: 'shader error' in m.text and cons.append(m.text[:300]))
    pg.goto(f"http://localhost:8765/v3build/{H}?chars=/skyrydahs-characters/&tier=hd&seed=1",timeout=240000); t0=time.time()
    while time.time()-t0<300:
        try:
            if pg.evaluate("typeof RIDERS!='undefined'&&RIDERS.ready&&GRIND.world"): break
        except Exception: pass
        time.sleep(.5)
    time.sleep(6); pg.keyboard.press("Enter"); time.sleep(2)
    pg.evaluate("garages.forEach(g=>g.gate&&(g.gate.dismissed=true));if(typeof GATE!='undefined'){GATE.uiOpen=false;gateUI()};window.__npcPassive=true;window.__npcFreeze=true"); pg.evaluate(HOOK)
    for tod in ("night","day"):
        if tod=="day": pg.evaluate(DAY)
        for v,js in V.items():
            if v=="close" and tod=="night" and "close_night" not in sys.argv: pass
            pg.evaluate(f"window.__pin={js}"); f0=pg.evaluate("frame"); t1=time.time()
            while pg.evaluate("frame")-f0<64 and time.time()-t1<500: time.sleep(1)
            n=pg.evaluate("frame")-f0; st=pg.evaluate("({uDay:FACADE.uniforms.uDay.value,sky:+SKY.day.toFixed(2),cam:camera.getWorldPosition(new THREE.Vector3()).toArray().map(v=>+v.toFixed(1)),pbr:PBR_WORLD.on})")
            pg.screenshot(path=f"/workspace/v3build/shots/hero/bldgbase_{v}_{tod}_{tag}.png",timeout=300000); print(tag,tod,v,"frames",n,json.dumps(st),errs[:2],cons[:1],flush=True)
    br.close()
