# Rooftop (L heaven) tag spots — reachability (Palma, Nov 12; static read + 1 runtime probe on /tmp/palma_cw.html, read-only)
Rule (graffiti.js grafFind, Systems): d <= 6.1 m, FRONT side (dot(p-spot, n) > -0.2), |p.y - roof| < 2.5.
WORLD_GROUND (ground.js) has NO roof surfaces; the only roof-height standing is a grapple deck (grapple.js, deck bounds = building footprint, +0.2 m tolerance).
So on a deck the legal band is the 0.2 m strip at the roof edge; otherwise only airborne in front of the face (what Systems saw).

| spot | district | roof y | grapple deck on that roof | ledge in front | wall-kick/panel within 8 m | verdict |
|---|---|---|---|---|---|---|
| g13 | The 98 · Billboard Mile (259.9,-69.4) n -z | 9.78 | BILLBOARD DECK y9.8 | none | none | edge-strip only (0.2 m) |
| g19 | The Cove (-149.5,-27.1) n +z | 9.04 | ROOFTOP y9.1 | none | none | edge-strip only |
| g29 | The Strip (225.9,137.5) n -z | 6.25 | ROOFTOP y6.3 | none | none | edge-strip only |
| g2  | East Blocks (180,55.9) n -z | 11.89 | none | none | none | **NO approach** (airborne only; 11.9 m > kick reach 11) |
| g11 | Portside Terminal (4.7,141.7) n +z | 14.66 | none | none | none | **NO approach** |
| g35 | The Yard (-76.7,-51.8) n +x | 10.46 | none | none | none | **NO approach** |

## Smallest Palma-side fix (NOT applied — new geometry in finish mode, needs Ani's OK)
1. Billboard maintenance catwalk in front of each heaven face (all 6): 1.0 m deep x 9 m steel grate at roof height, outside the face
   (dot 0.1..1.1 m), toe rail. Standable through ground.js (Palma) as an elevated surface keyed by yHint >= roof-1.5; rendered as ONE city-wide
   InstancedMesh (blockout.js, +1 draw max, frustum bounds per group). Makes g13/g19/g29 taggable standing (skate off the existing deck onto the catwalk).
2. Access for g2/g35 (no deck): a blockout kick alley (blockout.js kickwall pair, already one InstancedMesh -> +0 draws) next to the building
   up to the catwalk (g35 10.5 m within BO_KICK.reach 11; g2 11.9 m needs the catwalk at roof-1.0 = 10.9 m, still within dy<2.5).
3. g11 (14.7 m) is out of kick reach: needs a grapple point on its catwalk -> grapple.js (Systems) adds one entry; or Systems moves the spot to a 5.5-11 m face.
Colliders/WALL_KICKS change (+2 kick faces per alley) -> invariants and kick tests must be re-baselined; that is why this needs Ani's OK.
