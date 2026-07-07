"""FastMCP 서버 — search/read 도구를 Streamable HTTP로 노출 (FR-4)."""

import argparse
import os
from dataclasses import asdict
from pathlib import Path

from fastmcp import FastMCP

from .models import SearchEngine
from .search import DEFAULT_LIMIT, BM25SearchEngine, KeywordSearchEngine
from .store import DocumentStore, DocumentStoreError

mcp = FastMCP("mcp-wiki-server")

ENGINES = {"bm25": BM25SearchEngine, "keyword": KeywordSearchEngine}

_store: DocumentStore | None = None
_engine: SearchEngine | None = None


def configure(docs_root: Path, engine: str = "bm25") -> None:
    """문서 루트와 검색 엔진을 설정한다. 루트가 없으면 즉시 실패 (BR-11)."""
    global _store, _engine
    _store = DocumentStore(docs_root)
    _engine = ENGINES[engine](_store)


@mcp.tool
def search(query: str, limit: int = DEFAULT_LIMIT) -> dict:
    """위키 문서를 키워드로 검색합니다.

    공백으로 구분된 모든 키워드가 포함된(AND, 대소문자 무시) 마크다운 문서를 찾아
    경로/제목/매칭 수와 섹션 단위 발췌(snippet, 문서당 최대 3개)를 반환합니다.
    전체 내용이 필요하면 결과의 path로 read 도구를 호출하세요.
    """
    try:
        results = _engine.search(query, limit)
    except ValueError as e:
        return {"error": str(e)}
    return {
        "query": query,
        "total": len(results),
        "results": [asdict(r) for r in results],
        "message": None if results else "매칭되는 문서가 없습니다.",  # BR-9
    }


@mcp.tool
def read(path: str) -> dict:
    """마크다운 문서 전체 내용을 반환합니다.

    path는 search 결과가 돌려준 문서 루트 기준 상대 경로입니다.
    """
    try:
        return asdict(_store.load_document(path))
    except DocumentStoreError as e:
        return {"error": str(e)}


def main() -> None:
    parser = argparse.ArgumentParser(description="LLM Wiki MCP server (Streamable HTTP)")
    parser.add_argument(
        "--docs-root",
        default=os.environ.get("WIKI_DOCS_ROOT"),
        help="마크다운 문서 루트 디렉토리 (env: WIKI_DOCS_ROOT)",
    )
    parser.add_argument("--host", default=os.environ.get("WIKI_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("WIKI_PORT", "8000")))
    parser.add_argument(
        "--engine",
        choices=sorted(ENGINES),
        default=os.environ.get("WIKI_SEARCH_ENGINE", "bm25"),
        help="검색 엔진 (env: WIKI_SEARCH_ENGINE, 기본 bm25)",
    )
    args = parser.parse_args()

    if not args.docs_root:
        parser.error("--docs-root 인자 또는 WIKI_DOCS_ROOT 환경변수가 필요합니다")

    configure(Path(args.docs_root), engine=args.engine)
    mcp.run(transport="http", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
