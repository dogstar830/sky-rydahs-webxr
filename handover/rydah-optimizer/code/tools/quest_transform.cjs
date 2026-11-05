// Sky Rydahs Quest transform (glTF-Transform API). Called by quest_pipeline.py; never writes to its input.
// usage: node quest_transform.cjs IN OUT '<json opts>'
const GTN = process.env.GT_NODE_MODULES || '/workspace/tools/gt/node_modules';
const R = m => require(GTN + '/' + m);
const { NodeIO } = R('@gltf-transform/core');
const { ALL_EXTENSIONS, EXTMeshoptCompression, KHRDracoMeshCompression } = R('@gltf-transform/extensions');
const F = R('@gltf-transform/functions');
const draco3d = R('draco3dgltf'); const { MeshoptEncoder, MeshoptDecoder, MeshoptSimplifier } = R('meshoptimizer');
const sharp = R('sharp'); const path = require('path'); const fs = require('fs');
const [,, IN, OUT, OPTS] = process.argv; const o = JSON.parse(OPTS || '{}');
if (path.resolve(IN) === path.resolve(OUT)) { console.error('refusing: OUT == IN'); process.exit(2); }
(async () => {
  await MeshoptEncoder.ready; await MeshoptDecoder.ready;
  const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({
    'draco3d.decoder': await draco3d.createDecoderModule(), 'draco3d.encoder': await draco3d.createEncoderModule(),
    'meshopt.decoder': MeshoptDecoder, 'meshopt.encoder': MeshoptEncoder });
  const doc = await io.read(IN); const root = doc.getRoot(); const log = [];
  // start from plain float geometry: drop any input meshopt/draco/quantization so we re-encode cleanly (positions/_WC float32)
  for (const e of root.listExtensionsUsed()) if (['EXT_meshopt_compression','KHR_draco_mesh_compression'].includes(e.extensionName)) e.dispose();
  await doc.transform(F.dequantize());
  if (!root.listMeshes().some(m => m.listPrimitives().some(p => p.getAttribute('POSITION').getComponentType() !== 5126 || p.listAttributes().some(a => a.getNormalized()))))
    for (const e of root.listExtensionsUsed()) if (e.extensionName === 'KHR_mesh_quantization') e.dispose();
  // ---- textures: cap per slot type ----
  const caps = { base: o.maxBase || 2048, normal: o.maxNormal || 1024, orm: o.maxOrm || 1024, emissive: o.maxEmissive || o.maxBase || 2048, other: o.maxBase || 2048 };
  const crisp = o.keepCrisp ? new RegExp(o.keepCrisp, 'i') : null; const crispMax = o.crispMax || 2048;
  const slotOf = new Map();
  for (const m of root.listMaterials()) {
    const put = (t, s) => { if (!t) return; const p = slotOf.get(t) || { slots: new Set(), mats: new Set() }; p.slots.add(s); p.mats.add(m.getName()); slotOf.set(t, p); };
    put(m.getBaseColorTexture(), 'base'); put(m.getNormalTexture(), 'normal'); put(m.getMetallicRoughnessTexture(), 'orm');
    put(m.getOcclusionTexture(), 'orm'); put(m.getEmissiveTexture(), 'emissive');
  }
  // --pot: snap each axis to the nearest power of two (<= cap) so every mip level stays a multiple of 4 (BC1/BC7 on desktop reject e.g. 1368->684->342)
  const potN = n => { const lo = 2 ** Math.floor(Math.log2(n)), hi = lo * 2; return n === lo ? lo : (o.pot === 'up' ? hi : ((n - lo <= hi - n) ? lo : hi)); };  // --pot up: never lose resolution
  const dims = (W, H, cap) => { const s = Math.min(1, cap / Math.max(W, H)); let w = Math.round(W * s), h = Math.round(H * s); if (o.pot) { w = Math.min(cap, potN(w)); h = Math.min(cap, potN(h)); } return [w, h]; };
  for (const t of root.listTextures()) {
    const info = slotOf.get(t) || { slots: new Set(['other']), mats: new Set() };
    let cap = Math.max(...[...info.slots].map(s => caps[s]));
    const label = [t.getName(), t.getURI(), ...info.mats].join(' ');
    if (crisp && crisp.test(label)) cap = Math.max(cap, crispMax);
    const img = t.getImage(); if (!img || t.getMimeType() === 'image/ktx2') continue; const meta = await sharp(Buffer.from(img)).metadata();
    if (o.forcePng && t.getMimeType() !== 'image/png') { const [fw, fh] = dims(meta.width, meta.height, cap);
      t.setImage(new Uint8Array(await sharp(Buffer.from(img)).resize(fw, fh, { kernel: 'lanczos3', fit: 'fill' }).png().toBuffer())).setMimeType('image/png');
      const ext = t.getURI(); if (ext) t.setURI(ext.replace(/\.\w+$/, '.png')); log.push(`tex ${t.getName()||'?'} -> png ${fw}x${fh} (for KTX2 source)`); continue; }
    const [tw, th] = dims(meta.width, meta.height, cap);
    if (tw === meta.width && th === meta.height) { log.push(`tex ${t.getName()||'?'} [${[...info.slots]}] ${meta.width}x${meta.height} keep`); continue; }
    const w = tw, h = th;
    let p = sharp(Buffer.from(img)).resize(w, h, { kernel: 'lanczos3', fit: 'fill' }); const mt = t.getMimeType();
    p = mt === 'image/png' ? p.png({ compressionLevel: 9 }) : mt === 'image/webp' ? p.webp({ quality: 92 }) : p.jpeg({ quality: 92 });
    t.setImage(new Uint8Array(await p.toBuffer())); log.push(`tex ${t.getName()||'?'} [${[...info.slots]}] ${meta.width}x${meta.height} -> ${w}x${h}`);
  }
  // ---- optional simplify LOD0 ----
  if (o.simplify) { // target tri count for meshes whose name matches LOD0 (or all meshes if no LOD names)
    await MeshoptSimplifier.ready; const meshes = root.listMeshes(); const lod0 = meshes.filter(m => /LOD0/i.test(m.getName())); const tgt = lod0.length ? lod0 : meshes;
    const tris = m => m.listPrimitives().reduce((a, p) => a + (p.getIndices() ? p.getIndices().getCount() : p.getAttribute('POSITION').getCount()) / 3, 0);
    const total = tgt.reduce((a, m) => a + tris(m), 0); const ratio = Math.min(1, o.simplify / total);
    if (ratio < 1) { for (const m of tgt) for (const p of m.listPrimitives()) { if (p.listTargets().length) { log.push(`simplify skip ${m.getName()} (morph targets)`); continue; }
        await F.simplifyPrimitive(p, { simplifier: MeshoptSimplifier, ratio, error: o.simplifyError || 0.01, lockBorder: true }); }
      log.push(`simplify LOD0 ${total} -> target ${o.simplify} (ratio ${ratio.toFixed(3)}) after: ${tgt.reduce((a, m) => a + tris(m), 0)}`); }
    else log.push(`simplify: LOD0 ${total} already <= ${o.simplify}`);
  }
  await doc.transform(F.dedup({ propertyTypes: ['Accessor', 'Texture', 'Material'] }), F.prune({ keepAttributes: true, keepLeaves: true, keepSolidTextures: true }));
  // ---- geometry ----
  if (o.geometry === 'draco') {
    // Draco: custom _* attrs are encoded as GENERIC; positions decode back to float32, so _WC stays float in the same space.
    // 16-bit position+generic quantization keeps decode error ~1/65535 of bbox (sub-0.1 mm on a rider). Morph-target prims are left uncompressed by the encoder.
    for (const m of root.listMeshes()) for (const p of m.listPrimitives()) if (p.listTargets().length) log.push(`draco: ${m.getName()} has morph targets -> left uncompressed (KHR_draco cannot hold targets)`);
    doc.createExtension(KHRDracoMeshCompression).setRequired(true).setEncoderOptions({
      method: KHRDracoMeshCompression.EncoderMethod.EDGEBREAKER, encodeSpeed: 5, decodeSpeed: 5,
      quantizationBits: { POSITION: o.qPos || 16, NORMAL: 10, COLOR: 8, TEX_COORD: 12, GENERIC: o.qGeneric || 16 }, quantizationVolume: 'mesh' });
  } else if (o.geometry === 'meshopt16') {
    // Meshopt at 16 bit, but POSITION and every custom _* attribute (_WC etc) stay float32: only NORMAL/TEXCOORD/COLOR are quantized.
    await doc.transform(F.reorder({ encoder: MeshoptEncoder }),
      F.quantize({ pattern: /^(NORMAL|TANGENT|TEXCOORD_\d+|COLOR_\d+)$/, quantizeNormal: 16, quantizeTexcoord: 16, quantizeColor: 16 }));
    doc.createExtension(EXTMeshoptCompression).setRequired(true).setEncoderOptions({ method: EXTMeshoptCompression.EncoderMethod.FILTER });
  }
  if (o.forcePng) for (const e of root.listExtensionsUsed()) if (e.extensionName === 'EXT_texture_webp' && !root.listTextures().some(t => t.getMimeType() === 'image/webp')) e.dispose();
  await io.write(OUT, doc); console.log(log.join('\n'));
})().catch(e => { console.error(e.stack || e); process.exit(1); });
