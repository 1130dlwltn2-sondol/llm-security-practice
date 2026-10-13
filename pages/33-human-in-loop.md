# 33. 사람 승인(휴먼인더루프) 설계

아무리 정교한 가드레일을 쌓아도, 어떤 결정은 사람의 눈으로 확인해야 한다. 사람 승인(HITL, Human-in-the-Loop)은 자동화의 흐름 중간에 사람을 끼워 넣어 최종 판단을 맡기는 설계다. 이 장에서는 언제 사람을 끼워 넣을지, 승인을 어떻게 요청하면 피로하지 않을지, 승인 기록을 어떻게 남길지를 다룬다. Part 3의 다른 장치가 '자동으로 막는' 것이라면, 이 장은 '사람이 보고 막는' 최후의 장치다.

## 33.1 언제 사람을 끼워 넣을 것인가

모든 액션에 승인을 요구하면 시스템이 멈춘다. 아무 데도 승인을 두지 않으면 사고가 터진다. 기준이 필요하다. 실무에서 쓰는 기준은 두 가지다.

첫째, 민감한 액션이다. 돈이 움직이는 일(결제, 환불, 송금), 외부로 메시지가 나가는 일(고객 발송, 공개 게시), 개인정보를 다루는 일이 여기에 해당한다. 이런 액션은 에이전트의 판단만으로 실행되지 않게 한다.

둘째, 되돌릴 수 없는 액션이다. 삭제, 계약 체결, 설정 변경처럼 실행 후 원상 복구가 어렵거나 불가능한 일이다. 되돌릴 수 있는 일은 사후에 고치면 되지만, 되돌릴 수 없는 일은 사전에 막아야 한다.

두 기준을 조합하면 판단이 쉬워진다. "민감하고 되돌릴 수 없음"이면 반드시 사전 승인, "민감하지만 되돌릴 수 있음"이면 사후 알림, "민감하지 않음"이면 자동 실행이다. 이 차등 적용이 다음 절의 위험 등급으로 이어진다.

기준을 정할 때는 "이 액션이 잘못 실행됐을 때 되돌리는 데 드는 비용"을 구체적으로 따져본다. 잘못 보낸 이메일 한 통의 비용, 잘못 삭제된 데이터의 복구 비용을 숫자로 적어 보면 등급이 저절로 정해진다. 감으로 정한 등급은 운영 중에 흔들린다.

```python
def needs_approval(action: dict) -> str:
    sensitive = action.get("sensitive", False)
    reversible = action.get("reversible", True)
    if sensitive and not reversible:
        return "approve"   # 사전 승인 필수
    if sensitive and reversible:
        return "notify"    # 실행 후 알림
    return "auto"          # 자동 실행

print(needs_approval({"sensitive": True, "reversible": False}))  # approve
print(needs_approval({"sensitive": True, "reversible": True}))   # notify
print(needs_approval({"sensitive": False, "reversible": True}))  # auto
```

## 33.2 승인 UX: 요약, 차이점, 원클릭

승인을 요청할 때 사람이 실제로 판단할 수 있게 만들어야 한다. "승인하시겠습니까?"라는 말만 던지면 사람은 내용을 보지 않고 클릭하게 된다. 좋은 승인 요청은 세 요소를 갖는다.

첫째, 요약이다. 에이전트가 하려는 일을 한두 문장으로 정리한다. "A-123 주문을 45,000원에 환불 처리합니다"처럼, 판단에 필요한 핵심만 담는다.

둘째, 차이점 표시다. 변경 전과 변경 후를 나란히 보여준다. 설정 변경이라면 바뀌는 값의 전후를, 문서 수정이라면 수정된 부분을 표시한다. 사람은 차이점을 볼 때 가장 정확하게 판단한다.

셋째, 원클릭 승인/거부다. 승인 버튼 하나, 거부 버튼 하나. 거부할 때는 사유를 적을 수 있게 하되 필수는 아니다. 절차가 복잡하면 사람은 승인을 미루거나 대충 누르게 된다.

```python
def build_approval_request(action: dict) -> dict:
    return {
        "title": "승인 요청: " + action["name"],
        "summary": action["summary"],          # 한두 문장 요약
        "diff": action.get("diff", ""),        # 변경 전후 차이
        "risk": action.get("risk", "medium"),  # 위험 등급
        "actions": ["approve", "reject"],      # 원클릭 선택지
        "expires_in_min": 30,                  # 승인 유효 시간
    }

req = build_approval_request({
    "name": "환불 처리",
    "summary": "A-123 주문을 45,000원에 환불 처리합니다.",
    "diff": "주문 상태: 배송중 -> 환불완료 / 금액: 45,000원",
    "risk": "high",
})
print(req["title"])
print(req["summary"])
```

승인 유효 시간도 중요하다. 승인을 받고 너무 오래 지나면 상황이 바뀌어 있을 수 있다. 30분 같은 유효 시간을 두고, 만료되면 다시 요청하게 한다.

## 33.3 승인 로그: 누가, 언제, 무엇을

승인 기록은 반드시 남긴다. 나중에 "누가 이걸 승인했나?"라는 질문에 답할 수 있어야 하기 때문이다. 감사 추적의 기본이다.

로그에 남길 항목은 다섯 가지다. 요청 시각, 승인자, 액션 내용(요약), 판단(승인/거부), 판단 시각이다. 거부된 요청도 남긴다. 거부 기록은 에이전트의 판단 품질을 개선하는 자료가 된다.

```python
import datetime

APPROVAL_LOG = []

def record_approval(request: dict, approver: str, decision: str) -> None:
    APPROVAL_LOG.append({
        "requested_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "approver": approver,
        "action": request["title"],
        "summary": request["summary"],
        "decision": decision,  # approve 또는 reject
    })

record_approval(req, "kim.manager@example.com", "approve")
print(APPROVAL_LOG[0]["decision"])  # approve
```

승인 로그는 위변조가 어려우 게 보관한다. 일반 로그와 분리해 append-only 형태로 쌓는 것이 좋다. 누가 승인했는지를 나중에 부인할 수 없게 만드는 것이 목적이다.

## 33.4 과도한 승인은 피로도를 낳는다

사람 승인의 가장 큰 적은 승인 피로(alert fatigue)다. 승인 요청이 너무 자주 오면 사람은 내용을 보지 않고 승인 버튼을 누르는 기계가 된다. 그러면 승인은 보안 장치가 아니라 형식적 절차로 전락한다.

대책은 위험 등급별 차등 적용이다. 모든 액션을 같은 무게로 다루지 않는다.

- low: 자동 실행. 사후에 로그만 남긴다.
- medium: 실행 후 알림. 사람은 사후에 확인하고, 이상하면 되돌린다.
- high: 사전 승인 필수. 사람이 승인해야 실행된다.

```python
RISK_POLICY = {
    "low": {"mode": "auto"},
    "medium": {"mode": "notify"},
    "high": {"mode": "approve"},
}

def apply_policy(action: dict) -> dict:
    risk = action.get("risk", "low")
    mode = RISK_POLICY[risk]["mode"]
    if mode == "approve":
        return {"next": "승인 요청 생성", "request": build_approval_request(action)}
    if mode == "notify":
        return {"next": "실행 후 알림 발송"}
    return {"next": "자동 실행, 로그 기록"}

print(apply_policy({"name": "주문 조회", "risk": "low", "summary": "A-123 조회"}))
print(apply_policy({"name": "전액 환불", "risk": "high", "summary": "A-123 전액 환불"}))
```

등급 기준은 서비스 초기에 정하고 문서화한다. "금액 10만 원 이상 환불은 high" 같은 구체적 기준이어야 한다. 기준이 모호하면 에이전트도, 사람도 매번 헷갈린다. 운영하면서 승인 요청의 양을 모니터링하고, high 요청이 너무 많으면 기준을 손본다. 승인이 일상이 되면 피로가 오고, 피로가 오면 승인이 무력화된다는 것을 잊지 말자.

승인 요청량 자체도 지표로 관리한다. 일별 승인 요청 수, 승인율, 평균 판단 시간을 추적한다. 승인율이 99퍼센트를 넘으면 사실상 자동 승인과 다름없다. 기준이 너무 느슨하거나, 승인자가 내용을 보지 않고 있다는 신호다. 반대로 거부율이 갑자기 오르면 에이전트의 판단 품질에 문제가 생긴 것이다. 승인 로그(33.3절)는 쌓아 두는 것이 아니라 읽는 것이다.

```python
def approval_stats(log: list) -> dict:
    total = len(log)
    approved = sum(1 for e in log if e["decision"] == "approve")
    return {
        "total": total,
        "approval_rate": round(approved / total, 3) if total else 0,
    }
```

## 33.5 승인 UX 안티패턴

승인 설계를 망치는 흔한 실수 세 가지를 정리한다.

첫째, 정보 없는 승인 요청이다. "다음 작업을 승인하시겠습니까? [작업 ID: 48291]" 같은 요청은 사람이 판단할 수 없다. 사람은 결국 무조건 승인하거나, 귀찮아서 전부 거부한다. 33.2절의 요약과 차이점이 빠지면 승인은 형식 절차가 된다.

둘째, 거부가 어려운 구조다. 승인 버튼은 크고 눈에 띄는데, 거부하려면 숨겨진 메뉴를 열어야 하는 식이다. 거부 경로가 어려우면 사람은 승인 쪽으로 기울어진다. 승인 UI에서는 승인과 거부를 동등하게 둔다.

셋째, 만료 없는 승인이다. 한 번 받은 승인을 무기한으로 유효하게 두면, 나중에 상황이 바뀌어도 예전 승인으로 실행된다. 33.2절에서 다룬 유효 시간을 반드시 둔다. 재사용 가능한 승인은 '승인'이 아니라 '권한 부여'이며, 그건 32장의 도구 스코핑 문제다.

```python
import time

def is_approval_valid(granted_at: float, ttl_sec: int = 1800) -> bool:
    return (time.time() - granted_at) <= ttl_sec

# 사용: 승인 후 실행 직전에 유효성을 다시 확인한다.
# if not is_approval_valid(approval["granted_at"]):
#     승인을 다시 요청한다.
```

승인 UX의 목표는 한 문장으로 정리된다. "바쁜 사람이 10초 안에 정확히 판단할 수 있게 하라." 이 기준에 못 미치는 승인 요청은 없는 것보다 못하다. 형식적 절차가 실질적 검토를 대체해 버리기 때문이다.

## 33.6 실습: 위험 등급별 승인 정책을 코드로 표현

이번 장의 실습은 33.1절과 33.4절의 코드를 합쳐 작은 승인 정책 엔진을 만드는 것이다. 로컬에서 안전하게 따라 할 수 있는 방어 실습이다.

목표: 액션 목록을 받아 위험 등급을 매기고, 등급에 맞는 처리(자동/알림/승인 요청)를 결정하는 함수를 완성한다.

1. 새 파이썬 파일을 만들고 33.1절의 needs_approval, 33.2절의 build_approval_request, 33.4절의 RISK_POLICY와 apply_policy를 복사한다.
2. 아래 액션 목록에 대한 위험 등급 분류 함수를 작성한다. 등급 기준은 스스로 정하되, 문서화(주석)한다.

```python
ACTIONS = [
    {"name": "주문 조회", "summary": "A-123 주문 정보를 조회합니다."},
    {"name": "배송지 변경", "summary": "A-123 배송지를 변경합니다."},
    {"name": "부분 환불", "summary": "A-123 주문을 20,000원 부분 환불합니다."},
    {"name": "전액 환불", "summary": "A-123 주문을 450,000원 전액 환불합니다."},
    {"name": "고객 이메일 발송", "summary": "고객에게 사과 이메일을 발송합니다."},
    {"name": "주문 데이터 삭제", "summary": "A-123 주문 기록을 삭제합니다."},
]

def classify(action: dict) -> str:
    # 여기에 등급 기준을 코드로 작성한다. 예시:
    # - 삭제, 전액 환불 -> high
    # - 부분 환불, 외부 발송 -> medium
    # - 조회 -> low
    raise NotImplementedError
```

3. classify를 완성한 뒤 각 액션에 apply_policy를 적용하고 결과를 출력한다. "주문 데이터 삭제"가 사전 승인으로 걸리는지 확인한다.
4. 확인할 것: high로 분류된 액션에 대해 build_approval_request가 요약과 차이점, 원클릭 선택지를 포함한 요청을 만드는지.
5. 보너스 과제: 승인 요청이 30분 안에 처리되지 않으면 어떻게 할지 정책을 정하고 코드에 반영한다. 선택지는 '자동 거부', '에스컬레이션(상위 승인자에게 전달)', '재요청' 중 하나다. 각각의 장단점을 주석으로 적어 본다.
6. 완성된 정책 엔진에 33.4절의 approval_stats를 붙여, 액션 목록 전체의 승인율을 계산해 본다. high 액션이 전체의 몇 퍼센트인지 확인하고, 승인 피로 관점에서 적절한 수준인지 스스로 평가해 본다.

이 실습을 마치면 승인이 '그냥 사람이 확인하는 절차'가 아니라 '위험 등급에 따라 다르게 동작하는 정책'이라는 감각이 생긴다. Part 3 전체를 관통하는 메시지이기도 하다. 보안은 막는 것이 아니라, 위험에 맞게 다르게 대하는 것이다.

## 33.7 정리

- 사람 승인은 되돌릴 수 없는 결정 앞에서 최후의 판단자를 두는 설계다.
- 끼워 넣을 기준은 두 가지다. 민감한 액션인가, 되돌릴 수 없는 액션인가.
- 좋은 승인 UX는 요약, 차이점 표시, 원클릭 승인/거부로 이루어진다. 판단할 수 있는 정보를 줘야 승인이 의미가 있다.
- 승인 로그는 반드시 남긴다. 누가, 언제, 무엇을 승인(또는 거부)했는지 추적할 수 있어야 한다.
- 과도한 승인은 피로도를 낳아 승인을 무력화한다. 위험 등급별 차등 적용(low 자동, medium 사후 알림, high 사전 승인)이 정석이다.
- 승인 로그는 쌓아 두는 것이 아니라 읽는 것이다. 승인율과 판단 시간을 추적해 기준을 손본다.
