#!/bin/bash
# Palma Builder .testlock helper (Ani steering 2026-11-05 11:33): never overwrite a live pid.
# Usage:
#   source palma_testlock.sh
#   tl_acquire "ani garage hero" 20   # waits; writes lock with $$
#   ... browser work ...
#   tl_release                         # removes only if lock holds our pid
set -e
TL=/workspace/v3build/.testlock
tl_pid(){ [ -f "$TL" ] || { echo ""; return; }; grep -oP 'pid \K[0-9]+' "$TL" 2>/dev/null || echo ""; }
tl_alive(){ local p="$1"; [ -n "$p" ] && kill -0 "$p" 2>/dev/null; }
tl_acquire(){
  local what="${1:-palma}"; local maxm="${2:-20}"; local p
  while true; do
    p=$(tl_pid)
    if [ -z "$p" ] || ! tl_alive "$p"; then
      # atomic create: noclobber fails if someone raced us
      set -o noclobber
      if echo "Palma Builder: $what, max ${maxm} min, $(date +%H:%M) (pid $$)" > "$TL" 2>/dev/null; then
        set +o noclobber
        # re-read: we own it
        p=$(tl_pid); [ "$p" = "$$" ] && { echo "tl_acquire: got lock pid=$$"; return 0; }
        # lost race
        rm -f "$TL" 2>/dev/null || true
      fi
      set +o noclobber
    else
      echo "tl_acquire: waiting on live pid $p ($(cat "$TL"))"
    fi
    sleep 15
  done
}
tl_release(){
  local p; p=$(tl_pid)
  if [ "$p" = "$$" ]; then rm -f "$TL"; echo "tl_release: released"; return 0; fi
  echo "tl_release: not ours (pid=$p mine=$$) — left untouched"; return 1
}
