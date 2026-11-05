import os
# iLink phone test: raise/lower, every app, Crew mission accept -> Jobs, Hack opens nearest gate, draw calls, shots.
from playwright.sync_api import sync_playwright
import time,sys
S="/workspace/v3build/shots/"; U="http://localhost:8765/v3build/sky-rydahs-v3-ikki.html?chars=/skyrydahs-characters/"
res=[]
def check(n,c,i=""): res.append((n,bool(c))); print(("PASS " if c else "FAIL ")+n,i,flush=True)
def boot(pg,url):
    pg.goto(url,timeout=300000)
    for i in range(90):
        if pg.evaluate("typeof RIDERS!='undefined'&&RIDERS.ready&&TURF.ready"): break
        time.sleep(1)
    time.sleep(3); pg.keyboard.press("Enter"); time.sleep(2); pg.evaluate("window.__hideIkkiNpc=true")
def wf(pg,n=2,to=15):
    st=pg.evaluate("frame"); t0=time.time()
    while pg.evaluate("frame")<st+n and time.time()-t0<to: time.sleep(.03)
def until(pg,js,to=20):
    t0=time.time()
    while time.time()-t0<to:
        if pg.evaluate(js): return True
        time.sleep(.1)
    return False
def peak(pg,n=12):
    m=0; pg.evaluate("window.__noFX=true"); time.sleep(.4)
    for i in range(n): m=max(m,pg.evaluate("renderer.info.render.calls")); time.sleep(.15)
    pg.evaluate("window.__noFX=false"); return m
with sync_playwright() as p:
    b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    pg=b.new_page(viewport={"width":1280,"height":720}); pg.set_default_timeout(150000); errs=[]
    pg.on("pageerror",lambda e: errs.append(str(e)))
    boot(pg,U)
    check("controls overlay hidden by default",pg.evaluate("getComputedStyle(document.getElementById('objective')).display==='none'"))
    pg.screenshot(path=S+"phone_toptext_after.png")
    d0=peak(pg); 
    pg.keyboard.press("Tab"); c0=pg.evaluate("clock"); until(pg,"PHONE.t>.95||clock-%f>1"%c0,300)   # Systems 19:20: game-time wait (raise anim is dt-based, 0.2 s; cap 1 s game time), wall cap only a hang guard
    check("Tab raises",pg.evaluate("PHONE.up&&PHONE.g.visible&&PHONE.t>.9"),pg.evaluate("[PHONE.up,PHONE.t,State.mode,document.activeElement&&document.activeElement.tagName]"))
    x0=pg.evaluate("Ride.group.position.toArray()"); pg.keyboard.down("KeyW"); wf(pg,40); sp=pg.evaluate("Ride.speed"); pg.keyboard.up("KeyW"); x1=pg.evaluate("Ride.group.position.toArray()")
    check("skating (W) continues with phone up",sp>.3 or sum((a-b)**2 for a,b in zip(x0,x1))>.05,f"speed {sp:.2f}")
    pg.screenshot(path=S+"phone_gameplay_raised.png")
    d1=peak(pg); print("draw calls peak: phone down",d0,"phone up",d1,flush=True); check("draw calls < 300",max(d0,d1)<300,f"{d0}/{d1}")
    pg.keyboard.press("Backspace"); time.sleep(2); check("Backspace on home lowers",pg.evaluate("!PHONE.up"),pg.evaluate("[PHONE.t,PHONE.g.visible]"))
    pg.keyboard.press("ArrowUp"); time.sleep(.8); check("ArrowUp raises",pg.evaluate("PHONE.up"))
    pg.keyboard.press("Escape"); time.sleep(.6); check("Esc lowers",pg.evaluate("!PHONE.up&&State.mode==='ride'"))
    pg.keyboard.press("Tab"); time.sleep(.8)
    pg.evaluate("PHONE.dirty=true"); time.sleep(.3)
    pg.screenshot(path=S+"phone_home_full.png")
    pg.evaluate("document.body.insertAdjacentHTML('beforeend','<img id=phs style=position:fixed;left:0;top:0;height:720px;z-index:99>')")
    def scr(name): pg.evaluate("PHONE.dirty=true"); time.sleep(.25); pg.evaluate("document.getElementById('phs').src=PHONE.cv.toDataURL()"); time.sleep(.3); pg.locator("#phs").screenshot(path=S+name); pg.evaluate("document.getElementById('phs').removeAttribute('src')")
    scr("phone_home.png")
    if os.environ.get("PH_ONLY") in ("pad","pad2","grapple"): pg.keyboard.press("Escape"); time.sleep(.6)   # Systems 15:40: PH_ONLY=pad = gamepad/grapple section only (6-min window)
    else:
        names=pg.evaluate("PHONE.apps.map(a=>a[0])")
        for i,n in enumerate(names):
            pg.evaluate("PHONE.sel=0;PHONE.dirty=true")
            for _ in range(i%3): pg.keyboard.press("ArrowRight")
            for _ in range(i//3): pg.keyboard.press("ArrowDown")
            pg.keyboard.press("Enter"); time.sleep(.3); a=pg.evaluate("PHONE.app")
            check("open "+n,a==n,a)
            if n=="Jobs": jobs0=pg.evaluate("PHONE.jobs.length")
            pg.keyboard.press("Backspace"); time.sleep(.2)
        check("back to home",pg.evaluate("PHONE.app==='home'&&PHONE.up"))
        # Crew mission offer -> Accept -> Jobs
        for _ in range(40):
            if pg.evaluate("PHONE.offerSent"): break
            time.sleep(.25)
        pg.evaluate("PHONE.sel=2"); pg.keyboard.press("Enter"); time.sleep(.4); check("Crew offer has replies",pg.evaluate("PHONE.app==='Crew'&&PHONE.replies&&PHONE.replies[0]==='Accept'"))
        scr("phone_crew.png")
        pg.keyboard.press("Enter"); time.sleep(.4)
        check("Accept adds mission to Jobs",pg.evaluate("PHONE.accepted&&PHONE.jobs[0].m&&!PHONE.jobs[0].d"))
        pg.keyboard.press("Backspace"); pg.evaluate("PHONE.sel=0"); pg.keyboard.press("Enter"); time.sleep(.4); scr("phone_jobs.png"); pg.keyboard.press("Backspace")
        # Hack near a gate
        pg.evaluate("""(()=>{const g=garages.find(g=>g.gate);const v=new THREE.Vector3(-1.4,0,12);g.group.localToWorld(v);Ride.group.position.set(v.x,0,v.z);Ride.yaw=g.th+Math.PI;Ride.speed=0;window.__hg=g;g.gate.dismissed=true;GATE.uiOpen=false;gateUI();})()""")
        time.sleep(1.5); check("gate closed before hack",pg.evaluate("__hg.gate.state==='closed'"),pg.evaluate("__hg.gate.state"))
        pg.evaluate("PHONE.sel=3"); pg.keyboard.press("Enter"); time.sleep(.4)
        check("Hack started",pg.evaluate("PHONE.app==='Hack'&&!!PHONE.hack&&PHONE.hack.rot!==0"))
        scr("phone_hack.png")
        r=pg.evaluate("PHONE.hack.rot")
        for _ in range(r): pg.keyboard.press("ArrowLeft"); time.sleep(.08)
        time.sleep(.4); check("Hack success",pg.evaluate("PHONE.hack.state==='ok'"))
        time.sleep(1.2); st=pg.evaluate("__hg.gate.state"); check("Hack opened nearest gate",st in("opening","open"),st+" "+str(pg.evaluate("PHONE.lastGate")))
        check("mission job completed",pg.evaluate("PHONE.jobs[0].m&&PHONE.jobs[0].d"))
        scr("phone_hack_done.png")
        pg.keyboard.press("Backspace"); pg.keyboard.press("Backspace"); time.sleep(.6); check("lowered",pg.evaluate("!PHONE.up"))
    # skating still works with phone up (WASD not captured)
    if os.environ.get("PH_ONLY")=="apps": print("RESULT",sum(c for _,c in res),"/",len(res)); b.close(); sys.exit(0 if all(c for _,c in res) else 1)   # Systems 18:02: keyboard/apps part only
    # Xbox gamepad (stubbed navigator.getGamepads): phone, movement, jump, attacks, camera, pause
    pg.evaluate("""(()=>{window.__pb=Array.from({length:17},()=>({pressed:false,value:0}));window.__pad={id:'stub',index:0,connected:true,mapping:'standard',axes:[0,0,0,0],buttons:window.__pb,timestamp:0};navigator.getGamepads=()=>[__pad,null,null,null];})()""")
    def btn(i,fr=3): pg.evaluate(f"__pb[{i}].pressed=true;__pb[{i}].value=1"); wf(pg,fr); pg.evaluate(f"__pb[{i}].pressed=false;__pb[{i}].value=0"); wf(pg,2)
    def hold(js_on,js_off,fr): pg.evaluate(js_on); wf(pg,fr); pg.evaluate(js_off); wf(pg,1)
    def axes(a): pg.evaluate(f"__pad.axes={a}")
    pg.evaluate("PHONE.app='home';PHONE.hack=null;Ride.speed=0"); time.sleep(.3)
    if os.environ.get("PH_ONLY")!="grapple":   # Systems 15:45: PH_ONLY=grapple = pad stub + grapple section only
        if os.environ.get("PH_ONLY")!="pad2":   # Systems 18:30: PH_ONLY=pad = pad/phone/map up to here, pad2 = minimap..attacks..targeting
            check("pad: phone down before",pg.evaluate("!PHONE.up"))
            btn(12,20); check("pad: D-pad Up raises (held 1s = single edge)",pg.evaluate("PHONE.up&&State.mode==='ride'"))
            pg.evaluate("PHONE.sel=0"); btn(15); btn(15); check("pad: D-pad Right x2 -> sel 2",pg.evaluate("PHONE.sel")==2,pg.evaluate("PHONE.sel"))
            btn(13); check("pad: D-pad Down -> sel 5",pg.evaluate("PHONE.sel")==5); btn(14); check("pad: D-pad Left -> sel 4",pg.evaluate("PHONE.sel")==4)
            btn(12); check("pad: D-pad Up on row 2 navigates (sel 1, still up)",pg.evaluate("PHONE.sel===1&&PHONE.up"))
            pg.evaluate("WALL.air=null;ATK.act=null"); btn(0); check("pad: A selects app (Map)",pg.evaluate("PHONE.app")=="Map",pg.evaluate("PHONE.app"))
            check("pad: A in phone did not jump",pg.evaluate("!WALL.air"))
            btn(1); check("pad: B goes back to home",pg.evaluate("PHONE.app==='home'&&PHONE.up"))
            pg.evaluate("PHONE.sel=7"); btn(0); check("pad: open Settings",pg.evaluate("PHONE.app")=="Settings")
            check("Settings lists Xbox mapping",pg.evaluate("['D-UP phone','RT special','RT+Y','VIEW world map','L3 boost','LT lock-on','D-LEFT grapple','LB L-special','RB melee','R3 crew','X action','Y trick'].every(k=>PH_CTRL.some(s=>s.includes(k)))")); scr("phone_settings_pad.png")
            btn(1); btn(1); check("pad: B on home closes",pg.evaluate("!PHONE.up"))
            btn(12); pg.evaluate("PHONE.sel=1"); btn(12); check("pad: D-pad Up toggles (raise then lower)",pg.evaluate("!PHONE.up"))
            # View -> Palma City world map
            btn(8); check("map: View opens world map",pg.evaluate("MAP.open&&MAP.mesh.visible&&!PHONE.up"))
            check("map: recentred on player at open",pg.evaluate("Math.hypot(MAP.cx-Ride.group.position.x,MAP.cz-Ride.group.position.z)<1"))
            check("map: minimap hidden while map open",pg.evaluate("(()=>{const m=document.getElementById('skmini');return !m||m.style.visibility==='hidden'||getComputedStyle(m).display==='none'})()"))
            time.sleep(.5); pg.screenshot(path=S+"map_full.png")
            L=pg.evaluate("(()=>{const k={};for(const l of MAP.locs)k[l.kind]=(k[l.kind]||0)+1;return k;})()"); print("map locs",L,flush=True)
            check("map: districts/bases/gates/jobs/shops present",all(L.get(k,0)>0 for k in("district","garage","gate","job","shop","police")) and L["garage"]==len(pg.evaluate("PALMA.garages")),L)
            check("map: legend + player drawn (canvas non-empty)",pg.evaluate("(()=>{const d=MAP.cv.getContext('2d').getImageData(MAP.W-150,MAP.S-200,1,1).data;return d[3]>0})()"))
            pg.evaluate("Ride.speed=0"); x0=pg.evaluate("MAP.cx"); axes("[1,0,0,0]"); wf(pg,15); axes("[0,0,0,0]"); wf(pg,2)
            check("map: LS pans (player not moving)",pg.evaluate("MAP.cx")>x0+20 and pg.evaluate("Ride.speed")<.5,[x0,pg.evaluate("MAP.cx"),pg.evaluate("Ride.speed")])
            z0=pg.evaluate("MAP.zoom"); pg.evaluate("__pb[7].pressed=true;__pb[7].value=1"); wf(pg,20); pg.evaluate("__pb[7].pressed=false;__pb[7].value=0"); wf(pg,2); z1=pg.evaluate("MAP.zoom")
            pg.evaluate("__pb[6].pressed=true;__pb[6].value=1"); wf(pg,10); pg.evaluate("__pb[6].pressed=false;__pb[6].value=0"); wf(pg,2); z2=pg.evaluate("MAP.zoom")
            check("map: RT zooms in, LT zooms out",z1>z0*1.2 and z2<z1,[z0,z1,z2])
            btn(14); n1=pg.evaluate("MAP.cur&&MAP.cur.name"); btn(13); n2=pg.evaluate("MAP.cur&&MAP.cur.name")
            check("map: D-pad selects locations (name shown)",bool(n1) and bool(n2) and n1!=n2,[n1,n2]); pg.screenshot(path=S+"map_select.png")
            btn(0); check("map: A sets waypoint",pg.evaluate("MAP.wp&&MAP.wp.name")==n2 and pg.evaluate("MAP.beacon.visible"))
            check("map: A did not jump / attack",pg.evaluate("!WALL.air&&!ATK.act"))
            btn(1); check("map: B closes",pg.evaluate("!MAP.open&&!MAP.mesh.visible"))
            btn(8); btn(8); check("map: View toggles closed",pg.evaluate("!MAP.open"))
            pg.keyboard.press("KeyM"); time.sleep(.4); check("map: keyboard M opens",pg.evaluate("MAP.open")); pg.keyboard.press("Escape"); time.sleep(.4); check("map: Esc closes, still riding",pg.evaluate("!MAP.open&&State.mode==='ride'"))
        if os.environ.get("PH_ONLY")=="pad": print("RESULT",sum(c for _,c in res),"/",len(res)); b.close(); sys.exit(0 if all(c for _,c in res) else 1)
        # minimap (upper right)
        # minimap: MINIMAP_V2 (minimap_v2.js, other worker) replaces the legacy #skmini when present
        if pg.evaluate("typeof MM2!=='undefined'&&!/minimap=old/.test(location.search)"):
            until(pg,"!!document.getElementById('mm2')",20)
            check("minimap: MINIMAP_V2 active, legacy #skmini hidden",pg.evaluate("!!document.getElementById('mm2')&&(!document.getElementById('skmini')||getComputedStyle(document.getElementById('skmini')).display==='none')"))
        else:
            until(pg,"State.mode==='ride'&&getComputedStyle(document.getElementById('skmini')).display!=='none'",20); wf(pg,2)
            r=pg.evaluate("(()=>{const m=document.getElementById('skmini').getBoundingClientRect(),t=document.getElementById('turf').getBoundingClientRect(),s=document.getElementById('stats').getBoundingClientRect();const ov=(a,b)=>a.width&&b.width&&!(a.right<=b.left||b.right<=a.left||a.bottom<=b.top||b.bottom<=a.top);return {top:m.top,right:innerWidth-m.right,w:m.width,ovTurf:ov(m,t),ovStats:ov(m,s)}})()")
            check("minimap: upper right, no HUD overlap",r["top"]<30 and r["right"]<30 and r["w"]>100 and not r["ovTurf"] and not r["ovStats"],r)
        if not pg.evaluate("typeof MM2!=='undefined'&&!/minimap=old/.test(location.search)"):
            pg.evaluate("window.__mc=0;window.__omd=miniDraw;miniDraw=function(){__mc++;return __omd()}"); time.sleep(2); n=pg.evaluate("__mc"); pg.evaluate("miniDraw=__omd")
            check("minimap: ~10 Hz redraw (<=11/s)",0<n<=23,n)
        pg.evaluate("MAP.wp={x:Ride.group.position.x+400,z:Ride.group.position.z,name:'FAR'}"); time.sleep(.4); pg.screenshot(path=S+"worldmap_minimap_edge.png",clip={"x":1280-200,"y":0,"width":200,"height":200})
        check("minimap: shared icon data includes waypoint",pg.evaluate("icMarkers().some(m=>m.kind==='waypoint')"))
        # GTA-style targeting (hold LT)
        LT_ON="__pb[6].pressed=true;__pb[6].value=1"; LT_OFF="__pb[6].pressed=false;__pb[6].value=0"
        fov0=pg.evaluate("camera.fov")
        ok=pg.evaluate("""(()=>{const T=atkTargets();if(!T.length)return false;const n=T[0],q=n.holder.position;window.__tn=n;GRAP.deck=null;WALL.air=null;Ride.group.position.set(q.x+6*Math.sin(0.3),0,q.z+6*Math.cos(0.3));Ride.y=0;Ride.speed=0;Ride.yaw=Math.atan2(q.x-Ride.group.position.x,q.z-Ride.group.position.z)+.15;return true;})()""")
        if ok:
            pg.evaluate(LT_ON); until(pg,"TGT.mode==='lock'",5); wf(pg,6)
            check("target: LT soft-locks nearest enemy (red reticle)",pg.evaluate("TGT.mode==='lock'&&TGT.lock.ref===__tn&&document.getElementById('retLock').style.display===''"),pg.evaluate("TGT.mode"))
            check("target: crew-coloured marker on target",pg.evaluate("TGT.mk.visible&&('#'+TGT.mk.material.color.getHexString()).toUpperCase()===TGT.lock.col.toUpperCase()"),pg.evaluate("[TGT.lock&&TGT.lock.col,'#'+TGT.mk.material.color.getHexString()]"))
            check("target: over-shoulder zoom (FOV narrower)",pg.evaluate("camera.fov")<fov0-5,[fov0,pg.evaluate("camera.fov")])
            pg.screenshot(path=S+"target_lock.png")
            pg.evaluate("ATK.act=null;ATK.cd=[0,0,0];window.__ai=null;if(!window.__as0){window.__as0=atkStart;atkStart=function(i,s){__ai=i;return __as0(i,s)}}"); btn(5,1)
            check("target: RB melee goes toward locked target",pg.evaluate("__ai")==0 and pg.evaluate("Math.abs(angDiff(Ride.yaw,Math.atan2(__tn.holder.position.x-Ride.group.position.x,__tn.holder.position.z-Ride.group.position.z)))<.25"),pg.evaluate("[__ai,Ride.yaw]"))
            pg.evaluate(LT_OFF)
            # Systems 17:58: wait (game time, cap 3 s) until the reticle is hidden and the FOV is stable for 3 frames; then FOV must be the rest (speed) FOV +-0.1
            pg.evaluate("window.__ltR={c0:clock,n:0,f:camera.fov,last:frame};(function L(){const R=__ltR;if(frame!==R.last){R.last=frame;const hid=TGT.mode==='off'&&!TGT.saved&&document.getElementById('reticle').style.display==='none';R.n=(hid&&Math.abs(camera.fov-R.f)<.01)?R.n+1:0;R.f=camera.fov;}if(R.n<3&&clock-R.c0<3)requestAnimationFrame(L);else R.done=1;})()")
            until(pg,"!!__ltR.done",120); lr=pg.evaluate("[+(clock-__ltR.c0).toFixed(2),__ltR.n,+camera.fov.toFixed(3),TGT.fovWant==null?null:+TGT.fovWant.toFixed(3),document.getElementById('reticle').style.display,TGT.mode]")
            check("target: release LT restores camera + hides reticle",lr[1]>=3 and lr[3] is not None and abs(lr[2]-lr[3])<=.1 and lr[4]=="none" and lr[5]=="off",[fov0]+lr)
        else: check("target: an enemy exists for lock test",False)
        # lock-on buffer rules (synthetic targets)
        r=pg.evaluate("""(()=>{const orig=atkTargets, me=TURF.crews[TURF.me].id, foe=garages.find(g=>g.crew!==me), ally=garages.find(g=>g.crew===me)||{crew:me,color:'#FFD700'};
          const P=Ride.group.position; P.set(0,0,-46); Ride.yaw=0; const mk=(ang,d,g)=>({holder:{visible:true,position:new THREE.Vector3(P.x+Math.sin(ang)*d,0,P.z+Math.cos(ang)*d)},g});
          const R={}, deg=Math.PI/180; const run=(T)=>{ atkTargets=()=>T; TGT.lock=null; return tgtAcquire(0); };
          let t=run([mk(20*deg,6,foe)]); R.outsideCone=!t;
          t=run([mk(10*deg,6,foe)]); R.insideCone=!!t;
          t=run([mk(0,.5,foe)]); R.tooClose=!t;
          t=run([mk(0,6,ally)]); R.ally=!t;
          const A=mk(8*deg,4,foe), B=mk(2*deg,12,foe); t=run([A,B]); R.angleFirst=t&&t.ref===B;
          atkTargets=()=>[A,B]; TGT.lock={kind:'enemy',ref:A,x:A.holder.position.x,z:A.holder.position.z,col:'#f00'}; const C=mk(5*deg,4,foe); atkTargets=()=>[A,C]; R.sticky=tgtAcquire(0).ref===A;
          const D=mk(-2*deg,4,foe); atkTargets=()=>[A,D]; R.switchWhenClearlyBetter=tgtAcquire(0).ref===D;
          R.propsNotTargets=tgtCands().every(c=>c.kind==='enemy'||c.kind==='spot');
          atkTargets=orig; TGT.lock=null; return R; })()""")
        for k,v in r.items(): check("lock buffer: "+k,v)
        # free aim at a wall (no target): dot reticle + wall hit point
        r=pg.evaluate("""(()=>{const tn=atkTargets().map(n=>n.holder.position);for(const c of colliders){if(c.off||c.maxX-c.minX<4)continue;const x=(c.minX+c.maxX)/2,z=c.maxZ+8;if(!onLand(x,z))continue;if(tn.some(q=>Math.hypot(q.x-x,q.z-z)<20))continue;if(TURF.spots.some(s=>Math.hypot(s.x-x,s.z-z)<16))continue;Ride.group.position.set(x,0,z);Ride.yaw=Math.PI;Ride.speed=0;return [x,z];}return null})()""")
        if r:
            pg.evaluate(LT_ON); until(pg,"TGT.k>=1",4); wf(pg,4)
            check("target: free aim -> dot reticle on wall point",pg.evaluate("TGT.mode==='dot'&&TGT.aim&&TGT.aim.hit"),pg.evaluate("[TGT.mode,TGT.aim]")); pg.screenshot(path=S+"target_freeaim.png")
            pg.evaluate(LT_OFF); until(pg,"TGT.k<=0",4)
        # precise spray at a tag spot
        r=pg.evaluate("""(()=>{const s=TURF.spots.find(s=>s.owner!==TURF.me&&!s.piece&&onLand(s.x+s.nx*3.2,s.z+s.nz*3.2)&&!garages.some(g=>g.gate&&Math.hypot(g.cp[0]-s.x,g.cp[1]-s.z)<14)&&!cans.some(c=>c.visible&&Math.hypot(c.position.x-s.x,c.position.z-s.z)<6));GATE.uiOpen=false;if(!s)return null;window.__ts=s;Ride.group.position.set(s.x+s.nx*3.2,0,s.z+s.nz*3.2);Ride.yaw=Math.atan2(-s.nx,-s.nz);Ride.speed=0;return s.id})()""")
        if r:
            pg.evaluate(LT_ON); until(pg,"TGT.mode==='spray'",4); wf(pg,4)
            check("target: spray-can reticle + preview on valid spot",pg.evaluate("TGT.mode==='spray'&&TGT.spot.ref===__ts&&TGT.pv.visible&&TGT.sprayOk&&document.getElementById('retSpray').style.display===''"),pg.evaluate("[TGT.mode,TGT.sprayOk]"))
            pg.screenshot(path=S+"target_spray.png")
            pg.evaluate("__pb[2].pressed=true"); wf(pg,30); pg.evaluate("__pb[2].pressed=false"); wf(pg,2)
            check("target: spraying tags the aimed spot",pg.evaluate("__ts.sprayFor===TURF.me||__ts.owner===TURF.me"),pg.evaluate("[__ts.prog,__ts.owner,TURF.me]"))
            pg.evaluate(LT_OFF); until(pg,"TGT.k<=0",4)
            r2=pg.evaluate("""(()=>{const free=(x,z)=>onLand(x,z)&&!colliders.some(c=>!c.off&&x>c.minX-.6&&x<c.maxX+.6&&z>c.minZ-.6&&z<c.maxZ+.6);const s=TURF.spots.find(s=>s!==__ts&&s.owner!==TURF.me&&!s.piece&&s.prog>=1&&[2,4,6,8].every(k=>free(s.x+s.nx*k,s.z+s.nz*k)));if(!s)return null;window.__ts2=s;window.__p2=s.prog;Ride.group.position.set(s.x+s.nx*8,0,s.z+s.nz*8);Ride.yaw=Math.atan2(-s.nx,-s.nz);Ride.speed=0;return 1})()""")
            if r2:
                pg.evaluate(LT_ON); until(pg,"TGT.mode==='spray'",4); wf(pg,3)
                check("target: out-of-range spot preview is invalid (grey)",pg.evaluate("TGT.spot&&!TGT.sprayOk"),pg.evaluate("[TGT.mode,!!TGT.spot,TGT.sprayOk,TGT.spot&&Math.hypot(TGT.spot.ref.x-Ride.group.position.x,TGT.spot.ref.z-Ride.group.position.z),TGT.spot&&TGT.spot.ref===__ts2]"))
                pg.evaluate("__pb[2].pressed=true"); wf(pg,20); pg.evaluate("__pb[2].pressed=false"); wf(pg,2)
                check("target: no spray on invalid spot",pg.evaluate("__ts2.sprayFor!==TURF.me"))
                pg.evaluate(LT_OFF); until(pg,"TGT.k<=0",4)
        else: check("target: a tag spot exists",False)
        btn(9); check("pad: Menu still pauses",pg.evaluate("State.mode")=="pause"); btn(9); time.sleep(.3)
        pg.keyboard.press("ArrowUp"); time.sleep(.5); check("keyboard ArrowUp still raises",pg.evaluate("PHONE.up")); pg.keyboard.press("Escape"); time.sleep(.4)
        check("no top overlay text",pg.evaluate("getComputedStyle(document.getElementById('objective')).display==='none'"))
        # movement + deadzone
        pg.evaluate("Ride.speed=0"); axes("[0.1,-0.1,0,0]"); wf(pg,20); check("pad: LS inside deadzone = no throttle",pg.evaluate("Ride.speed")<.3,pg.evaluate("Ride.speed"))
        pg.evaluate("if(typeof GRIND!=='undefined'){GRIND.on=null;GRIND.cd=5;}Ride.grinding=false;(()=>{const hit=(x,z)=>colliders.some(c=>!c.off&&x>c.minX-1.5&&x<c.maxX+1.5&&z>c.minZ-1.5&&z<c.maxZ+1.5)||!onLand(x,z)||rails.some(r=>Math.hypot(r.x1-x,r.z1-z)<4);for(let i=0;i<5000;i++){const x=-150+Math.random()*300,z=-150+Math.random()*300;let ok=true;for(let d=0;d<=25&&ok;d+=1)if(hit(x,z+d))ok=false;if(ok){Ride.group.position.set(x,0,z);return}}Ride.group.position.set(0,0,-46)})();Ride.yaw=0;Ride.speed=0;GATE.uiOpen=false"); wf(pg,2); p0=pg.evaluate("Ride.group.position.toArray()"); axes("[0,-1,0,0]"); wf(pg,45); sp=pg.evaluate("Ride.speed"); p1=pg.evaluate("Ride.group.position.toArray()")
        check("pad: LS forward skates",sp>.3 and sum((a-b)**2 for a,b in zip(p0,p1))>.5,f"speed {sp:.2f}")
        pg.evaluate("__pb[10].pressed=true"); wf(pg,20); check("pad: L3 boosts",pg.evaluate("Ride.boost>.3||DASH.t>0"),pg.evaluate("[Ride.boost,DASH.t]")); pg.evaluate("__pb[10].pressed=false")
        pg.evaluate("__pb[1].pressed=true"); wf(pg,40); check("pad: hold B power slide",pg.evaluate("PAD.crouch>.4")); pg.evaluate("__pb[1].pressed=false"); axes("[0,0,0,0]"); time.sleep(.3)
        axes("[0,0,1,0]"); wf(pg,30); check("pad: RS orbits camera",abs(pg.evaluate("PAD.cam.yaw"))>.3,pg.evaluate("PAD.cam.yaw")); axes("[0,0,0,0]")
        pg.evaluate("__pb[6].pressed=true;__pb[6].value=1"); wf(pg,40); check("pad: LT aim recentres camera",abs(pg.evaluate("PAD.cam.yaw"))<.1 and pg.evaluate("PAD.lt>0")); pg.evaluate("__pb[6].pressed=false;__pb[6].value=0"); time.sleep(.3)
        # jump + attacks (move away from gates/spots so X is quick melee)
        pg.evaluate("Ride.group.position.set(0,0,-46);Ride.speed=0;GATE.uiOpen=false;for(const g of garages)if(g.gate)g.gate.dismissed=true;WALL.air=null;WALL.on=null"); wf(pg,3); btn(0,2); check("pad: A jumps",pg.evaluate("!!WALL.air||Ride.y>.05||!!WALL.on"),pg.evaluate("Ride.y"))
        time.sleep(1.2)
        def atk(nm,pre,fr,post,want):
            pg.evaluate("ATK.act=null;ATK.cd=[0,0,0];ATK.stun=0"); wf(pg,2); pg.evaluate("window.__ai=null;if(!window.__as0){window.__as0=atkStart;atkStart=function(i,s){__ai=i;return __as0(i,s)}}")
            pg.evaluate(pre); wf(pg,fr); pg.evaluate(post); wf(pg,3); got=pg.evaluate("__ai"); check("pad: "+nm,got==want,got); until(pg,"!ATK.act",4)
        atk("RB tap = light melee","__pb[5].pressed=true;__pb[5].value=1",1,"__pb[5].pressed=false;__pb[5].value=0",0)
        pg.evaluate("__pb[5].pressed=true;__pb[5].value=1"); t0=pg.evaluate("performance.now()"); until(pg,"performance.now()-%f>450"%t0,3); wf(pg,4)
        check("pad: hold RB shows charge",pg.evaluate("PAD.charging")); pg.evaluate("__pb[5].pressed=false;__pb[5].value=0"); wf(pg,3); check("pad: hold RB = charged heavy",pg.evaluate("__ai")==1,pg.evaluate("__ai")); until(pg,"!ATK.act",4)
        atk("RT = special","__pb[7].pressed=true;__pb[7].value=1",2,"__pb[7].pressed=false;__pb[7].value=0",2)
        pg.evaluate("window.__ai=null"); btn(2); check("pad: X does not melee",pg.evaluate("__ai")is None)
        pg.evaluate("DASH.meter=1;DASH.t=0;PAD.ultCd=0"); pg.evaluate("window.__ai=null;__pb[3].pressed=true"); wf(pg,2); pg.evaluate("__pb[7].pressed=true;__pb[7].value=1"); wf(pg,3); pg.evaluate("__pb[7].pressed=false;__pb[7].value=0;__pb[3].pressed=false"); wf(pg,2)
        check("pad: RT+Y crew ultimate (no special fired)",pg.evaluate("PAD.last")=="ult" and pg.evaluate("__ai")!=2,pg.evaluate("[PAD.last,__ai]"))
        pg.evaluate("PAD.trickCd=0"); btn(3); check("pad: Y trick",pg.evaluate("PAD.last")=="trick")
        pg.evaluate("DASH.meter=.6;DASH.t=0;PAD.last=null"); wf(pg,2); pg.evaluate("__pb[11].pressed=true"); wf(pg,3); pg.evaluate("__pb[11].pressed=false"); wf(pg,2); check("pad: R3 crew move",pg.evaluate("PAD.last")=="crew")
        # X pickup
        r=pg.evaluate("(()=>{const c=cans.find(c=>c.visible&&!c.userData.got);if(!c)return null;Ride.group.position.set(0,0,-46);GATE.uiOpen=false;const p=Ride.group.position;c.position.x=p.x+2.2;c.position.z=p.z;return Stats.cans})()")
        if r is not None:
            btn(2,3); wf(pg,4); check("pad: X picks up nearby can",pg.evaluate("Stats.cans")>r,[r,pg.evaluate("Stats.cans")])
    if True:
     pg.evaluate("PHONE.up&&phoneSet(false);Ride.speed=0;Ride.group.position.set(0,0,-46)")
    # RB grapple
    n=pg.evaluate("GRAP.pts.length"); kinds=pg.evaluate("[...new Set(GRAP.pts.map(p=>p.kind))]"); print("grapple points",n,kinds,flush=True)
    check("grapple points at catwalks/rooftops/billboards",n>=8 and {"catwalk","rooftop","billboard"}<=set(kinds),kinds)
    pg.evaluate("""(()=>{const free=(x,z)=>onLand(x,z)&&!colliders.some(c=>!c.off&&x>c.minX-.6&&x<c.maxX+.6&&z>c.minZ-.6&&z<c.maxZ+.6);const g=GRAP.pts.find(p=>{if(p.kind!=='catwalk')return false;const fx=p.lx-p.x,fz=p.lz-p.z,L=Math.hypot(fx,fz);return [2,3.5,5].every(k=>free(p.x-fx/L*k,p.z-fz/L*k));})||GRAP.pts.find(p=>p.kind==='catwalk');window.__gp=g;GATE.uiOpen=false;if(typeof GRIND!=='undefined'){GRIND.on=null;GRIND.cd=5;}Ride.grinding=false;WALL.air=null;WALL.on=null;GRAP.deck=null;const fx=g.lx-g.x,fz=g.lz-g.z,L=Math.hypot(fx,fz);Ride.group.position.set(g.x-fx/L*5,0,g.z-fz/L*5);Ride.y=0;Ride.speed=0;Ride.yaw=Math.atan2(fx,fz);})()""")
    until(pg,"GRAP.target===__gp",10); check("grapple: D-left prompt when in range & facing",pg.evaluate("GRAP.target===__gp&&document.getElementById('grapPrompt').style.display==='block'&&/\u25C0/.test(document.getElementById('grapPrompt').textContent)"),pg.evaluate("(()=>{const p=Ride.group.position;return [GRAP.target&&GRAP.target.name,__gp.name,p.x,p.z,Ride.y,Ride.yaw,!!WALL.air,!!WALL.on,!!GRAP.deck,TGT.aiming,PHONE.up,MAP.open,State.mode,GATE.uiOpen]})()"))
    pg.screenshot(path=S+"grapple_prompt.png")
    pg.evaluate("Ride.yaw+=Math.PI"); wf(pg,3); check("grapple: no prompt when facing away",pg.evaluate("!GRAP.target")); pg.evaluate("Ride.yaw-=Math.PI"); until(pg,"GRAP.target===__gp",4)
    btn(14,2); check("grapple: D-pad left fires cable",pg.evaluate("!!GRAP.act&&GRAP.line.visible"),pg.evaluate("GRAP.act&&GRAP.act.dur"))
    d=pg.evaluate("GRAP.act?GRAP.act.dur:0"); check("grapple: pull time 0.6-1.0 s",.6<=d<=1.0,d)
    wf(pg,2); pg.screenshot(path=S+"grapple_pull.png")
    until(pg,"!GRAP.act",6); wf(pg,3); y=pg.evaluate("Ride.group.position.y")
    check("grapple: set on the ledge",pg.evaluate("GRAP.deck===__gp.deck")and abs(y-pg.evaluate("__gp.y"))<.1,[y,pg.evaluate("__gp.y")]); pg.screenshot(path=S+"grapple_ledge.png")
    pg.evaluate("GRAP.deck=null;Ride.y=0;Ride.group.position.y=0;Ride.group.position.set(0,0,-46)"); wf(pg,3)
    btn(13); check("pad: D-pad Down pings",pg.evaluate("!!PAD.ping"))
    btn(9); check("pad: Menu pauses",pg.evaluate("State.mode")=="pause",pg.evaluate("State.mode")); btn(9); wf(pg,3); check("pad: Menu resumes",pg.evaluate("State.mode")=="ride",pg.evaluate("State.mode"))
    pg.evaluate("navigator.getGamepads=()=>[]"); time.sleep(.3)
    check("no page errors",not errs,errs[:3])
    pg2=b.new_page(viewport={"width":1280,"height":720}); boot(pg2,U+"&controls"); pg2.evaluate("rideT=1"); time.sleep(.5)
    check("?controls shows overlay",pg2.evaluate("getComputedStyle(document.getElementById('objective')).display!=='none'"))
    pg2.screenshot(path=S+"phone_toptext_before.png")
    check("fps overlay hidden by default",pg.evaluate("!document.getElementById('fpsOverlay')"))
    pg.close(); pg2.close()
    pg3=b.new_page(viewport={"width":1280,"height":720}); boot(pg3,U+"&fps"); until(pg3,"FPSO.stat&&FPSO.stat.calls>0",8)
    st=pg3.evaluate("FPSO.stat"); print("fps overlay",st,flush=True)
    check("?fps overlay shows FPS/min/ms/calls/tris",pg3.evaluate("getComputedStyle(document.getElementById('fpsOverlay')).display!=='none'") and st and st["avg"]>0 and st["min"]>0 and st["calls"]>0 and st["tris"]>0,st)
    check("?fps XR panel is head-locked on camera",pg3.evaluate("FPSO.mesh.parent===camera"))
    pg3.screenshot(path=S+"fps_overlay.png")
    b.close()
print("RESULT",sum(c for _,c in res),"/",len(res))
