# Contributing

ScoreFence is currently a design-stage repository. This document establishes the future rules so implementation does not blur the original problem.

## Core principle

Every adapter, probe pack, or rule must answer a question about the score contract. Changes that turn ScoreFence into a general relevance-evaluation framework should be discussed separately.

## Adding a probe pack

A probe pack must:

1. name one coherent score family and supported stages;
2. define controlled fixtures and expected relations independently of a target implementation;
3. declare required adapter capabilities;
4. document tolerances, confidence factors, and limitations;
5. return `INCONCLUSIVE` when evidence is insufficient;
6. avoid comparing its numeric range with another pack unless an explicit transformation contract exists;
7. include deterministic fixtures for PASS, FAIL, and ambiguous behavior.

## Adding an adapter

An adapter must:

1. declare its capabilities;
2. create an isolated probe namespace;
3. support idempotent cleanup;
4. return raw IDs, order, and scores without hidden normalization;
5. log requests with redaction;
6. include an integration test against a real backend;
7. document backend- and version-specific semantics.

## Adding a rule

A rule proposal must contain:

- the contract property;
- the minimum required evidence;
- a counterexample;
- the severity rationale;
- conditions for `INCONCLUSIVE`;
- remediation that does not mutate production automatically;
- tests for PASS, FAIL, and an ambiguous case.

## Documentation consistency

Behavior changes must update every related document, example, diagram, and report
format.

## Pull request checklist

- [ ] The scope concerns the score contract
- [ ] Findings are evidence-first
- [ ] The cleanup path is tested
- [ ] Secrets are redacted
- [ ] No unknown score is normalized silently
- [ ] Probe-pack assumptions are explicit and isolated from the core
- [ ] Documentation and examples are updated
- [ ] Regression tests are included
