# Pooled trail ribbon (trails.js, Rydah Systems): ONE mesh / 1 draw for player wheel trails + NPC trails (<= 12 m) + turf_dash streaks.
# Usage: python3 tests/trails.py [base_url] [page]   (run under .testlock). GAME-time waits. Shot: shots/trails.png
from playwright.sync_api import sync_playwright
import sys, time, json
BASE=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8765"; PAGE=sys.argv[2] if len(sys.argv)>2 else "v3build/sky-rydahs-v3-ikki.html"
SH="/workspace/v3build/shots/"; res=[]
def check(n,c,i=""): res.append((n,bool(c))); print(("PASS " if c else "FAIL ")+n,i,flush=True)
with sync_playwright() as p:
    b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    pg=b.new_page(viewport={"width":1280,"height":720}); pg.set_default_timeout(240000); errs=[]
    pg.on("pageerror",lambda e: errs.append("PAGEERROR "+str(e))); pg.goto(f"{BASE}/{PAGE}?chars=/skyrydahs-characters/",timeout=300000); ev=pg.evaluate
    for i in range(150):
        if ev("typeof RIDERS!='undefined'&&RIDERS.ready&&typeof TRAILS!=='undefined'"): break
        time.sleep(1)
    time.sleep(2)
    for k in range(8):
        if ev("State.mode")=="ride": break
        pg.keyboard.press("Enter"); time.sleep(2)
    def wc(sec,until=None,cap=200):
        c0=ev("clock"); t0=time.time()
        while time.time()-t0<cap:
            if until and ev(until): return True
            if ev("clock")>=c0+sec: return bool(until and ev(until))
            time.sleep(.1)
        return False
    ev("window.__npcPassive=true;try{garages.forEach(g=>g.gate&&(g.gate.dismissed=true));GATE.uiOpen=false}catch(e){}")
    # open ground far from NPCs (> 12 m), roll at 10 m/s
    o=ev("(()=>{for(let i=0;i<4000;i++){const x=-150+Math.random()*300,z=-150+Math.random()*300;if(onLand(x,z)&&!colliders.some(c=>x>c.minX-15&&x<c.maxX+15&&z>c.minZ-15&&z<c.maxZ+15)&&!atkTargets().some(n=>Math.hypot(n.holder.position.x-x,n.holder.position.z-z)<40))return [x,z]}return null})()")
    ev(f"WALL.on=WALL.air=null;GRIND.on=null;Ride.grinding=false;Ride.y=0;Ride.group.position.set({o[0]},0,{o[1]});Ride.yaw=0;Ride.speed=10;Ride.maxSpeed=Math.max(Ride.maxSpeed,10);window.__camHook=()=>{{const p=Ride.group.position;camera.position.set(p.x+3,2.2,p.z-4);camera.lookAt(p.x,.4,p.z+1.5);}}")
    ev("window.__keep=true;(function f(){ if(!window.__keep) return; Ride.speed=Math.max(Ride.speed,10); requestAnimationFrame(f); })()")
    wc(1.2)
    st=ev("JSON.stringify({vis:TRAILS.mesh.visible,live:TRAILS.live,stats:TRAILS.stats,range:TRAILS.mesh.geometry.drawRange.count,meshes:(()=>{let n=0;scene.traverse(o=>{if(o.name==='trails_ring')n++});return n})()})")
    S=json.loads(st); check("player wheel trails show (2 trails, ring mesh visible)", S["vis"] and S["live"]>=2 and S["stats"]["player"]==2 and S["range"]>0, st)
    check("NPCs farther than 12 m get no trails", S["stats"]["npc"]==0, st)
    check("exactly one trail ring mesh in the scene", S["meshes"]==1, st)
    dc=ev("(()=>{const r=renderer.info,a=r.autoReset;r.autoReset=false;const M=TRAILS.mesh,v=M.visible;M.visible=true;r.reset();renderer.render(scene,camera);const c1=r.render.calls;M.visible=false;r.reset();renderer.render(scene,camera);const c0=r.render.calls;M.visible=v;r.autoReset=a;return [c0,c1]})()")
    check("all trails = 1 draw (delta trails on/off)", dc[1]-dc[0]==1, dc)
    # dash streaks absorbed: dash on -> 2 more trails in the SAME mesh, turf_dash's own ribbon stays hidden
    ev("DASH.t=.75;DASH.fx=1"); wc(.25)
    d=ev("JSON.stringify({live:TRAILS.live,stats:TRAILS.stats,dashOwn:!!(DASH.trail&&DASH.trail.visible)})")
    check("dash ribbons go into the pooled ring (turf_dash ribbon hidden)", '"dash":2' in d and '"dashOwn":false' in d, d)
    try: pg.screenshot(path=SH+"trails.png",timeout=120000)
    except Exception as e: print("shot",e)
    dc2=ev("(()=>{const r=renderer.info,a=r.autoReset;r.autoReset=false;const M=TRAILS.mesh,v=M.visible;M.visible=true;r.reset();renderer.render(scene,camera);const c1=r.render.calls;M.visible=false;r.reset();renderer.render(scene,camera);const c0=r.render.calls;M.visible=v;r.autoReset=a;return [c0,c1]})()")
    check("player + dash trails still 1 draw", dc2[1]-dc2[0]==1, dc2)
    # NPC within 12 m (moving: its own loop) -> NPC trails appear, still 1 mesh
    ev("window.__keep=false;DASH.t=0;DASH.fx=0;const n=RIDERS.npcs.find(n=>n.g&&n.holder&&n.mode!==1)||RIDERS.npcs.find(n=>n.g);window.__N=n;const g=n.g,q=n.holder.position;Ride.group.position.set(g.pos[0]+Math.sin(g.th)*6,0,g.pos[1]+Math.cos(g.th)*6);Ride.speed=0;window.__camHook=()=>{const p=Ride.group.position;camera.position.set(p.x+4,4,p.z+6);camera.lookAt(q.x,.5,q.z);}")
    wc(3,"TRAILS.stats.npc>0",cap=300)
    mv=ev("(()=>{const q=__N.holder.position.clone();return new Promise(r=>{const c0=clock;(function f(){ if(clock<c0+.5) return requestAnimationFrame(f); r(JSON.stringify({mode:__N.mode,vis:__N.holder.visible,inT:atkTargets().includes(__N),moved:+q.distanceTo(__N.holder.position).toFixed(2),child:__N.holder.children.length}));})();});})()"); print("npc motion",mv,flush=True)
    n=ev("JSON.stringify({stats:TRAILS.stats,live:TRAILS.live,d:+Math.hypot(__N.holder.position.x-Ride.group.position.x,__N.holder.position.z-Ride.group.position.z).toFixed(2)})")
    check("moving NPC within 12 m gets wheel trails", '"npc":2' in n or '"npc":4' in n, n)
    check("no page errors", not errs and not ev("PG.fxErr||null"), (errs[:3],ev("PG.fxErr||null")))
    b.close()
nn=sum(1 for _,c in res if c); print("RESULT",nn,"/",len(res)); sys.exit(0 if nn==len(res) else 1)
