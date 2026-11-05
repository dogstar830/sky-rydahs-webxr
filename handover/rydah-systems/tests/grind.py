# Locked-in grind: snap, lock, ride to end, uphill/downhill speed, early A jump-off, B drop (momentum kept), keyboard fallbacks,
# palm trunk climb + pop, spark pool cap, rumble, vortex, drag profiles, draw calls, iLink controls text, shots/grind_*.png
from playwright.sync_api import sync_playwright
import time,json,math,os
D="/workspace/v3build/shots/"; B=os.environ.get("RYDAH_BASE","http://localhost:8765")+"/v3build/sky-rydahs-v3-ikki.html?chars=/skyrydahs-characters/"
ok=[]
def check(n,c,i=""): ok.append(bool(c)); print(("PASS " if c else "FAIL ")+n,i,flush=True)
def frames(pg,n=3):
    f=pg.evaluate("frame"); waitfor(pg,f"frame>{f+n}",20)
def hold(pg,i,cond,t=8):
    pg.evaluate(f"__btn({i},true)"); r=waitfor(pg,cond,t); pg.evaluate(f"__btn({i},false)"); frames(pg); return r
def key(pg,k,cond,t=8):
    pg.keyboard.press(k); r=waitfor(pg,cond,t); frames(pg); return r
def ridet(pg,t): return waitfor(pg,f"!GRIND.on||GRIND.on.t>{t}",30)
def waitfor(pg,e,t=20):
    t0=time.time()
    while time.time()-t0<t:
        if pg.evaluate(e): return True
        time.sleep(.08)
    return False
STUB="""window.__rumble=0;window.__gp={connected:true,id:'Xbox stub',index:0,mapping:'standard',timestamp:0,axes:[0,0,0,0],
 buttons:Array.from({length:17},()=>({pressed:false,touched:false,value:0})),vibrationActuator:{type:'dual-rumble',playEffect:()=>{window.__rumble++;return Promise.resolve('complete');}}};
navigator.getGamepads=()=>[window.__gp];"""
HELP="""window.__btn=(i,on)=>{__gp.buttons[i].pressed=on;__gp.buttons[i].value=on?1:0;};
window.__pick=k=>{const r=GRIND.S.filter(s=>s.kind===k&&s.L>12&&s.pts.every(p=>onLand(p.x,p.z))).sort((a,b)=>b.L-a.L)[0]; if(!r) throw new Error('__pick('+k+'): no spline (GRIND.S='+GRIND.S.length+', world='+!!GRIND.world+', mode='+State.mode+') - page not ready or splines missing'); return r;};
window.__air=(s,arc,sp)=>{GRIND.on=null;GRIND.cd=0;GRIND.ignore=null;const q=grindAt(s,arc,new THREE.Vector3()),t=new THREE.Vector3();grindAt(s,arc+.5,new THREE.Vector3(),t);
  Ride.group.position.set(q.x-t.x*.6,q.y+.5,q.z-t.z*.6);Ride.y=q.y+.5;WALL.on=null;wallLaunch(t.x*sp,t.z*sp,-1,false);WALL.air.y=q.y+.5;WALL.air.t=.3;};
window.__lock=(s,arc,dir,v)=>{GRIND.on=null;const q=grindAt(s,arc,new THREE.Vector3());Ride.group.position.copy(q);WALL.air=WALL.on=null;grindLock(s,arc,dir,v,1);GRIND.on.grip=0;};
window.__free=(x,z)=>!colliders.some(c=>!c.off&&x>c.minX-.6&&x<c.maxX+.6&&z>c.minZ-.6&&z<c.maxZ+.6);window.__follow=(side,h,back)=>{window.__camHook=()=>{const p=Ride.group.position,y=Ride.yaw;camera.position.set(p.x-Math.sin(y)*(back||5)+Math.cos(y)*(side||2.5),p.y+(h||1.6),p.z-Math.cos(y)*(back||5)-Math.sin(y)*(side||2.5));camera.lookAt(p.x+Math.sin(y)*3,p.y+.6,p.z+Math.cos(y)*3);};};0"""
DAY="""window.__day=()=>{scene.traverse(o=>{if(o.isHemisphereLight){o.intensity=1.1;o.color.set(0xdfeaff);o.groundColor.set(0x8a8478);} if(o.isDirectionalLight){o.intensity=Math.max(o.intensity,1.4);o.color.set(0xfff3e0);}});
 scene.fog.color.set(0xb8c8e0);if(typeof _fogBase!=='undefined')_fogBase.set(0xb8c8e0);scene.background.set(0x9ab8e0);};
 window.__dayHook=()=>{const h=window.__camHook;window.__camHook=()=>{__day();h&&h();};};__day();__dayHook();"""
CALLS="""new Promise(res=>{renderer.info.autoReset=false;let n=0,mx=0;renderer.info.reset();function f(){mx=Math.max(mx,renderer.info.render.calls);renderer.info.reset();if(++n<8)requestAnimationFrame(f);else{renderer.info.autoReset=true;res(mx);}}requestAnimationFrame(f);})"""
with sync_playwright() as p:
    b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    pg=b.new_page(viewport={"width":1280,"height":720}); pg.set_default_timeout(150000); errs=[]
    pg.add_init_script(STUB)
    pg.on("pageerror",lambda e: errs.append("PAGEERROR "+str(e))); pg.on("console",lambda m: errs.append(m.text) if m.type in("error","warning") and "grind" in m.text.lower() else None)
    pg.goto(B,timeout=120000); _rdy=waitfor(pg,"typeof RIDERS!='undefined'&&RIDERS.ready&&TURF.ready",150)
    if not _rdy:
        print("FAIL page not ready (loud):",pg.evaluate("JSON.stringify({riders:typeof RIDERS!='undefined'&&!!RIDERS.ready,npcs:typeof RIDERS!='undefined'&&RIDERS.npcs?RIDERS.npcs.length:-1,turf:typeof TURF!='undefined'&&!!TURF.ready,S:typeof GRIND!='undefined'?GRIND.S.length:-1,err:(window.SR_ERRORS||[]).slice(0,5).map(String)})"),flush=True); print("RESULT 0 / 1"); import sys; sys.exit(2)
    time.sleep(3)
    pg.keyboard.press("Enter"); time.sleep(1.5)
    for _k in range(6):  # wait until startRide() has actually run (it teleports to spawn 0,0,16); at 1-3 fps Enter can land seconds later
        if waitfor(pg,"State.mode==='ride'",20): break
        pg.keyboard.press("Enter")
    frames(pg,3); pg.evaluate(HELP); pg.evaluate("window.__npcPassive=true;window.__npcFreeze=true;window.__hideIkkiNpc=true;garages.forEach(g=>g.gate&&(g.gate.dismissed=true));if(typeof GATE!='undefined'){GATE.uiOpen=false;}")
    if not waitfor(pg,"GRIND.world&&GRIND.S.length>0",60): print("FAIL GRIND.world/splines never ready (loud)",pg.evaluate("[GRIND.S.length,!!GRIND.world]"),flush=True); import sys; sys.exit(2)
    cnt=pg.evaluate("(()=>{const c={};for(const s of GRIND.S)c[s.kind]=(c[s.kind]||0)+1;return c})()"); print("splines",cnt)
    check("cables/poles/bridge/palm splines registered",all(cnt.get(k,0)>0 for k in ["cable","pole","lamp","stay","main","rail","trunk","frond","zip"]),cnt)
    check("ride radius >= 8 cm (cables .09, stays .12, mains .22, rails .09)",pg.evaluate("GRIND.S.filter(s=>s.kind!=='frond').every(s=>s.r>=.08)"))
    check("drag profile: bark > cable > steel",pg.evaluate("GRIND.MAT.bark.mu>GRIND.MAT.cable.mu&&GRIND.MAT.cable.mu>GRIND.MAT.steel.mu&&GRIND.MAT.cable.k>GRIND.MAT.steel.k"))
    # 1. snap + lock from the air onto a telephone cable, ride to the end, pop off
    pg.evaluate("window.__c=__pick('cable');__follow(2.5,1.4,5);__air(__c,2,14)")
    st=waitfor(pg,"!!GRIND.on",15); check("air -> snaps + locks onto cable",st and pg.evaluate("GRIND.on.s===__c"))
    d=pg.evaluate("(()=>{const n=grindNear(Ride.group.position,3);return n?n.d:9})()"); check("snapped onto the spline",d<.35,round(d,3))
    ridet(pg,.4); check("locked: rides along automatically (no input)",pg.evaluate("!!GRIND.on&&GRIND.on.arc>3&&Ride.grinding"),pg.evaluate("GRIND.on&&[GRIND.on.arc,GRIND.on.v]"))
    pg.screenshot(path=D+"grind_cable_night.png"); calls=pg.evaluate(CALLS); print("draw calls grinding (night, FX on)",calls)
    st=waitfor(pg,"GRIND.stats.ends>0",90); le=pg.evaluate("GRIND.lastExit"); check("rides to the end and pops off with momentum",st and le and le["kind"]=="end" and le["h"]>3 and pg.evaluate("!!WALL.air||Ride.speed>2"),le)
    # 2. uphill / downhill on a bridge stay cable (top = pts[0])
    up=pg.evaluate("window.__s=GRIND.S.filter(s=>s.kind==='stay'&&s.pts.every(p=>onLand(p.x,p.z))).sort((a,b)=>Math.abs(b.pts[0].y-b.pts[b.pts.length-1].y)/b.L-Math.abs(a.pts[0].y-a.pts[a.pts.length-1].y)/a.L)[0];__lock(__s,__s.L*.75,-1,12);0"); ridet(pg,.5); v=pg.evaluate("GRIND.on?GRIND.on.v:-1"); check("uphill: slows down",0<v<11.5,round(v,2))
    pg.evaluate("__lock(__s,__s.L*.2,1,12)"); ridet(pg,.5); v2=pg.evaluate("GRIND.on?GRIND.on.v:-1"); check("downhill: speeds up",v2>12.3,round(v2,2)); check("downhill faster than uphill",v2>v)
    pg.evaluate("__follow(-3,2.2,7)"); time.sleep(.2); pg.screenshot(path=D+"grind_bridge_cable.png")
    # 3. early jump-off: A (gamepad) pops up, B (gamepad) drops with momentum
    m=pg.evaluate("window.__m=GRIND.S.filter(s=>s.kind==='main')[0];__lock(__m,10,1,14);0"); ridet(pg,.2); v0=pg.evaluate("GRIND.on.v")
    hold(pg,0,"!GRIND.on"); le=pg.evaluate("GRIND.lastExit")
    check("A = early jump-off (pops up, keeps momentum)",pg.evaluate("!GRIND.on") and le["kind"]=="jump" and le["vy"]>5 and le["h"]>=.6*v0,le)
    pg.evaluate("__lock(__m,10,1,14)"); ridet(pg,.2); v0=pg.evaluate("GRIND.on.v"); hold(pg,1,"!GRIND.on"); le=pg.evaluate("GRIND.lastExit")
    check("B = drop off (no pop, keeps momentum)",pg.evaluate("!GRIND.on") and le["kind"]=="drop" and le["vy"]<=0.01 and math.hypot(le["h"],le["vy"])>=.85*v0,le)
    check("no instant re-lock after B drop",not pg.evaluate("!!GRIND.on"))
    for frac,lab in [(.1,"start"),(.5,"mid"),(.9,"near end")]:
        pg.evaluate(f"__lock(__m,__m.L*{frac},1,12)"); ridet(pg,.15); hold(pg,0,"!GRIND.on")
        r=pg.evaluate("[!GRIND.on,GRIND.lastExit.kind,GRIND.stats]"); check(f"A ends the grind at any point ({lab})",r[0] and r[1]=="jump",r)
    pg.evaluate("__lock(__m,10,1,12)"); ridet(pg,.15); key(pg,"Space","!GRIND.on"); r=pg.evaluate("[!GRIND.on,GRIND.lastExit.kind,GRIND.on&&GRIND.on.arc]"); check("keyboard Space jump-off",r[0] and r[1]=="jump",r)
    pg.evaluate("__lock(__m,10,1,12)"); ridet(pg,.15); key(pg,"KeyC","!GRIND.on"); check("keyboard C drop",pg.evaluate("!GRIND.on&&GRIND.lastExit.kind==='drop'"))
    # 4. kick (L3) adds momentum
    pg.evaluate("__lock(__m,8,1,10)"); ridet(pg,.15); a=pg.evaluate("GRIND.on.v"); hold(pg,10,"GRIND.stats.kicks>0"); b2=pg.evaluate("GRIND.on?GRIND.on.v:0")
    check("L3 kick adds momentum",b2>a+2.5,(round(a,2),round(b2,2)))
    # 5. spark pool cap + vortex + rumble
    pg.evaluate("__lock(__m,20,1,38)"); ridet(pg,.8); sp=pg.evaluate("[GRIND.spk.n,GRIND.spk.alive(),GRIND.spk.pos.length/3]")
    check("spark pool capped at 160",sp[0]==160 and sp[2]==160 and 30<sp[1]<=160,sp)
    check("vortex focus quad active at speed",pg.evaluate("GRIND.vortex.visible&&GRIND.vk>.3"),pg.evaluate("GRIND.vk"))
    check("rumble via vibrationActuator",pg.evaluate("__rumble")>3,pg.evaluate("__rumble"))
    hold(pg,1,"!GRIND.on")
    # 6. palm trunk: skate into it -> climb -> pop at the crown (bark chips)
    tr=pg.evaluate("""(()=>{const L=GRIND.S.filter(s=>s.kind==='trunk');for(const s of L){const b=s.pts[0];for(let a=0;a<6.3;a+=.5){const x=b.x+Math.sin(a)*2.2,z=b.z+Math.cos(a)*2.2;if(onLand(x,z)&&__free(x,z)&&__free((x+b.x)/2,(z+b.z)/2)&&__free(b.x+(x-b.x)*.3,b.z+(z-b.z)*.3)){window.__t=s;window.__ta=[x,z,Math.atan2(b.x-x,b.z-z)];return [b.x,b.z,s.L];}}}return null;})()""" if pg.evaluate("typeof __free!=='undefined'") else "0")
    if not tr:
        pg.evaluate("window.__free=(x,z)=>!colliders.some(c=>!c.off&&x>c.minX-.6&&x<c.maxX+.6&&z>c.minZ-.6&&z<c.maxZ+.6)")
        tr=pg.evaluate("""(()=>{const L=GRIND.S.filter(s=>s.kind==='trunk');for(const s of L){const b=s.pts[0];for(let a=0;a<6.3;a+=.5){const x=b.x+Math.sin(a)*2.2,z=b.z+Math.cos(a)*2.2;if(onLand(x,z)&&__free(x,z)&&__free((x+b.x)/2,(z+b.z)/2)&&__free(b.x+(x-b.x)*.3,b.z+(z-b.z)*.3)){window.__t=s;window.__ta=[x,z,Math.atan2(b.x-x,b.z-z)];return [b.x,b.z,s.L];}}}return null;})()""")
    check("found a palm trunk",tr,tr)
    if tr:
        waitfor(pg,"!WALL.air",4); pg.evaluate("GRIND.on=null;GRIND.cd=0;GRIND.ignore=null;WALL.air=WALL.on=null;Ride.y=0;Ride.group.position.set(__ta[0],0,__ta[1]);Ride.yaw=__ta[2];Ride.speed=13;window.__camHook=()=>{const b=__t.pts[0],e=__t.pts[__t.pts.length-1],p=Ride.group.position,dx=b.x-__ta[0],dz=b.z-__ta[1],l=Math.hypot(dx,dz)||1;camera.position.set(b.x-dx/l*4.5+dz/l*3.5,Math.max(1.6,p.y*.6+1.5),b.z-dz/l*4.5-dx/l*3.5);camera.lookAt(b.x,Math.max(1.4,p.y*.8+.6),b.z);}")
        st=waitfor(pg,"GRIND.on&&GRIND.on.s===__t",15); check("skate into palm -> locks onto trunk (bark)",st)
        ridet(pg,.3); y=pg.evaluate("Ride.group.position.y"); check("climbs the trunk",y>1.5,round(y,2)); pg.screenshot(path=D+"grind_palm.png")
        check("bark particles mixed in (wood/leaf colours)",pg.evaluate("(()=>{const S=GRIND.spk;let n=0;for(let i=0;i<S.n;i++)if(S.life[i]>0&&S.base[i*3+1]>S.base[i*3+2]+.15&&S.base[i*3]<.7)n++;return n})()")>0)
        st=waitfor(pg,"!GRIND.on",40); le=pg.evaluate("GRIND.lastExit"); check("pops off at the crown",st and le["kind"]=="end" and le["vy"]>0,le)
    # 6b. lock discipline: glancing pole pass, aligned rail wins, jump-on, cooldown
    pg.evaluate("""window.__spot=(()=>{for(let x=-40;x<=260;x+=6)for(let z=-200;z<=200;z+=6){let f=onLand(x,z);for(let a=-9;a<=9&&f;a+=1.5)for(let b=-9;b<=9&&f;b+=1.5)if(!onLand(x+a,z+b)||!__free(x+a,z+b))f=false;
      if(f&&!grindAll(new THREE.Vector3(x,0,z),9).length&&!GRIND.S.some(s=>s.pts.some(p=>Math.hypot(p.x-x,p.z-z)<12)))return [x,z];}return null;})();
      window.__ground=()=>{GRIND.on=null;GRIND.cd=0;GRIND.ignore=null;WALL.air=WALL.on=null;Ride.y=0;GRIND.prevP=null;};0""")
    spot=pg.evaluate("__spot"); check("found free test area",spot,spot)
    if spot:
        # synthetic pole (vertical steel) + two rails, added through the normal registry
        pg.evaluate("""(()=>{const [x,z]=__spot;window.__pole=grindAdd([[x,.2,z],[x,4,z],[x,8,z]],'steel',.12,{vert:true,kind:'lamp'});
          window.__rA=grindAdd([[x+4,.6,z-8],[x+4,.6,z+8]],'steel',.09,{kind:'rail'}); window.__rB=grindAdd([[x+4.35-8*Math.sin(.7),.6,z-3-8*Math.cos(.7)],[x+4.35+8*Math.sin(.7),.6,z-3+8*Math.cos(.7)]],'steel',.09,{kind:'rail'}); grindGridBuild();})()""")
        pg.evaluate("__ground();const [x,z]=__spot;Ride.group.position.set(x+.5,0,z-6);Ride.yaw=0;Ride.speed=12;window.__camHook=null;window.__l0=GRIND.stats.locks;")
        waitfor(pg,"Ride.group.position.z>__spot[1]+4",15); check("skating past a pole at 0.5 m does not lock",pg.evaluate("GRIND.stats.locks===__l0&&!GRIND.on"),pg.evaluate("[GRIND.stats.locks-__l0,GRIND.lastPick]"))
        pg.evaluate("__ground();const [x,z]=__spot;Ride.group.position.set(x,0,z-5);Ride.yaw=0;Ride.speed=12;")
        st=waitfor(pg,"GRIND.on&&GRIND.on.s===__pole",15); check("head-on skate into pole locks",st); hold(pg,1,"!GRIND.on")
        # aligned rail wins over the closer, angled one (falling between them, nearer B)
        pg.evaluate("__ground();const [x,z]=__spot;Ride.group.position.set(x+4.3,1.0,z-3);Ride.y=1;wallLaunch(0,10,-2,false);WALL.air.y=1.0;WALL.air.t=.3;")
        st=waitfor(pg,"!!GRIND.on",10); r=pg.evaluate("GRIND.on&&[GRIND.on.s===__rA,GRIND.lastPick]"); check("two candidate rails in range: velocity-aligned one wins over the closer angled one",st and r and r[0] and r[1]["cands"]>=2,r)
        hold(pg,1,"!GRIND.on")
        # cooldown: right after a B drop, overlapping the rail must not re-lock for 0.4 s (game time)
        r=pg.evaluate("(()=>{const [x,z]=__spot;GRIND.on=null;__lock(__rA,8,1,10);return 1})()"); ridet(pg,.1); hold(pg,1,"!GRIND.on")
        pg.evaluate("const [x,z]=__spot;Ride.group.position.set(x+4,.75,z);WALL.air.y=.75;WALL.air.vx=0;WALL.air.vz=10;WALL.air.vy=-1;window.__cd0=GRIND.cdSet;window.__lk=GRIND.stats.locks;")
        f0=pg.evaluate("frame"); waitfor(pg,"GRIND.cd<=0||!!GRIND.on",10); r=pg.evaluate("[GRIND.stats.locks-__lk,__cd0,GRIND.cd]")
        check("0.4 s re-lock cooldown holds (all rails)",r[0]==0 and abs(r[1]-.4)<1e-6,r)
        # jump-on: skating beside the rail, press A -> hop -> lands and locks
        pg.evaluate("__ground();const [x,z]=__spot;Ride.group.position.set(x+3.3,0,z-7);Ride.yaw=.12;Ride.speed=10;window.__lk=GRIND.stats.locks;")
        frames(pg,2); hold(pg,0,"!!WALL.air||!!GRIND.on",4); st=waitfor(pg,"!!GRIND.on",10); check("jump-on (A hop) locks onto the rail",st and pg.evaluate("GRIND.on.s===__rA"),pg.evaluate("GRIND.lastPick"))
        hold(pg,1,"!GRIND.on")
    # 7. pole close-up + day cable shot
    pg.evaluate("""(()=>{const s=GRIND.S.find(s=>s.kind==='pole');const b=s.pts[0];Ride.group.position.set(b.x+1.5,0,b.z+1.5);window.__camHook=()=>{camera.position.set(b.x+1.6,8.6,b.z+2.2);camera.lookAt(b.x,9.8,b.z);};})()""")
    time.sleep(.8); pg.screenshot(path=D+"grind_pole_closeup.png")
    pg.evaluate("__follow(2.5,1.4,5)"); pg.evaluate(DAY); pg.evaluate("__air(__c,2,14)"); waitfor(pg,"!!GRIND.on",15); ridet(pg,.4); pg.screenshot(path=D+"grind_cable_day.png"); calls2=pg.evaluate(CALLS)
    check("draw calls < 300 while grinding",max(calls,calls2)<300,(calls,calls2))
    # 8. iLink settings controls text
    ctl=pg.evaluate("PH_CTRL.join(' | ')"); check("iLink controls list: B drop / A pop / auto-lock",("DROP OFF" in ctl) and ("POP" in ctl) and ("auto-locks" in ctl),ctl)
    E=[e for e in errs if "Custom UV" not in e]; check("no errors",not any("PAGEERROR" in e or "grind" in e.lower() for e in E),json.dumps(E[:6]))
    b.close()
print("RESULT",sum(ok),"/",len(ok))
