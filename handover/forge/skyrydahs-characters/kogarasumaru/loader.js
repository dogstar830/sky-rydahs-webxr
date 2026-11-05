// Sky Rydah's — Kogarasumaru rider loader. Drop-in for sky-rydahs-v3.html:
//   import { loadRider, loadRiderFP } from './skyrydahs-characters/kogarasumaru/loader.js';
//   const rider = await loadRider(scene, 'skyrydahs-characters/kogarasumaru/kogarasumaru-rider.glb', crewColors, { vr });
//   const fp    = await loadRiderFP(scene, 'skyrydahs-characters/kogarasumaru/kogarasumaru-fp.glb', crewColors, { vr });
//   every frame: rider.userData.update(camera, dt, boost01)
// crewColors: slot keys or palette roles (primary/secondary/accent/trim/skin); see ../shared/rider_loader.js.
import { loadRider as base, loadRiderFP as baseFP } from '../shared/rider_loader.js';
export const DEFAULTS = { skin: 0xf0c8a8, hair: 0x15131c, jacket: 0x232228, cloth: 0x2a2630, gold: 0xe0141e, metal: 0x9aa0ad, skate: 0x2e2c33, eyes: 0xffffff, iris: 0x00b8d4, wheelGlow: 0x00e5ff, glow2: 0x40f0ff, rim: 0x30d8ff, shadow: 0x4a3a7a, outline: 0x070509 };
export const OPTS = { slotRim: { hair: 0.3, skin: 0.2 } };
export const loadRider = (scene, url, crewColors = {}, opts = {}) => base(scene, url, crewColors, { defaults: DEFAULTS, crewName: 'Kogarasumaru', ...OPTS, ...opts });
export const loadRiderFP = (scene, url, crewColors = {}, opts = {}) => baseFP(scene, url, crewColors, { defaults: DEFAULTS, crewName: 'Kogarasumaru', ...OPTS, ...opts });
