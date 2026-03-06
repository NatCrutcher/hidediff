# HideDiff

Advanced differencing tool built in Rust. Goes beyond line-based diff with intra-line highlighting, format-aware diffing, move detection, cross-file analysis, VCS integration, and structural merges. The key new feature is the ability to hide certain types of changes, like moves, reformatting, and renaming.

## Documentation

- `docs/DESIGN.md` — Design document (architecture, algorithms, requirements, phased plan)
- `docs/HIDEDIFF_CONCEPT.md` — Original feature goals and research notes
- `docs/TASKS_IDEAS.md` — Task backlog and ideas
- `docs/TESTING_METHODOLOGY.md` — Testing specification
- `docs/*.md` — Additional topic specific documentation

## Technology Stack

- **Language:** Rust (2024 edition, MSRV 1.90+)
- **Key crates:** `similar`, `imara-diff` (diff algorithms), `tree-sitter` (AST parsing), `git2` (Git integration), `clap` (CLI), `serde`/`toml` (config), `rayon` (parallelism)
- **GUI (future):** Tauri

## Architecture

Cargo workspace with four crates (see DESIGN.md Section 3 for full details):

- **`hidediff-core`** — Core library. No I/O, no UI. Contains: `input/`, `normalize/`, `diff/`, `classify/`, `merge/`, `analysis/`, `vcs/`
- **`hidediff-cli`** — CLI frontend. Argument parsing, config loading, output rendering.
- **`hidediff-tui`** — TUI frontend (future, Phase 4+)
- **`hidediff-gui`** — GUI frontend (future, Phase 6)

### Processing Pipeline

```
Input -> Normalize -> Diff -> Classify -> Render
```

1. **Input:** Read files, detect content type, handle encoding
2. **Normalize:** Whitespace normalization, formatting, line endings
3. **Diff:** Line-level, token-level, or AST-based differencing
4. **Classify:** Whitespace-only, moves, renames, semantic vs. cosmetic
5. **Render:** Terminal (ANSI), unified diff, JSON, side-by-side

## Build / Test / Lint

```bash
cargo build --workspace
cargo test --all-features
cargo clippy --all-targets --all-features -- -D warnings
cargo fmt --all -- --check
```

## Conventions

- **Error handling:** `thiserror` with typed enums in `hidediff-core`; `anyhow` in `hidediff-cli`. Every public library function returns `Result<T, HidediffError>`. No panics in library code.
- **Exit codes:** 0 = identical, 1 = differences found, 2 = error
- **Config precedence:** CLI flags > env vars (`HIDEDIFF_*`) > config file (`~/.config/hidediff/config.toml`) > defaults
- **Per-repo config:** `.hidediff.toml` in repository root

## License

Licensed under MIT

## Testing Methodology

See `TESTING_METHODOLOGY.md` for the full specification. Key rules:

### Separation of Concerns
- **NEVER write implementation and tests in the same response.** Always separate them into distinct prompts.
- When writing tests, think adversarially — "what could go wrong?" not "does this code do what it does?"
- When asked to test existing code, do not restate implementation logic as assertions.

### Tier System
- **Tier 1 (core domain, public interfaces, traits, error types, unsafe):** Write tests BEFORE implementation. Tests are specifications.
- **Tier 2 (CLI, config, glue code, wrappers):** Implement first, then write tests in a separate prompt focused on catching real bugs.
- **Tier 3 (exploratory/prototype):** Defer testing but add `// TODO: add tests` stubs. Must promote to Tier 1/2 before merging to main.

### Test Types (in priority order)
1. **Integration tests** in `tests/` — organized by user-facing workflow, not by module. Use only public API surfaces.
2. **Property-based tests** using `proptest` — required for data structures, parsers, serializers, and any broad-input-domain function. Always check: round-trip, invariant preservation, boundary conditions.
3. **Unit tests** in `#[cfg(test)] mod tests` — focus on error variant coverage and boundary conditions.
4. **Doc tests** — for public API functions, demonstrating correct usage.

### Required Checks
All code must pass before committing:
```bash
cargo test --all-features
cargo clippy --all-targets --all-features -- -D warnings
cargo fmt --all -- --check
```

### Anti-Patterns
- No tautological tests (tests that mirror implementation logic)
- No `#[should_panic]` — use `assert!(result.is_err())` with error variant matching
- No `unwrap()` in production code without a corresponding test that exercises the panic path
- No test functions exceeding ~30 lines — split them

### Proptest
When creating new data types, derive or implement `Arbitrary` for them. Default to property-based tests for anything involving data transformation. CI runs with `PROPTEST_CASES=500`.
