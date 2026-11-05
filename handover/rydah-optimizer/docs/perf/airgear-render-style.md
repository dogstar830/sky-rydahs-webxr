# Air Gear character render style on Quest: outlines, ramp, cost
Rydah Optimizer, 2026-10-29 04:45 CDT. Research and plan only. No game files were edited.

## 1. Canon visual traits (each one cited)
- **Manga (Oh!Great): a hard light/dark split.** He says every panel pairs a very detailed area with an empty one, and "I don't just show the lit part, I always add the dark part... a game of light and shadow." For rendering, that means big flat black shadow shapes next to clean lit areas, not soft gradients. https://www.crunchyroll.com/zh-tw/news/interviews/2025/8/17/manga-author-oh-great-interview
- **Precise, dense linework and correct anatomy**: "clean, cold beauty", strong control of body proportions, dynamic panels, and 1–2 page spreads used as slow-motion beats. https://www.animenewsnetwork.com/review/air-gear/gn-2
- **Motion is shown by contrast.** If the shoulders move, the hips hold still (same interview). In-game, that argues for speed lines and trails on what moves and a crisp, stable silhouette on the body.
- **Screentone in manga is for pattern and pushing things back. Ink does the shading.** https://ogiuemaniax.com/2010/01/31/oel-screentone-revelations/ So shadows should be solid tinted blocks, not halftone dots across the whole body.
- **Toei 2006 TV anime.** The staff interviews say the manga was too detailed for normal anime shortcuts, so backgrounds came from heavy location scouting and photo reference. CG was used for the AT mechanisms, the depth of the town, and the abstract trick spaces, including Ikki's "翼の道" (Wing Road) effect, trick perspective shots, and Buccha's tank overlay. https://www.toei-anim.co.jp/tv/airgear/interview/vol05.html and https://www.toei-anim.co.jp/tv/airgear/interview/vol06.html Takeaway: realistic world, cel characters, and Road effects as a separate CG/FX layer.
- **TV cels**: flat fills plus painted shadow lines. Traditional cels often used light, shadow and a highlight/2nd shadow, which is a 3-step transition. https://www.pioroberson.com/Journal/Cel_experiments.html The TV animation is limited, with "snapshot" timing. https://anilist.co/review/3528
- **OVA "Kuro no Hane to Nemuri no Mori – Break on the Sky" (2010–11, 3 eps).** It was made by Satelight, not Toei, with a new staff and cast: dir. Shinji Ishihira, character design Osamu Horiuchi, mecha design Stanislas Brunet, 3DCGI by Satelight. It was billed as "high-quality". https://www.satelight.co.jp/works/... (Satelight works page), https://www.animenewsnetwork.com/encyclopedia/anime.php?id=11722, https://www.animenewsnetwork.com/news/2010-07-14/air-gear-black-rock-shooter-love-live-yozakura-promos-streamed (I did not verify frame-level differences from these sources.)
- **Road FX (lore that drives visuals).** Wing Road: wind/low-pressure fronts, and the "Bagram" Regalia wheels split into spirals and unfurl into wings while the skull emblem glows. Flame Road: friction heat, heat-haze mirages, and the Kitsune Regalia wheels throw torrents of flame. Thorn Regalia belonged to Gazelle and later Rika. https://airgear28.wordpress.com/2011/02/15/roads-regalias/ (fan wiki mirror, lore only)
- **Manga vs anime.** The manga is B/W, with solid spot blacks, dense hatching and screentone patterns. The anime is colour cel work with simplified detail, flat shadows and CG-composited Road effects. The game should take hard black shadow shapes and thick silhouettes from the manga, and coloured 2–3 band cels plus glowing wheel/Road FX from the anime.
- **Still unsourced**: per-crew palettes, rim highlights in the TV cels, and the Thorn Road visual. Check these against the screenshots in skyrydahs-ref/ before relying on them.

## 2. What the build does now (sky-rydahs-v3-ikki.html, polish.js, riders.js, ikki_skate/ikki_skate.js)
- **World props (polish.js):** MeshToonMaterial with `gradMap` (NearestFilter DataTexture) plus an onBeforeCompile hard fresnel rim (`step(.62,fr)`) and hard spec. The ink is a shared `inkMat` (BackSide MeshBasic, inverted hull, scaled with distance) added as a child mesh, so each inked box is +1 draw. The merge path (`mergeKey`) excludes inkMat.
- **Crew riders (riders.js `buildRider`):** a MeshToonMaterial skinned with `rGrad(tones)`, which gives 2 steps [95,255], 3 steps [85,185,255] (the default) or 4. A slot palette selected by UV, a tinted shadow, a smoothstep fresnel rim on the shadow side, and slot emissive. There is also `rOutline` (an inverted-hull ShaderMaterial, BackSide, skinned, opaque+discard, thickness scaled by distance, fading by `uFar`) and `rGlowMat` (MeshBasic for the wheel glow). The header says **3 draws/rider (body + hull + glow), LOD 0/14/32 m**. The hull is a second SkinnedMesh on the same geometry, so the shader skins it twice.
- **Player Ikki (ikki_skate.js):** **MeshStandardMaterial PBR** (map + normal + roughness) with a comment saying "v3 locked brief: stylized realism, NOT toon". The AT panels use emissive neon driven by uBoost, and there is a fresnel rim added as emissive. The outline is off unless `?ikkiOutline=1`. LOD 0–9 m is 19.7k tris, 9–24 m is 9.1k, 24 m+ is 2.6k, with 1 draw per level.
- **Post:** EffectComposer (RenderPass → UnrealBloomPass at half res, .6/.45/.68 → Grade → dash pass), pixelRatio ≤1.25. The comment says it is **skipped in XR**. So on Quest the glow comes only from emissive and additive sprites (the ShaderMaterial additive glow sprites in polish.js).
- **Where the cost goes on Quest:** r128 WebXR renders each eye separately with no multiview, so every draw call runs twice. The player is the biggest fragment cost because it uses MeshStandard with 3 maps, a full-res fragment, and is close to the camera. Each rider costs 3 draws × 2 eyes plus double skinning. Bloom costs nothing in XR because it is off. Desktop pays for bloom at ½ res, about 5–6 fullscreen passes counting the mip chain.
- **Conflict to settle:** skyrydahs-aesthetic-brief.md says cel, 2–3 bands and thick inverted-hull ink. ikki_skate.js says "stylized realism, NOT toon". production-plan.md (row ~206) compromises with "realistic PBR world + characters on a soft 3-step ramp with a thin outline on LOD0 only; neon from emissive, no post bloom in XR". This doc follows production-plan.

## 3. Options, cost per character (Quest 3, r128, 72 fps = 13.9 ms)
Draws are per eye. renderer.info in XR shows about 2× these numbers. GPU figures are rough estimates for a rider about 3 m away covering ~8% of the eye buffer, not measured on device.

| Option | Draws/char | Vertex | Fragment | Notes |
|---|---|---|---|---|
| A. Toon ramp only (gradientMap, 2–3 steps, NearestFilter) | 1 (+1 glow) | 1× skin | ≈ Lambert, cheaper than Standard | ~0.1–0.2 ms/char. Swapping Ikki from Standard to toon likely *saves* ~0.3–0.6 ms when he is close |
| B. A + inverted hull (current riders) | 2 (+1) | 2× skin | thin shell, cheap, but overdraw at the silhouette | ~+0.1–0.25 ms/char at LOD0. The draw count is the main cost: 8 riders = +16 draws/eye |
| C. A + fresnel "ink" darkening in the same shader | 1 (+1) | 1× | +~4 ALU | ~free. It only lines silhouettes that curve away from the camera: no line on flat planes or inner contours, and it varies with normals |
| D. Post Sobel depth/normal edges | +1 fullscreen pass (plus a depth/normal prepass) | 0 | the whole eye buffer twice (~2064×2208/eye at default scale) | ~1.5–3 ms on Quest. In r128 the composer **doesn't output to the XR framebuffer** (https://github.com/mrdoob/three.js/pull/18846, https://discourse.threejs.org/t/webxr-not-working-with-effectcomposer/47761) and it breaks foveation (https://graspable.dev/blog/webxr-performance-budget-quest-3). **Reject for Quest**, possible on desktop only |
| E. Baked contour (ink lines painted in the texture or as vertex colour) | 1 | 0 | 0 | Inner lines only (seams, folds). Combine it with B or C for the silhouette |
| F. Wheel glow: emissive slot + additive trail ribbon/sprites | +1 shared instanced trail for all riders | small | additive overdraw, keep it thin | ~0.1 ms total. Replaces bloom in XR |

Spot blacks: use a hard ramp threshold. A 2-step gradientMap (e.g. [40,255], or tint to a shadow colour ~0x1a1830 for manga-black) costs the same as any ramp, 0 extra. Rim: keep the existing shadow-side fresnel rim, ~3 ALU.

## 4. Recommendation
**Quest default:**
- Player (Ikki) and all riders on the riders.js toon path. Ikki switches from MeshStandard to MeshToon with the albedo map only, dropping the normal and roughness maps. Use a **3-step ramp [60,170,255] with a NearestFilter DataTexture** and a hard low step so the darkest band reads as a manga spot black (tinted 0x1a1830 via uShadowTint).
- **Hull outline (B) on LOD0 only (<9–14 m), capped to the player plus the 3 nearest riders.** All other riders use option C, the fresnel ink in the same draw. Add a baked contour (E) for inner lines when assets are re-textured.
- Rim: keep the shadow-side fresnel. Wheel glow: emissive slot plus one instanced additive trail (F). No composer in XR.
- Budget: player 2 + glow 1, 3 near riders × 3 = 9, other riders 2 each (body + glow). For 8 riders that is ~3 + 9 + 10 = **~22 draws/eye**, versus ~27 if every rider got a hull. GPU for characters ≈ **1.0–1.5 ms**, with +1.6 ms headroom against the 150 cap.
- Enable `renderer.xr.setFoveation(1)`. It only works while rendering direct to the XR framebuffer (Meta: https://developers.meta.com/vr/documentation/web/webxr-perf-bp/).

**Desktop default:** hulls on every rider at LOD0/1 (2–3 m distance fade), the same 3-step ramp, and keep the half-res UnrealBloom. Optionally add a depth-normal Sobel pass (D) at ≤1.0 pixelRatio for inner-line manga ink, ~0.5–1 ms on a mid GPU.

**To verify (the integrator owns test runs):** renderer.info.render.calls in XR with 8 riders, and ovrgpuprofiler for fragment vs vertex bound (https://developers.meta.com/vr/documentation/web/webxr-perf-tools/). Sign-off on toon vs "NOT toon" for Ikki is needed from the brief owner/Oliver.

## Sources
Listed inline above. Also https://polyfork.dev/threejs-shaders (skinned inverted hull, gradient-map toon without a composer) and https://github.com/mrdoob/three.js/issues/20401 (OutlinePass cost).

## 5. VFX cost of canon looks on Quest (no bloom in XR)
Canon targets: the Flame Road leaves a flame trail with heat mirage, the Fang is an air shockwave, Thorns are thin wind rods, and the Bagram wheels unfurl into wings (shared ref §5 and https://airgear28.wordpress.com/2011/02/15/roads-regalias/). The TV anime composited Road and trick-space effects as a separate CG layer (https://www.toei-anim.co.jp/tv/airgear/interview/vol05.html).

| Effect | Method | Draws/eye | Budget | Est. GPU |
|---|---|---|---|---|
| Wheel glow (all riders) | emissive slot in body shader (exists) | 0 extra | — | ~0 |
| Wheel trails | ONE shared ribbon BufferGeometry, additive, depthWrite off, opaque-sorted last; build already has a ribbon (`trail={n:TN,...}` html ~2575) | 1 total | ≤ 8 trails × 24 segments (≈400 tris) | 0.1–0.2 ms |
| Flame Road | instanced camera-facing quads (InstancedMesh, 1 atlas, additive), flicker in vertex shader; "heat mirage" = skip on Quest (needs scene copy) | 1 | ≤ 96 particles, each ≤ ~1% screen | 0.2–0.4 ms |
| Thorn Road | thin instanced stretched quads/cylinders (rods) | 1 | ≤ 64 rods | 0.1–0.2 ms |
| Fang/shockwave | 1 expanding ring mesh, additive, 0.4 s | 1 | 1 per rider at once | <0.1 ms |
| Wing Road / Bagram | 2 wing-shaped ribbons from the trail system | 0–1 | form 2/3 only | 0.1 ms |
| Speed streaks (VR stand-in for speed lines) | instanced lines in world space | 1 | ≤ 48 | 0.1 ms |
**Hard cap in XR:** ≤ 6 FX draws/eye, ≤ 256 live particles + 8 trails, additive overdraw ≤ ~3 layers at screen centre, no full-screen quads. Desktop can double the particle counts and keep UnrealBloom.

## 6. Animation budget
- **Skinning runs on the GPU** in r128 (bone uniforms or bone texture), so the CPU only pays for the skeleton matrix update. Rig sizes are 19 bones for crew riders (sleeping-forest-rider*.glb) and 66 for WITHHELD_CHAR/Ikki (Mixamo, WITHHELD_CHAR-rider.quest*.glb). The crew riders are posed procedurally by `rPose` with no mixer. Ikki uses an AnimationMixer.
- CPU per rider per frame (Quest browser JS, estimate): 19-bone procedural pose plus updateMatrixWorld is ~0.02–0.04 ms. A 66-bone mixer with 2 blended clips is ~0.08–0.15 ms. The inverted hull skins a second time on the GPU only (vertex cost ×2 at LOD0).
- **Update-rate LOD:** full rate under 14 m, 1/2 rate at 14–32 m, 1/4 rate beyond 32 m. Stagger by rider index so the work doesn't all land on one frame. Freeze when off-frustum. Keep the player and the trick-target rider at full rate during tricks.
- Trim Mixamo rigs for NPC use: drop fingers to get to about 24–30 bones. That cuts the CPU cost per mixer by ~2× (verify).

### Worst-case frame: player big trick + Road FX, N = 8 riders on screen, Quest 3 @72 (13.9 ms)
| System | ms |
|---|---|
| JS game logic, physics, input | 2.0 |
| Animation (player mixer 0.15 + 3 near riders full 0.12 + 4 at ½/¼ rate 0.05) | 0.35 |
| three.js scene traversal/culling/uniforms (~150 draws ×2 eyes) | 2.0–2.5 |
| GPU: world | 5.0–6.0 |
| GPU: characters (toon + 4 hulls, recommended setup) | 1.0–1.5 |
| GPU: FX at the cap above | 0.6–1.0 |
| Headroom for browser compositor/jank | ≥1.5 |
CPU and GPU overlap, so the frame time is the larger of the two (CPU ≈ 4.5–5 ms, GPU ≈ 7–8.5 ms). This fits at 72 fps. The first knob to turn is foveation, then framebuffer scale 0.9. All figures are estimates. Measure with renderer.info and ovrgpuprofiler (https://developers.meta.com/vr/documentation/web/webxr-perf-tools/, https://graspable.dev/blog/webxr-performance-budget-quest-3).

## 7. Default rider shading is now PBR, not toon (Oliver, 2026-10-29)
Oliver's new direction is CoD / NFS Heat / GTA V-VI realism. That replaces the toon ramp + hull recommendation in §3–4 as the **default**. The toon path is kept only as a stylized option.

The rider default is now:
- `MeshStandardMaterial` with KTX2 base 2048 (face crisp) and normal/ORM 1024.
- At most 3 materials (skin / cloth-gear / shared A-T).
- The world's PMREM env map.
- A skin wrap/SSS fake via `onBeforeCompile`.
- 1 shadow caster (the player proxy) and instanced blob shadows for NPCs.

Inverted-hull outlines are optional and off by default for the realistic look.

Budgets and the math (draws, PBR vs toon ms, KTX2 vs PNG memory, LOD distances) are in `perf/lod-budgets.md` → "PBR rider budget on Quest". The Road FX below are unchanged by this. In a realistic look they read as energy/air distortion layers, which still means additive, no bloom in XR.

## 8. FX budget per Road (Quest 3 @72 fps; caps: ≤ 6 FX draws/eye, ≈1 ms FX GPU)
Source: `skyrydahs-ref/airgear-deep-reference.md`, §5 visual styling (Road visualizations, wing motifs) and §7 movement. Roads it lists:
- Wing (Ikki)
- Gale (Mikan, a Wing variant)
- Fang / Bloody (WITHHELD_CHAR/WITHHELD_CHAR)
- Flame (Kazu)
- Thorn (Sleeping Forest / Ringo)
- Rock (Buccha)
- Smell (Onigiri)

### Shared rules
- WebXR multiview, so draws per eye equal draws per frame.
- All FX are additive, depthWrite off, drawn after opaques, from **1 shared 1024 FX atlas** (KTX2 ETC1S/UASTC, about 1.4 MB).
- All animation runs in the vertex shader from per-instance attributes (spawn time, seed, velocity). The CPU only writes new instances into a ring buffer.
- `InstancedBufferAttribute.updateRange` covers just the new slots, so there's no full re-upload and no textures are uploaded per frame.
- Pools are allocated at load. Nothing is allocated in the frame loop.
- No full-screen passes or scene-copy (refraction/heat mirage) on Quest.

### Per effect
| effect | technique | max draws | max particles / verts | est. GPU ms (Quest, at cap) | CPU ms | pooling / lifetime | Quest vs desktop |
|---|---|---|---|---|---|---|---|
| **Wing Road wings** (Ikki form 2/3, plus Wheel Spin Drop) | 2 wing ribbons spawned from the trail system (strip geometry, 2×24 segments), feather-gradient atlas cell, plus ≤ 24 feather quads (InstancedMesh) on the takeoff burst | 1 (ribbons in the shared trail draw) + 1 feathers | 96 ribbon tris + 24 quads | 0.10–0.15 | 0.02 | wings persist while airborne, 1.2 s fade; feathers 0.6 s, pool 32 | desktop: 48 feathers, bloom |
| **Gale Road** air blast (kick projectile) | 1 stretched cone/cylinder mesh, scrolling noise UV, additive | 1 | 64 tris, ≤ 2 live | 0.05–0.1 | <0.01 | 0.35 s, pool 4 | desktop: + heat distortion pass |
| **Fang shockwave / Leviathan** (WITHHELD_CHAR/WITHHELD_CHAR) | 1 expanding ring (flat disc, 48 tris) + 1 vertical crescent blade quad, both scaled in the vertex shader | 1 (ring and blade share an InstancedMesh) | ≤ 4 instances live (2 riders × 2) | 0.08–0.15 (large screen coverage, keep alpha ≤ 0.5, ring width ≤ 15% radius) | <0.01 | 0.4 s, pool 8 | desktop: + screen-space distortion |
| **Bloody Road** (carve/hooks) | reuse the Fang blade plus 3 instanced "cut" streak quads on the target | 0 extra (Fang draw) | +6 instances | +0.03 | <0.01 | 0.5 s | same |
| **Flame Road trail** (Kazu, F Dash "Stealth") | instanced camera-facing quads, flipbook flame cell, flicker in VS; the trail ribbon is tinted flame | 1 | ≤ 96 particles live (each ≤ ~1% screen) | 0.2–0.35 | 0.03 | 0.5–0.8 s, ring pool 128 | desktop: 192 + heat mirage (scene copy) |
| **Thorn Road** (thin wind rods) | instanced stretched quads (billboard along the axis) | 1 | ≤ 64 rods | 0.1–0.2 | 0.02 | 0.3–0.6 s, pool 96 | desktop: 128 rods |
| **Rock Road** (Buccha, wall bump, reflecting wall) | 1 hex-tile shield plane + dust puffs reusing the Flame instancer (grey cell) | 1 shield (dust shares the particle draw) | 128 tris + ≤ 24 puffs | 0.1–0.15 | 0.01 | shield 0.8 s, pool 2 | desktop: fresnel + more puffs |
| **Smell Road** fog (Onigiri, AoE gas) | ≤ 12 big soft sprites in the shared particle instancer, soft-edge atlas cell | 0 extra (particle draw) | 12 large quads (overdraw-heavy) | 0.15–0.25 | <0.01 | 2.0 s, pool 16 | desktop: 32 sprites; Quest caps alpha at 0.35 |
| **Wheel trails** (all riders) | ONE shared ribbon BufferGeometry (exists in the build, `trail={n:TN,...}`) | 1 total | 8 trails × 24 segs ≈ 400 tris | 0.1–0.2 | 0.03 | continuous | same |
| **Trick-name popups** (HUD text) | **one pre-baked trick-name atlas** (all trick names + numbers + combo ×N, 1024×1024 KTX2, about 1.4 MB), drawn by 1 InstancedMesh of quads, UV rect per instance; world-space, head-locked offset in XR; **no DOM in XR**; a canvas-texture sprite only as a desktop fallback for player-typed strings, redrawn on change only, never per frame | 1 | pool 6 popups × ≤ 16 glyph-or-word quads = 96 instances | 0.03–0.05 | 0.01 | 1.2 s (pop 0.15 s, hold, fade), pool 6, oldest recycled | desktop: same atlas, + DOM allowed outside XR |
| Speed streaks | instanced world-space lines | 1 | ≤ 48 | 0.1 | 0.01 | continuous at > 70% speed | desktop: 96 |

**Draw pooling:** all point-like FX share **one** particle InstancedMesh: Flame, Rock dust, Smell fog, Wing feathers, Bloody cuts and Fang ring/blade, with atlas cells and blend in the shader (all additive). A 2nd instancer handles stretched rods (Thorn/Gale/streaks). That turns "1 draw per effect" into a fixed set.

### Fixed FX draw set (Quest)
| # | draw | content |
|---|---|---|
| 1 | trail ribbons | all wheel trails + Wing wings |
| 2 | particle instancer (pool 256) | Flame, Rock dust, Smell fog, Wing feathers, Fang ring/blade, Bloody cuts |
| 3 | stretched instancer (pool 128) | Thorn rods, Gale cone, speed streaks |
| 4 | Rock shield / Gale cone meshes | only while active |
| 5 | trick popups | atlas instancer |
| 6 | spare | reserved (e.g. an Ultimate pose flash) |

### Worst-case stacking (Quest)
Player Flame Road + 2 rivals (Fang + Thorn) + popup + 8 trails + streaks:

| layer | draws | live elements | GPU ms |
|---|---|---|---|
| trails (8) + no wings | 1 | 400 tris | 0.15 |
| particles: Flame 96 + Fang 2×2 instances | 1 | 100 | 0.35 + 0.15 = 0.50 |
| rods: Thorn 64 + streaks 48 | 1 | 112 | 0.20 + 0.10 = 0.30 |
| popup | 1 | ≤ 32 instances | 0.04 |
| **total** | **4 of 6** | ≤ 256 particles + 8 trails | **≈ 1.0 ms**, at the cap |

If Wing (player) and Smell fog stack on top, GPU goes to about 1.3 ms, over budget. **Adjusted caps when ≥ 3 Roads are active:**
1. Halve rival particle counts (rivals' Flame/Thorn ×0.5). That saves about 0.15 ms.
2. Draw rival Roads beyond 15 m as trail-tint only (0 particles).
3. Cap Smell fog alpha at 0.35 and make the sprites ≤ 8 when the player is inside the cloud (overdraw is the cost).

With those, the stack stays at **≤ 1.0 ms and ≤ 5 draws**.

Rule of thumb: about 0.0035 ms per small additive particle and about 0.02 ms per screen-% of large additive coverage per layer. These are estimates. Verify with ovrgpuprofiler and the `?fps` overlay at Portside with 3 Road users.
