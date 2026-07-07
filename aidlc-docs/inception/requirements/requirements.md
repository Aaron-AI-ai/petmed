# Requirements — LLM Wiki MCP Service

## Intent Analysis Summary

- **User Request**: LLM 위키 컨셉 기반 MCP 서비스. 서버 특정 경로에 존재하는 마크다운(.md) 파일을 MCP 요청 시 검색하여 내용을 전달한다.
- **Request Type**: New Project (Greenfield)
- **Scope Estimate**: Single Component (단일 MCP 서버 애플리케이션)
- **Complexity Estimate**: Simple–Moderate (검색 로직 + MCP 서버, 외부 의존성 최소)
- **Requirements Depth**: Standard

## Functional Requirements

### FR-1: MCP 도구 — 문서 검색 (search)
- 키워드를 입력받아 문서 저장소 내 마크다운 파일을 검색한다.
- 검색 대상: 파일명 + 본문 (대소문자 무시)
- 검색 방식: 키워드 매칭 (1차 구현). 추후 시맨틱(임베딩) 검색으로 확장 가능한 구조를 유지한다 — 검색 로직을 MCP 도구 정의와 분리하여 교체 가능하게 설계.
- 반환 형식: 매칭된 문서별로 **파일 경로(상대 경로) + 매칭 부분 주변 발췌(snippet)** 목록.

### FR-2: MCP 도구 — 문서 전체 읽기 (read)
- 검색 결과의 파일 경로를 입력받아 해당 문서의 전체 내용을 반환한다.
- 존재하지 않는 경로 요청 시 명확한 오류 메시지를 반환한다.
- 문서 루트 경로 밖의 파일 접근(path traversal)은 차단한다.

### FR-3: 문서 저장소
- 서버 설정으로 지정된 **단일 루트 디렉토리**를 문서 저장소로 사용한다.
- 하위 디렉토리를 포함하여 **재귀적으로** `.md` 파일을 탐색한다.
- 파일 변경(추가/수정/삭제) 반영은 **서버 재시작**으로 충분하다 (실시간 감지 불필요).

### FR-4: MCP 서버
- FastMCP 기반, **Streamable HTTP** transport로 서비스한다.
- 문서 루트 경로, 호스트/포트는 환경변수 또는 실행 인자로 설정 가능하다.

## Non-Functional Requirements

### NFR-1: 규모 및 성능
- 예상 문서 규모: **수십 개 이하** (소규모).
- 이 규모에서는 별도 검색 인덱스 없이 요청 시 파일 스캔으로 충분한 응답 속도를 보장한다.

### NFR-2: 보안
- **인증/접근 제어 불필요** — 내부망/로컬 환경에서만 사용.
- 단, 문서 루트 밖 파일 접근 차단(path traversal 방지)은 기본 적용한다 (FR-2).
- Security Baseline 확장: **비활성** (사용자 opt-out).

### NFR-3: 확장성
- 검색 엔진 교체 가능 구조: 키워드 검색 → 시맨틱 검색 전환 시 MCP 도구 인터페이스 변경 없이 내부 구현만 교체 가능해야 한다.

### NFR-4: 기술 스택 (사용자 지정)
- Python 3.12
- uv (패키지/프로젝트 관리)
- FastMCP (Streamable HTTP transport)
- 테스트: pytest + **Hypothesis** (PBT Partial 모드 — PBT-09 프레임워크 선정)

### NFR-5: 테스트 (PBT Partial 모드)
- 적용 규칙: PBT-02 (round-trip), PBT-03 (invariant), PBT-07 (generator 품질), PBT-08 (shrinking/재현성), PBT-09 (프레임워크 선정)
- 순수 함수(검색/snippet 추출 등)에 대해 invariant 속성 테스트 적용.
- 예제 기반 테스트와 병행 (PBT는 보완재).

## Out of Scope
- 문서 작성/수정/삭제 기능 (읽기 전용 위키)
- 인증/인가
- 실시간 파일 변경 감지 (watch)
- 시맨틱/임베딩 검색 (구조만 대비, 구현하지 않음)
- 다중 문서 저장소

## Change Log (워크플로우 완료 후 변경)

| 일자 | 변경 | 근거 |
|---|---|---|
| 2026-07-07 | E2E 자동화 테스트 추가 (`tests/test_e2e.py`) | 사용자 요청 — Playwright 논의 후 fastmcp Client 방식 채택 |
| 2026-07-07 | Docker Compose 배포 구성 추가 (Dockerfile, compose.yaml, 호스트 포트 8800) | 사용자 요청 |
| 2026-07-07 | 문서 저장소 `wiki-docs/` 카테고리 구조 신설 + 웹 조사 기반 의학 문서 8건 생성 | 사용자 요청 — sample-docs/는 테스트 픽스처로 유지 |
| 2026-07-07 | FR-1 개정: 기본 검색을 문자 bigram BM25 랭킹으로 변경 (`BM25SearchEngine`, 기본값). 기존 AND 키워드 매칭은 `--engine keyword`로 유지. SearchResult에 score 필드 추가. 추후 임베딩 시맨틱 + BM25 하이브리드 확장 예정 | 사용자 요청 |

## Clarification Decisions (Q&A 기록)
| 항목 | 결정 |
|---|---|
| 검색 방식 | 키워드 우선, 시맨틱 확장 가능 구조 (Q1=D) |
| 도구 구성 | 도구 2개: search + read (Clarification=A, Q2/Q6 모순 해소) |
| 경로 구조 | 단일 루트, 재귀 탐색 (Q3=B) |
| 변경 반영 | 서버 재시작 (Q4=C) |
| 문서 규모 | 수십 개 이하 (Q5=A) |
| 반환 형식 | snippet + 경로, 전체는 read 도구 (Q6=B) |
| 인증 | 불필요 (Q7=A) |
| Security 확장 | 비활성 (Q8=B) |
| PBT 확장 | Partial (Q9=B) |
