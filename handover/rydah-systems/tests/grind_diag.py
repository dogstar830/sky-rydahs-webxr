# Cable air-snap diagnosis (Rydah Systems, read-only): replays tests/grind.py step 1 (__pick('cable') + __air(__c,2,14)) and logs
# grindTryLock inputs per frame. Variants: default / ?noperf / ?flatground=1. Result -> /tmp/rg_root/grind_diag.json
from playwright.sync_api import sync_playwright
import time, json, argparse
_ap=argparse.ArgumentParser(); _ap.add_argument("--port",type=int,default=8765); _ap.add_argument("--root",default="v3build"); _ap.add_argument("--html",default="sky-rydahs-v3-ikki.html"); _ap.add_argument("--out",default="/tmp/rg_root/grind_diag.json"); A=_ap.parse_args()
BASE=f"http://localhost:{A.port}/{A.root}/{A.html}?chars=/skyrydahs-characters/"
STUB="""window.__gp={id:'stub',index:0,connected:true,mapping:'standard',axes:[0,0,0,0],buttons:Array.from({length:17},()=>({pressed:false,value:0})),timestamp:0};navigator.getGamepads=()=>[window.__gp];"""
HELP="""window.__pick=k=>GRIND.S.filter(s=>s.kind===k&&s.L>12&&s.pts.every(p=>onLand(p.x,p.z))).sort((a,b)=>b.L-a.L)[0];
window.__air=(s,arc,sp)=>{GRIND.on=null;GRIND.cd=0;GRIND.ignore=null;const q=grindAt(s,arc,new THREE.Vector3()),t=new THREE.Vector3();grindAt(s,arc+.5,new THREE.Vector3(),t);
  Ride.group.position.set(q.x-t.x*.6,q.y+.5,q.z-t.z*.6);Ride.y=q.y+.5;WALL.on=null;wallLaunch(t.x*sp,t.z*sp,-1,false);WALL.air.y=q.y+.5;WALL.air.t=.3;};0"""
LOG="""()=>new Promise(res=>{ const c=__c, L=[]; let lf=frame;
 const tl=grindTryLock; let calls=0; grindTryLock=function(dt){ calls++; const A=WALL.air,p=Ride.group.position; const fy=A?A.y:Ride.y; const C=grindAll(new THREE.Vector3(p.x,fy,p.z),1.6);
   const me=C.find(n=>n.s===c); const r=tl(dt); L.push({f:frame,x:+p.x.toFixed(2),z:+p.z.toFixed(2),y:+p.y.toFixed(3),Ay:A?+A.y.toFixed(3):null,vy:A?+A.vy.toFixed(2):null,At:A?+A.t.toFixed(2):null,cd:+GRIND.cd.toFixed(2),
     cands:C.map(n=>n.s.kind+'#'+n.s.id+':'+n.d.toFixed(2)),meD:me?+me.d.toFixed(3):null,meQy:me?+me.q.y.toFixed(2):null,ret:r,pick:GRIND.lastPick,mode:State.mode,grap:typeof GRAP!=='undefined'?!!(GRAP.act||GRAP.deck||GRAP.airDeck):null}); return r; };
 __air(c,2,14); const f0=frame;
 (function l(){ if(GRIND.on||frame-f0>14){ grindTryLock=tl; res({locked:!!GRIND.on,lockedSame:!!GRIND.on&&GRIND.on.s===c,calls,log:L}); } else requestAnimationFrame(l); })(); })"""
out={}
with sync_playwright() as p:
    b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    for name,q in [("default",""),("noperf","&noperf"),("flatground","&flatground=1")]:
        pg=b.new_page(viewport={"width":1280,"height":720}); pg.set_default_timeout(300000); errs=[]
        pg.on("pageerror",lambda e: errs.append(str(e))); pg.add_init_script(STUB); pg.goto(BASE+q,timeout=300000); ev=pg.evaluate
        for i in range(150):
            if ev("typeof RIDERS!='undefined'&&RIDERS.ready&&typeof TURF!='undefined'&&TURF.ready"): break
            time.sleep(1)
        time.sleep(2)
        for k in range(8):  # leave the menu for real: startRide() teleports to spawn, so nothing may be placed before it ran
            if ev("State.mode==='ride'"): break
            pg.keyboard.press("Enter"); t0=time.time()
            while ev("State.mode")!="ride" and time.time()-t0<20: time.sleep(.2)
        st=ev("frame")
        while ev("frame")<st+3: time.sleep(.1)
        ev(HELP)
        ev("window.__npcPassive=true;window.__npcFreeze=true;window.__hideIkkiNpc=true;garages.forEach(g=>g.gate&&(g.gate.dismissed=true));if(typeof GATE!='undefined'){GATE.uiOpen=false;}")
        for i in range(30):
            if ev("!!GRIND.world"): break
            time.sleep(1)
        info=ev("""(()=>{ window.__c=__pick('cable'); const c=__c; if(!c) return null; return {id:c.id,kind:c.kind,mat:c.mat,L:+c.L.toFixed(1),r:c.r,n:c.pts.length,p0:c.pts[0].toArray().map(v=>+v.toFixed(2)),p1:c.pts[c.pts.length-1].toArray().map(v=>+v.toFixed(2)),
           ys:c.pts.map(p=>+p.y.toFixed(2)).slice(0,6),mode:State.mode,seed:location.search,inS:GRIND.S.indexOf(c)===c.id}; })()""")
        r={"cable":info}
        if info: r.update(ev(LOG))
        APEX="""async ([dy,vy,lat])=>{ const c=__c, R=Ride, p=R.group.position; GRIND.on=null; GRIND.cd=0; GRIND.ignore=null; GRIND.prevP=null; WALL.on=null;
          const q=grindAt(c,c.L/2,new THREE.Vector3()), t=new THREE.Vector3(); grindAt(c,c.L/2+.5,new THREE.Vector3(),t); const nx=-t.z, nz=t.x;
          p.set(q.x+nx*lat,q.y+dy,q.z+nz*lat); R.y=p.y; R.yaw=Math.atan2(t.x,t.z); wallLaunch(t.x*8,t.z*8,vy,false); WALL.air.y=p.y; WALL.air.t=.3; const f0=frame;
          return await new Promise(res=>{ (function l(){ if(GRIND.on||frame-f0>8||!WALL.air) res({dy,vy,lat,locked:!!GRIND.on,same:!!GRIND.on&&GRIND.on.s===c,frames:frame-f0}); else requestAnimationFrame(l); })(); }); }"""
        if info:
            r["apex"]=[ev(APEX,[dy,vy,lat]) for dy in (-1.4,-1.0,-0.5,0.5,1.0,1.4) for vy,lat in ((0,0),(0,.5),(1.0,0))]
            r["mode_at_pick"]=ev("State.mode")
        r["errs"]=errs[:4]; out[name]=r; print(name,"locked",r.get("locked"),"same",r.get("lockedSame"),"first",json.dumps((r.get("log") or [None])[0]),"\n apex",[(a["dy"],a["vy"],a["lat"],a["locked"]) for a in r.get("apex",[])],flush=True); pg.close()
    b.close()
json.dump(out,open(A.out,"w"),indent=1)
