# Shared rider skeleton (Rydah Rigger, 2026-10-29)
Files: `rider-skeleton.glb` (91 joints, rest = bind, 4-tri hip proxy so loaders build a THREE.Skeleton), `rider-skeleton.blend` (Blender 4.3.2 import of the same GLB), `rider-skeleton.bones.json` (per bone: name, parent, local t/r/s, bind world position, inverse bind matrix, kind).

## Source
Read-only from `wardrobe/riders/caali-g-hd.glb`, skin `SmartRigArmature` (70 joints). Its rest pose equals its bind pose (max |W·IBM − I| = 5e-6). The bones were copied from inverse(IBM), so the shared asset is exactly Caali G's bind. `headfront` (a non-Mixamo helper) is dropped.

## Bones (91)
- 65 standard Mixamo `mixamorig:*`: Hips…HeadTop_End, full 4-joint finger chains, Toe_End.
- 4 twist bones named as in caali-g-hd: `mixamorig:LeftArmTwist`/`RightArmTwist` (child of *Arm, about 0.08–0.09 m down the upper arm) and `mixamorig:LeftForeArmTwist`/`RightForeArmTwist` (child of *ForeArm, about 0.10 m, mid-forearm). Their rest rotation is identity relative to the parent, so the roll axis = the parent's +Y (the bone axis). Skin with about 50% roll share (bible §0.2) so arms don't candy-wrapper under PBR shading.
- 2 A-T roots: `L_AT_Root` (child of LeftFoot), `R_AT_Root` (child of RightFoot). Each sits at the ankle pivot = the foot bone origin and is world-aligned in bind (+Z forward, +Y up), as the skate root should be per at-standard-spec §1.
- 20 A-T sockets `L_at_*` / `R_at_*` (cuff, ankle_out, ankle_in, heel, toe, wheel_cover_out, motor, exhaust, emblem, led). They are children of the matching AT root. Socket +Y = surface normal, scale 1.

## Units, axes, bind pose, height
- Metres, +Y up, the rider faces +Z, **+X = the rider's LEFT**. The spec text says "−X for L"; the physical outer side wins, so `L_at_ankle_out` points +X.
- Bind pose: Caali G A-pose. Hips (0.009, 0.978, 0.004), LeftFoot (0.175, 0.213, −0.029), HeadTop_End y 1.696.
- **Height reference 1.916** (runtime `SR_CAALI_REF_H`): riders are scaled so `refH` = 1.916 game units, the Forge Caali bbox height that Caali G was fitted at. The native skeleton is 1.70 m class (bible "M" preset).

## Skate mapping
`wardrobe/skates/at-skate-meshy.glb` mesh space → AT root space: subtract the ankle pivot A = (0, 0.12, −0.06) and mirror X for the R foot. The same 20 sockets also live in that GLB as empties under `Skate_LOD0` in mesh space; they differ from the skeleton sockets by exactly A.

## How redesigned riders bind
1. Author or skin the garments in Blender on `rider-skeleton.blend` (link the armature; don't edit it). Keep the joint names exactly. Use ≤4 weights.
2. Export with the full joint list in this order (bones.json order) so skins can share one Skeleton at runtime.
3. Skates are not skinned in garment files. At runtime the shared skate binds rigid: weight 1 to `mixamorig:LeftFoot` / `RightFoot` (spec §1: shell rigid, toe 0%). Add-ons bake their socket matrix (from bones.json, AT-root space) into the skate geometry.
4. Twists: the poser (`ikki_skate.js`) puts a share of the forearm roll onto `*ForeArmTwist` and of the upper-arm roll onto `*ArmTwist` when present. Without them it falls back to the old behaviour.
5. Proportion presets (M, slim ×0.92 etc.) are bone scales applied at load. The bind data here stays untouched.

## A-T skate scale + ground offset (Rydah Rigger, 2026-10-30)
- Runtime skate scale `SR_SKATE_SCALE = 1.25` (jackets.js; set to 1 to revert), per Forge perf/forge/at-skate-v2.md (2 big wheels ruling). The skate GLBs and this skeleton are unchanged; the scale is applied at load.
- Module/v2.glb: scaled about the ankle pivot (0, 0.12, -0.06) in skate mesh space (vertices + sockets). Merged: vertices and `_WC` scaled about each foot's `*_AT_Root` bind position; socket local offsets from the AT root x s.
- `skate_ground_offset` (updated 2026-10-30 04:xx CDT): Forge moved the v2 skate GLBs up +24.16 mm (sockets moved with it; module md5 7c020dd3..., merged md5 e829857e...), so the bind wheel bottom is 0 at 1x. At 1.25x the rider lift is **+0.0532 m** (`SR_SKATE_LIFT`, = 0.25 x LeftFoot bind y 0.21284). Doc nominal was +0.059.
- Per-side skate offset `SR_SKATE_SIDE_DY = {L: 0, R: -0.0105}` m, applied to the R skate half verts, `_WC` and R sockets, not the rider. Cause: in this skeleton's bind (Caali G A-pose) RightFoot sits at y 0.22337 vs LeftFoot 0.21284 (+10.53 mm). The merged skate's foot roots copy that, so after scaling about each root plus one body lift the R wheels floated 10.5 mm. rider-skeleton.glb is NOT changed; if the bind is ever levelled, set R to 0.
- Measured at bind (sandbox, 1.25x): L wheel bottom -0.01 mm, R -0.00 mm.
- Forge 19-bone fit path: k and ky x s, skate dropped by (s-1) x (ankle bind y - old skate bottom) and the rider lifted by the same amount.
- IK / floor clamps that assume the wheel bottom is 0.236 m below the ankle should use 0.236 x s.
