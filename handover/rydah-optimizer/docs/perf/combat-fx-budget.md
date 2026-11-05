# Sky Rydahs combat FX, hit-stop, slow-mo and haptics budget (FF7R/Rebirth + Kingdom Hearts feel, Quest 3)
Rydah Optimizer, 2026-10-30 ~09:20 CDT. For Ani (asked for the Quest budget) and Rydah Systems (combat owner).
**All numbers are STATIC ESTIMATES from reading code and docs. No headset, no browser, no tests were run.** This doc is the only new file; no game files were edited.
Inputs: skyrydahs-ref/combat-ff7-kh-reference.md (mtime 09:00:12 CDT, re-checked at the end, see §9), COMBAT_PLAN_NOTES.md, perf/anika-fx-budget.md §2-3, perf/airgear-render-style.md §8, perf/texmem/audit.md, wallatk.js, target.js, trails.js, gamepad.js, gates.js (gateHaptic), sky-rydahs-v3-ikki.html animate() (line ~4779), DEMO_STATUS.md check-ins to 08:50 CDT.

Quest targets: 72 fps = 13.9 ms. Scene draws ≤150 per pass (world ~100 worst camera), **characters+FX ≤ 40**, **FX GPU ≈ 1 ms**, fill-rate bound (additive overdraw is the cost), r128 has **no multiview** (each draw is submitted twice in stereo: 40 per eye = 80 submits), **composer/bloom off in XR** (html !xr guard), so glow = additive/emissive only.

## 0. Top line
- **Combat adds +2 draws** (1 combat sprite instancer + 1 combat HUD/glyph instancer) on top of what exists, if slashes/rings/stars keep going into wallatk.js's FXB pool and wheel trails stay in trails.js. Worst-case characters+FX: **26 (no outlines) / 32 (outlines) / 34 (fixed-set slots unmerged) of 40**. Over 40 only if every FX type gets its own mesh or skinned afterimages ship on Quest.
- **Combat FX GPU on Quest ≤ ~0.45 ms at the caps** (stereo fill counted), leaving room inside the ~1 ms FX cap for trails (0.05-0.1) + pole helix (0.1-0.2), which don't usually overlap a big fight.
- **Textures: +~0.5 MB** (one 512² combat atlas ETC1S + 512×256 UASTC SDF digits) or **+~0.35 MB** if the numbers reuse the trick-name atlas. ~186 → ~186.5 MB of 256.
- **Hit-stop = scale gameplay dt only** for the attacker's animation and the victims. The XR head pose and the render loop never stop. In XR the player's locomotion does not freeze either (only the pose does).
- **Slow-mo = world/enemies only**, ≤ 0.4 s, never the player's rig or the camera in XR.
- **Camera shake: none in XR** → controller haptics (plan in §4). Desktop gets a small positional kick.

## 1. What already exists (code read, 09:10 CDT)
| system | file | draws | notes |
|---|---|---|---|
| FXB "PooledFX" | wallatk.js:219-256 | **1** | one dynamic BufferGeometry, maxQ 1800 quads (10.8k verts), rewritten each frame, drawRange = live quads. Holds every attack bolt/beam/arc/ring/burst, the stun **stars** and the wall-ride wheel streaks. ⚠ Material is `MeshBasicMaterial` with **normal blending, not additive** (opaque colour quads, depthWrite off). It reads as glow only because of desktop bloom; in XR (no bloom) it reads flat. Fix: `blending:AdditiveBlending, transparent:true` and the hot-core/fringe colours it already writes (0 draws, small fill increase). |
| TRAILS ring | trails.js | **1** | 8 slots × 24 seg, additive ShaderMaterial; also absorbs turf_dash streaks. |
| pole helix | polegrind.js | 1 (only while pole grinding) | |
| grind sparks | grind.js Points(160) | 1 | |
| lock marker `TGT.mk` | target.js | 1 when locked | RingGeometry 24, **depthTest:false**, renderOrder 998. |
| spray preview `TGT.pv` | target.js | 1 when spraying | CanvasTexture 128² plane; never at the same time as a combat lock. |
| DOM reticle `#reticle` | target.js | 0 | **targeting is off in XR** (`!renderer.xr.isPresenting` in tgtUpdate), so no lock UI in the headset today. |
| stun | wallatk.js:198 | 0 (FXB) | `n.stun` timer, wobble on holder rotation, stars pushed every 3rd frame. This becomes FF7 Pressure→Stagger. |
| haptics | gates.js `gateHaptic(s,ms)` (XR `hapticActuators[0].pulse`), gamepad.js `SR_PAD.rumble(strong,weak,ms)` (desktop pad) | 0 | wallatk already calls gateHaptic(.5,40) on attack start and (1,120) when hit. |
| time scale | none | — | grep for timeScale/slowmo/hitstop: **no hits**. animate() has one `dt=min(.05,…)`; there is **no fixed physics step**, every system integrates with `dt`. |

## 2. Combat FX list (what the reference implies) and the cheapest r128 form
Pool caps are hard caps; the oldest instance is recycled. Fill = Quest per-eye coverage estimate × 2 eyes. Tiers: **T2** = desktop/full, **T1** = Quest default, **T0** = Quest fallback when the frame goes over (perf_overlay/dynamic tier).

| # | FX (ref §) | cheapest r128 implementation | draws | verts (cap) | fill risk / est. GPU Quest | pool cap | Quest tier |
|---|---|---|---|---|---|---|---|
| 1 | **Kick/slash arcs** (KH combo hits 1-3 + road finisher, ref §5.1) | `fxArc`/`fxRibbon` into **FXB** (already exists); arc = 12-16 segment camera-facing ribbon, white core + crew fringe (2 ribbons as today). Finisher = road-keyed arc (Lightning bolt, Wing feather arc, Thorn spiral = existing `spiral`). | **0** (FXB) | ≤ 64 quads/arc; ≤ 4 live → 256 quads | medium: arcs pass close to the camera in 1st person. Clamp width by camera distance (`w*=clamp(d/1.5,.35,1)`), alpha ≤ .7. ~0.08-0.15 ms | 4 arcs live | T1: 1 ribbon/arc (no separate core), 10 seg. T0: core only, 6 seg |
| 2 | **Hit sparks + impact flash** (hit-stop partner, ref §3) | NEW **combat sprite instancer**: 1 InstancedMesh of quads, 1 shared 512² atlas (spark streak, star flash, ring, soft dot, feather, leaf, bolt cells). All motion in the VS from per-instance attrs (spawn t, seed, vel, cell, colour). Flash = 1 billboard per hit, 90-120 ms. Sparks 6-10 stretched quads per hit. | **+1** | 4 verts × 96 = 384 | **highest risk**: a flash on an enemy at 1 m covers 15-25% of the eye. Clamp flash size in the VS to ≤ 10% of view height, alpha ≤ .6, life ≤ 120 ms. ~0.1-0.2 ms in a 4-enemy fight | 96 instances (≤ 6 flashes + 80 sparks + stars) | T1: 6 sparks/hit, flash 0.4 m. T0: 3 sparks, no flash (target tint only) |
| 3 | **Target hit flash** (ref §5.2 "flash the target instead") | uniform on the rider material: `uHit` emissive add (white→crew colour, 80 ms). One shared uniform per material clone, or a per-instance colour on the NPC instancer. | **0** | 0 | none | per rider | all tiers |
| 4 | **Stun/stagger stars + Pressured ring** (FF7 stagger, ref §5.3) | stars move from FXB into the sprite instancer (4 instances/enemy, VS orbit, no CPU per frame). "Pressured" = a thin ground ring cell under the enemy (1 instance). | 0 (shares #2) | 5 inst/enemy | low (small, mostly below eye level) | 8 enemies × 5 = 40 inside the 96 | T0: ring only |
| 5 | **Pressure/stagger gauge + HP bar** (ref §5.3) | NEW **combat HUD instancer** (1 InstancedMesh, same 512² or glyph atlas, alpha-blended not additive). Each enemy bar = 3 quads (back, HP, pressure) billboarded above the head, fill via per-instance `scaleX`. Desktop may keep DOM (0 draws) like #retLock. | **+1** (shared with 6-9) | 3 inst/enemy | low (~0.5% screen each) ~0.02 ms | 8 bars (only engaged + locked, ≤ 15 m) | T1: locked + 2 nearest only. T0: locked only |
| 6 | **Lock-on reticle** (FF7 R3 lock / KH lock, ref §5.4) | move `TGT.mk` (its own 24-seg Ring, 1 draw) into the HUD instancer as a ring cell; keep depthTest off only for it (renderOrder last). Desktop keeps the DOM SVG. **XR needs this** because targeting is currently desktop-only. | 0 (shares #5); today 1 | 1-2 inst | low | 2 (lock + switch ghost) | all tiers |
| 7 | **Damage numbers / "STAGGER!" / "PRESSURED" / combo ×N / finisher name** (FF7 popups, KH combo) | same HUD instancer, 1 quad per glyph, UV rect per instance from an **SDF digit+word atlas** (or the render-style §8 trick-name atlas: whole words as one quad). VS does pop/rise/fade from spawn time. **No DOM and no CanvasTexture in XR.** (If Systems prefers a single dynamic BufferGeometry, same cost: 1 draw, rewrite only on spawn.) | 0 (shares #5) | 4 verts × 64 = 256 | low; keep glyphs ≥ 2.5 cm/m angular size for legibility | 8 numbers × ≤ 6 glyphs + 4 words = 64 | T0: words only (no per-hit numbers) |
| 8 | **ATB/Road super (Limit) meter + Reaction prompt "X"** (ref §5.6-5.7) | desktop: DOM (0 draws). XR: 3-5 HUD-instancer quads on a wrist/lower-view anchor (not head-locked centre). Prompt = 1 word quad at a fixed spot. | 0 (shares #5) | ≤ 8 inst | low | 8 | all tiers |
| 9 | **Ability / Limit (Road super) bursts** (finisher shockwave, Shock/Kick Dive ground ring, ref §2 Flowmotion) | expanding ground ring + 8-ray burst in **FXB** (`ring`, `burst` exist) + ≤ 16 sprite-instancer sparks. Road Mode = a tint uniform on the player material + trail colour (no post). **No full-screen quads in XR.** | 0 | ring 48 quads + burst 16 | **high at ground level when it sweeps under the camera**; keep ring width ≤ 15% radius, alpha ≤ .5, one live super at a time | 1 super, 2 rings | T0: ring only |
| 10 | **Dodge afterimages** (KH dodge roll / FF7 dodge, A/B cancel) | Skinned ghost copies cost +1 draw each **and** skinning; do NOT do this on Quest. Cheap form: 2-3 "silhouette streak" ribbons in TRAILS (hip, shoulders) for 150 ms, or a stretched sprite cell. Desktop T2 may add ≤ 2 ghosts: LOD2 mesh, pose snapshot (bone matrices copied once into a frozen Skeleton clone), additive fresnel material shared. | 0 (Quest), +2 (desktop T2) | 3 trails | low (Quest) / medium (desktop ghosts) | 2 ghosts | T1/T0: trail streak only |
| 11 | **Camera shake** | none in XR (see §4). Desktop: ≤ 3 cm / 0.6° decaying kick on the third-person camera only. | 0 | 0 | none | 1 | XR → haptics |
| 12 | Chain lightning / bolts (existing Chain Shock, Shotlock paint later) | existing `fxBolt` in FXB | 0 | ≤ 40 quads per bolt, 3 bolts | low-medium | 3 | T0: 1 bolt, fewer segments |

**Net new: 2 draws** (#2 sprite instancer, #5 HUD instancer), and **−1** when `TGT.mk` moves in (net +1 vs today). If render-style §8's fixed set (particle instancer slot #2, popups slot #5) is built first, combat uses those slots and the net is **0**.

FX GPU at caps (Quest, stereo): arcs 0.08-0.15 + sparks/flash 0.1-0.2 + super ring 0.05-0.1 (rare) + HUD 0.02-0.04 = **~0.25-0.45 ms**. CPU: FXB already rewrites up to 1800 quads; keep combat ≤ ~400 FXB quads (~0.05 ms) and instancers update only new slots (`updateRange`).

## 3. Hit-stop (impact freeze)
**Rule 1: the render loop, the XR head pose and the camera never freeze.** `setAnimationLoop` keeps running at 72 Hz; three.js keeps updating the XR camera from the viewer pose every frame. Hit-stop only changes the **gameplay dt** passed to combat, animation and NPC code.

**Per-entity time scale, not a global freeze.** A global freeze would also stop the player's rig translation, the trails, traffic and audio timing. In XR, stopping the player's forward motion at ~10-15 m/s for 80 ms is a sudden acceleration you didn't cause (a vection jolt). KH/FF7 freeze the attacker's pose and the victim; we copy that.

Proposed (Systems, wallatk.js; ~25 lines, CPU ~0):
```js
const TS={ world:1, stopT:0, stopUntil:0 };            // world = slow-mo scale (§5); per-entity: e.ts, e.stopT
function hitStop(att, victims, ms){ ms=Math.min(ms,150)*(SR_COMFORT.hitstop??1);   // comfort: 1 / .6 / 0
  for(const v of victims) v.stopT=Math.max(v.stopT||0, ms/1000);                  // max, never add (no stacking)
  att.stopT=Math.max(att.stopT||0, ms/1000); }
function edt(e,dt){ if(e.stopT>0){ e.stopT-=dt; return 0; } return dt*TS.world*(e.ts??1); } // real dt drains the timer
```
- **Animation:** each rider has its own `AnimationMixer` on the shared skeleton → `mixer.update(edt(e,dt))`. dt 0 holds the pose exactly (no extra cost). Spring chains (Anika's pigtails/skirt) step with the same scaled dt, or they flop while the body is frozen.
- **Physics/locomotion:** there's no fixed step; each system integrates with `dt`. Victims: knockback slide (`n.kv`), stun/pressure timers and NPC AI all use `edt(n,dt)`, so the knockback starts *after* the freeze (reads as the punch "landing"). **Player in XR:** `Ride` position/velocity keep integrating with real `dt` (the rig keeps moving); only the player mixer, the attack timer `ATK.act.t` and the attack lunge use `edt`. **Player on desktop:** the whole player may freeze (classic feel).
- **Timers:** cooldowns use real dt (they shouldn't stretch). Combo input windows and cancel windows use the player's `edt` and **input is buffered** during the stop (KH: a press during the freeze chains on release), so the stop never eats a press.
- **FX:** hit sparks spawn at impact and play at real time (they sell the hit); the impact flash lasts the freeze length. Audio plays immediately, unscaled.
- **Stacking:** `max()`, not sum. Budget: total player-side stop ≤ 25% of any 1 s window (multi-hit chains: hits 2+ inside 150 ms of each other use the "light" value).

| hit | frames @72 Hz | ms (start values to tune; ref §5.2 suggests 50-60 light, 100-120 finisher) | who freezes |
|---|---|---|---|
| light combo hit 1-2 (J/RB) | 4 | ~55 | attacker pose + victim |
| combo hit 3 | 5 | ~70 | same |
| road finisher / KH finisher | 7-8 | ~100-110 | same, + flash |
| dive / slam / Kick Dive / Shock Dive landing | 8 | ~110 | attacker pose + all victims in radius |
| **STAGGER break** (FF7) | 9-10 | ~125-140 (cap 150) | + optional slow-mo tail (§5) |
| player gets hit | 3 | ~40 | **victim (player) pose only; never the rig in XR** |
| chain lightning per jump | 2 | ~28 | victim only |
| grind/rail knock-back (KH Rail Slide) | 0-2 | 0-28 | victim only (player keeps flow) |

**Comfort rules (XR):** head pose 1:1 always; no camera/FOV/roll change on impact; the player rig never decelerates because of hit-stop; option "Impact freeze: Full / Reduced (×0.6) / Off", default Full on desktop, Reduced on Quest until a headset look; no hit-stop on hits taken while grinding or wall-riding (the player is on a spline at speed).

## 4. Camera shake → haptics (our file: gamepad.js)
XR: **no camera shake at all** (head-locked view moving on its own is the top sickness trigger). Desktop: ≤ 3 cm / 0.6° decaying kick (≤ 120 ms) on the 3rd-person camera only, off with the comfort flag.
Plan (Optimizer, gamepad.js): add one entry point `SR_PAD.haptic(evt, hand)` that maps an event name to **both** the XR actuator (`inputSources[i].gamepad.hapticActuators[0].pulse(i,ms)`, today's gateHaptic logic, plus `vibrationActuator.playEffect` when present) and the desktop pad (`SR_PAD.rumble(strong,weak,ms)`). gateHaptic/phBuzz keep working (they can call it later). Rate limit: one pulse per hand per 40 ms, stronger pulse wins; global scale by the comfort setting.

| event | XR hand | XR intensity, ms | desktop strong/weak, ms |
|---|---|---|---|
| attack start (whoosh) | attacking hand (RB = right) | .25, 20 | 0/.25, 30 |
| light hit 1-2 | attacking hand | .45, 35 | .2/.5, 50 |
| combo hit 3 | attacking hand | .6, 45 | .35/.6, 60 |
| finisher / dive / slam land | both | .85, 70 | .7/.8, 100 |
| STAGGER break | both, 2 pulses 60 ms apart | .9, 50 ×2 | .8/1, 120 |
| Pressured set | attacking hand | .35, 25 | 0/.4, 40 |
| player hit (today 1,120) | both | .8, 90 | 1/.6, 120 |
| perfect dodge / reaction prompt success | off hand | .5, 30 | .3/.3, 40 |
| lock-on acquired / switch | left (LT hand) | .15, 15 | 0/.15, 20 |
| Road super start | both, ramp .3→1 over 3 pulses | 1, 40 ×3 | 1/1, 200 |

## 5. Slow-mo
- Scale **only `TS.world`** (enemies, NPC AI, their mixers, projectiles, enemy FX). In XR the player's rig, the player's input response and the camera stay at 1.0 (all motion you see from your own body stays something you caused).
- Uses: STAGGER break tail (TS.world .35 for 0.3 s), last-enemy finisher (.3 for 0.4 s), Shotlock-style target paint (ref §5.9, *later*): desktop .2 while held; **XR .5 floor, ≤ 0.5 s, then it ends** even if held.
- Ease in 60 ms, out 120 ms (no step change of world motion). Cooldown 3 s between slow-mos. Never during a grind/wall-ride/pole-climb on the player side (camera on a spline).
- **No camera-driven moves**: no slow cinematic pans, orbit-cams, dolly zooms, FOV punches or letterbox in XR. Desktop may do a ≤ 0.4 s gentle FOV narrow (≤ 4°).
- Audio: low-pass/pitch-down on world SFX only (cheap WebAudio filter), player SFX unchanged.
- Optional XR cue instead of camera tricks: a short edge desaturation/vignette via the existing comfort vignette if any; **not** a new full-screen pass.
- Comfort option "Slow-mo: On / Off" (default On desktop, On-reduced (.6 floor) on Quest until a headset check).

## 6. Worst-case characters + FX table (Quest, per eye; ×2 submits without multiview)
Scene: big turf fight. Player + Anika (crew ally) + **3 enemies at LOD0** (rank cap) + 5 riders at LOD1/2, combo finisher + stagger + damage numbers + lock all live, wheel trails on, no pole grind (helix counted in the worst line).
| item | draws |
|---|---|
| player LOD0 (skin + cloth + shared skate) | 3 |
| Anika LOD0 (body atlas + skate) | 2 |
| 3 enemies LOD0 × 3 | 9 |
| 5 riders LOD1/2 × 1 | 5 |
| shadows (player proxy + NPC blob instancer) | 2 |
| TRAILS ring (wheel trails + dash + dodge streaks) | 1 |
| FXB (arcs, bolts, rings, bursts) | 1 |
| **combat sprite instancer** (sparks, flash, stars, pressured rings) NEW | 1 |
| **combat HUD instancer** (bars, reticle, numbers, words, meter, prompt) NEW (replaces TGT.mk) | 1 |
| grind sparks Points | 1 |
| **subtotal** | **26** |
| + pole helix (only if pole grinding mid-fight) | 27 |
| + inverted-hull outlines (5 LOD0 riders), if kept | 32 |
| + render-style fixed-set slots not yet merged (stretched instancer, shield) | 34 |
| desktop only: 2 afterimage ghosts | (36) |

**Within 40 on every line.** CPU submits on Quest without multiview: 26-34 × 2 = 52-68. **Cut order if over:** (1) outlines (−5); (2) enemies 3 → 2 at LOD0 for combat (−2; the locked target always keeps LOD0); (3) fold grind sparks into the combat sprite instancer (−1); (4) HUD bars → locked target only (draws same, fewer verts); (5) T0 FX tier (no flash, words-only numbers); (6) helix off while in combat. Never ship skinned afterimages on Quest.

## 7. Texture budget (KTX2)
| atlas | size | format (Quest transcode) | GPU MB w/ mips | notes |
|---|---|---|---|---|
| combat FX atlas (sparks, flash, ring, star, soft dot, feather, leaf, bolt cells, 8×8 grid of 64²) | 512² | ETC1S → ETC2 RGBA (1 B/px) | **~0.35** | additive cells are greyscale; colour from instance attrs. Could merge into the render-style §8 shared 1024 FX atlas (then 0 extra) |
| SDF glyph atlas (0-9, +, ×, !, words STAGGER / PRESSURED / BREAK / road-finisher names) | 512×256 | UASTC → ASTC 4×4 (1 B/px), linear | **~0.17** | SDF survives ETC1S badly, so UASTC. Or reuse the 1024² trick-name atlas (render-style §8) → 0 extra |
| HP/pressure bars, reticle | — | white cell in the FX atlas | 0 | |
| **total new** | | | **~0.5 MB** (0 if both reuse the planned shared atlases) | 186 → ~186.5 MB of 256. No CanvasTexture in XR (TGT.pv's 128² canvas stays desktop/spray only). |

## 8. Who does what + gates
- **Rydah Systems** (wallatk.js, target.js, turf_dash.js, grind.js): combo chain/finisher, Pressure→Stagger, `TS`/`hitStop`/`edt` and slow-mo in their update code; FXB → additive; the combat sprite instancer and HUD instancer (or slots in the shared FX set); move TGT.mk into the HUD instancer and add an **XR lock-on path** (targeting is desktop-only now); call `SR_PAD.haptic(evt)` at the events in §4.
- **Rydah Optimizer (us):** `SR_PAD.haptic` + rate limit + comfort scale in gamepad.js; this budget; FX tier switch thresholds; texture encodes (`toktx`/basisu commands) for the 2 atlases; perf gate updates below.
- **Rydah Forge / Rigger:** combo hit 1-3, finisher per road, dodge, hit-react, stagger loop, knock-back/recover clips **on the shared rider skeleton** (same bone names, no new bones; Anika's spring bones stay procedural). Clips should mark hit frames and cancel windows (NiER-style flags, ref §3) as clip events/userData so hit-stop fires on the hit frame.
- **Ani (integrator):** runs the gates (only the integrator runs tests, .testlock).
- **Proposed gates** (not written, not run):
  1. `tests/drawcall_budget.py` + `--scene combat`: spawn player + Anika + 3 LOD0 enemies + 5 far, trigger finisher + stagger + 8 numbers + lock; assert characters+FX ≤ 40 and scene ≤ 150; assert FXB/instancer count stays at 1 each.
  2. `tests/hitstop.py`: with a fake XR session (or `renderer.xr.isPresenting` stub) fire a finisher; per frame assert (a) the render loop ran, (b) the camera/rig world matrix changes when the stub head pose changes on **every** frame during the stop, (c) player `Ride.group` keeps moving in XR mode, (d) victim mixer time is unchanged for the stop length ±1 frame then resumes, (e) no stacking above 150 ms, (f) buffered input chains.
  3. `tests/slowmo.py`: TS.world ≤ .5 lasts ≤ 0.5 s in XR, player dt = 1.0, no camera FOV change.
  4. perf_overlay FX-ms check on the combat scene (desktop proxy only until a headset run).

## 9. Reference re-check
Re-read at the end (~09:25 CDT): mtime still 2026-10-30 09:00:12 CDT, md5 096003a5f468850a4884898c7c3d1a0f, unchanged since the first read. No changes to the numbers.
