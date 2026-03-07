#!/usr/bin/python3

import sys
import argparse
import math

def comp_pos(a: str, b: str, a_offset: int) -> tuple[list[int], list[str]]:
    a_len = len(a)
    b_len = len(b)
    max_len = max(a_len, b_len)
    ab_center_shift = (a_len - b_len) / 2
    comps = []    # Comparison values
    a_shift = []
    for ib in range(b_len):
        ia = ib + a_offset
        if ia < 0 or ia >= a_len:
            a_shift.append("_")
            comps.append(0.0)
        else:
            a_shift.append(a[ia])
            # Compute a scaled offset weight where more aligned matches get a higher weight
            offset = 4.0 * math.log2(1 + max_len - abs(ia - ib - ab_center_shift))
            comp = offset if a[ia] == b[ib] else 0.0
            comps.append(comp)
    return comps, a_shift


def slide(a: str, b: str):
    """Slide the two strings across each other looking for matching characters."""
    a_len = len(a)
    b_len = len(b)
    # Comparison positions. This is all the ways of aligning 'a' and 'b' with at least one overlapping char.
    positions = a_len + b_len - 1
    for ip in range(positions):
        a_offset = a_len - ip - 1   # Start with one char overlap
        comps, asub = comp_pos(a, b, a_offset)
        comp_str = ' '.join(f"{v:2.0f}" for v in comps)
        print(comp_str, ' ', ''.join(asub))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Slide two strings across each other, comparing characters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="",
    )
    parser.add_argument("strs", nargs=2, help="Two strings to compare")
    args = parser.parse_args()
    #print("1: ", args.strs[0])
    #print("2: ", args.strs[1])
    slide(args.strs[0], args.strs[1])
    return 0


if __name__ == "__main__":
    sys.exit(main())
