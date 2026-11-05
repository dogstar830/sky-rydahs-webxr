# World draw-call reduction plan (Rydah Optimizer, 2026-10-29 04:50 CDT, read-only analysis)
Metric: `renderer.info.render.calls`, desktop non-XR, fixed camera, post off. Cap 150 = world <=110 + characters/FX <=40.
Now: 267 at causeway west (day), 243 at 98 Bridge (was 180 at 23:xx). No game file was edited for this. /tmp/dc_bisect/results/ did not exist at 04:45, so these figures are **static estimates**. Confirm them with dc_probe.js (see the bottom of this file).

## 0. Headline finding (check this first)
- **`patch_world_perf.py` + `world_perf.js` (new, 04:38/04:41, owner unknown, probably Palma Builder or Rydah Systems) are NOT in `build_ikki.sh`**, and the 04:28 build contains 0 `WORLD_PERF`. That pass already does 4 of the wins below: base interiors culled within 45 m, asphalt merged per material, batcher tiles re-merged 90 m -> 270 m, and signs packed into a canvas atlas. Its author should say whether it is ready. Then the integrator adds `python3 patch_world_perf.py` after patch_quant_fix (anchor `// ===== LOOP =====`) and measures with `?noperf` vs. without. **Estimated saving: 40-70 calls at both cameras.** Do this before starting anything else.
- Camera: `far=600`, `Fog(0x1a1036, 70, 360)`. Everything from 360 m to 600 m is drawn fully fogged, which costs draws and shows nothing. The causeway west camera (~(-100,-240)) sees across the water to Portside and the Heights, and from 98 Bridge (~(220,-170)) the whole east side is open. That open sightline across the water is why these two cameras are the peaks.
- No shadow maps (0 castShadow/shadowMap in the build), so item (g) costs 0 today. Keep it that way on Quest.

## 1. Static inventory (from source; module -> what it adds)
| module | creates | already batched? | ink hulls | est. draws, causeway W / 98 Br |
|---|---|---|---|---|
| world.js (box/glow/ink + 5 InstancedMesh detail kinds per 90 m tile, each with an InstancedMesh hull culled at 50 m) | ~31 Mesh sites in loops, garages, signs | staticMerge per 90 m tile x material (VC materials collapse to vertex colour) | ink() = 1 child hull per mesh; merged into ink tiles (DETM r95) | 55-75 / 50-65 (tiles x materials x visible tiles, plus far-culled sign planes up to 170 m) |
| details.js | 2 InstancedMesh per chunk + 1 LineSegments (wires) + 1 Mesh, ~55 det() kinds | instanced per 90 m chunk; DETM r95-110 | 1 hull InstancedMesh per chunk (r50) | 20-30 / 20-28 |
| place.js | traffic lights, crosswalks, poles (det/box in district loops, 55% of cells), 1 LineSegments | via staticMerge / det | ink() on box | 8-15 / 12-18 (the98 district is next to 98 Bridge) |
| kits.js + facades.js | 3 InstancedMesh (one shared facade shader, CC0 atlas) | yes, instanced city-wide, frustumCulled default | 1 instanced hull | 4-6 / 4-6 |
| bridges.js | 1 InstancedMesh per kind per bridge (box/glow/cyl x 3 bridges) | instanced | no | 6-9 / 6-9 (all 3 bridges are often in view from either camera) |
| asphalt.js | 1 MeshStandard plane per district (~6-8) | no (world_perf merges them) | no | 6-8 / 6-8 |
| bases.js | 2 baked meshes per base x 8 + glow boxes | box/glow merge; 1 noMerge | via box | 4-10 / 2-6 (world_perf culls them at 45 m) |
| gates.js | 8 garages x (static box/glow + 2 baked moving meshes + 1 logo decal CanvasTexture) | static parts merged, moving parts 2 + 1 noMerge each | some | 6-12 / 3-8 |
| graffiti.js | 3 InstancedMesh + 1 Points, 4 frustumCulled=false | yes | no | 7 fixed (measured) |
| turf_dash.js | 1 InstancedMesh + 1 Mesh, 2 frustumCulled=false + per-spot tag planes | partly | no | 3-8 / 3-8 |
| grind.js | 1 InstancedMesh, 3 Mesh, Points, 3 frustumCulled=false (sparks/trail hidden until used) | partly | no | 3-6 / 3-6 (cables + tubes, mostly near bridges) |
| wallatk.js | wall panels + FX, 1 frustumCulled=false, noMerge | no | no | 2-6 / 1-4 |
| target.js, map.js, minimap_v2 | reticle meshes (hidden), MAP mesh (hidden unless View is open), 2D canvas | n/a | no | 0-2 |
| polish.js | sky/stars Points, 1 Sprite, glow textures; no per-object hulls (ink is in world.js `ink()`, and polish only changes the hull shader) | n/a | n/a | 2-4 |
| sky.js | 0 new (measured) | | | 0 |
| sign planes (FARCULL, one unique canvas texture each) | ~20-40 in the city | cannot batch without an atlas | no | 15-30 / 10-20 (the big causeway "STORE" sign is one of them) |
| **world total (est.)** | | | ink hull draws ~25-35% of world | **~150-200 / ~135-175** |
Characters/FX make up the rest (8 NPC riders + player, ~27-37 per lod-budgets.md). Since 23:xx the likely additions are graffiti 7, gates + bases (8 garages, ~10-20 including the hulls of unmerged parts and logo decals), turf tag planes, and grind cables. The bisect results should confirm or correct this.

## 2. Ranked contributors (estimate)
1. world.js static-merge tiles at 90 m x many toon colour materials, each with an ink hull tile: ~60-75.
2. Unique-texture sign/poster/tag planes (FARCULL up to 170 m): ~15-30.
3. details.js chunks + hull chunks: ~20-30.
4. Anything 360-600 m away (fully fogged): ~15-25 at these two open-water cameras.
5. gates/bases/turf (post-23:xx additions; moving parts and decals are noMerge): ~15-25.
6. Bridges + asphalt + kits: ~16-23 (already lean; asphalt can merge).

## 3. Reduction plan, ordered by calls saved per effort
| # | item | est. calls saved (cw W / 98) | owner | visual risk | effort |
|---|---|---|---|---|---|
| 1 | Wire `patch_world_perf.py` into build_ikki.sh (asphalt merge, 270 m tile re-merge, sign atlas, interior cull) | 40-70 / 35-60 | world_perf author -> integrator wires it | low (near signs swap back to full res within 28 m) | XS |
| 2 | (f) Quest tier: `camera.far=fog.far+20` (380), plus a distance cull of whole 270 m tiles beyond fog.far | 15-25 / 15-25 | Palma Builder (world.js init), tier flag in a new tier.js | none (fully fogged) | XS |
| 3 | (c) Ink hull tiles: draw hulls only within 60 m (now 95 m for merged ink, 50 m for instanced). Optionally merge the hull geometry into the same tile mesh as a second group (still 1 draw each, so no gain). Quest: hulls within 40 m | 10-20 / 8-15 | Palma Builder (merge.js / world.js DETM radii) | low-med (distant silhouettes lose ink; ink is already distance-scaled) | XS |
| 4 | (d) Collapse toon colour variants to vertex colour: make mergeKey always use the VC path for flat-colour toon/glow, so 1 toon + 1 glow material per tile instead of N colours | 15-30 / 12-25 | Palma Builder (world.js mergeKey/vcMat) | low (same shader, colour in attribute) | S |
| 5 | (a) Re-run staticMerge after late-built modules (gates, bases, turf, grind cables) or call a `staticMerge.late()` after their init, so their static parts join tiles | 6-12 / 4-8 | Palma Builder (merge); Rydah Systems for turf/wallatk static panels | low | S |
| 6 | (e) Sign atlas for the remaining planes: gate logo decals, turf tag planes, wallatk panels into the world_perf atlas (needs a whitelist so runtime-painted tags stay live) | 5-12 / 4-8 | Rydah Systems (graffiti/turf/wallatk) + world_perf author | low | M |
| 7 | (b) Repeated place.js props (traffic lights, poles, crosswalk) to InstancedMesh with instanceColor, per 270 m tile | 4-8 / 6-10 | Palma Builder (place.js) | none | M |
| 8 | Bridges: merge the per-kind InstancedMeshes of each bridge into 1 static merged mesh per material (they never move) | 3-5 / 3-5 | Palma Builder (bridges.js) | none | S |
| 9 | (h) Duplicate patches: patch scripts assert anchor count==1, and no duplicate module markers were found in the built HTML (each `// =====` section appears once). Check `?probe` output for identical module rows | 0 expected | integrator | - | XS |
| 10 | (g) Shadows: none today. Rule: no castShadow on the Quest tier; bake into vertex colour/lightmap instead (see realism-at-72fps.md) | 0 (guard) | all | - | - |
Expected after 1-5: about 150-200 -> **~85-110 (causeway W)** and **~80-100 (98 Br)**. Items 6-8 are the margin for realism work.

## 4. Quest tier toggle design (new `tier.js`, Palma Builder + integrator; no desktop look change)
```js
const TIER=(()=>{ const q=new URLSearchParams(location.search).get('tier');
  const ua=/OculusBrowser|Quest/i.test(navigator.userAgent);
  const t={ name: q|| (ua?'quest':'desktop'), listeners:[] };
  t.set=n=>{ if(t.name===n) return; t.name=n; t.listeners.forEach(f=>f(n)); };
  t.on=f=>{ t.listeners.push(f); f(t.name); };
  return t; })();
// auto: renderer.xr.addEventListener('sessionstart',()=>TIER.set('quest'));
//       sessionend -> TIER.set(paramOrUA || 'desktop')
```
`?tier=desktop` forces desktop, even on a Quest. Each owner subscribes with `TIER.on(n=>...)`:
| knob | desktop | quest |
|---|---|---|
| camera.far / fog | 600 / 70-360 | 380 / 60-330 (same colour) |
| tile cull radius (270 m tiles) | none | > fog.far + tile radius -> visible=false |
| ink hull radius (DETM) | 95 / 50 | 40 / 30 |
| details.js chunk radius | 110 | 70 |
| FARCULL sign radii 55/95/170 | same | 40/70/120 |
| sparks Points / speed lines / trail | on | trail on, sparks halved |
| shadows / post | none | none |
| pixel ratio / foveation | dpr | `renderer.xr.setFoveation(1)`, framebufferScale 1.0 |
On desktop (default) every value stays as it is now, so the look does not change. The cost cuts come from items 1-8.

## 5. dc_probe: integrator instructions (QUEUED; needs the .testlock)
1. Hold `/workspace/v3build/.testlock`, serve as usual, and open `http://localhost:8765/v3build/sky-rydahs-v3-ikki.html?chars=/skyrydahs-characters/&nofx`, desktop, non-XR, post off.
2. Wait >= 6 s, until `window.__merge` is set (staticMerge 1.5 s + 2.5 s).
3. In the console, paste `perf/drawcalls/dc_probe.js` (or inject it with a script tag at `/v3build/perf/drawcalls/dc_probe.js`).
4. Causeway west: use the same pose as `shots/demo_check_bridge_causeway_day.png` (`demo_check.py` scene `bridge_causeway`, day). Freeze the camera, then run `DC_PROBE.run('causeway_west_day')`.
5. 98 Bridge: use the `demo_check.py` 98 Bridge pose, then run `DC_PROBE.run('b98_day')`.
6. Repeat both with `&noperf` once world_perf is wired.
7. Save `DC_PROBE.json()` output to `perf/drawcalls/probe_<label>.json` and post the 2 totals and the top 10 modules on DEMO_STATUS.md.
The probe's `estDraws` should be within a few of `renderer_calls`. The difference is sky/background and multi-material groups.
