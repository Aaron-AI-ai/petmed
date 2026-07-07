"""DocumentStore 예제 기반 테스트 — BR-1/2/4/10/11."""

import pytest

from mcp_wiki.store import DocumentStore, DocumentStoreError


@pytest.fixture
def store(tmp_path):
    (tmp_path / "guide.md").write_text("# 가이드\n반려동물 예방접종 안내", encoding="utf-8")
    sub = tmp_path / "care"
    sub.mkdir()
    (sub / "nutrition.md").write_text("사료와 영양 정보 (헤딩 없음)", encoding="utf-8")
    (tmp_path / "ignore.txt").write_text("md 아님", encoding="utf-8")
    (tmp_path / "secret.txt").write_text("비밀", encoding="utf-8")
    return DocumentStore(tmp_path)


def test_list_documents_recursive_md_only(store):
    paths = [d.path for d in store.list_documents()]
    assert paths == ["care/nutrition.md", "guide.md"]  # 정렬 + .md만 + 재귀


def test_title_from_h1_or_filename(store):
    docs = {d.path: d.title for d in store.list_documents()}
    assert docs["guide.md"] == "가이드"
    assert docs["care/nutrition.md"] == "nutrition"  # H1 없으면 파일명


def test_load_document(store):
    doc = store.load_document("care/nutrition.md")
    assert doc.path == "care/nutrition.md"
    assert "영양" in doc.content


def test_load_rejects_path_traversal(store, tmp_path):
    outside = tmp_path.parent / "outside.md"
    outside.write_text("밖", encoding="utf-8")
    with pytest.raises(DocumentStoreError, match="허용되지 않는"):
        store.load_document("../outside.md")


def test_load_rejects_absolute_path(store, tmp_path):
    with pytest.raises(DocumentStoreError, match="허용되지 않는"):
        store.load_document(str(tmp_path / "guide.md"))


def test_load_rejects_non_md(store):
    with pytest.raises(DocumentStoreError, match="마크다운"):
        store.load_document("secret.txt")


def test_load_missing_document(store):
    with pytest.raises(DocumentStoreError, match="찾을 수 없습니다"):
        store.load_document("nope.md")


def test_missing_root_fails_fast(tmp_path):
    with pytest.raises(DocumentStoreError, match="루트 디렉토리"):
        DocumentStore(tmp_path / "does-not-exist")
