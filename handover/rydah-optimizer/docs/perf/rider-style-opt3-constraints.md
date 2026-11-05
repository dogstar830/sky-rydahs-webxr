# Rider style opt3 (stylized realistic): constraints for Rydah Forge
Rydah Optimizer, 2026-10-30 23:45 CDT. Read-only audit of the sources and the built html. Nothing was edited, built, or shot. Oliver's ruling: option 3, stylized realistic, no cel and no outline.

## Current state (what opt3 replaces)
- **Player and loadIkki riders** (ikki_skate/ikki_skate.js:330, used by wardrobe riders through patch_wardrobe.py): 1 MeshStandardMaterial per LOD, cache key `ikki-pbr-v3`, ORM-driven roughness/metal with cloth/skin/shell overrides, and a rim added to emissive. **envMap = ikkiEnv()**, a canvas CubeTexture that is not PMREM (the comment says PMREM blew out under swiftshader). The rider is not on pbr_world's env and does not get the day/night swap. All maps are forced to `LinearEncoding`, albedo included. That is the display-referred workflow with outputEncoding Linear. Wardrobe sets `noNormal:true` for Caali (`caali-g.nonormal.glb` on quest) and for WITHHELD_CHAR. `envI` is .6 / .9. The outline only appears with `?ikkiOutline=1`. Contact uses 1 blob/wheel-pool decal quad per rider. There are no shadow maps in the build.
- **Wardrobe live items** (wardrobe.js:29): MeshStandardMaterial, `envMap:mat.envMap`, envMapIntensity 1.1. They inherit whatever the body uses.
- **AT skate** (jackets.js:79): MeshStandardMaterial with ikkiEnv, envMapIntensity 1.1, normal+MR maps, cache key `crew-at-skate-m1-v2hub`, one shared program across clones.
- **Crew NPCs** (riders.js): **MeshToonMaterial + inverted-hull outline + glow = 3 draws per rider** (`rider-toon-r128`). This is the main cel holdover.
- **World** (pbr_world.js, Palma, DEFAULT ON): PMREM from `env_portside_{day,night}.png`, ACES, per-day exposure, and an env swap over `PBR_WORLD.mats`.

## 1. Env map / PMREM
- Use `PBR_WORLD.ENV[PBR_WORLD.ENV.cur||'night']` and push every rider material into `PBR_WORLD.mats` so tick() swaps day/night. **Do not create a PMREMGenerator per rider or per material.** Fall back to ikkiEnv() only when `!PBR_WORLD.on` or ENV isn't loaded yet.
- Source: a **generated** PMREM, not KTX2. The input is a 6x1 PNG strip with 128 px faces (768x128). r128 PMREM output is a cubeUV RGBE8 target of about 768x1024 (≈3 MB per env, so day+night ≈ 6 MB of GPU memory). This is already paid by the world, so sharing it costs riders +0 MB. Confirm it with the gate's texture count.
- Do the swiftshader blow-out check on the hd headless shot. It is the reason ikkiEnv exists.

## 2. Shader variants
- Give one fixed `customProgramCacheKey` per feature set (e.g. `rider-opt3-body-{q|hd}`, `rider-opt3-skate-{q|hd}`, `rider-opt3-crew-{q|hd}`) and put per-rider colours in uniforms only (the jackets.js clone pattern). No tier, rider or crew data in the key or in #defines.
- Expected programs per running tier: body 1 + skate 1 + crew 1 = **3**, replacing ikki-pbr-v3 + crew-at-skate + rider-toon + rider-outline + rider-glow (glow stays). Net change should be ≤ 0. Gate limit: **+2**. normalMap on/off is a real three.js variant, so the quest/hd split must not mix in one session.

## 3. noNormal on quest
- Keep `noNormal` (no normalMap, no tangents) on quest. Normals stay on for hd only.
- The rim must use the **geometric** normal (`normal` before normal_fragment_maps, or vNormal). It must not depend on the perturbed normal. That way quest and hd silhouettes match and normal-map noise doesn't sparkle the rim in VR. Compute the fresnel once and reuse it for the hair spec.

## 4. KTX2 and colour encoding
- The r128 KTX2Loader does not set encoding. The caller must set `albedo.encoding` explicitly, as jackets.js:77 does (`t.encoding=enc`, sRGB albedo, Linear MR/normal). The reference is the gate rule in `patch_draco.py.ktx2-candidate` (SR_KTX2: quest tier unless `?ktx2=0`, or `?ktx2=1`). Mirror WARDROBE_TIER and don't fork it.
- Pick one convention and apply it to body, skate and crew together. If you switch albedo to sRGBEncoding, outputEncoding has to move with it (Palma's call). Otherwise keep Linear and colour-grade in the slots. Mixing the two shifts hue between the body and the skate.

## 5. ACES vs FXBLOOM
- The composer renders to an 8-bit offscreen target where renderer tone mapping isn't applied. The high-pass in patch_xr_fxmem.py uses `uFxbHot=(.88,.97,.97,1.0)`: luma hot band .88–.97, and the saturated test passes at .97 with sat > .6. pbr_world also raises the threshold by +.3·day.
- Cap rim+spec contribution so the lit rider stays below **.85 luma** pre-tonemap: rim ≤ .25 × rimColor, hair spec ≤ .3, `min(rim, .85-luma)`. Only the skate neon (atGm) may bloom, as it does today. Check this at night, when the threshold is lowest.

## 6. XR path
- The composer is freed in XR (XRFXMEM v2), so the XR frame is renderer → framebuffer with `renderer.toneMapping` = ACES (set by pbr_world tick). Don't do tone mapping in-shader, and don't rely on composer passes for the rider look. Desktop with the composer and XR without it should look the same apart from bloom.

## 7. Per-tier limits
| | quest | hd |
|---|---|---|
| samplers/rider mat | albedo + ORM (+ env) only, no normal, no extra LUT/ramp | + normal |
| shadows | no shadow-map receive/cast on riders (world has none). Keep the existing blob decal (1 draw/rider) | same, blob. Shadow maps would only come with a world decision |
| draws | characters + FX ≤ 40. Same material count per rider (body 1/LOD, skate 1, blob 1). Crew drops the outline, so 3 → 2 draws | same |
| tris | player LOD0 100–120k, NPC ≤ 30k (unchanged) | hd GLB |
| tex | +0 MB (shared PMREM), ~256 MB total, KTX2 default | — |
| shader | ~+10 ALU/fragment (fresnel, wrap, cap). No loops added. Drop the riders.js 11-slot loop if possible | same + normal map |
