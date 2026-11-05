CREWS={
 'code-e':('Code : E','CodeE','#22e8f0',"skin: 0xe2b48e, hair: 0x111015, jacket: 0x17161c, cloth: 0x3a3350, gold: 0x7446d0, metal: 0xc3c7d0, skate: 0x5d5f68, eyes: 0xffffff, iris: 0x4a3a36, wheelGlow: 0x22e8f0, glow2: 0x22e8f0, rim: 0x9b7bff, shadow: 0x4a3f8e, outline: 0x07060c"),
 'static-angels':('Static Angels','StaticAngels','#00e5ff',"skin: 0xc98f6e, hair: 0x1e2050, jacket: 0x22d3e0, cloth: 0x1b1b22, gold: 0x9b3dff, metal: 0xd8dcf0, skate: 0x4a2a78, eyes: 0xffffff, iris: 0xa65cff, wheelGlow: 0x00e5ff, glow2: 0x7fe9ff, rim: 0x00e5ff, shadow: 0x4b3f9e, outline: 0x08061a"),
 'kogarasumaru':('Kogarasumaru','Kogarasumaru','#ff2a1a',"skin: 0xf0c8a8, hair: 0x15131c, jacket: 0x232228, cloth: 0x2a2630, gold: 0xe0141e, metal: 0x9aa0ad, skate: 0x2e2c33, eyes: 0xffffff, iris: 0xd01a22, wheelGlow: 0xff2a1a, glow2: 0xff5040, rim: 0xff3b30, shadow: 0x4a3a7a, outline: 0x070509"),
 'anubis':('Anubis','Anubis','#00e0d0',"skin: 0xd9a988, hair: 0x2b2f35, jacket: 0x1f2226, cloth: 0x1a1c20, gold: 0x00b8b0, metal: 0x7d8794, skate: 0x2b2f35, eyes: 0xffffff, iris: 0x00e0d0, wheelGlow: 0x00e0d0, glow2: 0x30fff0, rim: 0x00e5d5, shadow: 0x3c4a8a, outline: 0x05070a"),
 'sleeping-forest':('Sleeping Forest','SleepingForest','#6dffa8',"skin: 0xe8c4a8, hair: 0x1d4a36, jacket: 0xeef0ea, cloth: 0x123a2b, gold: 0x3fae6a, metal: 0xb9c2bb, skate: 0xd9ddd5, eyes: 0xffffff, iris: 0x3fd987, wheelGlow: 0x6dffa8, glow2: 0xa8ffd0, rim: 0x9effc8, shadow: 0x3e4f7a, outline: 0x061a10"),
 'genesis':('Genesis','Genesis','#ff2fae',"skin: 0xc58c6a, hair: 0x2a0f22, jacket: 0xd0158a, cloth: 0x161218, gold: 0xffc83a, metal: 0xe8d6a0, skate: 0xf2eee6, eyes: 0xffffff, iris: 0xff3cb4, wheelGlow: 0xff2fae, glow2: 0xffd36a, rim: 0xffb3e6, shadow: 0x5a2f7a, outline: 0x14040e"),
 'tool-toul-to':('Tool Toul To','ToolToulTo','#ff6a1a',"skin: 0xd2a07c, hair: 0x3a2a22, jacket: 0x6b6f74, cloth: 0x4a4d52, gold: 0xb8501e, metal: 0xa7adb3, skate: 0x8a3a1a, eyes: 0xffffff, iris: 0xff7a2a, wheelGlow: 0xff6a1a, glow2: 0xffb040, rim: 0xff8a3a, shadow: 0x4a3f6a, outline: 0x0a0705"),
 'behemoth':('Behemoth','Behemoth','#ff7a12',"skin: 0xa8765a, hair: 0x18161a, jacket: 0x222226, cloth: 0x2b2a2e, gold: 0xff7a12, metal: 0xd6dbe2, skate: 0x2c2c30, eyes: 0xffffff, iris: 0xff8a20, wheelGlow: 0xff7a12, glow2: 0xffa040, rim: 0xff8a20, shadow: 0x4a3f7a, outline: 0x080608"),
}
def loader(dirn,title,shared='../shared/rider_loader.js'):
    t,p,ring,d=CREWS['code-e' if dirn=='caali' else dirn]
    o="slotSpec: { gold: 0.06 }, slotRim: { hair: 0.25, gold: 0.45, skin: 0.2 }" if dirn in ('code-e','caali') else "slotRim: { hair: 0.3, skin: 0.2 }"
    if dirn=="anubis": o+=", slotEmi: { iris: 1.0 }, slotSpec: { gold: 0.06, skate: 0.3 }"
    return f'''// Sky Rydah's — {title} rider loader. Drop-in for sky-rydahs-v3.html:
//   import {{ loadRider, loadRiderFP }} from './skyrydahs-characters/{dirn}/loader.js';
//   const rider = await loadRider(scene, 'skyrydahs-characters/{dirn}/{dirn}-rider.glb', crewColors, {{ vr }});
//   const fp    = await loadRiderFP(scene, 'skyrydahs-characters/{dirn}/{dirn}-fp.glb', crewColors, {{ vr }});
//   every frame: rider.userData.update(camera, dt, boost01)
// crewColors: slot keys or palette roles (primary/secondary/accent/trim/skin); see ../shared/rider_loader.js.
import {{ loadRider as base, loadRiderFP as baseFP }} from '{shared}';
export const DEFAULTS = {{ {d} }};
export const OPTS = {{ {o} }};
export const loadRider = (scene, url, crewColors = {{}}, opts = {{}}) => base(scene, url, crewColors, {{ defaults: DEFAULTS, crewName: '{t}', ...OPTS, ...opts }});
export const loadRiderFP = (scene, url, crewColors = {{}}, opts = {{}}) => baseFP(scene, url, crewColors, {{ defaults: DEFAULTS, crewName: '{t}', ...OPTS, ...opts }});
'''
def test(dirn,title,glbname):
    t,p,ring,d=CREWS['code-e' if dirn=='caali' else dirn]
    return f'''<!doctype html><html><head><meta charset="utf-8"><title>{title} rider — toon test</title>
<style>html,body{{margin:0;height:100%;background:#0a0a1a;overflow:hidden}}#hud{{position:fixed;left:12px;top:10px;color:{ring};font:600 13px system-ui}}</style>
<script type="importmap">{{"imports":{{"three":"https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/"}}}}</script>
</head><body><div id="hud">{title.upper()} — drag to orbit · B boost · ?fp=1 first-person · ?vr=1 sprite glow (no bloom) · ?lod=0|1|2 · ?crew={{json}}</div>
<script type="module">
import * as THREE from 'three';
import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';
import {{ EffectComposer }} from 'three/addons/postprocessing/EffectComposer.js';
import {{ RenderPass }} from 'three/addons/postprocessing/RenderPass.js';
import {{ UnrealBloomPass }} from 'three/addons/postprocessing/UnrealBloomPass.js';
import {{ OutputPass }} from 'three/addons/postprocessing/OutputPass.js';
import {{ loadRider, loadRiderFP }} from './loader.js';
const q = new URLSearchParams(location.search);
if (q.get('shot')) document.getElementById('hud').style.display = 'none';
const VR = !!q.get('vr'), FP = !!q.get('fp');
const renderer = new THREE.WebGLRenderer({{ antialias: true, preserveDrawingBuffer: true }});
renderer.setPixelRatio(Math.min(devicePixelRatio, 2)); renderer.setSize(innerWidth, innerHeight);
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
document.body.appendChild(renderer.domElement);
const scene = new THREE.Scene(); scene.background = new THREE.Color('#1a1830'); scene.fog = new THREE.Fog(0x1a1830, 6, 22);
const camera = new THREE.PerspectiveCamera(FP ? 80 : 30, innerWidth / innerHeight, 0.03, 100);
const controls = new OrbitControls(camera, renderer.domElement);
const sun = new THREE.DirectionalLight(0xfff2dd, 2.4); sun.position.set(2, 4, 3); scene.add(sun);
scene.add(new THREE.HemisphereLight(0xb8c4ff, 0x40306a, 1.1));
const ground = new THREE.Mesh(new THREE.CircleGeometry(FP ? 6 : 1.4, 48), new THREE.MeshBasicMaterial({{ color: 0x14122a }}));
ground.rotation.x = -Math.PI / 2; scene.add(ground);
const ringG = new THREE.Mesh(new THREE.RingGeometry(1.36, 1.4, 64), new THREE.MeshBasicMaterial({{ color: '{ring}' }}));
ringG.rotation.x = -Math.PI / 2; ringG.position.y = 0.002; scene.add(ringG);
const crew = q.get('crew') ? JSON.parse(q.get('crew')) : {{}};
const rider = FP ? await loadRiderFP(scene, './{glbname}-fp.glb', crew, {{ vr: VR }}) : await loadRider(scene, './{glbname}-rider.glb', crew, {{ vr: VR }});
rider.userData.setLightDir(sun.position);
if (q.get('expr')) for (const e of q.get('expr').split(',')) {{ const [n, w] = e.split(':'); rider.userData.setExpression(n, w === undefined ? 1 : +w); }}
if (q.get('sil')) {{ scene.background = new THREE.Color('#ffffff'); scene.fog = null; ground.visible = ringG.visible = false; const blk = new THREE.MeshBasicMaterial({{ color: 0 }}); rider.traverse(o => {{ if (o.isMesh) o.material = blk; if (o.isSprite) o.visible = false; }}); }}
if (q.get('lod')) {{ const L = rider.userData.lod; L.autoUpdate = false; L.levels.forEach((l, i) => l.object.visible = i === +q.get('lod')); }}
const views = {{ front: 0, '34': Math.PI / 4, side: Math.PI / 2, back: Math.PI }};
const ang = views[q.get('view') || '34'], dist = +(q.get('dist') || 4.3), ty = +(q.get('ty') || 0.9);
if (FP) {{ camera.position.set(0, 1.62, 0.02); controls.target.set(0, 0.75, 0.75); }}
else {{ controls.target.set(0, ty, 0); camera.position.set(Math.sin(ang) * dist, ty + 0.1, Math.cos(ang) * dist); }}
controls.update();
if (q.get('shot')) {{ const a = (FP ? 0 : ang) + 0.6; sun.position.set(Math.sin(a) * 3, 4, Math.cos(a) * 3); rider.userData.setLightDir(sun.position); }}
let composer = null;
if (!VR && !q.get('sil')) {{ composer = new EffectComposer(renderer); composer.addPass(new RenderPass(scene, camera));
  composer.addPass(new UnrealBloomPass(new THREE.Vector2(innerWidth, innerHeight), 0.35, 0.35, 0.92)); composer.addPass(new OutputPass()); }}
let boost = 0, want = 0; addEventListener('keydown', e => {{ if (e.key === 'b') want = 1 - want; }});
addEventListener('resize', () => {{ camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix(); renderer.setSize(innerWidth, innerHeight); composer?.setSize(innerWidth, innerHeight); }});
const clock = new THREE.Clock();
renderer.setAnimationLoop(() => {{ const dt = clock.getDelta(); boost += (want - boost) * Math.min(1, dt * 4);
  controls.update(); rider.userData.update(camera, dt, boost); composer ? composer.render() : renderer.render(scene, camera);
  document.title = 'READY ' + renderer.info.render.calls; }});
</script></body></html>
'''
for dirn,(t,p,ring,d) in CREWS.items():
    open(f'{dirn}/loader.js','w').write(loader(dirn,t))
    open(f'{dirn}/test.html','w').write(test(dirn,t,dirn))
open('caali/loader.js','w').write(loader('caali','Caali (crew Code : E)'))
open('caali/test.html','w').write(test('caali','Caali (Code : E)','caali'))
