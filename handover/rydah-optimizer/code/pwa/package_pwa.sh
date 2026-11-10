#!/usr/bin/env bash
# Repeatable PWA packager for Sky Rydahs v3. Consumes the build output only; never edits sources.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="${SRC:-/workspace/v3build/sky-rydahs-v3-ikki.html}"
CHARS="${CHARS:-/workspace/skyrydahs-characters}"
OUT="${OUT:-$HERE/site}"
TV=0.128.0
# PUBLIC=1 -> public package: leave out WITHHELD_CHAR (unlicensed placeholder rider) assets listed in public-exclude.txt
# (one path glob per line, relative to skyrydahs-characters/). Local default (PUBLIC unset/0) keeps everything.
PUBLIC="${PUBLIC:-0}"; EXCL="${EXCL:-$HERE/public-exclude.txt}"
rm -rf "$OUT"; mkdir -p "$OUT/icons" "$OUT/vendor/three/examples/js"
cp "$SRC" "$OUT/index.html"
H="$OUT/index.html"

# 1) vendor three.js r128 + example scripts for offline use, rewrite CDN URLs
VC="$HERE/.vendor-cache"; mkdir -p "$VC"
get(){ [ -s "$VC/$2" ] || { mkdir -p "$(dirname "$VC/$2")"; curl -fsSL "$1" -o "$VC/$2"; }; mkdir -p "$(dirname "$OUT/vendor/three/$2")"; cp "$VC/$2" "$OUT/vendor/three/$2"; }
get https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js three.min.js
for f in $(grep -oE '"(loaders|utils|postprocessing|shaders|libs|controls|exporters|math|objects|modifiers)/[A-Za-z_]+\.js"' "$H" | tr -d '"' | sort -u; grep -oE 'three(@|/)[^/"]*/examples/js/[A-Za-z_/]+\.js' "$H" | sed -E 's#.*examples/js/##' ); do
  get "https://cdn.jsdelivr.net/npm/three@$TV/examples/js/$f" "examples/js/$f"
done
# meshopt decoder (patch_wardrobe.py adds "libs/meshopt_decoder.js" to initRiders' jsdelivr examples/js list)
grep -q '"libs/meshopt_decoder.js"' "$H" && get "https://cdn.jsdelivr.net/npm/three@$TV/examples/js/libs/meshopt_decoder.js" "examples/js/libs/meshopt_decoder.js"
# Rydah Optimizer: prefer exact r128 copies under /workspace/v3build/vendor/three when present (sha-matched to jsdelivr 0.128.0)
V3V="${V3B:-/workspace/v3build}/vendor/three"
if [ -d "$V3V/examples/js" ]; then
  for f in examples/js/loaders/GLTFLoader.js examples/js/utils/BufferGeometryUtils.js examples/js/libs/meshopt_decoder.js; do
    if [ -s "$V3V/$f" ]; then mkdir -p "$(dirname "$OUT/vendor/three/$f")"; cp "$V3V/$f" "$OUT/vendor/three/$f"; mkdir -p "$(dirname "$VC/$f")"; cp "$V3V/$f" "$VC/$f"; fi
  done
fi
# rewrite ANY spelling of a three CDN base (cdnjs/jsdelivr/unpkg, http(s) or protocol-relative, any version string: 0.128.0, $TV, r128,
# @latest...) to the vendored copy; we always ship pinned r128/0.128.0, so a different version in the source is forced to r128.
sed -i -E -e 's#(https?:)?//cdnjs\.cloudflare\.com/ajax/libs/three\.js/[^/"'"'"']+/three(\.min)?\.js#vendor/three/three.min.js#g' \
       -e 's#(https?:)?//(cdn\.jsdelivr\.net/npm|unpkg\.com)/three(@[^/"'"'"']*)?/build/three(\.min)?\.js#vendor/three/three.min.js#g' \
       -e 's#(https?:)?//(cdn\.jsdelivr\.net/npm|unpkg\.com)/three(@[^/"'"'"']*)?/examples/js/#vendor/three/examples/js/#g' \
       -e 's#(https?:)?//cdnjs\.cloudflare\.com/ajax/libs/three\.js/[^/"'"'"']+/examples/js/#vendor/three/examples/js/#g' "$H"
# every examples/js path now referenced locally must exist in vendor/ (fetch any that slipped through the scans above)
for f in $(grep -oE 'vendor/three/examples/js/[A-Za-z_/]+\.js' "$H" | sed 's#vendor/three/##' | sort -u); do [ -f "$OUT/vendor/three/$f" ] || get "https://cdn.jsdelivr.net/npm/three@$TV/$f" "$f"; done
sed -i -e 's#/workspace/skyrydahs-characters/#skyrydahs-characters/#g' -e 's#/workspace/v3build/##g' "$H"

# 2) copy GLB assets the game loads (relative to CHAR_BASE="skyrydahs-characters/")
excluded(){ [ "$PUBLIC" = 1 ] && [ -f "$EXCL" ] || return 1; while read -r g; do case "$g" in ''|'#'*) continue;; esac; case "$1" in $g) return 0;; esac; done < "$EXCL"; return 1; }
cpa(){ excluded "$1" && { echo "PUBLIC: excluded $1" >&2; return 0; }; [ -f "$CHARS/$1" ] || { echo "WARN missing asset: $1" >&2; return 0; }; mkdir -p "$OUT/skyrydahs-characters/$(dirname "$1")"; cp "$CHARS/$1" "$OUT/skyrydahs-characters/$1"; }
cpa meshy/ikki-meshy-skate.glb   # fallback (?ikki=orig)
cpa meshy/ikki-meshy-skate.quest-draco.glb   # default Ikki (Draco, Quest textures)
cpa wardrobe/riders/caali-g.nonormal.glb   # default Caali G (flat normal map stripped, step 4.2B); caali-g.glb below stays for ?texfull=1
cpa wardrobe/riders/caali-g.glb   # Caali G (meshopt, ?player=caali); also covered by the wardrobe sweep below
cpa anika/anika-rider.glb   # Anika (Code : E), SR_ROSTER.anika.url; Forge 2026-10-30 (Oliver approved 08:28 CDT)
cpa anika/anika-rider.opt-ktx2.glb   # Anika Optimizer Draco+KTX2 tier (for a future ?ktx2=1 map entry)
[ -f "$CHARS/anika/anika-rider.draco-webp.glb" ] && cpa anika/anika-rider.draco-webp.glb   # Anika default/hd tier (Rigger tiers); precached below
# Simca SOLO rider + NPC, all public tiers (mirror Anika explicit assets; no backups).
for f in simca/simca-rider.glb simca/simca-rider.quest.glb simca/simca-rider.quest-ktx2.glb simca/simca-npc.glb simca/simca-npc.quest.glb simca/simca-npc.quest-ktx2.glb; do cpa "$f"; done
[ -f "$CHARS/WITHHELD_CHAR/WITHHELD_CHAR-rider.glb" ] && cpa WITHHELD_CHAR/WITHHELD_CHAR-rider.glb   # WITHHELD_CHAR wardrobe rider (URL built from CHAR_BASE, not caught by the literal-ref sweep)
[ -f "$CHARS/WITHHELD_CHAR/WITHHELD_CHAR-npc.glb" ] && cpa WITHHELD_CHAR/WITHHELD_CHAR-npc.glb   # WITHHELD_CHAR NPC (local only; PUBLIC=1 drops it via public-exclude + gate)
# Draco decoder (three r128 examples/js, bundled by v3build/patch_draco.py; page uses setDecoderPath("libs/draco/"))
DRACO_SRC="${DRACO_SRC:-/workspace/v3build/libs/draco}"; mkdir -p "$OUT/libs/draco"
for f in DRACOLoader.js draco_decoder.js draco_decoder.wasm draco_wasm_wrapper.js; do cp "$DRACO_SRC/$f" "$OUT/libs/draco/$f"; done
# KTX2 (?ktx2=1): asphalt KTX2 textures (asphalt.js) + Basis transcoder / KTX2 loader libs (patch_draco.py.ktx2-candidate). Guarded: missing dirs are skipped.
V3B="${V3B:-/workspace/v3build}"
if ls "$V3B"/assets/asphalt/*.ktx2 >/dev/null 2>&1; then mkdir -p "$OUT/assets/asphalt" && cp "$V3B"/assets/asphalt/*.ktx2 "$OUT/assets/asphalt/"; else echo "WARN no asphalt ktx2 in $V3B/assets/asphalt" >&2; fi
for d in basis ktx2; do if [ -d "$V3B/libs/$d" ]; then mkdir -p "$OUT/libs/$d" && cp -r "$V3B/libs/$d/." "$OUT/libs/$d/"; else echo "WARN no $V3B/libs/$d" >&2; fi; done
# KTX2 step 4.4/4.5 (?ktx2=1 only; Rydah Optimizer): character *.s4-ktx2.glb / caali-g.nonormal.ktx2.glb (SR_KTX2.map targets) + world KTX2 copies. Guarded.
# WITHHELD_CHAR KTX2 files go through cpa, so PUBLIC=1 drops them via public-exclude (WITHHELD_CHAR/* and *WITHHELD_CHAR*) and the hard gate still sees 0 WITHHELD_CHAR.
for f in meshy/ikki-meshy-skate.s4-ktx2.glb wardrobe/riders/caali-g.nonormal.ktx2.glb WITHHELD_CHAR/WITHHELD_CHAR-npc.s4-ktx2.glb WITHHELD_CHAR/WITHHELD_CHAR-rider.s4-ktx2.glb \
         anubis/anubis-rider.s4-ktx2.glb behemoth/behemoth-rider.s4-ktx2.glb genesis/genesis-rider.s4-ktx2.glb kogarasumaru/kogarasumaru-rider.s4-ktx2.glb \
         sleeping-forest/sleeping-forest-rider.s4-ktx2.glb static-angels/static-angels-rider.s4-ktx2.glb tool-toul-to/tool-toul-to-rider.s4-ktx2.glb; do [ -f "$CHARS/$f" ] && cpa "$f"; done
if ls "$V3B"/assets/world_ktx2/*.ktx2 >/dev/null 2>&1; then mkdir -p "$OUT/assets/world_ktx2" && cp "$V3B"/assets/world_ktx2/*.ktx2 "$OUT/assets/world_ktx2/"; fi
for d in $(grep -oE '\{dir:"[a-z-]+",file:"[a-z-]+"' "$H" | sed -E 's/.*dir:"([^"]+)",file:"([^"]+)"/\1:\2/'); do
  cpa "${d%%:*}/${d#*:}-rider.glb"; [ -f "$CHARS/${d%%:*}/${d#*:}-rider.quest.glb" ] && cpa "${d%%:*}/${d#*:}-rider.quest.glb"; cpa "${d%%:*}/${d#*:}-fp.glb"; done   # .quest = Draco NPC riders (patch_crew_quest.py; ?crew=orig fallback)
# wardrobe: all current slot items + riders + base body (skip v1 backups / .npy)
( cd "$CHARS" && find wardrobe -type f \( -name '*.glb' -o -name '*.json' -o -name '*.png' \) \
   ! -path '*/v1_items/*' ! -name '*-v1.glb' ! -name '*.quest*.glb' ! -name '*.bak*' ! -name '*.pre*' ! -name '*.rigged*' ! -path '*/staging/*' ) | while read -r f; do cpa "$f"; done
# any other literal skyrydahs-characters/... refs in html
for f in $(grep -oE 'skyrydahs-characters/[A-Za-z0-9_./-]+\.(glb|png|jpg|webp|json)' "$H" | sed 's#skyrydahs-characters/##' | sort -u); do cpa "$f"; done

# crew Meshy skate textures + Caali G patch (jackets.js builds these URLs from CHAR_BASE, so the literal sweep misses them)
for f in shared/at-skate/at-skate-meshy-1k.png shared/at-skate/at-skate-meshy-1k-normal.png shared/at-skate/at-skate-meshy-1k-mr.png wardrobe/skates/at-skate-meshy.glb wardrobe/skates/at-skate-meshy.merged.quest.glb shared/crew-logos/caali-g-patch-noshadow.png shared/crew-logos/caali-g-patch.png; do cpa "$f"; done
# v3build/assets (kit PBR jpgs, kit_logos, asphalt) referenced as relative "assets/..." URLs
[ -d /workspace/v3build/assets ] && mkdir -p "$OUT/assets" && cp -r /workspace/v3build/assets/. "$OUT/assets/"
# v3build/props/kit (crewhouse kit props: manifest.json + GLBs, no backups/previews)
mkdir -p "$OUT/props/kit" && ( cd /workspace/v3build/props/kit && for f in *.json *.glb; do case "$f" in *.bak*) ;; *) cp "$f" "$OUT/props/kit/";; esac; done )
# 3) icons, manifest, SW, .nojekyll
python3 "$HERE/tools/icons.py" "$OUT/icons"
cat > "$OUT/manifest.webmanifest" <<'J'
{"name":"Sky Rydah's","short_name":"Sky Rydahs","id":"./","start_url":"./","scope":"./",
 "display":"fullscreen","display_override":["fullscreen","standalone"],"orientation":"landscape",
 "theme_color":"#0a0a0c","background_color":"#0a0a0c","description":"Sky Rydah's — air-trek street racing prototype (v3)",
 "icons":[{"src":"icons/icon-192.png","sizes":"192x192","type":"image/png","purpose":"any"},
  {"src":"icons/icon-512.png","sizes":"512x512","type":"image/png","purpose":"any"},
  {"src":"icons/icon-maskable-192.png","sizes":"192x192","type":"image/png","purpose":"maskable"},
  {"src":"icons/icon-maskable-512.png","sizes":"512x512","type":"image/png","purpose":"maskable"}]}
J
touch "$OUT/.nojekyll"
VER="$(cd "$OUT" && find . -type f ! -name sw.js -print0 | sort -z | xargs -0 sha1sum | sha1sum | cut -c1-10)"
PRE="$(cd "$OUT" && { find . -type f ! -name sw.js ! -name .nojekyll ! -name '*.glb'; echo ./skyrydahs-characters/meshy/ikki-meshy-skate.quest-draco.glb
   # KTX2 assets/libs (explicit, ?ktx2=1)
   for f in $(find assets/asphalt libs/basis libs/ktx2 -type f 2>/dev/null); do echo "./$f"; done
   [ -f skyrydahs-characters/wardrobe/riders/caali-g.nonormal.glb ] && echo ./skyrydahs-characters/wardrobe/riders/caali-g.nonormal.glb   # default Caali G (step 4.2B)
   # default-path rider GLBs (Rydah Optimizer 2026-11-05): crew NPC *.quest.glb, caali-rider.glb, Anika draco-webp; guarded
   for f in skyrydahs-characters/*/*-rider.quest.glb skyrydahs-characters/caali/caali-rider.glb skyrydahs-characters/anika/anika-rider.draco-webp.glb; do [ -f "$f" ] && echo "./$f"; done
   # decoders (explicit, so they stay precached even if the generic file list changes)
   for f in libs/draco/DRACOLoader.js libs/draco/draco_wasm_wrapper.js libs/draco/draco_decoder.wasm libs/draco/draco_decoder.js vendor/three/three.min.js vendor/three/examples/js/libs/meshopt_decoder.js vendor/three/examples/js/loaders/GLTFLoader.js vendor/three/examples/js/utils/BufferGeometryUtils.js $(find vendor -type f -name '*.js'); do [ -f "$f" ] && echo "./$f"; done; } | sed 's#^\./#./#' | sort -u | sed 's/.*/  "&",/')"
cat > "$OUT/sw.js" <<S
// Sky Rydahs SW — generated by package_pwa.sh
const VERSION='sr-$VER';
const CORE=[
$PRE
];
self.addEventListener('install',e=>{e.waitUntil(caches.open(VERSION).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting()));});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k.startsWith('sr-')&&k!==VERSION).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});
self.addEventListener('fetch',e=>{
  const r=e.request; if(r.method!=='GET') return; const u=new URL(r.url); if(u.origin!==location.origin) return;
  const isDoc=r.mode==='navigate'||u.pathname.endsWith('/')||u.pathname.endsWith('/index.html');
  if(isDoc){ // network-first so updates arrive
    e.respondWith(fetch(r).then(res=>{const cp=res.clone(); caches.open(VERSION).then(c=>c.put(r,cp)); return res;})
      .catch(()=>caches.match(r,{ignoreSearch:true}).then(m=>m||caches.match('./index.html'))));
    return; }
  e.respondWith(caches.match(r,{ignoreSearch:true}).then(m=>m||fetch(r).then(res=>{ // cache-first (GLBs cached on first use)
    if(res.ok){const cp=res.clone(); caches.open(VERSION).then(c=>c.put(r,cp));} return res;})));
});
S

# 4) inject manifest link, SW registration, install button
python3 - "$H" <<'P'
import sys,re
p=sys.argv[1]; s=open(p,encoding='utf-8').read()
head='''<link rel="manifest" href="manifest.webmanifest"><meta name="theme-color" content="#0a0a0c">
<link rel="icon" href="icons/icon-192.png"><link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-capable" content="yes">
'''
body='''<button id="pwaInstall" style="display:none;position:fixed;right:12px;bottom:12px;z-index:99999;padding:8px 14px;font:bold 13px sans-serif;background:#FFD700;color:#000;border:2px solid #000;border-radius:6px;cursor:pointer">&#9889; Install app</button>
<script>
(function(){var b=document.getElementById('pwaInstall'),dp=null;
function sa(){return matchMedia('(display-mode: standalone)').matches||matchMedia('(display-mode: fullscreen)').matches||navigator.standalone;}
addEventListener('beforeinstallprompt',function(e){e.preventDefault();dp=e;if(!sa())b.style.display='block';});
b.onclick=function(){if(!dp)return;b.style.display='none';dp.prompt();dp.userChoice.finally(function(){dp=null;});};
addEventListener('appinstalled',function(){b.style.display='none';});
if('serviceWorker' in navigator)addEventListener('load',function(){navigator.serviceWorker.register('sw.js',{scope:'./'}).catch(function(e){console.warn('SW reg failed',e);});});})();
</script>
'''
if 'rel="manifest"' not in s:
  s=re.sub(r'(<head[^>]*>)',lambda m:m.group(1)+'\n'+head,s,count=1)
  i=s.rfind('</body>'); s=s[:i]+body+s[i:] if i>=0 else s+body
open(p,'w',encoding='utf-8').write(s)
P
grep -qE 'cdn\.jsdelivr|cdnjs|unpkg\.com|gstatic|googleapis' "$H" && echo "WARN: CDN refs remain" >&2 || true
# PUBLIC=1: strip the local-only WITHHELD_CHAR wiring from the PACKAGED index.html copy only (source build untouched), then
# report any WITHHELD_CHAR mention left anywhere in $OUT (should be none)
if [ "$PUBLIC" = 1 ]; then python3 - "$H" <<'AK'
import re,sys
p=sys.argv[1]; s=open(p,encoding='utf-8').read(); n0=len(re.findall('(?i)WITHHELD_CHAR',s))
s=re.sub(r'(?m)^[ \t]*//[^\n]*WITHHELD_CHAR[^\n]*\n','',s)                                   # comment lines
s=re.sub(r"\s*WITHHELD_CHAR:\{ name:'WITHHELD_CHAR'.*?defaults:\{[^}]*\} \}",'',s,flags=re.S)          # WARDROBE_RIDERS.WITHHELD_CHAR entry
s=re.sub(r"if\(PLAYER_MODE!=='WITHHELD_CHAR'.*?WITHHELD_CHAR npc failed: [^}]*\}",'',s,flags=re.S)        # WITHHELD_CHAR NPC spawn
s=s.replace('WITHHELD_CHARNpc','npcX2')
s=re.sub(r'\n?/\*SR_LOCAL_BEGIN\*/.*?/\*SR_LOCAL_END\*/\n?','\n',s,flags=re.S)                      # local-demo-only rider block (ikki_skate/WITHHELD_CHAR_local.js via patch_ikki_skate.py)
def drop_prop(s,pat):                                                                # remove one object property `WITHHELD_CHAR: {...}` by brace matching (not a blind line delete)
  m=re.search(pat,s)
  if not m: return s
  i=m.start(); j=s.index('{',m.end()-1); d=0
  for k in range(j,len(s)):
    d+= s[k]=='{'; d-= s[k]=='}'
    if d==0: break
  k+=1
  t=re.match(r"[ \t]*,?[ \t]*(//[^\n]*)?",s[k:]); k+=t.end()                          # trailing comma + same-line comment
  ls=s.rfind('\n',0,i)+1
  if s[ls:i].strip()=='' and s[k:k+1]=='\n': i=ls; k+=1                                 # whole line(s) were the entry
  return s[:i]+s[k:]
s=drop_prop(s,r"(?m)^[ \t]*WITHHELD_CHAR:\s*\{(?=\s*stance)")                                 # RIDER_FEEL pose-table entry (incl. WITHHELD_CHAR comment)
s=re.sub(r"\|WITHHELD_CHAR(?=[|/])",'',s)                                                       # CHAR_RE alternation                                                        # leftover guarded update block (never set)
open(p,'w',encoding='utf-8').write(s); print("PUBLIC: WITHHELD_CHAR refs in index.html",n0,"->",len(re.findall('(?i)WITHHELD_CHAR',s)))
AK
fi
# PUBLIC=1 HARD GATE: zero case-insensitive 'WITHHELD_CHAR' in file names/paths or contents anywhere in $OUT, else fail
if [ "$PUBLIC" = 1 ]; then BAD=$( { grep -ril WITHHELD_CHAR "$OUT" || true; find "$OUT" -iname '*WITHHELD_CHAR*' || true; } | sort -u); if [ -n "$BAD" ]; then echo "PUBLIC GATE FAIL: WITHHELD_CHAR found in:" >&2; echo "$BAD" >&2; grep -rnoi '.\{0,60\}WITHHELD_CHAR.\{0,60\}' "$OUT" >&2 || true; exit 3; fi; echo "PUBLIC GATE OK: 0 WITHHELD_CHAR hits in $OUT" >&2; fi
# PUBLIC=1: report remaining WITHHELD_CHAR mentions so they can be reviewed/gated in the source build
if [ "$PUBLIC" = 1 ]; then n=$( (grep -rli WITHHELD_CHAR "$OUT" || true) | wc -l); echo "PUBLIC: files mentioning WITHHELD_CHAR in $OUT: $n" >&2; grep -rnoi '.\{0,40\}WITHHELD_CHAR.\{0,40\}' "$OUT" --include=*.html --include=*.js --include=*.json >&2 || true; fi
grep -q '/workspace/' "$H" && echo "WARN: /workspace paths remain" >&2 || true

# 5) size report
echo "== size report =="; du -sh "$OUT"
( cd "$OUT" && find . -type f -printf '%s\t%p\n' | sort -rn | awk -F'\t' '{f=$1>=100*1048576?"  !! >100MB (GitHub limit)":($1>=25*1048576?"  ! Quest-heavy":($1>=8*1048576?"  (large)":"")); printf "%9.2f MB  %s%s\n",$1/1048576,$2,f}' )
