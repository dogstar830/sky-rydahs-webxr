# Rider style opt3: perf gate plan (run AFTER Forge posts "ready for rebuild")
Rydah Optimizer, 2026-10-30 23:45 CDT. Not run yet. Results will be **desktop headless Chromium, Quest-like `?tier=quest`, no real headset**.

## Run
```
bash /workspace/v3build/build_copy.sh /tmp/opt-rstyle.html        # only allowed build
for s in $(python3 - <<'P'
import re;h=open('/tmp/opt-rstyle.html').read()
for i,m in enumerate(re.findall(r'<script(?![^>]*src)[^>]*>(.*?)</script>',h,re.S)): open(f'/tmp/rs_inline_{i}.js','w').write(m); print(f'/tmp/rs_inline_{i}.js')
P
); do node --check $s || echo "FAIL $s"; done
python3 /workspace/v3build/perf/render-style/rider_style_opt3_gate.py /tmp/opt-rstyle.html
```
The script takes `/workspace/v3build/.testlock` with O_EXCL and exits 9 if the lock is held. It launches one Chromium, serves v3build on a free port with a temporary `_rstyle_gate.html` copy (removed afterwards), and always releases the lock. No pkill, no test suites.

## Variants (both with pbr on, the default; `pbr=1` is passed explicitly)
- base: `?tier=quest&pbr=1`
- opt3: `?tier=quest&pbr=1&riderstyle=opt3`

## Measured (60 warm-up frames + FRAMES=240 timed)
`renderer.info.render.calls`, triangles, `renderer.info.programs.length`, `info.memory.textures`, estimated texture MB (scene material textures, RGBA8 or 1 B/px compressed, ×1.33 mips), and `DC_PROBE.run` (perf/drawcalls/dc_probe.js) rows. Frame ms are the median and p95 of rAF deltas. Output goes to `perf/render-style/gate-results.json`.

## Pass criteria
| check | limit |
|---|---|
| draws | opt3 − base ≤ **+0** |
| programs | ≤ **+2** |
| frame ms (median) | ≤ base × **1.05** |
| texture memory | ≤ **+2 MB** |
| page errors | no new ones |

Headless frame ms is a relative signal only. A real Quest 3 72 fps check is still owed.
