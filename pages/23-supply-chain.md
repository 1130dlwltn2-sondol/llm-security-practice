# 23. LLM04 공급망 공격

소프트웨어 공급망 공격은 어제오늘의 이야기가 아니다. 개발자가 신뢰하고 받아 쓰는 구성 요소 어딘가에 악성 코드가 심어지면, 그 구성 요소를 쓰는 모든 시스템이 함께 오염된다. LLM04는 이 고전적인 위협이 AI 시대에 어떻게 확장되는지를 다룬다.

공격 대상은 다양하다. 사전 학습된 모델 파일, 파인튜닝용 어댑터, 학습 데이터셋, 패키지 의존성, CI 파이프라인, 배포 플랫폼이 모두 공격 표면이다. 2026년판에서는 MCP(Model Context Protocol) 서버가 명시적으로 포함됐다. 에이전트가 외부 도구를 연결하는 표준 통로가 된 MCP 서버가 오염되면, 그 서버를 쓰는 모든 에이전트가 영향을 받는다.

공급망 공격이 무서운 이유는 신뢰의 전이 때문이다. 개발자는 허깅페이스에서 받은 모델 파일이 깨끗할 것이라 믿고, VS Code 마켓플레이스의 확장 프로그램이 안전할 것이라 믿고, 공식 MCP 서버가 정상일 것이라 믿는다. 공격자는 바로 이 믿음을 노린다. 신뢰받는 배포 경로를 오염시키면, 피해자는 의심 없이 악성 구성 요소를 받아들인다.

## 23.1 공격 경로: 모델, 패키지, 파이프라인, MCP 서버

첫 번째 경로는 손상된 모델 파일이다. 모델 가중치 파일은 수 기가바이트에 달하는 바이너리라 내용물을 눈으로 확인할 방법이 없다. 공격자가 인기 모델의 이름을 사칭한 변조 파일을 모델 허브에 올리면, 개발자는 해시 검증 없이 다운로드해 그대로 서빙한다. 모델 파일 포맷 자체의 역직렬화 취약점을 노리는 공격도 있다. 모델을 로드하는 순간 악성 코드가 실행되는 방식이다.

두 번째 경로는 패키지와 의존성이다. AI 프로젝트는 수많은 파이썬 패키지에 의존한다. 공격자가 인기 패키지와 이름이 비슷한 타이포스쿼팅 패키지를 올리거나, 정상 패키지의 maintainer 계정을 탈취해 악성 버전을 배포하면, pip install 한 줄로 개발 환경이 오염된다.

세 번째 경로는 빌드와 배포 파이프라인이다. CI 설정 파일에 들어 있는 토큰이 탈취당하면 공격자가 파이프라인 권한으로 코드를 수정하고 릴리스할 수 있다. 개발자의 로컬 환경은 깨끗한데 배포된 산출물만 오염되는, 탐지가 가장 어려운 유형이다.

네 번째 경로는 MCP 서버다. 에이전트가 파일 시스템, 데이터베이스, 외부 API에 접근할 때 거치는 MCP 서버가 변조되면, 에이전트의 눈과 손이 공격자의 것으로 바뀐다. 2026년판이 MCP 서버를 명시한 것은 에이전트 생태계에서 이 경로의 중요도가 급격히 커졌기 때문이다.

## 23.2 실제 사례: Amazon Q 공급망 오염 (CVE-2025-8217)

2025년 7월, AI 코딩 어시스턴트 자체가 공급망 공격의 피해자가 된 사건이 발생했다. 대상은 Amazon Q Developer for VS Code 확장이었다. VS Code 마켓플레이스에서 약 100만 건이 설치된 인기 확장 프로그램이다.

사건의 시작은 7월 13일이었다. lkmanka58이라는 계정이 오픈소스 리포지토리에 악성 코드를 커밋했다. 사용된 것은 부적절하게 범위가 지정된 GitHub 토큰으로, 코드빌드 설정에 들어 있던 토큰이었다. 이 커밋은 자동 릴리스 프로세스에 포함되어 7월 17일에 오염된 버전 1.84.0으로 배포됐다. 확장 프로그램을 업데이트한 약 100만 명의 개발자 환경에 악성 코드가 퍼진 것이다.

악성 코드의 내용은 단순한 정보 탈취가 아니었다. Q 에이전트에게 시스템을 공장 초기 상태로 정리하고, 로컬 파일과 AWS 클라우드 자원을 삭제하라는 인젝션 프롬프트가 포함되어 있었다. ec2 terminate-instances, s3 rm 같은 파괴적인 명령이 지시문에 들어 있었다. AI 어시스턴트의 업데이트를 가장해 AI 에이전트를 조종하는 파괴 명령을 심은 것이다.

다행히 최악의 시나리오는 벌어지지 않았다. AWS의 조사에 따르면 악성 코드에 구문 오류가 있어서 실제 실행에는 실패한 것으로 판단됐다. 7월 23일에 신고가 접수되어 조사가 시작됐고, 7월 24일에 깨끗한 버전 1.85.0이 배포됐다.

AWS는 보안 권고 AWS-2025-015를 발표했고, 이 취약점에는 CVE-2025-8217이 부여됐다.

이 사건이 보여주는 교훈은 세 가지다. 첫째, CI 파이프라인에 들어 있는 토큰의 권한 관리가 얼마나 중요한지다. 코드빌드 설정의 토큰 하나로 오픈소스 리포지토리에 커밋할 수 있었다는 것 자체가 권한 범위의 실패다. 둘째, 자동 릴리스는 속도와 함께 위험도 자동화한다는 점이다. 사람의 검토 없이 커밋이 릴리스로 이어지는 구조에서는 악성 커밋 하나가 곧바로 100만 설치 기반에 배포된다. 셋째, AI 도구 자체가 공격 대상이 되면 피해의 성격이 달라진다는 점이다. 개발자의 조종을 받는 줄 알았던 에이전트가 사실은 공격자의 지시를 따르고 있을 수 있다.

## 23.3 방어: 무결성 검증 파이프라인

공급망 공격의 방어는 한 마디로 무결성 검증이다. 받아 쓰는 모든 구성 요소가 내가 기대한 바로 그것인지 확인하는 절차를 파이프라인에 박아 넣는다.

![무결성 검증 파이프라인](assets/supply-chain-integrity.png)

예제 1. 모델 파일 해시 검증

```python
import hashlib


def sha256_of_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_model(path: str, expected_sha256: str) -> bool:
    # 모델을 로드하기 전에 게시자가 공개한 해시와 대조한다
    actual = sha256_of_file(path)
    if actual != expected_sha256:
        print("해시 불일치: 파일이 변조되었을 수 있습니다.")
        print("기대값:", expected_sha256)
        print("실제값:", actual)
        return False
    print("해시 검증 통과")
    return True


MODEL_PATH = "/tmp/models/dummy-model.bin"
PUBLISHED_SHA256 = "dummy-sha256-published-by-vendor"

with open(MODEL_PATH, "wb") as f:
    f.write(b"dummy model bytes")

if verify_model(MODEL_PATH, PUBLISHED_SHA256):
    print("모델 로드를 진행합니다.")
else:
    print("모델 로드를 중단합니다.")
```

원칙은 단순하다. 해시를 확인하기 전에는 모델 파일을 로드하지 않는다. 게시자가 공개한 해시값과 다운로드한 파일의 해시가 다르면 변조를 의심하고 로드를 중단한다. 수 기가바이트 파일도 청크 단위로 읽으면 메모리 부담 없이 검증할 수 있다.

예제 2. 패키지 무결성 확인

```python
import subprocess
import sys


def install_pinned(requirements_path: str) -> None:
    # 버전이 고정된 requirements 파일로만 설치한다
    # 해시 고정 모드(--require-hashes)를 쓰면 변조된 패키지를 설치 단계에서 차단한다
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--require-hashes",
         "-r", requirements_path],
        check=True,
    )


def audit_installed() -> None:
    # 설치된 패키지에 알려진 취약점이 있는지 검사한다
    result = subprocess.run(
        [sys.executable, "-m", "pip", "audit"],
        capture_output=True, text=True,
    )
    print(result.stdout)
```

requirements 파일에 패키지 해시를 함께 기록하는 습관이 중요하다. 버전만 고정하면 패키지 저장소가 변조됐을 때 같은 버전의 다른 파일을 받을 수 있지만, 해시까지 고정하면 내용이 바뀌는 순간 설치가 실패한다.

예제 3. MCP 서버 출처 검증

```python
TRUSTED_MCP_SERVERS = {
    "github": {"publisher": "github", "transport": "local"},
    "filesystem": {"publisher": "anthropics", "transport": "local"},
}


def verify_mcp_server(name: str, publisher: str, transport: str) -> bool:
    # 에이전트에 연결하기 전에 MCP 서버의 출처를 허용 목록과 대조한다
    expected = TRUSTED_MCP_SERVERS.get(name)
    if expected is None:
        print(name, "-> 알 수 없는 MCP 서버입니다. 연결을 거부합니다.")
        return False
    if expected["publisher"] != publisher or expected["transport"] != transport:
        print(name, "-> 게시자 또는 전송 방식이 기대와 다릅니다. 연결을 거부합니다.")
        return False
    print(name, "-> 출처 검증 통과")
    return True


verify_mcp_server("github", "github", "local")
verify_mcp_server("github", "attacker", "remote")
```

MCP 서버도 소프트웨어 공급망의 일부다. 이름만 보고 연결하지 말고, 게시자와 전송 방식을 허용 목록과 대조한다. 특히 원격 전송 방식의 MCP 서버는 서버 측 코드가 언제든 바뀔 수 있으므로, 로컬 실행 서버보다 엄격한 검토가 필요하다.

## 23.4 배포 산출물 서명

해시 검증이 다운로드 받는 쪽의 방어라면, 서명은 배포하는 쪽의 약속이다. 릴리스할 때마다 산출물에 서명을 붙이면, 받는 쪽은 게시자의 개인 키로 서명된 파일인지 확인할 수 있다. 해시 파일 자체가 변조될 수 있다는 점이 서명과의 차이다. 서명은 신뢰의 출발점을 게시자의 키로 옮긴다.

```python
def check_release_notes(version: str, advisory_feed: list) -> bool:
    # 새 버전을 적용하기 전에 보안 권고 목록을 확인하는 습관
    # Amazon Q 사건처럼 오염된 버전이 배포된 뒤에는
    # 빠른 버전 확인과 롤백 판단이 피해를 가른다
    for advisory in advisory_feed:
        if advisory["affected_version"] == version:
            print("경고:", advisory["advisory_id"], "-", advisory["summary"])
            return False
    print(version, "-> 알려진 보안 권고 없음")
    return True


feed = [{"advisory_id": "AWS-2025-015", "affected_version": "1.84.0",
         "summary": "오염된 릴리스, 1.85.0으로 업데이트 필요"}]
check_release_notes("1.84.0", feed)
check_release_notes("1.85.0", feed)
```

자동 업데이트를 쓰는 환경이라면 보안 권고 피드를 구독해 두자. 오염된 버전이 보고됐을 때 업데이트를 멈추거나 롤백하는 판단이 빨라질수록 피해는 작아진다. Amazon Q 사건에서 7월 17일 오염 버전 배포 후 7월 24일 클린 버전 배포까지의 일주일이 바로 이 판단의 시간이었다.

## 23.5 실습: 다운로드한 모델 파일의 해시 검증 스크립트

이번 실습은 방어 실습이다. 모델 파일을 다운로드한 뒤 로드하기 전에 해시를 검증하는 스크립트를 직접 작성하고, 변조된 파일을 탐지하는 과정을 확인한다. 로컬 환경에서 안전하게 따라 할 수 있다.

1단계. 작업 디렉터리에 테스트용 더미 모델 파일을 만든다.

```python
with open("/tmp/practice-model.bin", "wb") as f:
    f.write(b"p" * 1024 * 1024)
print("더미 모델 파일 생성 완료")
```

2단계. 23.3절의 예제 1을 참고해 verify_model 함수를 그대로 가져온 뒤, 생성한 파일의 해시를 구해 PUBLISHED_SHA256 자리에 넣어 본다.

```python
import hashlib


def sha256_of_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


MODEL_PATH = "/tmp/practice-model.bin"
PUBLISHED_SHA256 = sha256_of_file(MODEL_PATH)
print("게시된 해시로 사용할 값:", PUBLISHED_SHA256)
```

3단계. 파일 끝에 1바이트를 추가해 변조를 시뮬레이션하고, verify_model이 불일치를 탐지하는지 확인한다.

```python
with open(MODEL_PATH, "ab") as f:
    f.write(b"x")


def verify_model(path: str, expected_sha256: str) -> bool:
    actual = sha256_of_file(path)
    if actual != expected_sha256:
        print("해시 불일치: 파일이 변조되었을 수 있습니다.")
        return False
    print("해시 검증 통과")
    return True


print(verify_model(MODEL_PATH, PUBLISHED_SHA256))
```

4단계. 한 걸음 더 나아가 보자. 실제 모델 허브에서 모델을 받을 때 게시자가 해시를 어디에 공개하는지(모델 카드, 릴리스 노트, 서명 파일 등) 확인하고, 자신의 프로젝트에 모델 다운로드 후 자동 검증 단계를 넣는 방법을 설계해 본다. CI 파이프라인의 모델 다운로드 단계 바로 뒤에 검증 단계를 붙이는 것이 이상적이다.

이 실습의 핵심은 순서다. 검증은 로드보다 먼저다. 해시 검증 없이 모델 파일을 여는 습관은 출처 불명의 실행 파일을 더블클릭하는 것과 다르지 않다.

## 23.6 정리

LLM04 공급망 공격은 신뢰의 전이를 노린다. 개발자가 믿고 받아 쓰는 모델 파일, 패키지, 파이프라인, MCP 서버 어딘가에 악성 코드가 심어지면 피해는 그 구성 요소를 쓰는 모든 곳으로 번진다. 2026년판에 MCP 서버가 명시적으로 포함된 것은 에이전트 생태계에서 이 경로가 핵심 통로가 됐기 때문이다.

Amazon Q 사건(CVE-2025-8217)은 부적절하게 범위가 지정된 토큰 하나로 시작됐다. 코드빌드 설정의 토큰으로 오픈소스 리포지토리에 악성 커밋이 올라갔고, 자동 릴리스를 타고 약 100만 설치 기반에 오염된 버전 1.84.0이 배포됐다. 악성 코드에는 Q 에이전트에게 클라우드 자원을 삭제하라는 인젝션 프롬프트까지 들어 있었다. 구문 오류 덕분에 실제 실행은 실패했지만, AI 도구 자체가 공격 벡터가 될 수 있음을 보여준 사건이다.

방어는 무결성 검증 파이프라인이다. 모델 파일은 게시자가 공개한 해시와 대조한 뒤에만 로드하고, 패키지는 해시 고정 설치로 변조를 차단하고, MCP 서버는 허용 목록과 대조한 뒤에만 연결한다. 신뢰는 선언이 아니라 검증으로 유지된다.

이 책에서 다루는 공격 기법은 모두 학습·방어 목적이며, 허가되지 않은 시스템에 대한 공격 시도는 절대 하지 말 것.
