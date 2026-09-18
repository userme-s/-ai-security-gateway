"""Real local LLM calls via Ollama (http://localhost:11434).

$0 cost — the model runs entirely on your own machine, no API key, no
network egress once the model is pulled. Used when LLM_BACKEND=ollama
(see tools/llm_client.py). If Ollama isn't running or the model's output
can't be parsed as the expected JSON, this falls back to the same canned
response the mock backend would have returned, so a demo run never
hard-crashes just because the local model server is down.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

from core import Status

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/chat")
MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:1b")


def judge(agent_name: str, system_prompt: str, user_prompt: str, canned_response: dict[str, Any]) -> dict[str, Any]:
    print(f"    [OLLAMA CALL] {agent_name} agent -> model={MODEL} (local, $0 cost)")
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "format": "json",
        "stream": False,
    }
    try:
        req = urllib.request.Request(
            OLLAMA_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read())
        content = body["message"]["content"]
        parsed = json.loads(content)
    except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError, OSError) as e:
        print(f"        [!] Ollama call failed ({e}) -> falling back to canned response")
        return canned_response

    status_str = str(parsed.get("status", "")).upper()
    status = Status.PASS if status_str == "PASS" else Status.FAIL
    print(f"        -> ollama response: {status_str or 'UNPARSEABLE'} ({parsed.get('violation_type', 'no violation')})")

    if status is Status.FAIL:
        return {
            "status": Status.FAIL,
            "violation_type": parsed.get("violation_type", "UNKNOWN_VIOLATION"),
            "evidence": parsed.get("evidence", ""),
            "feedback": parsed.get("feedback", ""),
        }
    return {"status": Status.PASS}
