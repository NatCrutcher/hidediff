# HideDiff: Advanced Differencing Tool -- Design Document

**Version:** 0.1.0-draft  
**Date:** 2026-02-26  
**Status:** Draft  
**Authors:** Nathaniel Crutcher, Claude Code

---

## Table of Contents

1. [Overview & Motivation](#1-overview--motivation)
2. [Detailed Requirements](#2-detailed-requirements)
3. [Architecture](#3-architecture)
4. [Algorithm Design](#4-algorithm-design)
5. [Technology Stack](#5-technology-stack)
6. [Phased Implementation Plan](#6-phased-implementation-plan)
7. [CLI Interface Design](#7-cli-interface-design)
8. [Key Design Decisions & Trade-offs](#8-key-design-decisions--trade-offs)
9. [Open Questions](#9-open-questions)
10. [References](#10-references)

---

## 1. Overview & Motivation

### 1.1 What is HideDiff?

HideDiff is an advanced differencing tool built in Rust that goes far beyond traditional
line-based diff. The most novel feature is the ability to hide certain classes of changes like formatting changes, renaming, and text movement (or even copy-paste operations). It does this by changing either the original version to match the new version or to change the new version to match the original version for the types of changes that are being hidden. 

The term 'hide' does not fully capture the different options. For example, with a rename we could show it as a change, completely hide it so that it looked as though the original name was the same as the new name, or add a gentle highlight to show that something had changed while making the names look unchanged. For copy-paste we could show the full difference as a new block of text or we could show the original source of the copy next to the destination and only highlight any edits that were made after the paste was complete. Either way, there would be an option to indicate the source of the copy paste, with differently formatted text. Lastly, for reformatting, HideDiff would be able to hide that so that you would only see the non-formatting changes. It could do this by applying (not editing the file, just what's displayed) the formatting changes from one side to the other side.

HideDiff provides intra-line change highlighting, format-aware diffing,
move detection, cross-file analysis, VCS integration, and eventually three-way
structural merges. HideDiff treats code, prose, configuration, and structured data as
first-class content types, applying content-appropriate diffing strategies to each.

HideDiff is designed to be used as a standalone CLI tool, as a Git difftool/mergetool,
and eventually through a GUI for interactive exploration (scroll through time) of repository history.

### 1.2 Why HideDiff Exists

Existing differencing tools fall into one of several categories, each with significant
limitations:

| Category | Examples | Strengths | Limitations |
|----------|----------|-----------|-------------|
| **Line-based diff** | GNU diff, Git diff | Fast, universal | No intra-line detail, no structure awareness, cluttered by non-substantive changes |
| **Diff pagers/formatters** | delta, diff-so-fancy | Beautiful output, word highlighting | Not diff engines; rely on line-based diff underneath |
| **Structural diff** | difftastic | Tree-sitter AST diff, 30+ languages | O(L*R) complexity, poor on large diffs, no move detection |
| **AST diff (research)** | GumTree | Move detection, edit scripts | Java-only, research-focused, not user-friendly |
| **Commercial semantic diff** | SemanticDiff, SemanticMerge | Move/rename detection, style change hiding | Proprietary, limited language coverage, expensive |
| **Code Compare tools** | Code Compare, Beyond Compare | Moved block detection | Proprietary, not VCS-integrated, limited automation |

**No single open-source tool provides all of the following:**

- Options to hide non-substantive changes, like formatting, renaming, and moves
- Scalable structural diffing that handles large files gracefully
- Intra-file and cross-file copy-paste and move detection
- Format-aware diffing that can hide or reveal cosmetic changes
- Structural three-way merge
- Universal content support (code, prose, config, structured data)
- Utilize intermediate VCS history to provide improved differencing and change tracking

HideDiff aims to fill this gap as a single, open-source, high-performance tool.

### 1.3 Design Philosophy

1. **Correctness first, then speed.** A diff that is wrong or confusing is worse than
   a diff that is slow. Performance will be addressed through algorithm selection, profiling, and possibly caching.
   
2. **Progressive disclosure.** The simplest invocation (`HideDiff a.txt b.txt`) should
   produce immediately useful output. Advanced features (move detection, format
   normalization, AST-aware diffing) are activated via flags or configuration.

3. **Content-type awareness.** HideDiff recognizes that a Python file, a Markdown
   document, a YAML config, and a JSON API response all benefit from different
   diffing strategies, and may require customized hiding approaches. The tool should select strategies automatically based on
   content type, while allowing user overrides.

4. **Composable pipeline.** Internally, HideDiff is a pipeline of stages (parse,
   normalize, diff, classify, format, render). Each stage is independently testable
   and replaceable. This enables both extensibility and correctness.

5. **Git-native.** While HideDiff works on arbitrary files, its design prioritizes
   seamless Git integration: difftool protocol, blame correlation, commit history
   traversal, and merge conflict resolution. Although it will initially support Git, HideDiff should be structured so that other VCS tools can be easily integrated.

---

## 2. Detailed Requirements

### 2.1 Core Requirements (MVP -- Must-Have for a Useful Tool)

#### CR-1: Basic File Differencing

| Attribute | Detail |
|-----------|--------|
| **Description** | Compare two files and produce a diff showing additions, deletions, and modifications. |
| **User Behavior** | `hidediff file_a file_b` produces colored terminal output showing changes between the two files. |
| **Acceptance Criteria** | (1) Correctly identifies all added, deleted, and changed lines. (2) Output is at least as readable as `git diff --color-words`. (3) Handles files up to 100K lines within 2 seconds. (4) Correctly handles binary file detection with a clear message. (5) Supports reading from stdin via `-` argument. |
| **To Do** | Precisely specify the diff output format or formats. |

#### CR-2: Intra-Line Change Highlighting

| Attribute | Detail |
|-----------|--------|
| **Description** | Within changed lines, highlight the specific words or characters that differ, rather than marking the entire line as changed. |
| **User Behavior** | Changed lines show unchanged portions in normal text and changed portions with distinct background/foreground colors. Insertions, deletions, moves, and replacements are visually distinct. |
| **Acceptance Criteria** | (1) Token-level (word-boundary) diffing is the default. (2) Character-level diffing is available via `--char-diff` flag. (3) In a line where only a variable name changed, only the variable name is highlighted, not the entire line. (4) Works correctly with multi-byte UTF-8 characters. (5) Color scheme is configurable and respects terminal capabilities. |
| **To Do** | Split out UTF-8 into separate requirement. |

#### CR-3: Format-Aware Diffing (Basic)

| Attribute | Detail |
|-----------|--------|
| **Description** | Provide two modes for handling formatting changes: (a) normalize-then-diff, which reformats both files to a canonical style before diffing so that purely cosmetic changes disappear; (b) diff-then-annotate, which performs a normal diff but classifies each change as "semantic" or "cosmetic" and presents them differently. |
| **User Behavior** | `hidediff --normalize file_a file_b` uses mode (a). `hidediff --classify-format file_a file_b` uses mode (b). Default behavior shows all changes but uses dimmed styling for whitespace-only changes. |
| **Acceptance Criteria** | (1) Whitespace-only changes (indentation, trailing spaces, blank lines, changed line breaks) are detected and can be hidden via `--ignore-whitespace` or dimmed by default. (2) In normalize mode, the tool applies a content-type-specific normalizer before diffing. (3) In annotate mode, changes are tagged as `semantic` or `cosmetic` in both the display and the structured output. (4) Line-break changes in prose can be shown or hidden via `--ignore-line-breaks`. |
| **To Do** | I think we should distinguish between ignoring something and hiding something. For example, we might have a line of code that has a substantive change and a whitespace change. Because of the substantive change, we will show the line as having changed. But if we are hiding whitespace changes, then we will make it look as though the whitespace is the same before and after. |

#### CR-4: Multiple Output Formats

| Attribute | Detail |
|-----------|--------|
| **Description** | Support multiple output formats for different consumption contexts. |
| **User Behavior** | `hidediff --format=terminal` (default), `hidediff --format=unified`, `hidediff --format=json`, `hidediff --format=side-by-side`. |
| **Acceptance Criteria** | (1) Terminal format uses ANSI colors and is the default when stdout is a TTY. (2) Unified format produces standard unified diff compatible with `patch`. (3) JSON format produces machine-readable structured output with all classification metadata. (4) Side-by-side format shows files in two columns with aligned changes. (5) When stdout is not a TTY, defaults to unified format unless overridden. |
| **To Do** | Consider a 'delta' format option for the side-by-side format that matches or approximates the Delta diff tool's output. |

#### CR-5: Configuration System

| Attribute | Detail |
|-----------|--------|
| **Description** | Support configuration via file, environment variables, and command-line flags, with clear precedence. |
| **User Behavior** | Configuration is loaded from `~/.config/hidediff/config.toml`, then overridden by `HIDEDIFF_*` environment variables, then overridden by CLI flags. |
| **Acceptance Criteria** | (1) Config file uses TOML format. (2) All CLI flags can be set via config file. (3) Precedence: CLI flags > env vars > config file > defaults. (4) `hidediff --dump-config` shows the effective configuration. (5) Per-repository config via `.hidediff.toml` in repository root. |
| **To Do** | Do we need environment variable configuration? I'm guessing this is a standard feature and we should include it. It's just not something that I normally use. |



---

### 2.2 Enhanced Requirements (Important Differentiators)

#### ER-1: Git Integration

| Attribute | Detail |
|-----------|--------|
| **Description** | Integrate with Git as a difftool and provide direct access to Git objects (blobs, commits, trees) for diffing. |
| **User Behavior** | `git difftool -t hidediff` uses HideDiff for Git diffs. `hidediff --git HEAD~3..HEAD -- file.rs` diffs a file across commits. `hidediff --staged` shows staged changes. |
| **Acceptance Criteria** | (1) Works as a Git difftool via `GIT_EXTERNAL_DIFF` protocol. (2) Can diff Git objects directly without checkout via libgit2. (3) Supports commit range syntax (`A..B`, `A...B`). (4) Supports `--staged`, `--cached`, and working-tree diffs. (5) Provides setup command: `hidediff --install-git` to configure Git. (6) Respects `.gitattributes` for diff driver configuration. |

#### ER-2: Move Detection (Intra-File)

| Attribute | Detail |
|-----------|--------|
| **Description** | Detect when a block of code or text has been moved from one location to another within the same file, rather than showing it as a deletion and an unrelated insertion. |
| **User Behavior** | Moved blocks are shown with a distinct color/annotation (e.g., "moved from line 42" / "moved to line 107"). The user can toggle move detection via `--detect-moves` / `--no-detect-moves`. |
| **Acceptance Criteria** | (1) Detects exact moves (identical content relocated). (2) Detects near-moves (moved content with minor modifications) using configurable similarity threshold (default 80%). (3) Moved blocks are visually linked in terminal output. (4) In JSON output, moved blocks include `move_id`, `from_range`, and `to_range` fields. (5) (Optional) Performance: does not more than double the diff time for typical files. |
| **See Also** | AR-1: Cross-File Move Detection |

#### ER-3: Rename Detection

| Attribute | Detail |
|-----------|--------|
| **Description** | Detect when identifiers (variables, functions, classes) have been renamed and present the diff with renaming factored out. |
| **User Behavior** | `hidediff --renames file_a file_b` identifies systematic renames and shows them separately from semantic changes. The user sees a summary like "Renamed: `oldFunc` -> `newFunc` (12 occurrences)" followed by a diff with the renames already applied. |
| **Acceptance Criteria** | (1) Detects identifier renames that occur consistently across the file. (2) Language-aware mode (using tree-sitter) respects scoping rules. (3) Language-agnostic mode uses statistical token replacement detection. (4) Factored renames are listed in a summary section. (5) The remaining diff after factoring out renames shows only semantic changes. |

#### ER-4: Blame Integration

| Attribute | Detail |
|-----------|--------|
| **Description** | When diffing within a Git repository, optionally annotate diff output with blame information showing who last modified each line and when. |
| **User Behavior** | `hidediff --blame HEAD~1..HEAD -- file.rs` shows the diff with blame annotations in the gutter. |
| **Acceptance Criteria** | (1) Each line in the diff output can show the author and/or the commit hash. (2) Blame information is fetched via libgit2, not by shelling out to `git blame`. (3) Works with commit ranges. (4) (Optional) Performance: blame annotation adds less than 50% overhead to diff time. (5) Available in terminal and JSON output formats. |

#### ER-5: Commit Message Display

| Attribute | Detail |
|-----------|--------|
| **Description** | When diffing across commits, display relevant commit messages as context. |
| **User Behavior** | `hidediff --show-commits HEAD~5..HEAD -- file.rs` shows each commit's message and author as a header between the diff hunks that belong to that commit. |
| **Acceptance Criteria** | (1) Commit messages are shown as section headers. (2) Each hunk is attributed to the commit that introduced it. (3) Works with commit ranges and merge commits. (4) Can be combined with blame integration. |
| **To Do** | This is intended more for a GUI or TUI interface where the commit message can be shown by clicking or hovering. It may be too verbose for pure text output. Include an option to just show the commit summary or the first line of the commit message. |



---

### 2.3 Advanced Requirements (Ambitious Long-Term Goals)

#### AR-1: Cross-File Move Detection

| Attribute | Detail |
|-----------|--------|
| **Description** | Detect when code has been moved from one file to another within a repository, and present the move as a relocation rather than a deletion in one file and insertion in another. |
| **User Behavior** | `hidediff --cross-file HEAD~1..HEAD` analyzes all changed files and identifies cross-file moves. Output shows "Block moved from `src/old.rs:42-60` to `src/new.rs:10-28`" with the block's diff relative to its original location. |
| **Acceptance Criteria** | (1) Identifies blocks of N+ lines that appear in a deleted region of one file and an inserted region of another. (2) Handles moved-and-modified blocks with configurable similarity threshold. (3) Reports are per-move with source and destination locations. (4) Scales to repositories with hundreds of changed files per commit. (5) Integrates with Git's own rename detection as a baseline. |
| **See Also** | ER-2: Move Detection (Intra-File) |

#### AR-2: Copy-Paste Source Detection

| Attribute | Detail |
|-----------|--------|
| **Description** | When new code appears in a diff, search the repository (current and historical versions) to find the likely source that was copy-pasted. |
| **User Behavior** | `hidediff --detect-copies HEAD~1..HEAD -- file.rs` annotates new code blocks with their likely source: "Likely copied from `src/utils.rs:100-120` (92% similar)", and shows the source code on the left with changes to the source as edits on the right. |
| **Acceptance Criteria** | (1) Searches all files in the repository at the base commit for similar blocks. (2) Uses token-based similarity (not just line-based) for fuzzy matching. (3) Reports similarity percentage and source location. (4) Configurable minimum block size and similarity threshold. (5) Completes within 30 seconds for a repository of 100K LOC. |
| **To Do** | This seems very related to AR-1. Look at whether we should merge these two requirements. |

#### AR-3: Duplicate / Near-Duplicate Detection

| Attribute | Detail |
|-----------|--------|
| **Description** | Find duplicated or near-duplicated code blocks within a single file or across multiple files and present them as diffs against each other. This is a special analysis mode, not a standard diff operation. |
| **User Behavior** | `HideDiff --find-clones src/` scans all files under `src/` and reports groups of similar code blocks with their diffs. |
| **Acceptance Criteria** | (1) Detects Type-1 (exact), Type-2 (renamed), and Type-3 (near-miss) clones. (2) Reports clone groups with locations and similarity percentages. (3) Shows the diff between clone instances. (4) Scales to 100K+ LOC projects. (5) Configurable minimum clone size (default: 6 lines / 50 tokens). |

#### AR-4: Three-Way Merge

| Attribute | Detail |
|-----------|--------|
| **Description** | Perform three-way merge using a common ancestor, showing conflicts with structural awareness rather than line-based overlap detection. |
| **User Behavior** | `HideDiff --merge ancestor.rs ours.rs theirs.rs` produces a merged result, or `HideDiff --merge3 ancestor.rs ours.rs theirs.rs` shows the three-way diff. Can be used as Git mergetool. |
| **Acceptance Criteria** | (1) Produces correct merge when changes do not overlap. (2) For overlapping changes, provides conflict markers compatible with Git. (3) In structural mode, resolves conflicts that are line-based conflicts but not structural conflicts (e.g., two functions added at the same line but in different scopes). (4) Reports merge statistics (auto-resolved, conflicts). (5) Works as a Git mergetool via `git mergetool -t HideDiff`. |

#### AR-5: VCS History Navigation (GUI)

| Attribute | Detail |
|-----------|--------|
| **Description** | In the GUI version, provide the ability to scroll through file versions from the VCS, seeing the diff between any two selected versions. |
| **User Behavior** | GUI shows a timeline of commits affecting the current file. User clicks two points on the timeline to see the diff between those versions. Arrow keys move forward/backward through versions. |
| **Acceptance Criteria** | (1) Shows commit timeline for the selected file. (2) Diff updates in real-time as versions are selected. (3) Supports keyboard navigation (left/right arrow for version, up/down for scrolling). (4) Lazy-loads diffs for performance. (5) Integrates blame, commit messages, and move detection. |

#### AR-6: Intermediate Version Utilization

| Attribute | Detail |
|-----------|--------|
| **Description** | When diffing between two distant commits, use intermediate commits to improve change matching. For example, if a block was moved in commit 3 and then modified in commit 7, the tool can trace the move through the intermediate version rather than showing it as an unrelated deletion and insertion. |
| **User Behavior** | `HideDiff --use-intermediates HEAD~10..HEAD -- file.rs` analyzes the chain of commits to produce a more accurate composite diff. |
| **Acceptance Criteria** | (1) Traces block identity through intermediate commits. (2) Attributes each change to its originating commit. (3) Produces better move detection by using intermediate state. (4) Shows the "journey" of a block through versions. (5) Performance scales linearly with the number of intermediate commits. |

---

## 3. Architecture

### 3.1 High-Level Architecture

```
+-------------------------------------------------------------------+
|                         HideDiff                                      |
|                                                                    |
|  +---------------------+  +---------------------+  +------------+ |
|  |     CLI Frontend     |  |    TUI Frontend     |  | GUI (Tauri)| |
|  |  (clap + termcolor)  |  |    (ratatui)        |  | (future)   | |
|  +----------+----------+  +---------+-----------+  +-----+------+ |
|             |                       |                     |        |
|             +----------+------------+---------------------+        |
|                        |                                           |
|  +---------------------v-----------------------------------------+ |
|  |                   Rendering Layer                              | |
|  |                                                                | |
|  |  +----------+ +----------+ +--------+ +----------+ +--------+ | |
|  |  | Terminal  | | Unified  | | JSON   | | Side-by- | | HTML   | | |
|  |  | Renderer | | Renderer | | Render | | Side Rndr| | Render | | |
|  |  +----------+ +----------+ +--------+ +----------+ +--------+ | |
|  +---------------------+----------------------------------------+ | |
|                        |                                           |
|  +---------------------v-----------------------------------------+ |
|  |                Classification Layer                            | |
|  |                                                                | |
|  |  +-------------+ +-------------+ +-------------+ +---------+  | |
|  |  | Whitespace  | | Move        | | Rename      | | Format  |  | |
|  |  | Classifier  | | Detector    | | Detector    | | Classif.|  | |
|  |  +-------------+ +-------------+ +-------------+ +---------+  | |
|  +---------------------+-----------------------------------------+ |
|                        |                                           |
|  +---------------------v-----------------------------------------+ |
|  |                   Diff Engine                                  | |
|  |                                                                | |
|  |  +----------+ +----------+ +----------+ +------------------+  | |
|  |  | Line     | | Token    | | Char     | | AST Diff         |  | |
|  |  | Diff     | | Diff     | | Diff     | | (tree-sitter)    |  | |
|  |  | (Myers/  | | (intra-  | | (intra-  | |                  |  | |
|  |  | Patience/| | line)    | | line)    | |                  |  | |
|  |  | Histogrm)| |          | |          | |                  |  | |
|  |  +----------+ +----------+ +----------+ +------------------+  | |
|  +---------------------+-----------------------------------------+ |
|                        |                                           |
|  +---------------------v-----------------------------------------+ |
|  |                 Normalization Layer                             | |
|  |                                                                | |
|  |  +-------------+ +-------------+ +-------------+ +---------+  | |
|  |  | Whitespace  | | Line-ending | | Language-   | | Custom  |  | |
|  |  | Normalizer  | | Normalizer  | | Specific    | | (user)  |  | |
|  |  |             | |             | | Formatter   | |         |  | |
|  |  +-------------+ +-------------+ +-------------+ +---------+  | |
|  +---------------------+-----------------------------------------+ |
|                        |                                           |
|  +---------------------v-----------------------------------------+ |
|  |                   Input Layer                                  | |
|  |                                                                | |
|  |  +----------+ +----------+ +-----------+ +-----------------+  | |
|  |  | File     | | Stdin    | | Git Object| | Content-Type    |  | |
|  |  | Reader   | | Reader   | | Reader    | | Detector        |  | |
|  |  |          | |          | | (libgit2) | | (extension +    |  | |
|  |  |          | |          | |           | |  heuristics)    |  | |
|  |  +----------+ +----------+ +-----------+ +-----------------+  | |
|  +----------------------------------------------------------------+ |
+-------------------------------------------------------------------+
```

### 3.2 Crate / Module Organization

HideDiff is organized as a Cargo workspace with a core library crate and separate
frontend crates. This separation ensures the core diffing logic is reusable and
independently testable.

```
HideDiff/
  Cargo.toml                  # Workspace root
  
  crates/
    HideDiff-core/               # Core library (no I/O, no UI)
      Cargo.toml
      src/
        lib.rs
        input/                # Input handling, content type detection
          mod.rs
          content_type.rs     # File type detection & registry
          reader.rs           # Unified reader trait
        normalize/            # Pre-diff normalization
          mod.rs
          whitespace.rs       # Whitespace normalization
          line_endings.rs     # Line ending normalization
          formatter.rs        # Language-specific formatting bridge
        diff/                 # Core diff algorithms
          mod.rs
          line.rs             # Line-level diff (Myers, Patience, Histogram)
          token.rs            # Token-level (intra-line) diff
          char.rs             # Character-level diff
          ast.rs              # AST-based structural diff
          types.rs            # DiffResult, Hunk, Change, etc.
        classify/             # Post-diff classification
          mod.rs
          whitespace.rs       # Whitespace-only change detection
          moves.rs            # Move detection
          renames.rs          # Rename detection
          format.rs           # Semantic vs. cosmetic classification
        merge/                # Three-way merge (future)
          mod.rs
        analysis/             # Cross-file and clone analysis (future)
          mod.rs
          cross_file.rs       # Cross-file move/copy detection
          clones.rs           # Clone detection
        vcs/                  # VCS abstraction (Git first)
          mod.rs
          git.rs              # Git-specific operations via libgit2
          blame.rs            # Blame integration
          history.rs          # History traversal
    
    HideDiff-cli/                # CLI frontend
      Cargo.toml
      src/
        main.rs
        args.rs               # CLI argument definitions (clap)
        config.rs             # Configuration loading & merging
        render/               # Output renderers
          mod.rs
          terminal.rs         # ANSI terminal output
          unified.rs          # Unified diff format
          json.rs             # JSON structured output
          side_by_side.rs     # Side-by-side terminal output
    
    HideDiff-tui/                # TUI frontend (future, Phase 4+)
      Cargo.toml
      src/
        main.rs
    
    HideDiff-gui/                # GUI frontend (future, Phase 6)
      Cargo.toml
      src-tauri/
      src/                    # Web UI source
```

### 3.3 Core Data Types

The central data structures that flow through the pipeline:

```rust
/// Represents the type of content being diffed.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ContentType {
    /// Programming language with tree-sitter grammar name
    Code { language: String },
    /// Prose / natural language text (Markdown, plain text, reStructuredText)
    Prose { format: ProseFormat },
    /// Structured data (JSON, YAML, TOML, XML)
    StructuredData { format: DataFormat },
    /// Configuration file with known format
    Config { format: String },
    /// Unknown or binary
    Unknown,
    /// Explicitly binary
    Binary,
}

/// A single atomic change within a diff.
#[derive(Debug, Clone)]
pub struct Change {
    /// What kind of change this is
    pub kind: ChangeKind,
    /// Line range in the old file (None for insertions)
    pub old_range: Option<LineRange>,
    /// Line range in the new file (None for deletions)
    pub new_range: Option<LineRange>,
    /// Intra-line detail: specific spans within the line that changed
    pub spans: Vec<Span>,
    /// Classification metadata
    pub classification: ChangeClassification,
    /// If this change is part of a move, the move group ID
    pub move_id: Option<MoveId>,
    /// If this change is part of a rename, the rename group ID
    pub rename_id: Option<RenameId>,
}

/// Classification of a change for filtering and display purposes.
#[derive(Debug, Clone, Default)]
pub struct ChangeClassification {
    /// Is this a whitespace-only change?
    pub whitespace_only: bool,
    /// Is this a formatting/cosmetic change (not affecting semantics)?
    pub cosmetic: bool,
    /// Is this a line-break-only change in prose?
    pub line_break_only: bool,
    /// Is this part of a systematic rename?
    pub rename: bool,
    /// Is this a move (content relocated, not new)?
    pub moved: bool,
    /// Confidence score for the classification (0.0 - 1.0)
    pub confidence: f64,
}

/// A span within a single line, used for intra-line highlighting.
#[derive(Debug, Clone)]
pub struct Span {
    /// Byte offset within the line where this span starts
    pub start: usize,
    /// Byte offset within the line where this span ends (exclusive)
    pub end: usize,
    /// What kind of span this is
    pub kind: SpanKind,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum SpanKind {
    /// Unchanged text
    Equal,
    /// Inserted text (only in new file)
    Insert,
    /// Deleted text (only in old file)
    Delete,
    /// Replaced text (different in old and new)
    Replace,
}

/// A hunk groups contiguous changes with surrounding context.
#[derive(Debug, Clone)]
pub struct Hunk {
    pub old_start: usize,
    pub old_count: usize,
    pub new_start: usize,
    pub new_count: usize,
    pub changes: Vec<Change>,
    pub context_before: Vec<String>,
    pub context_after: Vec<String>,
}

/// The complete result of a diff operation.
#[derive(Debug, Clone)]
pub struct DiffResult {
    pub old_path: Option<PathBuf>,
    pub new_path: Option<PathBuf>,
    pub content_type: ContentType,
    pub hunks: Vec<Hunk>,
    pub moves: Vec<MoveGroup>,
    pub renames: Vec<RenameGroup>,
    pub stats: DiffStats,
}

/// Statistics about the diff.
#[derive(Debug, Clone, Default)]
pub struct DiffStats {
    pub lines_added: usize,
    pub lines_deleted: usize,
    pub lines_modified: usize,
    pub lines_moved: usize,
    pub lines_cosmetic: usize,
    pub lines_semantic: usize,
}
```

### 3.4 Pipeline Data Flow

The processing pipeline for a standard diff operation:

```
Input (file paths, git refs, stdin)
  |
  v
+-------------------+
| Input Layer       |  Read files, detect content type, decode encoding
+-------------------+
  |
  | (old_content: String, new_content: String, content_type: ContentType)
  v
+-------------------+
| Normalization     |  Optionally normalize whitespace, line endings,
| Layer             |  apply language-specific formatting
+-------------------+  (preserves mapping back to original positions)
  |
  | (old_normalized: String, new_normalized: String, position_maps: PositionMaps)
  v
+-------------------+
| Diff Engine       |  1. Line-level diff (Myers/Patience/Histogram)
|                   |  2. For each changed line pair: intra-line token/char diff
|                   |  3. Optionally: AST-level structural diff
+-------------------+
  |
  | (raw_changes: Vec<Change>)
  v
+-------------------+
| Classification    |  1. Whitespace classification
| Layer             |  2. Format (semantic vs. cosmetic) classification
|                   |  3. Move detection
|                   |  4. Rename detection
+-------------------+
  |
  | (classified_changes: Vec<Change>, moves: Vec<MoveGroup>,
  |  renames: Vec<RenameGroup>)
  v
+-------------------+
| Hunk Assembly     |  Group changes into hunks with context lines
+-------------------+
  |
  | (diff_result: DiffResult)
  v
+-------------------+
| Rendering Layer   |  Format output for terminal, unified diff, JSON, etc.
+-------------------+
  |
  | (formatted output to stdout / file / GUI)
  v
Output
```

### 3.5 Plugin / Extension Points

HideDiff provides extension points for language-specific and format-specific handling:

#### 3.5.1 Content Type Registry

```rust
/// Register a content type handler that provides normalization and
/// classification capabilities for a specific file type.
pub trait ContentHandler: Send + Sync {
    /// The content type this handler supports.
    fn content_type(&self) -> ContentType;

    /// File extensions this handler claims.
    fn extensions(&self) -> &[&str];

    /// Normalize content for canonical comparison.
    /// Returns normalized content and a position map back to originals.
    fn normalize(&self, content: &str, config: &NormalizeConfig) -> (String, PositionMap);

    /// Classify a change as semantic or cosmetic.
    /// Returns a confidence score (0.0 = definitely cosmetic, 1.0 = definitely semantic).
    fn classify_change(&self, change: &Change, old: &str, new: &str) -> f64;

    /// Provide tree-sitter language name for AST-based features (if applicable).
    fn tree_sitter_language(&self) -> Option<&str> { None }
}
```

Built-in handlers are provided for common content types. Users can add custom
handlers via shared libraries (`.so`/`.dylib`/`.dll`) placed in
`~/.config/HideDiff/plugins/` or via configuration pointing to a formatter command.

#### 3.5.2 External Formatter Bridge

For format-aware diffing, HideDiff can delegate to external formatters:

```toml
# In config.toml
[formatters]
rust = { command = "rustfmt", args = ["--edition", "2021"] }
python = { command = "black", args = ["-q", "-"] }
javascript = { command = "prettier", args = ["--parser", "babel"] }
go = { command = "gofmt" }
c = { command = "clang-format" }
```

The external formatter bridge reads content via stdin, runs the formatter, and
captures stdout, using the result as the normalized form.

#### 3.5.3 Diff Algorithm Selection

```rust
/// Users can select or register diff algorithms.
pub enum DiffAlgorithm {
    Myers,
    Patience,
    Histogram,
    /// Custom algorithm provided by a plugin
    Custom(Box<dyn LineDiffer>),
}

pub trait LineDiffer: Send + Sync {
    fn diff_lines<'a>(&self, old: &'a [&str], new: &'a [&str]) -> Vec<DiffOp>;
}
```

---

## 4. Algorithm Design

### 4.1 Core Line-Level Diff

#### Algorithm Choice: Histogram Diff (Default), with Myers and Patience Available

| Algorithm | Time Complexity | Strengths | Weaknesses |
|-----------|-----------------|-----------|------------|
| **Myers** | O(ND) where D = edit distance | Minimal edit distance, Git default | Can produce confusing results when common lines are frequent |
| **Patience** | O(N log N) for LCS of unique lines, then Myers for gaps | Better anchoring on unique lines, good for code | Slower on files with few unique lines |
| **Histogram** | O(N) average, O(N^2) worst | Deprioritizes high-frequency tokens, best readability for code | Slightly more complex implementation |

**Decision:** Histogram diff is the default because it produces the most readable output
for code (the primary use case). It avoids the "syncing on common but meaningless lines"
problem that Myers has with code containing many `{`, `}`, and blank lines. Patience is
available as a fallback and is preferred for prose (where unique lines are rare).

**Implementation approach:**

- Use the `similar` crate as the starting diff engine. It provides Myers and Patience
  algorithms with a clean API. For the Histogram algorithm, which `similar` does not
  provide, we use `imara-diff` which implements both Myers and Histogram and is used
  by gitoxide.
- Wrap both crates behind our `LineDiffer` trait so the algorithm is selectable at
  runtime.

**Fallback strategy:**

1. Use Histogram for code files.
2. Use Patience for prose and config files (better handling of repetitive structure).
3. If any algorithm exceeds a time budget (configurable, default 5 seconds), fall back
   to Myers which has the most predictable performance.
4. For very large files (>50K lines), use a faster preliminary pass with line hashing
   to identify unchanged regions, then apply the full algorithm only to changed regions.

### 4.2 Intra-Line (Token / Character) Diff

Once line-level diffing identifies changed line pairs, we perform a secondary diff
within each pair to identify exactly which parts of the line changed.

#### Token-Level Diff (Default)

1. **Tokenization:** Split the line into tokens at word boundaries. A "word" is defined
   as a contiguous sequence of alphanumeric characters or underscores. Everything else
   (operators, punctuation, whitespace) is a separate token.

   Example: `result = calculate_sum(a, b);` becomes:
   `["result", " ", "=", " ", "calculate_sum", "(", "a", ",", " ", "b", ")", ";"]`

2. **Diffing:** Apply Myers algorithm (via `similar`) on the token sequences. Myers is
   appropriate here because token sequences are short (typically <100 tokens) and
   minimal edit distance is desirable.

3. **Span mapping:** Map the diff operations back to byte offsets in the original line
   to produce `Span` entries.

#### Character-Level Diff (Optional, via `--char-diff`)

For cases where token-level is too coarse (e.g., a typo fix within a word), apply
Myers at the character level. This is only used when:
- The user explicitly requests `--char-diff`, or
- A token-level diff shows a single large replaced token, and character-level diff
  would reduce the highlighted region by more than 50%.

#### Adaptive Strategy

```
For each changed line pair (old_line, new_line):
  1. Compute token-level diff
  2. If any replaced span covers >80% of the line:
     - This is probably a rewrite; show the whole line as changed
  3. Else if any single replaced token has length >20:
     - Compute character-level diff within that token
     - If it reduces highlighted area by >50%, use it
  4. Otherwise: use the token-level diff as-is
```

### 4.3 Move Detection

Move detection identifies blocks of content that were deleted from one location and
inserted at another. This is performed as a post-processing step on the line-level
diff results.

#### Algorithm

```
Input: List of deleted line blocks (D) and inserted line blocks (I)
       from the line-level diff.

Phase 1: Exact Match
  For each deleted block d in D:
    For each inserted block i in I:
      If d.content == i.content:
        Mark (d, i) as an exact move
        Remove d from D, i from I

Phase 2: Fuzzy Match (for remaining unmatched blocks)
  Build token-set fingerprints for each remaining block:
    fingerprint(block) = { token -> count } for all tokens in block
  
  For each deleted block d in D (sorted by size, largest first):
    For each inserted block i in I:
      sim = jaccard_similarity(fingerprint(d), fingerprint(i))
      If sim >= threshold (default 0.7):
        Candidates.push((d, i, sim))
  
  Sort candidates by similarity descending
  Greedily match: for each candidate, if neither d nor i is already matched:
    Mark (d, i) as a fuzzy move with similarity score
    Remove d from D, i from I

Phase 3: Refinement
  For each fuzzy move pair, compute a full line-level diff between the
  moved block's old and new content to show what changed during the move.
```

**Performance considerations:**

- Phase 1 (exact match) uses hash comparison on whole blocks, so it is O(|D| * |I|)
  but with fast rejection via hash.
- Phase 2 (fuzzy match) builds inverted indexes on tokens for faster similarity
  computation. Expected complexity: O((|D| + |I|) * T) where T is average tokens
  per block.
- Minimum block size of 3 lines prevents matching trivial blocks (single blank lines,
  closing braces, etc.).
- Optional: restrict move detection to blocks within a configurable distance (e.g.,
  only look for moves within 500 lines of each other) for better performance and
  relevance.

### 4.4 Format Classification

Format classification determines whether each change is "semantic" (affects program
behavior or content meaning) or "cosmetic" (affects only visual presentation).

#### Two-Mode Architecture

**Mode A: Normalize-then-Diff**

```
old_file --> normalize(old_file) --\
                                    +--> diff --> result (only semantic changes)
new_file --> normalize(new_file) --/
```

The normalizer strips formatting to a canonical form:
- Collapse all whitespace to single spaces (for non-whitespace-significant languages)
- Normalize indentation to a standard (e.g., 2 spaces)
- Remove trailing whitespace
- Normalize line endings to LF
- Optionally run through an external formatter (rustfmt, black, prettier, etc.)

The position map tracks the correspondence between normalized and original positions
so that the diff result can be displayed against the original source.

**Mode B: Diff-then-Annotate**

```
old_file --\
            +--> diff --> classify each change --> result (all changes, annotated)
new_file --/
```

Each change is classified:
1. **Whitespace-only:** The change, when whitespace is stripped from both sides,
   is empty. Confidence: 1.0.
2. **Indentation-only:** Only leading whitespace differs. Confidence: 1.0 for
   non-Python, 0.5 for Python (indentation is semantic in Python).
3. **Formatter-equivalent:** Both old and new, when run through the language's
   formatter, produce the same output. Confidence: 0.95 (formatter may have bugs).
4. **Brace/style-only:** Change only affects code style (e.g., `if (x) {` vs
   `if (x)\n{`). Requires AST comparison. Confidence: 0.9.
5. **Unknown:** Cannot determine; treated as semantic. Confidence: 0.0.

#### Language-Specific Classification

For languages where formatting can be semantic (Python, YAML, Makefile), the
classifier uses language-specific rules:

| Language | Semantic Whitespace | Rules |
|----------|---------------------|-------|
| Python | Indentation | Indentation changes are semantic; trailing whitespace is cosmetic |
| YAML | Indentation | Indentation determines structure; trailing whitespace is cosmetic |
| Makefile | Tabs vs spaces | Leading tabs in recipes are semantic |
| Go | None (gofmt canonical) | All whitespace changes are cosmetic |
| Rust | None (rustfmt canonical) | All whitespace changes are cosmetic |
| Markdown | Line breaks, indentation | Double-space line endings are semantic; indentation in lists is semantic |

### 4.5 AST-Based Structural Diff

For language-aware features (rename detection, structural move detection, semantic
classification), HideDiff uses tree-sitter to parse source files into ASTs.

#### GumTree-Inspired Algorithm

HideDiff implements a simplified version of the GumTree algorithm adapted for
tree-sitter parse trees:

```
Input: Two tree-sitter parse trees, T_old and T_new

Phase 1: Top-Down Matching (Greedy Isomorphic Subtree)
  1. Compute hash for each subtree (hash of node type + children hashes)
  2. Find all pairs of subtrees with identical hashes
  3. Starting from the largest, greedily match subtrees:
     - Match if (a) hashes are equal AND (b) parent matching is consistent
     - Add all node pairs in matched subtrees to the mapping

Phase 2: Bottom-Up Matching (Container Mapping)
  For each unmatched node n in T_old, traversed bottom-up:
    Candidate = most similar unmatched node m in T_new where:
      - n.type == m.type
      - proportion of matched descendants exceeds threshold (default 0.5)
    If candidate found:
      Match n <-> m
      Apply optimal matching on direct children of n and m

Phase 3: Edit Script Generation
  From the mapping, generate edit operations:
    - DELETE: node in T_old with no match in T_new
    - INSERT: node in T_new with no match in T_old
    - UPDATE: matched nodes where labels/values differ
    - MOVE: matched nodes whose parents' matches differ

Output: List of (operation, node, details) tuples
```

**Scalability guard:** Tree-sitter parsing is fast (typically <100ms for 10K-line
files), but the matching phases can be expensive. If the AST has more than 50K nodes,
HideDiff falls back to line-based diff with token-level intra-line highlighting,
skipping the AST-based structural analysis.

**tree-sitter language coverage:** HideDiff ships with grammars for the most common
languages and can dynamically load additional grammars from the tree-sitter grammar
ecosystem.

Initial language support (grammars bundled):

| Tier | Languages |
|------|-----------|
| **Tier 1** (full handler) | Rust, Python, JavaScript/TypeScript, C/C++, Java, Go |
| **Tier 2** (grammar only) | Ruby, C#, Swift, Kotlin, Scala, PHP, Haskell, Lua, Bash |
| **Tier 3** (data formats) | JSON, YAML, TOML, XML, HTML, CSS, SQL |
| **Tier 4** (markup/prose) | Markdown, LaTeX, reStructuredText |

### 4.6 Clone Detection

For the advanced duplicate/near-duplicate detection feature (AR-3), HideDiff uses a
token-based approach inspired by SourcererCC.

#### Algorithm

```
Input: Set of source files to analyze

Phase 1: Tokenization and Blocking
  For each file:
    Parse into blocks (functions, methods, classes, or sliding windows)
    For each block:
      Tokenize (language-aware via tree-sitter if available)
      Remove type-2 noise (normalize identifiers, literals)
      Compute token frequency vector: { token -> count }

Phase 2: Inverted Index Construction
  Build inverted index: token -> list of (block_id, count)
  
Phase 3: Candidate Retrieval
  For each block b:
    Use inverted index to find blocks sharing tokens with b
    Apply filtering heuristics:
      - Sub-expression filtering: skip if shared tokens < threshold
      - Token ordering: use partial overlap as early rejection
    Compute overlap similarity for surviving candidates

Phase 4: Verification
  For each candidate pair (b1, b2) with similarity >= threshold:
    Compute precise token-level diff between b1 and b2
    Classify clone type:
      - Type 1: Identical (after whitespace normalization)
      - Type 2: Identical structure, renamed identifiers/literals
      - Type 3: Near-miss with modifications

Output: Clone groups with similarity scores and diffs
```

**Scaling:** The inverted index and filtering heuristics keep the algorithm
sub-quadratic in practice. For a 100K LOC project with ~5000 blocks, the expected
runtime is under 30 seconds.

### 4.7 Three-Way Merge

Three-way merge computes changes between a common ancestor and two derived versions,
then combines them.

#### Algorithm

```
Input: ancestor (A), ours (O), theirs (T)

Step 1: Compute two diffs
  diff_ours  = diff(A, O)
  diff_theirs = diff(A, T)

Step 2: Partition into regions
  Divide the ancestor into regions based on change boundaries from both diffs.
  Each region is one of:
    - Unchanged in both: take as-is
    - Changed only in ours: take ours
    - Changed only in theirs: take theirs
    - Changed in both (conflict region): attempt resolution

Step 3: Conflict Resolution
  For conflict regions:
    a. If both sides made identical changes: auto-resolve (take either)
    b. If changes are to different AST nodes within the region:
       auto-resolve by applying both (structural merge)
    c. Otherwise: emit conflict markers

Step 4: Output
  Produce merged content with conflict markers for unresolved conflicts.
  Report statistics: {auto_resolved, structural_resolved, conflicts}
```

The structural merge enhancement (Step 3b) requires AST awareness and is
implemented in later phases. The initial implementation performs only line-based
three-way merge (Steps 1-2 and 3a/3c).

---

## 5. Technology Stack

### 5.1 Language & Toolchain

| Component | Choice | Version | Rationale |
|-----------|--------|---------|-----------|
| Language | Rust | 2024 edition (MSRV 1.90+) | Memory safety, performance, strong ecosystem for CLI/systems tools |
| Build system | Cargo | (bundled with Rust) | Standard Rust build system, workspace support |
| CI | GitHub Actions | N/A | Free for open source, excellent Rust support |
| Minimum supported Rust | 1.90.0 | | Stable async, let-else, C-string literals |

### 5.2 Core Dependencies

| Crate | Version | Purpose | License |
|-------|---------|---------|---------|
| `similar` | 2.x | Myers and Patience diff algorithms | Apache-2.0 |
| `imara-diff` | 0.1.x | Histogram diff algorithm (used by gitoxide) | Apache-2.0 |
| `tree-sitter` | 0.26.x | Incremental parsing for AST features | MIT |
| `tree-sitter-*` | varies | Language grammars (rust, python, javascript, etc.) | MIT |
| `git2` | 0.20.x | libgit2 bindings for Git integration | MIT/Apache-2.0 |

### 5.3 CLI & TUI Dependencies

| Crate | Version | Purpose | License |
|-------|---------|---------|---------|
| `clap` | 4.5.x | CLI argument parsing with derive macros | MIT/Apache-2.0 |
| `ratatui` | 0.30.x | TUI framework (future interactive mode) | MIT |
| `crossterm` | 0.28.x | Cross-platform terminal manipulation | MIT |
| `termcolor` | 1.x | Cross-platform terminal coloring | MIT/Unlicense |
| `unicode-width` | 0.2.x | Correct column width for Unicode text | MIT/Apache-2.0 |

### 5.4 Serialization & Configuration

| Crate | Version | Purpose | License |
|-------|---------|---------|---------|
| `serde` | 1.x | Serialization framework | MIT/Apache-2.0 |
| `serde_json` | 1.x | JSON output format | MIT/Apache-2.0 |
| `toml` | 0.8.x | Configuration file parsing | MIT/Apache-2.0 |

### 5.5 Utility Dependencies

| Crate | Version | Purpose | License |
|-------|---------|---------|---------|
| `anyhow` | 1.x | Error handling in CLI | MIT/Apache-2.0 |
| `thiserror` | 2.x | Error types in library | MIT/Apache-2.0 |
| `rayon` | 1.x | Parallel iteration for multi-file operations | MIT/Apache-2.0 |
| `memmap2` | 0.9.x | Memory-mapped file I/O for large files | MIT/Apache-2.0 |
| `encoding_rs` | 0.8.x | Character encoding detection and conversion | MIT/Apache-2.0 |
| `log` | 0.4.x | Logging facade | MIT/Apache-2.0 |
| `env_logger` | 0.11.x | Logging implementation for CLI | MIT/Apache-2.0 |

### 5.6 Testing Dependencies

| Crate | Version | Purpose | License |
|-------|---------|---------|---------|
| `insta` | 1.x | Snapshot testing for diff output | Apache-2.0 |
| `proptest` | 1.x | Property-based testing for algorithm correctness | MIT/Apache-2.0 |
| `criterion` | 0.5.x | Benchmarking | Apache-2.0/MIT |
| `pretty_assertions` | 1.x | Readable test assertion diffs | MIT/Apache-2.0 |

### 5.7 Future Dependencies (GUI Phase)

| Crate/Framework | Version | Purpose | License |
|-----------------|---------|---------|---------|
| Tauri | 2.x | Desktop GUI framework (Rust backend + web frontend) | MIT/Apache-2.0 |
| (JS framework TBD) | | GUI frontend (likely Svelte or SolidJS) | |

### 5.8 Build Considerations

- **libgit2:** The `git2` crate bundles and statically links libgit2 by default.
  This simplifies distribution but increases compile time. For development builds,
  consider using a system-installed libgit2 via the `vendored` feature flag.
- **tree-sitter grammars:** Each grammar is a separate C library compiled at build
  time. The initial set of ~20 grammars adds approximately 30-60 seconds to a clean
  build. Consider making language tiers feature-gated:
  - `default` features: Tier 1 languages only
  - `all-languages` feature: all tiers
  - Individual language features: `lang-ruby`, `lang-csharp`, etc.
- **Cross-compilation:** Ensure all dependencies support `x86_64-unknown-linux-gnu`,
  `x86_64-apple-darwin`, `aarch64-apple-darwin`, and `x86_64-pc-windows-msvc`.
  tree-sitter's C compilation may require a C compiler in the cross-compilation
  toolchain.
- **Binary size:** Expected release binary size is ~15-25 MB with all Tier 1
  languages. Strip symbols and use `lto = true` in release profile.

---

## 6. Phased Implementation Plan

### 6.1 Phase 1: MVP -- Core Diff with Intra-Line Highlighting

**Duration:** 4-6 weeks  
**Goal:** A usable diff tool that is better than `diff --color` for everyday use.  
**Dependencies:** None (foundation phase).

| Deliverable | Description | Effort |
|-------------|-------------|--------|
| **D1.1** Project scaffolding | Cargo workspace, CI, linting, test harness | 2 days |
| **D1.2** Input layer | File reader, stdin reader, encoding detection, content-type detection by extension | 3 days |
| **D1.3** Line-level diff engine | Myers and Patience via `similar`, Histogram via `imara-diff`, behind `LineDiffer` trait | 5 days |
| **D1.4** Intra-line token diff | Token splitter, Myers on token sequences, span mapping to byte offsets | 5 days |
| **D1.5** Terminal renderer | ANSI-colored output with intra-line highlighting, context lines, hunk headers | 5 days |
| **D1.6** Unified diff renderer | Standard unified diff output compatible with `patch` | 2 days |
| **D1.7** JSON renderer | Structured JSON output with full change metadata | 2 days |
| **D1.8** Basic whitespace handling | `--ignore-whitespace`, `--ignore-blank-lines`, dimmed whitespace-only changes | 3 days |
| **D1.9** CLI argument parsing | `clap`-based argument handling, `--help`, `--version` | 2 days |
| **D1.10** Configuration system | TOML config file loading, env var overrides, precedence chain | 3 days |
| **D1.11** Side-by-side renderer | Two-column terminal output with aligned changes | 3 days |

**Exit criteria:**
- `HideDiff file_a file_b` produces colored output with intra-line highlighting.
- All three output formats (terminal, unified, JSON) work correctly.
- Performance: <1 second for files up to 10K lines.
- Test coverage >80% for core diff engine.
- Published as a `0.1.0` release on crates.io.

---

### 6.2 Phase 2: Git Integration

**Duration:** 3-4 weeks  
**Goal:** HideDiff works seamlessly as a Git difftool and can diff Git objects directly.  
**Dependencies:** Phase 1 complete.

| Deliverable | Description | Effort |
|-------------|-------------|--------|
| **D2.1** Git object reader | Read blobs, trees, and commits via `git2` | 4 days |
| **D2.2** Git difftool protocol | Support `GIT_EXTERNAL_DIFF` environment variables | 2 days |
| **D2.3** Commit range syntax | Parse and resolve `A..B`, `A...B`, `HEAD~N`, branch names | 3 days |
| **D2.4** Working tree / staged diffs | `--staged`, `--cached`, working tree vs HEAD | 3 days |
| **D2.5** Git setup command | `HideDiff --install-git` configures Git to use HideDiff | 1 day |
| **D2.6** `.gitattributes` support | Respect diff driver configuration | 2 days |
| **D2.7** Multi-file diff | Diff all changed files in a commit or range, with file headers | 3 days |
| **D2.8** Pager integration | Pipe output through configured pager (`less -R` default) | 1 day |

**Exit criteria:**
- `git difftool -t HideDiff` works.
- `HideDiff --git HEAD~3..HEAD -- file.rs` shows the diff with intra-line highlighting.
- `HideDiff --staged` shows staged changes.
- Multi-file diffs show clear file boundaries.

---

### 6.3 Phase 3: Move & Rename Detection

**Duration:** 4-5 weeks  
**Goal:** HideDiff detects and annotates moved blocks and systematic renames.  
**Dependencies:** Phase 1 complete. Phase 2 recommended but not required.

| Deliverable | Description | Effort |
|-------------|-------------|--------|
| **D3.1** Block extraction | Extract contiguous deleted and inserted blocks from diff results | 2 days |
| **D3.2** Exact move detection | Hash-based matching of identical blocks | 3 days |
| **D3.3** Fuzzy move detection | Token fingerprinting, Jaccard similarity, greedy matching | 5 days |
| **D3.4** Move visualization | Color-coding and annotations for moved blocks in all renderers | 4 days |
| **D3.5** Rename detection (statistical) | Detect consistent token replacements across the file | 5 days |
| **D3.6** Rename factoring | Show renames separately, then show remaining semantic diff | 3 days |
| **D3.7** Move/rename in JSON output | Structured move and rename metadata in JSON format | 2 days |
| **D3.8** Configuration & tuning | Configurable thresholds, minimum block sizes, distance limits | 2 days |

**Exit criteria:**
- Moved functions within a file are annotated rather than shown as delete+insert.
- Systematic renames (e.g., `oldName` -> `newName`) are factored out.
- Move detection adds <50% overhead to diff time.
- False positive rate for move detection <5% on a test corpus.

---

### 6.4 Phase 4: Language-Aware / AST Features

**Duration:** 6-8 weeks  
**Goal:** HideDiff uses tree-sitter for structural understanding of code changes.  
**Dependencies:** Phase 1 complete. Phase 3 enhances but is not required.

| Deliverable | Description | Effort |
|-------------|-------------|--------|
| **D4.1** tree-sitter integration | Parse files into ASTs, manage grammar loading | 5 days |
| **D4.2** AST hashing and matching | Implement top-down isomorphic subtree matching | 7 days |
| **D4.3** Bottom-up container mapping | Implement bottom-up matching for container nodes | 5 days |
| **D4.4** Structural edit script | Generate insert/delete/update/move operations from mapping | 5 days |
| **D4.5** Format classification (AST) | Use AST to classify formatting changes with high confidence | 5 days |
| **D4.6** Scope-aware rename detection | Use AST scoping for more accurate rename detection | 4 days |
| **D4.7** External formatter bridge | Integration with external formatters for normalize-then-diff | 3 days |
| **D4.8** Language handler registry | Plugin system for content-type-specific handlers | 3 days |
| **D4.9** Tier 1 language handlers | Full handlers for Rust, Python, JS/TS, C/C++, Java, Go | 8 days |
| **D4.10** Scalability guards | Fallback to line-based diff when AST is too large | 2 days |

**Exit criteria:**
- Structural diff correctly identifies moved AST nodes.
- Format changes in Go/Rust (gofmt/rustfmt-equivalent) are classified as cosmetic.
- Python indentation changes are classified as semantic.
- AST diff completes within 5 seconds for files up to 10K lines.
- Graceful fallback to line-based diff for unsupported languages.

---

### 6.5 Phase 5: Cross-File Analysis

**Duration:** 4-6 weeks  
**Goal:** HideDiff detects code moved between files and finds copy-paste sources.  
**Dependencies:** Phase 2 (Git integration), Phase 3 (move detection).

| Deliverable | Description | Effort |
|-------------|-------------|--------|
| **D5.1** Cross-file move detection | Analyze all changed files in a commit to find inter-file moves | 7 days |
| **D5.2** Copy-paste source detection | Search repository for likely sources of new code blocks | 7 days |
| **D5.3** Cross-file visualization | Clear presentation of cross-file relationships | 4 days |
| **D5.4** Performance optimization | Parallel analysis, caching, index-based search | 5 days |
| **D5.5** Blame integration | Annotate diff with `git blame` information via libgit2 | 4 days |
| **D5.6** Commit message display | Show commit messages as context in multi-commit diffs | 2 days |

**Exit criteria:**
- Extracting a function to a new file is shown as a cross-file move.
- Copy-pasted code from elsewhere in the repo is annotated with its source.
- Analysis of a 100-file commit completes within 30 seconds.
- Blame integration shows author/commit inline with diff.

---

### 6.6 Phase 6: GUI

**Duration:** 8-12 weeks  
**Goal:** Interactive GUI for exploring diffs and repository history.  
**Dependencies:** Phases 1-5 substantially complete.

| Deliverable | Description | Effort |
|-------------|-------------|--------|
| **D6.1** Tauri project setup | Tauri workspace, web frontend scaffolding | 3 days |
| **D6.2** Core-to-GUI bridge | Expose HideDiff-core functionality to the web frontend via Tauri commands | 5 days |
| **D6.3** Side-by-side diff view | Interactive side-by-side diff with syntax highlighting | 10 days |
| **D6.4** Version timeline | Visual commit timeline for a file with click-to-diff | 7 days |
| **D6.5** Interactive filtering | Toggle visibility of cosmetic changes, moves, renames | 5 days |
| **D6.6** Hover details | Hover over moved/renamed/copied blocks to see details | 4 days |
| **D6.7** Search within diff | Search for text within the diff view | 3 days |
| **D6.8** Keyboard navigation | Full keyboard navigation (vim-like and standard) | 3 days |
| **D6.9** Theming | Light/dark themes, customizable colors | 3 days |
| **D6.10** Packaging | Installers for macOS, Windows, Linux | 5 days |

**Exit criteria:**
- GUI launches and displays diffs with all the features of the CLI.
- Version timeline allows navigating file history with click-to-diff.
- Cosmetic changes can be toggled on/off interactively.
- Binary size <50 MB.

---

### 6.7 Phase 7: Three-Way Merge

**Duration:** 4-6 weeks  
**Goal:** HideDiff serves as a Git mergetool with structural merge capabilities.  
**Dependencies:** Phase 1, Phase 2, Phase 4 (for structural merge).

| Deliverable | Description | Effort |
|-------------|-------------|--------|
| **D7.1** Line-based three-way merge | Standard ancestor-based merge algorithm | 5 days |
| **D7.2** Conflict detection & markers | Git-compatible conflict markers | 3 days |
| **D7.3** Three-way diff display | Visual three-way diff (base, ours, theirs) | 5 days |
| **D7.4** Git mergetool integration | Work as `git mergetool -t HideDiff` | 2 days |
| **D7.5** Structural merge enhancement | Use AST awareness to resolve structural non-conflicts | 7 days |
| **D7.6** Interactive conflict resolution (TUI) | TUI mode for resolving conflicts one-by-one | 7 days |

**Exit criteria:**
- `git mergetool -t HideDiff` works for standard merge conflicts.
- Structural merge resolves more conflicts than line-based merge.
- All auto-resolved merges produce correct output on a test corpus.
- Interactive TUI allows selecting resolutions for each conflict.

---

### 6.8 Phase 8: Advanced Features

**Duration:** 8-12 weeks (can be parallelized)  
**Goal:** Clone detection, VCS history analysis, and advanced capabilities.  
**Dependencies:** Various (noted per deliverable).

| Deliverable | Description | Dependencies | Effort |
|-------------|-------------|--------------|--------|
| **D8.1** Clone detection engine | Token-based clone detection with inverted index | Phase 1, Phase 4 | 10 days |
| **D8.2** Clone visualization | Present clone groups as diffs against each other | Phase 1, D8.1 | 5 days |
| **D8.3** Intermediate version analysis | Use VCS history to trace block identity through commits | Phase 2, Phase 3 | 10 days |
| **D8.4** Incremental analysis cache | Cache diff results and clone indexes for fast re-analysis | Phase 2, D8.1 | 5 days |
| **D8.5** LSP integration (experimental) | Provide diff/clone information to editors via LSP | Phase 1 | 7 days |
| **D8.6** Custom output templates | User-defined output formats via templates | Phase 1 | 4 days |
| **D8.7** Diff quality metrics | Score diff readability, suggest better algorithm/settings | Phase 1 | 5 days |

**Exit criteria:**
- Clone detection finds duplicates in a 100K LOC project within 60 seconds.
- Intermediate version analysis produces better move detection for multi-commit ranges.
- Cache reduces repeated analysis time by >80%.

---

### Phase Dependency Graph

```
Phase 1 (MVP)
  |
  +---> Phase 2 (Git) --+---> Phase 5 (Cross-File) --+
  |                      |                             |
  +---> Phase 3 (Moves) -+                             +---> Phase 8 (Advanced)
  |                                                    |
  +---> Phase 4 (AST) ----+---> Phase 7 (Merge) ------+
                           |
                           +---> Phase 6 (GUI) --------+
```

---

## 7. CLI Interface Design

### 7.1 Command-Line Synopsis

```
HideDiff [OPTIONS] [--] <OLD> <NEW>
HideDiff [OPTIONS] --git <COMMIT_RANGE> [-- <PATH>...]
HideDiff [OPTIONS] --staged [-- <PATH>...]
HideDiff [OPTIONS] --merge <ANCESTOR> <OURS> <THEIRS>
HideDiff [OPTIONS] --find-clones <PATH>...
```

### 7.2 Positional Arguments

| Argument | Description |
|----------|-------------|
| `<OLD>` | Path to the old/original file. Use `-` for stdin. |
| `<NEW>` | Path to the new/modified file. Use `-` for stdin (only one can be stdin). |

### 7.3 Primary Options

| Flag | Short | Description | Default |
|------|-------|-------------|---------|
| `--format <FORMAT>` | `-f` | Output format: `terminal`, `unified`, `json`, `side-by-side` | `terminal` (TTY) or `unified` (pipe) |
| `--context <N>` | `-C` | Lines of context around changes | 3 |
| `--algorithm <ALG>` | `-a` | Diff algorithm: `histogram`, `patience`, `myers` | `histogram` |
| `--color <WHEN>` | | Color output: `auto`, `always`, `never` | `auto` |
| `--pager <WHEN>` | | Use pager: `auto`, `always`, `never` | `auto` |

### 7.4 Intra-Line Options

| Flag | Description | Default |
|------|-------------|---------|
| `--word-diff` | Enable word-level (token) intra-line diff | on |
| `--char-diff` | Use character-level intra-line diff | off |
| `--no-inline` | Disable intra-line highlighting entirely | off |

### 7.5 Format-Aware Options

| Flag | Description | Default |
|------|-------------|---------|
| `--normalize` | Normalize both files before diffing (mode A) | off |
| `--classify-format` | Classify changes as semantic or cosmetic (mode B) | off |
| `--ignore-whitespace` | `-w` | Ignore all whitespace differences | off |
| `--ignore-blank-lines` | Ignore changes in blank lines | off |
| `--ignore-line-breaks` | Ignore line-break differences (useful for prose) | off |
| `--formatter <CMD>` | External formatter command for normalization | per content type |
| `--dim-cosmetic` | Dim cosmetic changes instead of hiding them | on (when classify-format is enabled) |

### 7.6 Move & Rename Options

| Flag | Description | Default |
|------|-------------|---------|
| `--detect-moves` | Enable intra-file move detection | off |
| `--detect-moves-threshold <F>` | Similarity threshold for fuzzy moves (0.0-1.0) | 0.7 |
| `--detect-moves-min-lines <N>` | Minimum block size for move detection | 3 |
| `--factor-renames` | Detect and factor out systematic renames | off |
| `--detect-cross-file-moves` | Enable cross-file move detection | off |
| `--detect-copies` | Enable copy-paste source detection | off |

### 7.7 Git Options

| Flag | Description | Default |
|------|-------------|---------|
| `--git <RANGE>` | Diff using Git commit range | |
| `--staged` / `--cached` | Diff staged changes against HEAD | |
| `--blame` | Annotate diff with Git blame information | off |
| `--show-commits` | Show commit messages in multi-commit diffs | off |
| `--install-git` | Configure Git to use HideDiff as difftool | |

### 7.8 Advanced Options

| Flag | Description | Default |
|------|-------------|---------|
| `--merge <A> <O> <T>` | Three-way merge mode | |
| `--merge3 <A> <O> <T>` | Three-way diff display mode | |
| `--find-clones <PATH>...` | Clone detection mode | |
| `--clone-min-tokens <N>` | Minimum tokens for clone detection | 50 |
| `--clone-threshold <F>` | Similarity threshold for clone detection | 0.8 |
| `--use-intermediates` | Use intermediate VCS versions for better matching | off |
| `--language <LANG>` | Force language for parsing (overrides auto-detect) | auto |
| `--no-ast` | Disable AST-based features even if grammar available | off |

### 7.9 Meta Options

| Flag | Short | Description |
|------|-------|-------------|
| `--help` | `-h` | Show help |
| `--version` | `-V` | Show version |
| `--dump-config` | | Show effective configuration |
| `--list-languages` | | List supported languages and their status |
| `--verbose` | `-v` | Increase verbosity (can be repeated: `-vv`, `-vvv`) |

### 7.10 Configuration File Format

Configuration file location: `~/.config/HideDiff/config.toml` (XDG) or `~/.HideDiff.toml`.
Per-repository: `.HideDiff.toml` in repository root.

```toml
# HideDiff configuration

[display]
# Default output format
format = "terminal"
# Lines of context
context = 3
# Color mode: auto, always, never
color = "auto"
# Pager command (empty string disables pager)
pager = "less -RFX"
# Tab width for display
tab_width = 4

[diff]
# Default algorithm: histogram, patience, myers
algorithm = "histogram"
# Enable intra-line diff by default
inline = true
# Intra-line mode: word, char
inline_mode = "word"

[format_aware]
# Enable format classification by default
classify = false
# Dim cosmetic changes when classification is active
dim_cosmetic = true
# Ignore whitespace-only changes by default
ignore_whitespace = false

[moves]
# Enable move detection by default
detect = false
# Similarity threshold
threshold = 0.7
# Minimum lines for a moved block
min_lines = 3

[renames]
# Enable rename detection by default
detect = false

[git]
# Show blame by default
blame = false
# Show commits by default
show_commits = false

[colors]
# Terminal colors (256-color or RGB hex)
added = "#22aa22"
deleted = "#aa2222"
modified = "#aaaa22"
moved = "#2222aa"
cosmetic = "#666666"
context = "#888888"
line_number = "#555555"

[formatters]
# External formatters for normalize-then-diff mode
# Each entry: language = { command = "...", args = ["..."] }
rust = { command = "rustfmt", args = ["--edition", "2021"] }
python = { command = "black", args = ["-q", "-"] }
go = { command = "gofmt" }
javascript = { command = "prettier", args = ["--parser", "babel"] }
typescript = { command = "prettier", args = ["--parser", "typescript"] }
c = { command = "clang-format" }
cpp = { command = "clang-format" }

[languages]
# Per-language overrides
# [languages.python]
# algorithm = "patience"
# inline_mode = "word"
```

### 7.11 Git Difftool Integration

HideDiff integrates with Git via two mechanisms:

**Mechanism 1: GIT_EXTERNAL_DIFF protocol**

When invoked as a Git external diff, Git passes 7 arguments:
```
HideDiff <path> <old-file> <old-hex> <old-mode> <new-file> <new-hex> <new-mode>
```

HideDiff detects this mode by the argument count and format, and adjusts behavior
accordingly (e.g., using the path for language detection, the hex for display).

**Mechanism 2: difftool protocol**

When invoked via `git difftool`, Git sets environment variables `LOCAL` and `REMOTE`
pointing to temporary files. HideDiff uses these when present.

**Setup command:**

`HideDiff --install-git` writes the following to `~/.gitconfig`:

```ini
[diff]
    tool = HideDiff
[difftool "HideDiff"]
    cmd = HideDiff \"$LOCAL\" \"$REMOTE\"
[difftool]
    prompt = false
[merge]
    tool = HideDiff
[mergetool "HideDiff"]
    cmd = HideDiff --merge \"$BASE\" \"$LOCAL\" \"$REMOTE\" -o \"$MERGED\"
    trustExitCode = true
```

### 7.12 Output Format Examples

**Terminal output (default):**

```
--- a/src/main.rs
+++ b/src/main.rs
@@ -10,7 +10,7 @@

 fn calculate_total(items: &[Item]) -> f64 {
     let mut total = 0.0;
-    for item in items.iter() {
+    for item in items {
         total += item.price * item.quantity as f64;
     }
-    return total;
+    total
 }
```

Where `items.iter()` would show `items` in normal color and `.iter()` highlighted
as deleted; and `return ` highlighted as deleted in the last change.

**JSON output:**

```json
{
  "old_path": "src/main.rs",
  "new_path": "src/main.rs",
  "content_type": { "code": { "language": "rust" } },
  "hunks": [
    {
      "old_start": 10,
      "old_count": 7,
      "new_start": 10,
      "new_count": 7,
      "changes": [
        {
          "kind": "modified",
          "old_line": 12,
          "new_line": 12,
          "old_text": "    for item in items.iter() {",
          "new_text": "    for item in items {",
          "spans": [
            { "start": 19, "end": 31, "kind": "delete" },
            { "start": 19, "end": 24, "kind": "insert" }
          ],
          "classification": {
            "whitespace_only": false,
            "cosmetic": false,
            "semantic": true,
            "confidence": 1.0
          }
        }
      ]
    }
  ],
  "stats": {
    "lines_added": 0,
    "lines_deleted": 0,
    "lines_modified": 2,
    "lines_moved": 0,
    "lines_cosmetic": 0,
    "lines_semantic": 2
  }
}
```

---

## 8. Key Design Decisions & Trade-offs

### 8.1 Language Choice: Rust

| Considered | Pros | Cons | Decision |
|------------|------|------|----------|
| **Rust** | Memory safety without GC, excellent for CLI tools, proven ecosystem (delta, difftastic, gitoxide), first-class tree-sitter bindings, Tauri for GUI | Steeper learning curve, longer compile times | **Chosen** |
| C++ | Maximum performance, user's initial suggestion, large ecosystem | Memory safety risks, no package manager, complex build systems | Rejected: Rust matches C++ performance with much better safety and ecosystem |
| Go | Fast compilation, easy deployment, good CLI ecosystem | GC pauses problematic for large diffs, weaker type system, poor tree-sitter bindings | Rejected |
| Python | Rapid prototyping, tree-sitter bindings available | Too slow for core diff algorithms on large files | Rejected |

**Rationale:** Rust was chosen because delta and difftastic have demonstrated that
Rust is the right language for high-performance diff tools. The `similar`, `imara-diff`,
`git2`, and `tree-sitter` crates provide a mature foundation. Rust's ownership model
prevents the memory bugs that would be likely in a C++ implementation of complex
graph algorithms (AST matching, clone detection).

### 8.2 Build Approach: New Tool Using Libraries

| Considered | Pros | Cons | Decision |
|------------|------|------|----------|
| **New tool, reuse libraries** | Full control over architecture, can compose best-of-breed libraries, clean API design | More work than forking, need to write glue code | **Chosen** |
| Fork difftastic | Head start on tree-sitter integration, 30+ languages | Difftastic's O(L*R) algorithm is a fundamental limitation; architecture not designed for our pipeline | Rejected |
| Fork delta | Excellent rendering code | Delta is a pager/formatter, not a diff engine; wrong starting point | Rejected |
| Wrap existing tools | Least effort | Fragile, version coupling, performance overhead of process spawning, limited customization | Rejected |

**Rationale:** HideDiff's pipeline architecture (input -> normalize -> diff -> classify ->
render) is fundamentally different from any existing tool. Forking would mean fighting
the existing architecture. Using libraries (`similar` for diff, `tree-sitter` for
parsing, `git2` for Git) gives us the right primitives without the wrong abstractions.

### 8.3 Diff Algorithm Default: Histogram

**Rationale:** Histogram diff, as used by Git (`git diff --histogram`), produces the
most readable results for code because it deprioritizes high-frequency tokens (like
`{`, `}`, blank lines) that cause Myers to produce confusing alignments. For the
common case of diffing code, this produces noticeably better output. Patience diff
is available as an alternative and is better for prose. Myers is available as a
fallback for maximum compatibility.

### 8.4 Format-Aware: Both Modes

| Considered | Pros | Cons | Decision |
|------------|------|------|----------|
| Normalize-then-diff only | Simple, deterministic, one code path | Loses information about what formatting changed; requires formatter | Rejected as sole approach |
| Diff-then-annotate only | Preserves all changes, flexible display | More complex classification, less accurate without formatter | Rejected as sole approach |
| **Both modes, user-selectable** | Maximum flexibility, each mode has clear use cases | More code to maintain, potential user confusion | **Chosen** |

**Rationale:** Normalize-then-diff is ideal when the user simply does not care about
formatting changes and wants a clean semantic diff. Diff-then-annotate is ideal when
the user wants to see all changes but with cosmetic changes visually de-emphasized.
Both are valuable, and neither subsumes the other.

### 8.5 GUI Framework: Tauri (Future)

| Considered | Pros | Cons | Decision |
|------------|------|------|----------|
| **Tauri** | Rust backend (reuse HideDiff-core directly), 10-20x smaller than Electron, system webview | Younger ecosystem, cross-platform webview inconsistencies | **Chosen** |
| Electron | Mature, well-known, consistent rendering | 100+ MB binary, high memory usage, JavaScript backend cannot directly call HideDiff-core | Rejected |
| Native (GTK/Qt/Cocoa) | Best performance, native look | Different toolkit per platform, massive effort, no Rust ecosystem | Rejected |
| egui (Rust-native) | Pure Rust, no web dependency | Limited rich text rendering, immature for complex UIs | Considered for TUI; rejected for main GUI |

**Rationale:** Tauri's architecture is ideal for HideDiff because the heavy computation
happens in Rust (where HideDiff-core already lives) and only rendering is delegated to
the web layer. This avoids the serialization overhead of Electron's IPC while
providing rich UI capabilities for diff visualization.

### 8.6 AST Parsing: tree-sitter (Not Custom Parsers)

**Rationale:** tree-sitter provides incremental, error-tolerant parsing for 100+
languages with a single API. Writing custom parsers for even 5 languages would
consume more effort than the entire rest of the project. difftastic has proven that
tree-sitter works well for structural diffing. The main limitation (no semantic
analysis like type resolution) does not affect our use cases.

### 8.7 Clone Detection: Token-Based (Not AST-Based)

| Considered | Pros | Cons | Decision |
|------------|------|------|----------|
| **Token-based (SourcererCC-style)** | Scales to large codebases, language-agnostic, well-studied | Misses structural clones that look different at token level | **Chosen** |
| AST-based (Deckard-style) | Catches structural clones | Slow, requires full AST, limited language support | Rejected as primary approach |
| Hybrid | Best detection rate | Complex, slow | Considered for future enhancement |

**Rationale:** Token-based clone detection with inverted index scaling (SourcererCC
approach) has been proven to handle 250M LOC. For HideDiff's use case (project-level
clone detection, typically <1M LOC), this provides ample headroom with fast results.
AST-based refinement can be added later for higher precision.

### 8.8 Error Handling Strategy

- **HideDiff-core (library):** Uses `thiserror` with typed error enums. Every public
  function returns `Result<T, HidediffError>`. No panics in library code.
- **HideDiff-cli (binary):** Uses `anyhow` for ergonomic error handling. Errors are
  printed to stderr with context. Exit codes follow Unix convention (0 = identical,
  1 = differences found, 2 = error).

### 8.9 Performance Strategy

| Technique | Where Applied |
|-----------|---------------|
| Memory-mapped I/O | Large file reading (>1 MB) |
| Line hashing | Pre-filtering unchanged regions for large files |
| Parallel processing | Multi-file diffs (via rayon) |
| Lazy AST parsing | Only parse when AST features are requested |
| Algorithm timeout | Fall back to simpler algorithm if time budget exceeded |
| Streaming output | Begin rendering before entire diff is computed |
| Incremental caching | Cache intermediate results for repeated analysis |

**Performance targets:**

| Scenario | Target |
|----------|--------|
| Two 1K-line files, basic diff | <100ms |
| Two 10K-line files, basic diff | <500ms |
| Two 10K-line files, with move detection | <1s |
| Two 10K-line files, full AST diff | <5s |
| 100-file commit, cross-file analysis | <30s |
| Clone detection, 100K LOC project | <60s |

---

## 9. Open Questions

### 9.1 Algorithm Questions

| # | Question | Impact | Proposed Resolution |
|---|----------|--------|---------------------|
| Q1 | What is the right minimum block size for move detection? 3 lines may be too aggressive for some codebases, too conservative for others. | Move detection precision/recall | Start with 3, make configurable, tune based on user feedback and testing on open-source projects. |
| Q2 | For format classification, how do we handle languages without a canonical formatter? | Format-aware feature completeness | Use heuristic classification (whitespace analysis) as fallback. Crowdsource community-maintained rules. |
| Q3 | Should AST-based diff be opt-in or opt-out? It is slower but more accurate for structural changes. | Default user experience | Start as opt-in (`--ast`), switch to opt-out once performance is acceptable (<2x overhead). |
| Q4 | How should we handle files that tree-sitter fails to parse (syntax errors, unsupported language)? | Robustness | Fall back gracefully to line-based diff. Show a one-line notice that AST features are unavailable. |
| Q5 | For fuzzy move detection, should we use Jaccard similarity on token sets, cosine similarity on token frequency vectors, or both? | Move detection accuracy | Prototype both, benchmark on a corpus of real refactorings. Jaccard is simpler, cosine handles frequency better. |

### 9.2 UX Questions

| # | Question | Impact | Proposed Resolution |
|---|----------|--------|---------------------|
| Q6 | How should moved blocks be visually linked in terminal output? Color-coding alone may be insufficient with many moves. | Readability of move annotations | Use color + numbered labels (e.g., "[Move 1]"). In side-by-side view, draw connecting lines (Unicode box-drawing). Prototype and user-test. |
| Q7 | Should HideDiff page output by default (like `delta` does) or not page (like `diff`)? | User workflow | Page by default when output exceeds terminal height, matching delta's behavior. `--no-pager` to disable. |
| Q8 | What should the default behavior be when no flags are specified? Show all changes? Dim cosmetic? | First-run experience | Show all changes with no classification by default (fast, predictable). Cosmetic dimming requires `--classify-format` or config. |

### 9.3 Technical Questions

| # | Question | Impact | Proposed Resolution |
|---|----------|--------|---------------------|
| Q9 | Should tree-sitter grammars be bundled (static linking) or loaded dynamically at runtime? | Binary size vs. flexibility | Bundle Tier 1, dynamic-load Tier 2+. Provide `HideDiff --install-grammar <lang>` for additional grammars. |
| Q10 | How do we handle encoding detection for non-UTF-8 files? | International file support | Use `encoding_rs` for detection. Convert to UTF-8 internally. Warn user if conversion is lossy. |
| Q11 | Should the JSON output format be versioned? | API stability for tooling consumers | Yes. Include a `"version": 1` field. Document the schema. Commit to backward compatibility within major versions. |
| Q12 | How do we handle very large files (>100K lines)? | Performance and memory | Memory-map the file. Use line-hash pre-filtering to identify unchanged regions. Diff only changed regions. Set a configurable hard limit (default 1M lines) with a clear error message. |

### 9.4 Ecosystem Questions

| # | Question | Impact | Proposed Resolution |
|---|----------|--------|---------------------|
| Q13 | Should HideDiff support non-Git VCS (Mercurial, SVN, Pijul)? | User base | Design VCS abstraction layer from the start, implement only Git. Document the trait for community contributions. |
| Q14 | Should there be an HideDiff library API for programmatic use by other tools? | Ecosystem growth | Yes, HideDiff-core is designed as a library from day one. Publish to crates.io with stable API after Phase 2. |
| Q15 | Should HideDiff support Windows? | User base | Yes, from Phase 1. Use `crossterm` for terminal abstraction. CI tests on Windows. Avoid Unix-specific assumptions. |

---

## 10. References

### 10.1 Papers

| Paper | Authors | Year | Relevance |
|-------|---------|------|-----------|
| "An O(ND) Difference Algorithm and Its Variations" | Eugene W. Myers | 1986 | Foundation diff algorithm (Myers) |
| "Patience Diff Advantages" | Bram Cohen | 2005 | Patience diff algorithm design |
| "Fine-grained and Accurate Source Code Differencing" | Falleri, Morandat, Blanc, Martinez, Monperrus | 2014 | GumTree AST diff algorithm (top-down + bottom-up matching) |
| "SourcererCC: Scaling Code Clone Detection to Big Code" | Sajnani, Saini, Svajlenko, Roy, Lopes | 2016 | Scalable token-based clone detection |
| "A Survey on Software Clone Detection Research" | Roy, Cordy, Koschke | 2009 | Comprehensive clone detection survey |
| "Hyperparameter Optimization for AST Differencing" | Martinez, Falleri, Monperrus | 2021 | Tuning GumTree parameters |
| "Semantic Diff: A Tool for Summarizing the Semantic Effects of Modifications" | Jackson, Ladd | 1994 | Early work on semantic (vs syntactic) diffing |

### 10.2 Existing Tools

| Tool | URL | Relevance |
|------|-----|-----------|
| **difftastic** | https://github.com/Wilfred/difftastic | Rust tree-sitter structural diff; reference for tree-sitter integration |
| **delta** | https://github.com/dandavison/delta | Rust diff pager; reference for terminal rendering, intra-line highlighting |
| **similar** (crate) | https://github.com/mitsuhiko/similar | Rust diff library (Myers, Patience) |
| **imara-diff** (crate) | https://github.com/pascalkuthe/imara-diff | Rust diff library (Myers, Histogram), used by gitoxide |
| **GumTree** | https://github.com/GumTreeDiff/gumtree | Java AST diff; reference implementation of the GumTree algorithm |
| **SemanticDiff** | https://semanticdiff.com | Commercial language-aware diff; reference for UX goals |
| **SemanticMerge** | https://semanticmerge.com | Commercial semantic merge; reference for structural merge goals |
| **tree-sitter** | https://tree-sitter.github.io/tree-sitter/ | Incremental parsing library |
| **git2-rs** | https://github.com/rust-lang/git2-rs | Rust libgit2 bindings |
| **Tauri** | https://tauri.app | Desktop application framework (Rust + web) |
| **gitoxide** | https://github.com/Byron/gitoxide | Pure-Rust Git implementation; reference for Git integration patterns |

### 10.3 Specifications & Standards

| Specification | Relevance |
|---------------|-----------|
| [Unified Diff Format](https://www.gnu.org/software/diffutils/manual/html_node/Unified-Format.html) | Output format for `--format=unified` |
| [Git External Diff](https://git-scm.com/docs/git#Documentation/git.txt-codeGITEXTERNALDIFFcode) | Protocol for Git difftool integration |
| [Git Mergetool](https://git-scm.com/docs/git-mergetool) | Protocol for Git mergetool integration |
| [XDG Base Directory](https://specifications.freedesktop.org/basedir-spec/latest/) | Configuration file location |
| [TOML Specification](https://toml.io/en/v1.0.0) | Configuration file format |
| [Unicode Text Segmentation (UAX #29)](https://unicode.org/reports/tr29/) | Word boundary detection for token-level diff |

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **Cosmetic change** | A change that affects only visual presentation, not program behavior or content meaning |
| **Semantic change** | A change that affects program behavior or content meaning |
| **Hunk** | A contiguous group of changes in a diff, with surrounding context lines |
| **Intra-line diff** | Highlighting specific words or characters within a changed line, rather than the entire line |
| **Move detection** | Identifying when content is relocated rather than deleted and separately inserted |
| **Clone** | A block of code that is duplicated or nearly duplicated elsewhere |
| **Type-1 clone** | Exact duplicate (after whitespace normalization) |
| **Type-2 clone** | Structurally identical with renamed identifiers or changed literals |
| **Type-3 clone** | Near-miss with additions, deletions, or modifications |
| **Normalize-then-diff** | Reformatting both files to canonical style before diffing, hiding all cosmetic changes |
| **Diff-then-annotate** | Performing a standard diff and then classifying each change as semantic or cosmetic |
| **Content handler** | A pluggable component that provides language/format-specific normalization and classification |
| **Position map** | A mapping between byte positions in normalized and original text, enabling display of results against original source |

---

## Appendix B: Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Files are identical (no differences found) |
| 1 | Differences found (normal operation) |
| 2 | Error (file not found, permission denied, invalid arguments, etc.) |
| 130 | Interrupted (SIGINT / Ctrl-C) |

This matches the convention used by GNU diff and Git diff.

---

## Appendix C: Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `HIDEDIFF_CONFIG` | Override config file path | `/path/to/config.toml` |
| `HIDEDIFF_PAGER` | Override pager command | `less -RFX` |
| `HIDEDIFF_COLOR` | Override color mode | `always`, `never`, `auto` |
| `HIDEDIFF_DEFAULT_ALGORITHM` | Override default algorithm | `patience` |
| `NO_COLOR` | Disable colors (standard) | (any value) |
| `TERM` | Terminal type (used for capability detection) | `xterm-256color` |
| `GIT_EXTERNAL_DIFF` | Set by Git when using HideDiff as external diff | (set by Git) |
| `LOCAL` / `REMOTE` | Set by Git difftool | (set by Git) |
| `BASE` / `MERGED` | Set by Git mergetool | (set by Git) |

---

*End of design document.*
