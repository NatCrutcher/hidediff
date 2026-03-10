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
    a_shifts = []
    for ip in range(positions):
        a_offset = a_len - ip - 1   # Start with one char overlap

        a_shift_row = []
        for ib in range(b_len):
            ia = ib + a_offset
            if ia < 0 or ia >= a_len:
                a_shift_row.append("_")
                comps[ip,ib] = 0.0
            else:
                a_shift_row.append(a[ia])
                # Compute a scaled offset weight where more aligned matches get a higher weight
                offset = 4.0 * math.log2(1 + max_len - abs(ia - ib - ab_center_shift))
                comps[ip,ib] = offset if a[ia] == b[ib] else 0.0

        a_shifts.append(''.join(a_shift_row))

    return comps, a_shifts


def find_ins_del(comp_xy: np.array, y: str):
    """Find insertions by looking for empty (0) columns in the comp matrix.
    Find deletions by looking for empty (0) columns in the comp matrix. This same
    function works for both by choosing whether to pass in (comp_ab, b) for inserts
    or (comp_ba, a) for deletes.

    Note: some insertions may look like copies or moves, and some deletions may
    look like moves, and so they may be missed by this heuristic. An improved 
    approach would look for short isolated non-zero chunks and also treat them 
    as inserts or deletes.

    TODO: Investigate heuristics for finding inserts or deletes in the alternate matrices
    or cross-checking matches.
    
    Store as a list of positions in 'b' and inserted strings.
    """

    match_cols = ~np.any(comp_xy, axis=0)   # Find columns with no matches
    #print(''.join(str(int(b)) for b in match_cols))
    matches = []
    in_match_chunk = False
    start_pos = -1
    match_str = ""
    for icol in range(len(match_cols)):
        if match_cols[icol]:
            if in_match_chunk:
                match_str += y[icol]
            else:
                match_str = y[icol]
                start_pos = icol
                in_match_chunk = True
        else:
            if in_match_chunk:
                in_match_chunk = False
                matches.append((start_pos, match_str))
            else:
                pass

    if in_match_chunk:   # If we reach the end while processing a matched chunk,
        matches.append((start_pos, match_str))   # save the chunk.

    return matches


def print_comp_matrix(a: str, b: str, comps_ab, shift_a, comps_ba, shift_b):
    """Print the comp matrix with b chars as column labels."""
    rows_ab, cols_ab = comps_ab.shape
    rows_ba, cols_ba = comps_ba.shape

    # Header: padding for row label, then each b char
    header = " " + "  ".join(b) + " "*(cols_ab + 6) + "  ".join(a)
    print(header)
    print("-" * (len(header) + 3 + cols_ba))

    #print(f"rows_ba={rows_ba} cols_ba={cols_ba}")
    assert rows_ab == rows_ba
    for irow in range(rows_ab):
        row_vals_ab = " ".join(f"{comps_ab[irow,ib]:2.0f}" for ib in range(cols_ab))
        row_vals_ba = " ".join(f"{comps_ba[irow,ia]:2.0f}" for ia in range(cols_ba))
        print(f"{row_vals_ab} ", shift_a[irow], f"  {row_vals_ba} ", shift_b[irow])


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Slide two strings across each other, comparing characters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="",
    )
    parser.add_argument("strs", nargs=2, help="Two strings to compare")
    parser.add_argument("-c", "--comment", help="Test comment")
    args = parser.parse_args()
    a = args.strs[0]
    b = args.strs[1]
    cmt = args.comment
    comp_ab, shift_a = slide(a, b)
    comp_ba, shift_b = slide(b, a)
    ins = find_ins_del(comp_ab, b)
    dels = find_ins_del(comp_ba, a)
    print(f"### {a} -> {b} : {cmt}\n```")
    print_comp_matrix(a, b, comp_ab, shift_a, comp_ba, shift_b)
    print("Inserts: ", ins)
    print("Deletes: ", dels)
    print("```")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
