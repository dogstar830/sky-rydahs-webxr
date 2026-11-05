# Rydah Systems — Handover Inventory

Prepared 2026-11-05 for Unity flagship conversion. Source: `/workspace/v3build`. Branch target: `workshop-handover` → `handover/rydah-systems/`.

---

## 1. File inventory

Owner status: **mine** = Rydah Systems; **co-owned / verify** = shared or header unclear; **dep** = other bot's system we call (not packaged here).

### 1.1 Code (`code/`)

| Path | What it does | Owner |
|------|--------------|-------|
| `code/graffiti.js` | S/M/L tag + heaven spots; Xbox RS gesture rhythm; 4 surface InstancedMeshes + mist + glow; extends TURF; seeds minimal HEAT | mine |
| `code/heat.js` | Police Heat v1 ★0–★3 (foot/bike/G-Men), LOS, cooldown, BUSTED, bank at HQ; hooks for ★4–5 | mine |
| `code/minimap_v2.js` | Watch Dogs tilted GPS minimap (heading-up), rim markers, objective HUD `#mm2o`, HEAT cops 2D; `window.MINIMAP` | mine |
| `code/map.js` | Full Palma City world map (View/M) + legacy minimap helpers; shared icons | mine (via patch_phone) |
| `code/icons.js` | Procedural Air Gear map icon set for world map + minimap | mine (via patch_phone) |
| `code/perf_overlay.js` | `?perf=1` Quest HUD on Optimizer DC_METER: ms/avg/p95, scene draws, tris, tex MB, world/chars/fx split | mine |
| `code/wallatk.js` | Wall-ride + wall-to-wall; **wall-kick chain** (`KICK`); crew attacks (`ATK`); KH chain (`CHAIN`); sim hit-stop (`HITSTOP`); combat poser bridge (`CP`, `?combatposes=1`); CombatFX emit | mine (wallkick.js does not exist) |
| `code/ride_ground.js` | Rider Y follows `WORLD_GROUND`; step-up/down; water/void → `RIDER_RESET`; `?flatground=1` opt-out | mine |
| `code/tickguard.js` | Head helper: `SR_GUARD` / `SR_ERRORS` | mine |
| `code/tickguard_late.js` | Late wrap of per-frame systems + `setAnimationLoop` | mine |
| `code/polegrind.js` | Spiral climb on vertical poles; Rigger `setState('polegrind')`; double-helix FX (1 draw); top pop → cable grind | mine |
| `code/trails.js` | Pooled additive ribbon: player wheels + NPC ≤12 m + dash streaks; 1 draw; `window.TRAILS` | mine |
| `code/turf_dash.js` | Crew turf tagging (atlas InstancedMesh) + boost dash meter/FX; `TURF` / `DASH` | mine |
| `code/grind.js` | Locked-in grind on rails/cables/poles/palms; sparks/trail/vortex; `window.GRIND` | mine |
| `code/pad.js` | Xbox layer over `SR_PAD`: camera-relative move, LB=L special, D-pad left=grapple, brake 16 m/s², menus/phone/map | mine |
| `code/target.js` | GTA-style LT lock-on / free aim reticle; spray aim for graffiti; FOV ease | mine |
| `code/phone.js` | iLink crew phone (jobs/map/crew/hack/…); `PH_CTRL` controls list | mine |
| `code/grapple.js` | Grapple to marked roof/billboard points; prompt; `window.GRAP` | mine (bak-sys + remap glyph) |
| `code/fps.js` | `?fps` overlay (DOM / XR quad); bundled by `patch_phone` | mine (via patch_phone; co-exists with `?perf`) |
| `code/gamepad.js` | `window.SR_PAD` standard mapping + poll; **haptics by Optimizer**; remap comments by Systems | **co-owned / verify** |

**Not packaged (by design):**
- `perf/drawcalls/dc_meter.js` — Optimizer (**dep**); injected by `patch_graffiti.py` at build time.
- `wallkick.js` — does not exist; wall-kick is inside `wallatk.js`.
- All `*.bak-sys-*` backups.

### 1.2 Patch scripts (`patches/`)

| Path | Role | Owner |
|------|------|-------|
| `patches/patch_tickguard.py` | Injects tickguard head + late body; EARLY | mine |
| `patches/patch_turf.py` | Injects turf_dash + HUD divs/CSS | mine |
| `patches/patch_wallatk.py` | Injects wallatk; wraps ride loop with wallAtkPre/wallStep/wallAtkPost | mine |
| `patches/patch_ride_ground.py` | Injects after `window.WORLD_GROUND=…` | mine |
| `patches/patch_grind.py` | Injects grind; `grindStep` before `wallStep`; `grindTick` before render | mine |
| `patches/patch_polegrind.py` | Injects polegrind.js + trails.js after grind | mine |
| `patches/patch_graffiti.py` | Injects graffiti + heat + **Optimizer dc_meter** + perf_overlay; ticks before render | mine (pulls Optimizer dep) |
| `patches/patch_phone.py` | Injects phone+icons+map+grapple+pad+target+fps before `init()` | mine |
| `patches/patch_minimap.py` | Injects minimap_v2 before `init()` | mine |
| `patches/patch_gamepad.py` | Injects gamepad.js at INPUT; routes getGamepads; LB/LT remap edits by Systems | **co-owned / verify** (Optimizer haptic + Systems remap) |

### 1.3 Proposed patches (`patches_proposed/`)

| Path | What | Status |
|------|------|--------|
| `patches_proposed/grind_airsnap.diff` | Apex air-snap: `|vy|<1.5` → full cable radius + 1.5 m reach (wall-kick→cable) | proposed; Ani/grind worker to apply |
| `patches_proposed/grind_vortex_gate.diff` | Vortex focus only while grinding; XR cap | proposed; runtime gate already in polegrind.js |

### 1.4 Tests (`tests/`)

| Path | Covers | Owner |
|------|--------|-------|
| `tests/graffiti.py` | Tag gestures, TURF, HEAT night, draws | mine |
| `tests/heat.py` | ★0–3 ladder, LOS, BUSTED, bank, draws≤3 | mine |
| `tests/minimap_gps.py` | `MINIMAP.state` heading-up | mine |
| `tests/objective_hud.py` | Objective distance `#mm2o` | mine |
| `tests/perf_overlay.py` | `?perf=1` panel + no-perf zero cost | mine |
| `tests/ride_ground.py` | WORLD_GROUND follow | mine |
| `tests/respawn.py` | `RIDER_RESET` | mine |
| `tests/grind.py` | Snap/lock/ride/pop/draw | mine |
| `tests/grind_airsnap.py` | Air-snap A/B probe | mine |
| `tests/grind_diag.py` | Air-snap diagnostics JSON | mine |
| `tests/wallride.py` | Stick/run/flip/chain | mine |
| `tests/wallkick.py` | Spans, climb→cable, REAL-PLAY, hero | mine |
| `tests/polegrind.py` | Spiral, setState, helix, top pop | mine |
| `tests/trails.py` | 1 mesh / 1 draw pool | mine |
| `tests/attacks.py` | Crew moves static (+ ATK_ONLY filters) | mine |
| `tests/attacks_moving.py` | Moving targets | mine |
| `tests/combat_chain.py` | C1/C2 chain + hit-stop; CC_ONLY=off\|poses | mine |
| `tests/atk_steer_diag.py` | Attack steer probe | mine (header) |
| `tests/gamepad.py` | SR_PAD; GP_ONLY=p1\|p2\|p3; remap cases | mine (tests); module co-owned |
| `tests/phone.py` | iLink apps/pad/grapple; PH_ONLY filters | mine |
| `tests/tickguard.py` | Guard disables bad tick, loop lives | mine |

**Excluded:** `tests/demo_smoke.py` (Ani's).

### 1.5 Notes / refs / shots

| Path | What | Owner |
|------|------|-------|
| `notes/WALLKICK_NOTES.md` | Palma kick routes + airsnap note | mine |
| `notes/POLEGRIND_NOTES.md` | Helix / trails / vortex queue | mine |
| `notes/COMBAT_PROGRESS.md` | C1/C2 + poser bridge log | mine |
| `notes/GRAFFITI_PROGRESS.md` | Graffiti ship log | mine |
| `notes/CONTROLS_STATUS.md` | Phone/pad/map status scrap | mine / verify |
| `notes/build_ikki.sh.reference` | Exact integrator build chain (snapshot) | reference copy |
| `refs/graffiti-research.md` | Research from skyrydahs-ref | mine (copied) |
| `shots/graffiti_*.png` | Surface / night / turf / heaven | mine |
| `shots/wallkick_*.png` | Climb / cable / popup / realplay | mine |
| `shots/minimap_gps_*.png` | GPS heading shots | mine |
| `shots/trails.png` | Pooled trails | mine |
| `shots/hero/polegrind.png` | Hero (1920×1080) | mine |
| `shots/hero/wallkick_climb.png` | Hero climb | mine |
| `shots/hero/hud_minimap_topright*.png` | Hero HUD | mine |

---

## 2. Build chain order (`build_ikki.sh`)

Only **Ani (integrator)** runs this. Systems never runs `build_ikki.sh` or `pkill`. Scratch builds: `bash build_copy.sh /tmp/<you>.html`.

| # | Script | Systems? | Anchors / inject | Globals injected |
|---|--------|----------|------------------|------------------|
| 1 | `patch_ikki.py` | no | creates html | — |
| 2 | **`patch_tickguard.py`** | **YES (EARLY)** | `<head>` tickguard.js; before `</body>` tickguard_late.js | `SR_GUARD`, `SR_ERRORS`, `SR_TICKGUARD` |
| 3 | **`patch_turf.py`** | **YES** | `// ===== LOOP =====`; HUD `#turf/#welcome/#dash` | `TURF`, `DASH` |
| 4 | `patch_ikki_skate.py` | Rigger | — | poser API |
| 5 | `patch_gates.py` | other | — | — |
| 6 | **`patch_wallatk.py`** | **YES** | LOOP; wraps `updateRide` with wallAtkPre/wallStep; wallAtkPost after riders | `WALL`, `KICK`, `ATK`, `CHAIN`, `HITSTOP`, `COMMIT`, `CP` |
| 7–14 | asphalt…ground | Palma/others | — | `WORLD_GROUND` (ground) |
| 15 | **`patch_ride_ground.py`** | **YES** | after `window.WORLD_GROUND=WORLD_GROUND;` | `RIDER_RESET`, ride wrappers |
| 16 | **`patch_grind.py`** | **YES** | LOOP; `grindStep\|\|wallStep`; `grindTick` before render; wraps `sagWire` | `GRIND` |
| 17 | **`patch_polegrind.py`** | **YES** | before LOOP marker (needs GRIND) | `PG`, `TRAILS` |
| 18 | **`patch_graffiti.py`** | **YES** | LOOP; grafTick/heatTick/perfTick before render | `GRAF`, `HEAT`, `PERF` (+ Optimizer `DC_METER`) |
| 19 | **`patch_phone.py`** | **YES** | before `function init()`; ticks before render | `PHONE`, `MAP`, `ICON`, `GRAP`, `PAD`, `TGT`, `FPSO` |
| 20 | **`patch_gamepad.py`** | **co-owned** | `// ===== INPUT =====`; `SR_PAD.update()` before poll | `SR_PAD` |
| 21 | **`patch_minimap.py`** | **YES** | before `function init()` | `MM2`, `MINIMAP` |
| 22–end | draco/ktx2, crew, quant, kit, world_perf, pbr, xr_fxmem, **combat_fx** | Optimizer / Palma / Forge | CombatFX LAST | `CombatFX` |

---

## 3. Runtime flags (grep of Systems code)

| Flag | Effect |
|------|--------|
| `?perf=1` | Systems perf overlay (on DC_METER) |
| `?fps` | Lightweight FPS overlay (`fps.js`); hidden when `?perf` on |
| `?flatground=1` | Disable ride_ground (Y=0) |
| `?worldstick=1` | Old world-absolute LS (disable camera-relative) |
| `?hitstop=full\|off` | Hit-stop scale 1.0 / 0 (default **0.5**) |
| `?combatposes=1` | Enable Rigger combat poser bridge (`SR_COMBAT_POSES`) |
| `?haptics=full\|reduced\|off` | `SR_PAD.hapticScale` (Optimizer; default reduced in XR) |
| `?minimap=old` | Restore pre-v2 HUD minimap |
| `?nobatch=1` | Keep graffiti glow draw by day (skip -1 draw opt) |
| `?turfAway=N` | Simulate minutes away for rival retake |
| `?controls` / `showctl` | Show top controls overlay (hidden by default) |
| `?tier=hd` / `?seed=1` | Hero shots / world seed (integrator / Palma) |
| `?player=ikki` | Attacks tests player override |
| `?chars=…` | Character root (tests default `/skyrydahs-characters/`) |
| `?ktx2=1` / `?pbr=0` / `?toon=1` / `?nocfx` / `?fxdemo=1` | Other bots' flags; Systems consumes CombatFX when present |

---

## 4. Public globals / APIs

| Global | Source | API summary |
|--------|--------|-------------|
| `window.TURF` | turf_dash + graffiti bridge | spots, ownership, subscribe, points, spray |
| `window.HEAT` | graffiti stub + heat.js | stars, cops, state, bank, freeze/step (tests) |
| `window.RIDER_RESET(why)` | ride_ground | Safe respawn; clears air/grind/etc. |
| `window.SR_GUARD(name,fn,opts)` | tickguard | Wrap tick; first throw → disable + `SR_ERRORS` |
| `window.SR_ERRORS` | tickguard | `{system,message,stack,frame,t}[]` |
| `window.SR_TICKGUARD` | tickguard_late | wrap stats |
| `window.KICK` | wallatk | Wall-kick chain state + `up[]`, `upScale`, `g`, `win` |
| `window.ATK` / `CHAIN` / `HITSTOP` / `COMMIT` | wallatk | Attacks, KH chain, hit-stop scale, lock-commit |
| `window.GRIND` | grind | Splines, lock/ride/pop, vortex |
| `window.PG` | polegrind | Spiral climb / helix `k` |
| `window.TRAILS` | trails | Pooled ribbon stats |
| `window.TGT` | target | Aim / lock / spot / sprayR |
| `window.PAD` | pad | Stick/camera/edge state |
| `window.SR_PAD` | gamepad | `update`, `pressed`, `justPressed`, **`haptic(evt,opts)`** |
| `window.PHONE` / `MAP` / `GRAP` | phone bundle | UI + grapple |
| `window.MINIMAP` / `MM2` | minimap_v2 | `.state` (heading, obj, cops, rim) |
| `window.PERF` | perf_overlay | `{on}` + tick |
| `window.FPSO` | fps | FPS overlay |
| `window.WALL` | wallatk | Wall-ride state |
| `window.DASH` | turf_dash | Boost dash |

---

## 5. Dependencies on other bots

| Dep | Bot | How Systems uses it |
|-----|-----|---------------------|
| `CombatFX.emit` / `fromHitFrame` | **Forge** | Attack sparks/trails; hit-stop ms × `HITSTOP.scale`; CombatFX v3 attach points (wheels/hands) — **wiring in progress** |
| `SR_PAD.haptic` | **Optimizer** | Combat / graffiti / gate pulses; comfort scale |
| `RIDERS.player.userData.setState` / `combatQuery` / `combatHitStop` | **Rigger** (`ikki_skate`) | Polegrind climb/top; combat poser bridge |
| `WORLD_GROUND(x,z,yHint)` | **Palma** (`ground.js`) | ride_ground Y follow |
| `WALL_PANELS` / wallPanel colliders | **Palma** (`blockout`) | Wall-ride stick + kick faces |
| `KICK_ROUTES` / `WALL_KICKS` | **Palma** | Authored wall-kick climb routes (e.g. the98 alley → cable) |
| `DC_METER` | **Optimizer** | Split draws for `?perf=1` (injected beside our overlay) |
| `PALMA.districts` / `garages` | **Palma** | Map, turf crews, heat hide spots |

---

## 6. Controls map (current Xbox — Oliver remap 2026-10-30)

| Input | Action |
|-------|--------|
| **LS** | Move / steer (camera-relative unless `?worldstick=1`) |
| **RS** | Camera; graffiti gesture while tagging; LT fine-aim |
| **L3** | Boost dash; grind kick |
| **A** | Jump / wall-ride / wall-kick / grind pop / UI select |
| **B** | Back / power slide / grind drop / cancel tag |
| **X** | Context (pickup / gate hack / start tag) |
| **Y** | Trick; **RT+Y** = crew ultimate |
| **RB** | Melee: tap = light chain, hold ≥0.35 s = heavy |
| **RT** | Special (Hold RT = super) |
| **LB** | **L special only** (remap) |
| **LT** | **Lock-on / aim only** (remap; not L special) |
| **D-pad Left** | **Grapple** (at marked points) |
| **D-pad Up / Down** | Phone / ping |
| **VIEW / MENU** | World map / pause |
| **R3** | Crew move |
| Keyboard | WASD, Space, Shift boost, J/K/L attacks, G grapple, Q aim, M map, Tab phone |

Brake (S / stick back): **16 m/s²** in `pad.js` cam-relative layer.

---

## 7. Test suites — how to run + latest known results

**Rules:** Integrator only; hold `/workspace/v3build/.testlock`; one suite at a time; **never `pkill`**.

```bash
# Base
export RYDAH_BASE=http://localhost:8765   # optional; some suites use it
python3 tests/<suite>.py [base_url] [page]

# Filters (6-min windows)
GP_ONLY=p1|p2|p3          # gamepad.py
PH_ONLY=apps|pad|pad2|grapple
ATK_ONLY=static|rest|tail|ikki|commit
CC_ONLY=off|poses           # combat_chain.py
WK_ONLY=climb               # wallkick.py
```

Default page: `v3build/sky-rydahs-v3-ikki.html?chars=/skyrydahs-characters/`.

### Latest known greens (from DEMO_STATUS / Systems check-ins)

| Suite | Result | Notes |
|-------|--------|-------|
| graffiti | 30/30 | html 17:59:57 |
| heat | 35/35 | cops draws = 3 |
| minimap_gps | 7/7 | |
| objective_hud | 7/7 | |
| perf_overlay | 15/15 | AI rebuild #2 |
| wallride | 13/13 | |
| wallkick | 20/20 + climb 12/12 | REAL-PLAY green |
| polegrind | 14/14 (Systems copy); 15/15 AI#2 | |
| trails | 8/8 | |
| grind | 36/36 | |
| attacks static | 33/33 | |
| attacks (full windows) | 54/54 | |
| attacks_moving | 47/47 | |
| combat_chain | 15/15 off; 10/10 poses | |
| gamepad | 55/55 AI#2; remap p1 28/28 + p2 42/42 | |
| tickguard | 13/13 | |
| ride_ground | 25/25 (earlier); respawn suite exists | |
| phone | apps 25/25; pad/grapple remapped; LT FOV fix on /tmp/ltfix | load flakes under box 30–35 |

---

## 8. Status and open items

### Done
- Graffiti + TURF bridge + Heat ★0–3
- GPS minimap top-right + objective HUD
- Wall-ride + wall-to-wall + wall-kick climb → cable
- Pole grind + helix FX + pooled trails
- Grind lock/ride/pop; KH combat chain + sim hit-stop ×0.5
- Combat poser bridge (flag-gated)
- Camera-relative move + brake 16 m/s²
- Controller remap (LB / D-left / LT)
- Tickguard studio safeguard
- Ride ground + RIDER_RESET

### Partial / in progress
- **CombatFX v3 wiring** — Forge attach points live; Systems emit path + poser `fromHitFrame` coexistence still being hardened
- Phone LT-release FOV/reticle under heavy box load (fix on /tmp; full suite windows flaky)
- Grind air-snap for apex under cable (**diff proposed**, not applied)

### Pending / held
- **Heat stars ★4–5** — held (hooks only in heat.js)
- **Volt / Rust Claw content** — **UNHELD** (Oliver crew ruling 2026-11-02): Volt→The 98 garage = charging station; Rust Claw→The Cove garage = salvage shed. Palma places garages; Systems may ship content now
- Vortex gate diff apply (Ani grind worker)
- Public placeholder-rider rename gate (local-only; never in this handover)

---

## 9. Unity conversion notes (per system)

Budget target (Quest): **72 fps**, **≤150 draws total** (world ≤110, chars+FX ≤40).

| System | Unity mapping | Key constants |
|--------|---------------|---------------|
| **ride_ground** | CharacterController / ground probe sampler matching Palma heightfield | Step-up ≤0.35 m; water/void → respawn; brake unrelated (in pad) |
| **pad / cam-rel** | Input System PlayerInput; camera-relative move on Cinemachine follow | Deadzones LS 0.18 / RS 0.2 / trig 0.3; **brake 16 m/s²**; pivot when speed ≤1.5 |
| **wallatk wall-ride** | Physic material sticky + along-wall velocity | Shallow entry angle; hold jump = wall run; flip = jump+away |
| **wall-kick `KICK`** | Impulse chain on facade normals | `win=0.35 s`; `up=[4.5,4,3.5,3,2.5]` × `upScale=2.0`; `g=9`; `out=4.2`; `along=0.35`; `max=5`; ~street→9.5 m cable in 3–4 kicks |
| **grind** | SplineAnimate / custom rail follower | Material µ/drag table (steel/cable/bark); air snap radius; proposed apex reach 1.5 m |
| **polegrind** | Spline + orbit offset; Animator states climb/top | Fade in **0.30 s**, loop **1.6 s**, out **0.25 s**; `PG.CLIMB` 6 m/s²; helix 1.5 turns, 1 draw |
| **trails** | Single LineRenderer / VFX Graph ribbon pool | MAXT=8, SEG=24, NPC_R=12 m, minSp=3.5 |
| **graffiti** | GPU instancing + reveal shader | 4 surface programs + glow + mist Points(256) = 7 draws; S1/M3/L5 gestures |
| **heat** | AI police directors | Pool ≤6; ★0–3 live; ★4–5 hooks; night ×2; BUSTED 3 s pin / 3 knockdowns |
| **turf_dash** | Capture points + boost meter | Atlas 8 crews × 3 stamps; dash blur/ribbons (ribbons → TRAILS) |
| **combat ATK/CHAIN/HITSTOP** | Hitboxes + Timeline / Animancer cancels | Chain win **0.6 s**, minT **0.16 s**; finisher knock×2.4; **HITSTOP default ×0.5**; freeze attack+target only (never Ride) |
| **poser bridge CP** | Animator state machine | Root clamps 14 m/s, 6 m, XR 3 m; heavy hold J ≥0.35 s |
| **target / commit** | Soft lock + reticle UI | Cone 15°; commit cone 40°, range 14 m |
| **minimap_v2** | UGUI RawImage / RenderTexture | 320², range 110 m, 20 Hz, tilt 45°; heading-up |
| **phone / map** | UGUI phone prefab + fullscreen map | Same app list; grapple points as world markers |
| **tickguard** | try/catch per gameplay system Update | Disable after first throw; log once |
| **perf overlay** | Debug UI / SRDebugger | Scene-only draw metric (exclude post) |

### Tuning cheat-sheet
- Wall-kick heights: up bursts ×2.0 scale → ~4.5+3.6+2.7 m apex gain toward 9.5 m cables  
- Brake: **16 m/s²**  
- Hit-stop: CombatFX ms × **0.5** (`?hitstop=full|off`)  
- Chain: 3 hits, cancel A/B on 1–2, 0.6 s reset  
- Draws: graffiti ≤7 system; trails 1; pole helix 1; heat cops ≤3; total budget 150 (110+40) @ 72 Hz Quest  

---

## Exclusions summary

| Excluded | Why |
|----------|-----|
| `*.bak-sys-*` | Backups, not source of truth |
| Placeholder-rider local paths & strings | Local-only until renamed; zero matches in this package |
| Secrets / `.env` / tokens | None included |
| `demo_smoke.py` | Ani's integrator suite |
| `dc_meter.js` | Optimizer-owned (dep via patch_graffiti) |
| `wallkick.js` | N/A — logic in `wallatk.js` |
