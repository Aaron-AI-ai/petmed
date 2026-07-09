"""검색 엔진 — KeywordSearchEngine(AND 매칭) + BM25SearchEngine(bigram BM25 랭킹).

공통: 섹션 단위 snippet (BR-7), limit (BR-8), 빈 검색어 거부 (BR-3).
"""

import math
import re

from .models import Document, SearchResult, Section, Snippet
from .store import DocumentStore

MAX_SNIPPETS_PER_DOC = 3  # BR-7
MAX_SNIPPET_CHARS = 500  # PlayMCP 가이드: result 크기 최소화
DEFAULT_LIMIT = 10  # BR-8 / 설계 결정 D-1

_HEADING_RE = re.compile(r"^#{1,6}\s")


def tokenize(query: str) -> list[str]:
    """공백 분리 + 소문자화. 빈 토큰 없음 (BR-3/5)."""
    return [t.lower() for t in query.split()]


def split_sections(content: str) -> list[Section]:
    """헤딩 단위 무손실 분할 — 모든 Section.text를 이어 붙이면 원본과 동일 (P1)."""
    sections: list[Section] = []
    heading = ""
    lines: list[str] = []
    for line in content.splitlines(keepends=True):
        if _HEADING_RE.match(line):
            if lines:
                sections.append(Section(heading=heading, text="".join(lines)))
            heading = line.strip()
            lines = [line]
        else:
            lines.append(line)
    if lines:
        sections.append(Section(heading=heading, text="".join(lines)))
    return sections


def document_haystack(doc: Document) -> str:
    """매칭 대상 텍스트: 상대 경로(파일명 포함) + 본문, 소문자 (BR-5/6)."""
    return f"{doc.path}\n{doc.content}".lower()


def _count_matches(keywords: list[str], text_lower: str) -> int:
    return sum(text_lower.count(k) for k in keywords)


class KeywordSearchEngine:
    """SearchEngine 구현체. store는 list_documents()만 사용한다."""

    def __init__(self, store: DocumentStore) -> None:
        self._store = store

    def search(self, query: str, limit: int = DEFAULT_LIMIT) -> list[SearchResult]:
        keywords = tokenize(query)
        if not keywords:
            raise ValueError("검색어를 입력해 주세요")  # BR-3
        results: list[SearchResult] = []
        for doc in self._store.list_documents():
            haystack = document_haystack(doc)
            if not all(k in haystack for k in keywords):  # BR-6: AND
                continue
            results.append(
                SearchResult(
                    path=doc.path,
                    title=doc.title,
                    match_count=_count_matches(keywords, haystack),
                    snippets=_extract_snippets(doc, keywords),
                )
            )
        results.sort(key=lambda r: (-r.match_count, r.path))  # BR-8
        return results[: max(limit, 0)]


class BM25SearchEngine:
    """BM25 랭킹 검색 (SearchEngine 구현체).

    문자 bigram 토큰화로 한국어 조사/합성어에서도 부분 일치가 동작한다
    ("백신" ↔ "종합백신을"). 문서가 수십 개 규모라 인덱스는 요청 시 구축한다.
    추후 SemanticSearchEngine과 점수 융합(하이브리드)으로 확장하는 지점.
    """

    K1 = 1.5
    B = 0.75

    def __init__(self, store: DocumentStore) -> None:
        self._store = store

    def search(self, query: str, limit: int = DEFAULT_LIMIT) -> list[SearchResult]:
        keywords = tokenize(query)
        if not keywords:
            raise ValueError("검색어를 입력해 주세요")  # BR-3
        query_tokens = _bigrams(" ".join(keywords))
        docs = self._store.list_documents()
        if not docs or not query_tokens:
            return []

        doc_tokens = [_token_counts(_bigrams(document_haystack(d))) for d in docs]
        avgdl = sum(sum(tc.values()) for tc in doc_tokens) / len(docs)
        n = len(docs)

        results: list[SearchResult] = []
        for doc, counts in zip(docs, doc_tokens):
            score = 0.0
            dl = sum(counts.values())
            for token in set(query_tokens):
                tf = counts.get(token, 0)
                if tf == 0:
                    continue
                df = sum(1 for tc in doc_tokens if token in tc)
                idf = math.log((n - df + 0.5) / (df + 0.5) + 1)
                denom = tf + self.K1 * (1 - self.B + self.B * dl / avgdl) if avgdl else tf
                score += idf * tf * (self.K1 + 1) / denom
            if score <= 0.0:
                continue
            haystack = document_haystack(doc)
            results.append(
                SearchResult(
                    path=doc.path,
                    title=doc.title,
                    match_count=_count_matches(keywords, haystack),
                    snippets=_extract_snippets(doc, keywords),
                    score=round(score, 4),
                )
            )
        results.sort(key=lambda r: (-r.score, r.path))
        return results[: max(limit, 0)]


def _bigrams(text: str) -> list[str]:
    """공백 제거 후 문자 bigram. 1글자 단어도 검색되도록 길이 1 텍스트는 그대로."""
    tokens: list[str] = []
    for word in text.lower().split():
        if len(word) == 1:
            tokens.append(word)
        else:
            tokens.extend(word[i : i + 2] for i in range(len(word) - 1))
    return tokens


def _token_counts(tokens: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for t in tokens:
        counts[t] = counts.get(t, 0) + 1
    return counts


def _extract_snippets(doc: Document, keywords: list[str]) -> list[Snippet]:
    """키워드를 포함한 섹션 중 출현 횟수 상위 3개, 동률 시 문서 내 등장 순 (BR-7)."""
    scored: list[tuple[int, int, Section]] = []
    for idx, section in enumerate(split_sections(doc.content)):
        count = _count_matches(keywords, section.text.lower())
        if count > 0:
            scored.append((-count, idx, section))
    scored.sort(key=lambda t: (t[0], t[1]))
    return [
        Snippet(section=s.heading, text=s.text[:MAX_SNIPPET_CHARS])
        for _, _, s in scored[:MAX_SNIPPETS_PER_DOC]
    ]
