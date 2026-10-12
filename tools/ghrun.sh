#!/bin/bash
# Runs the headless Ghidra launcher on the Amok project.
# usage: [PROG=XLEMLAN1.BIN] ghrun.sh <logfile> [args...]
# args go after "-process $PROG -noanalysis -scriptPath ..."; PROG defaults to AMOKWIN95.exe
log="$1"; shift
prog="${PROG:-AMOKWIN95.exe}"
cd /c/Users/john/Documents/Amok/ghidra || exit 1
cmd //c "C:\\Users\\john\\Documents\\Tools\\ghidra-headless.bat C:\\Users\\john\\Documents\\Amok\\ghidra Amok -process $prog -noanalysis -scriptPath C:\\Users\\john\\Documents\\Amok\\ghidra\\scripts $*" > "$log" 2>&1
tail -3 "$log"
