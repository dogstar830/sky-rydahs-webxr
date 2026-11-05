# Testing Sky Rydahs on your Quest 3 (plain-language guide)

## 1. Open the game on the headset
- **Easiest: the GitHub Pages test link.** In the Quest Browser, open:
  `https://dogstar830.github.io/sky-rydahs-webxr/v3/?fps`
  It's HTTPS, so "Enter VR" works. It only has what has been pushed there. The local demo (with WITHHELD_CHAR) is never pushed.
- **The local build (the newest, with WITHHELD_CHAR):** the box isn't on your home Wi-Fi (its address is a private container IP), so your Quest can't open it directly. Instead:
  1. Download `/workspace/ship/sky-rydahs-v3-ikki-*.zip` to your PC and unzip it.
  2. On the PC, run `python -m http.server 8765` in that folder.
  3. Plug the Quest into the PC with USB and run `adb reverse tcp:8765 tcp:8765`.
  4. On the Quest, open `http://localhost:8765/sky-rydahs-v3-ikki.html?fps&chars=/skyrydahs-characters/`
  WebXR needs either `localhost` or HTTPS. A plain `http://192.168.x.x` address won't offer "Enter VR".

## 2. Show the numbers
- **In-game `?fps` overlay** (from `fps.js`): add `?fps` to the URL, or `&fps` if the URL already has a `?`.
  - It shows FPS (a 1-second average plus the minimum), frame time in ms, **draw calls** and **triangles** straight from `renderer.info`.
  - On desktop it sits in the bottom-right corner. In VR it's a small panel near the bottom-left of your view that updates 4 times a second.
  - It does **not** show texture memory.
- **OVR Metrics Tool** (free, from the Meta store): turn on its overlay to see FPS, GPU and CPU load, and the GPU level. It works over any app, including the browser.
- **USB remote debugging** (optional, gives the most detail):
  1. Turn on Developer Mode in the Meta Horizon phone app.
  2. Plug the Quest into the PC.
  3. In Chrome on the PC, open `chrome://inspect#devices` and click "inspect" next to the game tab.
  4. In the Console, `renderer.info.memory` shows the number of textures and geometries, and `FPSO.stat` shows the current fps, ms, calls and tris.

## 3. Two-minute checklist
Do one run in day and one at night if you can.
1. **Spawn:** note fps, min fps, ms, calls and tris after 10 seconds standing still.
2. **The causeway** (the wide view at the west end, where the "STORE" sign is): fps, ms, calls. Today's preview peak is 267 calls, and the Quest target is 150.
3. **Portside** (with NPC riders around): fps, ms, calls, and how many riders are visible.
4. **98 Bridge:** fps, ms, calls. The preview showed 243.
5. Skate fast for about 30 seconds and watch for drops below 72. Note where they happen.
6. Optionally, `renderer.info.memory` from remote debug, plus the OVR Metrics GPU %.
7. **Visual glitches:** floating or stretched body parts, skates detached from feet, missing or black textures, flicker, the blown-out white sign.

## 4. Where to put the results
Paste them into `/workspace/v3build/perf/quest-results.md`, or just send them to me in chat and I'll file them. One line per spot is enough:
`causeway day: 58 fps (min 41), 17.2 ms, 262 calls, 410k tris; glitch: none`
Phone screenshots of the overlay are fine too.
