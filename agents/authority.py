"""Authority Agent: 'Can the agent do this at all?'

Checks the proposed action against the set of tools that were actually
granted for this task, independent of why the agent wants to use them.
"""
from __future__ import annotations

from core import Action, Status, Task, VerificationResult
from tools.fake_llm import mock_llm_judge


class AuthorityAgent:
    name = "Authority"

    def verify(self, task: Task, action: Action, trajectory: list[Action]) -> VerificationResult:
        granted = action.tool in task.allowed_tools

        prompt = (
            f"Task goal: {task.goal}\n"
            f"Granted tools: {sorted(task.allowed_tools)}\n"
            f"Proposed action: {action.tool}({action.params})\n"
            f"Question: Is this agent authorized to use this tool for this task?"
        )
        canned = (
            {"status": Status.PASS}
            if granted
            else {
                "status": Status.FAIL,
                "violation_type": "PERMISSION_NOT_GRANTED",
                "evidence": f"tool='{action.tool}' is not in the granted tool set {sorted(task.allowed_tools)}",
                "feedback": (
                    f"'{action.tool}' 도구를 사용할 권한이 없습니다. "
                    f"허용된 도구만 사용해 계획을 다시 세우세요: {sorted(task.allowed_tools)}"
                ),
            }
        )
        response = mock_llm_judge(self.name, prompt, canned)

        if response["status"] is Status.FAIL:
            return VerificationResult(
                agent=self.name,
                status=Status.FAIL,
                violation_type=response["violation_type"],
                evidence=response["evidence"],
                feedback=response["feedback"],
            )
        return VerificationResult(agent=self.name, status=Status.PASS)
