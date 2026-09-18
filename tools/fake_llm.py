"""Fake LLM/API layer.

This module exists purely to *show* where a real call to an LLM API
(e.g. Anthropic's Messages API) would go in a production version of this
gateway. No network request is ever made here — no API key is needed and
this costs nothing to run. `mock_llm_judge` prints the prompt that would
have been sent and returns a pre-decided verdict, so the demo reads like
"the agent asked an LLM and got this answer" without actually calling one.
"""
from __future__ import annotations

from typing import Any


def mock_llm_judge(agent_name: str, prompt: str, canned_response: dict[str, Any]) -> dict[str, Any]:
    print(f"    [MOCK LLM CALL] {agent_name} agent -> (no real API call, ANTHROPIC_API_KEY not required)")
    for line in prompt.strip().splitlines():
        print(f"        | {line}")
    print(f"        -> mock response: {canned_response.get('status')} ({canned_response.get('violation_type', 'no violation')})")
    return canned_response
