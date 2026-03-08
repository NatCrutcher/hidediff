# Slide Algorithm Notes

- Center deletions
```
 # abcde -> abde
  0  0 10 10    
 10 10  0  0
```
```
 # abcdef -> abef
  0  0 10 10
  0  0  0  0
 10 10  0  0
```
- Start or end deletions
```
 # abcdef -> abcd OR abcdef -> cdef
  0  0  0  0
 10 10 10 10
  0  0  0  0
```
- Center insertions
```
 # abde -> abcde
 10 10  0  0  0
  0  0  0 10 10
```
```
 # abef -> abcdef
 10 10  0  0  0  0
  0  0  0  0  0  0
  0  0  0  0 10 10
```
- Start or end insertions
```
# abcd -> abcdef
 10 10 10 10  0  0
```
```
 # abcd -> efabcd
  0  0 10 10 10 10
```
- Swap ends
```
 # abcd -> cdab
  6  6  0  0
``0  0  0  0
  0  0  0  0
  0  0  0  0
  0  0  6  6
```
- Copy paste
```
 # abcde -> abcdeabc
12 12 12 12 12  0  0  0 
 0  0  0  0  0  0  0  0
 0  0  0  0  0  0  0  0
 0  0  0  0  0  0  0  0
 0  0  0  0  0  0  0  0
 0  0  0  0  0 10 10 10
```