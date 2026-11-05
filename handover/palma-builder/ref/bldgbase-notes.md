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
