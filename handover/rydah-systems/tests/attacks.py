# Crew attacks: player move sets (Caali default, Ikki via ?player=ikki, every crew via ATK.set), hits + knockback + stagger on NPC riders,
# cooldowns, NPC counter-attacks on the player, pooled-FX draw calls.
from playwright.sync_api import sync_playwright
import time,json,sys
D="/workspace/v3build/shots/"; import os
B=os.environ.get("RYDAH_BASE","http://localhost:8765")+"/v3build/"+os.environ.get("RYDAH_PAGE","sky-rydahs-v3-ikki.html")+"?chars=/skyrydahs-characters/"
CREWS=["codee","karasu","static","behemoth","anubis","forest","genesis","ttt"]
ok=[]; peak=[0]
def check(n,c,i=""): ok.append(bool(c)); print(("PASS " if c else "FAIL ")+n,i,flush=True)
def waitfor(pg,e,t=40):
    t0=time.time()
    while time.time()-t0<t:
        if pg.evaluate(e): return True
        time.sleep(.15)
    return False
HELP="""window.__worldStick=true;window.__npc=c=>{const r=RIDERS.npcs.find(n=>n.g&&n.g.crew===c)||RIDERS.npcs[0]; if(!r) throw new Error('__npc('+c+'): RIDERS.npcs empty (ready='+!!RIDERS.ready+', mode='+State.mode+') - riders not loaded'); return r;};
window.__near=n=>{const g=n.g;Ride.group.position.set(g.pos[0]+Math.sin(g.th)*11,0,g.pos[1]+Math.cos(g.th)*11);Ride.speed=0;window.__camHook=null;camera.position.set(Ride.group.position.x,3,Ride.group.position.z);};
window.__face=(n,d)=>{/* Systems 20:15: drop the knockback offset the NPC loop already baked into holder.position (n._ap) BEFORE placing the player. Zeroing n.off alone left _ap stale,
  so the next frame's hp.sub(_ap) slid the target ~1.3 m (static K after J's knock 7: d 1.9 -> 3.24 > Angel Wing r 3.2, a whiff with cd running) */
  if(n._ap){n.holder.position.sub(n._ap);n._ap.set(0,0,0);} n._last=null; n.kv=null; if(n.off)n.off.set(0,0,0);
  const q=n.holder.position,g=n.g;const ox=Math.sin(g.th+1.2),oz=Math.cos(g.th+1.2);Ride.group.position.set(q.x+ox*d,0,q.z+oz*d);Ride.y=0;Ride.yaw=Math.atan2(q.x-Ride.group.position.x,q.z-Ride.group.position.z);Ride.speed=0;WALL.on=WALL.air=null;
  n.stun=0;n.kv=null;if(n.off)n.off.set(0,0,0);};
window.__cam=n=>{window.__camHook=()=>{const p=Ride.group.position,q=n.holder.position;const mx=(p.x+q.x)/2,mz=(p.z+q.z)/2,dx=q.x-p.x,dz=q.z-p.z,l=Math.hypot(dx,dz)||1;camera.position.set(mx-dz/l*6.5,3.2,mz+dx/l*6.5);camera.lookAt(mx,1.1,mz);};};
window.__DC0=()=>{const a=renderer.info.autoReset;renderer.info.autoReset=false;renderer.info.reset();renderer.render(scene,camera);const c=renderer.info.render.calls;renderer.info.autoReset=a;return c};
window.__freeze=on=>{for(const n of RIDERS.npcs){n.ph0=n.ph0??n.ph;} window.__npcFreeze=on;};0"""
NOPAD="garages.forEach(g=>g.gate&&(g.gate.dismissed=true));GATE.uiOpen=false;gateUI()"
def load(pg,url):
    pg.goto(url,timeout=120000); _rdy=waitfor(pg,"typeof RIDERS!='undefined'&&RIDERS.ready&&TURF.ready&&RIDERS.npcs.length>0",150)
    if not _rdy:
        print("FAIL page not ready (loud):",pg.evaluate("JSON.stringify({riders:typeof RIDERS!='undefined'&&!!RIDERS.ready,npcs:typeof RIDERS!='undefined'&&RIDERS.npcs?RIDERS.npcs.length:-1,turf:typeof TURF!='undefined'&&!!TURF.ready,S:typeof GRIND!='undefined'?GRIND.S.length:-1,err:(window.SR_ERRORS||[]).slice(0,5).map(String)})"),flush=True); print("RESULT 0 / 1"); import sys; sys.exit(2)
    time.sleep(3)
    # first-crew warm-up: Enter + fixed 1.5 s wall sleep could leave the game in the menu / pre-ride at ~2 fps, so the first crew's J/K keypresses were
    # eaten (cd stayed [0,0,0]). Wait for ride mode + move sets + ~0.5 s of game time before any case.
    for _ in range(10):
        if pg.evaluate("State.mode==='ride'"): break
        pg.keyboard.press("Enter"); waitfor(pg,"State.mode==='ride'",15)
    waitfor(pg,"typeof MOVESETS!=='undefined'&&typeof ATK!=='undefined'",30); pg.evaluate("window.__w0=clock"); waitfor(pg,"clock>__w0+.5",60); pg.evaluate(HELP); pg.evaluate("window.__npcPassive=true;window.__hideIkkiNpc=true"); pg.evaluate("if(!window.__atkLogHk){window.__atkLogHk=1;window.__atkLog=[];const f0=atkStart;atkStart=function(i,src){const r=f0.apply(this,arguments);if(src)__atkLog.push([+clock.toFixed(2),i,src,r,ATK.set,ATK.cd.map(v=>+v.toFixed(2)),!!ATK.act]);if(__atkLog.length>60)__atkLog.shift();return r}}")
def calls(pg):
    c=pg.evaluate("""new Promise(res=>{renderer.info.autoReset=false;let n=0,mx=0;renderer.info.reset();function f(){mx=Math.max(mx,renderer.info.render.calls);renderer.info.reset();if(++n<8)requestAnimationFrame(f);else{renderer.info.autoReset=true;res(mx);}}requestAnimationFrame(f);})""")
    peak[0]=max(peak[0],c); return c
def player_moves(pg,crew,shot,key_shot):
    pg.evaluate(f"ATK.set='{crew}';ATK.cd=[0,0,0];ATK.act=null")
    tc="static" if crew=="codee" else "codee"
    # hold the target still: mode-0 NPCs carve a 3.2 m loop every frame, and at headless ~1-3 fps they drift ~1-2 m between
    # __face() and the key press, so short moves (J dash, cones, dives) whiffed with stun 0. Idle mode = fixed spot. (__npcFreeze no longer exists in the build.)
    tgt=pg.evaluate(f"(()=>{{window.__T=__npc('{tc}');__T.mode0=__T.mode0??__T.mode;__T.mode=1;return __T.g.crew}})()")
    names=pg.evaluate(f"MOVESETS['{crew}'].moves.map(m=>m.name)")
    pg.evaluate("__near(__T)"); waitfor(pg,"__T.holder.visible&&__T.holder.position.lengthSq()>1",10)
    for i,k in enumerate("JKL"):
        waitfor(pg,"!ATK.act&&!WALL.air&&ATK.stun<=0",10); pg.evaluate("__face(__T,1.9);__cam(__T)"); time.sleep(.5); pg.evaluate(NOPAD); h0=pg.evaluate("ATK.hits"); n0=pg.evaluate("__T.hitN||0")
        pg.keyboard.press("Key"+k)
        if i==0: check(f"{crew} cooldown blocks spam",waitfor(pg,"ATK.cd[0]>0",4) and pg.evaluate("atkStart(0)===false"))
        if shot and k==key_shot: time.sleep(.12); pg.screenshot(path=D+shot); c=calls(pg)
        # wait on GAME time, not 8 s wall: a dive is ~1 s of airtime and lands (atkLand hit) only then; at headless ~2 fps with the
        # loop's per-frame dt cap, 8 s wall was ~0.45 s of game time (cd showed 4.05/4.5), so behemoth/anubis L were sampled mid-air.
        pg.evaluate("window.__c0=clock"); hit=waitfor(pg,f"ATK.hits>{h0}||(__T.hitN||0)>{n0}||clock>__c0+3",90) and pg.evaluate(f"ATK.hits>{h0}||(__T.hitN||0)>{n0}")
        st=pg.evaluate("JSON.stringify({stun:+(__T.stun||0).toFixed(2),off:+(__T.off?__T.off.length():0).toFixed(2),cd:ATK.cd.map(v=>+v.toFixed(2))})")
        check(f"{crew} {k} '{names[i]}' hits + knockback/stagger",hit,st)
        if not hit:
            f0=pg.evaluate("frame"); time.sleep(3)
            if pg.evaluate("frame")==f0: print("  LOOP DEAD at frame",f0,"errors:",json.dumps([e for e in errs if 'AudioContext' not in e][-4:])[:3000],flush=True); raise SystemExit(3)
        if not hit: print("  atkLog",pg.evaluate("JSON.stringify(window.__atkLog&&__atkLog.slice(-6))"),"T",pg.evaluate("JSON.stringify({d:+Math.hypot(__T.holder.position.x-Ride.group.position.x,__T.holder.position.z-Ride.group.position.z).toFixed(2),vis:__T.holder.visible,inT:atkTargets().includes(__T)})"),flush=True)
        if not hit: print("  diag",pg.evaluate("JSON.stringify({mode:State.mode,ui:typeof GATE!=='undefined'&&GATE.uiOpen,stun:ATK.stun,act:ATK.act&&{m:ATK.act.m.name,t:ATK.act.t,landed:ATK.act.landed},air:WALL.air&&{y:WALL.air.y,vy:WALL.air.vy,t:WALL.air.t},on:!!WALL.on,clock:clock,frame:frame,atkErr:window.__atkErr?String(window.__atkErr.stack||window.__atkErr).slice(0,400):null,animErr:animated.map((f,i)=>{try{f(clock);return null}catch(e){return i+': '+String(e.stack||e).slice(0,300)}}).filter(Boolean),cd:ATK.cd})"),flush=True)
        waitfor(pg,"!ATK.act&&!WALL.air",8); time.sleep(.3)
GPSTUB="""(()=>{ if(!window.__gp){ window.__gp={id:'stub',index:0,connected:true,mapping:'standard',axes:[0,0,0,0],buttons:Array.from({length:17},()=>({pressed:false,value:0})),timestamp:0}; window.__gpOrig=navigator.getGamepads.bind(navigator); }
  navigator.getGamepads=()=>[window.__gp,null,null,null]; })()"""
def commit_cases(pg):
    # ATTACK LOCK-COMMIT (Oliver via Ani 01:41). All waits on game time; target held still (mode 1) unless stated.
    def gw(sec,e=None,cap=300):
        c0=pg.evaluate("clock"); t0=time.time()
        while time.time()-t0<cap:
            if e and pg.evaluate(e): return True
            if pg.evaluate("clock")>=c0+sec: return bool(e and pg.evaluate(e))
            time.sleep(.1)
        return False
    def setup(crew,tc,d):
        pg.evaluate(f"ATK.set='{crew}';ATK.cd=[0,0,0];ATK.act=null;ATK.stun=0;WALL.on=WALL.air=null;ATK.commit=null;window.__T=__npc('{tc}');__T.mode0=__T.mode0??__T.mode;__T.mode=1;__near(__T)")
        waitfor(pg,"__T.holder.visible",10); gw(.3); pg.evaluate(f"__face(__T,{d});__cam(__T)"); gw(.2); pg.evaluate(NOPAD)
    # 1 commit-on-start (+ marker, draw delta 0): anubis J on the static rider
    setup("anubis","static",1.9); pg.keyboard.press("KeyJ"); gw(.6,"!!ATK.commit")
    r=pg.evaluate("(()=>{const C=ATK.commit; if(!C) return {c:null}; const a=__DC0(); atkCommitMarker(); const b=__DC0(); return {kind:C.kind,same:C.ref===__T,src:C.src,since:C.since,mk:!!ATK.markerShown,ret:TGT.ui&&TGT.ui.querySelector('#retLock').style.display!=='none',mesh:!!(TGT.mk&&TGT.mk.visible),dc:[a,b]}})()")
    check("commit-on-start: J commits to the attacked rider (ATK.commit.kind/target)", r.get("kind")=="enemy" and r.get("same"), r)
    check("commit marker: target.js lock reticle shown while committed, no 3D marker mesh, draw delta 0", r.get("mk") and r.get("ret") and not r.get("mesh") and r.get("dc") and r["dc"][0]==r["dc"][1], r)
    gw(1.5,"!ATK.act&&!ATK.commit"); check("commit released when the attack ends", pg.evaluate("!ATK.commit&&ATK.commitLog.slice(-1)[0].why==='done'"), pg.evaluate("JSON.stringify(ATK.commitLog.slice(-1))"))
    # 2 no-switch: ttt L dive at the static rider 3.2 m out; a second rider is moved CLOSER, right in the dive path, mid-attack
    setup("ttt","static",3.2); pg.evaluate("window.__U=atkTargets().find(n=>n!==__T)||RIDERS.npcs.find(n=>n!==__T&&n.holder);__U.mode0=__U.mode0??__U.mode;__U.mode=1")
    pg.keyboard.press("KeyL"); gw(.6,"!!ATK.commit&&!!WALL.air")
    pg.evaluate("(()=>{const p=Ride.group.position,q=__T.holder.position,h=__U.holder.position; window.__U0=h.clone(); window.__sw=[]; window.__uMin=1e9; window.__uIn=false; (function f(){ const p=Ride.group.position,q=__T.holder.position; if(ATK.act){ __U.holder.position.set(p.x+(q.x-p.x)*.35+.3,__U.holder.position.y,p.z+(q.z-p.z)*.35); __U.holder.visible=true; } if(ATK.commit){ __sw.push(ATK.commit.ref===__T&&(!ATK.act||!ATK.act.tgt||ATK.act.tgt===__T)); __uMin=Math.min(__uMin,Math.hypot(__U.holder.position.x-p.x,__U.holder.position.z-p.z)); window.__uIn=window.__uIn||atkTargets().includes(__U); } if(ATK.act) requestAnimationFrame(f); else __U.holder.position.copy(__U0); })(); })()")
    gw(3,"!ATK.act")
    sw=pg.evaluate("JSON.stringify({n:__sw.length,allT:__sw.every(Boolean),log:ATK.commitLog.slice(-1)[0],uMin:+__uMin.toFixed(2),tD:+Math.hypot(__T.holder.position.x-Ride.group.position.x,__T.holder.position.z-Ride.group.position.z).toFixed(2),uInT:__uIn})")
    SW=json.loads(sw); check("no-switch: second rider passing closer mid-dive never takes the commit", SW["allT"] and SW["n"]>0 and SW["uMin"]<2.5 and SW["uInT"], sw)
    pg.evaluate("__U.mode=__U.mode0")
    # 3 break-out by B and by flick (gamepad stub), during an L dive
    for how,js in [("B","__gp.buttons[1].pressed=true;__gp.buttons[1].value=1"),("flick","__gp.axes[0]=1")]:
        pg.evaluate(GPSTUB); pg.evaluate("__gp.axes[0]=0;__gp.axes[1]=0;__gp.buttons[1].pressed=false"); setup("ttt","static",3.2); gw(.2)
        pg.keyboard.press("KeyL"); gw(.6,"!!ATK.commit")
        pg.evaluate(js); gw(.3,"!ATK.commit")
        r=pg.evaluate("JSON.stringify({commit:!!ATK.commit,last:ATK.commitLog.slice(-1)[0],noHome:!!(ATK.act&&ATK.act.noHome)})")
        pg.evaluate("__gp.buttons[1].pressed=false;__gp.buttons[1].value=0;__gp.axes[0]=0"); gw(2,"!ATK.act&&!WALL.air")
        check(f"break-out by {how}: commit dropped mid-attack, homing stops", '"commit":false' in r and f'"why":"{how}"' in r, r)
    pg.evaluate("navigator.getGamepads=window.__gpOrig")
    # 4 object target: a taggable turf spot (no rider in the cone) -> J commits kind 'spot'
    sp=pg.evaluate("""(()=>{ if(typeof TURF==='undefined'||!TURF.spots) return null; for(const s of TURF.spots){ if(s.owner===TURF.me) continue; const x=s.x+s.nx*2.4, z=s.z+s.nz*2.4; if(!onLand(x,z)) continue;
        if(atkTargets().some(n=>Math.hypot(n.holder.position.x-x,n.holder.position.z-z)<16)) continue; if(colliders.some(c=>!c.off&&x>c.minX-.5&&x<c.maxX+.5&&z>c.minZ-.5&&z<c.maxZ+.5)) continue;
        return {x,z,yaw:Math.atan2(-s.nx,-s.nz),id:s.id??null}; } return null; })()""")
    if sp:
        pg.evaluate(f"ATK.set='anubis';ATK.cd=[0,0,0];ATK.act=null;ATK.commit=null;WALL.on=WALL.air=null;Ride.group.position.set({sp['x']},0,{sp['z']});Ride.y=0;Ride.speed=0;Ride.yaw={sp['yaw']};window.__camHook=null"); gw(.3); pg.evaluate(NOPAD)
        pg.keyboard.press("KeyJ"); gw(.6,"!!ATK.commit")
        r=pg.evaluate("JSON.stringify({kind:ATK.commit&&ATK.commit.kind,src:ATK.commit&&ATK.commit.src,mk:!!ATK.markerShown})"); gw(1.5,"!ATK.act")
        r+=" objHits="+str(pg.evaluate("ATK.objHits||0"))
        check("object target: attack at a taggable spot commits to the spot (kind 'spot', marker shown)", '"kind":"spot"' in r and '"mk":true' in r, r)
    else: check("object target: found a taggable spot clear of riders", False, "no spot")
with sync_playwright() as p:
    b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    pg=b.new_page(viewport={"width":1280,"height":720}); pg.set_default_timeout(150000); errs=[]
    pg.on("console",lambda m: errs.append(m.type+": "+m.text) if m.type in("error","warning") else None); pg.on("pageerror",lambda e: errs.append("PAGEERROR "+str(e)))
    _IK=os.environ.get("ATK_ONLY")=="ikki"   # Systems 12:03: Ikki-player section only (own window)
    if not _IK: load(pg,B)
    if os.environ.get("ATK_ONLY")=="commit": commit_cases(pg)
    if os.environ.get("ATK_ONLY") not in ("realsteer","moving","commit","tail","ikki"):   # moving: only the moving-target dive cases (Systems 01:45)
        if os.environ.get("ATK_ONLY")!="rest":   # Systems 11:05: ATK_ONLY=static + ATK_ONLY=rest = the full suite in two <=6 min windows
          check("8 crew move sets x 3 moves",pg.evaluate("Object.keys(MOVESETS).length===8&&Object.values(MOVESETS).every(s=>s.moves.length===3)"))
          player_moves(pg,"codee","attack_caali.png","K")
          for crew in CREWS[2:]+["karasu"]: player_moves(pg,crew,None,None)
        if os.environ.get("ATK_ONLY")=="static":   # Systems 19:55: static (non-moving target) player move cases only, J/K/L for every crew
            b.close(); print("RESULT",sum(ok),"/",len(ok)); raise SystemExit(0 if all(ok) else 1)
        # NPC riders use their own crew style against you (turf battle) -> attack_<crew>.png shows that crew's rider + FX
        for crew in CREWS[1:]:
            pg.evaluate(f"(()=>{{window.__N=__npc('{crew}');__near(__N);}})()"); waitfor(pg,"__N.holder.visible&&__N.holder.position.lengthSq()>1",10)
            pg.evaluate("__face(__N,2.0);__cam(__N)"); time.sleep(.4); pg.evaluate("__face(__N,2.0)")
            h0=pg.evaluate("ATK.playerHits||0"); r=pg.evaluate(f"(npcAttack(__N),(ATK.playerHits||0)>{h0}&&ATK.lastNpc.crew==='{crew}'&&ATK.stun>0&&!!ATK.pk)"); time.sleep(.1); pg.screenshot(path=D+f"attack_{crew}.png"); calls(pg)
            check(f"NPC {crew} attacks with own style + player knockback/stagger",r,pg.evaluate("JSON.stringify(ATK.lastNpc)"))
            time.sleep(.6)
        # mouse + menus untouched
        pg.evaluate("window.__N=__npc('static');__near(__N)"); waitfor(pg,"__N.holder.visible",10); waitfor(pg,"ATK.stun<=0&&!ATK.act",10); pg.evaluate("ATK.cd=[0,0,0];__face(__N,1.9);__cam(__N)"); time.sleep(.3); pg.evaluate(NOPAD); h0=pg.evaluate("ATK.hits"); pg.mouse.click(640,360); check("left mouse = light attack",waitfor(pg,f"ATK.hits>{h0}",6))
        print("peak calls during attacks (noFX)",peak[0])
    # moving-target dives (Ani 09:39): anubis L 'Ankh Dive' + ttt L 'Tool Drop' vs a target strafing 3 m/s sideways (game-time driven), then each dive vs the NPC's own loop motion
    pg.evaluate("""window.__strafe=(n,v)=>{ window.__stOn=true; let c0=clock; (function f(){ if(!window.__stOn) return; const dt=clock-c0; c0=clock; n.off=n.off||new THREE.Vector3(); const p=Ride.group.position,q=n.holder.position,dx=q.x-p.x,dz=q.z-p.z,l=Math.hypot(dx,dz)||1; if(!(n.stun>0)) { n.off.x+=-dz/l*v*dt; n.off.z+=dx/l*v*dt; } requestAnimationFrame(f); })(); };0""")
    def gwait(sec,e,cap=90):
        c0=pg.evaluate("clock"); t0=time.time()
        while time.time()-t0<cap:
            if e and pg.evaluate(e): return True
            if pg.evaluate("clock")>=c0+sec: return bool(e and pg.evaluate(e))
            time.sleep(.1)
        return False
    for crew in ([] if os.environ.get("ATK_ONLY") in ("realsteer","tail","ikki") else ["anubis","ttt"]):
        for mode in ["strafe","loop"]:
            pg.evaluate(f"ATK.set='{crew}';ATK.cd=[0,0,0];ATK.act=null;window.__T=__npc('{'static' if crew!='static' else 'codee'}');__T.mode=__T.mode0??__T.mode;__near(__T)")
            waitfor(pg,"__T.holder.visible",10); gwait(1,"!ATK.act&&!WALL.air&&ATK.stun<=0")
            pg.evaluate("__face(__T,3.2);__cam(__T)"); pg.evaluate(NOPAD)
            if mode=="strafe": pg.evaluate("__strafe(__T,3)")
            gwait(.3,None)
            n0=pg.evaluate("__T.hitN||0"); pg.evaluate("window.__dv0={c:clock,f:frame};window.__dvA=null;(function lf(){ if(ATK.act&&ATK.act.m.kind==='dive') window.__dvA=ATK.act; if(window.__dv0&&clock<__dv0.c+4) requestAnimationFrame(lf); })()"); pg.keyboard.press("KeyL")
            # Systems 01:45: judge on GAME time with a generous wall cap and only once the dive is over. The old 90 s wall cap expired at the
            # integrator's very low fps after ~2 dive frames (homed:2, act still alive), so a dive still in the air was scored as a miss.
            cond=f"(__T.hitN||0)>{n0}||__T.stun>0"
            hit=gwait(3,cond,cap=420)
            if not hit: hit=gwait(3,f"{cond}||(clock>__dv0.c+.3&&!ATK.act)",cap=300) and pg.evaluate(cond)
            info=pg.evaluate("JSON.stringify({stun:+(__T.stun||0).toFixed(2),homed:(__dvA&&__dvA.homed)||0,locked:!!(__dvA&&__dvA.tgt),landed:!!(__dvA&&__dvA.landed),actAlive:!!ATK.act,gameT:+(clock-__dv0.c).toFixed(2),frames:frame-__dv0.f,d:+Math.hypot(__T.holder.position.x-Ride.group.position.x,__T.holder.position.z-Ride.group.position.z).toFixed(2)})")
            pg.evaluate("window.__stOn=false"); gwait(1.5,"!ATK.act&&!WALL.air")
            ci=pg.evaluate("JSON.stringify((ATK.commitLog||[]).slice(-1)[0]||null)"); info+=" commit="+ci
            check(f"{crew} L dive hits a MOVING target ({mode})",hit and '"homed":0' not in info and not pg.evaluate("!!window.__atkErr"),info+" atkErr="+str(pg.evaluate("window.__atkErr?String(window.__atkErr).slice(0,200):null")))
            if crew=="anubis" and mode=="strafe": check("anubis L strafe: dive committed to the strafing target (lock-commit)",'"kind":"enemy"' in ci and '"static"' in ci,ci)
        if os.environ.get("ATK_ONLY") in ("moving","commit","rest") and crew=="ttt": b.close(); print("RESULT",sum(ok),"/",len(ok)); raise SystemExit(0 if all(ok) else 1)
    # real-player steering (Ani 13:19): NO __worldStick. Camera behind the rider looking at the target, hold W (camera-forward), J when close; then L dive.
    if not _IK: pg.evaluate("window.__worldStick=false")
    for k,mv in ([] if _IK else [("J",0),("L",2)]):
        # clean state from the earlier cases: target idle (mode 1 = fixed spot; mode0 is the 3.2 m loop the moving-dive cases restored),
        # strafe hook off, no leftover player stun/attack/air (ATK.stun>0 zeroes Input.mag and blocks attacks)
        pg.evaluate("window.__stOn=false;ATK.set='anubis';ATK.cd=[0,0,0];ATK.act=null;ATK.stun=0;WALL.on=WALL.air=null;window.__T=__npc('static');__T.mode0=__T.mode0??__T.mode;__T.mode=1;__near(__T)"); waitfor(pg,"__T.holder.visible",10); gwait(.3,None)
        pg.evaluate("""(()=>{const q=__T.holder.position,g=__T.g,ox=Math.sin(g.th+1.2),oz=Math.cos(g.th+1.2);Ride.group.position.set(q.x+ox*7,0,q.z+oz*7);Ride.y=0;Ride.speed=0;WALL.on=WALL.air=null;
          Ride.yaw=Math.atan2(-ox,-oz); /* face the target (was atan2(-oz,ox): 90 deg off, so the follow cam the camrel latch reads on the first W frame pointed sideways) */ __T.stun=0;__T.kv=null;if(__T.off)__T.off.set(0,0,0);
          window.__camHook=()=>{const p=Ride.group.position,q=__T.holder.position,dx=q.x-p.x,dz=q.z-p.z,l=Math.hypot(dx,dz)||1;camera.position.set(p.x-dx/l*5,p.y+2.4,p.z-dz/l*5);camera.lookAt(q.x,1,q.z);};})()""")
        gwait(.3,None)  # let __camHook place the camera before W latches the camera-relative heading
        pg.evaluate(NOPAD); n0=pg.evaluate("__T.hitN||0"); pg.keyboard.down("KeyW")
        near=False; c0=pg.evaluate("clock"); t0=time.time()
        while time.time()-t0<120 and pg.evaluate("clock")<c0+6:
            if pg.evaluate(f"Math.hypot(__T.holder.position.x-Ride.group.position.x,__T.holder.position.z-Ride.group.position.z)<3.5"): near=True; break
            time.sleep(.1)
        cr=pg.evaluate("JSON.stringify({ref:PAD.camRel&&PAD.camRel.ref,on:PAD.camRel&&PAD.camRel.on,mag:Input.mag,ws:!!window.__worldStick,stun:ATK.stun})")  # sampled while W is still held
        pg.keyboard.up("KeyW"); pg.keyboard.press("Key"+k)
        pg.evaluate("window.__c0=clock"); hit=waitfor(pg,f"(__T.hitN||0)>{n0}||__T.stun>0||clock>__c0+3",90) and pg.evaluate(f"(__T.hitN||0)>{n0}||__T.stun>0")
        info=pg.evaluate(f"JSON.stringify({{near:{str(near).lower()},stun:+(__T.stun||0).toFixed(2),cd:ATK.cd.map(v=>+v.toFixed(2)),crErr:!!window.__crErr}})")+" held="+cr
        check(f"real steering (camera-relative W, no __worldStick): anubis {k} approaches + hits, stun>0, cooldown starts",near and hit and pg.evaluate(f"ATK.cd[{mv}]>0||__T.stun>0"),info)
        waitfor(pg,"!ATK.act&&!WALL.air",8); pg.evaluate("window.__camHook=null")
    if not _IK: pg.evaluate("window.__worldStick=true")
    if os.environ.get("ATK_ONLY")=="realsteer": b.close(); print("RESULT",sum(ok),"/",len(ok)); raise SystemExit(0 if all(ok) else 1)
    E=[e for e in errs if "Custom UV" not in e]
    if os.environ.get("ATK_ONLY")=="tail": b.close(); check("no errors",not any("PAGEERROR" in e or "atk" in e.lower() for e in E),json.dumps(E[:6])); print("RESULT",sum(ok),"/",len(ok)); raise SystemExit(0 if all(ok) else 1)
    if not _IK: check("no errors",not any("PAGEERROR" in e or "atk" in e.lower() for e in E),json.dumps(E[:6]))
    # Ikki player
    load(pg,B+"&player=ikki"); check("ikki uses Kogarasumaru set",pg.evaluate("atkSet().who.startsWith('Ikki')"))
    pg.evaluate("ATK.set=null"); player_moves(pg,"karasu","attack_ikki.png","J")
    pg.evaluate("__near(__T)"); time.sleep(1); pg.evaluate("__face(__T,3);__cam(__T);ATK.cd=[0,0,0]"); time.sleep(.4); pg.evaluate(NOPAD); pg.keyboard.press("KeyL"); time.sleep(.35); pg.screenshot(path=D+"attack_ikki_dive.png")
    b.close()
print("peak",peak[0]); print("RESULT",sum(ok),"/",len(ok))
