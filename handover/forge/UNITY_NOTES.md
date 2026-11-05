# Unity Port Notes — Rydah Forge handover

For converting Sky Rydahs WebXR (Three.js r128) character/FX work into the Unity flagship build.

## Skeleton

- **v2 riders (Caali G, Anika, shared redesign path):** Mixamo-based **91 joints** (Caali G live). Anika ships with **107 joints** = 91 shared + braid/skirt spring bones (`Anika_Braid*`, `Anika_Skirt_*`; springs solver still WIP in Rigger).
- **Akito (local-only placeholder):** **66-joint** skin (Air Gear placeholder). Keep out of public until renamed; do not import Akito GLBs from this handover (they are not packaged).
- Bind reference: `skyrydahs-characters/shared/skeleton/rider-skeleton.glb` (+ `.blend`, `.bones.json`).
- Import Mixamo humanoid (or equivalent) and map spring bones as additional non-humanoid transforms / Unity spring bones.

## A-T skate socket spec + scale

- Spec: `skyrydahs-ref/characters/at-standard-spec.md`.
- Runtime modules: `wardrobe/skates/at-skate-meshy.v2.glb` (per-foot module) and `at-skate-meshy.merged.v2.glb` (both feet, 1 draw).
- Sockets (empties, L_/R_ mirrored): `at_cuff`, `at_ankle_out`, `at_ankle_in`, `at_heel`, `at_toe`, `at_wheel_cover_out`, `at_motor`, `at_exhaust`, `at_emblem`, `at_led`.
- **Scale 1.25× about the ankle pivot**; per-rider ground lift historically `SR_SKATE_LIFT` ≈ **+0.059 m** (Rigger also used 0.0532 with side DY for skeleton asymmetry). Bake or apply as parent scale + local Y lift per rider Foot height.
- Colour slots (COLOR_0 masks): paint (R), frame (G), wheel (B), glow (A) → crew loadout uniforms.
- Oliver wheel ruling: **2 big Air Gear-style wheels per boot** (v2), not 4 inline.

## Material / shading (Option 3)

- Oliver: **Option 3 stylized realistic PBR** — rim/fresnel, hair spec, **no outline / no cel**.
- Web module: `rider_style.js` behind `?riderstyle=opt3` (not yet in default `build_ikki.sh`). Constraints: `v3build/perf/rider-style-opt3-constraints.md`.
- Unity: Standard/URP Lit (or custom) with:
  - Albedo + ORM (metallic/roughness/AO); normal on HD only (quest = noNormal).
  - Fresnel rim (use geometric normal, not normal-map perturbed).
  - Hair anisotropic/spec lobe capped so pre-tonemap luma stays &lt; ~0.85 (bloom-safe).
  - **Crew colour slots** on body + skate (paint/frame/wheel/glow) as material property blocks / HDRP diffusion profile equivalents.
  - Share one environment reflection probe (day/night), do not instance PMREM per rider.

## CombatFX event API + per-crew palettes

- Source: `v3build/combat_fx.js`, doc `v3build/perf/forge/combat-fx.md`.
- Primary entry: `CombatFX.emit(evt, data)` → also drives `SR_PAD.haptic` unless `haptics:false`.
- Events: `attackStart`, `lightHit`, `hit3`, `finisher`, `dive`, `stagger`, `pressured`, `playerHit`, `dodge`, `lockOn`, `roadSuper`, plus helpers `hit/slash/lightning/stagger/super/lockOn/trail/attach/fromHitFrame`.
- v3: resolve Rigger `userData.fx` attach points (wheels for kicks, hands for punches).
- Budget: **0 draws idle, max 3 live** (additive sprites, ribbons, ink).
- Crew palettes (c1 / c2 / motif) — see combat-fx.md table: Code : E gold, Kogarasumaru red, Static Angels purple/cyan, Anubis teal/sand, Sleeping Forest green, Behemoth orange, Genesis magenta/gold, Tool Toul To rust/gray, Volt hot pink/yellow, Rust Claw orange/rust.
- Unity: VFX Graph or particle systems keyed off the same event names; keep hit-stop **sim-only** (do not freeze XR camera).

## LOD budgets

- Quest player LOD0 ~**100–120k** tris (target ~**105k**); NPC ≤ **30k**.
- Characters + FX ≤ **40 draws** (world ≤ 110 is Palma).
- Skates: 2 skates ≤ ~18k LOD0; LOD1 ~6k; LOD2 ~1.5k (add-ons drop at LOD2).
- Caali G packaged LODs example: meshes `CaaliG_LOD0/1/2`, 91 joints, ~148k tris summed across LODs in one GLB (switch via mesh LOD group).

## Texture rules

- **Power-of-two** (Optimizer `quest_pipeline` default with `--ktx2`; `--no-pot` opt-out).
- Quest: **KTX2** (UASTC/ETC1S as authored); HD may keep PNG/WebP sources.
- Albedo sRGB; MR/normal linear. Match one encoding convention across body+skate.
- Atlas sizes commonly 2048 col / 1024 ORM (quest strips normals).

## Garage kit props

- `v3build/props/kit/`: pod, pod_closed, drone, couch, lockers, desk, kitchen, tv (+ `.ktx2.glb` variants) and `manifest.json`.
- Runtime today: `crewhouse_kit.js` `kitProp()` / `kitPodGlb` / `kitDroneGlb`. Drone rotors = nodes `rotor_FL/FR/BL/BR`. TV = `tv_body` + `screen` material.

## Known open issues (Forge)

1. **Caali G v2 has no `_slot` / `_bm` wardrobe hide attributes** — modular wardrobe hide/cover path incomplete on the monolithic v2 body.
2. **Akito dark outfit** pending a new Meshy model (local-only; straitjacket/dark GLBs exist on the box only).
3. **Straitjacket strap springs** pending (Rigger WIP; Akito local).
4. Shared A-T shell (`ShellBlend_L*`) can read as shards in extreme close-up — needs cleaner shell bake.
5. Anika braid/skirt spring solver not in live `ikki_skate.js` yet (bones follow parents statically).
6. `?riderstyle=opt3` gate not run; default build still prior PBR/toon split for crew NPCs.
7. Baked skates inside some Meshy rider meshes (sid 11–13) must stay hidden/stripped when using runtime shared skate.

## Suggested Unity import order

1. Skeleton + Caali G / Anika LOD GLBs + materials (opt3).
2. A-T skate v2 + socket empties as child Transforms; crew colour controller.
3. Wardrobe pieces (jacket/top/pants/… ) if modular path is required; else monolithic riders.
4. Crew logos/patches/coins as UI/decal textures.
5. Kit props into garage prefabs.
6. CombatFX event bus mirroring `CombatFX.emit` names + crew palettes.
7. Leave Akito until rename + new Meshy.
