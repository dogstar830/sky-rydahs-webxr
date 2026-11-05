# Grind air-snap A/B probe (Rydah Systems, read-only on grind.js): drop onto a cable / rail from the air and check GRIND.on.
# Variants: default, ?noperf, ?flatground=1. Per variant: (a) spline-data drop (place rider 1 m above a cable mid point, falling),
# (b) the same drop with the RIDE_GROUND wraps bypassed (others() forced), (c) hop from the ground onto a low steel rail.
from playwright.sync_api import sync_playwright
import time, argparse, json
_ap=argparse.ArgumentParser(); _ap.add_argument("--port",type=int,default=8765); _ap.add_argument("--root",default="v3build")
A=_ap.parse_args()
BASE=f"http://localhost:{A.port}/{A.root}/sky-rydahs-v3-ikki.html?chars=/skyrydahs-characters/"
STUB="""(()=>{window.__pb=Array.from({length:17},()=>({pressed:false,touched:false,value:0}));
window.__pad={id:'Xbox stub',index:0,connected:true,mapping:'standard',axes:[0,0,0,0],buttons:window.__pb,timestamp:0,vibrationActuator:{playEffect:()=>Promise.resolve('complete')}};
navigator.getGamepads=()=>[window.__pad,null,null,null];})()"""
PICK="""([mat,maxY,minY])=>{ const out=[]; for(const s of GRIND.S){ if(s.mat!==mat||s.vert||s.kind==='npc'||s.rider||s.L<8) continue; const i=Math.floor(s.pts.length/2)-1; if(i<0) continue; const a=s.pts[i], b=s.pts[i+1]; const m={x:(a.x+b.x)/2,y:(a.y+b.y)/2,z:(a.z+b.z)/2};
  if(m.y>maxY||m.y<minY) continue; const t={x:b.x-a.x,z:b.z-a.z}; const l=Math.hypot(t.x,t.z)||1; out.push({id:s.id,kind:s.kind,m,t:{x:t.x/l,z:t.z/l}}); if(out.length>=3) break; } return out; }"""
TRY="""async ([c,dy,lat,frames])=>{ const R=Ride,p=R.group.position; GRIND.on=null; GRIND.cd=0; GRIND.prevP=null; WALL.on=null; GRAP.act=null; GRAP.deck=null; GRAP.airDeck=false;
  const nx=-c.t.z, nz=c.t.x; p.set(c.m.x+nx*lat,c.m.y+dy,c.m.z+nz*lat); R.y=p.y; R.yaw=Math.atan2(c.t.x,c.t.z);
  WALL.air={vx:c.t.x*9,vz:c.t.z*9,vy:-1,y:p.y,flip:false,t:.3}; const log=[]; const f0=frame;
  return await new Promise(res=>{ (function l(){ log.push({f:frame,y:+Ride.group.position.y.toFixed(3),air:!!WALL.air,ay:WALL.air?+WALL.air.y.toFixed(3):null,on:!!GRIND.on,cd:+(GRIND.cd||0).toFixed(2),pick:GRIND.lastPick?GRIND.lastPick.id:null,rg:window.RIDE_GROUND?RIDE_GROUND.groundY:null});
    if(GRIND.on||frame-f0>frames) res({locked:!!GRIND.on,id:GRIND.on?GRIND.on.s.id:null,log:log.slice(0,8)}); else requestAnimationFrame(l); })(); }); }"""
out={}
with sync_playwright() as p:
    b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    for name,q in [("default",""),("noperf","&noperf"),("flatground","&flatground=1")]:
        pg=b.new_page(viewport={"width":960,"height":540}); pg.set_default_timeout(300000); errs=[]
        pg.on("pageerror",lambda e: errs.append(str(e))); pg.on("console",lambda m: errs.append(m.text) if m.type=="error" else None)
        pg.add_init_script(STUB); pg.goto(BASE+q,timeout=300000); ev=pg.evaluate
        for i in range(150):
            if ev("typeof RIDERS!='undefined'&&RIDERS.ready&&typeof TURF!='undefined'&&TURF.ready&&window.GRIND&&GRIND.world"): break
            time.sleep(1)
        def wf(n=3):
            st=ev("frame"); t0=time.time()
            while ev("frame")<st+n and time.time()-t0<120: time.sleep(.05)
        for k in range(12):
            if ev("State.mode")=="ride": break
            ev("__pb[0].pressed=true;__pb[0].value=1"); wf(4); ev("__pb[0].pressed=false;__pb[0].value=0"); wf(3); time.sleep(.5)
        ev("window.__hideIkkiNpc=true"); r={"S":ev("GRIND.S.length"),"grid":ev("GRIND.grid.size"),"perf":ev("JSON.stringify(window.WORLD_PERF&&WORLD_PERF.stats||null).slice(0,160)"),"mats":ev("(()=>{const m={};for(const s of GRIND.S){const k=s.mat+'/'+s.kind+(s.vert?'/v':'');m[k]=(m[k]||0)+1;}return m;})()")}
        cab=ev(PICK,["cable",40,1.5]) or []; rail=ev(PICK,["steel",1.3,.3]) or []
        r["cables"]=cab; r["rails"]=rail; r["drop"]=[]
        for c in cab[:2]:
            for dy,lat in [(1.0,0),(1.0,.6)]:
                x=ev(TRY,[c,dy,lat,25]); r["drop"].append({"id":c["id"],"dy":dy,"lat":lat,"locked":x["locked"],"log":x["log"]})
        if rail:
            x=ev(TRY,[rail[0],.8,.3,25]); r["rail_drop"]={"id":rail[0]["id"],"locked":x["locked"],"log":x["log"]}
        # real pad hop (A) from the ground directly under a cable, moving along it: apex vs cable height
        if cab:
            c=cab[0]; ev(f"GRIND.on=null;GRIND.cd=0;WALL.air=null;WALL.on=null;Ride.group.position.set({c['m']['x']},0,{c['m']['z']});Ride.y=0;Ride.yaw=Math.atan2({c['t']['x']},{c['t']['z']});Ride.speed=10"); wf(3)
            ev("window.__mx=0;window.__lk=false;(function l(){ __mx=Math.max(__mx,Ride.group.position.y); if(GRIND.on) __lk=true; if(!window.__stopL) requestAnimationFrame(l); })()")
            ev("__pb[0].pressed=true;__pb[0].value=1"); wf(4); ev("__pb[0].pressed=false;__pb[0].value=0"); wf(40); ev("window.__stopL=true")
            r["hop_under_cable"]={"cable_y":c["m"]["y"],"apex":ev("__mx"),"locked":ev("__lk")}
        r["errs"]=errs[:5]; out[name]=r
        print(name,json.dumps({k:(v if k not in("drop",) else [(d["id"],d["dy"],d["lat"],d["locked"]) for d in v]) for k,v in r.items() if k not in("cables","rails")},default=str)[:1500],flush=True)
        pg.close()
    b.close()
json.dump(out,open("/tmp/rg_root/grind_airsnap.json","w"),indent=1); print("saved /tmp/rg_root/grind_airsnap.json")
