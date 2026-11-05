# Sky Rydahs — Combat & Attack Animation Plan (FF7R/Rebirth + KH feel, Air Gear canon)
Owner: Rydah Rigger (poses/animation). Gameplay (input, hitboxes, damage, stagger meter) = Rydah Systems. VFX = Forge. PLANNING ONLY — no game code changed.
Sources read: combat-ff7-kh-reference.md (§5 mapping, top recs), airgear-deep-reference.md §7.2 (Ikki Wing/Wheel Spin Drop, Kazu, Buccha), ikki_skate.js (RIDER_JOINT_LIMITS, RIDER_FEEL, RIDER_SKATE_STATES, W, slew 720°/s, plant()), wallatk.js/MOVESETS (move kinds dash/sweep/cone/chain/slam/dive), COMBAT_PLAN_NOTES.md (C1–C6), shared skeleton README (91 joints; Anika +16 springs), DEMO_STATUS.md.
Designs are original: we borrow *structure* (chain→finisher, homing gap-closer, pressure→stagger, Flowmotion, Limit) not poses or timings from either game.

## 0. Conventions
- Joint targets: poser model-space Euler deg [x,y,z], same convention as RIDER_JOINT_LIMITS / RIDER_SKATE_STATES; K* = striking side (= feel.kickSide or `side` arg), S* = support side; Right mirrors y/z.
- Frames at 72 fps (1 f = 13.9 ms). Phases: **A** anticipation, **X** active (hitFrame inside), **R** recovery. **C** = cancel window (frames from move start).
- Every key below has been checked against RIDER_JOINT_LIMITS (ranges in brackets where tight). Spine twist total ≤ 40 (split .4/.3/.3) — values given as *total* twist `Tw` and distributed by the existing split.
- Skates column: **ROLL** = legs keep the skating pose layer (stride/tuck weight held, only upper body overlays), **PLANT** = strike leg(s) posed, plant() active on support foot, **AIR** = no plant, **RAIL** = grind/pole pose layer kept.
- Hand: **F** fist, **R** relaxed, **O** open/blade (new pose, see §3.4).

## 1. Move list (mapped to FF7/KH patterns)
| ID | Move (HUD name where it fits) | Pattern source | Input (proposal, Systems owns) | Kind (wallatk) |
|---|---|---|---|---|
| L1 | Jab Carve | KH ground combo hit 1 | J/RB tap | cone |
| L2 | Cross Carve (back-hand) | KH hit 2 | tap in window | cone |
| L3 | Spin Heel | KH hit 3 (rotation hit) | tap | sweep |
| LF | Road Finisher — Caali: **Lightning Dash Strike**; Ikki: **Wing-Sweep Kick**; Anika: Ribbon Pirouette; crew: template | KH finisher (commits) | tap | per rider |
| H1 | Heavy: Wheel Drive Kick (hold → release) | FF7 heavy/charged ability | K/RMB/hold | slam |
| G1 | Homing Lunge (gap closer) | KH Sonic-Blade-like homing dash, FF7 Braver lunge | J at range > 3 m with commit-lock | dash |
| AL | Launcher (from H1 or L3 hold) | KH launch → air combo | K + up | sweep |
| A1/A2 | Air Kick 1/2 | KH aerial combo | J in AIR | cone |
| AF | Air Finisher — Caali: **Thunder Drop**; Ikki: Raven Dive Kick | KH aerial finisher | J 3rd / K in air | dive |
| FG | Grind Sliding Slash (C4) | Flowmotion out of rail | RB/X on grind | dive (homing) |
| FW | Wall Kick Dive (C5) / Wall-top Shock Dive | Flowmotion wall | RB after wall-kick / top of wallride | dive |
| FP | Pole Buzz Spin (launches, sets Pressured) | Flowmotion pole | RB on polegrind | sweep |
| GD | Guard (hold) / Parry (frame-tight tap) | FF7 block + KH Guard/Reprisal | X hold / tap in telegraph | — |
| DG | Skate Dash (dodge) / Roll | FF7 dodge, KH Dodge Roll | B + dir | — (i-frames) |
| HL/HH/HK/HU/HW | Hit react: light flinch, heavy stagger, knockdown, launch, wall bounce | both | — | — |
| ST | Stagger (FF7 "STAGGERED" hold) / Pressured | FF7 | — | — |
| SP | Road Supers (Limit) — Caali **Chain Shock → Storm Line**, Ikki **Wing Road: Gale Ascend**, Anika **Braid Cyclone**, crew template | FF7 Limit / KH Drive finisher | RT+LB (HOLD per Oliver) | chain / per rider |

## 2. Key poses & timing (72 fps)
Timing column `A/X/R` in frames; hit = hitFrame (absolute). Root motion = metres along facing applied by Systems (poser only reports it). Lead = body part that initiates (drives slew-order and active-cap set).

### 2.1 Light chain + finisher (base rider = default feel; per-rider rows scale A by `windup`, X by `release`)
| ID | A/X/R (hit) | Cancel C | Root motion | Lead | Hand K/S | Skates |
|---|---|---|---|---|---|---|
| L1 | 5/3/12 (f7) | chain f9–20; dash/jump f8+ | +0.3 m | hips→K shoulder | F/R | ROLL |
| L2 | 4/3/13 (f6) | chain f8–20; dash/jump f7+ | +0.3 m | S shoulder (counter-rotate) | R/F | ROLL |
| L3 | 6/5/16 (f9) | chain f12–27; dash f11+ | +0.4 m, 360° Hips yaw over X (rider only) | hips→K leg | F/F | PLANT (support), K leg swings |
| LF | 8/6/22 (f12) | none until f30 (commits); dash only after recover | rider-specific (Caali dash 3.5 m) | per rider | F/F | per rider |
| H1 | 14 (+hold ≤ 72)/5/24 (rel+3) | dash f(rel+10)+ | +0.6 m | S leg load → hips → K leg | F/F | PLANT, kick leg strike |

Key poses (degrees; only changed bones listed, others from current locomotion layer):
- **L1 A (f0–5)**: Spine[16,Tw+10 →away,0], KArm[30,0,20], KForeArm[-110,0,0], Hand K F. **X (f6–8)**: Hips[0,-12,0], Spine[20,Tw-20,0], KArm[-85,0,10], KForeArm[-12,0,0], KHand[0,0,-10], Head[-6,-15,0] (eyes track target; look-at stays inside Neck/Head limits).
- **L2 X**: mirror of L1 with Tw +24 (≤40), SArm[-80,0,35], SForeArm[-20,0,0], KArm[35,0,15] (counter-swing, inside ext 50).
- **L3 A**: crouch-lite SUpLeg[-60,0,6] SLeg[96,0,0] SFoot[-24,0,0]; Hips yaw wind −30. **X**: KUpLeg[-70,0,38] KLeg[20,0,0] KFoot[30,0,0] (heel leads), Hips yaw sweeps +330 (root yaw, not joint — Hips joint only ±30 lean), Spine[10,0,-10], both Arms[-20,0,95] (wing-open, ≤120). **R**: K leg returns under hip; landing dip reuse (`landK=.5`).
- **H1 A/hold**: = `crouch` state keys at 70 % depth + KUpLeg[-95,0,10] KLeg[120,0,0] (chamber), KArm[40,0,20] SArm[-60,0,30]. **X**: KUpLeg[-80,0,8] KLeg[6,0,0] (≥ softKnee clamp zone, soft) KFoot[35,0,0], Spine[-8,0,0] (lean back, ext ≤10), Arms counter [40,0,40]/[-50,0,30].

### 2.2 Gap closer, dodge, guard
| ID | A/X/R | Cancel | Root motion | Lead | Hand | Skates |
|---|---|---|---|---|---|---|
| G1 Homing Lunge | 6/ travel 8–22 (dist/14 m·s⁻¹) /10; hit on arrival | into L1/L2 on arrival (KH chain continue); jump | Systems homing to target, ≤ 6 m, yaw-only | head+chest (tuck), then K arm | F/F | ROLL in `tuck` pose (W.tuck held 1) |
| DG Skate Dash | 2/10 (i-frames f2–10)/8 | any attack f12+ | 2.5 m in stick dir, yaw-only | hips | R/R | ROLL: deep crouch-lean, Hips z ±18 toward dir |
| DG Roll (only off-skate knockdown recover) | 3/14/8 | — | 1.5 m | spine curl | F | AIR→plant at f17 |
| GD Guard | 4 in / hold / 6 out | parry tap window f0–8 = Parry | none | forearms | F/F | ROLL, crouch .8 |
| GD Parry (Reprisal-like) | 0/4/14 | counter L1 f6–18 | +0.2 m | K forearm sweep out | O/F | PLANT |
- Lunge pose: Spine[24,0,0] Spine1[18,0,0] Neck[-20,0,0] Head[-15,0,0] (eyes forward), KArm[-40,0,20] KForeArm[-90,0,0] SArm[45,0,25] — reads as a sprint-tuck, swings to L1 X on arrival.
- Guard: both Arm[-75,±15,30] ForeArm[-125,0,0] Hand[10,0,0] F; Spine[18,0,0]; legs crouch .8.

### 2.3 Air combo
| ID | A/X/R | Cancel | Root | Lead | Hand | Skates |
|---|---|---|---|---|---|---|
| AL Launcher | 6/5/14 (f9) | jump f10–20 (follow target up, KH) | rider +1.2 m up if jump-cancel | S leg push → K knee rising | F/F | PLANT→AIR |
| A1 | 3/4/10 (f5) | A2 f8–18, AF f8–18 | Systems holds altitude (hover gravity .3 during combo) | K knee | F/R | AIR |
| A2 | 3/4/10 (f5) | AF f8–18 | same | S heel (scissor) | R/F | AIR |
| AF dive | 8/until ground/18 | none (commits) | Systems dive vector to target/ground | both feet | F/F | AIR → PLANT on impact f0 |
- AL X: KUpLeg[-120,0,6] KLeg[30,0,0] (rising knee, flex ≤125), Arms[-150,0,30] (upward, ≤170).
- A1 X: KUpLeg[-100,0,20] KLeg[10,0,0]; A2 X: SUpLeg[-100,0,-10] SLeg[10,0,0], KUpLeg[15,0,0] (ext ≤18).
- AF A: tuck (`tuck` keys) + Spine[27,0,0]; X: both UpLeg[-50,0,6] Leg[15,0,0] Foot[40,0,0] (stomp), Arms[30,0,70]. On contact: `land` dip forced 1.0, plant() snaps both feet (±3 mm gate).

### 2.4 Flowmotion (out of traversal; base pose layer = current state, attack overlays upper body)
| ID | From state | A/X/R | Cancel | Root | Lead | Skates |
|---|---|---|---|---|---|---|
| FG Grind Sliding Slash | grind | 4/6/12 then exits to `air` | air combo f12+ | Systems homing off rail (dive kind) | S arm sweep, hips unwind | RAIL until f4, then AIR |
| FW Wall Kick Dive | wall (after kick) | 5/until contact/16 | none | dive vector | K foot | AIR |
| FW Shock Dive | wall top | 10/until ground/18 | none | down | both fists | AIR→PLANT |
| FP Pole Buzz Spin | polegrind_climb/top | 6/18 (3 hit ticks f8,f14,f20)/12 | launcher-follow jump f24+ | none (orbits pole: existing poleAxis) | legs extended out | RAIL |
- FG X: Hips (grind stance yaw kept), Spine Tw −35, KArm[-60,0,100] KForeArm[-15,0,0], Hand O. FP X: KUpLeg[-70,0,40] KLeg[5,0,0] (scissor out), grip arm unchanged from polegrind keys (hand stays F on pole), free arm [-20,0,110].

### 2.5 Hit reactions & stagger (driven by Systems on victim; all ≤ 720°/s — reactions never need the raised cap except HU/HW first frame, see §2.7)
| ID | Frames | Root (Systems) | Pose peak | Skates |
|---|---|---|---|---|
| HL light flinch (dir: F/B/L/R) | 2 in / 10 out | 0.15 m knock | Spine[-8,±10,±8] Head[-15,0,±12] arms[25,0,30] | ROLL |
| HH heavy stagger | 4/26 | 0.6 m slide | Spine[-10,0,±12] Hips[-15,0,0] UpLeg[-20] Leg[60] arms flail [30,0,80] | PLANT both, skid |
| HK knockdown | 6 fall/40 down/24 getup (getup cancellable by DG roll f50+) | 1.5 m | down: Hips[30,0,0] Spine[27..-10] tuck curl; root pitch by Systems | none (ground) |
| HU launch | 3/until apex/→HK or AirRecover (A) | Systems ballistic | Spine[-10,0,0] Head[-30] arms[40,0,90] legs trail | AIR |
| HW wall bounce | 2 impact hold (hit-stop)/8 rebound/→HK | reflect | flat back: Spine[-10] Head[-20] Arms[30,0,110] | AIR |
| ST Pressured | loop 1.2 s | none | idle +Spine[8] guard-low arms, faster breathing ×1.5 | ROLL |
| ST Staggered | 8 in / loop until Systems clears / 18 out | drifts to stop | knees buckle Leg[110] UpLeg[-70] Spine[27,0,8] Head[25,0,0] (head down), arms hang Arm[-10,0,10] Hand R, slow sway 0.5 Hz | PLANT both |

### 2.6 Road Supers (Limit) — ~2–3.5 s, rider invulnerable; Systems drives meter
| Rider | Name | Beats (frames) | Root | Signature pose | Canon tie |
|---|---|---|---|---|---|
| Caali G | Storm Line (ends with **Chain Shock** chain arcs) | coil 18 → 3× zig dash-strikes 10 each → overhead fist plant 12 → recover 30 | 3 dashes ≤ 4 m each, yaw only | quiet upper body, then single explosive fist drive Arm[-160,0,20] → slam | "controlled power"; Code:E lightning |
| Ikki | Wing Road: Gale Ascend | Wheel Spin Drop windup 24 (stand, wheels spin) → rip-start dropkick 8 → rising wing spiral 40 → dive 20 | forward 5 m then up 4 m | arms wings Arm[-10,0,115], dropkick both UpLeg[-90] Leg[10] | Wheel Spin Drop, Wing Road |
| Anika (APPROVED (Oliver via Forge 14:39 CDT)) | Braid Cyclone | 3 pirouettes 18 each (Hips root yaw) → arabesque kick 10 → bow 24 | orbit 2 m | playful arms Arm[-150,0,60]; spring bones drive the read (braids/skirt) | original |
| Crew template | `<Crew> Road Rush` | windup 16 → 2 dash hits 10 → finisher (crew kind: slam/sweep/dive) 12 → recover 24 | ≤ 4 m | reuse LF + H1 keys with feel row | n/a |

### 2.7 Slew cap & plant()
- Current cap 720°/s (10°/f) global. L1 arm from A→X is ~115° in 3 frames → 38°/f: with the cap it would arrive after the hit (12 f). **Proposal: `RIDER_POSE_ACTIVE_DEG_S = 1800` (25°/f) applied only to the move's `lead` bone chain during X frames** (Arm/ForeArm/Hand or UpLeg/Leg/Foot of the striking side, plus Spine twist). Everything else (support leg, head, hips, fingers) stays at 720. Justification: strikes need 2–4-frame snaps to read as impact (KH/FF7 active frames are ~2–5 f at 60 fps); limiting the raised cap to one chain and ≤ 6 frames keeps the anti-pop guarantee for blends, and the soft clamp still bounds amplitude. Recovery uses 720 again (gives the "settle").
- Moves needing it: L1, L2, L3 (K leg), LF, H1 X, Parry, A1/A2, AL, FG, FP, supers' hit beats. Not needed: guard, dash, lunge travel, reactions (except HU/HW first 2 frames at 1440 so a heavy hit reads; victim only).
- plant(): stays ON for ROLL and PLANT moves (support foot), OFF during AIR and while the K foot is the striking foot (only S foot planted; plant uses S foot's y as `lo`). New flag per move `plant:'both'|'S'|'off'`. plant()'s correction stays at 720°/s (no raised cap — it would jitter feet).

## 3. Integration into ikki_skate.js (data-driven)
### 3.1 New data table (one entry per move; no per-move code)
```js
RIDER_COMBAT_MOVES = {
  L1:{ base:'stride', A:5, X:3, R:12, hit:[7], cancel:{chain:[9,20], dash:[8,99], jump:[8,99]}, root:[0.3,0],
       lead:'KArm', plant:'S', hand:{K:'fist',S:'relaxed'}, activeCap:1800, legs:'roll',
       keys:[[0,{...}],[5,{...}],[8,{...}],[20,{...}]] },   // frames; same bone keys as RIDER_SKATE_STATES
  ...
}
```
- `keys` in frames (converted to s internally = /72) so feel scaling reuses `riderStateTiming` (A→windup, X→release).
- `legs:'roll'` → overlay masks legs (upper-body only weight); `'plant'|'air'|'rail'` → full body.
- Rider overrides: `RIDER_COMBAT_MOVES_BY_RIDER['caali-g'].LF = {...}` (finisher/super only).

### 3.2 States & W
- One generic overlay state `atk` (W.atk) sampled from the active move (avoids 25 W entries); plus `react` (W.react) and `stagger` (W.stagger) and `guard` (W.guard, hold loop). Add to ST list so stateName() reports them.
- Enter blend: `enter = A/72` capped .06 s for chains (chain→chain cross-fade 3 f); exit `R/72`.
- Upper-body mask weight `W.atkUpper` for legs:'roll' moves so stride keeps cycling.

### 3.3 API for Rydah Systems
```js
rider.setState('atk',{ move:'L1', step:1..4, side:'Left'|'Right', target:Object3D|null, rider:'caali-g' });
rider.setState('react',{ type:'light'|'heavy'|'knockdown'|'launch'|'wallbounce', dir:THREE.Vector3 });
rider.setState('stagger',{ level:'pressured'|'staggered' });   rider.setState('guard',{hold:true});  setState(null) clears
rider.combatEvents = { onHitFrame(move,idx,boneWorldPos), onCancelOpen(move,kinds[]), onCancelClose(move), onRecover(move), onEnd(move) };
rider.combatQuery() -> { move, frame, phase:'A'|'X'|'R', cancel:[...], rootDelta:[fwd,up] }
rider.combatHitStop(sec)   // freezes OS.t advance only (Systems scales sim dt anyway; poser must not advance under hit-stop)
```
- `step` = combo-step parameter: picks L1/L2/L3/LF; also flips side on L2 automatically.
- Events fire from the poser's own clock (OS.t), once per frame crossing, deterministic at any dt (cross-check with frame index, not dt equality).
- Poser NEVER moves the root; it reports `rootDelta`, Systems applies (keeps collision/VR owned by Systems).

### 3.4 New hand pose
`RIDER_HAND_POSES.open` (blade/parry): Index..Pinky [5,8,5,spread 0], Thumb [0,5,5,10,10]. Inside finger limits.

## 4. Per-rider feel rows (add to RIDER_FEEL; combat-only keys, defaults = 1)
| Rider | atkWindup | atkRelease | atkRecover | armChainAmp | spineTwist | rootMul | overshoot | finisherKind | note |
|---|---|---|---|---|---|---|---|---|---|
| default/crew | 1 | 1 | 1 | 1 | 1 | 1 | 0 | per MOVESET | template |
| caali-g | .70 | .80 (hits ≤720 except lead) | .80 | .85 | .7 | 1.25 | 0 (clean stops) | dash (Lightning Dash Strike) | controlled power: still body, short hard bursts |
| anika (APPROVED (Oliver via Forge 14:39 CDT)) | .85 | .85 | 1.1 | 1.2 | 1.25 | .9 | .12 (springy follow-through, plus spring bones) | sweep (Ribbon Pirouette) | style: flowing, extra rotation, longer recover for flair |
| ikki | 1 | .9 | 1 | 1.3 (wings) | 1.1 | 1.1 | .06 | sweep (Wing-Sweep Kick) | airy, open; air moves +10 % hang |
Overshoot uses an eased target past the X key then back within R (amplitude still soft-clamped).

## 5. VR comfort & performance
- Player camera: own attacks NEVER rotate the XR camera (yaw/pitch/roll). Lunge/dash/root motion = translation only along the existing yaw; rig follows yaw + height (wallatk rule). L3/supers' spins rotate the **body**, not the rig; Quest 1st-person hides or fades the local body mesh during 360° spins (or camera stays forward).
- Root motion caps on Quest: ≤ 6 m/lunge, peak accel ≤ 20 m/s², no vertical root on own ground attacks except jump-cancels the player initiated; supers: vignette 30 % during dashes; no camera shake (target flash + rumble instead); hit-stop scales sim dt only, never head pose.
- Desktop: may add 3rd-person camera nudge ≤ 2° on finishers.
- Perf: purely procedural on existing bones — 0 new draws, 0 new textures/meshes; weapon none (fists/skates). CPU budget: +0.15 ms/frame per posed rider on Quest (sampling one move table + mask), ≤ 0.6 ms for 4 nearby combatants; far LOD riders (LOD2) skip atk overlays except reactions and use 1/2 rate update. No allocations per frame (pre-built key arrays, reused quats).

## 6. Build order & test gates (dependency order; each gate must pass before next)
| Gate | Layer | Acceptance checks (automated in a test page like attacks_diag.html, sweep all riders × feel rows × dt {1/72,1/90,1/30}) |
|---|---|---|
| G0 | Data + sampler (`RIDER_COMBAT_MOVES`, atk/react W) | joint-limit violations 0 (pre-clamp keys inside limits); spine twist total ≤ 40; JSON lint; existing skate tests unchanged |
| G1 | Light chain L1–L3+LF + HL/HH reacts | hitFrame events fire exactly once at expected frame ±0; cancelOpen/close frames match table; slew ≤ 720°/s on all non-lead bones, ≤ activeCap on lead only during X; feet planted on ground strikes ±3 mm (S foot / both); stride continues under ROLL moves (leg phase drift 0); chain at 4 steps in 1.2 s with no pop (max per-frame quat delta < cap) |
| G2 | Lunge G1 + DG dash + Guard/Parry | rootDelta reported, root untouched by poser; lunge arrival → L1 blend ≤ 3 f; i-frame window events correct; XR camera rotation delta from own moves = 0 |
| G3 | Air AL/A1/A2/AF + HU/HW/HK | plant() off in AIR (no foot correction); AF landing feet ±3 mm within 2 f of contact; knockdown getup ends in idle with limits 0 |
| G4 | Flowmotion FG/FW/FP | rail/pole base layer preserved (grip hand stays on pole ±1 cm); exits to air without W sum > 1.05; poleAxis honoured |
| G5 | Stagger poses + Supers (per rider) | per-rider feel rows applied; Anika spring bones stable (no NaN, amplitude < limits); Quest perf: frame ≤ 13.9 ms with 4 combatants, poser CPU ≤ 0.6 ms; 0 new draw calls (renderer.info diff) |

## 7. Answers from Rydah Systems (2026-10-30 12:23 CDT) — these override earlier sections where they differ
| # | Answer | Effect on this plan / implementation |
|---|---|---|
| 1 | Chain = 3 hits on J/RB. Hits 1-2 light, A/B cancel after 0.16 s; hit 3 IS the finisher (2.4x knockback, not cancellable); chain resets after 0.6 s idle. Steps 0/1/2 -> light1/light2/finisher. No 4th hit. Heavy provisional: hold J >= 0.35 s, charge cap 1.0 s, fires on release. | L3 (Spin Heel) dropped from the ground chain (kept as a later launcher candidate). `RIDER_COMBAT_STEP_MOVES=['light1','light2','finisher']`. Cancel opens at f12 (0.167 s, not feel-scaled), closes at move end; finisher `cancel:null`. Heavy: `hold:true, holdMax:1.0`, `combatRelease()` fires it. |
| 2 | Super = Hold RT 0.5 s (provisional). LT = lock-on. | Super layer (G5) keys on RT hold; nothing in G1. |
| 3 | Gameplay is authoritative for hits (radius/cone). Hit window opens on my `onHitFrame` (fallback: their timer); bone position only for FX. They own parry/guard window logic; I animate. | `onHitFrame.pos` = lead hand/foot world pos (FX only). No hitboxes in the poser. |
| 4 | Poser reports desired root motion; Systems applies through collision (14 m/s, 6 m max; XR 3 m max, no vertical). | `combatQuery().root = {fwdVel, up:0, total, applied:false}`; poser never moves the root. |
| 5 | Hit-stop freezes the attacker's move clock and the target; smoothing may run, pose must not advance. | `combatHitStop(ms)` on attacker AND victim freezes the move clock; slew keeps settling toward the frozen target. |
| 6 | NPCs use the same poser for reacts/stagger. LOD: full < 12 m, key poses only 12-30 m, none > 30 m or offscreen. Cost check with Optimizer. | G2 task: `combatDetail` per rider (full / keys = sample only at key frames, no slew stats / off). Not in G1. |
| 7 | Air-hit float >= 0.25 s per hit, reduced gravity. | Air moves (G3) authored with X+R >= 18 f per hit. |

## 8. G0/G1 implementation notes (2026-10-30, ikki_skate.js; flag-gated `window.SR_COMBAT_POSES=true` or `?combatposes=1`)
- Data: `RIDER_COMBAT_MOVES` = light1, light2, finisher, heavy (provisional), react_light, react_heavy, knockdown. `RIDER_COMBAT_FEEL` rows: default, caali-g, anika (APPROVED (Oliver via Forge 14:39 CDT)), ikki (+ local-only rows not in this repo). `RIDER_HAND_POSES.open` added (not driven yet).
- W gains `atk`, `react` (overlay weights driven from the move clock: ramp in over A, 1 through X, ramp out over the last 50% of R). Mask `upper` skips Hips/legs (skating legs keep cycling); `full` drives everything.
- Slew: 720 deg/s for every bone except the move's lead limb (Shoulder/Arm/ForeArm/Hand or UpLeg/Leg/Foot) during X frames only = `RIDER_POSE_ACTIVE_DEG_S` 1800. plant() unchanged.
- `stateName()` keeps the locomotion name during planted moves (the v2-skate ground contact `srSkateGrounded` only accepts idle/stride/tuck/kick); `combatState()` returns 'atk'/'react'. Knockdown (plant off) reports 'react'.
- Changes vs §2: L1/L2 timings A6/X4/R12 hit f9 and A5/X4/R13 hit f8 (cancel f12); finisher A8/X6/R22 hit f12 with the rear skate drawn up under the hip (a toe-drag dipped the rear wheels under the deck and the contact solver lifted the support skate); react_heavy uses plant 'any' (lowest skate +-3 mm, other <= 10 mm).

## 9. Remaining open questions
**Rydah Systems** (original Q1-7 answered in §7; follow-ups from the G1 implementation:)
- F1. onRecover also fires with `interrupted:true` (plus `by`) when a chain step replaces the previous move, or a react interrupts an attack. Is that OK, or do you want a separate onInterrupt?
- F2. `stateName()` keeps returning the locomotion name during planted moves, because `srSkateGrounded` turns the v2 skate ground contact off for any other name. `combatState()` returns 'atk'/'react'. Keep this split?
- F3. wallatk `CHAIN.n` is 1-based (1/2/3); my `step` is 0-based as you specified. Call `setState('atk',{step:CHAIN.n-1})`.
- F4. Heavy: wallatk's K move today is a separate per-crew move (Chain Shock / Crow Rush ...), not a hold-J. Which drives `move:'heavy'`, and will K moves get their own poses (G2)?
- F5. Reacts on NPCs: only loadIkki riders (player, Ikki NPC) have this poser. Crew NPCs use loadRiderR128 (mixer rig), so setState('react') does not exist there. Port, or skip crew NPCs for now?
**Forge**
- 8. VFX hooks: `onHitFrame.pos` = lead hand/foot world position. Which fx key per move (bolt/wing/feather/fang)? Do you need wheel sockets?
- 9. Weapon: confirm none (fists + skates, canon). Anika ribbons = spring bones only, or a trail?
- 11. Super framing on Quest: approve "body spins, rig never rotates" + the vignette rule.

## §7b Forge answers (2026-10-30 14:33 CDT)
- FX attach points: empty Object3D children named srFX_handL/R (hand bones), srFX_footL/R (foot bones), srFX_wheelL/R (front wheel, v2 skate wheel socket / Wheel_F, so they follow the 1.25x skate scale). Applies to poser riders and the crew 19-bone path. No draws. The names go into the onHitFrame pos lookup and into combatQuery. Forge maps them in combat_fx.js. STATUS: queued (not implemented yet).
- No weapons. Anika's ribbons are springs only, with no trail.
- Quest: bodies spin and the camera never rotates. The dash vignette belongs to Systems/FX.
## §9 update
- Resolved: Forge 8–11 (above). Still open: F1–F5 for Systems. Crew knockdown uses a root drop (U.crDrop) so the lower foot stays on the deck. Crew react_heavy maps to react_light until a 19-bone heavy is authored.
- Crew K/L specials (set_K/set_L, 16 entries) are in ikki_skate.js but NOT signed off. 14/16 pass. The sweep template (static_K, genesis_K) slides the support foot 93–142 mm. Follow-up.
