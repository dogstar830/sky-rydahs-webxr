# Volt + Rust Claw garage exterior references (Palma Builder, 2026-11-05)

## Ruling
- Volt → district **The 98**, rival to Highway crew turf. Garage = **charging station** off the boulevard.
- Rust Claw → district **The Cove**, rival to Fisher crew turf. Garage = **salvage shed** in the marina blocks.
- Shared kit interior (crewhouse_kit.js): upstairs loft + downstairs A-T bay; per-crew colours/logo/sign only.
- Skate rule: inline skates only — no motorcycles, skateboards, or cars as props.

## Volt — modern EV charging station
Real-world cues (Gulf / modern plazas, stylised neon grade):
- Slender canopy with continuous LED/neon edge (Genesis Morphosis EVC, CST canopies).
- Charging bollards / pedestal posts under canopy (no vehicles).
- Small glass kiosk / attendant booth with branded neon.
- Roll-up garage bay integrated into the rear/side of the canopy plaza.
- Hot-dip galvanized steel frame, powder-coat dark; Volt neon `#ff2fa0` + accent `#ffe600` (graffiti.js fallback; **TODO**: crews.js colours from Rydah Systems).
- Stylised realism, neon grade — never cartoonish. Share materials; instance bollards.

Refs:
- https://alushel.fi/en/products/fueling-and-charging-canopies/ev-charging-canopy-cst/
- https://www.theplan.it/eng/award-2023-Special-Projects/genesis-electric-vehicle-charging-station-responding-to-a-changing-mobility-network-morphosis-architects
- https://evcharging.electricautonomy.ca/awards2022-the-circle/

## Rust Claw — corrugated-steel salvage shed
Real-world cues (Gulf Coast / Panama City FL marina yards):
- Corrugated galvanized / rusted panel dry-storage shed (Treasure Island Marina PCB dry barn, Pelican’s Perch Pensacola working yard).
- Stacked marina salvage: buoys, crates, hull plates, chain, crane hook (no boats as rideable props; plates/buoys/crates only).
- Chain-link yard fence, timber bull-rail feel, salt-weathered steel.
- Rust Claw neon `#ff6a1a` + dark `#8b3a1a` (graffiti.js fallback; **TODO**: crews.js).
- Logo: `shared/crew-logos/rust-claw.png` exists (pack into kit_logos slot 9).

Refs:
- https://www.marinadockage.com/treasure-island-marina-bounces-back-after-hurricane-michael/
- https://pelicansperchmarina.com/welcome-copy/
- https://reesemm.com/pensacola-fl/

## District boxes (merged map / handover palma.json dump, seed 1)
- THE COVE: `[-240,-100,-120,10]` (marina NW coast, MARINA sign ~[-180,4,-101])
- THE 98 · BILLBOARD MILE: `[170,-100,320,-50]` (boulevard ring east spine / rail z≈-55)

## Draw budget
Each exterior ≤ ~6 draws; world ≤ 110 (dcsplit2, desktop non-XR, post off, seed=1).

## Progress log (resume notes)

### 2026-11-05 ~09:54–10:41 CST — Palma Builder

**Lots (merged map):**
- Volt → The 98 `[288, -74]` face `S` — charging station off boulevard (rail z≈−55). Kick-clear.
- Rust Claw → The Cove marina blocks `[−165, −88]` face `S`. Kick-clear of Static `[−190,−30]`.

**Files changed (Palma-owned only):**
- `crewhouse_kit.js` — logo slot rustclaw:9; theme TODO fallbacks (crews.js missing Volt/Rust Claw); `kitExtVolt` / `kitExtRustClaw` (6 draws each, merge+IM); deferred `kitExtAll` until `BufferGeometryUtils` loads.
- `patch_crewhouse_kit.py` — injects both into `PALMA.garages` (anchor uses forest `dark:0xe8e8e0` pre–world_perf); GATE_CODES/HINTS volt:`9800` rustclaw:`1984`.
- `assets/kit/kit_logos.png` — slot 8 volt, slot 9 rust-claw.png (bak `.bak-garages-20261105.png`).

**Status:**
- build_copy → `/tmp/palma_garages.html` (symlink `v3build/palma_garages.html`). Real html md5 `5ad0f564…` unchanged.
- Gate tests PASS (volt 9800, rustclaw 1984, karasu 8686): unlock → interior kit → exterior hide (cam layer 5) → exit restore. 0 pageerrors.
- Draws (nofx seed=1): before causeway mean 90.7 / street 72.3; after causeway 96.7 / street 77.0; volt_lot 77; rustclaw_lot 81.7. All ≤110.
- Minimap: `icMarkers`/`turfEnsureRivalGarages` already register these coords; live `garages[]` now has real buildings (placeholders no longer needed for markers).

**Shots done:**
- `shots/hero/garage_volt_lot_before.png`, `garage_rustclaw_lot_before.png`
- `garage_volt_exterior_day.png`, `garage_volt_exterior_night.png`, `garage_volt_lot_after.png`

**Shots TODO:**
- rustclaw exterior day/night, rustclaw lot after, volt+rustclaw interior

**Board/handover TODO:** DEMO_STATUS ready line + check-in; push `handover/palma-builder/` on workshop-handover.

**Rust Claw status:** logo EXISTS (`shared/crew-logos/rust-claw.png`, packed slot 9). Colours NOT in `crews.js` — using graffiti.js fallbacks `#ff6a1a` / `#8b3a1a` marked TODO for Systems. Volt same (logo slot 8; colours fallback `#ff2fa0` / `#ffe600`).
