#!/usr/bin/python3

import sys
import argparse
import math
import numpy as np

def slide(a: str, b: str) -> np.array:
    """Slide the two strings across each other looking for matching characters."""
    a_len = len(a)
    b_len = len(b)
    ab_center_shift = (a_len - b_len) / 2
    max_len = max(a_len, b_len)
    # Comparison positions. This is all the ways of aligning 'a' and 'b' with at least one overlapping char.
    positions = a_len + b_len - 1
    comps = np.zeros((positions, b_len))
    for ip in range(positions):
        a_offset = a_len - ip - 1   # Start with one char overlap

        for ib in range(b_len):
            ia = ib + a_offset
            if ia < 0 or ia >= a_len:
                #a_shift.append("_")
                comps[ip,ib] = 0.0
            else:
                #a_shift.append(a[ia])
                # Compute a scaled offset weight where more aligned matches get a higher weight
                offset = 4.0 * math.log2(1 + max_len - abs(ia - ib - ab_center_shift))
                comps[ip,ib] = offset if a[ia] == b[ib] else 0.0

    return comps


def print_comp_matrix(a: str, b: str, comps: np.array):
    """Print the comp matrix with b chars as column labels."""
    w = max(len(str(int(comps.max()))), 1) + 1  # column width

    # Header: padding for row label, then each b char
    header = " " + "  ".join(b)
    print(header)
    print("-" * (3 * len(b)))

    rows, cols = comps.shape
    for ip in range(rows):
        row_vals = " ".join(f"{comps[ip,ib]:2.0f}" for ib in range(cols))
        print(f"{row_vals}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Slide two strings across each other, comparing characters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="",
    )
    parser.add_argument("strs", nargs=2, help="Two strings to compare")
    args = parser.parse_args()
    a = args.strs[0]
    b = args.strs[1]
    #print("a: ", a)
    #print("b: ", b)
    comps = slide(a, b)
    print_comp_matrix(a, b, comps)
    return 0


if __name__ == "__main__":
    sys.exit(main())
