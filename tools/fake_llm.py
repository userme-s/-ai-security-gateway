"""Offline mock LLM backend.

No network request is ever made here — no API key needed, zero cost. This
prints the exact system/user prompt an agent built (so you can see what
would have been sent to a real model) and returns a pre-decided verdict.
Used when LLM_BACKEND is unset or "mock" (see tools/llm_client.py).
"""
from __future__ import annotations

from typing import Any


def mock_llm_judge(agent_name: str, system_prompt: str, user_prompt: str, canned_response: dict[str, Any]) -> dict[str, Any]:
    print(f"    [MOCK LLM CALL] {agent_name} agent")
    print("        --- system prompt ---")
    for line in system_prompt.strip().splitlines():
        print(f"        | {line}")
    print("        --- user prompt ---")
    for line in user_prompt.strip().splitlines():
        print(f"        | {line}")
    print(f"        -> mock response: {canned_response.get('status')} ({canned_response.get('violation_type', 'no violation')})")
    return canned_response
