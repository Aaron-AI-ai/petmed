"""문서 저장소 — 루트 디렉토리 재귀 스캔 및 안전한 문서 로드 (BR-1/2/4/10/11)."""

from pathlib import Path

from .models import Document


class DocumentStoreError(ValueError):
    """사용자에게 그대로 전달 가능한 문서 접근 오류."""


def _title_of(path: Path, content: str) -> str:
    for line in content.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


class DocumentStore:
    def __init__(self, root: Path) -> None:
        if not root.is_dir():
            raise DocumentStoreError(f"문서 루트 디렉토리가 없습니다: {root}")
        self.root = root.resolve()

    def list_documents(self) -> list[Document]:
        docs: list[Document] = []
        for p in sorted(self.root.rglob("*.md")):
            if not p.is_file():
                continue
            try:
                content = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue  # BR-11: 읽기 실패 파일은 건너뛰고 계속
            docs.append(
                Document(
                    path=str(p.relative_to(self.root)),
                    title=_title_of(p, content),
                    content=content,
                )
            )
        return docs

    def load_document(self, path: str) -> Document:
        candidate = Path(path)
        if candidate.is_absolute():
            raise DocumentStoreError("허용되지 않는 경로입니다")
        resolved = (self.root / candidate).resolve()
        if not resolved.is_relative_to(self.root):
            raise DocumentStoreError("허용되지 않는 경로입니다")  # BR-1
        if resolved.suffix.lower() != ".md":
            raise DocumentStoreError("마크다운(.md) 문서만 조회할 수 있습니다")  # BR-2
        if not resolved.is_file():
            raise DocumentStoreError(f"문서를 찾을 수 없습니다: {path}")  # BR-4
        content = resolved.read_text(encoding="utf-8", errors="replace")  # BR-10
        return Document(
            path=str(resolved.relative_to(self.root)),
            title=_title_of(resolved, content),
            content=content,
        )
