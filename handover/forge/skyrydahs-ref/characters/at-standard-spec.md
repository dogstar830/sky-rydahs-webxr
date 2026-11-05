# Standard Air Trek (A-T) Spec v1 (Rydah Forge, 2026-10-29)

> **Rig notes (Forge-confirmed 04:55 CDT, from Rydah Rigger's build):** 'out' sockets sit on the PHYSICAL outer side of each foot (+X on the left foot in the rig), not the −X noted below. The skate-origin-to-ankle offset lives in `shared/skeleton/rider-skeleton.glb` and `at-skate-meshy.merged.glb`; the original mesh is unmoved. The 4 colour slots are implemented as 3 mask channels plus glow from texels, with a separate `uCrewWheel` uniform.
One mesh on every rider. Identity = (a) crew colours on 4 fixed slots + (b) optional bolt-on add-ons on fixed sockets. No logos on the skate (emblem plate shows a crew *shape*, not text).

## 1. Mesh
- Runtime: `skyrydahs-characters/wardrobe/skates/at-skate-meshy.glb` · source: `skyrydahs-characters/meshy/airtreck-meshy.glb`.
- Look (AAA e-blade): black armored shell, oversized boot, 4 inline wheels with **hub motors**, rear motor/battery pod, side **LED strips**, glowing wheel rims, strap buckles. No more Forge toon skates (`*_skates` in `<crew>-rider.glb` are retired → fixes audit M1/M2/M11).
- Budget: 2 skates ≤ 18k tris LOD0 (inside the hands+A-T 25–30k), add-ons ≤ 4k extra per rider total; LOD1 6k, LOD2 1.5k (add-ons dropped at LOD2).
- Skinning: each skate rigid-bound 100% to `mixamorig:LeftFoot` / `RightFoot` (toe-wheel section to `*ToeBase` 0%: shell is rigid). Skate root origin = ankle pivot; +Z forward, Y up, units m.

## 2. Sockets (empties in the GLB, children of skate root; mirrored L/R, names prefixed `L_`/`R_`)
| Socket | Parent | Local transform intent |
|---|---|---|
| `at_cuff` | skate root (→Foot) | top rim of boot cuff, ~0.16 m up, faces +Y; cuff armor, collars |
| `at_ankle_out` | skate root | outer ankle, +X out (−X for L), normal outward; fins, wing plates, ear fins |
| `at_ankle_in` | skate root | inner ankle (keep ≤ 8 mm proud: legs cross) ; small plates only |
| `at_heel` | skate root | rear heel above last wheel, faces −Z; spoilers, spurs, crow fin |
| `at_toe` | skate root | toe cap front, faces +Z; toe guards, horns |
| `at_wheel_cover_out` | skate root | frame outer face centred on wheel line, +X; wheel covers/housings |
| `at_motor` | skate root | rear motor pod; motor housings, bolt kits |
| `at_exhaust` | skate root | behind/below motor pod, −Z; exhaust/thrusters (VFX ion-trail emitter too) |
| `at_emblem` | skate root | outer shell side panel, flat, 60×40 mm; emblem plates |
| `at_led` | skate root | LED strip line (reference only; no parts) |
Scale 1 at socket; add-ons authored in socket space so one file fits both feet (mirror X for L).

## 3. Colour slots (one shader, `M1 at_skate`)
Existing API (ikki_skate.js / wardrobe.js): `rider.setLoadout({paint, frame, wheel, glow})` → uniforms `uPaint, uFrame, uWheel, uGlowC`; `setWheelGlow(hex)` = glow only; `equip('skates')` is a no-op (module fixed).
Slot masks are baked into **COLOR_0** of the skate and every add-on so merged geometry keeps working:
| Slot | COLOR_0 | Shader | Default |
|---|---|---|---|
| `paint` (shell/highlight) | R=1 | albedo × uPaint | #0B0B0D black shell for all crews |
| `frame` (accent: frame rails, trim, add-on plates) | G=1 | albedo × uFrame | crew accent |
| `wheel` (tyres/hubs) | B=1 | albedo × uWheel | crew dark |
| `glow` (LED strips, wheel rims, add-on light lines) | A=1 | emissive = uGlowC × (1+uBoost) | crew glow |
Rule: albedo texture for the skate stays near-white/grey in masked areas so the multiply gives the exact hex. Per-crew values are the `paint/frame/wheel/glow` lines in `character-bible.md`; source table: `chars/crew-loadouts.json` (PROPOSED new file, generated from the bible, not from jacket-colorways.json).

## 4. Add-on merge (keeps 1 draw call per rider skate)
At load: for each add-on in the rider's `atAddons` list, clone geometry, apply socket world matrix in skate space, set skinIndex/skinWeight to the skate's foot bone, then `THREE.BufferGeometryUtils.mergeBufferGeometries([skate, ...addons])` (r128 examples/js) → one SkinnedMesh, `M1` material, shared atlas region (add-ons UV into a reserved 512×512 corner of the skate 1024 texture). Cache merged geometry per crew (NPCs of a crew share it). Add-ons: no own materials, no textures of their own, Draco-compressed in `wardrobe/skates/addons/<id>.glb`.

## 5. Add-on catalog (tris = per foot, both feet ×2)
| Crew | id | Socket | Tris/foot | Notes |
|---|---|---|---|---|
| Code : E | `ce_gold_cuff_armor` | at_cuff | 500 | filigree-relief ring, frame slot gold |
| Code : E | `ce_wheel_covers_filigree` | at_wheel_cover_out | 700 | open lattice, glow line |
| Code : E | `ce_emblem_plate` | at_emblem | 150 | lightning shape |
| Kogarasumaru | `kg_crow_fin` | at_heel | 400 | swept feather fin |
| Kogarasumaru | `kg_wing_spoiler` | at_cuff (rear) | 500 | Ikki only |
| Kogarasumaru | `kg_flame_exhaust` | at_exhaust | 450 | Kazu; twin nozzles, glow inner |
| Kogarasumaru | `kg_fang_wheel_housing` | at_wheel_cover_out | 900 | Akito; heavy full cover |
| Kogarasumaru | `kg_cuff_armor` | at_cuff | 400 | Akito |
| Static Angels | `sa_wing_fins` | at_ankle_out | 600 | 3-feather wing plate |
| Anubis | `an_jackal_ear_fins` | at_ankle_out | 450 | twin pointed ears |
| Anubis | `an_gold_emblem_plate` | at_emblem | 150 | ankh-free jackal profile |
| Sleeping Forest | `sf_bark_cuff_plates` | at_cuff | 500 | wood-grain via normal only |
| Behemoth | `bh_bull_horn_toe_guards` | at_toe | 600 | |
| Behemoth | `bh_heavy_cuff_armor` | at_cuff | 600 | |
| Genesis | `gn_sunburst_wheel_covers` | at_wheel_cover_out | 700 | ray pattern, glow core |
| Genesis | `gn_gold_spoiler` | at_heel | 400 | |
| Tool Toul To | `tt_exposed_bolt_motor_housing` | at_motor | 800 | bolts, pipes, mismatched plate |
| Volt | `vt_bolt_fins` | at_ankle_out | 450 | forked (not single zigzag) |
| Rust Claw | `rc_claw_heel_spurs` | at_heel | 500 | 3 curved spurs |
Max per rider: Code : E 1,350/foot = 2.7k (largest; within ≤4k).

## 6. Done when
Every rider in the build uses `at-skate-meshy.glb`; no per-crew skate meshes remain; glow hexes match the bible exactly; skates attach to feet (no float).

> **Wheel ruling (Oliver, 2026-10-30 02:58 CDT):** every rider keeps the 2 big Air Gear-style wheels per boot (not the 4 inline wheels in the Caali/Anika ref). Skate v2 at `wardrobe/skates/at-skate-meshy.v2.glb`, scale 1.25x about the ankle pivot, rider lift +0.059 m.
