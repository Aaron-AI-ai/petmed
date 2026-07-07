# Unit Test Execution

## Run Unit Tests

### 1. Execute All Unit Tests
```bash
cd /Users/koscom/workspace/petmed
uv run pytest -q
```

### 2. Review Test Results
- **Expected**: 24 tests pass, 0 failures
  - `tests/test_store.py` — 8 (BR-1/2/4/10/11: traversal, 절대경로, 비-md, 미존재, 루트 부재)
  - `tests/test_search.py` — 13 (BR-3/5~9: AND, 대소문자, 정렬, snippet, 빈 검색어, 0건, limit)
  - `tests/test_properties.py` — 3+1 (Hypothesis PBT: P1~P7)
- **Test Report Location**: 콘솔 출력 (별도 리포트 파일 없음)

### 3. PBT 재현성 (PBT-08)
- Hypothesis 기본 shrinking 활성 상태 — 실패 시 최소 실패 입력과 재현 방법이 콘솔에 출력됨
- 실패 재현: 출력된 `@reproduce_failure(...)` 데코레이터를 해당 테스트에 임시로 붙여 재실행
- 상세 출력: `uv run pytest tests/test_properties.py -v --hypothesis-show-statistics`

### 4. Fix Failing Tests
1. 콘솔 출력에서 실패 케이스 확인 (PBT는 shrunk 최소 입력 확인)
2. 코드 수정
3. 전체 재실행 (`uv run pytest -q`) — 모두 통과할 때까지 반복
4. PBT가 발견한 실패는 예제 기반 회귀 테스트로 고정 권장 (PBT-10)
