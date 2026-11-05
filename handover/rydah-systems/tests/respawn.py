# RIDER_RESET test (Rydah Systems): fall-off-world, water, air>2s, pause-menu 'RESET RIDER' via pad (MENU, D-pad, A), state cleared.
# Sampled by game frame (headless SwiftShader 1-3 fps). Runs default + ?flatground=1.
from playwright.sync_api import sync_playwright
import time, argparse
_ap=argparse.ArgumentParser(); _ap.add_argument("--port",type=int,default=8765); _ap.add_argument("--root",default="v3build")
A=_ap.parse_args()
BASE=f"http://localhost:{A.port}/{A.root}/sky-rydahs-v3-ikki.html?chars=/skyrydahs-characters/"
res=[]
def check(n,c,i=""): res.append((n,bool(c))); print(("PASS " if c else "FAIL ")+n,i,flush=True)
STUB="""(()=>{window.__pb=Array.from({length:17},()=>({pressed:false,touched:false,value:0}));
window.__pad={id:'Xbox stub',index:0,connected:true,mapping:'standard',axes:[0,0,0,0],buttons:window.__pb,timestamp:0,vibrationActuator:{playEffect:()=>Promise.resolve('complete')}};
navigator.getGamepads=()=>[window.__pad,null,null,null];})()"""
with sync_playwright() as p:
    b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    allerr=[]
    for q in ["","&flatground=1"]:
        tag="flat" if q else "ground"
        pg=b.new_page(viewport={"width":960,"height":540}); pg.set_default_timeout(200000); errs=[]
        pg.on("pageerror",lambda e: errs.append(str(e)))
        pg.on("console",lambda m: errs.append("console: "+m.text) if m.type=="error" else None)
        pg.add_init_script(STUB); pg.goto(BASE+q,timeout=300000); ev=pg.evaluate
        for i in range(150):
            if ev("typeof RIDERS!='undefined'&&RIDERS.ready&&typeof TURF!='undefined'&&TURF.ready"): break
            time.sleep(1)
        def wf(n=3,cap=150):
            st=ev("frame"); t0=time.time()
            while ev("frame")<st+n and time.time()-t0<cap: time.sleep(.05)
        def tap(i,hold=4): ev(f"__pb[{i}].pressed=true;__pb[{i}].value=1"); wf(hold); ev(f"__pb[{i}].pressed=false;__pb[{i}].value=0"); wf(3)
        for k in range(8):
            if ev("State.mode")=="ride": break
            tap(0); time.sleep(.5)
        ev("window.__hideIkkiNpc=true")
        check(f"[{tag}] in ride, RIDER_RESET present", ev("State.mode==='ride'&&typeof RIDER_RESET==='function'&&RIDE_GROUND.flat===%s"%("true" if q else "false")))
        # build a lastSafe: ride grounded on real ground at spawn for a few game-seconds
        ev("Ride.group.position.set(0,0,16);Ride.y=0;Ride.speed=0"); wf(3)
        c0=ev("clock")
        while ev("clock")-c0<1.2: wf(2)
        ls=ev("RIDE_GROUND.lastSafe"); check(f"[{tag}] lastSafe tracked while grounded", ls and abs(ls['x'])<1 and abs(ls['z']-16)<1, ls)
        def clean(): return ev("""(()=>{ const p=Ride.group.position; return {air:!!WALL.air,on:!!WALL.on,grind:!!(window.GRIND&&GRIND.on),grap:!!(typeof GRAP!=='undefined'&&(GRAP.act||GRAP.deck||GRAP.airDeck)),sp:Ride.speed,grinding:Ride.grinding,x:p.x,y:p.y,z:p.z}; })()""")
        def is_clean(c): return not(c['air'] or c['on'] or c['grind'] or c['grap'] or c['grinding']) and c['sp']<.5 and abs(c['x']-ls['x'])<1.5 and abs(c['z']-ls['z'])<1.5
        # 1) fall off the world: y < -10
        n0=ev("RIDE_GROUND.respawns"); ev("Ride.group.position.set(500,-12,500);Ride.y=-12;WALL.air=null"); wf(4)
        c=clean(); check(f"[{tag}] y<-10 -> respawn at lastSafe, state clean", ev("RIDE_GROUND.respawns")>n0 and ev("RIDE_GROUND.lastReason")=="void" and is_clean(c), (ev("RIDE_GROUND.lastReason"),c))
        # 2) air > 2 s with no ground below (far off the map)
        n0=ev("RIDE_GROUND.respawns"); ev("Ride.group.position.set(900,30,900);Ride.y=30;Ride.speed=0;WALL.air={vx:0,vz:0,vy:6,y:30,flip:false,t:.2}")
        c0=ev("clock"); t0=time.time()
        while ev("RIDE_GROUND.respawns")==n0 and ev("clock")-c0<4 and time.time()-t0<300: wf(2)
        dt=ev("clock")-c0; check(f"[{tag}] >2 s airborne with no ground below -> reset", ev("RIDE_GROUND.respawns")>n0 and ev("RIDE_GROUND.lastReason") in ("air","void") and 1.8<dt<3.5 and is_clean(clean()), f"reason={ev('RIDE_GROUND.lastReason')} after {dt:.2f}s game")
        # 3) water (hooked mode: stub ground -> water under the rider)
        if not q:
            n0=ev("RIDE_GROUND.respawns"); ev("window.__rw=WORLD_GROUND; window.WORLD_GROUND=function(){return {y:-2.5,nx:0,ny:1,nz:0,surf:'water'};}; WORLD_GROUND.version='1.0'")
            c0=ev("clock"); t0=time.time()
            while ev("RIDE_GROUND.respawns")==n0 and ev("clock")-c0<2 and time.time()-t0<300: wf(2)
            ev("window.WORLD_GROUND=__rw"); wf(2)
            check("[ground] water -> respawn", ev("RIDE_GROUND.respawns")>n0 and ev("RIDE_GROUND.lastReason")=="water" and is_clean(clean()), ev("RIDE_GROUND.lastReason"))
        # 4) menu path with dirty state (mid-air + fake grind/grapple flags), MENU -> D-pad down -> A
        ev("Ride.group.position.set(5,2,30);Ride.y=2;Ride.speed=15;WALL.air={vx:0,vz:15,vy:2,y:2,flip:true,t:.3};Ride.grinding=true")
        if ev("typeof GRAP!=='undefined'"): ev("GRAP.airDeck=false")
        n0=ev("RIDE_GROUND.respawns")
        tap(9,4); check(f"[{tag}] MENU pauses, pause menu lists RESET RIDER", ev("State.mode")=="pause" and "RESET RIDER" in ev("SCREENS.pause.opts()"), ev("[State.mode,SCREENS.pause.opts()]"))
        idx=ev("SCREENS.pause.opts().indexOf('RESET RIDER')"); ev("UI.sel=0")
        for k in range(idx): tap(13,3)
        check(f"[{tag}] D-pad selects RESET RIDER", ev("SCREENS.pause.opts()[UI.sel]")=="RESET RIDER", ev("UI.sel"))
        tap(0,4); wf(3); c=clean()
        check(f"[{tag}] A -> RIDER_RESET('menu') + unpaused + state clean", ev("State.mode")=="ride" and ev("RIDE_GROUND.respawns")>n0 and ev("RIDE_GROUND.lastReason")=="menu" and is_clean(c), (ev("State.mode"),ev("RIDE_GROUND.lastReason"),c))
        y=ev("Ride.group.position.y"); check(f"[{tag}] after reset y on ground", abs(y-(0 if q else ls['y']))<.05, y)
        # still rides after reset
        ev("__pad.axes=[0,-1,0,0]"); wf(10); ev("__pad.axes=[0,0,0,0]"); check(f"[{tag}] rides normally after reset", ev("Ride.speed")>.5, ev("Ride.speed"))
        allerr+=[tag+": "+e for e in errs]; pg.close()
    check("no console errors", not allerr, allerr[:5])
    b.close()
print(f"\n{sum(1 for _,c in res if c)}/{len(res)} PASS")
