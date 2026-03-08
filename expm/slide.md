# Slide Algorithm Notes

## Edit Types
- **Insert**
  - Start Insert: unmatched target tokens at the start
  - End Insert: unmatched target tokens at the end
  - Center Insert: unmatched target tokens in the center combined with a +Y shift for matched tokens after the insert. In other words, a two-token insert will cause a two-token +X shift and a two-token +Y shift in the target.
- **Delete**
  - Start Delete: no X gap in the target, source longer than target, match Y row shifted down below the midpoint.
  - End Delete: no X gap in the target, source longer than target, match Y row shifted up above the midpoint.
  - Center Delete: no X gap in the target, but a -Y shift in the target--one row for each deleted token.
- **Move** when a block of tokens are moved, the result looks like a swap of the moved block with an adjacent block.
    - One block appears first (smaller X) with a -Y shift (higher), while the second block (larger X) is adjacent with a +Y shift. The Y shifts may be large depending on the move distance.
    - TODO: figure out the sizes of the blocks and the shift distances.
    - TODO: figure out what happens if we combine a move and an edit.

- **Copy** a copy and a move can sometimes look very similar (see the following). For the copy, the target is longer and the Y shift smaller. For the move, the second block +Y shift will be larger by the size of the moved block.

## Edit Examples

### Center Deletions
```
# abCde -> abde
 0  0  0  0   e___
 0  0  0  0   de__
 0  0  0  0   Cde_
 0  0 10 10   bCde
10 10  0  0   abCd
 0  0  0  0   _abC
 0  0  0  0   __ab
 0  0  0  0   ___a
```
```
# abCDef -> abef
 0  0  0  0   f___
 0  0  0  0   ef__
 0  0  0  0   Def_
 0  0 10 10   CDef
 0  0  0  0   bCDe
10 10  0  0   abCD
 0  0  0  0   _abC
 0  0  0  0   __ab
 0  0  0  0   ___a
```
```
# aBCdef -> adef
 0  0  0  0   f___
 0  0  0  0   ef__
 0  0  0  0   def_
 0 10 10 10   Cdef
 0  0  0  0   BCde
10  0  0  0   aBCd
 0  0  0  0   _aBC
 0  0  0  0   __aB
 0  0  0  0   ___a
```

### Start or End Deletions
```
# abcdEF -> abcd
 0  0  0  0   F___
 0  0  0  0   EF__
 0  0  0  0   dEF_
 0  0  0  0   cdEF
 0  0  0  0   bcdE
10 10 10 10   abcd
 0  0  0  0   _abc
 0  0  0  0   __ab
 0  0  0  0   ___a
```
```
# ABcdef -> cdef
 0  0  0  0   f___
 0  0  0  0   ef__
 0  0  0  0   def_
10 10 10 10   cdef
 0  0  0  0   Bcde
 0  0  0  0   ABcd
 0  0  0  0   _ABc
 0  0  0  0   __AB
 0  0  0  0   ___A
```

### Center Insertions
```
# abde -> abCde
 0  0  0  0  0   e____
 0  0  0  0  0   de___
 0  0  0  0  0   bde__
10 10  0  0  0   abde_
 0  0  0 10 10   _abde
 0  0  0  0  0   __abd
 0  0  0  0  0   ___ab
 0  0  0  0  0   ____a
```
```
# abef -> abCDef
 0  0  0  0  0  0   f_____
 0  0  0  0  0  0   ef____
 0  0  0  0  0  0   bef___
10 10  0  0  0  0   abef__
 0  0  0  0  0  0   _abef_
 0  0  0  0 10 10   __abef
 0  0  0  0  0  0   ___abe
 0  0  0  0  0  0   ____ab
 0  0  0  0  0  0   _____a
```
### Start or End Insertions
```
# abc -> abcDE
 0  0  0  0  0   c____
 0  0  0  0  0   bc___
 9  9  9  0  0   abc__
 0  0  0  0  0   _abc_
 0  0  0  0  0   __abc
 0  0  0  0  0   ___ab
 0  0  0  0  0   ____a
```
```
# cde -> ABcde
 0  0  0  0  0   e____
 0  0  0  0  0   de___
 0  0  0  0  0   cde__
 0  0  0  0  0   _cde_
 0  0  9  9  9   __cde
 0  0  0  0  0   ___cd
 0  0  0  0  0   ____c
```

### Move (Swap Ends)
```
# ABcd -> cdAB
 0  0  0  0   d___
 6  6  0  0   cd__
 0  0  0  0   Bcd_
 0  0  0  0   ABcd
 0  0  0  0   _ABc
 0  0  6  6   __AB
 0  0  0  0   ___A
```

### Copy Paste
```
# ABcde -> ABcdABe
 0  0  0  0  0  0  0   e______
 0  0  0  0  0  0  0   de_____
 0  0  0  0  0  0  0   cde____
 0  0  0  0  0  0  0   Bcde___
11 11 11 11  0  0  0   ABcde__
 0  0  0  0  0  0  0   _ABcde_
 0  0  0  0  0  0 11   __ABcde
 0  0  0  0  0  0  0   ___ABcd
 0  0  0  0  9  9  0   ____ABc
 0  0  0  0  0  0  0   _____AB
 0  0  0  0  0  0  0   ______A
```
- Move
```
# aBCdef -> adeBCf
 0  0  0  0  0  0   f_____
 0  0  0  0  0  0   ef____
 0  0  0  0  0  0   def___
 0  9  9  0  0  0   Cdef__
 0  0  0  0  0  0   BCdef_
11  0  0  0  0 11   aBCdef
 0  0  0  0  0  0   _aBCde
 0  0  0  9  9  0   __aBCd
 0  0  0  0  0  0   ___aBC
 0  0  0  0  0  0   ____aB
 0  0  0  0  0  0   _____a
```