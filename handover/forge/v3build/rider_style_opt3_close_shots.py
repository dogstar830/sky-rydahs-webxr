# Rydah Forge: opt3 CLOSE before/after (3/4 front, rider ~60% frame height). 1920x1080 dsf1.5 ?tier=hd FX on, >=64 frames.
# Deterministic: seeded Math.random + virtual clock (performance.now/Date.now/rAF t) frozen until ready, then exact 1/60 steps;
# NPCs hidden, rider+camera pinned every frame (dcsplit2 HOOK). Only difference before/after = &riderstyle=opt3. Caller holds .testlock.
import time,json,os
from playwright.sync_api import sync_playwright
V3="/workspace/v3build/"; OUT=V3+"shots/hero/"; res={}
src=open(V3+'dcsplit2.py').read(); HOOK=src.split('HOOK=r"""')[1].split('"""')[0]
DAY=open(V3+"sky_shots.py").read().split('DAY="""')[1].split('"""')[0]
PL=os.environ.get("PLAYERS","caali,anika,ikki").split(","); PAGE=os.environ.get("PAGE","_rs_opt3.html")
INIT="""(()=>{ let s=12345; Math.random=()=>{ s|=0; s=s+0x6D2B79F5|0; let t=Math.imul(s^s>>>15,1|s); t=t+Math.imul(t^t>>>7,61|t)^t; return ((t^t>>>14)>>>0)/4294967296; };
 let V=0; const st={step:0}; window.__vc=st; performance.now=()=>V; const D0=1.7e12; Date.now=()=>D0+V;
 const oR=window.requestAnimationFrame.bind(window); let lastF=-1;
 window.requestAnimationFrame=cb=>oR(()=>{ const f=window.__vcF=(window.__vcF||0); if(f!==lastF){} cb(V); });
 (function tick(){ V+=st.step; window.__vcF=(window.__vcF||0)+1; oR(tick); })(); })()"""
CAM="""(()=>{ RIDERS.npcs.forEach(n=>{ if(n.holder) n.holder.visible=false; if(n.r&&n.r.visible!==undefined) n.r.visible=false; }); for(const k of ['ikkiNpc','akitoNpc']) if(RIDERS[k]&&RIDERS[k]!==RIDERS.player){ const o=RIDERS[k]; if(o.isObject3D) o.visible=false; if(o.holder) o.holder.visible=false; if(o.r&&o.r.visible!==undefined) o.r.visible=false; } try{ if(window.HEAT&&HEAT.cops) HEAT.cops.forEach(c=>{ for(const k of ['mesh','group','holder','root','body']) if(c[k]&&c[k].visible!==undefined) c[k].visible=false; }); if(window.HEAT) HEAT.stars=0; }catch(e){}
 const hideAll=()=>{ const keep=Ride.group; const tops=new Set(); scene.traverse(o=>{ if(o.isSkinnedMesh){ let a=o; while(a.parent&&a.parent!==scene) a=a.parent; let mine=false; for(let x=o;x;x=x.parent) if(x===keep) mine=true; if(!mine){ let n=0; a.traverse(()=>n++); tops.add(n<400?a:o); } } });   /* never hide a big world group: fall back to the mesh */ tops.forEach(t=>t.visible=false); window.__rsHidden=tops.size; };
 hideAll(); if(!window.__rsHideLoop){ window.__rsHideLoop=1; const oR=renderer.render.bind(renderer); renderer.render=function(sc,c){ if(sc===scene) hideAll(); return oR(sc,c); }; }   /* any skinned root not under the player (patrols, akito, rivals) stays hidden every frame */
 window.__npcPassive=true; window.__npcFreeze=true; const R=[-60,0,-30]; Ride.group.position.set(...R); Ride.group.rotation.set(0,0,0); Ride.group.updateMatrixWorld(true);
 const fw=new THREE.Vector3(); (RIDERS.player||Ride.group).getWorldDirection(fw); fw.y=0; fw.normalize().negate();   /* model faces -Z of its world dir */ const rt=new THREE.Vector3(-fw.z,0,fw.x);
 const d=(1.75/.6)/(2*Math.tan(THREE.MathUtils.degToRad(camera.fov)/2)); const a=Math.PI/6;
 const c=new THREE.Vector3(...R).addScaledVector(fw,d*Math.cos(a)).addScaledVector(rt,d*Math.sin(a)); window.__pin={rider:R,cam:[c.x,R[1]+1.0,c.z,R[0],R[1]+.9,R[2]]}; return {d,fov:camera.fov}; })()"""
def frames(pg,n):
    f0=pg.evaluate("frame"); t=time.time()
    while pg.evaluate("frame")-f0<n and time.time()-t<600: time.sleep(.5)
    return pg.evaluate("frame")-f0
for who in PL:
  for tag,q in (("before",""),("after","&riderstyle=opt3")):
    with sync_playwright() as p:
      br=p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
      pg=br.new_page(viewport={"width":1920,"height":1080},device_scale_factor=1.5); errs=[]
      pg.on("pageerror",lambda e: errs.append(str(e)[:200])); pg.on("console",lambda m: errs.append(m.text[:200]) if m.type=="error" else None)
      pg.add_init_script(INIT)
      pg.goto(f"http://localhost:8765/v3build/{PAGE}?chars=/skyrydahs-characters/&tier=hd&seed=1&player={who}{q}",timeout=240000); t0=time.time()
      while time.time()-t0<400:
        try:
          if pg.evaluate("typeof RIDERS!='undefined'&&RIDERS.ready&&GRIND.world&&(!window.PBR_WORLD||!PBR_WORLD.on||(PBR_WORLD.ENV.day&&PBR_WORLD.ENV.night))"): break
        except Exception: pass
        time.sleep(1)
      time.sleep(5)
      for _try in range(3):
        try:
          if pg.is_closed(): raise RuntimeError("page closed before Enter")
          pg.keyboard.press("Enter"); break
        except Exception as e:
          print("Enter retry", _try, e, flush=True); time.sleep(2)
      else:
        raise RuntimeError("Enter failed after retries")
      time.sleep(2)
      pg.evaluate("garages.forEach(g=>g.gate&&(g.gate.dismissed=true));if(typeof GATE!='undefined'){GATE.uiOpen=false;gateUI()}"); pg.evaluate(HOOK)
      for tod in ("night","day"):
        if tod=="day": pg.evaluate(DAY)
        cam=pg.evaluate(CAM); pg.evaluate("__vc.step=1000/60"); n=frames(pg,64); pg.evaluate("__vc.step=0"); frames(pg,4)
        pg.screenshot(path=f"{OUT}rider_style_opt3_close_{who}_{tod}_{tag}.png")
        res[f"{who}_{tod}_{tag}"]=dict(frames=n,cam=cam,rs=pg.evaluate("window.RIDER_STYLE&&RIDER_STYLE.stats"),env=pg.evaluate("window.PBR_WORLD&&PBR_WORLD.ENV.cur"),errs=errs[:5])
        print(who,tod,tag,res[f"{who}_{tod}_{tag}"],flush=True)
      br.close()
json.dump(res,open(V3+"perf/forge/rider_style_opt3_close_"+"_".join(PL)+".json","w"),indent=1)
