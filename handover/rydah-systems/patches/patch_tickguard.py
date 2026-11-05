import os as _os; _SRC=_os.environ.get('SR_SRC','/workspace/v3build').rstrip('/')+'/'; _OUT=_os.environ.get('SR_HTML','/workspace/v3build/sky-rydahs-v3-ikki.html')  # Systems 10:25: SR_HTML / SR_SRC (default = old paths)
# patch_tickguard.py (Rydah Systems) — studio safeguard: one bad system tick can't kill the game loop.
# Build order: run EARLY in build_ikki.sh, right after patch_ikki.py (which creates the html). Idempotent (marker blocks are replaced).
#   tickguard.js      -> first thing in <head>: defines window.SR_GUARD / window.SR_ERRORS before any game script runs.
#   tickguard_late.js -> just before the last </body>: wraps the known per-frame globals + every `animated` tick (and later pushes)
#                        + the setAnimationLoop callback. Patches that run later and add scripts after it are still covered:
#                        the wrap pass re-runs at window 'load' and on the first 4 frames (late definers / lazy pushes).
# Usage: python3 patch_tickguard.py [html]   (default sky-rydahs-v3-ikki.html)
import sys, re
D=_SRC; f=sys.argv[1] if len(sys.argv)>1 else _OUT
src=open(f).read(); A=open(D+"tickguard.js").read(); B=open(D+"tickguard_late.js").read()
def block(tag,js): return f"<script>/*<{tag}>*/\n{js}\n/*</{tag}>*/</script>"
for tag in ("SR_TICKGUARD_HEAD","SR_TICKGUARD_LATE"):
    src=re.sub(r"<script>/\*<"+tag+r">\*/.*?/\*</"+tag+r">\*/</script>\n?","",src,flags=re.S)
m=re.search(r"<head[^>]*>",src); assert m,"no <head>"
src=src[:m.end()]+"\n"+block("SR_TICKGUARD_HEAD",A)+"\n"+src[m.end():]
k=src.rfind("</body>"); assert k>=0,"no </body>"
src=src[:k]+block("SR_TICKGUARD_LATE",B)+"\n"+src[k:]
open(f,"w").write(src); print("patch_tickguard: guard inlined (head + late)",f)
