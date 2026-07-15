# Contributing

ScoreFence is currently a design-stage repository. This document establishes the future rules so implementation does not blur the original problem.

## Core principle

Every adapter or rule must answer a question about the score contract. Changes that turn ScoreFence into a general retrieval-evaluation framework should be discussed separately.

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

Behavior changes must update every related document, example, diagram, and report format. An automated check validates documentation structure and prevents one-sided changes to related files.

## Pull request checklist

- [ ] The scope concerns the score contract
- [ ] Findings are evidence-first
- [ ] The cleanup path is tested
- [ ] Secrets are redacted
- [ ] No unknown score is normalized silently
- [ ] Both documentation languages and examples are updated
- [ ] Regression tests are included
