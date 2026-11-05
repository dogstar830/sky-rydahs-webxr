# XR FX memory test v2 (Rydah Optimizer): composer rt1/rt2 (+depth) GL memory freed on XR sessionstart, restored on sessionend.
# Fake XR = tests/gamepad.py pattern (getCamera identity -> no r128 null-session updateRenderState race; isPresenting true outside
# renderer.render) + dispatching renderer.xr 'sessionstart'/'sessionend'.
# v2 fixes (AD_xrfxmem 6/10 were test bugs): r128 WebGLRenderer listens to its own xr 'sessionstart' -> animation.stop() (real XR then
# drives frames from session.requestAnimationFrame, the stub's is a no-op) => 0 frames. We now drive animate() from window rAF while
# faking. Screenshots/texture counts were taken minutes apart on a moving attract scene; now the loop is paused, the camera pinned and
# the composer rendered by hand for both shots, and bloom is checked as its own contribution (bloom on vs off) before vs after.
# Integrator-only (holds .testlock).
from playwright.sync_api import sync_playwright
import time, argparse, io
_ap=argparse.ArgumentParser(); _ap.add_argument("--port",type=int,default=8765); _ap.add_argument("--bloom",action="store_true",help="also test ?xrfxbloom=1")
A=_ap.parse_args(); PORT=A.port
U=f"http://localhost:{PORT}/v3build/sky-rydahs-v3-ikki.html?chars=/skyrydahs-characters/"+("&xrfxbloom=1" if A.bloom else "")
res=[]
def check(n,c,i=""): res.append((n,bool(c))); print(("PASS " if c else "FAIL ")+n,i,flush=True)
XR_ON="""(()=>{const src={handedness:'right',gamepad:{mapping:'xr-standard',buttons:Array.from({length:7},()=>({pressed:false,value:0})),axes:[0,0,0,0]}};
  window.__ses={inputSources:[src],renderState:{},updateRenderState(){},addEventListener(){},removeEventListener(){},requestAnimationFrame(){return 0},cancelAnimationFrame(){},end(){return Promise.resolve()}};
  window.__xrO={g:renderer.xr.getSession,c:renderer.xr.getCamera,d:Object.getOwnPropertyDescriptor(renderer.xr,'isPresenting')};renderer.xr.getCamera=c=>c;
  renderer.xr.getSession=()=>window.__rendering?null:__ses;window.__rendering=false;const R0=renderer.render.bind(renderer);window.__R0=renderer.render;
  renderer.render=(a,b)=>{__rendering=true;try{R0(a,b);}finally{__rendering=false;}};Object.defineProperty(renderer.xr,'isPresenting',{configurable:true,get:()=>!window.__rendering});
  window.__crc=0;const C=FX.composer,cr=C.render;window.__crO=cr;C.render=function(){ if(!__rendering&&renderer.xr.isPresenting) __crc++; return cr.apply(this,arguments); };
  renderer.xr.dispatchEvent({type:'sessionstart'});   // r128 renderer stops its own loop here (onXRSessionStart)
  window.__xrDrive=true;(function L(t){ if(!__xrDrive) return; try{ animate(t); }catch(e){ console.error('xr frame',e); } requestAnimationFrame(L); })(performance.now());})()"""
XR_OFF="""(()=>{window.__xrDrive=false;renderer.xr.getSession=__xrO.g;renderer.xr.getCamera=__xrO.c;renderer.render=__R0;delete renderer.xr.isPresenting;if(__xrO.d)Object.defineProperty(renderer.xr,'isPresenting',__xrO.d);
  FX.composer.render=__crO;renderer.xr.dispatchEvent({type:'sessionend'});})()"""  # sessionend -> renderer animation.start()
PAUSE="(()=>{renderer.setAnimationLoop(null);})()"
RESUME="(()=>{renderer.setAnimationLoop(animate);})()"
PIN="(()=>{camera.position.fromArray(__cam[0]);camera.quaternion.fromArray(__cam[1]);camera.updateMatrixWorld(true);})()"
with sync_playwright() as p:
    b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    pg=b.new_page(viewport={"width":1280,"height":720}); pg.set_default_timeout(150000); errs=[]
    pg.on("pageerror",lambda e: errs.append(str(e)))
    pg.on("console",lambda m: errs.append("console: "+m.text) if m.type=="error" else None)
    pg.goto(U,timeout=300000)
    for i in range(120):
        if pg.evaluate("typeof RIDERS!='undefined'&&RIDERS.ready&&TURF.ready&&!!(FX.composer&&FX.on)"): break
        time.sleep(1)
    time.sleep(3)
    ev=pg.evaluate
    def wf(n=3,tmo=180):
        st=ev("frame"); t0=time.time()
        while ev("frame")<st+n and time.time()-t0<tmo: time.sleep(.03)
        return ev("frame")-st
    def shots():  # paused loop, pinned camera, composer by hand: full and with bloom disabled
        ev(PIN); ev("FX.composer.render(0)"); time.sleep(.3); full=pg.screenshot()
        ev("FX.bloom.enabled=false"); ev(PIN); ev("FX.composer.render(0)"); time.sleep(.3); nob=pg.screenshot()
        ev("FX.bloom.enabled=true"); ev(PIN); ev("FX.composer.render(0)"); return full,nob
    check("composer + bloom up, __XRFXMEM hooked", ev("!!(FX.composer&&FX.bloom&&window.__XRFXMEM&&__XRFXMEM.hooked&&!__XRFXMEM.off)"), ev("JSON.stringify(window.__XRFXMEM||null)"))
    ev("window.__noFX=false"); wf(10)
    ev(PAUSE); ev("window.__cam=[camera.position.toArray(),camera.quaternion.toArray()]")
    A0,A1=shots(); tex0=ev("renderer.info.memory.textures"); print("textures before XR", tex0); ev(RESUME); wf(3)
    e0=len(errs); ev(XR_ON); time.sleep(.5)
    tex1=ev("renderer.info.memory.textures"); M=ev("JSON.stringify(__XRFXMEM)"); need=10 if A.bloom else 4
    check(f"XR sessionstart: textures drop >= {need} (rt1+rt2+2 depth{' + 11 bloom' if A.bloom else ''})", tex0-tex1>=need, f"{tex0}->{tex1} {M}")
    check("__XRFXMEM.disposed > 0 and freed flag set", ev("__XRFXMEM.disposed>0&&__XRFXMEM.freed"), M)
    print("bytesFreedEst MB", ev("(__XRFXMEM.bytesFreedEst/1048576).toFixed(1)"))
    n=wf(60); tex2=ev("renderer.info.memory.textures")
    check("60 XR frames, no composer.render while presenting, targets stay freed", n>=60 and ev("__crc")==0 and tex2<=tex1+2, f"frames={n} crc={ev('__crc')} tex={tex1}->{tex2}")
    check("no errors during XR frames", len(errs)==e0, errs[e0:e0+5])
    ev(XR_OFF); n=wf(60)
    check("sessionend: loop resumes, 60 desktop frames, no errors", n>=60 and len(errs)==e0, f"frames={n} {errs[e0:e0+5]}")
    ev(PAUSE); B0,B1=shots(); tex3=ev("renderer.info.memory.textures"); ev(RESUME)
    check("sessionend: restored + texture count back (+-2)", ev("__XRFXMEM.restored>=1&&!__XRFXMEM.freed") and abs(tex3-tex0)<=2, f"{tex0}->{tex3} {ev('JSON.stringify(__XRFXMEM)')}")
    try:
        from PIL import Image, ImageChops, ImageStat
        im=lambda s: Image.open(io.BytesIO(s)).convert("RGB")
        md=lambda x,y: sum(ImageStat.Stat(ImageChops.difference(x,y)).mean)/3
        a0,a1,b0,b1=map(im,(A0,A1,B0,B1))
        for nm,x in (("before",a0),("before_nobloom",a1),("after",b0),("after_nobloom",b1)): x.save(f"/tmp/xr_fxmem_{nm}.png")
        d=md(a0,b0); bl0=md(a0,a1); bl1=md(b0,b1)
        check("desktop shot after restore == before XR (paused, pinned cam; mean diff < 3/255)", d<3, f"meandiff={d:.2f}")
        check("bloom intact: bloom contribution after ~= before (within 25%)", bl0>0.2 and abs(bl1-bl0)/bl0<.25, f"bloom delta {bl0:.2f}->{bl1:.2f}")
    except ImportError: check("PIL available for pixel diff", False)
    check("no page/console errors", not errs, errs[:5])
    print(f"\n{sum(c for _,c in res)}/{len(res)} passed"); b.close()
