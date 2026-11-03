#!/bin/bash
# TEST ONLY (companion of ds_repl.py): usage: ds_send.sh <workdir> '<json list of steps>'   -> waits for out.json and prints it
W=$1; rm -f $W/out.json
echo "$2" > $W/cmd.tmp && mv $W/cmd.tmp $W/cmd.json
for i in $(seq 1 600); do [ -f $W/out.json ] && { cat $W/out.json; echo; exit 0; }; sleep 0.5; done
echo TIMEOUT; exit 1
