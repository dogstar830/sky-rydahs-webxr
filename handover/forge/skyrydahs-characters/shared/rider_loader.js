// Sky Rydah's — shared rider loader (all crews). Per-crew loader.js files wrap this with crew defaults.
//
//   import { loadRider, loadRiderFP } from './loader.js';
//   const rider = await loadRider(scene, 'kogarasumaru/kogarasumaru-rider.glb', { primary: 0x222222, accent: 0xe0141e }, { vr: false });
//   each frame: rider.userData.update(camera, dt, boost01)
//
// GLB layout (built by shared/rider_lib.py):
//   <Prefix>_Rig armature, meshes <Prefix>_LOD{0,1,2}_{body,hair,top,skates,accessory,glow}, all skinned to one skeleton,
//   *_Att attachment empties (Hat, Hair, Face, Neck, Collar, ShoulderL/R, BodyFront, BodyBack, Waist, GripL/R, FootL/R),
//   GlowPt_* empties (sprite glow anchors, extras.glowSize).
// Colour: one grey-banded atlas, each palette slot owns an atlas cell -> slot = floor(uv.x * NSLOTS); the shader multiplies
//   the slot colour from crewColors. Modules are merged here into ONE skinned mesh per LOD, so a rider costs 3 draw calls
//   (toon body + inverted-hull outline + glow) at whatever LOD is active.
// crewColors keys: slot names (skin hair jacket cloth gold metal skate eyes iris wheelGlow glow2), palette roles
//   (primary->jacket, secondary->cloth, accent->gold(+iris), trim->skate, skin), plus rim, shadow, outline.
// options: { vr:false, lodDistances:[0,14,32], outline:true, tones:3, normalScale:0.8 }
// Hero riders (painted atlas 512x128 + baked normal map on uv1 + expression morphs on LOD0):
//   rider.userData.expressions -> ['blink','smile','angry','surprised','sad','smirk','mouthOpen','focus']; setExpression(name, 0..1)
//   vr:true -> no bloom-dependent emissive boost; additive sprite glow on wheels/halo/visor instead (use without bloom).
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

export const SLOTS = ['skin', 'hair', 'jacket', 'cloth', 'gold', 'metal', 'skate', 'eyes', 'iris', 'wheelGlow', 'glow2'];
export const ROLES = { primary: 'jacket', secondary: 'cloth', accent: 'gold', trim: 'skate', skin: 'skin' };
const BASE = {
  skin: 0xffd9c2, hair: 0x23222f, jacket: 0x2a2a30, cloth: 0x34304a, gold: 0xffd700, metal: 0x8c93a3, skate: 0x3a3a3e,
  eyes: 0xffffff, iris: 0xffc21a, wheelGlow: 0xffd700, glow2: 0xffd700, rim: 0xffd700, shadow: 0x5a4f9e, outline: 0x07060c,
};
const SPEC = { hair: 0.0, metal: 1.0, gold: 1.0, skate: 0.8 };
const RIM = { jacket: 1.0, hair: 0.8, cloth: 0.6, skate: 0.9, skin: 0.35, metal: 0.6, gold: 0.4 };
const EMI = { iris: 0.35, eyes: 0.1 };
const HL = { hair: 0.32, iris: 1.0, eyes: 0.6, metal: 0.5 };   // painted-highlight strength (atlas texels ~1.0, painted atlas only)

export function resolveColors(defaults = {}, crew = {}) {
  const c = { ...BASE, ...defaults };
  const user = { ...crew };
  for (const [role, slot] of Object.entries(ROLES)) if (user[role] !== undefined && user[slot] === undefined) user[slot] = user[role];
  if (crew.accent !== undefined) for (const k of ['gold', 'iris']) if (crew[k] === undefined) user[k] = crew.accent;
  return { ...c, ...user };
}

// Flat Trigger-style ramp (Cyberpunk/Edgerunners research): 3 tones by default, 2 for extra-flat.
export function makeGradientMap(tones = 3) {
  const v = tones === 2 ? [95, 255] : tones === 4 ? [70, 150, 225, 255] : [85, 185, 255];
  const data = new Uint8Array(v.flatMap((x) => [x, x, x, 255]));
  const t = new THREE.DataTexture(data, v.length, 1, THREE.RGBAFormat);
  t.minFilter = t.magFilter = THREE.NearestFilter; t.generateMipmaps = false; t.needsUpdate = true; return t;
}

function slotUniforms(c, o = {}) {
  const rim = { ...RIM, ...(o.slotRim ?? {}) }, spec = { ...SPEC, ...(o.slotSpec ?? {}) }, emi = { ...EMI, ...(o.slotEmi ?? {}) };
  return {
    uSlotColor: { value: SLOTS.map((s) => new THREE.Color(c[s])) },
    uSlotRim: { value: SLOTS.map((s) => rim[s] ?? 0.5) },
    uSlotSpec: { value: SLOTS.map((s) => spec[s] ?? 0) },
    uSlotEmi: { value: SLOTS.map((s) => emi[s] ?? 0) },
    uSlotHL: { value: SLOTS.map((s) => HL[s] ?? 0.3) },
  };
}
const SLOT_GLSL = `#define NSLOTS ${SLOTS.length}
  uniform vec3 uSlotColor[NSLOTS]; uniform float uSlotRim[NSLOTS]; uniform float uSlotSpec[NSLOTS]; uniform float uSlotEmi[NSLOTS]; uniform float uSlotHL[NSLOTS]; uniform float uPainted;
  int riderSlot(vec2 uv){ return clamp(int(floor(uv.x * float(NSLOTS))), 0, NSLOTS - 1); }`;

function makeToonMaterial(map, shared, normalMap = null) {
  const m = new THREE.MeshToonMaterial({ color: 0xffffff, map, gradientMap: shared.gradientMap });
  if (normalMap) { m.normalMap = normalMap; m.normalScale = new THREE.Vector2(shared.normalScale, -shared.normalScale); }
  m.onBeforeCompile = (sh) => {
    Object.assign(sh.uniforms, shared.slots, { uPainted: shared.painted, uRimColor: shared.rimColor, uShadowTint: shared.shadowTint, uLightDirV: shared.lightDirV });
    sh.fragmentShader = sh.fragmentShader
      .replace('#include <common>', `#include <common>
        ${SLOT_GLSL}
        uniform vec3 uRimColor; uniform vec3 uShadowTint; uniform vec3 uLightDirV;`)
      .replace('#include <map_fragment>', `#include <map_fragment>
        int sl = riderSlot(vMapUv);
        float hlMask = uPainted * smoothstep(0.9, 0.98, sampledDiffuseColor.r);
        diffuseColor.rgb *= uSlotColor[sl];`)
      .replace('#include <emissivemap_fragment>', `#include <emissivemap_fragment>
        totalEmissiveRadiance += uSlotColor[sl] * uSlotEmi[sl];`)
      .replace('#include <opaque_fragment>', `
        vec3 Vd = normalize(vViewPosition); vec3 Nn = normalize(normal);
        float ndl = dot(Nn, uLightDirV);
        outgoingLight *= mix(uShadowTint, vec3(1.0), smoothstep(-0.08, 0.22, ndl));   // soft terminator, purple-blue shadows
        float fr = 1.0 - clamp(dot(Nn, Vd), 0.0, 1.0);
        outgoingLight += uRimColor * smoothstep(0.74, 0.8, fr) * smoothstep(0.1, -0.4, ndl - 0.25) * uSlotRim[sl] * 0.7;
        vec3 Hh = normalize(uLightDirV + Vd);
        outgoingLight += vec3(1.0, 0.97, 0.9) * step(0.975, dot(Nn, Hh)) * uSlotSpec[sl] * 0.8;   // one hard anime highlight
        outgoingLight += mix(vec3(1.0), uSlotColor[sl], 0.3) * hlMask * uSlotHL[sl];   // painted highlight (angel ring, catchlight)
        #include <opaque_fragment>`);
  };
  m.customProgramCacheKey = () => 'rider-toon' + (m.normalMap ? '-n' : '');
  return m;
}

function makeGlowMaterial(map, shared) {
  const m = new THREE.MeshBasicMaterial({ color: 0xffffff, map, toneMapped: false });
  m.onBeforeCompile = (sh) => {
    Object.assign(sh.uniforms, shared.slots, { uGlow: shared.glow });
    sh.fragmentShader = sh.fragmentShader
      .replace('#include <common>', `#include <common>
        ${SLOT_GLSL}
        uniform float uGlow;`)
      .replace('#include <map_fragment>', `diffuseColor.rgb = uSlotColor[riderSlot(vMapUv)] * uGlow;`);
  };
  m.customProgramCacheKey = () => 'rider-glow';
  return m;
}

function makeOutlineMaterial(c, shared) {
  return new THREE.ShaderMaterial({
    side: THREE.BackSide, transparent: true,
    uniforms: { uThick: shared.outlineThick, uFar: shared.outlineFar, uColor: { value: new THREE.Color(c.outline) } },
    vertexShader: `
      #include <common>
      #include <skinning_pars_vertex>
      uniform float uThick; uniform float uFar; varying float vFade;
      void main(){
        #include <beginnormal_vertex>
        #include <skinbase_vertex>
        #include <skinnormal_vertex>
        #include <begin_vertex>
        #include <skinning_vertex>
        vec4 mvPosition = modelViewMatrix * vec4(transformed, 1.0);
        vec3 n = normalize(normalMatrix * objectNormal);
        float d = -mvPosition.z;
        mvPosition.xyz += n * uThick * clamp(d, 0.6, 5.0);
        vFade = 1.0 - smoothstep(uFar * 0.55, uFar, d);
        gl_Position = projectionMatrix * mvPosition;
      }`,
    fragmentShader: `uniform vec3 uColor; varying float vFade;
      void main(){ if (vFade < 0.02) discard; gl_FragColor = vec4(uColor, vFade); }`,
  });
}

let glowTex = null;
function glowTexture() {
  if (glowTex) return glowTex;
  const cv = document.createElement('canvas'); cv.width = cv.height = 64; const g = cv.getContext('2d');
  const gr = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.25, 'rgba(255,255,255,0.55)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = gr; g.fillRect(0, 0, 64, 64); glowTex = new THREE.CanvasTexture(cv); return glowTex;
}

function mergeSkinned(meshes, material) {
  // union of expression morph names (only the face/body module carries them); zero-fill the rest so they merge
  const names = [];
  for (const m of meshes) for (const n of Object.keys(m.morphTargetDictionary ?? {})) if (!names.includes(n)) names.push(n);
  const keep = ['position', 'normal', 'uv', 'skinIndex', 'skinWeight'];
  if (meshes.every((m) => m.geometry.attributes.uv1)) keep.push('uv1');
  const geos = meshes.map((m) => {
    const g = m.geometry.clone();
    for (const k of Object.keys(g.attributes)) if (!keep.includes(k)) g.deleteAttribute(k);
    const cnt = g.attributes.position.count, dict = m.morphTargetDictionary ?? {}, src = m.geometry.morphAttributes;
    g.morphAttributes = {};
    if (names.length) {
      for (const at of ['position', 'normal']) g.morphAttributes[at] = names.map((n) => (dict[n] !== undefined && src[at]?.[dict[n]]) ? src[at][dict[n]] : new THREE.Float32BufferAttribute(new Float32Array(cnt * 3), 3));
      g.morphTargetsRelative = true;
    }
    return g;
  });
  const geo = mergeGeometries(geos, false);
  if (names.length) geo.morphTargetsRelative = true;
  const ref = meshes[0];
  const merged = new THREE.SkinnedMesh(geo, material);
  merged.bind(ref.skeleton, ref.bindMatrix);
  merged.frustumCulled = false;
  if (names.length) {
    // CPU expression morphs: faces change rarely, so blend on the CPU into the base buffers (portable to Quest/SwiftShader,
    // and the outline hull shares the geometry so it follows for free). Only vertices touched by any morph are updated.
    const pos = geo.attributes.position, nor = geo.attributes.normal, mp = geo.morphAttributes.position, mn = geo.morphAttributes.normal;
    const idx = [];
    for (let i = 0; i < pos.count; i++) { for (const a of mp) if (a.getX(i) || a.getY(i) || a.getZ(i)) { idx.push(i); break; } }
    const basePos = new Float32Array(idx.length * 3), baseNor = new Float32Array(idx.length * 3);
    idx.forEach((v, k) => { for (let c = 0; c < 3; c++) { basePos[k * 3 + c] = pos.array[v * 3 + c]; baseNor[k * 3 + c] = nor.array[v * 3 + c]; } });
    const dP = mp.map((a) => Float32Array.from(idx.flatMap((v) => [a.getX(v), a.getY(v), a.getZ(v)])));
    const dN = mn.map((a) => Float32Array.from(idx.flatMap((v) => [a.getX(v), a.getY(v), a.getZ(v)])));
    geo.morphAttributes = {};
    const w = names.map(() => 0);
    merged.userData.expr = {
      names, weights: w,
      set(name, val) {
        const t = names.indexOf(name); if (t < 0) return; w[t] = val;
        for (let k = 0; k < idx.length; k++) for (let c = 0; c < 3; c++) {
          let p = basePos[k * 3 + c], n = baseNor[k * 3 + c];
          for (let j = 0; j < w.length; j++) if (w[j]) { p += dP[j][k * 3 + c] * w[j]; n += dN[j][k * 3 + c] * w[j]; }
          pos.array[idx[k] * 3 + c] = p; nor.array[idx[k] * 3 + c] = n;
        }
        pos.needsUpdate = true; nor.needsUpdate = true;
      },
    };
  }
  return merged;
}

async function build(scene, url, crewColors, opts, fp) {
  const c = resolveColors(opts.defaults, crewColors);
  const gltf = await new GLTFLoader().loadAsync(url);
  const root = gltf.scene;
  const shared = {
    gradientMap: makeGradientMap(opts.tones ?? 3), slots: slotUniforms(c, opts),
    rimColor: { value: new THREE.Color(c.rim) }, shadowTint: { value: new THREE.Color(c.shadow) },
    lightDirV: { value: new THREE.Vector3(0.4, 0.8, 0.5).normalize() }, glow: { value: 1.3 },
    outlineThick: { value: 0.0022 }, outlineFar: { value: 40 }, painted: { value: 0 }, normalScale: opts.normalScale ?? 0.8,
  };
  let map = null, nmap = null;
  const levels = {}; const att = {}; const glowPts = [];
  root.traverse((o) => {
    if (o.isMesh) {
      if (!map && o.material.map) { map = o.material.map; map.colorSpace = THREE.SRGBColorSpace; map.magFilter = map.image?.width >= 512 ? THREE.LinearFilter : THREE.NearestFilter; map.minFilter = THREE.LinearFilter; map.generateMipmaps = false; map.needsUpdate = true; }
      if (!nmap && o.material.normalMap) nmap = o.material.normalMap;
      const m = o.name.match(/_LOD(\d)_(\w+)$/) || (fp ? o.name.match(/_FP_(body|glow)$/) && [null, '0', o.name.endsWith('glow') ? 'glow' : 'body'] : null);
      if (m) (levels[m[1]] ??= { body: [], glow: [] })[m[2] === 'glow' ? 'glow' : 'body'].push(o);
    } else if (/_Att$/.test(o.name)) att[o.name.replace(/_Att$/, '')] = o;
    else if (/^GlowPt_/.test(o.name)) glowPts.push(o);
  });
  shared.painted.value = map?.image?.width >= 512 ? 1 : 0;
  const lvl0 = levels[Object.keys(levels).sort()[0]];
  const toon = makeToonMaterial(map, shared, lvl0 && lvl0.body.every((o) => o.geometry.attributes.uv1) ? nmap : null), glowMat = makeGlowMaterial(map, shared), outlineMat = makeOutlineMaterial(c, shared);
  const lod = new THREE.LOD(); lod.name = 'riderLOD';
  const dists = opts.lodDistances ?? [0, 14, 32];
  let host = null;
  for (const li of Object.keys(levels).sort()) {
    const { body, glow } = levels[li];
    host ??= body[0].parent;
    const group = new THREE.Group(); group.name = 'LOD' + li;
    const b = mergeSkinned(body, toon); b.name = 'riderBody'; group.add(b);
    if (opts.outline !== false) { const ol = new THREE.SkinnedMesh(b.geometry, outlineMat); ol.bind(b.skeleton, b.bindMatrix); ol.renderOrder = -1; ol.frustumCulled = false; ol.name = 'riderOutline'; group.add(ol); }
    if (glow.length) { const g = mergeSkinned(glow, glowMat); g.name = 'riderGlow'; group.add(g); }
    for (const o of [...body, ...glow]) { o.parent.remove(o); o.geometry.dispose(); }
    lod.addLevel(group, dists[+li] ?? 60 * +li);
  }
  host.add(lod);
  // VR: additive sprites on glow anchors instead of bloom
  const sprites = [];
  if (opts.vr) {
    shared.glow.value = 1.0;
    for (const p of glowPts) {
      const slot = /halo|visor|eyes/.test(p.name) ? 'glow2' : 'wheelGlow';
      const sm = new THREE.SpriteMaterial({ map: glowTexture(), color: c[slot], blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, opacity: 0.7 });
      const s = new THREE.Sprite(sm); const size = p.userData.glowSize ?? 0.12; s.scale.setScalar(size); s.userData.base = size; p.add(s); sprites.push(s);
    }
  }
  const worldLight = new THREE.Vector3(0.5, 1.0, 0.6).normalize();
  Object.assign(root.userData, {
    crew: opts.crewName, colors: c, shared, lod, attachments: att, sprites, vr: !!opts.vr,
    expressions: [],
    setExpression: (name, w = 1) => { root.traverse((o) => { if (o.name === 'riderBody' && o.userData.expr) o.userData.expr.set(name, w); }); },
    clearExpressions: () => { root.traverse((o) => { if (o.name === 'riderBody' && o.userData.expr) for (const n of o.userData.expr.names) o.userData.expr.set(n, 0); }); },
    setLightDir: (v) => worldLight.copy(v).normalize(),
    setColor: (slot, hex) => { const k = ROLES[slot] ?? slot; const i = SLOTS.indexOf(k); if (i >= 0) shared.slots.uSlotColor.value[i].set(hex); },
    update: (camera, dt = 0, boost = 0) => {
      shared.lightDirV.value.copy(worldLight).transformDirection(camera.matrixWorldInverse);
      if (opts.vr) { for (const s of sprites) { s.material.opacity = 0.55 + 0.45 * boost; s.scale.setScalar(s.userData.base * (1 + 0.6 * boost)); } }
      else shared.glow.value = 1.3 + boost * 4.0;   // bloom picks this up on desktop
    },
  });
  root.traverse((o) => { if (o.name === 'riderBody' && o.userData.expr) root.userData.expressions = o.userData.expr.names; });
  scene.add(root);
  return root;
}

export function loadRider(scene, url, crewColors = {}, opts = {}) { return build(scene, url, crewColors, opts, false); }
export function loadRiderFP(scene, url, crewColors = {}, opts = {}) { return build(scene, url, crewColors, { ...opts, lodDistances: [0] }, true); }
