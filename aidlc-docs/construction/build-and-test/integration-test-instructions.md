# Integration Test Instructions

> **자동화됨 (2026-07-07)**: 아래 시나리오는 `tests/test_e2e.py`로 자동화되어
> `uv run pytest`에 포함된다 (서버 자동 기동/종료, 빈 포트 자동 할당).
> 아래 수동 절차는 참고용으로 유지한다.

## Purpose
MCP 클라이언트 ↔ 서버(Streamable HTTP) 전 구간이 실제로 동작하는지 검증한다.
단일 유닛 프로젝트이므로 유닛 간 통합은 없고, **클라이언트 → HTTP transport → MCP 도구 → 파일 시스템** 경로를 검증한다.

## Setup Integration Test Environment

### 1. Start Required Services
```bash
cd /Users/koscom/workspace/petmed
uv run mcp-wiki-server --docs-root sample-docs --port 8412 &
```

### 2. Configure Service Endpoints
- 엔드포인트: `http://127.0.0.1:8412/mcp` (Streamable HTTP)

## Test Scenarios

### Scenario 1: 도구 노출 확인
- **Test Steps**: fastmcp Client로 `list_tools()` 호출
- **Expected Results**: `['search', 'read']`

### Scenario 2: 검색 → 읽기 흐름 (FR-1 → FR-2)
- **Test Steps**: `search(query="강아지 백신")` 호출 → 결과의 path로 `read(path=...)` 호출
- **Expected Results**: search가 `care/vaccination.md`를 match_count와 섹션 snippet과 함께 반환(AND 매칭), read가 전체 내용 반환

### Scenario 3: 경로 이탈 차단 (BR-1)
- **Test Steps**: `read(path="../pyproject.toml")` 호출
- **Expected Results**: `{"error": "허용되지 않는 경로입니다"}`

### Scenario 4: 결과 없음 (BR-9)
- **Test Steps**: `search(query="존재하지않는말")` 호출
- **Expected Results**: `results: []`, `message: "매칭되는 문서가 없습니다."`

## Run Integration Tests

### 1. Execute Integration Test Suite
```bash
# 스모크 스크립트 (fastmcp Client 사용)
uv run python - <<'EOF'
import asyncio, json
from fastmcp import Client

async def main():
    async with Client("http://127.0.0.1:8412/mcp") as c:
        tools = [t.name for t in await c.list_tools()]
        assert tools == ["search", "read"], tools
        r = await c.call_tool("search", {"query": "강아지 백신"})
        assert r.data["total"] >= 1 and r.data["results"][0]["path"] == "care/vaccination.md"
        r2 = await c.call_tool("read", {"path": "care/vaccination.md"})
        assert "예방접종" in r2.data["title"]
        r3 = await c.call_tool("read", {"path": "../pyproject.toml"})
        assert "error" in r3.data
        r4 = await c.call_tool("search", {"query": "존재하지않는말"})
        assert r4.data["results"] == [] and r4.data["message"]
        print("integration smoke: ALL PASS")

asyncio.run(main())
EOF
```

### 2. Verify Service Interactions
- **Expected Results**: `integration smoke: ALL PASS`
- **Logs Location**: 서버 stdout (백그라운드 실행 시 리다이렉트한 파일)

### 3. Cleanup
```bash
pkill -f mcp-wiki-server
```
