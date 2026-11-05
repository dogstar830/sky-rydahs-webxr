# Bridges research — Palma City (Sky Rydahs)
Images: /workspace/skyrydahs-ref/bridges/ (licences in bridges/SOURCES.txt — CC0 / public domain only).
Rule: numbers below are quoted from the cited source; game values are stylized scale-downs (see "Game mapping").

## 1. Hathaway Bridge (US-98 / SR-30, St. Andrew Bay, Panama City <-> Panama City Beach)
- Twin precast segmental concrete box-girder bridges, each 80 ft wide; WB 3,814 ft, EB 3,383 ft; max span 330 ft; max height 85 ft; vertical clearance 65 ft; horizontal clearance 287 ft. Opened 2003-04, design-build Granite / HNTB / RS&H. [losthistory.net/bridgepros/projects/Hathaway/Index.htm]
- Seven 330-ft (100.6 m) main spans, 265-ft transition spans, 200-ft end spans; HNTB design, AASHTO LRFD. [TRR, doi.org/10.3141/trr.11s.k258x272x5888071]
- 544 precast segments, segment width 24.5 m, balanced-cantilever erection with overhead launching girder, epoxy joints, post-tensioning tendons. [rde.it/en/projects/hathaway-bridge-replacement/]
- Main-span pier foundations: 11 piles per bridge; >70 ft free pile length under 100-yr scour; designed for barge impact. [trid.trb.org/view/732586]
- Visual (photo hathaway_west_cc0.jpg, CC0): pale buff/grey concrete, haunched (variable-depth) box girder deepening over piers, tall flared/"hammerhead"-like pier columns in pairs, BLUE uplights washing piers and deck soffit at night, sodium-amber single-arm lamp poles on the parapet at regular spacing, thin metal rail atop concrete parapet, red/green navigation lights.

## 2. DuPont Bridge (US-98 / SR-30, St. Andrew Bay/ICWW, Tyndall AFB <-> Parker)
- NBI #460019, built 1965; prestressed concrete continuous, stringer/multi-beam girder; 4 lanes; structure length 2,748 ft (2,788 ft total); max span 120 ft; 3 main-unit spans + 28 approach spans; curb/sidewalk 2 ft; superstructure rated Poor (4) in 2022, replacement planned. [FDOT BIP application + 2022 inspection report cover, fdotwww.blob.core.windows.net/.../bridge-investment-2022-dupont/]
- "Typical of 1960s era construction with concrete guard rails and no shoulders", crests 49.9 ft above the ICWW. [aaroads.com/guides/us-098-west-bay-fl]
- Original 1929 truss bridge opened April 1929 (Hathaway one month later). [newsherald.com "Spanning the Bays", 2012]
- Look: multi-beam AASHTO/I-girders on multi-column bents with rectangular pier caps (bent caps), low concrete parapet.

## 3. Cable-stayed references
- Sunshine Skyway (I-275, Tampa Bay): main span 1,200 ft (366 m), side spans 540 ft; concrete pylons 435 ft above water / 240 ft above roadway; single central plane fan, 21 stays per pylon half, anchored every 24 ft (7.3 m); stays in 6 5/8 and 8 5/8 in steel pipe, grouted; 175 ft clearance; precast segmental box. [PCI Journal Nov-Dec 1986; FDOT Structures Research Center report] Pipes painted brilliant yellow; dolphins (ship-impact islands) around piers; 40-ft roadways either side of cables. [pbs.org/wgbh/buildingbig]
- Dames Point (Jacksonville, St. Johns River): 396.3 m centre span, 198.15 m flanking spans, concrete towers and edge-girder deck with floorbeams; vertical planes of stays in harp configuration, thread bars grouted in steel pipe. [IABSE reports 64 (1991), Loizias & McCabe] Deck 105 ft wide with two solid edge girders; tower legs linked by bow-shaped struts. [TRR 1290, onlinepubs.trb.org/Onlinepubs/trr/1991/1290vol1/1290-032.pdf]
- Cochrane-Africatown (Mobile, AL) photo only (cochrane_africatown_pd.jpg): white/grey concrete H-towers, two planes of semi-fan stays.

## 4. Suspension reference (Golden Gate)
- Towers 746 ft above water, 500 ft above roadway; main cable 36 3/8 in dia incl. wrapping; 250 pairs of vertical suspender ropes 50 ft on centre, 2 11/16 in dia. [goldengate.org design-construction stats]
- HAER detail photos (PD): cable bands clamp the main cable, suspenders hang in pairs from each band.

## 5. Barriers / parapets (FDOT)
- 32" F-Shape Traffic Railing (Index 420) was the basic default for FDOT bridges (TL-4). [FDOT ids-00420.pdf]
- 36" Single-Slope Traffic Railing (Index 521-427) is now the basic default; up to three 2" conduits with embedded junction boxes (used for lighting) allowed; drainage slots 2-3" high optional; form-liner texture on outside face allowed. [FDOT spi-521-427.pdf]
- 42" Vertical Shape (Index 521-422) for bridges with raised sidewalks. [FDOT spi-521-422.pdf]

## 6. Generic components to model (from the above)
deck slab + wearing surface, lane lines; girders (box or I-beams) with diaphragms; bearings on pier caps; pier caps/bents (hammerhead or multi-column); pier columns; pile cap/footing at waterline; fender/dolphin at channel piers; finger expansion joints at piers; abutment + wing walls + approach slab at ends; concrete parapet with conduit-fed lighting; single-arm lamp poles; nav lights (red on pylon tops, green channel marks); towers with cross struts, saddles; stays with anchor blocks; suspension: main cable, cable bands, suspenders, anchorages.

## Game mapping (stylized; the world is ~1/10 scale vertically)
Deck sits at y=0 over water at y=-2.4, so heights are compressed: real 65 ft clearance cannot be reproduced without moving grind cables, so the deck was kept. Colours: concrete 0x9c9a92 (pale buff-grey per Hathaway photo), steel 0x6d737c, Skyway-style yellow kept only as an accent idea. Night: blue pier/soffit uplights (Hathaway photo), bridge colour deck-edge strips, tower uplights, cable lights.
