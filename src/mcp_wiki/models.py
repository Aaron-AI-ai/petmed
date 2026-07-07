"""도메인 모델 — aidlc-docs/construction/mcp-wiki-server/functional-design/domain-entities.md 매핑."""

from dataclasses import dataclass
from typing import Protocol


@dataclass
class Document:
    path: str  # 문서 루트 기준 상대 경로
    title: str  # 첫 H1 헤딩, 없으면 파일명(확장자 제외)
    content: str


@dataclass
class Section:
    heading: str  # 헤딩 라인 텍스트("## ..." 형식), 전문(preamble)은 빈 문자열
    text: str  # 헤딩 라인 포함 섹션 전체 텍스트


@dataclass
class Snippet:
    section: str
    text: str


@dataclass
class SearchResult:
    path: str
    title: str
    match_count: int
    snippets: list[Snippet]
    score: float = 0.0  # 랭킹 점수 (BM25/시맨틱/하이브리드). KeywordSearchEngine은 match_count 사용


class SearchEngine(Protocol):
    """시맨틱 검색 확장을 위한 교체 지점 (NFR-3)."""

    def search(self, query: str, limit: int) -> list[SearchResult]: ...
