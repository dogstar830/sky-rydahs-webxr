// Caali G texture-only KTX2: geometry/accessors untouched (quantized ints kept), meshopt re-applied without re-quantizing.
// usage: node caali_ktx2.cjs topng IN OUT  |  node caali_ktx2.cjs meshopt IN OUT
const NM=process.env.GT_NODE_MODULES||'/workspace/tools/gt/node_modules';
const {NodeIO}=require(NM+'/@gltf-transform/core');const X=require(NM+'/@gltf-transform/extensions');
const {MeshoptDecoder,MeshoptEncoder}=require(NM+'/meshoptimizer');const sharp=require(NM+'/sharp');
(async()=>{await MeshoptDecoder.ready;await MeshoptEncoder.ready;const [mode,inp,out]=process.argv.slice(2);
const io=new NodeIO().registerExtensions(X.ALL_EXTENSIONS).registerDependencies({'meshopt.decoder':MeshoptDecoder,'meshopt.encoder':MeshoptEncoder});
const d=await io.read(inp);const root=d.getRoot();
if(mode==='topng'){for(const t of root.listTextures()){if(t.getMimeType()==='image/webp'){t.setImage(new Uint8Array(await sharp(Buffer.from(t.getImage())).png().toBuffer())).setMimeType('image/png');t.setURI((t.getURI()||t.getName())+'.png');}}
 for(const e of root.listExtensionsUsed()) if(e.extensionName==='EXT_texture_webp'||e.extensionName==='EXT_meshopt_compression') e.dispose();}
if(mode==='topng'&&process.env.DROP_NORMAL==='1'){ for(const m of root.listMaterials()){ const t=m.getNormalTexture(); if(t){ m.setNormalTexture(null); if(!t.listParents().some(p=>p!==root)) t.dispose(); } } } // wardrobe noNormal:true drops it at runtime anyway
if(mode==='meshopt'){d.createExtension(X.EXTMeshoptCompression).setRequired(true).setEncoderOptions({method:X.EXTMeshoptCompression.EncoderMethod.QUANTIZE});}
await io.write(out,d);console.log('wrote',out);})();
