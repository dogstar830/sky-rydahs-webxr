// Sky Rydah's — Anubis rider loader. Drop-in for sky-rydahs-v3.html:
//   import { loadRider, loadRiderFP } from './skyrydahs-characters/anubis/loader.js';
//   const rider = await loadRider(scene, 'skyrydahs-characters/anubis/anubis-rider.glb', crewColors, { vr });
//   const fp    = await loadRiderFP(scene, 'skyrydahs-characters/anubis/anubis-fp.glb', crewColors, { vr });
//   every frame: rider.userData.update(camera, dt, boost01)
// crewColors: slot keys or palette roles (primary/secondary/accent/trim/skin); see ../shared/rider_loader.js.
import { loadRider as base, loadRiderFP as baseFP } from '../shared/rider_loader.js';
export const DEFAULTS = { skin: 0xd9a988, hair: 0x2b2f35, jacket: 0x1f2226, cloth: 0x1a1c20, gold: 0x00b8b0, metal: 0x7d8794, skate: 0x2b2f35, eyes: 0xffffff, iris: 0x00e0d0, wheelGlow: 0x00e0d0, glow2: 0x30fff0, rim: 0x00e5d5, shadow: 0x3c4a8a, outline: 0x05070a };
export const OPTS = { slotRim: { hair: 0.3, skin: 0.2 }, slotEmi: { iris: 1.0 }, slotSpec: { gold: 0.06, skate: 0.3 } };
export const loadRider = (scene, url, crewColors = {}, opts = {}) => base(scene, url, crewColors, { defaults: DEFAULTS, crewName: 'Anubis', ...OPTS, ...opts });
export const loadRiderFP = (scene, url, crewColors = {}, opts = {}) => baseFP(scene, url, crewColors, { defaults: DEFAULTS, crewName: 'Anubis', ...OPTS, ...opts });
