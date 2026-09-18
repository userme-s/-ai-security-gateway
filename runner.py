"""Shared Plan -> Verify -> Feedback -> Re-plan -> Re-verify -> Execute loop."""
from __future__ import annotations

from typing import Callable

import display
from core import Action, Status, Task, VerificationResult
from gateway import SecurityGateway

PlanFn = Callable[[VerificationResult | None], list[Action]]
ToolMap = dict[str, Callable[[dict], dict]]


def run_scenario(title: str, task: Task, plan_fn: PlanFn, tool_map: ToolMap, max_retries: int = 3) -> None:
    display.header(title, task)
    gateway = SecurityGateway()
    feedback: VerificationResult | None = None

    for n in range(1, max_retries + 1):
        display.attempt(n)
        actions = plan_fn(feedback)
        trajectory: list[Action] = []
        blocking_feedback: VerificationResult | None = None

        for action in actions:
            display.action_line(action)
            verdict = gateway.verify(task, action, trajectory)
            display.verdict_line(verdict)
            if verdict.status is Status.FAIL:
                blocking_feedback = verdict.failures[0]
                break
            trajectory.append(action)

        if blocking_feedback is None:
            for action in trajectory:
                result = tool_map[action.tool](action.params)
                display.executed(action, result)
            display.success(title)
            return

        display.blocked(blocking_feedback.feedback)
        feedback = blocking_feedback

    display.exhausted(title)
