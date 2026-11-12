#!/bin/bash
cd /tmp/claude-0/-home-claude/7ca856ee-15e1-53b8-8651-f5ddfa4e969a/scratchpad/g5
for M in nar drama; do
  D=out_abraham_$M; mkdir -p $D
  python3 build5.py abraham $M tts > $D/tts.log 2>&1 || exit 1
  python3 build5.py abraham $M mix > $D/mix.log 2>&1 || exit 1
  python3 build5.py abraham $M render 0/2 > $D/r0.log 2>&1 &
  python3 build5.py abraham $M render 1/2 > $D/r1.log 2>&1 &
  wait
  python3 build5.py abraham $M concat 0/2 > $D/concat.log 2>&1 || exit 1
  echo "$M DONE"
done
