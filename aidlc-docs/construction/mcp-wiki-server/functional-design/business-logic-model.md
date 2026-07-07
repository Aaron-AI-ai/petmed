# Business Logic Model — mcp-wiki-server

## 개요
지정된 루트 디렉토리의 마크다운 문서를 키워드로 검색(search)하고 전체를 조회(read)하는 읽기 전용 위키 로직. 문서 규모가 작으므로(수십 개) 인덱스 없이 요청 시 스캔한다.

## Component: DocumentStore

**책임**: 문서 루트 디렉토리에서 문서를 열거/로드한다.

### Logic: list_documents()
1. 루트 디렉토리를 재귀 탐색하여 `*.md` 파일을 모두 수집 (심볼릭 링크는 따라가지 않음)
2. 각 파일을 UTF-8로 읽어 Document 생성 (디코딩 오류는 대체 문자로 처리)
3. 상대 경로 오름차순으로 정렬하여 반환

### Logic: load_document(path)
1. 입력 상대 경로를 루트 기준으로 해석(resolve)
2. **경로 안전성 검증** (business-rules.md BR-1) — 실패 시 오류
3. `.md` 파일 여부 검증 (BR-2) — 실패 시 오류
4. 파일 존재 검증 — 없으면 "문서 없음" 오류 (BR-4)
5. Document 반환

## Component: KeywordSearchEngine (implements SearchEngine)

### Logic: search(query, limit)
1. **토큰화**: query를 공백으로 분리, 소문자 변환, 빈 토큰 제거 → keywords
   - keywords가 비면 검증 오류 (BR-3)
2. **매칭 (AND, Q1=A)**: 각 Document에 대해 `파일명 + 본문`(소문자 변환)에 **모든** 키워드가 1회 이상 포함되면 매칭
3. **매칭 수 계산**: 모든 키워드의 총 출현 횟수 (파일명 + 본문 합산, 대소문자 무시)
4. **snippet 추출 (Q2=C, Q3=B)**:
   a. 문서를 Section 단위로 분할 (domain-entities.md 분할 규칙)
   b. 키워드가 1개 이상 포함된 섹션을 후보로 선정
   c. 섹션 내 키워드 출현 횟수 내림차순으로 상위 3개 선택, 동률이면 문서 내 등장 순
   d. 본문에 매칭 섹션이 없는 경우(파일명만 매칭) snippets는 빈 목록
5. **정렬 (Q3=B)**: match_count 내림차순, 동률이면 path 오름차순
6. **제한**: 상위 limit개 반환 (기본값 10 — 응답 크기 제한 목적, 설계 결정 D-1)
7. 결과 0건이면 빈 목록 반환 (Q6=A — 도구 계층에서 "매칭 없음" 메시지 부착)

## Component: MCP Tool Layer (FastMCP)

SearchEngine과 DocumentStore를 MCP 도구로 노출. 반환은 구조화 JSON (Q4=A).

### Tool: search
- **입력**: `query: str` (필수), `limit: int` (선택, 기본 10)
- **출력**:
```json
{
  "query": "pet vaccine",
  "total": 2,
  "results": [
    {
      "path": "care/vaccination.md",
      "title": "예방접종 가이드",
      "match_count": 7,
      "snippets": [
        {"section": "## 접종 일정", "text": "## 접종 일정\n..."}
      ]
    }
  ],
  "message": null
}
```
- 결과 0건: `results: []`, `message: "매칭되는 문서가 없습니다."`
- 빈 query: 오류 반환 (BR-3)

### Tool: read
- **입력**: `path: str` (search 결과의 상대 경로)
- **출력**:
```json
{
  "path": "care/vaccination.md",
  "title": "예방접종 가이드",
  "content": "# 예방접종 가이드\n..."
}
```
- 오류(경로 이탈/미존재/비-md): 구조화된 오류 메시지 반환 (BR-1/2/4)

## Data Flow

```
[LLM Client]
    | MCP call: search(query, limit)
    v
[MCP Tool Layer] -- validate query --> [KeywordSearchEngine]
    | search()                              |
    |                                       v
    |                              [DocumentStore.list_documents()]
    |                                       | (recursive *.md scan)
    v                                       v
[JSON response: results + snippets] <-- match / snippet / sort / limit

[LLM Client]
    | MCP call: read(path)
    v
[MCP Tool Layer] --> [DocumentStore.load_document(path)]
    |                       | (path safety check BR-1)
    v                       v
[JSON response: full content]
```

## Design Decisions
| ID | 결정 | 근거 |
|---|---|---|
| D-1 | search에 limit 파라미터 (기본 10) | 섹션 단위 snippet은 클 수 있어 LLM 컨텍스트 보호. 질문에서 미확정이었던 항목의 보수적 기본값 |
| D-2 | 인덱스 없이 요청 시 스캔 | 수십 개 규모(Q5=A), 재시작 반영 정책(Q4=C)과 일관 |
| D-3 | SearchEngine Protocol 분리 | 시맨틱 검색 교체 지점 (Q5=A) |

## Testable Properties (PBT-01 — advisory in Partial mode)

| # | 속성 | 카테고리 | 적용 규칙 |
|---|---|---|---|
| P1 | 섹션 분할 후 이어 붙이면 원본과 동일: `"".join(s.text for s in split(doc)) == doc` | Round-trip | PBT-02 (enforced) |
| P2 | 모든 검색 결과 문서는 모든 키워드를 포함한다 (AND 보장) | Easy verification / Invariant | PBT-03 (enforced) |
| P3 | 결과는 match_count 비증가 순으로 정렬되어 있다 | Invariant | PBT-03 (enforced) |
| P4 | 문서당 snippets ≤ 3, 각 snippet은 원본 문서의 부분 문자열이며 키워드를 포함한다 | Invariant | PBT-03 (enforced) |
| P5 | 토큰화 결과는 모두 비어있지 않고 소문자이며 공백을 포함하지 않는다 | Invariant | PBT-03 (enforced) |
| P6 | 임의 경로 입력에 대해 load_document는 루트 밖 파일을 절대 열지 않는다 | Invariant | PBT-03 (enforced) |
| P7 | 결과 수 ≤ limit | Invariant | PBT-03 (enforced) |
| — | MCP Tool Layer (FastMCP 바인딩) | No PBT properties identified — 얇은 I/O 계층, 예제 기반 통합 테스트로 커버 | PBT-10 (advisory) |
