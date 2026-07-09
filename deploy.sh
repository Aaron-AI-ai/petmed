#!/usr/bin/env bash
# petmed MCP 위키 서버 — 원커맨드 배포 스크립트
# 사용법: ./deploy.sh          (빌드 + facilities.db 준비 + 컨테이너 기동)
set -euo pipefail
cd "$(dirname "$0")"

command -v docker >/dev/null || { echo "ERROR: docker가 필요합니다"; exit 1; }
docker info >/dev/null 2>&1 || { echo "ERROR: docker 데몬이 실행 중이 아닙니다"; exit 1; }

echo "==> 이미지 빌드"
docker compose build

IMAGE=$(docker compose config --images | head -1)

# facilities.db 준비: 없으면 CSV 임포트, CSV도 없으면 빈 스키마 생성
if [ ! -f facilities.db ]; then
  if ls datas/*.csv >/dev/null 2>&1; then
    echo "==> facilities.db 생성 (datas/*.csv 임포트)"
    # 이미지에 설치된 실행 파일을 직접 사용 — 마운트된 프로젝트의 .venv를 건드리지 않음
    docker run --rm -v "$PWD:/work" -w /work "$IMAGE" \
      /app/.venv/bin/mcp-wiki-import datas/*.csv -o facilities.db
  else
    echo "==> facilities.db 없음, datas/*.csv 도 없음 — 빈 DB 생성 (find_facility는 빈 결과 반환)"
    docker run --rm -v "$PWD:/work" -w /work "$IMAGE" \
      /app/.venv/bin/python -c \
      "import sqlite3; from mcp_wiki.facilities import _SCHEMA; sqlite3.connect('/work/facilities.db').executescript(_SCHEMA)"
  fi
fi

echo "==> 컨테이너 기동"
docker compose up -d

echo "==> 헬스체크 (최대 15초)"
for _ in $(seq 1 15); do
  if curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8800/mcp | grep -qE '40[06]'; then
    # MCP 엔드포인트는 일반 GET에 400/406을 반환 = 서버 정상 기동
    echo "OK: http://127.0.0.1:8800/mcp"
    exit 0
  fi
  sleep 1
done
echo "WARN: 응답 확인 실패 — 'docker compose logs' 를 확인하세요"
exit 1
