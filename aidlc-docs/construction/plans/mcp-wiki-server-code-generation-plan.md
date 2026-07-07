# Code Generation Plan — mcp-wiki-server

**이 문서는 Code Generation 단계의 단일 진실 공급원(single source of truth)입니다.**

## Unit Context

- **Unit**: mcp-wiki-server (단일 유닛, 그린필드)
- **Workspace Root**: /Users/koscom/workspace/petmed
- **구조 패턴**: Greenfield single unit — `src/`, `tests/` in workspace root
- **의존 유닛**: 없음
- **구현 요구사항**: FR-1(search), FR-2(read), FR-3(문서 저장소), FR-4(FastMCP Streamable HTTP) — requirements.md
- **설계 근거**: functional-design/ 산출물 (domain-entities, business-logic-model, business-rules BR-1~11)
- **기술 스택**: Python 3.12, uv, FastMCP, pytest + Hypothesis

## Target Structure (Application Code — workspace root)

```
pyproject.toml                      # uv 프로젝트, 의존성, 스크립트
src/mcp_wiki/__init__.py
src/mcp_wiki/models.py              # Document, Section, Snippet, SearchResult, SearchEngine Protocol
src/mcp_wiki/store.py               # DocumentStore (스캔, 로드, 경로 안전성)
src/mcp_wiki/search.py              # tokenize, split_sections, KeywordSearchEngine
src/mcp_wiki/server.py              # FastMCP 앱, search/read 도구, 설정, 엔트리포인트
tests/test_store.py                 # DocumentStore 예제 기반 테스트 (BR-1/2/4 포함)
tests/test_search.py                # 검색 로직 예제 기반 테스트
tests/test_properties.py            # Hypothesis PBT — 속성 P1~P7
sample-docs/                        # 수동 검증용 샘플 위키 문서 (md 2~3개)
README.md                           # 실행/설정 방법 (기존 파일 수정)
```

## Generation Steps

- [x] **Step 1: 프로젝트 구조 셋업** — pyproject.toml (Python 3.12, fastmcp 의존성, dev group: pytest/hypothesis), `src/mcp_wiki/__init__.py`, uv 프로젝트 초기화
- [x] **Step 2: 도메인 모델 생성** — `src/mcp_wiki/models.py`: dataclass 4종 + SearchEngine Protocol (domain-entities.md 매핑)
- [x] **Step 3: DocumentStore 생성** — `src/mcp_wiki/store.py`: 재귀 `*.md` 스캔, UTF-8(errors=replace), 개별 파일 오류 스킵, load_document 경로 안전성 검증 [BR-1, BR-2, BR-4, BR-10, BR-11]
- [x] **Step 4: 검색 엔진 생성** — `src/mcp_wiki/search.py`: tokenize(공백 분리/소문자), split_sections(무손실 헤딩 분할), KeywordSearchEngine(AND 매칭, 매칭 수 집계, 섹션 snippet 최대 3개, match_count 정렬, limit) [BR-3, BR-5~BR-9]
- [x] **Step 5: MCP 서버 계층 생성** — `src/mcp_wiki/server.py`: FastMCP 인스턴스, `search`/`read` 도구(구조화 JSON 반환), 설정(WIKI_DOCS_ROOT/HOST/PORT 환경변수 + CLI 인자), Streamable HTTP 실행 엔트리포인트, 루트 부재 시 시작 실패 [FR-4, BR-11]
- [x] **Step 6: 예제 기반 단위 테스트 생성** — `tests/test_store.py`(path traversal 차단, 미존재 문서, 비-md 거부), `tests/test_search.py`(AND 매칭, snippet 추출, 정렬, 빈 검색어, 0건 처리) [PBT-10 보완 관계]
- [x] **Step 7: 속성 기반 테스트 생성** — `tests/test_properties.py`: Hypothesis로 P1(섹션 분할 round-trip), P2(AND 보장), P3(정렬 불변식), P4(snippet 상한/부분문자열), P5(토큰화 불변식), P6(경로 안전성), P7(limit 준수). 도메인 제너레이터(마크다운 문서 생성기) 중앙화 [PBT-02, PBT-03, PBT-07, PBT-08]
- [x] **Step 8: 샘플 문서 및 README** — `sample-docs/` 샘플 md 2~3개, README.md에 설치/실행/설정/테스트 방법 기록
- [x] **Step 9: 코드 생성 요약 문서** — `aidlc-docs/construction/mcp-wiki-server/code/code-generation-summary.md` (생성 파일 목록, 설계 매핑, PBT 준수 요약)

## Requirement Traceability

| Step | 구현 대상 |
|---|---|
| Step 3 | FR-3 (문서 저장소), FR-2 일부 (read 로직) |
| Step 4 | FR-1 (검색), NFR-3 (엔진 교체 구조) |
| Step 5 | FR-4 (Streamable HTTP), FR-1/FR-2 도구 노출 |
| Step 6~7 | NFR-5 (PBT Partial 준수), 품질 게이트 |

## PBT Compliance Plan (Partial mode — enforced rules)

| Rule | 계획 |
|---|---|
| PBT-02 | P1 섹션 분할 무손실 round-trip 테스트 (Step 7) |
| PBT-03 | P2~P7 불변식 테스트 (Step 7) |
| PBT-07 | 마크다운 문서/검색어 도메인 제너레이터 작성, 테스트 간 재사용 (Step 7) |
| PBT-08 | Hypothesis 기본 shrinking 유지, 실패 시 시드 출력 확인, derandomize 미사용 (Step 7, Build & Test에서 검증) |
| PBT-09 | Hypothesis를 dev 의존성으로 pyproject.toml에 명시 (Step 1) |
