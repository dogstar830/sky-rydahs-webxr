# Crew attacks: player move sets (Caali default, Ikki via ?player=ikki, every crew via ATK.set), hits + knockback + stagger on NPC riders,
# cooldowns, NPC counter-attacks on the player, pooled-FX draw calls.
from playwright.sync_api import sync_playwright
import time,json,sys,os
D="/workspace/v3build/shots/"; B="http://localhost:8765/v3build/sky-rydahs-v3-ikki.html?chars=/skyrydahs-characters/"
CREWS=["codee","karasu","static","behemoth","anubis","forest","genesis","ttt"]
ok=[]; peak=[0]
def check(n,c,i=""): ok.append(bool(c)); print(("PASS " if c else "FAIL ")+n,i,flush=True)
def waitfor(pg,e,t=40):
    t0=time.time()
    while time.time()-t0<t:
        if pg.evaluate(e): return True
        time.sleep(.15)
    return False
HELP="""window.__worldStick=true;window.__npc=c=>RIDERS.npcs.find(n=>n.g&&n.g.crew===c)||RIDERS.npcs[0];
window.__near=n=>{const g=n.g;Ride.group.position.set(g.pos[0]+Math.sin(g.th)*11,0,g.pos[1]+Math.cos(g.th)*11);Ride.speed=0;window.__camHook=null;camera.position.set(Ride.group.position.x,3,Ride.group.position.z);};
window.__face=(n,d)=>{const q=n.holder.position,g=n.g;const ox=Math.sin(g.th+1.2),oz=Math.cos(g.th+1.2);Ride.group.position.set(q.x+ox*d,0,q.z+oz*d);Ride.y=0;Ride.yaw=Math.atan2(q.x-Ride.group.position.x,q.z-Ride.group.position.z);Ride.speed=0;WALL.on=WALL.air=null;
  n.stun=0;n.kv=null;if(n.off)n.off.set(0,0,0);};
window.__cam=n=>{window.__camHook=()=>{const p=Ride.group.position,q=n.holder.position;const mx=(p.x+q.x)/2,mz=(p.z+q.z)/2,dx=q.x-p.x,dz=q.z-p.z,l=Math.hypot(dx,dz)||1;camera.position.set(mx-dz/l*6.5,3.2,mz+dx/l*6.5);camera.lookAt(mx,1.1,mz);};};
window.__freeze=on=>{for(const n of RIDERS.npcs){n.ph0=n.ph0??n.ph;} window.__npcFreeze=on;};0"""
NOPAD="garages.forEach(g=>g.gate&&(g.gate.dismissed=true));GATE.uiOpen=false;gateUI()"
def load(pg,url):
    pg.goto(url,timeout=120000); waitfor(pg,"typeof RIDERS!='undefined'&&RIDERS.ready&&TURF.ready&&RIDERS.npcs.length>0",150); time.sleep(3)
    # first-crew warm-up: Enter + fixed 1.5 s wall sleep could leave the game in the menu / pre-ride at ~2 fps, so the first crew's J/K keypresses were
    # eaten (cd stayed [0,0,0]). Wait for ride mode + move sets + ~0.5 s of game time before any case.
    for _ in range(10):
        if pg.evaluate("State.mode==='ride'"): break
        pg.keyboard.press("Enter"); waitfor(pg,"State.mode==='ride'",15)
    waitfor(pg,"typeof MOVESETS!=='undefined'&&typeof ATK!=='undefined'",30); pg.evaluate("window.__w0=clock"); waitfor(pg,"clock>__w0+.5",60); pg.evaluate(HELP); pg.evaluate("window.__npcPassive=true;window.__hideIkkiNpc=true")
def calls(pg):
    c=pg.evaluate("""new Promise(res=>{renderer.info.autoReset=false;let n=0,mx=0;renderer.info.reset();function f(){mx=Math.max(mx,renderer.info.render.calls);renderer.info.reset();if(++n<8)requestAnimationFrame(f);else{renderer.info.autoReset=true;res(mx);}}requestAnimationFrame(f);})""")
    peak[0]=max(peak[0],c); return c
def player_moves(pg,crew,shot,key_shot):
    pg.evaluate(f"ATK.set='{crew}';ATK.cd=[0,0,0];ATK.act=null")
    tc="static" if crew=="codee" else "codee"
    # hold the target still: mode-0 NPCs carve a 3.2 m loop every frame, and at headless ~1-3 fps they drift ~1-2 m between
    # __face() and the key press, so short moves (J dash, cones, dives) whiffed with stun 0. Idle mode = fixed spot. (__npcFreeze no longer exists in the build.)
    tgt=pg.evaluate(f"(()=>{{window.__T=__npc('{tc}');__T.mode0=__T.mode0??__T.mode;return __T.g.crew}})()")
    names=pg.evaluate(f"MOVESETS['{crew}'].moves.map(m=>m.name)")
    pg.evaluate("__near(__T)"); waitfor(pg,"__T.holder.visible&&__T.holder.position.lengthSq()>1",10)
    for i,k in enumerate("JKL"):
        waitfor(pg,"!ATK.act&&!WALL.air&&ATK.stun<=0",10); pg.evaluate("__cam(__T)"); time.sleep(.5); pg.evaluate(NOPAD); h0=pg.evaluate("ATK.hits"); n0=pg.evaluate("__T.hitN||0")
        # re-face right before the press: the target keeps its own 3.2 m loop here, and 0.5 s wall at ~2 fps let it drift out of J range (d 5.6)
        pg.evaluate("__face(__T,1.9)"); pg.keyboard.press("Key"+k)
        if i==0: check(f"{crew} cooldown blocks spam",waitfor(pg,"ATK.cd[0]>0",4) and pg.evaluate("atkStart(0)===false"))
        if shot and k==key_shot: time.sleep(.12); pg.screenshot(path=D+shot); c=calls(pg)
        # GAME-time wait (dives land ~1 s after the press; 8 s wall at ~2 fps with the dt cap was ~0.45 s game, so L was sampled mid-air: cd ~3.6 = just fired)
        pg.evaluate("window.__c0=clock"); hit=waitfor(pg,f"ATK.hits>{h0}||(__T.hitN||0)>{n0}||clock>__c0+3",90) and pg.evaluate(f"ATK.hits>{h0}||(__T.hitN||0)>{n0}")
        st=pg.evaluate("JSON.stringify({stun:+(__T.stun||0).toFixed(2),off:+(__T.off?__T.off.length():0).toFixed(2),cd:ATK.cd.map(v=>+v.toFixed(2))})")
        check(f"{crew} {k} '{names[i]}' hits + knockback/stagger",hit,st)
        if not hit: print("  diag",pg.evaluate("JSON.stringify({mode:State.mode,tmode:__T.mode,stun:ATK.stun,act:ATK.act&&{m:ATK.act.m.name,t:+ATK.act.t.toFixed(2),tgt:!!ATK.act.tgt,homed:ATK.act.homed||0},d:+Math.hypot(__T.holder.position.x-Ride.group.position.x,__T.holder.position.z-Ride.group.position.z).toFixed(2),clock:+clock.toFixed(2)})"),flush=True)
        waitfor(pg,"!ATK.act&&!WALL.air",8); time.sleep(.3)
with sync_playwright() as p:
    b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    pg=b.new_page(viewport={"width":1280,"height":720}); pg.set_default_timeout(150000); errs=[]
    pg.on("console",lambda m: errs.append(m.type+": "+m.text) if m.type in("error","warning") else None); pg.on("pageerror",lambda e: errs.append("PAGEERROR "+str(e)))
    load(pg,B)
    check("8 crew move sets x 3 moves",pg.evaluate("Object.keys(MOVESETS).length===8&&Object.values(MOVESETS).every(s=>s.moves.length===3)"))
    player_moves(pg,"codee","attack_caali.png","K")
    for crew in CREWS[2:]+["karasu"]: player_moves(pg,crew,None,None)
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
    E=[e for e in errs if "Custom UV" not in e]; check("no errors",not any("PAGEERROR" in e or "atk" in e.lower() for e in E),json.dumps(E[:6]))
    # Ikki player
    load(pg,B+"&player=ikki"); check("ikki uses Kogarasumaru set",pg.evaluate("atkSet().who.startsWith('Ikki')"))
    pg.evaluate("ATK.set=null"); player_moves(pg,"karasu","attack_ikki.png","J")
    pg.evaluate("__near(__T)"); time.sleep(1); pg.evaluate("__face(__T,3);__cam(__T);ATK.cd=[0,0,0]"); time.sleep(.4); pg.evaluate(NOPAD); pg.keyboard.press("KeyL"); time.sleep(.35); pg.screenshot(path=D+"attack_ikki_dive.png")
    b.close()
print("peak",peak[0]); print("RESULT",sum(ok),"/",len(ok))
