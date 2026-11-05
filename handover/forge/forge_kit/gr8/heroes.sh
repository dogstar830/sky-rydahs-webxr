cd /workspace/forge_kit/gr8; S=/workspace/v3build/shots/hero
for spec in "anika_lods.blend Anika_LOD0 anika front anika_front_vs_ref" "anika_lods.blend Anika_LOD0 anika q34 anika_34_vs_ref" "caali_lods.blend CaaliG_LOD0 caali front caali_v2_front_vs_ref" "caali_lods.blend CaaliG_LOD0 caali q34 caali_v2_34_vs_ref"; do
 set -- $spec; blender -b --python hero.py -- $1 $2 /tmp/forge_hero_$5.png $4 > /tmp/forge_hero_$5.log 2>&1
 python3 compose.py /tmp/forge_hero_$5.png /home/box/Downloads/gr8yzone/$3_crop.png $S/$5.png "$2 (LOD0) Blender Cycles, $4 view, A-pose"
done; echo HEROES_DONE
