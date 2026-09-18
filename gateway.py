"""Security Agent Team gateway.

Runs a proposed action through Authority -> Intent/Trajectory -> Consequence
in order, stopping at the first violation (no need to keep checking an
action that's already blocked).
"""
from __future__ import annotations

from core import Action, GatewayVerdict, Status, Task
from agents.authority import AuthorityAgent
from agents.intent import IntentTrajectoryAgent
from agents.consequence import ConsequenceAgent


class SecurityGateway:
    def __init__(self):
        self.agents = [AuthorityAgent(), IntentTrajectoryAgent(), ConsequenceAgent()]

    def verify(self, task: Task, action: Action, trajectory: list[Action]) -> GatewayVerdict:
        results = []
        for agent in self.agents:
            result = agent.verify(task, action, trajectory)
            results.append(result)
            if result.status is Status.FAIL:
                break
        status = Status.FAIL if any(r.status is Status.FAIL for r in results) else Status.PASS
        return GatewayVerdict(status=status, results=results)
