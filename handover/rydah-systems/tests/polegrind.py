# Pole grind (polegrind.js, Rydah Systems): entry on a real wooden pole, spiral climb around the pole axis, Rigger state calls
# (setState('polegrind',{variant:'climb'|'top',poleAxis,side}) / setState(null)), helix fade timing (.30 in / 1.6 loop / .25 out, GAME time),
# top -> pop onto the pole's cable (cable grind lock), draw delta <= 1, grind.js vortex gate (only while grinding; XR cap), no errors.
# Usage: python3 tests/polegrind.py [base_url] [page] [--hero]   (run under .testlock). --hero: Oliver's standard shot -> shots/hero/polegrind.png
from playwright.sync_api import sync_playwright
import sys, time, json, os
HERO="--hero" in sys.argv; sys.argv=[a for a in sys.argv if a!="--hero"]
BASE=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8765"; PAGE=sys.argv[2] if len(sys.argv)>2 else "v3build/sky-rydahs-v3-ikki.html"
SH="/workspace/v3build/shots/"; res=[]
def check(n,c,i=""): res.append((n,bool(c))); print(("PASS " if c else "FAIL ")+n,i,flush=True)
with sync_playwright() as p:
    b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    pg=(b.new_page(viewport={"width":1920,"height":1080},device_scale_factor=1.5) if HERO else b.new_page(viewport={"width":1280,"height":720})); pg.set_default_timeout(240000); errs=[]
    pg.on("pageerror",lambda e: errs.append("PAGEERROR "+str(e))); pg.on("console",lambda m: errs.append("console: "+m.text) if m.type=="error" else None)
    pg.goto(f"{BASE}/{PAGE}?chars=/skyrydahs-characters/"+("&tier=hd&seed=1" if HERO else ""),timeout=300000); ev=pg.evaluate
    for i in range(150):
        if ev("typeof RIDERS!='undefined'&&RIDERS.ready&&typeof GRIND!=='undefined'&&typeof PG!=='undefined'"): break
        time.sleep(1)
    time.sleep(2)
    for k in range(8):
        if ev("State.mode")=="ride": break
        pg.keyboard.press("Enter"); time.sleep(2)
    if ev("State.mode")!="ride": ev("startRide(false)"); time.sleep(1)
    def wc(sec,until=None,cap=200):
        c0=ev("clock"); t0=time.time()
        while time.time()-t0<cap:
            if until and ev(until): return True
            if ev("clock")>=c0+sec: return bool(until and ev(until))
            time.sleep(.1)
        return False
    if not ev("GRIND.built||GRIND.world"): wc(2,"GRIND.world",60)
    ev("window.__npcPassive=true;window.__hideIkkiNpc=true;try{garages.forEach(g=>g.gate&&(g.gate.dismissed=true));GATE.uiOpen=false}catch(e){}")
    check("in ride mode, PG + TRAILS loaded", ev("State.mode==='ride'&&!!window.PG&&!!window.TRAILS"))
    # wooden pole whose top has a cable within PG.POP_R
    pole=ev("""(()=>{ for(const s of GRIND.S){ if(!(s.vert&&s.kind==='pole')) continue; const t=s.pts[s.pts.length-1]; const c=grindAll(t,PG.POP_R).filter(n=>!n.s.vert&&Math.abs(n.q.y-t.y)<2.5);
        const b=s.pts[0]; if(!c.length) continue; for(const a of [0,1.57,3.14,4.71]){ const x=b.x+Math.sin(a)*4, z=b.z+Math.cos(a)*4; if(onLand(x,z)&&!colliders.some(o=>!o.off&&x>o.minX-.6&&x<o.maxX+.6&&z>o.minZ-.6&&z<o.maxZ+.6))
          return {id:s.id,base:[b.x,b.y,b.z],top:[t.x,t.y,t.z],L:s.L,r:s.r,cable:c[0].s.id,cmat:c[0].s.mat,start:[x,z],yaw:Math.atan2(b.x-x,b.z-z)}; } } return null; })()""")
    print("pole",pole,flush=True); check("found a wooden pole with a cable at its top", pole is not None, pole)
    if not pole: b.close(); print("RESULT",sum(c for _,c in res),"/",len(res)); sys.exit(1)
    ev("window.__ss=[];(()=>{const u=RIDERS.player&&RIDERS.player.userData; window.__hasSS=!!(u&&typeof u.setState==='function'); if(__hasSS&&!u.setState.__spy){ const f=u.setState; u.setState=function(n,o){ __ss.push([+clock.toFixed(2),n,o&&o.variant||null,!!(o&&o.poleAxis)]); return f.apply(this,arguments); }; u.setState.__spy=1; } })()")
    if HERO:
        ev("SKY&&SKY.setDay&&SKY.setDay(0)")   # night (ref1/ref3 FX read best at night)
    # ---- entry: skate head-on into the pole at dash speed (real lock path: grindTryLock head-on <= 20 deg, speed >= 5)
    x,z=pole["start"]; ev(f"WALL.on=WALL.air=null;GRIND.on=null;GRIND.cd=0;Ride.grinding=false;Ride.y=0;Ride.group.position.set({x},0,{z});Ride.yaw={pole['yaw']};Ride.speed=20;window.__camHook=null")
    ev("window.__pl=[];(function f(){ if(__pl.length>400) return; const p=Ride.group.position,O=GRIND.on; __pl.push([+clock.toFixed(3),+p.x.toFixed(3),+p.y.toFixed(3),+p.z.toFixed(3),O?O.s.id:0,O?O.s.mat:'',PG.on?1:0,+PG.k.toFixed(3),PG.ph,PG.mesh&&PG.mesh.visible?1:0,+PG.ang.toFixed(3),+Ride.group.rotation.x.toFixed(4),+Ride.group.rotation.z.toFixed(4)]); requestAnimationFrame(f); })()")
    real=wc(2,f"!!GRIND.on&&GRIND.on.s.id==={pole['id']}")
    if not real:   # fallback: direct lock at the foot (records that the head-on path missed)
        ev(f"(()=>{{const s=GRIND.S.find(s=>s.id==={pole['id']});GRIND.on=null;WALL.air=null;Ride.speed=20;grindLock(s,.3,1,17,1);}})()")
    check("entry: head-on skate-in locks onto the pole (real grindTryLock path)", real, ev("JSON.stringify({on:!!GRIND.on,id:GRIND.on&&GRIND.on.s.id,pg:PG.on,ph:PG.ph})"))
    if HERO:
        # Systems 04:05: hold the rider mid-climb (arc clamped to 3.5-5.5 m, speed kept) so the helix stays in full hold for the >=60-frame warm-up,
        # camera 6 m out on a clear, on-land side of the pole, ~1.6 m below the rider, looking UP at them (ref3 framing)
        ev(f"window.__hold=true;(function f(){{ if(!window.__hold) return; const O=GRIND.on; if(O&&O.s.id==={pole['id']}){{ if(O.arc>5.5) O.arc=3.5; O.v=Math.max(O.v,9); O.dir=1; PG.topT=-1; }} requestAnimationFrame(f); }})()")
        cam=ev(f"""(()=>{{ const b={pole['base']}; const segClear=(x0,z0,x1,z1)=>!colliders.some(c=>{{ if(c.off) return false; for(let i=1;i<20;i++){{ const t=i/20,x=x0+(x1-x0)*t,z=z0+(z1-z0)*t; if(x>c.minX&&x<c.maxX&&z>c.minZ&&z<c.maxZ) return true; }} return false; }});
          let best=null; for(let k=0;k<48;k++){{ const a=k/48*6.2832; for(const d of [3.8,3.5,4]){{ const x=b[0]+Math.sin(a)*d, z=b[2]+Math.cos(a)*d; if(!onLand(x,z)) continue; if(colliders.some(c=>!c.off&&x>c.minX-.6&&x<c.maxX+.6&&z>c.minZ-.6&&z<c.maxZ+.6)) continue; if(!segClear(x,z,b[0],b[2])) continue;
            const fx=-Math.sin(a),fz=-Math.cos(a); let clut=0; for(const c of colliders){{ if(c.off) continue; const cx=(c.minX+c.maxX)/2-x,cz=(c.minZ+c.maxZ)/2-z,L=Math.hypot(cx,cz); if(L<1||L>30) continue; if((cx*fx+cz*fz)/L>Math.cos(.6)) clut+=Math.max(1,(c.maxY||8))/L; }}   // walls inside the ~70deg view cone
            if(!best||clut<best.clut) best={{x,z,a,d,clut}}; break; }} }} return best; }})()""")
        print("hero cam",cam,flush=True)
        ev(f"window.__camHook=()=>{{const b={pole['base']},p=Ride.group.position;camera.position.set({cam['x']},Math.max(.8,p.y-3.),{cam['z']});camera.lookAt(b[0],p.y+.1,b[2]);}}")
        f0=ev("frame"); t0=time.time()
        while ev("frame")<f0+60 and time.time()-t0<420: time.sleep(.5)
        wc(.2,"PG.k>.99&&PG.mesh.visible")
        os.makedirs(SH+"hero",exist_ok=True); pg.screenshot(path=SH+"hero/polegrind.png",timeout=240000)
        print("HERO shot saved", ev("frame")-f0, "frames", ev("JSON.stringify({k:PG.k,ph:PG.ph,vis:PG.mesh.visible,y:+Ride.group.position.y.toFixed(2),day:SKY.u&&SKY.u.value,on:!!GRIND.on})"),flush=True)
        b.close(); sys.exit(0)
    wc(.4,"PG.ph==='hold'")
    # draw delta of the helix (direct render, same frame, helix on vs off)
    dc=ev("(()=>{const r=renderer.info,a=r.autoReset;r.autoReset=false;const M=PG.mesh,D=PG.deb,v=M.visible,w=D.visible;M.visible=D.visible=true;r.reset();renderer.render(scene,camera);const c1=r.render.calls;M.visible=D.visible=false;r.reset();renderer.render(scene,camera);const c0=r.render.calls;M.visible=v;D.visible=w;r.autoReset=a;return [c0,c1]})()")
    check("pole-grind FX draw delta <= 2 (helix + debris, 1 draw each)", 0<=dc[1]-dc[0]<=2, dc)
    check("Quest budget: total draws while pole grinding <= 150", dc[1]<=150, dc)
    vis_mid=ev("PG.mesh.visible&&PG.k>0.99"); check("helix visible at full strength during the climb (hold)", vis_mid, ev("JSON.stringify({k:PG.k,ph:PG.ph})"))
    # ---- climb to the top -> 'top' state -> pop onto the cable (chain into the cable grind)
    got=wc(6,f"!!GRIND.on&&!GRIND.on.s.vert&&PG.stats.cablePops>0",cap=300)
    pl=ev("JSON.stringify(__pl)"); PL=json.loads(pl)
    on=[r for r in PL if r[4]==pole["id"] and r[6]==1]
    import math
    angs=[r[10] for r in on]; ys=[r[2] for r in on]; bx,bz=pole["base"][0],pole["base"][2]; rads=[math.hypot(r[1]-bx,r[3]-bz) for r in on]
    sweep=sum(abs(math.atan2(math.sin(b2-a2),math.cos(b2-a2))) for a2,b2 in zip(angs,angs[1:])) if len(angs)>1 else 0
    info={"frames":len(on),"y0":ys[0] if ys else None,"y1":max(ys) if ys else None,"sweep_rad":round(sweep,2),"rmin":round(min(rads),3) if rads else None,"rmax":round(max(rads),3) if rads else None}
    check("spiral climb: rider orbits the pole axis at a constant radius while rising", len(on)>=4 and info["y1"]-info["y0"]>3 and sweep>math.pi and info["rmax"]-info["rmin"]<.05, info)
    check("VR-safe: rider rig never rolls/pitches on the pole (yaw only)", all(abs(r[11])<1e-6 and abs(r[12])<1e-6 for r in on) if on else False, [(r[11],r[12]) for r in on[:3]])
    pop=ev("JSON.stringify({stats:PG.stats,popTo:PG.popTo,on:GRIND.on&&{id:GRIND.on.s.id,mat:GRIND.on.s.mat},err:PG.err||null})")
    check("top: pops onto the pole's cable and locks into the cable grind", got, pop)
    wc(.5,"PG.ph==='off'")
    ss=ev("JSON.stringify({has:__hasSS,ss:__ss,log:PG.stateLog})"); S=json.loads(ss); seq=[(e[1],e[2]) for e in S["ss"]]
    check("Rigger state calls: setState('polegrind',climb) -> ('polegrind',top) -> setState(null), with poleAxis", S["has"] and seq[:3]==[("polegrind","climb"),("polegrind","top"),(None,None)] and all(e[3] for e in S["ss"][:2]), ss[:400])
    tl=ev("JSON.stringify(PG.tl)"); T=json.loads(tl); tt={}
    for e in T: tt.setdefault(e[0].split(":")[0],e[1])
    ent=round(tt.get("hold",0)-tt.get("enter",0),3); ex=round(tt.get("hidden",0)-tt.get("exit",0),3)
    check("helix timing: fade-in 0.30 s, fade-out 0.25 s (game time, +-0.08)", abs(ent-.30)<=.08 and abs(ex-.25)<=.08, {"in":ent,"out":ex,"tl":T[-8:]})
    check("helix + debris hidden after the exit fade (0 extra draws when idle)", ev("!PG.mesh.visible&&!PG.deb.visible&&PG.k===0"), ev("JSON.stringify({k:PG.k,vis:PG.mesh.visible,deb:PG.deb.visible})"))
    lp=ev("JSON.stringify({hold:PG.HOLD,uT:PG.mesh.material.uniforms.uT.value})"); check("hold loop period = Rigger's 1.6 s (uT wraps at PG.HOLD)", json.loads(lp)["hold"]==1.6, lp)
    # ---- grind.js vortex focus only while grinding (runtime gate / proposed diff)
    ev("GRIND.on=null;Ride.grinding=false;WALL.air=WALL.on=null;Ride.y=0;Ride.speed=14"); wc(.6)
    vg=ev("JSON.stringify({vk:+(GRIND.vk||0).toFixed(3),vis:GRIND.vortex.visible,speed:Ride.speed,diff:GRIND.VORTEX_XR_CAP!==undefined})")
    check("vortex focus quad off when NOT grinding at >7 m/s", '"vis":false' in vg, vg)
    check("no page errors / polegrind fx errors", not errs and not ev("PG.fxErr||PG.err||null"), (errs[:3],ev("PG.fxErr||PG.err||null")))
    b.close()
n=sum(1 for _,c in res if c); print("RESULT",n,"/",len(res)); sys.exit(0 if n==len(res) else 1)
