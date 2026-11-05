# Draw-call budget test (Rydah Optimizer). LOCKED metric: renderer.info.render.calls, desktop non-XR, fixed camera, ?nofx.
# Budget: total<=150, world<=110, chars+fx<=40. Integrator only, under /workspace/v3build/.testlock.
# usage: python3 drawcall_budget.py [--port 8765] [--url-path v3build/sky-rydahs-v3-ikki.html] [--player ikki] [--tier quest]
#                                   [--extra noperf] [--json-out FILE] [--frames 30]
#        python3 drawcall_budget.py --compare A.json B.json     (module diff table, e.g. 'diff 180 -> 271'; no browser)
import argparse,json,os,statistics,sys,time
ap=argparse.ArgumentParser(); ap.add_argument("--port",type=int,default=8765); ap.add_argument("--url-path",default="v3build/sky-rydahs-v3-ikki.html")
ap.add_argument("--player",default="ikki"); ap.add_argument("--tier",default=None); ap.add_argument("--extra",default="",help="extra query, e.g. noperf")
ap.add_argument("--json-out",default=None); ap.add_argument("--frames",type=int,default=30); ap.add_argument("--compare",nargs=2,metavar=("A","B"))
A=ap.parse_args()
RES="/workspace/v3build/perf/drawcalls/results"; METER="/workspace/v3build/perf/drawcalls/dc_meter.js"
BUD={"total":150,"world":110,"charsfx":40}

def load(p):
    d=json.load(open(p)); return d.get("cameras",d) if isinstance(d,dict) else d
def compare(a,b):
    A_,B_=load(a),load(b); print(f"compare {a} -> {b}")
    for cam in sorted(set(A_)|set(B_)):
        x,y=A_.get(cam,{}),B_.get(cam,{}); tx,ty=x.get("max",{}).get("calls","-"),y.get("max",{}).get("calls","-")
        print(f"\n== {cam}: diff {tx} to {ty}")
        for k in ("calls","world","chars","fx","triangles"):
            vx,vy=x.get("max",{}).get(k),y.get("max",{}).get(k); d=(vy-vx) if isinstance(vx,(int,float)) and isinstance(vy,(int,float)) else ""
            print(f"  {k:10s} {str(vx):>9s} {str(vy):>9s} {('%+d'%d) if d!='' else '':>8s}")
        mx={m["module"]:m["draws"] for m in x.get("byModule",[])}; my={m["module"]:m["draws"] for m in y.get("byModule",[])}
        rows=sorted(((m,mx.get(m,0),my.get(m,0)) for m in set(mx)|set(my)),key=lambda r:-abs(r[2]-r[1]))
        print(f"  {'module':48s} {'A':>5s} {'B':>5s} {'diff':>6s}")
        for m,u,v in rows:
            if u!=v: print(f"  {m[:48]:48s} {u:5d} {v:5d} {v-u:+6d}")
    sys.exit(0)
if A.compare: compare(*A.compare)

from playwright.sync_api import sync_playwright
q=f"chars=/skyrydahs-characters/&player={A.player}&nofx"+(f"&tier={A.tier}" if A.tier else "")+(("&"+A.extra.lstrip("&")) if A.extra else "")
URL=f"http://localhost:{A.port}/{A.url_path.lstrip('/')}?{q}"
# Day = same overrides as demo_check.py DAY (hemi light, fog, background, FACADE/BRIDGES/SKY setDay). Game boots in night.
DAY="""(()=>{scene.traverse(o=>{if(o.isHemisphereLight){o.intensity=.85;o.color.set(0xcfe0ff);o.groundColor.set(0x6a6470);}});
scene.fog.color.set(0xb8c8e0);if(typeof _fogBase!=='undefined')_fogBase.set(0xb8c8e0);scene.background.set(0x9ab8e0);
if(window.FACADE)FACADE.setDay(1);if(window.BRIDGES)BRIDGES.setDay(1);if(window.SKY)SKY.setDay(1);if(window.GRAF)GRAF.forceNight=false;})()"""
# Bridge poses = demo_check.py BR (bridge_causeway == causeway_west, bridge_b98 == b98). Portside = PALMA district box centre, looking +z.
BR="""((id)=>{GRIND.on=null;const b=PALMA.bridges.find(q=>q.id===id),mx=(b.a[0]+b.b[0])/2,mz=(b.a[1]+b.b[1])/2,L=Math.hypot(b.b[0]-b.a[0],b.b[1]-b.a[1]),
 ux=(b.b[0]-b.a[0])/L,uz=(b.b[1]-b.a[1])/L,px=uz,pz=-ux; Ride.group.position.set(b.a[0]-ux*30,0,b.a[1]-uz*30);
 window.__dcCam=[mx-px*L*.6+ux*L*.2,9,mz-pz*L*.6+uz*L*.2, mx,6,mz];})"""
PORT_JS="""(()=>{GRIND.on=null;const d=PALMA.districts.find(q=>q.id==='portside'),[x0,z0,x1,z1]=d.box,cx=(x0+x1)/2,cz=(z0+z1)/2;
 Ride.group.position.set(cx,0,z0+20);Ride.yaw=Math.PI;window.__dcCam=[cx,6,z0+10, cx,4,cz];})()"""
# camHook pins camera AND the NPC riders (8 crew + Ikki NPC) in a fan 8-20 m ahead of the camera, so chars are measured in view (worst case).
HOOK="""window.__npcPassive=true;window.__camHook=()=>{const V=window.__dcCam;if(!V)return;camera.position.set(V[0],V[1],V[2]);camera.lookAt(V[3],V[4],V[5]);
 if(!window.__dcPin)return;const N=[...(RIDERS.npcs||[]),RIDERS.ikkiNpc].filter(n=>n&&n.holder);const dx=V[3]-V[0],dz=V[5]-V[2],l=Math.hypot(dx,dz)||1,fx=dx/l,fz=dz/l;
 N.forEach((n,i)=>{const d=8+(i%3)*6,s=(i-(N.length-1)/2)*2.2;n.holder.visible=true;n.holder.position.set(V[0]+fx*d-fz*s,0,V[2]+fz*d+fx*s);});};"""
CAMS=[("causeway_west_night",BR+"('causeway')",False),("causeway_west_day",BR+"('causeway')",True),
      ("b98_day",BR+"('b98')",True),("portside_day",PORT_JS,True)]

def waitfor(pg,e,t=180):
    t0=time.time()
    while time.time()-t0<t:
        try:
            if pg.evaluate(e): return True
        except Exception: pass
        time.sleep(.3)
    return False
ok=0; tot=0; fails=[]
def check(name,cond,info=""):
    global ok,tot; tot+=1; ok+=bool(cond); print(("PASS " if cond else "FAIL ")+name+(" "+info if info else ""),flush=True)
    if not cond: fails.append(name)
out={"url":URL,"time":time.strftime("%Y-%m-%d %H:%M:%S %Z"),"frames":A.frames,"budget":BUD,"cameras":{}}
with sync_playwright() as p:
    b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    pg=b.new_page(viewport={"width":1280,"height":720}); pg.set_default_timeout(150000); errs=[]
    pg.on("pageerror",lambda e: errs.append("PAGEERROR "+str(e)))
    pg.goto(URL,timeout=120000)
    check("loaded (RIDERS.ready)",waitfor(pg,"typeof RIDERS!='undefined'&&RIDERS.ready"))
    waitfor(pg,"window.GRAF&&GRAF.ready&&GRIND.world",60); waitfor(pg,"!!window.__merge",30); time.sleep(3)
    pg.keyboard.press("Enter"); time.sleep(1.5)
    pg.evaluate("try{garages.forEach(g=>g.gate&&(g.gate.dismissed=true));if(typeof GATE!='undefined'){GATE.uiOpen=false;gateUI()}}catch(e){}")
    pg.add_script_tag(path=METER); check("DC_METER injected",pg.evaluate("!!window.DC_METER"))
    check("post-FX off (?nofx: no composer)",pg.evaluate("!(typeof FX!=='undefined'&&FX.on)"))
    check("not in XR",pg.evaluate("!renderer.xr.isPresenting"))
    pg.evaluate(HOOK); npc=pg.evaluate("[(RIDERS.npcs||[]).length,!!RIDERS.ikkiNpc]"); out["npcs"]=npc
    pg.evaluate("window.__dcPin=true"); check("8 NPC crew riders loaded",npc[0]>=8,f"npcs={npc[0]} ikkiNpc={npc[1]}")
    out["tier"]=pg.evaluate("(typeof WORLD_PERF!=='undefined'&&WORLD_PERF.tier)||new URLSearchParams(location.search).get('tier')||null")
    out["world_perf"]=pg.evaluate("typeof WORLD_PERF!=='undefined'?(WORLD_PERF.stats||true):null")
    day=False
    for name,js,want_day in CAMS:
        if want_day and not day: pg.evaluate(DAY); day=True
        pg.evaluate(js); time.sleep(2)
        S=[pg.evaluate(f"DC_METER.sample('{name}')") for _ in range(A.frames)]
        for s in S: s["charsfx"]=s["chars"]+s["fx"]
        mx={k:max(s[k] for s in S) for k in ("calls","world","chars","fx","charsfx","triangles","est")}
        md={k:statistics.median(s[k] for s in S) for k in ("calls","world","chars","fx","charsfx","triangles")}
        peak=max(S,key=lambda s:s["calls"]); out["cameras"][name]={"max":mx,"median":md,"cam":pg.evaluate("camera.position.toArray()"),
            "geometries":peak["geometries"],"textures":peak["textures"],"byModule":peak["byModule"][:60]}
    b.close()
print(f"\n{'camera':22s} {'calls':>6s} {'med':>6s} {'world':>6s} {'chars':>6s} {'fx':>4s} {'c+fx':>5s} {'tris':>9s} {'est':>5s}")
for n,c in out["cameras"].items():
    m,d=c["max"],c["median"]; print(f"{n:22s} {m['calls']:6d} {d['calls']:6.0f} {m['world']:6d} {m['chars']:6d} {m['fx']:4d} {m['charsfx']:5d} {m['triangles']:9d} {m['est']:5d}")
for n,c in out["cameras"].items():
    m=c["max"]; f0=len(fails)
    check(f"{n}: total<={BUD['total']}",m["calls"]<=BUD["total"],f"max={m['calls']}")
    check(f"{n}: world<={BUD['world']}",m["world"]<=BUD["world"],f"max={m['world']}")
    check(f"{n}: chars+fx<={BUD['charsfx']}",m["charsfx"]<=BUD["charsfx"],f"max={m['charsfx']}")
    if len(fails)>f0:
        print(f"  top-10 modules @ {n}:"); [print(f"    {r['draws']:4d}  {r['module']}") for r in c["byModule"][:10]]
check("no page errors",not errs,"; ".join(errs[:5]))
out["errors"]=errs[:20]; out["summary"]=f"{ok}/{tot} passed"
os.makedirs(RES,exist_ok=True); path=os.path.join(RES,time.strftime("%Y%m%d-%H%M%S")+".json")
for pth in filter(None,[path,A.json_out]): json.dump(out,open(pth,"w"),indent=1)
print(f"results -> {path}"+(f" , {A.json_out}" if A.json_out else ""))
print(f"{ok}/{tot} passed"); sys.exit(0 if ok==tot else 1)
