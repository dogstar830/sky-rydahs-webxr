# Simca spring bones (Rydah Rigger, 2026-11-05)

These live in `simca-rider*.glb` and `simca-npc*.glb` as extra joints after the shared 91 (joints 91..154 = 64 hair bones). Bone axis is +Y (head → tail). Each node has `extras.spring {chain,index,kind,tail,...}`, and `skins[0].extras.springChains` holds the solver params.

## Extra joint (Forge export)

- Forge shipped **92 joints = shared 91 + `neutral_bone`** (Blender leftover under `RiderArmature`, −90° X).
- **Not harmless:** ~30k verts (hair + body) were weighted 1.0 to it. Rigger remapped those weights to the next-best influence / nearest skeleton bone and **removed `neutral_bone` from the skin**. Post-rig joint count before springs = 91.

## Hair chains (8 locks × 8 bones)

| chain | parent | bones | bind length |
|---|---|---|---|
| Simca_HairBack_00..05 | mixamorig:Head | `_01.._08` | ~1.05–1.18 m |
| Simca_HairSideL_06 / HairSideR_07 | mixamorig:Head | `_01.._08` | ~1.11–1.16 m |

- Kind: **`braid`** (same solver defaults as Anika: stiffness 60 / root 90, damping 0.35, gravity 1, drag 0.3, maxSwing 70°, maxLink 35°).
- Root lock: top 8 % rigid to Head; then smoothstep along the lock centreline (≤2 influences). Cap + goggles stay on the body mesh (Head-weighted; not in the hair locks).
- LOD0 / LOD1 / LOD2 all weighted (NPC uses `*_NPC0`). Colliders noted in extras: Neck, Spine2 r.13, Hips r.12, Shoulders r.07, UpLegs r.085 (long hair torso/shoulder/back). Runtime uses `RIDER_SPRING_COLL` in `ikki_skate` (Hips/Spine2/thighs/shins); shoulder spheres are documented for a future solver bump — do **not** edit `ikki_skate*.js` until promotion.
- Mesh names: `Simca_HairBack_00..05_LOD{0,1,2}`, `Simca_HairSideL_06_LOD{0,1,2}`, `Simca_HairSideR_07_LOD{0,1,2}` (+ NPC0). Rings on LOD0 ≈ 103–123 along the centreline (Forge target 103–117).

## Weight fixes

- Export was clamped to 4 influences. Finger chains were mostly collapsed into ForeArm/Hand (Index/Middle/Ring often 0 verts). Rigger re-painted hand-prox verts onto digit bone segments; tip `*4` joints now receive distal weight from `*3`.
- Toes stay rigid on Foot (A·T skate shell). ToeBase / Toe_End intentionally unused.

## Files / script

- Script: `/workspace/rigwork/simca/simca_springs.py`
- Backups: `*.prerig-20261105-1245.glb`
- Strip: `/workspace/shots/rig/simca_spring_strip.png` (offline Verlet kick/turn; visible swing, hollow at torso = colliders holding)
- Validate: gltf-transform / gltf-validator **0 errors** on all 6 variants (rider/npc × base/quest/quest-ktx2). Draco + webp/KTX2 kept; POSITION near-float (qPos 16, same as quest_pipeline).
