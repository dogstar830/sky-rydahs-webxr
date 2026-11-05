# Caali G re-rig handoff: new Meshy mesh → shared skeleton (Rydah Rigger, 2026-10-30)
Forge is regenerating Caali G. The new mesh rebinds to shared/skeleton/rider-skeleton.glb, which was derived from caali-g-hd.glb, so his bones are already the reference.
Caali stays **Code : E**. Gr8yzone is his shirt brand. Wheel glow stays gold **0xffd700** (Oliver confirmed).

## What must stay the same
- Height ref **1.916 m**. He is the scale reference for every rider. Root scale 1.0, Y up, +Z forward, grounded at y=0 in skates.
- Joint names, hierarchy and rest pose as in rider-skeleton.bones.json, including the 4 twist bones (`mixamorig:{Left,Right}{ArmTwist,ForeArmTwist}`), AT_L/AT_R and the 20 sockets.
- Feel row `RIDER_FEEL['caali-g']` (the controlled-power row) and RIDER_JOINT_LIMITS, both unchanged.
- The gold phoenix back patch (`crew-logos/caali-g-patch*.png`) is placed by the key `caali-g`, so keep `key:'caali-g'` and keep the upper-back area flat and unoccluded for the decal.
- Wardrobe slots, `wardrobe/slots.json` and `riders/caali-g.outfit.json`: hair, top, jacket, pants, gloves, neck, accessory, skates (`at-skate-meshy`), head. Keep the same slot names and material and mesh naming, so wardrobe.js swaps still resolve (the Caali worker owns wardrobe.js).
- `_WC` and float POSITION rules: POSITION stays float with no KHR_mesh_quantization or meshopt (riders.js rMerge concatenates raw arrays). Any `_WC` wheel-centre attribute must be in the same space and units as POSITION. Run deinterleave.py after export.
- File names `caali-g.glb`, `caali-g.nonormal.glb` and `caali-g-hd.glb` stay as tiered by the existing loader.

## What changes versus the current wardrobe caali-g.glb
- New topology, UVs and textures from Meshy, with new weights painted from scratch on the shared skeleton. Do not transfer the old weights blindly across differing topology.
- Proportions may shift slightly. If so, re-snap the joint heads to the new landmarks, then re-normalise to 1.916 m. Bone names and rolls do not change.
- LOD targets for the player: LOD0 100–120k, LOD1 40k, LOD2 15k.

## Handoff checklist (Forge worker → Rigger)
1. [ ] Deliver the mesh in T-pose or A-pose at 1.916 m, feet flat, facing +Z, split into the wardrobe slot materials listed above.
2. [ ] Rigger snaps shared joints to the mesh (rest-pose deviation ≤1 mm after re-normalising), then auto-weights and does a hand pass (twist gradients, knuckles, elbow and knee, chains rigid on the Hips).
3. [ ] At most 4 weights per vertex. Float POSITION. `_WC` in POSITION space. Deinterleaved.
4. [ ] Write to a staging path `wardrobe_build/staging/caali-g.new.glb` (Caali worker's dir), not over the live files, until sign-off.
5. [ ] Node check: ikki_skate poser binds with all 65 + 4 twist joints found, and every state stays within the limits and the 720°/s slew.
6. [ ] Hero render (standard 1920x1080 @1.5, tier=hd, FX on, ≥60 frames): front, back (phoenix patch reads), side in crouch, kick, polegrind_climb, plus a twist test at forearm roll ±90°.
7. [ ] Draws: player ≤5, 1 skate draw with gold glow.
8. [ ] Oliver signs off, then the Caali worker swaps the live files and Rigger re-runs the limit check.
