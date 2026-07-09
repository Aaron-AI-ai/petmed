"""FastMCP 서버 — search/read 도구를 Streamable HTTP로 노출 (FR-4)."""

import argparse
import os
from dataclasses import asdict
from pathlib import Path

from fastmcp import FastMCP

from .facilities import FacilityStore
from .models import SearchEngine
from .search import DEFAULT_LIMIT, BM25SearchEngine, KeywordSearchEngine
from .store import DocumentStore, DocumentStoreError

mcp = FastMCP("mcp-wiki-server")

ENGINES = {"bm25": BM25SearchEngine, "keyword": KeywordSearchEngine}

_store: DocumentStore | None = None
_engine: SearchEngine | None = None
_facilities: FacilityStore | None = None


def configure(docs_root: Path, engine: str = "bm25", facilities_db: Path | None = None) -> None:
    """문서 루트와 검색 엔진을 설정한다. 루트가 없으면 즉시 실패 (BR-11)."""
    global _store, _engine, _facilities
    _store = DocumentStore(docs_root)
    _engine = ENGINES[engine](_store)
    _facilities = FacilityStore(facilities_db) if facilities_db else None


@mcp.tool(
    annotations={
        "title": "Search Pet Medical Wiki",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
def search(query: str, limit: int = DEFAULT_LIMIT) -> dict:
    """Searches pet medical wiki documents from PetMed(펫메드) by keyword.

    Documents (in Korean) cover vaccination, diseases, symptom triage with urgency
    levels, toxic foods, grooming, nutrition, and life-stage care for dogs and cats.
    Returns BM25-ranked results with path, title, and up to 3 section snippets each.
    Use Korean symptom keywords (e.g. "구토", "경련") to find triage guides; call the
    read tool with a result path for full content.
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


@mcp.tool(
    annotations={
        "title": "Read Wiki Document",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
def read(path: str) -> dict:
    """Reads the full content of a pet medical wiki document from PetMed(펫메드).

    The path parameter must be a document path returned by the search tool.
    """
    try:
        return asdict(_store.load_document(path))
    except DocumentStoreError as e:
        return {"error": str(e)}


@mcp.tool(
    annotations={
        "title": "Find Animal Facilities in Korea",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    }
)
def find_facility(
    facility_type: str | None = None,
    region: str | None = None,
    name: str | None = None,
    include_closed: bool = False,
    limit: int = 20,
) -> dict:
    """Finds Korean animal facilities from PetMed(펫메드) public license data.

    facility_type: "동물병원" (hospital) | "동물약국" (pharmacy) | "동물미용업" (grooming).
    region: Korean sido/sigungu/neighborhood or address fragment, e.g. "강남구".
    name: facility name fragment — use name="24시" to find 24-hour emergency hospitals.
    Only active businesses are returned unless include_closed=true.
    """
    if _facilities is None:
        return {"error": "시설 DB가 설정되지 않았습니다 (--facilities-db 또는 WIKI_FACILITIES_DB)"}
    results = _facilities.find(
        facility_type=facility_type,
        region=region,
        name=name,
        include_closed=include_closed,
        limit=limit,
    )
    # PlayMCP 가이드: 결과 최소화 — 빈 필드는 제거하고 반환
    slim = [{k: v for k, v in r.items() if v not in ("", None)} for r in results]
    return {
        "total": len(slim),
        "results": slim,
        "message": None if slim else "조건에 맞는 시설이 없습니다.",
    }


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
    parser.add_argument(
        "--facilities-db",
        default=os.environ.get("WIKI_FACILITIES_DB"),
        help="시설 SQLite DB 경로 (env: WIKI_FACILITIES_DB, 선택)",
    )
    args = parser.parse_args()

    if not args.docs_root:
        parser.error("--docs-root 인자 또는 WIKI_DOCS_ROOT 환경변수가 필요합니다")

    configure(
        Path(args.docs_root),
        engine=args.engine,
        facilities_db=Path(args.facilities_db) if args.facilities_db else None,
    )
    mcp.run(transport="http", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
