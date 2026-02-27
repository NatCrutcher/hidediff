# Testing (CLAUDE.md Section)

Paste the following into your project's CLAUDE.md file.

---

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
