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

### 2026-11-05 11:03 CST — initial place DONE (pre Ani review)
- All hero shots on disk (10 files).
- DEMO_STATUS Goals + ready check-in + Systems open item for crews.js colours.
- Handover pushed: commit **15d9f28** (`workshop-handover` → `handover/palma-builder/`).
- Real html md5 still `5ad0f5646468f5fef7d25f9153144e8e`.


### 2026-11-05 11:03–~12:30 CST — Ani review fixes (in progress)

**Ani asked (3):**
1. Volt exterior cam on canopy roof → move to gate height in front of canopy; clearance ≥3.5 m + collision check.
2. Empty black emblem discs on Volt + Rust Claw (kit_logos slots 8/9); keep Kogarasumaru emblem.
3. Rust Claw day: MARINA background reads mirrored (ANIRAM).

**Causes + fixes (code landed, copy build `/tmp/palma_garages.html`):**
1. **Cam:** hero harness used `clz=12, cy=5.5` — sat on/behind canopy deck (local z≈5.2, y≈3.55). Shot script now `clz=10, cy=2.3` (gate height, in front of canopy). **Clearance:** canopy underside was 3.46 m (`y=3.55`, th `.18`); raised deck to `y=3.85` → underside **3.76 m**. Posts lengthened to match. No canopy footprint AABB (2D colliders would block the under-pass); kiosk+bollards still collide; thin deck has no ground height so it is non-walkable.
2. **Emblems:** `emblemTex()` in baked `world.js` has no `volt`/`rustclaw` branches → disc+ring only. `kitFixEmblems()` in `crewhouse_kit.js` paints slots 8/9 from `kit_logos.png`, replaces exterior planes at y=10, and detaches them from `world_perf` SIGN atlas (which had baked the empty disc). Karasu/others untouched. Retries at +3.5 s after atlas.
3. **MARINA:** `putSign("MARINA",…,Math.PI)` in baked base HTML (from old `patch4.py` layout; **not** in `world_perf`/`facades`/`blockout`). `+Z`=south; `ry=PI` faced north → Cove street (looking north from Rust Claw) saw DoubleSide back = mirrored. `patch_crewhouse_kit.py` now rewrites to `ry=0` (face south).

**Files:** `crewhouse_kit.js`, `patch_crewhouse_kit.py`, `garage_hero_shots.py` (harness). Backups `*.bak-ani-fix-20261105-110732`. Lock helper: `palma_testlock.sh` (never overwrite live pid).

**Tests so far (under lock; then browser pause for Rigger/Forge):**
- Gate tests **PASS** volt/rustclaw/karasu (unlock → interior → exterior hide camMask 32 → exit restore); **0 pageerrors**. `/tmp/garage_gate_test.json`.
- Real html md5 still `5ad0f5646468f5fef7d25f9153144e8e`.
- Hero re-shoot + dcsplit2 **pending** (no browser until ~12:03 CST per Ani steering after lock clash; Forge holds `.testlock` at 11:33). Old heroes saved as `shots/hero/garage_{volt,rustclaw}_*_{exterior_day,exterior_night,interior}_v1.png`.

**Next:** acquire lock via `palma_testlock.sh`, RUNS=3 dcsplit2 (`≤110`), re-shoot 6 heroes (overwrite, keep v1), view shots, update DEMO_STATUS ready line, push `handover/palma-builder/`.

**CREW_RIVALS (Systems 11:58):** kitTheme now `(CREWS.find(...)||CREW_RIVALS.find(...))`; hard volt/rustclaw overrides + TODO removed. patch injects `const CREW_RIVALS` from crews.js into the copy. Expected: Volt c1=0xffe600 / c2=0xff2d95; Rust Claw c1=0xff7a1a / c2=0x8a3416. Exterior kitExt neon uses kitTheme. PALMA.garages color → #ff2d95 / #ff7a1a. Karasu locked. DEMO_STATUS Systems open item closed.

### 2026-11-05 12:48 CST — resume after interrupt
- Code + `/tmp/palma_garages.html` verified intact: CREW_RIVALS inject, kitTheme lookup, canopy 3.76 m, kitFixEmblems, MARINA ry=0, hero cam clz=10/cy=2.3. Real md5 `5ad0f564` unchanged. Gate PASS on disk. Heroes still pre-fix (v1=current). dcsplit/hero re-shoot pending lock.
- `.testlock` held by Forge pid 2040307 (alive) — waiting; will acquire via `palma_testlock.sh` (kill -0, noclobber).

### 2026-11-05 13:25 CST — still queued on .testlock
- Waiter (tl_acquire) correctly yielded: Forge extended to 13:22, then Ani AI4b_smoke suite took lock at 13:21 (pid 2039166, alive). No overwrite. Code/copy unchanged; remaining: theme runtime check, dcsplit≤110, hero re-shoot, view, DEMO_STATUS ready, handover push.

## Ani review fixes + CREW_RIVALS — DONE 2026-11-05 13:58 CST

### Causes / fixes
1. **Volt exterior camera / canopy**
   - Cause: hero cam sat on/behind canopy roof (`clz=12 cy=5.5`); canopy deck underside was ~3.46 m.
   - Fix: `garage_hero_shots.py` Volt exterior → `clz=10 cy=2.3 tlz=-1 ty=2.0 rlz=8` (gate-height in front of canopy). `kitExtVolt` deck raised to `y=3.85` (underside **3.76 m** ≥ 3.5); posts/neon matched. Canopy footprint still non-collider (kiosk/bollards own collision).
2. **Empty black emblem discs**
   - Cause: `world.js emblemTex` / SIGN atlas had no Volt/Rust Claw UV; discs stayed black.
   - Fix: `kitPaintEmblem` + `kitFixEmblems` in `crewhouse_kit.js` paint slot 8/9 from `kit_logos.png` onto canvas textures, replace exterior emblem materials, `kitEmblem`/`noMerge`, detach from SIGN.list (retry). Runtime emblem_check: volt bright=8986, rustclaw=7151. Karasu path untouched (`noPlane` in kit probe = different placement; still uses existing emblem).
3. **Mirrored MARINA**
   - Cause: baked `putSign("MARINA",…, Math.PI)` faced north → street saw ANIRAM.
   - Fix: Palma-owned via `patch_crewhouse_kit.py` → `ry=0` (face south). Day+night heroes read **MARINA**.
4. **CREW_RIVALS colours (Systems)**
   - Cause: hard overrides L13–14 + TODO fallbacks; `CREW_RIVALS` not in HTML.
   - Fix: `kitTheme` looks up `(CREWS.find…||CREW_RIVALS.find…)`; overrides/TODO removed. `patch_crewhouse_kit.py` injects `CREW_RIVALS` after `CREWS`. Runtime THEME_PASS: Volt c1=`0xffe600` c2=`0xff2d95`; Rust Claw c1=`0xff7a1a` c2=`0x8a3416`; Karasu `0x00e5ff`/`0x9a3cff`.

### Verification (copy `/tmp/palma_garages.html`, lock via `palma_testlock.sh`, pid 2010810, released 13:58)
- Theme: THEME_PASS, 0 page errors.
- Gate: PASS volt/rustclaw/karasu, PAGEERRORS 0 OVERALL PASS.
- dcsplit2 RUNS=3 seed=1: causeway **world** mean **101.7** (≤110); street 78; b98 92.7; aerial 93.3. (n includes chars+fx.)
- Heroes overwritten (v1 kept): `shots/hero/garage_{volt,rustclaw}_{exterior_day,exterior_night,interior}.png`. Viewed: Volt gate clear + yellow/pink neon; both emblems filled; MARINA correct; real CREW_RIVALS colours.
- Real `sky-rydahs-v3-ikki.html` md5 still `5ad0f5646468f5fef7d25f9153144e8e`.

### Files
`crewhouse_kit.js`, `patch_crewhouse_kit.py`, `garage_hero_shots.py`, `palma_testlock.sh`. Backups `*.bak-ani-fix-*`.

### 2026-11-05 14:01 CST — Volt canopy underside (Ani)
- Cause: `kitExtBox(10.7,.06,6.4)` neon1 MeshBasic (toneMapped:false) = blown-out yellow sheet under night cam.
- Fix in `crewhouse_kit.js` kitExtVolt: remove full slab; dark PBR deck (M.dark roughness .6) + thin MeshStandard emissive strips (intensity 1.15, toneMapped); still 6 draws. build_copy → `/tmp/palma_garages.html`. Waiting lock (pbr_base + bases queue first).

### 2026-11-05 14:51 CST — resume canopy re-shoot
- Code + copy OK (emissiveIntensity 1.15 strips, no full slab). Waiter pid 2090461 healthy, yielding to Rigger 2078568 (simca+dark2, lock from 14:35). Pre-fix heroes still at garage_volt_exterior_{day,night}.png; *_v2 are same-byte pre-fix backups (not new shots).

### 2026-11-05 15:57 CST — Volt canopy heroes VERIFIED
- Existing waiter acquired at 15:51 CST; built copy only. New day/night shots captured at df=70/69, 1920×1080 dsf=1.5 HD seed=1 FX on; both viewed. Dark underside, thin yellow strips, no flat yellow blowout; gate/pad still clear. *_v2 files are intentionally the previous pre-fix heroes, NOT the new outputs.
- Runtime probe: extVariant draws=6; dark material #1c1e22 roughness .6 metalness .45; primary strips MeshStandardMaterial emissiveIntensity=1.15, toneMapped=true.
- dcsplit2 actual HOOK+BRV b98 view: world=95 ≤110, no page errors. Characters=106 (assets still loading in this short run), FX=5; 110 cap is WORLD metric.
- Quick gate harness wrongly asserted extVariant.visible=false (visibility uses camera layers); gate replay queued with original layer-aware test, Volt only. Do not use that harness FAIL as a gameplay regression.

### 2026-11-05 16:07 CST — Volt canopy ready for rebuild
- Correct original layer-aware Volt gate test PASS (unlock/enter/layer-hide/exit restore), PAGEERRORS 0. Gate-only lock released promptly.
- Both new heroes visually approved; prior heroes retained as *_v2. b98 world 95; exterior 6 draws. Real html md5 unchanged: 5ad0f5646468f5fef7d25f9153144e8e.
- DEMO_STATUS backed up and ready line added. CloudAgent unavailable; parent handover instructions at /tmp/volt_canopy_parent_message.txt. pbr_base mip-bias/storefront-glow polish intentionally deferred.
