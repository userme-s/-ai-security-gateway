"""Console pretty-printing helpers for the demo. No external deps."""
from __future__ import annotations

from core import Action, GatewayVerdict, Status, Task

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def header(title: str, task: Task) -> None:
    print("\n" + "=" * 70)
    print(f"{BOLD}{CYAN}{title}{RESET}")
    print("=" * 70)
    print(f"목표: {task.goal}")
    print(f"허용된 도구: {sorted(task.allowed_tools)}")
    if task.constraints:
        print(f"제약조건: {task.constraints}")


def attempt(n: int) -> None:
    print(f"\n{BOLD}--- 시도 {n}: Planner가 행동 계획 생성 ---{RESET}")


def action_line(action: Action) -> None:
    print(f"\n[Step {action.step}] {BOLD}{action.tool}{RESET}({action.params})")
    print(f"    목적: {action.purpose}")


def verdict_line(verdict: GatewayVerdict) -> None:
    for r in verdict.results:
        if r.status is Status.PASS:
            print(f"    {GREEN}[{r.agent}] PASS{RESET}")
        else:
            print(f"    {RED}[{r.agent}] FAIL - {r.violation_type}{RESET}")
            print(f"        evidence: {r.evidence}")
            print(f"        feedback: {r.feedback}")


def blocked(feedback_text: str) -> None:
    print(f"\n{YELLOW}>>> 계획 차단됨. Feedback을 Planner에게 전달하여 재계획합니다.{RESET}")
    print(f"    feedback: {feedback_text}")


def executed(action: Action, result: dict) -> None:
    print(f"    {GREEN}[실행]{RESET} {action.tool}({action.params}) -> {result}")


def success(title: str) -> None:
    print(f"\n{GREEN}{BOLD}=== {title}: 모든 검증 통과, 안전하게 실행 완료 ==={RESET}")


def exhausted(title: str) -> None:
    print(f"\n{RED}{BOLD}!!! {title}: 최대 재시도 초과 - 사람의 승인이 필요합니다 !!!{RESET}")
