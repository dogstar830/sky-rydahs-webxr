# POLICE HEAT v1 test (heat.js via patch_graffiti.py). Mocked Xbox pad + deterministic time stub (HEAT.freeze + HEAT.step) + player override.
# Covers: API backward-compat, ladder ★0-3 rosters + pool<=6, sight cone, LOS break -> cooldown -> escape, hiding-spot speed-up,
# ★3 60 s reinforcement timer (freezes in cooldown), BUSTED after 3 s pinned / 3 knockdowns (at-risk lost), bank at crew HQ, night x2,
# v1 cap at ★3, added draw calls (<= 3), no console errors.
# Usage: python3 tests/heat.py [base_url] [page]   default http://localhost:8765 + v3build/sky-rydahs-v3-ikki.html  (take .testlock first)
from playwright.sync_api import sync_playwright
import time, json, sys
BASE=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8765"
PAGE=sys.argv[2] if len(sys.argv)>2 else "v3build/sky-rydahs-v3-ikki.html"
U=f"{BASE}/{PAGE}?fps&chars=/skyrydahs-characters/"
SH="/workspace/v3build/shots/"
res=[]
def check(n,c,i=""): res.append((n,bool(c))); print(("PASS " if c else "FAIL ")+n,i,flush=True)
STUB="""(()=>{window.__pb=Array.from({length:17},()=>({pressed:false,touched:false,value:0}));
window.__pad={id:'Xbox stub',index:0,connected:true,mapping:'standard',axes:[0,0,0,0],buttons:window.__pb,timestamp:0,vibrationActuator:{playEffect:()=>Promise.resolve('complete')}};
navigator.getGamepads=()=>[window.__pad,null,null,null];})()"""
with sync_playwright() as p:
    b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader","--autoplay-policy=no-user-gesture-required"])
    pg=b.new_page(viewport={"width":1280,"height":720}); pg.set_default_timeout(180000); errs=[]
    pg.on("pageerror",lambda e: errs.append("PAGEERROR "+str(e)))
    pg.on("console",lambda m: errs.append("console: "+m.text) if m.type=="error" else None)
    pg.add_init_script(STUB); pg.goto(U,timeout=300000); ev=pg.evaluate
    for i in range(150):
        if ev("typeof RIDERS!='undefined'&&RIDERS.ready&&window.GRAF&&GRAF.ready&&!!window.heatTick"): break
        time.sleep(1)
    time.sleep(2)
    ev("__pb[0].pressed=true;__pb[0].value=1"); time.sleep(.3); ev("__pb[0].pressed=false;__pb[0].value=0"); time.sleep(1.5)
    for k in range(10):
        if ev("State.mode")=="ride": break
        pg.keyboard.press("Enter") if k%2 else (ev("__pb[0].pressed=true;__pb[0].value=1"), time.sleep(.3), ev("__pb[0].pressed=false;__pb[0].value=0"))
        time.sleep(1.5)
    check("in ride mode", ev("State.mode")=="ride")
    check("HEAT API backward-compatible", ev("['add','set','decay','night','subscribe'].every(k=>typeof HEAT[k]==='function')&&'level' in HEAT&&'stars' in HEAT&&HEAT.max===5"))
    check("HEAT police API", ev("HEAT.api===2&&Array.isArray(HEAT.cops)&&typeof HEAT.step==='function'&&typeof HEAT.bank==='function'&&!!HEAT.hooks&&'tier4' in HEAT.hooks&&'tier5' in HEAT.hooks"))
    # draw calls added: direct render, post-FX off, with 6 cops vs 0 cops
    ev("HEAT.freeze=true;HEAT.clearCops()")
    DC="(()=>{renderer.info.autoReset=false;renderer.info.reset();renderer.render(scene,camera);const c=renderer.info.render.calls;renderer.info.autoReset=true;return c})()"
    # open test ground: find a point with a clear 30 m line east+north
    o=ev("""(()=>{const P=HEAT.police;for(let i=0;i<4000;i++){const x=-200+Math.random()*450,z=-300+Math.random()*450;
      if(P._los(x,z,x+30,z)||P._los(x,z,x,z+30)||P._los(x,z,x-12,z)||P._los(x,z,x,z-12)) continue; if(P._hiding({x,y:0,z,speed:9})) continue; return [x,z]} return null})()""")
    check("found open test ground", o is not None, o); X,Z=o
    ev(f"Ride.group.position.set({X},0,{Z});HEAT.playerOverride={{x:{X},y:0,z:{Z},speed:9}};HEAT.set(0);GRAF.forceNight=false")
    ev("HEAT.step(.05)"); time.sleep(.5); d0=ev(DC)
    for k,t in enumerate(["patrol","patrol","bike","bike","gmen","gmen"]): ev(f"HEAT.spawnCop('{t}',{X}+3+{k},{Z}+6,Math.PI)")
    ev("HEAT.police.ladder=HEAT.police.ladder") ; ev("(()=>{const f=HEAT.freeze;})()")
    ev("HEAT.state='idle';"); time.sleep(.3); ev("window.heatTick&&0")
    # sync without roster changes: call internal sync by stepping 0 with a pool-preserving ladder
    ev("window.__lad=HEAT.police.ladder;HEAT.police.ladder=[{patrol:2,bike:2,gmen:2},{patrol:2,bike:2,gmen:2},{patrol:2,bike:2,gmen:2},{patrol:2,bike:2,gmen:2}];HEAT.step(0.001)")
    d6=ev(DC); ev("scene.children.filter(o=>o.name==='heat_cops').forEach(o=>o.userData.v=o.visible,o.visible=false)") if False else None; d0=ev("(()=>{const L=scene.children.filter(o=>o.name==='heat_cops');const v=L.map(o=>o.visible);L.forEach(o=>o.visible=false);const c="+DC+";L.forEach((o,i)=>o.visible=v[i]);return c})()"); check("6 cops add <= 3 draw calls", 0<d6-d0<=3, f"{d0} -> {d6} (+{d6-d0})"); added=d6-d0
    ev(f"HEAT.set(.5);HEAT.step(.001);window.__camHook=()=>{{camera.position.set({X}+5.5,3.2,{Z}-5);camera.lookAt({X}+5.5,.8,{Z}+6);}}"); c0=ev("frame")
    t0=time.time()
    while ev("frame")<c0+4 and time.time()-t0<30: time.sleep(.1)
    ev("HEAT.police.ladder=__lad"); pg.screenshot(path=SH+"heat_cops.png",timeout=120000); ev("window.__camHook=null")
    # ---- ladder rosters (stars 0..3)
    ros={}
    for s in range(4):
        ev(f"HEAT.clearCops();HEAT.set({s}+.5);HEAT.state='idle';HEAT.playerOverride={{x:{X},y:0,z:{Z},speed:9}}")
        ev("HEAT.step(.05)"); ros[s]=ev("HEAT.cops.reduce((a,c)=>(a[c.type]=(a[c.type]||0)+1,a),{})")
    print("rosters",ros,flush=True)
    check("★0 = 2 patrol", ros[0]=={"patrol":2}); check("★1 = 3 patrol", ros[1]=={"patrol":3})
    check("★2 adds bike cops", ros[2].get("bike")==2 and ros[2].get("patrol")==2); check("★3 adds G-Men, pool <= 6", ros[3].get("gmen")==2 and sum(ros[3].values())<=6)
    # ---- ★0 sight cone: spotted tagging -> ★1
    ev(f"HEAT.clearCops();HEAT.set(0);HEAT.state='idle';HEAT.police.ladder=[{{patrol:1}},{{patrol:1}},{{patrol:1}},{{patrol:1}}]")
    ev(f"HEAT.spawnCop('patrol',{X}+10,{Z},-Math.PI/2)"); ev("GRAF.cur={fake:1};HEAT.step(.05);GRAF.cur=null")
    check("★0 cone: spotted tagging -> ★1", ev("HEAT.stars")==1, ev("HEAT.level"))
    ev(f"HEAT.clearCops();HEAT.set(0);HEAT.spawnCop('patrol',{X}+10,{Z},Math.PI/2)"); ev("GRAF.cur={fake:1};HEAT.step(.05);GRAF.cur=null")
    check("★0 cone: cop facing away doesn't see", ev("HEAT.stars")==0)
    # ---- pursuit, LOS break -> cooldown -> escape
    ev(f"HEAT.clearCops();HEAT.set(1.2);HEAT.state='idle';HEAT.spawnCop('patrol',{X}+10,{Z},-Math.PI/2);HEAT.step(.05)")
    check("★1 pursuit when seen", ev("HEAT.state")=="pursuit")
    # break LOS: move player far out of sight range (no cop sees)
    ev(f"HEAT.playerOverride={{x:{X}+70,y:0,z:{Z}+70,speed:9}};HEAT.police.cullR=1e9;HEAT.step(.05)")
    check("LOS broken -> cooldown", ev("HEAT.state")=="cooldown", ev("HEAT.cops"))
    cm=ev("HEAT.cooldownMax"); t=0
    while ev("HEAT.state")=="cooldown" and t<60: ev(f"HEAT.playerOverride={{x:{X}+70+{t}*9,y:0,z:{Z}+70,speed:9}};HEAT.step(.25)"); t+=.25
    check("cooldown completes -> escaped", ev("HEAT.state")=="idle" and ev("HEAT.escapes")>=1, f"{t:.2f}s / max {cm}")
    t_open=t
    # hiding spot (own crew HQ) speeds it up
    g=ev("(()=>{const g=PALMA.garages.find(q=>q.crew===GRAF.me())||PALMA.garages[0];return g.pos})()")
    ev(f"HEAT.clearCops();HEAT.set(1.2);HEAT.state='cooldown';HEAT.cooldown=0;HEAT.cooldownMax=HEAT.police.coolBase+HEAT.police.coolPerStar*1;HEAT.playerOverride={{x:{g[0]},y:0,z:{g[1]},speed:9}}")
    ev("HEAT.police.ladder=[{},{},{},{}]"); t=0
    while ev("HEAT.state")=="cooldown" and t<60: ev("HEAT.step(.25)"); t+=.25
    hid=ev("HEAT.police._hiding(HEAT.playerOverride)")
    check("hiding spot speeds cooldown (x2.5)", t<t_open*.6, f"hide '{hid}' {t:.2f}s vs open {t_open:.2f}s")
    # ---- ★3 reinforcement timer + freeze during cooldown
    ev(f"HEAT.police.ladder=[{{}},{{gmen:1}},{{gmen:1}},{{gmen:1}}];HEAT.clearCops();HEAT.set(3.2);HEAT.state='idle';HEAT.reinforce=null;HEAT.playerOverride={{x:{X},y:0,z:{Z},speed:20}}")
    ev(f"HEAT.spawnCop('gmen',{X}+20,{Z},-Math.PI/2);HEAT.step(.05)")
    r0=ev("HEAT.reinforce"); check("★3 reinforcement timer starts at 60 s", ev("HEAT.state")=="pursuit" and r0 is not None and 59<r0<=60, r0)
    ev("window.__rf=0;HEAT.hooks.onReinforce=()=>__rf++;HEAT.police.knockR=0;HEAT.police.pinR=0")
    for i in range(62): ev(f"HEAT.playerOverride={{x:{X},y:0,z:{Z},speed:20}};HEAT.cops.length&&0;HEAT.step(1)")
    check("reinforcements fire after 60 s", ev("__rf")>=1, ev("HEAT.reinforce"))
    check("v1 caps at ★3 without tier4 hook", ev("HEAT.stars")==3 and ev("HEAT.level")<4)
    ev(f"HEAT.state='cooldown';HEAT.cooldown=0;HEAT.cooldownMax=1e9;HEAT.clearCops();HEAT.police.ladder=[{{}},{{}},{{}},{{}}];HEAT.playerOverride={{x:{X}+300,y:0,z:{Z}+300,speed:20}}")
    a=ev("HEAT.reinforce"); ev("HEAT.step(5)"); bb=ev("HEAT.reinforce")
    check("reinforcement timer frozen in cooldown", a==bb, f"{a} -> {bb}")
    ev("HEAT.hooks.onReinforce=null;HEAT.police.cullR=150;HEAT.police.knockR=1.3;HEAT.police.pinR=1.7")
    # ---- BUSTED: pinned 3 s, at-risk lost
    ev(f"HEAT.police.ladder=[{{}},{{patrol:1}},{{patrol:1}},{{patrol:1}}];HEAT.clearCops();HEAT.set(1.5);HEAT.state='idle';HEAT.atRisk={{parts:0,turf:[]}};HEAT.addParts(5);HEAT.playerOverride={{x:{X},y:0,z:{Z},speed:0}}")
    ev(f"HEAT.spawnCop('patrol',{X}+1,{Z},-Math.PI/2)"); b0=ev("HEAT.busts")
    ev("HEAT.step(1)"); ev("HEAT.step(1)"); s2=ev("HEAT.busts"); pin2=ev("HEAT.pinned"); ev("HEAT.step(1.1)")
    check("not busted before 3 s pinned", s2==b0, pin2); check("BUSTED after 3 s pinned", ev("HEAT.busts")==b0+1 and ev("HEAT.lastBust.why")=="pinned")
    check("bust loses at-risk parts + resets heat", ev("HEAT.lastBust.lost.parts")==5 and ev("HEAT.atRisk.parts")==0 and ev("HEAT.stars")==0)
    # ---- BUSTED: 3 knockdowns (bike cop tackles while you skate)
    ev(f"HEAT.police.ladder=[{{}},{{}},{{bike:1}},{{bike:1}}];HEAT.clearCops();HEAT.set(2.5);HEAT.state='idle';HEAT.playerOverride={{x:{X},y:0,z:{Z},speed:9}}")
    b1=ev("HEAT.busts"); kd=[]
    for i in range(3):
        ev(f"HEAT.clearCops();HEAT.spawnCop('bike',{X}+.5,{Z},-Math.PI/2);HEAT.cops;0"); ev("HEAT.step(.05)"); ev("HEAT.step(1.3)"); ev("HEAT.step(1.3)"); kd.append(ev("[HEAT.knockdowns,HEAT.busts]"))
    print("knockdowns",kd,flush=True)
    check("BUSTED after 3 knockdowns", ev("HEAT.busts")==b1+1 and ev("HEAT.lastBust.why")=="knockdowns", kd)
    # ---- bank at crew HQ
    ev(f"HEAT.clearCops();HEAT.state='idle';HEAT.atRisk={{parts:0,turf:[]}};HEAT.addParts(4);HEAT.playerOverride={{x:{X},y:0,z:{Z},speed:0}}")
    check("bank refused away from HQ", ev("HEAT.bank()")==False)
    ev(f"HEAT.playerOverride={{x:{g[0]},y:0,z:{g[1]},speed:0}}"); bk=ev("HEAT.bank()")
    check("bank at crew HQ secures at-risk", bool(bk) and ev("HEAT.banked.parts")>=4 and ev("HEAT.atRisk.parts")==0, bk)
    # ---- night x2 (heat gain and pay)
    ev("HEAT.set(0);GRAF.forceNight=false;HEAT.gain(.5,'t')"); hd=ev("HEAT.level"); ev("HEAT.atRisk.parts=0;HEAT.addParts(3)"); pd=ev("HEAT.atRisk.parts")
    ev("HEAT.set(0);GRAF.forceNight=true;HEAT.gain(.5,'t')"); hn=ev("HEAT.level"); ev("HEAT.atRisk.parts=0;HEAT.addParts(3)"); pn=ev("HEAT.atRisk.parts")
    check("night x2 heat", abs(hn-2*hd)<1e-6, f"day {hd} night {hn}"); check("night x2 pay", pn==2*pd, f"day {pd} night {pn}")
    # ---- live loop smoke: unfreeze, ★2 at night for 3 s with real rider, then screenshot HUD
    ev(f"HEAT.police.ladder=__lad;HEAT.playerOverride=null;HEAT.clearCops();HEAT.atRisk={{parts:0,turf:[]}};HEAT.set(2.4);HEAT.state='idle';HEAT.freeze=false")
    time.sleep(4); live=ev("JSON.stringify({n:HEAT.cops.length,state:HEAT.state,stars:HEAT.stars})"); print("live",live,flush=True)
    check("live tick runs, cops spawn", json.loads(live)["n"]>=1)
    pg.screenshot(path=SH+"heat_hud_live.png"); ev("GRAF.forceNight=null;HEAT.set(0)")
    # ---- minimap (heading-up) + world map (north-up): cop east (+x) of a north-facing (-z) player renders to the right, 0 WebGL draws
    ev(f"HEAT.freeze=true;HEAT.police.ladder=[{{patrol:1}},{{patrol:1}},{{patrol:1}},{{patrol:1}}];HEAT.clearCops();HEAT.set(1.5);HEAT.state='pursuit';HEAT.playerOverride={{x:{X},y:0,z:{Z},speed:0}};HEAT.spawnCop('patrol',{X}+20,{Z},-Math.PI/2);HEAT.step(.01)")
    if ev("typeof MM2!=='undefined'&&typeof mm2Draw==='function'"):
        dcA=ev(DC); mm=ev(f"(()=>{{MM2.cx={X};MM2.cz={Z};MM2.rot=0;mm2Draw();const s=MINIMAP.state;return {{W:s.W,H:s.H,n:s.n,cops:s.cops}}}})()"); dcB=ev(DC)
        c0=(mm["cops"] or [{}])[0]; print("minimap",json.dumps(mm)[:300],flush=True)
        check("minimap: N up when facing north", mm["n"][1]<mm["H"]/2 and abs(mm["n"][0]-mm["W"]/2)<2)
        check("minimap: cop east renders right of player", bool(mm["cops"]) and c0["x"]>mm["W"]/2+5 and abs(c0["y"]-mm["H"]/2)<3, c0)
        check("minimap: cop arrow points west (toward player)", bool(mm["cops"]) and abs(abs(c0["ang"])-3.14159)<.05, c0.get("ang"))
        check("minimap cops add 0 WebGL draws", dcA==dcB, f"{dcA} vs {dcB}")
    else: check("minimap v2 present", False)
    # reference = HEAT.playerOverride (X,Z), the same point the cop was spawned against; Ride.group may sit elsewhere (it did: (0,16) vs (X,Z))
    wm=ev(f"(()=>{{ if(!MAP.cv) mapBuild(); MAP.cx={X}; MAP.cz={Z}; MAP.locs=MAP.locs||[]; mapDraw(); const pp=mapW2S({X},{Z}); return {{pp, cops:MAP.copsDrawn, p:[{X},{Z}]}} }})()")
    print("worldmap",json.dumps(wm)[:300],flush=True); w0=(wm["cops"] or [{}])[0]
    check("world map: cop east renders right of player", bool(wm["cops"]) and w0["x"]>wm["pp"][0]+5 and abs(w0["y"]-wm["pp"][1])<3, w0)
    check("world map: cop seeing you is highlighted flag", "seeing" in w0)
    ev("HEAT.clearCops();HEAT.state='idle';HEAT.set(0);HEAT.playerOverride=null;HEAT.freeze=false;HEAT.police.ladder=__lad")
    check("no console errors", not errs, errs[:5])
    b.close()
n=sum(1 for _,c in res if c); print(f"\nheat.py: {n}/{len(res)} passed; added draws for 6 cops = {added}")
