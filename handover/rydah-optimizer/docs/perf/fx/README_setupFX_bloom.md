# setupFX bloom: PROPOSAL (not applied). Palma Builder, for Rydah Optimizer (FX owner), 2026-10-30

## Cause
- The composer's render targets are 8-bit, and r128 skips renderer tonemapping when rendering into a target. So UnrealBloomPass's high-pass sees clamped, untonemapped linear colour.
- The high-pass is a near-binary luma cut (threshold .68, smoothWidth .01). Large mid-bright, low-saturation areas just above .68 (lit window grids, white panels, garage door, bright sky) pass completely and come back at about 1.8x area gain (5 mips x radius, strength .6). They then clip to white.
- With bloom disabled, the same frame has 0.08% of pixels at or above 245, so the clipping is bloom, not the materials.

## Change (`setupFX_bloom.proposed.diff`, against `polish.js` `setupFX`)
- One block after `cmp.addPass(bloom)`. It patches only `bloom.materialHighPassFilter`, the LuminosityHighPass shader, and adds the uniform `uFxbHot`.
- A pixel feeds bloom if either:
  - its luma is at least about .88 to .97 (hot cores, lamps), or
  - its max channel is at least about .80 to .95 AND its saturation is at least about .35 to .6 (neon).
- The scene image, bloom strength, radius, colour, render targets and draw calls are all unchanged.
- If the shader anchor is missing, it warns and leaves bloom unchanged. `FX.bloomHot=true` marks that the change is active.
- Live build note: `patch_ikki_skate.py` rewrites the bloom constructor to (.6,.45,.68). The diff's anchor `cmp.addPass(bloom); cmp.addPass(new THREE.ShaderPass(GradeShader));` survives that patch, and it is checked in the built copy.

## Tested
- Built with `build_copy.sh` (`fxb_before.html`), then the block was injected into the copy (`fxb_after.html`). The shared `polish.js` and the real html are untouched (md5 checked).
- Hero standard: 1920x1080, dsf 1.5, `?tier=hd`, FX on, seed 1, 65 frames.

| street day | p95 | % >= 245 |
|---|---|---|
| `?toon=1` before | 254 | 8.98 |
| `?toon=1` after | 221 | 0.63 |
| `?pbr=1` before | 253 | 6.27 |
| `?pbr=1` after | 183 | 0.09 |

- Side-by-sides: `shots/hero/fxbloom_{toon,pbr}_street_day_side_by_side.png`.
- The neon signs (TOOL TOUL TO, crown and edge strips, cyan prop) keep their glow, with a slightly tighter halo.
- 0 page errors.
- Not yet shot: night views and the causeway (see the board).

## XR / Quest path (verified in code, `xrFxMemInit`, built line ~292)
- On `sessionstart`, `M.onStart` disposes `C.renderTarget1/2` (plus bloom targets only with `?xrfxbloom=1`), and `C.render` falls back to `renderer.render` while freed. In XR, bloom does not run at all.
- The diff touches no render target, pass list, or `xrFxMemInit`. It runs before `xrFxMemInit()` inside the same `setupFX`.
- `?tier=quest` only affects `WARDROBE_TIER` and `SR_KTX2`. `setupFX` and `loadFX` have no tier branch (`loadFX` is skipped only with `?nofx`), so behaviour is unchanged.

## Risks
- Pale, low-saturation emitters (white signage, white lamp heads below .88 luma) lose bloom. This is deliberate, but check the night views.
- `needsUpdate` triggers one extra shader compile at setup (about 1 program).
- The thresholds are tuned for 8-bit targets. If the composer moves to HalfFloat, revisit them.
- Harness caveat (not FX): the test "day" hack calls `window.FACADE.setDay(1)`, but `FACADE` is a top-level const, so in every test "day" shot the facades stayed in night mode. Nothing in the game calls `setDay`.

## Draws (fxb_after.html, world)
- `?pbr=1`: street 79, causeway 94, b98 95, aerial 95.
- `?toon=1`: street 76, causeway 91, b98 87, aerial 89.
- All within 110, 0 errors. The change adds no meshes or passes.

## Full matrix, 20:00-20:50 (fixed day harness: facades/bridges really in day mode)
- before = fxb_before.html (build_copy 18:50, no FXBLOOM)
- after = fxb_landed.html (build_copy 20:03, Optimizer's landed /*FXBLOOM*/ in patch_xr_fxmem.py; same uFxbHot .88/.97/.80/.95)
- Caveat: "after" also picks up other changes made between the builds (PBR default-on flip, other workers' pbr_world.js edits). The pbr-day before/after is therefore not pure A/B: the after sky is brighter.
| mode | view | tod | p95 before | >=245 before % | p95 after | >=245 after % |
|---|---|---|---|---|---|---|
| toon | street | day | 254 | 11.98 | 241 | 2.82 |
| toon | street | night | 188 | 1.09 | 180 | 0.77 |
| toon | causeway | day | 254 | 16.31 | 246 | 6.89 |
| toon | causeway | night | 222 | 2.4 | 210 | 0.99 |
| pbr | street | day | 186 | 0.09 | 224 | 0.15 |
| pbr | street | night | 178 | 2.0 | 166 | 0.1 |
| pbr | causeway | day | 207 | 0.12 | 223 | 0.14 |
| pbr | causeway | night | 157 | 0.17 | 155 | 0.08 |

Side-by-sides: shots/hero/fxbloom_{toon,pbr}_{street,causeway}_{day,night}_side_by_side.png. 0 page errors in all 16 shots.

Night white emitters:
- Lamp heads (white, causeway) keep a halo, slightly tighter.
- Orange street lamp and all neon are unchanged.
- The MOON loses its bloom halo (white, low-saturation); the disc itself is unchanged.
- Lit white windows bloom less.
- Toon day still clips 2.8% (street) and 6.9% (causeway) after; the source is sky/haze, not facades.

## PURE A/B gate matrix (21:40-22:15). This SUPERSEDES the 20:00 table above.
- One fresh build_copy (fxb2_after.html, landed /*FXBLOOM*/) and the same copy with that block stripped (fxb2_before.html, equivalent to .bak-opt-202610302001).
- Fixed day harness; hero standard; 0 page errors in all 16 shots.
| mode | view | tod | p95 before | >=245 before % | p95 after | >=245 after % |
|---|---|---|---|---|---|---|
| toon | street | day | 254 | 12.53 | 241 | 2.85 |
| toon | street | night | 187 | 1.07 | 179 | 0.75 |
| toon | causeway | day | 254 | 16.41 | 246 | 6.78 |
| toon | causeway | night | 222 | 2.4 | 209 | 0.99 |
| pbr | street | day | 190 | 0.1 | 224 | 0.16 |
| pbr | street | night | 174 | 1.7 | 164 | 0.1 |
| pbr | causeway | day | 207 | 0.1 | 223 | 0.13 |
| pbr | causeway | night | 157 | 0.14 | 155 | 0.08 |

Findings:
- Toon: clipping is cut everywhere (street day 12.5% -> 2.9%, causeway day 16.4% -> 6.8%). The causeway-day residue is sky haze and the white deck.
- Night: neon, orange lamps and white causeway lamp heads keep their halos (slightly tighter); the moon halo is a little smaller. White signage shows no visible loss.
- REGRESSION (pbr day): p95 goes up (street 190 -> 224, causeway 207 -> 223). The deep-blue day sky is saturated with a max channel near 1, so it passes the "saturated emitter" branch and now blooms, washing the sky cyan. Suggested fix for Optimizer: raise uFxbHot.z/w to about .97/1.0, or require mx>=.97 && sat>=.6, or exclude blue-dominant hue. Re-test pbr day after that.

## FXBLOOM v2 check (22:20-23:05; uFxbHot .88/.97/.97/1.0, sat ramp .6-.75)
- One fresh build_copy: fxb3_after.html (v2), and fxb3_before.html (same copy, block stripped).
- .testlock held; hero standard; fixed day switch; 0 page errors.
| mode | view | tod | p95 before | >=245 before % | p95 after | >=245 after % |
|---|---|---|---|---|---|---|
| pbr | street | day | 188 | 0.1 | 224 | 0.19 |
| pbr | causeway | day | 207 | 0.11 | 223 | 0.12 |
| pbr | street | night | 178 | 2.0 | 165 | 0.09 |
| pbr | causeway | night | 157 | 0.17 | 155 | 0.08 |
| toon | street | day | 254 | 12.52 | 222 | 0.79 |

Results:
- Toon street day fixed: 12.5% -> 0.79%.
- Night: neon and lamps keep their bloom.
- pbr day STILL washes the sky cyan (p95 188 -> 224).

Root cause (not the saturation branch):
- pbr_world.js (s13, by day) raises FX.bloom.threshold to .68+.3*uDay = .98.
- FXBLOOM computes smoothstep(max(luminosityThreshold,.88), .97, v) = smoothstep(.98, .97, v). With edge0 > edge1, GLSL's result is undefined and in practice inverted: nearly every pixel BELOW .98, i.e. the whole sky, gets alpha of about 1.

Fix (one of):
- (a) FXBLOOM: use `float e0=max(luminosityThreshold,uFxbHot.x); smoothstep(e0, max(uFxbHot.y, e0+.02), v)`. This is robust for any threshold.
- (b) pbr_world.js drops its day threshold/strength tweak, which is now redundant with FXBLOOM. That file is with another worker right now.
