# SR_PAD standard gamepad module test (mocked navigator.getGamepads, standard mapping).
from playwright.sync_api import sync_playwright
import time, math, argparse, os, sys
_GP=os.environ.get("GP_ONLY","")  # "", "p1", "p2" (remap) or "p3" (RT..end); p1+p2+p3 = full suite
_ap=argparse.ArgumentParser(); _ap.add_argument("--port",type=int,default=8765)
PORT=_ap.parse_args().port
U=f"http://localhost:{PORT}/v3build/sky-rydahs-v3-ikki.html?chars=/skyrydahs-characters/"
res=[]
def check(n,c,i=""): res.append((n,bool(c))); print(("PASS " if c else "FAIL ")+n,i,flush=True)
STUB="""(()=>{window.__pb=Array.from({length:17},()=>({pressed:false,touched:false,value:0}));window.__rum=0;
window.__pad={id:'Xbox stub',index:0,connected:true,mapping:'standard',axes:[0,0,0,0],buttons:window.__pb,timestamp:0,vibrationActuator:{playEffect:()=>{window.__rum++;return Promise.resolve('complete');}}};
window.__padOn=true; navigator.getGamepads=()=>window.__padOn?[window.__pad,null,null,null]:[null,null,null,null];})()"""
with sync_playwright() as p:
    b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    pg=b.new_page(viewport={"width":1280,"height":720}); pg.set_default_timeout(150000); errs=[]
    pg.on("pageerror",lambda e: errs.append(str(e)))
    pg.on("console",lambda m: errs.append("console: "+m.text) if m.type=="error" else None)
    pg.add_init_script(STUB)
    pg.goto(U,timeout=300000)
    for i in range(90):
        if pg.evaluate("typeof RIDERS!='undefined'&&RIDERS.ready&&TURF.ready"): break
        time.sleep(1)
    time.sleep(3)
    ev=pg.evaluate
    def wf(n=3):
        st=ev("frame"); t0=time.time()
        while ev("frame")<st+n and time.time()-t0<20: time.sleep(.03)
    def btn(i,on,v=None): ev(f"__pb[{i}].pressed={'true' if on else 'false'};__pb[{i}].value={v if v is not None else (1 if on else 0)}")
    def tap(i,hold=6): btn(i,True); wf(hold); btn(i,False); wf(3)
    check("SR_PAD present, pad already connected at launch picked up", ev("!!window.SR_PAD&&SR_PAD.connected&&SR_PAD.pad.id==='Xbox stub'"))
    check("BUTTONS map is Oliver's standard", ev("JSON.stringify(SR_BUTTONS)")=='{"A":0,"B":1,"X":2,"Y":3,"LB":4,"RB":5,"LT":6,"RT":7,"VIEW":8,"MENU":9,"L3":10,"R3":11,"DPAD_UP":12,"DPAD_DOWN":13,"DPAD_LEFT":14,"DPAD_RIGHT":15,"XBOX":16}')
    ev("window.__dn={};window.__upc={};window.__trig=[];SR_PAD.onButtonDown=i=>__dn[i]=(__dn[i]||0)+1;SR_PAD.onButtonUp=i=>__upc[i]=(__upc[i]||0)+1;SR_PAD.onTrigger=(l,r)=>{__trig.push([l,r]);if(__trig.length>400)__trig.shift();}")
    # non-standard pad ignored
    ev("__pad.mapping=''"); wf(2); check("non-standard mapping ignored", ev("!SR_PAD.connected")); ev("__pad.mapping='standard'"); wf(2)
    mode0=ev("State.mode"); check("starts in menu", mode0=="menu", mode0)
    # D-pad menu nav one step per press
    s0=ev("JSON.stringify([UI.screen,UI.sel])") if ev("typeof UI!=='undefined'") else None
    tap(13,10); s1=ev("JSON.stringify([UI.screen,UI.sel])")
    check("D-pad down held 10 frames moves menu once", s0!=s1 and ev("__dn[13]")==1 and ev("__upc[13]")==1, f"{s0}->{s1} downs={ev('__dn[13]')}")
    tap(12,4); check("D-pad up back", ev("JSON.stringify([UI.screen,UI.sel])")==s0, ev("JSON.stringify([UI.screen,UI.sel])"))
    tap(0,10); time.sleep(1); wf(3); m=ev("State.mode")
    check("A selects in menu (one edge for 10-frame hold)", m!="menu" or ev("UI.screen")!=s0, f"mode={m} A downs={ev('__dn[0]')}")
    check("edge detection: one press = one event", ev("__dn[0]")==1)
    for k in range(4):
        if ev("State.mode")=="ride": break
        tap(0,4); time.sleep(.8)
    check("in ride after A", ev("State.mode")=="ride", ev("State.mode")); ev("window.__hideIkkiNpc=true")
    if _GP not in ("p2","p3"):   # GP_ONLY=p2/p3 skip pause/deadzone/steering/camrel/boost (they run in GP_ONLY=p1); Systems 15:05 split for 6-min windows
        # pause via MENU
        tap(9,8); check("MENU pauses (single toggle for held press)", ev("State.mode")=="pause", ev("State.mode"))
        tap(9,3); check("MENU resumes", ev("State.mode")=="ride", ev("State.mode"))
        # deadzone
        ev("__pad.axes=[0.1,0.05,0,0]"); wf(3)
        check("inside deadzone -> zero stick & no move", ev("SR_PAD.left.x===0&&SR_PAD.left.y===0&&Input.mag===0"), ev("JSON.stringify([SR_PAD.left,Input.mag])"))
        ev("__pad.axes=[0.5,0,0,0]"); wf(3); x=ev("SR_PAD.left.x")
        check("radial rescale (0.5 -> 0.4318)", abs(x-(0.5-.12)/.88)<1e-3, x)
        # steering
        ev("__pad.axes=[0.9,0,0,0]"); wf(4); yaw=ev("Input.yaw"); mag=ev("Input.mag")
        yaw=ev("PAD.camRel?PAD.camRel.raw:Input.yaw")
        check("LS right raw stick angle ~ +pi/2 (before camera transform)", abs(yaw-math.pi/2)<.05 and mag>.85, f"raw={yaw:.3f} mag={mag:.3f}")
        ev("__pad.axes=[0,-1,0,0]"); wf(4); check("LS up raw stick angle ~0", abs(ev("PAD.camRel?PAD.camRel.raw:Input.yaw"))<.05 and ev("Input.mag")>.95)
        ev("__pad.axes=[0,0,0,0]"); wf(3)
        # ---- camera-relative movement (CORE): camera at 0 / 90 / 180 deg world yaw, LS up -> along rendered camera forward; LS left/right -> camera left/right ----
        ev("""window.__camF=null;(function L(){ const v=new THREE.Vector3();camera.getWorldDirection(v);window.__camF=[v.x,v.z];requestAnimationFrame(L)})()""")
        CF="(()=>{const v=new THREE.Vector3();camera.getWorldDirection(v);const y=Math.atan2(v.x,v.z);return [Math.sin(y),Math.cos(y)]})()"  # between frames the camera is the RENDERED one (RS orbit already applied)
        for deg in (0,90,180):
            ev(f"WALL.air=null;Ride.speed=0;Ride.yaw={math.radians(deg)};Ride.group.position.set(0,Ride.group.position.y,16);if(window.PAD)PAD.cam.yaw=0"); wf(30)
            f=ev(CF); q0=ev("[Ride.group.position.x,Ride.group.position.z]")
            ev("__pad.axes=[0,-1,0,0]"); wf(20); ev("__pad.axes=[0,0,0,0]"); wf(2); q1=ev("[Ride.group.position.x,Ride.group.position.z]")
            d=[q1[0]-q0[0],q1[1]-q0[1]]; n=math.hypot(*d) or 1; dot=(d[0]*f[0]+d[1]*f[1])/n
            check(f"CORE LS up moves along camera forward, camera at {deg} deg", n>.3 and dot>.9, f"dot={dot:.2f} dist={n:.2f} cam={[round(v,2) for v in f]}")
            for lab,ax,sgn in (("right",1,1),("left",-1,-1)):
                ev(f"__pad.axes=[{ax},0,0,0]"); wf(3); iy=ev("Input.yaw"); f=ev(CF); ev("__pad.axes=[0,0,0,0]"); wf(2)
                rx,rz=-f[1],f[0]  # camera right
                dd=(math.sin(iy)*rx+math.cos(iy)*rz)*sgn
                check(f"LS {lab} = camera {lab}, camera at {deg} deg", dd>.95, f"dot={dd:.2f}")
        # RS orbit ~90 deg, release, LS up -> along the orbited (rendered) camera forward
        ev("WALL.air=null;Ride.speed=0;Ride.yaw=Math.PI;PAD.cam.yaw=0"); wf(20)
        ev("__pad.axes=[0,0,-1,0]"); c0=ev("clock")
        while abs(ev("PAD.cam.yaw"))<1.4 and ev("clock")-c0<3: wf(2)
        oy=ev("PAD.cam.yaw"); f=ev(CF); ev("__pad.axes=[0,-1,0,0]"); q0=ev("[Ride.group.position.x,Ride.group.position.z]"); wf(16); ev("__pad.axes=[0,0,0,0]"); wf(2)
        q1=ev("[Ride.group.position.x,Ride.group.position.z]"); d=[q1[0]-q0[0],q1[1]-q0[1]]; n=math.hypot(*d) or 1; dot=(d[0]*f[0]+d[1]*f[1])/n
        check("CORE RS-orbited camera (~90 deg) then LS up -> along that camera forward", n>.3 and dot>.9, f"orbit={oy:.2f} dot={dot:.2f} dist={n:.2f}")
        # keyboard W -> camera forward
        ev("WALL.air=null;Ride.speed=0;Ride.yaw=Math.PI/2;PAD.cam.yaw=0"); wf(30); f=ev(CF); q0=ev("[Ride.group.position.x,Ride.group.position.z]")
        pg.keyboard.down("w"); wf(20); pg.keyboard.up("w"); wf(2); q1=ev("[Ride.group.position.x,Ride.group.position.z]")
        d=[q1[0]-q0[0],q1[1]-q0[1]]; n=math.hypot(*d) or 1; dot=(d[0]*f[0]+d[1]*f[1])/n
        check("keyboard W moves along camera forward (camera at 90 deg)", n>.3 and dot>.9, f"dot={dot:.2f} dist={n:.2f}")
        # frame-count based (headless SwiftShader runs ~0.3-3 fps and dt is clamped to 50 ms, so 1 s wall = ~0.1 s game time)
        p0=ev("[Ride.group.position.x,Ride.group.position.z]"); f0=ev("frame"); t0=time.time(); d=0
        while time.time()-t0<90:
            p1=ev("[Ride.group.position.x,Ride.group.position.z]"); d=math.hypot(p1[0]-p0[0],p1[1]-p0[1])
            if d>.5 and ev("frame")-f0>=20: break
            time.sleep(.1)
        check("rider moves with stick", d>.5 and ev("Ride.speed")>0, f"{p0}->{p1} d={d:.3f} frames={ev('frame')-f0} wall={time.time()-t0:.1f}s"); ev("__pad.axes=[0,0,0,0]"); wf(3)
        # boost (L3 in current layer) + dash edge
        ev("DASH.meter=1;DASH.t=0;window.__bst=0;window.__dash=0;const _o=window.__oP||poll;window.__oP=_o;"); 
        ev("(()=>{const f=animate;})()")
        btn(10,True); wf(2); b1=ev("Input.boost"); m1=ev("DASH.meter"); wf(8); m2=ev("DASH.meter"); btn(10,False); wf(3)
        check("L3 boost held -> Input.boost, dash fires once", b1 and abs(m1-.67)<.02 and abs(m2-m1)<.02, f"boost={b1} meter {m1:.2f}->{m2:.2f}")
    if _GP=="p1": b.close(); print("RESULT",sum(c for _,c in res),"/",len(res)); sys.exit(0 if all(c for _,c in res) else 1)
    if _GP!="p3":   # GP_ONLY=p3 = setup + RT analog..end (skips the remap block, which runs in p2)
        # ---- Oliver remap 2026-10-30: LB = L special (I.a[2]), LT = no special, LB no boost, L3 boost, D-pad left = grapple (not with phone up)
        ev("window.__ia=[];if(!window.__wiH){window.__wiH=1;const o=wallInput;wallInput=function(){const I=o.apply(this,arguments);if(I&&I.a)__ia.push(I.a.slice());return I;};}")
        ev("PHONE.up&&phoneSet(false);ATK.act=null;__ia.length=0"); btn(4,True); wf(3); lbB=ev("Input.boost"); btn(4,False); wf(3)
        check("remap: LB press fires L special (I.a[2])", ev("__ia.some(a=>a[2])"), ev("JSON.stringify(__ia.filter(a=>a.some(Boolean)))"))
        check("remap: LB does not boost", not lbB, lbB)
        ev("ATK.act=null;__ia.length=0"); btn(6,True,1); wf(4); btn(6,False,0); wf(3)
        check("remap: LT press fires no special", ev("!__ia.some(a=>a.some(Boolean))"), ev("JSON.stringify(__ia.filter(a=>a.some(Boolean)))"))
        ev("DASH.t=0;DASH.meter=1;Ride.boost=0;window.__ib=0;if(!window.__ibH){window.__ibH=1;const o=poll;poll=function(){const r=o.apply(this,arguments);if(Input.boost)__ib++;return r;};}"); m0=ev("DASH.meter")
        btn(10,True); wf(6); l3=ev("[__ib,+Ride.boost.toFixed(3),DASH.t>0,+DASH.meter.toFixed(2)]"); btn(10,False); wf(3)
        check("remap: L3 still boosts (Input.boost + Ride.boost/dash state changes)", l3[0]>0 and (l3[1]>0 or l3[2] or l3[3]<m0), l3)
        ev("window.__gs=0;if(!window.__gsH){window.__gsH=1;const g=grapStart;window.__gsO=g;grapStart=function(t){__gs++;};const p=poll;poll=function(){if(window.__forceT)GRAP.target=__forceT;return p.apply(this,arguments);};}")
        ev("GRAP.act=null;window.__forceT=GRAP.pts[0]||{x:0,y:3,z:0,name:'stub'}"); tap(14,3)
        check("remap: D-pad left starts grapple when GRAP.target set", ev("__gs")>=1, ev("__gs"))
        ev("__gs=0;phoneSet(true);PHONE.app='home';PHONE.sel=1"); wf(3); s0=ev("JSON.stringify([PHONE.app,PHONE.sel])"); tap(14,3); s1=ev("JSON.stringify([PHONE.app,PHONE.sel])")
        check("remap: D-pad left with phone up navigates phone, no grapple", ev("__gs")==0 and s0!=s1, f"{s0}->{s1} grapples={ev('__gs')}")
        ev("phoneSet(false)"); wf(3)
        # D-left in UI modes: gate keypad open -> keypad nav, no grapple; pause -> menu nav, no grapple
        ev("__gs=0;window.__pl=0;if(!window.__plH){window.__plH=1;const o=poll;poll=function(){const r=o.apply(this,arguments);if(Input.pLeft)__pl++;return r;};}")
        if ev("typeof GATE!=='undefined'&&garages.length&&!!garages[0].gate"):
            ev("GATE.uiOpen=true;GATE.sel=5;GATE.prevPad={}"); btn(14,True); wf(2)
            gs=ev("(()=>{gatePadInput(garages[0]);return GATE.sel;})()"); wf(2); btn(14,False); wf(3); g=ev("__gs"); ev("GATE.uiOpen=false"); wf(2)
            check("remap: gate keypad open -> D-left navigates keypad, no grapple", gs==4 and g==0, f"sel 5->{gs} grapples={g}")
        tap(9,3); pm=ev("State.mode"); ev("__gs=0;__pl=0"); tap(14,3); pg_=[ev("__gs"),ev("__pl")]; tap(9,3); wf(3)
        check("remap: pause -> D-left is menu nav, no grapple", pm=="pause" and pg_[0]==0 and pg_[1]>0, f"mode={pm} grapples/pLeft={pg_} back={ev('State.mode')}")
        ev("window.__forceT=null;grapStart=__gsO;GRAP.target=null"); wf(3)
    if _GP=="p2": b.close(); print("RESULT",sum(c for _,c in res),"/",len(res)); sys.exit(0 if all(c for _,c in res) else 1)
    # RT analog / trigger every frame incl 0
    ev("__trig.length=0")  # buffer is capped at 400 (shift), so the length check needs headroom
    btn(7,True,.6); wf(3); t=ev("__trig[__trig.length-1]"); check("RT analog value reported", abs(t[1]-.6)<1e-6, t)
    btn(7,False,0); wf(2); n0=ev("__trig.length"); wf(3); t=ev("__trig.slice(-3)")
    check("trigger reported every frame incl 0 on release", all(x[1]==0 for x in t) and ev("__trig.length")>n0, t)
    # tag: X held at a turf spot
    ev("(()=>{const s=TURF.spots.find(s=>s.owner!==TURF.me)||TURF.spots[0];window.__sp=s;Ride.group.position.set(s.x+s.nx*2,0,s.z+s.nz*2);Ride.speed=0;})()"); wf(3)
    ev("window.__tg=0;(()=>{const o=poll;poll=function(){o();if(Input.tag)__tg++;};})()")
    btn(2,True); wf(8); btn(2,False); wf(3)
    check("X at turf spot -> tag", ev("__tg")>0, f"tagFrames={ev('__tg')} near={ev('PAD.xNear')}")
    # rumble through SR_PAD
    r0=ev("__rum"); ev("gateHaptic(.5,40);grindRumble(.3,.6,50)"); check("rumble via SR_PAD (gate+grind)", ev("__rum")-r0==2, ev("__rum")-r0)
    # gate keypad nav (A press)
    if ev("typeof GATE!=='undefined'&&garages.length&&!!garages[0].gate"):
        ev("GATE.sel=4;GATE.prevPad={};window.gateUI=window.gateUI||(()=>{})"); btn(15,True); wf(2)
        s=ev("(()=>{const q=garages[0];gatePadInput(q);gatePadInput(q);gatePadInput(q);return GATE.sel;})()"); btn(15,False); wf(2)
        check("gate keypad D-pad right moves once (3 calls while held)", s==5, s)
    # ---- faked XR presenting: Quest emulated standard pad + touch controllers ----
    # fake XR: three r128 WebXRManager.getCamera() uses its private session (null here) -> session.updateRenderState throws; game code calls getCamera
    # outside render (minimap/map/wallFX timers) whenever isPresenting, so the stub replaces getCamera with identity while faking.
    ev("""(()=>{window.__xrb=Array.from({length:7},()=>({pressed:false,value:0}));const src={handedness:'right',gamepad:{mapping:'xr-standard',buttons:__xrb,axes:[0,0,0,0]}};
      window.__ses={inputSources:[src],renderState:{},updateRenderState(){},addEventListener(){},removeEventListener(){},requestAnimationFrame(){return 0},cancelAnimationFrame(){},end(){return Promise.resolve()}};window.__xrO={g:renderer.xr.getSession,c:renderer.xr.getCamera,d:Object.getOwnPropertyDescriptor(renderer.xr,'isPresenting')};renderer.xr.getCamera=c=>c;
      renderer.xr.getSession=()=>window.__rendering?null:__ses;window.__rendering=false;const R0=renderer.render.bind(renderer);window.__R0=renderer.render;renderer.render=(a,b)=>{__rendering=true;try{R0(a,b);}finally{__rendering=false;}};Object.defineProperty(renderer.xr,'isPresenting',{configurable:true,get:()=>!window.__rendering});})()""")
    ev("__xrb[0].pressed=true"); wf(4); t=ev("__tg"); wf(4)
    check("XR+pad: raw XR trigger(tag) ignored while standard pad connected", ev("__tg")==t, ev("__tg")-t)
    ev("__xrb[0].pressed=false; DASH.meter=1; DASH.t=0"); btn(10,True); wf(3); bx=ev("Input.boost"); btn(10,False); wf(2)
    check("XR+pad: L3 boost works while XR presenting", bx)
    ev("__pad.axes=[0.9,0,0,0]"); wf(4); check("XR+pad: LS steering works", ev("Input.mag")>.85, ev("Input.mag")); ev("__pad.axes=[0,0,0,0]"); wf(3)
    tap(9,6); check("XR+pad: MENU pauses", ev("State.mode")=="pause"); tap(9,3)
    # ---- SR_PAD.haptic (Rydah Optimizer): stub hapticActuators.pulse on the fake XR sources (right + an added left), fake clock for the rate limit ----
    ev("""(()=>{window.__hl=[];const mk=h=>({pulse:(i,ms)=>{__hl.push([h,Math.round(i*1000)/1000,ms]);return Promise.resolve(true);}});
      const S=__ses.inputSources; S[0].gamepad.hapticActuators=[mk('right')];
      S.push({handedness:'left',gamepad:{mapping:'xr-standard',buttons:Array.from({length:7},()=>({pressed:false,value:0})),axes:[0,0,0,0],hapticActuators:[mk('left')]}});
      window.__hn0=SR_PAD.hapticNow;window.__ht=0;SR_PAD.hapticNow=()=>__ht;SR_PAD._hapticReset();})()""")
    check("haptic: API + table exposed", ev("typeof SR_PAD.haptic==='function'&&Object.keys(SR_PAD.hapticEvents).join()")=="attackStart,lightHit,hit3,finisher,dive,stagger,pressured,playerHit,dodge,lockOn,roadSuper")
    check("haptic: default scale 'reduced' (0.6) in XR", abs(ev("SR_PAD.hapticScale")-.6)<1e-9 or "haptics=" in U, ev("SR_PAD.hapticScale"))
    ev("SR_PAD.hapticScale=1; __hl.length=0; SR_PAD.haptic('lightHit')")
    check("haptic: lightHit -> right hand only, .45/35", ev("JSON.stringify(__hl)")=='[["right",0.45,35]]', ev("JSON.stringify(__hl)"))
    ev("__ht=1000; __hl.length=0; SR_PAD.haptic('hit3',{hand:'left'})")
    check("haptic: opts.hand left -> left hand .6/45", ev("JSON.stringify(__hl)")=='[["left",0.6,45]]', ev("JSON.stringify(__hl)"))
    ev("__ht=2000; __hl.length=0; SR_PAD.haptic('finisher')")
    check("haptic: finisher -> both hands .85/70", ev("JSON.stringify(__hl.slice().sort())")=='[["left",0.85,70],["right",0.85,70]]', ev("JSON.stringify(__hl)"))
    ev("__ht=3000; __hl.length=0; SR_PAD._hapticReset(); SR_PAD.haptic('attackStart'); __ht=3010; SR_PAD.haptic('playerHit'); SR_PAD.haptic('lockOn',{hand:'right'})")
    n_now=ev("__hl.length"); time.sleep(.3); hl=ev("JSON.stringify(__hl)")
    check("haptic: rate limit 1/hand/40 ms, extras merged keeping the stronger", n_now==2 and hl=='[["right",0.25,20],["left",0.8,90],["right",0.8,90]]', f"immediate={n_now} {hl}")
    ev("__ht=5000; __hl.length=0; SR_PAD.hapticScale=.5; SR_PAD.haptic('dodge')")
    check("haptic: scale multiplies intensity", ev("JSON.stringify(__hl)")=='[["right",0.25,30]]', ev("JSON.stringify(__hl)"))
    ev("SR_PAD.hapticNow=__hn0; SR_PAD._hapticReset(); SR_PAD.hapticScale=1; __hl.length=0; SR_PAD.haptic('stagger')"); time.sleep(.4); ev("SR_PAD.haptic('roadSuper')"); time.sleep(.6)
    st=ev("__hl.filter(x=>x[1]===0.9).length"); rs=ev("JSON.stringify(__hl.filter(x=>x[2]===40&&x[0]==='left').map(x=>x[1]))")
    check("haptic: stagger x2 on both hands, roadSuper x3 ramp .6/.8/1", st==4 and rs=='[0.6,0.8,1]', f"stagger={st} road={rs} {ev('JSON.stringify(__hl)')}")
    ev("SR_PAD._hapticReset(); __hl.length=0; SR_PAD.hapticScale='off'"); r=ev("[SR_PAD.haptic('playerHit'),SR_PAD.haptic('finisher')]"); time.sleep(.2)
    check("haptic: Off scale -> no pulses, no count", ev("__hl.length===0&&SR_PAD._hapticCount===0&&SR_PAD.hapticScale===0") and r==[False,False])
    ev("SR_PAD.hapticScale=1"); check("haptic: unknown event / junk opts never throw", ev("(()=>{try{return SR_PAD.haptic('nope')===false&&SR_PAD.haptic(null,5)===false&&SR_PAD.haptic('dodge',{hand:7})===true}catch(e){return false}})()"))
    ev("SR_PAD._hapticReset(); __ses.inputSources[0].gamepad.hapticActuators=[]; __ses.inputSources[0].gamepad.vibrationActuator={playEffect:()=>{window.__hv=(window.__hv||0)+1;return Promise.resolve('complete')}}; __hl.length=0; SR_PAD.haptic('lightHit')")
    check("haptic: falls back to vibrationActuator when no hapticActuators", ev("window.__hv===1&&SR_PAD._hapticCount===1"), ev("[window.__hv,SR_PAD._hapticCount]"))
    ev("__ses.inputSources.pop(); delete __ses.inputSources[0].gamepad.vibrationActuator; SR_PAD.hapticScale=null")
    ev("__padOn=false"); wf(3); ev("__xrb[0].pressed=true"); wf(3); t=ev("__tg"); wf(4)
    check("XR without pad: touch controller input still works", ev("__tg")>t, ev("__tg")-t)
    ev("__xrb[0].pressed=false; renderer.xr.getSession=__xrO.g;renderer.xr.getCamera=__xrO.c;renderer.render=__R0; delete renderer.xr.isPresenting; if(__xrO.d) Object.defineProperty(renderer.xr,'isPresenting',__xrO.d)"); wf(3)
    # keyboard with pad unplugged
    ev("__padOn=false"); wf(3); check("unplug -> SR_PAD disconnected", ev("!SR_PAD.connected"))
    pg.keyboard.down("KeyW"); wf(4); km=ev("Input.mag"); pg.keyboard.up("KeyW"); wf(2)
    check("keyboard W moves", km>.9, km)
    pg.keyboard.down("ShiftLeft"); wf(3); kb=ev("Input.boost"); pg.keyboard.up("ShiftLeft"); check("keyboard Shift boost", kb)
    pg.keyboard.press("Escape"); wf(4); check("keyboard Esc pauses", ev("State.mode")=="pause", ev("State.mode")); pg.keyboard.press("Escape"); wf(4)
    check("keyboard Esc resumes", ev("State.mode")=="ride")
    check("no page/console errors", not errs, errs[:5])
    print(f"\n{sum(c for _,c in res)}/{len(res)} passed"); b.close()
