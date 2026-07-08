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


@mcp.tool
def search(query: str, limit: int = DEFAULT_LIMIT) -> dict:
    """위키 문서를 키워드로 검색합니다.

    공백으로 구분된 모든 키워드가 포함된(AND, 대소문자 무시) 마크다운 문서를 찾아
    경로/제목/매칭 수와 섹션 단위 발췌(snippet, 문서당 최대 3개)를 반환합니다.
    전체 내용이 필요하면 결과의 path로 read 도구를 호출하세요.

    반려동물 증상 상담 시: 증상 키워드(예: "구토", "배뇨", "경련")로 검색하면
    symptoms/ 카테고리의 긴급도(트리아지) 가이드가 매칭됩니다. 응급 신호가 있으면
    find_facility로 근처 병원(야간은 name="24시")을 함께 안내하세요.
    피부/상처 사진이 첨부된 경우: 사진에서 관찰한 특징(예: "원형 탈모", "농포",
    "물린 상처")으로 검색하면 사진 판독 가이드(symptoms/skin-lesions.md)가 매칭됩니다.
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


@mcp.tool
def find_facility(
    facility_type: str | None = None,
    region: str | None = None,
    name: str | None = None,
    include_closed: bool = False,
    limit: int = 20,
) -> dict:
    """동물 관련 시설을 조건으로 검색합니다 (전국 인허가 공공데이터).

    facility_type: "동물병원" | "동물약국" | "동물미용업" (부분 일치 가능)
    region: 시/도, 시/군/구, 동 단위 또는 주소 일부 (예: "강남구", "역삼동", "서울")
    name: 시설명 일부 — 야간/응급 병원을 찾을 때는 name="24시"로 검색
    기본적으로 영업 중인 시설만 반환하며, include_closed=True면 폐업 이력 포함.
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
    return {
        "total": len(results),
        "results": results,
        "message": None if results else "조건에 맞는 시설이 없습니다.",
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
