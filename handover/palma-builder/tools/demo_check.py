# usage: python3 demo_check.py <url> -> shots/demo_check_<scene>_<day|night>.png + json (calls, errors, sky state)
import sys,time,json
from playwright.sync_api import sync_playwright
B=sys.argv[1]; D="/workspace/v3build/shots/demo_check_"+(sys.argv[2]+"_" if len(sys.argv)>2 else "")
def waitfor(pg,e,t=180):
    t0=time.time()
    while time.time()-t0<t:
        try:
            if pg.evaluate(e): return True
        except Exception: pass
        time.sleep(.3)
CALLS="""new Promise(res=>{renderer.info.autoReset=false;let n=0,mx=0;renderer.info.reset();function f(){mx=Math.max(mx,renderer.info.render.calls);renderer.info.reset();if(++n<8)requestAnimationFrame(f);else{renderer.info.autoReset=true;res(mx);}}requestAnimationFrame(f);})"""
DAY="""(()=>{scene.traverse(o=>{if(o.isHemisphereLight){o.intensity=.85;o.color.set(0xcfe0ff);o.groundColor.set(0x6a6470);}});
scene.fog.color.set(0xb8c8e0);_fogBase.set(0xb8c8e0);scene.background.set(0x9ab8e0);if(typeof FACADE!=='undefined')FACADE.setDay(1);if(typeof BRIDGES!=='undefined')BRIDGES.setDay(1);})()"""
BR="""((id,v)=>{GRIND.on=null;const b=PALMA.bridges.find(q=>q.id===id),mx=(b.a[0]+b.b[0])/2,mz=(b.a[1]+b.b[1])/2,L=Math.hypot(b.b[0]-b.a[0],b.b[1]-b.a[1]),
 ux=(b.b[0]-b.a[0])/L,uz=(b.b[1]-b.a[1])/L,px=uz,pz=-ux; Ride.group.position.set(b.a[0]-ux*30,0,b.a[1]-uz*30);
 const V=[mx-px*L*.6+ux*L*.2,9,mz-pz*L*.6+uz*L*.2, mx,6,mz]; window.__camHook=()=>{camera.position.set(V[0],V[1],V[2]);camera.lookAt(V[3],V[4],V[5]);};})"""
SC={"street":"GRIND.on=null;Ride.group.position.set(-60,0,-30);Ride.yaw=Math.PI;window.__camHook=()=>{camera.position.set(-59.2,1.7,-17);camera.lookAt(-60,6,-44);}",
 "bridge_causeway":BR+"('causeway')","bridge_shore":BR+"('shore')","bridge_b98":BR+"('b98')",
 "grind_bridge":"""(()=>{const s=GRIND.S.filter(s=>s.kind==='stay'&&s.pts.every(p=>onLand(p.x,p.z)))[0]||GRIND.S.find(s=>s.kind==='main');WALL.air=WALL.on=null;
  const q=grindAt(s,s.L*.4,new THREE.Vector3());Ride.group.position.copy(q);grindLock(s,s.L*.4,-1,6,1);GRIND.on.grip=0;
  window.__camHook=()=>{const p=Ride.group.position,y=Ride.yaw;camera.position.set(p.x-Math.sin(y)*6+Math.cos(y)*3,p.y+2.2,p.z-Math.cos(y)*6-Math.sin(y)*3);camera.lookAt(p.x,p.y+.6,p.z);};})()""",
 "graffiti":"""(()=>{GRIND.on=null;const inC=(x,z)=>colliders.some(c=>!c.off&&x>c.minX-.3&&x<c.maxX+.3&&z>c.minZ-.3&&z<c.maxZ+.3);
  let best=null; for(const s of GRAF.spots){ if(s.ground||s.heaven||s.size==='S') continue; for(const sg of [1,-1]){ let ok=true; for(let d=1.5;d<=7;d+=.5) if(inC(s.x+s.nx*sg*d,s.z+s.nz*sg*d)){ok=false;break;} if(ok){best=[s,sg];break;} } if(best) break; }
  const [s,sg]=best||[GRAF.spots[0],1]; window.__grafPick=[s.id,sg]; Ride.group.position.set(s.x+s.nx*sg*5,0,s.z+s.nz*sg*5);
  window.__camHook=()=>{camera.position.set(s.x+s.nx*sg*7,Math.max(1.6,s.y+.6),s.z+s.nz*sg*7);camera.lookAt(s.x,s.y,s.z);};})()"""}
out={}
with sync_playwright() as p:
    br=p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"]); pg=br.new_page(viewport={"width":1280,"height":720})
    errs=[]; pg.on("pageerror",lambda e: errs.append(str(e))); pg.on("console",lambda m: errs.append(m.text[:160]) if m.type=="error" else None); pg.on("response",lambda r: errs.append(f"HTTP {r.status} {r.url[-90:]}") if r.status>=400 else None)
    pg.goto(B,timeout=180000); waitfor(pg,"typeof RIDERS!='undefined'&&RIDERS.ready"); waitfor(pg,"window.GRAF&&GRAF.ready&&GRIND.world",60); time.sleep(3)
    pg.keyboard.press("Enter"); time.sleep(1.5)
    pg.evaluate("garages.forEach(g=>g.gate&&(g.gate.dismissed=true));if(typeof GATE!='undefined'){GATE.uiOpen=false;gateUI()};window.__npcPassive=true;window.__npcFreeze=true")
    for mode in ["night","day"]:
        if mode=="day": pg.evaluate(DAY)
        for k,js in SC.items():
            try:
                pg.evaluate(js); time.sleep(2); pg.screenshot(path=D+f"{k}_{mode}.png"); out[f"{k}_{mode}"]=pg.evaluate(CALLS)
            except Exception as e: out[f"{k}_{mode}"]="ERR "+str(e)[:200]
        out["sky_"+mode]=pg.evaluate("typeof SKY!='undefined'?SKY.day:'no SKY'")
    out["graf_pick"]=pg.evaluate("window.__grafPick||null"); out["errors"]=errs[:20]; br.close()
print(json.dumps(out))
