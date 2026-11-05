# PROPOSAL (not applied): Dash road downhill profile (Heights)
Author: Palma Builder, 2026-10-29 07:10 CDT. Status: proposal only; nothing in blockout.js, ground.js, or the grind rails is changed.

## Today (rendered)
- Note: the route length varies per reload (440–479 m) until the shipping seed lands; the table is from one load. Recompute it on the seeded layout before applying.
- Route: BLOCKOUT.dashPath, 360 points, 440.7 m, (203,-254) east/top to (-107,-250) west/bottom, 7.32 m wide.
- Road top 0.035 everywhere (flat). WORLD_GROUND reports 0.035 flat. Guard rails 387/388 (bo_dash_guard_L/R) are flat at y=0.79.

## Proposed profile
- East end raised to **+6.0 m**, falling to 0.035 at the west end. 24 m flat tie-ins at each end (start pad / run-out). Smoothstep easing between them, so there are no grade kinks.
- Average grade 1.53 %; **max grade 2.28 %** (mid-route). It reads as a downhill without the rider stalling on the flats.
- Formula: u=(s-24)/(L-48); y = 0.035 + 5.965·(1-(3u²-2u³)), clamped to the ends.

| s (m) | x | z | road top y | grade % (downhill +) |
|---|---|---|---|---|
| 0 | 203.0 | -254.0 | 6.0 | 0 |
| 40.0 | 181.4 | -286.8 | 5.971 | 0.36 |
| 80.2 | 167.2 | -260.2 | 5.668 | 1.12 |
| 119.7 | 133.1 | -258.0 | 5.109 | 1.68 |
| 158.6 | 105.0 | -284.1 | 4.378 | 2.05 |
| 198.7 | 70.7 | -295.2 | 3.509 | 2.25 |
| 239.8 | 53.5 | -267.6 | 2.576 | 2.26 |
| 280.0 | 15.5 | -260.0 | 1.699 | 2.07 |
| 319.6 | -8.6 | -283.4 | 0.949 | 1.7 |
| 360.3 | -44.2 | -283.7 | 0.369 | 1.12 |
| 399.9 | -70.5 | -255.9 | 0.067 | 0.37 |
| 440.7 | -107.0 | -250.0 | 0.035 | 0 |

## Matching changes if approved (must land together, in one patch)
1. **Road ribbon** (blockout.js dash()): each P[i] vertex gets y(s_i) + 0.035, plus a skirt down to ground (0.01) on both sides so the raised section reads as an embankment, not a floating slab. East start: a 6 m berm/terrace mesh (Heights grass) that the road leaves from, with a ramp from the ground street at about 8 % (75 m; 1:12, within ride_ground's 1:6 wall limit) or a stair/grind access.
2. **Rails 387/388** (bo_dash_guard_L/R): today Q=[x,.79,z]; becomes [x, y(s)+0.79, z] at the same x/z (decimated to about 60 points, as now). Splines are not moved in plan, only lifted; GRIND.S IDs are unchanged. grindGridBuild has to be re-run.
3. **ground.js**: the Dash capsules carry y(s) per segment (lerp along the segment) and the normal from the grade (ny = cos(atan(grade))). The self-test adds 3 sloped rows checked by raycast.
4. **Colliders / underpass**: the west end at (-107,-250) meets the underpass approach at ground level; no change there. Check that the TURF/graffiti spots along the route don't land under the embankment.
5. Gameplay JSON: the rail point y values change, so this is NOT byte-identical. It needs owner sign-off (Rydah Systems: ride_ground slope handling).

## Risks / open questions
- The rider lerps R.y to 0 today. Slopes need Systems' ride_ground to consume WORLD_GROUND normals first.
- An alternative with no embankment: dig the west end down (-3 m cut with retaining walls). It needs water/underpass clearance checks; not recommended.
