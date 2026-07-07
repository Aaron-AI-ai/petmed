"""검색 로직 예제 기반 테스트 — BR-3/5/6/7/8/9 + BM25."""

import pytest

from mcp_wiki.models import Document
from mcp_wiki.search import BM25SearchEngine, KeywordSearchEngine, split_sections, tokenize


class FakeStore:
    """list_documents()만 사용하는 엔진 계약에 맞춘 스텁."""

    def __init__(self, docs):
        self._docs = docs

    def list_documents(self):
        return self._docs


def _engine(docs):
    return KeywordSearchEngine(FakeStore(docs))


DOCS = [
    Document("care/vaccine.md", "예방접종", "# 예방접종\n\n## 일정\n강아지 vaccine 일정\n\n## 비용\nvaccine 비용 안내"),
    Document("care/food.md", "사료", "# 사료\n강아지 사료 고르기"),
    Document("intro.md", "소개", "# 소개\n고양이 건강 위키"),
]


def test_and_matching():
    results = _engine(DOCS).search("강아지 vaccine")
    assert [r.path for r in results] == ["care/vaccine.md"]  # food.md에는 vaccine 없음


def test_case_insensitive():
    results = _engine(DOCS).search("VACCINE")
    assert results and results[0].path == "care/vaccine.md"


def test_sort_by_match_count_desc():
    results = _engine(DOCS).search("강아지")
    assert [r.path for r in results] == ["care/food.md", "care/vaccine.md"]  # 동률 시 경로 순


def test_snippets_are_matching_sections():
    results = _engine(DOCS).search("vaccine")
    snippets = results[0].snippets
    assert len(snippets) == 2
    assert {s.section for s in snippets} == {"## 일정", "## 비용"}
    assert all("vaccine" in s.text for s in snippets)


def test_snippets_capped_at_three():
    content = "\n".join(f"## s{i}\nword here" for i in range(5))
    results = _engine([Document("a.md", "a", content)]).search("word")
    assert len(results[0].snippets) == 3


def test_filename_only_match_has_no_snippets():
    results = _engine([Document("vaccine.md", "v", "본문에는 키워드 없음")]).search("vaccine")
    assert results[0].snippets == []


def test_empty_query_rejected():
    with pytest.raises(ValueError, match="검색어"):
        _engine(DOCS).search("   ")


def test_no_match_returns_empty():
    assert _engine(DOCS).search("존재하지않는단어") == []


def test_limit():
    results = _engine(DOCS).search("강아지", limit=1)
    assert len(results) == 1


def test_tokenize():
    assert tokenize("  Pet  Vaccine ") == ["pet", "vaccine"]


def test_split_sections_preamble_and_headings():
    doc = "preamble\n# H1\nbody\n## H2\nmore"
    sections = split_sections(doc)
    assert [s.heading for s in sections] == ["", "# H1", "## H2"]
    assert "".join(s.text for s in sections) == doc


# --- BM25SearchEngine ---------------------------------------------------------


def _bm25(docs):
    return BM25SearchEngine(FakeStore(docs))


def test_bm25_ranks_relevant_doc_first():
    results = _bm25(DOCS).search("vaccine 일정")
    assert results[0].path == "care/vaccine.md"
    assert results[0].score > 0


def test_bm25_korean_partial_match_via_bigrams():
    docs = [Document("a.md", "a", "종합백신을 접종합니다"), Document("b.md", "b", "사료 이야기")]
    results = _bm25(docs).search("백신")  # 조사가 붙은 "종합백신을"과 매칭
    assert [r.path for r in results] == ["a.md"]


def test_bm25_scores_sorted_desc():
    results = _bm25(DOCS).search("강아지")
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_bm25_empty_query_rejected():
    with pytest.raises(ValueError, match="검색어"):
        _bm25(DOCS).search("  ")


def test_bm25_no_match_and_limit():
    assert _bm25(DOCS).search("zzzz없는말qq") == []
    assert len(_bm25(DOCS).search("강아지", limit=1)) == 1
