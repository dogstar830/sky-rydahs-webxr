# Building-base polish2 verification — 2026-11-05 20:46 EST

## Decision: READY FOR REBUILD

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
