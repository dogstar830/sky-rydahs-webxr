# causeway_west world draws 114/110 on real 4d4d9558 — Palma Builder analysis + plan (Phase 1, static only)
Written 08:30 CST Nov 12 during QUIET WINDOW (no Chromium, no .testlock). Nothing edited yet; real html untouched.

## Ownership
world_perf.js / patch_world_perf.py = Palma Builder (DEMO_STATUS l.512/626/628: created 04:44-04:57 CDT Oct 29 by Palma; header has no other owner).
Optimizer's steering confirms. crewhouse_kit.js, facades.js, bridges.js, pbr_world.js, pbr_base.js also Palma. heat.js / tests/drawcall_budget.py / dc_meter.js are NOT Palma.

## Camera
tests/drawcall_budget.py CAMS `causeway_west_{night,day}` = demo_check BR('causeway') = SAME pose as dcsplit2 V 'causeway'.
Bridge causeway a[85,-100] b[-100,-240] -> cam (39.5, 9, -309) looking at (-7.5, 6, -170); rider pinned (109, 0, -82). FOV 65, far 600, fog 70..360.

## What changed since Nov 10 (98-103)
1. Palma's last causeway number: dcsplit2 on /tmp/palma_kogfix.html (Nov 10 00:01 CST) = world 101/101/101. world_perf.js == .bak-pm2-1041 (byte-identical); crewhouse_kit.js = kogfix version. No Palma world file changed after that (Nov 11 22:05 mtimes = box restore).
2. Chain diff rebuild_nov10_1111_2115.log -> rebuild_l1brake_1112_0125.log: NEW = patch_tickguard_keep, patch_visible_error, patch_vr_body (SR_VRBODY1), patch_layer1, patch_brake. None adds a desktop world mesh (vr_body only hides/shows Ride.group children in XR; brake.js has no THREE meshes; visible_error = DOM HUD). Other chain steps unchanged/same order.
3. **The 114 is a different metric/pose, not (only) a regression.** drawcall_budget.py was first run ever on 4d4d9558 (perf/drawcalls/results has one file, 07:18:55). It differs from dcsplit2:
   - pins all 8 NPCs (7 crew + Ikki NPC) in a fan 8-20 m in front of the camera (dcsplit2: none in view);
   - world = renderer.info.calls − ESTIMATED chars − ESTIMATED fx (frustum traversal, holder-rooted). Anything NPC-related that is not under a holder, or any estimate miss, lands in "world". (est 158 vs real 144 shows the estimate is off by 14 at this cam.)
   - NO seed=1 (layout of cans/details/pools is Math.random), max over 30 frames, ?player=ikki.
   - Board history with "renderer − chars − FX": causeway ≈113 (l.855-858), 109.3 (l.879), 111/114.4/118 (l.929) — the same ~114 band. Per-draw dcsplit2 has always read lower (98-101).
   So expect most of the +13 to be: NPC-fan side draws classified world + unseeded layout + estimator subtraction. Needs Phase 2 attribution to confirm.

## Merge / instance candidates in that view (static read)
| # | what | where / why in view | draws now | cut | owner |
|---|------|------|------|------|------|
| A | Rust Claw kit exterior (kit_ext_rc_panels/steel/crates/plates/buoys/neon), added by kitExtAll at kitInit -> after staticMerge, all userData.noMerge, MeshStandard (world_perf singles() skips Standard) | garage (-165,-88), ~300 m, ~24° off view axis -> inside frustum (far 600) but 79% fogged | 6 | far-LOD: beyond 150 m swap to ONE pre-merged vertex-colour mesh (panels+steel+crates+plates+buoys) + neon stays = 2 (−4). Near/hero unchanged. | Palma crewhouse_kit.js |
| B | Volt kit exterior | (288,-74), ~65° off axis -> likely OUT of frustum | ~6 | same LOD (0 here, helps b98/aerial) | Palma |
| C | Sleeping Forest garage group (40,-275), 34 m in front of cam: unmerged children (CHECKPOINT/DRESS signs, emblems, glow pads/ring, clubhouse windows) | board l.858 "crew garage group @40,-275: 5" | ~5 | world_perf late pass: merge static no-map glow planes/cylinders per colour (3 clubhouse windows -> 1, cp+dp pads -> 1) −2..3; bobbing CHECKPOINT sign stays | Palma world_perf.js |
| D | heat_cops: 3 InstancedMesh (body/cone/bar), frustumCulled=false | in every view when cops active | 3 | one IM w/ instanceColor or merged cop geometry −2; or hide when count 0 | NOT Palma (heat.js) -> proposal only |
| E | gate harness: add &seed=1, report world from per-draw attribution (renderBufferDirect wrap, like dcsplit2) instead of calls−estimate | — | — | metric fix, no game change | NOT Palma (Optimizer/Systems) -> proposal only |
Goal: ≤105 on the gate metric. A+C give −6..7 from Palma files; D −2; that reaches ~105-106 on the current reading. If Phase 2 shows NPC-fan side draws classified world (e.g. per-NPC extras outside holder), that is the real lever and belongs to the rider/meter owner.

## Phase 2 plan (only after 'QUIET WINDOW END')
1. `bash build_copy.sh /tmp/palma_cw.html` of the CURRENT chain (baseline, no edits). Under .testlock (kill -0, atomic, own-pid unlink, waiters first). Headless Chromium via Shell only.
2. Baseline on /tmp/palma_cw.html: (a) dcsplit2 RUNS=3 seed=1 causeway/street/b98/aerial; (b) dcsplit2 + same 8-NPC fan pin as the gate; (c) drawcall_budget.py --url-path /tmp copy with and without &seed=1. Dump per-draw object paths at causeway_west (top-level group + name + material) to attribute every world draw.
3. Apply A (crewhouse_kit.js, backup .bak-cw-<ts>) and C (world_perf.js, backup .bak-cw-<ts>) only if their draws show up in step 2; rebuild copy; re-measure; gates: 0 page/shader errors, colliders 1003 / WALL_KICKS 26 / WALL_PANELS 17 unchanged, before/after causeway_west day+night shots identical to the eye (RC garage at 300 m fogged).
4. Ready line on DEMO_STATUS (backup first) with measured causeway_west (both metrics) + chain line (unchanged: patch_crewhouse_kit after patch_quant_fix, patch_world_perf after it).
Note: live Palma sources are deliberately NOT edited in Phase 1 — Ani's next build_ikki.sh would pick them up unverified.
