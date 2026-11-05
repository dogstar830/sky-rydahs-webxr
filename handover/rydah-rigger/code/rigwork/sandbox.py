import sys,json,time,base64
from playwright.sync_api import sync_playwright
PORT=open('/tmp/rig_port').read().strip(); url=sys.argv[1]; tag=sys.argv[2]; mode=sys.argv[3] if len(sys.argv)>3 else 'full'
H=float(sys.argv[4]) if len(sys.argv)>4 else 1.916
STATES=['idle','kick','crouch','grind','polegrind_top','polegrind_climb']
def snap(pg,path):
  d=pg.evaluate("renderer.domElement.toDataURL('image/png')"); open(path,'wb').write(base64.b64decode(d.split(',')[1]))
with sync_playwright() as p:
  b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"]); pg=b.new_page(viewport={"width":720,"height":900}); pg.set_default_timeout(300000)
  errs=[]; pg.on("pageerror",lambda e: errs.append(str(e))); cons=[]; pg.on("console",lambda m: cons.append(m.type+': '+m.text) if m.type in ('error','warning') else None)
  pg.goto(f"http://127.0.0.1:{PORT}/rig-20261030/index.html"); pg.wait_for_function("window.__ready===true")
  res={'url':url,'load':pg.evaluate(f"__load('{url}',{1.916})")}
  if mode=='full':
    res['poses']={}
    for st in STATES:
      name=pg.evaluate(f"__pose('{st}',1.5)"); m=pg.evaluate("__metrics()"); res['poses'][st]={'state':name,**m}
      for v in ['front','34']: pg.evaluate(f"__cam('{v}')"); snap(pg,f'/workspace/rigwork/shots2/{tag}_{st}_{v}.png')
    pg.evaluate("__pose('idle',1.0)"); res['forearm_idle']=pg.evaluate("__forearm()")
    for deg in [90,-90]:
      pg.evaluate("__pose('idle',1.0)"); pg.evaluate(f"__roll({deg})"); res[f'roll{deg}']={'metrics':pg.evaluate("__metrics()"),'forearm':pg.evaluate("__forearm()")}
      pg.evaluate("__cam('front')"); snap(pg,f'/workspace/rigwork/shots2/{tag}_roll{deg}_front.png')
  else:
    name=pg.evaluate("__pose('idle',1.0)"); res['idle']=pg.evaluate("__metrics()")
  res['errors']=errs; res['console']=cons[:20]
  print(json.dumps(res)); b.close()
