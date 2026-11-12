# gamepad.js "rider moves with stick" failure — diagnosis (2026-10-28, CDT)

## Verdict: (a) headless slowness — NOT a gamepad.js bug. No pad.js/phone.js changes needed.

## Evidence
- Run as-is (copy on port 8792, `asis.log`): 32/33 pass. Only failure: `rider moves with stick`, displacement 0.0987 in 1 s wall (threshold > 0.1).
- The checks right before it pass: `LS up = forward` (Input.yaw≈0, Input.mag>0.95), deadzone/rescale exact (0.4318). So the stick reaches Input correctly.
- `animate()` uses `dt=Math.min(.05,(t-lastTime)/1000)`, so each frame is capped at 50 ms of game time.
- Headless SwiftShader frame rate (`diag.py`, `diag_*.json`): **0.3 to 3.3 fps** (box load average was 65 to 78). In 4 to 10 s of wall time there were 2 to 26 frames, which is 0.1 to 0.36 s of game time. One wall second is about 0.05 to 0.15 s of game time, so ~0.1 units is what you'd expect.
- Keyboard W, same run and same setup: 0.193 units in 10.4 s wall (3 frames), 1.28 units per game-second. Pad: 0.147 units in 6 s (3 frames), 0.98 units per game-second, and 0.758 units / 2.1 units per game-second over 26 frames. Pad and keyboard move about the same per frame. The keyboard path is not meaningfully faster.
- Input.mag = 1 for the whole run and speed keeps building (0 → 2.8 and rising toward maxSpeed 24). pad.js doesn't zero the input. After the patch, pad.js `padGet`/`padNoPad` go through `SR_PAD.active()`/`withMuted`, and the legacy poll reads `SR_PAD.stick`.
- Chromium flags (`--disable-background-timer-throttling --disable-renderer-backgrounding --disable-backgrounding-occluded-windows --disable-gpu-vsync --disable-frame-rate-limit`) made no material difference (0.3 to 3.3 fps vs 0.5 to 0.7). The limit is the SwiftShader software render cost, not rAF throttling.
- With a frame-count-based check (`test_fix.patch`): PASS, d=4.005 units after 20 frames (35.9 s wall).

## Proposed fix (not applied): `test_fix.patch` (tests/gamepad.py only)
Instead of `time.sleep(1)`, wait for at least 20 frames and more than 0.5 units of displacement, capped at 90 s wall. Also assert `Ride.speed>0`.

## Caveat
In the single run with the patched test, 9 later checks in the faked-XR and keyboard sections failed. That included the page error `Cannot read properties of null (reading 'updateRenderState')` from the test's fake XR session/isPresenting shim. All of them passed in the as-is run. That run had load average 65 or more, and the rider ended up 4 units further away. The likely cause is the XR stub racing the very slow render loop, but this was not confirmed. Rerun on a quieter box before landing the patch.

Files: diag.py (instrumented copy, rAF timestamps), diag_swiftshader.json, diag_flags.json, asis.log, fixed.log, test_asis.py / test_fixed_8792.py (port 8792 copies).

## Update 2026-10-28 23:29 CDT: test fix landed in tests/ (NOT yet run: the box never went quiet)
- Backup: tests/gamepad.py.bak-202610282253
- Applied test_fix.patch (frame-count based "rider moves with stick").
- Root cause of the fake-XR race: in three r128, `WebXRManager.getCamera()` calls `session.updateRenderState(...)` on its private `session` (null when XR is faked) the first time near/far differ from the cache (the cache starts at null). Game code calls `renderer.xr.getCamera(camera)` outside render whenever `isPresenting` is true: minimap MM2 on a 1/hz timer (line ~3215), map (~2891), wallFX (~2354). At very low fps the clamped-dt minimap timer sometimes fires inside the fake-XR window. Then the throw breaks every frame after it, which explains the 9 later failures. This is a test-stub artifact, not a game bug: in a real XR session the private session is set.
- Stub fix (tests/gamepad.py only): while faking, `renderer.xr.getCamera` becomes the identity function (restored with getSession/render/isPresenting). The fake `__ses` also gets no-op `updateRenderState`/`renderState`/`add/removeEventListener`/`requestAnimationFrame`/`cancelAnimationFrame`/`end`. It parses OK.
- Not run: polled from 22:53 to 23:28 CDT (quiet.log). Load stayed 31 to 52 the whole time, with 35 to 49 headless-browser/test processes from other agents (graffiti.py, phone.py, attacks.py, grind.py) and available memory as low as 1.1 GB. The fix is unverified.
