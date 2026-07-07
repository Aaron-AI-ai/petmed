# Code Generation Summary — mcp-wiki-server

## 생성 파일 (워크스페이스 루트)

| 파일 | 역할 | 설계 매핑 |
|---|---|---|
| `pyproject.toml` | uv 프로젝트, fastmcp 의존성, dev: pytest/hypothesis, `mcp-wiki-server` 스크립트 | NFR-4, PBT-09 |
| `src/mcp_wiki/models.py` | Document/Section/Snippet/SearchResult dataclass, SearchEngine Protocol | domain-entities.md |
| `src/mcp_wiki/store.py` | DocumentStore — 재귀 `*.md` 스캔, 경로 안전성, 오류 내성 | FR-3, BR-1/2/4/10/11 |
| `src/mcp_wiki/search.py` | tokenize / split_sections(무손실) / KeywordSearchEngine (AND, snippet≤3, 정렬, limit) | FR-1, BR-3/5~9, NFR-3 |
| `src/mcp_wiki/server.py` | FastMCP 앱, search/read 도구(구조화 JSON), 설정(CLI+env), Streamable HTTP | FR-2/4 |
| `tests/test_store.py` | 예제 기반 — traversal/절대경로/비-md/미존재/루트 부재 | BR-1/2/4/11 |
| `tests/test_search.py` | 예제 기반 — AND/대소문자/정렬/snippet/빈검색어/0건/limit | BR-3/5~9, PBT-10 |
| `tests/test_properties.py` | Hypothesis PBT — P1~P7, 도메인 제너레이터 중앙화 | PBT-02/03/07/08 |
| `sample-docs/` | 샘플 위키 문서 3개 (수동 검증용) | — |
| `README.md` (수정) | 설치/실행/설정/테스트 안내 | — |

## 구현 노트

- "파일명 매칭"은 상대 경로 전체(디렉토리명 포함) 매칭으로 구현 — 파일명을 포함하는 상위 집합이며 폴더명 검색도 가능. (`search.document_haystack`)
- `KeywordSearchEngine`은 store의 `list_documents()`만 사용 → 테스트에서 FakeStore로 대체 가능, 시맨틱 엔진 교체 지점은 `SearchEngine` Protocol.
- 서버 시작 시 문서 루트가 없으면 즉시 실패(BR-11). 개별 파일 읽기 오류는 건너뜀.
- FastMCP `transport="http"` = Streamable HTTP, 기본 엔드포인트 `/mcp`.

## PBT Compliance (Partial mode)

| Rule | Status | 근거 |
|---|---|---|
| PBT-02 | Compliant | P1 섹션 분할 round-trip (`test_p1_split_sections_roundtrip`, 생성 입력) |
| PBT-03 | Compliant | P2~P7 불변식 테스트 (AND 보장, 정렬, snippet 상한/부분문자열, 토큰화, 경로 안전성, limit) |
| PBT-07 | Compliant | 마크다운 문서/경로/검색어 도메인 제너레이터를 test_properties.py 상단에 중앙화 |
| PBT-08 | Compliant | Hypothesis 기본 shrinking/시드 리포팅 유지 (비활성화 설정 없음) — 실행 검증은 Build & Test |
| PBT-09 | Compliant | Hypothesis dev 의존성으로 pyproject.toml 명시 |
| PBT-10 (advisory) | Followed | 예제 기반 테스트 파일과 PBT 파일 분리, 핵심 시나리오는 예제 기반으로 고정 |

테스트 실행은 Build & Test 단계에서 수행한다.
