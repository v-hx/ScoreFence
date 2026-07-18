"""Typed score-contract primitives.

The models in this module sit on configuration and API boundaries. They validate
untrusted input, serialize predictably, and remain immutable after construction.
"""

from __future__ import annotations

import math
from enum import StrEnum
from typing import Annotated, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    StringConstraints,
    model_validator,
)

Identifier = Annotated[
    str,
    StringConstraints(
        min_length=1,
        max_length=128,
        pattern=r"^[A-Za-z0-9](?:[A-Za-z0-9._:/-]*[A-Za-z0-9])?$",
        strip_whitespace=True,
    ),
]
FiniteScore = Annotated[float, Field(strict=True, allow_inf_nan=False)]


class BetterWhen(StrEnum):
    """Direction in which a score becomes semantically better."""

    HIGHER = "higher"
    LOWER = "lower"

    @property
    def expected_result_order(self) -> ResultOrder:
        """Return the natural sort order for this direction."""
        if self is BetterWhen.HIGHER:
            return ResultOrder.DESCENDING
        return ResultOrder.ASCENDING

    @property
    def expected_threshold_operator(self) -> ThresholdOperator:
        """Return the natural acceptance operator for this direction."""
        if self is BetterWhen.HIGHER:
            return ThresholdOperator.GTE
        return ThresholdOperator.LTE


class ResultOrder(StrEnum):
    """Ordering used by a result list."""

    ASCENDING = "ascending"
    DESCENDING = "descending"


class ThresholdOperator(StrEnum):
    """Supported inclusive threshold operators."""

    GTE = "gte"
    LTE = "lte"

    def accepts(self, score: float, threshold: float) -> bool:
        """Evaluate the operator without changing either numeric value."""
        if not math.isfinite(score) or not math.isfinite(threshold):
            msg = "score and threshold must be finite"
            raise ValueError(msg)
        if self is ThresholdOperator.GTE:
            return score >= threshold
        return score <= threshold


class ConsistencyIssueKind(StrEnum):
    """Static contradictions that can be detected without probe evidence."""

    RESULT_ORDER_POLARITY = "result_order_polarity"
    THRESHOLD_POLARITY = "threshold_polarity"
    THRESHOLD_OUTSIDE_RANGE = "threshold_outside_expected_range"


class ContractModel(BaseModel):
    """Shared behavior for externally supplied contract objects."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        validate_default=True,
    )


class ScoreRange(RootModel[tuple[FiniteScore, FiniteScore]]):
    """Closed numeric range serialized as a two-item array."""

    model_config = ConfigDict(frozen=True)

    @model_validator(mode="after")
    def validate_bounds(self) -> Self:
        """Reject ranges whose lower bound exceeds their upper bound."""
        if self.lower > self.upper:
            msg = "expected range lower bound must not exceed its upper bound"
            raise ValueError(msg)
        return self

    @property
    def lower(self) -> float:
        """Return the inclusive lower bound."""
        return self.root[0]

    @property
    def upper(self) -> float:
        """Return the inclusive upper bound."""
        return self.root[1]

    def contains(self, value: float) -> bool:
        """Return whether a finite value is inside the closed range."""
        return math.isfinite(value) and self.lower <= value <= self.upper


class Threshold(ContractModel):
    """Configured inclusive threshold."""

    operator: ThresholdOperator
    value: FiniteScore

    def accepts(self, score: float) -> bool:
        """Return whether the configured policy accepts a score."""
        return self.operator.accepts(score, self.value)


class ConsistencyIssue(ContractModel):
    """A semantic contradiction retained for later reporting."""

    kind: ConsistencyIssueKind
    fields: tuple[Identifier, ...]
    message: str


class ScoreContract(ContractModel):
    """Declared semantics of one score at one system boundary and stage."""

    contract_id: Identifier
    pack: Identifier
    boundary: Identifier
    score_stage: Identifier
    metric: Identifier
    value_kind: Identifier
    better_when: BetterWhen
    result_order: ResultOrder
    expected_range: ScoreRange | None = None
    threshold: Threshold | None = None

    def consistency_issues(self) -> tuple[ConsistencyIssue, ...]:
        """Return contradictions that do not require runtime observations."""
        issues: list[ConsistencyIssue] = []

        # Semantic contradictions are evidence, not parsing failures. Keeping the
        # contract representable lets ScoreFence explain the defect precisely.
        expected_order = self.better_when.expected_result_order
        if self.result_order is not expected_order:
            issues.append(
                ConsistencyIssue(
                    kind=ConsistencyIssueKind.RESULT_ORDER_POLARITY,
                    fields=("better_when", "result_order"),
                    message=(
                        f"{self.better_when.value}-is-better scores naturally require "
                        f"{expected_order.value} result order"
                    ),
                )
            )

        if (
            self.threshold is not None
            and self.threshold.operator is not self.better_when.expected_threshold_operator
        ):
            issues.append(
                ConsistencyIssue(
                    kind=ConsistencyIssueKind.THRESHOLD_POLARITY,
                    fields=("better_when", "threshold"),
                    message=(
                        f"{self.better_when.value}-is-better scores naturally require "
                        f"the {self.better_when.expected_threshold_operator.value} "
                        "threshold operator"
                    ),
                )
            )

        if (
            self.threshold is not None
            and self.expected_range is not None
            and not self.expected_range.contains(self.threshold.value)
        ):
            issues.append(
                ConsistencyIssue(
                    kind=ConsistencyIssueKind.THRESHOLD_OUTSIDE_RANGE,
                    fields=("expected_range", "threshold"),
                    message="threshold lies outside the declared score range",
                )
            )

        return tuple(issues)
