import { KTX2Loader } from './package/examples/jsm/loaders/KTX2Loader.js';
if (!window.THREE) throw new Error('KTX2Loader.classic.js: load three.min.js (r128) first');
window.THREE.KTX2Loader = KTX2Loader;
