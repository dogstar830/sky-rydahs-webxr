# Air Treck skate v2 — Rydah Forge, 2026-10-30

## Files (written next to the originals; v1 untouched)
- `skyrydahs-characters/wardrobe/skates/at-skate-meshy.v2.glb`: module. Same node layout as v1: `Skate_LOD0..2` > `ShellBlend_L{i}`, `Wheel_F_L{i}` and `Wheel_R_L{i}`, plus the 20 sockets (copied verbatim from v1).
- `skyrydahs-characters/wardrobe/skates/at-skate-meshy.merged.v2.glb`: both feet. Nodes 0-24 are copied verbatim from v1 (RiderArmature, foot bones, `*_AT_Root`, 20 sockets). The skin and IBM come from v1.
- `skyrydahs-characters/shared/at-skate/at-skate-meshy-v2-1k.png`, `-mr.png` and `-normal.png`: a NEW texture set. **The v2 UVs only match these textures, not `at-skate-meshy-1k*`.**
- Both GLBs use Draco (float positions, no `KHR_mesh_quantization`), are de-interleaved (no `byteStride`), and validate with 0 errors.

## Cause of the shards
v1 `ShellBlend_L0` is 1,352 tris in **242 disconnected open fragments**, even after welding vertices at 0.5 mm: 1,666 boundary edges in total, with no non-manifold edges and consistent winding. The wheels are 32 and 51 fragments. The source `meshy/airtreck-meshy.glb` is watertight (0 boundary edges after welding 1e-5), so the damage came from the v1 reduction step: decimating a mesh that wasn't welded (split at UV seams) breaks it into separate surfaces that pull apart. No double layer is involved. The old 1K texture was baked onto those fragments.

## What changed
- Shell: the source's left skate was registered to v1 module space (ICP with scale, median error about 3.5 mm). I then cut out the source wheels, welded and decimated the shell, and rebaked colour, MR and normal at 1K from the 1.8M source. The result is 1 large closed piece plus a few small closed parts. The only open edges are where the wheels were cut out, and the new wheels cover them.
- Wheels: modelled procedurally. Each has a tyre, a cyan rim band on both faces (glow via cyan texels; the shader's `cy` detector is unchanged), a gold hub ring with 5 spokes per side, gold hub caps and an axle.
  - The wheel nodes now sit on the TRUE axle centres measured from the source: F `(0,-0.0425,0.0895)` and R `(0,-0.0485,-0.1715)`, in glTF metres. v1 had `(0,-0.051,0.0778)` and `(0,-0.046,-0.1739)`, which are off by up to 12 mm. Wheel radii are F 0.0725 and R 0.0685.
  - In merged, `_WC` follows the new centres.
- UV layout: the shell islands use v in [0, 0.93] (glTF). The bottom 72 px rows (glTF v > 0.93) hold a 4-cell palette strip: u 0-0.25 tyre (28,28,30), 0.25-0.5 gold (196,168,84), 0.5-0.75 cyan rim (0,229,255), 0.75-1 tyre.
- Masks: same rules as v1.
  - COLOR_0 (u8 normalised): R = shell at glTF y >= -0.02, G = shell below that (frame), B = all wheel geometry. A = 255.
  - COLOR_1 (u16 normalised) uses the same legacy-flag values as v1: wheel (0.75,1,0,1) and shell (0.6875,0,0,1).
  - `_WC`, `JOINTS_0` (0 = LeftFoot, 1 = RightFoot), `WEIGHTS_0` (1,0,0,0) and the skin all work as in v1.
- Tris per foot (budget 9k/3k/750):

  | LOD | Shell | Wheels | Total per foot |
  |---|---|---|---|
  | LOD0 | 7,200 | 2 x 912 | 9,024 |
  | LOD1 | 2,200 | 2 x 432 | 3,064 |
  | LOD2 | 559 | 2 x 60 | 679 |

  merged: 18,048 / 6,128 / 1,358 for both feet. Sizes: module 105 KB, merged 192 KB.

## Gold hubs need one shader line (the asset can't do it alone)
The live shader sets `diffuse = slot * luma`, with the B mask as `uCrewWheel`. Any texture hue is discarded, so the hubs render in the crew wheel colour, as v1 did. The gold texels were picked so they DON'T trip the red-glow detector (r - max(g,b) = 0.11 < 0.12). To show gold, add this to `SR_SKATE.obc` after the `slot` line:
```
float au=smoothstep(.25,.4,t.r-t.b)*smoothstep(.55,.7,t.r)*(1.-atGm); diffuseColor.rgb=mix(diffuseColor.rgb,t,au);
```
It detects gold by texel hue, so it works for both the module and merged paths without any attribute change. The gold palette cell's MR is metal 1, rough 0.3.

## Scale proposal (live scale NOT changed)
Measured on the ref (`caali-anika-ref2-day-clean.jpg`, Anika's near skate): floor to cuff top 213 px, floor to knee 313 px, ratio **0.68**. Boot width is about 1.3x mid-calf width.
Rig (`rider-skeleton.bones.json`): knee (LeftLeg) y 0.566, ankle (LeftFoot) y 0.213. The skate in merged runs from y -0.021 (wheel bottom) to 0.318 (cuff), a ratio of **0.57**.
Scaling the skate by s about the ankle pivot (wheel bottom is 0.236 m below the pivot, cuff is 0.10 m above) gives ratio = 0.336s / (0.236s + 0.353):

| s | Ratio |
|---|---|
| 1.00 | 0.57 |
| 1.20 | 0.64 |
| **1.25** | **0.65** |
| 1.30 | 0.66 |
| 1.37 | 0.68 (literal ref) |

**Proposal: 1.25x** (range 1.2-1.3). The ref's low, close camera exaggerates the near skate, so 1.37 would overshoot from the game camera.

Effects at s = 1.25:
- **Rider ground offset:** +0.236 x 0.25 = **+0.059 m** (1.3x: +0.071 m). The rider's hips and root must be lifted by this amount, or the wheels sink into the floor.
- **Module / v2.glb:** scale about the ankle pivot `[0,0.12,-0.06]` (bones.json `ankle_pivot_in_skate_mesh`), i.e. p' = pivot + s(p - pivot) for vertices, wheel node translations and socket translations. The pivot value itself stays the same.
- **merged:**
  - `*_AT_Root` nodes and the skin IBMs are unchanged.
  - Scale vertex positions and `_WC` around each foot's root position by s.
  - Multiply each socket node's local translation by s.
- **`shared/skeleton/rider-skeleton.glb`:** no bone change is needed (the skate is rigid on the foot). Record the +0.059 m ground offset (e.g. as a `skate_ground_offset` field next to `ankle_pivot_in_skate_mesh` in bones.json). Any IK or floor clamp that assumes wheel bottom = 0.236 m below the ankle should use 0.236s.
- **Fit path (`crewSkates`, Forge 19-bone crews):** it fits the skate to the old toon-skate box, so it needs k *= s and ky *= s plus the same lift.

## What Rigger must do to swap in
1. Set `SR_SKATE.url` to `at-skate-meshy.v2.glb` and `SR_SKATE.tex` to `shared/at-skate/at-skate-meshy-v2-1k`. Both GLB and textures must switch together, because the UVs only match the v2 set.
2. In `srSkateHalves` and `srSkateMerged`, load `at-skate-meshy.merged.v2.glb`.
3. Draco: these are Draco files, so `srSkateSource` and `srSkateHalves` must call `setDRACOLoader(window.SR_DRACO)`; they currently use a bare `GLTFLoader`. The `.quest` variant can simply be the same file.
4. Optional: add the gold-hub shader line above.
5. Optional: apply the scale proposal in a later pass (Rigger owns the ankle offset and grounding).
