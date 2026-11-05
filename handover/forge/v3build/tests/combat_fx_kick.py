# Rydah Forge: kick trail from Rigger's srFX_wheel attach point (scratch build, ?combatposes=1). Takes /workspace/v3build/.testlock (one Chromium at a time).
from playwright.sync_api import sync_playwright
import time,json,os,sys
LOCK="/workspace/v3build/.testlock"; PAGE=sys.argv[1] if len(sys.argv)>1 else "fxdemo_scratch.html"; OUT="/workspace/v3build/shots/hero/"
while os.path.exists(LOCK): time.sleep(10)
open(LOCK,"w").write(f"Rydah Forge: combat_fx_kick on {PAGE} :8765, max 15 min, {time.strftime('%H:%M')} (pid {os.getpid()})\n")
try:
  with sync_playwright() as p:
    b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    pg=b.new_page(viewport={"width":1920,"height":1080},device_scale_factor=1.5); pg.set_default_timeout(240000); errs=[]
    pg.on("pageerror",lambda e: errs.append(str(e))); ev=pg.evaluate
    pg.goto(f"http://localhost:8765/v3build/{PAGE}?chars=/skyrydahs-characters/&tier=hd&seed=1&player=ikki&combatposes=1",timeout=300000)
    t0=time.time()
    while time.time()-t0<300 and not ev("typeof RIDERS!='undefined'&&RIDERS.ready&&TURF.ready"): time.sleep(1)
    for k in range(10):
        if ev("State.mode")=="ride": break
        pg.keyboard.press("Enter"); t1=time.time()
        while ev("State.mode")!="ride" and time.time()-t1<15: time.sleep(.3)
    ev("try{garages.forEach(g=>g.gate&&(g.gate.dismissed=true));GATE.uiOpen=false;gateUI&&gateUI()}catch(e){}")
    while ev("frame")<60 and time.time()-t0<500: time.sleep(.3)
    info=ev("""(()=>{const P=RIDERS.player,u=P&&P.userData; const fx=u&&u.fx?Object.keys(u.fx):null;
      const api=[u&&typeof u.setState, P&&typeof P.setState, u&&typeof u.combatQuery, P&&typeof P.combatQuery];
      window.__R=(P&&typeof P.setState==='function'&&P.combatQuery)?P:u; window.__hits=[];
      try{ (__R.onCombat||u.onCombat).call(__R,'onHitFrame',e=>{ __hits.push([e.fxName,e.side,e.fxCharge]); CombatFX.fromHitFrame(e,'hit3','karasu'); }); }catch(e){}
      return {fx, api, attachResolved: !!CombatFX.attach(P,'wheelL')}; })()""")
    print("INFO",info,flush=True)
    def frames(n):
        f0=ev("frame")
        while ev("frame")<f0+n: time.sleep(.1)
    ev("CombatFX.clear()"); frames(2); base=ev("({calls:(()=>{const i=renderer.info;i.autoReset=false;i.reset();renderer.render(scene,camera);const c=i.render.calls;i.autoReset=true;return c})(),fx:Object.assign({},CombatFX.stats)})")
    ev("__R.setState('atk',{move:'heavy'})")
    t1=time.time()
    while (ev("(__R.combatQuery()||{frame:99}).frame") or 0)<9 and time.time()-t1<60: time.sleep(.05)
    st=ev("""(()=>{ const ok=true; CombatFX.timeScale=.35; /* test only: swiftshader frames are ~10x slower than the poser's clamped game dt */ const q=__R.combatQuery&&__R.combatQuery(); const side=q?q.side:'Left';
       CombatFX.emit('attackStart',{rider:RIDERS.player,fxName:'foot',side,crew:'karasu',fxCharge:.6,haptics:false}); return {ok,side,move:q&&q.move}; })()""")
    print("START",st,flush=True); shots=[]
    for i,n in enumerate([2,2,2,3]):
        frames(n); d=ev("({calls:(()=>{const i=renderer.info;i.autoReset=false;i.reset();renderer.render(scene,camera);const c=i.render.calls;i.autoReset=true;return c})(),fx:Object.assign({},CombatFX.stats),q:__R.combatQuery&&__R.combatQuery()&&__R.combatQuery().frame,hits:__hits})")
        nm=f"combat_fx_kick_wheel_{i}.png"; pg.screenshot(path=OUT+nm); d["shot"]=nm; shots.append(d); print(nm,d,flush=True)
    json.dump({"info":info,"base":base,"start":st,"shots":shots,"errors":errs[:5]},open("/workspace/v3build/perf/forge/combat-fx-kick.json","w"),indent=1); print("errors",errs[:5]); b.close()
finally:
    try:
        if open(LOCK).read().startswith("Rydah Forge"): os.remove(LOCK)
    except Exception: pass
