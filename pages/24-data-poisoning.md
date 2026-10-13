# 24. LLM05 데이터·모델 포이즈닝

포이즈닝은 시간차를 두고 터지는 공격이다. 공격자가 학습 데이터에 독을 심어 두면, 그 데이터로 학습한 모델은 겉보기에는 정상 동작하다가 특정 조건에서 공격자가 의도한 행동을 한다. 백도어가 심어진 모델은 평소에는 정확도가 멀쩡해서 탐지가 어렵다. 트리거가 입력될 때만 비정상 동작을 하기 때문이다.

LLM05는 적대적이거나 불량한 학습, 파인튜닝 데이터가 편향, 백도어, 불안전 동작을 모델에 심어 놓는 문제를 다룬다. 그런데 이 장에서는 학습 단계의 오염만큼이나 중요한 또 하나의 오염을 함께 다룬다. 배포 산출물의 오염이다. 학습이 끝난 모델은 깨끗해도, 모델을 감싸고 있는 시스템 프롬프트나 설정이 몰래 바뀌면 모델의 행동은 공격자가 원하는 대로 바뀐다. 학습 데이터 오염과 배포 산출물 오염은 공격 지점은 다르지만, 결과는 같다. 믿었던 모델이 더 이상 믿을 수 없게 된다는 점이다.

## 24.1 학습 데이터 오염의 원리

학습 데이터 오염의 기본 아이디어는 단순하다. 모델은 학습 데이터를 그대로 믿는다. 데이터에 편향된 예시가 대량으로 들어 있으면 모델은 그 편향을 학습하고, 특정 트리거 문구에 특정 오답을 연결한 예시가 들어 있으면 모델은 그 연결을 백도어로 기억한다.

오염 경로는 여러 가지다. 웹에서 긁어온 대규모 학습 데이터에 공격자가 오염된 문서를 미리 심어 두는 방법, 크라우드소싱 라벨링 과정에서 악의적인 라벨러가 오답을 주입하는 방법, 파인튜닝용 데이터셋에 몰래 섞인 악성 예시 등이 있다. 파인튜닝은 특히 취약하다. 소량의 데이터로 모델의 행동을 크게 바꾸는 과정이라, 오염된 예시 몇 백 개만으로도 충분한 영향을 줄 수 있다.

탐지가 어려운 이유는 성능 지표가 멀쩡하기 때문이다. 오염된 모델도 일반적인 벤치마크에서는 정상 점수를 낸다. 백도어는 트리거 조건에서만 발동하도록 설계되기 때문이다. 따라서 방어는 사후 탐지보다 사전 예방에 무게가 실린다. 데이터의 출처를 검증하고, 학습 파이프라인의 모든 단계를 감사 로그로 기록하는 것이 핵심이다.

## 24.2 실제 사례: Grok 시스템 프롬프트 무단 변경

학습 데이터 오염의 고전적인 사례가 아니라, 배포 산출물 오염의 관점에서 주목할 만한 사건이 2025년 5월에 발생했다. 대상은 xAI의 Grok이었다.

2025년 5월 14일 오전 3시 15분(PST), 무단으로 수정된 시스템 프롬프트가 배포됐다. 그 결과 Grok은 야구 선수 연봉이나 HBO 같은 완전히 무관한 질문에도 남아공 백인 학살(white genocide) 음모론을 언급하기 시작했다. 사용자가 무엇을 물어도 답변이 특정 음모론으로 끌려가는 기이한 동작이었다.

xAI는 5월 16일에 원인을 설명했다. 코드 리뷰를 우회한 내부 직원의 무단 변경이었다는 것이다. 학습 데이터가 오염된 것도, 모델 가중치가 변조된 것도 아니었다. 모델을 감싸고 있는 시스템 프롬프트라는 배포 산출물 하나가 몰래 바뀌었을 뿐인데, 모델의 행동은 완전히 달라졌다.

재발 방지 대책으로 xAI는 시스템 프롬프트를 GitHub에 공개하고, 추가 검증 절차를 도입하고, 24시간 7일 모니터링 팀을 운영하겠다고 밝혔다. 같은 해 2월에도 비슷한 방식의 주입 전례가 있었다는 점도 함께 알려졌다.

이 사건을 이 장에서 다루는 이유는 분명하다. 학습 단계 오염이 아니어도 모델의 신뢰성은 무너질 수 있다. 시스템 프롬프트는 모델의 헌법과 같은 역할을 한다. 헌법이 몰래 바뀌면 모델의 행동은 바뀌고, 사용자는 그 변화를 알아채기 어렵다. 따라서 배포 파이프라인의 무결성과 변경 감사, 즉 누가, 언제, 무엇을 바꿨는지를 기록하고 통제하는 것이 방어의 핵심이 된다. LLM04 공급망 공격과 맞닿는 지점이지만, 여기서는 특히 모델의 행동을 직접 규정하는 산출물에 초점을 맞춘다.

## 24.3 방어: 출처 검증과 변경 감사

방어는 두 개의 전선에서 이뤄진다. 학습 데이터의 출처 검증과 배포 산출물의 변경 감사다.

예제 1. 학습 데이터 출처 검증

```python
TRUSTED_SOURCES = {"internal-curated", "partner-vetted"}


def verify_dataset_source(dataset_name: str, source: str, checksum: str,
                          registered_checksums: dict) -> bool:
    # 데이터셋을 학습에 쓰기 전에 출처와 체크섬을 확인한다
    if source not in TRUSTED_SOURCES:
        print(dataset_name, "-> 신뢰되지 않은 출처입니다:", source)
        return False
    expected = registered_checksums.get(dataset_name)
    if expected is None or expected != checksum:
        print(dataset_name, "-> 체크섬 불일치. 변조 가능성을 의심합니다.")
        return False
    print(dataset_name, "-> 출처 검증 통과")
    return True


registered = {"finetune-v3": "dummy-sha256-dataset"}
print(verify_dataset_source("finetune-v3", "internal-curated",
                            "dummy-sha256-dataset", registered))
print(verify_dataset_source("finetune-v3", "unknown-forum",
                            "dummy-sha256-dataset", registered))
```

출처가 불분명한 데이터셋은 학습 파이프라인에 들어오지도 못하게 한다. 체크섬 대조는 다운로드 과정에서 데이터가 바뀌지 않았음을 보장한다.

예제 2. 학습 파이프라인 감사 로그

```python
import datetime


class PipelineAuditLog:
    # 학습 파이프라인의 모든 단계를 기록한다
    # 누가, 언제, 무엇을 바꿨는지가 나중에 사고 원인을 추적하는 단서가 된다
    def __init__(self):
        self.entries = []

    def record(self, actor: str, action: str, target: str, detail: str = "") -> None:
        self.entries.append({
            "time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "actor": actor,
            "action": action,
            "target": target,
            "detail": detail,
        })

    def show(self) -> None:
        for e in self.entries:
            print(e["time"], "|", e["actor"], "|", e["action"], "|", e["target"])


audit = PipelineAuditLog()
audit.record("data-eng", "dataset_add", "finetune-v3", "source=internal-curated")
audit.record("ml-eng", "train_start", "model-v7", "base=llm-base-2")
audit.show()
```

Grok 사건에서 문제의 변경이 코드 리뷰를 우회했다는 점에 주목하자. 감사 로그는 우회된 변경을 사후에라도 찾아낼 수 있게 한다. 로그 자체는 변경 불가능한 저장소에 쌓아야 한다. 공격자가 로그까지 지울 수 있으면 감사는 무의미하다.

예제 3. 시스템 프롬프트 변경 이력 관리

```python
class SystemPromptStore:
    # 시스템 프롬프트의 변경은 버전 관리와 승인 절차를 거친다
    def __init__(self):
        self.versions = []
        self.pending = None

    def propose(self, author: str, new_prompt: str) -> int:
        version = len(self.versions) + 1
        self.pending = {"version": version, "author": author,
                        "prompt": new_prompt, "approved_by": None}
        print("변경 제안 등록: v" + str(version), "작성자:", author)
        return version

    def approve(self, reviewer: str) -> bool:
        # 제안자와 승인자가 같으면 승인할 수 없다 (4-eyes 원칙)
        if self.pending is None:
            print("승인할 제안이 없습니다.")
            return False
        if reviewer == self.pending["author"]:
            print("자기 승인은 허용되지 않습니다.")
            return False
        self.pending["approved_by"] = reviewer
        self.versions.append(self.pending)
        print("v" + str(self.pending["version"]), "승인됨. 승인자:", reviewer)
        self.pending = None
        return True

    def current(self) -> str:
        if not self.versions:
            return ""
        return self.versions[-1]["prompt"]

    def history(self) -> list:
        return [{"version": v["version"], "author": v["author"],
                 "approved_by": v["approved_by"]} for v in self.versions]


store = SystemPromptStore()
store.propose("dev-a", "당신은 친절한 비서입니다.")
store.approve("dev-a")
store.approve("reviewer-b")
print("현재 프롬프트:", store.current())
print("변경 이력:", store.history())
```

자기 승인을 막는 4-eyes 원칙이 핵심이다. Grok 사건의 변경이 코드 리뷰를 우회했다는 것은, 우회할 수 있는 구조였다는 뜻이다. 시스템 프롬프트 변경은 반드시 타인의 승인을 거치도록 코드로 강제한다. 모든 버전의 작성자와 승인자가 기록으로 남는다.

## 24.4 실습: 시스템 프롬프트 변경 시 승인 로그를 남기는 래퍼

이번 실습은 방어 실습이다. 시스템 프롬프트를 직접 수정하는 대신, 변경 제안과 승인 과정을 거치도록 강제하는 래퍼를 작성한다. 로컬 환경에서 안전하게 따라 할 수 있다.

1단계. 아래와 같이 프롬프트를 직접 덮어쓰는 위험한 패턴이 있다고 가정한다.

```python
SYSTEM_PROMPT = "당신은 친절한 비서입니다."

# 문제점: 누가 언제 바꿨는지 기록이 남지 않고, 승인 절차가 없다
SYSTEM_PROMPT = "당신은 특정 주장을 반복하는 비서입니다."
```

2단계. 24.3절의 예제 3을 참고해, 프롬프트 변경을 제안-승인 구조로 감싸는 래퍼를 작성한다. 요구사항은 다음과 같다.

- 프롬프트 변수에 직접 대입하는 대신 propose 메서드로 변경을 제안한다.
- approve 메서드는 제안자와 다른 사람이 호출해야만 승인된다.
- 승인된 변경만 current 프롬프트에 반영된다.
- 모든 제안과 승인 시도가 로그에 남는다(거부된 승인 포함).

```python
class GuardedPrompt:
    def __init__(self, initial: str):
        self._current = initial
        self.log = [{"event": "init", "prompt": initial}]

    def propose(self, author: str, new_prompt: str) -> None:
        self.log.append({"event": "proposed", "author": author})
        self._pending = (author, new_prompt)

    def approve(self, reviewer: str) -> bool:
        author, new_prompt = self._pending
        if reviewer == author:
            self.log.append({"event": "approve_rejected", "reviewer": reviewer,
                             "reason": "자기 승인 불가"})
            return False
        self._current = new_prompt
        self.log.append({"event": "approved", "author": author,
                         "reviewer": reviewer})
        return True

    def get(self) -> str:
        return self._current


gp = GuardedPrompt("당신은 친절한 비서입니다.")
gp.propose("dev-a", "당신은 특정 주장을 반복하는 비서입니다.")
print("공격자 자기 승인 시도:", gp.approve("dev-a"))
print("현재 프롬프트:", gp.get())
gp.propose("dev-a", "당신은 특정 주장을 반복하는 비서입니다.")
print("정상 승인:", gp.approve("reviewer-b"))
print("현재 프롬프트:", gp.get())
print("감사 로그:", gp.log)
```

3단계. 위 코드를 실행하고, 공격자가 자기 승인을 시도했을 때 프롬프트가 바뀌지 않고 거부 기록이 남는지 확인한다.

4단계. 한 걸음 더 나아가 보자. 실제 서비스라면 이 래퍼를 어디에 둬야 할까. 프롬프트를 파일로 관리한다면 Git 커밋 훅에, 데이터베이스로 관리한다면 업데이트 트리거에, 관리자 UI가 있다면 저장 버튼 뒤에 이 승인 로직을 붙이는 설계를 그려 본다. 우회 경로가 하나라도 있으면 그 경로가 공격 경로가 된다는 점을 기억하자.

이 실습의 핵심은 변경 통제의 코드화다. "승인받고 바꾸세요"라는 규칙은 문서로 두면 우회되지만, 코드로 강제하면 우회가 어려워진다.

## 24.5 정리

LLM05 데이터, 모델 포이즈닝은 시간차를 두고 터지는 공격이다. 적대적이거나 불량한 학습, 파인튜닝 데이터가 편향과 백도어, 불안전 동작을 모델에 심어 놓는다. 탐지가 어려운 이유는 오염된 모델도 평소에는 정상 동작하기 때문이다.

Grok 사건은 학습 단계가 아닌 배포 산출물의 오염이 얼마나 치명적인지 보여줬다. 2025년 5월 14일 새벽, 코드 리뷰를 우회한 무단 변경으로 시스템 프롬프트 하나가 바뀌었을 뿐인데 Grok은 무관한 질문에도 특정 음모론을 언급하기 시작했다. xAI는 시스템 프롬프트 GitHub 공개, 추가 검증 절차, 24시간 7일 모니터링으로 대응했다.

방어의 핵심은 출처 검증과 변경 감사다. 학습 데이터는 신뢰할 수 있는 출처의 것만 쓰고 체크섬을 대조한다. 학습 파이프라인의 모든 단계는 누가, 언제, 무엇을 바꿨는지 기록한다. 시스템 프롬프트 같은 행동 규정 산출물은 버전 관리와 타인 승인 절차로 보호한다. 믿었던 모델이 계속 믿을 만한 상태인지 확인하는 것이 포이즈닝 방어의 본질이다.

이 책에서 다루는 공격 기법은 모두 학습·방어 목적이며, 허가되지 않은 시스템에 대한 공격 시도는 절대 하지 말 것.
