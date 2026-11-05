// Sky Rydah's — Caali (crew Code : E) rider loader. Drop-in for sky-rydahs-v3.html:
//   import { loadRider, loadRiderFP } from './skyrydahs-characters/caali/loader.js';
//   const rider = await loadRider(scene, 'skyrydahs-characters/caali/caali-rider.glb', crewColors, { vr });
//   const fp    = await loadRiderFP(scene, 'skyrydahs-characters/caali/caali-fp.glb', crewColors, { vr });
//   every frame: rider.userData.update(camera, dt, boost01)
// crewColors: slot keys or palette roles (primary/secondary/accent/trim/skin); see ../shared/rider_loader.js.
import { loadRider as base, loadRiderFP as baseFP } from '../shared/rider_loader.js';
export const DEFAULTS = { skin: 0xe2b48e, hair: 0x111015, jacket: 0x17161c, cloth: 0x3a3350, gold: 0x7446d0, metal: 0xc3c7d0, skate: 0x5d5f68, eyes: 0xffffff, iris: 0x4a3a36, wheelGlow: 0xffd700, glow2: 0x22e8f0, rim: 0x9b7bff, shadow: 0x4a3f8e, outline: 0x07060c };
export const OPTS = { slotSpec: { gold: 0.06 }, slotRim: { hair: 0.25, gold: 0.45, skin: 0.2 } };
export const loadRider = (scene, url, crewColors = {}, opts = {}) => base(scene, url, crewColors, { defaults: DEFAULTS, crewName: 'Code : E', ...OPTS, ...opts });
export const loadRiderFP = (scene, url, crewColors = {}, opts = {}) => baseFP(scene, url, crewColors, { defaults: DEFAULTS, crewName: 'Code : E', ...OPTS, ...opts });
