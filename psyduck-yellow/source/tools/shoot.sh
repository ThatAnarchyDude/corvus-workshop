#!/bin/bash
# usage: shoot.sh <rom> <outdir> <shotname> [extra json actions...]  (continue from the 0040 fixture save, 4 A presses, then B to close any menu)
ROM=$1; O=$2; N=$3; shift 3
mkdir -p $O; cp -n build/0040-release-v1/native-pickup-refreshed3/*.dsv $O/$(basename ${ROM%.nds}).dsv 2>/dev/null
A='{"frames":30,"buttons":[8]}'
EXTRA=""; for a in "$@"; do EXTRA="$EXTRA,$a"; done
.venv/bin/python tools/emulator_smoke.py $ROM '[{"frames":900},'"$A"',{"frames":60},'"$A"',{"frames":60},'"$A"',{"frames":120},'"$A"',{"frames":700},{"frames":20,"buttons":[0]},{"frames":60}'"$EXTRA"',{"frames":10,"screenshot":"'$N'.png"}]' --fresh --output-dir $O 2>&1 | tail -0; rm -f $O/state.bin $O/ram.bin
