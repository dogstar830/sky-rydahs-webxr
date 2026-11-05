# Standard Xbox gamepad input layer: inject gamepad.js (window.SR_PAD) and route every navigator.getGamepads read through it. Runs last in build_ikki.sh.
f='/workspace/v3build/sky-rydahs-v3-ikki.html'; src=open(f).read(); js=open('/workspace/v3build/gamepad.js').read()
if 'window.SR_PAD=S' in src: print("patch_gamepad: already applied"); raise SystemExit
def rep(a,b):
    global src
    assert src.count(a)==1, ("anchor",a[:70],src.count(a)); src=src.replace(a,b)
rep('// ===== INPUT =====', js+'\n// ===== INPUT =====')
# frame loop drives polling
rep('  poll(); try{ gatesPre(dt);','  SR_PAD.update(); poll(); try{ gatesPre(dt);')
# main poll (legacy block; pad.js runs it muted and applies its own mapping)
rep('window._kp={}; const pads=navigator.getGamepads?[...navigator.getGamepads()].filter(Boolean):[], gp=pads[0];','window._kp={}; const P=SR_PAD, gp=P.active();')
rep('''  if(gp){ const lx=gp.axes[0]||0, ly=gp.axes[1]||0;
    if(Math.hypot(lx,ly)>.2){ ix=lx; iz=-ly; }
    const b=i=>!!(gp.buttons[i]&&gp.buttons[i].pressed);
    cur.up=cur.up||b(12)||ly<-.6; cur.down=cur.down||b(13)||ly>.6; cur.left=cur.left||b(14)||lx<-.6; cur.right=cur.right||b(15)||lx>.6;
    cur.select=cur.select||b(0); cur.start=cur.start||b(9); cur.back=cur.back||b(1); Input.boost=Input.boost||b(4); Input.tag=Input.tag||b(5)||b(2); }''',
'''  if(gp){ const {x:lx,y:ly}=P.stick("left"), b=P.pressed;
    if(Math.hypot(lx,ly)>0){ ix=lx; iz=-ly; }
    cur.up=cur.up||b("DPAD_UP")||ly<-.6; cur.down=cur.down||b("DPAD_DOWN")||ly>.6; cur.left=cur.left||b("DPAD_LEFT")||lx<-.6; cur.right=cur.right||b("DPAD_RIGHT")||lx>.6;
    cur.select=cur.select||b("A"); cur.start=cur.start||b("MENU"); cur.back=cur.back||b("B");  Input.tag=Input.tag||b("RB")||b("X"); }''')
# rumble
rep('''    for(const gp of (navigator.getGamepads?[...navigator.getGamepads()]:[])) if(gp&&gp.vibrationActuator) gp.vibrationActuator.playEffect("dual-rumble",{duration:ms,strongMagnitude:strength*.5,weakMagnitude:strength}); }catch(e){} }''',
'''    SR_PAD.rumble(strength*.5,strength,ms); }catch(e){} }''')
rep('''function grindRumble(strong,weak,ms){ try{ for(const gp of (navigator.getGamepads?[...navigator.getGamepads()]:[])) if(gp&&gp.vibrationActuator&&gp.vibrationActuator.playEffect){ gp.vibrationActuator.playEffect("dual-rumble",{duration:ms,strongMagnitude:strong,weakMagnitude:weak}); GRIND.rumbles=(GRIND.rumbles||0)+1; } }catch(e){} }''',
'''function grindRumble(strong,weak,ms){ try{ GRIND.rumbles=(GRIND.rumbles||0)+SR_PAD.rumble(strong,weak,ms); }catch(e){} }''')
# gate keypad
rep('''function gatePadInput(q){ const gp=(navigator.getGamepads?[...navigator.getGamepads()]:[]).find(Boolean); if(!gp||renderer.xr.isPresenting) return; const P=GATE.prevPad, b=i=>!!(gp.buttons[i]&&gp.buttons[i].pressed), ax=gp.axes||[];
  const now={u:b(12)||ax[1]<-.6,d:b(13)||ax[1]>.6,l:b(14)||ax[0]<-.6,r:b(15)||ax[0]>.6,a:b(0),x:b(1)};''',
'''function gatePadInput(q){ if(!SR_PAD.active()) return; const P=GATE.prevPad, b=SR_PAD.pressed, ls=SR_PAD.stick("left");
  const now={u:b("DPAD_UP")||ls.y<-.6,d:b("DPAD_DOWN")||ls.y>.6,l:b("DPAD_LEFT")||ls.x<-.6,r:b("DPAD_RIGHT")||ls.x>.6,a:b("A"),x:b("B")};''')
# legacy wall input (run muted by pad.js)
rep('''  const gp=(navigator.getGamepads?[...navigator.getGamepads()]:[]).find(Boolean), xr=renderer.xr.isPresenting;
  if(gp&&!xr){ const b=i=>!!(gp.buttons[i]&&gp.buttons[i].pressed), P=ATK.prevPad, e=i=>b(i)&&!P[i];
    if(e(0)) I.jumpP=true; if(b(0)) I.jump=true; if(e(3)) I.a[0]=true; if(e(7)) I.a[1]=true; if(e(6)) I.a[2]=true;
    const ly=gp.axes[1]||0, lx=gp.axes[0]||0; if(ly>.5) I.back=true; if(Math.abs(lx)>.5) I.side=Math.sign(lx); for(const i of [0,3,6,7]) P[i]=b(i); }''',
'''  const gp=SR_PAD.active(), xr=renderer.xr.isPresenting;
  if(gp){ const b=SR_PAD.pressed, e=SR_PAD.justPressed;
    if(e("A")) I.jumpP=true; if(b("A")) I.jump=true; if(e("Y")) I.a[0]=true; if(e("RT")) I.a[1]=true; if(e("LB")) I.a[2]=true;
    const {x:lx,y:ly}=SR_PAD.stick("left"); if(ly>.5) I.back=true; if(Math.abs(lx)>.5) I.side=Math.sign(lx); }''')
# pad.js layer: read the shared module instead of navigator.getGamepads; mute instead of stubbing navigator
rep('''function padGet(){ try{ return (navigator.getGamepads?[...navigator.getGamepads()]:[]).find(Boolean)||null; }catch(e){ return null; } }''',
'''function padGet(){ return SR_PAD.active()?SR_PAD.pad:null; }''')
rep('''function padNoPad(fn){ const own=Object.prototype.hasOwnProperty.call(navigator,"getGamepads"), real=navigator.getGamepads; try{ navigator.getGamepads=()=>[]; return fn(); } finally { if(own) navigator.getGamepads=real; else delete navigator.getGamepads; } }''',
'''function padNoPad(fn){ return SR_PAD.withMuted(fn); }''')
rep('''function padRead(){ const gp=padGet(); const P=PAD.prev, C={};
  const b=i=>!!(gp&&gp.buttons[i]&&(gp.buttons[i].pressed||gp.buttons[i].value>PAD.dz.trig)), v=i=>gp&&gp.buttons[i]?(gp.buttons[i].value||(gp.buttons[i].pressed?1:0)):0;
  for(let i=0;i<17;i++){ C[i]=b(i); } const e=i=>C[i]&&!P[i]; const ax=gp?gp.axes||[]:[];
  const r={gp, b:i=>C[i], e, v, ls:padStick(ax[0]||0,ax[1]||0,PAD.dz.ls), rs:padStick(ax[2]||0,ax[3]||0,PAD.dz.rs)}; PAD.cur=C; return r; }''',
'''function padRead(){ const S=SR_PAD, gp=padGet(), C={}; for(let i=0;i<17;i++) C[i]=S.pressed(i);
  const st=w=>{ const s=S.stick(w), m=Math.min(1,Math.hypot(s.x,s.y)); return [s.x,s.y,m]; };
  const r={gp, b:i=>C[i], e:i=>S.justPressed(i), u:i=>S.justReleased(i), v:i=>S.value(i), ls:st("left"), rs:st("right")}; PAD.cur=C; return r; }''')

# --- XR: the standard pad (incl. Quest gamepad-emulation: Meta+Menu) works in and out of XR; when one is connected, raw XR inputSources button reads are skipped (no double-fire).
rep('const ses=renderer&&renderer.xr&&renderer.xr.getSession&&renderer.xr.getSession(); if(ses) for(const s of ses.inputSources){','const ses=!SR_PAD.connected&&renderer&&renderer.xr&&renderer.xr.getSession&&renderer.xr.getSession(); if(ses) for(const s of ses.inputSources){')
rep('const ses=xr&&renderer.xr.getSession(); if(ses){ for(const s of ses.inputSources){','const ses=xr&&!SR_PAD.connected&&renderer.xr.getSession(); if(ses){ for(const s of ses.inputSources){')
rep('gp=R&&R.gp&&!renderer.xr.isPresenting, K=GRIND.keyPrev;','gp=R&&R.gp, K=GRIND.keyPrev;')
rep('const xr=renderer.xr.isPresenting&&renderer.xr.getSession();\n  let drop','const xr=renderer.xr.isPresenting&&!SR_PAD.connected&&renderer.xr.getSession();\n  let drop') if 'const xr=renderer.xr.isPresenting&&renderer.xr.getSession();\n  let drop' in src else rep('if(gp&&R.ls[2]>0) lean=R.ls[0]; const xr=renderer.xr.isPresenting&&renderer.xr.getSession();','if(gp&&R.ls[2]>0) lean=R.ls[0]; const xr=renderer.xr.isPresenting&&!SR_PAD.connected&&renderer.xr.getSession();')
rep('  if(!R.gp||renderer.xr.isPresenting){ padCommit(); return; }','  if(!R.gp){ padCommit(); return; }')
rep('const I=padNoPad(_wi), R=PAD.R; if(!R||!R.gp||renderer.xr.isPresenting) return I;','const I=padNoPad(_wi), R=PAD.R; if(!R||!R.gp) return I;')
# RS camera orbit / LT over-the-shoulder aim stay off in XR (headset owns the camera); all other pad actions are live in XR.
assert 'getGamepads' not in src.replace(js,''), "stray getGamepads read"
open(f,'w').write(src); print("patch_gamepad ok")
