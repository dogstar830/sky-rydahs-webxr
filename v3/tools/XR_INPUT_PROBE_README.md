# XR Input Probe — founder procedure (about 2 minutes)

Standalone Quest 3S input map for Sky Rydahs menus. It does **not** load the game, and it does **not** read or write `skyrydahs-save-v1`.

File: `v3build/tools/xr_input_probe.html`  
Open it in **Meta Quest Browser** on the Quest 3S (same way you open a hosted page — Ani will give you a URL). Hard-refresh once (or clear this site’s data) so you are not on a cached copy.

## 2-minute run

1. **Pair the Xbox pad** in Quest Settings → Devices, if you will test it. Leave it on.
2. Open this page. In the 2D live readout, confirm the Xbox pad appears (press A if it does not show yet). You can also tap **Start 2D checklist (Xbox pad)** and run the Xbox steps before entering VR.
3. Tap the large **ENTER VR** button and put the headset on. A panel appears about 1.5 m in front of you.
4. Follow each prompt (`Press A on right Touch`, sticks, grips, then the Xbox face/bumpers/triggers/D-pad/L3/R3/View/Menu/Guide). Any **new** press or stick push advances. If nothing happens, wait for the countdown — that prompt is skipped and tagged as a timeout.
5. When it says **Press menu button**, press the **left Touch ☰**. The session may pause or exit. That is expected, and it is the result we need. If VR only pauses, resume and continue the remaining Xbox prompts. If VR exits, you are done with the headset part.
6. Back on the 2D page, review the **Summary (input → index)** table, tap **Download JSON**, and send that file to Anika / Systems.

A copy is also stored in this browser as localStorage key `sr_input_probe_v1`. Use **Reset log** only if you want to throw away a partial run and start over.

If **ENTER VR** fails, stay in 2D, finish the Xbox checklist, and send the JSON plus the error shown at the top of the page.

## What this will detect

- Every Touch / XR input source: handedness, `targetRayMode`, `profiles[]`, `gamepad.mapping`, button count, axis count, and each button’s `pressed` / `touched` / `value` plus each axis’s raw value.
- Whether the left Touch menu (☰) button is exposed to the page as a button or event, or instead blurs/ends the XR session (`session.visibilityState` and session `end`).
- `select` / `selectstart` / `selectend` / `squeeze*` and `inputsourceschange`.
- Whether a Bluetooth Xbox pad is visible to `navigator.getGamepads()` in 2D **and** while immersive, and that pad’s id, mapping, buttons, and axes.
- A tagged mapping of “this prompt → this index”, so the menu button map can be decided without guesswork.

## What this will not detect

- System UI itself. If Quest swallows a button before the page sees it, we only see the side effect (session hidden/ended, or a timeout with no input).
- Hardware failure vs OS remap — we log what the browser reports, not why.
- Haptics, hand-skeleton joints (we only note that a hand-tracking source appeared, if the optional feature is granted), eye tracking, or passthrough.
- The in-game input path. This page uses the same WebXR / Gamepad APIs the game will use, but it is not the game. After the menu layer is built, those bindings should be re-checked in-game.
- A real immersive session in the desktop self-test. Headless Chromium verifies load, 2D gamepad logging with a stub pad, summary/JSON/localStorage — not Touch hardware or the menu button.

## Hosting note

WebXR requires a secure origin (https or localhost). Do not rely on a `file://` open for the headset run. Systems will not publish this page; Ani hosts the copy the founder opens.
