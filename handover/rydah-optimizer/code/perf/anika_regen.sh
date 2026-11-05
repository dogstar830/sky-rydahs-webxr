#!/usr/bin/env bash
# Regenerate anika-{rider,npc}.opt-ktx2.glb from the rigged sources (Rydah Optimizer, chosen 2026-10-30).
# Normals: LOD0 (rider) / NPC0 (npc) resized to 768 (Lanczos), UASTC q2 + RDO lambda 1.0 + zstd 20, mips; LOD1/LOD2 normals dropped.
# Geometry: Draco edgebreaker, POSITION 16 / GENERIC 16 bits (pipeline default). Other textures: pipeline KTX2 (ETC1S col/ORM).
# Never overwrites: refuses if the output exists (move it to *.v1 first).
set -euo pipefail
A=${A:-/workspace/skyrydahs-characters/anika}; T=/workspace/v3build/tools; P=/workspace/v3build/perf
K=$T/ktx/bin; export LD_LIBRARY_PATH=$T/ktx/lib; W=$(mktemp -d /tmp/anika_regen.XXXX)
run(){ who=$1 base=$2 nrm=$3 drop=$4
  out=$A/anika-$who.opt-ktx2.glb; [ -e "$out" ] && { echo "refusing: $out exists"; exit 2; }
  python3 $T/quest_pipeline.py $A/anika-$who.glb --out-dir $W --suffix opt --geometry draco --max-base $base --max-normal 1024 --max-orm 1024 --ktx2 >/dev/null
  python3 - "$A/anika-$who.glb" "$nrm" "$W/n.png" <<'PY'
import json,struct,sys,io
from PIL import Image
b=open(sys.argv[1],'rb').read();n=struct.unpack('<I',b[12:16])[0];j=json.loads(b[20:20+n]);o0=20+n+8
im=[i for i in j['images'] if i['name']==sys.argv[2]][0];bv=j['bufferViews'][im['bufferView']];o=o0+bv.get('byteOffset',0)
Image.open(io.BytesIO(b[o:o+bv['byteLength']])).convert('RGB').resize((768,768),Image.LANCZOS).save(sys.argv[3])
PY
  $K/ktx create --format R8G8B8_UNORM --assign-tf linear --generate-mipmap --encode uastc --uastc-quality 2 --uastc-rdo --uastc-rdo-l 1.0 --zstd 20 $W/n.png $W/n.ktx2
  node $P/anika_nrm_swap.cjs $W/anika-$who.opt-ktx2.glb "$W/sw.glb" "{\"nrm\":{\"$nrm\":\"$W/n.ktx2\"},\"drop\":$drop}"
  python3 $P/glb_strip_normals.py $W/sw.glb "$out"; rm -f $W/sw.glb   # 09:46: roster inherits noNormal:true -> ship without normals
}
run rider 2048 anika_LOD0_nrm '["anika_LOD1_nrm","anika_LOD2_nrm"]'
run npc   1024 anika_NPC0_nrm '["anika_LOD2_nrm"]'
rm -rf $W; ls -l $A/anika-{rider,npc}.opt-ktx2.glb
