# Rydah Forge — Workshop Handover Inventory

- **Bot:** Rydah Forge (characters / wardrobe / skates / kit props / CombatFX / rider shading / Forge tools)
- **Date:** 2026-11-05 (America/Chicago); **updated 2026-11-09** (opt3 rider shading + close shots + Simca)
- **Branch:** `workshop-handover` → folder `handover/forge/`
- **Repo visibility:** PUBLIC (`dogstar830/sky-rydahs-webxr`)
- **Privacy:** ALL Akito/Agito files are **local-only** (excluded from this handover regardless of visibility), per Ani integrator update + DEMO_STATUS RULES. Listed at the bottom.
- **Packaged files:** 1219
- **Total size:** 1595.16 MB (1672641563 bytes)
- **Excluded from pack:** backups (`*.bak*`), intermediates (`*prespring*`, `*prerebind*`, `*v2raw*`, `*presym*`, `*.prefix-*`, `*.static-*`, `*.nrm768*`), Blender caches (`*.blend1`), `__pycache__`, and `.blend` sources ≥ 50 MB.

## Git LFS required

All `.glb`, `.png`, `.jpg`, `.webp`, `.blend`, and `.npz` files under `handover/forge/` are **Git LFS objects** (see the repo-root `.gitattributes`). A plain `git clone`, a GitHub zip download, a raw link, or a GitHub Pages fetch only gives ~130-byte pointer stubs — not the real binaries.

To materialize the real files after a clone:

```
git lfs install && git lfs pull
```

On this workshop box, `git-lfs` is at `/home/box/.local/bin/git-lfs` (add that directory to `PATH` if `git lfs` is not found).

GitHub Pages, `raw.githubusercontent.com` links, and the “Download ZIP” button only serve those pointer stubs. For browser tests, use the non-LFS copies in `handover/rydah-rigger/assets/` or `handover/rydah-optimizer/assets/`, or serve this folder from a local server after a `git lfs pull`.

## Code chain (build_ikki.sh)

Forge-owned / Forge-initiated steps in `/workspace/v3build/build_ikki.sh` (1-indexed patch order):

| Step | Patch | Module | Flags | Status |
|------|-------|--------|-------|--------|
| 10 | `patch_wardrobe.py` | `wardrobe_js/wardrobe.js` | `?player=`, `?outfit=`, `?tier=`, `?texfull=1`, `?ktx2` | live |
| 21 | `patch_gamepad.py` | `gamepad.js` | `?haptics=full\|reduced\|off` | live (Forge-initiated) |
| 22 | `patch_minimap.py` | `minimap_v2.js` | `?minimap=old` | live |
| 25 | `patch_quant_fix.py` | (inline SR_DEQUANT) | `?dequant=0` | live |
| 31 (LAST) | `patch_combat_fx.py` | `combat_fx.js` | `?fxdemo=1`, `?nocfx` | live |
| — | `patch_rider_style.py` | `rider_style.js` | `?riderstyle=opt3` | opt-in; official gate PASS; hook after `patch_pbr_base.py`, before `patch_xr_fxmem.py` (Ani wiring next rebuild) |
| — | `tools/deinterleave.py` | CLI | — | tool (offline) |

### Code file details

#### `tools/deinterleave.py`
- **Type/size/md5:** py, 1.7 KB, `efacb7576f87caa9bb0d906aba44f821`
- **What it does:** Rewrites GLB accessors from interleaved to non-interleaved buffers (fixes mergeBufferGeometries).
- **Chain order:** Offline CLI after Blender/gltf export; not in build_ikki.sh
- **URL flags:** CLI args
- **Dependencies:** GLB files (esp. at-skate-meshy*.glb)
- **Status:** tool

#### `v3build/combat_fx.js`
- **Type/size/md5:** js, 44.1 KB, `3bb87245062ca0bcb0a416159702b8cf`
- **What it does:** CombatFX API: emit/hit/slash/lightning/stagger/super/lockOn/trail/attach/fromHitFrame; per-crew palettes; max 3 draws.
- **Chain order:** Inlined by patch_combat_fx.py (step 31)
- **URL flags:** ?fxdemo=1, ?nocfx
- **Dependencies:** THREE, scene, SR_PAD optional, rider userData.fx (Rigger srFX)
- **Status:** live

#### `v3build/gamepad.js`
- **Type/size/md5:** js, 10.3 KB, `52e471720805b2fc1a00f728997f4cce`
- **What it does:** Xbox/standard pad layer: sticks, buttons, triggers, SR_PAD.haptic(evt,opts) with comfort scale.
- **Chain order:** Inlined by patch_gamepad.py (step 21)
- **URL flags:** ?haptics=full|reduced|off
- **Dependencies:** Gamepad API + optional XR gamepad haptic actuators
- **Status:** live

#### `v3build/minimap_v2.js`
- **Type/size/md5:** js, 19.6 KB, `707054b6a46cc951112ef0d3d8a07dfd`
- **What it does:** Tilted heading-up minimap, rim N, rim-clamped waypoints, window.MINIMAP.state API.
- **Chain order:** Inlined by patch_minimap.py (step 22)
- **URL flags:** ?minimap=old
- **Dependencies:** canvas 2D HUD, objective/cops markers
- **Status:** live

#### `v3build/patch_combat_fx.py`
- **Type/size/md5:** py, 845 B, `6d2a6fdc90ffcf3ea8914773dbc4fb57`
- **What it does:** Injects combat_fx.js CombatFX module before </body>; idempotent; SR_HTML/argv aware.
- **Chain order:** build_ikki.sh step 31 LAST (needs scene/camera/renderer/animated globals)
- **URL flags:** ?fxdemo=1 (loop demo), ?nocfx (disable module)
- **Dependencies:** combat_fx.js, SR_PAD.haptic (gamepad), Rigger srFX attach points, THREE
- **Status:** live (ready for rebuild; CombatFX v3)

#### `v3build/patch_gamepad.py`
- **Type/size/md5:** py, 7.1 KB, `840d419d42fc3a77c0987fce65dd2487`
- **What it does:** Injects gamepad.js as window.SR_PAD; routes navigator.getGamepads through it; haptics API used by CombatFX.
- **Chain order:** build_ikki.sh step 21 (after patch_phone.py #20; before patch_minimap.py #22). Comment historically said last; CombatFX is now last.
- **URL flags:** ?haptics=full|reduced|off (also localStorage sr_haptics)
- **Dependencies:** gamepad.js; XR renderer.xr session for pulses; Systems/combat callers of SR_PAD.haptic
- **Status:** live (Forge-initiated; Optimizer extended haptics)

#### `v3build/patch_minimap.py`
- **Type/size/md5:** py, 1.0 KB, `14734f38be23f809abc254bd7b259aa1`
- **What it does:** Injects minimap_v2.js Watch Dogs-style tilted GPS minimap + direction markers.
- **Chain order:** build_ikki.sh step 22 (after patch_gamepad.py #21; needs map.js/icons.js from patch_phone)
- **URL flags:** ?minimap=old (restore old HUD)
- **Dependencies:** minimap_v2.js, map.js, icons.js, phone HUD
- **Status:** live

#### `v3build/patch_quant_fix.py`
- **Type/size/md5:** py, 2.4 KB, `9746c0f2b2d25abcc7e915303fff369e`
- **What it does:** Dequantizes KHR_mesh_quantization POSITION back to float metres and fixes skin IBM so AT wheel centres (_WC) spin correctly.
- **Chain order:** build_ikki.sh step 25 (after patch_crew_quest.py #24; before patch_crewhouse_kit.py #26)
- **URL flags:** ?dequant=0 (disable)
- **Dependencies:** Skinned wardrobe/Ikki riders with quantized POSITION; IKKI_AT_VERT / _WC attributes
- **Status:** live

#### `v3build/patch_rider_style.py`
- **Type/size/md5:** py, 663 B, `5fcf4e3be7a1d6926d3e655be3e01ae4`
- **What it does:** Inlines rider_style.js Option 3 stylized-realistic shading before `// ===== LOOP =====`.
- **Chain order:** Hook for `build_ikki.sh`: after `patch_pbr_base.py`, before `patch_xr_fxmem.py` (Ani wiring into the next rebuild). Still opt-in at runtime.
- **URL flags:** ?riderstyle=opt3 (default remains the old look)
- **Dependencies:** rider_style.js, RIDERS, PBR_WORLD env when present, MeshStandardMaterial riders
- **Status:** opt-in; official gate PASS; ready for rebuild

#### `v3build/patch_wardrobe.py`
- **Type/size/md5:** py, 7.8 KB, `be0ebe08ea19e01bec4125d21d99d403`
- **What it does:** Injects wardrobe system + Caali G as default player on shared Meshy skeleton/skate poser; wires WARDROBE_RIDERS, outfit apply, hide slots.
- **Chain order:** build_ikki.sh step 10 (after patch_asphalt.py #9; before patch_facades.py #11)
- **URL flags:** ?player=caali|forge|ikki|…, ?outfit=<preset|+slot:item>, ?tier=hd|quest, ?texfull=1, ?ktx2=1 (via SR_KTX2), ?akito=0 (local)
- **Dependencies:** wardrobe_js/wardrobe.js (inlined/loaded), jackets.js AT skate API, riders.js loadIkki, CHAR_BASE assets under skyrydahs-characters/
- **Status:** live

#### `v3build/patch_wardrobe_v6pre.py`
- **Type/size/md5:** py, 5.9 KB, `f87700fec224bbfe069b0abd9efda8d3`
- **What it does:** Older wardrobe patch variant (v6pre); superseded by patch_wardrobe.py.
- **Chain order:** NOT in build_ikki.sh
- **URL flags:** same family as wardrobe
- **Dependencies:** wardrobe_v6pre.js
- **Status:** WIP/archive

#### `v3build/rider_style.js`
- **Type/size/md5:** js, 8.8 KB, `45ca2ff822c6d9b4624fe66494f3cfc7`
- **What it does:** Option 3 stylized-realistic rider shading: shared PMREM/env, fresnel rim in crew colour, hair/metal spec, drop toon hull; luma capped under the FX bloom band.
- **Chain order:** Inlined by patch_rider_style.py (hook after patch_pbr_base.py, before patch_xr_fxmem.py)
- **URL flags:** ?riderstyle=opt3 (default off)
- **Dependencies:** Optimizer constraints perf/rider-style-opt3-constraints.md; PBR_WORLD; official gate PASS (see v3build/perf/forge/rider-style-opt3.md)
- **Status:** opt-in; official gate PASS; ready for rebuild

#### `v3build/rider_style_opt3_shots.py`
- **Type/size/md5:** py, 3.4 KB, `f4c62de362663059f578e0bc28747cba`
- **What it does:** Renders chase-distance before/after hero shots of Caali, Anika and Ikki (day and night) plus a contact sheet.
- **Chain order:** Offline shot tool; not in build_ikki.sh
- **URL flags:** uses ?riderstyle=opt3 / default for the after/before pairs
- **Dependencies:** built HTML, .testlock, hero shot harness
- **Status:** tool

#### `v3build/rider_style_opt3_close_shots.py`
- **Type/size/md5:** py, 5.3 KB, `b87b136187286d310870426952659045`
- **What it does:** Close-up (~3/4 front, rider filling ~60% of the frame) before/after pairs with locked camera/time and NPCs hidden; builds the close contact sheet.
- **Chain order:** Offline shot tool; not in build_ikki.sh
- **URL flags:** uses ?riderstyle=opt3 / default for the after/before pairs
- **Dependencies:** built HTML, .testlock, hero shot harness
- **Status:** tool


#### `v3build/wardrobe_js/wardrobe.js`
- **Type/size/md5:** js, 5.3 KB, `3593fa562c2cf0d421c1edba8fdb598c`
- **What it does:** Wardrobe catalog: slots, presets (caali/ikki), WARDROBE_RIDERS URL map (Caali G / Akito local), equip()/apply(), tier pick.
- **Chain order:** Loaded/used by patch_wardrobe.py (step 10); not a separate patch step
- **URL flags:** ?tier=hd|quest, ?outfit=…, ?texfull=1, ?ktx2=1
- **Dependencies:** THREE GLTFLoader + DRACO, CHAR_BASE wardrobe/* and riders GLBs
- **Status:** live

#### `v3build/wardrobe_js/wardrobe_v6pre.js`
- **Type/size/md5:** js, 4.5 KB, `87bdeefa366a23ce3d885f92d723215e`
- **What it does:** Pre-v6 wardrobe snapshot kept for reference/rollback.
- **Chain order:** NOT in build_ikki.sh (companion to patch_wardrobe_v6pre.py)
- **URL flags:** —
- **Dependencies:** —
- **Status:** WIP/archive

### Other Forge scripts / tests

| Path | Type | Size | md5 | What | Status |
|------|------|------|-----|------|--------|
| `forge_kit/build.py` | py | 6.8 KB | `aba63609e1204530bd0ba660eae70710` | Tool/source build.py | tool |
| `forge_kit/build_v1.py` | py | 6.2 KB | `68b72f8662b9bac5a6d14ef620decc43` | Tool/source build_v1.py | tool |
| `forge_kit/gk/bake.py` | py | 5.0 KB | `9b46b4212a69d8c24e15526888e83551` | Tool/source bake.py | tool |
| `forge_kit/gk/fin.py` | py | 721 B | `f1da39b291b81c3815741dffd955dbf8` | Tool/source fin.py | tool |
| `forge_kit/gk/q.py` | py | 596 B | `e574d9071b3760828dd91b3448d38b5e` | Tool/source q.py | tool |
| `forge_kit/gk/scr.py` | py | 400 B | `1a553eb82d8e54213d87be292747efb4` | Tool/source scr.py | tool |
| `forge_kit/gr8/bb.py` | py | 635 B | `1ee77ad42194b09d843e482001753a24` | Tool/source bb.py | tool |
| `forge_kit/gr8/build_gr8.py` | py | 15.4 KB | `14f289e1d3ae4014a1e172740808b7fd` | Tool/source build_gr8.py | tool |
| `forge_kit/gr8/compose.py` | py | 624 B | `d4a5410d3b9537339ffdeb5578d69967` | Tool/source compose.py | tool |
| `forge_kit/gr8/compose2.py` | py | 662 B | `4c306946099af3784dda4195b2ee8602` | Tool/source compose2.py | tool |
| `forge_kit/gr8/dbg.py` | py | 349 B | `65499c5730f49b271eb9377087f54c32` | Tool/source dbg.py | tool |
| `forge_kit/gr8/decals.py` | py | 1.8 KB | `787a277e5a40764ede8e60cd30449823` | Tool/source decals.py | tool |
| `forge_kit/gr8/export.py` | py | 1.6 KB | `008803490d8676f19771e2b5e1b16789` | Tool/source export.py | tool |
| `forge_kit/gr8/fix/fixrider.py` | py | 12.5 KB | `aa4a454b5366dea12c699c18ad9d5335` | Tool/source fixrider.py | tool |
| `forge_kit/gr8/fix/glbio.py` | py | 1.7 KB | `1b2a15fb8ca4097c742d2ec754131ebb` | Tool/source glbio.py | tool |
| `forge_kit/gr8/fix/measure.py` | py | 2.2 KB | `3f86424daed0cb2e32c893bab5a203da` | Tool/source measure.py | tool |
| `forge_kit/gr8/fix/plot.py` | py | 978 B | `38b3ceacfe4a196972cf6c7ddc69ab18` | Tool/source plot.py | tool |
| `forge_kit/gr8/fix/probe.py` | py | 2.9 KB | `6f855eedb3d4ba5ec2115c356723d64f` | Tool/source probe.py | tool |
| `forge_kit/gr8/fix/skate_bake.py` | py | 1.5 KB | `c462bdfb23f1009d7ccb5dd7b0b24288` | Tool/source skate_bake.py | tool |
| `forge_kit/gr8/fix/skate_lift.py` | py | 1.6 KB | `e95fbf0c487c0d16f820c6f8d90d5c51` | Tool/source skate_lift.py | tool |
| `forge_kit/gr8/fix/skate_shot.py` | py | 3.4 KB | `a84a002d5f4df3c00d33f703c4da86d8` | Tool/source skate_shot.py | tool |
| `forge_kit/gr8/fix/sockgap.py` | py | 2.3 KB | `217e7c860f26320defb2c12cb8563f1d` | Tool/source sockgap.py | tool |
| `forge_kit/gr8/fixorm.py` | py | 768 B | `2c3b52939cdca301839d5e7e8becc306` | Tool/source fixorm.py | tool |
| `forge_kit/gr8/glbinspect.py` | py | 827 B | `aafca2d607d839d4f134ff777c5c7b5c` | Tool/source glbinspect.py | tool |
| `forge_kit/gr8/hero.py` | py | 2.7 KB | `3c8ff31f4c2da8f5e03d89f13a9e6294` | Tool/source hero.py | tool |
| `forge_kit/gr8/hero_glb.py` | py | 3.4 KB | `9f7cb7d8be6327d31c92224046eab1c2` | Tool/source hero_glb.py | tool |
| `forge_kit/gr8/hero_ply.py` | py | 3.2 KB | `983188f98fe43964fb528fab1b8c6c5a` | Tool/source hero_ply.py | tool |
| `forge_kit/gr8/hero_ply2.py` | py | 3.4 KB | `05ad3ee4bbdd231aec8c93c4ce7d4942` | Tool/source hero_ply2.py | tool |
| `forge_kit/gr8/hero_ply3.py` | py | 3.5 KB | `884043b053b217010e0f9d93d7aabd9e` | Tool/source hero_ply3.py | tool |
| `forge_kit/gr8/heroes.sh` | sh | 588 B | `295e060b929dabe7007f76b49a1101a2` | Tool/source heroes.sh | tool |
| `forge_kit/gr8/pieces.py` | py | 2.0 KB | `0159b0800e3016d8c7d01ac519434030` | Tool/source pieces.py | tool |
| `forge_kit/gr8/prep.py` | py | 1.8 KB | `939377764114ca7b84d540728f4e9443` | Tool/source prep.py | tool |
| `forge_kit/gr8/qc.py` | py | 872 B | `0a9a6e34cbf73ea09c20c5b700a63759` | Tool/source qc.py | tool |
| `forge_kit/gr8/qcs.sh` | sh | 272 B | `e2a538bccf0f6acfb6be0e8d0eb6c4f2` | Tool/source qcs.sh | tool |
| `forge_kit/gr8/qv.py` | py | 838 B | `c06077373975a44f8968a1f9adfdf385` | Tool/source qv.py | tool |
| `forge_kit/gr8/qz.py` | py | 656 B | `6d2e5da578235c9b163d97b0bff065e7` | Tool/source qz.py | tool |
| `forge_kit/gr8/qz_red.py` | py | 898 B | `ca4d0b865e1ce73ada325d2d20a5cff0` | Tool/source qz_red.py | tool |
| `forge_kit/gr8/runall.sh` | sh | 800 B | `43f27307230307fe7d6d4b8ee88b97cb` | Tool/source runall.sh | tool |
| `forge_kit/gr8/ship.sh` | sh | 790 B | `d654c089162a7fb061b24f0bf4809159` | Tool/source ship.sh | tool |
| `forge_kit/gr8/sk2.py` | py | 649 B | `7b6cffa3964dd5daab5e4e82257780c1` | Tool/source sk2.py | tool |
| `forge_kit/gr8/sk3.py` | py | 599 B | `44eb327df33f7f70c927ca1b96831222` | Tool/source sk3.py | tool |
| `forge_kit/gr8/sk4.py` | py | 722 B | `9f45c0eb04ef2d643e978721368c64e6` | Tool/source sk4.py | tool |
| `forge_kit/gr8/sk5.py` | py | 989 B | `dc398db984f25fef173f7784dccf6a5a` | Tool/source sk5.py | tool |
| `forge_kit/gr8/sk6.py` | py | 866 B | `9c49f941dd5965f29532cfeaf8f467b9` | Tool/source sk6.py | tool |
| `forge_kit/render.py` | py | 2.0 KB | `0a11ac3875a1b642b6f1fe96d16ba772` | Tool/source render.py | tool |
| `forge_kit/render_neutral.py` | py | 2.0 KB | `2fa6f2eb7c3d38d9a5e3fe0c0e5872a9` | Tool/source render_neutral.py | tool |
| `forge_kit/skate/bl.py` | py | 493 B | `a66642d8e1a51e2ed901f53e8ece02dc` | Tool/source bl.py | tool |
| `forge_kit/skate/build_skate.py` | py | 4.6 KB | `64eea3f8ec480c3da6ac85cdd66dab7f` | Tool/source build_skate.py | tool |
| `forge_kit/skate/diag.py` | py | 1.6 KB | `d37f3b615f85e34730a9e9e4eb988743` | Tool/source diag.py | tool |
| `forge_kit/skate/diag2.py` | py | 1.3 KB | `5d8474636f061c99434ba068e3d787a8` | Tool/source diag2.py | tool |
| `forge_kit/skate/diag3.py` | py | 689 B | `97b1c2627e6ba30b79998df500171720` | Tool/source diag3.py | tool |
| `forge_kit/skate/dump.py` | py | 447 B | `88be2e3a0e0e6618fc254802edbe984a` | Tool/source dump.py | tool |
| `forge_kit/skate/look.py` | py | 1.4 KB | `c0d83f971d1f738aaf5e93be3adeb34a` | Tool/source look.py | tool |
| `forge_kit/skate/pv.py` | py | 1.4 KB | `2874dc6a31d404c4ca57d1e6ac349931` | Tool/source pv.py | tool |
| `forge_kit/skate/q2.py` | py | 551 B | `61e85c2ab85cfec4c601add72090c27f` | Tool/source q2.py | tool |
| `forge_kit/skate/rad.py` | py | 679 B | `f0c4c57a353cdb374cc847d233235178` | Tool/source rad.py | tool |
| `forge_kit/skate/rcmp.py` | py | 2.5 KB | `a8b08b5daf0240d86ffb4c1ba7d3ece5` | Tool/source rcmp.py | tool |
| `forge_kit/skate/reg.py` | py | 1.6 KB | `d12c0d6a2287fc053964f8f779b69359` | Tool/source reg.py | tool |
| `forge_kit/skate/wh.py` | py | 622 B | `86a53573c6e81a838d5a41709cd1a640` | Tool/source wh.py | tool |
| `forge_kit/skate/wheels_export.py` | py | 4.1 KB | `826a214434c1f3e221ccfa4af250e6f0` | Tool/source wheels_export.py | tool |
| `forge_kit/skate/write_glb.py` | py | 6.1 KB | `36f6a30b7b05bbcc8ee54cd85bfde99a` | Tool/source write_glb.py | tool |
| `forge_kit/tv.py` | py | 2.4 KB | `46abb59457b2f87dd1c844928682b66b` | Tool/source tv.py | tool |
| `skyrydahs-characters/anika/src/build_gr8.py` | py | 15.4 KB | `14f289e1d3ae4014a1e172740808b7fd` | build_gr8.py | live |
| `skyrydahs-characters/anika/src/compose.py` | py | 624 B | `d4a5410d3b9537339ffdeb5578d69967` | compose.py | live |
| `skyrydahs-characters/anika/src/decals.py` | py | 1.8 KB | `787a277e5a40764ede8e60cd30449823` | decals.py | live |
| `skyrydahs-characters/anika/src/export.py` | py | 1.6 KB | `008803490d8676f19771e2b5e1b16789` | export.py | live |
| `skyrydahs-characters/anika/src/hero.py` | py | 2.7 KB | `3c8ff31f4c2da8f5e03d89f13a9e6294` | hero.py | live |
| `skyrydahs-characters/anika/src/pieces.py` | py | 2.0 KB | `0159b0800e3016d8c7d01ac519434030` | pieces.py | live |
| `skyrydahs-characters/anika/src/ship.sh` | sh | 790 B | `d654c089162a7fb061b24f0bf4809159` | ship.sh | live |
| `skyrydahs-characters/anubis/src/build_rider.py` | py | 11.2 KB | `cb381367f6b04766cd5c53ef20c48969` | Crew character asset build_rider.py | live |
| `skyrydahs-characters/anubis/src/shoot.sh` | sh | 180 B | `6a202962e1047e76e6e07576716a8f28` | Crew character asset shoot.sh | live |
| `skyrydahs-characters/behemoth/src/build_rider.py` | py | 8.6 KB | `0344089904415802b8fd7fe73ac857b7` | Crew character asset build_rider.py | live |
| `skyrydahs-characters/behemoth/src/shoot.sh` | sh | 182 B | `8e973b72198f3279ef0c073045065e2a` | Crew character asset shoot.sh | live |
| `skyrydahs-characters/caali/src/build_rider.py` | py | 18.5 KB | `785b5bcd2c106946a4f0d6d9bd9d96da` | Crew character asset build_rider.py | live |
| `skyrydahs-characters/caali/src/build_rider_v1.py` | py | 18.2 KB | `8bb994116468dbc4975fae0da020885c` | Crew character asset build_rider_v1.py | live |
| `skyrydahs-characters/caali/src/shoot.sh` | sh | 612 B | `a234f2f6a09d0c135bc20fb11efe4a90` | Crew character asset shoot.sh | live |
| `skyrydahs-characters/code-e/src/build_rider.py` | py | 18.5 KB | `785b5bcd2c106946a4f0d6d9bd9d96da` | Crew character asset build_rider.py | live |
| `skyrydahs-characters/code-e/src/build_rider_v1.py` | py | 18.2 KB | `8bb994116468dbc4975fae0da020885c` | Crew character asset build_rider_v1.py | live |
| `skyrydahs-characters/code-e/src/shoot.sh` | sh | 180 B | `611591a68877aca6baa719937999811b` | Crew character asset shoot.sh | live |
| `skyrydahs-characters/genesis/src/build_rider.py` | py | 11.5 KB | `d86c7b38a0cb6883671d6fb003d53437` | Crew character asset build_rider.py | live |
| `skyrydahs-characters/kogarasumaru/src/build_rider.py` | py | 11.5 KB | `c3897de64690bac9d70bf67420f535a2` | Crew character asset build_rider.py | live |
| `skyrydahs-characters/kogarasumaru/src/shoot.sh` | sh | 186 B | `c3ba2150c1483dd989f19d9e616b6f61` | Crew character asset shoot.sh | live |
| `skyrydahs-characters/sleeping-forest/src/build_rider.py` | py | 12.0 KB | `4cd4dc444206d3421857f602e7208117` | Crew character asset build_rider.py | live |
| `skyrydahs-characters/static-angels/src/build_rider.py` | py | 8.7 KB | `cb1c45dffef59b7621503c610678a9c1` | Crew character asset build_rider.py | live |
| `skyrydahs-characters/static-angels/src/shoot.sh` | sh | 187 B | `554af5bd834aeeca64e09f02a46587b5` | Crew character asset shoot.sh | live |
| `skyrydahs-characters/tool-toul-to/src/build_rider.py` | py | 13.2 KB | `48d6a3ef04ef1c420c833557ca6cd46c` | Crew character asset build_rider.py | live |
| `v3build/rider_style_opt3_close_shots.py` | py | 5.3 KB | `b87b136187286d310870426952659045` | Close-up (~3/4 front, rider ~60% of frame) opt3 before/after shots with locked camera/time and NPCs hidden; builds close contact sheet. | tool |
| `v3build/rider_style_opt3_shots.py` | py | 3.4 KB | `f4c62de362663059f578e0bc28747cba` | Chase-distance opt3 before/after hero shots for Caali, Anika, Ikki (day/night) plus contact sheet. | tool |
| `v3build/tests/combat_fx_hue.py` | py | 2.4 KB | `bf32fa45a8ef2536ff5c27df15815de3` | combat_fx_hue.py | live |
| `v3build/tests/combat_fx_kick.py` | py | 3.7 KB | `f38397506b1f8f15df1e489094cd22dd` | combat_fx_kick.py | live |
| `v3build/tests/combat_fx_shots.py` | py | 3.1 KB | `fbab99e49b2bc6e2c343c9a8d90a7537` | combat_fx_shots.py | live |
| `v3build/wardrobe_build/assemble_rider.py` | py | 10.7 KB | `e7f575fe9083b5703a54302fb17c779f` | Tool/source assemble_rider.py | tool |
| `v3build/wardrobe_build/assemble_rider_v6pre.py` | py | 10.7 KB | `e67ca1f826c9f6f676713575bdd59984` | Tool/source assemble_rider_v6pre.py | tool |
| `v3build/wardrobe_build/build_wardrobe.py` | py | 52.9 KB | `de89d407674543deb690f5002778a5b5` | Tool/source build_wardrobe.py | tool |
| `v3build/wardrobe_build/build_wardrobe_v1.py` | py | 18.6 KB | `7b429143de025b51817556100413e6b6` | Tool/source build_wardrobe_v1.py | tool |
| `v3build/wardrobe_build/build_wardrobe_v2.py` | py | 28.6 KB | `f408d87357cf3d5c6dd2bcd38dea9305` | Tool/source build_wardrobe_v2.py | tool |
| `v3build/wardrobe_build/build_wardrobe_v3pre.py` | py | 31.6 KB | `9a970b7c9927f1f0d237d6aafb0916d8` | Tool/source build_wardrobe_v3pre.py | tool |
| `v3build/wardrobe_build/build_wardrobe_v4pre.py` | py | 34.4 KB | `7179e37440da7e200a4780abc8514f43` | Tool/source build_wardrobe_v4pre.py | tool |
| `v3build/wardrobe_build/build_wardrobe_v5pre.py` | py | 36.8 KB | `233d3b24955ebbd274d25a9eaf2c77de` | Tool/source build_wardrobe_v5pre.py | tool |
| `v3build/wardrobe_build/build_wardrobe_v6pre.py` | py | 38.8 KB | `37fdf8310c5863a505969a120026549d` | Tool/source build_wardrobe_v6pre.py | tool |
| `v3build/wardrobe_build/build_wardrobe_v7pre.py` | py | 45.3 KB | `74d537dbbe8ad7796002c9884a4f771c` | Tool/source build_wardrobe_v7pre.py | tool |
| `v3build/wardrobe_build/look.py` | py | 1.3 KB | `449256a87f81db2f2455daf54d4062e6` | Tool/source look.py | tool |
| `v3build/wardrobe_build/make_logo.py` | py | 1.4 KB | `b107e0501e939d22d1912e02f8066b94` | Tool/source make_logo.py | tool |
| `v3build/wardrobe_build/measure.py` | py | 2.2 KB | `4d9a9071f2d195c1b3fb3f14b5e1e03a` | Tool/source measure.py | tool |
| `v3build/wardrobe_build/prev.py` | py | 2.0 KB | `290653c120d75ede82076c14ff47422d` | Tool/source prev.py | tool |
| `v3build/wardrobe_build/sleeve_check.py` | py | 1.3 KB | `f444b01741de8fe6207b6b7fdf6d2269` | Tool/source sleeve_check.py | tool |

## Assets (every packaged file)

| Path | Type | Size | md5 | Tris/LODs/Joints | What | Runtime loader | Status |
|------|------|------|-----|------------------|------|----------------|--------|
| `forge_kit/build.py` | py | 6.8 KB | `aba63609e1204530bd0ba660eae70710` | — | Tool/source build.py | — | tool |
| `forge_kit/build_v1.py` | py | 6.2 KB | `68b72f8662b9bac5a6d14ef620decc43` | — | Tool/source build_v1.py | — | tool |
| `forge_kit/drone_raw.glb` | glb | 69.3 KB | `79b5aa56306effc6fbf32793152e8d75` | tris=972; meshes=drone_body,rotor_BL,rotor_BR,rotor_FL | Tool/source drone_raw.glb | — | tool |
| `forge_kit/gk/bake.py` | py | 5.0 KB | `9b46b4212a69d8c24e15526888e83551` | — | Tool/source bake.py | — | tool |
| `forge_kit/gk/bk_couch.png` | png | 957.6 KB | `9e2316a6c4e7dd36788e367f142bc078` | — | Tool/source bk_couch.png | — | tool |
| `forge_kit/gk/bk_lockers.png` | png | 893.5 KB | `052d6249754d7a0952d90a41e7e9e62a` | — | Tool/source bk_lockers.png | — | tool |
| `forge_kit/gk/couch_col.png` | png | 1.01 MB | `107dcbc235ffa35961dbf34e2699b8d2` | — | Tool/source couch_col.png | — | tool |
| `forge_kit/gk/couch_col_src.png` | png | 3.87 MB | `011e67009eb66a5ea29d010c246d6dc9` | — | Tool/source couch_col_src.png | — | tool |
| `forge_kit/gk/couch_img0.jpg` | jpg | 2.12 MB | `86aea68692612235991542cec447cda3` | — | Tool/source couch_img0.jpg | — | tool |
| `forge_kit/gk/couch_img1.jpg` | jpg | 1.20 MB | `279fbc15fd344152296da8920991e660` | — | Tool/source couch_img1.jpg | — | tool |
| `forge_kit/gk/couch_img2.jpg` | jpg | 1.63 MB | `1abc1bc0b32087e061da877c97891441` | — | Tool/source couch_img2.jpg | — | tool |
| `forge_kit/gk/couch_lo.blend` | blend | 2.49 MB | `8b2e874d53ee300192441327a94eb2b1` | — | Tool/source couch_lo.blend | — | tool |
| `forge_kit/gk/couch_nrm.png` | png | 944.5 KB | `14d585fb243f6c1222bf6cb2c919a6cd` | — | Tool/source couch_nrm.png | — | tool |
| `forge_kit/gk/couch_orm.png` | png | 709.5 KB | `54246fc71cd1ff31730291f977de1234` | — | Tool/source couch_orm.png | — | tool |
| `forge_kit/gk/couch_orm_src.png` | png | 1.92 MB | `e7f743c0838ddf2617ccc39a6d897974` | — | Tool/source couch_orm_src.png | — | tool |
| `forge_kit/gk/couch_raw.glb` | glb | 424.9 KB | `96e8983bcf9c33acfee3da9abb33a177` | tris=5500; meshes=Mesh_0.001 | Tool/source couch_raw.glb | — | tool |
| `forge_kit/gk/couch_rawj.glb` | glb | 2.79 MB | `11e6747050783d4c1a2b70d7b6916afe` | tris=5500; meshes=Mesh_0.001 | Tool/source couch_rawj.glb | — | tool |
| `forge_kit/gk/desk_col.png` | png | 1.17 MB | `b627d1edd4a47c00c986c2e5076d1bb1` | — | Tool/source desk_col.png | — | tool |
| `forge_kit/gk/desk_col_src.png` | png | 4.62 MB | `b022f2a3970adf89de65674946a83bea` | — | Tool/source desk_col_src.png | — | tool |
| `forge_kit/gk/desk_em.png` | png | 3.6 KB | `e1b8d293cd18dfed366a5f93f5b5b2a5` | — | Tool/source desk_em.png | — | tool |
| `forge_kit/gk/desk_img0.jpg` | jpg | 2.56 MB | `b56fd1a6138ce4530c7487fc8b6c3aa5` | — | Tool/source desk_img0.jpg | — | tool |
| `forge_kit/gk/desk_img1.jpg` | jpg | 1.37 MB | `e2296eddd68a30bf4838122ca7db0f97` | — | Tool/source desk_img1.jpg | — | tool |
| `forge_kit/gk/desk_img2.jpg` | jpg | 1.81 MB | `950dc2f38531e46bf585dbddc85ccdce` | — | Tool/source desk_img2.jpg | — | tool |
| `forge_kit/gk/desk_lo.blend` | blend | 2.66 MB | `c755b316a2173e319982c478db964a05` | — | Tool/source desk_lo.blend | — | tool |
| `forge_kit/gk/desk_nrm.png` | png | 1.10 MB | `bccd4efd6bb5921cbda106e54ae75fdb` | — | Tool/source desk_nrm.png | — | tool |
| `forge_kit/gk/desk_orm.png` | png | 669.4 KB | `5157500b133ca7813046b50cd137c343` | — | Tool/source desk_orm.png | — | tool |
| `forge_kit/gk/desk_orm_src.png` | png | 2.27 MB | `ea2432083ee58c2c9c81e07caa5891f5` | — | Tool/source desk_orm_src.png | — | tool |
| `forge_kit/gk/desk_raw.glb` | glb | 538.7 KB | `37345c727046984d6e25e79bd815b45a` | tris=5494; meshes=Mesh_0.001 | Tool/source desk_raw.glb | — | tool |
| `forge_kit/gk/desk_rawj.glb` | glb | 3.13 MB | `e62e893a2552c8d80a7629c768cf58b0` | tris=5494; meshes=Mesh_0.001 | Tool/source desk_rawj.glb | — | tool |
| `forge_kit/gk/fin.py` | py | 721 B | `f1da39b291b81c3815741dffd955dbf8` | — | Tool/source fin.py | — | tool |
| `forge_kit/gk/final_sheet.png` | png | 643.9 KB | `e83aa574b4114e8559f07dce0a4c7d85` | — | Tool/source final_sheet.png | — | tool |
| `forge_kit/gk/kitchen_col.png` | png | 1.11 MB | `a80e5fa8943cf1c099abc600dca949fa` | — | Tool/source kitchen_col.png | — | tool |
| `forge_kit/gk/kitchen_col_src.png` | png | 3.53 MB | `9695d6be95d8c616f700539655bf6341` | — | Tool/source kitchen_col_src.png | — | tool |
| `forge_kit/gk/kitchen_img0.jpg` | jpg | 1.89 MB | `5fbb794f0c4489f3d4fcda23c44a3ae9` | — | Tool/source kitchen_img0.jpg | — | tool |
| `forge_kit/gk/kitchen_img1.jpg` | jpg | 1.25 MB | `39cb18e39c07a7e83bfa5a6458952640` | — | Tool/source kitchen_img1.jpg | — | tool |
| `forge_kit/gk/kitchen_img2.jpg` | jpg | 1.42 MB | `ca9db1485172ba21ce6aadf5fb27596f` | — | Tool/source kitchen_img2.jpg | — | tool |
| `forge_kit/gk/kitchen_lo.blend` | blend | 2.43 MB | `a2c167ca359bad515c68fc46bab74f67` | — | Tool/source kitchen_lo.blend | — | tool |
| `forge_kit/gk/kitchen_nrm.png` | png | 891.3 KB | `1723894ca78ef51a6b1d708d573cb0cb` | — | Tool/source kitchen_nrm.png | — | tool |
| `forge_kit/gk/kitchen_orm.png` | png | 842.3 KB | `1746520159e4ebc3a00c1904e07ac255` | — | Tool/source kitchen_orm.png | — | tool |
| `forge_kit/gk/kitchen_orm_src.png` | png | 2.38 MB | `ba5ec28fc0b433d95e3419c1470b0f5e` | — | Tool/source kitchen_orm_src.png | — | tool |
| `forge_kit/gk/kitchen_raw.glb` | glb | 426.5 KB | `ad8b2ebffbabff69dfd7976174315aa8` | tris=7800; meshes=Mesh_0.001 | Tool/source kitchen_raw.glb | — | tool |
| `forge_kit/gk/kitchen_rawj.glb` | glb | 3.03 MB | `001800c4d957d5fe4c863881790595b2` | tris=7800; meshes=Mesh_0.001 | Tool/source kitchen_rawj.glb | — | tool |
| `forge_kit/gk/lockers_col.png` | png | 582.9 KB | `b39c47658d349bf643ec13cf4576b5c4` | — | Tool/source lockers_col.png | — | tool |
| `forge_kit/gk/lockers_col_src.png` | png | 1.45 MB | `8f38a09e65f4e64a7cb66a324a59ee84` | — | Tool/source lockers_col_src.png | — | tool |
| `forge_kit/gk/lockers_img0.jpg` | jpg | 1.71 MB | `acc907551d2002682a6837246578b5ef` | — | Tool/source lockers_img0.jpg | — | tool |
| `forge_kit/gk/lockers_img1.jpg` | jpg | 2.06 MB | `a571cf969a3fe14511205becfd66c8bb` | — | Tool/source lockers_img1.jpg | — | tool |
| `forge_kit/gk/lockers_img2.jpg` | jpg | 1.43 MB | `5b86a64b898691e8fe970ca276a9288c` | — | Tool/source lockers_img2.jpg | — | tool |
| `forge_kit/gk/lockers_lo.blend` | blend | 2.45 MB | `5660a1de4ddce6da646bc8d6291af56c` | — | Tool/source lockers_lo.blend | — | tool |
| `forge_kit/gk/lockers_nrm.png` | png | 1.21 MB | `f13fa4d85ffe148777ed08fbc2166819` | — | Tool/source lockers_nrm.png | — | tool |
| `forge_kit/gk/lockers_orm.png` | png | 869.8 KB | `8273d0a918d22cf66c4c6ac9af062eda` | — | Tool/source lockers_orm.png | — | tool |
| `forge_kit/gk/lockers_orm_src.png` | png | 2.17 MB | `905e3fa942e36d3dde6f43019c2a5e1e` | — | Tool/source lockers_orm_src.png | — | tool |
| `forge_kit/gk/lockers_raw.glb` | glb | 533.7 KB | `8da56b0dcb20554c34f5775f393dac26` | tris=7900; meshes=Mesh_0.001 | Tool/source lockers_raw.glb | — | tool |
| `forge_kit/gk/lockers_rawj.glb` | glb | 2.90 MB | `5b463693fea88fec3fd1a927e354d68d` | tris=7900; meshes=Mesh_0.001 | Tool/source lockers_rawj.glb | — | tool |
| `forge_kit/gk/log_couch.txt` | txt | 2.8 KB | `568bfc3e96a6fba07ce2ca9ef98f020c` | — | Tool/source log_couch.txt | — | tool |
| `forge_kit/gk/log_desk.txt` | txt | 2.8 KB | `9b5cdd604d852e5f800f8f22c3a12be9` | — | Tool/source log_desk.txt | — | tool |
| `forge_kit/gk/log_kitchen.txt` | txt | 2.9 KB | `ba63a8cd37baef7e0829648491281c6a` | — | Tool/source log_kitchen.txt | — | tool |
| `forge_kit/gk/log_lockers.txt` | txt | 2.9 KB | `f1966c5fa35e52e3b482378eb54486c7` | — | Tool/source log_lockers.txt | — | tool |
| `forge_kit/gk/out/couch_raw.quest-ktx2.glb` | glb | 942.5 KB | `85d45e5db4074ebc15b28b1f6a0be5df` | tris=5500; meshes=Mesh_0.001 | Tool/source couch_raw.quest-ktx2.glb | — | tool |
| `forge_kit/gk/out/couch_raw.quest.glb` | glb | 284.5 KB | `309d8838c352d80999b6b365aa87dcd4` | tris=5500; meshes=Mesh_0.001 | Tool/source couch_raw.quest.glb | — | tool |
| `forge_kit/gk/out/desk_raw.quest-ktx2.glb` | glb | 1.11 MB | `f548968c8066d8c369febdd54ea23b76` | tris=5494; meshes=Mesh_0.001 | Tool/source desk_raw.quest-ktx2.glb | — | tool |
| `forge_kit/gk/out/desk_raw.quest.glb` | glb | 365.6 KB | `439b9a5158de412a41e018d7f27606b0` | tris=5494; meshes=Mesh_0.001 | Tool/source desk_raw.quest.glb | — | tool |
| `forge_kit/gk/out/kitchen_raw.quest-ktx2.glb` | glb | 782.6 KB | `82593955e5ac2a67f991c032205e0fca` | tris=7800; meshes=Mesh_0.001 | Tool/source kitchen_raw.quest-ktx2.glb | — | tool |
| `forge_kit/gk/out/kitchen_raw.quest.glb` | glb | 227.1 KB | `24e1e90681776de37f1a1660b6d39a9f` | tris=7800; meshes=Mesh_0.001 | Tool/source kitchen_raw.quest.glb | — | tool |
| `forge_kit/gk/out/lockers_raw.quest-ktx2.glb` | glb | 1.15 MB | `7fd22804ba90af550c77e6f60c8231ed` | tris=7896; meshes=Mesh_0.001 | Tool/source lockers_raw.quest-ktx2.glb | — | tool |
| `forge_kit/gk/out/lockers_raw.quest.glb` | glb | 304.6 KB | `f56d0ae7d4bbf833ab317722475aaa4f` | tris=7896; meshes=Mesh_0.001 | Tool/source lockers_raw.quest.glb | — | tool |
| `forge_kit/gk/outj/couch_rawj.quest-ktx2.glb` | glb | 1004.2 KB | `6447a9cd67bc86006b6c01085e656482` | tris=5500; meshes=Mesh_0.001 | Tool/source couch_rawj.quest-ktx2.glb | — | tool |
| `forge_kit/gk/outj/couch_rawj.quest.glb` | glb | 2.65 MB | `bff86a0258ef0daa5d8ac9a57e89d1bf` | tris=5500; meshes=Mesh_0.001 | Tool/source couch_rawj.quest.glb | — | tool |
| `forge_kit/gk/outj/desk_rawj.quest-ktx2.glb` | glb | 1.19 MB | `51fd6547d38578258c5c6b0ed3025717` | tris=5494; meshes=Mesh_0.001 | Tool/source desk_rawj.quest-ktx2.glb | — | tool |
| `forge_kit/gk/outj/desk_rawj.quest.glb` | glb | 2.96 MB | `d4513a074bd603d16b9ed5df35e52a9a` | tris=5494; meshes=Mesh_0.001 | Tool/source desk_rawj.quest.glb | — | tool |
| `forge_kit/gk/outj/kitchen_rawj.quest-ktx2.glb` | glb | 981.8 KB | `10ea861eadb93d7ed8b490993c610c27` | tris=7800; meshes=Mesh_0.001 | Tool/source kitchen_rawj.quest-ktx2.glb | — | tool |
| `forge_kit/gk/outj/kitchen_rawj.quest.glb` | glb | 2.84 MB | `e8f6f9a49e960e61c957dc622c70c83b` | tris=7800; meshes=Mesh_0.001 | Tool/source kitchen_rawj.quest.glb | — | tool |
| `forge_kit/gk/outj/lockers_rawj.quest-ktx2.glb` | glb | 1.22 MB | `5c0d3c224dbee6b1220ad71fe00b7d5a` | tris=7896; meshes=Mesh_0.001 | Tool/source lockers_rawj.quest-ktx2.glb | — | tool |
| `forge_kit/gk/outj/lockers_rawj.quest.glb` | glb | 2.68 MB | `76cbb637ea3923e01b9375428ff0a4c6` | tris=7896; meshes=Mesh_0.001 | Tool/source lockers_rawj.quest.glb | — | tool |
| `forge_kit/gk/q.py` | py | 596 B | `e574d9071b3760828dd91b3448d38b5e` | — | Tool/source q.py | — | tool |
| `forge_kit/gk/scr.py` | py | 400 B | `1a553eb82d8e54213d87be292747efb4` | — | Tool/source scr.py | — | tool |
| `forge_kit/gk/screen_uv.json` | json | 3.3 KB | `4f8b63444ba539cab125735fb96f3929` | — | Tool/source screen_uv.json | — | tool |
| `forge_kit/gk/sheet.png` | png | 1.09 MB | `fb09d581b888213cc86cb3312103df48` | — | Tool/source sheet.png | — | tool |
| `forge_kit/gk/t_couch.png` | png | 700.5 KB | `c400bd9fb3635216ceca0333fa6fd0ff` | — | Tool/source t_couch.png | — | tool |
| `forge_kit/gk/t_desk.png` | png | 697.7 KB | `ab440dd100fac4c13a4c43d88271afa7` | — | Tool/source t_desk.png | — | tool |
| `forge_kit/gk/t_desk2.png` | png | 815.7 KB | `0903ae0f95778e8897f9012573071ad2` | — | Tool/source t_desk2.png | — | tool |
| `forge_kit/gk/t_kitchen.png` | png | 714.4 KB | `c9d2745c89af09cdd7dd5750e5974763` | — | Tool/source t_kitchen.png | — | tool |
| `forge_kit/gk/t_lockers.png` | png | 730.5 KB | `89a5537aa75c57aa7d64833a45ef57bf` | — | Tool/source t_lockers.png | — | tool |
| `forge_kit/gk/t_tv.png` | png | 647.6 KB | `f6f80b950a1a4cefb6800dc2fead12e2` | — | Tool/source t_tv.png | — | tool |
| `forge_kit/gk/tsheet1.png` | png | 585.6 KB | `983502f7d31bfc48857bd7314be4fe04` | — | Tool/source tsheet1.png | — | tool |
| `forge_kit/gk/tsheet2.png` | png | 583.9 KB | `ad13f16eace4ef780490d20754d5a251` | — | Tool/source tsheet2.png | — | tool |
| `forge_kit/gk/tsheet3.png` | png | 527.4 KB | `be0fe8618db3a2eab788bfe72577c928` | — | Tool/source tsheet3.png | — | tool |
| `forge_kit/gk/tv_raw.glb` | glb | 12.5 KB | `729b12cc9e195943fcc62f7aa7d73562` | tris=86; meshes=screen,tv_body | Tool/source tv_raw.glb | — | tool |
| `forge_kit/gr8/anika_back.png` | png | 847.4 KB | `582e6fedb9a0df9fbce5b6e2715455a6` | — | Tool/source anika_back.png | — | tool |
| `forge_kit/gr8/anika_build.log` | log | 29.7 KB | `46a90b5dff6941e9ea2cb549b5a7f7da` | — | Tool/source anika_build.log | — | tool |
| `forge_kit/gr8/anika_front.png` | png | 864.3 KB | `e9aebe4fcfa9f5504031e77355aacf16` | — | Tool/source anika_front.png | — | tool |
| `forge_kit/gr8/anika_pieces.blend` | blend | 27.65 MB | `0c5892386864f0a3129fad6c609c07ab` | — | Tool/source anika_pieces.blend | — | tool |
| `forge_kit/gr8/anika_prep.log` | log | 2.5 KB | `897ffd913c2f97615db3c3b72488750e` | — | Tool/source anika_prep.log | — | tool |
| `forge_kit/gr8/anika_sheet.png` | png | 1.38 MB | `364b0fd4e0a895cb5bb33e84fcca22e6` | — | Tool/source anika_sheet.png | — | tool |
| `forge_kit/gr8/anika_side.png` | png | 723.1 KB | `cbaa03ae5fb8b53c307798b296704566` | — | Tool/source anika_side.png | — | tool |
| `forge_kit/gr8/bb.py` | py | 635 B | `1ee77ad42194b09d843e482001753a24` | — | Tool/source bb.py | — | tool |
| `forge_kit/gr8/build_gr8.py` | py | 15.4 KB | `14f289e1d3ae4014a1e172740808b7fd` | — | Tool/source build_gr8.py | — | tool |
| `forge_kit/gr8/caali_back.png` | png | 850.7 KB | `4ec8d08d15e4861276784bc822091d0b` | — | Tool/source caali_back.png | — | tool |
| `forge_kit/gr8/caali_build.log` | log | 46.2 KB | `b60f2a3f13e88280ebe3fa0cc713d016` | — | Tool/source caali_build.log | — | tool |
| `forge_kit/gr8/caali_front.png` | png | 903.7 KB | `c5eccae1946700a3abbea09a180783e5` | — | Tool/source caali_front.png | — | tool |
| `forge_kit/gr8/caali_pieces.blend` | blend | 40.73 MB | `01204c67b0ebdfd558ef8c5eb60045e5` | — | Tool/source caali_pieces.blend | — | tool |
| `forge_kit/gr8/caali_prep.log` | log | 2.8 KB | `ee3a1a79a61cda112b6c018aab0f8eab` | — | Tool/source caali_prep.log | — | tool |
| `forge_kit/gr8/caali_sheet.png` | png | 1.47 MB | `937c2f930451a145bce857580bc272e3` | — | Tool/source caali_sheet.png | — | tool |
| `forge_kit/gr8/caali_side.png` | png | 766.4 KB | `1dc33876826f8ea1a7327cfea72d049b` | — | Tool/source caali_side.png | — | tool |
| `forge_kit/gr8/chk2.png` | png | 455.3 KB | `4c77efeddffcb3e6543603cfbfaee02e` | — | Tool/source chk2.png | — | tool |
| `forge_kit/gr8/chk_col.png` | png | 438.1 KB | `e91ca4af6f103deb3254e2243145a8c6` | — | Tool/source chk_col.png | — | tool |
| `forge_kit/gr8/chk_hero.png` | png | 913.5 KB | `b1379d3c4cfe35a0ac0024322d0edd53` | — | Tool/source chk_hero.png | — | tool |
| `forge_kit/gr8/chk_hero2.png` | png | 870.0 KB | `ee1d94bfd597b4d9ea4bf38c1c04c0a1` | — | Tool/source chk_hero2.png | — | tool |
| `forge_kit/gr8/chk_sk.png` | png | 1.11 MB | `8444cc991ac53e79325b3721c22fe23c` | — | Tool/source chk_sk.png | — | tool |
| `forge_kit/gr8/chk_tee.png` | png | 25.7 KB | `18bbef3bcfec2b9d6abf60c391ae576d` | — | Tool/source chk_tee.png | — | tool |
| `forge_kit/gr8/compose.py` | py | 624 B | `d4a5410d3b9537339ffdeb5578d69967` | — | Tool/source compose.py | — | tool |
| `forge_kit/gr8/compose2.py` | py | 662 B | `4c306946099af3784dda4195b2ee8602` | — | Tool/source compose2.py | — | tool |
| `forge_kit/gr8/dbg.py` | py | 349 B | `65499c5730f49b271eb9377087f54c32` | — | Tool/source dbg.py | — | tool |
| `forge_kit/gr8/decal_anika_back.png` | png | 1.00 MB | `7d3de268a23ef4a7d1c7e854ce515faa` | — | Tool/source decal_anika_back.png | — | tool |
| `forge_kit/gr8/decal_caali_back.png` | png | 1.01 MB | `2597932b1bead65a310258df0069a98f` | — | Tool/source decal_caali_back.png | — | tool |
| `forge_kit/gr8/decal_gr8yzone_tee.png` | png | 80.1 KB | `dc0767610df74a2226ff5ebd08c02747` | — | Tool/source decal_gr8yzone_tee.png | — | tool |
| `forge_kit/gr8/decals.py` | py | 1.8 KB | `787a277e5a40764ede8e60cd30449823` | — | Tool/source decals.py | — | tool |
| `forge_kit/gr8/export.py` | py | 1.6 KB | `008803490d8676f19771e2b5e1b16789` | — | Tool/source export.py | — | tool |
| `forge_kit/gr8/fix/fixrider.py` | py | 12.5 KB | `aa4a454b5366dea12c699c18ad9d5335` | — | Tool/source fixrider.py | — | tool |
| `forge_kit/gr8/fix/glbio.py` | py | 1.7 KB | `1b2a15fb8ca4097c742d2ec754131ebb` | — | Tool/source glbio.py | — | tool |
| `forge_kit/gr8/fix/measure.py` | py | 2.2 KB | `3f86424daed0cb2e32c893bab5a203da` | — | Tool/source measure.py | — | tool |
| `forge_kit/gr8/fix/pa.png` | png | 37.1 KB | `d0ac2c1e7545524042d30aa628c0662f` | — | Tool/source pa.png | — | tool |
| `forge_kit/gr8/fix/pc.png` | png | 46.4 KB | `30743cb69dacfc71d707e8a2c2cc9bdd` | — | Tool/source pc.png | — | tool |
| `forge_kit/gr8/fix/plot.py` | py | 978 B | `38b3ceacfe4a196972cf6c7ddc69ab18` | — | Tool/source plot.py | — | tool |
| `forge_kit/gr8/fix/pp.png` | png | 247.8 KB | `fabd9a2b3633ddc73323e44270e703bf` | — | Tool/source pp.png | — | tool |
| `forge_kit/gr8/fix/probe.py` | py | 2.9 KB | `6f855eedb3d4ba5ec2115c356723d64f` | — | Tool/source probe.py | — | tool |
| `forge_kit/gr8/fix/skate_bake.py` | py | 1.5 KB | `c462bdfb23f1009d7ccb5dd7b0b24288` | — | Tool/source skate_bake.py | — | tool |
| `forge_kit/gr8/fix/skate_lift.py` | py | 1.6 KB | `e95fbf0c487c0d16f820c6f8d90d5c51` | — | Tool/source skate_lift.py | — | tool |
| `forge_kit/gr8/fix/skate_shot.py` | py | 3.4 KB | `a84a002d5f4df3c00d33f703c4da86d8` | — | Tool/source skate_shot.py | — | tool |
| `forge_kit/gr8/fix/sockgap.py` | py | 2.3 KB | `217e7c860f26320defb2c12cb8563f1d` | — | Tool/source sockgap.py | — | tool |
| `forge_kit/gr8/fixorm.py` | py | 768 B | `2c3b52939cdca301839d5e7e8becc306` | — | Tool/source fixorm.py | — | tool |
| `forge_kit/gr8/glbinspect.py` | py | 827 B | `aafca2d607d839d4f134ff777c5c7b5c` | — | Tool/source glbinspect.py | — | tool |
| `forge_kit/gr8/hero.py` | py | 2.7 KB | `3c8ff31f4c2da8f5e03d89f13a9e6294` | — | Tool/source hero.py | — | tool |
| `forge_kit/gr8/hero_glb.py` | py | 3.4 KB | `9f7cb7d8be6327d31c92224046eab1c2` | — | Tool/source hero_glb.py | — | tool |
| `forge_kit/gr8/hero_ply.py` | py | 3.2 KB | `983188f98fe43964fb528fab1b8c6c5a` | — | Tool/source hero_ply.py | — | tool |
| `forge_kit/gr8/hero_ply2.py` | py | 3.4 KB | `05ad3ee4bbdd231aec8c93c4ce7d4942` | — | Tool/source hero_ply2.py | — | tool |
| `forge_kit/gr8/hero_ply3.py` | py | 3.5 KB | `884043b053b217010e0f9d93d7aabd9e` | — | Tool/source hero_ply3.py | — | tool |
| `forge_kit/gr8/heroes.log` | log | 276 B | `f2448727c7ce6c60001dbd0cc5aea983` | — | Tool/source heroes.log | — | tool |
| `forge_kit/gr8/heroes.sh` | sh | 588 B | `295e060b929dabe7007f76b49a1101a2` | — | Tool/source heroes.sh | — | tool |
| `forge_kit/gr8/pieces.py` | py | 2.0 KB | `0159b0800e3016d8c7d01ac519434030` | — | Tool/source pieces.py | — | tool |
| `forge_kit/gr8/prep.py` | py | 1.8 KB | `939377764114ca7b84d540728f4e9443` | — | Tool/source prep.py | — | tool |
| `forge_kit/gr8/qc.png` | png | 291.1 KB | `69ac24ed558481cf68c55f53ad2cd315` | — | Tool/source qc.png | — | tool |
| `forge_kit/gr8/qc.py` | py | 872 B | `0a9a6e34cbf73ea09c20c5b700a63759` | — | Tool/source qc.py | — | tool |
| `forge_kit/gr8/qc_a0.png` | png | 798.0 KB | `ecc80c7bf26c4ba7cafbc515ba28c8c8` | — | Tool/source qc_a0.png | — | tool |
| `forge_kit/gr8/qc_c0.png` | png | 795.9 KB | `59eca5225e711606997be905ae5f0462` | — | Tool/source qc_c0.png | — | tool |
| `forge_kit/gr8/qcs.sh` | sh | 272 B | `e2a538bccf0f6acfb6be0e8d0eb6c4f2` | — | Tool/source qcs.sh | — | tool |
| `forge_kit/gr8/qv.py` | py | 838 B | `c06077373975a44f8968a1f9adfdf385` | — | Tool/source qv.py | — | tool |
| `forge_kit/gr8/qv_a2.png` | png | 1.11 MB | `a87ad22d96a7f6603577e08da5d60604` | — | Tool/source qv_a2.png | — | tool |
| `forge_kit/gr8/qv_a2_back.png` | png | 688.4 KB | `e741bb06956078f66810c8af4fd9f3b2` | — | Tool/source qv_a2_back.png | — | tool |
| `forge_kit/gr8/qv_a2_front.png` | png | 705.1 KB | `869ac00dd7f6d2c78120ddfbb8460923` | — | Tool/source qv_a2_front.png | — | tool |
| `forge_kit/gr8/qv_a2_q.png` | png | 721.3 KB | `e966bec62b253e926ca69eff8b9511a8` | — | Tool/source qv_a2_q.png | — | tool |
| `forge_kit/gr8/qv_s_back.png` | png | 597.1 KB | `513daef5a802e84b289d4063cb99b8a4` | — | Tool/source qv_s_back.png | — | tool |
| `forge_kit/gr8/qv_s_front.png` | png | 587.8 KB | `9fb80b941188aa6399303da57dbea551` | — | Tool/source qv_s_front.png | — | tool |
| `forge_kit/gr8/qv_s_q.png` | png | 597.6 KB | `763adfd470e77dcb6aa6db063d1ba964` | — | Tool/source qv_s_q.png | — | tool |
| `forge_kit/gr8/qz.py` | py | 656 B | `6d2e5da578235c9b163d97b0bff065e7` | — | Tool/source qz.py | — | tool |
| `forge_kit/gr8/qz2.png` | png | 521.6 KB | `489d3e99fb2984587a9c36081b4533c2` | — | Tool/source qz2.png | — | tool |
| `forge_kit/gr8/qz_cfeet.png` | png | 456.6 KB | `b5e8e5fed3854eeca37b84101bbe7d57` | — | Tool/source qz_cfeet.png | — | tool |
| `forge_kit/gr8/qz_feet.png` | png | 381.1 KB | `0181d929d67a07f7d5449a0b6a647b97` | — | Tool/source qz_feet.png | — | tool |
| `forge_kit/gr8/qz_red.png` | png | 471.8 KB | `a4c73c4b3a7313deabb3a04948870a02` | — | Tool/source qz_red.png | — | tool |
| `forge_kit/gr8/qz_red.py` | py | 898 B | `ca4d0b865e1ce73ada325d2d20a5cff0` | — | Tool/source qz_red.py | — | tool |
| `forge_kit/gr8/runall.log` | log | 22 B | `688440bf70a0489222c651e9322b4e92` | — | Tool/source runall.log | — | tool |
| `forge_kit/gr8/runall.sh` | sh | 800 B | `43f27307230307fe7d6d4b8ee88b97cb` | — | Tool/source runall.sh | — | tool |
| `forge_kit/gr8/ship.sh` | sh | 790 B | `d654c089162a7fb061b24f0bf4809159` | — | Tool/source ship.sh | — | tool |
| `forge_kit/gr8/sk2.py` | py | 649 B | `7b6cffa3964dd5daab5e4e82257780c1` | — | Tool/source sk2.py | — | tool |
| `forge_kit/gr8/sk3.py` | py | 599 B | `44eb327df33f7f70c927ca1b96831222` | — | Tool/source sk3.py | — | tool |
| `forge_kit/gr8/sk4.py` | py | 722 B | `9f45c0eb04ef2d643e978721368c64e6` | — | Tool/source sk4.py | — | tool |
| `forge_kit/gr8/sk5.png` | png | 311.7 KB | `4a660da9a580b1d473714cff2b4477a0` | — | Tool/source sk5.png | — | tool |
| `forge_kit/gr8/sk5.py` | py | 989 B | `dc398db984f25fef173f7784dccf6a5a` | — | Tool/source sk5.py | — | tool |
| `forge_kit/gr8/sk6.png` | png | 406.5 KB | `f494ff573e09879484450d5c214c3974` | — | Tool/source sk6.png | — | tool |
| `forge_kit/gr8/sk6.py` | py | 866 B | `9c49f941dd5965f29532cfeaf8f467b9` | — | Tool/source sk6.py | — | tool |
| `forge_kit/gr8/sk6a.png` | png | 341.9 KB | `57d26099ed39be9792790ae7cdeaa86e` | — | Tool/source sk6a.png | — | tool |
| `forge_kit/gr8/sk6b.png` | png | 267.9 KB | `f0605d700917171469e109217083a42c` | — | Tool/source sk6b.png | — | tool |
| `forge_kit/gr8/test_anika.log` | log | 6.0 KB | `64702357a336613c7f3699a20d64a932` | — | Tool/source test_anika.log | — | tool |
| `forge_kit/gr8/tex/anika_LOD0_col.png` | png | 4.06 MB | `62bae5c7b62c28156f95cfc2509fe3de` | — | Tool/source anika_LOD0_col.png | — | tool |
| `forge_kit/gr8/tex/anika_LOD0_nrm.png` | png | 1.14 MB | `3c4190d1de3e36e39f29eb275b708f2e` | — | Tool/source anika_LOD0_nrm.png | — | tool |
| `forge_kit/gr8/tex/anika_LOD0_orm.png` | png | 768.8 KB | `c29ec48959bff1b52b6c69a7656673dd` | — | Tool/source anika_LOD0_orm.png | — | tool |
| `forge_kit/gr8/tex/anika_LOD1_col.png` | png | 1.44 MB | `89bf89f975eb2b84007ba78bdfe92eea` | — | Tool/source anika_LOD1_col.png | — | tool |
| `forge_kit/gr8/tex/anika_LOD1_nrm.png` | png | 413.8 KB | `1e787c150963ee0a3a336cc86e3bd256` | — | Tool/source anika_LOD1_nrm.png | — | tool |
| `forge_kit/gr8/tex/anika_LOD1_orm.png` | png | 255.9 KB | `fab204e69bd84f9642f8930e06f69e98` | — | Tool/source anika_LOD1_orm.png | — | tool |
| `forge_kit/gr8/tex/anika_LOD2_col.png` | png | 438.8 KB | `31c9816ea32702ad999b702220047966` | — | Tool/source anika_LOD2_col.png | — | tool |
| `forge_kit/gr8/tex/anika_LOD2_nrm.png` | png | 127.1 KB | `df32ab4a91f57439db995d45cc46d7ba` | — | Tool/source anika_LOD2_nrm.png | — | tool |
| `forge_kit/gr8/tex/anika_LOD2_orm.png` | png | 76.9 KB | `7f0f84835c47b9f13179540e256a89bd` | — | Tool/source anika_LOD2_orm.png | — | tool |
| `forge_kit/gr8/tex/anika_NPC0_col.png` | png | 1.43 MB | `c17e8f6bfc6661932bfaee6dd869889d` | — | Tool/source anika_NPC0_col.png | — | tool |
| `forge_kit/gr8/tex/anika_NPC0_nrm.png` | png | 1.33 MB | `f16513389c974bfcb7ae43155a04ba86` | — | Tool/source anika_NPC0_nrm.png | — | tool |
| `forge_kit/gr8/tex/anika_NPC0_orm.png` | png | 889.4 KB | `4e62b46912335acf36ebe80af14a9d6e` | — | Tool/source anika_NPC0_orm.png | — | tool |
| `forge_kit/gr8/tex/caali_HD0_col.png` | png | 10.45 MB | `6b69c3dedd3173ae19689af26e566c0f` | — | Tool/source caali_HD0_col.png | — | tool |
| `forge_kit/gr8/tex/caali_HD0_nrm.png` | png | 3.32 MB | `5f7ae8f137a3143c940ba024604814cf` | — | Tool/source caali_HD0_nrm.png | — | tool |
| `forge_kit/gr8/tex/caali_HD0_orm.png` | png | 2.79 MB | `28bd16f5dd1f4b9325942064bd56e29d` | — | Tool/source caali_HD0_orm.png | — | tool |
| `forge_kit/gr8/tex/caali_LOD0_col.png` | png | 3.90 MB | `5b74f7f3c73c44448226e6125510c512` | — | Tool/source caali_LOD0_col.png | — | tool |
| `forge_kit/gr8/tex/caali_LOD0_nrm.png` | png | 1.22 MB | `bb46359f1bf8482b14c9bfec34d35f0b` | — | Tool/source caali_LOD0_nrm.png | — | tool |
| `forge_kit/gr8/tex/caali_LOD0_orm.png` | png | 1.01 MB | `fb16b37c06249649e8d01bdce04092a3` | — | Tool/source caali_LOD0_orm.png | — | tool |
| `forge_kit/gr8/tex/caali_LOD1_col.png` | png | 1.35 MB | `7b43e4b9e387fc6f1bdacafabba3bd33` | — | Tool/source caali_LOD1_col.png | — | tool |
| `forge_kit/gr8/tex/caali_LOD1_nrm.png` | png | 417.2 KB | `f7b2fc42403951bb76132c185354af21` | — | Tool/source caali_LOD1_nrm.png | — | tool |
| `forge_kit/gr8/tex/caali_LOD1_orm.png` | png | 320.7 KB | `500df249a50d9ba1b409de51e7a6c9db` | — | Tool/source caali_LOD1_orm.png | — | tool |
| `forge_kit/gr8/tex/caali_LOD2_col.png` | png | 405.2 KB | `7077f8e9a091e53ad11d05c637cab729` | — | Tool/source caali_LOD2_col.png | — | tool |
| `forge_kit/gr8/tex/caali_LOD2_nrm.png` | png | 126.0 KB | `ca9e88b21847e9861acddf2a1f599b97` | — | Tool/source caali_LOD2_nrm.png | — | tool |
| `forge_kit/gr8/tex/caali_LOD2_orm.png` | png | 91.8 KB | `a8f2f76e68bdc3014266cd692b687c51` | — | Tool/source caali_LOD2_orm.png | — | tool |
| `forge_kit/out/drone_raw.quest-ktx2.glb` | glb | 14.0 KB | `5966baae0a370f489087390a085b18d3` | tris=972; meshes=drone_body,rotor_BL,rotor_BR,rotor_FL | Tool/source drone_raw.quest-ktx2.glb | — | tool |
| `forge_kit/out/drone_raw.quest.glb` | glb | 14.9 KB | `137e70c0fb507b68ae29281c66b40f1f` | tris=972; meshes=drone_body,rotor_BL,rotor_BR,rotor_FL | Tool/source drone_raw.quest.glb | — | tool |
| `forge_kit/out/pod_raw.quest-ktx2.glb` | glb | 18.8 KB | `8d5e4f6cbe490fc0280ad56e00bd9c8e` | tris=2756; meshes=pod | Tool/source pod_raw.quest-ktx2.glb | — | tool |
| `forge_kit/out/pod_raw.quest.glb` | glb | 19.7 KB | `303b6490c062474897bb0496ad1939bd` | tris=2756; meshes=pod | Tool/source pod_raw.quest.glb | — | tool |
| `forge_kit/out2/pod_closed_raw.quest-ktx2.glb` | glb | 20.8 KB | `86726a710869697aef1027ccfd346371` | tris=2468; meshes=pod | Tool/source pod_closed_raw.quest-ktx2.glb | — | tool |
| `forge_kit/out2/pod_closed_raw.quest.glb` | glb | 34.5 KB | `788429aa255b527bee164e40e3315923` | tris=2468; meshes=pod | Tool/source pod_closed_raw.quest.glb | — | tool |
| `forge_kit/out2/pod_raw.quest-ktx2.glb` | glb | 22.0 KB | `43dc99f3d6893fe4416e5a867bd89791` | tris=2756; meshes=pod | Tool/source pod_raw.quest-ktx2.glb | — | tool |
| `forge_kit/out2/pod_raw.quest.glb` | glb | 35.8 KB | `2405e724878ba180b2dfe2eaee82e91c` | tris=2756; meshes=pod | Tool/source pod_raw.quest.glb | — | tool |
| `forge_kit/pal_col.png` | png | 4.2 KB | `5b02713f63523c01f4a6e7999ba74122` | — | Tool/source pal_col.png | — | tool |
| `forge_kit/pal_em.png` | png | 3.6 KB | `45bd8398bc900137fcddcc3a6d0c8b7f` | — | Tool/source pal_em.png | — | tool |
| `forge_kit/pal_orm.png` | png | 5.2 KB | `7421093d8aba31691beabf08d770d1d4` | — | Tool/source pal_orm.png | — | tool |
| `forge_kit/pod_closed_raw.glb` | glb | 98.3 KB | `ad1891ea286d59d54fc6f53d12f94c97` | tris=2468; meshes=pod | Tool/source pod_closed_raw.glb | — | tool |
| `forge_kit/pod_raw.glb` | glb | 104.5 KB | `4b521ad8c72aeb221311efb0cb62d3aa` | tris=2756; meshes=pod | Tool/source pod_raw.glb | — | tool |
| `forge_kit/pvA.png` | png | 757.5 KB | `865f29906e6a4317a497102876d4923c` | — | Tool/source pvA.png | — | tool |
| `forge_kit/pvB.png` | png | 752.3 KB | `8148c558875f9a14b63ff64927fb102d` | — | Tool/source pvB.png | — | tool |
| `forge_kit/pv_drone.png` | png | 790.0 KB | `b72722cb16cb67f3f5942f7bdb1b5b9a` | — | Tool/source pv_drone.png | — | tool |
| `forge_kit/pv_drone2.png` | png | 790.0 KB | `b72722cb16cb67f3f5942f7bdb1b5b9a` | — | Tool/source pv_drone2.png | — | tool |
| `forge_kit/pv_pod.png` | png | 802.0 KB | `a650274af93a07f228c8b18548c52449` | — | Tool/source pv_pod.png | — | tool |
| `forge_kit/pv_pod2.png` | png | 802.0 KB | `a650274af93a07f228c8b18548c52449` | — | Tool/source pv_pod2.png | — | tool |
| `forge_kit/pv_pod3.png` | png | 813.7 KB | `d6d8a1dd190b1cfcc6bbc10b4bde3ab0` | — | Tool/source pv_pod3.png | — | tool |
| `forge_kit/render.py` | py | 2.0 KB | `0a11ac3875a1b642b6f1fe96d16ba772` | — | Tool/source render.py | — | tool |
| `forge_kit/render_neutral.py` | py | 2.0 KB | `2fa6f2eb7c3d38d9a5e3fe0c0e5872a9` | — | Tool/source render_neutral.py | — | tool |
| `forge_kit/skate/at-skate-meshy.merged.v2.raw.glb` | glb | 2.87 MB | `0da8b3d356cb5c0daf54661b75a9a46e` | tris=25534; joints=2; LODs=ATSkate_LOD0,ATSkate_LOD1,ATSkate_LOD2 | Tool/source at-skate-meshy.merged.v2.raw.glb | — | tool |
| `forge_kit/skate/at-skate-meshy.v2.raw.glb` | glb | 896.9 KB | `5afa6b984c1a05e9d3be10d064204c7b` | tris=12767; LODs=ShellBlend_L0,Wheel_F_L0,Wheel_R_L0,ShellBlend_L1,Wheel_F_L1,Wheel_R_L1 | Tool/source at-skate-meshy.v2.raw.glb | — | tool |
| `forge_kit/skate/bake_col.png` | png | 1.20 MB | `dc7a240ed626732d19303147f4a73000` | — | Tool/source bake_col.png | — | tool |
| `forge_kit/skate/bake_mr.png` | png | 1.06 MB | `12b110b15c97c3e03991bf91f4a2ed84` | — | Tool/source bake_mr.png | — | tool |
| `forge_kit/skate/bake_nrm.png` | png | 1.14 MB | `5d9ca85769da79c3da7815a2983b20a8` | — | Tool/source bake_nrm.png | — | tool |
| `forge_kit/skate/bl.py` | py | 493 B | `a66642d8e1a51e2ed901f53e8ece02dc` | — | Tool/source bl.py | — | tool |
| `forge_kit/skate/build_skate.py` | py | 4.6 KB | `64eea3f8ec480c3da6ac85cdd66dab7f` | — | Tool/source build_skate.py | — | tool |
| `forge_kit/skate/cmp.png` | png | 1.05 MB | `b3ea70e8cdc2d1c402ca87a26f934901` | — | Tool/source cmp.png | — | tool |
| `forge_kit/skate/cmp2.png` | png | 986.4 KB | `ed1d23f25d8643efeb4da6a47f9edb33` | — | Tool/source cmp2.png | — | tool |
| `forge_kit/skate/cmp_small.png` | png | 1.07 MB | `b205281f2dcfee83f354f8097e0f4647` | — | Tool/source cmp_small.png | — | tool |
| `forge_kit/skate/cmp_small2.png` | png | 885.7 KB | `e6f7a994e7b75f54b29a110f13be4194` | — | Tool/source cmp_small2.png | — | tool |
| `forge_kit/skate/diag.py` | py | 1.6 KB | `d37f3b615f85e34730a9e9e4eb988743` | — | Tool/source diag.py | — | tool |
| `forge_kit/skate/diag2.py` | py | 1.3 KB | `5d8474636f061c99434ba068e3d787a8` | — | Tool/source diag2.py | — | tool |
| `forge_kit/skate/diag3.py` | py | 689 B | `97b1c2627e6ba30b79998df500171720` | — | Tool/source diag3.py | — | tool |
| `forge_kit/skate/dump.py` | py | 447 B | `88be2e3a0e0e6618fc254802edbe984a` | — | Tool/source dump.py | — | tool |
| `forge_kit/skate/look.py` | py | 1.4 KB | `c0d83f971d1f738aaf5e93be3adeb34a` | — | Tool/source look.py | — | tool |
| `forge_kit/skate/old.png` | png | 761.7 KB | `cb5a2b45658471bf644b93a760d74f22` | — | Tool/source old.png | — | tool |
| `forge_kit/skate/old_pts.npy` | npy | 42.6 KB | `31d710405ec6d2b7eb6c038fa451f1ef` | — | Tool/source old_pts.npy | — | tool |
| `forge_kit/skate/pv.py` | py | 1.4 KB | `2874dc6a31d404c4ca57d1e6ac349931` | — | Tool/source pv.py | — | tool |
| `forge_kit/skate/pv_shell0.png` | png | 698.4 KB | `7ffc12747d75355ddf3794a716c0e4d6` | — | Tool/source pv_shell0.png | — | tool |
| `forge_kit/skate/pv_shell0b.png` | png | 742.7 KB | `1ee4fc5e6004762e69a410429642c9d9` | — | Tool/source pv_shell0b.png | — | tool |
| `forge_kit/skate/pv_shell0c.png` | png | 745.2 KB | `33281a3e906350485f82c36e0b2142da` | — | Tool/source pv_shell0c.png | — | tool |
| `forge_kit/skate/pv_shell0d.png` | png | 744.4 KB | `8886030fc501d37d0e11a772a682bce5` | — | Tool/source pv_shell0d.png | — | tool |
| `forge_kit/skate/pv_shell0e.png` | png | 747.8 KB | `e41cf3600a3d1c0f860ed9eab9cc00ee` | — | Tool/source pv_shell0e.png | — | tool |
| `forge_kit/skate/pv_shell0f.png` | png | 748.6 KB | `d538ab0c83527e44cb0a2be56c9330fe` | — | Tool/source pv_shell0f.png | — | tool |
| `forge_kit/skate/q/at-skate-meshy.merged.v2.raw.quest.glb` | glb | 187.8 KB | `26ce0c8813664072f8d16b8cfa84d606` | tris=25534; joints=2; LODs=ATSkate_LOD0,ATSkate_LOD1,ATSkate_LOD2 | Tool/source at-skate-meshy.merged.v2.raw.quest.glb | — | tool |
| `forge_kit/skate/q/at-skate-meshy.v2.raw.quest.glb` | glb | 102.4 KB | `3107500683a015d5ad308eb9a1db0b16` | tris=12767; LODs=ShellBlend_L0,Wheel_F_L0,Wheel_R_L0,ShellBlend_L1,Wheel_F_L1,Wheel_R_L1 | Tool/source at-skate-meshy.v2.raw.quest.glb | — | tool |
| `forge_kit/skate/q2.py` | py | 551 B | `61e85c2ab85cfec4c601add72090c27f` | — | Tool/source q2.py | — | tool |
| `forge_kit/skate/r_new_34.png` | png | 1.36 MB | `464f7e3f718211d7f053562739b8787f` | — | Tool/source r_new_34.png | — | tool |
| `forge_kit/skate/r_new_side.png` | png | 1.38 MB | `27233e3962ffbd19429071218b9c9ce6` | — | Tool/source r_new_side.png | — | tool |
| `forge_kit/skate/r_old_34.png` | png | 1.41 MB | `43ccf39f220fce6c0e4944d4501540d5` | — | Tool/source r_old_34.png | — | tool |
| `forge_kit/skate/r_old_side.png` | png | 1.43 MB | `812ebd8614f4fd17dd8b5bc19470ca1e` | — | Tool/source r_old_side.png | — | tool |
| `forge_kit/skate/rad.py` | py | 679 B | `f0c4c57a353cdb374cc847d233235178` | — | Tool/source rad.py | — | tool |
| `forge_kit/skate/rcmp.py` | py | 2.5 KB | `a8b08b5daf0240d86ffb4c1ba7d3ece5` | — | Tool/source rcmp.py | — | tool |
| `forge_kit/skate/refcrop.png` | png | 553.5 KB | `6f0895b4b64a231d687173f48ef032e3` | — | Tool/source refcrop.png | — | tool |
| `forge_kit/skate/reg.py` | py | 1.6 KB | `d12c0d6a2287fc053964f8f779b69359` | — | Tool/source reg.py | — | tool |
| `forge_kit/skate/skate_v2_geo.npz` | npz | 744.2 KB | `4e388c6f34a7163f4c3aa33780cf5629` | — | Tool/source skate_v2_geo.npz | — | tool |
| `forge_kit/skate/skate_v2_work.blend` | blend | 7.58 MB | `f1e62a688665a0b3dd5a2556ba4badd0` | — | Tool/source skate_v2_work.blend | — | tool |
| `forge_kit/skate/skate_v2_work2.blend` | blend | 7.70 MB | `4ed7070e34edcd5e3c76d5167e392218` | — | Tool/source skate_v2_work2.blend | — | tool |
| `forge_kit/skate/slice.png` | png | 11.6 KB | `1c8eaeee629b424f4c6ffaf8b9a0d895` | — | Tool/source slice.png | — | tool |
| `forge_kit/skate/src.png` | png | 729.9 KB | `6c93682108614905ed41ecf94586cd8d` | — | Tool/source src.png | — | tool |
| `forge_kit/skate/src_front.png` | png | 745.7 KB | `c62faffd502079e2d8c1d5095e7f00c9` | — | Tool/source src_front.png | — | tool |
| `forge_kit/skate/src_img0.jpg` | jpg | 2.55 MB | `54d58ce081851d4dde76a13b8468e46e` | — | Tool/source src_img0.jpg | — | tool |
| `forge_kit/skate/src_img1.jpg` | jpg | 1.97 MB | `01a986dca86a551251b9f574947f6860` | — | Tool/source src_img1.jpg | — | tool |
| `forge_kit/skate/src_img2.jpg` | jpg | 1.76 MB | `b97c28217ceaa928bf9df791da42db19` | — | Tool/source src_img2.jpg | — | tool |
| `forge_kit/skate/src_pts.npy` | npy | 10.90 MB | `0f35e59eaba47970683265a7be034723` | — | Tool/source src_pts.npy | — | tool |
| `forge_kit/skate/src_top.png` | png | 638.1 KB | `e2a4abb68a19f6d3883ba0d1e2a90192` | — | Tool/source src_top.png | — | tool |
| `forge_kit/skate/texcmp.png` | png | 705.7 KB | `5e6572d1f81c48bcc490f5a22f1f9c5e` | — | Tool/source texcmp.png | — | tool |
| `forge_kit/skate/wh.py` | py | 622 B | `86a53573c6e81a838d5a41709cd1a640` | — | Tool/source wh.py | — | tool |
| `forge_kit/skate/wheels.npy` | npy | 224 B | `c33a3366c1e8f51a92f757f01da1b365` | — | Tool/source wheels.npy | — | tool |
| `forge_kit/skate/wheels_export.py` | py | 4.1 KB | `826a214434c1f3e221ccfa4af250e6f0` | — | Tool/source wheels_export.py | — | tool |
| `forge_kit/skate/write_glb.py` | py | 6.1 KB | `36f6a30b7b05bbcc8ee54cd85bfde99a` | — | Tool/source write_glb.py | — | tool |
| `forge_kit/skate/xf.npz` | npz | 1.1 KB | `94c3a68d1c584c2528dc27569f330333` | — | Tool/source xf.npz | — | tool |
| `forge_kit/tv.py` | py | 2.4 KB | `46abb59457b2f87dd1c844928682b66b` | — | Tool/source tv.py | — | tool |
| `skyrydahs-characters/REFERENCES.md` | md | 21.6 KB | `cbb7d1d883d50f2b01b36be8e0f75a6e` | — | REFERENCES.md | — | live |
| `skyrydahs-characters/anika/anika-npc.draco-webp.glb` | glb | 1.04 MB | `5ba883d0cc9e476eaa8c4bb56b1e8e6d` | tris=39296; joints=107; LODs=AnikaNPC_LOD1,AnikaNPC_LOD0,AnikaNPC_LOD2 | anika-npc.draco-webp.glb | — | live |
| `skyrydahs-characters/anika/anika-npc.glb` | glb | 5.35 MB | `d6e0231f12ecc5f28a790c2fc4addff2` | tris=39296; joints=107; LODs=AnikaNPC_LOD1,AnikaNPC_LOD0,AnikaNPC_LOD2 | Anika NPC | NPC roster | live |
| `skyrydahs-characters/anika/anika-npc.opt-ktx2.glb` | glb | 916.4 KB | `ebfbf40dcf251a1c3166cdc776e04638` | tris=39296; joints=107; LODs=AnikaNPC_LOD1,AnikaNPC_LOD0,AnikaNPC_LOD2 | anika-npc.opt-ktx2.glb | — | live |
| `skyrydahs-characters/anika/anika-npc.opt-ktx2.v1.glb` | glb | 1.91 MB | `a5186789d74bcea3ef7b06bbe715cb13` | tris=39296; joints=107; LODs=AnikaNPC_LOD1,AnikaNPC_LOD0,AnikaNPC_LOD2 | anika-npc.opt-ktx2.v1.glb | — | live |
| `skyrydahs-characters/anika/anika-npc.opt.glb` | glb | 1.31 MB | `2809988f8f71213b8c8a1941e109fe72` | tris=39296; joints=107; LODs=AnikaNPC_LOD1,AnikaNPC_LOD0,AnikaNPC_LOD2 | anika-npc.opt.glb | — | live |
| `skyrydahs-characters/anika/anika-npc.quest-ktx2.glb` | glb | 6.35 MB | `c2f0d194a09aadfa1a2d07cfb2aa2133` | tris=39296; joints=107; LODs=AnikaNPC_LOD1,AnikaNPC_LOD0,AnikaNPC_LOD2 | anika-npc.quest-ktx2.glb | — | live |
| `skyrydahs-characters/anika/anika-npc.quest.glb` | glb | 5.75 MB | `9b4cc58a09625f57ef1aadcf048e262f` | tris=39296; joints=107; LODs=AnikaNPC_LOD1,AnikaNPC_LOD0,AnikaNPC_LOD2 | anika-npc.quest.glb | — | live |
| `skyrydahs-characters/anika/anika-rider.draco-webp.glb` | glb | 2.72 MB | `6827307e2719e8317e0448ff9691e4c9` | tris=149476; joints=107; LODs=Anika_LOD0,Anika_LOD1,Anika_LOD2 | anika-rider.draco-webp.glb | — | live |
| `skyrydahs-characters/anika/anika-rider.glb` | glb | 15.98 MB | `cf0513222ab6d0b1f759d0d0e2761c1c` | tris=149476; joints=107; LODs=Anika_LOD0,Anika_LOD1,Anika_LOD2 | Anika player LOD0-2 | package_pwa + SR_ROSTER.anika | live |
| `skyrydahs-characters/anika/anika-rider.opt-ktx2.glb` | glb | 2.38 MB | `1c7ef3a3df3a4a053ef5709713162955` | tris=149476; joints=107; LODs=Anika_LOD0,Anika_LOD1,Anika_LOD2 | anika-rider.opt-ktx2.glb | — | live |
| `skyrydahs-characters/anika/anika-rider.opt-ktx2.v1.glb` | glb | 3.57 MB | `09426ed19c84082f9708c430842e673e` | tris=149476; joints=107; LODs=Anika_LOD0,Anika_LOD1,Anika_LOD2 | anika-rider.opt-ktx2.v1.glb | — | live |
| `skyrydahs-characters/anika/anika-rider.opt.glb` | glb | 3.03 MB | `12c39cce1522446ce222ed69fcfde085` | tris=149476; joints=107; LODs=Anika_LOD0,Anika_LOD1,Anika_LOD2 | anika-rider.opt.glb | — | live |
| `skyrydahs-characters/anika/anika-rider.quest-ktx2.glb` | glb | 17.74 MB | `02438b1ef9d066dd4407e884e2d049e9` | tris=149468; joints=107; LODs=Anika_LOD0,Anika_LOD1,Anika_LOD2 | anika-rider.quest-ktx2.glb | — | live |
| `skyrydahs-characters/anika/anika-rider.quest.glb` | glb | 17.19 MB | `3cb590eee9a7231d19a33181adb4ce64` | tris=149468; joints=107; LODs=Anika_LOD0,Anika_LOD1,Anika_LOD2 | anika-rider.quest.glb | — | live |
| `skyrydahs-characters/anika/anika-rig-report.json` | json | 20.0 KB | `6d585d7146e92e4f1439b597c34ae2c7` | — | anika-rig-report.json | — | live |
| `skyrydahs-characters/anika/anika-springs.md` | md | 2.5 KB | `49ed01e6a14529e40aea2f490477e546` | — | anika-springs.md | — | live |
| `skyrydahs-characters/anika/src/anika-npc-raw.flat.glb` | glb | 4.86 MB | `d004d076d9524b6b4d9e34ab83983030` | tris=43155; LODs=AnikaNPC_LOD1,AnikaNPC_LOD0,AnikaNPC_LOD2 | anika-npc-raw.flat.glb | — | live |
| `skyrydahs-characters/anika/src/anika-npc-raw.glb` | glb | 4.86 MB | `d004d076d9524b6b4d9e34ab83983030` | tris=43155; LODs=AnikaNPC_LOD1,AnikaNPC_LOD0,AnikaNPC_LOD2 | anika-npc-raw.glb | — | live |
| `skyrydahs-characters/anika/src/anika-rider-raw.flat.glb` | glb | 14.02 MB | `a057185428048071c630c500de7dd6ab` | tris=157131; LODs=Anika_LOD0,Anika_LOD1,Anika_LOD2 | anika-rider-raw.flat.glb | — | live |
| `skyrydahs-characters/anika/src/anika-rider-raw.glb` | glb | 14.02 MB | `a057185428048071c630c500de7dd6ab` | tris=157131; LODs=Anika_LOD0,Anika_LOD1,Anika_LOD2 | anika-rider-raw.glb | — | live |
| `skyrydahs-characters/anika/src/anika_pieces.blend` | blend | 27.65 MB | `0c5892386864f0a3129fad6c609c07ab` | — | anika_pieces.blend | — | live |
| `skyrydahs-characters/anika/src/build_gr8.py` | py | 15.4 KB | `14f289e1d3ae4014a1e172740808b7fd` | — | build_gr8.py | — | live |
| `skyrydahs-characters/anika/src/compose.py` | py | 624 B | `d4a5410d3b9537339ffdeb5578d69967` | — | compose.py | — | live |
| `skyrydahs-characters/anika/src/decal_anika_back.png` | png | 1.00 MB | `7d3de268a23ef4a7d1c7e854ce515faa` | — | decal_anika_back.png | — | live |
| `skyrydahs-characters/anika/src/decal_caali_back.png` | png | 1.01 MB | `2597932b1bead65a310258df0069a98f` | — | decal_caali_back.png | — | live |
| `skyrydahs-characters/anika/src/decal_gr8yzone_tee.png` | png | 80.1 KB | `dc0767610df74a2226ff5ebd08c02747` | — | decal_gr8yzone_tee.png | — | live |
| `skyrydahs-characters/anika/src/decals.py` | py | 1.8 KB | `787a277e5a40764ede8e60cd30449823` | — | decals.py | — | live |
| `skyrydahs-characters/anika/src/export.py` | py | 1.6 KB | `008803490d8676f19771e2b5e1b16789` | — | export.py | — | live |
| `skyrydahs-characters/anika/src/hero.py` | py | 2.7 KB | `3c8ff31f4c2da8f5e03d89f13a9e6294` | — | hero.py | — | live |
| `skyrydahs-characters/anika/src/pieces.py` | py | 2.0 KB | `0159b0800e3016d8c7d01ac519434030` | — | pieces.py | — | live |
| `skyrydahs-characters/anika/src/ship.sh` | sh | 790 B | `d654c089162a7fb061b24f0bf4809159` | — | ship.sh | — | live |
| `skyrydahs-characters/anubis/anubis-fp.glb` | glb | 588.2 KB | `1f1e1822483a972193f9e6a89371f288` | tris=2956; joints=7; meshes=Anubis_FP_body,Anubis_FP_glow | Crew character asset anubis-fp.glb | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/anubis/anubis-rider.glb` | glb | 2.72 MB | `35ec62ae730320c8db1ebe43e41f9c65` | tris=24493; joints=19; LODs=Anubis_LOD0_accessory,Anubis_LOD0_body,Anubis_LOD0_glow,Anubis_LOD0_hair,Anubis_LOD0_skates,Anubis_LOD0_top | Crew character asset anubis-rider.glb | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/anubis/anubis-rider.quest.glb` | glb | 772.5 KB | `02226f5f7d4fc73f9b8fa38485984cfd` | tris=24309; joints=19; LODs=Anubis_LOD0_accessory,Anubis_LOD0_body,Anubis_LOD0_glow,Anubis_LOD0_hair,Anubis_LOD0_skates,Anubis_LOD0_top | Crew character asset anubis-rider.quest.glb | riders.js SR_CREW_GLB | staged |
| `skyrydahs-characters/anubis/anubis-rider.quest2-ktx2.glb` | glb | 678.8 KB | `53c020673f6509550764bfccc5376007` | tris=24289; joints=19; LODs=Anubis_LOD0_accessory,Anubis_LOD0_body,Anubis_LOD0_glow,Anubis_LOD0_hair,Anubis_LOD0_skates,Anubis_LOD0_top | Crew character asset anubis-rider.quest2-ktx2.glb | riders.js SR_CREW_GLB | staged |
| `skyrydahs-characters/anubis/anubis-rider.s4-ktx2.glb` | glb | 673.0 KB | `122815b8035ae5c177dcf08c2145bc0a` | tris=24309; joints=19; LODs=Anubis_LOD0_accessory,Anubis_LOD0_body,Anubis_LOD0_glow,Anubis_LOD0_hair,Anubis_LOD0_skates,Anubis_LOD0_top | Crew character asset anubis-rider.s4-ktx2.glb | riders.js SR_CREW_GLB | staged |
| `skyrydahs-characters/anubis/anubis-rider.s4.glb` | glb | 785.5 KB | `367cac045243a0b802cc339903e02a48` | tris=24309; joints=19; LODs=Anubis_LOD0_accessory,Anubis_LOD0_body,Anubis_LOD0_glow,Anubis_LOD0_hair,Anubis_LOD0_skates,Anubis_LOD0_top | Crew character asset anubis-rider.s4.glb | riders.js SR_CREW_GLB | staged |
| `skyrydahs-characters/anubis/loader.js` | js | 1.3 KB | `594c177626b0d41ad40553501d701811` | — | Crew character asset loader.js | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/anubis/renders/34.png` | png | 132.1 KB | `b174c34cc3cde440017caf85e0cc73b0` | — | Crew character asset 34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/anubis/renders/back.png` | png | 107.5 KB | `f1bf17cc547d684ffc64da90b9b61e59` | — | Crew character asset back.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/anubis/renders/face_closeup.png` | png | 148.6 KB | `947020084ff703614f031785c19daf5d` | — | Crew character asset face_closeup.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/anubis/renders/face_expressions.png` | png | 484.4 KB | `dbcca4e86f17ee2c320e6a4b9c22d000` | — | Crew character asset face_expressions.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/anubis/renders/fp_view.png` | png | 65.6 KB | `ce945aff73d4352f4237a665fbbd3daf` | — | Crew character asset fp_view.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/anubis/renders/front.png` | png | 125.1 KB | `4c9e9ba32f7225e7011431c2057fd45a` | — | Crew character asset front.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/anubis/renders/head_34.png` | png | 85.3 KB | `ea2b18b0cd186bb8c668f2bba1caf33e` | — | Crew character asset head_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/anubis/renders/keyart.png` | png | 597.3 KB | `dbbd780955e16b5e02f7e6afad749bf8` | — | Crew character asset keyart.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/anubis/renders/lod1_34.png` | png | 131.2 KB | `5e1e022be370bc6e07431e5716026af4` | — | Crew character asset lod1_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/anubis/renders/lod2_34.png` | png | 99.3 KB | `23b72316fd041f79aa1d378de3816297` | — | Crew character asset lod2_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/anubis/renders/rigtest_front.png` | png | 474.1 KB | `06c4e9f3356a77c79afb964ffbc1f043` | — | Crew character asset rigtest_front.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/anubis/renders/rigtest_side.png` | png | 435.6 KB | `173725f8738e96b3b95cfcb36c575891` | — | Crew character asset rigtest_side.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/anubis/renders/side.png` | png | 79.2 KB | `e2a26cc1e1eeb44162d91049bd097320` | — | Crew character asset side.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/anubis/renders/sil_34.png` | png | 12.3 KB | `a5681a9b2dad561231321eae169f2740` | — | Crew character asset sil_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/anubis/renders/sil_back.png` | png | 12.8 KB | `282e015498afb90a08e8c77760b979a6` | — | Crew character asset sil_back.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/anubis/renders/turnaround.png` | png | 448.6 KB | `2453a7f099c64b6f7369f1aa1deb898f` | — | Crew character asset turnaround.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/anubis/renders/vr_34.png` | png | 135.6 KB | `9eb684e8c31a84be87282f56e26ca1c4` | — | Crew character asset vr_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/anubis/src/anubis-rider.blend` | blend | 4.66 MB | `ef6416986a6415c60b4081b13fa665f5` | — | Crew character asset anubis-rider.blend | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/anubis/src/atlas.png` | png | 21.9 KB | `1e93158fc72a9a9163e96f38ee5c766e` | — | Crew character asset atlas.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/anubis/src/build_report.json` | json | 699 B | `a9b9354a5e51606d9a159afc05a2d4bc` | — | Crew character asset build_report.json | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/anubis/src/build_rider.py` | py | 11.2 KB | `cb381367f6b04766cd5c53ef20c48969` | — | Crew character asset build_rider.py | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/anubis/src/normal_bake.png` | png | 351.5 KB | `fe41cc8ab18f406fa94351e84e74990c` | — | Crew character asset normal_bake.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/anubis/src/shoot.sh` | sh | 180 B | `6a202962e1047e76e6e07576716a8f28` | — | Crew character asset shoot.sh | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/anubis/test.html` | html | 4.6 KB | `6d8080a1f9e3b8b7376780c2716c398e` | — | Crew character asset test.html | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/behemoth/behemoth-fp.glb` | glb | 608.7 KB | `3c99bdce5d6e8c7d8fbe2b358c718d0b` | tris=2956; joints=7; meshes=Behemoth_FP_body,Behemoth_FP_glow | Crew character asset behemoth-fp.glb | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/behemoth/behemoth-rider.glb` | glb | 2.53 MB | `d5c59e423d45fd1d502636a37f5f568c` | tris=23989; joints=19; LODs=Behemoth_LOD0_accessory,Behemoth_LOD0_body,Behemoth_LOD0_glow,Behemoth_LOD0_hair,Behemoth_LOD0_skates,Behemoth_LOD0_top | Crew character asset behemoth-rider.glb | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/behemoth/behemoth-rider.quest.glb` | glb | 948.3 KB | `d9dbad11b4b2aa803b4c29236a188c59` | tris=23953; joints=19; LODs=Behemoth_LOD0_accessory,Behemoth_LOD0_body,Behemoth_LOD0_glow,Behemoth_LOD0_hair,Behemoth_LOD0_skates,Behemoth_LOD0_top | Crew character asset behemoth-rider.quest.glb | riders.js SR_CREW_GLB | staged |
| `skyrydahs-characters/behemoth/behemoth-rider.quest2-ktx2.glb` | glb | 842.2 KB | `c34f74d90861a43e8beb3b5548fd8227` | tris=23953; joints=19; LODs=Behemoth_LOD0_accessory,Behemoth_LOD0_body,Behemoth_LOD0_glow,Behemoth_LOD0_hair,Behemoth_LOD0_skates,Behemoth_LOD0_top | Crew character asset behemoth-rider.quest2-ktx2.glb | riders.js SR_CREW_GLB | staged |
| `skyrydahs-characters/behemoth/behemoth-rider.s4-ktx2.glb` | glb | 830.6 KB | `a9fb5ba686cc87fc424b0c24b18685c2` | tris=23953; joints=19; LODs=Behemoth_LOD0_accessory,Behemoth_LOD0_body,Behemoth_LOD0_glow,Behemoth_LOD0_hair,Behemoth_LOD0_skates,Behemoth_LOD0_top | Crew character asset behemoth-rider.s4-ktx2.glb | riders.js SR_CREW_GLB | staged |
| `skyrydahs-characters/behemoth/behemoth-rider.s4.glb` | glb | 955.0 KB | `3b4f609c777c18b5cbedc6b88bca26d0` | tris=23953; joints=19; LODs=Behemoth_LOD0_accessory,Behemoth_LOD0_body,Behemoth_LOD0_glow,Behemoth_LOD0_hair,Behemoth_LOD0_skates,Behemoth_LOD0_top | Crew character asset behemoth-rider.s4.glb | riders.js SR_CREW_GLB | staged |
| `skyrydahs-characters/behemoth/loader.js` | js | 1.3 KB | `251abc773d6477259fe09f84a552d9b8` | — | Crew character asset loader.js | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/behemoth/renders/34.png` | png | 124.2 KB | `cc9c496a4c1c6a8a8737f4d00e74a761` | — | Crew character asset 34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/behemoth/renders/back.png` | png | 109.5 KB | `af3e4352044f169cd7840b888f41200a` | — | Crew character asset back.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/behemoth/renders/face_34.png` | png | 85.3 KB | `a73ae9d0d6a50c7a1463ac1df92530c7` | — | Crew character asset face_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/behemoth/renders/face_closeup.png` | png | 97.6 KB | `01b17442c1098e0bdc038b2e82a07158` | — | Crew character asset face_closeup.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/behemoth/renders/face_expressions.png` | png | 206.3 KB | `3c943606e7b0470cf746102427f2dbae` | — | Crew character asset face_expressions.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/behemoth/renders/fp_view.png` | png | 75.5 KB | `e3382e7deba95a28c5f525882a243e5a` | — | Crew character asset fp_view.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/behemoth/renders/front.png` | png | 124.2 KB | `65ea7545c0ab9673e0593984ac32e53d` | — | Crew character asset front.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/behemoth/renders/keyart.png` | png | 594.8 KB | `40c92cfa2e652a309eefd4bd56de3b80` | — | Crew character asset keyart.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/behemoth/renders/lod1_34.png` | png | 122.4 KB | `e6a451f054284a89d177827173129586` | — | Crew character asset lod1_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/behemoth/renders/lod2_34.png` | png | 112.7 KB | `035e9dfe30307f9d415aac215e9dac36` | — | Crew character asset lod2_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/behemoth/renders/rigtest_front.png` | png | 484.5 KB | `ffd50cba5279dac88dae73af32df889e` | — | Crew character asset rigtest_front.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/behemoth/renders/rigtest_side.png` | png | 444.2 KB | `2541fc673e60ac8e746b49f51176edb0` | — | Crew character asset rigtest_side.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/behemoth/renders/side.png` | png | 78.2 KB | `92a17fa641ec62cd33e65871bb246dd7` | — | Crew character asset side.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/behemoth/renders/sil_34.png` | png | 12.0 KB | `6960b960d3ecd01751506f83166875c6` | — | Crew character asset sil_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/behemoth/renders/sil_back.png` | png | 12.3 KB | `505bc4858efd3a610a1d0f6b7ddcc220` | — | Crew character asset sil_back.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/behemoth/renders/turnaround.png` | png | 437.5 KB | `cda10a35d5febaa0879387e7b2ad622d` | — | Crew character asset turnaround.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/behemoth/renders/vr_34.png` | png | 141.5 KB | `d66dd21c8b7ca57b74e624d6039e2f50` | — | Crew character asset vr_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/behemoth/src/atlas.png` | png | 21.9 KB | `1e93158fc72a9a9163e96f38ee5c766e` | — | Crew character asset atlas.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/behemoth/src/behemoth-rider.blend` | blend | 5.09 MB | `21d59d618518d451d263f465f117a76d` | — | Crew character asset behemoth-rider.blend | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/behemoth/src/build_report.json` | json | 622 B | `74229744325a7544b7a98da3660489f2` | — | Crew character asset build_report.json | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/behemoth/src/build_rider.py` | py | 8.6 KB | `0344089904415802b8fd7fe73ac857b7` | — | Crew character asset build_rider.py | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/behemoth/src/normal_bake.png` | png | 369.4 KB | `2bbb3f224c3ad30e0258bb06b92c4b9c` | — | Crew character asset normal_bake.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/behemoth/src/shoot.sh` | sh | 182 B | `8e973b72198f3279ef0c073045065e2a` | — | Crew character asset shoot.sh | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/behemoth/test.html` | html | 4.6 KB | `26a63393abf7b34973eff360c500459e` | — | Crew character asset test.html | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/caali/README.txt` | txt | 151 B | `3bb26a3f66ad86ae4a80069a8feb5a4d` | — | Crew character asset README.txt | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/caali/caali-fp.glb` | glb | 604.2 KB | `cfda8cbdf9148bdb96d40b5b550633c5` | tris=2956; joints=7; meshes=CodeE_FP_body,CodeE_FP_glow | Crew character asset caali-fp.glb | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/caali/caali-rider.glb` | glb | 2.52 MB | `e0bd62b9d5567a7576264c812ba3150f` | tris=24149; joints=19; LODs=CodeE_LOD0_accessory,CodeE_LOD0_body,CodeE_LOD0_glow,CodeE_LOD0_hair,CodeE_LOD0_skates,CodeE_LOD0_top | Crew character asset caali-rider.glb | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/caali/keyart.html` | html | 7.4 KB | `112fc0018f66bad2b1afd1a67777cedc` | — | Crew character asset keyart.html | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/caali/loader.js` | js | 1.3 KB | `92287bdc86856a10059b3a70ff021ed2` | — | Crew character asset loader.js | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/caali/renders/34.png` | png | 114.9 KB | `ff1d97cdd25611c9d884154a750cb898` | — | Crew character asset 34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/caali/renders/back.png` | png | 109.5 KB | `4a373c88b4c7daf8c34536b0c49af56a` | — | Crew character asset back.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/caali/renders/crew_tint_test.png` | png | 129.1 KB | `f36bbfb3e137b7a509676f0cf4df21d7` | — | Crew character asset crew_tint_test.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/caali/renders/face_34.png` | png | 82.2 KB | `1052ff5e80f21b104b45b7a8ce646082` | — | Crew character asset face_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/caali/renders/face_closeup.png` | png | 237.4 KB | `1b694ed7ce6020548cd75fc804f61cca` | — | Crew character asset face_closeup.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/caali/renders/face_expressions.png` | png | 180.2 KB | `194cb4050cfb05698cb997ba45359f80` | — | Crew character asset face_expressions.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/caali/renders/face_front.png` | png | 87.8 KB | `8e55e5181b63fb87eb3c6b5ec2dc2f9d` | — | Crew character asset face_front.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/caali/renders/face_side.png` | png | 60.7 KB | `bac850efa0224bc7f9dad77a1e56478f` | — | Crew character asset face_side.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/caali/renders/fp_view.png` | png | 68.1 KB | `45501b47feb7a0d257c2becf3412ea3a` | — | Crew character asset fp_view.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/caali/renders/front.png` | png | 118.1 KB | `3118fc76c18333633be613678ad9efde` | — | Crew character asset front.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/caali/renders/hero_compare.png` | png | 667.3 KB | `59a531e769410f85641f296440d00f1d` | — | Crew character asset hero_compare.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/caali/renders/keyart.png` | png | 639.2 KB | `c57e316ec200d8ff8b73929209a3befd` | — | Crew character asset keyart.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/caali/renders/lod1_34.png` | png | 114.3 KB | `cf7a1a031b3d27a081e44febb6b44a48` | — | Crew character asset lod1_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/caali/renders/lod2_34.png` | png | 98.9 KB | `e863b48a7b84763a628c08f86529db71` | — | Crew character asset lod2_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/caali/renders/rigtest_front.png` | png | 464.6 KB | `5c7d73be7bfc87a8f619dec58e8969d0` | — | Crew character asset rigtest_front.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/caali/renders/rigtest_side.png` | png | 427.9 KB | `813edbd967cdf6dda1531a0106d2d339` | — | Crew character asset rigtest_side.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/caali/renders/side.png` | png | 70.4 KB | `d598d70ce49ee579243d1513de498153` | — | Crew character asset side.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/caali/renders/sil_34.png` | png | 12.7 KB | `1770cef085020b85388283699dfad087` | — | Crew character asset sil_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/caali/renders/sil_back.png` | png | 13.0 KB | `0d91ac4cfb7fa6ce9d8afeeee7a18d38` | — | Crew character asset sil_back.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/caali/renders/skate_34.png` | png | 116.3 KB | `4a8f0ef6f0befb9043fcd7485f929d1d` | — | Crew character asset skate_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/caali/renders/turnaround.png` | png | 410.8 KB | `a5ed51f083f5b773bd0b60c31ad6e638` | — | Crew character asset turnaround.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/caali/renders/vr_34.png` | png | 138.1 KB | `d7b7300070ab68acaf94e5439fbaea21` | — | Crew character asset vr_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/caali/src/atlas.png` | png | 15.8 KB | `b5d30c13679cc4a5ee7e995fa727679e` | — | Crew character asset atlas.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/caali/src/build_rider.py` | py | 18.5 KB | `785b5bcd2c106946a4f0d6d9bd9d96da` | — | Crew character asset build_rider.py | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/caali/src/build_rider_v1.py` | py | 18.2 KB | `8bb994116468dbc4975fae0da020885c` | — | Crew character asset build_rider_v1.py | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/caali/src/code-e-rider.blend` | blend | 2.29 MB | `473ca6ab6ede7a8b2e1db33b0cd42f23` | — | Crew character asset code-e-rider.blend | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/caali/src/shoot.sh` | sh | 612 B | `a234f2f6a09d0c135bc20fb11efe4a90` | — | Crew character asset shoot.sh | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/caali/test.html` | html | 4.6 KB | `b7376fe0c66377229b3099cb9f93af3c` | — | Crew character asset test.html | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/code-e/code-e-fp.glb` | glb | 604.2 KB | `cfda8cbdf9148bdb96d40b5b550633c5` | tris=2956; joints=7; meshes=CodeE_FP_body,CodeE_FP_glow | Crew character asset code-e-fp.glb | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/code-e/code-e-rider.glb` | glb | 2.52 MB | `e0bd62b9d5567a7576264c812ba3150f` | tris=24149; joints=19; LODs=CodeE_LOD0_accessory,CodeE_LOD0_body,CodeE_LOD0_glow,CodeE_LOD0_hair,CodeE_LOD0_skates,CodeE_LOD0_top | Crew character asset code-e-rider.glb | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/code-e/loader.js` | js | 1.3 KB | `c2004402d6f00efcbedaef754126aded` | — | Crew character asset loader.js | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/code-e/renders/34.png` | png | 114.9 KB | `ff1d97cdd25611c9d884154a750cb898` | — | Crew character asset 34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/code-e/renders/back.png` | png | 109.5 KB | `4a373c88b4c7daf8c34536b0c49af56a` | — | Crew character asset back.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/code-e/renders/crew_tint_test.png` | png | 129.1 KB | `f36bbfb3e137b7a509676f0cf4df21d7` | — | Crew character asset crew_tint_test.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/code-e/renders/face_34.png` | png | 82.2 KB | `1052ff5e80f21b104b45b7a8ce646082` | — | Crew character asset face_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/code-e/renders/face_closeup.png` | png | 237.4 KB | `1b694ed7ce6020548cd75fc804f61cca` | — | Crew character asset face_closeup.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/code-e/renders/face_expressions.png` | png | 180.2 KB | `194cb4050cfb05698cb997ba45359f80` | — | Crew character asset face_expressions.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/code-e/renders/face_front.png` | png | 87.8 KB | `8e55e5181b63fb87eb3c6b5ec2dc2f9d` | — | Crew character asset face_front.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/code-e/renders/face_side.png` | png | 60.7 KB | `bac850efa0224bc7f9dad77a1e56478f` | — | Crew character asset face_side.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/code-e/renders/fp_view.png` | png | 68.1 KB | `45501b47feb7a0d257c2becf3412ea3a` | — | Crew character asset fp_view.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/code-e/renders/front.png` | png | 118.1 KB | `3118fc76c18333633be613678ad9efde` | — | Crew character asset front.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/code-e/renders/hero_compare.png` | png | 667.3 KB | `59a531e769410f85641f296440d00f1d` | — | Crew character asset hero_compare.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/code-e/renders/keyart.png` | png | 639.2 KB | `c57e316ec200d8ff8b73929209a3befd` | — | Crew character asset keyart.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/code-e/renders/lod1_34.png` | png | 114.3 KB | `cf7a1a031b3d27a081e44febb6b44a48` | — | Crew character asset lod1_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/code-e/renders/lod2_34.png` | png | 98.9 KB | `e863b48a7b84763a628c08f86529db71` | — | Crew character asset lod2_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/code-e/renders/rigtest_front.png` | png | 464.6 KB | `5c7d73be7bfc87a8f619dec58e8969d0` | — | Crew character asset rigtest_front.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/code-e/renders/rigtest_side.png` | png | 427.9 KB | `813edbd967cdf6dda1531a0106d2d339` | — | Crew character asset rigtest_side.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/code-e/renders/side.png` | png | 70.4 KB | `d598d70ce49ee579243d1513de498153` | — | Crew character asset side.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/code-e/renders/sil_34.png` | png | 12.7 KB | `1770cef085020b85388283699dfad087` | — | Crew character asset sil_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/code-e/renders/sil_back.png` | png | 13.0 KB | `0d91ac4cfb7fa6ce9d8afeeee7a18d38` | — | Crew character asset sil_back.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/code-e/renders/skate_34.png` | png | 116.3 KB | `4a8f0ef6f0befb9043fcd7485f929d1d` | — | Crew character asset skate_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/code-e/renders/turnaround.png` | png | 410.8 KB | `a5ed51f083f5b773bd0b60c31ad6e638` | — | Crew character asset turnaround.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/code-e/renders/vr_34.png` | png | 138.1 KB | `d7b7300070ab68acaf94e5439fbaea21` | — | Crew character asset vr_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/code-e/src/atlas.png` | png | 21.9 KB | `1e93158fc72a9a9163e96f38ee5c766e` | — | Crew character asset atlas.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/code-e/src/build_report.json` | json | 635 B | `e9e7665196063be2164739cd56de346e` | — | Crew character asset build_report.json | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/code-e/src/build_rider.py` | py | 18.5 KB | `785b5bcd2c106946a4f0d6d9bd9d96da` | — | Crew character asset build_rider.py | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/code-e/src/build_rider_v1.py` | py | 18.2 KB | `8bb994116468dbc4975fae0da020885c` | — | Crew character asset build_rider_v1.py | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/code-e/src/code-e-rider.blend` | blend | 5.01 MB | `293a1b9c3f5435a5b1cafeb100fa8a51` | — | Crew character asset code-e-rider.blend | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/code-e/src/normal_bake.png` | png | 368.4 KB | `afa2836b88b47570529a28dc2f45a297` | — | Crew character asset normal_bake.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/code-e/src/shoot.sh` | sh | 180 B | `611591a68877aca6baa719937999811b` | — | Crew character asset shoot.sh | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/code-e/test.html` | html | 4.6 KB | `2abd763fef1f8120942572253364c1af` | — | Crew character asset test.html | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/genesis/genesis-fp.glb` | glb | 608.4 KB | `02071f90d3230ae3063c3e1df5f1d013` | tris=2956; joints=7; meshes=Genesis_FP_body,Genesis_FP_glow | Crew character asset genesis-fp.glb | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/genesis/genesis-rider.glb` | glb | 2.63 MB | `296ce0cd910613d90946874a807ace62` | tris=25404; joints=19; LODs=Genesis_LOD0_accessory,Genesis_LOD0_body,Genesis_LOD0_glow,Genesis_LOD0_hair,Genesis_LOD0_skates,Genesis_LOD0_top | Crew character asset genesis-rider.glb | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/genesis/genesis-rider.quest.glb` | glb | 993.6 KB | `4a0764757271de37e95b4ec382ceecc9` | tris=25368; joints=19; LODs=Genesis_LOD0_accessory,Genesis_LOD0_body,Genesis_LOD0_glow,Genesis_LOD0_hair,Genesis_LOD0_skates,Genesis_LOD0_top | Crew character asset genesis-rider.quest.glb | riders.js SR_CREW_GLB | staged |
| `skyrydahs-characters/genesis/genesis-rider.quest2-ktx2.glb` | glb | 890.6 KB | `45f4447a170f8095ba7077dc08c0d81a` | tris=25368; joints=19; LODs=Genesis_LOD0_accessory,Genesis_LOD0_body,Genesis_LOD0_glow,Genesis_LOD0_hair,Genesis_LOD0_skates,Genesis_LOD0_top | Crew character asset genesis-rider.quest2-ktx2.glb | riders.js SR_CREW_GLB | staged |
| `skyrydahs-characters/genesis/genesis-rider.s4-ktx2.glb` | glb | 880.6 KB | `00c60aa906b1c68e703a19d20a220550` | tris=25368; joints=19; LODs=Genesis_LOD0_accessory,Genesis_LOD0_body,Genesis_LOD0_glow,Genesis_LOD0_hair,Genesis_LOD0_skates,Genesis_LOD0_top | Crew character asset genesis-rider.s4-ktx2.glb | riders.js SR_CREW_GLB | staged |
| `skyrydahs-characters/genesis/genesis-rider.s4.glb` | glb | 1003.4 KB | `4c4734d708cfdb463ec283449996f7f7` | tris=25368; joints=19; LODs=Genesis_LOD0_accessory,Genesis_LOD0_body,Genesis_LOD0_glow,Genesis_LOD0_hair,Genesis_LOD0_skates,Genesis_LOD0_top | Crew character asset genesis-rider.s4.glb | riders.js SR_CREW_GLB | staged |
| `skyrydahs-characters/genesis/loader.js` | js | 1.3 KB | `a84658808ea874c94240c73691a3c95c` | — | Crew character asset loader.js | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/genesis/renders/34.png` | png | 152.0 KB | `e7c2113f2ffa762c3e8abb9783bf4020` | — | Crew character asset 34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/genesis/renders/back.png` | png | 155.1 KB | `8d7c627a86c8d61bfe8850412b3b53e1` | — | Crew character asset back.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/genesis/renders/face_closeup.png` | png | 130.1 KB | `218da644b452d3ad73b94d860ebd361a` | — | Crew character asset face_closeup.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/genesis/renders/face_expressions.png` | png | 170.0 KB | `2167fb6780757f258b585db974375adf` | — | Crew character asset face_expressions.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/genesis/renders/fp_view.png` | png | 92.8 KB | `80e07c618cbbd90e0f405c17b7af7d35` | — | Crew character asset fp_view.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/genesis/renders/front.png` | png | 155.7 KB | `b1da8f79b5aebf6c8387db4b5b909ff2` | — | Crew character asset front.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/genesis/renders/keyart.png` | png | 671.4 KB | `aa6c6d12e440ea76a7c78545ffcdb934` | — | Crew character asset keyart.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/genesis/renders/lod1_34.png` | png | 149.3 KB | `5de3d4fac8b8bef614fc951d9cab63fc` | — | Crew character asset lod1_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/genesis/renders/lod2_34.png` | png | 118.9 KB | `8183be5fd27df4ac51c7feb723bd2bd7` | — | Crew character asset lod2_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/genesis/renders/rigtest_front.png` | png | 475.9 KB | `45ecb7ee5a9a2d886620e84e51e10680` | — | Crew character asset rigtest_front.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/genesis/renders/rigtest_side.png` | png | 430.0 KB | `3f31f201dc181c30fd5e77a1bee93e88` | — | Crew character asset rigtest_side.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/genesis/renders/side.png` | png | 92.8 KB | `5392c2b647ba489ba0ee7f769f6ecc8c` | — | Crew character asset side.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/genesis/renders/sil_34.png` | png | 12.4 KB | `6e23f6fe134ebca10196669380cd4ffc` | — | Crew character asset sil_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/genesis/renders/sil_back.png` | png | 13.5 KB | `3591409794216cad8117fe2e2e6927e9` | — | Crew character asset sil_back.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/genesis/renders/turnaround.png` | png | 559.5 KB | `589ff20a22e6a9734fd2b72c823bc553` | — | Crew character asset turnaround.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/genesis/renders/vr_34.png` | png | 157.9 KB | `cb98d81e7d660679af41c3e7279b487a` | — | Crew character asset vr_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/genesis/src/atlas.png` | png | 21.9 KB | `1e93158fc72a9a9163e96f38ee5c766e` | — | Crew character asset atlas.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/genesis/src/build_report.json` | json | 667 B | `b6c02c9cc028d22fc18f56dcf2827229` | — | Crew character asset build_report.json | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/genesis/src/build_rider.py` | py | 11.5 KB | `d86c7b38a0cb6883671d6fb003d53437` | — | Crew character asset build_rider.py | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/genesis/src/genesis-rider.blend` | blend | 5.21 MB | `d054ca43924900ebfb81d4d6fa2c71ec` | — | Crew character asset genesis-rider.blend | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/genesis/src/normal_bake.png` | png | 367.0 KB | `a6127d3842ac87a658b921b7b2d2302b` | — | Crew character asset normal_bake.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/genesis/test.html` | html | 4.6 KB | `53e06761742b83b7070888d085738eae` | — | Crew character asset test.html | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/kogarasumaru/kogarasumaru-fp.glb` | glb | 588.0 KB | `4c75af54e9a767b0357a7c6c1feb72e5` | tris=2956; joints=7; meshes=Kogarasumaru_FP_body,Kogarasumaru_FP_glow | Crew character asset kogarasumaru-fp.glb | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/kogarasumaru/kogarasumaru-rider.glb` | glb | 2.75 MB | `7091b60e104a26d37b436ab7213e2182` | tris=25653; joints=19; LODs=Kogarasumaru_LOD0_accessory,Kogarasumaru_LOD0_body,Kogarasumaru_LOD0_glow,Kogarasumaru_LOD0_hair,Kogarasumaru_LOD0_skates,Kogarasumaru_LOD0_top | Crew character asset kogarasumaru-rider.glb | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/kogarasumaru/kogarasumaru-rider.quest.glb` | glb | 999.0 KB | `9f806501215eeaa729384792f417db7f` | tris=25617; joints=19; LODs=Kogarasumaru_LOD0_accessory,Kogarasumaru_LOD0_body,Kogarasumaru_LOD0_glow,Kogarasumaru_LOD0_hair,Kogarasumaru_LOD0_skates,Kogarasumaru_LOD0_top | Crew character asset kogarasumaru-rider.quest.glb | riders.js SR_CREW_GLB | staged |
| `skyrydahs-characters/kogarasumaru/kogarasumaru-rider.quest2-ktx2.glb` | glb | 902.9 KB | `84c28b0c65b73c42e4fd1dbcfb836fc5` | tris=25617; joints=19; LODs=Kogarasumaru_LOD0_accessory,Kogarasumaru_LOD0_body,Kogarasumaru_LOD0_glow,Kogarasumaru_LOD0_hair,Kogarasumaru_LOD0_skates,Kogarasumaru_LOD0_top | Crew character asset kogarasumaru-rider.quest2-ktx2.glb | riders.js SR_CREW_GLB | staged |
| `skyrydahs-characters/kogarasumaru/kogarasumaru-rider.s4-ktx2.glb` | glb | 891.6 KB | `7f167a47a3cbf13c48818b91a83aeeec` | tris=25617; joints=19; LODs=Kogarasumaru_LOD0_accessory,Kogarasumaru_LOD0_body,Kogarasumaru_LOD0_glow,Kogarasumaru_LOD0_hair,Kogarasumaru_LOD0_skates,Kogarasumaru_LOD0_top | Crew character asset kogarasumaru-rider.s4-ktx2.glb | riders.js SR_CREW_GLB | staged |
| `skyrydahs-characters/kogarasumaru/kogarasumaru-rider.s4.glb` | glb | 1007.5 KB | `0f693ca47561e09b8792bbc4222c966a` | tris=25617; joints=19; LODs=Kogarasumaru_LOD0_accessory,Kogarasumaru_LOD0_body,Kogarasumaru_LOD0_glow,Kogarasumaru_LOD0_hair,Kogarasumaru_LOD0_skates,Kogarasumaru_LOD0_top | Crew character asset kogarasumaru-rider.s4.glb | riders.js SR_CREW_GLB | staged |
| `skyrydahs-characters/kogarasumaru/loader.js` | js | 1.3 KB | `4e46eae2554bbf05cbfd44016fceb0f6` | — | Crew character asset loader.js | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/kogarasumaru/renders/34.png` | png | 100.0 KB | `bf345e09298ba5e44a83e3f9a5ff4d59` | — | Crew character asset 34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/kogarasumaru/renders/back.png` | png | 100.3 KB | `95e51aa6762c3f7bcadf4af571b51322` | — | Crew character asset back.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/kogarasumaru/renders/face_34.png` | png | 54.0 KB | `1f3bb1dacc2427111826e4f0b157b4f0` | — | Crew character asset face_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/kogarasumaru/renders/face_closeup.png` | png | 101.6 KB | `bd5f63fee1a46910df691a137cd1e516` | — | Crew character asset face_closeup.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/kogarasumaru/renders/face_expressions.png` | png | 164.8 KB | `93ce3dbf9151991213b043fec0aff160` | — | Crew character asset face_expressions.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/kogarasumaru/renders/face_front.png` | png | 57.5 KB | `8cf860743b0cad9537919ea726911e79` | — | Crew character asset face_front.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/kogarasumaru/renders/fp_view.png` | png | 63.5 KB | `74dd4eb5326036e0cf12fee0dc795958` | — | Crew character asset fp_view.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/kogarasumaru/renders/front.png` | png | 100.5 KB | `dfeb8ac21927191c633d4ca33643bb60` | — | Crew character asset front.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/kogarasumaru/renders/keyart.png` | png | 614.7 KB | `4a7532d092dcf496ff51fc849162aef3` | — | Crew character asset keyart.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/kogarasumaru/renders/lod1_34.png` | png | 97.6 KB | `b04b0019bc567d419216933147b72a28` | — | Crew character asset lod1_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/kogarasumaru/renders/lod2_34.png` | png | 81.2 KB | `ed01e9a99c319b0dd82e25890e5a60d7` | — | Crew character asset lod2_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/kogarasumaru/renders/rigtest_front.png` | png | 462.2 KB | `3ea7f889de8bf04988045111820e2ce5` | — | Crew character asset rigtest_front.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/kogarasumaru/renders/rigtest_side.png` | png | 437.8 KB | `3c3b260c5fb0718a5a92a43a19051582` | — | Crew character asset rigtest_side.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/kogarasumaru/renders/side.png` | png | 73.4 KB | `338101d814ff630e86914e2922483d13` | — | Crew character asset side.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/kogarasumaru/renders/sil_34.png` | png | 12.2 KB | `b011f720d42b9374894c11f4616b8de6` | — | Crew character asset sil_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/kogarasumaru/renders/sil_back.png` | png | 13.3 KB | `a08bfd4ade0dadfb52512358fb5b7903` | — | Crew character asset sil_back.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/kogarasumaru/renders/turnaround.png` | png | 369.5 KB | `73814760f07d09b2ee8075d618a198eb` | — | Crew character asset turnaround.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/kogarasumaru/renders/vr_34.png` | png | 124.3 KB | `9754697a95c1cc460b9169601820a1eb` | — | Crew character asset vr_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/kogarasumaru/src/atlas.png` | png | 21.9 KB | `1e93158fc72a9a9163e96f38ee5c766e` | — | Crew character asset atlas.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/kogarasumaru/src/build_report.json` | json | 661 B | `1f4ac2ad5354b4af5e0d0d0151015fa4` | — | Crew character asset build_report.json | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/kogarasumaru/src/build_rider.py` | py | 11.5 KB | `c3897de64690bac9d70bf67420f535a2` | — | Crew character asset build_rider.py | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/kogarasumaru/src/kogarasumaru-rider.blend` | blend | 5.24 MB | `51c11704fcd6a6bc3426d7104cc9e187` | — | Crew character asset kogarasumaru-rider.blend | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/kogarasumaru/src/normal_bake.png` | png | 352.2 KB | `83f3d363b1ae6186fdd579aac8e593b7` | — | Crew character asset normal_bake.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/kogarasumaru/src/shoot.sh` | sh | 186 B | `c3ba2150c1483dd989f19d9e616b6f61` | — | Crew character asset shoot.sh | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/kogarasumaru/test.html` | html | 4.6 KB | `a5af3c4162e533e6d6680ff52277c1e9` | — | Crew character asset test.html | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/legacy/anubis/build_rider_prelib.py` | py | 23.2 KB | `d754c1008e66eb8d4687fea86d5e478e` | — | Crew character asset build_rider_prelib.py | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/legacy/behemoth/build_rider_prelib.py` | py | 24.7 KB | `af1f77234b4a5ce260499103a513c636` | — | Crew character asset build_rider_prelib.py | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/legacy/code-e/build_rider_prelib.py` | py | 24.8 KB | `e00800f15305c9d65286c86a6cfc020c` | — | Crew character asset build_rider_prelib.py | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/legacy/code-e/build_rider_stormjacket.py` | py | 14.5 KB | `6cfed362269646235807d808770a84d6` | — | Crew character asset build_rider_stormjacket.py | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/legacy/hero7/anubis-build_rider.py` | py | 10.5 KB | `5ebe810b96004c88a1194de013e1264c` | — | anubis-build_rider.py | — | live |
| `skyrydahs-characters/legacy/hero7/behemoth-build_rider.py` | py | 11.5 KB | `1c397c96e8555259a23e26d900a859d3` | — | behemoth-build_rider.py | — | live |
| `skyrydahs-characters/legacy/hero7/genesis-build_rider.py` | py | 13.8 KB | `fb4d2c8e9306c0a1723d00cc3a732d5b` | — | genesis-build_rider.py | — | live |
| `skyrydahs-characters/legacy/hero7/kogarasumaru-build_rider.py` | py | 14.3 KB | `a5920349ee7a2a57b5ba47b5c9bf302c` | — | kogarasumaru-build_rider.py | — | live |
| `skyrydahs-characters/legacy/hero7/sleeping-forest-build_rider.py` | py | 13.7 KB | `b4ec9b64b4b2d376f087a85bade41f24` | — | sleeping-forest-build_rider.py | — | live |
| `skyrydahs-characters/legacy/hero7/static-angels-build_rider.py` | py | 12.4 KB | `15c57b8c369963952dd1bb7886a1183f` | — | static-angels-build_rider.py | — | live |
| `skyrydahs-characters/legacy/hero7/tool-toul-to-build_rider.py` | py | 14.8 KB | `576796bdb95ed4b15dcf7449a22f067a` | — | tool-toul-to-build_rider.py | — | live |
| `skyrydahs-characters/legacy/kogarasumaru/build_rider_prelib.py` | py | 27.2 KB | `b35fd32a6fb2a113504b32148ef00734` | — | Crew character asset build_rider_prelib.py | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/legacy/static-angels/build_rider_prelib.py` | py | 25.4 KB | `37993662cc71e9a22ce48c68a1a903a4` | — | Crew character asset build_rider_prelib.py | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/lineup.png` | png | 709.2 KB | `27191325761115b9983804131bdd70c0` | — | lineup.png | — | live |
| `skyrydahs-characters/lineup_back.png` | png | 675.8 KB | `798adb6be55aebc43df04f7484b1003f` | — | lineup_back.png | — | live |
| `skyrydahs-characters/lineup_silhouettes.png` | png | 141.9 KB | `05cc20a93ec2d04cf6eb20c5bfe5dbb3` | — | lineup_silhouettes.png | — | live |
| `skyrydahs-characters/meshy/airtreck-meshy.glb` | glb | 56.11 MB | `6728db4f63aec38dd42fddb35e4fa564` | tris=1815196 | Meshy source/intermediate airtreck-meshy.glb | — | source |
| `skyrydahs-characters/meshy/caali-meshy-result.webp` | webp | 284.9 KB | `31f63604b42b7e32dc019e21a11fb398` | — | Meshy source/intermediate caali-meshy-result.webp | — | source |
| `skyrydahs-characters/meshy/caali-meshy-rigged.glb` | glb | 9.16 MB | `dd5db490d910d4bd8b89d417e3824a85` | tris=15778; joints=66; meshes=Mesh_0 | Meshy source/intermediate caali-meshy-rigged.glb | — | source |
| `skyrydahs-characters/meshy/download-paywall.webp` | webp | 179.7 KB | `e15decb8e913082e78abfec97481f1f5` | — | Meshy source/intermediate download-paywall.webp | — | source |
| `skyrydahs-characters/meshy/ikki-cyan-baked-2k-v1holes.png` | png | 1.97 MB | `24f876261e9487d6a7ef06d515104275` | — | Meshy source/intermediate ikki-cyan-baked-2k-v1holes.png | — | source |
| `skyrydahs-characters/meshy/ikki-cyan-baked-2k.png` | png | 4.85 MB | `9f88c3fcfd3ff3f3dfa6a2ef16a51c85` | — | Meshy source/intermediate ikki-cyan-baked-2k.png | — | source |
| `skyrydahs-characters/meshy/ikki-meshy-cyan.glb` | glb | 8.51 MB | `b579ec11360047cd73293bef5ece5365` | tris=15778 | Meshy source/intermediate ikki-meshy-cyan.glb | — | source |
| `skyrydahs-characters/meshy/ikki-meshy-rigged-opt.glb` | glb | 1.06 MB | `90c7e6db4d8b7733b3023ba9c4bdaecd` | tris=15778; joints=66; meshes=Mesh_0 | Meshy source/intermediate ikki-meshy-rigged-opt.glb | — | source |
| `skyrydahs-characters/meshy/ikki-meshy-rigged.glb` | glb | 9.16 MB | `dd5db490d910d4bd8b89d417e3824a85` | tris=15778; joints=66; meshes=Mesh_0 | Meshy source/intermediate ikki-meshy-rigged.glb | — | source |
| `skyrydahs-characters/meshy/ikki-meshy-skate-v2.glb` | glb | 5.00 MB | `a0f9718d324b259cd592430d82f96bb5` | tris=31516; joints=66; LODs=Ikki_LOD0,Ikki_LOD1,Ikki_LOD2 | Meshy source/intermediate ikki-meshy-skate-v2.glb | — | source |
| `skyrydahs-characters/meshy/ikki-meshy-skate.glb` | glb | 5.03 MB | `8bc958a359e616f4527d8d19985b6ab0` | tris=31450; joints=66; LODs=Ikki_LOD0,Ikki_LOD1,Ikki_LOD2 | Meshy source/intermediate ikki-meshy-skate.glb | — | source |
| `skyrydahs-characters/meshy/ikki-meshy-skate.quest-draco.glb` | glb | 850.8 KB | `20a70f4acaf5e753495572c5fccda121` | tris=31450; joints=66; LODs=Ikki_LOD0,Ikki_LOD1,Ikki_LOD2 | Meshy source/intermediate ikki-meshy-skate.quest-draco.glb | — | source |
| `skyrydahs-characters/meshy/ikki-meshy-skate.quest-meshopt.glb` | glb | 1.14 MB | `83e995b23bf79e4f4bb6a056fd01d316` | tris=31450; joints=198; LODs=Ikki_LOD0,Ikki_LOD1,Ikki_LOD2 | Meshy source/intermediate ikki-meshy-skate.quest-meshopt.glb | — | source |
| `skyrydahs-characters/meshy/ikki-meshy-skate.quest-meshopt16.glb` | glb | 1.27 MB | `7a30195cb3fda4713e9968e69c511771` | tris=31450; joints=198; LODs=Ikki_LOD0,Ikki_LOD1,Ikki_LOD2 | Meshy source/intermediate ikki-meshy-skate.quest-meshopt16.glb | — | source |
| `skyrydahs-characters/meshy/ikki-meshy-skate.quest.glb` | glb | 4.51 MB | `6ba570afb2cc66bb6fb08bb5223cacf3` | tris=31450; joints=66; LODs=Ikki_LOD0,Ikki_LOD1,Ikki_LOD2 | Meshy source/intermediate ikki-meshy-skate.quest.glb | — | source |
| `skyrydahs-characters/meshy/ikki-meshy-skate.s4-ktx2.glb` | glb | 2.00 MB | `d356190c0382e8db4aface5353100fea` | tris=31450; joints=66; LODs=Ikki_LOD0,Ikki_LOD1,Ikki_LOD2 | Meshy source/intermediate ikki-meshy-skate.s4-ktx2.glb | — | source |
| `skyrydahs-characters/meshy/ikki-meshy-skate.s4.glb` | glb | 1.26 MB | `499724c0f30249a3d74a2e58fcfafc07` | tris=31450; joints=66; LODs=Ikki_LOD0,Ikki_LOD1,Ikki_LOD2 | Meshy source/intermediate ikki-meshy-skate.s4.glb | — | source |
| `skyrydahs-characters/meshy/rigged-anim.webp` | webp | 273.1 KB | `8efa678b856bd4f3ffe0861c073ca92c` | — | Meshy source/intermediate rigged-anim.webp | — | source |
| `skyrydahs-characters/refs/Aggressive_Inline_Skate_Gawds_Ground_Control_Dead_Wheels_Bla.jpg` | jpg | 261.1 KB | `0ea2208e90423a15f37af03692ec810b` | — | Aggressive_Inline_Skate_Gawds_Ground_Control_Dead_Wheels_Bla.jpg | — | live |
| `skyrydahs-characters/refs/Aggressive_Inline_Skate_Gawds_Symetrics_Dead_Wheels_Bottom_v.jpg` | jpg | 181.0 KB | `2e50f635f2f6b78315ce68814bbd5362` | — | Aggressive_Inline_Skate_Gawds_Symetrics_Dead_Wheels_Bottom_v.jpg | — | live |
| `skyrydahs-characters/refs/MA_1_Jacket_in_petrol_jpg.jpg` | jpg | 52.5 KB | `494ec9c663a7b68e0bb6b149b25fca94` | — | MA_1_Jacket_in_petrol_jpg.jpg | — | live |
| `skyrydahs-characters/refs/Rollerblader_Soul_Grind_jpg.jpg` | jpg | 193.9 KB | `271918d7fc4bee701701ad61a3b2f32b` | — | Rollerblader_Soul_Grind_jpg.jpg | — | live |
| `skyrydahs-characters/refs/cyberpunk2077-design-research.md` | md | 12.6 KB | `de5a3f8247d81bd55ced6c7538b883b4` | — | cyberpunk2077-design-research.md | — | live |
| `skyrydahs-characters/refs/licenses.json` | json | 821 B | `12fbc3af44db5386f01afc4440996516` | — | licenses.json | — | live |
| `skyrydahs-characters/refs/roblox-design-research.md` | md | 6.7 KB | `405104439176422d2762be792af97171` | — | roblox-design-research.md | — | live |
| `skyrydahs-characters/refs/vr-games-research.txt` | txt | 39.8 KB | `a9b08d2056bcaa84d4de549330d50314` | — | vr-games-research.txt | — | live |
| `skyrydahs-characters/shared/at-skate/at-skate-meshy-1k-mr.png` | png | 1.16 MB | `7151778b679874209275f81e34766bfe` | — | at-skate-meshy-1k-mr.png | — | live |
| `skyrydahs-characters/shared/at-skate/at-skate-meshy-1k-normal.png` | png | 1.22 MB | `ef9dcbc9a2ac814b54969a606f0e13c4` | — | at-skate-meshy-1k-normal.png | — | live |
| `skyrydahs-characters/shared/at-skate/at-skate-meshy-1k.png` | png | 1.11 MB | `8444cc991ac53e79325b3721c22fe23c` | — | at-skate-meshy-1k.png | — | live |
| `skyrydahs-characters/shared/at-skate/at-skate-meshy-v2-1k-mr.png` | png | 902.6 KB | `299f1da4ab30e3e95fc8d7be4ffef1d7` | — | at-skate-meshy-v2-1k-mr.png | — | live |
| `skyrydahs-characters/shared/at-skate/at-skate-meshy-v2-1k-normal.png` | png | 1009.0 KB | `d6893f993f8516590ab84963c3b9b57f` | — | at-skate-meshy-v2-1k-normal.png | — | live |
| `skyrydahs-characters/shared/at-skate/at-skate-meshy-v2-1k.png` | png | 1.08 MB | `5350f2ae6535ea4ec71ce9e5b21847a0` | — | at-skate-meshy-v2-1k.png | — | live |
| `skyrydahs-characters/shared/at-skate/at-skate-meshy.blend` | blend | 7.47 MB | `3815f043512aef31b240639e5e593b48` | — | at-skate-meshy.blend | — | live |
| `skyrydahs-characters/shared/at-skate/at-skate-module.blend` | blend | 608.1 KB | `15361df4b654b3aab270ef1d26c6dab8` | — | at-skate-module.blend | — | live |
| `skyrydahs-characters/shared/at-skate/at-skate-module.glb` | glb | 220.4 KB | `2f91c4982deca5c49e04ceda7f17460c` | tris=3452; meshes=Chassis,Cuff,Shell,Wheel_F | at-skate-module.glb | — | live |
| `skyrydahs-characters/shared/at-skate/ktx2/at-skate-meshy-v2-1k-mr.ktx2` | ktx2 | 605.3 KB | `d30bafad5a651dee61db81791cbd36c7` | — | at-skate-meshy-v2-1k-mr.ktx2 | — | live |
| `skyrydahs-characters/shared/at-skate/ktx2/at-skate-meshy-v2-1k-normal.ktx2` | ktx2 | 764.7 KB | `1a930016af66646f16a171d0e5378b42` | — | at-skate-meshy-v2-1k-normal.ktx2 | — | live |
| `skyrydahs-characters/shared/at-skate/ktx2/at-skate-meshy-v2-1k.ktx2` | ktx2 | 178.2 KB | `8c41cfe6b7ba99cc07419f8f0ab5162f` | — | at-skate-meshy-v2-1k.ktx2 | — | live |
| `skyrydahs-characters/shared/crew-coins/_archive/volt-back-basecolor.png` | png | 142.3 KB | `d95bce998ab42c0b6af3b07e1c0fe2bd` | — | Crew coin volt-back-basecolor.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/_archive/volt-back-height.png` | png | 47.8 KB | `81e473e439d3de1557497f7606aa7d74` | — | Crew coin volt-back-height.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/_archive/volt-back-normal.png` | png | 112.0 KB | `d4187d151aec2f9f9ece411415cda127` | — | Crew coin volt-back-normal.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/_archive/volt-back-orm.png` | png | 77.9 KB | `33fc4c26006e110cb0e15136458c9632` | — | Crew coin volt-back-orm.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/_archive/volt-coin.blend` | blend | 772.4 KB | `1c6c3012382017ba078bee6d24f12e42` | — | Crew coin volt-coin.blend | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/_archive/volt-coin.glb` | glb | 689.3 KB | `dac897a227a0a4679a3f703fd3e0ddb0` | tris=1024; meshes=volt-coin | Crew coin volt-coin.glb | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/_archive/volt-edge-basecolor.png` | png | 357 B | `6fa44f7ea38e5ade3709cc6e3230c36c` | — | Crew coin volt-edge-basecolor.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/_archive/volt-edge-normal.png` | png | 360 B | `7e74c36d8313cc251d3ed0bbf4b7cc11` | — | Crew coin volt-edge-normal.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/_archive/volt-edge-orm.png` | png | 348 B | `62502ad513a7c9a45381cb76e976f1b9` | — | Crew coin volt-edge-orm.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/_archive/volt-front-basecolor.png` | png | 138.0 KB | `dd737abc0685707da7e60a3d12907095` | — | Crew coin volt-front-basecolor.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/_archive/volt-front-height.png` | png | 47.8 KB | `2bf4ff93b67ddbd62e6737ede127f74b` | — | Crew coin volt-front-height.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/_archive/volt-front-normal.png` | png | 107.3 KB | `9385f3374a66aff957b8b9cf8b616bfa` | — | Crew coin volt-front-normal.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/_archive/volt-front-orm.png` | png | 76.2 KB | `404e256841d123dab04fe86bdf8e67c0` | — | Crew coin volt-front-orm.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/anubis-coin.glb` | glb | 735.3 KB | `9bb5d21bbec9e57f7b4b3b199c8824e2` | tris=1024; meshes=anubis-coin | Crew coin anubis-coin.glb | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/behemoth-coin.glb` | glb | 713.5 KB | `2a3f77d0b0325846f67994cc50ef61fc` | tris=1024; meshes=behemoth-coin | Crew coin behemoth-coin.glb | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/blend/anubis-coin.blend` | blend | 680.2 KB | `051693c9fe5b1170bb35fa2c740374de` | — | Crew coin anubis-coin.blend | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/blend/behemoth-coin.blend` | blend | 657.1 KB | `41a0b3e002897f7e21028ed7940f1a32` | — | Crew coin behemoth-coin.blend | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/blend/code-e-coin.blend` | blend | 928.6 KB | `fd27d102dddf6d50313cf1dd60895669` | — | Crew coin code-e-coin.blend | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/blend/genesis-coin.blend` | blend | 828.7 KB | `930c58ec00e3034a29c66c0f3b257591` | — | Crew coin genesis-coin.blend | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/blend/kogarasumaru-coin.blend` | blend | 902.0 KB | `4fab92ba1427265b74a20d88a317fb5d` | — | Crew coin kogarasumaru-coin.blend | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/blend/rust-claw-coin.blend` | blend | 921.5 KB | `2afb535f3489540f08d194f67eccc60b` | — | Crew coin rust-claw-coin.blend | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/blend/sleeping-forest-coin.blend` | blend | 728.7 KB | `821888f72a8e7278dcc6793259242c96` | — | Crew coin sleeping-forest-coin.blend | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/blend/static-angels-coin.blend` | blend | 862.4 KB | `10c3534f7238b076ef26be1025149b2a` | — | Crew coin static-angels-coin.blend | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/blend/team-storm-coin.blend` | blend | 808.5 KB | `62bc643b48792e20c883915b9ffc3631` | — | Crew coin team-storm-coin.blend | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/blend/tool-toul-to-coin.blend` | blend | 715.1 KB | `b36cf8cc65cdea63a2c16b392d1e103b` | — | Crew coin tool-toul-to-coin.blend | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/blend/volt-coin.blend` | blend | 767.4 KB | `71905a08fb3b6676a1cabc9d06bc6c35` | — | Crew coin volt-coin.blend | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/build_coins.py` | py | 4.0 KB | `4b2f607714adfb81e109caf60166c3f3` | — | Crew coin build_coins.py | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/code-e-coin.glb` | glb | 957.8 KB | `123c5e2bf0fc0f1dae904801df8bb698` | tris=1024; meshes=code-e-coin | Crew coin code-e-coin.glb | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/coins-contact-sheet.png` | png | 3.09 MB | `5f7df082148f45bb24e1aa70b3533dfc` | — | Crew coin coins-contact-sheet.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/gen_coin_textures.py` | py | 8.9 KB | `27cfbd8138bcd06297cc46eca3faeaac` | — | Crew coin gen_coin_textures.py | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/genesis-coin.glb` | glb | 876.5 KB | `67b16c0b794731522bc9631574279085` | tris=1024; meshes=genesis-coin | Crew coin genesis-coin.glb | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/kogarasumaru-coin.glb` | glb | 918.9 KB | `d9e1fde455ce350ecfe8cd54c8713153` | tris=1024; meshes=kogarasumaru-coin | Crew coin kogarasumaru-coin.glb | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/render_coins.py` | py | 9.8 KB | `4efdca4133261e7fda736633e77629b7` | — | Crew coin render_coins.py | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/renders/coin-in-hand.png` | png | 1.10 MB | `d6cd4d7df6d034a33ffab78d06dcda86` | — | Crew coin coin-in-hand.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/renders/coins-contact-raw.png` | png | 4.08 MB | `a95c8bc264bc2af286ec7774ade91a10` | — | Crew coin coins-contact-raw.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/renders/turntable-code-e.gif` | gif | 3.06 MB | `50ac71bde61aa06e3a69b0d4eb55d568` | — | Crew coin turntable-code-e.gif | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/rust-claw-coin.glb` | glb | 943.1 KB | `410d44f471c9448c765e7bdaae7c746a` | tris=1024; meshes=rust-claw-coin | Crew coin rust-claw-coin.glb | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/sleeping-forest-coin.glb` | glb | 773.7 KB | `5e28068ab6445a3186a077def05bd828` | tris=1024; meshes=sleeping-forest-coin | Crew coin sleeping-forest-coin.glb | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/static-angels-coin.glb` | glb | 896.6 KB | `101c68f228df04ddfaa75ac3875ed94b` | tris=1024; meshes=static-angels-coin | Crew coin static-angels-coin.glb | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/team-storm-coin.glb` | glb | 840.0 KB | `1eac8549621ff0b5dda89fce45bbf66d` | tris=1024; meshes=team-storm-coin | Crew coin team-storm-coin.glb | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/anubis-back-basecolor.jpg` | jpg | 99.1 KB | `e768dc9f75b72e7cdd2e0a44bdf6ff9f` | — | Crew coin anubis-back-basecolor.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/anubis-back-height.png` | png | 122.4 KB | `5a43d591926dfbd465846ee001f169c7` | — | Crew coin anubis-back-height.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/anubis-back-normal.jpg` | jpg | 163.2 KB | `4f2c8006bf8f4fd9a76a3ad5f09b3862` | — | Crew coin anubis-back-normal.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/anubis-back-orm.jpg` | jpg | 96.0 KB | `01e903349cd008c4d70b851883ca44fb` | — | Crew coin anubis-back-orm.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/anubis-edge-basecolor.png` | png | 417 B | `28c83412223019b9ff09d1f8875dec81` | — | Crew coin anubis-edge-basecolor.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/anubis-edge-normal.png` | png | 360 B | `7e74c36d8313cc251d3ed0bbf4b7cc11` | — | Crew coin anubis-edge-normal.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/anubis-edge-orm.png` | png | 348 B | `8ada7bcb2155b054af01e4f80db1334e` | — | Crew coin anubis-edge-orm.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/anubis-front-basecolor.jpg` | jpg | 98.2 KB | `f32bc213f362163805cf0cf0d92b8a3e` | — | Crew coin anubis-front-basecolor.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/anubis-front-height.png` | png | 117.2 KB | `8ab6bced2877a53d7e6ba8e778a6df4e` | — | Crew coin anubis-front-height.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/anubis-front-normal.jpg` | jpg | 149.9 KB | `1dd0db77ee4ba5841720a0fd8323fd65` | — | Crew coin anubis-front-normal.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/anubis-front-orm.jpg` | jpg | 93.3 KB | `01d0904ef36a7f24d313142adaaf3f5a` | — | Crew coin anubis-front-orm.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/behemoth-back-basecolor.jpg` | jpg | 73.8 KB | `02592509fc938b7d3624e5d7464e6eb3` | — | Crew coin behemoth-back-basecolor.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/behemoth-back-height.png` | png | 126.2 KB | `cfc3b8281f760dc087064dc00028e007` | — | Crew coin behemoth-back-height.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/behemoth-back-normal.jpg` | jpg | 170.9 KB | `52b67925238e62bb79e534e1ca5c3f4d` | — | Crew coin behemoth-back-normal.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/behemoth-back-orm.jpg` | jpg | 101.8 KB | `16959a5ad88d9cb3d79b2f5553d97fc6` | — | Crew coin behemoth-back-orm.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/behemoth-edge-basecolor.png` | png | 349 B | `8519c62ba82b831a79e546788304652e` | — | Crew coin behemoth-edge-basecolor.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/behemoth-edge-normal.png` | png | 360 B | `7e74c36d8313cc251d3ed0bbf4b7cc11` | — | Crew coin behemoth-edge-normal.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/behemoth-edge-orm.png` | png | 348 B | `c4b59f094bc31674ca0c06a1743cd3d0` | — | Crew coin behemoth-edge-orm.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/behemoth-front-basecolor.jpg` | jpg | 76.6 KB | `7e37b093a28d7fa229faa72c93e4d857` | — | Crew coin behemoth-front-basecolor.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/behemoth-front-height.png` | png | 118.3 KB | `b50f51d9e504722864f1f92661a1c8d6` | — | Crew coin behemoth-front-height.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/behemoth-front-normal.jpg` | jpg | 156.2 KB | `2b43137169567784e9a2b3ad70d81777` | — | Crew coin behemoth-front-normal.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/behemoth-front-orm.jpg` | jpg | 98.4 KB | `fca64cb8cd17919fba18e03d3d2b624d` | — | Crew coin behemoth-front-orm.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/code-e-back-basecolor.jpg` | jpg | 146.9 KB | `a74866833662aeb73cf09acc9d9fcbf3` | — | Crew coin code-e-back-basecolor.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/code-e-back-height.png` | png | 144.5 KB | `4085454756e42a21071eed5abf2ddd72` | — | Crew coin code-e-back-height.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/code-e-back-normal.jpg` | jpg | 192.4 KB | `84199a76ef70b0f8326c315479411c16` | — | Crew coin code-e-back-normal.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/code-e-back-orm.jpg` | jpg | 118.3 KB | `ddbfbb28174db5622ab7547eeb7a82eb` | — | Crew coin code-e-back-orm.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/code-e-edge-basecolor.png` | png | 363 B | `eccb0a97e299a8ed3b73d6014dd2c5c1` | — | Crew coin code-e-edge-basecolor.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/code-e-edge-normal.png` | png | 360 B | `7e74c36d8313cc251d3ed0bbf4b7cc11` | — | Crew coin code-e-edge-normal.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/code-e-edge-orm.png` | png | 348 B | `9a9ca0d6e59a12059f604bc8790489eb` | — | Crew coin code-e-edge-orm.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/code-e-front-basecolor.jpg` | jpg | 146.3 KB | `180e0507fc0c4ffb7cca6485505fbbf7` | — | Crew coin code-e-front-basecolor.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/code-e-front-height.png` | png | 151.0 KB | `467926953383bfbcd84267f4f5efcd0c` | — | Crew coin code-e-front-height.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/code-e-front-normal.jpg` | jpg | 196.0 KB | `ba5d43f907bfac4bdc89b5875823b293` | — | Crew coin code-e-front-normal.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/code-e-front-orm.jpg` | jpg | 122.4 KB | `f8b1382478d88ec4ef75b2bde03eef49` | — | Crew coin code-e-front-orm.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/genesis-back-basecolor.jpg` | jpg | 136.0 KB | `e4c659d800a12a681940855f6b190362` | — | Crew coin genesis-back-basecolor.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/genesis-back-height.png` | png | 128.7 KB | `8d774324240ef1c5cb3e62ea23a3cffd` | — | Crew coin genesis-back-height.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/genesis-back-normal.jpg` | jpg | 173.8 KB | `0dd6d5a9b6002a724a481e7ad26a7a37` | — | Crew coin genesis-back-normal.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/genesis-back-orm.jpg` | jpg | 107.0 KB | `b031949188f3ca8f3893d9571c7023a5` | — | Crew coin genesis-back-orm.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/genesis-edge-basecolor.png` | png | 426 B | `328f7425150624a0a00d14af6ee41241` | — | Crew coin genesis-edge-basecolor.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/genesis-edge-normal.png` | png | 360 B | `7e74c36d8313cc251d3ed0bbf4b7cc11` | — | Crew coin genesis-edge-normal.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/genesis-edge-orm.png` | png | 348 B | `9a9ca0d6e59a12059f604bc8790489eb` | — | Crew coin genesis-edge-orm.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/genesis-front-basecolor.jpg` | jpg | 139.4 KB | `04691956fa003a1240618d098099a36d` | — | Crew coin genesis-front-basecolor.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/genesis-front-height.png` | png | 127.0 KB | `b087773a642ce4ec4f4d50ff85589232` | — | Crew coin genesis-front-height.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/genesis-front-normal.jpg` | jpg | 173.1 KB | `beeda3f01dfee927b58d69e58036c133` | — | Crew coin genesis-front-normal.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/genesis-front-orm.jpg` | jpg | 111.5 KB | `f066a1ee177cb26fa2c2a384f0f6e21b` | — | Crew coin genesis-front-orm.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/kogarasumaru-back-basecolor.jpg` | jpg | 121.3 KB | `8839deddb481581793bf6b332641766b` | — | Crew coin kogarasumaru-back-basecolor.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/kogarasumaru-back-height.png` | png | 132.7 KB | `4ffa043db7c9b12975d152aa342115db` | — | Crew coin kogarasumaru-back-height.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/kogarasumaru-back-normal.jpg` | jpg | 179.8 KB | `1fef594dc95eca0a85d1a918da85bb88` | — | Crew coin kogarasumaru-back-normal.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/kogarasumaru-back-orm.jpg` | jpg | 135.5 KB | `f78ed1548864b7292fc447bc8553907a` | — | Crew coin kogarasumaru-back-orm.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/kogarasumaru-edge-basecolor.png` | png | 412 B | `f1f048a1e0f9c071df3dcbb0656099b1` | — | Crew coin kogarasumaru-edge-basecolor.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/kogarasumaru-edge-normal.png` | png | 360 B | `7e74c36d8313cc251d3ed0bbf4b7cc11` | — | Crew coin kogarasumaru-edge-normal.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/kogarasumaru-edge-orm.png` | png | 348 B | `2bbf81ccb14bc8e5ec82b0fe9e6b3ec4` | — | Crew coin kogarasumaru-edge-orm.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/kogarasumaru-front-basecolor.jpg` | jpg | 129.7 KB | `f6f4e5cd473c69c1f08e7052f0204815` | — | Crew coin kogarasumaru-front-basecolor.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/kogarasumaru-front-height.png` | png | 135.6 KB | `daa7d6a7bcff730b85d4b436cb704685` | — | Crew coin kogarasumaru-front-height.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/kogarasumaru-front-normal.jpg` | jpg | 179.1 KB | `cfc56e5fdde25c76b596bca947e93f29` | — | Crew coin kogarasumaru-front-normal.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/kogarasumaru-front-orm.jpg` | jpg | 137.8 KB | `68179b3975e994c31bf2a0de7d70786b` | — | Crew coin kogarasumaru-front-orm.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/rust-claw-back-basecolor.jpg` | jpg | 132.2 KB | `a5284f61e9f89bd6fa30c178b692e5e8` | — | Crew coin rust-claw-back-basecolor.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/rust-claw-back-height.png` | png | 141.4 KB | `81c7694e4f22beabe0341dec96a22d53` | — | Crew coin rust-claw-back-height.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/rust-claw-back-normal.jpg` | jpg | 190.7 KB | `9be8d61cd0d7bed3ec0353a7d6b5f2c6` | — | Crew coin rust-claw-back-normal.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/rust-claw-back-orm.jpg` | jpg | 115.5 KB | `4bd22f2a68a8d26779a4664521f8ed65` | — | Crew coin rust-claw-back-orm.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/rust-claw-edge-basecolor.png` | png | 416 B | `b05cde3790b967109a62a38c4beee5d8` | — | Crew coin rust-claw-edge-basecolor.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/rust-claw-edge-normal.png` | png | 360 B | `7e74c36d8313cc251d3ed0bbf4b7cc11` | — | Crew coin rust-claw-edge-normal.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/rust-claw-edge-orm.png` | png | 348 B | `7c548aebbdf6cf028d276c8a90d755d0` | — | Crew coin rust-claw-edge-orm.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/rust-claw-front-basecolor.jpg` | jpg | 143.4 KB | `5173f9d1139c736514a7883727fb523e` | — | Crew coin rust-claw-front-basecolor.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/rust-claw-front-height.png` | png | 150.7 KB | `8e3c5008bd043b716dbb0ea30ea3fa7f` | — | Crew coin rust-claw-front-height.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/rust-claw-front-normal.jpg` | jpg | 196.2 KB | `2fc02eb33de64eb6bd06dd1f0044f672` | — | Crew coin rust-claw-front-normal.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/rust-claw-front-orm.jpg` | jpg | 129.4 KB | `06f3675313e82c75cd0434954147fb5c` | — | Crew coin rust-claw-front-orm.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/sleeping-forest-back-basecolor.jpg` | jpg | 103.0 KB | `b074a978eb4584a6f4e105072bb2385b` | — | Crew coin sleeping-forest-back-basecolor.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/sleeping-forest-back-height.png` | png | 129.8 KB | `88026b220a6e62365b9c6479240aaf4b` | — | Crew coin sleeping-forest-back-height.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/sleeping-forest-back-normal.jpg` | jpg | 174.6 KB | `5ea4bafc88bef15263052c992aeb1b39` | — | Crew coin sleeping-forest-back-normal.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/sleeping-forest-back-orm.jpg` | jpg | 105.3 KB | `6e217a16c23baae39053c19acbc6f4c1` | — | Crew coin sleeping-forest-back-orm.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/sleeping-forest-edge-basecolor.png` | png | 412 B | `a1bffddfad965045dde886bcc3693c3f` | — | Crew coin sleeping-forest-edge-basecolor.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/sleeping-forest-edge-normal.png` | png | 360 B | `7e74c36d8313cc251d3ed0bbf4b7cc11` | — | Crew coin sleeping-forest-edge-normal.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/sleeping-forest-edge-orm.png` | png | 348 B | `8e779f04a3d5ad22fc3c9ff6b1baa323` | — | Crew coin sleeping-forest-edge-orm.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/sleeping-forest-front-basecolor.jpg` | jpg | 92.5 KB | `1cee8249199ddb5066b8d7dac7b98a95` | — | Crew coin sleeping-forest-front-basecolor.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/sleeping-forest-front-height.png` | png | 121.4 KB | `e14247cef25cd9e32555f2f1036ec9fe` | — | Crew coin sleeping-forest-front-height.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/sleeping-forest-front-normal.jpg` | jpg | 159.2 KB | `3544eb2159834aca746f9ee06675f34a` | — | Crew coin sleeping-forest-front-normal.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/sleeping-forest-front-orm.jpg` | jpg | 103.2 KB | `c3b1c26f20bd621bab31b359dce47ed4` | — | Crew coin sleeping-forest-front-orm.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/static-angels-back-basecolor.jpg` | jpg | 127.8 KB | `b51e46196fd4c48ec7e9dfa5d152b63b` | — | Crew coin static-angels-back-basecolor.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/static-angels-back-height.png` | png | 136.6 KB | `086b5e9a49e3af46ff83366a69b670f5` | — | Crew coin static-angels-back-height.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/static-angels-back-normal.jpg` | jpg | 188.4 KB | `299b0063de21b5b3e3ed627994c262c6` | — | Crew coin static-angels-back-normal.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/static-angels-back-orm.jpg` | jpg | 117.3 KB | `c83b4188397524c3ab4762fc913647bd` | — | Crew coin static-angels-back-orm.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/static-angels-edge-basecolor.png` | png | 411 B | `60e180ea0828ecf65b111f5b27bb3a16` | — | Crew coin static-angels-edge-basecolor.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/static-angels-edge-normal.png` | png | 360 B | `7e74c36d8313cc251d3ed0bbf4b7cc11` | — | Crew coin static-angels-edge-normal.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/static-angels-edge-orm.png` | png | 348 B | `9254f3826bf079781b5f9ae30a43e402` | — | Crew coin static-angels-edge-orm.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/static-angels-front-basecolor.jpg` | jpg | 128.9 KB | `35eef64d1a90b4df7d6cf9d7741bbcc6` | — | Crew coin static-angels-front-basecolor.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/static-angels-front-height.png` | png | 133.8 KB | `9e5de9ff29ffbb9df0897a4ce6a85d8d` | — | Crew coin static-angels-front-height.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/static-angels-front-normal.jpg` | jpg | 180.9 KB | `8ff569d4ae7c3a1cf993115ab954fe4e` | — | Crew coin static-angels-front-normal.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/static-angels-front-orm.jpg` | jpg | 117.7 KB | `d3bb6a0d4f620ede6b73d7881e1716c1` | — | Crew coin static-angels-front-orm.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/team-storm-back-basecolor.jpg` | jpg | 110.9 KB | `ea90c7bad3f48f98eff53585e3c579c5` | — | Crew coin team-storm-back-basecolor.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/team-storm-back-height.png` | png | 129.8 KB | `9e2f08374b600aade743a408955d895a` | — | Crew coin team-storm-back-height.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/team-storm-back-normal.jpg` | jpg | 176.0 KB | `3d5abef493d070b8c610406c957116ce` | — | Crew coin team-storm-back-normal.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/team-storm-back-orm.jpg` | jpg | 103.6 KB | `5264334fcfe36b88331be62b149bfae4` | — | Crew coin team-storm-back-orm.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/team-storm-edge-basecolor.png` | png | 357 B | `6fa44f7ea38e5ade3709cc6e3230c36c` | — | Crew coin team-storm-edge-basecolor.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/team-storm-edge-normal.png` | png | 360 B | `7e74c36d8313cc251d3ed0bbf4b7cc11` | — | Crew coin team-storm-edge-normal.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/team-storm-edge-orm.png` | png | 348 B | `62502ad513a7c9a45381cb76e976f1b9` | — | Crew coin team-storm-edge-orm.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/team-storm-front-basecolor.jpg` | jpg | 122.0 KB | `7696e5f2e9f3c60ce9b8ce2a03b7a96a` | — | Crew coin team-storm-front-basecolor.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/team-storm-front-height.png` | png | 133.3 KB | `5903fd6fe101563c6e7ce74a7252b950` | — | Crew coin team-storm-front-height.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/team-storm-front-normal.jpg` | jpg | 177.2 KB | `98986a9b0d016160df717a5cc4c08763` | — | Crew coin team-storm-front-normal.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/team-storm-front-orm.jpg` | jpg | 114.7 KB | `dd8b1e661c16cdb326c78a4da5b65fac` | — | Crew coin team-storm-front-orm.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/tool-toul-to-back-basecolor.jpg` | jpg | 80.3 KB | `57f543e81c046336c9db35a8b398f39b` | — | Crew coin tool-toul-to-back-basecolor.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/tool-toul-to-back-height.png` | png | 130.8 KB | `62595ee1f6b86439f553cfd143383082` | — | Crew coin tool-toul-to-back-height.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/tool-toul-to-back-normal.jpg` | jpg | 175.8 KB | `c022d8cbfda7e372877515c2ee8de6fe` | — | Crew coin tool-toul-to-back-normal.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/tool-toul-to-back-orm.jpg` | jpg | 102.0 KB | `eb05143249ff7e717a02bf703ad76293` | — | Crew coin tool-toul-to-back-orm.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/tool-toul-to-edge-basecolor.png` | png | 354 B | `d8b71878aa1da395ec6f5213a62548fc` | — | Crew coin tool-toul-to-edge-basecolor.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/tool-toul-to-edge-normal.png` | png | 360 B | `7e74c36d8313cc251d3ed0bbf4b7cc11` | — | Crew coin tool-toul-to-edge-normal.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/tool-toul-to-edge-orm.png` | png | 348 B | `8ada7bcb2155b054af01e4f80db1334e` | — | Crew coin tool-toul-to-edge-orm.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/tool-toul-to-front-basecolor.jpg` | jpg | 82.0 KB | `33c894ada7ea67b5295de384d84a1ac9` | — | Crew coin tool-toul-to-front-basecolor.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/tool-toul-to-front-height.png` | png | 130.8 KB | `68dc1b96215624c9387690b228e633df` | — | Crew coin tool-toul-to-front-height.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/tool-toul-to-front-normal.jpg` | jpg | 172.1 KB | `dd510bcdf0a6382cb3b07cdf998fa596` | — | Crew coin tool-toul-to-front-normal.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/tool-toul-to-front-orm.jpg` | jpg | 105.1 KB | `c6a2bff5fb1870998efe3a418982aa84` | — | Crew coin tool-toul-to-front-orm.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/volt-back-basecolor.jpg` | jpg | 108.1 KB | `845a20d8c826b439bf33c68af971a8db` | — | Crew coin volt-back-basecolor.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/volt-back-height.png` | png | 126.5 KB | `dc0cb49f7d6219caebae476d359330eb` | — | Crew coin volt-back-height.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/volt-back-normal.jpg` | jpg | 170.5 KB | `8d5e4bcb9ec5b1ff9e49c5884838b521` | — | Crew coin volt-back-normal.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/volt-back-orm.jpg` | jpg | 101.2 KB | `c99ecf8487c18d2373a4863d19a863c1` | — | Crew coin volt-back-orm.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/volt-edge-basecolor.png` | png | 357 B | `6fa44f7ea38e5ade3709cc6e3230c36c` | — | Crew coin volt-edge-basecolor.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/volt-edge-normal.png` | png | 360 B | `7e74c36d8313cc251d3ed0bbf4b7cc11` | — | Crew coin volt-edge-normal.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/volt-edge-orm.png` | png | 348 B | `62502ad513a7c9a45381cb76e976f1b9` | — | Crew coin volt-edge-orm.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/volt-front-basecolor.jpg` | jpg | 115.7 KB | `b380f79682cc85b695b61d354d87e060` | — | Crew coin volt-front-basecolor.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/volt-front-height.png` | png | 127.0 KB | `502fc7c0e6e589a40db828e5fd450859` | — | Crew coin volt-front-height.png | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/volt-front-normal.jpg` | jpg | 166.8 KB | `5c0801253f602e4b8926b9f263e4a12d` | — | Crew coin volt-front-normal.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/textures/volt-front-orm.jpg` | jpg | 109.3 KB | `22e483d65b3fc3e55a102599293c0ac1` | — | Crew coin volt-front-orm.jpg | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/tool-toul-to-coin.glb` | glb | 753.0 KB | `b976a5afb09e510a9b069a1fdfa1e4bb` | tris=1024; meshes=tool-toul-to-coin | Crew coin tool-toul-to-coin.glb | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/validate_coins.py` | py | 1.2 KB | `d3fbd66d63e58bfabad9957fe3e7df05` | — | Crew coin validate_coins.py | coins UI | live |
| `skyrydahs-characters/shared/crew-coins/volt-coin.glb` | glb | 807.2 KB | `7069cfd6a2adea553fd65eb88161520e` | tris=1024; meshes=volt-coin | Crew coin volt-coin.glb | coins UI | live |
| `skyrydahs-characters/shared/crew-logos/_archive/volt-patch-height.png` | png | 228.1 KB | `70a1fbc6119d76a36086ce817fb38783` | — | Crew logo/patch volt-patch-height.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/_archive/volt-patch-normal.png` | png | 1.01 MB | `b41715b1cd6d846983471e9c3402f233` | — | Crew logo/patch volt-patch-normal.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/_archive/volt-patch-noshadow.png` | png | 1.05 MB | `f684ef1e9ea2d26bf13aeeca3fa77b75` | — | Crew logo/patch volt-patch-noshadow.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/_archive/volt-patch.png` | png | 1.07 MB | `f7ab4a51d3de0f06eec491edf90473cc` | — | Crew logo/patch volt-patch.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/_archive/volt.png` | png | 243.2 KB | `ae31dde36b51117f10e7f5730b0d41f1` | — | Crew logo/patch volt.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/_archive/volt.svg` | svg | 4.4 KB | `35488bac4097a50fd531854f708ab2c2` | — | Crew logo/patch volt.svg | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/anubis-patch-height.png` | png | 204.9 KB | `72c8449f197fe8ee7b57165ff03cc5ff` | — | Crew logo/patch anubis-patch-height.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/anubis-patch-normal.png` | png | 985.8 KB | `7e9aa0f4e76d30e852d66161560f18bc` | — | Crew logo/patch anubis-patch-normal.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/anubis-patch-noshadow.png` | png | 1.04 MB | `0e27a36ab23d7354b5b1a0010407511b` | — | Crew logo/patch anubis-patch-noshadow.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/anubis-patch.png` | png | 1.06 MB | `2c91b240e00686ac15ce07eca1867427` | — | Crew logo/patch anubis-patch.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/anubis.png` | png | 259.1 KB | `d4f74829c3fe655508c5a7fab0d9aa9d` | — | Crew logo/patch anubis.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/anubis.svg` | svg | 5.2 KB | `46341114c569145398359e17b7448b45` | — | Crew logo/patch anubis.svg | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/behemoth-patch-height.png` | png | 203.9 KB | `b62e607bb608fe5e41da06092f45f4c4` | — | Crew logo/patch behemoth-patch-height.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/behemoth-patch-normal.png` | png | 978.6 KB | `2cc366132ada5e9cf1c329a9ba0186aa` | — | Crew logo/patch behemoth-patch-normal.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/behemoth-patch-noshadow.png` | png | 988.1 KB | `59bd98b1e4bc57d959b5ffa57072f41a` | — | Crew logo/patch behemoth-patch-noshadow.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/behemoth-patch.png` | png | 1010.7 KB | `f6577c9428482c08c7b1599e58eff9b0` | — | Crew logo/patch behemoth-patch.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/behemoth.png` | png | 226.3 KB | `346f14071881191351fa0fe30b1f56c9` | — | Crew logo/patch behemoth.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/behemoth.svg` | svg | 5.2 KB | `8e713de935d32d8421ee78d01ea5b5db` | — | Crew logo/patch behemoth.svg | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/caali-g-patch-height.png` | png | 216.6 KB | `428f3c09eb7cc3cee188bc15a7baf592` | — | Crew logo/patch caali-g-patch-height.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/caali-g-patch-normal.png` | png | 1014.8 KB | `942debc029be70d951c0df50350ab860` | — | Crew logo/patch caali-g-patch-normal.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/caali-g-patch-noshadow.png` | png | 1000.3 KB | `7508e0bb8cf55866e3338768f16887bd` | — | Crew logo/patch caali-g-patch-noshadow.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/caali-g-patch.png` | png | 1022.9 KB | `a0e258ce4ff4d6982cdf410375263266` | — | Crew logo/patch caali-g-patch.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/caali-g.png` | png | 248.8 KB | `807c2406e48ba29f17575d7a8864555a` | — | Crew logo/patch caali-g.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/caali-g.svg` | svg | 2.7 KB | `716631fd23da8290b298cfe12370df13` | — | Crew logo/patch caali-g.svg | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/check_readability.py` | py | 1.2 KB | `8d00f1f4762e2b60aa4e545364f993ed` | — | Crew logo/patch check_readability.py | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/code-e-patch-height.png` | png | 222.5 KB | `ce8ddb00b9aedf5379b0888a4b15618b` | — | Crew logo/patch code-e-patch-height.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/code-e-patch-normal.png` | png | 1.01 MB | `28b3add3a76181769f23c59e42d4e2b1` | — | Crew logo/patch code-e-patch-normal.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/code-e-patch-noshadow.png` | png | 1006.2 KB | `19b6954f0ab70d76fd72631c72bced61` | — | Crew logo/patch code-e-patch-noshadow.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/code-e-patch.png` | png | 1.00 MB | `7d3de268a23ef4a7d1c7e854ce515faa` | — | Crew logo/patch code-e-patch.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/code-e.png` | png | 286.4 KB | `0b88014d23df7708c4d61787fb4477b8` | — | Crew logo/patch code-e.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/code-e.svg` | svg | 6.5 KB | `c02588849c7181396232aafdad889b76` | — | Crew logo/patch code-e.svg | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/gen_caali_g_emblem.py` | py | 2.4 KB | `f22d33a45942cd43cb934991f6b80f5a` | — | Crew logo/patch gen_caali_g_emblem.py | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/gen_colorways.py` | py | 6.0 KB | `ebf660b2794293924e0ebaebcd8df9c6` | — | Crew logo/patch gen_colorways.py | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/gen_crew_logos.py` | py | 15.6 KB | `4d7bb8a05e921b7dae7d2d04730dba63` | — | Crew logo/patch gen_crew_logos.py | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/gen_crew_patches.py` | py | 8.2 KB | `7bd1ba452dc0607ca67b8cd30ef5ddf3` | — | Crew logo/patch gen_crew_patches.py | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/genesis-patch-height.png` | png | 194.5 KB | `601a11dd07c422de692a525dfede4843` | — | Crew logo/patch genesis-patch-height.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/genesis-patch-normal.png` | png | 956.8 KB | `7765f76d05d28a66624770901906daa3` | — | Crew logo/patch genesis-patch-normal.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/genesis-patch-noshadow.png` | png | 1.11 MB | `4e70127713b0411a64275e795bfebc3f` | — | Crew logo/patch genesis-patch-noshadow.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/genesis-patch.png` | png | 1.13 MB | `389b04a08c0eb22698965ffbbe101882` | — | Crew logo/patch genesis-patch.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/genesis.png` | png | 273.4 KB | `d88792c5daae69a4f5a5728aea60b766` | — | Crew logo/patch genesis.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/genesis.svg` | svg | 5.5 KB | `d17f8a0729b7b4a29500f68b361e085e` | — | Crew logo/patch genesis.svg | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/jacket-colorways-preview.png` | png | 1.18 MB | `530052d51b821bdb3ec8e8bb37206527` | — | Crew logo/patch jacket-colorways-preview.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/jacket-colorways.json` | json | 23.7 KB | `739dd28aefb5da7e805780257970d415` | — | Crew logo/patch jacket-colorways.json | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/kogarasumaru-patch-height.png` | png | 235.9 KB | `5eb5b2e8df05772f79afcdbc2082c861` | — | Crew logo/patch kogarasumaru-patch-height.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/kogarasumaru-patch-normal.png` | png | 1.02 MB | `d315d199de9d7209ddd0ae01973ac608` | — | Crew logo/patch kogarasumaru-patch-normal.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/kogarasumaru-patch-noshadow.png` | png | 1.04 MB | `2065df6c76fdcb501a133ef486fb28b2` | — | Crew logo/patch kogarasumaru-patch-noshadow.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/kogarasumaru-patch.png` | png | 1.06 MB | `6e2d610144d14800bd5cb62cc876cd9f` | — | Crew logo/patch kogarasumaru-patch.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/kogarasumaru.png` | png | 258.1 KB | `d296543817c8ccf50918b068a6dc6667` | — | Crew logo/patch kogarasumaru.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/kogarasumaru.svg` | svg | 8.5 KB | `6cb9435be79130b3a794dee4d5846911` | — | Crew logo/patch kogarasumaru.svg | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/logos-contact-sheet.png` | png | 2.09 MB | `1048b3f7c07abff6cb45c91e2314ccd5` | — | Crew logo/patch logos-contact-sheet.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/patch-readability-check.png` | png | 1.01 MB | `f7d60430e4f600f5d0001b24e7894d02` | — | Crew logo/patch patch-readability-check.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/rust-claw-patch-height.png` | png | 249.8 KB | `6bc0f6c8cd11c967af147fad58ae13bc` | — | Crew logo/patch rust-claw-patch-height.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/rust-claw-patch-normal.png` | png | 1.06 MB | `a390dfdfc28e8d3fb8938fa1058aaac5` | — | Crew logo/patch rust-claw-patch-normal.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/rust-claw-patch-noshadow.png` | png | 1.19 MB | `05eaaa2cfa6e008f3a3b7ecacc50ad88` | — | Crew logo/patch rust-claw-patch-noshadow.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/rust-claw-patch.png` | png | 1.21 MB | `79cd597ad52221680d68a589ed2b2061` | — | Crew logo/patch rust-claw-patch.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/rust-claw.png` | png | 277.4 KB | `e935dca9055261fd8ec12673d6921e25` | — | Crew logo/patch rust-claw.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/rust-claw.svg` | svg | 7.0 KB | `565175c862171b09ee20ea9587ca9729` | — | Crew logo/patch rust-claw.svg | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/sleeping-forest-patch-height.png` | png | 228.6 KB | `99071a8c9b8ad9e9a2db7bd6b66b9388` | — | Crew logo/patch sleeping-forest-patch-height.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/sleeping-forest-patch-normal.png` | png | 1.03 MB | `2be38beca7f1b9d92160fe8794787662` | — | Crew logo/patch sleeping-forest-patch-normal.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/sleeping-forest-patch-noshadow.png` | png | 1.07 MB | `0d40288a874c6b6c1b8ff5af1d8c9307` | — | Crew logo/patch sleeping-forest-patch-noshadow.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/sleeping-forest-patch.png` | png | 1.10 MB | `1c9ff52b40cadbf6d5e57953f40e8b9f` | — | Crew logo/patch sleeping-forest-patch.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/sleeping-forest.png` | png | 264.7 KB | `eada739a3402c67079ae9a10ab928bdb` | — | Crew logo/patch sleeping-forest.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/sleeping-forest.svg` | svg | 6.9 KB | `321f79891c3b1168c8f8ffd0ac059bb9` | — | Crew logo/patch sleeping-forest.svg | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/static-angels-patch-height.png` | png | 210.4 KB | `f071aaf5bf601408ba69c214379f4273` | — | Crew logo/patch static-angels-patch-height.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/static-angels-patch-normal.png` | png | 1003.6 KB | `0a331c2f7b8ddb1048ab7de90336efda` | — | Crew logo/patch static-angels-patch-normal.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/static-angels-patch-noshadow.png` | png | 1.09 MB | `a056d8d03a9b1876f72225feda940fb0` | — | Crew logo/patch static-angels-patch-noshadow.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/static-angels-patch.png` | png | 1.12 MB | `88d4862f08f7eff83ccfd5c6c1fad504` | — | Crew logo/patch static-angels-patch.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/static-angels.png` | png | 281.8 KB | `b1ed30691ce1a7d88f4afe4be325729d` | — | Crew logo/patch static-angels.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/static-angels.svg` | svg | 6.7 KB | `9f624d191b355c4ed0c7c22ca9d52d52` | — | Crew logo/patch static-angels.svg | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/team-storm-before-after.png` | png | 343.6 KB | `aee802c03a175863865914c486527851` | — | Crew logo/patch team-storm-before-after.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/team-storm-patch-height.png` | png | 219.2 KB | `1ffb6d5256589fde38ab84e86d6d3abd` | — | Crew logo/patch team-storm-patch-height.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/team-storm-patch-normal.png` | png | 1010.8 KB | `6f97fb8c23388ae54d050cdb5e0b7e10` | — | Crew logo/patch team-storm-patch-normal.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/team-storm-patch-noshadow.png` | png | 1.10 MB | `80869ba580532ebe9cfff1c87830e41d` | — | Crew logo/patch team-storm-patch-noshadow.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/team-storm-patch.png` | png | 1.12 MB | `b7e3307d9c33d45653d414a18c5cacb9` | — | Crew logo/patch team-storm-patch.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/team-storm.png` | png | 279.1 KB | `ef6bd6f1954fbefc023c00e23952f5f3` | — | Crew logo/patch team-storm.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/team-storm.svg` | svg | 7.9 KB | `6fb4a83f04718cbc2b767df427f12f4d` | — | Crew logo/patch team-storm.svg | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/tool-toul-to-patch-height.png` | png | 210.2 KB | `a1e652ca05f3bb1cc49d937e612629c9` | — | Crew logo/patch tool-toul-to-patch-height.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/tool-toul-to-patch-normal.png` | png | 985.9 KB | `f7639333c64120d35e8afc7442b7e009` | — | Crew logo/patch tool-toul-to-patch-normal.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/tool-toul-to-patch-noshadow.png` | png | 896.4 KB | `642e670169d7604e45fd6639be8467c2` | — | Crew logo/patch tool-toul-to-patch-noshadow.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/tool-toul-to-patch.png` | png | 916.5 KB | `94e210ef298b1f50cb779748590ec20c` | — | Crew logo/patch tool-toul-to-patch.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/tool-toul-to.png` | png | 260.0 KB | `10037403d25f5daa00feb99b9e098149` | — | Crew logo/patch tool-toul-to.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/tool-toul-to.svg` | svg | 7.1 KB | `4a0dd88a32121f7dd2f7b4e729bd2564` | — | Crew logo/patch tool-toul-to.svg | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/volt-patch-height.png` | png | 214.0 KB | `6ee16b2c2c0f26fcc23cfd3e963e7ef2` | — | Crew logo/patch volt-patch-height.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/volt-patch-normal.png` | png | 998.7 KB | `0893f2d3ebc6bd9057cad9fdbe0ad630` | — | Crew logo/patch volt-patch-normal.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/volt-patch-noshadow.png` | png | 1.09 MB | `513c6c9fbc1ebbc96f2d9481e9bec891` | — | Crew logo/patch volt-patch-noshadow.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/volt-patch.png` | png | 1.11 MB | `8ea80a1b2ba3e1d21e82a8eb45f440d8` | — | Crew logo/patch volt-patch.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/volt.png` | png | 269.9 KB | `c323167504331ead23cb20668d42259d` | — | Crew logo/patch volt.png | kit logos / decals | live |
| `skyrydahs-characters/shared/crew-logos/volt.svg` | svg | 7.2 KB | `51d139827652d933ac3ba47ca90a2407` | — | Crew logo/patch volt.svg | kit logos / decals | live |
| `skyrydahs-characters/shared/fix_open_items.py` | py | 3.5 KB | `0f33ddeb011a2585aab99f6abb564b9d` | — | fix_open_items.py | — | live |
| `skyrydahs-characters/shared/gen_crew_pages.py` | py | 8.7 KB | `43b80f9deaa695e723a6d21873f11822` | — | gen_crew_pages.py | — | live |
| `skyrydahs-characters/shared/hero_face.py` | py | 11.1 KB | `6c540246f3b5bc28b6ca0e22da398a04` | — | hero_face.py | — | live |
| `skyrydahs-characters/shared/keyart.html` | html | 7.7 KB | `a65ced4aed645b3ecee936e910ae7377` | — | keyart.html | — | live |
| `skyrydahs-characters/shared/rider_lib.py` | py | 34.0 KB | `26d622d5739f584e0c8c4871ae0d1ba8` | — | rider_lib.py | — | live |
| `skyrydahs-characters/shared/rider_loader.js` | js | 15.8 KB | `d4e645a55e45432996a0ab215b1bec35` | — | rider_loader.js | — | live |
| `skyrydahs-characters/shared/shoot.sh` | sh | 1.0 KB | `d8dda5eaea58c0d8ed4223fbe8b6ae75` | — | shoot.sh | — | live |
| `skyrydahs-characters/shared/shoot_hero.sh` | sh | 1.2 KB | `e2d2f1fda964fb4fbb4e5a0b536901a9` | — | shoot_hero.sh | — | live |
| `skyrydahs-characters/shared/skeleton/README.md` | md | 4.8 KB | `4bdc26bae33a309238eb530b615a7490` | — | README.md | — | live |
| `skyrydahs-characters/shared/skeleton/rider-skeleton.blend` | blend | 624.3 KB | `4a170a10ee6f0ec1e4c0657f2bf8f579` | — | Shared Mixamo rider skeleton | Rigger bind | live |
| `skyrydahs-characters/shared/skeleton/rider-skeleton.bones.json` | json | 64.4 KB | `c2c1ef76552ffd4c356bb113dfc5623b` | — | Shared Mixamo rider skeleton | Rigger bind | live |
| `skyrydahs-characters/shared/skeleton/rider-skeleton.glb` | glb | 27.3 KB | `46cf26e936058052d26eccf19f08710c` | tris=4; joints=91; meshes=SkeletonProxy | Shared Mixamo rider skeleton | Rigger bind | live |
| `skyrydahs-characters/shared/upgrade_hero.py` | py | 8.6 KB | `60b1bad11d701e91ce0e13ce6ee6aa7d` | — | upgrade_hero.py | — | live |
| `skyrydahs-characters/simca/simca-npc.glb` | glb | 817.4 KB | `d06bd6e2da84454eb99fa4a3994722d2` | tris=27994; joints=155; LODs=Simca_NPC0 + 8 hair locks | Simca NPC / crowd (28k tris, 155 joints, 8 hair locks). | package_pwa + roster (solo / unaffiliated) | ready for rebuild |
| `skyrydahs-characters/simca/simca-npc.quest-ktx2.glb` | glb | 1.39 MB | `4ea675cf11209537801d2fe2b506b251` | tris=27994; joints=155; LODs=Simca_NPC0 + 8 hair locks | Simca NPC Quest KTX2 variant. | package_pwa + roster (solo / unaffiliated) | ready for rebuild |
| `skyrydahs-characters/simca/simca-npc.quest.glb` | glb | 817.4 KB | `9a557ac99aa43a300ab8e27e77e47d53` | tris=27994; joints=155; LODs=Simca_NPC0 + 8 hair locks | Simca NPC Quest variant (Draco). | package_pwa + roster (solo / unaffiliated) | ready for rebuild |
| `skyrydahs-characters/simca/simca-rider.glb` | glb | 2.98 MB | `4ab768a8caa588360b726bc91a8cd9a5` | tris=161249; joints=155; LODs=Simca_LOD0,Simca_LOD1,Simca_LOD2 + 8 hair locks | Simca player LOD0-2, solo/unaffiliated (white/green), 8 hair-lock spring chains (155 joints). | package_pwa + roster (solo / unaffiliated) | ready for rebuild |
| `skyrydahs-characters/simca/simca-rider.quest-ktx2.glb` | glb | 4.21 MB | `c2eaf989ed5f831babfd1b0051ffcd77` | tris=161249; joints=155; LODs=Simca_LOD0,Simca_LOD1,Simca_LOD2 + 8 hair locks | Simca player Quest KTX2 variant. | package_pwa + roster (solo / unaffiliated) | ready for rebuild |
| `skyrydahs-characters/simca/simca-rider.quest.glb` | glb | 2.83 MB | `ef9996905ba34e7ef0ffdcb7d1cad8b4` | tris=161249; joints=155; LODs=Simca_LOD0,Simca_LOD1,Simca_LOD2 + 8 hair locks | Simca player Quest variant (Draco). | package_pwa + roster (solo / unaffiliated) | ready for rebuild |
| `skyrydahs-characters/simca/simca-springs.md` | md | 2.6 KB | `580c2d7c22ef159adea0181453061655` | — | Simca spring-bone doc (copy next to the models): 8 hair chains × 8 bones, 155 joints. | — | live |
| `skyrydahs-characters/sleeping-forest/loader.js` | js | 1.3 KB | `9a5372dd1d251087d16a735246745c88` | — | Crew character asset loader.js | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/sleeping-forest/renders/34.png` | png | 156.5 KB | `1e674cead45f3001dd613edbc99718bf` | — | Crew character asset 34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/sleeping-forest/renders/back.png` | png | 140.7 KB | `bf8f01391330f7e19722b98f20f255a5` | — | Crew character asset back.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/sleeping-forest/renders/face_closeup.png` | png | 114.7 KB | `892c5d82075643f27096d7f421e4d20c` | — | Crew character asset face_closeup.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/sleeping-forest/renders/face_expressions.png` | png | 228.7 KB | `1b29729bfc38c101908e63905a535cdc` | — | Crew character asset face_expressions.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/sleeping-forest/renders/fp_view.png` | png | 89.6 KB | `58214755099e64556722846c22692545` | — | Crew character asset fp_view.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/sleeping-forest/renders/front.png` | png | 143.8 KB | `e232bb29e83ec45d54c95a2ee431672e` | — | Crew character asset front.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/sleeping-forest/renders/keyart.png` | png | 611.6 KB | `1c9bbc17ccea8b5380536e996d9bf00e` | — | Crew character asset keyart.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/sleeping-forest/renders/lod1_34.png` | png | 156.0 KB | `1f8f6274e34a14604cd6dac278f2ca6d` | — | Crew character asset lod1_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/sleeping-forest/renders/lod2_34.png` | png | 137.3 KB | `54bcdc889ea1299bb252848ac164de9b` | — | Crew character asset lod2_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/sleeping-forest/renders/rigtest_front.png` | png | 454.6 KB | `f32168cf0e8ac3ae7af75174ba4a12a8` | — | Crew character asset rigtest_front.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/sleeping-forest/renders/rigtest_side.png` | png | 433.9 KB | `2057367a6368cfccc6d208822255888b` | — | Crew character asset rigtest_side.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/sleeping-forest/renders/side.png` | png | 96.9 KB | `0409b6de6d2fdf4d2a93a19e47db1a9f` | — | Crew character asset side.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/sleeping-forest/renders/sil_34.png` | png | 11.3 KB | `8d9c52f168addcc2175803bf94e8fa3d` | — | Crew character asset sil_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/sleeping-forest/renders/sil_back.png` | png | 11.9 KB | `a68e72ae47829a2e25ac4e6d7eaf3fe2` | — | Crew character asset sil_back.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/sleeping-forest/renders/turnaround.png` | png | 540.1 KB | `670d490f3d6994b6cb0e04afe0800db4` | — | Crew character asset turnaround.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/sleeping-forest/renders/vr_34.png` | png | 158.5 KB | `f76f67deb1aaacf280bd2a12059237dc` | — | Crew character asset vr_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/sleeping-forest/sleeping-forest-fp.glb` | glb | 606.3 KB | `89c4760642d0782ef97af5f9da519ea6` | tris=2956; joints=7; meshes=SleepingForest_FP_body,SleepingForest_FP_glow | Crew character asset sleeping-forest-fp.glb | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/sleeping-forest/sleeping-forest-rider.glb` | glb | 2.53 MB | `e108e0b79fd20143cbac79a892d34db0` | tris=24684; joints=19; LODs=SleepingForest_LOD0_accessory,SleepingForest_LOD0_body,SleepingForest_LOD0_glow,SleepingForest_LOD0_hair,SleepingForest_LOD0_skates,SleepingForest_LOD0_top | Crew character asset sleeping-forest-rider.glb | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/sleeping-forest/sleeping-forest-rider.quest.glb` | glb | 958.0 KB | `1780a8d89812d3cec8b29e4eb40dbbe4` | tris=24648; joints=19; LODs=SleepingForest_LOD0_accessory,SleepingForest_LOD0_body,SleepingForest_LOD0_glow,SleepingForest_LOD0_hair,SleepingForest_LOD0_skates,SleepingForest_LOD0_top | Crew character asset sleeping-forest-rider.quest.glb | riders.js SR_CREW_GLB | staged |
| `skyrydahs-characters/sleeping-forest/sleeping-forest-rider.quest2-ktx2.glb` | glb | 852.9 KB | `5dcf2f9e15e089cf13c602c46b1743a0` | tris=24648; joints=19; LODs=SleepingForest_LOD0_accessory,SleepingForest_LOD0_body,SleepingForest_LOD0_glow,SleepingForest_LOD0_hair,SleepingForest_LOD0_skates,SleepingForest_LOD0_top | Crew character asset sleeping-forest-rider.quest2-ktx2.glb | riders.js SR_CREW_GLB | staged |
| `skyrydahs-characters/sleeping-forest/sleeping-forest-rider.s4-ktx2.glb` | glb | 842.4 KB | `4e2798ef06618a02da87eb270e1d161b` | tris=24648; joints=19; LODs=SleepingForest_LOD0_accessory,SleepingForest_LOD0_body,SleepingForest_LOD0_glow,SleepingForest_LOD0_hair,SleepingForest_LOD0_skates,SleepingForest_LOD0_top | Crew character asset sleeping-forest-rider.s4-ktx2.glb | riders.js SR_CREW_GLB | staged |
| `skyrydahs-characters/sleeping-forest/sleeping-forest-rider.s4.glb` | glb | 966.9 KB | `cf2ff0a06c88686a53cf52431c0b648d` | tris=24648; joints=19; LODs=SleepingForest_LOD0_accessory,SleepingForest_LOD0_body,SleepingForest_LOD0_glow,SleepingForest_LOD0_hair,SleepingForest_LOD0_skates,SleepingForest_LOD0_top | Crew character asset sleeping-forest-rider.s4.glb | riders.js SR_CREW_GLB | staged |
| `skyrydahs-characters/sleeping-forest/src/atlas.png` | png | 21.9 KB | `1e93158fc72a9a9163e96f38ee5c766e` | — | Crew character asset atlas.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/sleeping-forest/src/build_report.json` | json | 658 B | `584d8bdf16adc7888275e8fca1da01e8` | — | Crew character asset build_report.json | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/sleeping-forest/src/build_rider.py` | py | 12.0 KB | `4cd4dc444206d3421857f602e7208117` | — | Crew character asset build_rider.py | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/sleeping-forest/src/normal_bake.png` | png | 369.9 KB | `da01cba130850b56379b3fe929a4e736` | — | Crew character asset normal_bake.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/sleeping-forest/src/sleeping-forest-rider.blend` | blend | 5.17 MB | `d1280a3df36493a43b7b53e868083caa` | — | Crew character asset sleeping-forest-rider.blend | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/sleeping-forest/test.html` | html | 4.6 KB | `ac5916337104c48c45e370a8862d4e7f` | — | Crew character asset test.html | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/static-angels/loader.js` | js | 1.3 KB | `61359af86e0af66761a7d2dcf274795a` | — | Crew character asset loader.js | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/static-angels/renders/34.png` | png | 124.3 KB | `f9a935efe433aeefc1fcdb0abb937cec` | — | Crew character asset 34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/static-angels/renders/back.png` | png | 129.7 KB | `f1513fa225179f277ceba27e2ebf7235` | — | Crew character asset back.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/static-angels/renders/face_34.png` | png | 135.4 KB | `df2446c7502f160c5704c121025c8031` | — | Crew character asset face_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/static-angels/renders/face_closeup.png` | png | 149.5 KB | `8e2d84adf7eed8fc97094c033f3315b3` | — | Crew character asset face_closeup.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/static-angels/renders/face_expressions.png` | png | 250.2 KB | `3b7792ce15c561aefb80bc325ffaa67f` | — | Crew character asset face_expressions.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/static-angels/renders/fp_view.png` | png | 79.5 KB | `e02f3df079b422bb6241f4b6434db0ae` | — | Crew character asset fp_view.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/static-angels/renders/front.png` | png | 126.6 KB | `7429d9281f804cc3f5190d9ee210bda5` | — | Crew character asset front.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/static-angels/renders/keyart.png` | png | 654.9 KB | `c3f32e7c28173e2d8c58752f4d570a05` | — | Crew character asset keyart.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/static-angels/renders/lod1_34.png` | png | 121.3 KB | `3a0d9755701eecef9a960fb74323d478` | — | Crew character asset lod1_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/static-angels/renders/lod2_34.png` | png | 109.7 KB | `7bcf01c731aa9d26c3b2e8623d10e1ab` | — | Crew character asset lod2_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/static-angels/renders/rigtest_front.png` | png | 468.0 KB | `a239652aab94a700beccf6708565d68e` | — | Crew character asset rigtest_front.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/static-angels/renders/rigtest_side.png` | png | 433.0 KB | `42bbbbee761774e0324afdd843c456cb` | — | Crew character asset rigtest_side.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/static-angels/renders/side.png` | png | 71.6 KB | `e2d1740a36f89b0b5da8b1e6d48b26db` | — | Crew character asset side.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/static-angels/renders/sil_34.png` | png | 14.2 KB | `7acf62b846c84fd214fb56802ba15ec3` | — | Crew character asset sil_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/static-angels/renders/sil_back.png` | png | 16.4 KB | `7fe12e924bd1ece0c9d1d2092d34ddec` | — | Crew character asset sil_back.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/static-angels/renders/turnaround.png` | png | 447.4 KB | `72d441a8ba2d252ab331dc36b1b6a1e0` | — | Crew character asset turnaround.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/static-angels/renders/vr_34.png` | png | 163.8 KB | `9e4fe5f3a85a190336c770935f2ae659` | — | Crew character asset vr_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/static-angels/src/atlas.png` | png | 21.9 KB | `1e93158fc72a9a9163e96f38ee5c766e` | — | Crew character asset atlas.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/static-angels/src/build_report.json` | json | 630 B | `060395824e29dae522130fbd6ee5d76f` | — | Crew character asset build_report.json | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/static-angels/src/build_rider.py` | py | 8.7 KB | `cb1c45dffef59b7621503c610678a9c1` | — | Crew character asset build_rider.py | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/static-angels/src/normal_bake.png` | png | 371.7 KB | `02a7383ebd3c0a3161440e0e90ea1c62` | — | Crew character asset normal_bake.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/static-angels/src/shoot.sh` | sh | 187 B | `554af5bd834aeeca64e09f02a46587b5` | — | Crew character asset shoot.sh | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/static-angels/src/static-angels-rider.blend` | blend | 5.38 MB | `972617ad74bc14f65a16de41f8555af9` | — | Crew character asset static-angels-rider.blend | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/static-angels/static-angels-fp.glb` | glb | 609.5 KB | `84b3c72af739afad8ca30b172b99d699` | tris=2956; joints=7; meshes=StaticAngels_FP_body,StaticAngels_FP_glow | Crew character asset static-angels-fp.glb | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/static-angels/static-angels-rider.glb` | glb | 2.65 MB | `f0cf9a76575dea3b04190857b00710c3` | tris=26202; joints=19; LODs=StaticAngels_LOD0_accessory,StaticAngels_LOD0_body,StaticAngels_LOD0_glow,StaticAngels_LOD0_hair,StaticAngels_LOD0_skates,StaticAngels_LOD0_top | Crew character asset static-angels-rider.glb | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/static-angels/static-angels-rider.quest.glb` | glb | 992.7 KB | `c161003dd8536a4a988f9b5baadd1a90` | tris=26038; joints=19; LODs=StaticAngels_LOD0_accessory,StaticAngels_LOD0_body,StaticAngels_LOD0_glow,StaticAngels_LOD0_hair,StaticAngels_LOD0_skates,StaticAngels_LOD0_top | Crew character asset static-angels-rider.quest.glb | riders.js SR_CREW_GLB | staged |
| `skyrydahs-characters/static-angels/static-angels-rider.quest2-ktx2.glb` | glb | 884.2 KB | `a08aa1ef68293f9e1bc104fc280ccffd` | tris=26010; joints=19; LODs=StaticAngels_LOD0_accessory,StaticAngels_LOD0_body,StaticAngels_LOD0_glow,StaticAngels_LOD0_hair,StaticAngels_LOD0_skates,StaticAngels_LOD0_top | Crew character asset static-angels-rider.quest2-ktx2.glb | riders.js SR_CREW_GLB | staged |
| `skyrydahs-characters/static-angels/static-angels-rider.s4-ktx2.glb` | glb | 867.5 KB | `d3e5c07c905ef502cf322ac509a63f58` | tris=26038; joints=19; LODs=StaticAngels_LOD0_accessory,StaticAngels_LOD0_body,StaticAngels_LOD0_glow,StaticAngels_LOD0_hair,StaticAngels_LOD0_skates,StaticAngels_LOD0_top | Crew character asset static-angels-rider.s4-ktx2.glb | riders.js SR_CREW_GLB | staged |
| `skyrydahs-characters/static-angels/static-angels-rider.s4.glb` | glb | 995.2 KB | `6c22617843d95ab2ef7e3710e6a9a673` | tris=26038; joints=19; LODs=StaticAngels_LOD0_accessory,StaticAngels_LOD0_body,StaticAngels_LOD0_glow,StaticAngels_LOD0_hair,StaticAngels_LOD0_skates,StaticAngels_LOD0_top | Crew character asset static-angels-rider.s4.glb | riders.js SR_CREW_GLB | staged |
| `skyrydahs-characters/static-angels/test.html` | html | 4.6 KB | `39d9b392f0dad56a7e2a9fa449a69b2d` | — | Crew character asset test.html | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/tool-toul-to/loader.js` | js | 1.3 KB | `bfbc74aa168e4b507ac1cfd8fb57be78` | — | Crew character asset loader.js | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/tool-toul-to/renders/34.png` | png | 158.2 KB | `b69de4f14a26d4fb6ab495c1d1beba64` | — | Crew character asset 34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/tool-toul-to/renders/back.png` | png | 149.1 KB | `c7fcfc01dd88515ade6aca8ccdeb5481` | — | Crew character asset back.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/tool-toul-to/renders/face_closeup.png` | png | 242.9 KB | `5d7e91421bb37fa544a0b4664d74b8d7` | — | Crew character asset face_closeup.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/tool-toul-to/renders/face_expressions.png` | png | 359.6 KB | `eeda2b37c89df0c42f6a37b325577640` | — | Crew character asset face_expressions.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/tool-toul-to/renders/fp_view.png` | png | 76.4 KB | `aae2c7e49410371af9421460abb7a4ea` | — | Crew character asset fp_view.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/tool-toul-to/renders/front.png` | png | 149.9 KB | `de1725eae41e79338db6af2dae09efd0` | — | Crew character asset front.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/tool-toul-to/renders/keyart.png` | png | 604.3 KB | `62ae098a4f1b03b90bc1f845110b1119` | — | Crew character asset keyart.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/tool-toul-to/renders/lod1_34.png` | png | 160.4 KB | `33d8baf26f50231dc4103c8b1a2462a5` | — | Crew character asset lod1_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/tool-toul-to/renders/lod2_34.png` | png | 120.1 KB | `f2cde98612ff929c21123a216ac51639` | — | Crew character asset lod2_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/tool-toul-to/renders/rigtest_front.png` | png | 482.0 KB | `e83da55d6043aee1780ef7af2081a294` | — | Crew character asset rigtest_front.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/tool-toul-to/renders/rigtest_side.png` | png | 454.2 KB | `0bd5726b7d094562e9b7f4bea7a4f9ac` | — | Crew character asset rigtest_side.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/tool-toul-to/renders/side.png` | png | 111.5 KB | `0b78e9739064e4fd175c897e8f4e1ceb` | — | Crew character asset side.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/tool-toul-to/renders/sil_34.png` | png | 11.9 KB | `8fc5efdb0e2fcd81f714523f89baae8e` | — | Crew character asset sil_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/tool-toul-to/renders/sil_back.png` | png | 12.0 KB | `30050241f873eed3070235a50dd9ce83` | — | Crew character asset sil_back.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/tool-toul-to/renders/turnaround.png` | png | 573.7 KB | `4784298db21fb53aa34f083cca2db892` | — | Crew character asset turnaround.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/tool-toul-to/renders/vr_34.png` | png | 178.2 KB | `3912de34df30530100ac581fce43d846` | — | Crew character asset vr_34.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/tool-toul-to/src/atlas.png` | png | 21.9 KB | `1e93158fc72a9a9163e96f38ee5c766e` | — | Crew character asset atlas.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/tool-toul-to/src/build_report.json` | json | 666 B | `9e3e045d89e64bc3ea9829ab6d9938ec` | — | Crew character asset build_report.json | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/tool-toul-to/src/build_rider.py` | py | 13.2 KB | `48d6a3ef04ef1c420c833557ca6cd46c` | — | Crew character asset build_rider.py | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/tool-toul-to/src/normal_bake.png` | png | 362.5 KB | `fcb4f172391a3298175cb29869ae7415` | — | Crew character asset normal_bake.png | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/tool-toul-to/src/tool-toul-to-rider.blend` | blend | 5.20 MB | `6748c591f4243e68108988509d9e972d` | — | Crew character asset tool-toul-to-rider.blend | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/tool-toul-to/test.html` | html | 4.6 KB | `92f59beda154883f3e24ae58590d0273` | — | Crew character asset test.html | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/tool-toul-to/tool-toul-to-fp.glb` | glb | 598.3 KB | `6c1a38e4730c1495a104cfd8c0f4e10c` | tris=2956; joints=7; meshes=ToolToulTo_FP_body,ToolToulTo_FP_glow | Crew character asset tool-toul-to-fp.glb | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/tool-toul-to/tool-toul-to-rider.glb` | glb | 2.68 MB | `5e5c55ded0d64e9789e7228d3063e213` | tris=25323; joints=19; LODs=ToolToulTo_LOD0_accessory,ToolToulTo_LOD0_body,ToolToulTo_LOD0_glow,ToolToulTo_LOD0_hair,ToolToulTo_LOD0_skates,ToolToulTo_LOD0_top | Crew character asset tool-toul-to-rider.glb | riders.js SR_CREW_GLB | live |
| `skyrydahs-characters/tool-toul-to/tool-toul-to-rider.quest.glb` | glb | 951.4 KB | `82b7777e0f65a757b24ab572c838f909` | tris=25143; joints=19; LODs=ToolToulTo_LOD0_accessory,ToolToulTo_LOD0_body,ToolToulTo_LOD0_glow,ToolToulTo_LOD0_hair,ToolToulTo_LOD0_skates,ToolToulTo_LOD0_top | Crew character asset tool-toul-to-rider.quest.glb | riders.js SR_CREW_GLB | staged |
| `skyrydahs-characters/tool-toul-to/tool-toul-to-rider.quest2-ktx2.glb` | glb | 850.2 KB | `5aab51e6acef502605abb86b64f047f6` | tris=25143; joints=19; LODs=ToolToulTo_LOD0_accessory,ToolToulTo_LOD0_body,ToolToulTo_LOD0_glow,ToolToulTo_LOD0_hair,ToolToulTo_LOD0_skates,ToolToulTo_LOD0_top | Crew character asset tool-toul-to-rider.quest2-ktx2.glb | riders.js SR_CREW_GLB | staged |
| `skyrydahs-characters/tool-toul-to/tool-toul-to-rider.s4-ktx2.glb` | glb | 838.7 KB | `f64ff371837a1e34bca82d099a6058e1` | tris=25143; joints=19; LODs=ToolToulTo_LOD0_accessory,ToolToulTo_LOD0_body,ToolToulTo_LOD0_glow,ToolToulTo_LOD0_hair,ToolToulTo_LOD0_skates,ToolToulTo_LOD0_top | Crew character asset tool-toul-to-rider.s4-ktx2.glb | riders.js SR_CREW_GLB | staged |
| `skyrydahs-characters/tool-toul-to/tool-toul-to-rider.s4.glb` | glb | 958.6 KB | `26b7221c73adb166aa486b60504faaa2` | tris=25143; joints=19; LODs=ToolToulTo_LOD0_accessory,ToolToulTo_LOD0_body,ToolToulTo_LOD0_glow,ToolToulTo_LOD0_hair,ToolToulTo_LOD0_skates,ToolToulTo_LOD0_top | Crew character asset tool-toul-to-rider.s4.glb | riders.js SR_CREW_GLB | staged |
| `skyrydahs-characters/wardrobe/accessory/gold_pants_chains.glb` | glb | 127.7 KB | `6fb07a9cd75f0c932974e67a8e935ef8` | tris=768; joints=70; LODs=gold_pants_chains_LOD0,gold_pants_chains_LOD1,gold_pants_chains_LOD2 | Wardrobe asset gold_pants_chains.glb | wardrobe.js equip() / jackets.js | live |
| `skyrydahs-characters/wardrobe/accessory/gold_pants_chains.quest-ktx2.glb` | glb | 30.4 KB | `3c3b1c4773f8b197fd37bff0b3339204` | tris=768; joints=70; LODs=gold_pants_chains_LOD0,gold_pants_chains_LOD1,gold_pants_chains_LOD2 | Wardrobe asset gold_pants_chains.quest-ktx2.glb | wardrobe.js equip() / jackets.js | staged |
| `skyrydahs-characters/wardrobe/accessory/gold_pants_chains.quest.glb` | glb | 29.9 KB | `305474a7ce3ff08476820729183c8bb4` | tris=768; joints=70; LODs=gold_pants_chains_LOD0,gold_pants_chains_LOD1,gold_pants_chains_LOD2 | Wardrobe asset gold_pants_chains.quest.glb | wardrobe.js equip() / jackets.js | staged |
| `skyrydahs-characters/wardrobe/body/base-v1.glb` | glb | 966.7 KB | `7e81d46e15faf46b3b8683e8c14378c0` | tris=8500; joints=66; LODs=body_base_LOD0,body_base_LOD1,body_base_LOD2 | Wardrobe asset base-v1.glb | wardrobe.js equip() / jackets.js | live |
| `skyrydahs-characters/wardrobe/body/base.glb` | glb | 1.13 MB | `de2ffed5070302dc744e64519e1ed6d5` | tris=11369; joints=70; LODs=body_base_LOD0,body_base_LOD1,body_base_LOD2 | Wardrobe asset base.glb | wardrobe.js equip() / jackets.js | live |
| `skyrydahs-characters/wardrobe/body/base.quest-ktx2.glb` | glb | 530.1 KB | `4b111fdc8376539c78abbc2122f2b72f` | tris=11369; joints=70; LODs=body_base_LOD0,body_base_LOD1,body_base_LOD2 | Wardrobe asset base.quest-ktx2.glb | wardrobe.js equip() / jackets.js | staged |
| `skyrydahs-characters/wardrobe/body/base.quest.glb` | glb | 291.0 KB | `9a9f17f6bba8385c30cdd744ec97d675` | tris=11369; joints=70; LODs=body_base_LOD0,body_base_LOD1,body_base_LOD2 | Wardrobe asset base.quest.glb | wardrobe.js equip() / jackets.js | staged |
| `skyrydahs-characters/wardrobe/body/base_mask_rigged_verts.npy` | npy | 165.6 KB | `10d233ff5ac9a1d175e305ddbf0ad204` | — | Wardrobe asset base_mask_rigged_verts.npy | wardrobe.js equip() / jackets.js | live |
| `skyrydahs-characters/wardrobe/gloves/caali_fingerless.glb` | glb | 759.6 KB | `63ddc3851759e5ff0e7688c221643176` | tris=11300; joints=70; LODs=caali_fingerless_LOD0,caali_fingerless_LOD1,caali_fingerless_LOD2 | Wardrobe asset caali_fingerless.glb | wardrobe.js equip() / jackets.js | live |
| `skyrydahs-characters/wardrobe/gloves/caali_fingerless.quest-ktx2.glb` | glb | 434.9 KB | `df901cd16381a4581987f501f443fd85` | tris=11300; joints=70; LODs=caali_fingerless_LOD0,caali_fingerless_LOD1,caali_fingerless_LOD2 | Wardrobe asset caali_fingerless.quest-ktx2.glb | wardrobe.js equip() / jackets.js | staged |
| `skyrydahs-characters/wardrobe/gloves/caali_fingerless.quest.glb` | glb | 203.1 KB | `44ba1934a7c6621929215414befb0224` | tris=11300; joints=70; LODs=caali_fingerless_LOD0,caali_fingerless_LOD1,caali_fingerless_LOD2 | Wardrobe asset caali_fingerless.quest.glb | wardrobe.js equip() / jackets.js | staged |
| `skyrydahs-characters/wardrobe/hair/caali_curly_short.glb` | glb | 1.29 MB | `03bf10a2b2d9f43018d640ac0ce3c40f` | tris=19200; joints=70; LODs=caali_curly_short_LOD0,caali_curly_short_LOD1,caali_curly_short_LOD2 | Wardrobe asset caali_curly_short.glb | wardrobe.js equip() / jackets.js | live |
| `skyrydahs-characters/wardrobe/hair/caali_curly_short.quest-ktx2.glb` | glb | 565.8 KB | `7483e8c39a96736e832dd3522acc636b` | tris=19200; joints=70; LODs=caali_curly_short_LOD0,caali_curly_short_LOD1,caali_curly_short_LOD2 | Wardrobe asset caali_curly_short.quest-ktx2.glb | wardrobe.js equip() / jackets.js | staged |
| `skyrydahs-characters/wardrobe/hair/caali_curly_short.quest.glb` | glb | 282.5 KB | `0e60bb246fdd4a110c98bbcc3896105b` | tris=19200; joints=70; LODs=caali_curly_short_LOD0,caali_curly_short_LOD1,caali_curly_short_LOD2 | Wardrobe asset caali_curly_short.quest.glb | wardrobe.js equip() / jackets.js | staged |
| `skyrydahs-characters/wardrobe/head/caali_head.glb` | glb | 1.03 MB | `c5a00e300413aece5185922dafd839fb` | tris=23996; joints=70; LODs=caali_head_LOD0,caali_head_LOD1,caali_head_LOD2 | Wardrobe asset caali_head.glb | wardrobe.js equip() / jackets.js | live |
| `skyrydahs-characters/wardrobe/head/caali_head.quest-ktx2.glb` | glb | 413.3 KB | `0a1d8095e0fdd53c1820e3c3f2588b8e` | tris=23996; joints=70; LODs=caali_head_LOD0,caali_head_LOD1,caali_head_LOD2 | Wardrobe asset caali_head.quest-ktx2.glb | wardrobe.js equip() / jackets.js | staged |
| `skyrydahs-characters/wardrobe/head/caali_head.quest.glb` | glb | 228.8 KB | `46051726591e7bd0056c82d6d154d04b` | tris=23996; joints=70; LODs=caali_head_LOD0,caali_head_LOD1,caali_head_LOD2 | Wardrobe asset caali_head.quest.glb | wardrobe.js equip() / jackets.js | staged |
| `skyrydahs-characters/wardrobe/jacket/caali_bomber.glb` | glb | 2.00 MB | `623f19f9ca3522f6fc017a2a509cec39` | tris=23999; joints=70; LODs=caali_bomber_LOD0,caali_bomber_LOD1,caali_bomber_LOD2 | Wardrobe asset caali_bomber.glb | wardrobe.js equip() / jackets.js | live |
| `skyrydahs-characters/wardrobe/jacket/caali_bomber.quest-ktx2.glb` | glb | 1.23 MB | `9347e430ac15be1560278d0c38c9c87f` | tris=23999; joints=70; LODs=caali_bomber_LOD0,caali_bomber_LOD1,caali_bomber_LOD2 | Wardrobe asset caali_bomber.quest-ktx2.glb | wardrobe.js equip() / jackets.js | staged |
| `skyrydahs-characters/wardrobe/jacket/caali_bomber.quest.glb` | glb | 922.9 KB | `a7ba2a12d40bdca706f3e03171714067` | tris=23999; joints=70; LODs=caali_bomber_LOD0,caali_bomber_LOD1,caali_bomber_LOD2 | Wardrobe asset caali_bomber.quest.glb | wardrobe.js equip() / jackets.js | staged |
| `skyrydahs-characters/wardrobe/neck/gold_chain_thick.glb` | glb | 635.7 KB | `84618d43586e9e1adb6dd1ae753d3a06` | tris=5560; joints=70; LODs=gold_chain_thick_LOD0,gold_chain_thick_LOD1,gold_chain_thick_LOD2 | Wardrobe asset gold_chain_thick.glb | wardrobe.js equip() / jackets.js | live |
| `skyrydahs-characters/wardrobe/neck/gold_chain_thick.quest-ktx2.glb` | glb | 962.4 KB | `ce9c8eff6c7057573fd825d311d933eb` | tris=5560; joints=70; LODs=gold_chain_thick_LOD0,gold_chain_thick_LOD1,gold_chain_thick_LOD2 | Wardrobe asset gold_chain_thick.quest-ktx2.glb | wardrobe.js equip() / jackets.js | staged |
| `skyrydahs-characters/wardrobe/neck/gold_chain_thick.quest.glb` | glb | 268.1 KB | `bc014c05562b7624244ae1deebe31ca5` | tris=5560; joints=70; LODs=gold_chain_thick_LOD0,gold_chain_thick_LOD1,gold_chain_thick_LOD2 | Wardrobe asset gold_chain_thick.quest.glb | wardrobe.js equip() / jackets.js | staged |
| `skyrydahs-characters/wardrobe/pants/caali_cargo.glb` | glb | 1.57 MB | `c29db25003f4bf91b8a6ef275f16bf5c` | tris=23999; joints=70; LODs=caali_cargo_LOD0,caali_cargo_LOD1,caali_cargo_LOD2 | Wardrobe asset caali_cargo.glb | wardrobe.js equip() / jackets.js | live |
| `skyrydahs-characters/wardrobe/pants/caali_cargo.quest-ktx2.glb` | glb | 891.6 KB | `9f97705c7a1fa6040c820074abbbfb98` | tris=23999; joints=70; LODs=caali_cargo_LOD0,caali_cargo_LOD1,caali_cargo_LOD2 | Wardrobe asset caali_cargo.quest-ktx2.glb | wardrobe.js equip() / jackets.js | staged |
| `skyrydahs-characters/wardrobe/pants/caali_cargo.quest.glb` | glb | 540.8 KB | `3dc9b18ebc4e17206b1e621353d45b13` | tris=23999; joints=70; LODs=caali_cargo_LOD0,caali_cargo_LOD1,caali_cargo_LOD2 | Wardrobe asset caali_cargo.quest.glb | wardrobe.js equip() / jackets.js | staged |
| `skyrydahs-characters/wardrobe/riders/caali-g-4k.glb` | glb | 15.22 MB | `b360b97133909bce82e2a4ebb2ede8f6` | tris=140361; joints=66; LODs=CaaliG_LOD0,CaaliG_LOD1,CaaliG_LOD2 | caali-g-4k.glb | — | live |
| `skyrydahs-characters/wardrobe/riders/caali-g-flatnormals.glb` | glb | 15.22 MB | `b360b97133909bce82e2a4ebb2ede8f6` | tris=140361; joints=66; LODs=CaaliG_LOD0,CaaliG_LOD1,CaaliG_LOD2 | caali-g-flatnormals.glb | — | live |
| `skyrydahs-characters/wardrobe/riders/caali-g-hd-raw.glb` | glb | 29.36 MB | `6f10426041a99a879dd10221bf0444c1` | tris=342793; joints=70; LODs=CaaliG_LOD0,CaaliG_LOD1,CaaliG_LOD2 | caali-g-hd-raw.glb | — | live |
| `skyrydahs-characters/wardrobe/riders/caali-g-hd.glb` | glb | 4.26 MB | `cabe06217f4c295cd4957129989e71cc` | tris=294416; joints=91; LODs=CaaliG_LOD0,CaaliG_LOD1,CaaliG_LOD2 | Caali G HD | wardrobe.js ?tier=hd | live |
| `skyrydahs-characters/wardrobe/riders/caali-g-hd.ktx2.glb` | glb | 4.03 MB | `81537d9636ea500c022cabe2b88a6581` | tris=294416; joints=91; LODs=CaaliG_LOD0,CaaliG_LOD1,CaaliG_LOD2 | caali-g-hd.ktx2.glb | — | live |
| `skyrydahs-characters/wardrobe/riders/caali-g-hd.ktx2.v1-20261030-0848.glb` | glb | 7.07 MB | `714772ab6267975795a084a8e3875a66` | tris=342793; joints=70; LODs=CaaliG_LOD0,CaaliG_LOD1,CaaliG_LOD2 | caali-g-hd.ktx2.v1-20261030-0848.glb | — | live |
| `skyrydahs-characters/wardrobe/riders/caali-g-raw.glb` | glb | 15.34 MB | `dc33dbe0402b76a5584e7f7be30044b1` | tris=144229; joints=70; LODs=CaaliG_LOD0,CaaliG_LOD1,CaaliG_LOD2 | caali-g-raw.glb | — | live |
| `skyrydahs-characters/wardrobe/riders/caali-g-v1.glb` | glb | 5.47 MB | `0521eab270713dab169385460cc6592a` | tris=31809; joints=66; LODs=CaaliG_LOD0,CaaliG_LOD1,CaaliG_LOD2 | caali-g-v1.glb | — | live |
| `skyrydahs-characters/wardrobe/riders/caali-g-v2-hd-raw.flat.glb` | glb | 22.05 MB | `b733113a55b42ecf0d6b708bff36396e` | tris=302812; LODs=CaaliG_LOD0.001,CaaliG_LOD1,CaaliG_LOD2 | caali-g-v2-hd-raw.flat.glb | — | live |
| `skyrydahs-characters/wardrobe/riders/caali-g-v2-hd-raw.glb` | glb | 22.05 MB | `b733113a55b42ecf0d6b708bff36396e` | tris=302812; LODs=CaaliG_LOD0.001,CaaliG_LOD1,CaaliG_LOD2 | caali-g-v2-hd-raw.glb | — | live |
| `skyrydahs-characters/wardrobe/riders/caali-g-v2-hd.glb` | glb | 4.13 MB | `bbde1cf96bd5a2ce7c66cc8e38c4f9af` | tris=302812; LODs=CaaliG_LOD0,CaaliG_LOD1,CaaliG_LOD2 | caali-g-v2-hd.glb | — | live |
| `skyrydahs-characters/wardrobe/riders/caali-g-v2-hd.opt-ktx2.glb` | glb | 6.08 MB | `297a7455e354c4c7ac66a762240c173d` | tris=294416; joints=91; LODs=CaaliG_LOD0,CaaliG_LOD1,CaaliG_LOD2 | caali-g-v2-hd.opt-ktx2.glb | — | live |
| `skyrydahs-characters/wardrobe/riders/caali-g-v2-hd.rigged.glb` | glb | 25.66 MB | `b1bb58935213187b02ba1b0e7e70a7ad` | tris=294416; joints=91; LODs=CaaliG_LOD0,CaaliG_LOD1,CaaliG_LOD2 | caali-g-v2-hd.rigged.glb | — | live |
| `skyrydahs-characters/wardrobe/riders/caali-g-v2-raw.flat.glb` | glb | 12.57 MB | `d0384bff31f1c9100d0d546342bc1559` | tris=156811; LODs=CaaliG_LOD0,CaaliG_LOD1,CaaliG_LOD2 | caali-g-v2-raw.flat.glb | — | live |
| `skyrydahs-characters/wardrobe/riders/caali-g-v2-raw.glb` | glb | 12.57 MB | `d0384bff31f1c9100d0d546342bc1559` | tris=156811; LODs=CaaliG_LOD0,CaaliG_LOD1,CaaliG_LOD2 | caali-g-v2-raw.glb | — | live |
| `skyrydahs-characters/wardrobe/riders/caali-g-v2.glb` | glb | 2.24 MB | `05d799b03bc09ee9dee0ea5da4bc3672` | tris=156811; LODs=CaaliG_LOD0,CaaliG_LOD1,CaaliG_LOD2 | caali-g-v2.glb | — | live |
| `skyrydahs-characters/wardrobe/riders/caali-g-v2.opt-ktx2.glb` | glb | 2.57 MB | `9e73946dbc0c27372ac57f25d6d7ca77` | tris=148308; joints=91; LODs=CaaliG_LOD0,CaaliG_LOD1,CaaliG_LOD2 | caali-g-v2.opt-ktx2.glb | — | live |
| `skyrydahs-characters/wardrobe/riders/caali-g-v2.quest-ktx2.glb` | glb | 2.98 MB | `643b583d0aefe932d11a32676e7554cd` | tris=156764; LODs=CaaliG_LOD0,CaaliG_LOD1,CaaliG_LOD2 | caali-g-v2.quest-ktx2.glb | — | live |
| `skyrydahs-characters/wardrobe/riders/caali-g-v2.quest-ktx2.rigged.glb` | glb | 15.94 MB | `e63a57846a4fca151427337527577479` | tris=148308; joints=91; LODs=CaaliG_LOD0,CaaliG_LOD1,CaaliG_LOD2 | caali-g-v2.quest-ktx2.rigged.glb | — | live |
| `skyrydahs-characters/wardrobe/riders/caali-g-v2.quest.glb` | glb | 2.26 MB | `8215eaace6fc090dcbfb6a6d83906337` | tris=156764; LODs=CaaliG_LOD0,CaaliG_LOD1,CaaliG_LOD2 | caali-g-v2.quest.glb | — | live |
| `skyrydahs-characters/wardrobe/riders/caali-g-v2.quest.rigged.glb` | glb | 15.22 MB | `9e54f407a05295ade5d7f70a6ea38d47` | tris=148308; joints=91; LODs=CaaliG_LOD0,CaaliG_LOD1,CaaliG_LOD2 | caali-g-v2.quest.rigged.glb | — | live |
| `skyrydahs-characters/wardrobe/riders/caali-g-v2.rig-report.json` | json | 16.3 KB | `e47bd05a49b6b693f26e34d040920d2c` | — | caali-g-v2.rig-report.json | — | live |
| `skyrydahs-characters/wardrobe/riders/caali-g-v2.rigged.glb` | glb | 14.15 MB | `b92e238373f9e1aecd0eaa297f5317b2` | tris=148308; joints=91; LODs=CaaliG_LOD0,CaaliG_LOD1,CaaliG_LOD2 | caali-g-v2.rigged.glb | — | live |
| `skyrydahs-characters/wardrobe/riders/caali-g.glb` | glb | 14.15 MB | `b92e238373f9e1aecd0eaa297f5317b2` | tris=148308; joints=91; LODs=CaaliG_LOD0,CaaliG_LOD1,CaaliG_LOD2 | Caali G body (?texfull=1) | wardrobe.js | live |
| `skyrydahs-characters/wardrobe/riders/caali-g.nonormal.glb` | glb | 2.32 MB | `450e571902552d5d90f327a353f58220` | tris=148308; joints=91; LODs=CaaliG_LOD0,CaaliG_LOD1,CaaliG_LOD2 | Caali G quest default body | wardrobe.js WARDROBE_RIDERS.caali | live |
| `skyrydahs-characters/wardrobe/riders/caali-g.nonormal.ktx2.glb` | glb | 2.09 MB | `7241506267351a37b371369bdc8946bb` | tris=148308; joints=91; LODs=CaaliG_LOD0,CaaliG_LOD1,CaaliG_LOD2 | caali-g.nonormal.ktx2.glb | — | live |
| `skyrydahs-characters/wardrobe/riders/caali-g.outfit.json` | json | 250 B | `d340d586582539de6d23d4594936f2cb` | — | caali-g.outfit.json | — | live |
| `skyrydahs-characters/wardrobe/riders/caali-g.quest-ktx2.glb` | glb | 1.65 MB | `f43ad3b3bc0ad267c99584bb880c5aff` | tris=144229; joints=70; LODs=CaaliG_LOD0,CaaliG_LOD1,CaaliG_LOD2 | caali-g.quest-ktx2.glb | — | live |
| `skyrydahs-characters/wardrobe/riders/caali-g.quest.glb` | glb | 1.50 MB | `b1cefed45f48e02e37c3052564df797e` | tris=144229; joints=70; LODs=CaaliG_LOD0,CaaliG_LOD1,CaaliG_LOD2 | caali-g.quest.glb | — | live |
| `skyrydahs-characters/wardrobe/skates/at-skate-meshy.glb` | glb | 321.3 KB | `0a44e2346fc4f2877142efe1d18e9ecf` | tris=3419; meshes=Mesh_0.013,Mesh_0.014,Mesh_0.015,Mesh_0.016 | Wardrobe asset at-skate-meshy.glb | wardrobe.js equip() / jackets.js | live |
| `skyrydahs-characters/wardrobe/skates/at-skate-meshy.merged.glb` | glb | 1.01 MB | `bd915dcac893bd5ba60e6942334b3053` | tris=6838; joints=2; LODs=ATSkate_LOD0,ATSkate_LOD1,ATSkate_LOD2 | Wardrobe asset at-skate-meshy.merged.glb | wardrobe.js equip() / jackets.js | live |
| `skyrydahs-characters/wardrobe/skates/at-skate-meshy.merged.quest.glb` | glb | 118.1 KB | `2e7e3b8cfac0918d3c002d578c716678` | tris=6838; joints=2; LODs=ATSkate_LOD0,ATSkate_LOD1,ATSkate_LOD2 | Wardrobe asset at-skate-meshy.merged.quest.glb | wardrobe.js equip() / jackets.js | staged |
| `skyrydahs-characters/wardrobe/skates/at-skate-meshy.merged.v2.glb` | glb | 176.9 KB | `e829857e30b2c6aa6d44ca7374a1409a` | tris=25534; joints=2; LODs=ATSkate_LOD0,ATSkate_LOD1,ATSkate_LOD2 | Merged L+R A-T skate v2 | jackets.js srSkateMerged | live |
| `skyrydahs-characters/wardrobe/skates/at-skate-meshy.v2.glb` | glb | 97.2 KB | `5de1f2f9681f1c5958d3666b133c324d` | tris=12767; LODs=ShellBlend_L0,Wheel_F_L0,Wheel_R_L0,ShellBlend_L1,Wheel_F_L1,Wheel_R_L1 | Shared A-T skate v2 module (+24.16mm baked) | jackets.js SR_SKATE | live |
| `skyrydahs-characters/wardrobe/skates/staging/at-skate-meshy.merged.v2.glb` | glb | 176.9 KB | `e829857e30b2c6aa6d44ca7374a1409a` | tris=25534; joints=2; LODs=ATSkate_LOD0,ATSkate_LOD1,ATSkate_LOD2 | Merged L+R A-T skate v2 | jackets.js srSkateMerged | live |
| `skyrydahs-characters/wardrobe/skates/staging/at-skate-meshy.v2.glb` | glb | 97.2 KB | `7c020dd3a7c4f29938567e9bbdd22f12` | tris=12767; LODs=ShellBlend_L0,Wheel_F_L0,Wheel_R_L0,ShellBlend_L1,Wheel_F_L1,Wheel_R_L1 | Shared A-T skate v2 module (+24.16mm baked) | jackets.js SR_SKATE | live |
| `skyrydahs-characters/wardrobe/slots.json` | json | 221 B | `7c96984531e06a2ff4b98c5d6c0df105` | — | slots.json | — | live |
| `skyrydahs-characters/wardrobe/top/caali_gr8yzone_tee.glb` | glb | 1.02 MB | `2be0cccd96ace2ecf11066eaede395f5` | tris=17200; joints=70; LODs=caali_gr8yzone_tee_LOD0,caali_gr8yzone_tee_LOD1,caali_gr8yzone_tee_LOD2 | Wardrobe asset caali_gr8yzone_tee.glb | wardrobe.js equip() / jackets.js | live |
| `skyrydahs-characters/wardrobe/top/caali_gr8yzone_tee.quest-ktx2.glb` | glb | 319.1 KB | `89366f121b1c5540a54e31c9cccbea30` | tris=17200; joints=70; LODs=caali_gr8yzone_tee_LOD0,caali_gr8yzone_tee_LOD1,caali_gr8yzone_tee_LOD2 | Wardrobe asset caali_gr8yzone_tee.quest-ktx2.glb | wardrobe.js equip() / jackets.js | staged |
| `skyrydahs-characters/wardrobe/top/caali_gr8yzone_tee.quest.glb` | glb | 258.9 KB | `f24524c837344cd25b4ae28e601437df` | tris=17200; joints=70; LODs=caali_gr8yzone_tee_LOD0,caali_gr8yzone_tee_LOD1,caali_gr8yzone_tee_LOD2 | Wardrobe asset caali_gr8yzone_tee.quest.glb | wardrobe.js equip() / jackets.js | staged |
| `skyrydahs-characters/wardrobe/top/gr8yzone_logo.png` | png | 90.4 KB | `46a9871806eb0ddb26d6a0b3ecf3e7aa` | — | Wardrobe asset gr8yzone_logo.png | wardrobe.js equip() / jackets.js | live |
| `skyrydahs-characters/wardrobe/v1_items/caali_bomber.glb` | glb | 537.3 KB | `35286f796b8ec2f0f0fe55b954340f86` | tris=5000; joints=66; LODs=caali_bomber_LOD0,caali_bomber_LOD1,caali_bomber_LOD2 | caali_bomber.glb | — | live |
| `skyrydahs-characters/wardrobe/v1_items/caali_cargo.glb` | glb | 400.5 KB | `9aafb3a99ffbb2977780eb95c4afaf26` | tris=3680; joints=66; LODs=caali_cargo_LOD0,caali_cargo_LOD1,caali_cargo_LOD2 | caali_cargo.glb | — | live |
| `skyrydahs-characters/wardrobe/v1_items/caali_curly_short.glb` | glb | 234.6 KB | `5f2142819fddd448d4ce970ed5cb96ae` | tris=2449; joints=66; LODs=caali_curly_short_LOD0,caali_curly_short_LOD1,caali_curly_short_LOD2 | caali_curly_short.glb | — | live |
| `skyrydahs-characters/wardrobe/v1_items/caali_fingerless.glb` | glb | 171.1 KB | `82344753eba749fb4ecdc9a5a01989d8` | tris=1198; joints=66; LODs=caali_fingerless_LOD0,caali_fingerless_LOD1,caali_fingerless_LOD2 | caali_fingerless.glb | — | live |
| `skyrydahs-characters/wardrobe/v1_items/caali_gr8yzone_tee.glb` | glb | 227.7 KB | `b816886e793ec606172718a68d4d155b` | tris=1802; joints=66; LODs=caali_gr8yzone_tee_LOD0,caali_gr8yzone_tee_LOD1,caali_gr8yzone_tee_LOD2 | caali_gr8yzone_tee.glb | — | live |
| `skyrydahs-characters/wardrobe/v1_items/gold_chain_thick.glb` | glb | 246.1 KB | `7bcbb037bb6aa20facb88552c19a1b71` | tris=1574; joints=66; LODs=gold_chain_thick_LOD0,gold_chain_thick_LOD1,gold_chain_thick_LOD2 | gold_chain_thick.glb | — | live |
| `skyrydahs-characters/wardrobe/v1_items/gold_pants_chains.glb` | glb | 126.6 KB | `da4cf29cdbf430fb9c0952402fd2adb5` | tris=768; joints=66; LODs=gold_pants_chains_LOD0,gold_pants_chains_LOD1,gold_pants_chains_LOD2 | gold_pants_chains.glb | — | live |
| `skyrydahs-characters/wardrobe_build/forge-caali-v2/caali_pieces.blend` | blend | 40.73 MB | `01204c67b0ebdfd558ef8c5eb60045e5` | — | Tool/source caali_pieces.blend | — | tool |
| `skyrydahs-characters/wardrobe_hd/accessory/gold_pants_chains.glb` | glb | 126.6 KB | `2a8a83a02234077c49a817da7ee0ccb8` | tris=768; joints=66; LODs=gold_pants_chains_LOD0,gold_pants_chains_LOD1,gold_pants_chains_LOD2 | gold_pants_chains.glb | — | live |
| `skyrydahs-characters/wardrobe_hd/body/base.glb` | glb | 819.7 KB | `0ab4b47a2920cb369d8178bf0573ed59` | tris=7499; joints=66; LODs=body_base_LOD0,body_base_LOD1,body_base_LOD2 | base.glb | — | live |
| `skyrydahs-characters/wardrobe_hd/body/base_mask_rigged_verts.npy` | npy | 165.6 KB | `6e63f0df465b573209b40d413a148a31` | — | base_mask_rigged_verts.npy | — | live |
| `skyrydahs-characters/wardrobe_hd/gloves/caali_fingerless.glb` | glb | 1.31 MB | `541fd8a63970984a03fca5eb1df88ba3` | tris=23300; joints=66; LODs=caali_fingerless_LOD0,caali_fingerless_LOD1,caali_fingerless_LOD2 | caali_fingerless.glb | — | live |
| `skyrydahs-characters/wardrobe_hd/hair/caali_curly_short.glb` | glb | 3.52 MB | `920f55a82693365c93cb112d2d04bae8` | tris=65200; joints=66; LODs=caali_curly_short_LOD0,caali_curly_short_LOD1,caali_curly_short_LOD2 | caali_curly_short.glb | — | live |
| `skyrydahs-characters/wardrobe_hd/head/caali_head.glb` | glb | 2.27 MB | `bf9c141cd995a5d140b22f92b8913214` | tris=57997; joints=66; LODs=caali_head_LOD0,caali_head_LOD1,caali_head_LOD2 | caali_head.glb | — | live |
| `skyrydahs-characters/wardrobe_hd/jacket/caali_bomber.glb` | glb | 3.40 MB | `9246f8bf73d14620d54878ce0e587853` | tris=58595; joints=66; LODs=caali_bomber_LOD0,caali_bomber_LOD1,caali_bomber_LOD2 | caali_bomber.glb | — | live |
| `skyrydahs-characters/wardrobe_hd/neck/gold_chain_thick.glb` | glb | 1.47 MB | `e838cfd2f8761c2e8ee2ebb8bd8c8c74` | tris=11570; joints=66; LODs=gold_chain_thick_LOD0,gold_chain_thick_LOD1,gold_chain_thick_LOD2 | gold_chain_thick.glb | — | live |
| `skyrydahs-characters/wardrobe_hd/pants/caali_cargo.glb` | glb | 3.80 MB | `80b0e9b4160f5b59b4bac6364b737b65` | tris=57998; joints=66; LODs=caali_cargo_LOD0,caali_cargo_LOD1,caali_cargo_LOD2 | caali_cargo.glb | — | live |
| `skyrydahs-characters/wardrobe_hd/riders/caali-g-hd-raw.glb` | glb | 28.32 MB | `c744714249e190dad049d4f8df6acead` | tris=334965; joints=66; LODs=CaaliG_LOD0,CaaliG_LOD1,CaaliG_LOD2 | caali-g-hd-raw.glb | — | live |
| `skyrydahs-characters/wardrobe_hd/slots.json` | json | 221 B | `7c96984531e06a2ff4b98c5d6c0df105` | — | slots.json | — | live |
| `skyrydahs-characters/wardrobe_hd/top/caali_gr8yzone_tee.glb` | glb | 2.20 MB | `84d2250a0886c67a21b057e4ec073eed` | tris=45200; joints=66; LODs=caali_gr8yzone_tee_LOD0,caali_gr8yzone_tee_LOD1,caali_gr8yzone_tee_LOD2 | caali_gr8yzone_tee.glb | — | live |
| `skyrydahs-characters/wardrobe_hd/top/gr8yzone_logo.png` | png | 90.4 KB | `46a9871806eb0ddb26d6a0b3ecf3e7aa` | — | gr8yzone_logo.png | — | live |
| `skyrydahs-ref/characters/anika-rig-plan.md` | md | 7.0 KB | `5464d4e5e78a25a98c972f8f9e24ac9d` | — | anika-rig-plan.md | — | live |
| `skyrydahs-ref/characters/at-standard-spec.md` | md | 6.3 KB | `684d8562d2c0bfbd5b1e30b4423e3070` | — | at-standard-spec.md | — | live |
| `skyrydahs-ref/characters/caali-anika-2026-10-30/README.md` | md | 1.7 KB | `bade601c98393ef097cae4f9464c1da0` | — | README.md | — | live |
| `skyrydahs-ref/characters/caali-anika-2026-10-30/caali-anika-ref1-night-fx.jpg` | jpg | 922.8 KB | `4e43a33c9802ab760a6810dab1655780` | — | caali-anika-ref1-night-fx.jpg | — | live |
| `skyrydahs-ref/characters/caali-anika-2026-10-30/caali-anika-ref2-day-clean.jpg` | jpg | 763.1 KB | `3a47ff8532ee6901eb589ad0b9c5d766` | — | caali-anika-ref2-day-clean.jpg | — | live |
| `skyrydahs-ref/characters/caali-anika-2026-10-30/caali-anika-ref3-pole-grind.jpg` | jpg | 843.7 KB | `0bf5d9bd53d6024233c8a4dd174802c4` | — | caali-anika-ref3-pole-grind.jpg | — | live |
| `skyrydahs-ref/characters/caali-anika-2026-10-30/forge-plan.md` | md | 15.3 KB | `f03c5b69947c97b47138d6f398d909ef` | — | forge-plan.md | — | live |
| `skyrydahs-ref/characters/caali-g-rerig-plan.md` | md | 3.1 KB | `23ddd71c057939647589239fa0259b3a` | — | caali-g-rerig-plan.md | — | live |
| `skyrydahs-ref/characters/character-bible.md` | md | 15.9 KB | `1389f3009bd0be774c9a48b4ec6ac28e` | — | Character bible (updated 2026-11-05 with Simca — solo / unaffiliated, the Migratory Bird). | — | live |
| `skyrydahs-ref/characters/meshy-batch-plan.md` | md | 7.8 KB | `c3fdf289291c68299571203a6dd0959a` | — | meshy-batch-plan.md | — | live |
| `skyrydahs-ref/characters/simca-springs.md` | md | 2.6 KB | `580c2d7c22ef159adea0181453061655` | — | Simca spring-bone doc: 8 hair chains × 8 bones on Head, 155 joints; export notes for Rigger. | — | live |
| `skyrydahs-ref/meshy-prompts-crews.md` | md | 21.7 KB | `0f47f6284cf02e704fb54b736965fd6e` | — | meshy-prompts-crews.md | — | live |
| `skyrydahs-ref/simca/refs-2026-11-05/contact.jpg` | jpg | 114.1 KB | `f3da33067e1a977f503a95f6f77f134e` | — | Simca reference still contact.jpg (2026-11-05). | — | ref-shot |
| `skyrydahs-ref/simca/refs-2026-11-05/ref1.jpg` | jpg | 43.0 KB | `0dd9bf49dd0c0241d5a016ebc8ab009b` | — | Simca reference still ref1.jpg (2026-11-05). | — | ref-shot |
| `skyrydahs-ref/simca/refs-2026-11-05/ref2.jpg` | jpg | 26.3 KB | `8ee501adabcae35c2cc29ee78f8aff23` | — | Simca reference still ref2.jpg (2026-11-05). | — | ref-shot |
| `skyrydahs-ref/simca/refs-2026-11-05/ref3.jpg` | jpg | 49.2 KB | `2c8448080c70471162f815ee8dc111aa` | — | Simca reference still ref3.jpg (2026-11-05). | — | ref-shot |
| `skyrydahs-ref/simca/refs-2026-11-05/ref4.jpg` | jpg | 8.7 KB | `de45d4633e99f93528c459d3d22444f0` | — | Simca reference still ref4.jpg (2026-11-05). | — | ref-shot |
| `skyrydahs-ref/simca/refs-2026-11-05/ref5.jpg` | jpg | 5.6 KB | `6b56614e501eafc9c42e2a25334e84f6` | — | Simca reference still ref5.jpg (2026-11-05). | — | ref-shot |
| `skyrydahs-ref/simca/refs-2026-11-05/ref6.jpg` | jpg | 20.3 KB | `425a18ce5f2b6ee4038d42aded29d0dd` | — | Simca reference still ref6.jpg (2026-11-05). | — | ref-shot |
| `skyrydahs-ref/simca/refs-2026-11-05/ref7.jpg` | jpg | 27.6 KB | `17dd4a422308492a54c449a2c9f8a444` | — | Simca reference still ref7.jpg (2026-11-05). | — | ref-shot |
| `tools/deinterleave.py` | py | 1.7 KB | `efacb7576f87caa9bb0d906aba44f821` | — | Rewrites GLB accessors from interleaved to non-interleaved buffers (fixes mergeBufferGeometries). | GLB files (esp. at-skate-meshy*.glb) | tool |
| `v3build/combat_fx.js` | js | 44.1 KB | `3bb87245062ca0bcb0a416159702b8cf` | — | CombatFX API: emit/hit/slash/lightning/stagger/super/lockOn/trail/attach/fromHitFrame; per-crew palettes; max 3 draws. | THREE, scene, SR_PAD optional, rider userData.fx (Rigger srFX) | live |
| `v3build/gamepad.js` | js | 10.3 KB | `52e471720805b2fc1a00f728997f4cce` | — | Xbox/standard pad layer: sticks, buttons, triggers, SR_PAD.haptic(evt,opts) with comfort scale. | Gamepad API + optional XR gamepad haptic actuators | live |
| `v3build/minimap_v2.js` | js | 19.6 KB | `707054b6a46cc951112ef0d3d8a07dfd` | — | Tilted heading-up minimap, rim N, rim-clamped waypoints, window.MINIMAP.state API. | canvas 2D HUD, objective/cops markers | live |
| `v3build/patch_combat_fx.py` | py | 845 B | `6d2a6fdc90ffcf3ea8914773dbc4fb57` | — | Injects combat_fx.js CombatFX module before </body>; idempotent; SR_HTML/argv aware. | combat_fx.js, SR_PAD.haptic (gamepad), Rigger srFX attach points, THREE | live (ready for rebuild; CombatFX v3) |
| `v3build/patch_gamepad.py` | py | 7.1 KB | `840d419d42fc3a77c0987fce65dd2487` | — | Injects gamepad.js as window.SR_PAD; routes navigator.getGamepads through it; haptics API used by CombatFX. | gamepad.js; XR renderer.xr session for pulses; Systems/combat callers of SR_PAD.haptic | live (Forge-initiated; Optimizer extended haptics) |
| `v3build/patch_minimap.py` | py | 1.0 KB | `14734f38be23f809abc254bd7b259aa1` | — | Injects minimap_v2.js Watch Dogs-style tilted GPS minimap + direction markers. | minimap_v2.js, map.js, icons.js, phone HUD | live |
| `v3build/patch_quant_fix.py` | py | 2.4 KB | `9746c0f2b2d25abcc7e915303fff369e` | — | Dequantizes KHR_mesh_quantization POSITION back to float metres and fixes skin IBM so AT wheel centres (_WC) spin correctly. | Skinned wardrobe/Ikki riders with quantized POSITION; IKKI_AT_VERT / _WC attributes | live |
| `v3build/patch_rider_style.py` | py | 663 B | `5fcf4e3be7a1d6926d3e655be3e01ae4` | — | Inlines rider_style.js Option 3 shading before // ===== LOOP =====. Hook: after patch_pbr_base.py, before patch_xr_fxmem.py. Opt-in ?riderstyle=opt3. | rider_style.js, RIDERS, PBR_WORLD env when present | opt-in; official gate PASS; ready for rebuild |
| `v3build/patch_wardrobe.py` | py | 7.8 KB | `be0ebe08ea19e01bec4125d21d99d403` | — | Injects wardrobe system + Caali G as default player on shared Meshy skeleton/skate poser; wires WARDROBE_RIDERS, outfit apply, hide slots. | wardrobe_js/wardrobe.js (inlined/loaded), jackets.js AT skate API, riders.js loadIkki, CHAR_BASE assets under skyrydahs-characters/ | live |
| `v3build/patch_wardrobe_v6pre.py` | py | 5.9 KB | `f87700fec224bbfe069b0abd9efda8d3` | — | Older wardrobe patch variant (v6pre); superseded by patch_wardrobe.py. | wardrobe_v6pre.js | WIP/archive |
| `v3build/perf/forge/at-skate-v2.md` | md | 6.4 KB | `091685abebdb856bda7285b8defc81f1` | — | Doc at-skate-v2.md | — | doc |
| `v3build/perf/forge/cfx_base.png` | png | 2.55 MB | `9597f29aa3ba4423e57e213c8a247c4f` | — | Doc cfx_base.png | — | doc |
| `v3build/perf/forge/cfx_base_combat_fx_anubis.png` | png | 2.64 MB | `b37640cd697846f7f2d41159b2f64f09` | — | Doc cfx_base_combat_fx_anubis.png | — | doc |
| `v3build/perf/forge/cfx_base_combat_fx_behemoth.png` | png | 2.64 MB | `5162e6e7ebc6df71688e45220c0c3fd6` | — | Doc cfx_base_combat_fx_behemoth.png | — | doc |
| `v3build/perf/forge/cfx_base_combat_fx_codee.png` | png | 2.86 MB | `8df4bb93f828b522d225d82c1b1a5809` | — | Doc cfx_base_combat_fx_codee.png | — | doc |
| `v3build/perf/forge/cfx_base_combat_fx_forest.png` | png | 2.65 MB | `9703b22695d3ac716ac5c1455a2b8063` | — | Doc cfx_base_combat_fx_forest.png | — | doc |
| `v3build/perf/forge/cfx_base_combat_fx_genesis.png` | png | 2.64 MB | `a2796cc2edac1b9969ae7240e3e85b8a` | — | Doc cfx_base_combat_fx_genesis.png | — | doc |
| `v3build/perf/forge/cfx_base_combat_fx_karasu.png` | png | 2.63 MB | `b351c9529caefd5f4a7ccaf4b80beb75` | — | Doc cfx_base_combat_fx_karasu.png | — | doc |
| `v3build/perf/forge/cfx_base_combat_fx_pressured_forest.png` | png | 2.66 MB | `ba606d41ac7f7f081822a680d85fa02c` | — | Doc cfx_base_combat_fx_pressured_forest.png | — | doc |
| `v3build/perf/forge/cfx_base_combat_fx_rustclaw.png` | png | 2.65 MB | `56e62b9b4d568015d139cbf065a8e8ee` | — | Doc cfx_base_combat_fx_rustclaw.png | — | doc |
| `v3build/perf/forge/cfx_base_combat_fx_static.png` | png | 2.64 MB | `30db5732009fd6e998d9d8ca36b7f113` | — | Doc cfx_base_combat_fx_static.png | — | doc |
| `v3build/perf/forge/cfx_base_combat_fx_super_codee.png` | png | 2.65 MB | `af511b44dc582f44b1f85630778bd405` | — | Doc cfx_base_combat_fx_super_codee.png | — | doc |
| `v3build/perf/forge/cfx_base_combat_fx_super_karasu.png` | png | 2.66 MB | `751670240cc134565e210d7be2331e9c` | — | Doc cfx_base_combat_fx_super_karasu.png | — | doc |
| `v3build/perf/forge/cfx_base_combat_fx_ttt.png` | png | 2.64 MB | `7e28fa1f674dc144eb47d9bdbe6f5229` | — | Doc cfx_base_combat_fx_ttt.png | — | doc |
| `v3build/perf/forge/cfx_base_combat_fx_volt.png` | png | 2.64 MB | `903affe895fa4c75183bc346fd223ff7` | — | Doc cfx_base_combat_fx_volt.png | — | doc |
| `v3build/perf/forge/combat-fx-hue-delta.json` | json | 429 B | `65215aaba5389dc67340f203993bfba4` | — | Doc combat-fx-hue-delta.json | — | doc |
| `v3build/perf/forge/combat-fx-hue-final.json` | json | 1.4 KB | `d1ad96958b35a351d6a1907d4bf538dd` | — | Doc combat-fx-hue-final.json | — | doc |
| `v3build/perf/forge/combat-fx-hue.json` | json | 435 B | `e784e8c8fe88553efab0d3afb9ee23a8` | — | Doc combat-fx-hue.json | — | doc |
| `v3build/perf/forge/combat-fx-kick.json` | json | 1.3 KB | `834c77d97e9ff7a0d51a432a88d0e940` | — | Doc combat-fx-kick.json | — | doc |
| `v3build/perf/forge/combat-fx-shots.json` | json | 1.2 KB | `12936c8302e565f4de8ef38a96c16cd5` | — | Doc combat-fx-shots.json | — | doc |
| `v3build/perf/forge/combat-fx.md` | md | 13.2 KB | `ab30654d1fe026e456f1066b67db0925` | — | Doc combat-fx.md | — | doc |
| `v3build/perf/forge/deinterleave-guard.diff` | diff | 1.1 KB | `405a15e405dcab36f3c1f6a8bee858cd` | — | Doc deinterleave-guard.diff | — | doc |
| `v3build/perf/forge/rider-style-opt3.md` | md | 3.0 KB | `da06c645d25cb07a270a1f158a58789b` | — | Opt3 rider-style gate results (official PASS) and build-hook notes. | — | doc |
| `v3build/perf/rider-style-opt3-constraints.md` | md | 5.6 KB | `0413bbc63f86be340c317bb80423d008` | — | rider-style-opt3-constraints.md | — | live |
| `v3build/perf/rider-style-opt3-gate.md` | md | 1.8 KB | `ea11f2cb9412d51addf98e2d7b52da8f` | — | rider-style-opt3-gate.md | — | live |
| `v3build/props/kit/couch.glb` | glb | 284.5 KB | `a143bbc991e90d5a5fb3a604fe5c2864` | tris=5500; meshes=Mesh_0.001 | Garage kit prop couch | crewhouse_kit.js kitProp/kitPodGlb/kitDroneGlb | live |
| `v3build/props/kit/couch.ktx2.glb` | glb | 942.5 KB | `018c6270b2f8cb2dab60edae0b1ca177` | tris=5500; meshes=Mesh_0.001 | Garage kit prop couch.ktx2 | crewhouse_kit.js kitProp/kitPodGlb/kitDroneGlb | staged |
| `v3build/props/kit/desk.glb` | glb | 365.6 KB | `322ba96b9c3cf7a262e252964a7e816b` | tris=5494; meshes=Mesh_0.001 | Garage kit prop desk | crewhouse_kit.js kitProp/kitPodGlb/kitDroneGlb | live |
| `v3build/props/kit/desk.ktx2.glb` | glb | 1.11 MB | `3dfcead686a490cd4d0f172b1df33e20` | tris=5494; meshes=Mesh_0.001 | Garage kit prop desk.ktx2 | crewhouse_kit.js kitProp/kitPodGlb/kitDroneGlb | staged |
| `v3build/props/kit/drone.glb` | glb | 14.9 KB | `3519ca7c389d5d3242558fcd4ddd48ec` | tris=972; meshes=drone_body,rotor_BL,rotor_BR,rotor_FL | Garage kit prop drone | crewhouse_kit.js kitProp/kitPodGlb/kitDroneGlb | live |
| `v3build/props/kit/drone.ktx2.glb` | glb | 14.0 KB | `ce1c5893700f0f3b3468d7613896a9e3` | tris=972; meshes=drone_body,rotor_BL,rotor_BR,rotor_FL | Garage kit prop drone.ktx2 | crewhouse_kit.js kitProp/kitPodGlb/kitDroneGlb | staged |
| `v3build/props/kit/garage_props_sheet.png` | png | 574.3 KB | `0257510b99b20af2308c037c721454ee` | — | garage_props_sheet.png | — | live |
| `v3build/props/kit/kitchen.glb` | glb | 227.1 KB | `2fb1cb40114ec3367515376357764290` | tris=7800; meshes=Mesh_0.001 | Garage kit prop kitchen | crewhouse_kit.js kitProp/kitPodGlb/kitDroneGlb | live |
| `v3build/props/kit/kitchen.ktx2.glb` | glb | 782.6 KB | `181c86b96958c4edbc2586ea82dac357` | tris=7800; meshes=Mesh_0.001 | Garage kit prop kitchen.ktx2 | crewhouse_kit.js kitProp/kitPodGlb/kitDroneGlb | staged |
| `v3build/props/kit/lockers.glb` | glb | 304.5 KB | `118180b9a550a8b6f6bcf64ebeb98f1c` | tris=7896; meshes=Mesh_0.001 | Garage kit prop lockers | crewhouse_kit.js kitProp/kitPodGlb/kitDroneGlb | live |
| `v3build/props/kit/lockers.ktx2.glb` | glb | 1.15 MB | `217792f203f12a4dc87b54b9722194a9` | tris=7896; meshes=Mesh_0.001 | Garage kit prop lockers.ktx2 | crewhouse_kit.js kitProp/kitPodGlb/kitDroneGlb | staged |
| `v3build/props/kit/manifest.json` | json | 78 B | `2c1e2ddd09623a35018cb3d6ef307e53` | — | manifest.json | — | live |
| `v3build/props/kit/pod.glb` | glb | 35.8 KB | `91329b2c56b03e9443a8bd79706836cf` | tris=2756; meshes=pod | Garage kit prop pod | crewhouse_kit.js kitProp/kitPodGlb/kitDroneGlb | live |
| `v3build/props/kit/pod.ktx2.glb` | glb | 22.0 KB | `b13dc750afb746bf29f4d412e31fc693` | tris=2756; meshes=pod | Garage kit prop pod.ktx2 | crewhouse_kit.js kitProp/kitPodGlb/kitDroneGlb | staged |
| `v3build/props/kit/pod_closed.glb` | glb | 34.5 KB | `a831bab9331be9223baa8fca23bf33a4` | tris=2468; meshes=pod | Garage kit prop pod_closed | crewhouse_kit.js kitProp/kitPodGlb/kitDroneGlb | live |
| `v3build/props/kit/pod_closed.ktx2.glb` | glb | 20.8 KB | `1a73214df90fef28f6bc83c70ebd4bf2` | tris=2468; meshes=pod | Garage kit prop pod_closed.ktx2 | crewhouse_kit.js kitProp/kitPodGlb/kitDroneGlb | staged |
| `v3build/props/kit/preview_couch.png` | png | 679.5 KB | `4566a59f4b58465e078a89e844dd9275` | — | preview_couch.png | — | live |
| `v3build/props/kit/preview_desk.png` | png | 685.9 KB | `610adbb6f243218029d36bb9d1ab0ea0` | — | preview_desk.png | — | live |
| `v3build/props/kit/preview_drone.png` | png | 790.0 KB | `b72722cb16cb67f3f5942f7bdb1b5b9a` | — | preview_drone.png | — | live |
| `v3build/props/kit/preview_kitchen.png` | png | 676.1 KB | `a38fae7dfcc463eb033b7032173c90df` | — | preview_kitchen.png | — | live |
| `v3build/props/kit/preview_lockers.png` | png | 765.0 KB | `36445a8a7f8a58f4c06f2f58f6008986` | — | preview_lockers.png | — | live |
| `v3build/props/kit/preview_pod.png` | png | 757.5 KB | `865f29906e6a4317a497102876d4923c` | — | preview_pod.png | — | live |
| `v3build/props/kit/preview_pod_closed.png` | png | 752.3 KB | `8148c558875f9a14b63ff64927fb102d` | — | preview_pod_closed.png | — | live |
| `v3build/props/kit/preview_tv.png` | png | 647.6 KB | `a0bf9753da6172366d35b40f531a5895` | — | preview_tv.png | — | live |
| `v3build/props/kit/tv.glb` | glb | 7.2 KB | `704c628e4ccdaa3eaa59a05930970290` | tris=86; meshes=screen,tv_body | Garage kit prop tv | crewhouse_kit.js kitProp/kitPodGlb/kitDroneGlb | live |
| `v3build/props/kit/tv.ktx2.glb` | glb | 7.6 KB | `ff7097fc62f2847d36283181aca4508a` | tris=86; meshes=screen,tv_body | Garage kit prop tv.ktx2 | crewhouse_kit.js kitProp/kitPodGlb/kitDroneGlb | staged |
| `v3build/rider_style.js` | js | 8.8 KB | `45ca2ff822c6d9b4624fe66494f3cfc7` | — | Option 3 stylized-realistic rider shading: shared PMREM/env, fresnel rim in crew colour, hair/metal spec, drop toon hull; opt-in ?riderstyle=opt3. Official gate PASS (−1 draw). | Inlined by patch_rider_style.py; PBR_WORLD | opt-in; official gate PASS; ready for rebuild |
| `v3build/rider_style_opt3_close_shots.py` | py | 5.3 KB | `b87b136187286d310870426952659045` | — | Close-up (~3/4 front, rider ~60% of frame) opt3 before/after shots with locked camera/time and NPCs hidden; builds close contact sheet. | — | tool |
| `v3build/rider_style_opt3_shots.py` | py | 3.4 KB | `f4c62de362663059f578e0bc28747cba` | — | Chase-distance opt3 before/after hero shots for Caali, Anika, Ikki (day/night) plus contact sheet. | — | tool |
| `v3build/shots/hero/anika_34_vs_ref.png` | png | 3.26 MB | `ad6fec4bf6f30e0747085b35848af50f` | — | Forge hero shot anika_34_vs_ref.png | — | ref-shot |
| `v3build/shots/hero/anika_front_vs_ref.png` | png | 3.25 MB | `d9f82e3fc1f6a23f1ca0e0928cc8d747` | — | Forge hero shot anika_front_vs_ref.png | — | ref-shot |
| `v3build/shots/hero/build_AI4_anika.png` | png | 2.83 MB | `dd34c6c74feb8c6d7c15f819718694d3` | — | Forge hero shot build_AI4_anika.png | — | ref-shot |
| `v3build/shots/hero/build_AI4_caali.png` | png | 2.84 MB | `acb4f411a059aca75dcac7420708c254` | — | Forge hero shot build_AI4_caali.png | — | ref-shot |
| `v3build/shots/hero/build_AI_anika.png` | png | 2.57 MB | `b501e4df6dd743a3699fd6c2b89d81e9` | — | Forge hero shot build_AI_anika.png | — | ref-shot |
| `v3build/shots/hero/build_AI_caali_v2.png` | png | 2.64 MB | `27ba532d3594e7f9bb97154852be4554` | — | Forge hero shot build_AI_caali_v2.png | — | ref-shot |
| `v3build/shots/hero/caali_v2_34_vs_ref.png` | png | 3.13 MB | `875a23164fb426dcce58f4cbd2c55bb3` | — | Forge hero shot caali_v2_34_vs_ref.png | — | ref-shot |
| `v3build/shots/hero/caali_v2_front_vs_ref.png` | png | 3.11 MB | `8fe0a0a10eca92eb48bfba950571efef` | — | Forge hero shot caali_v2_front_vs_ref.png | — | ref-shot |
| `v3build/shots/hero/combat_fx_anubis.png` | png | 2.78 MB | `bc3a94acaef481178654e85893168bea` | — | Forge hero shot combat_fx_anubis.png | — | ref-shot |
| `v3build/shots/hero/combat_fx_behemoth.png` | png | 2.78 MB | `bc00ac793b79c97effca5229b993e66d` | — | Forge hero shot combat_fx_behemoth.png | — | ref-shot |
| `v3build/shots/hero/combat_fx_codee.png` | png | 3.09 MB | `29b0e6a89e785769d6e8bf0cac59dc99` | — | Forge hero shot combat_fx_codee.png | — | ref-shot |
| `v3build/shots/hero/combat_fx_contact_sheet.png` | png | 2.33 MB | `eeb863db69ed105929ec2d8740323c42` | — | Forge hero shot combat_fx_contact_sheet.png | — | ref-shot |
| `v3build/shots/hero/combat_fx_contact_sheet_v1.png` | png | 2.79 MB | `524386d2a5cdc5cf1f51c64d5f8eb75d` | — | Forge hero shot combat_fx_contact_sheet_v1.png | — | ref-shot |
| `v3build/shots/hero/combat_fx_forest.png` | png | 2.79 MB | `6b55bd62ab026ac09de5b2c52155959c` | — | Forge hero shot combat_fx_forest.png | — | ref-shot |
| `v3build/shots/hero/combat_fx_genesis.png` | png | 2.79 MB | `74e9eea517f3518173e90f447ea9abf0` | — | Forge hero shot combat_fx_genesis.png | — | ref-shot |
| `v3build/shots/hero/combat_fx_karasu.png` | png | 2.75 MB | `1ea68a47f816ccc965652b0f15ddb2ee` | — | Forge hero shot combat_fx_karasu.png | — | ref-shot |
| `v3build/shots/hero/combat_fx_kick_wheel_0.png` | png | 2.90 MB | `1e557db7d37313f6cf9f59017b1089a5` | — | Forge hero shot combat_fx_kick_wheel_0.png | — | ref-shot |
| `v3build/shots/hero/combat_fx_kick_wheel_1.png` | png | 3.00 MB | `6addd6cdae0ec7089408e1db79ae9eea` | — | Forge hero shot combat_fx_kick_wheel_1.png | — | ref-shot |
| `v3build/shots/hero/combat_fx_kick_wheel_2.png` | png | 2.67 MB | `903a595fa1c3fe9c389f1d88cb596156` | — | Forge hero shot combat_fx_kick_wheel_2.png | — | ref-shot |
| `v3build/shots/hero/combat_fx_kick_wheel_3.png` | png | 2.65 MB | `a8ccebdeb81f0a7a9c90f1349b11e502` | — | Forge hero shot combat_fx_kick_wheel_3.png | — | ref-shot |
| `v3build/shots/hero/combat_fx_pressured_forest.png` | png | 2.74 MB | `a7bf11cb129c8592a09e0ff0c4299b18` | — | Forge hero shot combat_fx_pressured_forest.png | — | ref-shot |
| `v3build/shots/hero/combat_fx_rustclaw.png` | png | 2.73 MB | `da3183b06122cb85a18edae57a8aa2eb` | — | Forge hero shot combat_fx_rustclaw.png | — | ref-shot |
| `v3build/shots/hero/combat_fx_static.png` | png | 2.83 MB | `012186b75921bfec2dec068bfa9f84b5` | — | Forge hero shot combat_fx_static.png | — | ref-shot |
| `v3build/shots/hero/combat_fx_super_codee.png` | png | 3.14 MB | `3c3d4a7c3da6c4884d93e8e4f09042cc` | — | Forge hero shot combat_fx_super_codee.png | — | ref-shot |
| `v3build/shots/hero/combat_fx_super_karasu.png` | png | 3.06 MB | `ee3edc59a0c7666ffef85a5807d73c85` | — | Forge hero shot combat_fx_super_karasu.png | — | ref-shot |
| `v3build/shots/hero/combat_fx_ttt.png` | png | 2.76 MB | `7cd429a034ed5cd41856e2a956725d18` | — | Forge hero shot combat_fx_ttt.png | — | ref-shot |
| `v3build/shots/hero/combat_fx_volt.png` | png | 2.77 MB | `8658d234d9e0662b738358b010a4d48d` | — | Forge hero shot combat_fx_volt.png | — | ref-shot |
| `v3build/shots/hero/rider_style_opt3_anika_day_after.png` | png | 4.18 MB | `9b5dd8bf84579cb713e8f01f35942a24` | — | Forge hero shot rider_style_opt3_anika_day_after.png (opt3 rider shading before/after). | — | ref-shot |
| `v3build/shots/hero/rider_style_opt3_anika_day_before.png` | png | 4.16 MB | `f00e17050180cd525a8c12a8f2c30a98` | — | Forge hero shot rider_style_opt3_anika_day_before.png (opt3 rider shading before/after). | — | ref-shot |
| `v3build/shots/hero/rider_style_opt3_anika_night_after.png` | png | 4.32 MB | `cee7beb86fbd601ec6eab001f93bd442` | — | Forge hero shot rider_style_opt3_anika_night_after.png (opt3 rider shading before/after). | — | ref-shot |
| `v3build/shots/hero/rider_style_opt3_anika_night_before.png` | png | 4.33 MB | `5517f56c72cc69b1271ff7db9bb4bb38` | — | Forge hero shot rider_style_opt3_anika_night_before.png (opt3 rider shading before/after). | — | ref-shot |
| `v3build/shots/hero/rider_style_opt3_caali_day_after.png` | png | 4.20 MB | `4d3dd8ff33fddae0ca07c260f1e1a177` | — | Forge hero shot rider_style_opt3_caali_day_after.png (opt3 rider shading before/after). | — | ref-shot |
| `v3build/shots/hero/rider_style_opt3_caali_day_before.png` | png | 4.20 MB | `65212c6bf21491cee947d3aee48cadca` | — | Forge hero shot rider_style_opt3_caali_day_before.png (opt3 rider shading before/after). | — | ref-shot |
| `v3build/shots/hero/rider_style_opt3_caali_night_after.png` | png | 4.33 MB | `9a284bdb6118dd5380cbd80f8f069982` | — | Forge hero shot rider_style_opt3_caali_night_after.png (opt3 rider shading before/after). | — | ref-shot |
| `v3build/shots/hero/rider_style_opt3_caali_night_before.png` | png | 4.35 MB | `2c3405247c14eb671c516798498033e9` | — | Forge hero shot rider_style_opt3_caali_night_before.png (opt3 rider shading before/after). | — | ref-shot |
| `v3build/shots/hero/rider_style_opt3_close_anika_day_after.png` | png | 3.35 MB | `11c830028b41b7ce31eead950fdea669` | — | Forge hero shot rider_style_opt3_close_anika_day_after.png (opt3 rider shading before/after). | — | ref-shot |
| `v3build/shots/hero/rider_style_opt3_close_anika_day_before.png` | png | 3.31 MB | `faa2fca0d770619e2659303a061efc89` | — | Forge hero shot rider_style_opt3_close_anika_day_before.png (opt3 rider shading before/after). | — | ref-shot |
| `v3build/shots/hero/rider_style_opt3_close_anika_night_after.png` | png | 3.47 MB | `36f028f457c859fb9f4cbc2bc08947f9` | — | Forge hero shot rider_style_opt3_close_anika_night_after.png (opt3 rider shading before/after). | — | ref-shot |
| `v3build/shots/hero/rider_style_opt3_close_anika_night_before.png` | png | 3.43 MB | `cfaa3e72a7ce6177698bf0a3c3c4b06a` | — | Forge hero shot rider_style_opt3_close_anika_night_before.png (opt3 rider shading before/after). | — | ref-shot |
| `v3build/shots/hero/rider_style_opt3_close_caali_day_after.png` | png | 3.37 MB | `93f6089e780c979d5a793c0c885c6b99` | — | Forge hero shot rider_style_opt3_close_caali_day_after.png (opt3 rider shading before/after). | — | ref-shot |
| `v3build/shots/hero/rider_style_opt3_close_caali_day_before.png` | png | 3.32 MB | `28c21727b1ff30f39d123f91d40ba4c1` | — | Forge hero shot rider_style_opt3_close_caali_day_before.png (opt3 rider shading before/after). | — | ref-shot |
| `v3build/shots/hero/rider_style_opt3_close_caali_night_after.png` | png | 3.48 MB | `66e9336e57c6789a5d2b673e7c84036c` | — | Forge hero shot rider_style_opt3_close_caali_night_after.png (opt3 rider shading before/after). | — | ref-shot |
| `v3build/shots/hero/rider_style_opt3_close_caali_night_before.png` | png | 3.41 MB | `1967fa7748ea9b90457cb1377df564ab` | — | Forge hero shot rider_style_opt3_close_caali_night_before.png (opt3 rider shading before/after). | — | ref-shot |
| `v3build/shots/hero/rider_style_opt3_close_contact.png` | png | 3.98 MB | `4763dd1e49c04b0a07cffb4dadca670a` | — | Opt3 close-up before/after contact sheet (Caali, Anika, Ikki; day/night; NPCs hidden). | — | ref-shot |
| `v3build/shots/hero/rider_style_opt3_close_ikki_day_after.png` | png | 3.36 MB | `21781b336256750452de9793064ae45e` | — | Forge hero shot rider_style_opt3_close_ikki_day_after.png (opt3 rider shading before/after). | — | ref-shot |
| `v3build/shots/hero/rider_style_opt3_close_ikki_day_before.png` | png | 3.34 MB | `b6e8d1a82b60e2f6572e90765e6a99dc` | — | Forge hero shot rider_style_opt3_close_ikki_day_before.png (opt3 rider shading before/after). | — | ref-shot |
| `v3build/shots/hero/rider_style_opt3_close_ikki_night_after.png` | png | 3.48 MB | `190cbbe3dd46f1b43078565d59337fc8` | — | Forge hero shot rider_style_opt3_close_ikki_night_after.png (opt3 rider shading before/after). | — | ref-shot |
| `v3build/shots/hero/rider_style_opt3_close_ikki_night_before.png` | png | 3.45 MB | `f780d68551d3ab256cdd2bba278ad16a` | — | Forge hero shot rider_style_opt3_close_ikki_night_before.png (opt3 rider shading before/after). | — | ref-shot |
| `v3build/shots/hero/rider_style_opt3_contact.png` | png | 1.70 MB | `de392d76dfddacdad9e02ba91f9879dd` | — | Opt3 chase-distance before/after contact sheet (Caali, Anika, Ikki; day/night). | — | ref-shot |
| `v3build/shots/hero/rider_style_opt3_ikki_day_after.png` | png | 4.23 MB | `88a9d2ccaf1950a53a96ee5aef704154` | — | Forge hero shot rider_style_opt3_ikki_day_after.png (opt3 rider shading before/after). | — | ref-shot |
| `v3build/shots/hero/rider_style_opt3_ikki_day_before.png` | png | 4.22 MB | `4f97b12eaf1fef10de6b99d4301350d4` | — | Forge hero shot rider_style_opt3_ikki_day_before.png (opt3 rider shading before/after). | — | ref-shot |
| `v3build/shots/hero/rider_style_opt3_ikki_night_after.png` | png | 4.37 MB | `685fce834c75d8ad8ce9ec3c14f6240d` | — | Forge hero shot rider_style_opt3_ikki_night_after.png (opt3 rider shading before/after). | — | ref-shot |
| `v3build/shots/hero/rider_style_opt3_ikki_night_before.png` | png | 4.34 MB | `fca3c29c381d31d023caad54ffcd12b4` | — | Forge hero shot rider_style_opt3_ikki_night_before.png (opt3 rider shading before/after). | — | ref-shot |
| `v3build/shots/hero/simca_34.png` | png | 2.13 MB | `c8f8914915ee3be0f771d049c5e25581` | — | Simca 3/4 review shot. | — | ref-shot |
| `v3build/shots/hero/simca_back.png` | png | 2.07 MB | `1b4e646135240818ee17d7d07ea3ae4a` | — | Simca back review shot. | — | ref-shot |
| `v3build/shots/hero/simca_contact.png` | png | 5.07 MB | `261203d61f060a2bcaa3587a24a301c6` | — | Simca turnaround contact sheet. | — | ref-shot |
| `v3build/shots/hero/simca_face.png` | png | 2.29 MB | `a2a8d2ed7def7f67d6ca72b660408bda` | — | Simca face close-up. | — | ref-shot |
| `v3build/shots/hero/simca_front.png` | png | 2.13 MB | `148d6a8e2ab49a5d6902651a9d84566a` | — | Simca front review shot. | — | ref-shot |
| `v3build/shots/hero/simca_vs_ref.png` | png | 3.08 MB | `4d2f36e96ec939556b705511c3bc5b8b` | — | Simca vs reference comparison. | — | ref-shot |
| `v3build/shots/hero/skate_v2_hubs_ingame.png` | png | 2.51 MB | `1a997b06eb71966bce2ed2dd286f6cbe` | — | Forge hero shot skate_v2_hubs_ingame.png | — | ref-shot |
| `v3build/shots/hero/skate_v2_hubs_ingame_before.png` | png | 2.49 MB | `cbbc105b5bbb02e68553d92dd3b14697` | — | Forge hero shot skate_v2_hubs_ingame_before.png | — | ref-shot |
| `v3build/shots/hero/skate_v2_vs_old.png` | png | 3.09 MB | `d7bc7ea3b940d8bdcc5ad3a7e318a7ab` | — | Forge hero shot skate_v2_vs_old.png | — | ref-shot |
| `v3build/shots/hero/skatev2_after_contact.png` | png | 5.63 MB | `5ed3455dc9b398aad4753b43c34204b2` | — | Forge hero shot skatev2_after_contact.png | — | ref-shot |
| `v3build/shots/hero/skatev2_after_crew0_npc0_feet.png` | png | 1.54 MB | `072a87d93ffbbd26149e6a69f8355286` | — | Forge hero shot skatev2_after_crew0_npc0_feet.png | — | ref-shot |
| `v3build/shots/hero/skatev2_after_crew0_npc0_front.png` | png | 2.06 MB | `d98e837a95475481c1ae07c7e466b4fd` | — | Forge hero shot skatev2_after_crew0_npc0_front.png | — | ref-shot |
| `v3build/shots/hero/skatev2_after_crew0_npc0_side.png` | png | 2.04 MB | `84496779c08c78bbadf433bdde829d24` | — | Forge hero shot skatev2_after_crew0_npc0_side.png | — | ref-shot |
| `v3build/shots/hero/skatev2_after_crew1_npc1_feet.png` | png | 2.57 MB | `99fbf5abb8304caa3efb2cbefbab0f1d` | — | Forge hero shot skatev2_after_crew1_npc1_feet.png | — | ref-shot |
| `v3build/shots/hero/skatev2_after_crew1_npc1_front.png` | png | 2.23 MB | `cf2f7813dc07702f19a2c60eb1ecd5ee` | — | Forge hero shot skatev2_after_crew1_npc1_front.png | — | ref-shot |
| `v3build/shots/hero/skatev2_after_crew1_npc1_side.png` | png | 3.36 MB | `6f4ab10aa3d0625355c0bfee51aad7f1` | — | Forge hero shot skatev2_after_crew1_npc1_side.png | — | ref-shot |
| `v3build/shots/hero/skatev2_after_crew2_npc2_feet.png` | png | 1.53 MB | `1ba5aaf67f61bb06a5feb3664296bf79` | — | Forge hero shot skatev2_after_crew2_npc2_feet.png | — | ref-shot |
| `v3build/shots/hero/skatev2_after_crew2_npc2_front.png` | png | 1.99 MB | `7ccfc453db9031086836e56e822de42f` | — | Forge hero shot skatev2_after_crew2_npc2_front.png | — | ref-shot |
| `v3build/shots/hero/skatev2_after_crew2_npc2_side.png` | png | 2.14 MB | `4892e2f954e11a16c5f664b2f6860429` | — | Forge hero shot skatev2_after_crew2_npc2_side.png | — | ref-shot |
| `v3build/shots/hero/skatev2_after_crew3_npc3_feet.png` | png | 1.55 MB | `3110d2e3461a7b24014559b809470e23` | — | Forge hero shot skatev2_after_crew3_npc3_feet.png | — | ref-shot |
| `v3build/shots/hero/skatev2_after_crew3_npc3_front.png` | png | 2.13 MB | `47d0cad666e2e100a58ed61b3d6d19dc` | — | Forge hero shot skatev2_after_crew3_npc3_front.png | — | ref-shot |
| `v3build/shots/hero/skatev2_after_crew3_npc3_side.png` | png | 2.15 MB | `fb0524bb8e8c76a00c718305bd5e2927` | — | Forge hero shot skatev2_after_crew3_npc3_side.png | — | ref-shot |
| `v3build/shots/hero/skatev2_after_crew4_npc4_feet.png` | png | 1.54 MB | `bad539212b773a76a97bd65b1bf277e0` | — | Forge hero shot skatev2_after_crew4_npc4_feet.png | — | ref-shot |
| `v3build/shots/hero/skatev2_after_crew4_npc4_front.png` | png | 2.16 MB | `5035e5738557e73889a19b71cb4ffbb6` | — | Forge hero shot skatev2_after_crew4_npc4_front.png | — | ref-shot |
| `v3build/shots/hero/skatev2_after_crew4_npc4_side.png` | png | 2.06 MB | `86c6c6eda8aeca96a1f5a437d4c0af5e` | — | Forge hero shot skatev2_after_crew4_npc4_side.png | — | ref-shot |
| `v3build/shots/hero/skatev2_after_crew5_npc5_feet.png` | png | 1.53 MB | `efbae08f5abb36f0caad3738a584a11e` | — | Forge hero shot skatev2_after_crew5_npc5_feet.png | — | ref-shot |
| `v3build/shots/hero/skatev2_after_crew5_npc5_front.png` | png | 2.15 MB | `1a14c5cf2359fc07f62fab9afb6945ae` | — | Forge hero shot skatev2_after_crew5_npc5_front.png | — | ref-shot |
| `v3build/shots/hero/skatev2_after_crew5_npc5_side.png` | png | 2.00 MB | `4cb971742c87bda02092edb8f64ec2d5` | — | Forge hero shot skatev2_after_crew5_npc5_side.png | — | ref-shot |
| `v3build/shots/hero/skatev2_after_crew6_npc6_feet.png` | png | 2.42 MB | `488a12b2708f7d0abb6422b67c63e33c` | — | Forge hero shot skatev2_after_crew6_npc6_feet.png | — | ref-shot |
| `v3build/shots/hero/skatev2_after_crew6_npc6_front.png` | png | 2.88 MB | `9f782ab27618783c19ee9619c3fc49ca` | — | Forge hero shot skatev2_after_crew6_npc6_front.png | — | ref-shot |
| `v3build/shots/hero/skatev2_after_crew6_npc6_side.png` | png | 2.81 MB | `3d679f193469aa5d31e20d3d41540616` | — | Forge hero shot skatev2_after_crew6_npc6_side.png | — | ref-shot |
| `v3build/shots/hero/skatev2_after_ikki_feet.png` | png | 2.72 MB | `b79bc384c8f5ad1ca63038cb703cfbee` | — | Forge hero shot skatev2_after_ikki_feet.png | — | ref-shot |
| `v3build/shots/hero/skatev2_after_ikki_front.png` | png | 2.90 MB | `831d43058e15949b4575ae423945feac` | — | Forge hero shot skatev2_after_ikki_front.png | — | ref-shot |
| `v3build/shots/hero/skatev2_after_ikki_side.png` | png | 2.72 MB | `6243d82872b9498fd7a7f8854218b9ef` | — | Forge hero shot skatev2_after_ikki_side.png | — | ref-shot |
| `v3build/shots/hero/skatev2_after_player_feet.png` | png | 2.01 MB | `3a70ce3880686c4b7742ab6207db7b3e` | — | Forge hero shot skatev2_after_player_feet.png | — | ref-shot |
| `v3build/shots/hero/skatev2_after_player_front.png` | png | 2.53 MB | `5ca23d2e59dc7105af4f0e9b83d79ebe` | — | Forge hero shot skatev2_after_player_front.png | — | ref-shot |
| `v3build/shots/hero/skatev2_after_player_side.png` | png | 2.24 MB | `825038223b5aecf45d35f6964bd3e999` | — | Forge hero shot skatev2_after_player_side.png | — | ref-shot |
| `v3build/shots/hero/skatev2_before_contact.png` | png | 5.44 MB | `1b4696483a5ed6e5404ea2bab726b21f` | — | Forge hero shot skatev2_before_contact.png | — | ref-shot |
| `v3build/shots/hero/skatev2_before_crew0_npc0_feet.png` | png | 1.54 MB | `88e69ba2f2a0c734007cf4e5ac489502` | — | Forge hero shot skatev2_before_crew0_npc0_feet.png | — | ref-shot |
| `v3build/shots/hero/skatev2_before_crew0_npc0_front.png` | png | 2.17 MB | `c518d3b1b7a6b651a2fee4fb64afbdfe` | — | Forge hero shot skatev2_before_crew0_npc0_front.png | — | ref-shot |
| `v3build/shots/hero/skatev2_before_crew0_npc0_side.png` | png | 2.04 MB | `a3542e756d29773bca2d808f4600f456` | — | Forge hero shot skatev2_before_crew0_npc0_side.png | — | ref-shot |
| `v3build/shots/hero/skatev2_before_crew1_npc1_feet.png` | png | 2.49 MB | `7c82c04439465bb221f61724c4734e45` | — | Forge hero shot skatev2_before_crew1_npc1_feet.png | — | ref-shot |
| `v3build/shots/hero/skatev2_before_crew1_npc1_front.png` | png | 2.80 MB | `ee0db3115b6ad786861562842e3ea0a6` | — | Forge hero shot skatev2_before_crew1_npc1_front.png | — | ref-shot |
| `v3build/shots/hero/skatev2_before_crew1_npc1_side.png` | png | 3.17 MB | `2ba41164da0b221981e22c49bb8607b1` | — | Forge hero shot skatev2_before_crew1_npc1_side.png | — | ref-shot |
| `v3build/shots/hero/skatev2_before_crew2_npc2_feet.png` | png | 1.54 MB | `e62b63327d283a1b78a2724ee8bbc1ce` | — | Forge hero shot skatev2_before_crew2_npc2_feet.png | — | ref-shot |
| `v3build/shots/hero/skatev2_before_crew2_npc2_front.png` | png | 2.14 MB | `5af1a73b49ef0e010e4055679595f178` | — | Forge hero shot skatev2_before_crew2_npc2_front.png | — | ref-shot |
| `v3build/shots/hero/skatev2_before_crew2_npc2_side.png` | png | 2.01 MB | `c80a16eb650dc8d2de4d6f0822985254` | — | Forge hero shot skatev2_before_crew2_npc2_side.png | — | ref-shot |
| `v3build/shots/hero/skatev2_before_crew3_npc3_feet.png` | png | 1.53 MB | `a44c73f5690879b57cd3786137865e4d` | — | Forge hero shot skatev2_before_crew3_npc3_feet.png | — | ref-shot |
| `v3build/shots/hero/skatev2_before_crew3_npc3_front.png` | png | 2.00 MB | `bc0a9343606ce482f1d3b62d9aec0e98` | — | Forge hero shot skatev2_before_crew3_npc3_front.png | — | ref-shot |
| `v3build/shots/hero/skatev2_before_crew3_npc3_side.png` | png | 2.15 MB | `799a457f6bba446216281960106d4c55` | — | Forge hero shot skatev2_before_crew3_npc3_side.png | — | ref-shot |
| `v3build/shots/hero/skatev2_before_crew4_npc4_feet.png` | png | 1.53 MB | `10b07dc0e9e163774d77613da15366db` | — | Forge hero shot skatev2_before_crew4_npc4_feet.png | — | ref-shot |
| `v3build/shots/hero/skatev2_before_crew4_npc4_front.png` | png | 2.02 MB | `4860e6c14282c1e260d44280ad9bfc4a` | — | Forge hero shot skatev2_before_crew4_npc4_front.png | — | ref-shot |
| `v3build/shots/hero/skatev2_before_crew4_npc4_side.png` | png | 2.16 MB | `6690e79ad617950c273df485e229f4ca` | — | Forge hero shot skatev2_before_crew4_npc4_side.png | — | ref-shot |
| `v3build/shots/hero/skatev2_before_crew5_npc5_feet.png` | png | 1.54 MB | `dfe7c3b52a25c0b2a5f84f579e6eba9f` | — | Forge hero shot skatev2_before_crew5_npc5_feet.png | — | ref-shot |
| `v3build/shots/hero/skatev2_before_crew5_npc5_front.png` | png | 2.15 MB | `fbef155b3076097a87e607086f7bf71e` | — | Forge hero shot skatev2_before_crew5_npc5_front.png | — | ref-shot |
| `v3build/shots/hero/skatev2_before_crew5_npc5_side.png` | png | 2.14 MB | `c6340e970a5b8970aaa029e527bdeae2` | — | Forge hero shot skatev2_before_crew5_npc5_side.png | — | ref-shot |
| `v3build/shots/hero/skatev2_before_crew6_npc6_feet.png` | png | 1.54 MB | `af288034208b9b2aaae72d57198846f7` | — | Forge hero shot skatev2_before_crew6_npc6_feet.png | — | ref-shot |
| `v3build/shots/hero/skatev2_before_crew6_npc6_front.png` | png | 2.14 MB | `7cb1d7f56de1ffbee4473a2ef607714e` | — | Forge hero shot skatev2_before_crew6_npc6_front.png | — | ref-shot |
| `v3build/shots/hero/skatev2_before_crew6_npc6_side.png` | png | 2.16 MB | `41bce433f82ae4a66669fc81cb81153f` | — | Forge hero shot skatev2_before_crew6_npc6_side.png | — | ref-shot |
| `v3build/shots/hero/skatev2_before_ikki_feet.png` | png | 2.71 MB | `07f1c3a3fc44ee78c3770c84ae12684c` | — | Forge hero shot skatev2_before_ikki_feet.png | — | ref-shot |
| `v3build/shots/hero/skatev2_before_ikki_front.png` | png | 2.91 MB | `b8cfeec95a3217d9bb78284163dd1241` | — | Forge hero shot skatev2_before_ikki_front.png | — | ref-shot |
| `v3build/shots/hero/skatev2_before_ikki_side.png` | png | 2.87 MB | `ccb8047273a6bfcd4a0ab9ee0922c12c` | — | Forge hero shot skatev2_before_ikki_side.png | — | ref-shot |
| `v3build/shots/hero/skatev2_before_player_feet.png` | png | 2.01 MB | `9bcfcf8e5a66bc79f96ba1db7b4334a9` | — | Forge hero shot skatev2_before_player_feet.png | — | ref-shot |
| `v3build/shots/hero/skatev2_before_player_front.png` | png | 2.52 MB | `612a3ce2856635f8b912826bcb9065b2` | — | Forge hero shot skatev2_before_player_front.png | — | ref-shot |
| `v3build/shots/hero/skatev2_before_player_side.png` | png | 2.26 MB | `0c2e94215f7aa166ed727211b71da89f` | — | Forge hero shot skatev2_before_player_side.png | — | ref-shot |
| `v3build/tests/combat_fx_hue.py` | py | 2.4 KB | `bf32fa45a8ef2536ff5c27df15815de3` | — | combat_fx_hue.py | — | live |
| `v3build/tests/combat_fx_kick.py` | py | 3.7 KB | `f38397506b1f8f15df1e489094cd22dd` | — | combat_fx_kick.py | — | live |
| `v3build/tests/combat_fx_shots.py` | py | 3.1 KB | `fbab99e49b2bc6e2c343c9a8d90a7537` | — | combat_fx_shots.py | — | live |
| `v3build/wardrobe_build/assemble_rider.py` | py | 10.7 KB | `e7f575fe9083b5703a54302fb17c779f` | — | Tool/source assemble_rider.py | — | tool |
| `v3build/wardrobe_build/assemble_rider_v6pre.py` | py | 10.7 KB | `e67ca1f826c9f6f676713575bdd59984` | — | Tool/source assemble_rider_v6pre.py | — | tool |
| `v3build/wardrobe_build/build_wardrobe.py` | py | 52.9 KB | `de89d407674543deb690f5002778a5b5` | — | Tool/source build_wardrobe.py | — | tool |
| `v3build/wardrobe_build/build_wardrobe_v1.py` | py | 18.6 KB | `7b429143de025b51817556100413e6b6` | — | Tool/source build_wardrobe_v1.py | — | tool |
| `v3build/wardrobe_build/build_wardrobe_v2.py` | py | 28.6 KB | `f408d87357cf3d5c6dd2bcd38dea9305` | — | Tool/source build_wardrobe_v2.py | — | tool |
| `v3build/wardrobe_build/build_wardrobe_v3pre.py` | py | 31.6 KB | `9a970b7c9927f1f0d237d6aafb0916d8` | — | Tool/source build_wardrobe_v3pre.py | — | tool |
| `v3build/wardrobe_build/build_wardrobe_v4pre.py` | py | 34.4 KB | `7179e37440da7e200a4780abc8514f43` | — | Tool/source build_wardrobe_v4pre.py | — | tool |
| `v3build/wardrobe_build/build_wardrobe_v5pre.py` | py | 36.8 KB | `233d3b24955ebbd274d25a9eaf2c77de` | — | Tool/source build_wardrobe_v5pre.py | — | tool |
| `v3build/wardrobe_build/build_wardrobe_v6pre.py` | py | 38.8 KB | `37fdf8310c5863a505969a120026549d` | — | Tool/source build_wardrobe_v6pre.py | — | tool |
| `v3build/wardrobe_build/build_wardrobe_v7pre.py` | py | 45.3 KB | `74d537dbbe8ad7796002c9884a4f771c` | — | Tool/source build_wardrobe_v7pre.py | — | tool |
| `v3build/wardrobe_build/look.py` | py | 1.3 KB | `449256a87f81db2f2455daf54d4062e6` | — | Tool/source look.py | — | tool |
| `v3build/wardrobe_build/make_logo.py` | py | 1.4 KB | `b107e0501e939d22d1912e02f8066b94` | — | Tool/source make_logo.py | — | tool |
| `v3build/wardrobe_build/measure.py` | py | 2.2 KB | `4d9a9071f2d195c1b3fb3f14b5e1e03a` | — | Tool/source measure.py | — | tool |
| `v3build/wardrobe_build/prev.py` | py | 2.0 KB | `290653c120d75ede82076c14ff47422d` | — | Tool/source prev.py | — | tool |
| `v3build/wardrobe_build/sleeve_check.py` | py | 1.3 KB | `f444b01741de8fe6207b6b7fdf6d2269` | — | Tool/source sleeve_check.py | — | tool |
| `v3build/wardrobe_js/wardrobe.js` | js | 5.3 KB | `3593fa562c2cf0d421c1edba8fdb598c` | — | Wardrobe catalog: slots, presets (caali/ikki), WARDROBE_RIDERS URL map (Caali G / Akito local), equip()/apply(), tier pick. | THREE GLTFLoader + DRACO, CHAR_BASE wardrobe/* and riders GLBs | live |
| `v3build/wardrobe_js/wardrobe_v6pre.js` | js | 4.5 KB | `87bdeefa366a23ce3d885f92d723215e` | — | Pre-v6 wardrobe snapshot kept for reference/rollback. | — | WIP/archive |

## Local-only (Akito / Agito) — NOT in this repo

Per DEMO_STATUS RULES and Ani (2026-11-05): Akito stays out of public PRs/deploys until renamed. Listed here with **box paths** only.

| Box path | Reason |
|----------|--------|
| `/workspace/forge_kit/akito_sj/ao_build.py` | akito-privacy |
| `/workspace/forge_kit/akito_sj/geo_new.py` | akito-privacy |
| `/workspace/forge_kit/akito_sj/paint_new.py` | akito-privacy |
| `/workspace/forge_kit/akito_sj/raster.py` | akito-privacy |
| `/workspace/forge_kit/akito_sj/sj_build.py` | akito-privacy |
| `/workspace/forge_kit/akito_sj/sj_build.v1.py` | akito-privacy |
| `/workspace/rigwork/akito/akito-dark2-npc.dec.glb` | akito-privacy (dark2 local-only) |
| `/workspace/rigwork/akito/akito-dark2-npc.quest-ktx2.dec.glb` | akito-privacy (dark2 local-only) |
| `/workspace/rigwork/akito/akito-dark2-npc.quest.dec.glb` | akito-privacy (dark2 local-only) |
| `/workspace/rigwork/akito/akito-dark2-rider.dec.glb` | akito-privacy (dark2 local-only) |
| `/workspace/rigwork/akito/akito-dark2-rider.dec.test.glb` | akito-privacy (dark2 local-only) |
| `/workspace/rigwork/akito/akito-dark2-rider.quest-ktx2.dec.glb` | akito-privacy (dark2 local-only) |
| `/workspace/rigwork/akito/akito-dark2-rider.quest.dec.glb` | akito-privacy (dark2 local-only) |
| `/workspace/skyrydahs-characters/akito/akito-dark-npc.glb` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/akito-dark-npc.s4-ktx2.glb` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/akito-dark-npc.s4.glb` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/akito-dark-rider.glb` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/akito-dark-rider.s4-ktx2.glb` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/akito-dark-rider.s4.glb` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/akito-dark2-npc.glb` | akito-privacy (dark2 local-only) |
| `/workspace/skyrydahs-characters/akito/akito-dark2-npc.glb.bak-pre-fixv2` | akito-privacy (dark2 local-only) |
| `/workspace/skyrydahs-characters/akito/akito-dark2-npc.prerig-20261105-1245.glb` | akito-privacy (dark2 local-only) |
| `/workspace/skyrydahs-characters/akito/akito-dark2-npc.quest-ktx2.glb` | akito-privacy (dark2 local-only) |
| `/workspace/skyrydahs-characters/akito/akito-dark2-npc.quest-ktx2.glb.bak-cuff-20261105-152226` | akito-privacy (dark2 local-only) |
| `/workspace/skyrydahs-characters/akito/akito-dark2-npc.quest-ktx2.prerig-20261105-1245.glb` | akito-privacy (dark2 local-only) |
| `/workspace/skyrydahs-characters/akito/akito-dark2-npc.quest.glb` | akito-privacy (dark2 local-only) |
| `/workspace/skyrydahs-characters/akito/akito-dark2-npc.quest.glb.bak-cuff-20261105-152226` | akito-privacy (dark2 local-only) |
| `/workspace/skyrydahs-characters/akito/akito-dark2-npc.quest.prerig-20261105-1245.glb` | akito-privacy (dark2 local-only) |
| `/workspace/skyrydahs-characters/akito/akito-dark2-rider.glb` | akito-privacy (dark2 local-only) |
| `/workspace/skyrydahs-characters/akito/akito-dark2-rider.glb.bak-pre-fixv2` | akito-privacy (dark2 local-only) |
| `/workspace/skyrydahs-characters/akito/akito-dark2-rider.prerig-20261105-1245.glb` | akito-privacy (dark2 local-only) |
| `/workspace/skyrydahs-characters/akito/akito-dark2-rider.quest-ktx2.glb` | akito-privacy (dark2 local-only) |
| `/workspace/skyrydahs-characters/akito/akito-dark2-rider.quest-ktx2.glb.bak-cuff-20261105-152226` | akito-privacy (dark2 local-only) |
| `/workspace/skyrydahs-characters/akito/akito-dark2-rider.quest-ktx2.prerig-20261105-1245.glb` | akito-privacy (dark2 local-only) |
| `/workspace/skyrydahs-characters/akito/akito-dark2-rider.quest.glb` | akito-privacy (dark2 local-only) |
| `/workspace/skyrydahs-characters/akito/akito-dark2-rider.quest.glb.bak-cuff-20261105-152226` | akito-privacy (dark2 local-only) |
| `/workspace/skyrydahs-characters/akito/akito-dark2-rider.quest.prerig-20261105-1245.glb` | akito-privacy (dark2 local-only) |
| `/workspace/skyrydahs-characters/akito/akito-npc.bak-forge-preskate-20261030.glb` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/akito-npc.glb` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/akito-npc.glb.bak-0500-202610290527` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/akito-npc.s4-ktx2.bakedskate-20261030-1026.glb` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/akito-npc.s4-ktx2.glb` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/akito-npc.s4.bakedskate-20261030-1026.glb` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/akito-npc.s4.glb` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/akito-rider.bak-forge-preskate-20261030.glb` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/akito-rider.glb` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/akito-rider.glb.bak-0500-202610290527` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/akito-rider.s4-ktx2.bakedskate-20261030-1026.glb` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/akito-rider.s4-ktx2.glb` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/akito-rider.s4.bakedskate-20261030-1026.glb` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/akito-rider.s4.glb` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/akito-springs.md` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/akito-straitjacket-npc.bak-forge-v1-20261030.glb` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/akito-straitjacket-npc.glb` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/akito-straitjacket-npc.prestrapspring-20261030-2115.glb` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/akito-straitjacket-npc.s4-ktx2.glb` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/akito-straitjacket-npc.s4.glb` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/akito-straitjacket-rider.bak-forge-v1-20261030.glb` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/akito-straitjacket-rider.glb` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/akito-straitjacket-rider.prestrapspring-20261030-2115.glb` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/akito-straitjacket-rider.s4-ktx2.glb` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/akito-straitjacket-rider.s4.glb` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/akito-straps-rig-report.json` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/src/akito-npc-raw.glb` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/src/akito-rider-raw.glb` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/src/akito_atlas_c.png` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/src/akito_atlas_c_eyes.png` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/src/akito_atlas_mr.png` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/src/build_akito.py` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/src/build_akito_v2pre.py` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/src/build_akito_v3b.py` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/src/dump_islands.py` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/src/img0_normal.png` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/src/img1_texture_0.png` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/src/img2_texture_0_metallic_roughness.png` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/src/render3pt.py` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/src/renders/akito_body_front_3pt.png` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/src/renders/akito_face_34_3pt.png` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/src/renders/akito_face_blender.png` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/src/renders/akito_face_front_3pt.png` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/src/renders/akito_review_sheet_3pt.png` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/src/repair_tex.py` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/src/repair_tex_v3pre.py` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/src/v2/akito_atlas_c.png` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/src/v2/akito_atlas_mr.png` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/src/v2/hair_mask_1k.png` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/src/v2/img0_normal.png` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/src/v2/img1_texture_0.png` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/src/v2/img2_texture_0_metallic_roughness.png` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/src/v2/islands.npz` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/src/v2/tex_fixed_4k.png` | akito-privacy |
| `/workspace/skyrydahs-characters/akito/src/v2/tex_tinted_4k.png` | akito-privacy |
| `/workspace/skyrydahs-ref/akito/akito-details.md` | akito-privacy |
| `/workspace/skyrydahs-ref/akito/akito-ref.jpg` | akito-privacy |
| `/workspace/skyrydahs-ref/akito/akito-straitjacket-refs.md` | akito-privacy |
| `/workspace/skyrydahs-ref/akito/refs-2026-10-30/README.md` | akito-privacy |
| `/workspace/skyrydahs-ref/akito/refs-2026-10-30/ref1.jpg` | akito-privacy |
| `/workspace/skyrydahs-ref/akito/refs-2026-10-30/ref2.jpg` | akito-privacy |
| `/workspace/skyrydahs-ref/akito/refs-2026-10-30/ref3.jpg` | akito-privacy |
| `/workspace/skyrydahs-ref/akito/refs-2026-10-30/ref4.jpg` | akito-privacy |
| `/workspace/skyrydahs-ref/akito/refs-2026-10-30/ref5.jpg` | akito-privacy |
| `/workspace/skyrydahs-ref/akito/refs-2026-10-30/ref6.jpg` | akito-privacy |
| `/workspace/skyrydahs-ref/akito/refs-2026-10-30/ref7.jpg` | akito-privacy |
| `/workspace/skyrydahs-ref/akito/refs-2026-10-30/ref8.jpg` | akito-privacy |
| `/workspace/v3build/shots/hero/akito_dark_34.png` | akito-privacy |
| `/workspace/v3build/shots/hero/akito_dark_back.png` | akito-privacy |
| `/workspace/v3build/shots/hero/akito_dark_front.png` | akito-privacy |
| `/workspace/v3build/shots/hero/akito_straitjacket_34.bak-forge-v1.png` | akito-privacy |
| `/workspace/v3build/shots/hero/akito_straitjacket_34.png` | akito-privacy |
| `/workspace/v3build/shots/hero/akito_straitjacket_back.bak-forge-v1.png` | akito-privacy |
| `/workspace/v3build/shots/hero/akito_straitjacket_back.png` | akito-privacy |
| `/workspace/v3build/shots/hero/akito_straitjacket_front.bak-forge-v1.png` | akito-privacy |
| `/workspace/v3build/shots/hero/akito_straitjacket_front.png` | akito-privacy |
| `/workspace/v3build/shots/hero/akito_v2skate_34.png` | akito-privacy |
| `/workspace/v3build/shots/hero/akito_v2skate_front.png` | akito-privacy |

Total local-only paths recorded: **115**.

Also local-only (not enumerated file-by-file if already covered): `/workspace/forge_kit/akito_sj/`, `/workspace/skyrydahs-ref/akito/`, `/workspace/skyrydahs-characters/akito/`, `/workspace/v3build/shots/hero/akito_*`, `/workspace/rigwork/akito/`, `/workspace/shots/akito/`.

## Could not / did not include

- All `*.blend` sources **≥ 50 MB** (e.g. `forge_kit/gr8/anika_hi.blend`, `caali_hi.blend`, `anika_lods.blend`, `caali_lods.blend`, `skyrydahs-characters/anika/src/anika_lods.blend`, `wardrobe_build/forge-caali-v2/caali_lods.blend`). Under-50 MB blends that are real sources were included.
- Backup/intermediate GLBs and PNGs matching bak/prespring/prerebind/v2raw/presym/prefix/static/nrm768.
- Non-Forge hero shots under `v3build/shots/hero/` (Palma/Optimizer/Systems world A/B plates). Forge-authored finals included: `combat_fx_*`, `skate_v2*`, `skatev2_*`, `anika_*`, `caali_v2_*`, `build_AI*_anika/caali`.
- Order named `forgerider.py`; on disk the tool is `forge_kit/gr8/fix/fixrider.py` (included).
- `patch_rider_style.py` / `rider_style.js` are packaged and **official gate PASS** (opt-in `?riderstyle=opt3`). Hook for `build_ikki.sh`: after `patch_pbr_base.py`, before `patch_xr_fxmem.py` (Ani wiring into the next rebuild; default look unchanged).
- Simca `meshy/` raw Meshy export and `*.bak*` / `*.prerig-*` backups were left out (current rigged rider/npc × base/quest/quest-ktx2 only).
- Akito dark2 (`akito-dark2-*.glb` and related) is **local-only**; paths are listed in § Local-only and are not in this public repo.
