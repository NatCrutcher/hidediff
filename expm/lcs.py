#!/usr/bin/python3

import sys
import argparse
import math
import numpy as np


def lcs(x: str, y: str) -> np.array:
    x_len = len(x)
    y_len = len(y)
    lxy = np.zeros((x_len, y_len))

    # Find the value diagonally up-left by one position.
    def diag(ix: int, iy: int):
        return lxy[ix-1,iy-1] if (ix > 0 and iy > 0) else 0

    # Find the value left by one position.
    def left(ix: int, iy: int):
        return lxy[ix-1,iy] if (ix > 0) else 0

    # Find the value up by one position.
    def up(ix: int, iy: int):
        return lxy[ix,iy-1] if (iy > 0) else 0

    for ix in range(x_len):
        for iy in range(y_len):
            if x[ix] == y[iy]:
                lxy[ix,iy] = diag(ix, iy) + 1
            else:
                lxy[ix,iy] = max(left(ix, iy), up(ix, iy))

    return lxy


def print_lcs_matrix(x: str, y: str, lxy: np.array):
    """Print the LCS matrix with x chars as row labels and y chars as column labels."""
    w = max(len(str(int(lxy.max()))), 1) + 1  # column width

    # Header: padding for row label, then each y char
    header = "    " + "".join(c.rjust(w) for c in y)
    print(header)
    print("    " + "-" * (w * len(y)))

    for ix, ch in enumerate(x):
        row_vals = "".join(str(int(lxy[ix, iy])).rjust(w) for iy in range(len(y)))
        print(f" {ch} |{row_vals}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Perform LCS diff of two strings, comparing characters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="",
    )
    parser.add_argument("strs", nargs=2, help="Two strings to compare")
    args = parser.parse_args()
    x, y = args.strs[0], args.strs[1]
    print("x:", x)
    print("y:", y)
    print()
    lxy = lcs(x, y)
    print_lcs_matrix(x, y, lxy)
    print()
    print("LCS length:", int(lxy[-1, -1]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
