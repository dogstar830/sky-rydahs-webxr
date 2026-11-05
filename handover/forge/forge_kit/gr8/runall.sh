cd /workspace/forge_kit/gr8
N=anika CFG='{"boot":0.33,"prefix":"Anika","mat":"AnikaAtlas","decals":[{"img":"decal_anika_back.png","x":0,"z":1.19,"w":0.15,"h":0.15,"side":"back"}],"lods":[["LOD0",104000,2048,1024,0],["LOD1",33000,1024,512,1],["LOD2",11000,512,256,2],["NPC0",23500,1024,1024,1]]}' blender -b --python build_gr8.py > anika_build.log 2>&1
echo ANIKA_DONE
N=caali CFG='{"boot":0.37,"prefix":"CaaliG","mat":"CaaliGAtlas","decals":[{"img":"decal_gr8yzone_tee.png","x":-0.005,"z":1.365,"w":0.21,"h":0.2835,"side":"front"},{"img":"decal_caali_back.png","x":0,"z":1.405,"w":0.34,"h":0.34,"side":"back"}],"lods":[["HD0",250000,4096,2048,0],["LOD0",104000,2048,1024,0],["LOD1",33000,1024,512,1],["LOD2",11000,512,256,2]]}' blender -b --python build_gr8.py > caali_build.log 2>&1
echo CAALI_DONE
