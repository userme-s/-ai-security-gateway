"""Entry point: runs all three Security Agent Team demo scenarios.

Nothing in this project makes a real network call — no API key required,
no cost incurred. The 'LLM calls' inside agents/*.py are mocked in
tools/fake_llm.py purely to illustrate where a real model call would sit.
"""
from __future__ import annotations

from runner import run_scenario
from scenarios import scenario1_authority as s1
from scenarios import scenario2_intent as s2
from scenarios import scenario3_consequence as s3


def main() -> None:
    run_scenario(s1.TITLE, s1.TASK, s1.plan, s1.TOOL_MAP)
    run_scenario(s2.TITLE, s2.TASK, s2.plan, s2.TOOL_MAP)
    run_scenario(s3.TITLE, s3.TASK, s3.plan, s3.TOOL_MAP)


if __name__ == "__main__":
    main()
