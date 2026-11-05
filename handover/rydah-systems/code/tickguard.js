// ===== TICKGUARD (Rydah Systems, patch_tickguard.py) =====
// One bad system tick must never kill the game loop (2026-10-29: crewhouse_kit 'kitT0 is not defined' froze the game for good).
//  * window.SR_GUARD(name, fn, opts) -> guarded fn. On the first throw: console.error('[SR] <name> tick disabled:', err) ONCE,
//    push {system,message,stack,frame,t} to window.SR_ERRORS, and the fn becomes a no-op (opts.keep=true: keep calling, still logged once).
//  * Runtime wrapping (no edits to other bots' files): every fn in `animated` (incl. later pushes, e.g. kit/crewhouse ticks) and the
//    known per-frame globals below are swapped for guarded versions at load AND again on the first frames (catches late definers).
//  * Last resort: renderer.setAnimationLoop callbacks are wrapped, so if the whole frame body throws the loop still runs next frame;
//    each distinct frame error is recorded + console.error'd once. Never silent. Cost: one try/catch per call, 0 draws.
(function(){ if(window.SR_GUARD) return;
  const E=window.SR_ERRORS=window.SR_ERRORS||[]; const seen=new Set();
  function rec(system,err,disabled){ const m=String(err&&err.message||err), key=system+"|"+m; if(seen.has(key)) return; seen.add(key);
    E.push({system,message:m,stack:String(err&&err.stack||""),frame:typeof frame!=="undefined"?frame:-1,t:typeof clock!=="undefined"?clock:performance.now()/1000,disabled:!!disabled});
    console.error("[SR] "+system+(disabled?" tick disabled:":" frame error (loop kept alive):"),err); }
  function SR_GUARD(name,fn,opts){ if(typeof fn!=="function"||fn.__srg) return fn; const keep=!!(opts&&opts.keep); let dead=false;
    const g=function(){ if(dead) return undefined; try{ return fn.apply(this,arguments); }catch(e){ if(!keep) dead=true; rec(name,e,!keep); return undefined; } };
    g.__srg=name; g.__srInner=fn; g.__srDead=()=>dead; return g; }
  window.SR_GUARD=SR_GUARD; window.__srRecord=rec; })();
