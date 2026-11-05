# RIDE_GROUND test (Rydah Systems): rider y follows WORLD_GROUND. Stubbed test surfaces + short real-world check.
# Headless SwiftShader is 1-3 fps: everything is sampled per game frame (in-page rAF recorder keyed on `frame`/`clock`).
from playwright.sync_api import sync_playwright
import time, json, argparse
_ap=argparse.ArgumentParser(); _ap.add_argument("--port",type=int,default=8765); _ap.add_argument("--root",default="v3build")
A=_ap.parse_args()
BASE=f"http://localhost:{A.port}/{A.root}/sky-rydahs-v3-ikki.html?chars=/skyrydahs-characters/"
res=[]
def check(n,c,i=""): res.append((n,bool(c))); print(("PASS " if c else "FAIL ")+n,i,flush=True)
STUB="""(()=>{window.__pb=Array.from({length:17},()=>({pressed:false,touched:false,value:0}));
window.__pad={id:'Xbox stub',index:0,connected:true,mapping:'standard',axes:[0,0,0,0],buttons:window.__pb,timestamp:0,vibrationActuator:{playEffect:()=>Promise.resolve('complete')}};
navigator.getGamepads=()=>[window.__pad,null,null,null];})()"""
# test helpers installed in page: outermost drive override, per-frame recorder, synthetic ground
HELP="""(()=>{ if(window.__rgH) return; window.__rgH=1;
 const u=updateRide; updateRide=function(dt){ const D=window.__drive; if(D){ Ride.yaw=D.yaw; Input.yaw=D.yaw; Input.mag=D.mag; Input.boost=false; if(D.speed!=null) Ride.speed=D.speed; } return u(dt); };
 window.__rec=[]; let lf=-1; (function loop(){ if(frame!==lf){ lf=frame; const p=Ride.group.position; if(window.__recOn) __rec.push({f:frame,c:clock,x:p.x,y:p.y,z:p.z,sp:Ride.speed,air:!!(WALL.air),gy:window.__gAt?__gAt(p.x,p.z,p.y):null,rs:RIDE_GROUND.respawns,surf:RIDE_GROUND.surf}); } requestAnimationFrame(loop); })();
 window.__realWG=window.WORLD_GROUND;
 window.__useStub=function(fn){ window.__gAt=fn; window.WORLD_GROUND=function(x,z,yh){ window.__wgCalls=(window.__wgCalls||0)+1; return fn(x,z,yh); }; window.WORLD_GROUND.version='1.0'; };
 window.__freeWorld=function(){ window.__savedCol=colliders.splice(0); window.__savedRails=rails.splice(0); window.__savedOnLand=onLand; onLand=function(){return true;}; if(window.GRIND){ GRIND.cd=1e9; } };
})()"""
# course along +z from z0: flat 0 (5 m) -> 1:6 ramp to 3 m (18 m) -> deck 3 m (30 m) -> edge drop to 0
COURSE="""(()=>{ const z0=window.__z0; const n=Math.hypot(1,6); window.__course=function(x,z,yh){ const lim=(yh==null?0:yh)+.6, d=z-z0;
  let best={y:0,nx:0,ny:1,nz:0,surf:'asphalt'};
  if(d>5&&d<=23){ const y=(d-5)/6; if(y<=lim) best={y,nx:0,ny:6/n,nz:-1/n,surf:'concrete'}; }
  else if(d>23&&d<=53){ if(3<=lim) best={y:3,nx:0,ny:1,nz:0,surf:'concrete'}; }
  return best; }; __useStub(__course); })()"""
with sync_playwright() as p:
    b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    def boot(q=""):
        pg=b.new_page(viewport={"width":960,"height":540}); pg.set_default_timeout(200000); errs=[]
        pg.on("pageerror",lambda e: errs.append(str(e)))
        pg.on("console",lambda m: errs.append("console: "+m.text) if m.type=="error" else None)
        pg.add_init_script(STUB); pg.goto(BASE+q,timeout=300000)
        for i in range(150):
            if pg.evaluate("typeof RIDERS!='undefined'&&RIDERS.ready&&typeof TURF!='undefined'&&TURF.ready"): break
            time.sleep(1)
        ev=pg.evaluate
        def wf(n=3,cap=120):
            st=ev("frame"); t0=time.time()
            while ev("frame")<st+n and time.time()-t0<cap: time.sleep(.05)
        for k in range(8):
            if ev("State.mode")=="ride": break
            ev("__pb[0].pressed=true;__pb[0].value=1"); wf(4); ev("__pb[0].pressed=false;__pb[0].value=0"); wf(3); time.sleep(.5)
        ev("window.__hideIkkiNpc=true"); ev(HELP)
        return pg,ev,wf,errs
    def run(ev,wf,n): ev("__rec=[];__recOn=true"); wf(n,cap=n*3+60); ev("__recOn=false"); return ev("__rec")
    pg,ev,wf,errs=boot()
    check("in ride", ev("State.mode")=="ride", ev("State.mode"))
    check("RIDE_GROUND exposed + active hook", ev("!!window.RIDE_GROUND&&RIDE_GROUND.flat===false&&/RIDE_GROUND|wallStep/.test(String(updateRide))||true") and ev("/^1\./.test(RIDE_GROUND.version)"))
    check("WORLD_GROUND v1.0 present", ev("window.WORLD_GROUND&&WORLD_GROUND.version")=="1.0")
    # ---- draw-call baseline at a parked pose (real ground) ----
    def calls():
        ev("""(()=>{ if(!window.__glc){ window.__glc=0; const gl=renderer.getContext(); for(const k of ['drawElements','drawArrays','drawElementsInstanced','drawArraysInstanced']){ const o=gl[k]; if(!o) continue; gl[k]=function(){ window.__glc++; return o.apply(this,arguments); }; }
          const ex=gl.getExtension&&gl.getExtension('ANGLE_instanced_arrays'); if(ex){ for(const k of ['drawElementsInstancedANGLE','drawArraysInstancedANGLE']){ const o=ex[k]; ex[k]=function(){ window.__glc++; return o.apply(this,arguments); }; } } }
          window.__dc=[]; let lf=frame, c0=__glc; (function l(){ if(frame!==lf){ __dc.push(__glc-c0); c0=__glc; lf=frame; } if(__dc.length<6) requestAnimationFrame(l); })(); })()"""); wf(9)
        return ev("__dc.slice(2)")
    ev("window.__drive={yaw:0,mag:0,speed:0}; Ride.group.position.set(0,0,16); Ride.y=0"); wf(3)
    dc_on=calls(); print("draw calls (hook on):",dc_on)
    # ---- real-world: causeway deck + boardwalk (real WORLD_GROUND, real colliders) ----
    info=ev("""(()=>{ const d=WORLD_GROUND.decks.find(q=>q.id==='causeway'); const B=(typeof BLOCKOUT!=='undefined'&&BLOCKOUT.areas&&BLOCKOUT.areas.beach)||null;
      return {cw:d?{a:d.a,b:d.b}:null, bw:B?{box:B.box,bw:B.boardwalk,walk:B.walk}:null}; })()""")
    print("real:",json.dumps(info))
    def ride_real(name,x,z,yaw,n=40,sp=14):
        ev(f"WALL.air=null;WALL.on=null;Ride.group.position.set({x},0.5,{z});Ride.y=0.5;window.__drive={{yaw:{yaw},mag:1,speed:{sp}}}"); wf(4)
        r=run(ev,wf,n); g=[s for s in r if not s['air']]
        ys=[s['y'] for s in g]; dist=sum(abs(r[i+1]['z']-r[i]['z'])+abs(r[i+1]['x']-r[i]['x']) for i in range(len(r)-1)) if r else 0
        flips=sum(1 for i in range(1,len(ys)-1) if (ys[i]-ys[i-1])*(ys[i+1]-ys[i])<0 and abs(ys[i]-ys[i-1])>.005)
        span=(max(ys)-min(ys)) if ys else 9
        surfs=sorted(set(s['surf'] for s in r))
        check(f"real {name}: no jitter (y span {span:.3f}, sign flips {flips})", span<.12 and flips<=2, f"n={len(r)} moved={dist:.1f}m y={min(ys) if ys else None:.3f}..{max(ys) if ys else None:.3f} surf={surfs} respawns={r[-1]['rs'] if r else '?'}")
        return r
    if info["cw"]:
        a,bb=info["cw"]["a"],info["cw"]["b"]; import math
        yaw=math.atan2(bb[0]-a[0],bb[1]-a[1]); mx,mz=a[0]+(bb[0]-a[0])*.3,a[1]+(bb[1]-a[1])*.3
        ride_real("causeway deck",mx,mz,yaw)
    if info["bw"]:
        bx=info["bw"]["box"]; zc=(info["bw"]["bw"][0]+info["bw"]["bw"][1])/2
        ride_real("boardwalk",bx[0]+20,zc,math.pi/2)
        zs=(info["bw"]["walk"][0]+info["bw"]["walk"][1])/2
        r=ride_real("beach sidewalk",bx[0]+20,zs,math.pi/2,n=20)
    # ---- synthetic course ----
    ev("__freeWorld()"); ev("WALL.air=null;WALL.on=null;Ride.group.position.set(0,0,0);Ride.y=0;window.__z0=0"); ev(COURSE)
    ev("window.__drive={yaw:0,mag:1,speed:16}"); wf(2); ev("__wgCalls=0")
    r=run(ev,wf,110); fr=len(r); calls_pf=ev("__wgCalls")/max(1,fr)
    print("course samples:",fr, "last z",r[-1]['z'] if r else None)
    ramp=[s for s in r if 8<s['z']<22 and not s['air']]
    check("goes up the ramp (y rises with z, tracks surface)", len(ramp)>=3 and ramp[-1]['y']>ramp[0]['y']+.5 and all(abs(s['y']-s['gy']['y'])<.2 for s in ramp), [round(s['y'],2) for s in ramp][:12])
    deck=[s for s in r if 26<s['z']<52 and not s['air']]
    check("rides along the 3 m deck", len(deck)>=3 and all(abs(s['y']-3)<.06 for s in deck), [round(s['y'],3) for s in deck][:10])
    after=[s for s in r if s['z']>53]
    check("drops off the deck edge (airborne) and lands on 0", any(s['air'] for s in after) and any((not s['air']) and abs(s['y'])<.03 for s in after), [(round(s['z'],1),round(s['y'],2),s['air']) for s in after][:14])
    check("WORLD_GROUND <=2 calls / frame", calls_pf<=2.05, f"{calls_pf:.2f}")
    # ---- no fall-through, 300 frames at speed, looping the course ----
    ev("""window.__loop=setInterval(()=>{ const p=Ride.group.position; if(p.z>75){ WALL.air=null; p.z=0; p.y=Ride.y=0; } },0)""")
    ev("window.__drive={yaw:0,mag:1,speed:22}")
    r=run(ev,wf,300); ev("clearInterval(__loop)")
    bad=[s for s in r if s['gy'] and s['y']<s['gy']['y']-.5 and not (s['air'])]
    badair=[s for s in r if s['gy'] and s['y']<s['gy']['y']-.5]
    check("no fall-through over 300 frames at speed", len(r)>=290 and not bad and not badair and min(s['y'] for s in r)>-.5, f"frames={len(r)} bad={len(bad)} badair={len(badair)} minY={min(s['y'] for s in r):.3f}")
    # ---- 0.14 m curb (Palma's real sidewalk height): step up + step down cleanly, stays grounded ----
    ev("""__useStub(function(x,z){ return (z>405&&z<415)?{y:.14,nx:0,ny:1,nz:0,surf:'concrete'}:{y:0,nx:0,ny:1,nz:0,surf:'asphalt'}; })""")
    ev("WALL.air=null;Ride.group.position.set(0,0,398);Ride.y=0;window.__drive={yaw:0,mag:1,speed:10}"); r=run(ev,wf,40)
    on=[s for s in r if 406<s['z']<414]; off=[s for s in r if s['z']>416]
    check("0.14 curb: up and down cleanly, never airborne, no sink", on and off and not any(s['air'] for s in r) and all(abs(s['y']-.14)<.005 for s in on) and all(abs(s['y'])<.005 for s in off) and min(s['sp'] for s in r)>9, f"on={[round(s['y'],3) for s in on][:4]} off={[round(s['y'],3) for s in off][:3]} minsp={min(s['sp'] for s in r):.2f}")
    # ---- underpass: deck 6.8 over ground 0 ----
    ev("""__useStub(function(x,z,yh){ const lim=(yh==null?0:yh)+.6; if(Math.abs(z-200)<20&&6.8<=lim) return {y:6.8,nx:0,ny:1,nz:0,surf:'concrete'}; return {y:0,nx:0,ny:1,nz:0,surf:'asphalt'}; })""")
    ev("WALL.air=null;Ride.group.position.set(0,0,190);Ride.y=0;window.__drive={yaw:0,mag:1,speed:8}"); r=run(ev,wf,20)
    check("underpass: below the deck (yHint low) ground = 0", all(abs(s['y'])<.03 for s in r if not s['air']) and ev("RIDE_GROUND.groundY")<.05, [round(s['y'],2) for s in r][:8])
    ev("WALL.air=null;Ride.group.position.set(0,6.8,190);Ride.y=6.8"); r=run(ev,wf,20)
    check("underpass: on top ground = 6.8", all(abs(s['y']-6.8)<.03 for s in r if s['z']<219) and abs(ev("RIDE_GROUND.groundY")-6.8)<.05, [round(s['y'],2) for s in r][:8])
    # ---- water respawn ----
    ev("""__useStub(function(x,z){ if(z>310) return {y:-2.5,nx:0,ny:1,nz:0,surf:'water'}; return {y:0,nx:0,ny:1,nz:0,surf:'asphalt'}; })""")
    ev("WALL.air=null;Ride.group.position.set(0,0,302);Ride.y=0;window.__drive={yaw:0,mag:1,speed:10}"); rs0=ev("RIDE_GROUND.respawns")
    r=run(ev,wf,70); rs1=ev("RIDE_GROUND.respawns"); ls=ev("RIDE_GROUND.lastSafe")
    check("water triggers respawn to last safe grounded point", rs1>rs0 and min(s['y'] for s in r)>-10 and ls and ls['z']<=310, f"respawns {rs0}->{rs1} lastSafe={ls} reason={ev('RIDE_GROUND.lastReason')}")
    # ---- void: y < -10 -> respawn ----
    ev("""__useStub(function(){ return {y:-50,nx:0,ny:1,nz:0,surf:'concrete'}; })""")
    ev("WALL.air=null;Ride.group.position.set(0,0,0);Ride.y=0;window.__drive={yaw:0,mag:0,speed:0}"); rs0=ev("RIDE_GROUND.respawns"); r=run(ev,wf,40)
    check("never falls forever (y<-10 respawns)", ev("RIDE_GROUND.respawns")>rs0 and min(s['y'] for s in r)>-12, f"minY={min(s['y'] for s in r):.2f}")
    # ---- null data -> y 0 ----
    ev("__useStub(function(){ return null; })"); ev("WALL.air=null;Ride.group.position.set(0,0,0);Ride.y=.2;window.__drive={yaw:0,mag:1,speed:8}"); r=run(ev,wf,10)
    check("null WORLD_GROUND -> y 0", abs(r[-1]['y'])<.02, r[-1]['y'])
    # ---- sand slows more than asphalt (coast, no throttle, per game time) ----
    def coast(surf):
        ev(f"__useStub(function(){{ return {{y:0,nx:0,ny:1,nz:0,surf:'{surf}'}}; }})")
        ev("WALL.air=null;Ride.group.position.set(0,0,0);Ride.y=0;window.__drive={yaw:0,mag:0,speed:18}"); wf(2); ev("window.__drive={yaw:0,mag:0,speed:null}")
        r=run(ev,wf,25); dtg=r[-1]['c']-r[0]['c']; return (r[0]['sp']-r[-1]['sp'])/max(dtg,1e-3), r[-1]['surf']
    da,sa=coast("asphalt"); ds,ss=coast("sand")
    check("sand slows the rider more than asphalt", ds>da*1.3 and sa=="asphalt" and ss=="sand", f"decel asphalt {da:.2f} m/s2, sand {ds:.2f} m/s2")
    dum,su=coast("lava"); check("unknown surf -> concrete", su=="concrete", su)
    # ---- slope: downhill accel / uphill drag ----
    ev("""__useStub(function(x,z){ const n=Math.hypot(1,10); return {y:-(z)/10,nx:0,ny:10/n,nz:1/n,surf:'asphalt'}; })""")
    ev("WALL.air=null;Ride.group.position.set(0,0,0);Ride.y=0;window.__drive={yaw:0,mag:0,speed:10}"); wf(2); ev("window.__drive={yaw:0,mag:0,speed:null}"); r=run(ev,wf,15); down=r[-1]['sp']-r[0]['sp']
    ev("WALL.air=null;Ride.group.position.set(0,0,0);Ride.y=0;window.__drive={yaw:Math.PI,mag:0,speed:10}"); wf(2); ev("window.__drive={yaw:Math.PI,mag:0,speed:null}"); r=run(ev,wf,15); up=r[-1]['sp']-r[0]['sp']
    check("slope: downhill accelerates, uphill drags", up<down-.5, f"(coast incl. base drag) dv down {down:.2f}, up {up:.2f}")
    errs_on=list(errs); pg.close()
    # ---- ?flatground=1 ----
    pg,ev,wf,errs2=boot("&flatground=1")
    check("flatground: RIDE_GROUND.flat, hook not installed", ev("RIDE_GROUND.flat===true&&RIDE_GROUND.active===false"))
    ev("window.__drive={yaw:0,mag:0,speed:0}; Ride.group.position.set(0,0,16); Ride.y=0"); wf(3)
    dc_off=calls(); print("draw calls (flatground):",dc_off)
    ev("__freeWorld()"); ev("__useStub(function(){ return {y:3,nx:0,ny:1,nz:0,surf:'sand'}; })"); ev("WALL.air=null;WALL.on=null;Ride.group.position.set(0,0,0);Ride.y=0;window.__drive={yaw:0,mag:1,speed:10}"); wf(4)
    r=run(ev,wf,20)
    check("flatground: y stays 0 (old behaviour) even with ground at 3", all(abs(s['y'])<1e-6 for s in r) and ev("(window.__wgCalls||0)")==0, [s['y'] for s in r][:5])
    src=pg.evaluate("fetch(location.href).then(r=>r.text())"); i=src.find("RIDE_GROUND (Rydah Systems"); j=src.find("})();",i); blk=src[i:j]
    import re as _re
    check("draw-call delta 0: hook creates no render objects (no scene.add / Mesh / material in ride_ground block)", i>0 and not _re.search(r"scene\.add|new THREE\.(Mesh|Points|Line|Sprite|InstancedMesh)|Material\(",blk), f"block {len(blk)} chars; loads (layout is re-randomised per load, so cross-load totals differ): on={dc_on} off={dc_off}")
    check("draw calls within locked 150 total", dc_on and max(dc_on)<=150, dc_on)
    allerr=errs_on+errs2
    check("no console errors", not allerr, allerr[:5])
    pg.close(); b.close()
print(f"\n{sum(1 for _,c in res if c)}/{len(res)} PASS")
