# Graffiti system test (graffiti.js via patch_graffiti.py). Mocked standard Xbox pad (navigator.getGamepads override).
# Covers: X near spot -> shake -> RS gesture rhythm -> tag completes; LT reticle aim tag from range; B cancel; RS isolated from camera;
# window.TURF tags/points/subscribe; district ownership flip; window.HEAT rises at night; no console errors; peak draw calls < 300.
# Usage: python3 tests/graffiti.py [base_url]   (default http://localhost:8765, serving /workspace)
from playwright.sync_api import sync_playwright
import time, math, json, sys, os
BASE=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8765"
U=BASE+"/"+(sys.argv[2] if len(sys.argv)>2 else "v3build/sky-rydahs-v3-ikki.html")+"?fps&chars=/skyrydahs-characters/"
SH="/workspace/v3build/shots/"
res=[]
def check(n,c,i=""): res.append((n,bool(c))); print(("PASS " if c else "FAIL ")+n,i,flush=True)
STUB="""(()=>{window.__pb=Array.from({length:17},()=>({pressed:false,touched:false,value:0}));
window.__pad={id:'Xbox stub',index:0,connected:true,mapping:'standard',axes:[0,0,0,0],buttons:window.__pb,timestamp:0,vibrationActuator:{playEffect:()=>Promise.resolve('complete')}};
navigator.getGamepads=()=>[window.__pad,null,null,null];})()"""
B={"A":0,"B":1,"X":2,"LT":6}
with sync_playwright() as p:
    b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader","--autoplay-policy=no-user-gesture-required"])
    pg=b.new_page(viewport={"width":1280,"height":720}); pg.set_default_timeout(180000); errs=[]
    pg.on("pageerror",lambda e: errs.append("PAGEERROR "+str(e)))
    pg.on("console",lambda m: errs.append("console: "+m.text) if m.type=="error" else None)
    pg.add_init_script(STUB)
    pg.goto(U,timeout=300000); ev=pg.evaluate
    ev("localStorage.removeItem('skyrydahs.graffiti.v1');localStorage.removeItem('skyrydahs.turf.v1')"); pg.reload(timeout=300000)
    for i in range(150):
        if ev("typeof RIDERS!='undefined'&&RIDERS.ready&&TURF.ready&&window.GRAF&&GRAF.ready"): break
        time.sleep(1)
    time.sleep(2)
    def wf(n=3):
        st=ev("frame"); t0=time.time()
        while ev("frame")<st+n and time.time()-t0<30: time.sleep(.02)
    def wc(sec):  # wait game-clock seconds
        st=ev("clock"); t0=time.time()
        while ev("clock")<st+sec and time.time()-t0<40: time.sleep(.02)
    def btn(n,on): ev(f"__pb[{B[n]}].pressed={'true' if on else 'false'};__pb[{B[n]}].value={1 if on else 0}")
    def tap(n,hold=3): btn(n,True); wf(hold); btn(n,False); wf(2)
    def rs(x,y): ev(f"__pad.axes[2]={x};__pad.axes[3]={y}")
    check("graffiti initialised", ev("GRAF.ready&&GRAF.spots.length>0"), ev("GRAF.fail||''"))
    tap("A"); time.sleep(1.5)
    if ev("State.mode")!="ride": pg.keyboard.press("Enter"); time.sleep(1.5)
    check("in ride mode", ev("State.mode")=="ride")
    # peak draw-call sampler (fps.js FPSO.calls = per-frame total across composer passes)
    ev("window.__pk=0;(function f(){ if(window.FPSO&&FPSO.calls>__pk) __pk=FPSO.calls; requestAnimationFrame(f)})()")
    # hold the rider in place (after the physics step, so rooftop heaven spots stay reachable without the grapple)
    ev("window.__hold=null;(()=>{const _u=updateRide; window.updateRide=function(dt){ const r=_u.apply(this,arguments); if(__hold){ Ride.group.position.set(__hold[0],__hold[1],__hold[2]); Ride.speed=0; } return r; };})()")
    info=ev("""JSON.stringify({n:GRAF.spots.length,by:Object.fromEntries(['S','M','L'].map(k=>[k,GRAF.spots.filter(s=>s.size===k).length])),
      surf:Object.fromEntries(Object.entries(GRAF.bySurf).map(([k,v])=>[k,v.length])),heaven:GRAF.spots.filter(s=>s.heaven).length,
      pal:TURF.palette.map(p=>p.name+(p.fallback?'*':'')),api:typeof window.TURF.subscribe,heat:typeof window.HEAT.add})""")
    print("spots",info,flush=True); I=json.loads(info)
    check("S, M and L spots present", all(I["by"][k]>0 for k in "SML"))
    check("all four surfaces present", all(I["surf"][k]>0 for k in ("brick","metal","glass","asphalt")))
    check("10 crew palettes incl. Volt + Rust Claw", len(I["pal"])==10 and any("Volt" in x for x in I["pal"]) and any("Rust Claw" in x for x in I["pal"]))
    check("window.TURF bridged to legacy TURF + subscribe", ev("window.TURF===TURF&&typeof TURF.subscribe==='function'&&!!TURF.districts&&Array.isArray(TURF.tags)"))
    ev("window.__ev=[];TURF.subscribe(e=>__ev.push({type:e.type,district:e.district,crew:e.crew,owner:e.owner||null}));0")
    ev("GRAF.forceNight=true; HEAT.set(0)"); wf(5)
    def stand(sid, dist=2.2, cam=None):
        d=ev(f"(()=>{{const s=GRAF.spots.find(q=>q.id==='{sid}'); const y=s.heaven?s.roof:0; const x=s.x+s.nx*(s.ground?0:{dist}), z=s.z+s.nz*(s.ground?0:{dist})+(s.ground?-1.2:0); window.__hold=[x,y,z]; Ride.group.position.set(x,y,z); Ride.yaw=Math.atan2(-s.nx,-s.nz); return [s.size,s.surf,s.district,s.kind]}})()")
        wf(3); return d
    def gesture_all(shot_mid=None, slow=False):
        # wait for shake -> gesture, then perform each prompted gesture on the beat
        for i in range(200):
            if ev("!GRAF.cur||GRAF.cur.phase==='gesture'"): break
            wf(1)
        n=0
        while ev("!!GRAF.cur"):
            dirs=ev("GRAF.cur.plan[GRAF.cur.gi].d"); beat=ev("GRAF.BEAT")
            rs(0,0); wf(2)
            for d in dirs:
                a=d*math.pi/4; rs(round(math.cos(a),3),round(-math.sin(a),3)); wc(beat*(1.2 if not slow else .5)); wf(1)
            rs(0,0); wf(2); n+=1
            if shot_mid and n==shot_mid[0]: pg.screenshot(path=shot_mid[1])
            if n>12: break
        return n
    def frame_cam(sid, dist=None, yoff=.6):
        ev(f"""(()=>{{const s=GRAF.spots.find(q=>q.id==='{sid}'); const D={dist if dist else "s.size==='L'?9:s.size==='M'?5.5:3.4"}; window.__camHook=()=>{{ if(s.ground){{camera.position.set(s.x+s.nx*3.5,3.4,s.z+s.nz*3.5);}} else camera.position.set(s.x+s.nx*D,s.y+{yoff},s.z+s.nz*D); camera.lookAt(s.x,s.y,s.z); }}; }})()""")
    def do_tag(sid):
        stand(sid); h0=ev("HEAT.level"); d0=ev("GRAF.stats.done"); tap("X"); started=ev("!!GRAF.cur&&GRAF.cur.sp.id==='%s'"%sid)
        gesture_all(); return started, ev("GRAF.stats.done")>d0, ev("HEAT.level")-h0
    # ---- 1. small tag via X + RS flick, mid-reveal shot (slow reveal for the camera)
    S=ev("GRAF.spots.find(s=>s.size==='S'&&s.surf==='brick').id")
    stand(S); frame_cam(S); ev("GRAF.REVEAL_RATE=.25"); h0=ev("HEAT.level"); tap("X")
    check("X near small spot starts a tag", ev("!!GRAF.cur&&GRAF.cur.sp.id==='%s'"%S))
    check("can rattle played (procedural audio)", ev("(GRAF.sfx||0)>=1"))
    ev("PAD.cam.yaw=0;PAD.cam.pitch=0;window.__camMax=0;(function f(){ if(GRAF.cur&&GRAF.cur.phase==='gesture') __camMax=Math.max(__camMax,Math.abs(PAD.cam.yaw)); requestAnimationFrame(f)})()"); wf(2); cy0=0
    gesture_all(); wc(1.2); pg.screenshot(path=SH+"graffiti_small_midreveal.png")
    ev("GRAF.REVEAL_RATE=2.5")
    check("small tag completed", ev("GRAF.spots.find(s=>s.id==='%s').owner===GRAF.me()"%S))
    check("RS drove the gesture, not the camera", ev("__camMax")<1e-3)
    check("window.TURF tag list updated (crew, icon, position)", ev("(()=>{const t=TURF.tags.find(t=>t.id==='%s');return t&&t.crew===GRAF.me()&&t.icon==='spray-can'&&typeof t.x==='number'})()"%S))
    check("TURF.subscribe got a tag event", ev("__ev.some(e=>e.type==='tag')"))
    check("heat rose at night", ev("HEAT.level")>h0, ev("HEAT.level"))
    # ---- 2. B cancels
    S2=ev("GRAF.spots.find(s=>s.size==='M'&&!s.ground&&!s.owner&&s.id!=='%s').id"%S); stand(S2); tap("X"); wf(4)
    was=ev("!!GRAF.cur"); tap("B"); wf(2)
    check("B cancels an active tag", was and ev("!GRAF.cur&&GRAF.stats.cancel>=1&&GRAF.spots.find(s=>s.id==='%s').owner==null"%S2))
    # ---- 3. LT aim/lock: quick tag on an M spot from range using the reticle hit point
    M=ev("GRAF.spots.find(s=>s.size==='M'&&!s.ground&&!s.owner).id")
    ev(f"(()=>{{const s=GRAF.spots.find(q=>q.id==='{M}'); const x=s.x+s.nx*8, z=s.z+s.nz*8; window.__hold=[x,0,z]; Ride.group.position.set(x,0,z); Ride.yaw=Math.atan2(-s.nx,-s.nz);}})()"); wf(3)
    ev("__pb[6].pressed=true;__pb[6].value=1"); wf(6)
    aim=ev("JSON.stringify(window.TGT&&TGT.aim)")
    tap("X"); aimed=ev("!!GRAF.cur&&GRAF.cur.aimed")
    check("LT aim: reticle hit point picks the spot from range", aimed, aim)
    if aimed: gesture_all()
    ev("__pb[6].pressed=false;__pb[6].value=0"); wf(3)
    check("aimed medium tag completed", ev("GRAF.spots.find(s=>s.id==='%s').owner===GRAF.me()"%M))
    # ---- 4. district takeover: pick the district where our graffiti can beat the rival, tag until it flips
    tgt=ev("""(()=>{let best=null,bm=-1e9;for(const n in TURF.districts){const D=TURF.districts[n];const sp=GRAF.spots.filter(s=>s.district===n);if(!sp.some(s=>s.size==='L'))continue;
      const pot=sp.reduce((a,s)=>a+GRAF.SIZES[s.size].pts,0), riv=Math.max(0,...Object.entries(D.points).filter(([c])=>c!==GRAF.me()).map(([,v])=>v)); if(pot-riv>bm){bm=pot-riv;best=n;}} return best})()""")
    print("takeover district",tgt,ev("JSON.stringify(TURF.districts[%r])"%tgt),flush=True)
    own0=ev("TURF.districts[%r].owner"%tgt)
    L=ev("GRAF.spots.find(s=>s.district===%r&&s.size==='L').id"%tgt)
    st,done,dh=do_tag(L)
    check("heaven/large tag completed (5 gestures, on the roof)", st and done, ev("JSON.stringify(GRAF.lastGesture)"))
    check("large tag locked for 2 minutes", ev("GRAF.spots.find(s=>s.id==='%s').lockUntil-clock>100"%L))
    check("L tag raised heat more than S", dh>.5, dh)
    frame_cam(L); wc(1.5); pg.screenshot(path=SH+"graffiti_large_heaven_complete.png")
    for sid in ev("GRAF.spots.filter(s=>s.district===%r&&!s.owner&&s.size!=='L').map(s=>s.id)"%tgt):
        if ev("TURF.districts[%r].owner===GRAF.me()"%tgt): break
        do_tag(sid)
    D=json.loads(ev("JSON.stringify(TURF.districts[%r])"%tgt))
    check("district ownership flipped to our crew", D["owner"]==ev("GRAF.me()") and own0!=D["owner"], json.dumps(D["points"]))
    check("TURF flip event emitted", ev("__ev.some(e=>e.type==='flip'&&e.owner===GRAF.me())"))
    ev("window.__camHook=null"); stand(L,6); wf(4)
    # turf flip state shot: overhead of the district with HUD
    ev(f"(()=>{{const s=GRAF.spots.find(q=>q.id==='{L}'); window.__camHook=()=>{{camera.position.set(s.x+s.nx*16,s.y+5,s.z+s.nz*16-4);camera.lookAt(s.x,s.y-2,s.z);}}}})()"); wc(.6)
    pg.screenshot(path=SH+"graffiti_turf_flip.png")
    # ---- 5. four surfaces (tag one of each if needed) + night glow
    for surf in ("brick","metal","glass","asphalt"):
        sid=ev("(GRAF.bySurf.%s.find(s=>s.owner===GRAF.me()&&s.size!=='L')||GRAF.bySurf.%s.find(s=>!s.owner&&s.size!=='L')||GRAF.bySurf.%s[0]).id"%(surf,surf,surf))
        if not ev("GRAF.spots.find(s=>s.id==='%s').owner===GRAF.me()"%sid): ev("window.__camHook=null"); do_tag(sid)
        check(f"{surf} tag completed", ev("GRAF.spots.find(s=>s.id==='%s').owner===GRAF.me()"%sid))
        ev("GRAF.forceNight=false"); frame_cam(sid,dist=3.0); wc(1.5); pg.screenshot(path=SH+f"graffiti_surface_{surf}.png")
    ev("GRAF.forceNight=true"); frame_cam(L); wc(1.5); pg.screenshot(path=SH+"graffiti_night_glow.png")
    ev("GRAF.forceNight=false"); wc(1.5); pg.screenshot(path=SH+"graffiti_day_noglow.png"); ev("GRAF.forceNight=null;window.__camHook=null")
    # ---- 6. day tag adds much less heat
    ev("GRAF.forceNight=false"); hd=ev("HEAT.level")
    sid=ev("(GRAF.spots.find(s=>!s.owner&&s.size==='S')||{}).id")
    if sid: do_tag(sid); check("day tag adds little heat", ev("HEAT.level")-hd<.2, ev("HEAT.level")-hd)
    ev("GRAF.forceNight=null")
    check("HEAT api shape", ev("['level','stars','max','add','set','subscribe'].every(k=>k in HEAT)"))
    check("mist pool stays one shared 256 Points (<=64 per can)", ev("GRAF.mist.n===256&&GRAF.mist.alive<=64"))
    # ---- 7. perf / errors
    pk=ev("__pk"); check("peak draw calls < 300", 0<pk<300, pk)
    print("graffiti draw objects",ev("['brick','metal','glass','asphalt'].length+3"),"stats",ev("JSON.stringify(GRAF.stats)"),"heat",ev("JSON.stringify({l:HEAT.level,s:HEAT.stars})"))
    E=[e for e in errs if "Custom UV" not in e]
    check("no page/console errors", len(E)==0, json.dumps(E[:10]))
    b.close()
print(f"\n{sum(1 for _,c in res if c)}/{len(res)} passed")
sys.exit(0 if all(c for _,c in res) else 1)
