# Graffiti progress (Rydah Systems) - 2026-10-29 00:15 CDT
Stopped: Grok Bot usage ran out mid-run.
Done on disk: graffiti.js (44.5KB), patch_graffiti.py (in build_ikki.sh line 13, before patch_phone),
tests/graffiti.py, shots/graffiti_{small_midreveal,large_heaven_complete,surface_brick,surface_metal,surface_glass,surface_asphalt,night_glow,day_noglow,turf_flip}.png
Remaining: clean build_ikki.sh run, run tests/graffiti.py + all tests/*.py on :8765, verify peak draw calls < 300,
rebuild /workspace/ship/sky-rydahs-v3-ikki.zip (Python zipfile), report to Ani.
No PR: Ani opens one combined unmerged PR for v3/index.html.
- 00:30 clean build OK (patch_graffiti idempotent). graffiti.py run1 27/30: fixed test bugs (subscribe fn auto-invoked by evaluate; B-cancel spot pick). Peak calls 232.
- 00:40 rebuilt w/ softer night glow; graffiti.py 29/30 (RS camera check flaky: yaw decay) -> test fix
- 00:45 zip rebuilt from clean build; running all tests/*.py into /tmp/post
- 01:00 fix: zero PAD.R.rs in grafTick during tagging (RS->camera leak); rebuilt
- 01:25 build 01:19 (has RS fix) confirmed; rerunning all tests/*.py -> /tmp/post2
- 01:40 graffiti.py RS check sampled camera after tag end (stick still held); now samples only during gesture phase
- 02:05 box D-Bus crash at 01:59 killed browsers mid-run; failures around then to be rerun
- 02:16 step1: rerun graffiti.py vs 02:01 build (single browser, xargs loop stopped)
- 02:24 step1 done: graffiti.py 30/30, peak calls 231, no console errors. step2: rerun grind gates flprobe7 jackets minimap_v2_test ikki* sequentially
- 02:26 step3: zip rebuilt from 02:01 build (10712104 bytes, same layout: html + README + skyrydahs-characters GLBs)
- 02:52 step2 partial: grind PASS, gates PASS (were D-Bus kills), flprobe7 timeout 900s (probe script, no asserts)
- 04:31 demo fixes: graffiti.js X/legacy-spray fix, rebuild 04:16; awaiting integrator phone.py + wallride.py runs (lock rule)
