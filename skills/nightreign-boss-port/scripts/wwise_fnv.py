#!/usr/bin/env python3
# Part of Nightreign Boss Skills - CC BY-NC-SA 4.0, see LICENSE and NOTICE (non-commercial, attribution required).
"""Wwise short ids (FNV-1 32-bit of the lower-case name), as used by Nightreign banks.

Use it to name TAE 129 / FXR / Bullet sound events (play_c<id>, play_s<id>, stop_...), music state names and bank names,
and to check that an id you put into a TAE, FXR or EMEVD resolves to an event in a bank the caller loads.

  python wwise_fnv.py play_c123400100 stop_c123400100 heatup1
  python wwise_fnv.py --event c 123400100          # prints play_ / stop_ names and their ids
  python wwise_fnv.py --file names.txt             # one name per line

No dependencies. Prints: name <TAB> decimal id <TAB> hex id.
"""
import argparse
import sys

FNV_OFFSET = 2166136261
FNV_PRIME = 16777619


def fnv1_32(name: str) -> int:
    """Wwise ShortID: FNV-1 (multiply, then xor) over the lower-case UTF-8 bytes."""
    h = FNV_OFFSET
    for b in name.lower().encode("utf-8"):
        h = (h * FNV_PRIME) & 0xFFFFFFFF
        h ^= b
    return h


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("names", nargs="*", help="names to hash")
    ap.add_argument("--event", nargs=2, metavar=("KIND", "ID"),
                    help="KIND = c | s | v ; prints play_/stop_ event names for that sound id")
    ap.add_argument("--file", help="text file with one name per line")
    a = ap.parse_args(argv)

    names = list(a.names)
    if a.event:
        kind, sid = a.event
        if kind not in ("c", "s", "v"):
            ap.error("KIND must be c, s or v")
        names += [f"play_{kind}{sid}", f"stop_{kind}{sid}"]
    if a.file:
        with open(a.file, encoding="utf-8") as f:
            names += [line.strip() for line in f if line.strip()]
    if not names:
        ap.print_help()
        return 1
    for n in names:
        h = fnv1_32(n)
        print(f"{n}\t{h}\t0x{h:08X}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
