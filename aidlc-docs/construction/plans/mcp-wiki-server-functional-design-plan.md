# Functional Design Plan — mcp-wiki-server

## Design Plan (Checkboxes)

- [x] Step 1: 도메인 모델 정의 (Document, SearchResult, Snippet)
- [x] Step 2: 검색 엔진 추상화 설계 (키워드 → 시맨틱 교체 가능 구조)
- [x] Step 3: 검색 알고리즘 상세 설계 (키워드 매칭, snippet 추출)
- [x] Step 4: MCP 도구 인터페이스 정의 (search, read — 입력/출력 스키마)
- [x] Step 5: 비즈니스 규칙 정의 (path traversal 차단, 오류 처리, 검색 결과 제한)
- [x] Step 6: 테스트 가능 속성 식별 (PBT-01, advisory)
- [x] Step 7: 설계 산출물 문서 생성 (business-logic-model.md, business-rules.md, domain-entities.md)

## Design Questions

설계 결정에 필요한 질문입니다. 각 `[Answer]:` 태그 뒤에 보기 문자를 입력해 주세요.

## Question 1
검색어가 여러 단어일 때(예: "진료 기록") 어떻게 처리할까요?

A) AND 조건 — 모든 단어가 포함된 문서만 매칭 (정확도 높음)
B) OR 조건 — 하나라도 포함되면 매칭 (재현율 높음)
C) 구문(phrase) 검색 — 입력 문자열 전체가 그대로 포함된 문서만 매칭
D) AND 우선, 결과 없으면 OR로 완화 (fallback)
E) Other (please describe after [Answer]: tag below)

[Answer]: A) AND 조건 — 모든 단어가 포함된 문서만 매칭 (정확도 높음)


## Question 2
snippet(발췌) 형식은 어떻게 할까요?

A) 매칭 위치 주변 고정 길이 (예: 앞뒤 ~100자)
B) 매칭된 라인 + 앞뒤 1~2줄
C) 매칭 위치가 속한 마크다운 섹션(헤딩 단위) 전체
D) Other (please describe after [Answer]: tag below)

[Answer]: C) 매칭 위치가 속한 마크다운 섹션(헤딩 단위) 전체

## Question 3
한 문서에 매칭이 여러 곳일 때와 결과 정렬은?

A) 문서당 첫 매칭 1개 snippet, 결과는 매칭 횟수 많은 순 정렬
B) 문서당 최대 N개(예: 3개) snippet, 매칭 횟수 순 정렬
C) 문서당 첫 매칭 1개 snippet, 파일 경로 알파벳 순
D) Other (please describe after [Answer]: tag below)

[Answer]: 문서당 최대 N개(예: 3개) snippet, 매칭 횟수 순 정렬

## Question 4
MCP 도구의 반환 형식은 어떻게 할까요? (LLM이 읽을 응답)

A) 구조화된 JSON (파일 경로, snippet, 매칭 수 등 필드로 반환)
B) 사람이 읽기 좋은 마크다운 텍스트로 포맷팅하여 반환
C) Other (please describe after [Answer]: tag below)

[Answer]: A) 구조화된 JSON (파일 경로, snippet, 매칭 수 등 필드로 반환)


## Question 5
검색 엔진 확장(시맨틱) 대비 추상화 수준은?

A) Python Protocol/ABC 기반 SearchEngine 인터페이스 정의 — 구현체 교체 방식 (권장)
B) 단순 함수 분리 수준 — 나중에 필요할 때 리팩토링
C) Other (please describe after [Answer]: tag below)

[Answer]: A) Python Protocol/ABC 기반 SearchEngine 인터페이스 정의 — 구현체 교체 방식 (권장)


## Question 6
검색 결과가 0건일 때의 동작은?

A) 빈 결과 + "매칭 없음" 메시지 반환
B) 빈 결과 + 전체 문서 목록(경로/제목)을 함께 반환하여 LLM이 탐색 가능하게 함
C) Other (please describe after [Answer]: tag below)

[Answer]: A) 빈 결과 + "매칭 없음" 메시지 반환

