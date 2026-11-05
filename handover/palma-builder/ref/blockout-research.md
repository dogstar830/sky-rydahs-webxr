# Blockout dimensions (realism step 1) — sources
Tags: [S] sourced, [GAME] measured from the build's movement code, [OURS] design choice (not a real-world fact).

## Movement numbers used for sizing [GAME] (bo_scratch.html / ikki_skate, read only)
- Ground is flat: R.y lerps to 0 unless grinding; no roof/ramp heights exist. Walkable = onLand() (islands +4 m, bridge decks, new land).
- maxSpeed 24 m/s, accel 7, drag .45. Jump launch vy 5.6 (flip 7.6, 6.4 kick), gravity 13 m/s2 -> apex 1.2 m (2.2 m flip), air ~0.86 s,
  so a full-speed gap ~20 m, typical 12-15 m. Wall ride: minSpeed 8.5, height cap 6.5 m, 2.2 s (4.5 s held). Rider radius 0.4 m.
- Colliders are 2D AABBs; above y 7 the air code skips them.

## Sources
- 40 ft ISO 1AA container 12.192 x 2.438 x 2.591 m. [S] ISO 668:2020 (https://www.iso.org/standard/76912.html); Hapag-Lloyd container spec PDF.
- STS crane, Tampa (Ports America/ZPMC 2016): gauge 100 ft = 30.48 m, outreach 53.04 m, lift 39.62 m. [S] https://www.nidec-conversion.com/wp-content/uploads/2023/07/DEP2017.05.26EN.01.US_.Case-Study_PortsAmerica_AC_STS_Cranes-1.pdf
- STS typical: 18.0 m clearance between legs, 14/17 m clearance under portal beam, backreach 20-25 m. [S] Konecranes STS spec https://www.konecranes.com/sites/default/files/2021-07/STS_crane_typical_technical_spec.pdf
- Front Beach Road (PCB) plan: 10 ft travel lanes, 8-10 ft south sidewalks, >=12 ft north, beach-access boardwalks >= 6 ft. [S] https://pcbdaily.com/wp-content/uploads/2007/09/desnmanu.pdf
- FDOT urban lane 11 ft; sidewalk 10-12 ft in urban centre/core. [S] FDOT FDM 222 (2026) and PPM vol.1 ch.2.
- Sand albedo #EDE8DC. [S, in-repo] beach-sky-palms-research.md §1.
- W-beam guardrail: MGS top of rail 31 in (0.79 m), posts every 6 ft 3 in (1.905 m). Commonly published FHWA/MwRSF values; verify before final art.

## Applied
| Area | Placement | Key dims | Basis |
|---|---|---|---|
| Strip beach boulevard + boardwalk | x168-322, z198-242 (new land south of the Strip) | 4 lanes x 3.05 m = 12.2 m; 3.05 m sidewalk; 4 m timber boardwalk; 1.07 m handrail; 3 beach-access gaps | [S] Front Beach Road; rail height [OURS] |
| Causeway rails + underpass | parapet top rails at +-4.35 m, y 1.15 (world.js geometry); 48 x 12 m deck, soffit 5.6 m, 16 m inland of the north abutment | soffit [OURS] |
| Port quay + container maze + STS | apron x-330..-238, z22-198; crane rails x-326 / -295.5; legs z 100.2/119.8 | gauge 30.48, outreach 53.04, backreach 20, portal 14, boom 42 m; 136 containers, 4 m aisles, stacks 1-3 | [S] Tampa/Konecranes/ISO; aisle [OURS] (> rider 0.8 m and wall-ride approach) |
| Portside landmark tower | auto-placed free lot (seed=1: 54,134) | 24 m footprint, 114 m + spire 134 m | [OURS] sightline anchor |
| Heights Dash road | A* route from 98 bridge head to causeway head, serpentine waypoints | 7.32 m (2 x 12 ft), 439 m long (seed=1), guardrail 0.79 m | lanes [S] FDOT; flat (no ground height) |
| Boulevard ring | painted spine West (Portside) + East (East Blocks/Drive), 4 RING gantries 6.5 m | 693 m painted (seed=1) | [OURS] |
| G-Men precinct | auto-placed in The Drive (seed=1: 276,-9) | 30 x 18 x 12.6 m (3 x 4 m storeys), 30 x 12 m impound lot, 6 m gate | [OURS] |
