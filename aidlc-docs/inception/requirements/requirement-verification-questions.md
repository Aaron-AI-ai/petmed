# 요구사항 확인 질문 (Requirement Verification Questions)

아래 질문에 대해 각 `[Answer]:` 태그 뒤에 선택한 보기 문자를 입력해 주세요.
보기 중 맞는 것이 없으면 마지막 보기(Other)를 선택하고 설명을 적어주세요.

## Question 1
MD 파일 검색 방식은 어떤 수준이 필요한가요?

A) 단순 키워드 매칭 (파일명 + 본문에 대한 대소문자 무시 부분 문자열 검색)
B) 전문(full-text) 검색 — 토큰화 기반 랭킹 포함 (예: 관련도 순 정렬)
C) 시맨틱 검색 — 임베딩 기반 유사도 검색 (벡터 인덱스 필요)
D) 키워드 검색 먼저 구현하고, 추후 시맨틱 검색 확장 가능한 구조
E) Other (please describe after [Answer]: tag below)

[Answer]: D) 키워드 검색 먼저 구현하고, 추후 시맨틱 검색 확장 가능한 구조


## Question 2
MCP 서버가 제공해야 할 기능(도구) 범위는 무엇인가요?

A) 검색만 — 키워드로 검색하여 관련 문서 내용 반환
B) 검색 + 문서 목록 조회 + 특정 문서 전체 읽기
C) B + 문서 작성/수정 (위키처럼 쓰기 기능 포함)
D) Other (please describe after [Answer]: tag below)

[Answer]: A) 검색만 — 키워드로 검색하여 관련 문서 내용 반환


## Question 3
MD 파일이 위치하는 경로 구조는 어떻게 되나요?

A) 단일 디렉토리 (하위 디렉토리 없음, flat 구조)
B) 하위 디렉토리 포함 재귀 탐색 필요
C) 여러 개의 루트 경로를 설정으로 지정 (복수 문서 저장소)
D) Other (please describe after [Answer]: tag below)

[Answer]: B) 하위 디렉토리 포함 재귀 탐색 필요


## Question 4
MD 파일의 변경(추가/수정/삭제) 반영은 어떻게 처리하나요?

A) 요청 시마다 파일 시스템을 직접 읽음 (인덱스 없음, 항상 최신 반영)
B) 서버 시작 시 인덱스 구축 + 요청 시 파일 변경 감지하여 갱신
C) 파일 변경은 드물어서 서버 재시작으로 반영해도 무방
D) Other (please describe after [Answer]: tag below)

[Answer]: C) 파일 변경은 드물어서 서버 재시작으로 반영해도 무방


## Question 5
예상되는 문서 규모는 어느 정도인가요?

A) 소규모 — 수십 개 이하
B) 중규모 — 수백 개
C) 대규모 — 수천 개 이상
D) Other (please describe after [Answer]: tag below)

[Answer]: A) 소규모 — 수십 개 이하


## Question 6
검색 결과 반환 형식은 어떤 것이 적절한가요?

A) 매칭된 문서의 전체 내용 반환
B) 매칭된 부분 주변 발췌(snippet) + 파일 경로 반환, 필요 시 전체 읽기 도구로 조회
C) 파일 경로/제목 목록만 반환
D) Other (please describe after [Answer]: tag below)

[Answer]: B) 매칭된 부분 주변 발췌(snippet) + 파일 경로 반환, 필요 시 전체 읽기 도구로 조회


## Question 7
인증/접근 제어가 필요한가요? (Streamable HTTP는 네트워크로 노출됩니다)

A) 불필요 — 내부망/로컬에서만 사용
B) 간단한 토큰(Bearer/API Key) 인증 필요
C) Other (please describe after [Answer]: tag below)

[Answer]: A) 불필요 — 내부망/로컬에서만 사용


## Question 8: Security Extensions
이 프로젝트에 보안 확장 규칙(Security Baseline)을 적용할까요?

A) Yes — 모든 SECURITY 규칙을 필수 제약으로 적용 (프로덕션급 애플리케이션에 권장)
B) No — SECURITY 규칙 생략 (PoC, 프로토타입, 실험용 프로젝트에 적합)
X) Other (please describe after [Answer]: tag below)

[Answer]: B) No — SECURITY 규칙 생략 (PoC, 프로토타입, 실험용 프로젝트에 적합)


## Question 9: Property-Based Testing Extension
이 프로젝트에 속성 기반 테스트(PBT) 규칙을 적용할까요?

A) Yes — 모든 PBT 규칙을 필수 제약으로 적용 (비즈니스 로직, 데이터 변환, 직렬화, 상태 유지 컴포넌트가 있는 프로젝트에 권장)
B) Partial — 순수 함수와 직렬화 왕복(round-trip)에만 PBT 적용 (알고리즘 복잡도가 낮은 프로젝트에 적합)
C) No — PBT 규칙 생략 (단순 CRUD, UI 전용, 얇은 통합 계층 프로젝트에 적합)
X) Other (please describe after [Answer]: tag below)

[Answer]: B) Partial — 순수 함수와 직렬화 왕복(round-trip)에만 PBT 적용 (알고리즘 복잡도가 낮은 프로젝트에 적합)

