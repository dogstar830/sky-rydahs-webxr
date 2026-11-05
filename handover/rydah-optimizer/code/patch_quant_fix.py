# Wardrobe/Ikki riders built with KHR_mesh_quantization (Caali G: caali-g.glb / caali-g-hd.glb) store POSITION as int16-normalized
# with the dequantization folded into the skin's inverse bind matrices, but the custom AT attributes _WC (wheel centre) and the
# uComp/vRestY maths in IKKI_AT_VERT are in metres. Wheel spin then rotates wheel verts about a pivot ~0.8 m away -> dark "clumps"
# orbiting the feet + shards on the skates (only while uSpin!=0). Fix: at load, dequantize POSITION back to Float32 metres with the
# exact per-mesh matrix D = meshWorld^-1 * boneWorld * boneInverse (constant over joints at rest) and set boneInverse_k *= D^-1.
# Skinned result is unchanged; _WC/uComp/vRestY become consistent again. Float GLBs (Ikki) are skipped. ?dequant=0 disables. Idempotent.
f='/workspace/v3build/sky-rydahs-v3-ikki.html'; src=open(f).read()
if 'SR_DEQUANT' in src: print("patch_quant_fix: already applied"); raise SystemExit
A='  const root=gltf.scene, lv=[], bones={};\n'
assert src.count(A)==1, src.count(A)
src=src.replace(A,'  const root=gltf.scene, lv=[], bones={}; SR_DEQUANT(root);\n',1)
B='async function loadIkki(parent,refH,fresh,opt){'
assert src.count(B)==1
src=src.replace(B,r'''function SR_DEQUANT(root){ if(new URLSearchParams(location.search).get('dequant')==='0'||root.userData.srDequant) return; root.userData.srDequant=true; root.updateMatrixWorld(true);
  const DEN={Int8Array:127,Uint8Array:255,Int16Array:32767,Uint16Array:65535};
  root.traverse(m=>{ if(!m.isSkinnedMesh) return; const P=m.geometry.attributes.position; if(!P||P.array instanceof Float32Array||!m.geometry.attributes._wc) return;
    const sk=m.skeleton, k=sk.bones.length-1, D=new THREE.Matrix4().copy(m.matrixWorld).invert().multiply(sk.bones[0].matrixWorld).multiply(sk.boneInverses[0]);
    const s=P.normalized?DEN[P.array.constructor.name]||1:1, out=new Float32Array(P.count*3), v=new THREE.Vector3();
    for(let i=0;i<P.count;i++){ v.set(Math.max(P.getX(i)/s,-1),Math.max(P.getY(i)/s,-1),Math.max(P.getZ(i)/s,-1)).applyMatrix4(D); out[i*3]=v.x; out[i*3+1]=v.y; out[i*3+2]=v.z; }
    m.geometry.setAttribute('position',new THREE.BufferAttribute(out,3)); m.geometry.computeBoundingBox(); m.geometry.computeBoundingSphere();
    const Di=D.clone().invert(); for(const b of sk.boneInverses) b.multiply(Di); m.userData.srDequant=D.elements.map(x=>+x.toFixed(4)); }); }
'''+B,1)
open(f,'w').write(src); print("patch_quant_fix: SR_DEQUANT installed in loadIkki")
