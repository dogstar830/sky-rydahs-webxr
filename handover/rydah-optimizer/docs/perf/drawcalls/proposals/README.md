# Draw-call proposals for Rydah Systems (Rydah Optimizer, 2026-10-29 05:14 CDT). PROPOSALS ONLY: no game file was edited.
Each diff applies with `cd /workspace/v3build && patch -p1 < <diff>`. Each is independent of the other. Both passed `patch --dry-run` and `node --check` on patched copies in /tmp/dcchk.

## What the data says
The bisect groups at the causeway (build 18, ~222) plus Palma's world_perf table put Rydah Systems' files at **14 calls**: graffiti 6, grind 4, grapple 3, turf_dash 1. All of them are already instanced. Graffiti tags already come from ONE procedural canvas atlas (`grafAtlas`, 4 surface shaders); turf tags are 1 InstancedMesh; wallatk FX is 1 pooled mesh, hidden when empty; and target.js meshes are hidden unless LT is held. A shared decal atlas or a re-merge pass in these files has very little left to collapse: the ~109 single unlit meshes are in world.js (Palma). So the diffs below are small, targeted cuts. I did not write a generic atlas-packer or re-merge module, because it would have nothing to merge in these files, and it would only add risk.
- Gate logo/keypad face (gates.js `GATE.face`) is one runtime-redrawn canvas per active gate. It is interactive, so keep it live. gates.js is not on the Systems ownership line, and world_perf already handles the gates' static parts (batcher tiles).
- Grapple: the ring material pulses its colour every frame (grapple.js:59), and the beam is transparent. Neither can merge without changing the look, so there is no diff for grapple.
- The Palma world-unlit-instancing diff was dropped (superseded: Palma is doing unlit instancing + ?seed in world_perf pass 2). It was never written.

## Apply order (calls saved per effort)
| # | diff | calls saved (causeway day / night) | risk | verify |
|---|---|---|---|---|
| 1 | `systems-graffiti-dayglow.proposed.diff`: hide `graffiti_glow` when uNight<=0.003, because its shader discards every fragment by day. One line next to the uNight update. Base: sha1 21bdea72, mtime 04:16:51 CDT; rebase onto the heat.js change | -1 / 0 | very low (the glow already fades with uNight; at dusk it turns back on when uNight > 0.003) | graffiti.py (tag paints, night glow on), phone.py spray items, `?nobatch=1` A/B, drawcall_budget.py --compare (day causeway -1) |
| 2 | `systems-grind-poleatlas.proposed.diff`: wood + galv grind poles become one InstancedMesh with a 2-cell runtime canvas atlas (same procedural canvases); per-instance `aPole` picks the half, V repeat, colour, roughness and metalness | -1 / -1 (whenever poles are in view; both cameras) | low-med: possible faint mip seam at the atlas middle on distant poles; shader-chunk replace on r128 MeshStandard (map/roughness/metalness chunks) | grind.py (pole grinds still lock; GRIND.S/rails untouched), wallride.py + attacks.py (no regressions), `?nobatch=1` A/B screenshot of the poles, drawcall_budget.py --compare |
Total: -2 by day at the causeway, -1 at night. Systems' share goes from 14 to 12 calls. The remaining world gap is Palma's world_perf pass 2.

Fallback: `?nobatch=1` restores the old path in both diffs.
