# Build Instructions

## Prerequisites
- **Build Tool**: uv (Python 패키지/프로젝트 관리자)
- **Python**: 3.12 이상
- **Dependencies**: fastmcp>=2.0 (런타임), pytest>=8 + hypothesis>=6 (dev) — pyproject.toml에 정의
- **Environment Variables**: 빌드에는 불필요. 실행 시 `WIKI_DOCS_ROOT` (또는 `--docs-root` 인자) 필수
- **System Requirements**: macOS/Linux, 특별한 리소스 요구 없음

## Build Steps

### 1. Install Dependencies
```bash
cd /Users/koscom/workspace/petmed
uv sync
```

### 2. Configure Environment
```bash
# 실행 시에만 필요 (아래 중 택1)
export WIKI_DOCS_ROOT=sample-docs
# 또는 실행 인자로: --docs-root sample-docs
```

### 3. Build All Units
```bash
# Python 프로젝트 — 별도 컴파일 없음. uv sync가 editable 설치까지 수행.
# 배포용 wheel이 필요한 경우:
uv build
```

### 4. Verify Build Success
- **Expected Output**: `uv sync` 완료 (Resolved/Installed 메시지, 오류 없음)
- **Build Artifacts**: `.venv/` (로컬 환경), `uv build` 시 `dist/*.whl`
- **실행 확인**: `uv run mcp-wiki-server --docs-root sample-docs` → `http://127.0.0.1:8000/mcp` 에서 Streamable HTTP 서비스 시작

## Troubleshooting

### uv sync가 Python 버전 오류로 실패
- **Cause**: 시스템에 Python 3.12+ 미설치
- **Solution**: `uv python install 3.12` 후 재시도

### 서버 시작 시 "문서 루트 디렉토리가 없습니다"
- **Cause**: `--docs-root`/`WIKI_DOCS_ROOT`가 없거나 잘못된 경로 (BR-11 fail-fast 설계)
- **Solution**: 실제 존재하는 마크다운 문서 디렉토리를 지정
