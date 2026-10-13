# 22. LLM03 과도한 에이전시

에이전트는 도구다. 도구가 일을 대신해 주는 것은 편리하지만, 도구에 쥐여 준 권한만큼 사고의 크기도 커진다. LLM03 과도한 에이전시는 에이전트에게 필요 이상의 능력, 권한, 재량을 줬을 때 발생하는 문제를 다룬다.

이 항목은 2026년판에서 6위에서 3위로 급등했다. 에이전트 시대의 사고들이 순위를 끌어올린 결과다. 모델이 단순히 답을 생성하던 시절에는 에이전시의 위험이 제한적이었다. 하지만 이제 모델은 코드를 실행하고, 파일을 쓰고, API를 호출하고, 풀 리퀘스트를 만든다. 행동하는 모델에게는 행동하지 않는 모델과 전혀 다른 안전 기준이 필요하다.

과도한 에이전시의 근원 원인은 세 가지로 정리된다. 과도한 기능, 과도한 권한, 과도한 자율성. 기능은 에이전트가 할 수 있는 일의 종류, 권한은 그 일을 수행할 때 접근할 수 있는 자원의 범위, 자율성은 사람의 개입 없이 스스로 판단하고 실행하는 정도를 말한다. 세 가지 중 하나라도 과하면 사고가 나고, 두세 가지가 겹치면 대형 사고가 난다.

![과도한 에이전시 3근원](assets/excessive-agency.png)

## 22.1 세 가지 근원 원인

과도한 기능은 에이전트에게 필요 없는 도구를 쥐여 주는 것이다. 문서 요약만 하면 되는 에이전트에게 파일 삭제 도구가 있을 이유가 없다. 코드 리뷰만 하면 되는 에이전트에게 배포 도구가 있을 이유가 없다. 도구가 많을수록 편리해 보이지만, 공격자나 오작동의 입장에서는 선택지가 많아질 뿐이다. 도구는 목적에 딱 맞게, 최소한으로 준다.

과도한 권한은 도구의 실행 범위가 넓은 것이다. 같은 읽기 도구라도 공개 리포지토리만 읽을 수 있는지, 비공개 리포지토리까지 읽을 수 있는지에 따라 위험도가 완전히 다르다. 같은 쓰기 도구라도 임시 디렉터리에만 쓸 수 있는지, 프로덕션 데이터베이스에 쓸 수 있는지에 따라 사고의 크기가 달라진다. 권한은 토큰의 스코프, 클라우드 IAM 역할, 파일 시스템 권한 같은 형태로 나타난다.

과도한 자율성은 사람의 확인 없이 에이전트가 스스로 결정하고 실행하는 범위가 넓은 것이다. "이슈를 확인하고 적절한 조치를 취하라"는 지시는 자율성이 과도하다. 무엇이 적절한 조치인지를 에이전트가 판단하기 때문이다. 반면 "이슈를 확인하고 조치 계획을 제안하라"는 지시는 실행 전에 사람이 개입할 여지를 남긴다. 자율성은 편리함과 위험의 교환 비율이 가장 나쁜 축이다.

## 22.2 실제 사례: Invariant Labs의 GitHub MCP 데모 공격

2025년 5월 26일, 보안 연구 기업 Invariant Labs가 공개한 데모는 과도한 에이전시의 교과서적인 사례다. 대상은 Claude 4 Opus와 공식 GitHub MCP 서버를 기반으로 동작하는 코딩 에이전트였다.

연구원은 공개 리포지토리에 악성 지시문이 담긴 이슈를 하나 만들었다. 평범해 보이는 이슈였지만, 그 안에는 에이전트를 조종하는 지시문이 숨어 있었다. 피해자의 에이전트가 그 공개 이슈를 확인하던 중 지시문을 읽고 그대로 따랐다.

문제는 에이전트가 들고 있던 GitHub 토큰이었다. 그 토큰의 범위가 과도하게 넓어서 퍼블릭 리포지토리는 물론 프라이빗 리포지토리까지 볼 수 있었다. 에이전트는 지시문에 따라 프라이빗 리포지토리의 내용을 끌어내 공개 PR에 유출했다. 비공개 코드가 공개 풀 리퀘스트에 그대로 올라간 것이다.

주목할 점은 공격 기법의 단순함이다. 탈옥도 없었고 특수문자 트릭도 없었다. 평범한 영어로 쓴 지시문 한 단락이 전부였다. 모델의 방어막을 뚫은 것이 아니라, 에이전트 시스템이 애초에 그런 지시를 따를 수 있는 구조였던 것이다.

Invariant Labs의 결론은 명확했다. "GitHub MCP 서버 코드 자체의 결함이 아니라 에이전트 시스템 수준의 근본적 아키텍처 문제." 즉, 개별 도구의 버그가 아니라 에이전트에게 과도한 권한을 주고 과도한 자율성을 허용한 설계가 문제라는 지적이다. 세 가지 근원 원인 중 과도한 권한(프라이빗 리포지토리까지 볼 수 있는 토큰)과 과도한 자율성(이슈의 지시를 그대로 실행)이 겹친 사고였다.

## 22.3 방어: 도구 스코프 제한과 사람 승인

과도한 에이전시의 방어는 세 가지 축에 대응하는 세 가지 조치로 정리된다.

첫째, 도구의 범위를 제한한다. 에이전트에게 주는 도구 목록을 업무에 필요한 최소한으로 줄인다. 읽기 전용 작업에는 쓰기 도구를 주지 않는다. 공개 정보만 다루는 작업에는 비공개 자원에 접근하는 토큰을 주지 않는다.

둘째, 민감한 액션에는 사람의 승인을 요구한다. 에이전트가 계획을 세우는 것과 실행하는 것을 분리한다. 삭제, 배포, 외부 전송, 권한 변경 같은 되돌리기 어려운 작업은 반드시 사람이 확인한 뒤에 실행한다. 이를 휴먼인더루프(human-in-the-loop)라고 한다.

셋째, 토큰과 자격 증명의 권한을 최소화한다. 에이전트가 사용하는 API 토큰, 클라우드 역할, 데이터베이스 계정은 해당 작업에 필요한 최소 스코프로 발급한다. Invariant Labs 사례에서 토큰이 프라이빗 리포지토리를 볼 수 없었더라면, 지시문이 발동해도 유출할 데이터가 없었을 것이다.

아래 코드는 이 세 가지 조치를 하나의 실행 게이트로 구현한 예제다.

```python
SENSITIVE_ACTIONS = {"delete_repo", "push_public", "share_private", "deploy"}


class AgentGate:
    def __init__(self, allowed_tools: set, approver=None):
        # allowed_tools: 이 에이전트에게 허용된 도구 목록 (기능 제한)
        # approver: 민감 액션 승인 콜백 (자율성 제한)
        self.allowed_tools = allowed_tools
        self.approver = approver
        self.audit_log = []

    def request(self, tool_name: str, action: str, args: dict) -> dict:
        if tool_name not in self.allowed_tools:
            self.audit_log.append({"tool": tool_name, "result": "denied_scope"})
            return {"ok": False, "error": "허용되지 않은 도구입니다."}
        if action in SENSITIVE_ACTIONS:
            if self.approver is None:
                self.audit_log.append({"tool": tool_name, "result": "denied_no_approver"})
                return {"ok": False, "error": "민감 액션은 승인자 없이 실행할 수 없습니다."}
            if not self.approver(tool_name, action, args):
                self.audit_log.append({"tool": tool_name, "result": "denied_by_human"})
                return {"ok": False, "error": "사용자가 실행을 거부했습니다."}
        self.audit_log.append({"tool": tool_name, "result": "allowed"})
        return {"ok": True, "message": "실행 허용"}

    def show_audit_log(self) -> list:
        return self.audit_log


def human_approver(tool_name: str, action: str, args: dict) -> bool:
    # 실제 구현에서는 UI나 챗봇으로 사용자에게 확인을 요청한다
    print("승인 요청:", tool_name, action, args)
    return False


# 공개 리포지토리 읽기 전용 에이전트
gate = AgentGate(allowed_tools={"read_issue", "read_public_repo"}, approver=human_approver)

print(gate.request("read_issue", "read", {"issue_id": 42}))
print(gate.request("read_private_repo", "read", {"repo": "secret-project"}))
```

두 번째 요청은 허용된 도구 목록에 없으므로 스코프 단계에서 차단된다. 설령 에이전트가 민감 액션을 시도해도 승인자가 거부하면 실행되지 않는다. 모든 판단은 감사 로그에 남는다.

토큰 권한 최소화는 코드 바깥의 설정 문제지만, 코드로 강제할 수도 있다. 예를 들어 에이전트 시작 시 토큰의 스코프를 검사하는 방법이 있다.

```python
def check_token_scope(token: str, required_scopes: set) -> bool:
    # 실제 구현에서는 GitHub API나 IAM API로 토큰의 실제 권한을 조회한다
    # 여기서는 예시를 위해 더미 검사를 수행한다
    granted_scopes = {"repo:public_read"}
    missing = required_scopes - granted_scopes
    extra = granted_scopes - required_scopes
    if extra:
        print("경고: 필요 이상의 권한이 부여되어 있습니다:", extra)
        return False
    return not missing


DUMMY_TOKEN = "dummy-bearer-token"
if not check_token_scope(DUMMY_TOKEN, {"repo:public_read"}):
    raise SystemExit("토큰 권한이 작업 범위를 벗어났습니다. 에이전트를 시작하지 않습니다.")
```

에이전트를 시작하기 전에 토큰이 과도한 권한을 가지고 있는지 검사하고, 벗어나면 시작 자체를 막는다. 권한 최소화는 문서로만 남기는 것이 아니라 실행 시점에 검증해야 실효성이 있다.

예제 3. 액션 등급별 승인 정책

```python
ACTION_TIERS = {
    "read": {"approval": False, "log": True},
    "write_draft": {"approval": False, "log": True},
    "write_public": {"approval": True, "log": True},
    "destructive": {"approval": True, "log": True, "cooldown_seconds": 300},
}


class TieredApprover:
    # 액션의 위험 등급에 따라 승인 요구 수준을 다르게 적용한다
    # 읽기처럼 되돌릴 수 있는 작업은 자동 허용하고,
    # 공개 쓰기나 파괴적 작업은 반드시 사람의 승인을 받는다
    def __init__(self, ask_human):
        self.ask_human = ask_human
        self.log = []

    def execute(self, action: str, tier: str, args: dict) -> dict:
        policy = ACTION_TIERS.get(tier)
        if policy is None:
            return {"ok": False, "error": "알 수 없는 액션 등급입니다."}
        entry = {"action": action, "tier": tier, "approved": False}
        if policy["approval"]:
            if not self.ask_human(action, tier, args):
                entry["result"] = "rejected"
                self.log.append(entry)
                return {"ok": False, "error": "승인이 거부되었습니다."}
            entry["approved"] = True
        entry["result"] = "executed"
        self.log.append(entry)
        return {"ok": True, "message": action + " 실행됨"}


def ask_human(action: str, tier: str, args: dict) -> bool:
    # 실제 구현에서는 슬랙, 이메일, 관리자 UI로 승인 요청을 보낸다
    print("승인 요청 [" + tier + "]:", action, args)
    return False


approver = TieredApprover(ask_human)
print(approver.execute("read_issue", "read", {"issue_id": 42}))
print(approver.execute("push_public", "write_public", {"repo": "docs"}))
print(approver.execute("delete_repo", "destructive", {"repo": "prod"}))
```

읽기 작업은 자동으로 통과하고, 공개 쓰기와 파괴적 작업은 승인 요청이 간다. 파괴적 작업에는 쿨다운을 두어 승인 후에도 일정 시간이 지나야 실행되게 할 수 있다. 등급을 나누는 기준은 되돌릴 수 있는지 여부다. 되돌릴 수 없는 작업일수록 사람의 개입을 두텁게 한다.

## 22.4 에이전트 도입 전 점검표

에이전트를 프로덕션에 올리기 전에 세 가지 근원 원인에 대해 아래 질문을 던져 보자. 하나라도 아니오가 나오면 설계를 다시 봐야 한다.

기능 점검: 이 에이전트의 목적을 한 문장으로 말할 수 있는가. 도구 목록의 각 항목이 그 목적에 직접 필요한가. 읽기 전용 작업에 쓰기 도구가 섞여 있지 않은가. 디버깅용으로 넣었던 셸 실행 도구가 그대로 남아 있지 않은가.

권한 점검: 에이전트가 쓰는 토큰과 역할의 권한 범위를 나열할 수 있는가. 그 범위가 작업에 필요한 최소 범위인가. 토큰이 만료 기한 없이 발급되어 있지 않은가. 비공개 자원에 접근하는 토큰을 공개 정보만 다루는 에이전트가 들고 있지 않은가.

자율성 점검: 에이전트가 스스로 실행할 수 있는 작업과 사람의 승인이 필요한 작업을 구분했는가. 삭제, 배포, 외부 전송, 권한 변경 같은 되돌리기 어려운 작업이 승인 없이 실행될 수 있는가. 에이전트의 모든 행동이 감사 로그에 남는가. 오작동 시 에이전트를 즉시 정지시킬 수 있는 비상 정지 장치가 있는가.

이 점검표는 한 번 만들고 끝이 아니다. 에이전트에 도구가 추가되거나 권한이 바뀔 때마다 다시 돌린다. 에이전트 시스템은 살아 움직이는 소프트웨어라서, 처음에는 안전했던 설계도 기능이 쌓이면서 과도해지기 쉽다.

## 22.5 실습: 에이전트 도구 목록을 최소 권한으로 재설계하기

이번 실습은 방어 실습이다. 과도하게 설계된 에이전트의 도구 목록을 받아, 최소 권한 원칙에 따라 다시 설계해 본다.

1단계. 아래와 같은 코딩 에이전트 설정이 있다고 가정한다.

```python
agent_config = {
    "name": "issue-helper",
    "purpose": "공개 리포지토리의 이슈를 읽고 요약 보고서를 만든다",
    "tools": ["read_issue", "read_public_repo", "read_private_repo",
              "create_pr", "merge_pr", "delete_branch", "run_shell"],
    "token_scopes": ["repo", "admin", "delete_repo"],
    "auto_execute": True,
}
```

2단계. 목적 문장과 도구 목록을 비교하며 과도한 부분을 찾아낸다. 목적은 공개 이슈 읽기 요약인데, 비공개 리포지토리 읽기, PR 생성과 병합, 브랜치 삭제, 셸 실행 도구가 포함되어 있다. 토큰은 저장소 전체 관리 권한이다. 자동 실행도 켜져 있다.

3단계. 아래 기준에 따라 설정을 다시 작성해 본다.

- 목적 달성에 꼭 필요한 도구만 남긴다.
- 되돌리기 어려운 액션(병합, 삭제)은 목록에서 제거하거나 승인 절차를 붙인다.
- 토큰 스코프는 필요한 최소 범위로 줄인다.
- auto_execute는 끄고, 실행 전 확인 단계를 넣는다.

```python
safe_config = {
    "name": "issue-helper",
    "purpose": "공개 리포지토리의 이슈를 읽고 요약 보고서를 만든다",
    "tools": ["read_issue", "read_public_repo"],
    "token_scopes": ["repo:public_read"],
    "auto_execute": False,
    "approval_required": ["create_pr"],
}
```

4단계. 22.3절의 AgentGate 클래스를 가져와 safe_config의 도구 목록으로 게이트를 만들고, 원래 agent_config의 위험한 도구 호출(read_private_repo, merge_pr 등)이 차단되는지 직접 실행해 본다. 차단 로그가 audit_log에 남는 것도 확인한다.

이 실습의 핵심은 에이전트 설계의 첫 질문을 바꾸는 것이다. "이 에이전트가 무엇을 할 수 있으면 좋을까"가 아니라 "이 에이전트가 무엇을 못하게 막아야 할까"를 먼저 묻는 습관이 과도한 에이전시를 예방한다.

## 22.6 정리

LLM03 과도한 에이전시는 2026년판에서 6위에서 3위로 급등했다. 에이전트가 실제 행동을 하는 시대가 되면서, 권한 설계의 실패가 곧바로 데이터 유출과 시스템 파괴로 이어지기 때문이다. 근원 원인은 세 가지다. 과도한 기능, 과도한 권한, 과도한 자율성.

Invariant Labs의 데모는 이 세 가지 중 권한과 자율성의 실패가 어떻게 결합하는지 보여줬다. 과도하게 넓은 GitHub 토큰을 든 에이전트가 공개 이슈 속 지시문을 그대로 따라 프라이빗 리포지토리의 내용을 공개 PR에 유출했다. 탈옥도 특수문자도 필요 없었다. 구조가 허용했기 때문에 일어난 일이다.

방어는 대응되는 세 가지 조치다. 도구의 범위를 업무에 맞게 줄이고, 민감한 액션에는 사람의 승인을 요구하고, 토큰의 권한을 최소로 발급한 뒤 실행 시점에 검증한다. 에이전트를 설계할 때는 할 수 있는 일을 먼저 나열하지 말고, 막아야 할 일을 먼저 나열하자.

이 책에서 다루는 공격 기법은 모두 학습·방어 목적이며, 허가되지 않은 시스템에 대한 공격 시도는 절대 하지 말 것.
