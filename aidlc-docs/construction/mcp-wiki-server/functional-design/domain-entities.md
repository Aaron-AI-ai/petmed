# Domain Entities — mcp-wiki-server

기술 중립적 도메인 모델. (구현 시 Python dataclass/TypedDict로 매핑)

## Entity: Document
문서 저장소의 마크다운 파일 1개.

| 속성 | 타입 | 설명 |
|---|---|---|
| path | string | 문서 루트 기준 상대 경로 (예: `guides/setup.md`) |
| title | string | 첫 번째 H1 헤딩 텍스트. 없으면 파일명(확장자 제외) |
| content | string | 파일 전체 내용 (UTF-8) |

## Entity: Section
문서를 헤딩 단위로 분할한 조각. snippet 추출의 단위.

| 속성 | 타입 | 설명 |
|---|---|---|
| heading | string | 섹션 헤딩 라인 텍스트. 첫 헤딩 이전 내용(전문)은 빈 문자열 |
| text | string | 헤딩 라인 포함 섹션 전체 텍스트 (다음 헤딩 직전까지) |

**분할 규칙**: 모든 레벨의 헤딩(`#`~`######`) 라인이 새 섹션을 시작한다. 헤딩 계층(중첩)은 고려하지 않는다(flat 분할). 첫 헤딩 이전 내용이 있으면 전문(preamble) 섹션으로 취급한다.

**불변식**: 모든 Section.text를 순서대로 이어 붙이면 원본 content와 동일하다 (무손실 분할).

## Entity: SearchQuery

| 속성 | 타입 | 설명 |
|---|---|---|
| raw | string | 사용자 입력 원문 |
| keywords | list[string] | 공백 기준 분리 + 소문자 변환된 토큰 목록 (빈 토큰 제거) |

## Entity: Snippet

| 속성 | 타입 | 설명 |
|---|---|---|
| section | string | snippet이 속한 섹션의 헤딩 (전문이면 빈 문자열) |
| text | string | 섹션 전체 텍스트 (Q2=C 결정) |

## Entity: SearchResult
문서 1개에 대한 검색 결과.

| 속성 | 타입 | 설명 |
|---|---|---|
| path | string | Document.path |
| title | string | Document.title |
| match_count | int | 파일명 + 본문에서 모든 키워드의 총 출현 횟수 (≥1) |
| snippets | list[Snippet] | 최대 3개 (Q3=B 결정) |

## Interface: SearchEngine (Protocol)
시맨틱 검색 확장을 위한 교체 지점 (Q5=A 결정).

```
SearchEngine (Protocol)
  search(query: str, limit: int) -> list[SearchResult]
```

- 1차 구현체: `KeywordSearchEngine` (키워드 AND 매칭)
- 향후 구현체: `SemanticSearchEngine` (임베딩 기반) — MCP 도구 계층 변경 없이 교체

## Entity Relationships

```
DocumentStore (root dir) --1:N--> Document --1:N--> Section
SearchEngine.search(query) --> SearchResult (N개) --1:N--> Snippet
SearchResult --references--> Document.path
```
