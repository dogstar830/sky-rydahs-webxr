# Step 4.2 texture free wins: PROPOSALS (Rydah Optimizer, 2026-10-29). All MB are STATIC ESTIMATES, no headset or browser used, no tests run.
Before: ~295 MB static at spawn (audit.md), Quest budget 256 MB.
| change | owner | files | GPU MB saved | projected after |
|---|---|---|---|---|
| A shared crew atlas | Rydah Forge + Rydah Rigger | A_tex_share.proposed.diff, A_tex_share.md | ~2.0 | ~293 |
| B Caali G normal strip | Rydah Forge + Rydah Rigger | caali-g.nonormal.glb (chars/wardrobe/riders), B_caali_nonormal.proposed.diff, B_caali_nonormal.md, B_caali_accessor_check.txt | 0 GPU (~21 MB transient CPU + one 2K decode) | ~293 |
| C sign originals | **Palma Builder (implementing in world_perf.js now; not in this folder)** | - | ~30-40 per audit, Palma's estimate governs | ~255-263 if Palma's lands |
Note: the "~50 MB" for step 2 was mostly the sign originals. A+B alone are about 2 MB GPU.
WITHHELD_CHAR is untouched (A skips WITHHELD_CHAR URLs and images above 512²). Nothing owned by another bot was edited. Patched JS copies: /tmp/s2/*.patched.js.
Step 3 (KTX2 loader) is queued for the integrator: /workspace/v3build/patch_draco.py.ktx2-candidate behind ?ktx2=1.
