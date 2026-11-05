## Palma final kick data (12:32 EDT 2026-10-29)
- KICK_ROUTES[0] = 3-kick alley wallkick_the98_13 <-> wallkick_the98_12 (4.0 m apart, facing), cable 9.45 m at x 298.5-302.5, z -98.15.
- Start [291,0.01,-98.15] heading +x, 7.5 m run-up, asphalt, no kerb/colliders.
- Key tests on face names / route runtime splineId (spline IDs shifted +7 by crewhouse_kit), never fixed numbers.
- 23 kick faces, 66 routes (64 facade, 2 alley), 14 added kick walls in 1 InstancedMesh (<=1 draw), zip line unreachable, bridge stays/mains not reachable.
- noKick: fillers, garages, gates, pylons, boundaries, crane/containers, beach stands, underpass piers, gantries, tower, precinct. Full list on board @10:48.
- Ani applied grind_airsnap.diff (apex lock 1.0-1.4 m under cable) - confirm feel in wallkick.py.
- M bug in boKickWalls already fixed 10:45 CT; real html (10:17) predates it. Wall-kick test needs a build after 10:45 CT.
