# Plan: Foundational Setup for hidediff

## Context

The hidediff project (formerly "ndiff") is an advanced differencing tool in Rust, currently in the documentation/planning phase with no code, no git repo, and no scaffolding. Before implementation can begin, we need foundational infrastructure: finalized name, license, project CLAUDE.md, and a GitHub repository. This batch covers those four tasks.

**Decisions made:**
- **Name**: `hidediff` (available on crates.io, GitHub, and zero search conflicts)
- **License**: Dual MIT/Apache-2.0 (Rust ecosystem standard)
- **Rename existing docs**: Yes, update all "ndiff" references to "hidediff" now
- **`.claude/` in repo**: Yes, commit it

---

## Step 0: Rename local directory

Rename `/home/nat/ndiff` to `/home/nat/hidediff` before any other work.

## Step 1: Rename "ndiff" to "hidediff" in existing docs

Rename file: `docs/NDIFF_CONCEPT.md` -> `docs/HIDEDIFF_CONCEPT.md`

Update all occurrences of `ndiff` to `hidediff` in these files:

| File | Approx. occurrences |
|------|---------------------|
| `docs/DESIGN.md` | ~80+ (pervasive: crate names, CLI examples, config paths, etc.) |
| `docs/HIDEDIFF_CONCEPT.md` | 1 (line 4, task item) |
| `docs/TASKS_IDEAS.md` | ~3 |
| `docs/TESTING_METHODOLOGY.md` | 0 (no project name references) |

Key renames in DESIGN.md:
- `ndiff` -> `hidediff` (tool name, CLI invocations, section headers)
- `ndiff-core` -> `hidediff-core` (crate name)
- `ndiff-cli` -> `hidediff-cli` (crate name)
- `ndiff-tui` -> `hidediff-tui` (crate name)
- `ndiff-gui` -> `hidediff-gui` (crate name)
- `NdiffError` -> `HidediffError` (Rust type name)
- `~/.config/ndiff/` -> `~/.config/hidediff/` (config paths)
- `.ndiff.toml` -> `.hidediff.toml` (config file name)
- `NDIFF_*` env vars -> `HIDEDIFF_*` env vars

Also update `docs/DESIGN.md` line 6: `**Authors:** [Your Name]` -> `**Authors:** Nathaniel Crutcher`

## Step 2: Create license files

**Create `/home/nat/hidediff/LICENSE-MIT`** with standard MIT text, copyright `2026 Nathaniel Crutcher`.

**Create `/home/nat/hidediff/LICENSE-APACHE`** with the full Apache License 2.0 text, copyright `2026 Nathaniel Crutcher`.

## Step 3: Create CLAUDE.md

**Create `/home/nat/hidediff/CLAUDE.md`** containing:
- Project name and one-line description (hidediff)
- Key documentation references (DESIGN.md, HIDEDIFF_CONCEPT.md, TASKS_IDEAS.md, TESTING_METHODOLOGY.md)
- Technology stack summary (Rust, key crates)
- Architecture overview (workspace structure, crate layout) — concise, referencing DESIGN.md Section 3
- Processing pipeline summary (Input -> Normalize -> Diff -> Classify -> Render)
- Build/test/lint commands
- Coding conventions (thiserror in library, anyhow in CLI, no panics in library, exit codes)
- License note
- Testing methodology section — verbatim from `docs/CLAUDE_MD_TESTING_SECTION.md` lines 7-43

Source files:
- `docs/CLAUDE_MD_TESTING_SECTION.md` (lines 7-43 for the testing section)
- `docs/DESIGN.md` (Sections 3, 5, 8.8 for architecture, tech stack, error handling)

## Step 4: Create .gitignore

**Create `/home/nat/hidediff/.gitignore`** covering:
- Rust/Cargo: `/target/`, `**/*.rs.bk`
- IDE: `.idea/`, `.vscode/`, swap files
- OS: `.DS_Store`, `Thumbs.db`
- Environment: `.env`
- Coverage: `tarpaulin-report.html`, `coverage/`
- Benchmarks: `target/criterion/`

Note: Do NOT exclude `Cargo.lock` — it should be committed for workspaces with binary crates (per Rust convention). It doesn't exist yet, so this is future-proofing.

## Step 5: Initialize git and create GitHub repo

1. `git init` in `/home/nat/hidediff`
2. Create GitHub repo `NatCrutcher/hidediff` (public, no auto-init) via GitHub MCP tool
3. Stage all files:
   - `docs/DESIGN.md`, `docs/HIDEDIFF_CONCEPT.md`, `docs/TASKS_IDEAS.md`, `docs/TESTING_METHODOLOGY.md`, `docs/CLAUDE_MD_TESTING_SECTION.md`
   - `CLAUDE.md`, `LICENSE-MIT`, `LICENSE-APACHE`, `.gitignore`
   - `.claude/settings.local.json`
4. Initial commit with descriptive message
5. `git remote add origin` + `git push -u origin main`

---

## Verification

- [ ] All docs use "hidediff" (grep for "ndiff" should return zero false positives)
- [ ] `LICENSE-MIT` and `LICENSE-APACHE` exist with correct copyright
- [ ] `CLAUDE.md` exists, is concise, and includes testing section
- [ ] `.gitignore` covers Rust artifacts
- [ ] GitHub repo `NatCrutcher/hidediff` is public and accessible
- [ ] All files are present in the repo on GitHub
- [ ] `git log` shows clean initial commit
