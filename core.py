"""Core data types shared across the security gateway prototype."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Status(Enum):
    PASS = "PASS"
    FAIL = "FAIL"


@dataclass
class Task:
    """Structured representation of what the user actually asked for.

    allowed_tools = Authority scope. constraints = conditions Consequence
    must check the final state against (e.g. max_price).
    """

    name: str
    goal: str
    allowed_tools: set[str]
    constraints: dict[str, Any] = field(default_factory=dict)


@dataclass
class Action:
    """One proposed step in the agent's plan."""

    step: int
    tool: str
    params: dict[str, Any] = field(default_factory=dict)
    purpose: str = ""


@dataclass
class VerificationResult:
    agent: str
    status: Status
    violation_type: str = ""
    evidence: str = ""
    feedback: str = ""


@dataclass
class GatewayVerdict:
    status: Status
    results: list[VerificationResult]

    @property
    def failures(self) -> list[VerificationResult]:
        return [r for r in self.results if r.status is Status.FAIL]
