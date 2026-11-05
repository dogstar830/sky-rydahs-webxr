# ?perf=1 overlay test (perf_overlay.js + Rydah Optimizer's dc_meter.js via patch_graffiti.py).
# ?perf=1: panel shows frame ms/avg/p95, scene-only draws (post excluded), tris, textures/MB, DC_METER split; desktop panel adds 0 draws.
# no ?perf: no panel, no hook, perfTick absent, draws unchanged.  Usage: python3 tests/perf_overlay.py [base_url] [page]
from playwright.sync_api import sync_playwright
import sys, time
BASE=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8765"; PAGE=sys.argv[2] if len(sys.argv)>2 else "v3build/sky-rydahs-v3-ikki.html"
res=[]
def check(n,c,i=""): res.append((n,bool(c))); print(("PASS " if c else "FAIL ")+n,i,flush=True)
DC="(()=>{const a=renderer.info.autoReset;renderer.info.autoReset=false;renderer.info.reset();renderer.render(scene,camera);const c=renderer.info.render.calls;renderer.info.autoReset=a;return c})()"
with sync_playwright() as p:
    b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
    for q in ["perf=1","none"]:
        pg=b.new_page(viewport={"width":1280,"height":720}); errs=[]; pg.on("pageerror",lambda e: errs.append(str(e)))
        pg.goto(f"{BASE}/{PAGE}?chars=/skyrydahs-characters/"+("&"+q if q!="none" else ""),timeout=300000); ev=pg.evaluate
        for i in range(150):
            if ev("typeof RIDERS!='undefined'&&RIDERS.ready"): break
            time.sleep(1)
        pg.keyboard.press("Enter"); time.sleep(1.5)
        st=ev("clock")
        while ev("clock")<st+2.5: time.sleep(.2)
        if q=="perf=1":
            txt=ev("(document.getElementById('perfOverlay')||{}).textContent||''"); print(txt,flush=True)
            check("perf=1: panel visible", ev("!!document.getElementById('perfOverlay')&&document.getElementById('perfOverlay').style.display!=='none'"))
            check("perf=1: frame ms + avg + p95", "ms" in txt and "avg" in txt and "p95" in txt)
            check("perf=1: draws labelled post-FX excluded", "post-FX excluded" in txt and ev("PERF.stat&&PERF.stat.calls>0"), ev("PERF.stat&&PERF.stat.calls"))
            check("perf=1: tris + textures + MB", "tris" in txt and "textures" in txt and "MB" in txt)
            check("perf=1: reuses DC_METER split", "DC_METER world" in txt and ev("!!window.DC_METER"))
            # texture memory (audit fixes): hidden never-uploaded canvas not counted; ShaderMaterial uniform texture counted; cross-check audit snippet
            m0=ev("PERF.texMem()")
            ev("""(()=>{const c=document.createElement('canvas');c.width=c.height=1024;const t=new THREE.CanvasTexture(c);const m=new THREE.Mesh(new THREE.PlaneGeometry(1,1),new THREE.MeshBasicMaterial({map:t}));m.visible=false;m.name='__hiddenTex';scene.add(m);})()""")
            m1=ev("PERF.texMem()")
            check("tex: hidden un-uploaded canvas not counted", abs(m1["mb"]-m0["mb"])<1e-6 and m1["skipped"]==m0["skipped"]+1, f"{m0} -> {m1}")
            ev("""(()=>{const c=document.createElement('canvas');c.width=c.height=512;const t=new THREE.CanvasTexture(c);t.minFilter=THREE.LinearFilter;t.generateMipmaps=false;
              const m=new THREE.Mesh(new THREE.PlaneGeometry(1,1),new THREE.ShaderMaterial({uniforms:{uTex:{value:t}},vertexShader:'void main(){gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',fragmentShader:'uniform sampler2D uTex;void main(){gl_FragColor=texture2D(uTex,vec2(.5));}'}));
              m.frustumCulled=false;m.position.copy(camera.position).add(new THREE.Vector3(0,0,-2).applyQuaternion(camera.quaternion));m.name='__uniTex';scene.add(m);renderer.render(scene,camera);})()""")
            m2=ev("PERF.texMem()"); exp=512*512*4/1048576
            check("tex: ShaderMaterial uniform texture counted (512² RGBA8, no mips = 1.0 MB)", abs((m2["mb"]-m1["mb"])-exp)<.01, f"+{m2['mb']-m1['mb']:.3f} MB")
            ev("['__hiddenTex','__uniTex'].forEach(n=>{const o=scene.getObjectByName(n);if(o)scene.remove(o)})")
            snip=ev("""(()=>{const T=THREE,B={[T.RGB_ETC1_Format]:.5,[T.RGB_ETC2_Format]:.5,[T.RGBA_ETC2_EAC_Format]:1,[T.RGBA_ASTC_4x4_Format]:1,[T.RGB_S3TC_DXT1_Format]:.5,[T.RGBA_S3TC_DXT1_Format]:.5,[T.RGBA_S3TC_DXT3_Format]:1,[T.RGBA_S3TC_DXT5_Format]:1,[T.RGBA_BPTC_Format]:1,[T.RGB_PVRTC_4BPPV1_Format]:.5,[T.RGBA_PVRTC_4BPPV1_Format]:.5};const MM=[T.NearestMipmapNearestFilter,T.NearestMipmapLinearFilter,T.LinearMipmapNearestFilter,T.LinearMipmapLinearFilter];const s=new Set(),L=[];scene.traverse(o=>{[].concat(o.material||[]).forEach(m=>{const vs=[...Object.values(m),...Object.values(m.uniforms||{}).map(u=>u&&u.value)];vs.forEach(t=>{if(t&&t.isTexture&&!s.has(t)){s.add(t);const i=t.image||{},w=i.width||0,h=i.height||0,c=!!t.isCompressedTexture,bpp=c?(B[t.format]??1):4,mip=c?((t.mipmaps||[]).length>1):(t.generateMipmaps&&MM.includes(t.minFilter)),f=mip?1.33:1;L.push([t.name||(i.src||'').slice(-40)||(i.constructor&&i.constructor.name),w,h,c?'c'+t.format:'rgba8',!!renderer.properties.get(t).__webglTexture,(w*h*bpp*f/1048576).toFixed(2)]);}})})});L.sort((a,b)=>b[5]-a[5]);return L.filter(r=>r[4]).reduce((a,r)=>a+ +r[5],0);})()""")  # KTX2-aware bpp per format, mips only when present (audit.md section 1)
            ov=ev("PERF.texMem()")
            print(f"TEXMB overlay {ov['mb']:.1f} MB (uploaded {ov['uploaded']}, skipped {ov['skipped']}, GL {ov['gl']}) vs audit snippet {snip:.1f} MB",flush=True)
            check("tex: overlay MB within 5% of audit snippet", abs(ov["mb"]-snip)<=.05*max(snip,1e-6), f"{ov['mb']:.1f} vs {snip:.1f}")
            check("texshare line hidden when __TEXSHARE absent", "texshare" not in txt or ev("!!window.__TEXSHARE"))
            ev("window.__TEXSHARE={ms:12.5,textures:7,shared:6,savedBytes:3*1048576}"); st2=ev("clock")
            while ev("clock")<st2+.6: time.sleep(.2)
            t2=ev("document.getElementById('perfOverlay').textContent"); check("texshare line shown", "texshare 12.5 ms / 3.0 MB saved" in t2, t2.splitlines()[-1:])
            ev("PERF.mesh.visible=false"); d1=ev(DC); ev("PERF.dom.style.display='none'"); d0=ev(DC)
            check("perf=1 desktop panel adds 0 draws", d1==d0, f"{d0}/{d1}")
            ev("PERF.mesh.visible=true"); dx=ev(DC); ev("PERF.mesh.visible=false")
            check("perf=1 XR panel adds exactly 1 draw", dx-d0==1, f"{d0}->{dx}")
            try: pg.screenshot(path="/workspace/v3build/shots/perf_overlay.png",timeout=120000)
            except Exception as e: print("screenshot skipped",e)
        else:
            check("no ?perf: no panel, no tick, no hook", ev("!document.getElementById('perfOverlay')&&!window.perfTick&&PERF.on===false&&!scene.getObjectByName('perf_overlay_xr')"))
        check(f"[{q}] no page errors", not errs, errs[:3]); pg.close()
    b.close()
n=sum(1 for _,c in res if c); print(f"perf_overlay.py: {n}/{len(res)} passed")
