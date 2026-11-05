# per-frame diag of attacks.py 'real steering' case (Rydah Systems). Reuses attacks.py HELP/NOPAD/load setup.
import re,time,json,os,sys
from playwright.sync_api import sync_playwright
src=open('/workspace/v3build/tests/attacks.py').read()
HELP=re.search(r'HELP="""(.*?)"""',src,re.S).group(1); NOPAD=re.search(r'NOPAD="(.*?)"\n',src).group(1)
B="http://localhost:8765/v3build/"+os.environ.get("RYDAH_PAGE","attacks_diag.html")+"?chars=/skyrydahs-characters/"
LOG="""window.__L=[];(function L(){ const p=Ride.group.position,q=__T.holder.position,v=new THREE.Vector3();camera.getWorldDirection(v);
 __L.push({f:frame,c:+clock.toFixed(2),mode:State.mode,mag:+(Input.mag||0).toFixed(2),iy:+(Input.yaw||0).toFixed(2),cr:PAD.camRel?{ref:PAD.camRel.ref==null?null:+PAD.camRel.ref.toFixed(2),raw:+(+PAD.camRel.raw).toFixed(2),on:PAD.camRel.on}:null,
  ws:!!window.__worldStick,ry:+Ride.yaw.toFixed(2),sp:+Ride.speed.toFixed(2),cy:+Math.atan2(v.x,v.z).toFixed(2),d:+Math.hypot(q.x-p.x,q.z-p.z).toFixed(2),
  act:ATK.act?ATK.act.m.name||ATK.act.m.kind:null,cd:ATK.cd.map(x=>+x.toFixed(2)),stun:+(ATK.stun||0).toFixed(2),air:!!WALL.air,on:!!WALL.on,grind:!!(window.GRIND&&GRIND.on),kW:!!(window._k&&_k.KeyW),gate:typeof GATE!=='undefined'&&GATE.uiOpen,phone:!!(window.PHONE&&PHONE.up),tgt:typeof TGT!=='undefined'?!!TGT.aiming:null});
 if(__L.length<400&&!window.__Lstop) requestAnimationFrame(L)})()"""
with sync_playwright() as p:
    b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    pg=b.new_page(viewport={"width":1280,"height":720}); pg.set_default_timeout(150000); ev=pg.evaluate
    pg.goto(B,timeout=120000)
    for i in range(150):
        if ev("typeof RIDERS!='undefined'&&RIDERS.ready&&TURF.ready&&RIDERS.npcs.length>0"): break
        time.sleep(1)
    time.sleep(3); pg.keyboard.press("Enter"); time.sleep(1.5); ev(HELP); ev("window.__npcPassive=true;window.__hideIkkiNpc=true")
    print("mode after attacks.py load():",ev("State.mode"),flush=True)
    t0=time.time()
    while ev("State.mode")!="ride" and time.time()-t0<30: time.sleep(.3)
    print("mode now:",ev("State.mode"),flush=True)
    ev("window.__worldStick=false")
    ev("ATK.set='anubis';ATK.cd=[0,0,0];ATK.act=null;window.__T=__npc('static');__T.mode=__T.mode0??__T.mode;__near(__T)"); time.sleep(1)
    ev("""(()=>{const q=__T.holder.position,g=__T.g,ox=Math.sin(g.th+1.2),oz=Math.cos(g.th+1.2);Ride.group.position.set(q.x+ox*7,0,q.z+oz*7);Ride.y=0;Ride.speed=0;WALL.on=WALL.air=null;
          Ride.yaw=Math.atan2(-oz,ox); __T.stun=0;__T.kv=null;if(__T.off)__T.off.set(0,0,0);
          window.__camHook=()=>{const p=Ride.group.position,q=__T.holder.position,dx=q.x-p.x,dz=q.z-p.z,l=Math.hypot(dx,dz)||1;camera.position.set(p.x-dx/l*5,p.y+2.4,p.z-dz/l*5);camera.lookAt(q.x,1,q.z);};})()""")
    ev(NOPAD); ev(LOG); pg.keyboard.down("KeyW")
    c0=ev("clock"); t0=time.time()
    while time.time()-t0<150 and ev("clock")<c0+6:
        if ev("Math.hypot(__T.holder.position.x-Ride.group.position.x,__T.holder.position.z-Ride.group.position.z)<2.2"): break
        time.sleep(.1)
    pg.keyboard.up("KeyW"); pg.keyboard.press("KeyJ"); time.sleep(4); ev("window.__Lstop=true")
    L=ev("__L"); json.dump(L,open("/tmp/rg_root/atk_steer_diag.json","w"))
    for e in L[:6]+L[6:-1:max(1,len(L)//25)]+L[-4:]: print(json.dumps(e),flush=True)
    b.close()
