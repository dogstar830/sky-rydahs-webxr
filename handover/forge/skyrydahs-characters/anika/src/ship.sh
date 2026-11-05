# ship.sh RAW FINAL : deinterleave raw -> draco (float decode, no KHR_mesh_quantization) -> validate; quest + ktx2 tiers
set -e; GT=/workspace/tools/gt/node_modules/.bin/gltf-transform; RAW=$1; FIN=$2
python3 /workspace/tools/deinterleave.py $RAW ${RAW%.glb}.flat.glb
$GT draco ${RAW%.glb}.flat.glb $FIN.tmp.glb --method edgebreaker >/dev/null
python3 /workspace/tools/deinterleave.py $FIN.tmp.glb $FIN >/dev/null; rm $FIN.tmp.glb
$GT validate $FIN 2>&1 | tail -6
cd /workspace/v3build && python3 tools/quest_pipeline.py $FIN --geometry draco --max-base 2048 --max-normal 1024 --max-orm 1024 --ktx2 --force 2>&1 | grep -E "AFTER|size|WARN|FLAG|refus"
for q in ${FIN%.glb}.quest.glb ${FIN%.glb}.quest-ktx2.glb; do [ -f $q ] && $GT validate $q 2>&1 | grep -iE "error|warning" | head -3; done
