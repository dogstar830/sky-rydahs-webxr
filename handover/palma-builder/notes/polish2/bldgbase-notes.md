# Building ground-floor band (Palma Builder) — progress log
Task (Oliver via Ani, 10/30 20:11): PBR building bases 0-5 m: brick/poured concrete per kit, steel I-beam columns + lintels, framed storefront windows (env reflection, lit interiors at night), kick plate/plinth, grime + AO. ?toon=1 unchanged.

- 2026-10-30 20:12 CDT: backups facades.js / patch_facades.py / pbr_world.js / DEMO_STATUS.md *.bak-bldgbase-20261030201[1-2]*. Board "started" posted.
- 20:12: atlas page B built by pbr_base_atlas.py -> assets/pbr_base/pbrB_{albedo 2048 ETC1S q192, nrm 1024 UASTC, orm 1024 ETC1S q192}.ktx2 + jpg. Sources CC0 ambientCG (Bricks105, Concrete034, PaintedMetal004, MetalPlates008), see assets/pbr_base/SOURCES.txt. Quest est. 4.9 MB.
- 20:15-20:25: shader in pbr_world.js only (facade convert(): vertex vFace = along-face metres + face width; fragment block before 'emi*=mix(1.,.25,uDay); float aa='). Shader-only, 0 new meshes. facades.js / patch_facades.py NOT changed (not needed). First build had a #define swallowing a uniform line -> fixed. Compiles, 0 warnings.
- Copies (build_copy.sh only): bo_bldgbase.html (after), bo_bldgbase_base.html (baseline: same sources, pre-change pbr_world.js via SR_SRC=/tmp/palma_src). Real html md5 d6403ad93baf6b6d62ac731957f69c1c unchanged.
- 20:46: team .testlock rule adopted; all browser work serialized by /tmp/bb_all.sh (shots after, shots before, invariants, dcsplit2 default/toon, tests graffiti/wallride/wallkick base vs after).
- 21:19: after shots done: shots/hero/bldgbase_{street,close}_{day,night}_after.png (day confirmed: FACADE.uniforms.uDay=1, SKY.day=1; harness uses global FACADE, not window.FACADE).
- 21:32: before shots done (same views, baseline copy).
- 21:40: invariants run 1 (default only, script bug skipped toon/quest): 0 errors/404/shader errors base+after; WALL_KICKS, colliders (888), noKick (410), tag spots (9) hashes IDENTICAL; WALL_PANELS count same (27) but hash differs -> queued inv2 (/tmp/bb_inv2.py) to dump WALL_PANELS twice on base (determinism) + toon/quest errors.
- 21:50: STOP order (AI#4): pbr_world.js restored to 20:11 ready version (= .bak-bldgbase-20261030201214; verified byte-identical to the block in ready copy bo_pbr_def2.html). Bases WIP moved to pbr_base_wip.js (full variant), pbr_base_wip_inject.py, pbr_base_wip.glsl — not in any chain. facades.js/patch_facades.py were never edited (md5 = backups). Killed my bb_all queue (dcsplit2 default done: causeway world 91/94/96).
- 22:18: AI#4-safe check PASSED, board posted.
- 22:35: restructured: pbr_base.js (layer: waits for pbr_world's converted facade material, adds pbrB uniforms + vFace varying + base-band GLSL; own pbrB loader) + patch_pbr_base.py (inserts after PBR_WORLD, before LOOP). NOT in build_ikki.sh. Test method: build_copy.sh -> copy = baseline (bo_bldgbase_base.html); then `python3 patch_pbr_base.py /tmp/palma_bb2.html` on the /tmp copy -> bo_bldgbase.html (build_copy.sh has no extra-patch hook; it only runs build_ikki.sh's chain).
- 22:35: look fixes folded in before measuring (so all checks run on the final WIP): day ambient/env lift on base band, smooth interior card (soft shelves, low-contrast stock), concrete fascia + inset sign panel (keeps neon) instead of the corrugated band, concrete cap, stronger brick/mortar contrast, blue-grey beams, stronger day glass reflection. pbr_base_wip.* kept as the older reference.
- 22:57: (1) RESOLVED: WALL_PANELS fingerprint differs between two loads of the SAME baseline (fbb032 vs d7fe9f); entries hold three.js meshes whose JSON carries random UUIDs. Not a gameplay change. (Counts 27 / kicks / colliders 888 / noKick 410 / tags 9 identical earlier.) (2) base x2, WIP default, WIP toon: 0 errors/404/shader errors; PBR_BASE on=1 facade patched, toon: PBR_BASE off.
- 22:55: step (1)(2) done -> /tmp/bb_inv2.log (shader errors: 0)
- 23:05: step (3) draws done -> shots/dc2_bldgbase2_{default,toon}.json
- 23:06: (3) draws dcsplit2 seed 1, 3 runs, world min/mean/max: WIP default causeway 91/93.7/95, street 76/76.7/78; WIP ?toon=1 causeway 90/92.7/94, street 70/72.3/77. All <=110. (2) quest: 0 errors/404/shader; PBR_BASE loaded all 3 pbrB KTX2.
- 23:16: Ani approved chain slot. pbr_base.js made OPT-IN (?pbrbase=1); backup pbr_base.js.bak-optin-*. Running chain (tests, shots) uses the pre-gate copy bo_bldgbase.html = same code as ?pbrbase=1.
- 23:17: build_ikki.sh backed up (build_ikki.sh.bak-pbrbase-*) and patch_pbr_base.py added right after patch_pbr_world (not run). build_copy -> bo_bldgbase3.html: 'patch_pbr_base ok', PBR_BASE present. NOTE real html md5 changed to 03d50b55... before my build (someone's real rebuild, not mine); unchanged across my build. Queued bb_all4 (errors on chain copy) after bb_all3.
- 23:18: step (4) graffiti on bo_bldgbase_base.html: 30 PASS / 0 FAIL; 
- 23:34: step (4) graffiti on bo_bldgbase.html: 30 PASS / 0 FAIL; lock released for Rydah Rigger (courtesy)
- 23:48: step (4) wallride on bo_bldgbase_base.html: 13 PASS / 0 FAIL; RESULT 13 / 13
- 00:15: step (4) wallride on bo_bldgbase.html: 13 PASS / 0 FAIL; RESULT 13 / 13
- 00:27: step (4) wallkick on bo_bldgbase_base.html: 20 PASS / 0 FAIL; . Lock released; courtesy for Rigger run3 pid 1641690.
- 10:33: step (4) wallkick on bo_bldgbase.html: 0 PASS / 0 FAIL; 
- 10:44: chain copy bo_bldgbase3.html: default: err 0 404 0 shader 0 base False; &pbrbase=1: err 0 404 0 shader 0 base True; &toon=1: err 0 404 0 shader 0 base False; &tier=quest: err 0 404 0 shader 0 base False; &tier=quest&ktx2=1&pbrbase=1: err 0 404 0 shader 0 base True
- 09:15: after shots: Traceback (most recent call last):   File "/workspace/v3build/bldgbase_shots.py", line 25, in <module>     pg.evaluate("garages.forEach(g=>g.gate&&(g.gate.dismissed=true));if(typeof GATE!='undefined'){GATE.uiOpen=false;gateUI()};window.__npcPassive=true;window.__npcFreeze=true"); pg.evaluate(HOOK)  
- 09:22: step (6) hero shots done

## 2026-11-05 — finish-mode close-out (opt-in shippable)

- Goal: ship as `?pbrbase=1` (default only after Ani look + Oliver before/after). Chain: `patch_pbr_base.py` after `patch_pbr_world.py` (already in build_ikki.sh).
- Contrast/scale pass on `pbr_base.js` (bak `pbr_base.js.bak-contrast-20261105-*`): bay width `P0.x*1.6→2.05`; masonry `qsc` brick `1.4→.95` / concrete `2.6→1.7`; columns `qcw .21→.30`; lintel `.34→.42`; plinth `qPl .38→.48`; frames `fw .075→.11`; brick stretch `1.25→1.75`; steel flange/web contrast up; day glass `+.28→+.45 uDay`; night interior emi `1.1→1.35`; normals `1.2→1.65`; stronger AO/grime/spec. Target: band reads at 15–40 m, stylised realism.
- Next: build_copy `/tmp/palma_base.html`, wait .testlock (Systems/other Palma), shoot `bldgbase_final_*` street/close day+night baseline vs pbrbase=1 SBS, dcsplit2 draws ≤110, spawn/wallkick/colliders/0 errors.

### 11:34 CST — distance-AA fix + lock freeze
- Root cause of "too subtle at street distance": facades fragment does `o=mix(col, avg=wall*.7+..., aa)` where `aa` rises with fwidth. Base band set `wall` to flat masonry, so at 15–40 m beams/windows in `col` were AA-washed away. Fix: `wall=mix(masonry, col, .92)` (bak `pbr_base.js.bak-distAA-*`).
- Contrast/scale pass kept (thicker columns/frames, larger brick modules, stronger mortar/glass/grime).
- Copy rebuilt `/tmp/palma_base.html`; real html md5 unchanged `5ad0f564…`.
- LOCK RULE (urgent): before writing `.testlock`, read pid + `kill -0`; never overwrite a live pid; atomic O_EXCL only; unlink only if claim holds our pid. Shared helper `/tmp/palma_testlock.py`. Browser freeze until **12:03 CST** (Rigger ~25 min slot). No Chromium from Palma until then.
- Queue ready: `/tmp/palma_base_queue.sh` (freeze→verify shots→dcsplit2 nofx seed=1 baseline+pbrbase→gameplay invariants). Lock via `/tmp/palma_testlock.py`.
- 12:03–12:18+ CST: freeze lifted; correctly waiting on live lock holder pid 1985743 (`bash /tmp/rs_shots.sh` → `rider_style_opt3_shots.py`, chromium active). Claimed max 45 min from 11:33 but still running — we do NOT overwrite.

### 12:23 CST — resume after interrupt
- State OK: contrast+distance-AA in `pbr_base.js` (md5 `1d49f28a…`) and `/tmp/palma_base.html` (built 11:34); real html `5ad0f564…` unchanged; `pbr_world.js` untouched (`d35c25d1…`).
- No dead own lock to clear. Queue pid 1987813 still waiting correctly on live holder 1985743 (`rs_shots.sh` / opt3 hero, ~50 min, over claimed 45 — still alive, do not overwrite).
- Pending: hero `bldgbase_final_*` shots + SBS, dcsplit2 nofx, gameplay invariants, DEMO_STATUS ready, handover push.
- 12:31 CST: Forge released; Rigger took lock (`anika springs+combat run9`, pid 1987007, max 30 min from 12:29). Our queue correctly re-read lock and waits on live Rigger — no overwrite, no browser.
- 12:51 CST: old queue (1h wait from 12:03) near timeout while Forge holds another opt3-close slot (pid 2040307, max 30 min from 12:45). Stopped waiting queue (never held lock). Restarted `/tmp/palma_base_queue2.sh` with 2h wait + 10s poll; still kill -0 / O_EXCL / own-pid release only.
- 13:05 CST: still waiting on Forge opt3-close (pid 2040307); shots progressing (caali close day/night before/after landed). Queue2 healthy. No browser from us.
- 13:13 CST: resume — queue2 pid 2044808 still sole waiter; Forge extended lock to 13:22 for anika after. No second queue. Watching log only.
- 13:16 CST: Forge released; queue2 entered shots+verify; Rigger immediately took lock (run10, pid 2044257, max 40 min). verify take_lock correctly waiting — no overwrite.
- 13:22–13:30 CST: Rigger → Ani AI4b_smoke suite (pid 2039166, runq: smoke/grind/atk/wallride/gamepad). Queue2 verify still waiting correctly on live Ani pid.
- 13:34 Rigger run10 again; 13:37 **other Palma** took lock (`ani garage dcsplit+hero+rivals`, pid 2010810, max 30 min). Queue2 yields (same bot family, let waiters/holders finish). Still no second queue from us.
- 13:58 CST: LOCK acquired by queue2 verify (pid 2060005). Shots starting. No second queue.
- 14:04 CST: resume — verify 2060005 holds lock, first shot `bldgbase_final_street_night_before.png` landed. Watching only; no duplicate queue. Will release promptly for garage Volt re-shoot waiters.

### 14:35 CST — queue2 complete (opt-in shippable)
- Verify ok: PBR_BASE on, facade patched=1, warn=[], 0 page/shader errors. SBS written.
- Hero finals: `shots/hero/bldgbase_final_{street,close}_{day,night}_{before,after}.png` + `{street_day,street_night,close_day}_side_by_side.png`.
- Look: street day after — skyscraper base shows concrete + dark steel frames/windows at 15–40 m (distance-AA wall←col fix working). Close day — textured masonry, speckled I-beams, storefront glass. Night — lit interiors. Before flats vs after structured. No further shader iterate needed.
- dcsplit2 nofx seed=1 (3 runs): **pbrbase** street world 75/75.7/77, causeway 101/101/101; **baseline** street 75/78/82, causeway 101/101/101. All ≤110; ~0 added draws (shader-only).
- Gameplay invariants: colliders 973, WALL_KICKS 26, WALL_PANELS 17, tags 9, noKick 808 identical base vs pbrbase; 0 pageerrors; grind world true.
- Real html md5 unchanged `5ad0f564…`. `pbr_world.js` untouched. Lock released promptly (Rigger took next).
- Chain: `python3 patch_pbr_base.py` after `patch_pbr_world.py`. Opt-in `?pbrbase=1` until Ani look + Oliver before/after.
- 14:37 CST: DEMO_STATUS ready (opt-in) + check-in posted. Handover pushed **afe79fb**. Lock left free for garage Volt re-shoot waiters / Rigger.

## 2026-11-05 14:57 CST — Oliver ruled DEFAULT ON (via Ani)

- Ruling: building bases (`pbrbase`) are the DEFAULT; `?pbrbase=0` to opt out. Window-interior / night-glow polish NOT in this pass.
- Backups: `pbr_base.js.bak-default-20261105-145819`, `patch_pbr_base.py.bak-default-*`, `build_ikki.sh.bak-default-*`.
- Flip: `pbr_base.js` gate now `!PBR_WORLD.on || /[?&]pbrbase=0/` → early return; otherwise `S.on=true`. `?pbrbase=1` kept as force-on/no-op. Matches `pbr_world` default-on pattern.
- `patch_pbr_base.py` + `build_ikki.sh` comments updated (DEFAULT ON). Chain line unchanged: `python3 patch_pbr_base.py` immediately after `patch_pbr_world.py`. Did NOT run `build_ikki.sh`.
- Test copy: `bash build_copy.sh /tmp/palma_base_default.html` → `patch_pbr_base ok`. Real html md5 still `5ad0f564…`.
- Gate runner `/tmp/palma_base_default_run.sh` queued: lets Volt canopy waiter go first, then flag/error/invariant gate + dcsplit2 nofx seed=1 (street/causeway ≤110).

### 16:08 CST — DEFAULT ON gates PASS
- Ready for rebuild: building bases DEFAULT ON; ?pbrbase=0 opt-out; chain `python3 patch_pbr_base.py` immediately after patch_pbr_world.py.
- Gate `/tmp/palma_base_default_gate.json`: default ON (facade=1, warn=[]); pbrbase=0 OFF; pbrbase=1 ON; toon=1 PBR/bases OFF; every case 0 pageerrors / 0 shader errors.
- dcsplit2 `/workspace/v3build/shots/dc2_bldgbase_defon.json`: desktop non-XR, post off (`nofx`), seed=1, 3 runs. World min/mean/max: street 75/77.3/80, causeway 98/100/101. All ≤110; errors=[].
- Default vs opt-out counts unchanged: colliders 973, WALL_KICKS 26, WALL_PANELS 17, tags 9. Supplemental harness COLL ReferenceError prevented spawn/noKick follow-up; this is not an application pageerror. Fresh spawn not claimed.
- Runner completed 16:05:56 CST; own locks released. Real HTML md5 `5ad0f5646468f5fef7d25f9153144e8e` unchanged. Never ran build_ikki.sh. No window-interior/night-glow polish.
- DEMO_STATUS Goals + check-in posted. Handover push needed from parent: see `/tmp/palma_base_default_handover_msg.txt`; no new commit SHA from this executor.

### 2026-11-05 16:14 CST — finish polish implemented, VISUAL/RENDER GATES PENDING
- Backup: pbr_base.js.bak-polish-20261105-161329. Procedural shelf/product edges now derivative-filtered and discrete (stock silhouettes, shelf lips, label strips), replacing soft sine-card stock. Day interior lift .38→.48.
- Night: broad warm lit-bay fill, bounded ceiling fixture strip, stronger interior emission (1.35→2.4); unlit bays remain dark. Shader-only, no new meshes/materials/draw submissions; default-on gate unchanged.
- build_copy.sh /tmp/palma_base_polish.html succeeded, patch_pbr_base ok; node --check passed. Real HTML md5 5ad0f5646468f5fef7d25f9153144e8e unchanged.
- No browser-capable subagent/tool is exposed in this executor. Browser skill forbids Shell Playwright automation; therefore no renderer/shader-error, draw, gameplay or visual pass is claimed. No .testlock touched.
- NOT ready for real rebuild until parent runs fresh gates and views shots. Previous default-on draw result is NOT evidence for this polish.
- Package /workspace/palma_ho_push_polish/ contains code, built copy, build log and adapted shot harness for an authorized test runner; no push.

## 2026-11-05 20:08 EST — fresh verification complete; visual hold

 NOT READY — visual hold

Runtime, flag, draw-budget, and count-invariant gates pass. Do not promote this polish as visually approved.

- Default PBR_BASE.on=true, facade=1, warn=[]; ?pbrbase=0=false; ?pbrbase=1=true; ?toon=1 disables PBR and bases.
- All four gate cases: 0 pageerrors and 0 shader errors; hero baseline/after error arrays are empty.
- dcsplit2 desktop non-XR, nofx (post off), seed=1, RUNS=3 world min/mean/max:
  - street 75 / 76.7 / 80
  - causeway 98 / 99 / 101
  - b98 92 / 93.3 / 96
  - aerial 93 / 93.3 / 94
  - errors=[]; every maximum <=110.
- Gameplay counts match default vs opt-out: colliders 973, WALL_KICKS 26, WALL_PANELS 17, tags 9. Hero gameplay capture independently confirms these counts; baseline GRIND.world=true. No new physical movement/spawn-height test is claimed (riderY=null). Older gate's optional noKick expression throws a harness-only COLL ReferenceError after the required counts; not an application pageerror.

## Images actually reviewed

All 10 PNGs under shots/hero/bldgbase_polish_* were opened using Read, plus a native-resolution interior crop and the previous bldgbase_final_close_day_after.png for visual context.

Hero settings: 1920x1080 viewport, device scale factor 1.5 (2880x1620 PNGs), tier=hd, FX on, seed=1; every hero logged 67+ stabilized frames. Day switching uses typeof-guarded FACADE.setDay/BRIDGES.setDay. Night close restores the original night fog/background/hemisphere lighting after day.

- PASS: street-night before/after and side-by-side clearly show brighter storefront windows at street distance.
- HOLD: close-day stock/shelf edges remain visibly soft at native resolution; the selected close-day view does not convincingly demonstrate sharper interiors than the previous hero. This is a visual observation, not a diagnosed shader root cause.
- HOLD: close-night lit storefront clips nearly white, concealing interior detail; glow strength is evident, but the sharp-lit-interior goal is not met in this hero.
- The generic close camera is partly occluded by the HALO sign/tree. A clearer storefront hero could help assess the existing code; no source changes were made by this verification runner.

## Lock / integrity

Prior holders and waiters were yielded to. Optimizer exited; the first own waiter was then stopped and observed exited before a single clean replacement was started (no duplicate). The remaining old waiter had failed to claim free gaps for over an hour; replacement allowed a 120-second free-lock grace interval before O_EXCL acquisition. No live lock or other worker was killed or overwritten. Replacement pid2250895 acquired its own lock and removed only its exact pid claim in finally; verified exited and own lock absent.

Real sky-rydahs-v3-ikki.html MD5 remains 5ad0f5646468f5fef7d25f9153144e8e. Only test copy /tmp/palma_base_polish.html was rendered. No real rebuild, commit, push, or outside message was sent.

Required next step: address/accept the visual holds and re-review before publishing a ready-for-rebuild line. Technical gate PASS must not be relabeled full visual approval.

## 2026-11-05 20:46 EST — polish2 visual fixes verified; READY FOR REBUILD

 READY FOR REBUILD

Supersedes the polish1 visual hold. Shader-only edits to pbr_base.js; no new meshes/materials/draw submissions or gameplay edits. Local workspace has no Git checkout.

## Implementation

- Backup before edit: pbr_base.js.bak-polish2-20261105-200845-EST.
- Night raw light/fixture peaks reduced; max-channel rational shoulder scales RGB together (.72/(.72+peak)) to retain hue. Final interior emission multiplier 2.4 -> .85. Keeps restrained warm storefront light rather than a white neon rectangle.
- High-contrast product bodies, cream label bands, dark shelf lips, narrower derivative-filtered edges at close range; shelf geometry painted procedurally on back AND side walls. Close glass reflection mix reduced to let detail read. Soft environment reflections remain intentional glass reflections, not the shelf edges.
- pbr_base.js MD5 e0675587bd31a39d122c18a420481338. Default-on flags/chain unchanged.
- node --check PASS; build_copy.sh /tmp/palma_base_polish2.html PASS. Never invoked real build_ikki.sh directly.

## Fresh gates

- Default PBR_BASE.on=true, facade=1, warn=[]; ?pbrbase=0=false; force-on=true; toon=1 PBR/bases=false.
- Four runtime cases and hero baseline/after: 0 pageerrors / 0 shader errors.
- dcsplit2 desktop non-XR, nofx (post off), seed=1, RUNS=3 world min/mean/max:
  - street 80 / 80.7 / 82
  - causeway 98 / 100 / 101
  - b98 92 / 93.3 / 96
  - aerial 93 / 94 / 95
  - errors=[]; every maximum <=110. Draw variation from the prior measurement is not new shader draw submissions.
- Default/opt-out counts identical: colliders 973, WALL_KICKS 26, WALL_PANELS 17, tags 9. GRIND.world=true; sampled riderY=.01, spawn [0,16] in runtime gate (not a new movement test). Optional noKick is unavailable/null; no claim for it. Harness-only undefined COLL guard corrected for this rerun.

## Visual review PASS

Opened all 10 shots/hero/bldgbase_polish2_*.png with Read, plus native close-day detail.

- Street-night before/after/SBS: restrained orange/warm lit bays clearly distinguish the after from baseline at street distance.
- Close-day: individual product bodies/labels and dark horizontal shelf edges visibly resolved; strong improvement over polish1's soft interior cards.
- Close-night: warm ceiling/walls, orange/blue stock and shelf lines remain visible; lit pane no longer clips white. Unlit bays remain dark.
- Matching lit-pane native crop [1810,760,2180,1000]: polish1 had 100% pixels with red or green >=254 and max RGB [255,255,249]; polish2 has 0% and max RGB [193,165,156]. This checks the sampled pane, not every emissive surface in the city.
- Hero standard: 1920x1080 viewport, dsf=1.5 (2880x1620 output), tier=hd, FX=true, seed=1, 67+ stabilized frames per shot. typeof-guarded FACADE.setDay/BRIDGES.setDay; original night atmosphere restored for night close. Existing HALO/tree partial occlusion retained for matched camera comparison; clear right-hand pane shows detail.

## Lock / integrity / handoff

Single runner pid2287106. Read/kill-0 holder check, 120-second free-lock grace for earlier waiters, atomic O_EXCL take, exact-pid-only release. Runner exited 0; own lock confirmed absent. No other worker/lock removed.

Real sky-rydahs-v3-ikki.html MD5 remains 5ad0f5646468f5fef7d25f9153144e8e. Only /tmp/palma_base_polish2.html built/rendered. DEMO_STATUS ready line posted after image review; notes backed up first. Package refreshed; no commit, push, external message, or real HTML rebuild.
