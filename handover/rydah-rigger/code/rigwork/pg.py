import json
from playwright.sync_api import sync_playwright
P=open('/tmp/rig_port').read().strip()
with sync_playwright() as p:
  b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"]); pg=b.new_page(); errs=[]; pg.on("pageerror",lambda e:errs.append(str(e)))
  pg.goto(f"http://127.0.0.1:{P}/rig-20261030/index.html"); pg.wait_for_function("window.__ready===true")
  for u in ['out/caali-g-v2.glb','out/anika-rider.glb']:
    pg.evaluate(f"__load('{u}')"); out={}
    for st in ['grind','polegrind_top','polegrind_climb']:
      out[st]=pg.evaluate(f"(()=>{{ const s=__pose('{st}',1.5); const w=R.userData.weights; const d=R.userData.poseDbg; return {{state:s,w:w['{st}'],LeftUpLeg:d.LeftUpLeg.map(v=>+v.toFixed(1)),LeftArm:d.LeftArm.map(v=>+v.toFixed(1))}}; }})()")
    print(u,json.dumps(out)); pg.evaluate("__clear()")
  print('errors',errs); b.close()
