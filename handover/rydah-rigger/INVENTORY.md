# Rydah Rigger handover: inventory (2026-11-05)
Character rigging and integration for Sky Rydahs (WebXR, three.js r128, Quest 3 + desktop). Everything here is a COPY of a box working file (/workspace/...). Local-only placeholder-rider material is not in this repo by design (public repo).

## Layout
- `code/`: runtime JS, build patches, tests, progress notes, `rigwork/` numpy rig tools
- `assets/`: shared skeleton, crew logos/patches/colorways, crew coins, rigged riders (Anika, Caali G v2)
- `docs/`: rig plans, combat animation plan, Meshy crew prompts
- `shots/`: curated reference shots (pose sheets, combat, skate v2, in-game), ~23 MB

## Build chain (build_ikki.sh, integrator-only; see code/build_ikki.sh.reference)
Patches edit `sky-rydahs-v3-ikki.html` in place, in this order (my steps in **bold**):
patch_ikki → patch_tickguard → patch_turf → **patch_ikki_skate.py** (pastes `ikki_skate/ikki_skate.js` over the `loadIkki()` body, Ikki palette, NPC figure-8 loop, drive(…,boost)) → gates → wallatk → asphalt → **patch_wardrobe** (inlines riders.js / jackets.js wardrobe code; owner: shared, Forge/Rigger) → facades … minimap → patch_draco.py.ktx2-candidate (Optimizer: Draco + ?ktx2=1) → **patch_crew_quest.py** (crew .quest.glb, Anika roster, Caali v2 default player + SR_CAALI_REF_H, title, NPC ground) → quant_fix → crewhouse_kit → world_perf → pbr_world → pbr_base → xr_fxmem → combat_fx (Forge CombatFX, consumes my srFX points).
`ikki_skate.WIP.js` is NOT in the chain (WIP rule: unfinished work stays out of the chain).
Ownership note: how jackets.js / riders.js are inlined lives in patch_wardrobe.py (not mine, not copied); check that file in the Systems/Forge handover.

## Runtime flags / URL params
| flag | effect | where |
|---|---|---|
| `window.SR_COMBAT_POSES` / `?combatposes=1` | enables combat poses (atk/react states, events). Default OFF | ikki_skate.js, jackets.js |
| `?noplant=1` | disables plant() foot lock and crew plant | ikki_skate.js, jackets.js |
| `?atskate=merged(default)\|fit\|legacy\|off` | v2 merged skate / old fitted halves / old single skate / none on loadIkki rider | jackets.js |
| `?crewskate=toon` | crews keep old toon skate | jackets.js |
| `?attint=crew\|flat\|clamp` | baked skate tint mode (SR_SKATE_TINT.mode, default flat) | jackets.js |
| `?notint` | disables skate tint (A/B shots) | jackets.js |
| `?npcglow=mesh` | old separate NPC glow mesh (default: glow folded into body draw) | jackets.js |
| `?patch=` | back-patch override | jackets.js |
| `?ktx2=1` / `window.SR_KTX2` | KTX2 texture path (Optimizer gate); my skate textures use SR_KTX2.loader() when on | jackets.js, riders.js |
| `window.SR_DRACO` | Draco loader hook (Optimizer) | jackets.js |
| `?texfull` | full-res textures (Optimizer param; my loaders honour the shared texture path) | riders/optimizer |
| `?player=` | pick the player rider (caali default, anika, …) | riders.js / jackets.js |
| `?chars=` | character base URL | riders.js |
| `?crew=orig` | original non-Draco crew GLBs | patch_crew_quest |
| `SR_SKATE_SCALE=1.25`, `SR_SKATE_PIVOT=(0,.12,-.06)`, `SR_SKATE_LIFT=0.0532`, `SR_SKATE_SIDE_DY={L:0,R:-0.0105}`, `SR_SKATE_CONTACT_MAX=0.03` | skate scale about ankle pivot, rider lift, R-half drop, crew plant max correction | jackets.js consts |
| `root.userData.setDetail('full'\|'lite')` (alias root.setDetail) | per-rider LOD detail toggle used by the Optimizer sorter | jackets.js srDetailInstall |
| `window.SR_RIDER_HOOKS` | per-rider hook table (local-only extensions plug in here; empty in public) | ikki_skate.js |

## Dependencies
three.js r128 (global build), GLTFLoader r128, BufferGeometryUtils r128 (mergeBufferGeometries; non-interleaved attrs required, hence the deinterleave guard), DRACOLoader (geometry), KTX2Loader + Basis transcoder (candidate, ?ktx2=1). Tests: Python 3 + Playwright (chromium), local http server on :8765. rigwork: Python 3 + numpy, node for decode.mjs (gltf decode). Blender 4.3.2 for the .blend.

## Skeleton spec (assets/skeleton/README.md has the full text)
- 91 joints: 65 Mixamo `mixamorig:*` (Hips…HeadTop_End, full fingers, Toe_End), 4 twist bones (`LeftArmTwist/RightArmTwist` child of *Arm, `LeftForeArmTwist/RightForeArmTwist` child of *ForeArm, ~50% roll share), 2 A-T roots `L_AT_Root/R_AT_Root` (child of feet, at ankle pivot, world-aligned in bind), 20 sockets `L_at_*/R_at_*` (cuff, ankle_out, ankle_in, heel, toe, wheel_cover_out, motor, exhaust, emblem, led; +Y = surface normal).
- Metres, +Y up, faces +Z, +X = rider's LEFT. Bind = Caali G A-pose. Height ref 1.916 (SR_CAALI_REF_H). Joint order = bones.json order.
- Spring bones: extra joints after the 91 (Anika joints 91..106): `Anika_BraidL_01..05`, `Anika_BraidR_01..05` (parent Head), `Anika_Skirt_00..05` (parent Hips, 1-bone chains). Regex `/^<Rider>_(Braid[LR]|Skirt)_\d\d$/` after stripping `mixamorig:`.
- glTF extras: node `extras.spring = {chain, index, kind:'braid'|'skirt', tail, [stiffness,damping,gravity,drag,maxSwing,maxLink]}`; `skin.extras.springChains` = array of chain params (name, bones, k, damping, maxSwing, colliders). Defaults: braid k60 d.3 g1 drag.3 swing 70/35°; skirt 90/.45/.5/.4 swing 40°. Colliders: hips, chest, 2/thigh, 1/shin spheres + deck plane.
- Skates are not skinned; the shared skate binds rigid (weight 1) to Left/RightFoot at runtime.

## Combat API contract (ikki_skate.js riders; crew riders get the 19-bone subset in jackets.js)
- `u=root.userData`; `u.setState('atk',{step:0..2}|{move:'heavy',charge}|{set,key})`, `u.setState('react',{kind:'light'|'heavy'|'knockdown',dir})`.
- `u.onCombat(type,fn)` → unsubscribe fn. Events: `onHitFrame {move,f,fxName,pos,fx}`, `onCancelOpen`, `onCancelClose`, `onRecover {interrupted?,by?}`. Authored at 72 fps; fire on frame ±1.
- `u.combatQuery()` → {move, kind, frames{hit[],cancel[a,b],end}, side, plant, root, fx{handL..wheelR}}; `u.combatState()`; `u.combatHitStop(ms)` freezes the move clock (Systems scales via HITSTOP_SCALE 0.5).
- Moves (RIDER_COMBAT_MOVES): light1, light2, finisher, heavy (provisional), react_light, react_heavy, knockdown, plus crew K/L specials (`<set>_<key>`). Upper-body mask, slew 720°/s base, 1800°/s lead limb in active frames only; plant 'both'|'S'|'any'|'off'.
- srFX points: Object3D children `srFX_handL/R`, `srFX_footL/R`, `srFX_wheelL/R` (rigid on bones), `u.fx[name]`, `u.fxPos(name)`. Forge CombatFX attaches here.
- Hooks: `u.mirrorStance(bool)` flips kickSide/lead side; `u.combatFeelMods({windup,...}|null)` scales the feel row.

## Export rules
- POSITION must stay float32: NO KHR_mesh_quantization / meshopt on riders (rMerge concatenates raw arrays). Draco is allowed for geometry (decodes to float).
- No interleaved buffers (BufferGeometryUtils r128 cannot merge InterleavedBufferAttributes); jackets.js deinterleaves defensively.
- ≤4 weights/vertex, full joint list in bones.json order, rest = bind. Baked skate verts flagged by sid (vertex color R*16: 11-13) get discarded/tinted at runtime.

## Known issues
- Spring solver is WIP (ikki_skate.WIP.js), latest rig_springs run 24/28; swing checks failed while the solver idled (camDist).
- camDist bug fix is WIP: update() used cam.position (local in the XR rig) instead of cam.getWorldPosition, so the springs went idle at >12 m. The fix exists only in the WIP file.
- Caali's right skate sits 1.7 mm low (dyR), from the skeleton bind asymmetry (RightFoot +10.53 mm), low priority. A mirrored-stance finisher on Caali plants at 3.6 mm (threshold 3 mm).
- Anika braids fused into the top / braid tips clip the chest in a deep crouch. The Caali v2 jacket side panel stretches a little with raised arms.
- The shared A-T skate is baked into the Anika/Caali v2 meshes (sid 11-13). At runtime it is discarded in favour of the v2 merged skate.
- tests/rig_springs.py is NOT included (its harness, page and default cases are built around the local-only rider). Rebuild it from the springs section above.

## Unity conversion notes
- Humanoid: the 65 `mixamorig:*` bones map 1:1 to Unity's Mixamo Humanoid avatar (strip the prefix or use the Mixamo preset). Map the twist bones as non-humanoid extras, or drive them with Twist Correction / a TwistChain constraint (~50% roll). Keep AT roots and sockets as plain transforms: skates are rigid children of the feet, and sockets are attach points for VFX/props.
- Procedural poser → Animator + Animation Rigging: author locomotion (push/glide/tuck/air/grind) as blend-tree clips driven by speed/boost/airborne. Replace pose() layer weights W with Animator layers (upper-body avatar mask = the combat mask). plant() → Two Bone IK constraints on the legs, with a deck raycast target and the weight blended per plant mode. Slew caps → damped transform or rate-limit in a rig job.
- RIDER_JOINT_LIMITS → Humanoid muscle limits in the Avatar config (spine twist 40° total split .4/.3/.3, soft knee etc.). Leave clamps that IK needs as rig constraints.
- Spring bones → a Unity spring-bone solution (e.g. UniVRM VRMSpringBone or Magica Cloth / Dynamic Bone). Port node extras.spring + skin.extras.springChains to stiffness/drag/gravity/colliders. Sphere colliders on hips/chest/thighs/shins, plane collider for the deck. Distance LOD 12 m.
- Combat → AnimationClips per move at 72 fps, with Animation Events at the hit/cancel/end frames (onHitFrame, onCancelOpen/Close, onRecover). Hit-stop = Animator.speed 0 for ms × HITSTOP_SCALE. srFX_* → empty child transforms for VFX Graph/Particle anchors. combatQuery → a ScriptableObject move table.
- Assets: use the full (non-Draco) GLBs for import (anika-rider.glb, caali-g-v2*.rigged.glb), via glTFast/UniGLTF. The .blend has the armature for FBX re-export.

## Not included / skipped (box paths)
- Backups (*.bak*, *.prefix-*, *.prespring-*, *.presym-*, *.prerebind-*, *.static-*, *.v1*, *.nrm768-*), __pycache__, _archive dirs.
- /workspace/rigwork/out (153 MB, 12 intermediate rigged GLBs + reports; the final versions are in assets/riders) and /workspace/rigwork/dec (125 MB of decoded intermediates). Skipped as large duplicates. /workspace/rigwork/shots, shots2 (117 MB of debug shots), skipped.
- Live wardrobe/riders/caali-g.glb: identical to assets/riders/caali-g/caali-g-v2.rigged.glb (md5 b92e238373f9e1aecd0eaa297f5317b2), so not duplicated. caali-g-hd.glb (md5 cabe06217f4c295cd4957129989e71cc), caali-g.nonormal*.glb and *.ktx2 are Forge post-processed outputs: reference only.
- A-T skates are Forge's assets (referenced, not copied): wardrobe/skates/at-skate-meshy.glb 0a44e2346fc4f2877142efe1d18e9ecf, at-skate-meshy.v2.glb 5de1f2f9681f1c5958d3666b133c324d, at-skate-meshy.merged.v2.glb e829857e30b2c6aa6d44ca7374a1409a, at-skate-meshy.merged.glb bd915dcac893bd5ba60e6942334b3053, at-skate-meshy.merged.quest.glb 2e7e3b8cfac0918d3c002d578c716678. shared/at-skate/ (Forge) not copied.
- ikki_skate/ikki_skate_v1/v2/v3.js are old versions, superseded and not copied. ikki_skate/build_lod.py etc. belong to the Ikki pipeline; ownership is unclear, so they were not copied.
- No file was skipped only for size: every copied file is under 30 MB (largest: caali-g-v2-hd.rigged.glb, 26.9 MB).

## Files
| path | size | what | owner | status |
|---|---|---|---|---|
| `assets/crew-coins/anubis-coin.glb` | 735 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/behemoth-coin.glb` | 713 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/blend/anubis-coin.blend` | 680 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/blend/behemoth-coin.blend` | 657 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/blend/code-e-coin.blend` | 928 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/blend/genesis-coin.blend` | 828 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/blend/kogarasumaru-coin.blend` | 901 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/blend/rust-claw-coin.blend` | 921 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/blend/sleeping-forest-coin.blend` | 728 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/blend/static-angels-coin.blend` | 862 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/blend/team-storm-coin.blend` | 808 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/blend/tool-toul-to-coin.blend` | 715 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/blend/volt-coin.blend` | 767 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/build_coins.py` | 4 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/code-e-coin.glb` | 957 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/coins-contact-sheet.png` | 3164 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/gen_coin_textures.py` | 8 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/genesis-coin.glb` | 876 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/kogarasumaru-coin.glb` | 918 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/render_coins.py` | 9 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/renders/coin-in-hand.png` | 1122 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/renders/coins-contact-raw.png` | 4173 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/renders/turntable-code-e.gif` | 3134 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/renders/turntable-code-e/frame_000.png` | 392 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/renders/turntable-code-e/frame_001.png` | 394 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/renders/turntable-code-e/frame_002.png` | 393 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/renders/turntable-code-e/frame_003.png` | 382 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/renders/turntable-code-e/frame_004.png` | 367 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/renders/turntable-code-e/frame_005.png` | 348 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/renders/turntable-code-e/frame_006.png` | 321 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/renders/turntable-code-e/frame_007.png` | 347 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/renders/turntable-code-e/frame_008.png` | 371 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/renders/turntable-code-e/frame_009.png` | 385 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/renders/turntable-code-e/frame_010.png` | 385 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/renders/turntable-code-e/frame_011.png` | 392 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/renders/turntable-code-e/frame_012.png` | 394 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/renders/turntable-code-e/frame_013.png` | 394 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/renders/turntable-code-e/frame_014.png` | 392 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/renders/turntable-code-e/frame_015.png` | 381 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/renders/turntable-code-e/frame_016.png` | 368 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/renders/turntable-code-e/frame_017.png` | 348 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/renders/turntable-code-e/frame_018.png` | 321 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/renders/turntable-code-e/frame_019.png` | 347 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/renders/turntable-code-e/frame_020.png` | 371 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/renders/turntable-code-e/frame_021.png` | 387 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/renders/turntable-code-e/frame_022.png` | 385 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/renders/turntable-code-e/frame_023.png` | 391 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/rust-claw-coin.glb` | 943 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/sleeping-forest-coin.glb` | 773 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/static-angels-coin.glb` | 896 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/team-storm-coin.glb` | 839 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/anubis-back-basecolor.jpg` | 99 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/anubis-back-height.png` | 122 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/anubis-back-normal.jpg` | 163 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/anubis-back-orm.jpg` | 95 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/anubis-edge-basecolor.png` | 0 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/anubis-edge-normal.png` | 0 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/anubis-edge-orm.png` | 0 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/anubis-front-basecolor.jpg` | 98 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/anubis-front-height.png` | 117 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/anubis-front-normal.jpg` | 149 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/anubis-front-orm.jpg` | 93 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/behemoth-back-basecolor.jpg` | 73 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/behemoth-back-height.png` | 126 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/behemoth-back-normal.jpg` | 170 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/behemoth-back-orm.jpg` | 101 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/behemoth-edge-basecolor.png` | 0 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/behemoth-edge-normal.png` | 0 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/behemoth-edge-orm.png` | 0 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/behemoth-front-basecolor.jpg` | 76 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/behemoth-front-height.png` | 118 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/behemoth-front-normal.jpg` | 156 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/behemoth-front-orm.jpg` | 98 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/code-e-back-basecolor.jpg` | 146 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/code-e-back-height.png` | 144 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/code-e-back-normal.jpg` | 192 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/code-e-back-orm.jpg` | 118 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/code-e-edge-basecolor.png` | 0 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/code-e-edge-normal.png` | 0 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/code-e-edge-orm.png` | 0 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/code-e-front-basecolor.jpg` | 146 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/code-e-front-height.png` | 151 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/code-e-front-normal.jpg` | 195 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/code-e-front-orm.jpg` | 122 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/genesis-back-basecolor.jpg` | 136 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/genesis-back-height.png` | 128 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/genesis-back-normal.jpg` | 173 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/genesis-back-orm.jpg` | 106 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/genesis-edge-basecolor.png` | 0 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/genesis-edge-normal.png` | 0 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/genesis-edge-orm.png` | 0 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/genesis-front-basecolor.jpg` | 139 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/genesis-front-height.png` | 127 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/genesis-front-normal.jpg` | 173 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/genesis-front-orm.jpg` | 111 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/kogarasumaru-back-basecolor.jpg` | 121 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/kogarasumaru-back-height.png` | 132 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/kogarasumaru-back-normal.jpg` | 179 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/kogarasumaru-back-orm.jpg` | 135 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/kogarasumaru-edge-basecolor.png` | 0 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/kogarasumaru-edge-normal.png` | 0 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/kogarasumaru-edge-orm.png` | 0 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/kogarasumaru-front-basecolor.jpg` | 129 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/kogarasumaru-front-height.png` | 135 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/kogarasumaru-front-normal.jpg` | 179 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/kogarasumaru-front-orm.jpg` | 137 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/rust-claw-back-basecolor.jpg` | 132 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/rust-claw-back-height.png` | 141 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/rust-claw-back-normal.jpg` | 190 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/rust-claw-back-orm.jpg` | 115 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/rust-claw-edge-basecolor.png` | 0 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/rust-claw-edge-normal.png` | 0 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/rust-claw-edge-orm.png` | 0 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/rust-claw-front-basecolor.jpg` | 143 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/rust-claw-front-height.png` | 150 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/rust-claw-front-normal.jpg` | 196 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/rust-claw-front-orm.jpg` | 129 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/sleeping-forest-back-basecolor.jpg` | 103 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/sleeping-forest-back-height.png` | 129 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/sleeping-forest-back-normal.jpg` | 174 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/sleeping-forest-back-orm.jpg` | 105 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/sleeping-forest-edge-basecolor.png` | 0 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/sleeping-forest-edge-normal.png` | 0 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/sleeping-forest-edge-orm.png` | 0 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/sleeping-forest-front-basecolor.jpg` | 92 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/sleeping-forest-front-height.png` | 121 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/sleeping-forest-front-normal.jpg` | 159 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/sleeping-forest-front-orm.jpg` | 103 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/static-angels-back-basecolor.jpg` | 127 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/static-angels-back-height.png` | 136 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/static-angels-back-normal.jpg` | 188 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/static-angels-back-orm.jpg` | 117 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/static-angels-edge-basecolor.png` | 0 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/static-angels-edge-normal.png` | 0 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/static-angels-edge-orm.png` | 0 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/static-angels-front-basecolor.jpg` | 128 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/static-angels-front-height.png` | 133 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/static-angels-front-normal.jpg` | 180 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/static-angels-front-orm.jpg` | 117 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/team-storm-back-basecolor.jpg` | 110 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/team-storm-back-height.png` | 129 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/team-storm-back-normal.jpg` | 175 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/team-storm-back-orm.jpg` | 103 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/team-storm-edge-basecolor.png` | 0 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/team-storm-edge-normal.png` | 0 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/team-storm-edge-orm.png` | 0 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/team-storm-front-basecolor.jpg` | 121 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/team-storm-front-height.png` | 133 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/team-storm-front-normal.jpg` | 177 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/team-storm-front-orm.jpg` | 114 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/tool-toul-to-back-basecolor.jpg` | 80 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/tool-toul-to-back-height.png` | 130 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/tool-toul-to-back-normal.jpg` | 175 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/tool-toul-to-back-orm.jpg` | 102 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/tool-toul-to-edge-basecolor.png` | 0 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/tool-toul-to-edge-normal.png` | 0 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/tool-toul-to-edge-orm.png` | 0 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/tool-toul-to-front-basecolor.jpg` | 81 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/tool-toul-to-front-height.png` | 130 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/tool-toul-to-front-normal.jpg` | 172 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/tool-toul-to-front-orm.jpg` | 105 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/volt-back-basecolor.jpg` | 108 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/volt-back-height.png` | 126 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/volt-back-normal.jpg` | 170 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/volt-back-orm.jpg` | 101 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/volt-edge-basecolor.png` | 0 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/volt-edge-normal.png` | 0 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/volt-edge-orm.png` | 0 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/volt-front-basecolor.jpg` | 115 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/volt-front-height.png` | 126 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/volt-front-normal.jpg` | 166 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/textures/volt-front-orm.jpg` | 109 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/tool-toul-to-coin.glb` | 753 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/validate_coins.py` | 1 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-coins/volt-coin.glb` | 807 KB | Crew coin GLB/texture/render or generator script | Rydah Rigger | live |
| `assets/crew-logos/anubis-patch-height.png` | 204 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/anubis-patch-normal.png` | 985 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/anubis-patch-noshadow.png` | 1063 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/anubis-patch.png` | 1087 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/anubis.png` | 259 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/anubis.svg` | 5 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/behemoth-patch-height.png` | 203 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/behemoth-patch-normal.png` | 978 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/behemoth-patch-noshadow.png` | 988 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/behemoth-patch.png` | 1010 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/behemoth.png` | 226 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/behemoth.svg` | 5 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/caali-g-patch-height.png` | 216 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/caali-g-patch-normal.png` | 1014 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/caali-g-patch-noshadow.png` | 1000 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/caali-g-patch.png` | 1022 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/caali-g.png` | 248 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/caali-g.svg` | 2 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/check_readability.py` | 1 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/code-e-patch-height.png` | 222 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/code-e-patch-normal.png` | 1030 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/code-e-patch-noshadow.png` | 1006 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/code-e-patch.png` | 1028 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/code-e.png` | 286 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/code-e.svg` | 6 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/gen_caali_g_emblem.py` | 2 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/gen_colorways.py` | 5 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/gen_crew_logos.py` | 15 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/gen_crew_patches.py` | 8 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/genesis-patch-height.png` | 194 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/genesis-patch-normal.png` | 956 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/genesis-patch-noshadow.png` | 1133 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/genesis-patch.png` | 1156 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/genesis.png` | 273 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/genesis.svg` | 5 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/jacket-colorways-preview.png` | 1206 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/jacket-colorways.json` | 23 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/kogarasumaru-patch-height.png` | 235 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/kogarasumaru-patch-normal.png` | 1041 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/kogarasumaru-patch-noshadow.png` | 1061 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/kogarasumaru-patch.png` | 1084 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/kogarasumaru.png` | 258 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/kogarasumaru.svg` | 8 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/logos-contact-sheet.png` | 2140 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/patch-readability-check.png` | 1037 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/rust-claw-patch-height.png` | 249 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/rust-claw-patch-normal.png` | 1089 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/rust-claw-patch-noshadow.png` | 1216 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/rust-claw-patch.png` | 1241 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/rust-claw.png` | 277 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/rust-claw.svg` | 7 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/sleeping-forest-patch-height.png` | 228 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/sleeping-forest-patch-normal.png` | 1058 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/sleeping-forest-patch-noshadow.png` | 1099 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/sleeping-forest-patch.png` | 1122 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/sleeping-forest.png` | 264 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/sleeping-forest.svg` | 6 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/static-angels-patch-height.png` | 210 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/static-angels-patch-normal.png` | 1003 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/static-angels-patch-noshadow.png` | 1120 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/static-angels-patch.png` | 1143 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/static-angels.png` | 281 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/static-angels.svg` | 6 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/team-storm-before-after.png` | 343 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/team-storm-patch-height.png` | 219 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/team-storm-patch-normal.png` | 1010 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/team-storm-patch-noshadow.png` | 1124 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/team-storm-patch.png` | 1148 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/team-storm.png` | 279 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/team-storm.svg` | 7 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/tool-toul-to-patch-height.png` | 210 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/tool-toul-to-patch-normal.png` | 985 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/tool-toul-to-patch-noshadow.png` | 896 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/tool-toul-to-patch.png` | 916 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/tool-toul-to.png` | 259 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/tool-toul-to.svg` | 7 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/volt-patch-height.png` | 213 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/volt-patch-normal.png` | 998 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/volt-patch-noshadow.png` | 1113 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/volt-patch.png` | 1136 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/volt.png` | 269 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/crew-logos/volt.svg` | 7 KB | Crew logo/patch/colorway art or generator script | Rydah Rigger | live |
| `assets/riders/anika/anika-npc.draco-webp.glb` | 1061 KB | Anika rigged rider (91 joints + 16 spring bones); variant by suffix: none=full, .quest=Draco, .quest-ktx2, .opt, .opt-ktx2, .draco-webp | Rydah Rigger | variant |
| `assets/riders/anika/anika-npc.glb` | 5476 KB | Anika rigged rider (91 joints + 16 spring bones); variant by suffix: none=full, .quest=Draco, .quest-ktx2, .opt, .opt-ktx2, .draco-webp | Rydah Rigger | variant |
| `assets/riders/anika/anika-npc.opt-ktx2.glb` | 916 KB | Anika rigged rider (91 joints + 16 spring bones); variant by suffix: none=full, .quest=Draco, .quest-ktx2, .opt, .opt-ktx2, .draco-webp | Rydah Rigger | variant |
| `assets/riders/anika/anika-npc.opt.glb` | 1339 KB | Anika rigged rider (91 joints + 16 spring bones); variant by suffix: none=full, .quest=Draco, .quest-ktx2, .opt, .opt-ktx2, .draco-webp | Rydah Rigger | variant |
| `assets/riders/anika/anika-npc.quest-ktx2.glb` | 6505 KB | Anika rigged rider (91 joints + 16 spring bones); variant by suffix: none=full, .quest=Draco, .quest-ktx2, .opt, .opt-ktx2, .draco-webp | Rydah Rigger | live |
| `assets/riders/anika/anika-npc.quest.glb` | 5889 KB | Anika rigged rider (91 joints + 16 spring bones); variant by suffix: none=full, .quest=Draco, .quest-ktx2, .opt, .opt-ktx2, .draco-webp | Rydah Rigger | live |
| `assets/riders/anika/anika-rider.draco-webp.glb` | 2783 KB | Anika rigged rider (91 joints + 16 spring bones); variant by suffix: none=full, .quest=Draco, .quest-ktx2, .opt, .opt-ktx2, .draco-webp | Rydah Rigger | variant |
| `assets/riders/anika/anika-rider.glb` | 16363 KB | Anika rigged rider (91 joints + 16 spring bones); variant by suffix: none=full, .quest=Draco, .quest-ktx2, .opt, .opt-ktx2, .draco-webp | Rydah Rigger | variant |
| `assets/riders/anika/anika-rider.opt-ktx2.glb` | 2432 KB | Anika rigged rider (91 joints + 16 spring bones); variant by suffix: none=full, .quest=Draco, .quest-ktx2, .opt, .opt-ktx2, .draco-webp | Rydah Rigger | variant |
| `assets/riders/anika/anika-rider.opt.glb` | 3098 KB | Anika rigged rider (91 joints + 16 spring bones); variant by suffix: none=full, .quest=Draco, .quest-ktx2, .opt, .opt-ktx2, .draco-webp | Rydah Rigger | variant |
| `assets/riders/anika/anika-rider.quest-ktx2.glb` | 18164 KB | Anika rigged rider (91 joints + 16 spring bones); variant by suffix: none=full, .quest=Draco, .quest-ktx2, .opt, .opt-ktx2, .draco-webp | Rydah Rigger | live |
| `assets/riders/anika/anika-rider.quest.glb` | 17602 KB | Anika rigged rider (91 joints + 16 spring bones); variant by suffix: none=full, .quest=Draco, .quest-ktx2, .opt, .opt-ktx2, .draco-webp | Rydah Rigger | live |
| `assets/riders/anika/anika-rig-report.json` | 19 KB | Anika rigged rider (91 joints + 16 spring bones); variant by suffix: none=full, .quest=Draco, .quest-ktx2, .opt, .opt-ktx2, .draco-webp | Rydah Rigger | live |
| `assets/riders/anika/anika-springs.md` | 2 KB | Anika rigged rider (91 joints + 16 spring bones); variant by suffix: none=full, .quest=Draco, .quest-ktx2, .opt, .opt-ktx2, .draco-webp | Rydah Rigger | live |
| `assets/riders/caali-g/caali-g-v2-hd.rigged.glb` | 26275 KB | Caali G v2 rigged (Rigger rebind of Forge Meshy v2). caali-g-v2.rigged.glb == live wardrobe/riders/caali-g.glb (md5 b92e2383...); -hd.rigged == caali-g-hd.v2raw | Rydah Rigger | live |
| `assets/riders/caali-g/caali-g-v2.quest-ktx2.rigged.glb` | 16317 KB | Caali G v2 rigged (Rigger rebind of Forge Meshy v2). caali-g-v2.rigged.glb == live wardrobe/riders/caali-g.glb (md5 b92e2383...); -hd.rigged == caali-g-hd.v2raw | Rydah Rigger | live |
| `assets/riders/caali-g/caali-g-v2.quest.rigged.glb` | 15580 KB | Caali G v2 rigged (Rigger rebind of Forge Meshy v2). caali-g-v2.rigged.glb == live wardrobe/riders/caali-g.glb (md5 b92e2383...); -hd.rigged == caali-g-hd.v2raw | Rydah Rigger | live |
| `assets/riders/caali-g/caali-g-v2.rig-report.json` | 16 KB | Caali G v2 rigged (Rigger rebind of Forge Meshy v2). caali-g-v2.rigged.glb == live wardrobe/riders/caali-g.glb (md5 b92e2383...); -hd.rigged == caali-g-hd.v2raw | Rydah Rigger | live |
| `assets/riders/caali-g/caali-g-v2.rigged.glb` | 14493 KB | Caali G v2 rigged (Rigger rebind of Forge Meshy v2). caali-g-v2.rigged.glb == live wardrobe/riders/caali-g.glb (md5 b92e2383...); -hd.rigged == caali-g-hd.v2raw | Rydah Rigger | live |
| `assets/skeleton/README.md` | 4 KB | Shared 91-joint rider skeleton (see README) | Rydah Rigger | live |
| `assets/skeleton/rider-skeleton.blend` | 624 KB | Shared 91-joint rider skeleton (see README) | Rydah Rigger | live |
| `assets/skeleton/rider-skeleton.bones.json` | 64 KB | Shared 91-joint rider skeleton (see README) | Rydah Rigger | live |
| `assets/skeleton/rider-skeleton.glb` | 27 KB | Shared 91-joint rider skeleton (see README) | Rydah Rigger | live |
| `code/build_ikki.sh.reference` | 1 KB | Read-only copy of the integrator build chain (owner Ani/integrator), for chain order reference | Rydah Rigger | reference |
| `code/ikki_skate/ikki_skate.WIP.js` | 91 KB | WIP copy of the poser with riderSpringsInstall() spring solver + camDist world-position fix. NOT in build chain (source: ikki_skate/ikki_skate.wip.js) | Rydah Rigger | WIP |
| `code/ikki_skate/ikki_skate.js` | 84 KB | Procedural skate poser (replaces loadIkki body): RIDER_JOINT_LIMITS, W blend weights, pose(), plant() foot lock, RIDER_COMBAT_MOVES + combat API, mirrorStance/combatFeelMods/SR_RIDER_HOOKS, twist-bone share, srFX points | Rydah Rigger | live (combat flag-gated) |
| `code/jackets.js` | 65 KB | Crew jacket colouring + back-patch atlas, setDetail full/lite, deinterleave guard, v2 merged A-T skate on every rider, SR_SKATE scale/lift/side offsets, baked-skate sid discard + tint, KTX2 skate path, crew plant + crew 19-bone reacts, srFX points, glow-to-body | Rydah Rigger | live |
| `code/patch_crew_quest.py` | 8 KB | Build patch: crew Draco .quest.glb swap + Rigger roster fixes (Anika, Caali v2 default player, title, NPC ground) | Rydah Rigger | live (co-owned with Optimizer) |
| `code/patch_ikki_skate.py` | 5 KB | Build patch pass 3: injects ikki_skate.js into the loadIkki body, Ikki palette, NPC loop. Public copy: local-only include line removed | Rydah Rigger | live |
| `code/perf/anika-roster.md` | 0 KB | Rigger progress notes (local-only lines removed) | Rydah Rigger | notes |
| `code/perf/rigger-combat-progress.md` | 0 KB | Rigger progress notes (local-only lines removed) | Rydah Rigger | notes |
| `code/riders.js` | 18 KB | r128 GLB crew rider loader (port of shared/rider_loader.js); NPC spawn on ground (Rigger edit). File is co-owned: original loader by Systems/Optimizer, Rigger did NPC ground | Rydah Rigger | live (co-owned) |
| `code/rigwork/anika_lod2_skirt.py` | 2 KB | numpy rig tooling (rig.py = skin Meshy riders to 91-joint skeleton + springs; caali_* rebind/arms/shoulder fixes; anika_* sym/skirt; glb.py IO; sandbox.py validator) | Rydah Rigger | tool |
| `code/rigwork/anika_sym.py` | 2 KB | numpy rig tooling (rig.py = skin Meshy riders to 91-joint skeleton + springs; caali_* rebind/arms/shoulder fixes; anika_* sym/skirt; glb.py IO; sandbox.py validator) | Rydah Rigger | tool |
| `code/rigwork/back.py` | 1 KB | numpy rig tooling (rig.py = skin Meshy riders to 91-joint skeleton + springs; caali_* rebind/arms/shoulder fixes; anika_* sym/skirt; glb.py IO; sandbox.py validator) | Rydah Rigger | tool |
| `code/rigwork/braidseg.py` | 1 KB | numpy rig tooling (rig.py = skin Meshy riders to 91-joint skeleton + springs; caali_* rebind/arms/shoulder fixes; anika_* sym/skirt; glb.py IO; sandbox.py validator) | Rydah Rigger | tool |
| `code/rigwork/caali_arms.py` | 3 KB | numpy rig tooling (rig.py = skin Meshy riders to 91-joint skeleton + springs; caali_* rebind/arms/shoulder fixes; anika_* sym/skirt; glb.py IO; sandbox.py validator) | Rydah Rigger | tool |
| `code/rigwork/caali_rebind.py` | 3 KB | numpy rig tooling (rig.py = skin Meshy riders to 91-joint skeleton + springs; caali_* rebind/arms/shoulder fixes; anika_* sym/skirt; glb.py IO; sandbox.py validator) | Rydah Rigger | tool |
| `code/rigwork/caali_shoulder.py` | 2 KB | numpy rig tooling (rig.py = skin Meshy riders to 91-joint skeleton + springs; caali_* rebind/arms/shoulder fixes; anika_* sym/skirt; glb.py IO; sandbox.py validator) | Rydah Rigger | tool |
| `code/rigwork/decode.mjs` | 0 KB | numpy rig tooling (rig.py = skin Meshy riders to 91-joint skeleton + springs; caali_* rebind/arms/shoulder fixes; anika_* sym/skirt; glb.py IO; sandbox.py validator) | Rydah Rigger | tool |
| `code/rigwork/glb.py` | 3 KB | numpy rig tooling (rig.py = skin Meshy riders to 91-joint skeleton + springs; caali_* rebind/arms/shoulder fixes; anika_* sym/skirt; glb.py IO; sandbox.py validator) | Rydah Rigger | tool |
| `code/rigwork/joints.py` | 0 KB | numpy rig tooling (rig.py = skin Meshy riders to 91-joint skeleton + springs; caali_* rebind/arms/shoulder fixes; anika_* sym/skirt; glb.py IO; sandbox.py validator) | Rydah Rigger | tool |
| `code/rigwork/main.py` | 9 KB | numpy rig tooling (rig.py = skin Meshy riders to 91-joint skeleton + springs; caali_* rebind/arms/shoulder fixes; anika_* sym/skirt; glb.py IO; sandbox.py validator) | Rydah Rigger | tool |
| `code/rigwork/pg.py` | 0 KB | numpy rig tooling (rig.py = skin Meshy riders to 91-joint skeleton + springs; caali_* rebind/arms/shoulder fixes; anika_* sym/skirt; glb.py IO; sandbox.py validator) | Rydah Rigger | tool |
| `code/rigwork/rig.py` | 10 KB | numpy rig tooling (rig.py = skin Meshy riders to 91-joint skeleton + springs; caali_* rebind/arms/shoulder fixes; anika_* sym/skirt; glb.py IO; sandbox.py validator) | Rydah Rigger | tool |
| `code/rigwork/sandbox.py` | 1 KB | numpy rig tooling (rig.py = skin Meshy riders to 91-joint skeleton + springs; caali_* rebind/arms/shoulder fixes; anika_* sym/skirt; glb.py IO; sandbox.py validator) | Rydah Rigger | tool |
| `code/rigwork/sb2_anika-npc.json` | 2 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/rigwork/sb2_anika-npc.quest-ktx2.json` | 2 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/rigwork/sb2_anika-npc.quest.json` | 2 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/rigwork/sb2_anika-rider.json` | 2 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/rigwork/sb2_anika-rider.quest-ktx2.json` | 2 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/rigwork/sb2_anika-rider.quest.json` | 2 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/rigwork/sb2_caali-g-v2-hd.rigged.json` | 2 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/rigwork/sb2_caali-g-v2.quest-ktx2.rigged.json` | 2 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/rigwork/sb2_caali-g-v2.quest.rigged.json` | 2 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/rigwork/sb2_caali-g-v2.rigged.json` | 2 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/rigwork/sb3_bad.json` | 3 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/rigwork/sb3_new.json` | 2 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/rigwork/sb3_newhd.json` | 2 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/rigwork/sb3_newk.json` | 2 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/rigwork/sb3_newq.json` | 2 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/rigwork/sb3_nolock.json` | 2 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/rigwork/sb3_pre.json` | 2 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/rigwork/sb4_anika-npc.json` | 2 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/rigwork/sb4_anika-npc.quest-ktx2.json` | 2 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/rigwork/sb4_anika-npc.quest.json` | 2 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/rigwork/sb4_anika-rider.json` | 2 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/rigwork/sb4_anika-rider.presym-20261030-0331.json` | 3 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/rigwork/sb4_anika-rider.quest-ktx2.json` | 3 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/rigwork/sb4_anika-rider.quest-ktx2.presym-20261030-0331.json` | 3 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/rigwork/sb4_anika-rider.quest.json` | 2 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/rigwork/sb_anika-npc.json` | 2 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/rigwork/sb_anika-npc.quest-ktx2.json` | 2 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/rigwork/sb_anika-npc.quest.json` | 2 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/rigwork/sb_anika-rider.json` | 2 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/rigwork/sb_anika-rider.quest-ktx2.json` | 2 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/rigwork/sb_anika-rider.quest.json` | 2 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/rigwork/sb_caali-g-v2-hd.json` | 2 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/rigwork/sb_caali-g-v2.json` | 2 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/rigwork/sb_caali-g-v2.quest-ktx2.json` | 2 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/rigwork/sb_caali-g-v2.quest.json` | 2 KB | Sandbox validation report for a rigged GLB (bind/skin/limits) | Rydah Rigger | report |
| `code/tests/combat_poses.py` | 24 KB | Playwright combat pose harness: events on frames, limits, slew, plant, draws, srFX, crew specials. Local-only persona cases removed | Rydah Rigger | live test (edited for public) |
| `code/tests/skate_floor_probe.py` | 8 KB | Playwright probe: wheel-bottom vs deck per foot, skate_fit dump | Rydah Rigger | live test |
| `docs/anika-rig-plan.md` | 6 KB | Rigger plan/spec doc | Rydah Rigger | doc |
| `docs/caali-g-rerig-plan.md` | 3 KB | Rigger plan/spec doc | Rydah Rigger | doc |
| `docs/combat-anim-plan.md` | 23 KB | Rigger plan/spec doc | Rydah Rigger | doc |
| `docs/meshy-prompts-crews.md` | 21 KB | Rigger plan/spec doc | Rydah Rigger | doc |
| `shots/combat/anika_finisher_hit_front34.png` | 740 KB | Representative screenshot | Rydah Rigger | reference |
| `shots/combat/anika_heavy_hit_front34.png` | 745 KB | Representative screenshot | Rydah Rigger | reference |
| `shots/combat/anika_knockdown_front34.png` | 738 KB | Representative screenshot | Rydah Rigger | reference |
| `shots/combat/anika_light1_hit_front34.png` | 742 KB | Representative screenshot | Rydah Rigger | reference |
| `shots/combat/anika_react_heavy_front34.png` | 744 KB | Representative screenshot | Rydah Rigger | reference |
| `shots/combat/caali_finisher_hit_front34.png` | 739 KB | Representative screenshot | Rydah Rigger | reference |
| `shots/combat/caali_heavy_hit_front34.png` | 740 KB | Representative screenshot | Rydah Rigger | reference |
| `shots/combat/caali_knockdown_front34.png` | 736 KB | Representative screenshot | Rydah Rigger | reference |
| `shots/combat/caali_light1_hit_front34.png` | 743 KB | Representative screenshot | Rydah Rigger | reference |
| `shots/combat/caali_react_heavy_front34.png` | 735 KB | Representative screenshot | Rydah Rigger | reference |
| `shots/combat/tune_before_after.png` | 1208 KB | Representative screenshot | Rydah Rigger | reference |
| `shots/hero/anika_ingame_34.png` | 809 KB | Representative screenshot | Rydah Rigger | reference |
| `shots/hero/caali_v2_ingame_34.png` | 804 KB | Representative screenshot | Rydah Rigger | reference |
| `shots/hero/skate_v2_scale_after.png` | 768 KB | Representative screenshot | Rydah Rigger | reference |
| `shots/hero/skate_v2_wired_after_player_34.png` | 2771 KB | Representative screenshot | Rydah Rigger | reference |
| `shots/rig/anika_34.png` | 148 KB | Representative screenshot | Rydah Rigger | reference |
| `shots/rig/anika_braids_crouch.png` | 205 KB | Representative screenshot | Rydah Rigger | reference |
| `shots/rig/anika_npc_pose_sheet.png` | 265 KB | Representative screenshot | Rydah Rigger | reference |
| `shots/rig/anika_pose_sheet.png` | 265 KB | Representative screenshot | Rydah Rigger | reference |
| `shots/rig/anika_twist_test.png` | 195 KB | Representative screenshot | Rydah Rigger | reference |
| `shots/rig/caali_v2_34.png` | 250 KB | Representative screenshot | Rydah Rigger | reference |
| `shots/rig/caali_v2_arms_before_after_grind_34.png` | 358 KB | Representative screenshot | Rydah Rigger | reference |
| `shots/rig/caali_v2_hd_pose_sheet.png` | 449 KB | Representative screenshot | Rydah Rigger | reference |
| `shots/rig/caali_v2_pose_sheet.png` | 447 KB | Representative screenshot | Rydah Rigger | reference |
| `shots/rig/caali_v2_twist_test.png` | 321 KB | Representative screenshot | Rydah Rigger | reference |
| `shots/skate-v2/ab_default_8.7.png` | 618 KB | Representative screenshot | Rydah Rigger | reference |
| `shots/skate-v2/ab_notint-1_8.7.png` | 601 KB | Representative screenshot | Rydah Rigger | reference |
| `shots/skate-v2/ktx2_ab.png` | 221 KB | Representative screenshot | Rydah Rigger | reference |
| `shots/skate-v2/lodpop_ab.png` | 1521 KB | Representative screenshot | Rydah Rigger | reference |
| `shots/skate-v2/offset_after_player.png` | 1594 KB | Representative screenshot | Rydah Rigger | reference |
| `shots/skate-v2/probe_player_feet.png` | 586 KB | Representative screenshot | Rydah Rigger | reference |
| `shots/skate-v2/scale_after_npc.png` | 802 KB | Representative screenshot | Rydah Rigger | reference |