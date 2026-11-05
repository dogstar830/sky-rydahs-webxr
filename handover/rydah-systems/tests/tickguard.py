# TICKGUARD (patch_tickguard.py / tickguard.js): a throwing tick is disabled + recorded once, the loop keeps running, other systems keep ticking.
# Usage: python3 tests/tickguard.py [base_url] [page]   (default http://localhost:8899 v3build/sky-rydahs-v3-ikki.html)
from playwright.sync_api import sync_playwright
import sys, time, json
BASE=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8899"; PAGE=sys.argv[2] if len(sys.argv)>2 else "v3build/sky-rydahs-v3-ikki.html"
res=[]
def check(n,c,i=""): res.append(bool(c)); print(("PASS " if c else "FAIL ")+n,i,flush=True)
with sync_playwright() as p:
    b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    pg=b.new_page(viewport={"width":960,"height":540}); pg.set_default_timeout(180000); cerr=[]; perr=[]
    pg.on("console",lambda m: cerr.append(m.text) if m.type=="error" else None); pg.on("pageerror",lambda e: perr.append(str(e)))
    pg.goto(f"{BASE}/{PAGE}?chars=/skyrydahs-characters/",timeout=300000); ev=pg.evaluate
    for i in range(180):
        if ev("typeof RIDERS!='undefined'&&RIDERS.ready&&typeof frame!=='undefined'&&frame>5"): break
        time.sleep(1)
    time.sleep(2)
    for k in range(8):
        if ev("State.mode")=="ride": break
        pg.keyboard.press("Enter"); time.sleep(2)
    def frames(n,cap=150):
        f0=ev("frame"); t0=time.time()
        while time.time()-t0<cap:
            if ev("frame")>=f0+n: return ev("frame")-f0
            time.sleep(.2)
        return ev("frame")-f0
    tg=ev("JSON.stringify({head:typeof SR_GUARD,errs:Array.isArray(window.SR_ERRORS),tg:window.SR_TICKGUARD&&{n:SR_TICKGUARD.wrapped.length,w:SR_TICKGUARD.wrapped,loop:SR_TICKGUARD.loop,passes:SR_TICKGUARD.passes,re:!!SR_TICKGUARD.rearmed},animGuarded:animated.filter(f=>f.__srg).length,anim:animated.length})")
    print("install",tg,flush=True); T=json.loads(tg)
    check("installed: SR_GUARD + SR_ERRORS + late wrap + loop guard", T["head"]=="function" and T["errs"] and T["tg"] and T["tg"]["loop"] and T["tg"]["n"]>5, T["tg"] and T["tg"]["n"])
    check("every animated tick guarded", T["animGuarded"]==T["anim"], f'{T["animGuarded"]}/{T["anim"]}')
    check("baseline: SR_ERRORS empty, no [SR] console errors", ev("SR_ERRORS.length")==0 and not any("[SR]" in e for e in cerr), ev("JSON.stringify(SR_ERRORS)")[:300])
    # spies on systems that must keep ticking
    ev("""window.__spy={anim:0,heat:0}; animated.push(function okTick(){ __spy.anim++; });
      if(window.HEAT&&typeof HEAT.decay==='function'&&!HEAT.decay.__spy){ const d=HEAT.decay; HEAT.decay=function(){ __spy.heat++; return d.apply(this,arguments); }; HEAT.decay.__spy=1; }""")
    # 1) throwing tick pushed later (lazy push path, like the crewhouse kit)
    c0=len([e for e in cerr if "[SR]" in e]); ev("animated.push(function boomTick(){ throw new Error('boom from test'); })")
    n=frames(30); s=ev("JSON.stringify({errs:SR_ERRORS,spy:__spy})"); S=json.loads(s)
    c1=len([e for e in cerr if "[SR]" in e])
    check("loop alive after a throwing tick (30+ frames)", n>=30, n)
    check("SR_ERRORS: exactly one entry naming boomTick, disabled", len(S["errs"])==1 and "boomTick" in S["errs"][0]["system"] and S["errs"][0]["disabled"] and S["errs"][0]["stack"], json.dumps(S["errs"])[:300])
    check("console.error '[SR] ... tick disabled:' fired exactly once", c1-c0==1 and any("[SR]" in e and "boomTick" in e and "tick disabled" in e for e in cerr), [e[:120] for e in cerr if "[SR]" in e])
    check("other systems keep ticking (sentinel tick + HEAT.decay via grafTickCore)", S["spy"]["anim"]>=25 and (S["spy"]["heat"]>=25 or not ev("!!window.HEAT")), S["spy"])
    # 2) kitT0-style ReferenceError inside the crewhouse kit tick
    # synthetic (the real kitT0 bug is fixed in sources): push a tick named kitTick into animated[] (guarded as 'animated:kitTick') that throws a kitT0-style ReferenceError
    kit=ev("typeof animated!=='undefined'&&Array.isArray(animated)")
    if kit:
        ev("window.__kitBoom=true; animated.push(function kitTick(){ if(window.__kitBoom){ const o=undefined; return kitT0_synthetic_undefined_for_test; } })")
        e0=ev("SR_ERRORS.length"); h0=ev("__spy.anim"); n=frames(30)
        K=json.loads(ev("JSON.stringify(SR_ERRORS.slice(%d))"%e0))
        check("kitT0-style throw in kitTick: loop alive 30+ frames", n>=30, n)
        check("kitTick disabled + recorded once (ReferenceError kitT0)", len(K)==1 and "kitTick" in K[0]["system"] and "kitT0" in K[0]["message"] and "ReferenceError" in (K[0].get("stack") or ""), json.dumps(K)[:300])
        check("others still tick after the kit is disabled", ev("__spy.anim")-h0>=25, ev("__spy.anim")-h0)
        ev("window.__kitBoom=false")
    else: check("animated[] present for kitTick injection", False, "no animated[]")
    # 3) last resort: an unguarded line of the frame body throws (checkpoints.forEach in animate) -> loop must survive
    if ev("typeof checkpoints!=='undefined'&&checkpoints.length>0"):
        ev("window.__cp0=checkpoints[0].m; checkpoints[0].m=null")
        e0=ev("SR_ERRORS.length"); n=frames(30); F=json.loads(ev("JSON.stringify(SR_ERRORS.slice(%d))"%e0))
        ev("checkpoints[0].m=window.__cp0")
        check("frame-body throw: loop still advances 30+ frames (setAnimationLoop guard)", n>=30, n)
        check("frame-body throw recorded once as 'frame' (not silent)", len(F)==1 and F[0]["system"]=="frame", json.dumps(F)[:300])
    # 4) suites that require 0 console errors still fail on a guarded throw
    check("guarded throws surface as console errors (0-error suites still fail)", any("[SR]" in e for e in cerr) and ev("SR_ERRORS.length")>=1)
    # 5) draw calls unchanged by the guard (locked metric: direct render, same camera)
    dc=ev("(()=>{window.__camHook=null;const a=renderer.info.autoReset;renderer.info.autoReset=false;renderer.info.reset();renderer.render(scene,camera);const c1=renderer.info.render.calls;renderer.info.reset();renderer.render(scene,camera);const c2=renderer.info.render.calls;renderer.info.autoReset=a;return [c1,c2]})()")
    check("draw calls stable (guard adds 0 draws)", dc[0]==dc[1], dc)
    check("no uncaught page errors", not perr, perr[:3])
    pg.screenshot(path="/workspace/v3build/shots/tickguard.png")
    b.close()
print("RESULT",sum(res),"/",len(res)); sys.exit(0 if all(res) else 1)
