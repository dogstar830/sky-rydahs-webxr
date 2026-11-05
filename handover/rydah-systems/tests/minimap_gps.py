# Minimap GPS (heading-up) tests. Asserts on window.MINIMAP.state numbers, not pixels. Run by the integrator under .testlock.
# usage: python3 tests/minimap_gps.py [--port 8796]
import sys,time,json,math
from playwright.sync_api import sync_playwright
port=sys.argv[sys.argv.index("--port")+1] if "--port" in sys.argv else "8796"
PAGE=sys.argv[sys.argv.index("--page")+1] if "--page" in sys.argv else "v3build/sky-rydahs-v3-ikki.html"
B=f"http://localhost:{port}/{PAGE}?chars=/skyrydahs-characters/"
SH="/workspace/v3build/shots/minimap_gps_"
def waitfor(pg,e,t=150):
    t0=time.time()
    while time.time()-t0<t:
        if pg.evaluate(e): return True
        time.sleep(.3)
def wrap(a): return math.atan2(math.sin(a),math.cos(a))
res=[]
def check(name,ok,info): res.append((name,bool(ok),info)); print(("PASS " if ok else "FAIL ")+name,json.dumps(info))
with sync_playwright() as p:
    br=p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"]); pg=br.new_page(viewport={"width":1280,"height":720})
    errs=[]; pg.on("pageerror",lambda e: errs.append(str(e)))
    pg.goto(B,timeout=120000); waitfor(pg,"typeof RIDERS!='undefined'&&RIDERS.ready"); time.sleep(3)
    pg.keyboard.press("Enter"); time.sleep(1.5)
    pg.evaluate("garages.forEach(g=>g.gate&&(g.gate.dismissed=true));if(typeof GATE!='undefined'){GATE.uiOpen=false;gateUI()};window.__npcPassive=true;window.__npcFreeze=true")
    waitfor(pg,"!!window.MINIMAP&&MINIMAP.state.heading!==null",20)
    # freeze the rider: zero throttle/speed so only our yaw/position edits move it
    hold="Ride.speed=0;Ride.throttle=0;"
    # settle on GAME time + frames, not wall time: swiftshader runs ~1-3 fps, so 1.5 s wall was only a frame or two and
    # MINIMAP.state (written in mm2Tick) was sampled before the heading smoothing / centre update had run.
    def settle(js,t=1.5):
        pg.evaluate(js); c0=pg.evaluate("clock"); f0=pg.evaluate("frame"); t0=time.time()
        while time.time()-t0<90:
            pg.evaluate(hold)
            if pg.evaluate("clock")>=c0+t and pg.evaluate("frame")>=f0+4: break
            time.sleep(.05)
        return pg.evaluate("MINIMAP.state")
    # (a) stopped: heading follows body yaw; turning 90deg rotates map 90deg, arrow (centre chevron) stays up
    s0=settle(hold+"Ride.yaw=0;MM2.lx=null;")
    s1=settle(hold+"Ride.yaw=Math.PI/2;")
    d=wrap(s1["rot"]-s0["rot"])
    check("a_turn90_rotates_map90", abs(abs(d)-math.pi/2)<0.05 and not s1["moving"], {"rot0":s0["rot"],"rot1":s1["rot"],"drot":d})
    # forward point (10 m along heading) must land straight up from centre
    up=pg.evaluate("(()=>{const s=MINIMAP.state,P=Ride.group.position,h=s.heading,p=MINIMAP.w2s(P.x+Math.sin(h)*10,P.z+Math.cos(h)*10);return [p[0]-s.W/2,p[1]-s.H/2]})()")
    check("a_heading_points_up", abs(up[0])<0.5 and up[1]<-20, {"fwd_px":up})
    # N marker orbits: at yaw=PI/2 (facing +x/east) north is to the LEFT on the map
    n=s1["n"]; check("a_N_marker_on_rim_left", n[0]<s1["W"]/2-100 and abs(n[1]-s1["H"]/2)<10, {"n":n})
    # (b) moving 50 m north (-z): heading -> PI (velocity), map rot ~0, a fixed world point moves 50*scale px down
    # move to a lane with no collider / water for 60 m north, so collision push-back can't eat the 50 m test move
    pg.evaluate("""(()=>{const hit=(x,z)=>colliders.some(c=>!c.off&&x>c.minX-1&&x<c.maxX+1&&z>c.minZ-1&&z<c.maxZ+1)||!onLand(x,z);
      for(let i=0;i<5000;i++){const x=-200+Math.random()*450,z=-250+Math.random()*450;let ok=true;for(let d=0;d<=60&&ok;d+=1) if(hit(x,z-d)) ok=false; if(ok){Ride.group.position.set(x,0,z);MM2.lx=null;return [x,z]}} return null})()""")
    settle(hold+"Ride.yaw=Math.PI;",1.0)
    ref=pg.evaluate("(()=>{const P=Ride.group.position;window.__ref={x:P.x+5,z:P.z-30};return MINIMAP.w2s(__ref.x,__ref.z)})()")
    cz0=pg.evaluate("Ride.group.position.z")
    for i in range(25): pg.evaluate(hold+"Ride.group.position.z-=2;"); settle(hold,0.02)  # one frame per 2 m step so velocity heading + centre track the move
    sb=settle(hold,0.4)
    ref2=pg.evaluate("MINIMAP.w2s(__ref.x,__ref.z)")
    dy=ref2[1]-ref[1]; exp=50*sb["scale"]
    check("b_north50_translates", abs(sb["cz"]-(cz0-50))<0.01 and abs(dy-exp)<0.06*exp and abs(ref2[0]-ref[0])<2, {"dy":dy,"expected":exp,"cz":sb["cz"],"rot":sb["rot"]})
    # (c) off-screen waypoint 400 m east; facing north -> rim arrow at right (ang~0); facing east -> rim arrow at top (ang~-PI/2)
    pg.evaluate("MAP.wp={x:Ride.group.position.x+400,z:Ride.group.position.z,name:'GPS'};")
    sc1=settle(hold+"Ride.yaw=Math.PI;MM2.lx=null;MM2.moving=false;MM2.vs=0;",1.5)
    sc2=settle(hold+"Ride.yaw=Math.PI/2;",1.5)
    o1=[r for r in sc1["rim"] if r["kind"]=="objective"]; o2=[r for r in sc2["rim"] if r["kind"]=="objective"]
    ok=o1 and o2 and o1[0]["onRim"] and o2[0]["onRim"] and abs(wrap(o1[0]["ang"]-0))<0.08 and abs(wrap(o2[0]["ang"]+math.pi/2))<0.08
    check("c_offscreen_waypoint_rim_dir", ok, {"northUp":o1,"eastUp":o2})
    pg.screenshot(path=SH+"east.png",clip={"x":980,"y":440,"width":300,"height":280})
    settle(hold+"Ride.yaw=Math.PI*0.75;",1.5); pg.screenshot(path=SH+"ne.png",clip={"x":980,"y":440,"width":300,"height":280})
    # (d) world map stays north-up; player arrow rot = true heading (PI - yaw, forward=(sin,cos))
    dres=pg.evaluate("""(()=>{let got=null;const o=window.mapPlayer;window.mapPlayer=function(c,x,y,rot){ got=rot; return o.apply(this,arguments); };  // mapDraw draws the player via mapPlayer(), not icDraw
      try{ Ride.yaw=0.6; if(!MAP.cv) mapBuild(); mapDraw(); }finally{ window.mapPlayer=o; }
      const a=mapW2S(0,-100), b=mapW2S(0,0); return {rot:got,yaw:0.6,northDy:a[1]-b[1],northDx:a[0]-b[0]}; })()""")
    fwd=(math.sin(dres["rot"]),-math.cos(dres["rot"])) if dres["rot"] is not None else (0,0)
    check("d_worldmap_northup_true_heading", dres["northDy"]<0 and abs(dres["northDx"])<1e-6 and abs(fwd[0]-math.sin(.6))<1e-3 and abs(fwd[1]-math.cos(.6))<1e-3, dres)
    check("no_page_errors", not errs, errs[:5])
    br.close()
f=sum(1 for r in res if not r[1]); print(f"minimap_gps: {len(res)-f} PASS / {f} FAIL"); sys.exit(1 if f else 0)
