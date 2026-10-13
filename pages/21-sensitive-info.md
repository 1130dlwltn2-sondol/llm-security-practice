# 21. LLM02 민감정보 노출

언어 모델이 해서는 안 될 말을 하는 경우는 두 가지다. 하나는 모델이 학습 단계에서 민감정보를 외워 버린 경우고, 다른 하나는 서비스 구조가 권한 없는 데이터를 모델의 손에 쥐여 주는 경우다. LLM02 민감정보 노출은 후자에 가깝다. 모델 자체의 결함이라기보다, 모델 주변 시스템의 설계 결함이 원인이 되는 경우가 대부분이다.

가장 전형적인 패턴은 RAG(검색 증강 생성)에서의 권한 우회다. 사용자가 볼 권한이 없는 문서가 검색 단계에서 걸러지지 않고 모델의 컨텍스트에 들어간다. 모델은 그 문서가 이 사용자에게 보여도 되는 문서인지 판단하지 못한다. 컨텍스트에 들어온 이상, 사용자의 질문에 답하는 재료로 쓸 뿐이다. 권한 검사는 모델이 아니라 검색 파이프라인이 해야 할 일인데, 그 검사가 빠져 있는 시스템이 의외로 많다.

이 항목에서 가장 신뢰할 만한 통제는 명확하다. 민감 데이터를 처음부터 모델에 가까이 두지 않고, 검색 전에 사용자 권한을 확인하는 것이다. 모델이 모르는 데이터는 유출할 수 없다. 권한 없는 데이터가 컨텍스트에 들어오지 않으면 모델이 실수로라도 뱉어낼 일이 없다. 단순하지만 가장 확실한 원칙이다.

## 21.1 RAG 권한 우회의 원리

RAG 시스템의 일반적인 흐름을 보자. 사용자가 질문하면 벡터 데이터베이스에서 관련 문서를 검색하고, 검색된 문서를 프롬프트에 붙여 모델에게 전달하고, 모델이 문서를 근거로 답변을 생성한다. 문제는 검색 단계다.

많은 RAG 구현이 검색을 할 때 사용자 권한을 고려하지 않는다. 전체 문서 집합에서 유사도가 높은 문서를 가져온 뒤에야 접근 권한을 확인하거나, 아예 확인하지 않는다. 전자의 경우에도 위험하다. 권한 없는 문서가 모델 컨텍스트에 한 번 들어가면, 이후 단계에서 걸러진다고 해도 모델이 이미 그 내용을 읽었기 때문이다. 모델이 읽은 내용은 답변에 스며들 수 있다.

더 근본적인 문제는 권한 모델의 불일치다. 원본 시스템(예: 사내 위키, 문서 관리 시스템)에는 문서별, 사용자별 접근 권한이 촘촘하게 설정되어 있다. 그런데 RAG용으로 문서를 벡터 데이터베이스에 복제하면서 권한 정보가 떨어져 나간다. 검색 인덱스에는 문서 내용과 임베딩만 있고, 누가 볼 수 있는 문서인지에 대한 정보는 없다. 권한이 증발한 검색 계층이 만들어지는 것이다.

또 하나의 원인은 과도한 컨텍스트다. 관련 문서를 넉넉하게 가져오려는 욕심에 top-k 값을 크게 잡으면, 질문과 엉뚱하게 연결된 민감 문서까지 딸려 들어온다. 검색 정확도와 보안은 트레이드오프 관계가 아니라, 보안이 먼저다. 권한 없는 문서 1건이 컨텍스트에 들어오는 순간 검색 정확도는 의미가 없어진다.

## 21.2 실제 사례: DeepSeek 데이터베이스 노출

2026년 1월, 보안 업체 Wiz가 충격적인 보고서를 발표했다. 중국의 AI 기업 DeepSeek의 내부 데이터베이스 2개가 인터넷에 인증 없이 공개되어 있었다는 내용이었다.

발견 시점은 2025년 1월 29일부터 30일 사이였다. 문제가 된 데이터베이스는 oauth2callback.deepseek.com:9000과 dev.deepseek.com:9000에 있던 ClickHouse 데이터베이스 2개다. 두 데이터베이스 모두 인증 없이 외부에서 접속할 수 있는 상태였다.

내부에는 log_stream이라는 테이블이 있었고, 100만 건이 넘는 평문 로그가 쌓여 있었다. 내용은 사용자 채팅 기록, API 키, 백엔드 상세 정보, 운영 메타데이터까지 포함했다. 로그 축적은 2025년 1월 6일부터 시작됐으니, 약 3주 분량의 운영 데이터가 그대로 노출된 셈이다.

더 심각한 점은 읽기 권한을 넘어선 문제였다. 인증 없이 임의의 SQL 쿼리를 실행할 수 있었고, 이를 통한 특권 상승까지 가능했다. 단순한 정보 노출을 넘어 데이터베이스 전체를 장악할 수 있는 상태였다는 의미다.

Wiz의 책임 있는 공개 이후 DeepSeek는 약 1시간 만에 접근을 차단했다. 대응 속도는 빨랐지만, 그 전에 누군가 데이터를 가져갔는지는 확인되지 않았다. 사전 악용 여부는 미확인으로 남아 있다.

이 사건이 LLM02와 연결되는 지점은 명확하다. 민감 데이터가 모델 주변 시스템에 평문으로, 그것도 인증 없이 접근 가능한 상태로 방치되어 있었다. 모델이 유출한 것이 아니라 인프라가 유출한 것이다. LLM02의 방어는 모델 튜닝이 아니라 데이터 아키텍처와 접근 통제의 문제임을 보여주는 사례다.

## 21.3 방어: 검색 전 권한 확인

이 절에서는 RAG 파이프라인에 권한 필터를 넣는 방법을 코드로 살펴본다. 핵심 원칙은 검색 쿼리를 날리기 전에 사용자가 볼 수 있는 문서 집합을 먼저 확정하는 것이다.

![권한 확인 후 검색 RAG 구조](assets/rag-access-control.png)

예제 1. 권한 필터가 적용된 검색 함수

```python
def get_accessible_doc_ids(user_id: str) -> set:
    # 실제 구현에서는 권한 관리 시스템(예: 사내 IAM)에서 조회한다
    # 여기서는 예시를 위해 더미 데이터를 반환한다
    permissions = {
        "user_001": {"doc_public", "doc_team_a"},
        "user_002": {"doc_public"},
    }
    return permissions.get(user_id, set())


def vector_search(query: str, allowed_ids: set, top_k: int = 5) -> list:
    # 실제 구현에서는 벡터 DB에 필터를 걸어 검색한다
    # allowed_ids에 없는 문서는 검색 대상에서 원천 제외된다
    print("검색 필터 적용:", allowed_ids)
    return [{"doc_id": "doc_public", "score": 0.91}]


def retrieve(user_id: str, query: str) -> list:
    # 검색 전에 사용자 권한을 먼저 확인한다
    # 권한 없는 문서는 벡터 검색 쿼리 자체에 들어가지 않는다
    allowed_ids = get_accessible_doc_ids(user_id)
    if not allowed_ids:
        return []
    results = vector_search(query, allowed_ids=allowed_ids)
    return [r for r in results if r["doc_id"] in allowed_ids]
```

여기서 중요한 것은 순서다. 검색을 먼저 하고 나중에 거르는 것이 아니라, 허용된 문서 집합을 먼저 구한 뒤 그 안에서만 검색한다. 이렇게 해야 권한 없는 문서가 모델 컨텍스트 근처에도 가지 않는다. 이중 확인을 위해 검색 후에도 한 번 더 필터링하는 것은 좋은 습관이지만, 1차 방어는 반드시 검색 전이어야 한다.

예제 2. 민감 데이터 분리 아키텍처

```python
SENSITIVE_TIERS = {
    "public": {"embedding_allowed": True, "model_context_allowed": True},
    "internal": {"embedding_allowed": True, "model_context_allowed": True},
    "confidential": {"embedding_allowed": False, "model_context_allowed": False},
}


def index_document(doc_id: str, text: str, tier: str) -> None:
    # 민감 등급이 confidential인 문서는 벡터 인덱스에 넣지 않는다
    # 모델에 가까이 두지 않는 것이 가장 확실한 통제다
    policy = SENSITIVE_TIERS[tier]
    if not policy["embedding_allowed"]:
        print(doc_id, "-> 인덱싱 제외 (민감 등급)")
        return
    print(doc_id, "-> 인덱싱 진행")


def build_prompt(user_id: str, query: str, docs: list) -> str:
    # 컨텍스트에 들어가는 문서도 등급을 다시 확인한다
    safe_docs = [d for d in docs if d["tier"] != "confidential"]
    context = "\n".join(d["text"] for d in safe_docs)
    return "참고 문서:\n" + context + "\n\n질문: " + query
```

기밀 등급 문서는 애초에 벡터 인덱스에 넣지 않는다. 모델이 검색할 수 없는 데이터는 유출할 수도 없다. 편의상 모든 문서를 인덱싱하고 나중에 필터링하는 방식은 유혹적이지만, 인덱스 자체가 유출되면 필터는 무의미해진다.

예제 3. 로그 최소화

```python
import re

API_KEY_PATTERN = re.compile(r"sk-[A-Za-z0-9]+")
EMAIL_PATTERN = re.compile(r"[\w.]+@[\w.]+")
TOKEN_PATTERN = re.compile(r"dummy-bearer-token|bearer [A-Za-z0-9._-]+")


def sanitize_log(message: str) -> str:
    # 로그에 민감정보가 평문으로 남지 않도록 마스킹한다
    message = API_KEY_PATTERN.sub("sk-[MASKED]", message)
    message = EMAIL_PATTERN.sub("[MASKED]@[MASKED]", message)
    message = TOKEN_PATTERN.sub("bearer [MASKED]", message)
    return message


def write_log(event: str, detail: str) -> None:
    safe_detail = sanitize_log(detail)
    print("[LOG]", event, "|", safe_detail)


write_log("api_call", "user=aldqlz@naver.com key=sk-dummy-0000 ok")
```

DeepSeek 사례에서 100만 건의 평문 로그가 노출된 것을 기억하자. 로그는 운영에 필요하지만, 민감정보가 평문으로 쌓이는 로그는 제2의 데이터베이스다. 기록 전에 마스킹하는 습관이 로그 유출 사고의 피해를 결정적으로 줄인다.

## 21.4 검색 인덱스와 원본 권한의 동기화

권한 필터를 검색 앞에 두는 것만으로는 충분하지 않다. 원본 시스템의 권한이 바뀌었는데 검색 인덱스에 반영되지 않으면, 필터는 오래된 권한 정보를 기준으로 동작한다. 퇴사한 직원의 계정으로 검색했을 때 예전에는 볼 수 있었던 문서가 계속 나오는 식이다.

따라서 권한 정보는 문서 내용과 함께 인덱싱하고, 원본 권한이 변경되면 인덱스도 함께 갱신해야 한다. 아래 예제는 문서마다 접근 가능한 사용자 집합을 메타데이터로 저장하는 방식이다.

```python
def index_with_acl(doc_id: str, text: str, tier: str, acl: set) -> dict:
    # 문서 내용과 함께 접근 통제 목록(ACL)을 메타데이터로 저장한다
    # 검색 시 이 ACL을 필터 조건으로 사용한다
    return {
        "doc_id": doc_id,
        "text": text,
        "tier": tier,
        "acl": sorted(acl),
        "indexed_at": "2026-10-13T00:00:00Z",
    }


def on_permission_changed(doc_id: str, new_acl: set, index: dict) -> None:
    # 원본 시스템의 권한 변경 이벤트를 받아 인덱스를 갱신한다
    # 권한 회수는 즉시 반영되어야 한다
    if doc_id in index:
        index[doc_id]["acl"] = sorted(new_acl)
        print(doc_id, "-> ACL 갱신:", sorted(new_acl))


index = {}
index["doc_plan"] = index_with_acl("doc_plan", "신제품 기획안", "internal",
                                   {"user_001", "user_002"})
on_permission_changed("doc_plan", {"user_001"}, index)


def retrieve_with_acl(user_id: str, query: str, index: dict) -> list:
    # 검색 조건에 사용자 ID를 포함해 ACL 필터링을 DB 단계에서 수행한다
    return [doc for doc in index.values()
            if user_id in doc["acl"] and query in doc["text"]]


print(retrieve_with_acl("user_002", "기획안", index))
print(retrieve_with_acl("user_001", "기획안", index))
```

user_002는 권한 회수 후 검색 결과에서 제외된다. 실무에서는 원본 시스템의 권한 변경 이벤트를 구독해 인덱스를 갱신하는 파이프라인을 별도로 둔다. 권한 변경에서 인덱스 반영까지의 시차가 곧 노출 위험 구간이므로, 이 시차를 모니터링 지표로 관리하는 것이 좋다.

## 21.5 실습: 권한 필터를 검색 파이프라인 앞에 두기

이번 실습은 방어 실습이다. 권한 확인이 빠진 RAG 검색 함수를 받아, 권한 필터를 검색 앞에 배치하는 코드로 고쳐 본다. 로컬 환경에서 안전하게 따라 할 수 있다.

1단계. 아래와 같이 권한 확인이 없는 검색 함수가 있다고 가정한다.

```python
def unsafe_retrieve(user_id: str, query: str) -> list:
    # 문제점: 사용자 권한을 확인하지 않고 전체 문서에서 검색한다
    all_docs = [
        {"doc_id": "doc_public", "tier": "public", "text": "회사 소개 자료"},
        {"doc_id": "doc_salary", "tier": "confidential", "text": "임원 연봉 테이블"},
    ]
    return [d for d in all_docs if query in d["text"]]
```

2단계. 21.3절의 예제 1을 참고해 safe_retrieve 함수를 작성한다. 요구사항은 다음과 같다.

- 검색 전에 get_accessible_doc_ids로 허용 문서 집합을 구한다.
- tier가 confidential인 문서는 어떤 경우에도 결과에 포함하지 않는다.
- 허용 집합이 비어 있으면 빈 리스트를 반환한다.

```python
def get_accessible_doc_ids(user_id: str) -> set:
    permissions = {
        "user_001": {"doc_public"},
    }
    return permissions.get(user_id, set())


def safe_retrieve(user_id: str, query: str) -> list:
    # TODO: 위 요구사항을 만족하도록 이 함수를 완성해 보자
    allowed = get_accessible_doc_ids(user_id)
    all_docs = [
        {"doc_id": "doc_public", "tier": "public", "text": "회사 소개 자료"},
        {"doc_id": "doc_salary", "tier": "confidential", "text": "임원 연봉 테이블"},
    ]
    results = []
    for doc in all_docs:
        if doc["doc_id"] not in allowed:
            continue
        if doc["tier"] == "confidential":
            continue
        if query in doc["text"]:
            results.append(doc)
    return results
```

3단계. user_001과 권한 없는 사용자(user_999)로 각각 "연봉"을 검색해 보고, 기밀 문서가 결과에서 제외되는지 확인한다.

4단계. 한 걸음 더 나아가 보자. 실제 벡터 DB(예: 로컬에 띄운 Chroma나 FAISS)를 쓴다면, 검색 쿼리의 where 필터에 allowed 집합을 넣는 방식으로 바꿔 본다. 애플리케이션 단의 필터링이 아니라 데이터베이스 단에서 제외하는 것이 더 안전한 이유를 스스로 설명해 보자.

이 실습의 핵심은 순서다. 권한 확인은 검색보다 먼저다. 이 순서를 코드 구조로 강제하는 것이 LLM02 방어의 출발점이다.

## 21.6 정리

LLM02 민감정보 노출의 전형적인 경로는 RAG에서의 권한 우회다. 권한 없는 데이터가 모델 컨텍스트에 들어오면 모델은 그것을 재료로 답을 만든다. DeepSeek 사례는 모델이 아닌 주변 인프라의 부실한 접근 통제가 얼마나 큰 유출로 이어질 수 있는지 보여줬다. 인증 없이 접속 가능한 ClickHouse 데이터베이스에 100만 건이 넘는 평문 로그가 쌓여 있었고, 임의 SQL 실행과 특권 상승까지 가능했다.

방어의 핵심은 두 문장으로 요약된다. 민감 데이터를 처음부터 모델에 가까이 두지 말고, 검색 전에 사용자 권한을 확인하라. 권한 필터를 검색 앞에 배치하고, 기밀 등급 문서는 인덱싱 자체에서 제외하고, 로그에는 민감정보를 마스킹하라. 모델을 똑똑하게 만드는 것보다 모델 주변을 단단하게 만드는 것이 먼저다.

이 책에서 다루는 공격 기법은 모두 학습·방어 목적이며, 허가되지 않은 시스템에 대한 공격 시도는 절대 하지 말 것.
