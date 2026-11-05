import sys,base64,json
from playwright.sync_api import sync_playwright
PORT=open('/tmp/rig_port').read().strip()
with sync_playwright() as p:
  b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"]); pg=b.new_page(viewport={"width":720,"height":900})
  pg.goto(f"http://127.0.0.1:{PORT}/rig-20261030/index.html"); pg.wait_for_function("window.__ready===true")
  for url,tag in [('out/anika-rider.glb','anika_rider'),('out/caali-g-v2.glb','caali_v2')]:
    pg.evaluate(f"__load('{url}')"); pg.evaluate("__pose('idle',1.0)")
    pg.evaluate("window.__camD=1.6; (()=>{ camera.position.set(0,1.45,-1.6); camera.lookAt(0,1.3,0); renderer.render(scene,camera); })()")
    d=pg.evaluate("renderer.domElement.toDataURL('image/png')"); open(f'shots/{tag}_back_close.png','wb').write(base64.b64decode(d.split(',')[1]))
    pg.evaluate("(()=>{ camera.position.set(0,1.45,1.6); camera.lookAt(0,1.3,0); renderer.render(scene,camera); })()")
    d=pg.evaluate("renderer.domElement.toDataURL('image/png')"); open(f'shots/{tag}_chest_close.png','wb').write(base64.b64decode(d.split(',')[1]))
    pg.evaluate("window.__camD=undefined; __clear()")
  b.close()
