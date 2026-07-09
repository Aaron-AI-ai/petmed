FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# 의존성 레이어 캐시: 소스 변경 시 재설치 방지
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src ./src
RUN uv sync --frozen --no-dev

# 위키 문서와 시설 DB를 이미지에 포함 — 이미지 하나로 완전 독립 실행
COPY wiki-docs /docs
COPY facilities.db /data/facilities.db

ENV WIKI_DOCS_ROOT=/docs \
    WIKI_FACILITIES_DB=/data/facilities.db \
    WIKI_HOST=0.0.0.0 \
    WIKI_PORT=8000

EXPOSE 8000

CMD ["uv", "run", "--frozen", "--no-dev", "mcp-wiki-server"]
