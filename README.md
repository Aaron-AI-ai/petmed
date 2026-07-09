# petmed — LLM Wiki MCP Server

서버의 특정 디렉토리에 있는 마크다운(.md) 문서를 검색/조회하는 MCP 서비스입니다.
FastMCP 기반 **Streamable HTTP** transport로 동작합니다.

## MCP 도구

| 도구 | 입력 | 출력 |
|---|---|---|
| `search` | `query` (공백 구분 키워드), `limit` (기본 10) | 문서별 경로/제목/점수(score)/매칭 수 + 섹션 단위 snippet(최대 3개) JSON |
| `read` | `path` (search 결과의 상대 경로) | 문서 전체 내용 JSON |
| `find_facility` | `facility_type`(동물병원/동물약국/동물미용업), `region`, `name`, `include_closed`, `limit` | 전국 인허가 시설 목록 JSON (기본: 영업 중만) |

## 검색 엔진

`SearchEngine` Protocol 기반으로 교체 가능:

- **bm25** (기본) — 문자 bigram 토큰화 BM25 랭킹. 한국어 조사/합성어 부분 매칭 지원 ("백신" ↔ "종합백신을")
- **keyword** — 공백 키워드 AND 부분 문자열 매칭 (정확 매칭 위주)
- (예정) 임베딩 기반 시맨틱 검색 + BM25 하이브리드(점수 융합)

## 시설 정형 데이터 (SQLite)

동물병원/동물약국/동물미용업 인허가 데이터(공공데이터포털 LOCALDATA CSV)는 위키(md)와 분리하여 SQLite에 저장한다:

```bash
# CSV(cp949/utf-8 자동 인식) → facilities.db 생성/갱신 (전체 교체 방식)
uv run mcp-wiki-import datas/*.csv -o facilities.db
```

서버에 `--facilities-db facilities.db` (또는 `WIKI_FACILITIES_DB`)로 연결하면 `find_facility` 도구가 활성화된다. 미설정 시 도구는 안내 오류를 반환한다. `datas/`(원본 CSV)와 `facilities.db`는 git에 커밋하지 않는다.

## 문서 저장소

- `wiki-docs/` — 실제 서비스 문서 (카테고리별: `vaccination/`, `diseases/`, `emergency/`, `prevention/`, `nutrition/`)
- `sample-docs/` — 테스트 픽스처 (E2E 테스트가 참조하므로 내용 변경 금지)

## 설치 및 실행

```bash
uv sync                                        # 의존성 설치 (Python 3.12)
uv run mcp-wiki-server --docs-root wiki-docs   # http://127.0.0.1:8000/mcp
```

### Docker (원커맨드 배포)

```bash
./deploy.sh    # facilities.db 준비 → 이미지 빌드 → 기동 → 헬스체크. http://<호스트>:8800/petmed-mcp
```

이미지의 MCP 엔드포인트 경로 기본값은 **`/petmed-mcp`** 입니다 (`WIKI_MCP_PATH` env로 변경 가능, 로컬 실행 기본값은 `/mcp`).

**wiki-docs/와 facilities.db는 이미지 안에 포함**됩니다(Dockerfile COPY). 이미지 하나로 완전 독립 실행이 가능하며(`docker run -p 8800:8000 petmed-mcp-wiki`), 문서/데이터 갱신은 `./deploy.sh` 재실행(재빌드)으로 반영합니다. 단, `docker build`에는 `facilities.db` 파일이 미리 있어야 합니다 — deploy.sh가 자동 생성합니다.

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
