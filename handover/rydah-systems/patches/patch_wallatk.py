import os as _os; _SRC=_os.environ.get('SR_SRC','/workspace/v3build').rstrip('/')+'/'; _OUT=_os.environ.get('SR_HTML','/workspace/v3build/sky-rydahs-v3-ikki.html')  # Systems 10:25: SR_HTML / SR_SRC (default = old paths)
# Wall rides + crew attacks. Runs after patch_gates.py in build_ikki.sh.
f=_OUT; src=open(f).read(); js=open(_SRC+'wallatk.js').read()
def rep(o,n):
    global src; assert src.count(o)==1,("patch_wallatk miss",o[:70]); src=src.replace(o,n,1)
rep("// ===== LOOP =====",js+"\n// ===== LOOP =====")
rep("  if(State.mode===\"ride\") updateRide(dt);","  try{ wallAtkPre(dt); }catch(e){ console.warn('wall in',e); }\n  if(State.mode===\"ride\"){ let w=false; try{ w=wallStep(dt); }catch(e){ if(!window.__wallErr) console.warn('wall',e); window.__wallErr=e; } if(!w) updateRide(dt); }")
rep("  updateRiders(dt); districtMood(dt);","  updateRiders(dt); wallAtkPost(dt); districtMood(dt);")
src=src.replace("Stick / WASD to skate · Shift / LB boost dash · hold T / RB to tag walls","Stick / WASD to skate · Space / A jump + wall ride · J K L / Y RT LT attacks · Shift / LB dash · T / RB tag")
open(f,'w').write(src); print("patch_wallatk ok")
