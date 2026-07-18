from __future__ import annotations

import math
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from scorefence import (
    BetterWhen,
    ConsistencyIssueKind,
    ResultOrder,
    ScoreContract,
    ScoreRange,
    Threshold,
    ThresholdOperator,
)


def make_contract(**overrides: Any) -> ScoreContract:
    data: dict[str, Any] = {
        "contract_id": "candidate-search-public-score",
        "pack": "vector_retrieval/v1alpha1",
        "boundary": "consumer_api",
        "score_stage": "vector_search",
        "metric": "cosine",
        "value_kind": "distance",
        "better_when": BetterWhen.LOWER,
        "result_order": ResultOrder.ASCENDING,
        "expected_range": [0.0, 2.0],
        "threshold": {"operator": ThresholdOperator.LTE, "value": 0.3},
    }
    data.update(overrides)
    return ScoreContract.model_validate(data)


def test_contract_matches_the_public_configuration_shape() -> None:
    contract = make_contract()

    assert contract.model_dump(mode="json") == {
        "contract_id": "candidate-search-public-score",
        "pack": "vector_retrieval/v1alpha1",
        "boundary": "consumer_api",
        "score_stage": "vector_search",
        "metric": "cosine",
        "value_kind": "distance",
        "better_when": "lower",
        "result_order": "ascending",
        "expected_range": [0.0, 2.0],
        "threshold": {"operator": "lte", "value": 0.3},
    }
    assert contract.consistency_issues() == ()


def test_higher_is_better_contract_is_consistent() -> None:
    contract = make_contract(
        value_kind="similarity",
        better_when=BetterWhen.HIGHER,
        result_order=ResultOrder.DESCENDING,
        expected_range=[-1.0, 1.0],
        threshold={"operator": ThresholdOperator.GTE, "value": 0.7},
    )

    assert contract.consistency_issues() == ()


def test_contract_round_trips_through_its_serialized_shape() -> None:
    contract = make_contract()

    restored = ScoreContract.model_validate(contract.model_dump(mode="json"))

    assert restored == contract


def test_contract_is_immutable() -> None:
    contract = make_contract()

    with pytest.raises(ValidationError, match="frozen"):
        contract.boundary = "another_boundary"  # type: ignore[misc]


def test_contract_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        make_contract(undocumented=True)


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_threshold_rejects_non_finite_values(value: float) -> None:
    with pytest.raises(ValidationError, match="finite number"):
        Threshold(operator=ThresholdOperator.LTE, value=value)


def test_threshold_rejects_numeric_strings() -> None:
    with pytest.raises(ValidationError, match="valid number"):
        Threshold.model_validate({"operator": "lte", "value": "0.3"})


def test_score_range_rejects_reversed_bounds() -> None:
    with pytest.raises(ValidationError, match="lower bound"):
        ScoreRange((1.0, 0.0))


def test_contract_reports_result_order_polarity() -> None:
    contract = make_contract(result_order=ResultOrder.DESCENDING)

    assert [issue.kind for issue in contract.consistency_issues()] == [
        ConsistencyIssueKind.RESULT_ORDER_POLARITY
    ]


def test_contract_reports_threshold_polarity() -> None:
    contract = make_contract(threshold={"operator": ThresholdOperator.GTE, "value": 0.3})

    assert [issue.kind for issue in contract.consistency_issues()] == [
        ConsistencyIssueKind.THRESHOLD_POLARITY
    ]


def test_contract_reports_threshold_outside_expected_range() -> None:
    contract = make_contract(threshold={"operator": ThresholdOperator.LTE, "value": 2.1})

    assert [issue.kind for issue in contract.consistency_issues()] == [
        ConsistencyIssueKind.THRESHOLD_OUTSIDE_RANGE
    ]


def test_contract_reports_all_static_issues_in_stable_order() -> None:
    contract = make_contract(
        result_order=ResultOrder.DESCENDING,
        threshold={"operator": ThresholdOperator.GTE, "value": 2.1},
    )

    assert [issue.kind for issue in contract.consistency_issues()] == [
        ConsistencyIssueKind.RESULT_ORDER_POLARITY,
        ConsistencyIssueKind.THRESHOLD_POLARITY,
        ConsistencyIssueKind.THRESHOLD_OUTSIDE_RANGE,
    ]


@given(
    lower=st.floats(allow_nan=False, allow_infinity=False, width=64),
    upper=st.floats(allow_nan=False, allow_infinity=False, width=64),
)
def test_score_range_contains_its_ordered_endpoints(lower: float, upper: float) -> None:
    low, high = sorted((lower, upper))
    score_range = ScoreRange((low, high))

    assert score_range.contains(low)
    assert score_range.contains(high)


@given(
    score=st.floats(allow_nan=False, allow_infinity=False, width=64),
    threshold=st.floats(allow_nan=False, allow_infinity=False, width=64),
)
def test_threshold_operators_match_numeric_comparison(score: float, threshold: float) -> None:
    assert ThresholdOperator.GTE.accepts(score, threshold) is (score >= threshold)
    assert ThresholdOperator.LTE.accepts(score, threshold) is (score <= threshold)


def test_threshold_delegates_acceptance_to_its_operator() -> None:
    threshold = Threshold(operator=ThresholdOperator.LTE, value=0.3)

    assert threshold.accepts(0.3)
    assert not threshold.accepts(0.31)


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_threshold_operator_rejects_non_finite_runtime_values(value: float) -> None:
    with pytest.raises(ValueError, match="must be finite"):
        ThresholdOperator.GTE.accepts(value, 0.0)
    with pytest.raises(ValueError, match="must be finite"):
        ThresholdOperator.LTE.accepts(0.0, value)
