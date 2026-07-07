"""E2E 테스트 — 실제 서버(Streamable HTTP)를 띄우고 MCP 클라이언트로 전 구간 검증.

integration-test-instructions.md의 시나리오를 자동화한 것.
"""

import asyncio
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest
from fastmcp import Client

SAMPLE_DOCS = Path(__file__).parent.parent / "sample-docs"


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def server_url():
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, "-m", "mcp_wiki.server",
         "--docs-root", str(SAMPLE_DOCS), "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                pytest.fail("서버 프로세스가 시작 직후 종료됨")
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                    break
            except OSError:
                time.sleep(0.1)
        else:
            pytest.fail("서버가 15초 내에 기동하지 않음")
        yield f"http://127.0.0.1:{port}/mcp"
    finally:
        proc.terminate()
        proc.wait(timeout=5)


def _run(server_url, coro_fn):
    async def wrapper():
        async with Client(server_url) as c:
            return await coro_fn(c)

    return asyncio.run(wrapper())


def test_tools_exposed(server_url):
    async def check(c):
        return sorted(t.name for t in await c.list_tools())

    assert _run(server_url, check) == ["find_facility", "read", "search"]


def test_search_then_read_flow(server_url):
    async def check(c):
        r = await c.call_tool("search", {"query": "강아지 백신"})
        assert r.data["total"] >= 1
        top = r.data["results"][0]
        assert top["path"] == "care/vaccination.md"
        assert top["snippets"] and "백신" in top["snippets"][0]["text"]
        r2 = await c.call_tool("read", {"path": top["path"]})
        assert r2.data["title"] == "예방접종 가이드"
        assert "광견병" in r2.data["content"]

    _run(server_url, check)


def test_path_traversal_rejected(server_url):
    async def check(c):
        r = await c.call_tool("read", {"path": "../pyproject.toml"})
        assert r.data == {"error": "허용되지 않는 경로입니다"}

    _run(server_url, check)


def test_no_match_message(server_url):
    async def check(c):
        # bigram BM25는 부분 매칭 재현율이 높으므로 문서에 없는 문자 조합 사용
        r = await c.call_tool("search", {"query": "zxqwvk"})
        assert r.data["results"] == []
        assert r.data["message"] == "매칭되는 문서가 없습니다."

    _run(server_url, check)


def test_empty_query_error(server_url):
    async def check(c):
        r = await c.call_tool("search", {"query": "   "})
        assert "검색어" in r.data["error"]

    _run(server_url, check)
