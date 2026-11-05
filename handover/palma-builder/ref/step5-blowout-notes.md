# Step 5 slice 1: street blowout + causeway shot notes (Palma Builder, 2026-10-30)
## (1) Street ground blowout, hero settings, FX on. FIXED in pbr_world.js (copy bo_pbr_s4.html)
- Root cause: setupFX's UnrealBloomPass(res W/2,H/2, strength .6, radius .45, threshold .68). LuminosityHighPass uses smoothWidth .01, so it is effectively a binary cut. The composer targets are 8-bit, and ACES/fog output is already in 0..1 there.
- The ACES-mapped PBR ground sat at about .66-.70 luminance (measured ~170/255 at 960x540, FX on), right on the threshold. Any large flat area over .68 gets its full colour added back by all 5 bloom mips (factors 1+.8+.6+.4+.2 = 3.0 x strength .6 ≈ 1.8x), which turns it white.
- Why it depends on resolution: dsf 1.5 means renderer pixel ratio 1.5 and composer pixel ratio 1.25, so the ground's mip/aniso sampling and sun-spec average shift by a few %. At 960x540 it stayed just under .68; at 1920x1080 at 1.5 it crossed. The toon ground (before) sits at ~.43, well below the threshold.
- Fix (pbr_world.js only, no FX code touched): FCAP is injected before dithering_fragment (so after tonemapping and fog) on PBR world materials. It soft-caps final luminance at about .6-.65, below the bloom threshold. Diffuse world surfaces never bloom; neon/emissive are separate materials and untouched.
- Result: the hero street after-shots (12:5x) show textured grey asphalt and no blowout, day and night.
## (2) Causeway shot camera
- dcsplit2 BRV side cam = (40,9,-309), which sits behind the Sleeping Forest garage (40,-275). A rider pinned on the deck still triggered BAIL! RESPAWN, and its respawn view replaced the pinned camera.
- Fix in pbr_hero.py: the rider stays parked at the safe street spot (-60,0,-30). The camera is teleported alone to a deck chase view, 13 m behind a point 60 m along the causeway from end a, 4.2 m high, looking 70 m down the deck.
- Draws s4 (2 runs, world min/mean/max), default → pbr=1: causeway 95/95/95 → 91/93.5/96; street 71/71.5/72 → 72/74/76. All ≤110. Errors/404: 0 for default, pbr=1, pbr=1&ktx2=1.

## Day bloom tweak removal — verify close-out (2026-11-05 11:24 CST)

**Already done 2026-10-31 00:18** (bak `pbr_world.js.bak-bloomtweak-0018`). `tick()` no longer sets `FX.bloom.threshold/strength` via `S.bTh/S.bSt` or injects `pbrDay` high-pass (`S.bMask`). Comment left: `/* day bloom tweaks removed 10/31: replaced by FXBLOOM in patch_xr_fxmem.py (Optimizer) */`.

**Verify 2026-11-05 (copy `/tmp/palma_bloom.html`, FX on, seed=1):**
- `window.PBR_WORLD` exports stable: on, tick/boot/convert/install, ENV.{day,night,cube,cur}, GR.
- Day bloom: threshold **0.68**, strength **0.6**, `FX.bloomHot=true`, **no** `pbrDay` uniform (tweak absent). Night same th/st (neon bloom path intact).
- Day sky sample street (84,138,229) / causeway (101,154,233) = blue, not cyan wash. Ground L≈72–82, no blowout.
- 0 pageerrors. Draws world: street day/night 80/81, causeway day/night 73/74 (≤110).
- Hero finals: `shots/hero/pbr_{street,causeway}_{day,night}_final.png` + `pbr_street_day_before_after_side_by_side.png` (before = bak-bloomtweak copy).
- Real html md5 unchanged `5ad0f564…`.
