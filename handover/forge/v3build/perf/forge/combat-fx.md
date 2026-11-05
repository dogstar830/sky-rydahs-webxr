# CombatFX: attack FX module (Rydah Forge, 2026-10-30)
Files: `combat_fx.js` (module), `patch_combat_fx.py` (injects the module before `</body>`; idempotent; takes `argv[1]` or `SR_HTML`, otherwise writes the real html), hook line added at the end of `build_ikki.sh` (backup `build_ikki.sh.bak-cfx-*`), `tests/combat_fx_shots.py` (shots + draw measurement).
Look only. It contains no gameplay or input code. It's inert until called: the pools are prewarmed on the first frame and stay hidden, so they cost 0 draws when idle. `?nocfx` disables the module and `?fxdemo=1` loops every effect for every crew next to the player.

## API (window.CombatFX)
`crew` can be an id (`codee karasu static anubis forest behemoth genesis ttt volt rustclaw`), a display name ("Code : E", "Kogarasumaru"…), a `TURF.crews` index, or `{id}`. Targets and riders can be an Object3D, `{holder}` (an NPC), `{group}` (Ride) or a Vector3. Object3D targets are followed while the effect plays.
- `emit(evt, data)` → returns the sim hit-stop in ms. Event names are exactly the ones `SR_PAD.haptic` uses, and `data` is passed straight to `SR_PAD.haptic(evt, data)` (its `{scale, hand}` opts) unless `data.haptics===false`, so one call fires both the FX and the rumble. Data fields: `{crew,pos,dir,rider,target,arc,strength,scale,hand,haptics}`. Reuse one data object so there's no allocation per call.
  | evt | FX | hit-stop ms (sim only) |
  |---|---|---|
  | attackStart | `slash(rider, arc‖default, crew)` | 0 |
  | lightHit | `hit(pos‖target+1.1m, dir, crew, .7)` | 40 |
  | hit3 | `hit(…, 1.15)` | 70 |
  | finisher | `hit(…, 1.8)` + shatter ring; bolt crews also get lightning from rider to target | 110 |
  | dive | `hit(…, 1.5)` + ground shock ring + shatter decal | 110 |
  | stagger | `stagger(target,"staggered")` | 150 |
  | pressured | `stagger(target,"pressured")` | 0 |
  | playerHit | red flash + ring + sparks on the rider | 0 |
  | dodge | crew afterimage column + ground ring | 0 |
  | lockOn | `lockOn(target‖null)` | 0 |
  | roadSuper | `super(rider, crew)` | 0 |
  `CombatFX.HITSTOP` holds this table.
- `hit(pos, dir, crew, strength)`: frame-1 burst flash, 4-point star, expanding ring, glow, velocity-stretched sparks along `dir`, crew motif and ink motif. Lasts about 0.25 s.
- `slash(riderObj, arc, crew)`: a swept crescent with a hard bright outer edge and a second inner arc in c2. It sheds motif sprites from the blade head. `arc={start:-110,end:110 (deg from forward), radius:1.2, height:1.0, tilt:0 (deg roll: 35 diagonal, 90 vertical kick), width:.45, dur:.22, dir:Vector3 forward}`. Without `dir` it uses the object's world +Z, so **Systems should pass `dir`** (the rider's facing).
- `lightning(from, to, crew)`: a jagged camera-facing bolt plus 2 branches, regenerated every 34 ms, with end flash and sparks. Lasts 0.3 s.
- `stagger(target, "pressured"|"staggered"|"off")`: FF7 readability. **Pressured** = 3 amber chevrons orbiting over the head plus a pulsing broken ground ring. **Staggered** = white flash, a gold shatter ring (billboard and ground), 10 gold shards, then 4 gold diamonds and stars orbiting with a counter-rotating ground ring until `"off"`. Up to 8 targets at once.
- `super(rider, crew)`: KH finisher / Road super. White flash, ground ring and shatter ring, a halo above, a light pillar, 20 radial streaks, an 18-motif spiral rising round the rider, and a motif burst. Bolt crews (Code : E, Volt) add 4 lightning strikes. Lasts about 0.9 s.
- `lockOn(target)`: a white and pink counter-rotating reticle with an amber snap-in ring. `null` clears it.
- `update(dt)`: auto-ticked from `animated` using real frame time, clamped to 50 ms. Set `CombatFX.manual=true` to drive it yourself.
- Also available: `timeScale`, `paused`, `clear()`, `stats {sprites, ink, ribbons, draws, prewarmMs}`, `CREWS`, `demo.fire(crew, kind)`, `demo.auto`.

## Hit-stop contract (from Systems)
Hit-stop is applied **in the sim only**: scale the gameplay dt, never the XR camera or head pose, and never shake the camera. `CombatFX.update` must receive the **real** dt. The auto-tick already does this, so sparks and flashes keep moving during the freeze, and that's what sells the impact. Every hit has a full-intensity frame-1 flash so it reads even through a 150 ms freeze. In `?fxdemo=1` the demo target bobs on sim time and freezes for the returned hit-stop while the FX keep running. The label shows "HIT-STOP n ms (sim only)".

## Per-crew road look (c1 / c2 / ink motif)
| crew | colours | motif (additive) | ink (dark, normal blend) |
|---|---|---|---|
| Code : E | gold #ffc21a / pale gold | bolt glyph + stars, lightning in hits and super | black bolt cracks |
| Kogarasumaru | red #ff2233 / salmon | crow feathers | black crow feathers |
| Static Angels | purple #a040ff / cyan #5ff4ff | halo rings | none |
| Anubis | teal #00d6b4 / sand gold | ankh + shards | none |
| Sleeping Forest | deep green #1fbf55 / white | leaves + glow | dark-green thorns |
| Behemoth | orange #ff6a00 / amber | rock shards | black rock shards |
| Genesis | magenta #ff2bd6 / gold | halo + stars | none |
| Tool Toul To | rust #d0602a / gray #b8bcc4 | gears + rivet shards | gray gears |
| Volt | hot pink #ff3fa8 / yellow #fff23a | bolt glyph, lightning in super | none |
| Rust Claw | orange #ff7a1a / rust | claw marks | dark-rust claw marks |
Black can't show under additive blending, which is why the third ("ink") draw exists, for the black and dark motifs.

## Cost
- Draws: **0 idle, at most 3 while live**: 1 additive sprite InstancedBufferGeometry (1024 slots), 1 additive merged ribbon BufferGeometry (24 ribbons × 28 points, drawRange = live ribbons only), 1 ink sprite instanced mesh (256 slots). Each mesh is hidden when it has 0 live items.
- Textures: **1** procedural canvas atlas, 512×512 RGBA (R = shape, G = hot core), 4×4 cells: spark, ring, dot, feather, leaf, thorn, halo, claw, shard, gear, reticle, chevron, shatter, bolt, ankh, burst. Mipmapped, about 1.4 MB of GPU memory.
- Shaders: 3 ShaderMaterials (additive and ink share a vertex shader), compiled at init with `renderer.compile` on a private scene (prewarm 14–19 ms, once). The renderer program count did not change during FX in the measurement (67 before and during).
- Blending: additive (ink uses normal blending), `depthWrite:false`, `depthTest` on, no fog, no postprocessing needed. In VR the bloom-friendly colours carry the glow by themselves.
- Allocation: all typed-array pools, scratch vectors and one shared emit-params object, so nothing is allocated per hit. When a pool is full the oldest slot is overwritten.
- CPU: about 20 floats written per live sprite per frame. A heavy multi-effect burst is about 60–120 sprites.

## Measured (fxdemo_scratch.html = the 09:16 real build + patch_combat_fx.py; ?tier=hd&seed=1&fxdemo=1, 1920x1080 @1.5, swiftshader; tests/combat_fx_shots.py, raw data in perf/forge/combat-fx-shots.json)
- `renderer.info` on a direct scene render: 107 calls before FX, 100–102 during FX. The world/NPC culling noise between frames (about ±6) is bigger than the FX delta. Counted from the module itself, `CombatFX.stats.draws` = **0 idle, 2–3 during** (3 for crews with ink motifs; super_codee = 97 sprites + 12 ribbons + 3 ink in 3 draws). Textures 76 → 76, programs 67 → 67 (no compile mid-fight). Prewarm 14–19 ms, once.
- Shots: shots/hero/combat_fx_<crew>.png ×10, combat_fx_super_codee.png, combat_fx_super_karasu.png, combat_fx_pressured_forest.png, combat_fx_contact_sheet.png (10 crews). 0 page errors.
- (v1 gap, fixed in v2 below: white wash-out under HD bloom.)

## v2 look pass (2026-10-30 10:20–12:05 CDT, scratch copy only; the real html was never built or written)
What changed in combat_fx.js:
- **No more white wash-out.** Hot cores are now the crew colour ×1.35 instead of a mix toward white. Output goes through a hue-preserving clamp (max channel ≤ .92 sprites / .85 ribbons). White now appears only as a 45 ms pinpoint on the hit's first frame (and when white is passed explicitly). Big flashes use crew c1 and stagger uses crew c2 instead of white.
- **Blend:** premultiplied additive (`One, OneMinusSrcAlpha`, coverage alpha .75), still `depthWrite:false`, 1 draw per pool. Plain additive turned red into pink over the purple-blue plaza; with partial occlusion the crew hue holds.
- **Dark crew-tinted underlay** (ink pool, now 512 slots, still 1 draw) behind rings, the reticle, chevrons, stars and motifs.
- Status FX take the crew colour: `stagger(target, phase, crew)` and `lockOn(target, crew)`; `emit` passes `data.crew`. Without a crew they fall back to amber/gold/white.
- Deeper palettes: Kogarasumaru c1 #ff1020 / c2 #b00010, Code : E #ffb000/#ffd84a, Behemoth #ff5a00/#ff9a1a, Rust Claw #ff6a10/#b8400c, Sleeping Forest #12a845/#e8ffe8. Volt c1 is pushed to #ff2f78 to make up for the scene's blue shift; the target in the hue check is still Volt's #ff3fa8.
- `?fxdemo=1` now has a charcoal capsule stand-in target (demo only, +1 draw, +1 program, never in normal play). It's placed 3.5 m in front of the camera and 0.9 m right, and the demo slash wraps it.
- `CombatFX.hide` (test helper) hides the FX meshes so a test can grab a no-FX base frame.

Measured (10 per-crew shots 11:42–12:02 CDT, same standard): scene calls 108 before FX → 102 during (world noise); **CombatFX draws 3** (sprites + ribbons + ink); textures 79 → 79; programs 68 → 68; prewarm 15 ms; 0 page errors.

Hue check (`tests/combat_fx_hue.py final`, straight from the saved PNGs, no re-render). FX pixels = shot vs. its own no-FX base frame (max channel Δ > .22) inside the FX zone. Core-edge band = 70–95th percentile of brightness. Measured hue = the 10° histogram peak of pixels with saturation > .25, so readings are ±5°. Pass = within 10° of c1 or c2, and median saturation ≥ .6. Output: perf/forge/combat-fx-hue-final.json.
| crew | target c1 / c2 hue | measured | sat | pass |
|---|---|---|---|---|
| Code : E | 41 / 47 | 55 | .87 | yes (8° from c2, 14° from c1) |
| Kogarasumaru | 356 | 355 | .89 | yes, reads red |
| Static Angels | 270 / 184 | 275 | .64 | yes |
| Anubis | 170 / 40 | 175 | .91 | yes |
| Sleeping Forest | 140 / 120 | 145 | .70 | yes |
| Behemoth | 21 | 25 | .91 | yes |
| Genesis | 312 / 42 | 305 | .73 | yes |
| Tool Toul To | 20 / 220 | 25 | .73 | yes |
| Volt | 327 / 56 | 335 | .69 | yes |
| Rust Claw | 23 | 25 | .92 | yes |
Watch list: Code : E gold drifts toward yellow (55° vs 41° c1), and Static Angels saturation is close to the limit (.64).
Shots: shots/hero/combat_fx_<crew>.png ×10 (v2), combat_fx_contact_sheet.png (v2), combat_fx_contact_sheet_v1.png (old). combat_fx_super_*.png and combat_fx_pressured_forest.png are still v1 (10:39–10:42) and were not re-shot.

## v3: Rigger FX attach points (2026-10-30 evening; only combat_fx.js changed)
Rigger's `srFXAttach` (jackets.js) puts empty Object3Ds `srFX_handL/R, srFX_footL/R, srFX_wheelL/R` on the bones of poser riders and crew NPCs, exposed as `rider.userData.fx = {handL,...}`. The wheel points sit at the bottom of the front wheel and follow the 1.25x skate. CombatFX resolves them like this:
- `data.rider` can be the rider root (RIDERS.player / NPC root), `Ride.group` (falls through to RIDERS.player), an NPC `{holder}`, or any parent whose direct child carries `userData.fx`. The lookup is cached per rider in a WeakMap; a miss is retried at most once a second, because the points attach after the GLB loads. Nothing is allocated per hit.
- The name comes from `data.fxName` ("footL", ...) or `data.fx` when it's a name string. "foot", "hand" or "wheel" alone takes its side from `data.side` ("Left"/"Right"). Rigger's `fx` positions map (an object) is ignored, since the live Object3Ds are used instead.
- `attackStart` with an attach point: **kick** (foot or wheel name) = a wheel trail ribbon (crew c1, 0.11 m) plus a thin foot trail (c2). **Punch** (hand) = a hand trail (0.08 m). Trails sample the point's world path for 65% of their 0.3–0.36 s life, then the tail catches up with the head. They shed motif sprites. With no attach point you get the old crescent `slash`.
- `lightHit / hit3 / finisher / dive` with `rider` + `fxName`: sparks spawn at the attach point (the wheel for kicks), otherwise at `pos` or the target as before.
- `roadSuper` with an attach-point rider: the usual super, plus a burst and a 0.6 s trail from **both wheels**.
- `fxCharge` scales intensity by 1 + min(charge, 1.5) × 0.6, applied to the hit strength and the trail width.
- New helpers: `CombatFX.trail(attachObj, crew, width, dur)`, `CombatFX.attach(rider, name)`, and `CombatFX.fromHitFrame(ev, evtName='lightHit', crew)`. The last one is a direct adapter for Rigger's `onHitFrame` event (uses rider, fxName, side, fxCharge, pos, target; haptics off).
- Cost: unchanged. Trails share the ribbon pool (24 slots), so it's still 3 draws max and 0 new programs.
Test (no hero shot yet: the .testlock was busy at 21:30, and a first attempt had the trail expiring before capture): `tests/combat_fx_kick.py` (takes .testlock) on a fresh `build_copy.sh` scratch build with `?player=ikki&combatposes=1`. It confirmed 6 attach points on the player, `CombatFX.attach` resolving, and `onHitFrame` firing with `fxName:'footL', fxCharge:1.03` into `fromHitFrame` (hit sparks at wheelL). The shot test uses `CombatFX.timeScale=.35`, because swiftshader frames are far slower than the poser's clamped game dt. In-game, keep timeScale at 1.
