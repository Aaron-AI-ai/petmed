# AI-DLC Audit Log

## Initial User Request
**Timestamp**: 2026-07-07T12:50:00Z
**User Input**: "이 프로젝트는 llm wiki 컨셉 기반에 mcp 서비스를 만들고 싶어요. 서버 특정 경로에 md파일이 존재하고이 mcp를 통해 요청이 오면 md파일의 내용을 검색해서 전달하는 컨셉 입니다. 먼저 설계 및 계획부터 하겠습니다. 기술 스택은 python 3.12에 uv 사용하고 fastmcp Streamable HTTP  방식으로 구현할께"
**AI Response**: Started AI-DLC workflow. Displayed welcome message, executed Workspace Detection.
**Context**: INCEPTION - Workspace Detection

---

## Workspace Detection Findings
**Timestamp**: 2026-07-07T12:52:00Z
**User Input**: N/A (automatic stage)
**AI Response**: Workspace scanned. No source code files or build files found (only README.md, CLAUDE.md, .aidlc-rule-details/). Determined: Greenfield project. brownfield = false. Next phase: Requirements Analysis.
**Context**: INCEPTION - Workspace Detection complete

---

## Requirements Analysis - Clarifying Questions Created
**Timestamp**: 2026-07-07T12:55:00Z
**User Input**: N/A (AI-generated questions)
**AI Response**: Intent analysis performed (New Project / Multiple Components / Moderate complexity / Standard depth). Created requirement-verification-questions.md with 7 requirement questions + 2 extension opt-in questions (Security Baseline, Property-Based Testing). Waiting for user answers.
**Context**: INCEPTION - Requirements Analysis, Step 6 gate (awaiting answers)

---

## Requirements Analysis - Answers Received
**Timestamp**: 2026-07-07T13:05:00Z
**User Input**: "진행" (user filled answers in requirement-verification-questions.md: Q1=D keyword-first extensible to semantic, Q2=A search only, Q3=B recursive subdirectories, Q4=C restart to reflect changes, Q5=A dozens of docs, Q6=B snippet+path with full-read tool, Q7=A no auth internal/local, Q8=B Security extension OFF, Q9=B PBT Partial)
**AI Response**: Contradiction detected between Q2-A (search-only tool) and Q6-B (assumes separate full-read tool). Created requirements-clarification-questions.md with 1 clarification question. Waiting for answer.
**Context**: INCEPTION - Requirements Analysis, clarification gate

---

## Requirements Analysis - Clarification Answer & Requirements Generated
**Timestamp**: 2026-07-07T13:15:00Z
**User Input**: "A로 답변했어, 진행해" (Clarification Q1 = A: 2 tools — search returning snippet+path, plus full document read tool)
**AI Response**: Contradiction resolved. Loaded PBT rules (Partial mode: PBT-02, 03, 07, 08, 09 enforced). Recorded Extension Configuration in aidlc-state.md (Security=No, PBT=Partial). Generated aidlc-docs/inception/requirements/requirements.md (Standard depth). Presenting approval gate.
**Context**: INCEPTION - Requirements Analysis, Step 9 (awaiting approval)

---

## Requirements Analysis - Approval
**Timestamp**: 2026-07-07T13:25:00Z
**User Input**: "✅ Approve & Continue — 요구사항 승인 후 Workflow Planning으로 진행"
**AI Response**: Requirements approved. Proceeded to Workflow Planning. Created execution-plan.md: EXECUTE Functional Design + Code Generation + Build and Test (single unit mcp-wiki-server); SKIP User Stories, Application Design, Units Generation, NFR Requirements, NFR Design, Infrastructure Design. Risk: Low. Presenting plan approval gate.
**Context**: INCEPTION - Workflow Planning, Step 9 (awaiting approval)

---

## Workflow Planning - Approval
**Timestamp**: 2026-07-07T13:35:00Z
**User Input**: "✅ Approve & Continue — Functional Design으로 진행"
**Status**: Approved
**AI Response**: Execution plan approved. Entered CONSTRUCTION phase, Functional Design for unit mcp-wiki-server. Created mcp-wiki-server-functional-design-plan.md with 7-step plan and 6 design questions (multi-keyword handling, snippet format, result ordering, tool return format, search engine abstraction level, zero-result behavior). Waiting for answers.
**Context**: CONSTRUCTION - Functional Design, Step 5 gate (awaiting answers)

---

## Functional Design - Answers Received & Artifacts Generated
**Timestamp**: 2026-07-07T13:50:00Z
**User Input**: "답변 완료했어, 진행해" (answers in plan file: Q1=A AND matching, Q2=C section-level snippet, Q3=B max 3 snippets sorted by match count, Q4=A structured JSON, Q5=A Protocol/ABC SearchEngine interface, Q6=A empty results + no-match message)
**AI Response**: No ambiguities detected. Generated functional design artifacts: domain-entities.md (Document, Section, SearchQuery, Snippet, SearchResult, SearchEngine Protocol), business-logic-model.md (DocumentStore, KeywordSearchEngine, MCP Tool Layer, data flow, design decisions D-1..D-3, PBT-01 testable properties P1-P7), business-rules.md (BR-1..BR-11). All plan checkboxes marked complete. Presenting approval gate.
**Context**: CONSTRUCTION - Functional Design, Step 8 (awaiting approval)

---

## Functional Design - Approval
**Timestamp**: 2026-07-07T14:00:00Z
**User Input**: "✅ Continue to Next Stage — 설계 승인 후 Code Generation으로 진행"
**Status**: Approved
**AI Response**: Functional design approved. Started Code Generation Part 1 (Planning). Created mcp-wiki-server-code-generation-plan.md with 9 numbered steps, target structure (src/mcp_wiki: models/store/search/server + tests + sample-docs), requirement traceability, and PBT compliance plan (Partial mode).
**Context**: CONSTRUCTION - Code Generation Part 1, Step 6 (approval prompt logged, awaiting approval)

---

## Code Generation - Plan Approval & Part 2 Execution
**Timestamp**: 2026-07-07T14:15:00Z
**User Input**: "✅ Approve & Generate — 계획 승인 후 Part 2 코드 생성 실행"
**Status**: Approved
**AI Response**: Executed all 9 plan steps. Created: pyproject.toml, src/mcp_wiki/{__init__,models,store,search,server}.py, tests/{test_store,test_search,test_properties}.py, sample-docs/ (3 files), code-generation-summary.md; modified README.md. All Python files syntax-checked (ast.parse OK). All plan checkboxes marked [x]. PBT Partial rules (02/03/07/08/09) implemented in test_properties.py. Presenting approval gate.
**Context**: CONSTRUCTION - Code Generation Part 2, Step 15 (awaiting approval)

---

## Code Generation - Approval
**Timestamp**: 2026-07-07T14:30:00Z
**User Input**: "✅ Continue to Next Stage — Build & Test로 진행"
**Status**: Approved
**Context**: CONSTRUCTION - Code Generation approved, proceeding to Build and Test

---

## Build and Test Stage
**Timestamp**: 2026-07-07T14:45:00Z
**Build Status**: Success (uv sync, Python 3.12, fastmcp + pytest + hypothesis installed)
**Test Status**: Pass — 24/24 unit tests (incl. Hypothesis PBT P1~P7, 1.46s); 5/5 integration E2E scenarios over real Streamable HTTP server (tools list, search→read flow, path traversal rejection, no-match message, Korean query)
**Files Generated**:
- build-instructions.md
- unit-test-instructions.md
- integration-test-instructions.md
- performance-test-instructions.md (N/A with rationale)
- build-and-test-summary.md
**Context**: CONSTRUCTION - Build and Test, Step 9 (awaiting approval)

---

## Build and Test - Approval & Workflow Complete
**Timestamp**: 2026-07-07T14:55:00Z
**User Input**: "✅ Approve & Continue — 결과 승인하고 워크플로우 완료"
**Status**: Approved
**AI Response**: Build and Test approved. Operations stage is a placeholder — workflow marked COMPLETE in aidlc-state.md. All stages finished: Workspace Detection, Requirements Analysis, Workflow Planning, Functional Design, Code Generation (9/9), Build and Test (24 unit + 5 integration tests pass).
**Context**: AI-DLC workflow complete

---

## Post-Workflow - E2E Test Question & Addition
**Timestamp**: 2026-07-07T15:10:00Z
**User Input**: "그럼 playwrite와 같은 서비스를 통해 e2e 테스트 가능한가요 ?" → (assessment: Playwright unsuitable, no UI; fastmcp Client is the E2E equivalent) → "추가해주세요"
**AI Response**: Added tests/test_e2e.py — auto-starts server subprocess on a free port, verifies via fastmcp Client over real Streamable HTTP (5 scenarios). 29/29 tests pass. Updated integration-test-instructions.md and build-and-test-summary.md.
**Context**: Post-workflow enhancement

---

## Post-Workflow - Docker Compose
**Timestamp**: 2026-07-07T15:25:00Z
**User Input**: "docker compose 기반으로 서비스 바로 실행할수 있도록 준비해주세요"
**AI Response**: Created Dockerfile (python:3.12-slim + uv, frozen sync), compose.yaml, .dockerignore. Host port 8000 occupied by fico-mcp container → mapped 8800:8000. Started Docker Desktop daemon, built and ran container, verified via MCP client.
**Context**: Post-workflow enhancement

---

## Post-Workflow - Wiki Content Generation
**Timestamp**: 2026-07-07T15:40:00Z
**User Input**: "추가적으로 웹에서 반려동물이나 동물에 대한 의학 정보들을 겁색해서 그 데이터로 md 파일을 만들어주세요 md파일은 어디저장하도록 경로 설정되어 있나요 ? 경로도 검색하기 용이하게 카테고리화 하면 좋을 것 같아요"
**AI Response**: Explained docs path config (WIKI_DOCS_ROOT / compose volume). Created categorized wiki-docs/ (vaccination/, diseases/, emergency/, prevention/, nutrition/) with 8 documents researched via web search (WSAVA vaccination guidelines, common dog/cat diseases, toxic foods, parasite prevention, dental care, feeding basics — sources cited in each file). Switched compose volume from sample-docs to wiki-docs; sample-docs retained as test fixture.
**Context**: Post-workflow enhancement

---

## Post-Workflow - Skin/Grooming Docs, MCP Client Connection, Facilities SQLite
**Timestamp**: 2026-07-07T17:00:00Z
**User Input**: (sequence) "강아지 피부 관리나 미용과 관련된 논문이나 자료도 검색해서 추가해줘" / "공공 데이터나 동물 병원 약국 등에 대한 정보를 외부에서 가져올수 없을까 ? 방법 알아봐줘" / "이런 데이터들은 정형 데이터 일것 같아요 이런 데이터는 별도 sqlite와 같은 db에 저장하는건 어떻게 생각해 ?" / "현재까지 구현된 것으로 먼저 docker로 local에 실행부터 해줘" / "현재 pc에 claude pc에 mcp 연결해줄래 >" / "공공 데이터에 어떤 데이터를 csv로 줘야 하나요 ?" / "datas 폴더 아래 csv파일 두었습니다."
**AI Response**: (1) Added wiki-docs/grooming/{skin-care,grooming-basics}.md with ICADA/AAHA/PMC citations. (2) Researched Korean public data sources (data.go.kr, LOCALDATA, animal.go.kr APIs). (3) Agreed SQLite for structured facility data. (4) Rebuilt/started Docker service on :8800, smoke-tested. (5) Connected MCP to Claude Code (user scope, HTTP, ✔ Connected) and Claude Desktop (mcp-remote bridge in claude_desktop_config.json). (6) Guided CSV selection. (7) CSVs located at ~/workspace/gordian-coder/datas, copied to petmed/datas/ (동물병원 10,578 / 동물약국 20,560 / 동물미용업 15,952 rows, cp949). Implemented facilities.py (import_csvs + FacilityStore + mcp-wiki-import CLI), find_facility MCP tool, 8 tests (42 total pass). Imported 47,090 rows to facilities.db, mounted into compose with WIKI_FACILITIES_DB, rebuilt container, verified find_facility E2E (강남구 동물병원, 부산 약국, no-match). datas/ and facilities.db excluded from git.
**Context**: Post-workflow enhancement

---

## Post-Workflow - Symptom Triage Guides
**Timestamp**: 2026-07-08T10:30:00Z
**User Input**: "그럼 추가적으로 동물의 증상으로 어떤 병일 가능성과 어떤 병원을 가도록 가이드 할수 있을까 ?" → "진행해주세요"
**AI Response**: Created wiki-docs/symptoms/ with 8 triage documents (triage-guide index + vomiting-diarrhea, urinary-problems, breathing-difficulty, seizures, limping, itching, appetite-loss) using 🔴/🟡/🟢 urgency levels, cross-links to disease/prevention docs, medical disclaimers, and cited sources (BluePearl, VCA, Vets Now, AAHA). Enhanced search/find_facility tool docstrings (symptom workflow + name="24시" emergency hospital tip). 42 tests pass, Docker rebuilt, verified E2E: symptom queries rank triage docs first, 역삼동 24시 hospital lookup works.
**Context**: Post-workflow enhancement

---

## Post-Workflow - BM25 Search Engine
**Timestamp**: 2026-07-07T15:55:00Z
**User Input**: "서치에 대한 부분에 bm25 알고리즘 도입할수 없나요? 추후 시멘틱 검색 즉 임베딩 정보 유사도랑 하이브리드로 관리하고 싶어요"
**AI Response**: Implemented BM25SearchEngine (character-bigram tokenization for Korean partial matching, no new dependency) as SearchEngine Protocol implementation; now default engine. Keyword AND engine retained via --engine keyword / WIKI_SEARCH_ENGINE. SearchResult gained score field. Added 5 example tests + P8 property test (35/35 pass; e2e no-match query updated for bigram recall). Rebuilt Docker image and verified BM25 ranking over wiki-docs on port 8800. Hybrid (embedding similarity + BM25 score fusion) remains the documented extension point. requirements.md Change Log updated.
**Context**: Post-workflow enhancement

---
