# Detection model

## Why a separate model is needed

One unexpected score does not prove an error. The detection model defines which observations are sufficient for each conclusion and how ScoreFence avoids false certainty.

## Scope of the model

The built-in probe families below belong to `vector_retrieval/v1alpha1`. They validate mathematically controlled distance and similarity behavior. Generic findings such as direction, order, threshold polarity, boundary mismatch, and stage ambiguity may be reused by future packs, but evidence generation remains pack-specific.

A future pack must declare:

- controlled fixtures and expected relations;
- required target capabilities;
- supported contract fields;
- tolerance and stability policy;
- confidence factors;
- limitations and conditions that require `INCONCLUSIVE`.

The core must not run vector metric inference on observations produced by another score family.

## Probe families

### P1 — Identity

The query equals a stored vector.

Validates that:

- the exact candidate is present;
- its value is optimal relative to the other candidates;
- the threshold does not remove the exact match.

### P2 — Ordered neighborhood

Uses `exact`, `near`, `orthogonal`, and `opposite`.

Validates:

- semantic order;
- monotonic direction;
- actual sorting.

### P3 — Magnitude

Compares `exact=(1,0)` and `scaled=(2,0)`.

Tests sensitivity to magnitude and helps distinguish cosine, dot, and L2 behavior.

### P4 — Threshold boundary

Selects a threshold between two observed values and repeats the search through the production-like filtering path.

Checks which candidates pass on either side of the boundary.

### P5 — Stability

Repeats an identical probe several times.

Validates:

- ordering stability;
- score variation;
- the effect of approximate search.

### P6 — Native vs pipeline

Runs one plan directly against the search backend and through the consumer-facing retrieval API.

Checks whether semantics change in an intermediate layer.

The comparison key includes `pack_id`, `boundary_id`, and `score_stage`. Observations from different packs or stages are not numerically compared unless an explicit transformation contract allows it.

## Built-in findings

| Rule | Severity | Condition |
|---|---|---|
| `SF101` | High | Observed `better_when` contradicts the contract |
| `SF102` | High | Results are ordered opposite to observed relevance |
| `SF103` | Critical | The threshold accepts worse probes and rejects better ones |
| `SF104` | Critical | The exact match is rejected or missing in deterministic exact mode |
| `SF105` | High | The observed fingerprint contradicts the declared metric |
| `SF106` | Medium | Multiple score stages share one unnamed value |
| `SF107` | High | Native and pipeline directions differ |
| `SF201` | Medium | Ordering is unstable beyond tolerance |
| `SF202` | Low | The score range drifted while direction was preserved |
| `SF301` | Critical | The probe namespace is not isolated |
| `SF302` | High | Cleanup could not be verified |

## Direction inference

Assume the expected semantic rank is:

```text
exact=4, near=3, orthogonal=2, opposite=1
```

ScoreFence measures agreement of raw values with two hypotheses:

```text
H_high: higher value means better
H_low:  lower value means better
```

For a simple MVP, pairwise comparisons are sufficient:

```text
exact vs near
near vs orthogonal
orthogonal vs opposite
```

If every comparison supports `H_low`, direction is considered strongly inferred. If contradictions exist, the result depends on exact or approximate mode and the separation margin.

## Tolerances

Floating-point values must not be compared using strict equality. Configuration should support:

```yaml
tolerance:
  absolute: 1.0e-6
  relative: 1.0e-5
  ordering_margin: 0.01
```

No ordering finding is emitted for a pair whose difference is below the margin; the pair is marked `tie_or_ambiguous`.

## Confidence factors

Confidence increases with:

- direct-vector insertion;
- exact search;
- a known collection metric;
- a large separation margin;
- repeatability;
- agreement between native and pipeline observations.

Confidence decreases with:

- text embeddings;
- approximate-only search;
- an unknown reranker;
- a small score separation;
- unstable results;
- an incomplete result set;
- unknown normalization.

## Evidence-first report

A poor finding:

```text
Threshold seems wrong.
```

A good finding:

```text
SF103 threshold polarity mismatch

Expected:
  observed better_when=lower requires value <= 0.30

Observed through pipeline endpoint:
  exact       0.00 rejected
  near        0.20 rejected
  orthogonal  1.00 accepted

Confidence:
  0.99, direct vectors + exact search + 3/3 pairwise agreement
```

## Why ScoreFence does not fix everything automatically

Automatically replacing `>=` with `<=` still requires human confirmation because:

- the threshold may be applied to a transformed score;
- the report may have validated the wrong stage;
- the production corpus has a different distribution;
- changing the operator is a real behavioral change.

The tool proposes remediation, but the MVP remains read-only.
