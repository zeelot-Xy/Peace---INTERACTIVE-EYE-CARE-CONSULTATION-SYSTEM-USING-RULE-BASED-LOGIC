"""Failures raised by the deterministic inference subsystem."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class FactValidationIssue:
    """One stable, machine-readable problem with supplied consultation facts."""

    code: str
    fact_id: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "fact_id": self.fact_id, "message": self.message}


class FactValidationError(ValueError):
    """Raised when facts cannot safely be evaluated."""

    def __init__(self, issues: tuple[FactValidationIssue, ...]):
        self.issues = tuple(sorted(issues))
        super().__init__("Facts failed validation.")

    def to_dict(self) -> dict[str, object]:
        return {
            "code": "invalid_facts",
            "message": str(self),
            "issues": [issue.to_dict() for issue in self.issues],
        }


class InferenceConfigurationError(RuntimeError):
    """Raised when validated authored knowledge is not executable."""
