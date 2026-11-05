# Pass 7 (after patch_asphalt.py): wardrobe system + Caali G (?player=caali) on the shared Meshy skeleton / skate poser.
f='/workspace/v3build/sky-rydahs-v3-ikki.html'; src=open(f).read()
def rep(o,n,cnt=1):
    global src; assert o in src,o[:80]; src=src.replace(o,n,cnt)
rep("async function loadIkki(parent,refH,fresh){ const c=rResolve(IKKI_DEFAULTS,{});",
    open('/workspace/v3build/wardrobe_js/wardrobe.js').read()+"\nasync function loadIkki(parent,refH,fresh,opt){ opt=opt||{}; const URL_=opt.url||IKKI_URL; const c=rResolve(Object.assign({},IKKI_DEFAULTS,opt.defaults||{}),{});")
rep("new THREE.GLTFLoader().load(IKKI_URL,res,undefined,rej)):rLoad(IKKI_URL))","new THREE.GLTFLoader().load(URL_,res,undefined,rej)):rLoad(URL_))")
rep("glowC:{value:hx('atGlow',IKKI_WHEEL_GLOW.toString(16).padStart(6,'0'))}, paintC:{value:hx('atPaint','ffffff')}, frameC:{value:hx('atFrame','ffffff')}, wheelC:{value:hx('atWheel','ffffff')},",
    "glowC:{value:opt.glow!==undefined?new THREE.Color(opt.glow):hx('atGlow',IKKI_WHEEL_GLOW.toString(16).padStart(6,'0'))}, paintC:{value:new THREE.Color((opt.loadout||{}).paint??0xffffff)}, frameC:{value:new THREE.Color((opt.loadout||{}).frame??0xffffff)}, wheelC:{value:new THREE.Color((opt.loadout||{}).wheel??0xffffff)},\n    ikFx:{value:opt.fx??1}, hide:{value:0}, cover:{value:0}, frameLift:{value:opt.frameLift||1},")
if True:   # url overrides only for Ikki (avoid ?atGlow leaking onto other riders)
    src=src.replace("paintC:{value:new THREE.Color((opt.loadout||{}).paint??0xffffff)}","paintC:{value:opt.loadout?new THREE.Color(opt.loadout.paint??0xffffff):hx('atPaint','ffffff')}",1)
    src=src.replace("frameC:{value:new THREE.Color((opt.loadout||{}).frame??0xffffff)}","frameC:{value:opt.loadout?new THREE.Color(opt.loadout.frame??0xffffff):hx('atFrame','ffffff')}",1)
    src=src.replace("wheelC:{value:new THREE.Color((opt.loadout||{}).wheel??0xffffff)}","wheelC:{value:opt.loadout?new THREE.Color(opt.loadout.wheel??0xffffff):hx('atWheel','ffffff')}",1)
rep("uWheel:sh.wheelC,uRimColor:sh.rimColor});\n    s.vertexShader=IKKI_AT_VERT(s.vertexShader,true);",
    """uWheel:sh.wheelC,uRimColor:sh.rimColor,uIkFx:sh.ikFx,uHide:sh.hide,uCover:sh.cover,uFrameLift:sh.frameLift});
    s.vertexShader=IKKI_AT_VERT(s.vertexShader,true).replace('#include <common>','#include <common>\\n attribute float _slot; attribute float _bm; uniform float uHide; uniform float uCover; varying float vHide;\\n float wdAnd(float a,float b){ float r=0.; for(int i=0;i<10;i++){ float p=exp2(float(i)); r+=mod(floor(a/p),2.)*mod(floor(b/p),2.); } return r; }')
      .replace('#include <begin_vertex>','#include <begin_vertex>\\n vHide=_slot>.5?wdAnd(uHide,exp2(floor(_slot+.5)-1.)):wdAnd(floor(_bm+.5),uCover);');""")
rep("uniform vec3 uRimColor; varying vec3 vFlag; varying float vRestY;')","uniform vec3 uRimColor; varying vec3 vFlag; varying float vRestY; uniform float uIkFx; uniform float uFrameLift; varying float vHide;')\n     .replace('#include <clipping_planes_fragment>','if(vHide>.5) discard;\\n#include <clipping_planes_fragment>')")
rep("max(diffuseColor.rgb*1.6,vec3(.17,.18,.21))","max(diffuseColor.rgb*1.6,vec3(.17,.18,.21)*(sid==13.?uFrame*uFrameLift:vec3(1.)))")
rep("float blu=(1.-atSk)*","float blu=(1.-atSk)*uIkFx*")
rep("totalEmissiveRadiance+=diffuseColor.rgb*atSkin*.18;","totalEmissiveRadiance+=diffuseColor.rgb*atSkin*mix(.0,.18,uIkFx);")
rep("roughnessFactor=mix(roughnessFactor,.75,atSkin);","roughnessFactor=mix(roughnessFactor,mix(.92,.75,uIkFx),atSkin);")
rep("pow(fr,2.5)*low*.55)","pow(fr,2.5)*low*mix(.12,.55,uIkFx)*mix(1.,.15,1.-atSk))")   # wardrobe riders: rim stays on the skates, faint on cloth
rep("mat.customProgramCacheKey=()=>'ikki-pbr-v3';","mat.customProgramCacheKey=()=>'ikki-pbr-v3w';")   # shared program; fx/frame are uniforms
rep("envMapIntensity:1.3});","envMapIntensity:opt.envI??1.3});")
rep("normalMap:src.normalMap,normalScale:src.normalScale","normalMap:opt.noNormal?null:src.normalMap,normalScale:src.normalScale")
rep("patch=jacketDecal('karasu',1);","patch=jacketDecal(opt.crew||'karasu',1);")
rep("Object.assign(root.userData,{ ikki:true, crew:'Ikki',","Object.assign(root.userData,{ ikki:true, crew:opt.name||'Ikki', riderId:opt.key||'ikki', wardrobe:wardrobeAttach(root,{host,mat,bones,cover:sh.cover,hide:sh.hide,baked:WARDROBE.presets[opt.baked||'ikki']}),")
rep("brand:{id:'karasu'}","brand:{id:opt.crew||'karasu'}")
# ---- ?player=caali: wardrobe-built Caali G (skate poser, Meshy AT w/ gold glow). Forge Caali kept hidden as height reference.
rep("""        if(cr.garage==="codee"&&cr.dir==="caali"){ const r=await loadRiderR128(""","""        if(cr.garage==="codee"&&cr.dir==="caali"&&WARDROBE_RIDERS[PLAYER_MODE]){ const ref=new THREE.Group(); ref.visible=false; scene.add(ref);
          const fr=await loadRiderR128(ref,CHAR_BASE+cr.dir+"/"+cr.file+"-rider.glb",{wheelGlow:0xffd700},Object.assign({defaults:cr.defaults,crewName:cr.crew},cr.opts)); RIDERS.ref={r:fr,holder:ref,h:riderHeight(fr)};
          try{ const r=await loadIkki(Ride.group,RIDERS.ref.h,true,WARDROBE_RIDERS[PLAYER_MODE]); RIDERS.player=r; for(const ch of Ride.group.children) if(ch!==r&&ch!==Ride.aura) ch.visible=false; Ride.useGLB=true; }
          catch(e){ console.warn("wardrobe player failed, falling back to Forge Caali: "+(e&&e.message||e)); ref.remove(fr); Ride.group.add(fr); RIDERS.player=fr; RIDERS.ref=null; for(const ch of Ride.group.children) if(ch!==fr&&ch!==Ride.aura) ch.visible=false; Ride.useGLB=true; }
          continue; }
        if(cr.garage==="codee"&&cr.dir==="caali"){ const r=await loadRiderR128(""")
# ?outfit= applied to the player once everything is loaded
rep("    RIDERS.ready=true; };","""    const OUT=new URLSearchParams(location.search).get('outfit'); if(OUT&&RIDERS.player&&RIDERS.player.userData.wardrobe){ try{ await RIDERS.player.userData.wardrobe.apply(OUT); }catch(e){ console.warn('outfit failed: '+(e&&e.message||e)); } }
    RIDERS.ready=true; };""")
open(f,'w').write(src); print('patched',len(src))
