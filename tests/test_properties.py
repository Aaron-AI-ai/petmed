"""속성 기반 테스트 (Hypothesis) — functional design의 P1~P7.

PBT-02: P1 (섹션 분할 round-trip)
PBT-03: P2~P7 (불변식)
PBT-07: 도메인 제너레이터(마크다운 문서/검색어)를 이 모듈에 중앙화
PBT-08: Hypothesis 기본 shrinking/시드 리포팅 사용 (비활성화 설정 없음)
"""

import string
import tempfile
from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

from mcp_wiki.models import Document
from mcp_wiki.search import (
    MAX_SNIPPET_CHARS,
    MAX_SNIPPETS_PER_DOC,
    BM25SearchEngine,
    KeywordSearchEngine,
    document_haystack,
    split_sections,
    tokenize,
)
from mcp_wiki.store import DocumentStore, DocumentStoreError

# --- 도메인 제너레이터 (PBT-07) ---------------------------------------------

_word = st.text(alphabet=string.ascii_lowercase, min_size=1, max_size=8)
_line = st.lists(_word, max_size=8).map(" ".join)
_heading_line = st.builds(lambda lvl, t: "#" * lvl + " " + t, st.integers(1, 6), _line)
_markdown_content = st.lists(st.one_of(_line, _heading_line), max_size=15).map("\n".join)
_doc_path = st.lists(_word, min_size=1, max_size=3).map(lambda parts: "/".join(parts) + ".md")

documents = st.builds(Document, path=_doc_path, title=_word, content=_markdown_content)
document_lists = st.lists(documents, max_size=8, unique_by=lambda d: d.path)
queries = st.lists(_word, min_size=1, max_size=3).map(" ".join)


class FakeStore:
    def __init__(self, docs):
        self._docs = docs

    def list_documents(self):
        return self._docs


# --- P1: 섹션 분할 무손실 round-trip (PBT-02) --------------------------------


@given(st.text(max_size=2000))
def test_p1_split_sections_roundtrip(content):
    assert "".join(s.text for s in split_sections(content)) == content


# --- P5: 토큰화 불변식 -------------------------------------------------------


@given(st.text(max_size=200))
def test_p5_tokenize_invariants(query):
    tokens = tokenize(query)
    for t in tokens:
        assert t, "빈 토큰 없음"
        assert t == t.lower(), "소문자"
        assert not any(c.isspace() for c in t), "공백 미포함"


# --- P2/P3/P4/P7: 검색 결과 불변식 (PBT-03) ----------------------------------


@given(docs=document_lists, query=queries, limit=st.integers(0, 20))
def test_p2_p3_p4_p7_search_invariants(docs, query, limit):
    results = KeywordSearchEngine(FakeStore(docs)).search(query, limit)
    keywords = tokenize(query)
    by_path = {d.path: d for d in docs}

    assert len(results) <= limit, "P7: limit 준수"

    counts = [r.match_count for r in results]
    assert counts == sorted(counts, reverse=True), "P3: match_count 비증가 정렬"

    for r in results:
        doc = by_path[r.path]
        haystack = document_haystack(doc)
        assert all(k in haystack for k in keywords), "P2: AND 보장"
        assert r.match_count >= 1

        assert len(r.snippets) <= MAX_SNIPPETS_PER_DOC, "P4: snippet 상한"
        for s in r.snippets:
            assert s.text in doc.content, "P4: snippet은 원본의 부분 문자열"
            assert len(s.text) <= MAX_SNIPPET_CHARS, "P4: snippet 길이 상한"
            if len(s.text) < MAX_SNIPPET_CHARS:  # 잘리지 않은 snippet만 키워드 보장
                assert any(k in s.text.lower() for k in keywords), "P4: snippet은 키워드 포함"


# --- P8: BM25 검색 불변식 (PBT-03) --------------------------------------------


@given(docs=document_lists, query=queries, limit=st.integers(0, 20))
def test_p8_bm25_invariants(docs, query, limit):
    results = BM25SearchEngine(FakeStore(docs)).search(query, limit)
    by_path = {d.path: d for d in docs}

    assert len(results) <= limit, "limit 준수"

    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True), "score 비증가 정렬"

    for r in results:
        assert r.score > 0, "0점 문서는 제외"
        doc = by_path[r.path]
        assert len(r.snippets) <= MAX_SNIPPETS_PER_DOC
        for s in r.snippets:
            assert s.text in doc.content, "snippet은 원본의 부분 문자열"


# --- P6: 경로 안전성 (PBT-03 / BR-1) -----------------------------------------

_ROOT = Path(tempfile.mkdtemp(prefix="mcp-wiki-pbt-"))
(_ROOT / "sub").mkdir()
(_ROOT / "a.md").write_text("# a\nhello", encoding="utf-8")
(_ROOT / "sub" / "b.md").write_text("# b\nworld", encoding="utf-8")
(_ROOT.parent / "mcp-wiki-pbt-outside.md").write_text("outside", encoding="utf-8")
_STORE = DocumentStore(_ROOT)


@given(st.text(min_size=1, max_size=100))
def test_p6_load_document_never_escapes_root(path):
    try:
        doc = _STORE.load_document(path)
    except (DocumentStoreError, ValueError, OSError):
        return  # 거부는 안전한 결과
    resolved = (_ROOT / doc.path).resolve()
    assert resolved.is_relative_to(_ROOT.resolve()), "P6: 루트 밖 파일을 열지 않음"


@given(st.sampled_from(["../", "..\\", "/", "~", "%2e%2e/"]).flatmap(
    lambda prefix: st.just(prefix + "mcp-wiki-pbt-outside.md")
))
def test_p6_traversal_prefixes_rejected_or_contained(path):
    try:
        doc = _STORE.load_document(path)
    except (DocumentStoreError, ValueError, OSError):
        return
    assert (_ROOT / doc.path).resolve().is_relative_to(_ROOT.resolve())
