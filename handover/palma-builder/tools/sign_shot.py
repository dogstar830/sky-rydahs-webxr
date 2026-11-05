# legibility shots: same sign at 8 m (swap-in) and 30 m (atlas) for default vs ?oldsigns=1. Scratch only.
import sys,time
from playwright.sync_api import sync_playwright
H=sys.argv[1]
JS='''(async(D)=>{ const S=WORLD_PERF.SIGN; window.__hold=true;
 let it=S.list.find(i=>!i.dead&&i.t.image.width===1024&&i.t.image.height===256); if(!it) it=S.list[0];
 const o=it.o; o.updateMatrixWorld(true); const n=new THREE.Vector3(0,0,1).transformDirection(o.matrixWorld); o.geometry.computeBoundingSphere(); const c=o.geometry.boundingSphere.center.clone().applyMatrix4(o.matrixWorld); const hidd=camera.children.filter(q=>q.visible); hidd.forEach(q=>q.visible=false);
 if(!window.__orig){ window.__orig=1; const r0=renderer.render.bind(renderer); renderer.render=(s,cm)=>{ if(window.__pose){ camera.position.copy(window.__pose[0]); camera.lookAt(window.__pose[1]); camera.updateMatrixWorld(true);} r0(s,cm); }; }
 const rc=new THREE.Raycaster(c.clone().addScaledVector(n,.2),n,0,D); rc.camera=camera; const M2=[]; scene.traverse(q=>{ if(q.isMesh&&q.visible&&q!==o) M2.push(q); }); const blk=rc.intersectObjects(M2,false).filter(h=>h.object.visible).length; if(blk) n.negate();
 document.querySelectorAll('body > *:not(canvas)').forEach(e=>{ if(!e.querySelector||!e.querySelector('canvas')) e.style.display='none'; });
 window.__pose=[c.clone().addScaledVector(n,D).add(new THREE.Vector3(0,.3,0)),c]; camera.fov=50; camera.updateProjectionMatrix();
 const cam2=new THREE.PerspectiveCamera(50,16/9,.1,2000); cam2.position.copy(window.__pose[0]); cam2.lookAt(c); cam2.updateMatrixWorld(true);
 camera.position.copy(cam2.position); camera.updateMatrixWorld(true); for(let k=0;k<3;k++) WORLD_PERF.tick(); await new Promise(r=>requestAnimationFrame(r)); for(let k=0;k<3;k++){ camera.position.copy(cam2.position); camera.updateMatrixWorld(true); WORLD_PERF.tick(); }
 const rc2=new THREE.Raycaster(); rc2.camera=cam2; const hide=[]; for(const [px,py] of [[0,0],[-.3,.2],[.3,-.2],[0,.3],[-.3,-.3]]){ rc2.setFromCamera({x:px,y:py},cam2); const M3=[]; scene.traverse(q=>{ if((q.isMesh||q.isSprite)&&q.visible) M3.push(q); }); for(const h of rc2.intersectObjects(M3,false)){ if(h.distance<D-1.5&&h.object!==o&&!h.object.userData.worldPerf){ let r=h.object; while(r.parent&&r.parent!==scene) r=r.parent; if(!hide.includes(r)&&r!==scene){ hide.push(r); r.visible=false; } } } }
 renderer.render(scene,cam2); hide.forEach(q=>q.visible=true); window.__shot=renderer.domElement.toDataURL('image/png'); hidd.forEach(q=>q.visible=true);
 return {D,c:c.toArray().map(Math.round),hid:hidd.length,src:it.src?[it.src.width,it.src.height]:null,near:it.near,orig:[it.t.image.width,it.t.image.height]}; })'''
with sync_playwright() as p:
    br=p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
    for tag,q in (("new",""),("old","&oldsigns=1")):
        pg=br.new_page(viewport={"width":960,"height":540}); pg.goto(f"http://localhost:8765/v3build/{H}?chars=/skyrydahs-characters/&nofx&seed=1{q}",timeout=180000)
        t0=time.time()
        while time.time()-t0<200:
            try:
                if pg.evaluate("window.GRAF&&GRAF.ready&&GRIND.world"): break
            except Exception: pass
            time.sleep(.5)
        time.sleep(2)
        for D in (8,30):
            print(tag,pg.evaluate(JS+f"({D})")); import base64; open(f'shots/signs_{tag}_{D}m.png','wb').write(base64.b64decode(pg.evaluate('window.__shot').split(',')[1]))
        pg.close()
    br.close()
