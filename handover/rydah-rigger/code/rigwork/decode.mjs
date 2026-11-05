import {NodeIO} from '@gltf-transform/core'; import {ALL_EXTENSIONS} from '@gltf-transform/extensions';
import draco3d from 'draco3dgltf';
const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'draco3d.decoder':await draco3d.createDecoderModule()});
const [inp,out]=process.argv.slice(2); const doc=await io.read(inp);
for(const e of doc.getRoot().listExtensionsUsed()) if(e.extensionName==='KHR_draco_mesh_compression') e.dispose();
await io.write(out,doc); console.log('ok',out);
