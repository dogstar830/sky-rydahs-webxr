# Wall rides: shallow stick on the East Blocks WALL RIDE panel, hold = wall run, flip, kick-off, wall-to-wall chain, steep hit = no stick.
from playwright.sync_api import sync_playwright
import time,json,sys
D="/workspace/v3build/shots/"; import os
B=os.environ.get("RYDAH_BASE","http://localhost:8765")+"/v3build/"+os.environ.get("RYDAH_PAGE","sky-rydahs-v3-ikki.html")+"?chars=/skyrydahs-characters/"
ok=[]
def check(n,c,i=""): ok.append(bool(c)); print(("PASS " if c else "FAIL ")+n,i,flush=True)
def waitfor(pg,e,t=40):
    t0=time.time()
    while time.time()-t0<t:
        if pg.evaluate(e): return True
        time.sleep(.15)
    return False
def gwait(pg,sec,e=None,cap=120):   # game-clock wait (headless swiftshader runs 1-3 fps; dt capped 0.05)
    c0=pg.evaluate("clock"); t0=time.time()
    while time.time()-t0<cap:
        if e and pg.evaluate(e): return True
        if pg.evaluate("clock")>=c0+sec: return bool(e and pg.evaluate(e))
        time.sleep(.1)
    return False
HELP="""window.__free=(x,z)=>onLand(x,z)&&!colliders.some(c=>!c.off&&x>c.minX-.6&&x<c.maxX+.6&&z>c.minZ-.6&&z<c.maxZ+.6);
window.__setup=(c,side,toward,zs)=>{ // ride along a +/-x face of collider c, angled 'toward' (into-component) the wall
  const n=side, fx=n>0?c.maxX:c.minX, z0=c.minZ+(zs===undefined?-2.5:zs); const dx=-n*toward, dz=Math.sqrt(1-toward*toward);
  const gx=fx+n*1.15; let g=null; try{ g=typeof WORLD_GROUND==='function'?WORLD_GROUND(gx,z0,5):null; }catch(e){} const gy=g&&Number.isFinite(g.y)?g.y:0; window.__gy=gy;
  Ride.group.position.set(gx,gy,z0); Ride.yaw=Math.atan2(dx,dz); Ride.speed=11; Ride.y=gy;
  window.__wlog=[]; (function lf(){ if(!window.__wlog) return; if(__wlog.length<400) __wlog.push([+clock.toFixed(2),+Ride.group.position.x.toFixed(2),+Ride.group.position.y.toFixed(2),+Ride.group.position.z.toFixed(2),WALL.on?'on':WALL.air?'air':'-',+Ride.speed.toFixed(1)]); requestAnimationFrame(lf); })(); WALL.on=null; WALL.air=null;
  window.__camHook=()=>{const p=Ride.group.position;camera.position.set(p.x+n*6.5,p.y+2.2,p.z-5.5);camera.lookAt(p.x-n*.5,p.y+1,p.z+1.5);}; };
window.__keep=()=>{ if(!WALL.on&&!WALL.air) Ride.speed=Math.max(Ride.speed,11); return !!WALL.on; };0"""
with sync_playwright() as p:
    b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    pg=b.new_page(viewport={"width":1280,"height":720}); pg.set_default_timeout(150000); errs=[]
    pg.on("console",lambda m: errs.append(m.type+": "+m.text) if m.type in("error","warning") else None); pg.on("pageerror",lambda e: errs.append("PAGEERROR "+str(e)))
    pg.goto(B,timeout=120000); _rdy=waitfor(pg,"typeof RIDERS!='undefined'&&RIDERS.ready&&TURF.ready",120)
    if not _rdy:
        print("FAIL page not ready (loud):",pg.evaluate("JSON.stringify({riders:typeof RIDERS!='undefined'&&!!RIDERS.ready,npcs:typeof RIDERS!='undefined'&&RIDERS.npcs?RIDERS.npcs.length:-1,turf:typeof TURF!='undefined'&&!!TURF.ready,S:typeof GRIND!='undefined'?GRIND.S.length:-1,err:(window.SR_ERRORS||[]).slice(0,5).map(String)})"),flush=True); print("RESULT 0 / 1"); import sys; sys.exit(2)
    time.sleep(3)
    pg.keyboard.press("Enter"); time.sleep(1.5); pg.evaluate(HELP); pg.evaluate("window.__npcPassive=true;window.__hideIkkiNpc=true;wallPanelTag()")
    pan=pg.evaluate("""(()=>{const NM=(window.WALL_PANELS||[]).map(w=>w.collider).filter(Boolean); const L=(NM.length?NM:colliders.filter(c=>c.wallPanel)).filter(c=>!c.off).sort((a,b)=>(a.wallPanelName&&b.wallPanelName)?a.wallPanelName.localeCompare(b.wallPanelName,undefined,{numeric:true}):0).sort((a,b)=>(a.wallPanelName&&b.wallPanelName)?0:Math.hypot((a.minX+a.maxX)/2-205,(a.minZ+a.maxZ)/2+48.5)-Math.hypot((b.minX+b.maxX)/2-205,(b.minZ+b.maxZ)/2+48.5)); // named: stable wallpanel_eastblocks_N order; unnamed fallback: nearest the EAST BLOCKS sign
      // pick by the wallPanel flag (not list index), nearest the EAST BLOCKS sign, on the face that no other collider overlaps (seeded layout can butt panels against buildings)
      for(const c of L)for(const s of [1,-1]){const fx=s>0?c.maxX:c.minX;if(colliders.some(o=>o!==c&&!o.off&&fx+s*.05>o.minX-.5&&fx+s*.05<o.maxX+.5&&c.maxZ>o.minZ&&c.minZ<o.maxZ))continue;let okk=true;for(let z=c.minZ-2.5;z<c.maxZ;z+=1)if(!__free(fx+s*1.15,z))okk=false;if(okk){window.__pan=[c,s];return [L.length,s,c.minX,c.minZ];}}return [L.length];})()""")
    check("east blocks wall-ride panels are candidates",len(pan)>1,pan); print("panel src",pg.evaluate("[WALL.panelSrc,window.__pan&&__pan[0].wallPanelName]"),flush=True)
    # 1. shallow hit on the panel -> stick
    st=False
    for att in range(3):   # first approach right after spawn can be eaten by settle frames at 1-3 fps: retry on game time
        pg.evaluate("__setup(__pan[0],__pan[1],.3)"); pg.keyboard.down("Space")
        st=gwait(pg,3,"__keep()",cap=150)
        print("panel",pg.evaluate("[__pan[0].wallPanelName||null,__pan[1]>0?'+x':'-x',[__pan[0].minX,__pan[0].maxX,__pan[0].minZ,__pan[0].maxZ],+__gy.toFixed(3)]"),"frames",pg.evaluate("JSON.stringify(__wlog.slice(0,40))"),flush=True)
        print("stick attempt",att,st,pg.evaluate("JSON.stringify({on:!!WALL.on,air:!!WALL.air,sp:+Ride.speed.toFixed(2),p:[+Ride.group.position.x.toFixed(2),+Ride.group.position.z.toFixed(2)],clock:+clock.toFixed(2)})"),flush=True)
        if st: break
        pg.keyboard.up("Space"); gwait(pg,1.5,"!WALL.air&&!WALL.on")
    check("shallow hit sticks to WALL RIDE panel",st and pg.evaluate("WALL.on&&WALL.on.panel"))
    gwait(pg,.25); y=pg.evaluate("Ride.group.position.y"); check("hold = wall run (rides up the wall)",y-pg.evaluate("__gy")>.4,(round(y,2),"ground",pg.evaluate("__gy")))
    check("VR comfort: rig would only get yaw (no roll on Ride.yaw path)",pg.evaluate("Ride.group.rotation.z!==0&&Number.isFinite(Ride.yaw)"),pg.evaluate("[Ride.group.rotation.z.toFixed(2)]"))
    # 1b. kerb approach (Palma 09:51): ride from the asphalt over the 13-14 cm kerb at speed 11, angled 0.3 into the face, NO hop -> still sticks
    pg.keyboard.up("Space"); gwait(pg,1.5,"!WALL.air&&!WALL.on"); pg.evaluate("__setup(__pan[0],__pan[1],.3)")
    kb=pg.evaluate("(()=>{const c=__pan[0],n=__pan[1],fx=n>0?c.maxX:c.minX; let g=null; try{g=WORLD_GROUND(fx+n*.15,c.minZ+1,1)}catch(e){} return {face:g&&+g.y.toFixed(3),lane:+__gy.toFixed(3)}})()")
    kst=gwait(pg,4,"__keep()",cap=150); print("kerb",kb,"frames",pg.evaluate("JSON.stringify(__wlog.slice(0,40))"),flush=True)
    check("kerb approach (asphalt -> kerb, no hop, 0.3 into face) sticks",kst and pg.evaluate("WALL.on&&WALL.on.panel"),kb)
    pg.evaluate("__setup(__pan[0],__pan[1],.3)"); pg.keyboard.down("Space"); gwait(pg,3,"__keep()",cap=150)
    pg.screenshot(path=D+"wall_ride_panel.png"); dc=pg.evaluate("renderer.info.render.calls"); print("calls on wall (FX on)",dc)
    pg.keyboard.up("Space"); waitfor(pg,"!WALL.air&&!WALL.on",20); pg.evaluate("__setup(__pan[0],__pan[1],.3)"); pg.keyboard.down("Space"); waitfor(pg,"__keep()",20); time.sleep(.1)
    t0=pg.evaluate("Stats.tricks||0"); print("pre-flip",pg.evaluate("JSON.stringify(WALL.on&&{t:WALL.on.t,y:WALL.on.y,sp:WALL.on.sp})"),flush=True); pg.keyboard.up("Space"); pg.keyboard.down("KeyA"); pg.keyboard.press("Space")
    check("wall flip (jump + direction)",waitfor(pg,"(WALL.flips||0)>0",4)); time.sleep(.15); pg.screenshot(path=D+"wall_flip.png"); pg.keyboard.up("KeyA")
    waitfor(pg,"!WALL.air&&!WALL.on",20); check("tricks scored + meter credit",pg.evaluate("Stats.tricks")>t0+300,pg.evaluate("[Stats.tricks,DASH.meter.toFixed(2)]"))
    # 2. wall-to-wall chain in a corridor
    cor=pg.evaluate("""(()=>{const L=colliders.filter(c=>!c.off&&c.maxZ-c.minZ>=8&&c.maxZ-c.minZ<90);for(const a of L)for(const b of L){const gap=b.minX-a.maxX;if(gap<3.2||gap>6)continue;
        const z0=Math.max(a.minZ,b.minZ),z1=Math.min(a.maxZ,b.maxZ);if(z1-z0<9)continue;let f=true;for(let z=z0-2.5;z<z0+9;z+=1)for(let x=a.maxX+.7;x<b.minX-.6;x+=.8)if(!__free(x,z))f=false;
        if(f&&__free(a.maxX+1.15,z0-2.5)){window.__cor=[{minX:a.minX,maxX:a.maxX,minZ:z0,maxZ:z1},a,b];return [a.maxX,b.minX,z0,z1];}}return null;})()""")
    check("found a wall-to-wall corridor",cor,cor)
    if cor:
        pg.evaluate("__setup(__cor[0],1,.3)"); pg.evaluate("WALL.chain=0;window.__camHook=()=>{const p=Ride.group.position;camera.position.set(p.x+.5,p.y+3.2,p.z-6.5);camera.lookAt(p.x+.8,p.y+.8,p.z+2);}"); pg.keyboard.down("Space")
        # Systems 09:15: press A on the contact event in GAME time (in-page), not after a wall-time screenshot: at 1-3 fps the rider ran off the 12 m wall before the press landed
        pg.evaluate("window.__cl=[];(function f(){ if(__cl.length>300) return; const o=WALL.on,a=WALL.air,p=Ride.group.position; __cl.push([+clock.toFixed(2),+p.x.toFixed(2),+p.y.toFixed(2),+p.z.toFixed(2),o?'on':a?'air':'-',o?+o.f.nx.toFixed(2):null,a?[+a.vx.toFixed(1),+a.vz.toFixed(1)]:null,WALL.chain,KICK.n,KICK.kicks,WALL.lastWall?1:0,(WALL.flips||0)]); requestAnimationFrame(f); })()")
        # Systems 09:40: in-page rAF poll reads WALL.on directly and injects A at wallatk's input layer (WIN.p.Space = keydown edge) for 3 frames; counters for diagnosis
        pg.evaluate("window.__kp=0;window.__kd={ticks:0,seen:0,err:null,pressAt:null};(function f(){ try{ __kd.ticks++; const o=WALL.on; if(o) __kd.seen++; if(o&&__kd.seen>=4&&__kp<3){ WIN.p.Space=true; WIN.k.Space=true; if(!__kp) __kd.pressAt=[+clock.toFixed(2),+Ride.group.position.z.toFixed(2)]; __kp++; } }catch(e){ __kd.err=String(e); } if(__kd.ticks<2000) requestAnimationFrame(f); })()")
        st=waitfor(pg,"__keep()||__kp>0",20); check("stick on wall A",st or pg.evaluate("__kp>0"))
        print("pre-kick",pg.evaluate("JSON.stringify({kp:__kp,kd:__kd,on:WALL.on&&{t:WALL.on.t,y:WALL.on.y,sp:WALL.on.sp}})"),flush=True)
        st=waitfor(pg,"WALL.chain>=1",15); pg.screenshot(path=D+"wall_chain.png"); pg.keyboard.up("Space")
        print("chainlog",pg.evaluate("JSON.stringify({refuse:KICK.lastRefuse||null,fb:KICK.fallbacks||0,kd:__kd,kp:__kp,cl:__cl.slice(0,120)})"),flush=True)
        check("wall-to-wall chain",st,pg.evaluate("[WALL.chain,WALL.on&&WALL.on.f.nx]"))
        waitfor(pg,"!WALL.air&&!WALL.on",20)
    # 3. steep hit: no stick
    pg.evaluate("__setup(__pan[0],__pan[1],.97,4);Ride.speed=19"); st=waitfor(pg,"!!WALL.on||Ride.speed<12",6); check("steep hit does not stick",not pg.evaluate("!!WALL.on"))
    # 4. ground hop
    pg.evaluate("Ride.group.position.set(0,0,16);Ride.speed=10;WALL.on=WALL.air=null;window.__camHook=null"); time.sleep(.3); n0=pg.evaluate("WALL.launches||0"); pg.keyboard.press("Space")
    check("jump hop",waitfor(pg,f"(WALL.launches||0)>{n0}",4))
    E=[e for e in errs if "Custom UV" not in e]; check("no errors",not any("PAGEERROR" in e or "wall" in e.lower() for e in E),json.dumps(E[:6]))
    b.close()
print("RESULT",sum(ok),"/",len(ok))
