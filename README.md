# petmed — LLM Wiki MCP Server

서버의 특정 디렉토리에 있는 마크다운(.md) 문서를 검색/조회하는 MCP 서비스입니다.
FastMCP 기반 **Streamable HTTP** transport로 동작합니다.

## MCP 도구

| 도구 | 입력 | 출력 |
|---|---|---|
| `search` | `query` (공백 구분 키워드), `limit` (기본 10) | 문서별 경로/제목/점수(score)/매칭 수 + 섹션 단위 snippet(최대 3개) JSON |
| `read` | `path` (search 결과의 상대 경로) | 문서 전체 내용 JSON |

## 검색 엔진

`SearchEngine` Protocol 기반으로 교체 가능:

- **bm25** (기본) — 문자 bigram 토큰화 BM25 랭킹. 한국어 조사/합성어 부분 매칭 지원 ("백신" ↔ "종합백신을")
- **keyword** — 공백 키워드 AND 부분 문자열 매칭 (정확 매칭 위주)
- (예정) 임베딩 기반 시맨틱 검색 + BM25 하이브리드(점수 융합)

## 문서 저장소

- `wiki-docs/` — 실제 서비스 문서 (카테고리별: `vaccination/`, `diseases/`, `emergency/`, `prevention/`, `nutrition/`)
- `sample-docs/` — 테스트 픽스처 (E2E 테스트가 참조하므로 내용 변경 금지)

## 설치 및 실행

```bash
uv sync                                        # 의존성 설치 (Python 3.12)
uv run mcp-wiki-server --docs-root wiki-docs   # http://127.0.0.1:8000/mcp
```

### Docker Compose

```bash
docker compose up -d --build    # http://127.0.0.1:8800/mcp (호스트 8000은 다른 서비스 사용 중)
```

`compose.yaml`이 `./wiki-docs`를 컨테이너 `/docs`에 읽기 전용 마운트합니다. 문서 경로를 바꾸려면 volumes 항목 수정.

설정 (CLI 인자 또는 환경변수):

| 항목 | CLI | 환경변수 | 기본값 |
|---|---|---|---|
| 문서 루트 | `--docs-root` | `WIKI_DOCS_ROOT` | (필수) |
| 호스트 | `--host` | `WIKI_HOST` | `127.0.0.1` |
| 포트 | `--port` | `WIKI_PORT` | `8000` |
| 검색 엔진 | `--engine` | `WIKI_SEARCH_ENGINE` | `bm25` |

문서 변경(추가/수정/삭제)은 서버 재시작으로 반영됩니다 (인덱스는 요청 시 구축).

## 테스트

```bash
uv run pytest                # 예제 기반 + 속성 기반(Hypothesis) 테스트
```

속성 기반 테스트 실패 시 Hypothesis가 최소 실패 입력과 재현 시드를 출력합니다.

## 설계 문서

AI-DLC 워크플로우 산출물은 `aidlc-docs/` 참고 (요구사항, 실행 계획, 기능 설계, 감사 로그).
