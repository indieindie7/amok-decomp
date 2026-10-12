# AMOK (Lemon / Scavenger, 1996) reverse-engineering notes and symbols

Hand-named function maps, Ghidra scripts, tools and working notes for the mech shooter **AMOK**
(PC DOS and Win95 builds, Watcom x86; Sega Saturn build, SH-2). Same method and scripts as
[scorcher-decomp](https://github.com/indieindie7/scorcher-decomp). Non-commercial, done for study and preservation.

## What is here

| Path | Content |
|---|---|
| `NOTES.md` | the full working log: disc layout, file formats, engine structure, every naming pass (DOS passes 1-99, Win95 W0-W15, Saturn S1-S17) |
| `GOTCHAS.md` | compiler and tool quirks met on the way |
| `ghidra/hand_amokdos.txt` | 1628 hand lines for the DOS build (`AMOKDOS.EXE` flattened LE image, 1768 functions, all named) |
| `ghidra/hand_AMOKWIN95.txt` | 546 hand lines for the Win95 build (`AMOKWIN95.EXE`, 1030 functions, all named) |
| `ghidra/hand_XLEMLAN1.txt` | 634 hand lines for the Saturn game program `XLEMLAN1.BIN` (634 functions, all named) |
| `ghidra/globals_*.txt` | global variable labels (`0x<addr> <name>`, apply with `ApplyGlobals.java`): DOS 1118, Win95 841, Saturn 358 RAM variables + 1961 `p_<name>` literal-pool slots; names with an address suffix are best guesses |
| `ghidra/structs_amok.txt`, `ghidra/structtypes_*.txt` | entity / fx / player / type-row struct layouts (define with `scripts/DefineStructs.java <spec> /Amok`) and the globals typed with them (apply with `ApplyGlobals.java`) |
| `ghidra/funcinfo_*.tsv` | per-function export: address, name, size, callees, string references |
| `ghidra/xalign_*.txt`, `sig_*.txt`, `bogus_deleted_amokdos.txt` | cross-build alignment, Watcom runtime signatures, false functions removed |
| `ghidra/x86watcom.cspec` | compiler spec for the Watcom register calling convention |
| `ghidra/scripts/*.java` | headless Ghidra scripts: find function starts, repair bodies, apply names, export, dump decompilation |
| `tools/*.py`, `tools/ghrun.sh` | cross-build aligner, twin mappers, pointer-table mapper, headless runner |

Line format of the hand files: `0x<addr> func <name> hand <comment>`. The comment describes the body,
callers, data addresses and strings as read by hand. Names marked `provisional` were given from the
body alone, without a confirmed twin in another build. `AIL_wrap_` / `AIL_API_` are Miles Sound System
wrappers, `_asm` are register-only assembly helpers.

## What is NOT here

No game files. No executables, disc images, `XLEMLAN1.BIN`, level data, graphics, sound, or the
Ghidra project database (which embeds the binaries). You need your own copy of the game.

## Reproducing the Ghidra project

1. Ghidra 12.1.4 (headless). Create a project named `Amok`.
2. Import `XLEMLAN1.BIN` (SH-2, base 0x06004000), `AMOKWIN95.EXE` (PE) and the flattened DOS image
   made from `AMOKDOS.EXE` (DOS/4GW LE) with the Scorcher `leflatten.py`. `NOTES.md` has the exact
   steps, the Watcom cspec install and the function-start repair order.
3. Run `ghidra/scripts/ApplyNames.java` with the matching `hand_<program>.txt` in `hand` mode, then
   `ExportFuncInfo.java` to regenerate the tsv.

## Rights and takedown

AMOK is copyright its rights holders (Lemon / Scavenger, Inc., 1996; the publisher went bankrupt
in 1998 and the current holder is unknown). This repository contains only work made by reading the
shipped program: symbol names, comments, notes, scripts and tools. The symbol names, comments and
notes are offered without any licence claim of our own over the game. The scripts and tools
(`ghidra/scripts`, `tools`, `x86watcom.cspec`) are MIT licensed (see `LICENSE`).

**If you hold the rights and want this removed, file a notice through GitHub's DMCA form.
It will not be contested.** No need to contact the author first.
