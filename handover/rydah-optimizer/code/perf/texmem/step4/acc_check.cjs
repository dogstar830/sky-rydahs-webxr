// decoded accessor fingerprint: name/attr, type, componentType, normalized, count, sha1 of decoded array
const NM=process.env.GT_NODE_MODULES||'/workspace/tools/gt/node_modules';
const {NodeIO}=require(NM+'/@gltf-transform/core');const {ALL_EXTENSIONS}=require(NM+'/@gltf-transform/extensions');
const {MeshoptDecoder}=require(NM+'/meshoptimizer');const crypto=require('crypto');
(async()=>{await MeshoptDecoder.ready;const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'meshopt.decoder':MeshoptDecoder});
for(const f of process.argv.slice(2)){const d=await io.read(f);const out=[];
for(const m of d.getRoot().listMeshes())m.listPrimitives().forEach((p,i)=>{for(const s of p.listSemantics()){const a=p.getAttribute(s);const arr=a.getArray();
out.push(`${m.getName()}#${i} ${s} ${a.getType()} ${a.getComponentType()} n=${a.getNormalized()} c=${a.getCount()} ${crypto.createHash('sha1').update(Buffer.from(arr.buffer,arr.byteOffset,arr.byteLength)).digest('hex').slice(0,16)}`);}
const ix=p.getIndices();if(ix){const arr=ix.getArray();out.push(`${m.getName()}#${i} INDICES ${ix.getComponentType()} c=${ix.getCount()} ${crypto.createHash('sha1').update(Buffer.from(arr.buffer,arr.byteOffset,arr.byteLength)).digest('hex').slice(0,16)}`);}});
console.log('## '+f+' ext='+d.getRoot().listExtensionsUsed().map(e=>e.extensionName).join(','));console.log(out.join('\n'));}})();
