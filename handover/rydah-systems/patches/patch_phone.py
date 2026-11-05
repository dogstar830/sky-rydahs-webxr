# iLink phone (phone.js) + icon set (icons.js) + world map/minimap (map.js) + grapple (grapple.js) + targeting (target.js) + ?fps overlay (fps.js) + Xbox gamepad layer (pad.js) + hide top controls/instructions overlay unless ?controls. Runs last in build_ikki.sh.
f=__import__('os').environ.get('SR_HTML','/workspace/v3build/sky-rydahs-v3-ikki.html'); src=open(f).read(); js=open('/workspace/v3build/phone.js').read()+'\n'+open('/workspace/v3build/icons.js').read()+'\n'+open('/workspace/v3build/map.js').read()+'\n'+open('/workspace/v3build/grapple.js').read()+'\n'+open('/workspace/v3build/pad.js').read()+'\n'+open('/workspace/v3build/target.js').read()+'\n'+open('/workspace/v3build/fps.js').read()
if 'const PHONE={' in src: print("patch_phone: already applied"); raise SystemExit
def rep(a,b):
    global src
    assert src.count(a)==1, ("anchor",a[:60],src.count(a)); src=src.replace(a,b)
rep('\nfunction init(){', '\n'+js+'\nfunction init(){')
R='  if(FX.on&&!xr&&!window.__noFX) FX.composer.render(); else renderer.render(scene,camera);'
rep(R,'  if(window.fpsTick) fpsTick(dt,xr);\n  if(window.grapTick) grapTick();\n  if(window.padTick) padTick(dt,xr);\n  if(window.tgtTick) tgtTick(dt);\n  if(window.mapTick) mapTick(dt,xr);\n  if(window.phoneTick) phoneTick(dt,xr);\n'+R)
rep('const ATK_KEYS={ light:"J / LMB / Y / right B", heavy:"K / RMB / RT / left X", special:"L / LT / left Y" };','const ATK_KEYS={ light:"J / LMB / RB tap", heavy:"K / RMB / hold RB", special:"L / RT" };')
rep('</style>','body:not(.showctl) #objective{display:none!important}\n</style>',) if src.count('</style>')==1 else None
if 'body:not(.showctl)' not in src:
    i=src.index('</style>'); src=src[:i]+'body:not(.showctl) #objective{display:none!important}\n'+src[i:]
rep('<div id="status" class="hud">','<script>if(/[?&]controls\\b/.test(location.search)) document.body.classList.add("showctl");</script><div id="status" class="hud">')
open(f,'w').write(src); print("patch_phone ok")
