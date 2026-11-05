# Rydah Systems — Workshop Handover

Gameplay systems + QA package for **Sky Rydahs** (WebXR / Three.js r128 inline-skating game), prepared for conversion to the Unity flagship build.

**Owner:** Rydah Systems (Oliver Moore's workshop bot)  
**Repo path:** `handover/rydah-systems/` on branch `workshop-handover`  
**Source tree:** `/workspace/v3build` (built by `build_ikki.sh`; only the integrator runs that script)

## Layout

| Folder | Contents |
|--------|----------|
| `code/` | Runtime JS modules injected into `sky-rydahs-v3-ikki.html` |
| `patches/` | `patch_*.py` injectors (anchors + globals) |
| `patches_proposed/` | Unapplied diffs awaiting Ani / grind worker review |
| `tests/` | Playwright suites (integrator holds `.testlock`) |
| `notes/` | Progress / design notes + `build_ikki.sh.reference` |
| `refs/` | Research docs copied from `skyrydahs-ref/` |
| `shots/` | Latest graffiti / wallkick / polegrind / minimap / trails screenshots |
| `INVENTORY.md` | Full file list, chain order, flags, APIs, deps, Unity notes |

## Quick start (local WebXR demo)

1. Serve `/workspace` on `:8765`.
2. Integrator holds `/workspace/v3build/.testlock`, then e.g.  
   `python3 tests/graffiti.py http://localhost:8765`
3. Never run `build_ikki.sh` or `pkill` from this bot — use Ani's `build_copy.sh` for scratch builds.

## Ownership highlights

- **Mine:** graffiti, heat, minimap_v2, ride_ground, tickguard, wallatk (wall-ride + wall-kick + combat), polegrind, trails, turf_dash, grind, phone/map/icons/pad/target/grapple/fps, perf_overlay.
- **Co-owned / verify:** `gamepad.js` + `patch_gamepad.py` (Optimizer owns `SR_PAD.haptic`; Systems remapped LB / D-pad left / LT).
- **Not mine (dependency only):** `perf/drawcalls/dc_meter.js` (Optimizer), CombatFX (Forge), `ikki_skate` poser (Rigger), `WORLD_GROUND` / `WALL_PANELS` / `KICK_ROUTES` (Palma).
- **Excluded:** `.bak-sys-*` backups, placeholder-rider assets, secrets/`.env`, Ani's `demo_smoke.py`, Optimizer's `dc_meter.js`. Separate `wallkick.js` does not exist — wall-kick lives in `wallatk.js`.

See **INVENTORY.md** for the complete conversion brief.
