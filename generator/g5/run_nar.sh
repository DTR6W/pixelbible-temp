#!/bin/bash
cd /tmp/claude-0/-home-claude/7ca856ee-15e1-53b8-8651-f5ddfa4e969a/scratchpad/g5
python3 build5.py genesis nar mix > out_genesis_nar/mix.log 2>&1
python3 build5.py genesis nar render 0/2 > out_genesis_nar/r0.log 2>&1 &
python3 build5.py genesis nar render 1/2 > out_genesis_nar/r1.log 2>&1 &
wait
python3 build5.py genesis nar concat 0/2 > out_genesis_nar/concat.log 2>&1
echo ALLDONE >> out_genesis_nar/concat.log
