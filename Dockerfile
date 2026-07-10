FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# 의존성 레이어 캐시: 소스 변경 시 재설치 방지
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src ./src
RUN uv sync --frozen --no-dev

# 위키 문서와 시설 DB를 이미지에 포함 — 이미지 하나로 완전 독립 실행.
# /data, /docs 같은 최상위 경로는 배포 플랫폼이 볼륨을 마운트해 가릴 수 있어 /app 아래에 둔다.
COPY wiki-docs /app/wiki-docs
COPY facilities.db /app/facilities.db

ENV WIKI_DOCS_ROOT=/app/wiki-docs \
    WIKI_FACILITIES_DB=/app/facilities.db \
    WIKI_HOST=0.0.0.0 \
    WIKI_PORT=8000 \
    FASTMCP_HTTP_ALLOWED_HOSTS='["*"]' \
    FASTMCP_STATELESS_HTTP=true \
    WIKI_MCP_PATH=/mcp

# 배포 플랫폼 콘솔의 컨테이너 포트 설정(8000)과 일치
EXPOSE 8000

CMD ["uv", "run", "--frozen", "--no-dev", "mcp-wiki-server"]
