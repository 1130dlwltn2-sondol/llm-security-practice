# 29. LLM10 부적절한 출력 처리

모델이 코드를 짜줬는데, 그 코드를 그대로 실행해도 될까. LLM10 'Improper Output Handling(부적절한 출력 처리)'은 이 질문에 대한 답이 "안 된다"인 경우들을 다룬다. 하위 시스템이 검증 없이 LLM 출력을 신뢰할 때 생기는 위협이다. 대표적인 예가 안전하지 않은 생성 코드의 실행이다.

OWASP LLM Top 10 2026년판에서 LLM10은 5위에서 10위로 다섯 계단 하락했다. 순위는 내려갔지만 여전히 Top 10 안에 있다. 하락의 배경에는 이 문제를 다룬 가이드와 도구가 늘어난 영향도 있겠지만, "모델 출력은 신뢰할 수 없는 입력"이라는 원칙을 모르는 개발자가 여전히 많다는 점에서 방심할 항목은 아니다. 이 장에서는 LLM 출력을 코드 실행, SQL, 셸에 넘길 때의 위험과, 출력 검증·샌드박스·권한 분리라는 세 가지 방어를 코드와 함께 다룬다. 특정 사고 사례는 다루지 않고 원리와 방어에 집중한다.

## 29.1 LLM 출력은 '신뢰할 수 없는 입력'이다

전통적인 보안 원칙 중에 "모든 입력은 검증하라"는 것이 있다. 사용자가 폼에 입력한 값, URL 파라미터, 파일 업로드는 모두 검증 대상이다. LLM10은 이 원칙을 한 칸 확장한다. 모델의 출력도 검증 대상이라는 것이다.

왜 그럴까. 모델의 출력은 결국 외부에서 들어온 영향(사용자 입력, 검색된 문서, 학습 데이터)이 뒤섞인 결과물이다. 프롬프트 인젝션으로 오염될 수도 있고, 할루시네이션으로 엉뚱한 값이 들어갈 수도 있다. 그런데 많은 개발자가 모델 출력을 '우리 시스템이 만든 깨끗한 데이터'처럼 취급한다. 이 착각이 문제의 시작이다.

위험한 지점은 출력이 '실행되는 곳'으로 흘러들어갈 때다. 코드 실행(exec, eval), SQL 쿼리 조립, 셸 명령어 생성, HTML 렌더링, 파일 쓰기가 대표적이다. 예를 들어 모델이 생성한 SQL을 그대로 DB에 날리거나, 모델이 짠 스크립트를 그대로 실행하는 구조가 그렇다. 출력이 실행되는 순간, 출력에 섞인 악의적 내용은 곧 시스템에 대한 명령이 된다.

## 29.2 어디에서 터지는가: 다섯 가지 위험 지점

첫째, 코드 실행이다. 모델이 생성한 파이썬 코드를 exec나 eval로 바로 실행하는 패턴이다. 데이터 분석 도우미나 코딩 어시스턴트에서 흔히 볼 수 있다. 코드 한 줄에 시스템 전체가 넘어갈 수 있는 가장 위험한 지점이다.

둘째, SQL 조립이다. "매출 상위 10개 상품을 조회해줘" 같은 요청에 모델이 SQL을 만들고, 이를 그대로 실행하는 구조다. 모델이 WHERE 절을 빼먹거나, 악의적 입력의 영향으로 DROP 같은 구문을 섞으면 데이터가 날아간다.

셋째, 셸 명령이다. 모델이 생성한 명령어를 subprocess로 실행하는 패턴이다. 파일 삭제, 권한 변경 같은 파괴적 명령이 섞일 수 있다.

넷째, HTML 렌더링이다. 모델 출력을 이스케이프 없이 웹 페이지에 그대로 보여주면 XSS(크로스 사이트 스크립팅)가 된다. 모델이 script 태그를 출력하는 순간 방문자의 브라우저에서 실행된다.

다섯째, 파일 쓰기다. 모델이 생성한 내용을 설정 파일이나 스크립트 파일로 저장하는 경우다. 나중에 그 파일이 실행되면 공격이 완성된다.

다섯 지점의 공통점은 '출력과 실행 사이의 검증이 없다'는 것이다. 방어는 이 사이에 검증과 격리를 끼워 넣는 일이다.

## 29.3 방어 1: 출력 검증 — 스키마와 허용 목록

첫 번째 방어는 출력을 실행하기 전에 형식을 검증하는 것이다. "이런 모양의 출력만 통과시킨다"는 규칙을 코드로 강제한다.

SQL 생성의 경우를 보자. 읽기 전용 조회만 허용하는 서비스라면, 생성된 SQL이 SELECT로 시작하고 위험한 키워드를 포함하지 않는지 검사한다.

```python
import re
import sqlparse  # pip install sqlparse

FORBIDDEN = ["drop", "delete", "update", "insert", "alter", "grant", "--"]

def validate_select_only(sql: str) -> dict:
    cleaned = sql.strip().rstrip(";")
    lowered = cleaned.lower()
    for kw in FORBIDDEN:
        if re.search(r"\b" + kw + r"\b", lowered):
            return {"ok": False, "reason": "금지된 키워드 포함: " + kw}
    parsed = sqlparse.parse(cleaned)
    if not parsed or parsed[0].get_type() != "SELECT":
        return {"ok": False, "reason": "SELECT 문이 아님"}
    return {"ok": True, "reason": ""}

print(validate_select_only("SELECT name FROM products LIMIT 10"))
# {'ok': True, 'reason': ''}
print(validate_select_only("SELECT * FROM users; DROP TABLE users"))
# {'ok': False, 'reason': '금지된 키워드 포함: drop'}
```

JSON 출력이라면 스키마 검증을 쓴다. pydantic 같은 라이브러리로 필드 타입과 허용 값을 고정하면, 모델이 엉뚱한 구조를 내놔도 실행 단계까지 넘어가지 않는다. 원칙은 같다. "모델이 뭘 내놓든, 우리가 정한 틀에 맞는 것만 통과시킨다."

```python
from pydantic import BaseModel, ValidationError
from typing import Literal

class RefundResult(BaseModel):
    order_id: str
    amount: int
    currency: Literal["KRW"]  # 허용된 값만 받는다

def validate_json_output(raw: str) -> dict:
    import json
    try:
        data = json.loads(raw)
        checked = RefundResult(
            order_id=data["order_id"],
            amount=data["amount"],
            currency=data["currency"],
        )
    except (json.JSONDecodeError, ValidationError, TypeError, KeyError) as e:
        return {"ok": False, "reason": "스키마 검증 실패: " + str(e)[:100]}
    return {"ok": True, "data": checked.model_dump()}

print(validate_json_output('{"order_id": "A-123", "amount": 45000, "currency": "KRW"}'))
print(validate_json_output('{"order_id": "A-123", "amount": "많이", "currency": "KRW"}'))
```

amount에 문자열이 들어오면 검증에서 탈락한다. 모델이 "많이"라고 답해도 실행 단계까지 가지 않는다. 스키마는 모델과 하위 시스템 사이의 계약서다.

## 29.4 방어 2: 샌드박스 실행

검증을 통과한 출력도 100퍼센트 안전하다고 장담할 수는 없다. 그래서 두 번째 방어는 실행 환경을 격리하는 것이다. 설령 악의적 내용이 검증을 뚫어도, 피해가 격리된 공간 안에 머물게 만드는 구조다.

샌드박스의 기본 요소는 세 가지다. 네트워크 차단(외부로 데이터를 빼내지 못하게), 파일 시스템 제한(작업 디렉터리 밖을 건드리지 못하게), 타임아웃과 리소스 제한(무한 루프나 과도한 연산으로 시스템을 마비시키지 못하게)이다.

```python
import subprocess

def run_in_sandbox(code_path: str, timeout_sec: int = 10) -> dict:
    # 최소 예시: 별도 프로세스로 실행하고 시간 제한을 둔다.
    # 실제 운영에서는 컨테이너나 전용 샌드박스 환경을 사용한다.
    try:
        proc = subprocess.run(
            ["python3", code_path],
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            cwd="/tmp/sandbox",  # 작업 디렉터리 고정
        )
        return {"ok": proc.returncode == 0, "stdout": proc.stdout, "stderr": proc.stderr}
    except subprocess.TimeoutExpired:
        return {"ok": False, "stdout": "", "stderr": "시간 초과로 중단됨"}

# 운영 환경에서는 여기에 네트워크 차단, 읽기 전용 파일 시스템,
# 메모리/CPU 제한을 얹는다. 이 예시는 뼈대이며 그대로 운영에 쓰지 않는다.
```

위 코드는 개념을 보여주는 뼈대다. 실제 운영에서는 컨테이너(Docker 등)나 언어별 샌드박스 환경을 쓰고, 네트워크를 끊고, 파일 시스템을 읽기 전용으로 마운트하는 등의 조치를 얹는다. 중요한 것은 "검증된 코드라도 격리된 곳에서만 돌린다"는 원칙을 지키는 것이다.

## 29.5 방어 3: 권한 분리

세 번째 방어는 '누구의 권한으로 실행되는가'의 문제다. 코드가 실행되는 주체의 권한을 낮추면, 설령 악의적 코드가 실행되더라도 할 수 있는 일이 제한된다.

대표적인 예가 DB 계정 분리다. 모델이 생성한 SQL을 실행하는 계정은 읽기 전용(SELECT만 가능) 계정으로 만든다. 애플리케이션의 다른 기능이 쓰는 쓰기 권한 계정과 분리한다. 이렇게 해두면 검증 로직에 구멍이 있어 DELETE가 넘어가더라도, DB 계정 권한에서 막힌다.

```python
# 개념 예시: 용도별 DB 접속 정보 분리
DB_READONLY = {
    "host": "db.internal",
    "user": "report_reader",      # SELECT 권한만 있는 계정
    "password": "sk-dummy-0000",  # 더미 값. 실제로는 시크릿 매니저에서 주입
}

DB_ADMIN = {
    "host": "db.internal",
    "user": "app_writer",         # 쓰기 권한 계정. 모델 생성 SQL에는 절대 사용 금지
    "password": "sk-dummy-0000",
}

def run_generated_sql(sql: str) -> dict:
    check = validate_select_only(sql)  # 29.3절의 검증
    if not check["ok"]:
        return {"ok": False, "error": check["reason"]}
    # 검증 통과 후에도 읽기 전용 계정으로만 실행
    return execute_with(DB_READONLY, sql)
```

셸 실행도 마찬가지다. 모델이 만든 명령을 실행하는 프로세스는 최소 권한 사용자로 돌리고, sudo나 관리자 권한은 절대 주지 않는다. 파일 쓰기가 필요하면 쓰기 가능한 디렉터리를 하나로 한정한다.

세 가지 방어를 겹쳐 보면 방어의 깊이(defense in depth)가 보인다. 출력 검증에서 걸러내고, 뚫린 것은 샌드박스에 가두고, 샌드박스를 뚫어도 권한이 없어서 할 일이 없다. 한 겹이 뚫려도 다음 겹이 막는 구조다.

## 29.6 HTML 렌더링과 파일 쓰기 방어

29.2절에서 언급한 나머지 두 위험 지점, HTML 렌더링과 파일 쓰기의 방어를 마저 다룬다.

HTML 렌더링의 방어는 이스케이프다. 모델 출력을 웹 페이지에 보여줄 때는 HTML 특수 문자를 반드시 이스케이프한다. 파이썬의 html.escape가 표준 도구다.

```python
import html

def render_model_output(raw: str) -> str:
    # 모델 출력은 항상 이스케이프 후 렌더링
    return "<div>" + html.escape(raw) + "</div>"

print(render_model_output("<script>alert('xss')</script>"))
# <div>&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;</div>
```

모델이 마크다운을 출력하고 이를 렌더링해야 한다면, 허용된 태그만 남기는 새니타이저를 쓴다. 직접 정규식으로 태그를 지우는 것은 우회되기 쉬우므로, 검증된 라이브러리를 쓰는 것이 좋다. "보여줄 수 있는 것"을 허용 목록으로 정하는 원칙은 29.3절의 스키마 검증과 같다.

파일 쓰기의 방어는 경로 제한이다. 모델이 지정한 파일명(또는 모델 출력에서 파생된 파일명)을 그대로 쓰지 않는다. 32.3절의 safe_delete와 같은 발상으로, 쓰기 가능한 디렉터리를 하나로 한정하고 경로를 정규화해 검사한다.

```python
import os

ALLOWED_WRITE_DIR = "/tmp/agent-output"

def safe_write(filename: str, content: str) -> dict:
    # 파일명은 경로 구분자를 제거하고 평탄화
    base = os.path.basename(filename)
    if not base or base.startswith("."):
        return {"ok": False, "error": "허용되지 않은 파일명"}
    real = os.path.realpath(os.path.join(ALLOWED_WRITE_DIR, base))
    allowed = os.path.realpath(ALLOWED_WRITE_DIR)
    if not real.startswith(allowed + os.sep):
        return {"ok": False, "error": "허용된 디렉터리 밖의 쓰기 금지"}
    with open(real, "w", encoding="utf-8") as f:
        f.write(content)
    return {"ok": True, "path": real}

print(safe_write("../../etc/cron.d/evil", "malicious"))
# basename 평탄화 + realpath 검사로 차단됨
```

basename으로 평탄화하면 "../../etc/cron.d/evil" 같은 경로 탈출 시도가 단순 파일명으로 축소된다. 그래도 realpath 검사는 이중으로 둔다. 방어의 겹침은 여기서도 유효하다.

## 29.7 실습: 생성된 SQL을 실행 전 검증하는 래퍼

이번 장의 실습은 29.3절의 검증 함수를 확장해 '실행 전 검증 래퍼'를 완성하는 것이다. 로컬에서 안전하게 따라 할 수 있는 방어 실습이다. 실제 DB에 연결하지 않고 검증 로직까지만 만든다.

목표: 모델이 생성한 SQL 문자열을 받아, 실행해도 되는 것인지 판정하는 래퍼 함수를 작성한다.

1. 새 파이썬 파일을 만들고 29.3절의 validate_select_only 함수를 복사한다. sqlparse가 없으면 pip로 설치한다.
2. 다음 규칙을 추가한다.
   - 조회 대상 테이블을 허용 목록으로 제한한다. 예: ["products", "orders"]만 허용하고, users 같은 민감 테이블이 FROM에 나오면 차단한다.
   - LIMIT이 없으면 차단한다. 대량 조회를 막는 규칙이다. (LIMIT 값의 상한도 정해 본다. 예: 1000 이하)
   - 서브쿼리 안에도 금지 키워드가 있는지 검사한다. 본문만 보고 통과시키는 실수를 막는다.
3. 테스트 케이스를 6개 이상 만들어 실행한다. 예: 정상 조회, DROP 포함, 허용되지 않은 테이블, LIMIT 없음, 서브쿼리에 DELETE 숨김, 세미콜론으로 문장 연결.
4. 모든 테스트를 통과하면, 판정 결과를 로그로 남기는 기능을 추가한다. 차단된 SQL의 원문과 사유, 시각을 기록한다.

이 실습을 마치면 '모델이 만든 것은 실행 전에 반드시 코드가 검사한다'는 습관이 생긴다. 30장의 출력 검증, 31장의 가드레일로 이어지는 기본기다.

## 29.8 정리

- LLM10 부적절한 출력 처리는 OWASP LLM Top 10 2026년판에서 5위에서 10위로 하락했지만 여전히 Top 10에 있는 위협이다.
- 핵심 원칙은 하나다. 모델의 출력은 '신뢰할 수 없는 입력'이다. 전통 보안의 입력 검증 원칙이 그대로 적용된다.
- 방어는 세 겹이다. 출력 검증(스키마와 허용 목록), 샌드박스 실행(격리된 환경), 권한 분리(실행 주체의 권한 최소화).
- 한 겹이 뚫려도 다음 겹이 막는 식으로 겹겹이 쌓는 것이 정석이다.

이 책에서 다루는 공격 기법은 모두 학습·방어 목적이며, 허가되지 않은 시스템에 대한 공격 시도는 절대 하지 말 것.
