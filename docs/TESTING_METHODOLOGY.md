# Testing Methodology

## Philosophy

This project follows a **hybrid testing methodology** optimized for AI-assisted development with Claude Code. Rather than strict test-driven development, we separate test authoring from implementation authoring to avoid tautological tests — where an AI writes tests that merely confirm its own implementation rather than catching real defects.

The core principle: **tests are specifications, not afterthoughts.** Even when written after initial implementation, tests should be authored in a distinct phase with adversarial intent — asking "what could go wrong?" rather than "does this code do what it does?"

## Testing Tiers

### Tier 1: Core Domain & Public Interfaces — Tests First

For modules that other code depends on — data models, trait definitions, public API surfaces, state machines, and business logic — write tests before or concurrently with implementation.

**Workflow:**

1. **Define the interface.** Write the function/trait signature with `todo!()` or `unimplemented!()` bodies.
2. **Write tests in a separate prompt.** Ask Claude to write tests against the signature, explicitly requesting edge cases, error paths, and boundary conditions. Do not provide the implementation.
3. **Review the tests yourself.** This is where your engineering judgment is most valuable. Are the invariants correct? Are the edge cases the right ones? Revise as needed.
4. **Implement.** In a new prompt, ask Claude to implement against the existing tests. Run `cargo test` after each implementation pass.
5. **Refine.** If tests pass trivially or miss important cases discovered during implementation, add targeted tests.

**What qualifies as Tier 1:**

- Trait definitions and their implementations
- Error types and error propagation logic
- State machines and transition logic
- Serialization/deserialization contracts
- Any module with more than two downstream dependents
- Anything involving `unsafe` code

### Tier 2: Infrastructure & Glue Code — Implement Then Test

For straightforward code where correct behavior is obvious — CLI parsing, configuration loading, database query wrappers, logging setup — implement and test in a single pass, but always in separate prompts.

**Workflow:**

1. **Implement.** Ask Claude to write the module.
2. **Test in a separate prompt.** Ask Claude to write tests for the module, emphasizing: "Write tests that could catch real bugs, not tests that confirm the implementation." Provide the implementation for reference but instruct Claude to think adversarially.
3. **Review.** Verify tests exercise error paths and aren't simply restating the implementation logic.

**What qualifies as Tier 2:**

- CLI argument parsing and validation
- Configuration file loading
- Logging and telemetry setup
- Simple data transformations with well-defined inputs/outputs
- Thin wrappers around external crates

### Tier 3: Exploratory & Prototype Code — Deferred Testing

During early exploration — testing crate compatibility, prototyping async patterns, evaluating borrow checker constraints — defer formal testing. Add tests once the approach stabilizes.

**Constraints even during exploration:**

- Code must compile and pass `cargo clippy`
- Add `#[cfg(test)]` module stubs with `// TODO: add tests once approach stabilizes`
- Convert to Tier 1 or Tier 2 before merging to main

## Test Types

### Unit Tests

Place in `#[cfg(test)] mod tests` within the source file. Focus on:

- Individual function correctness
- Error variant coverage (every `Err` path should have a test)
- Boundary conditions for numeric types, string handling, and collection sizes
- `Option` handling — test both `Some` and `None` paths

### Integration Tests

Place in `tests/` directory. These are often **more valuable** than unit tests for Rust applications because they exercise the borrow checker and lifetime constraints across module boundaries.

**Structure integration tests around user-facing workflows:**

```
tests/
├── common/
│   └── mod.rs          # Shared test fixtures and helpers
├── workflow_create.rs  # Tests the "create" user workflow end-to-end
├── workflow_update.rs  # Tests the "update" user workflow end-to-end
└── error_recovery.rs   # Tests error handling across module boundaries
```

**Guidelines:**

- Each integration test file should test a coherent workflow, not a single module
- Use the public API surface only — if you need to reach into internals, that's a sign the public API is incomplete
- Test error propagation across module boundaries (this is where `?` chains and `From` implementations get exercised)
- Include at least one "happy path" and one "degraded path" per workflow

### Property-Based Tests

Use `proptest` for data structures, parsers, serializers, and any function with a broad input domain. Property-based tests catch edge cases that hand-written tests miss — off-by-one errors, Unicode handling, integer overflow, empty collections.

**When to use property-based tests:**

- Any function that transforms data: `f(input) -> output` where the relationship between input and output can be expressed as an invariant
- Serialization round-trips: `deserialize(serialize(x)) == x`
- Data structure invariants: "after any sequence of operations, the invariant holds"
- Parsers: valid input always parses; parse(display(x)) == x
- Numeric computations: commutativity, associativity, bounds

**Example patterns:**

```rust
use proptest::prelude::*;

proptest! {
    // Round-trip property
    #[test]
    fn serialization_roundtrip(input in any::<MyStruct>()) {
        let bytes = input.serialize();
        let output = MyStruct::deserialize(&bytes).unwrap();
        prop_assert_eq!(input, output);
    }

    // Invariant preservation
    #[test]
    fn capacity_never_exceeded(ops in vec(any::<Op>(), 0..100)) {
        let mut structure = MyStructure::new(MAX_CAP);
        for op in ops {
            structure.apply(op);
            prop_assert!(structure.len() <= MAX_CAP);
        }
    }
}
```

**To use proptest, implement `Arbitrary` for your core types** or use proptest's strategy combinators. Ask Claude to derive `Arbitrary` implementations when creating new data types.

### Doc Tests

Use `///` doc comments with embedded examples for public API functions. These serve double duty as documentation and regression tests. Keep doc tests focused on demonstrating correct usage, not edge cases.

## Prompting Patterns for Claude Code

### Requesting tests (Tier 1 — tests first)

> Here is the trait signature and type definitions for [module]. Write comprehensive tests covering: happy paths, all error variants, boundary conditions, and at least two property-based tests using proptest. Do NOT write the implementation. Think about what could go wrong.

### Requesting tests (Tier 2 — implement then test)

> Here is the implementation of [module]. Write tests that could catch real bugs. Focus on error paths, edge cases, and any assumptions the implementation makes that might not hold. Do not simply restate the implementation logic as assertions.

### Requesting adversarial review of existing tests

> Review these tests for [module]. Are there any missing edge cases? Are any tests tautological — i.e., they would pass regardless of whether the implementation is correct? Suggest concrete additional tests.

### Requesting property-based tests

> For [type/function], identify invariants that should hold across all valid inputs, then write proptest property tests for them. Consider: round-trip properties, commutativity, invariant preservation, and idempotency.

## CI Integration

Every PR must pass:

```bash
cargo test --all-features
cargo clippy --all-targets --all-features -- -D warnings
cargo fmt --all -- --check
```

For property-based tests, the CI configuration should set `PROPTEST_CASES=500` (locally defaults to 256). Increase to `10000` for pre-release testing.

## Coverage Expectations

These are guidelines, not hard gates:

- **Tier 1 modules:** ≥ 85% line coverage, 100% of public API functions exercised
- **Tier 2 modules:** ≥ 70% line coverage, all error paths exercised
- **Tier 3 modules:** No coverage requirement until promoted to Tier 1 or 2

Use `cargo tarpaulin` or `cargo llvm-cov` for coverage measurement. Focus on meaningful coverage — a function with five branches should have at least five tests, not one test that happens to traverse three branches.

## Anti-Patterns to Avoid

- **Tautological tests:** Tests that simply mirror the implementation (e.g., testing that `add(2, 3)` returns the same thing the production `add` function returns by calling the same code).
- **Testing the framework:** Don't test that serde serializes correctly — test that YOUR types serialize to the format you expect.
- **Ignoring error paths:** Every `Result::Err` variant and every `panic!` / `unwrap()` in production code should have a corresponding test that exercises that path.
- **Overuse of `#[should_panic]`:** Prefer `assert!(result.is_err())` with specific error variant matching. `should_panic` tests are fragile and provide poor diagnostics.
- **Giant test functions:** If a test function exceeds ~30 lines, it's probably testing multiple things. Split it.
