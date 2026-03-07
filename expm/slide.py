#!/usr/bin/python3

import sys
import argparse

def comp_pos(a: str, b: str, a_offset: int) -> tuple[list[int], list[str]]:
    a_len = len(a)
    b_len = len(b)
    max_len = max(a_len, b_len)
    b_offset = -(max_len - b_len) // 2   # Integer division
    print(f"a_offset={a_offset}, b_offset={b_offset}, max_len={max_len}")
    comps = []    # Comparison values
    a_shift = []
    for i in range(max_len):
        ia = i + a_offset
        ib = i + b_offset
        if ia < 0 or ia >= a_len or ib < 0 or ib >= b_len:
            a_shift.append("_")
            comps.append(0)
        else:
            a_shift.append(a[ia])
            comp = 1 if a[ia] == b[ib] else 0
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
        comp_str = ''.join(str(d) for d in comps)
        print(comp_str, ' ', ''.join(asub))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Slide two strings across each other, comparing characters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="",
    )
    parser.add_argument("strs", nargs=2, help="Two strings to compare")
    args = parser.parse_args()
    print("1: ", args.strs[0])
    print("2: ", args.strs[1])
    slide(args.strs[0], args.strs[1])
    return 0


if __name__ == "__main__":
    sys.exit(main())
