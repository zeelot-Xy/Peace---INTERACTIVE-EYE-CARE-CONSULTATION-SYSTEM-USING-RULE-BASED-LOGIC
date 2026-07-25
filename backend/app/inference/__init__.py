"""Public inference subsystem API."""

from app.inference.contracts import (
    CriteriaScore,
    ExpressionEvaluation,
    ExpressionTrace,
    InferenceResult,
    RuleEvaluation,
    TruthValue,
)
from app.inference.engine import MATCH_SCORE_NOTICE, InferenceEngine
from app.inference.exceptions import (
    FactValidationError,
    FactValidationIssue,
    InferenceConfigurationError,
)
from app.inference.expressions import evaluate_expression
from app.inference.facts import normalize_facts

__all__ = [
    "MATCH_SCORE_NOTICE",
    "CriteriaScore",
    "ExpressionEvaluation",
    "ExpressionTrace",
    "FactValidationError",
    "FactValidationIssue",
    "InferenceConfigurationError",
    "InferenceEngine",
    "InferenceResult",
    "RuleEvaluation",
    "TruthValue",
    "evaluate_expression",
    "normalize_facts",
]
