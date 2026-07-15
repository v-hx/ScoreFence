# ScoreFence report

> Example report. Values are illustrative and were not produced by an implemented CLI.

| Field | Value |
|---|---|
| Target | `retrieval-staging` |
| Adapter | `generic_http` |
| Mode | `direct_vectors` |
| Verdict | **FAIL** |
| Confidence | `0.99 — verified` |
| Cleanup | `verified` |

## Summary

The target returns cosine **distance**, where lower values are better, but the configured threshold accepts values greater than or equal to `0.70`.

## Findings

### SF103 — Threshold polarity mismatch

**Severity:** Critical  
**Confidence:** 0.99

Expected from the observed direction:

```text
accept if score <= threshold
```

Configured behavior:

```text
accept if score >= 0.70
```

Evidence:

| Probe | Expected relevance | Score | Accepted |
|---|---:|---:|---:|
| exact | 4 | 0.000 | No |
| near | 3 | 0.200 | No |
| orthogonal | 2 | 1.000 | Yes |
| opposite | 1 | 2.000 | Yes |

Suggested remediation:

```yaml
value_kind: distance
better_when: lower
threshold:
  operator: lte
  value: 0.30
```

The suggested operator is strongly supported by the probe. The suggested value `0.30` is illustrative and must be validated on a labeled domain dataset before production use.

## Observed contract

```yaml
metric_compatible_with:
  - cosine_distance
value_kind: distance
better_when: lower
result_order: ascending
observed_range: [0.0, 2.0]
score_stage: vector_search
```

## Execution

```text
Namespace created: sf_probe_01J7F42
Probe vectors inserted: 5
Search executions: 3
Ordering stability: 100%
Namespace deleted: yes
Deletion verified: yes
```
