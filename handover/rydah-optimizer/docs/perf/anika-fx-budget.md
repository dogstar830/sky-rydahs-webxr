# Anika Quest budget + light-trail / pole-grind vortex FX plan + 22 off-scene textures
Rydah Optimizer, 2026-10-30 ~01:30 CDT. **Every number here is a static estimate. No headset or browser was used and no tests were run.** Read-only on everyone's files; this doc is the only new file.
Inputs: Oliver's ref1/ref2/ref3 + README (skyrydahs-ref/characters/caali-anika-2026-10-30/), lod-budgets.md ("PBR rider budget on Quest"), texmem/audit.md §5, airgear-render-style.md §5/§8, quest_pipeline.py, riders.js, grind.js, wallatk.js, turf_dash.js, POLEGRIND_NOTES.md (Systems).

## 0. What the refs show
- **ref2 (day, clean):** Anika: long blonde braided pigtails (to mid-chest), pink cropped sailor top with red neckerchief + GR8YZONE patch, pink pleated mini skirt with gold trim + hanging gold chain, white thigh-highs with pink bows. Caali G per README. **Both on the standard black-shell A·T skate with gold accents and gold wheels**, so the shared skate fits Oliver's rule. Anika's crew identity = colours (pink/gold) + add-ons only; no custom skate.
- **ref1 (night FX):** every wheel is a glowing disc (gold core, pink/cyan/violet fringe) with **light trails streaming back from the wheels** in thin, wispy multi-colour ribbons, plus sparks and road debris kicked up at speed. The trails are short (about 1-2 body lengths), bright in the core and fading toward the tail.
- **ref3 (pole grind):** Anika on top of the pole crossarm with glowing wheel rings. Caali climbing the pole. A **double-helix light ribbon spirals up the pole** (orange/white core, violet + electric-blue fringe), about 3-4 turns over the visible height, with radius about 0.6-0.9 m around a ~0.3 m pole, plus floating rock debris and sparks.

## 1. Anika budget (player-capable and NPC)
Shares the standard rig/skeleton and the one shared skate (`at-skate-meshy.merged.glb`, its Quest copy `at-skate-meshy.merged.quest.glb` 121 KB). Body = **one material, one atlas** (skin + sailor outfit + hair + socks + add-ons, all in one), so the body is 1 draw.

| | Player (LOD0/1/2) | NPC (LOD0/1/2) |
|---|---|---|
| tris body (no skate) | **~100k** / 34k / 11k | **~25k** / 12k / 5k |
| + shared skate pair | +~6.8k (2×3.4k), merged, shared material | same (LOD2: skate baked into the body atlas, or dropped to a 0.8k proxy) |
| total LOD0 | **~107k** (inside 100-120k) | **~≤30k incl. skate (hard cap: body ≤ 23k if the skate pair counts)** |
| switch distances | 0 / 9 m / 24 m (as Ikki/Caali player) | 0 / 14 m / 32 m (riders.js default) |
| draws | LOD0 **2** (body + shared skate); LOD1/2 **1** (skate merged into the atlas) | LOD0 2, LOD1/2 1 |
| materials | 1 body MeshStandardMaterial (+ the shared A·T material) | same, 1K atlas |
| bones | standard rig (shared skeleton, same bone names as Caali G) **+ ~14 secondary**: 2 pigtails × 4 = 8, skirt 6 (front, back, 2 sides, 2 diagonals × 1 joint) | same skeleton. Pigtail/skirt chains are simulated only at LOD0 within 14 m, frozen to the rest pose beyond |
| morphs | **none** (no face morphs; any expression via a bone or the atlas) | none |
| textures | 2K colour (ETC1S sRGB) + 1K normal (UASTC+zstd, linear) + 1K ORM (R=AO G=rough B=metal, ETC1S q≥128), per audit §5 | 1K / 1K / 1K (or reuse the player atlas when she is the same asset; then 0 MB extra) |
| GPU tex MB (KTX2 on Quest) | ~**5.6 MB** (2K ≈ 2.8-5.6 + normal 1.4 + ORM 0.7-1.4) | ~**3 MB** |
| GPU tex MB if PNG/WebP (fallback) | ~33.6 MB (2K RGBA8+mips 22.4 + 2×5.6) | ~16.8 MB |
| GLB on disk | **≤ 4 MB** (Draco + KTX2); ≤ 5.5 MB WebP | **≤ 1.5 MB** |

**Pigtails/skirt, cheap:** bone chains with a per-bone damped spring (verlet or a critically damped follow of the parent's previous-frame world position, gravity + Ride velocity as an inertial offset), ~22 joints of math per frame ≈ <0.02 ms CPU. Skirt: 6 single-joint flaps with a spring toward rest plus a capsule-vs-thigh clamp (just clamp the angle, no collision mesh). Pigtails: limit the swing cone (~60°) and do a sphere-vs-head/shoulder push-out on the root 2 bones. **No cloth sim, no morph targets, no physics engine.** Same skinning cost, no extra draws. Freeze the chains beyond 14 m and in LOD1/2 bake them into the body (LOD1 keeps 1 joint per chain, LOD2 none).

Texture memory impact: +5.6 MB (player) or +3 MB (NPC) against the ~74 MB post-KTX2 target. That's fine. On the current ~324 MB pre-KTX2 path she adds ~34 MB, which pushes it further over 256 MB, so **ship her KTX2-only on Quest** (or after step 4 lands).

## 2. Updated characters+FX 40-draw table (Quest, multiview assumed)
Scenario: player + 8 NPCs + Anika as a 9th rider on screen (worst case), LOD0 rank cap 3 NPCs + Anika near.

| item | draws |
|---|---|
| FX fixed set (trails, particles, stretched, shield, popups, spare) | 6 |
| pole-grind vortex | **0 extra**: uses the spare slot #6 (it's 1 draw if the spare is already used by an Ultimate flash) |
| player LOD0 (skin + cloth + shared skate) | 3 (2 if Anika is the player) |
| 3 NPCs at LOD0 × 3 | 9 |
| **Anika LOD0 (body atlas + shared skate)** | **2** |
| 5 NPCs at LOD1/2 × 1 | 5 |
| shadows (player proxy + NPC blob InstancedMesh) | 2 |
| **subtotal** | **27** |
| inverted-hull outlines (player + 3 NPC + Anika), only if kept | +5 → **32** |
| worst: spare slot already used, so vortex +1 | **33** |

**40 is not at risk** (7 spare with outlines). It is at risk if: (a) the existing trail implementations stay separate (see §3: grind.js trail, turf_dash streak ribbons and the wallatk FXB mesh are 3 different meshes, so up to +2 over the "1 trail draw" plan), (b) Anika gets a separate skin material (+1 each LOD0) or her hair/skirt are separate meshes (+1-2), (c) the LOD0 rank cap is lifted. **Cut order:** outlines (−5), then merge the trail meshes into one, then drop Anika to the LOD0 rank queue (she counts as one of the 3 LOD0 NPCs, −2 net), then NPC trails beyond 15 m.

Note: if WebXR multiview is not active (r128 has no multiview, and Quest Browser support for `OCULUS_multiview` through three.js isn't guaranteed), every draw runs twice per frame: draws per eye stay at 27-33, but the per-frame submits double to 54-66 and CPU draw cost doubles. The 40 is a per-eye count.

## 3. FX: what exists already (reuse first)
- **grind.js** (Rydah Systems): grind trail = 1 ribbon (TN=28 pairs, vertexColors, AdditiveBlending, depthWrite off, DoubleSide); sparks = 1 pooled Points (160); "vortex focus" = **a full-screen clip-space quad** (radial streaks + tunnel vignette, depthTest off). ⚠ This is a full-screen additive layer per eye whenever speed > 7 (not only while grinding: ×0.45 off-grind). On Quest that's about 0.3-0.5 ms of fill at full res, and it is not the ref3 look. Recommend: XR keeps it off or at ≤ 0.3 alpha, with a centre cut-out (discard where the vignette weight < 0.05 so only the outer ring is shaded).
- **wallatk.js** (Systems): `fxRibbon()` writes every ribbon/arc/spiral into **one pooled dynamic mesh (FXB)**, with camera-facing ribbons and a `spiral` shape for Rebirth Spiral. The wall-ride trail already uses it. **This is the right home for the wheel trails** and the cheapest reuse: 0 new draws.
- **turf_dash.js**: crew streak ribbons (DASH.trail, its own mesh, history buffer) plus a post DashShader pass (desktop only, off in XR, good).
- So there are 3 ribbon meshes today. Plan target: 1 (FXB).

## 4a. Wheel light-trail ribbons
**Recommendation:** one preallocated ring-buffer ribbon BufferGeometry holding all player wheel trails (2 skates × 1 trail each from the rear wheel centre; per wheel is 8 trails and looks noisy, and ref1 reads as one stream per skate with a wide fringe). Either inside the FXB pool or as a dedicated `TRAILS` mesh that also absorbs grind.js and turf_dash ribbons.
- Geometry: per trail 24 segments × 2 verts = 48 verts. Player 2 trails = 96 verts / 92 tris. NPCs within **12 m**: up to 4 more riders × 2 = 384 verts more. Cap 8 trails (the render-style §5 cap) → ≤ 384 verts / ~370 tris. Stereo doubles vertex work (~770 vert invocations); trivial.
- Material: unlit additive ShaderMaterial, `depthWrite:false`, `transparent:true`, no texture (gradient across the width is analytic: `1-abs(v*2-1)` with a hot core). Colour from a per-vertex attribute (gold core → pink/cyan/violet fringe: lerp by `v` and a crew tint uniform). Alpha = (1 − age/life)². Width tapers to 0 at the tail.
- Fill: thin (≤ 6 cm wide at the head, mostly near the ground, behind the player in first person). Expected ≤ 1-2 layers over ~2-4% of the screen → ~0.05-0.1 ms. Main risk is third-person/spectator when the camera is right behind and low: cap the width by camera distance (`w *= clamp(dist/2.0,0.4,1)`).
- **Draws: 1 for all trails** (0 if folded into FXB).
- **Fallback tier:** (T1) 2 player trails only, 12 segments, no NPC trails; (T0) no ribbons, just emissive wheel colour on the shared A·T material (0 draws).

```js
// r128. One mesh for up to MAXT trails, ring buffer per trail, positions rewritten each frame.
const SEG=24, MAXT=8, V=MAXT*SEG*2;
const tg=new THREE.BufferGeometry(), pos=new Float32Array(V*3), aux=new Float32Array(V*2); // aux: age01, side
tg.setAttribute('position',new THREE.BufferAttribute(pos,3).setUsage(THREE.DynamicDrawUsage));
tg.setAttribute('aux',new THREE.BufferAttribute(aux,2).setUsage(THREE.DynamicDrawUsage));
const idx=[]; for(let t=0;t<MAXT;t++) for(let i=0;i<SEG-1;i++){ const a=(t*SEG+i)*2; idx.push(a,a+1,a+2, a+1,a+3,a+2); }
tg.setIndex(idx); tg.setDrawRange(0,0);
const trailMat=new THREE.ShaderMaterial({ transparent:true, depthWrite:false, blending:THREE.AdditiveBlending, side:THREE.DoubleSide,
  uniforms:{ uCore:{value:new THREE.Color(0xffd27a)}, uFringe:{value:new THREE.Color(0xff4fd8)} },
  vertexShader:`attribute vec2 aux; varying vec2 vA; void main(){ vA=aux; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }`,
  fragmentShader:`uniform vec3 uCore,uFringe; varying vec2 vA; void main(){ float x=1.-abs(vA.y*2.-1.), a=(1.-vA.x); a*=a;
    vec3 c=mix(uFringe,uCore,smoothstep(.4,1.,x)); gl_FragColor=vec4(c*x*a,1.); }` });
const trails=new THREE.Mesh(tg,trailMat); trails.frustumCulled=false; trails.renderOrder=9000; trails.userData.noMerge=true;
// per frame: for each live trail, push head (wheel world pos ± side*width along cross(vel,camDir)), write SEG pairs oldest->newest
// into pos/aux, then pos attr.needsUpdate=true; aux attr.needsUpdate=true; tg.setDrawRange(0,liveTrails*(SEG-1)*6);
```
CPU: ≤ 384 verts written per frame, ~0.02 ms. Upload ~6 KB/frame.

## 4b. Pole-grind spiral vortex
**Recommendation:** static double-helix ribbon mesh built once (r128 BufferGeometry), animated fully in the vertex shader: a `uT` time uniform scrolls the light along the strand (UV.x), `uTwist` spins it around the pole axis, and `uLen` cuts the visible length (alpha-cut window that grows from the rider's feet). Placed at the pole base when `GRIND.on && kind==='pole'`, scaled to the pole height, `uSpeed` from Ride.speed. Hidden otherwise.
- Geometry: 2 strands × 96 segments × 2 verts = **384 verts / 380 tris**. Radius 0.7 m, 3.5 turns over a unit height (scaled per pole), width 6-10 cm (plus a 2nd thinner bright core via the same strand's `v`, no extra geometry).
- **Draws: 1** (the spare FX slot #6), shown only while pole-grinding.
- Fill risk: the helix wraps the pole and the camera often sits close to the pole in XR, so both near and far strands overlap the view. Keep it thin, use `uLen` to show only ~1.5 turns (the 2-3 m band around the rider, ref3's brightest part), and fade with distance from the rider. Expected ≤ 2 additive layers over ≤ 8-10% of the screen ≈ **0.1-0.2 ms**. **Do not** use a full tube or a volumetric cylinder (a cylinder shell = 100% of the pole silhouette as 2 layers).
- Reuse: debris = the existing particle instancer (slot #2, grey rock cell), sparks = grind.js Points. 0 extra draws.
- **Fallback tier:** (T1) 1 strand, 48 segments, 1 turn; (T0) skip the helix and just tint the existing grind trail and sparks violet/orange (0 extra draws). In XR also keep grind.js's full-screen vortex-focus quad off while the helix shows (they would stack fill).

```js
// r128 static double helix: u = along strand 0..1, v = across 0..1, s = strand phase
function helixGeo(turns=3.5, segs=96){ const P=[],U=[],I=[]; for(let s=0;s<2;s++) for(let i=0;i<=segs;i++){ const u=i/segs;
  for(const v of [0,1]){ P.push(u,v,s); U.push(u,v); } }
  for(let s=0;s<2;s++) for(let i=0;i<segs;i++){ const a=(s*(segs+1)+i)*2; I.push(a,a+1,a+2, a+1,a+3,a+2); }
  const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.Float32BufferAttribute(P,3)); g.setIndex(I); return g; }
const vortexMat=new THREE.ShaderMaterial({ transparent:true, depthWrite:false, blending:THREE.AdditiveBlending, side:THREE.DoubleSide,
  uniforms:{ uT:{value:0}, uR:{value:.7}, uH:{value:6}, uTurns:{value:3.5}, uW:{value:.08}, uHead:{value:.5}, uLen:{value:.35}, uK:{value:0} },
  vertexShader:`uniform float uT,uR,uH,uTurns,uW; varying vec2 vUv; varying float vS;
    void main(){ float u=position.x, v=position.y, s=position.z; vUv=vec2(u,v); vS=s;
      float a=6.2832*(u*uTurns+s*.5)+uT*2.5;                   // twist + strand offset
      vec3 c=vec3(cos(a)*uR, u*uH, sin(a)*uR);
      vec3 n=normalize(vec3(cos(a),0.,sin(a)));               // ribbon faces outward-ish; widen along pole axis
      vec3 p=c+vec3(0.,(v-.5)*uW,0.)+n*(v-.5)*uW*.5;
      gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.); }`,
  fragmentShader:`uniform float uT,uHead,uLen,uK; varying vec2 vUv; varying float vS;
    void main(){ float d=abs(vUv.x-uHead); if(d>uLen) discard;      // short alpha-cut window around the rider
      float w=1.-abs(vUv.y*2.-1.), streak=.6+.4*sin(vUv.x*80.-uT*20.);
      float a=uK*(1.-d/uLen)*w*streak;
      vec3 core=vec3(1.,.8,.5), fr=mix(vec3(.6,.3,1.),vec3(.3,.6,1.),vS);
      gl_FragColor=vec4(mix(fr,core,w*w)*a,1.); }` });
const vortex=new THREE.Mesh(helixGeo(),vortexMat); vortex.visible=false; vortex.renderOrder=9001; vortex.frustumCulled=false;
// on pole grind: vortex.position.copy(poleBase); uH=poleHeight; uHead=(riderY-baseY)/poleHeight; uK→1 (ease), uT+=dt*(.5+speed/10)
```

## 5. XR notes
- Stereo: vertex work ×2 (trails ~770 + helix ~770 vert invocations, negligible); fragment/fill ×2 eyes, which is the real cost; draws are the same per eye.
- Multiview: three r128 does not implement OVR_multiview2 for WebXR, and Quest Browser support via three.js isn't guaranteed. Without it, each draw is submitted twice (CPU). The +1-2 FX draws are fine either way.
- No camera roll from the helix. Both FX are world-space meshes (not clip-space), so they are per-eye correct. Avoid adding more full-screen clip-space quads in XR.
- Total FX budget with both: trails 0.05-0.1 ms + helix 0.1-0.2 ms, inside the ≈1 ms FX cap (render-style §8), ≤ 6 FX draws.

## 6. Pipeline recipe (when Forge's Meshy GLB arrives)
Dry run first, never overwrite the input. Input must be rigged on the standard skeleton by Rigger, skates stripped (shared skate attaches at runtime), POSITION float (no quantized POSITION; `_WC` same format).
```bash
cd /workspace/v3build
# player tier (Quest): LOD0 ~100k body, 2K colour / 1K normal+ORM, face crisp, Draco, KTX2 sibling
python3 tools/quest_pipeline.py /workspace/skyrydahs-characters/wardrobe/riders/anika.glb \
  --out-dir /workspace/skyrydahs-characters/wardrobe/riders/quest --geometry draco \
  --max-base 2048 --max-normal 1024 --max-orm 1024 --keep-crisp 'face|head' --crisp-max 2048 \
  --simplify 100000 --ktx2 --dry-run          # then rerun without --dry-run
# NPC tier: 1K everything, ~23k body tris (≤30k with the skate pair)
python3 tools/quest_pipeline.py <anika-lod-source>.glb --out-dir /workspace/skyrydahs-characters/wardrobe/riders/quest-npc \
  --geometry draco --max-base 1024 --max-normal 1024 --max-orm 1024 --keep-crisp 'face' --crisp-max 1024 \
  --simplify 23000 --ktx2 --suffix quest2 --dry-run
python3 tools/glb_inspect.py <out>.quest.glb   # check: 1 body material, tris, POSITION float, no KHR_mesh_quantization on POSITION
python3 tools/lod_report.py                    # refresh lod-budgets.md row
```
The exact input path/name is whatever Forge/Rigger deliver. LOD1/LOD2 meshes (`_LOD1_`, `_LOD2_` names as riders.js expects) come from Forge/Rigger; `--simplify` only targets LOD0. Gates for the integrator: rider bodyshots, perf_overlay.py, drawcall_budget.py, smoke CORE.

## 7. The 22 off-scene textures (overlay 79 vs renderer.info.memory.textures 101)
Static read of sky-rydahs-v3-ikki.html (17:59 build). r128 counts every render target's colour texture and any DepthTexture in `info.memory.textures`. Sizes assume a 1920×1080 desktop canvas (the Quest XR framebuffer is separate, and these RTs are still allocated even though the composer is skipped in XR).

| # | candidate | count | est. MB | evidence |
|---|---|---|---|---|
| 1 | EffectComposer renderTarget1/2 (RGBA8, full res) | 2 | ~16.6 | html:270 `setupFX` |
| 2 | DepthTexture on both composer RTs (UnsignedInt) | 2 | ~16.6 | html:270 `rt.depthTexture=new THREE.DepthTexture()` |
| 3 | UnrealBloomPass (res W/2: bright RT + 5 mips × H/V blur RTs) | 11 | ~1.9 | html:274 |
| 4 | PMREM cubeUV output kept as KIT.env (768×1024 RGBE) | 1 | ~3.1 | html:5573 `fromScene(sc,.02)`; generator disposed, output kept (intended) |
| 5 | Sign originals swapped for pre-baked/resized pages (`it.sw` replaces `it.t`, original not disposed) | ~2-4 | ~4-16 | html:4180; audit §4 "dispose sign originals" |
| 6 | Cached canvas/data textures no longer on a visible material: `tagTexs[]` cache (434), rider `rGrad` DataTextures per call (536), MM2 alphaMap/dot sprite (5121/5124), JACKET.atlas (2838), UI.tex/FPSO.tex (XR-only HUD, hidden) | ~2-4 | ~1-6 | not reachable via scene traverse while hidden/unattached |
| **total** | | **~20-24** | **~43-60 MB** (of which ~38 MB = composer + bloom, desktop only) |

Items 1-3 (15 textures) almost certainly account for most of the gap. Fixes for owners (proposals, not edits): in XR, `cmp.renderTarget1/2.dispose()` + bloom `dispose()` on sessionstart, recreating on end (saves ~35 MB on Quest if they're allocated at the browser canvas size); drop the depthTextures if the EdgeShader doesn't need them in the current look; dispose the sign originals after swap; cache `rGrad` per tone count. Verify with a `renderer.info.memory.textures` diff before/after each, which the integrator runs.

## 8. Who does what
- **Rydah Forge:** Anika mesh (one atlas, body ~100k / NPC ~23k, LOD1/2, no skate, add-ons: neckerchief, GR8YZONE patch, skirt chain, sock bows in the atlas).
- **Rydah Rigger:** standard skeleton + 8 pigtail + 6 skirt bones, spring-chain update (LOD0 ≤ 14 m), shared skate attach, `_LODn_` naming; runs the pipeline recipe.
- **Rydah Systems (grind.js / wallatk.js owner):** the pole helix (spare FX slot) per POLEGRIND_NOTES; fold the grind trail + wheel trails into the FXB pool; XR cap on the full-screen vortex-focus quad.
- **Ani's FX owner / turf_dash owner:** fold the DASH streak ribbons into the same pool. Integrator: gate runs (drawcall_budget, perf_overlay, bodyshots).
- **Me:** re-run lod_report once the GLB exists and verify the texture count after the disposals.
