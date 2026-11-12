#!/bin/bash
cd /tmp/claude-0/-home-claude/7ca856ee-15e1-53b8-8651-f5ddfa4e969a/scratchpad/g5
D=out_genesis_drama
python3 build5.py genesis drama tts > $D/tts.log 2>&1
python3 build5.py genesis drama mix > $D/mix.log 2>&1
python3 build5.py genesis drama render 0/2 > $D/r0.log 2>&1 &
python3 build5.py genesis drama render 1/2 > $D/r1.log 2>&1 &
wait
python3 build5.py genesis drama concat 0/2 > $D/concat.log 2>&1
echo ALLDONE >> $D/concat.log
