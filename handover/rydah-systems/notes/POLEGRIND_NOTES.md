# Pole-grind look (Oliver ref3, 2026-10-30) - Rydah Systems queue, after wallkick/anubis reds
Ref: /workspace/skyrydahs-ref/characters/caali-anika-2026-10-30/caali-anika-ref3-pole-grind.jpg
- Vertical pole grind already exists (grind.js grindPole -> vert spline, kind pole/lamp).
- FX: double-helix light ribbon spiralling up the pole around the rider (warm orange/white core, violet + electric-blue fringe), sparks at skate wheels, small floating debris chunks.
- Feel: rider climbs the pole in a spiral (orbit around pole axis while rising), skates on the pole surface; at top, pop onto crossarm / cable (chain into cable grind) or launch.
- Budget: FX in one pooled ribbon mesh (1 draw, additive), reuse particle pool; draw delta <=1. VR: no camera roll.
- Night FX ref: ref1-night-fx.jpg.

## Queue from Ani (2026-10-30 01:3x CDT), after reds + attack lock-commit
1. grind.js full-screen 'vortex focus' quad: only while grinding (not just >7 m/s); cap/disable in XR (fill per eye on Quest). grind.js owner = Ani's grind worker -> diff if needed.
2. Pole-grind helix per Optimizer spec /workspace/v3build/perf/anika-fx-budget.md: static double-helix mesh, vertex-shader scroll, ~1.5 turns, 1 draw. Drive fade-in/loop/fade-out from Rigger's polegrind state: rider.userData.setState('polegrind',{variant:'top'|'climb',poleAxis,side}); entry 0.30 s, hold loop 1.6 s, exit 0.25 s. Root placement / orientation along poleAxis / pole snap / exit physics = mine.
3. One pooled additive ring-buffer ribbon for all wheel trails + turf_dash.js dash ribbons (1 draw; NPCs within 12 m only). I own turf_dash.js.
Also Optimizer: 22 extra textures, composer/bloom targets dispose on XR start - Optimizer asking Ani who owns setupFX (not mine yet).
