# Roadmap

The roadmap deliberately keeps the first version narrow. The goal is a finished contract probe, not another universal retrieval-evaluation platform.

## Phase 0 — Design package ✅

- [x] Problem statement
- [x] Score contract model
- [x] Deterministic vector probes
- [x] Detection rules
- [x] Safety and cleanup model
- [x] Example configuration and reports
- [x] Vendor-neutral integration scenarios
- [x] Complete documentation set with an automated consistency check
- [ ] License and IP ownership decision

## Phase 1 — Local engine

Goal: implement the mathematics and inference without an external backend.

- [ ] Python package and CLI skeleton
- [ ] Probe vector definitions
- [ ] Expected metric calculator
- [ ] Direction inference
- [ ] Rule engine for `SF101`–`SF105`
- [ ] Confidence model
- [ ] Terminal and JSON reports
- [ ] Unit tests with synthetic observation sets

**Exit criterion:** the CLI analyzes recorded fixtures and produces the expected verdicts consistently.

## Phase 2 — First external target

Goal: prove end-to-end value through the public adapter protocol without adding vendor-specific logic to the core.

- [ ] Adapter capability protocol
- [ ] Generic HTTP adapter with configurable field mapping
- [ ] Temporary namespace lifecycle
- [ ] Direct-vector insertion and exact search
- [ ] Verified cleanup
- [ ] Integration tests in a container
- [ ] Markdown report

**Exit criterion:** ScoreFence detects a deliberately inverted threshold on a real backend.

## Phase 3 — Universal execution modes

- [ ] Stable Python library API
- [ ] Native vs pipeline comparison
- [ ] Versioned score contract fingerprint
- [ ] OCI container image
- [ ] Example Kubernetes Job
- [ ] GitHub Actions example
- [ ] Redaction review

**Exit criterion:** the report localizes a difference between backend behavior and retrieval API behavior.

## Phase 4 — Migration and drift

- [ ] `scorefence compare`
- [ ] Baseline fingerprint storage
- [ ] Drift report
- [ ] Community adapter SDK and compatibility tests
- [ ] Approximate-search stability rule

## Explicit non-goals before v1.0

- LLM-as-a-judge;
- answer faithfulness evaluation;
- automatic production threshold tuning;
- an always-on proxy;
- automatic configuration mutation;
- a broad observability dashboard;
- support for every vector database.

## Suggested first demo

1. Run the reference in-memory target and a generic HTTP wrapper locally.
2. Show the correct `distance <= threshold` behavior — PASS.
3. Switch the consumer to `distance >= threshold` — FAIL `SF103`.
4. Show the evidence table and cleanup verification.
5. Fix the operator and obtain PASS again.

This demo takes only a few minutes and explains the value without a prepared business dataset or LLM credentials.
