# Rider style opt3 (stylized realistic): Rydah Forge, 2026-11-05
Files: `rider_style.js` (runtime module), `patch_rider_style.py` (inlines it before `// ===== LOOP =====`). No edits to Rigger's ikki_skate.js, riders.js, jackets.js or wardrobe.js.

## Flags
- `?riderstyle=opt3`: opt3 on. **Default is off** (`RIDER_STYLE_DEFAULT='old'`).
- To make opt3 the default, set `window.RIDER_STYLE_DEFAULT='opt3'` before the module runs (or change `DEF` in rider_style.js). After that, `?riderstyle=old` reverts. Not flipped yet.

## What changed (opt3 only)
- **Env:** riders use pbr_world's shared PMREM, `PBR_WORLD.ENV[ENV.cur||'night']`, and replace ikkiEnv(). The env is set before the first compile, so no cube-variant program gets built. Materials are pushed into `PBR_WORLD.mats`, so pbr_world's tick swaps day/night. The module also re-checks every frame, which covers the async load. Everything is guarded by `PBR_WORLD&&PBR_WORLD.on`; without PBR it falls back to the original material. No new PMREMGenerator.
- **Colour:** albedo `map.encoding=sRGBEncoding` on body, skate and crew together. This fixes ikki_skate's forced Linear at runtime. Rider shaders add `LinearTosRGB` after tonemapping because the game output is still Linear (Palma's world isn't touched). ACES comes from `renderer.toneMapping` (pbr_world), `toneMapped=true`, so the XR path with no composer is the same.
- **Shading:** fresnel rim on the geometric normal in the crew colour, capped at ≤ .25. Anime hair/metal spec band, capped at ≤ .3. Cool shadow tint and skin warmth. Rim+spec is scaled so the lit rider stays ≤ .70 linear = **.85 display luma** (under the FXBLOOM hot band). The rim is additive and capped, so Kogarasumaru red doesn't go white.
- **Crew NPCs:** rider-toon-r128 is rebuilt as MeshStandard with the same slot recolour. The inverted hull is hidden and disposed (3 → 2 draws each). The old toon/outline materials are disposed so their programs are released.
- **Programs:** fixed keys `rider-opt3|<orig key>` and `rider-opt3|crew`. Per-rider colours are uniforms only.
- **Quest:** `tier=quest` drops normalMap (albedo + ORM only, noNormal).

## Gate (perf/render-style/rider_style_opt3_gate.py, 11:33 CST, headless quest tier)
| | base | opt3 | limit | |
|---|---|---|---|---|
| draws | 73 | 72 | +0 | PASS |
| programs | 74 | 75 | +2 | PASS |
| tex MB | 84.06 | 84.06 | +2 | PASS |
| frame ms med | 460 | 281.7 | +5% | PASS (noisy: box under load, another bot was running Chromium) |
| errors | 0 | 0 | none new | PASS |
First gate run (10:24) FAILED programs (+21). That was caused by the `renderer.compile(scene)` prewarm compiling world/FX programs, plus the old toon/outline programs never being released. Both are fixed. A real Quest 3 72 fps check is still owed.

## Build hook
`python3 patch_rider_style.py   # Rydah Forge: opt3 rider shading, OPT-IN ?riderstyle=opt3` goes after `python3 patch_pbr_base.py` and before `patch_xr_fxmem.py` in build_ikki.sh. It must come after the RIDERS/ikki_skate/pbr_world patches. It anchors on `// ===== LOOP =====`.
