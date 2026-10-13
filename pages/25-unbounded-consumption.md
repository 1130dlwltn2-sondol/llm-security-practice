# 25. LLM06 무제한 소비

언어 모델의 추론에는 비용이 든다. 토큰 하나하나가 GPU 시간이고, GPU 시간은 돈이다. LLM06 무제한 소비는 이 당연한 사실을 간과한 시스템에서 발생한다. 통제되지 않은 추론 부하가 비용 폭증, 서비스 거부, 자원 남용으로 이어지는 문제다.

이 항목은 2026년판에서 10위에서 6위로 상승했다. 에이전트와 자동화 호출이 늘어나면서 추론 비용이 운영 리스크로 부상한 흐름이 반영된 결과로 해석된다. 사람이 한 번씩 질문하던 시절에는 비용이 예측 가능했다. 하지만 에이전트가 스스로 반복 호출하고, 자동화 파이프라인이 대량 요청을 날리는 시대에는 이야기가 달라진다. 한 번의 설정 실수나 한 건의 악의적 입력이 수천, 수만 건의 모델 호출로 증폭될 수 있다.

무제한 소비는 보안 사고처럼 보이지 않을 수 있다. 데이터가 유출되는 것도 아니고 시스템이 파괴되는 것도 아니다. 하지만 청구서가 도착하는 순간 운영팀에게는 충분히 심각한 사고다. 그리고 비용 폭증이 서비스 마비로 이어지면 가용성 침해, 즉 DoS와 다를 바 없어진다.

## 25.1 무제한 소비가 발생하는 세 가지 경로

첫 번째 경로는 비용 폭증이다. 모델 호출에 상한이 없으면 예상치 못한 대규모 호출이 그대로 청구로 이어진다. 에이전트의 반복 루프가 종료 조건 없이 돌거나, 사용자가 의도적으로 긴 입력을 반복 전송하면 추론 비용이 기하급수적으로 늘어난다. 특히 자동화 시스템에서는 사람이 중간에 개입할 기회조차 없다.

두 번째 경로는 서비스 거부(DoS)다. 추론 자원은 유한하다. 한 사용자나 한 세션이 자원을 독점하면 다른 사용자의 요청이 처리되지 않는다. 공격자가 고의로 무거운 요청을 대량으로 보내면 서비스 전체가 마비된다. 모델 추론은 일반 웹 요청보다 연산 비용이 훨씬 크기 때문에, 적은 요청으로도 큰 효과를 내는 비대칭적인 DoS가 가능하다.

세 번째 경로는 자원 남용이다. 무료 체험이나 저렴한 요금제를 악용해 모델을 대량 호출하는 경우다. 암호화폐 채굴에 GPU를 도용하던 고전적인 자원 남용이 AI 시대에는 추론 API 남용의 형태로 나타난다. 서비스 제공자의 자원을 공격자의 이익을 위해 쓰는 구조다.

세 가지 경로의 공통점은 통제의 부재다. 호출 횟수, 토큰 사용량, 비용에 대한 상한과 감시가 없으면 어떤 경로로든 문제가 커진다. 방어도 그만큼 명확하다. 한도를 정하고, 속도를 제한하고, 예산을 할당한다.

## 25.2 방어 패턴: 요금 한도, 레이트 리밋, 토큰 예산

실무에서 무제한 소비를 막는 방어 패턴은 세 가지로 정리된다.

요금 한도는 비용에 대한 상한선이다. 일별, 월별, 프로젝트별로 지출 한도를 정하고, 한도에 접근하면 알림을 보내고, 한도를 넘으면 호출을 차단한다. 알림만 보내고 차단은 하지 않는 설정이 많은데, 공격 상황에서는 알림을 보는 사이에 비용이 계속 쌓인다. 자동 차단까지 연결해야 실효성이 있다.

레이트 리밋은 속도에 대한 제한이다. 사용자별, API 키별, IP별로 단위 시간당 호출 횟수를 제한한다. 정상 사용자의 사용 패턴을 분석해 합리적인 상한을 정한다. 급격한 호출 증가는 그 자체로 이상 징후이므로, 임계값을 넘으면 일시 차단하고 경고를 발생시킨다.

토큰 예산은 사용량에 대한 할당이다. 사용자별, 세션별로 쓸 수 있는 토큰량을 미리 정한다. 입력 토큰과 출력 토큰을 합산해 계산하고, 예산을 초과하면 요청을 거부한다. 에이전트처럼 반복 호출하는 주체에게는 호출 체인 전체에 걸친 총예산을 부여한다. 개별 호출은 적법해 보여도 합산하면 과도한 경우가 많기 때문이다.

세 가지 패턴은 서로 보완 관계다. 레이트 리밋은 순간적인 폭주를 막고, 토큰 예산은 누적 사용량을 통제하고, 요금 한도는 최종적인 비용 상한을 보장한다. 하나만으로는 구멍이 생긴다. 겹겹이 쌓아야 한다.

## 25.3 방어 코드 예제

아래 코드는 세 가지 방어 패턴을 하나의 미들웨어로 구현한 예제다.

예제 1. 레이트 리밋

```python
import time


class RateLimiter:
    # 사용자별로 단위 시간당 호출 횟수를 제한한다
    def __init__(self, max_calls: int, window_seconds: int):
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self.calls = {}

    def allow(self, user_id: str) -> bool:
        now = time.time()
        history = self.calls.get(user_id, [])
        history = [t for t in history if now - t < self.window_seconds]
        if len(history) >= self.max_calls:
            self.calls[user_id] = history
            return False
        history.append(now)
        self.calls[user_id] = history
        return True


limiter = RateLimiter(max_calls=10, window_seconds=60)
for i in range(12):
    print(i, "허용" if limiter.allow("user_001") else "차단")
```

분당 10회로 제한한 예제다. 11번째 호출부터 차단된다. 슬라이딩 윈도우 방식으로 구현했기 때문에, 시간이 지나면 오래된 호출 기록은 자동으로 만료된다.

예제 2. 사용자, 세션별 토큰 예산

```python
class TokenBudget:
    # 사용자별, 세션별로 쓸 수 있는 토큰량을 할당한다
    def __init__(self, budget_per_user: int):
        self.budget_per_user = budget_per_user
        self.used = {}

    def consume(self, user_id: str, input_tokens: int,
                output_tokens: int) -> dict:
        total = input_tokens + output_tokens
        spent = self.used.get(user_id, 0)
        if spent + total > self.budget_per_user:
            return {"ok": False,
                    "error": "토큰 예산을 초과했습니다.",
                    "spent": spent,
                    "budget": self.budget_per_user}
        self.used[user_id] = spent + total
        return {"ok": True, "spent": self.used[user_id],
                "budget": self.budget_per_user}


budget = TokenBudget(budget_per_user=10000)
print(budget.consume("user_001", 3000, 1000))
print(budget.consume("user_001", 5000, 3000))
```

두 번째 호출에서 누적 사용량이 예산 10000을 넘으므로 차단된다. 입력과 출력 토큰을 합산하는 점에 유의하자. 출력 토큰은 모델이 생성하기 전까지 정확히 알 수 없으므로, 실무에서는 예상 최대치를 기준으로 사전 차감하고 실제 사용량으로 정산하는 방식을 쓴다.

예제 3. 요금 한도 알림과 자동 차단

```python
class CostGuard:
    # 지출 한도에 접근하면 알림을 보내고, 초과하면 차단한다
    def __init__(self, daily_limit_usd: float, warn_ratio: float = 0.8):
        self.daily_limit = daily_limit_usd
        self.warn_ratio = warn_ratio
        self.spent = 0.0
        self.warned = False
        self.blocked = False

    def charge(self, amount_usd: float) -> dict:
        if self.blocked:
            return {"ok": False, "error": "일일 요금 한도 초과로 차단되었습니다."}
        self.spent += amount_usd
        if self.spent >= self.daily_limit:
            self.blocked = True
            return {"ok": False, "error": "일일 요금 한도에 도달했습니다. 호출을 중단합니다."}
        if not self.warned and self.spent >= self.daily_limit * self.warn_ratio:
            self.warned = True
            print("경고: 일일 요금 한도의 80%에 도달했습니다.")
        return {"ok": True, "spent": round(self.spent, 4)}


guard = CostGuard(daily_limit_usd=50.0)
print(guard.charge(30.0))
print(guard.charge(15.0))
print(guard.charge(10.0))
print(guard.charge(1.0))
```

80% 지점에서 경고를 보내고, 한도에 도달하면 자동으로 차단한다. 경고에서 멈추지 않고 차단까지 연결하는 것이 핵심이다. 공격 상황에서 사람이 경고를 보고 대응하기를 기다리면 이미 늦다.

## 25.4 실습: 토큰 예산을 초과하면 차단하는 미들웨어

이번 실습은 방어 실습이다. 모델 호출 앞단에 토큰 예산 검사 미들웨어를 두고, 예산을 초과하면 호출을 차단하는 구조를 직접 만든다. 로컬 환경에서 안전하게 따라 할 수 있다.

1단계. 아래와 같이 예산 검사 없이 모델을 호출하는 함수가 있다고 가정한다.

```python
def call_model(prompt: str) -> str:
    # 문제점: 호출 횟수와 토큰 사용량에 제한이 없다
    return "모델 응답 더미"


for i in range(100):
    call_model("긴 문서 요약해줘 " * 100)
```

2단계. 25.3절의 예제들을 조합해, 호출 전에 예산을 검사하는 미들웨어를 작성한다. 요구사항은 다음과 같다.

- 사용자별 토큰 예산을 관리한다.
- 프롬프트의 길이를 기준으로 입력 토큰을 어림잡는다(예: 글자 수 나누기 4).
- 예산 초과 시 모델을 호출하지 않고 차단 메시지를 반환한다.
- 차단된 호출은 로그에 남긴다.

```python
class BudgetMiddleware:
    def __init__(self, budget_per_user: int):
        self.budget_per_user = budget_per_user
        self.used = {}
        self.blocked_log = []

    def estimate_tokens(self, text: str) -> int:
        # 간단한 어림셈: 글자 수 나누기 4
        # 실제 서비스에서는 토크나이저로 정확히 계산한다
        return max(1, len(text) // 4)

    def __call__(self, user_id: str, prompt: str) -> str:
        need = self.estimate_tokens(prompt)
        spent = self.used.get(user_id, 0)
        if spent + need > self.budget_per_user:
            self.blocked_log.append({"user": user_id, "prompt_len": len(prompt)})
            return "차단: 토큰 예산을 초과했습니다."
        self.used[user_id] = spent + need
        return call_model(prompt)


def call_model(prompt: str) -> str:
    return "모델 응답 더미"


mw = BudgetMiddleware(budget_per_user=1000)
for i in range(10):
    result = mw("user_001", "긴 문서 요약해줘 " * 100)
    print(i, result[:20], "| 누적:", mw.used.get("user_001", 0))
print("차단 기록:", mw.blocked_log)
```

3단계. 위 코드를 실행하고, 몇 번째 호출부터 차단되는지 확인한다. 예산을 다르게 설정해 보면서 차단 지점이 어떻게 바뀌는지 관찰한다.

4단계. 한 걸음 더 나아가 보자. 에이전트처럼 한 번의 사용자 요청이 여러 번의 모델 호출로 이어지는 구조에서는 개별 호출 예산이 아니라 요청 전체의 총예산을 관리해야 한다. BudgetMiddleware에 request_id 개념을 추가해, 같은 요청에 속한 호출들의 토큰을 합산하는 방식으로 확장해 본다. 개별 호출은 적법해 보여도 합산하면 과도한 경우를 잡아내는 것이 목표다.

이 실습의 핵심은 호출 앞단의 게이트다. 모델 호출 함수는 예산을 모른다. 예산 검사는 호출보다 먼저, 호출과 분리된 계층에서 이뤄져야 한다. 그래야 우회되지 않는다.

## 25.5 정리

LLM06 무제한 소비는 2026년판에서 10위에서 6위로 상승했다. 에이전트와 자동화 호출이 늘어나면서 추론 비용이 운영 리스크로 부상한 흐름이 반영된 결과로 해석된다. 통제되지 않은 추론 부하는 비용 폭증, 서비스 거부, 자원 남용으로 이어진다.

방어는 세 가지 패턴의 조합이다. 요금 한도는 비용의 상한을 정하고 초과 시 자동으로 차단한다. 레이트 리밋은 단위 시간당 호출 속도를 제한해 순간적인 폭주를 막는다. 토큰 예산은 사용자별, 세션별로 쓸 수 있는 양을 할당해 누적 사용량을 통제한다. 어느 하나만으로는 구멍이 생기므로 겹겹이 쌓아야 한다.

이 장에는 특정 사고 사례를 싣지 않았다. 무제한 소비는 하나의 사건으로 기억되기보다, 한도를 정하지 않은 모든 시스템에 잠재된 구조적 위험에 가깝기 때문이다. 청구서가 날아오기 전에 한도를 정하자. 비용 통제는 사후 정산이 아니라 사전 설계의 영역이다.

이 책에서 다루는 공격 기법은 모두 학습·방어 목적이며, 허가되지 않은 시스템에 대한 공격 시도는 절대 하지 말 것.
