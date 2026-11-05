# Pass 3 on the Ikki build (run after patch_ikki.py + patch_turf.py; see build_ikki.sh).
# Swaps the Mixamo walk/run mixer for a procedural skate-stride poser, LOD'd single-draw-call toon body (skates+crow merged
# in ikki-meshy-skate.glb by ikki_skate/build_lod.py), screen-space depth edge pass, cyan Kogarasumaru palette, Portside NPC loop.
import re
f='/workspace/v3build/sky-rydahs-v3-ikki.html'; src=open(f).read()
def rep(o,n):
    global src; assert o in src,o[:70]; src=src.replace(o,n,1)
# --- sync Ani's cyan crew edits (crews.js line for kogarasumaru, world.js karasu garage) into the build
crew=[l for l in open('/workspace/v3build/crews.js') if 'dir:"kogarasumaru"' in l][0].rstrip('\n')
src=re.sub(r'^\s*\{dir:"kogarasumaru".*$',lambda m:crew,src,count=1,flags=re.M)
gar=[l for l in open('/workspace/v3build/world.js') if 'crew:"karasu"' in l][0].rstrip('\n')
src=re.sub(r'^\s*\{crew:"karasu",name:"KOGARASUMARU".*$',lambda m:gar,src,count=1,flags=re.M)
rep('const IKKI_DEFAULTS={ skate:0x3a3a3e, wheelGlow:IKKI_WHEEL_GLOW, rim:0x30d8ff,','const IKKI_DEFAULTS={ skate:0x2e2c38, wheelGlow:IKKI_WHEEL_GLOW, glow2:0x00e5ff, iris:0x00b8d4, crow:0x0b0a12, rim:0x00e5ff,')  # every Ikki glow (wheel, secondary, rim) = 0x00e5ff (Oliver)
src=re.sub(r"^const IKKI_NPC_LOOP=.*$",lambda m:"const IKKI_NPC_LOOP={garage:'karasu',out:9,rx:7,rz:4.5,speed:.42}; // figure-8 carve in front of the Kogarasumaru garage (Portside, 55,30)",src,count=1,flags=re.M)
rep('const IKKI_URL=(new URLSearchParams(location.search).get("ikki"))||(CHAR_BASE+"meshy/ikki-meshy-rigged-opt.glb");',
    'const IKKI_URL=(new URLSearchParams(location.search).get("ikki"))||(CHAR_BASE+"meshy/ikki-meshy-skate.glb"); // LOD0/1/2 + merged skates + crow emblem')
# --- replace loader body
a=src.index('async function loadIkki('); b=src.index('parent.add(root); return root; }',a)+len('parent.add(root); return root; }')
NEW=open('/workspace/v3build/ikki_skate/ikki_skate.js').read()
src=src[:a]+NEW+src[b:]
# --- player drive: pass airborne/boost
rep("RIDERS.player.userData.drive(dt,sp,R.grinding,clock);","RIDERS.player.userData.drive(dt,sp,R.grinding,clock,R.boost);")
# --- NPC: figure-8 at Portside garage, speed varies so it pushes, glides and tucks
a=src.index("  if(RIDERS.ikkiNpc){"); b=src.index("\n",a)
src=src[:a]+"""  if(RIDERS.ikkiNpc){ const n=RIDERS.ikkiNpc, L=IKKI_NPC_LOOP; n.ph+=dt; if(!n.c){ const g=garages.find(q=>q.crew===L.garage); n.c=g?[g.pos[0]+Math.sin(g.th)*L.out,g.pos[1]+Math.cos(g.th)*L.out]:[55,30]; n.prev=null; }
    const a=n.ph*L.speed, x=n.c[0]+Math.sin(a)*L.rx, z=n.c[1]+Math.sin(a*2)*L.rz; n.holder.position.set(x,0,z);
    const dx=Math.cos(a)*L.rx, dz=2*Math.cos(a*2)*L.rz; n.holder.rotation.y=Math.atan2(dx,dz); const nsp=.45+.4*Math.abs(Math.cos(a)); // fast through the crossing, slow at the lobes
    n.holder.visible=!window.__hideIkkiNpc&&n.holder.position.distanceToSquared(cam.position)<70*70; n.r.visible=n.holder.visible; if(n.holder.visible){ n.r.userData.drive(dt,window.__npcSp??nsp,!!window.__npcGrind,clock,0); n.r.userData.update(cam,dt,.3); } else if(n.r.userData.ground) n.r.userData.ground.visible=false; }"""+src[b:]
# --- screen-space depth edge pass (desktop composer only; XR renders direct)
rep("const cmp=new THREE.EffectComposer(renderer); cmp.addPass(new THREE.RenderPass(scene,camera));",
 """const cmp=new THREE.EffectComposer(renderer); for(const rt of [cmp.renderTarget1,cmp.renderTarget2]){ rt.depthTexture=new THREE.DepthTexture(); rt.depthTexture.type=THREE.UnsignedIntType; rt.depthBuffer=true; }
  cmp.addPass(new THREE.RenderPass(scene,camera)); const edge=new THREE.ShaderPass(EdgeShader); const er=edge.render.bind(edge);
  edge.render=(r,w,rd,dt,m)=>{ edge.uniforms.tDepth.value=rd.depthTexture; edge.uniforms.uTexel.value.set(1/rd.width,1/rd.height); edge.uniforms.uNF.value.set(camera.near,camera.far); er(r,w,rd,dt,m); };
  if(/[?&]edge=1/.test(location.search)) cmp.addPass(edge); FX.edge=edge; // v3 brief: stylized realism -> ink edge pass off by default""")
rep("function setupFX(){","""// depth-discontinuity ink lines (log-depth ratio, fades with distance so far city stays clean)
const EdgeShader={ uniforms:{tDiffuse:{value:null},tDepth:{value:null},uTexel:{value:new THREE.Vector2()},uNF:{value:new THREE.Vector2(.1,600)},uInk:{value:new THREE.Color(0x07060c)},uStr:{value:.8}},
  vertexShader:`varying vec2 vUv; void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
  fragmentShader:`uniform sampler2D tDiffuse; uniform sampler2D tDepth; uniform vec2 uTexel; uniform vec2 uNF; uniform vec3 uInk; uniform float uStr; varying vec2 vUv;
    float lz(vec2 uv){ float d=texture2D(tDepth,uv).x; return uNF.x*uNF.y/(uNF.y-d*(uNF.y-uNF.x)); }
    void main(){ vec4 c=texture2D(tDiffuse,vUv); float z=lz(vUv); float zx=lz(vUv+vec2(uTexel.x,0.)), zX=lz(vUv-vec2(uTexel.x,0.)), zy=lz(vUv+vec2(0.,uTexel.y)), zY=lz(vUv-vec2(0.,uTexel.y));
      float e=max(max(abs(zx-z),abs(zX-z)),max(abs(zy-z),abs(zY-z)))/z; float k=smoothstep(.06,.14,e)*(1.-smoothstep(18.,45.,z))*uStr;
      gl_FragColor=vec4(mix(c.rgb,uInk,k),c.a); }` };
function setupFX(){""")
# bloom: gentler
rep("new THREE.UnrealBloomPass(new THREE.Vector2(W/2,H/2),.75,.5,.62)","new THREE.UnrealBloomPass(new THREE.Vector2(W/2,H/2),.6,.45,.68)")
open(f,'w').write(src); print("patched",len(src))
