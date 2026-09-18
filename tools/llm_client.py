"""Single entry point every verification agent calls to get a judgment.

Routes to one of two backends depending on the LLM_BACKEND environment
variable — both are $0 cost:

  LLM_BACKEND unset or "mock"   -> tools/fake_llm.py   (fully offline, deterministic)
  LLM_BACKEND=ollama            -> tools/ollama_client.py (real local model via Ollama)
"""
from __future__ import annotations

import os
from typing import Any

from tools import ollama_client
from tools.fake_llm import mock_llm_judge


def judge(agent_name: str, system_prompt: str, user_prompt: str, canned_response: dict[str, Any]) -> dict[str, Any]:
    backend = os.environ.get("LLM_BACKEND", "mock")
    if backend == "ollama":
        return ollama_client.judge(agent_name, system_prompt, user_prompt, canned_response)
    return mock_llm_judge(agent_name, system_prompt, user_prompt, canned_response)
