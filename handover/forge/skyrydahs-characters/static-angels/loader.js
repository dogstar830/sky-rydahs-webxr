// Sky Rydah's — Static Angels rider loader. Drop-in for sky-rydahs-v3.html:
//   import { loadRider, loadRiderFP } from './skyrydahs-characters/static-angels/loader.js';
//   const rider = await loadRider(scene, 'skyrydahs-characters/static-angels/static-angels-rider.glb', crewColors, { vr });
//   const fp    = await loadRiderFP(scene, 'skyrydahs-characters/static-angels/static-angels-fp.glb', crewColors, { vr });
//   every frame: rider.userData.update(camera, dt, boost01)
// crewColors: slot keys or palette roles (primary/secondary/accent/trim/skin); see ../shared/rider_loader.js.
import { loadRider as base, loadRiderFP as baseFP } from '../shared/rider_loader.js';
export const DEFAULTS = { skin: 0xc98f6e, hair: 0x1e2050, jacket: 0x22d3e0, cloth: 0x1b1b22, gold: 0x9b3dff, metal: 0xd8dcf0, skate: 0x4a2a78, eyes: 0xffffff, iris: 0xa65cff, wheelGlow: 0x00e5ff, glow2: 0x7fe9ff, rim: 0x00e5ff, shadow: 0x4b3f9e, outline: 0x08061a };
export const OPTS = { slotRim: { hair: 0.3, skin: 0.2 } };
export const loadRider = (scene, url, crewColors = {}, opts = {}) => base(scene, url, crewColors, { defaults: DEFAULTS, crewName: 'Static Angels', ...OPTS, ...opts });
export const loadRiderFP = (scene, url, crewColors = {}, opts = {}) => baseFP(scene, url, crewColors, { defaults: DEFAULTS, crewName: 'Static Angels', ...OPTS, ...opts });
