import time, os, json
from playwright.sync_api import sync_playwright
OUT='/workspace/v3build/shots/hero'
os.makedirs(OUT, exist_ok=True)
B='http://localhost:8765/v3build/palma_garages.html?chars=/skyrydahs-characters/&tier=hd&seed=1'
DAY="(()=>{ if(typeof FACADE!=='undefined')FACADE.setDay(1); if(typeof BRIDGES!=='undefined')BRIDGES.setDay(1); try{SKY.setDay(1)}catch(e){} })()"
NIGHT="(()=>{ if(typeof FACADE!=='undefined')FACADE.setDay(0); if(typeof BRIDGES!=='undefined')BRIDGES.setDay(0); try{SKY.setDay(0)}catch(e){} })()"
HOOK=r'''(()=>{ if(window.__pinHook) return; window.__pinHook=1; const R=renderer,oR=R.render.bind(R);
 const M=new THREE.Matrix4(),P=new THREE.Vector3(),T=new THREE.Vector3(),Sc=new THREE.Vector3(),UP=new THREE.Vector3(0,1,0);
 R.render=function(s,c){ if(s===scene&&window.__pin){ const v=window.__pin;
   if(v.crew){ const G=garages.find(g=>g.crew===v.crew); if(G){ const th=G.th,[gx,gz]=G.pos; const W=(lx,lz)=>[gx+lx*Math.cos(th)+lz*Math.sin(th), gz-lx*Math.sin(th)+lz*Math.cos(th)];
     const rp=W(v.rlx||0,v.rlz||6); Ride.group.position.set(rp[0],v.ry||0,rp[1]); if('speed' in Ride) Ride.speed=0;
     const cp=W(v.clx,v.clz), at=W(v.tlx,v.tlz); P.set(cp[0],v.cy,cp[1]); T.set(at[0],v.ty,at[1]);
   }} else { Ride.group.position.set(v.rx,0,v.rz); if('speed' in Ride) Ride.speed=0; P.set(v.cx,v.cy,v.cz); T.set(v.tx,v.ty,v.tz); }
   M.lookAt(P,T,UP); M.setPosition(P);
   if(c.parent){ c.parent.updateMatrixWorld(true); M.premultiply(new THREE.Matrix4().copy(c.parent.matrixWorld).invert()); }
   M.decompose(c.position,c.quaternion,Sc); c.updateMatrixWorld(true); }
  return oR(s,c); }; })()'''
# local garage coords: +z street. Exterior: look from street at bay. Interior: downstairs kit force.
shots=[
  dict(name='garage_volt_exterior_day', crew='volt', day=1, clx=0, clz=10, cy=2.3, tlx=0, tlz=-1, ty=2.0, rlx=0, rlz=8),
  dict(name='garage_volt_exterior_night', crew='volt', day=0, clx=0, clz=10, cy=2.3, tlx=0, tlz=-1, ty=2.0, rlx=0, rlz=8),
  dict(name='garage_volt_lot_after', crew='volt', day=1, clx=0, clz=18, cy=9, tlx=0, tlz=-4, ty=2, rlx=0, rlz=14),
  dict(name='garage_rustclaw_exterior_day', crew='rustclaw', day=1, clx=0, clz=12, cy=5.5, tlx=0, tlz=-2, ty=2.5, rlx=0, rlz=10),
  dict(name='garage_rustclaw_exterior_night', crew='rustclaw', day=0, clx=0, clz=12, cy=5.5, tlx=0, tlz=-2, ty=2.5, rlx=0, rlz=10),
  dict(name='garage_rustclaw_lot_after', crew='rustclaw', day=1, clx=0, clz=18, cy=9, tlx=0, tlz=-4, ty=2, rlx=0, rlz=14),
]
# emblem regression (volt/rustclaw filled; karasu still procedural) — run after first exterior day pins
EMBLEM_CHECK=r"""(() => {
  const out={};
  for(const crew of ['volt','rustclaw','karasu']){
    const G=garages.find(g=>g.crew===crew); if(!G){ out[crew]={ok:false,why:'noG'}; continue; }
    let found=null;
    G.group.traverse(o=>{ if(found||!o.isMesh||!o.material||!o.material.map) return;
      if(!(o.geometry&&o.geometry.type==='PlaneGeometry')) return;
      if(Math.abs(o.position.y-10)>0.2) return;
      const img=o.material.map.image; if(!img||!img.getContext) { found={ok:false,why:'noCanvas'}; return; }
      const x=img.getContext('2d'), d=x.getImageData(200,200,112,112).data; let bright=0,n=d.length/4;
      for(let i=0;i<d.length;i+=4){ if((d[i]+d[i+1]+d[i+2])/3>30) bright++; }
      found={ok:bright>n*0.05, bright, n, kitEmblem:!!o.userData.kitEmblem, w:img.width};
    });
    out[crew]=found||{ok:false,why:'noPlane'};
  }
  // canopy clearance volt
  const V=garages.find(g=>g.crew==='volt'); let und=null;
  if(V&&V.extVariant){ V.extVariant.traverse(o=>{ if(o.name==='kit_ext_volt_dark'&&o.geometry){ o.geometry.computeBoundingBox(); const b=o.geometry.boundingBox; und=+(b.max.y>3? (/*deck+kiosk merged*/ null):null); }});
    // deck box was translated to y=3.85 th=.18 -> underside 3.76; read from userData if set
  }
  out.canopy={plannedUnderside:3.76, note:'deck y=3.85 th=.18'};
  return out;
})()"""

# interiors via KIT_FORCE
ints=[
  dict(name='garage_volt_interior', crew='volt', floor='down'),
  dict(name='garage_rustclaw_interior', crew='rustclaw', floor='down'),
]
with sync_playwright() as p:
  br=p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
  pg=br.new_page(viewport={'width':1920,'height':1080}, device_scale_factor=1.5)
  errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)[:240]))
  print('goto', flush=True)
  pg.goto(B, timeout=180000)
  t0=time.time()
  while time.time()-t0<150:
    try:
      st=pg.evaluate("({r:!!(RIDERS&&RIDERS.ready),k:!!KIT_READY,ext:garages.filter(g=>g.extVariant).length,f:frame})")
      print('wait', st, flush=True)
      if st['f']>20 and st['ext']>=2: break
    except Exception as e:
      print('e', e, flush=True)
    time.sleep(1.5)
  try: pg.keyboard.press('Enter')
  except Exception: pass
  time.sleep(2)
  pg.evaluate("window.__npcPassive=true;window.__npcFreeze=true; garages.forEach(g=>g.gate&&(g.gate.dismissed=true,g.gate.state='open',g.gate.t=1)); if(typeof GATE!='undefined'){GATE.uiOpen=false; try{gateUI()}catch(e){}}")
  pg.evaluate(HOOK)
  for sh in shots:
    pg.evaluate(DAY if sh['day'] else NIGHT)
    pin={k:sh[k] for k in sh if k not in ('name','day')}
    pg.evaluate(f"window.__pin={json.dumps(pin)}; window.KIT_FORCE=null; window.KIT_FLOOR=null;")
    f0=pg.evaluate('frame'); t1=time.time()
    while pg.evaluate('frame')-f0 < 60 and time.time()-t1 < 100: time.sleep(1)
    path=f"{OUT}/{sh['name']}.png"
    pg.screenshot(path=path, timeout=120000)
    print('shot', path, 'df', pg.evaluate('frame')-f0, flush=True)
  # emblem + canopy probe (no extra screenshot)
  try:
    emb=pg.evaluate(EMBLEM_CHECK); print('emblem_check', emb, flush=True)
    open('/tmp/garage_emblem_check.json','w').write(__import__('json').dumps(emb,indent=2))
  except Exception as e:
    print('emblem_check_err', e, flush=True)
  # interiors
  for sh in ints:
    pg.evaluate(NIGHT)
    pg.evaluate(f"""() => {{
      window.KIT_FORCE={json.dumps(sh['crew'])}; window.KIT_FLOOR={json.dumps(sh['floor'])};
      const G=garages.find(g=>g.crew===window.KIT_FORCE); const th=G.th,[gx,gz]=G.pos;
      const W=(lx,lz)=>[gx+lx*Math.cos(th)+lz*Math.sin(th), gz-lx*Math.sin(th)+lz*Math.cos(th)];
      const p=W(0,-4); Ride.group.position.set(p[0],0.05,p[1]);
      window.__pin={{crew:window.KIT_FORCE, clx:0, clz:-3, cy:2.2, tlx:0, tlz:-7, ty:1.4, rlx:0, rlz:-4}};
    }}""")
    # wait kit props
    t1=time.time()
    while time.time()-t1<60:
      if pg.evaluate("!!(KIT.propsReady||KIT.root)"): break
      time.sleep(1)
    f0=pg.evaluate('frame'); t1=time.time()
    while pg.evaluate('frame')-f0 < 60 and time.time()-t1 < 100: time.sleep(1)
    path=f"{OUT}/{sh['name']}.png"
    pg.screenshot(path=path, timeout=120000)
    print('shot', path, 'df', pg.evaluate('frame')-f0, flush=True)
  print('errs', errs[:8], flush=True)
  br.close()
print('hero done', flush=True)
