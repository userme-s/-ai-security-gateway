"""Consequence Agent: 'Even if authorized and on-task, does the resulting
state actually satisfy the constraints the user originally asked for?'
"""
from __future__ import annotations

from core import Action, Status, Task, VerificationResult
from tools.fake_llm import mock_llm_judge

BOOKING_TOOLS = {"book_hotel", "book_flight"}


class ConsequenceAgent:
    name = "Consequence"

    def verify(self, task: Task, action: Action, trajectory: list[Action]) -> VerificationResult:
        violation = None

        if action.tool in BOOKING_TOOLS:
            max_price = task.constraints.get("max_price")
            price = action.params.get("price")
            if max_price is not None and price is not None and price > max_price:
                violation = {
                    "violation_type": "EXPECTED_STATE_VIOLATION",
                    "evidence": f"expected price<={max_price}, actual price={price}",
                    "feedback": (
                        f"예산 조건({max_price:,}원 이하)을 초과했습니다. "
                        f"조건을 만족하는 항목을 다시 찾아 계획을 세우세요."
                    ),
                }

        prompt = (
            f"Task goal: {task.goal}\n"
            f"Constraints: {task.constraints}\n"
            f"Proposed action: {action.tool}({action.params})\n"
            f"Question: If executed, does the resulting state satisfy the user's constraints?"
        )
        canned = {"status": Status.FAIL, **violation} if violation else {"status": Status.PASS}
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
