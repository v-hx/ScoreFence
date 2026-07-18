# Application areas and use cases

## Purpose

This document defines where ScoreFence provides a useful guarantee, how it fits into real system lifecycles, and where another kind of test is more appropriate.

ScoreFence is not tied to one application type. It applies to systems that pass ranked numeric outputs across independently implemented boundaries:

```text
score producer → adapter → service/API → ranking policy → consumer
```

The project validates whether those boundaries agree on meaning, direction, order, range, threshold behavior, and score provenance. It does not decide whether a result is useful to a human.

## Fit test

ScoreFence is a strong fit when several of the following statements are true:

- a numeric score leaves the component that computed it;
- more than one backend, SDK, adapter, or API representation is possible;
- sorting, filtering, top-k selection, or a decision threshold depends on the score;
- components can be upgraded or deployed independently;
- a defect can return a valid response with the wrong ranking;
- the system needs a low-level deterministic check before quality evaluation;
- a migration must preserve behavior without preserving native score values;
- the same public field may contain values produced by different stages.

The presence of a field named `score` is not sufficient. If the value never crosses a boundary and a local unit test completely specifies its formula and use, ScoreFence may add little value.

## Scope layers

ScoreFence separates current support from architectural extensibility:

| Layer | What is validated | Status |
|---|---|---|
| Vector retrieval | distance/similarity direction, ordering, metric fingerprint, threshold polarity | MVP scope |
| Retrieval pipeline | preservation between a native target and consumer-facing path | MVP scope |
| Migration and drift | contract differences between baseline and candidate | Planned core mode |
| Hybrid and reranking stages | stage identity and contract separation | Partial in MVP; richer packs later |
| Recommendation, anomaly, and risk outputs | domain-specific relative relations and thresholds | Requires dedicated probe packs |
| End-user relevance and business quality | usefulness, precision, recall, conversion, answer quality | Outside ScoreFence |

The extension boundary is explicit: a new score family requires a probe pack that defines controlled fixtures, expected relations, tolerances, capabilities, and limitations. The core must never treat every numeric field as vector similarity.

## When to run ScoreFence

ScoreFence is an out-of-band validation job, not a permanent request-path proxy. Typical trigger points are:

| Trigger | Validation goal |
|---|---|
| Target onboarding | establish and approve the initial contract |
| Adapter or SDK change | detect transformation, field-mapping, or ordering drift |
| Backend migration | compare baseline and candidate before cutover |
| Metric or index change | verify direction, fingerprint, and threshold compatibility |
| New ranking stage | require a distinct `score_stage` and prevent field reuse |
| Scheduled regression check | compare the current observation fingerprint with the approved one |
| Incident investigation | separate contract failure from content or model-quality failure |

## Application-area matrix

| Application area | Objects being ranked | Useful ScoreFence boundary |
|---|---|---|
| Knowledge and document search | passages, pages, tickets, messages | search backend to retrieval API |
| Product and catalog search | products, offers, categories | candidate search to filtering policy |
| Retrieval-augmented applications | context chunks, memories, tool outputs | retriever to context builder |
| Code search | files, symbols, snippets, changes | vector index to developer-facing API |
| Recommendation candidate generation | candidate items | nearest-neighbor service to ranking model |
| Multimodal search | images, audio, video, text | modality-specific index to shared gateway |
| Entity resolution and deduplication | possible record pairs | candidate generator to match decision service |
| Support and incident similarity | cases, alerts, incident histories | similarity service to automation policy |
| Multi-backend search platform | results from interchangeable targets | each adapter to one public contract |
| Migration and compatibility tooling | baseline and candidate behavior | old path to new path |

These applications share a technical shape even when their business domains differ: ranked candidates cross a component boundary and downstream code assumes a score contract.

## Scenario 1: backend migration

### System

A catalog-search service exposes higher-is-better relevance. Its source backend returns lower-is-better distance, so an adapter converts the native value:

```text
public_score = 1 - native_distance
```

The consumer sorts descending and accepts `public_score >= 0.75`.

### Failure

The target is replaced by a backend that already returns higher-is-better similarity. The response schema still contains a numeric `score`, so the old transformation remains:

```text
native similarity   0.98   0.82   0.07
public score        0.02   0.18   0.93
expected quality    best   near   unrelated
```

Transport checks, schema checks, and non-empty-result tests all pass. The effective ranking is inverted.

### ScoreFence run

ScoreFence executes the same deterministic probe pack against:

1. the candidate backend directly;
2. the consumer-facing search API;
3. the threshold-enabled path.

The direct target reports `higher_is_better`; the public path behaves as `lower_is_better`; the configured threshold rejects the exact match and accepts the far candidate. The comparison reports a likely inversion in the integration layer.

### Result

The cutover is blocked until the public contract is restored. The approved observation becomes a baseline fingerprint for later upgrades.

## Scenario 2: one API over multiple targets

### System

A search gateway offers one response schema while several target implementations remain interchangeable:

```json
{
  "results": [
    {"id": "item-a", "score": 0.82}
  ]
}
```

Each adapter must expose the same consumer contract even when native targets differ in metric, direction, range, or sort order.

### Failure

One adapter forwards native distance, another forwards normalized relevance, and a third changes result order but leaves scores untouched. All responses are schema-valid.

### ScoreFence run

The gateway maintains one expected public contract and runs the same probe pack for every adapter. Target-specific behavior stays inside the adapter; validation and reports remain unchanged.

### Result

An adapter is accepted only when its consumer-facing observations conform to the shared contract. New targets can be onboarded without adding product names or special cases to the core.

## Scenario 3: externally managed target onboarding

### System

A hosted application allows an operator to connect an externally managed search target. The application knows the endpoint and credentials but cannot safely assume how its score is represented.

### Failure

The configured metric name appears compatible, but the target API returns a transformed value and the application applies a threshold from another scale.

### ScoreFence run

An onboarding job creates a temporary namespace, writes controlled probes, observes behavior through the same API path the application will use, verifies cleanup, and produces a portable report.

### Result

Activation requires an explicit approved contract. If isolation, insertion, or cleanup cannot be guaranteed, the verdict is `INCONCLUSIVE` rather than a guessed configuration.

## Scenario 4: adapter or SDK upgrade

### System

An application updates a client library or internal adapter. Functional tests verify authentication, transport, IDs, and result count.

### Failure

The new version changes one of the following without breaking the response shape:

- raw distance becomes normalized relevance;
- a score field is renamed and mapped from the wrong source;
- default result ordering changes;
- a server-side threshold is applied before the client receives results;
- an approximate-search option changes ordering stability.

### ScoreFence run

CI compares the candidate observation fingerprint with the approved baseline and emits evidence for every changed contract field.

### Result

Expected changes can be reviewed and accepted by updating the contract. Accidental semantic drift fails the release check.

## Scenario 5: multi-stage retrieval and reranking

### System

A pipeline contains several incomparable numeric values:

```text
vector_score → sparse_score → fusion_score → reranker_score → final_rank
```

### Failure

A wrapper reuses the field name `score` after reranking. Downstream code applies a vector-search threshold to the reranker output, or observability cannot identify which stage produced the value.

### ScoreFence run

Each validated stage has a separate contract and explicit `score_stage`. The vector-retrieval pack validates the vector stage. Native-versus-pipeline comparison checks whether later components preserve or intentionally replace the value. An unknown mixed-stage path produces `SF106` or `INCONCLUSIVE`, not a false vector conclusion.

### Result

The pipeline gains score provenance. Different stages may use different directions and ranges without pretending that their values are comparable.

## Scenario 6: incident diagnosis

### System

Users report that search or context quality suddenly declined. Error rates and latency remain normal.

### Failure candidates

Possible causes include content changes, a new encoder, index configuration, approximate-search behavior, an adapter transform, threshold polarity, or a reranker change.

### ScoreFence run

A deterministic probe checks the low-level contract independently of production content. A pass narrows the investigation toward model and relevance quality. A fail provides reproducible evidence at the exact boundary where semantics changed.

### Result

ScoreFence is a localization tool, not a universal root-cause engine. It reduces the search space by proving or excluding one important class of silent failures.

## Scenario 7: non-text similarity systems

The vector-retrieval pack is independent of what vectors represent. The same contract checks apply to:

- image or video similarity;
- audio matching;
- code and symbol search;
- recommendation candidate retrieval;
- duplicate-candidate generation;
- similar-case or incident lookup.

ScoreFence validates the retrieval boundary only. A later business decision, classifier, or ranking model requires its own tests or a dedicated probe pack.

## Deployment patterns

| Pattern | Best use | Output consumer |
|---|---|---|
| Local CLI | adapter development and incident reproduction | engineer |
| CI job | release and dependency-change gates | pipeline exit code and artifacts |
| Ephemeral container job | isolated access to a remote target | scheduler or control plane |
| Embedded library | onboarding inside an application workflow | application service |
| Scheduled check | contract-drift detection | alerting or audit system |
| Migration comparison | pre-cutover review | migration owner |

All modes execute the same core. Deployment changes how configuration and credentials are supplied, not what the contract means.

## Where ScoreFence is not the right tool

Do not use ScoreFence as a substitute for:

- labeled relevance evaluation;
- precision, recall, ranking-quality, or conversion measurement;
- answer correctness or faithfulness evaluation;
- embedding-model selection;
- automatic production-threshold optimization;
- model fairness, calibration, robustness, or security testing;
- application-specific decision validation.

ScoreFence may also be unnecessary when one in-process implementation computes and consumes the value under a fully specified type and unit test, with no adapter, API, threshold, migration, or independently deployed boundary.

## Adoption checklist

Before adding ScoreFence, identify:

1. the score producer;
2. every boundary the value crosses;
3. the exact stage being validated;
4. the consumer assumptions about direction, range, order, and threshold;
5. an isolation mechanism for controlled fixtures;
6. the trigger points that should rerun validation;
7. the owner who can approve an intentional contract change.

If those answers are explicit, ScoreFence can turn them into an executable contract. If they are not, discovery can collect evidence, but it must preserve uncertainty and avoid changing production behavior.

## Summary

ScoreFence has a deliberately focused implementation and a broad integration surface. It is not a general evaluator of every numeric model output. It is a contract-testing system for ranked values whose meaning can be lost between replaceable components.

The vector-retrieval MVP covers the most deterministic form of this problem. Probe packs provide a controlled path to additional score families without weakening the core guarantee or hiding domain assumptions.
