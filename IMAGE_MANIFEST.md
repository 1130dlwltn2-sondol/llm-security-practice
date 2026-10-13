# 이미지 목록 (IMAGE MANIFEST)

'LLM 보안 실전' 책에 필요한 이미지 목록. 이미지 파일 자체는 별도 생성 단계에서 제작하며,
본문 md에서는 이미 `![설명](assets/파일명.png)` 형태로 참조해 두었다.
파일명에 한글·특수문자 사용 금지, PNG 형식.

## 표지

- assets/cover.png — 1000x1300 — 책 표지. 짙은 남색 배경에 자물쇠와 LLM 회로 모티프, 제목 'LLM 보안 실전', 저자 '순돌', 부제 표기 — 참조: pages/00-first-page.md

## 본문 도식 (9종, 권장 1200x800 내외)

- assets/llm-threat-surface.png — 1200x800 — LLM 앱의 공격 표면 다이어그램. 사용자 입력·RAG 문서·도구 결과·외부 API·벡터 DB에서 모델을 향한 화살표 5개 — 참조: pages/10-why-llm-security.md
- assets/owasp-2026-changes.png — 1200x800 — OWASP LLM Top 10 2026 vs 2025 순위 변화 도표. 10개 항목의 순위 변동(상승·하락·개명)을 화살표로 표시 — 참조: pages/11-owasp-2026-overview.md
- assets/threat-model.png — 1200x800 — LLM 앱 위협 모델링 개념도. 신뢰 경계선, 자산(모델·데이터·도구), 공격 표면 지점을 한 그림에 — 참조: pages/12-threat-modeling.md
- assets/indirect-injection.png — 1200x800 — EchoLeak 간접 인젝션 공격 흐름도. 공격자 이메일 → Copilot 검색 → 컨텍스트 오염 → 메일박스·OneDrive·SharePoint 수집 → Teams 이미지 프록시 경유 유출의 5단계 — 참조: pages/20-prompt-injection.md
- assets/rag-access-control.png — 1200x800 — 권한 확인 후 검색하는 RAG 아키텍처. 사용자 권한 필터가 벡터 검색보다 앞에 위치하고, 권한 없는 청크는 모델 컨텍스트에 들어가지 않는 구조 — 참조: pages/21-sensitive-info.md
- assets/excessive-agency.png — 1200x800 — 과도한 에이전시의 3근원(과도한 기능·과도한 권한·과도한 자율성) 삼각 도식 — 참조: pages/22-excessive-agency.md
- assets/supply-chain-integrity.png — 1200x800 — 모델·패키지·MCP 서버 무결성 검증 파이프라인. 다운로드 → 해시 검증 → 서명 확인 → 격리 실행의 단계 — 참조: pages/23-supply-chain.md
- assets/guardrail-pipeline.png — 1200x800 — 탐지 → 판단 → 조치 가드레일 파이프라인. 입력/출력 단계의 3단계 게이트와 로깅·알림 분기 — 참조: pages/31-guardrails.md
- assets/secure-doc-assistant.png — 1200x800 — 실전 프로젝트: 안전한 사내 문서 도우미 에이전트 전체 방어 아키텍처. 권한 필터·입출력 검증·가드레일·사람 승인이 결합된 구조 — 참조: pages/70-project.md

## 검수 기록 (2026-10-13)

- Part·Chapter 번호 순서: 00, 01, 02, 10~12, 20~29, 30~33, 40~42, 70, 80, 81 — 26개 파일 전부 존재, TOC.md 링크와 1:1 일치 확인.
- 목차 순서와 파일 일치: TOC.md의 링크 26개가 pages/ 디렉터리 파일 26개와 정확히 일치 (diff 확인).
- 누락·중복: 없음.
- `**` 사용: 26개 파일 + README + TOC 전수 검사 결과 0건. 작성 중 발견된 위반 4건(21장 마스킹 패턴 3건, 30장 kwargs 2건, 29장 언패킹 1건 — 각 담당 에이전트가 자체 수정 완료).
- 이모지: 전수 검사 결과 0건.
- 과장 표현('완벽 가이드'·'완전 정복'·'궁극의 가이드'): 0건.
- 주의 문구("이 책에서 다루는 공격 기법은 모두 학습·방어 목적이며, 허가되지 않은 시스템에 대한 공격 시도는 절대 하지 말 것."): 00 + Part 2 전 장(20~29) + 70에 명시 확인, 다른 장에는 없음.
- 연락처(이메일 1130dlwltn2@gmail.com, 오픈채팅 https://open.kakao.com/o/s4OEqBai): 00·01·81에 포함 확인.
- 비밀값: 전부 더미(sk-dummy-0000 등), 실제 API 키 형태 0건.
- 사실 범위: 리서치 파일(llm-security-research.md) 범위 내 사실만 사용, 출처를 본문에 자연스럽게 언급. 브리프에 사례가 없는 장(25·26·28·29)은 사례를 지어내지 않고 원리·방어 중심으로 작성.
- 오탈자: 담당 에이전트별 자체 점검 완료(한자 혼입 2건 수정, 영문 오타 1건 수정). 대표 샘플(20장) 직접 확인 — 문체·사실 표기 정상.
