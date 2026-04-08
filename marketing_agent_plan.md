# 마케팅 전용 멀티에이전트 & 오케스트레이터 구축 계획

> 작성일: 2026-04-08  
> 목표: 블로그 자동 업로드 기능을 갖춘 마케팅 전용 멀티에이전트 시스템 설계 및 구현 로드맵

---

## 목차

1. [핵심 개념 설명](#1-핵심-개념-설명)
2. [시스템 아키텍처 개요](#2-시스템-아키텍처-개요)
3. [블로그 주제 선정](#3-블로그-주제-선정)
4. [구현 계획 (단계별 로드맵)](#4-구현-계획-단계별-로드맵)
5. [기술 스택 상세](#5-기술-스택-상세)
6. [디렉토리 구조 설계](#6-디렉토리-구조-설계)
7. [리스크 및 고려사항](#7-리스크-및-고려사항)

---

## 1. 핵심 개념 설명

### 1.1 하네스 엔지니어링 (Harness Engineering)

**정의:** AI 에이전트가 실제 작업을 수행할 수 있도록 외부 도구(Tool)와 실행 환경(Runtime)을 연결하는 "실행 프레임"이다.

```
┌───────────────────────────────────────────┐
│              Harness Layer                │
│                                           │
│  ┌──────────┐    ┌──────────────────────┐ │
│  │  Tool    │    │   Execution Runtime  │ │
│  │ Registry │───▶│  (Docker / Subprocess│ │
│  └──────────┘    │   / API Sandbox)     │ │
│                  └──────────────────────┘ │
│                                           │
│  ┌──────────────────────────────────────┐ │
│  │  Permission & Safety Controls        │ │
│  └──────────────────────────────────────┘ │
└───────────────────────────────────────────┘
```

**역할:**
- 에이전트가 호출할 수 있는 **도구 목록(tool schema)** 을 정의
- 도구 실행 결과를 LLM이 이해할 수 있는 형식으로 **반환**
- 실행 권한(파일 읽기/쓰기, 웹 접근, API 호출 등)을 **샌드박스** 수준에서 제어
- Claude Code 자체가 하네스의 좋은 예: `Read`, `Write`, `Bash`, `WebFetch` 등이 모두 하네스 도구

**마케팅 에이전트에서의 역할:**
- 블로그 플랫폼 API (Tistory, Velog, Notion 등)를 도구로 등록
- 이미지 생성 API, SEO 분석 도구를 하네스에 연결
- 각 에이전트가 안전하게 외부 서비스를 호출하도록 제어

---

### 1.2 LangChain 기반 에이전트

**정의:** Python 라이브러리 LangChain은 LLM을 중심으로 도구 호출, 메모리, 체인(Chain), 에이전트를 추상화한 프레임워크다.

**핵심 컴포넌트:**

| 컴포넌트 | 역할 | 마케팅 에이전트 예시 |
|---------|------|-----------------|
| `ChatModel` | Claude/GPT 같은 LLM 래퍼 | 글쓰기, 분석 수행 |
| `Tool` | 에이전트가 호출할 수 있는 함수 | 블로그 포스팅 API |
| `AgentExecutor` | ReAct 루프로 도구 선택 및 실행 | 리서치 에이전트 실행 |
| `Memory` | 대화 이력 및 컨텍스트 관리 | 이전 포스팅 기록 유지 |
| `Chain` | 여러 작업을 파이프라인으로 연결 | 리서치→작성→업로드 |

**ReAct 패턴 (LangChain 에이전트의 동작 원리):**

```
Thought:  무엇을 해야 할지 추론
Action:   어떤 도구를 쓸지 결정
Action Input: 도구에 전달할 입력
Observation: 도구 실행 결과
... (반복)
Final Answer: 최종 결과 반환
```

---

### 1.3 멀티에이전트 (Multi-Agent)

**정의:** 하나의 복잡한 작업을 여러 개의 전문화된 에이전트로 분산하여 처리하는 패턴.

```
                    ┌──────────────────┐
                    │  Orchestrator    │
                    │  (Master Agent)  │
                    └────────┬─────────┘
                             │ 작업 분배
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
    ┌──────────────┐ ┌─────────────┐ ┌──────────────┐
    │  Research    │ │   Writer    │ │  Publisher   │
    │   Agent      │ │   Agent     │ │   Agent      │
    │              │ │             │ │              │
    │ - 주제 조사  │ │ - 초안 작성 │ │ - SEO 최적화 │
    │ - 트렌드 분석│ │ - 구조화    │ │ - 블로그 업로드│
    └──────────────┘ └─────────────┘ └──────────────┘
```

**멀티에이전트가 필요한 이유:**
- 단일 에이전트는 컨텍스트 길이 제한에 걸림
- 전문화된 에이전트가 각 단계에서 더 높은 품질 보장
- 병렬 실행으로 속도 향상 가능
- 각 에이전트를 독립적으로 테스트/개선 가능

**에이전트 통신 패턴:**

```python
# 에이전트 간 메시지 전달 예시
{
  "from": "research_agent",
  "to": "writer_agent",
  "payload": {
    "topic": "IT 뉴스 파이프라인 구축기",
    "key_points": ["RSS 수집", "AI 분석", "편향 감지"],
    "target_length": 2000,
    "tone": "기술 블로그"
  }
}
```

---

### 1.4 오케스트레이터 (Orchestrator)

**정의:** 여러 에이전트의 실행 순서, 조건 분기, 오류 처리, 결과 통합을 총괄하는 **마스터 에이전트 또는 제어 레이어**.

**오케스트레이터의 핵심 책임:**

```
┌─────────────────────────────────────────────┐
│              Orchestrator                   │
│                                             │
│  1. Task Decomposition  작업 분해           │
│  2. Agent Routing       에이전트 배정       │
│  3. State Management    상태 추적           │
│  4. Error Recovery      실패 시 재시도      │
│  5. Result Aggregation  결과 취합           │
│  6. Quality Gate        품질 검증           │
└─────────────────────────────────────────────┘
```

**LangGraph를 이용한 오케스트레이터 패턴:**

LangGraph는 LangChain의 확장으로, 에이전트 간 흐름을 **방향 그래프(DAG)** 로 정의한다.

```python
from langgraph.graph import StateGraph, END

# 상태 정의
class BlogState(TypedDict):
    topic: str
    research_result: str
    draft: str
    seo_score: int
    published_url: str

# 그래프 구성
workflow = StateGraph(BlogState)
workflow.add_node("research", research_agent)
workflow.add_node("write", writer_agent)
workflow.add_node("seo_check", seo_agent)
workflow.add_node("publish", publisher_agent)

# 흐름 정의
workflow.add_edge("research", "write")
workflow.add_conditional_edges(
    "seo_check",
    lambda state: "publish" if state["seo_score"] > 70 else "write"
)
```

---

## 2. 시스템 아키텍처 개요

### 전체 플로우

```
[트리거]
  │
  │ (스케줄 / 수동 실행)
  ▼
┌─────────────────────────────────────────────────────┐
│                  ORCHESTRATOR                       │
│                                                     │
│  입력: 주제 키워드 또는 GitHub 레포지토리 URL        │
│  출력: 발행된 블로그 포스트 URL                     │
└────────────┬────────────────────────────────────────┘
             │
    ┌────────▼────────┐
    │  Research Agent  │  ← GitHub README, 코드 분석
    │                  │    트렌드 키워드 수집
    └────────┬────────┘
             │ research_result
    ┌────────▼────────┐
    │  Writer Agent    │  ← 블로그 초안 작성
    │                  │    마크다운 포맷팅
    └────────┬────────┘
             │ draft
    ┌────────▼────────┐
    │  SEO Agent       │  ← 제목/소제목 최적화
    │                  │    키워드 밀도 체크
    └────────┬────────┘
             │ optimized_draft
    ┌────────▼────────┐
    │  Publisher Agent │  ← 블로그 플랫폼 API 호출
    │                  │    이미지 삽입, 태그 설정
    └────────┬────────┘
             │
         [발행 완료]
```

---

## 3. 블로그 주제 선정

### 후보 프로젝트 비교

| 항목 | it-news-pipeline | my_wallet_pattern_v2 |
|------|-----------------|---------------------|
| 주요 기술 | Python, OpenAI, Supabase, RSS | Next.js, FastAPI, SQLite, OpenAI |
| 프로젝트 성격 | **자동화 파이프라인** | 풀스택 SaaS 앱 |
| 기술 블로그 적합도 | ★★★★★ | ★★★☆☆ |
| 자동화 스토리텔링 | 매우 풍부 | 부분적 |
| 설명 난이도 | 중간 | 높음 |
| 연계성 (이번 과제와) | **직접 연결** | 간접 연결 |

### 추천: **it-news-pipeline** (강력 추천)

**이유:**
1. 이 프로젝트 자체가 "자동화 파이프라인"이므로 마케팅 에이전트와 **컨셉이 동일**
2. RSS → AI 분석 → 시각화의 3단계 구조가 멀티에이전트 워크플로우와 **구조적으로 일치**
3. 기술 블로그 독자(개발자)에게 **실용적이고 흥미로운 주제**
4. 에이전트가 GitHub README와 코드를 분석해 자동으로 포스팅하기에 적합한 문서화 수준

### 추가 제안 주제 (자동화에 더 최적화)

만약 기존 프로젝트보다 더 임팩트 있는 블로그 주제를 원한다면:

| 주제 | 설명 | 예상 반응 |
|------|------|---------|
| "이 멀티에이전트 시스템 자체 구축기" | 오늘 만드는 시스템을 포스팅 | 매우 높음 |
| "LangChain으로 블로그 자동화한 방법" | How-to 가이드 형식 | 높음 |
| "AI가 내 사이드프로젝트 소개 글 써줬다" | it-news-pipeline 기반 | 중간~높음 |

---

## 4. 구현 계획 (단계별 로드맵)

### Phase 1: 기반 환경 구성 (Week 1)

**목표:** 개발 환경, 도구 등록, 기본 에이전트 1개 동작 확인

- [ ] Python 가상환경 구성 및 의존성 설치
  - `langchain`, `langgraph`, `langchain-anthropic`, `python-dotenv`
- [ ] Claude API 키 설정 및 기본 호출 테스트
- [ ] 하네스 도구 설계
  - `fetch_github_readme(repo_url)` — GitHub API로 README 읽기
  - `search_web(query)` — 트렌드 키워드 검색
  - `post_to_blog(title, content, tags)` — 블로그 API 연동
- [ ] Research Agent 단독 동작 테스트

**산출물:** `tools/` 디렉토리, `agents/research_agent.py`

---

### Phase 2: 개별 에이전트 구현 (Week 2)

**목표:** 4개 에이전트 각각 독립 동작

#### Research Agent
```python
# 입력: GitHub repo URL + 추가 검색 키워드
# 출력: 구조화된 리서치 결과 (JSON)
tools = [fetch_github_readme, search_web, analyze_code_structure]
```

#### Writer Agent
```python
# 입력: 리서치 결과
# 출력: 마크다운 블로그 초안
tools = [format_markdown, check_korean_grammar]
prompt = "기술 블로그 작가로서 개발자 독자를 위한 포스팅을 작성하라..."
```

#### SEO Agent
```python
# 입력: 블로그 초안
# 출력: SEO 점수 + 개선된 초안
tools = [analyze_keywords, suggest_title, check_readability]
```

#### Publisher Agent
```python
# 입력: SEO 최적화된 초안
# 출력: 발행된 포스트 URL
tools = [post_to_tistory, post_to_velog, upload_image]
```

---

### Phase 3: 오케스트레이터 + LangGraph 연결 (Week 3)

**목표:** LangGraph로 에이전트 흐름 연결 및 상태 관리

```python
# 오케스트레이터 핵심 로직
class MarketingOrchestrator:
    def run(self, input: dict) -> dict:
        # 1. 작업 분해
        subtasks = self.decompose(input["topic"])

        # 2. Research → Write → SEO → Publish 순차 실행
        state = self.graph.invoke({"topic": input["topic"]})

        # 3. 품질 게이트: SEO 점수 70 미만이면 재작성
        if state["seo_score"] < 70:
            state = self.graph.invoke(state, entry="write")

        return state
```

**산출물:** `orchestrator/workflow.py`, LangGraph 상태 다이어그램

---

### Phase 4: 자동화 트리거 및 스케줄링 (Week 4)

**목표:** 완전 자동화 (스케줄 실행, 결과 알림)

- [ ] GitHub Actions 또는 cron 기반 스케줄 설정
- [ ] Slack/Discord 알림 연동 (발행 성공/실패 알림)
- [ ] 로깅 및 실행 이력 DB 저장
- [ ] 파라미터화: 주제, 길이, 톤(tone) 를 설정 파일로 관리

---

## 5. 기술 스택 상세

```
┌─────────────────────────────────────────────────────────┐
│                    기술 스택                            │
│                                                         │
│  LLM           Claude claude-sonnet-4-6 (Anthropic)     │
│  Framework     LangChain + LangGraph                    │
│  Language      Python 3.11+                             │
│  Harness       Custom Tool Registry (함수 래핑)          │
│  Orchestrator  LangGraph StateGraph                     │
│  Blog Target   Tistory API / Velog GraphQL (선택)       │
│  Scheduler     APScheduler 또는 GitHub Actions          │
│  Storage       SQLite (실행 이력) / Supabase (확장 시)  │
│  Env           python-dotenv, pydantic-settings         │
└─────────────────────────────────────────────────────────┘
```

### 주요 패키지 버전

```toml
# pyproject.toml
[dependencies]
langchain = ">=0.3"
langchain-anthropic = ">=0.3"
langgraph = ">=0.2"
langchain-community = ">=0.3"
python-dotenv = ">=1.0"
pydantic = ">=2.0"
httpx = ">=0.27"
```

---

## 6. 디렉토리 구조 설계

```
multi_agent_orchestration/
│
├── agents/
│   ├── __init__.py
│   ├── research_agent.py      # GitHub + 웹 리서치
│   ├── writer_agent.py        # 블로그 초안 작성
│   ├── seo_agent.py           # SEO 최적화
│   └── publisher_agent.py     # 블로그 발행
│
├── tools/
│   ├── __init__.py
│   ├── github_tools.py        # GitHub API 래퍼
│   ├── search_tools.py        # 웹 검색 도구
│   ├── blog_tools.py          # 블로그 플랫폼 API
│   └── seo_tools.py           # SEO 분석 도구
│
├── orchestrator/
│   ├── __init__.py
│   ├── workflow.py            # LangGraph 상태 그래프
│   ├── state.py               # 공유 상태 스키마 (TypedDict)
│   └── quality_gates.py      # 품질 검증 로직
│
├── config/
│   ├── settings.py            # 환경변수, 설정값
│   └── prompts.py             # 각 에이전트 시스템 프롬프트
│
├── tests/
│   ├── test_research.py
│   ├── test_writer.py
│   └── test_orchestrator.py
│
├── .env.example
├── main.py                    # 진입점
└── marketing_agent_plan.md   # 이 파일
```

---

## 7. 리스크 및 고려사항

### 기술적 리스크

| 리스크 | 영향도 | 대응 방안 |
|--------|--------|---------|
| 블로그 플랫폼 API 제한 (Tistory 인증) | 높음 | Velog 또는 Notion을 1차 타겟으로 변경 |
| LLM 응답 품질 불일치 | 중간 | 프롬프트 버전 관리 + few-shot 예시 추가 |
| 토큰 비용 증가 | 중간 | claude-haiku-4-5 를 리서치 단계에 사용 |
| GitHub API Rate Limit | 낮음 | 캐싱 레이어 추가 |

### 설계 원칙

1. **각 에이전트는 독립적으로 테스트 가능해야 한다** — 단위 테스트 필수
2. **상태(State)는 오케스트레이터가 소유한다** — 에이전트 간 직접 통신 금지
3. **도구(Tool)는 순수 함수로 작성한다** — 부작용 최소화
4. **재시도 로직은 오케스트레이터에서 처리한다** — 에이전트 내부 재시도 금지

### 학습 포인트 요약

```
멘토님 숙제 핵심 체크리스트
─────────────────────────────
✅ 하네스 엔지니어링  → tools/ 디렉토리 설계
✅ LangChain 기반    → AgentExecutor + Tool 등록
✅ 멀티에이전트      → 4개 전문 에이전트 분리
✅ 오케스트레이터    → LangGraph StateGraph로 흐름 제어
✅ 자동화 블로그 업로드 → Publisher Agent + 스케줄러
```

---

*이 문서는 구현 전 설계 단계 문서입니다. 실제 구현 시 각 Phase를 순서대로 진행하고, 완료 시 체크박스를 업데이트하세요.*
