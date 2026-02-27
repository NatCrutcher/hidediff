# New Differencing Tool

## Feature Goals 

- Start with a command line version, but also plan to support a GUI version.
- Designed to work with version control systems, starting with Git.
- This must be able to detect and show small changes within a line, and not just treat the entire line as different.
- Include options to hide certain classes of changes from either the original version or from the new version. The hidden changes could still be marked with color highlighting or an underline, and with the option of hovering to show the hidden changes.
  - Formatting changes - For example, if a C++ file has been reformatted, this would have the ability to make the original code look like it was using the same format as the new code, or vice versa, so that only non-format changes would appear as differences.
  - An important subset of hiding formatting changes will be the ability to show or ignore line
    break changes. This will be especially helpful with non-code documents.
  - Renaming - This would take effect by renaming the original code to match the new names. Or alternatively, renaming the new code to match the old names. Ideally, this would be language-aware so that it would know the scope over which the renaming applied.
  - Moves - This would hide the move by doing the move in the original or the new version to match the version being compared against.
- The tools should be able to take advantage of intermediate versions from a version control system
  to better understand the changes and to be able to better match up the original and the new version.
- If a block of code has been copy-pasted, have the option to display the original source for the copy. In other words, instead of just showing a new block of code appearing, we would actually show the code from which it was copied.
- For the GUI version, when working from a version control repository, include the option to scroll back and forth through different versions.
- When working from a version control repository include the ability to show who made changes,
  like the blame feature.
- When working from a version control repository, include the ability to show commit messages.
- Advanced feature: add the ability to look for the source of new code from different files within a project. In particular, this would help find when something had been moved from one
  file to another file. Tag such moves indicating the source location. 
- Advanced feature: find duplicated and near duplicated code within one file or
  across multiple files and present them as differences. This would likely be a special mode of operation.
- Advanced feature: include three-way merges.

## Research Notes

- Some of this may be very difficult to implement. For example, determining whether a format change is meaningful or not meaningful may require understanding the programming language being used.
  In Python, changing the indentation can change the meaning, whereas in C++ it will not.
- Finding moves, especially when they are combined with changes, will be algorithmically challenging.
- Research algorithms for matching up different versions in the presence of changes, moves, reformatting, and copy/paste operations. This will require some degree of fuzzy matching.
- Search for any existing open source or proprietary systems that include these types of
  features. If this substantially already exists, then there is no need to recreate it. If there is open source code that implements aspects of this, then we should try to reuse that code or at least the algorithms.
- I am guessing we would want to implement this in C++ for speed.
