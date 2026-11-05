# Palma Builder handover: world / environment (Sky Rydahs WebXR, Three.js r128)

For the Unity flagship conversion. Owner: Palma Builder (world/environment bot). Packaged 2026-11-05.
Layout: `code/` (runtime JS + build patches), `tools/` (asset generators, shot and measure scripts), `assets/`, `data/` (exported world JSON), `ref/` (research), `shots/hero/`.

## How the build works
The game is one HTML file. `build_ikki.sh` runs `patch_*.py` scripts in a fixed order; each injects one JS module into the HTML. "Chain #N" below means position N in that order (1 = patch_ikki.py). Ours: #9 facades, #10 bridges, #11 sky, #12 blockout, #13 ground, #24 crewhouse_kit, #25 world_perf, #26 pbr_world, #27 pbr_base. Systems' ride_ground (#14) consumes our WORLD_GROUND right after #13.
Flags are URL query params. `?seed=` drives the world rnd (shipping seed = 1). `?tier=` (low/hd) is read by world_perf. `?ktx2=1` switches to the KTX2 textures (gate owned by Rydah Optimizer, patch_draco). `?pbr=0`/`?toon=1` brings back the old toon look. `?pbrbase=1` turns on the building-base band. `?oldsigns=1` and `?sea=1` are debug switches in world_perf.
Status: **shipped default** = on in the build. **opt-in** = in the chain but behind a default-off flag. **WIP** = outside the chain.

## Inventory (every file)
| path | size | purpose | chain | runtime globals | URL flags | deps | status |
|---|---|---|---|---|---|---|---|
| `assets/kit/Concrete034_Color.jpg` | 28 KB | Crew garage kit textures (crewhouse_kit.js); kit_logos.png = crew logo atlas | - | - | - | - | asset |
| `assets/kit/Concrete034_NormalGL.jpg` | 42 KB | Crew garage kit textures (crewhouse_kit.js); kit_logos.png = crew logo atlas | - | - | - | - | asset |
| `assets/kit/Concrete034_Roughness.jpg` | 29 KB | Crew garage kit textures (crewhouse_kit.js); kit_logos.png = crew logo atlas | - | - | - | - | asset |
| `assets/kit/Concrete046_Color.jpg` | 38 KB | Crew garage kit textures (crewhouse_kit.js); kit_logos.png = crew logo atlas | - | - | - | - | asset |
| `assets/kit/Concrete046_NormalGL.jpg` | 6 KB | Crew garage kit textures (crewhouse_kit.js); kit_logos.png = crew logo atlas | - | - | - | - | asset |
| `assets/kit/Concrete046_Roughness.jpg` | 41 KB | Crew garage kit textures (crewhouse_kit.js); kit_logos.png = crew logo atlas | - | - | - | - | asset |
| `assets/kit/PaintedMetal004_Color.jpg` | 60 KB | Crew garage kit textures (crewhouse_kit.js); kit_logos.png = crew logo atlas | - | - | - | - | asset |
| `assets/kit/PaintedMetal004_NormalGL.jpg` | 19 KB | Crew garage kit textures (crewhouse_kit.js); kit_logos.png = crew logo atlas | - | - | - | - | asset |
| `assets/kit/PaintedMetal004_Roughness.jpg` | 45 KB | Crew garage kit textures (crewhouse_kit.js); kit_logos.png = crew logo atlas | - | - | - | - | asset |
| `assets/kit/kit_logos.png` | 628 KB | Crew garage kit textures (crewhouse_kit.js); kit_logos.png = crew logo atlas | - | - | - | - | asset |
| `assets/pbr/env_portside_day.png` | 143 KB | Equirect env map for PBR reflections (pbr_env_bake.py) | - | - | - | - | asset |
| `assets/pbr/env_portside_night.png` | 136 KB | Equirect env map for PBR reflections (pbr_env_bake.py) | - | - | - | - | asset |
| `assets/pbr/pbrF_albedo.jpg` | 539 KB | PBR world atlas (pbr_world.js); F=facade, G=ground; _orm = R AO, G rough, B metal | - | - | - | - | asset |
| `assets/pbr/pbrF_albedo.ktx2` | 371 KB | PBR world atlas (pbr_world.js); F=facade, G=ground; _orm = R AO, G rough, B metal | - | - | - | - | asset |
| `assets/pbr/pbrF_nrm.jpg` | 1.1 MB | PBR world atlas (pbr_world.js); F=facade, G=ground; _orm = R AO, G rough, B metal | - | - | - | - | asset |
| `assets/pbr/pbrF_nrm.ktx2` | 580 KB | PBR world atlas (pbr_world.js); F=facade, G=ground; _orm = R AO, G rough, B metal | - | - | - | - | asset |
| `assets/pbr/pbrF_orm.jpg` | 372 KB | PBR world atlas (pbr_world.js); F=facade, G=ground; _orm = R AO, G rough, B metal | - | - | - | - | asset |
| `assets/pbr/pbrG_albedo.jpg` | 1.2 MB | PBR world atlas (pbr_world.js); F=facade, G=ground; _orm = R AO, G rough, B metal | - | - | - | - | asset |
| `assets/pbr/pbrG_albedo.ktx2` | 710 KB | PBR world atlas (pbr_world.js); F=facade, G=ground; _orm = R AO, G rough, B metal | - | - | - | - | asset |
| `assets/pbr/pbrG_nrm.jpg` | 1.6 MB | PBR world atlas (pbr_world.js); F=facade, G=ground; _orm = R AO, G rough, B metal | - | - | - | - | asset |
| `assets/pbr/pbrG_nrm.ktx2` | 1.2 MB | PBR world atlas (pbr_world.js); F=facade, G=ground; _orm = R AO, G rough, B metal | - | - | - | - | asset |
| `assets/pbr/pbrG_orm.jpg` | 992 KB | PBR world atlas (pbr_world.js); F=facade, G=ground; _orm = R AO, G rough, B metal | - | - | - | - | asset |
| `assets/pbr/pbrG_orm.ktx2` | 175 KB | PBR world atlas (pbr_world.js); F=facade, G=ground; _orm = R AO, G rough, B metal | - | - | - | - | asset |
| `assets/pbr_base/SOURCES.txt` | 1 KB | Building-base PBR atlas (pbr_base.js) | - | - | - | - | asset |
| `assets/pbr_base/pbrB_albedo.jpg` | 959 KB | Building-base PBR atlas (pbr_base.js) | - | - | - | - | asset |
| `assets/pbr_base/pbrB_albedo.ktx2` | 686 KB | Building-base PBR atlas (pbr_base.js) | - | - | - | - | asset |
| `assets/pbr_base/pbrB_nrm.jpg` | 191 KB | Building-base PBR atlas (pbr_base.js) | - | - | - | - | asset |
| `assets/pbr_base/pbrB_nrm.ktx2` | 931 KB | Building-base PBR atlas (pbr_base.js) | - | - | - | - | asset |
| `assets/pbr_base/pbrB_orm.jpg` | 203 KB | Building-base PBR atlas (pbr_base.js) | - | - | - | - | asset |
| `assets/pbr_base/pbrB_orm.ktx2` | 137 KB | Building-base PBR atlas (pbr_base.js) | - | - | - | - | asset |
| `assets/props_kit/garage_props_sheet.png` | 574 KB | Forge kit props manifest / sheet (GLBs owned by Rydah Forge, already in repo at v3/props/kit/) | - | - | - | - | asset |
| `assets/props_kit/manifest.json` | 0 KB | Forge kit props manifest / sheet (GLBs owned by Rydah Forge, already in repo at v3/props/kit/) | - | - | - | - | asset |
| `assets/textures/facade_albedo.jpg` | 287 KB | Facade atlas source, base64-embedded by patch_facades.py | - | - | - | - | asset |
| `assets/textures/facade_nr.jpg` | 293 KB | Facade atlas source, base64-embedded by patch_facades.py | - | - | - | - | asset |
| `assets/world_ktx2/Concrete034_Color.ktx2` | 52 KB | KTX2 (produced by Rydah Optimizer) used by facades.js/crewhouse_kit.js under ?ktx2=1 | - | - | - | - | asset |
| `assets/world_ktx2/Concrete034_NormalGL.ktx2` | 290 KB | KTX2 (produced by Rydah Optimizer) used by facades.js/crewhouse_kit.js under ?ktx2=1 | - | - | - | - | asset |
| `assets/world_ktx2/Concrete034_Roughness.ktx2` | 50 KB | KTX2 (produced by Rydah Optimizer) used by facades.js/crewhouse_kit.js under ?ktx2=1 | - | - | - | - | asset |
| `assets/world_ktx2/Concrete046_Color.ktx2` | 61 KB | KTX2 (produced by Rydah Optimizer) used by facades.js/crewhouse_kit.js under ?ktx2=1 | - | - | - | - | asset |
| `assets/world_ktx2/Concrete046_NormalGL.ktx2` | 44 KB | KTX2 (produced by Rydah Optimizer) used by facades.js/crewhouse_kit.js under ?ktx2=1 | - | - | - | - | asset |
| `assets/world_ktx2/Concrete046_Roughness.ktx2` | 60 KB | KTX2 (produced by Rydah Optimizer) used by facades.js/crewhouse_kit.js under ?ktx2=1 | - | - | - | - | asset |
| `assets/world_ktx2/PaintedMetal004_Color.ktx2` | 63 KB | KTX2 (produced by Rydah Optimizer) used by facades.js/crewhouse_kit.js under ?ktx2=1 | - | - | - | - | asset |
| `assets/world_ktx2/PaintedMetal004_NormalGL.ktx2` | 191 KB | KTX2 (produced by Rydah Optimizer) used by facades.js/crewhouse_kit.js under ?ktx2=1 | - | - | - | - | asset |
| `assets/world_ktx2/PaintedMetal004_Roughness.ktx2` | 59 KB | KTX2 (produced by Rydah Optimizer) used by facades.js/crewhouse_kit.js under ?ktx2=1 | - | - | - | - | asset |
| `assets/world_ktx2/facade_albedo.ktx2` | 339 KB | KTX2 (produced by Rydah Optimizer) used by facades.js/crewhouse_kit.js under ?ktx2=1 | - | - | - | - | asset |
| `assets/world_ktx2/facade_nr.ktx2` | 1.7 MB | KTX2 (produced by Rydah Optimizer) used by facades.js/crewhouse_kit.js under ?ktx2=1 | - | - | - | - | asset |
| `code/blockout.js` | 46 KB | Realism step 1 grey-box: towers/precinct lots, Dash road, ring paths, East Blocks wall-ride panels, wall-kick faces + route solver. | #12 patch_blockout.py | const BLOCKOUT; window.WALL_PANELS, WALL_KICKS, KICK_ROUTES, KICK_UNREACHABLE, KICK_BRIDGE, BLOCKOUT_LIVE | ?seed (slots), &uj= (debug) | world.js PALMA, colliders | shipped default |
| `code/bridges.js` | 7 KB | Full-structure bridges (segmental box, multi-beam bents, cable-stayed, suspension) refs bridges-research.md. Additive to createBridge(). | #10 patch_bridges.py | const BRIDGES | - | world.js createBridge | shipped default |
| `code/crewhouse_kit.js` | 89 KB | One shared parameterised crew garage interior: upstairs = Kogarasumaru pod loft, downstairs = A-T tuning bay; per-crew theme via crews.js colours + logo atlas; lazy build, 14 m player gate. | #24 patch_crewhouse_kit.py | window.KIT, KIT_READY, KIT_FLOOR, KIT_GROUND, KIT_LANE, KIT_POD_FOOT, KOG_GROUND, KOG_THEME, SR_DRACO; const KIT_LOGO_SLOT, KIT_PODS, KIT_PROP_FIT | ?ktx2=1, &mode= | assets/kit, assets/world_ktx2, props/kit GLBs (Forge), crews.js | shipped default |
| `code/facades.js` | 3 KB | Building facade material: 8 CC0 materials in one 2048x1024 albedo atlas + normal/roughness atlas, world-space box UVs on the single instanced building shader. | #9 patch_facades.py | const FACADE (uniforms.uDay) | ?ktx2=1 (assets/world_ktx2/facade_*.ktx2) | textures/facade_*.jpg (base64-embedded by patch), SR_KTX2 (Optimizer) | shipped default |
| `code/ground.js` | 5 KB | WORLD_GROUND 1.0: analytic height/surface lookup (8 m spatial hash), contract with Rydah Systems ride_ground.js. | #13 patch_ground.py | window.WORLD_GROUND(x,z,yHint)->{y,nx,ny,nz,surf}|null; .at .heightAt .surfAt .decks .entries | - | world/bridges/blockout geometry | shipped default |
| `code/patch_blockout.py` | 1 KB | Injects blockout.js. | #12 | - | - | blockout.js | shipped default |
| `code/patch_bridges.py` | 1 KB | Injects bridges.js. | #10 | - | - | bridges.js | shipped default |
| `code/patch_crewhouse_kit.py` | 6 KB | Injects crewhouse_kit.js. | #24 | - | - | crewhouse_kit.js | shipped default |
| `code/patch_facades.py` | 5 KB | Injects facades.js; embeds textures/facade_{albedo,nr}.jpg as data URIs. | #9 | - | - | facades.js | shipped default |
| `code/patch_ground.py` | 1 KB | Injects ground.js. | #13 | - | - | ground.js | shipped default |
| `code/patch_pbr_base.py` | 1 KB | Injects pbr_base.js after pbr_world, before LOOP. Ani approved slot. | #27 | - | - | pbr_base.js | shipped opt-in |
| `code/patch_pbr_world.py` | 1 KB | Injects pbr_world.js. | #26 | - | - | pbr_world.js | shipped default |
| `code/patch_sky.py` | 1 KB | Injects sky.js. | #11 | - | - | sky.js | shipped default |
| `code/patch_world_perf.py` | 2 KB | Injects world_perf.js. | #25 | - | - | world_perf.js | shipped default |
| `code/pbr_base.js` | 10 KB | PBR building-base band 0..~5 m: brick/concrete per kit, steel I-beams+lintels, framed storefronts (env glass + night interiors), kick plate, grime/AO. Shader-only 0 new draws. Contrast+distance-AA fix 11/05 so band reads at 15–40 m. | #27 patch_pbr_base.py (after #26 pbr_world) | const PBR_BASE | ?pbrbase=1 (opt-in until Ani/Oliver), ?toon=1/?pbr=0 no-op | pbr_world.js, assets/pbr_base | opt-in ready |
| `code/pbr_base_wip.glsl` | 5 KB | Building-base GLSL chunk for the WIP. | not in chain | - | - | - | WIP |
| `code/pbr_base_wip.js` | 30 KB | WIP fork of pbr_world.js with building-base shader work. NOT in chain. | not in chain | PBR_WORLD (would replace) | ?pbr, ?toon, ?ktx2 | pbr_base_wip.glsl | WIP |
| `code/pbr_base_wip_inject.py` | 2 KB | Test-copy injector for pbr_base_wip.js. | not in chain (copy builds only) | - | - | pbr_base_wip.js | WIP |
| `code/pbr_world.js` | 22 KB | Step-5 PBR world: converts ground/building materials to PBR (albedo/normal/ORM, env map, wet). DEFAULT ON since 10/30 20:11; ?toon=1 or ?pbr=0 = old toon look. Day bloom threshold/strength + pbrDay high-pass removed 10/31 (Optimizer /*FXBLOOM*/ owns bloom). Exports: ENV.day/night/cube/cur, GR.exp/fog, tick/convert/boot/install. | #26 patch_pbr_world.py | const/window.PBR_WORLD | ?toon=1, ?pbr=0/1, ?ktx2=1 | assets/pbr (+env_portside_day/night.png); FX (Optimizer FXBLOOM) | shipped default (build_ikki comment still says opt-in; header is authoritative) |
| `code/sky.js` | 1 KB | Sky dome follows day/night state live, 0 extra draws. | #11 patch_sky.py | const SKY (SKY.day) | - | scene.background, FACADE.uniforms.uDay | shipped default |
| `code/world.js` | 31 KB | Palma City base world (islands, districts, bridges, 8 garages, colliders[], rails). ORIGINAL SOURCE (pre-workshop); the base our patches layer on. Not modified by us. | core (in base html, before all patches) | const PALMA, colliders, miniRects, rails, checkpoints, cans, tagSpots, animated, districtAt() | ?seed (world rnd) | THREE r128 | original source |
| `code/world_perf.js` | 39 KB | Runtime draw-call pass after staticMerge: base-interior distance cull, asphalt merge, 270 m tile re-merge, sign atlas, cans. | #25 patch_world_perf.py | const WORLD_PERF (.SIGN); window.CANS_HIDE, CANS_SYNC | ?tier=, ?oldsigns=1, ?sea=1 | staticMerge, asphalt.js | shipped default |
| `data/KICK_BRIDGE.json` | 5 KB | Exported world data (dump_world_json.py, seed 1) | - | - | - | - | - |
| `data/KICK_ROUTES.json` | 9 KB | Exported world data (dump_world_json.py, seed 1) | - | - | - | - | - |
| `data/KICK_UNREACHABLE.json` | 0 KB | Exported world data (dump_world_json.py, seed 1) | - | - | - | - | - |
| `data/WALL_KICKS.json` | 8 KB | Exported world data (dump_world_json.py, seed 1) | - | - | - | - | - |
| `data/WALL_PANELS.json` | 64 KB | Exported world data (dump_world_json.py, seed 1) | - | - | - | - | - |
| `data/colliders.json` | 82 KB | Exported world data (dump_world_json.py, seed 1) | - | - | - | - | - |
| `data/ground.json` | 506 KB | Exported world data (dump_world_json.py, seed 1) | - | - | - | - | - |
| `data/palma.json` | 2 KB | Exported world data (dump_world_json.py, seed 1) | - | - | - | - | - |
| `ref/bldgbase-notes.md` | 6 KB | Research/design reference | - | - | - | - | - |
| `ref/blockout-research.md` | 3 KB | Research/design reference | - | - | - | - | - |
| `ref/bridges-research.md` | 5 KB | Research/design reference | - | - | - | - | - |
| `ref/dash-road-profile-proposal.md` | 3 KB | Research/design reference | - | - | - | - | - |
| `ref/step5-bake-plan.md` | 18 KB | Research/design reference | - | - | - | - | - |
| `ref/step5-blowout-notes.md` | 4 KB | Step-5 blowout + day-bloom removal verify notes | - | - | - | - | - |
| `ref/step5-texture-atlas-plan.md` | 15 KB | Research/design reference | - | - | - | - | - |
| `ref/bridges/SOURCES.txt` | 2 KB | Research/design reference | - | - | - | - | - |
| `ref/bridges/cochrane_africatown_pd.jpg` | 245 KB | Research/design reference | - | - | - | - | - |
| `ref/bridges/dames_point_pd.jpg` | 225 KB | Research/design reference | - | - | - | - | - |
| `ref/bridges/golden_gate_cable_haer_pd.jpg` | 141 KB | Research/design reference | - | - | - | - | - |
| `ref/bridges/golden_gate_cable_suspender_haer_pd.jpg` | 251 KB | Research/design reference | - | - | - | - | - |
| `ref/bridges/hathaway_1929_postcard_pd.jpg` | 396 KB | Research/design reference | - | - | - | - | - |
| `ref/bridges/hathaway_west_cc0.jpg` | 127 KB | Research/design reference | - | - | - | - | - |
| `ref/bridges/sunshine_skyway_pd.jpg` | 35 KB | Research/design reference | - | - | - | - | - |
| `ref/crew-houses/kogarasumaru-downstairs-inspo.webp` | 885 KB | Research/design reference | - | - | - | - | - |
| `ref/crew-houses/kogarasumaru-upstairs-ref.webp` | 714 KB | Research/design reference | - | - | - | - | - |
| `ref/pbr/SOURCES.txt` | 2 KB | Research/design reference | - | - | - | - | - |
| `shots/hero/bldgbase_close_day_after.png` | 3.8 MB | Hero shot (screenshot standard) | - | - | - | - | - |
| `shots/hero/bldgbase_close_day_before.png` | 3.8 MB | Hero shot (screenshot standard) | - | - | - | - | - |
| `shots/hero/bldgbase_close_night_after.png` | 3.4 MB | Hero shot (screenshot standard) | - | - | - | - | - |
| `shots/hero/bldgbase_close_night_before.png` | 3.5 MB | Hero shot (screenshot standard) | - | - | - | - | - |
| `shots/hero/bldgbase_street_day_after.png` | 3.6 MB | Hero shot (screenshot standard) | - | - | - | - | - |
| `shots/hero/bldgbase_street_day_before.png` | 3.6 MB | Hero shot (screenshot standard) | - | - | - | - | - |
| `shots/hero/bldgbase_street_night_after.png` | 3.3 MB | Hero shot (screenshot standard) | - | - | - | - | - |
| `shots/hero/bldgbase_street_night_before.png` | 3.3 MB | Hero shot (screenshot standard) | - | - | - | - | - |
| `shots/hero/crew_garages_contact_sheet_downscaled.jpg` | 1.1 MB | Hero shot (screenshot standard) | - | - | - | - | - |
| `shots/hero/crew_garages_upstairs_contact_sheet.png` | 24.2 MB | Hero shot (screenshot standard) | - | - | - | - | - |
| `shots/hero/fxbloom_pbr_causeway_day_side_by_side.png` | 7.3 MB | Hero shot (screenshot standard) | - | - | - | - | - |
| `shots/hero/fxbloom_pbr_causeway_night_side_by_side.png` | 5.1 MB | Hero shot (screenshot standard) | - | - | - | - | - |
| `shots/hero/fxbloom_pbr_street_day_side_by_side.png` | 6.3 MB | Hero shot (screenshot standard) | - | - | - | - | - |
| `shots/hero/fxbloom_pbr_street_night_side_by_side.png` | 5.4 MB | Hero shot (screenshot standard) | - | - | - | - | - |
| `shots/hero/fxbloom_toon_causeway_day_side_by_side.png` | 3.9 MB | Hero shot (screenshot standard) | - | - | - | - | - |
| `shots/hero/fxbloom_toon_causeway_night_side_by_side.png` | 3.4 MB | Hero shot (screenshot standard) | - | - | - | - | - |
| `shots/hero/fxbloom_toon_street_day_side_by_side.png` | 5.3 MB | Hero shot (screenshot standard) | - | - | - | - | - |
| `shots/hero/fxbloom_toon_street_night_side_by_side.png` | 4.6 MB | Hero shot (screenshot standard) | - | - | - | - | - |
| `shots/hero/hero_kog_downstairs_side_by_side_night.png` | 10.7 MB | Hero shot (screenshot standard) | - | - | - | - | - |
| `shots/hero/hero_kog_upstairs_side_by_side_night.png` | 8.0 MB | Hero shot (screenshot standard) | - | - | - | - | - |
| `shots/hero/kog_downstairs_side_by_side.png` | 10.7 MB | Hero shot (screenshot standard) | - | - | - | - | - |
| `shots/hero/kog_loft_wide.png` | 3.0 MB | Hero shot (screenshot standard) | - | - | - | - | - |
| `shots/hero/kog_upstairs_side_by_side.png` | 7.4 MB | Hero shot (screenshot standard) | - | - | - | - | - |
| `shots/hero/pbr_causeway_day_side_by_side.png` | 5.8 MB | Hero shot (screenshot standard) | - | - | - | - | - |
| `shots/hero/pbr_causeway_night_side_by_side.png` | 5.5 MB | Hero shot (screenshot standard) | - | - | - | - | - |
| `shots/hero/pbr_default_street_day.png` | 3.5 MB | Hero shot (screenshot standard) | - | - | - | - | - |
| `shots/hero/pbr_street_day_side_by_side.png` | 6.1 MB | Hero shot (screenshot standard) | - | - | - | - | - |
| `shots/hero/pbr_street_night_side_by_side.png` | 6.0 MB | Hero shot (screenshot standard) | - | - | - | - | - |
| `shots/hero/pbr_street_day_final.png` | 3.0 MB | PBR street day hero final (post day-bloom removal; 1920x1080 dsf1.5 tier=hd FX on seed=1) | - | - | - | - | - |
| `shots/hero/pbr_street_night_final.png` | 3.2 MB | PBR street night hero final (neon bloom intact) | - | - | - | - | - |
| `shots/hero/pbr_causeway_day_final.png` | 3.5 MB | PBR causeway day hero final | - | - | - | - | - |
| `shots/hero/pbr_causeway_night_final.png` | 3.6 MB | PBR causeway night hero final | - | - | - | - | - |
| `shots/hero/pbr_street_day_before_tweak.png` | 3.0 MB | Day street with bak-bloomtweak-0018 (pre-removal) for SBS | - | - | - | - | - |
| `shots/hero/pbr_street_day_before_after_side_by_side.png` | 3.6 MB | Day street before/after day-bloom tweak removal SBS | - | - | - | - | - |
| `shots/hero/bldgbase_final_street_day_after.png` | 3.0 MB | Building-base hero final (street day, ?pbrbase=1) | - | - | - | - | - |
| `shots/hero/bldgbase_final_street_day_before.png` | 3.0 MB | Building-base hero final (street day baseline) | - | - | - | - | - |
| `shots/hero/bldgbase_final_street_night_after.png` | 3.2 MB | Building-base hero final (street night, ?pbrbase=1) | - | - | - | - | - |
| `shots/hero/bldgbase_final_street_night_before.png` | 3.2 MB | Building-base hero final (street night baseline) | - | - | - | - | - |
| `shots/hero/bldgbase_final_close_day_after.png` | 3.9 MB | Building-base hero final (~15 m storefront day) | - | - | - | - | - |
| `shots/hero/bldgbase_final_close_day_before.png` | 3.2 MB | Building-base hero final (~15 m storefront day baseline) | - | - | - | - | - |
| `shots/hero/bldgbase_final_close_night_after.png` | 4.2 MB | Building-base hero final (~15 m storefront night, lit interiors) | - | - | - | - | - |
| `shots/hero/bldgbase_final_street_day_side_by_side.png` | 3.6 MB | Building-base day street before/after SBS | - | - | - | - | - |
| `shots/hero/bldgbase_final_street_night_side_by_side.png` | 3.9 MB | Building-base night street before/after SBS | - | - | - | - | - |
| `shots/hero/bldgbase_final_close_day_side_by_side.png` | 4.6 MB | Building-base close day before/after SBS | - | - | - | - | - |
| `shots/hero/spawn_view_day.png` | 626 KB | Hero shot (screenshot standard) | - | - | - | - | - |
| `shots/hero/spawn_view_night.png` | 614 KB | Hero shot (screenshot standard) | - | - | - | - | - |
| `tools/bldgbase_shots.py` | 3 KB | Playwright hero/before-after shot script (1920x1080 dsf1.5, tier hd, seed 1). | - | - | - | - | tool |
| `tools/bo_shots.py` | 2 KB | Playwright hero/before-after shot script (1920x1080 dsf1.5, tier hd, seed 1). | - | - | - | - | tool |
| `tools/bridges_shots.py` | 3 KB | Playwright hero/before-after shot script (1920x1080 dsf1.5, tier hd, seed 1). | - | - | - | - | tool |
| `tools/dcavg.py` | 3 KB | Draw-call / frame-time measurement (per-category draws, min/mean/max over runs). | - | - | - | - | tool |
| `tools/dcsplit.py` | 5 KB | Draw-call / frame-time measurement (per-category draws, min/mean/max over runs). | - | - | - | - | tool |
| `tools/dcsplit2.py` | 6 KB | Draw-call / frame-time measurement (per-category draws, min/mean/max over runs). | - | - | - | - | tool |
| `tools/demo_check.py` | 4 KB | Headless demo smoke check + screenshots. | - | - | - | - | tool |
| `tools/dump_world_json.py` | 2 KB | NEW: dumps colliders, PALMA, WALL_PANELS, WALL_KICKS, KICK_ROUTES, WORLD_GROUND grid to data/*.json from a build_copy.sh html. | - | - | - | - | tool |
| `tools/facades_shots.py` | 2 KB | Playwright hero/before-after shot script (1920x1080 dsf1.5, tier hd, seed 1). | - | - | - | - | tool |
| `tools/kit_shots.py` | 4 KB | Playwright hero/before-after shot script (1920x1080 dsf1.5, tier hd, seed 1). | - | - | - | - | tool |
| `tools/kit_shots_hd.py` | 4 KB | Playwright hero/before-after shot script (1920x1080 dsf1.5, tier hd, seed 1). | - | - | - | - | tool |
| `tools/pbr_base_atlas.py` | 2 KB | Builds assets/pbr_base atlas (pbrB_albedo/nrm/orm) from ambientCG sources. | - | - | - | - | tool |
| `tools/pbr_env_bake.py` | 2 KB | Bakes env_portside_day/night.png env maps. | - | - | - | - | tool |
| `tools/pbr_hero.py` | 3 KB | Playwright hero/before-after shot script (1920x1080 dsf1.5, tier hd, seed 1). | - | - | - | - | tool |
| `tools/perf_measure.py` | 7 KB | Draw-call / frame-time measurement (per-category draws, min/mean/max over runs). | - | - | - | - | tool |
| `tools/sign_shot.py` | 3 KB | Sign legibility shots (world_perf sign atlas vs ?oldsigns=1). | - | - | - | - | tool |
| `tools/sky_shots.py` | 2 KB | Playwright hero/before-after shot script (1920x1080 dsf1.5, tier hd, seed 1). | - | - | - | - | tool |
## Ownership notes
- `code/world.js` is from the **original source** (the pre-workshop Palma City base). We patch around it and never edited it. It's included because every coordinate below comes from it.
- `assets/world_ktx2/*` was **produced by Rydah Optimizer** (KTX2 encodes of our kit and facade textures). Our files load it under `?ktx2=1`.
- Kit furniture GLBs (couch, desk, kitchen, lockers, drone, pod, pod_closed, plus their .ktx2 variants) are **Rydah Forge's**. They're already in the repo at `v3/props/kit/`, so they're not duplicated here. Only `manifest.json` and the props sheet are copied.
- `crews.js` (crew colours) is not ours. It's referenced below and not copied.

## Skipped / not committed
| item | reason | box path | md5 |
|---|---|---|---|
| crew_garages_contact_sheet.png (11520x6480, 55 MB) | over the 50 MB rule (repo has no LFS). A 3000 px JPG copy is committed as `shots/hero/crew_garages_contact_sheet_downscaled.jpg` | /workspace/v3build/shots/hero/crew_garages_contact_sheet.png | 18ea274fe5f03c50ec90903740091080 |
| 11 ambientCG 2K zips (~204 MB) | raw sources, re-downloadable. URLs are in `ref/pbr/SOURCES.txt` (Asphalt031, Bark001, Bricks105, Concrete034, Concrete046, CorrugatedSteel005, Ground080, MetalPlates008, PaintedMetal004, PaintedPlaster017, Planks037A; `https://ambientcg.com/get?file=<id>_2K-JPG.zip`, CC0) | /workspace/skyrydahs-ref/pbr/*.zip | - |
| hero before/after singles where a side_by_side exists (fxbloom_*, pbr_causeway/street_*) | duplicates. Every side_by_side is kept, plus the latest of each view | /workspace/v3build/shots/hero/ | - |
| *.bak* backups | not source | - | - |

## Unity conversion notes
### World layout (units = metres; origin = Terminal Plaza; +X east, +Z south; Unity: flip Z or mirror, since three.js is right-handed)
Boxes are [minX, minZ, maxX, maxZ] (the full set is in `data/palma.json`):
- Islands: west [-240,-100,90,200], east [170,-100,320,200], north [-160,-320,240,-180].
- Districts: Portside Terminal [-70,-100,90,60]; The Cove [-240,-100,-70,40]; Industrial Port [-240,40,-70,200]; The Yard [-70,60,90,200]; The 98 [170,-100,320,-20]; The Drive [170,-20,320,90]; The Strip [170,90,320,200]; The Heights [-160,-320,240,-180]. Blockout adds an `eastblocks` district (wall panels).
- Bridges (a to b): Causeway (-20,-100)->(40,-180); Shore (90,150)->(170,165); 98 Bridge (240,-100)->(200,-180). Decks are flush with the ground (top y 0.01), with no ramps.
- Garages (pos, door face): codee (-36,-24) E; karasu (55,30) W; static (-190,-30) W; behemoth (-190,150) S; anubis (-110,170) E; ttt (20,150) N; genesis (250,150) N; forest (40,-260) S.

### Data formats (exported in `data/`, seed 1, by `tools/dump_world_json.py`)
- `colliders.json` (888 entries): XZ AABBs `{minX,maxX,minZ,maxZ}` with infinite height, plus optional `noKick`/`noKickWhy`. Unity: BoxColliders with a tall Y extent. **Height-aware collision is not modelled** (see open items).
- `ground.json`: WORLD_GROUND sampled on a 4 m grid, yHint 50 (topmost surface): `[x,z,y,surf]`, where surf is asphalt|concrete|wood|metal|grass|sand|water. The runtime contract is `WORLD_GROUND(x,z,yHint)` -> the highest walkable top <= yHint+0.6, with normal. Every surface today is level. Underpass deck top = 6.80. Unity: use real mesh colliders. The JSON is only for validation and for tagging surface types (physics material per surf).
- `WALL_PANELS.json`: wall-ride panels (East Blocks), named slots stable under any seed.
- `WALL_KICKS.json` (faces), `KICK_ROUTES.json` (66 solved wall-kick routes), `KICK_UNREACHABLE.json`, `KICK_BRIDGE.json`: wall-kick climb graph built by blockout.js. Unity: import as ScriptableObjects or tag the wall faces.
- Re-export: `bash /workspace/v3build/build_copy.sh /tmp/x.html && python3 tools/dump_world_json.py file:///tmp/x.html data` (hold .testlock).

### PBR material conventions
- Texture sets: `*_albedo` (sRGB), `*_nrm` (OpenGL +Y normal), `*_orm` packed **R=AO, G=roughness, B=metallic** (linear). This maps to a URP/HDRP mask map after repacking (HDRP mask = R metal, G AO, A smoothness = 1-rough).
- KTX2 (Basis): colour and ORM = ETC1S (sRGB for colour, linear for ORM); normals = UASTC; pre-flipped, flipY off. In Unity, use ASTC/ETC2 platform overrides from the JPG sources instead of the KTX2s.
- Sampling: world-space box / triplanar UVs on one instanced building shader (no per-building UVs). Env: equirect `env_portside_day/night.png`. Wetness and asphalt params live in pbr_world uniforms (pbrWet, pbrAsph).
- Facades: 8 materials in a 2048x1024 atlas (`assets/textures/facade_*.jpg`), tile rects in FACADE.uniforms.uFT.

### Draw-call budget lessons (Quest target <=110 world draws)
- Measured with dcsplit2 (seed 1): PBR default causeway 92-97, street 72-77; toon about the same. Graffiti peak 125 before the fixes.
- What worked: one instanced building shader for all buildings, with materials in an atlas not separate materials. Re-merge the static batch into 270 m tiles per material. Merge asphalt per material. Sign atlas. Crew interiors only built and visible when the **player** (not the camera) is within 14 m of the garage footprint, with a lazy build at 40 m. Sky follows day state with 0 extra draws.
- Unity: use the SRP Batcher, static batching per district, GPU instancing for buildings, and interiors as additive scenes or LOD-culled.

### Crew garage kit (crewhouse_kit.js)
- One shared kit for all crews. Upstairs = Kogarasumaru pod loft (pods at KIT_PODS, scale KIT_PS 1.45). Downstairs = A-T tuning bay. Prop fits live in KIT_PROP_FIT. Visibility radius KIT_R 14 m, lazy radius 40 m, layer 5.
- Theme per crew from crews.js `defaults` (jacket / gold / wheelGlow / rim colours): codee gold 0x7446d0 glow 0xffd700; static 0x9b3dff/0x00e5ff; karasu 0x40f0ff/0x00e5ff; anubis 0x00b8b0/0x00e0d0; behemoth 0xff7a12; forest 0x3fae6a/0x6dffa8; genesis 0xffc83a/0xff2fae; ttt 0xb8501e/0xff6a1a.
- Logo atlas `assets/kit/kit_logos.png` slots (KIT_LOGO_SLOT): codee 0, karasu 1, static 2, behemoth 3, anubis 4, ttt 5, genesis 6, forest 7, volt 8. Rust Claw has no slot yet.

## Open items
1. **Building-base**: pbr_base.js OPT-IN ready (`?pbrbase=1`) as of 2026-11-05 — waiting Ani look check + Oliver before/after before default-on. pbr_base_wip.* kept as older reference outside chain.
2. **FACADE harness fix**: the shot/measure harness reads day state through the global `const FACADE` (FACADE.uniforms.uDay). It needs a proper fix so the shot scripts don't depend on that global.
3. **Pod collision** in the Kog loft needs a height-aware check (the colliders are XZ-only, so pods block at any height).
4. **Catwalk posts** in the garage kit are still to do.
5. **Volt** + **Rust Claw** garages: **placed** 2026-11-05 (see Update below).

## Update 2026-11-05 — Volt + Rust Claw garages (Palma Builder)
- `code/crewhouse_kit.js` + `code/patch_crewhouse_kit.py`: inject Volt `[288,-74]` (The 98 charging station) + Rust Claw `[-165,-88]` (Cove salvage shed) into `PALMA.garages`; GATE_CODES volt=`9800` rustclaw=`1984`; per-crew exterior variants (`kitExtVolt` / `kitExtRustClaw`, ≤6 draws); logo slots volt=8 rustclaw=9; theme colour fallbacks TODO until crews.js lands.
- `assets/kit/kit_logos.png`: slot 9 = `shared/crew-logos/rust-claw.png`.
- `ref/garages-volt-rustclaw.md`: design refs + progress log.
- `shots/hero/garage_{volt,rustclaw}_{exterior_{day,night},interior,lot_{before,after}}.png` (10 files).
- Chain: `python3 patch_crewhouse_kit.py` (after patch_quant_fix, before patch_world_perf).

## Update 2026-11-05 — Day bloom tweak removal verified (Palma Builder)
- `code/pbr_world.js`: day-bloom tweak in `tick()` already removed 2026-10-31 00:18 (`bak-bloomtweak-0018`). No longer sets `FX.bloom.threshold/strength` via `S.bTh`/`.98`/`S.bSt`, nor injects `pbrDay` high-pass (`S.bMask`). Comment left pointing at Optimizer `/*FXBLOOM*/` in `patch_xr_fxmem.py`. `window.PBR_WORLD` exports unchanged: ENV.day/night/cube/cur, GR.exp/fog, tick/convert/boot/install.
- Verify (build_copy `/tmp/palma_bloom.html`, FX on, seed=1): day sky blue not cyan; bloom th/st 0.68/0.6 day+night with bloomHot; no ground blowout; 0 pageerrors; draws street 80–81 / causeway 73–74.
- Hero finals: `shots/hero/pbr_{street,causeway}_{day,night}_final.png` + `pbr_street_day_before_after_side_by_side.png`.
- Real html md5 unchanged (`5ad0f5646468f5fef7d25f9153144e8e`). Chain: `python3 patch_pbr_world.py` (after patch_world_perf).

## 2026-11-05 13:59 CST update
Ani review fixes + CREW_RIVALS: crewhouse_kit.js (kitTheme←CREW_RIVALS, kitFixEmblems, Volt canopy 3.76m), patch_crewhouse_kit.py (inject CREW_RIVALS, MARINA ry=0), tools/garage_hero_shots.py (Volt cam), tools/palma_testlock.sh. Heroes re-shot under shots/hero/garage_{volt,rustclaw}_*.png. Real html untouched.

## Update 2026-11-05 — Building ground-floor bases opt-in (Palma Builder)
- `code/pbr_base.js` + `code/patch_pbr_base.py`: 0–5 m band on facade ShaderMaterial after pbr_world convert. Brick/concrete per kit, steel I-beam columns+lintels, framed storefronts (env glass + night interiors), kick plate, grime/AO. Shader-only (0 new draws). OPT-IN `?pbrbase=1`.
- Contrast/scale + distance-AA fix 11/05: larger masonry modules, thicker beams/frames, stronger mortar/glass/grime; `wall=mix(masonry,col,.92)` so facades distance-AA no longer washes beams/windows at 15–40 m.
- Assets: `assets/pbr_base/pbrB_{albedo,nrm,orm}.{jpg,ktx2}` (CC0 ambientCG; see SOURCES.txt).
- Chain: `python3 patch_pbr_base.py` immediately after `patch_pbr_world.py` (Ani approved). Default-on only after Ani look check + Oliver before/after.
- Hero finals: `shots/hero/bldgbase_final_{street,close}_{day,night}_{before,after}.png` + `*_side_by_side.png`.
- WIP refs kept out of chain: `pbr_base_wip.js`, `pbr_base_wip_inject.py`, `pbr_base_wip.glsl`.
