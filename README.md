# AI Agent Security Gateway

AI Agent가 외부 도구(Tool/API)를 호출하기 **전에**, 서로 다른 세 가지 보안 관점의 검증 에이전트가 행동을 검증하고, 문제가 발견되면 위반 원인과 피드백을 Planner에게 돌려주어 안전한 행동으로 **재계획**하게 하는 Multi-Agent Security Gateway 프로토타입입니다.

> 사후 감시(post-hoc monitoring)가 아니라, 실행 전 검증 → 피드백 → 재계획 → 재검증 구조로 AI Agent의 행동을 통제합니다.

이 프로젝트는 **완전히 오프라인으로 동작하는 데모**입니다. 실제 항공권/호텔/이메일 API는 물론, LLM API(Anthropic API 등)도 전혀 호출하지 않습니다 — 모두 목업(mock)입니다.

## 핵심 아이디어

AI Agent 행동의 보안 문제는 단순히 "권한이 있는가"만으로 판단할 수 없습니다. 이 프로젝트는 세 가지 관점을 분리된 에이전트로 검증합니다.

| 관점 | 질문 | 담당 에이전트 |
|---|---|---|
| **Authority** | 이 행동을 할 권한이 있는가? | `agents/authority.py` |
| **Intent / Trajectory** | 권한이 있어도, 이 행동(흐름)이 현재 task의 목적에 맞는가? | `agents/intent.py` |
| **Consequence** | 행동의 결과가 사용자가 요구한 조건을 만족하는가? | `agents/consequence.py` |

세 에이전트 중 하나라도 위반을 발견하면, 단순히 차단하지 않고 **위반 유형 + 근거(evidence) + 피드백(feedback)** 을 Planner에게 반환합니다. Planner는 이를 받아 계획을 수정하고, 수정된 계획은 다시 세 에이전트의 검증을 거칩니다.

```
사용자 요청
   ↓
Planner (행동 계획 생성)
   ↓
Security Gateway ── Authority → Intent/Trajectory → Consequence
   ↓                                   │
PASS → 실행                        FAIL → Violation + Evidence + Feedback
                                        │
                                   Planner 재계획
                                        │
                                   다시 검증 (재시도, 최대 3회)
```

## 시나리오 3가지

각 시나리오는 한 가지 보안 관점만을 위반하도록 설계되어, 어떤 에이전트가 무엇을 잡아내는지 명확히 보여줍니다.

| 시나리오 | 상황 | 위반 유형 | 잡아내는 에이전트 |
|---|---|---|---|
| 1. Authority | 항공권 예약 작업 중, 권한이 부여되지 않은 `read_contacts`(연락처 조회) 시도 | `PERMISSION_NOT_GRANTED` | Authority |
| 2. Intent/Trajectory | 이메일 접근 권한은 있지만, 예약 확인과 무관하게 전체 메일함을 읽어 외부 서버로 전송 시도 | `TASK_PURPOSE_VIOLATION` | Intent/Trajectory |
| 3. Consequence | 검색·선택·예약 행동은 모두 정상이지만, 최종 결제 금액이 사용자가 지정한 예산(10만원)을 초과 | `EXPECTED_STATE_VIOLATION` | Consequence |

각 시나리오는 먼저 "위반이 발생하는 나쁜 계획"을 시도하고, Gateway가 이를 차단 → 피드백을 반영한 "좋은 계획"으로 재계획 → 재검증 통과 → 실행까지 전체 흐름을 콘솔에 출력합니다.

## 실행 방법

```bash
python3 main.py
```

의존성 없이 Python 표준 라이브러리만 사용합니다 (Python 3.9+).

## 프로젝트 구조

```
core.py                    # Task / Action / VerificationResult 등 공통 데이터 타입
gateway.py                 # 3개 검증 에이전트를 순서대로 호출하는 Security Gateway
runner.py                  # Plan → Verify → Feedback → Re-plan 루프 (최대 재시도 3회)
display.py                 # 콘솔 출력 포맷팅

agents/
  authority.py              # Authority Agent
  intent.py                 # Intent/Trajectory Agent
  consequence.py            # Consequence Agent

tools/
  fake_apis.py               # 항공권/호텔/이메일 등 가짜 외부 세계 (mock 데이터)
  fake_llm.py                 # "LLM에게 판단을 요청한다"는 흐름을 보여주는 목업.
                               # 실제 네트워크 요청 없이 프롬프트만 출력하고 사전에
                               # 정해둔 판단 결과를 반환합니다 (API 키 불필요, 비용 없음).

scenarios/
  scenario1_authority.py     # 시나리오 1: Authority 위반
  scenario2_intent.py        # 시나리오 2: Intent/Trajectory 위반
  scenario3_consequence.py   # 시나리오 3: Consequence 위반

main.py                     # 3개 시나리오 순차 실행
```

## 실제 LLM 연동으로 확장하려면

지금은 각 에이전트의 판단 로직이 규칙 기반(rule-based)이며, `tools/fake_llm.py`가 LLM 호출을 흉내만 냅니다. 실제 Claude API 등으로 교체하려면 `mock_llm_judge()` 호출부를 `anthropic` SDK를 사용한 실제 API 호출로 바꾸면 됩니다 (agents/*.py 세 곳의 `mock_llm_judge(...)` 호출부만 수정하면 됩니다).

## 배경: 왜 세 가지 관점이 필요한가

- 개별 행동은 정상이어도, 행동들을 이어 붙인 **흐름**이 사용자의 원래 목적과 무관할 수 있습니다 (Intent/Trajectory).
- 모든 행동이 권한 안에서, 목적에 맞게 수행되어도 **최종 결과**가 사용자가 명시한 조건(예산, 날짜 등)을 위반할 수 있습니다 (Consequence).
- 따라서 "권한 검사"만으로는 부족하고, `Authority → Intent/Trajectory → Consequence`를 각각 독립적으로 검증한 뒤, 위반 시 구조화된 피드백으로 Agent를 재계획시키는 폐루프(closed loop)가 필요합니다.
