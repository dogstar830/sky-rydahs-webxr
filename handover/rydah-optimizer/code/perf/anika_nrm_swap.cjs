// Anika normal-map swap + Draco re-encode. usage: node anika_nrm_swap.cjs IN.glb OUT.glb '<json>'
// json: {"nrm":{"anika_LOD0_nrm":"/path.ktx2",...}, "drop":["anika_LOD1_nrm",...], "qPos":16, "qGeneric":16}
// Never writes IN. Normal textures listed in "drop" are unbound from their material and pruned.
const GTN=process.env.GT_NODE_MODULES||'/workspace/tools/gt/node_modules',R=m=>require(GTN+'/'+m);
const {NodeIO}=R('@gltf-transform/core');const {ALL_EXTENSIONS,KHRDracoMeshCompression}=R('@gltf-transform/extensions');
const F=R('@gltf-transform/functions');const draco3d=R('draco3dgltf');const fs=require('fs'),path=require('path');
const [,,IN,OUT,OPTS]=process.argv;const o=JSON.parse(OPTS||'{}');
if(path.resolve(IN)===path.resolve(OUT)){console.error('refusing OUT==IN');process.exit(2);}
if(fs.existsSync(OUT)&&!o.force){console.error('refusing: OUT exists');process.exit(2);}
(async()=>{const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'draco3d.decoder':await draco3d.createDecoderModule(),'draco3d.encoder':await draco3d.createEncoderModule()});
const doc=await io.read(IN),root=doc.getRoot();
for(const t of root.listTextures()){const n=t.getName();if(o.nrm&&o.nrm[n]){t.setImage(fs.readFileSync(o.nrm[n]));console.log('swap',n,o.nrm[n]);}}
for(const m of root.listMaterials()){const t=m.getNormalTexture();if(t&&(o.drop||[]).includes(t.getName())){m.setNormalTexture(null);console.log('drop',t.getName(),'from',m.getName());}}
await doc.transform(F.prune({keepAttributes:true,keepLeaves:true,keepSolidTextures:true}));
doc.createExtension(KHRDracoMeshCompression).setRequired(true).setEncoderOptions({method:KHRDracoMeshCompression.EncoderMethod.EDGEBREAKER,encodeSpeed:5,decodeSpeed:5,
 quantizationBits:{POSITION:o.qPos||16,NORMAL:10,COLOR:8,TEX_COORD:12,GENERIC:o.qGeneric||16},quantizationVolume:'mesh'});
await io.write(OUT,doc);console.log('wrote',OUT,fs.statSync(OUT).size);})().catch(e=>{console.error(e);process.exit(1)});
