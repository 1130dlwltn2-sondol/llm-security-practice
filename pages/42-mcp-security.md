# 42. MCP 서버 보안 실전

MCP(Model Context Protocol)는 LLM 애플리케이션이 외부 도구와 대화하는 표준 규약이다.
구조는 세 부분이다.
호스트는 LLM 애플리케이션 본체(예: 챗봇 데스크톱 앱),
클라이언트는 호스트 안에서 MCP 서버와 연결을 유지하는 부분,
서버는 실제 도구를 제공하는 외부 프로세스다.
중요한 점은 도구의 정의와 실행이 "외부 서버"에 있다는 것이다.
에이전트가 호출하는 함수의 정체를 우리가 직접 통제하지 못할 수 있다.
예를 들어 "프로젝트 목록을 가져와"라는 도구가
실제로는 프로젝트 목록과 함께 사용자 토큰을 어딘가로 전송하고 있을 수도 있다.
호스트는 도구가 "무엇을 하는지"가 아니라
서버가 "무엇을 한다고 주장하는지"만 안다.
이 간극이 MCP 보안의 출발점이다.
이 특성 때문에 MCP는 LLM04 공급망과 LLM03 과도한 에이전시의 교차점이 된다.

## 사례: Asana MCP 테넌트 격리 결함

2025년 6월 4일, Asana의 실험적 MCP 서버에서 버그가 발견되었다.
MCP 연동 로직의 결함으로 테넌트 격리가 깨진 것이다.
그 결과 일부 사용자는 자신의 권한 범위 안에서
다른 조직의 프로젝트·태스크·팀·댓글·파일을 조회할 수 있게 되었다.
외부의 침입이 아니라 내부 설계와 구현의 버그였다.

Asana의 대응은 빨랐다.
6월 5일부터 17일까지 약 2주간 MCP 서버를 오프라인으로 전환하고,
연동 로직을 패치한 뒤 모든 MCP 연결을 리셋했다.
고객은 연결을 다시 설정해야 했다.
약 1,000개의 고객이 영향을 받았을 가능성이 제기되었다.
이 사례는 OWASP MCP 보안 테스트 가이드의 사례 연구로 정리되어 있다.

이 사건이 주는 교훈은 두 가지다.
첫째, 테넌트 격리는 "설정"이 아니라 "코드"다.
격리가 깨지면 멀티테넌트 서비스의 모든 고객이 동시에 위험해진다.
둘째, MCP 서버는 실험적이라는 이유로 보안 검토를 건너뛰기 쉽다.
그러나 한 번 연결되면 에이전트는 그 서버의 도구를 자기 손발처럼 쓴다.

## 방어 1: OAuth 스코프 최소화

MCP 서버에 연결할 때 요청하는 권한은 필요한 만큼만으로 줄인다.
Asana 사례처럼 프로젝트 읽기 도구가 문제를 일으켰다면,
처음부터 "읽기" 범위를 특정 조직으로 한정했어야 했다.
OAuth 스코프는 넓게 받아 놓고 나중에 조이는 방식이 아니라,
좁게 시작해서 필요할 때만 넓히는 방식이어야 한다.

스코프를 정할 때는 도구 목록을 먼저 펼친다.
"이 서버가 제공하는 도구가 12개인데, 우리 에이전트가 쓰는 것은 3개뿐"이라면
나머지 9개에 대한 권한은 요청하지 않는다.
쓰지 않는 도구의 권한까지 받아 두면,
그 도구가 악용되었을 때 피해 범위가 넓어진다.
스코프 목록은 41장의 AI-BOM 인벤토리에 기록해 두고,
정기적으로 "지금도 이 권한이 필요한가"를 검토한다.

## 방어 2: 테넌트 격리 검증 — 조직 ID를 모든 요청에 강제

테넌트 격리를 지키는 가장 확실한 방법은
조직 ID를 모든 도구 호출에 강제로 포함시키는 것이다.
클라이언트가 "어느 조직의 요청인지"를 매번 선언하게 하고,
서버는 선언된 조직 ID와 세션의 조직 ID가 일치하는지 검증한다.
검증 로직은 각 도구에 흩어 놓지 않고
도구 호출을 감싸는 래퍼(wrapper) 한 곳에 둔다.
그래야 새 도구가 추가되어도 격리가 자동으로 적용된다.

## 방어 3: MCP 서버 출처 검증

외부 MCP 서버를 연결하기 전에는 출처를 확인한다.
공식 배포처에서 받았는지, 서명이나 해시가 일치하는지,
유지보수 주체가 누구인지 확인한다.
개인 블로그에서 내려받은 MCP 서버를
회사 내부 문서에 접근하는 에이전트에 연결하는 일은 없어야 한다.
출처가 불분명한 서버는 샌드박스 환경에서 먼저 동작을 관찰하고,
호출하는 도구와 전송하는 데이터를 기록해 본 뒤 도입을 결정한다.

도입 전 확인 목록은 다음과 같다.
배포처가 공식 저장소인지,
최근 업데이트 시점과 유지보수 주체가 명확한지,
요청하는 권한이 도구의 기능과 비례하는지,
네트워크로 전송하는 데이터의 목적지가 문서화되어 있는지다.
네 가지 중 하나라도 답을 구할 수 없으면 도입을 보류한다.
Invariant Labs가 시연한 GitHub MCP 경유 프라이빗 리포지토리 유출 데모는
바로 이 확인을 건너뛰었을 때 무슨 일이 생기는지 보여 준다.

## MCP 서버를 직접 운영할 때

지금까지는 외부 MCP 서버를 "쓰는" 입장이었다.
반대로 우리 팀이 MCP 서버를 "제공하는" 입장이라면
서버 쪽에서도 격리를 구현해야 한다.
원칙은 같다.
모든 도구 핸들러가 요청의 조직 ID를 검증하고,
검증 실패 시 호출을 거부한다.
검증 로직을 각 핸들러에 흩어 놓지 말고
미들웨어나 데코레이터 한 곳에 둔다.
그래야 새 도구를 추가해도 격리가 자동으로 적용된다.
Asana 사건이 "MCP 연동 로직의 결함"이었다는 점을 기억하자.
서버 쪽 로직 한 줄의 실수가 전체 테넌트를 위험에 빠뜨린다.

## 실습: 테넌트 ID 검증 래퍼 작성

아래 코드는 MCP 도구 호출 전에 테넌트 ID를 검증하는 래퍼의 뼈대다.
자신의 프로젝트 구조에 맞게 채워 넣어 보자.

```python
# 테넌트 ID 검증 래퍼
# 모든 MCP 도구 호출은 이 함수를 거쳐야 한다

class TenantViolationError(Exception):
    pass

def call_mcp_tool(tool_name, arguments, session_org_id):
    # 1. 요청에 조직 ID가 있는지 확인한다
    org_id = arguments.get("organization_id")
    if org_id is None:
        raise TenantViolationError(
            "요청에 organization_id가 없습니다. "
            "테넌트를 식별할 수 없는 호출은 차단합니다."
        )

    # 2. 세션의 조직 ID와 일치하는지 확인한다
    if org_id != session_org_id:
        raise TenantViolationError(
            "요청 조직 ID가 세션 조직 ID와 다릅니다. "
            "타 조직 데이터 접근 시도로 간주하고 차단합니다."
        )

    # 3. 검증을 통과한 호출만 실제 도구로 전달한다
    return invoke_tool(tool_name, arguments)


def invoke_tool(tool_name, arguments):
    # 실제 MCP 도구 호출 로직이 들어가는 자리
    # 여기서는 더미 반환
    return {"status": "ok", "tool": tool_name}


# 사용 예시: 정상 호출
result = call_mcp_tool(
    tool_name="list_projects",
    arguments={"organization_id": "org-a12"},
    session_org_id="org-a12",
)
print(result)

# 사용 예시: 타 조직 ID로 호출하면 차단된다
try:
    call_mcp_tool(
        tool_name="list_projects",
        arguments={"organization_id": "org-b34"},
        session_org_id="org-a12",
    )
except TenantViolationError as e:
    print("차단됨:", e)
```

이 래퍼의 핵심은 두 가지다.
첫째, 검증이 "모든 도구 호출의 유일한 통로"에 있다.
도구를 직접 호출하는 코드가 여기저기 흩어지면 격리는 구멍이 생긴다.
둘째, 실패 시 기본값은 차단이다.
조직 ID가 없거나 일치하지 않으면 조용히 넘어가지 않고 예외를 던진다.

실습 과제는 이 래퍼를 확장하는 것이다.
세션의 조직 ID가 허용 목록에 있는지도 확인하고,
차단된 시도를 로그 파일에 기록하는 기능을 추가해 보자.
아래는 로깅을 추가한 확장 예시다.

```python
# 확장: 차단 시도를 로그에 기록하는 버전

import datetime

BLOCK_LOG = "mcp_block.log"

def log_block(tool_name, arguments, session_org_id, reason):
    timestamp = datetime.datetime.now().isoformat()
    with open(BLOCK_LOG, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} | tool={tool_name} | "
                f"requested_org={arguments.get('organization_id')} | "
                f"session_org={session_org_id} | reason={reason}\n")


def call_mcp_tool_with_log(tool_name, arguments, session_org_id):
    org_id = arguments.get("organization_id")
    if org_id is None:
        log_block(tool_name, arguments, session_org_id, "organization_id 누락")
        raise TenantViolationError("요청에 organization_id가 없습니다.")
    if org_id != session_org_id:
        log_block(tool_name, arguments, session_org_id, "조직 ID 불일치")
        raise TenantViolationError("요청 조직 ID가 세션 조직 ID와 다릅니다.")
    return invoke_tool(tool_name, arguments)
```

Asana 사례의 대응(연결 리셋 후 재연결 요구)을 떠올리며,
"격리 위반이 감지되면 해당 세션의 모든 MCP 연결을 끊는다"는 정책도
코드로 표현해 보면 좋다.
로그는 나중에 레드팀 보고서의 증거 자료가 된다.

## 정리

MCP의 구조는 호스트·클라이언트·서버이며, 도구는 외부 서버가 제공한다.
Asana MCP 사례(2025년 6월 4일 발견, 약 2주간 오프라인, 약 1,000개 고객 영향 가능)는
테넌트 격리 결함이 얼마나 큰 파급력을 가지는지 보여 준다.
방어는 세 가지다.
OAuth 스코프 최소화, 조직 ID를 모든 요청에 강제하는 검증 래퍼,
MCP 서버 출처 검증이다.
다음 Part에서는 지금까지의 방어를 한데 모아 실전 프로젝트로 완성한다.
