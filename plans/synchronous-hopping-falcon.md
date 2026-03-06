# Plan: ndiff Design Document

## Context
The user has a feature goals document (`New_Diff.md`) for an advanced differencing tool called ndiff. They requested additional research followed by a detailed design document. Research has been completed (existing tools, algorithms, implementation approaches) and a comprehensive design document has been drafted.

## What was done (research phase)
1. **Surveyed existing tools**: difftastic, delta, GumTree, SemanticMerge, SemanticDiff, Beyond Compare, Meld, KDiff3, Code Compare, etc.
2. **Researched algorithms**: Myers, Patience, Histogram diff; GumTree AST matching; token-based clone detection (SourcererCC); three-way merge; fuzzy matching approaches
3. **Evaluated implementation options**: Language choice, libraries, architecture patterns, performance considerations

## Key decisions made (via user input)
- **Language**: Rust
- **Approach**: New tool from scratch, reusing libraries (tree-sitter, similar, git2)
- **MVP priority**: Intra-line highlighting + format-aware diffing
- **Scope**: Universal (code, prose, config, structured data)
- **Format-aware**: Both normalize-then-diff and diff-then-annotate modes
- **Deliverable**: Comprehensive design document

## What will be created
Save the drafted design document as `/home/nat/ndiff/DESIGN.md` (1781 lines). It covers:

1. **Overview & Motivation** — market gaps, design philosophy
2. **Detailed Requirements** — 15 requirements (5 core, 5 enhanced, 6 advanced) with acceptance criteria
3. **Architecture** — pipeline design (input → normalize → diff → classify → render), crate structure, core data types
4. **Algorithm Design** — Histogram diff default, intra-line token diff, move detection (exact + fuzzy), format classification, GumTree-inspired AST diff, clone detection
5. **Technology Stack** — specific Rust crates with versions and licenses
6. **Phased Implementation Plan** — 8 phases from MVP through advanced features, with deliverables and exit criteria
7. **CLI Interface Design** — full command-line spec, config file format, Git integration protocol, output examples
8. **Design Decisions & Trade-offs** — rationale for each major choice
9. **Open Questions** — 15 items needing further investigation
10. **References** — papers, tools, specifications

## Verification
- Review the document for completeness against the original `New_Diff.md` goals
- Verify all original feature goals are addressed in the requirements
- Check that the phased plan has clear dependencies and exit criteria
