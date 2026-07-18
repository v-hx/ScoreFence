# Originality and adjacent work

## Short conclusion

ScoreFence uses established mathematics and familiar integration-test techniques. Its originality is not the cosine-distance formula but the productization of a narrow problem:

> automated end-to-end validation of the numeric-score semantic contract between a search backend, an adapter, and any retrieval consumer.

The current deterministic scope is vector retrieval, but the problem shape is broader: ranked values cross independently implemented boundaries in document search, catalog search, recommendation candidate generation, multimodal similarity, entity matching, and multi-stage ranking. The architecture represents that breadth through explicit probe packs, not by applying vector assumptions to every numeric output.

The core works only with public adapter and probe-pack protocols plus a typed observation model. It contains no logic, configuration objects, or API assumptions from a particular database, platform, or retrieval framework.

The targeted search did not find an obvious mature open-source project that combines all of the following:

- deterministic direct-vector probes;
- inference of `better_when` from observed behavior;
- threshold-polarity validation;
- native-versus-pipeline comparison;
- stage and boundary provenance;
- a versioned contract fingerprint;
- operation as a read-only CI or control-plane check.

This is not proof of worldwide or patent novelty. A separate landscape review is required before making public claims.

## Closest solution categories

### Vector-database documentation

Official search-engine documentation demonstrates a variety of approaches:

- some APIs return distance operators;
- some APIs return similarity or transformed relevance;
- migration guides warn that an identically named field may change direction or range.

These sources help a human understand the problem, but they do not automatically validate a particular user pipeline. ScoreFence neither imports nor requires any vendor SDK.

### Retrieval evaluation frameworks

Retrieval evaluation usually measures:

- context relevance;
- answer faithfulness;
- recall and precision on a dataset;
- answer quality through a judge model.

ScoreFence operates at a lower layer: it validates the technical meaning of the score before evaluating content quality.

### Vector migration tools

Migration tooling moves data and indexes and may compare search quality. ScoreFence can be used during migration, but its primary artifact is a score contract and evidence that the contract was preserved.

### API contract testing

Pact, schema validation, and integration tests validate response structure. A schema can confirm that `score` is a `number`, but it cannot prove that smaller is better or that the threshold uses the correct operator.

## Differentiation

| Capability | API schema test | Retrieval evaluation | Migration test | ScoreFence |
|---|---:|---:|---:|---:|
| Confirms that score is numeric | ✅ | Sometimes | Sometimes | ✅ |
| Validates direction | ❌ | Indirectly | Sometimes manually | ✅ |
| Validates threshold polarity | ❌ | Indirectly | ❌ | ✅ |
| Direct-vector deterministic probes | ❌ | Usually not | Sometimes | ✅ |
| Native-versus-pipeline comparison | ❌ | ❌ | Sometimes | ✅ |
| Explicit score-stage provenance | ❌ | Sometimes | Sometimes | ✅ |
| Contract fingerprint for drift | ❌ | ❌ | ❌ | ✅ |
| Requires no labeled dataset or LLM judge | ✅ | ❌ | ✅ | ✅ |

## Claims to avoid

Without further research, the project must not claim:

- “the first in the world”;
- “patent-unique”;
- “the only open-source tool”;
- “guarantees correctness of the entire retrieval system”;
- “automatically finds the best threshold.”
- “validates every numeric model score.”

An accurate formulation is:

> ScoreFence is a focused contract-testing tool for discovering and validating vector-score semantics across retrieval pipelines. At the time of the initial targeted review, no obvious mature open-source equivalent with the same capability set was found.

It is also accurate to describe the architecture as extensible to additional ranked-score families through explicit probe packs. That is a design property, not a claim that those packs already exist or that all score families can be validated with the same evidence.

## Naming note

A targeted web search for `ScoreFence` in software and vector-database contexts did not show an obvious conflicting project. Before registering a project namespace, package, or domain, check again:

- code repositories and organizations;
- relevant package registries;
- domains;
- relevant trademark databases.
