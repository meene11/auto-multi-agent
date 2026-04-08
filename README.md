# auto-multi-agent

> LangChain + LangGraph 기반 멀티에이전트 오케스트레이터  
> GitHub 레포 분석부터 티스토리 · 네이버 블로그 자동 발행까지 자동화하는 마케팅 에이전트 시스템

---

## 목차

1. [프로젝트 소개](#프로젝트-소개)
2. [1차 블로그 포스팅 소재](#1차-블로그-포스팅-소재)
3. [시스템 아키텍처](#시스템-아키텍처)
4. [에이전트 구성](#에이전트-구성)
5. [기술 스택](#기술-스택)
6. [디렉토리 구조](#디렉토리-구조)
7. [설치 및 실행](#설치-및-실행)
8. [블로그 플랫폼 연동](#블로그-플랫폼-연동)
9. [GitHub Actions 자동화](#github-actions-자동화)
10. [구현 로드맵](#구현-로드맵)
11. [설계 원칙](#설계-원칙)

---

## 프로젝트 소개

`auto-multi-agent`는 사이드 프로젝트를 기술 블로그 포스팅으로 자동 변환하는 **마케팅 전용 멀티에이전트 시스템**이다.

GitHub 레포지토리 URL을 입력하면:

1. **Research Agent** 가 README, 코드 구조, 핵심 기술을 자동 분석
2. **Writer Agent** 가 개발자 독자를 위한 기술 블로그 초안을 작성
3. **SEO Agent** 가 제목, 키워드, 가독성을 최적화
4. **Publisher Agent** 가 티스토리와 네이버 블로그에 동시 발행

모든 흐름은 **LangGraph 오케스트레이터**가 상태를 관리하며, SEO 점수가 기준 미달이면 자동으로 재작성 루프를 실행한다.

```
GitHub 레포 URL 입력
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR                           │
│                    (LangGraph StateGraph)                   │
└──────┬──────────────┬──────────────┬───────────────┬────────┘
       ▼              ▼              ▼               ▼
┌────────────┐ ┌────────────┐ ┌───────────┐ ┌──────────────────┐
│  Research  │ │   Writer   │ │    SEO    │ │    Publisher     │
│   Agent    │ │   Agent    │ │   Agent   │ │     Agent        │
│            │ │            │ │           │ │                  │
│ README 분석│ │ 블로그 초안│ │ 제목 최적화│ │ 티스토리 발행   │
│ 코드 구조  │ │ 마크다운   │ │ 키워드 밀도│ │ 네이버 블로그   │
│ 트렌드 수집│ │ 포맷팅     │ │ 가독성 점수│ │ 발행           │
└────────────┘ └────────────┘ └───────────┘ └──────────────────┘
```

---

## 1차 블로그 포스팅 소재

### it-news-pipeline

> **레포지토리:** https://github.com/meene11/it-news-pipeline  
> **배포 주소:** https://it-news-pipeline.vercel.app

RSS 수집 + AI 분석 뉴스 파이프라인 프로젝트로, 이 시스템의 **1차 블로그 포스팅 소재**로 활용된다.

#### 프로젝트 개요

ZDNet Korea, Bloter, ETNews 등 주요 IT 매체의 뉴스를 자동으로 수집하고, GPT-4o-mini 기반 AI로 감성 분석 및 트렌드를 시각화하는 파이프라인이다.

#### 3단계 구조

| 버전 | 역할 | 핵심 기능 |
|------|------|---------|
| **v1** | 데이터 수집 | RSS 파싱 → Supabase 저장 → 대시보드 시각화 |
| **v2** | AI 분석 | GPT-4o-mini 감성 분석 (긍정/부정/중립) + 신뢰도 점수 |
| **v3** | 인사이트 | 키워드 트렌드 추출, 매체별 편향 분석, Chart.js 시각화 |

#### 기술 스택 (it-news-pipeline)

- **Backend:** Python 3.10+, OpenAI API (gpt-4o-mini), Supabase REST API
- **Frontend:** Vanilla JS, Chart.js, Supabase JS SDK
- **Infra:** GitHub Actions (매일 자동 크롤링), Vercel (정적 호스팅)

#### 자동화 방식과의 연계성

it-news-pipeline 자체가 "자동화 파이프라인" 구조를 가지고 있어, `auto-multi-agent`의 **멀티에이전트 워크플로우와 구조적으로 일치**한다. Research Agent가 이 레포의 README, 코드, 배포 사이트를 분석해 포스팅을 자동 생성하는 데 최적의 소재다.

---

## 시스템 아키텍처

### 전체 워크플로우

```
[트리거: 수동 실행 또는 GitHub Actions 스케줄]
        │
        ▼
  입력: GitHub 레포 URL
        │
        ▼
┌──────────────────────────────────────────────────────┐
│                   ORCHESTRATOR                       │
│                                                      │
│  BlogState:                                          │
│    topic           → 입력 주제 / GitHub URL          │
│    research_result → 리서치 결과 (JSON)              │
│    draft           → 블로그 초안 (Markdown)          │
│    seo_score       → SEO 점수 (0~100)                │
│    published_urls  → { tistory: "...", naver: "..." }│
└──────────────────────────────────────────────────────┘
        │
        ├──▶ research ──▶ write ──▶ seo_check
        │                               │
        │              seo_score >= 70 ─┼──▶ publish (티스토리 + 네이버)
        │              seo_score < 70  ─┘──▶ write (재작성 루프)
        │
        ▼
  출력: 발행된 포스트 URL x2
```

### LangGraph 상태 그래프 (코드 예시)

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class BlogState(TypedDict):
    topic: str
    research_result: str
    draft: str
    seo_score: int
    published_urls: dict

workflow = StateGraph(BlogState)
workflow.add_node("research", research_agent)
workflow.add_node("write", writer_agent)
workflow.add_node("seo_check", seo_agent)
workflow.add_node("publish", publisher_agent)

workflow.set_entry_point("research")
workflow.add_edge("research", "write")
workflow.add_edge("write", "seo_check")
workflow.add_conditional_edges(
    "seo_check",
    lambda state: "publish" if state["seo_score"] >= 70 else "write"
)
workflow.add_edge("publish", END)
```

---

## 에이전트 구성

### Research Agent

GitHub 레포지토리를 분석해 블로그 포스팅에 필요한 정보를 수집한다.

```
입력: GitHub repo URL
출력: 구조화된 리서치 결과 (JSON)

사용 도구:
  - fetch_github_readme(repo_url)   → README 전문 수집
  - analyze_code_structure(repo_url) → 디렉토리 구조 분석
  - search_web(query)               → 관련 트렌드 키워드 수집
```

### Writer Agent

리서치 결과를 바탕으로 개발자 독자를 위한 기술 블로그 초안을 작성한다.

```
입력: 리서치 결과 (JSON)
출력: 마크다운 블로그 초안

시스템 프롬프트:
  "당신은 10년 경력의 기술 블로그 작가입니다.
   개발자 독자를 위한 실용적이고 읽기 쉬운 포스팅을 작성합니다.
   프로젝트의 문제 정의, 해결 방법, 핵심 코드, 회고 순서로 구성합니다."
```

### SEO Agent

블로그 초안의 SEO 점수를 분석하고 최적화한다.

```
입력: 블로그 초안
출력: SEO 점수 (0~100) + 개선된 초안

검사 항목:
  - 제목 키워드 포함 여부
  - 소제목(H2/H3) 구조
  - 핵심 키워드 밀도 (2~5%)
  - 본문 길이 (1500자 이상 권장)
  - 내부 링크 및 태그 설정
```

### Publisher Agent

SEO 최적화된 초안을 티스토리와 네이버 블로그에 동시 발행한다.

```
입력: SEO 최적화된 초안
출력: 발행된 포스트 URL x2 (티스토리, 네이버)

사용 도구:
  - post_to_tistory(title, content, tags)
  - post_to_naver_blog(title, content, category)
  - upload_image(image_path) → 썸네일 이미지 업로드
```

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| LLM | Claude claude-sonnet-4-6 (Anthropic) |
| 에이전트 프레임워크 | LangChain >= 0.3 |
| 오케스트레이터 | LangGraph >= 0.2 |
| 언어 | Python 3.11+ |
| 블로그 플랫폼 | 티스토리 REST API, 네이버 블로그 Open API |
| 스케줄러 | GitHub Actions |
| 환경 관리 | python-dotenv, pydantic-settings |
| HTTP 클라이언트 | httpx |

### 주요 패키지

```toml
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

## 디렉토리 구조

```
auto-multi-agent/
│
├── agents/
│   ├── __init__.py
│   ├── research_agent.py       # GitHub + 웹 리서치
│   ├── writer_agent.py         # 블로그 초안 작성
│   ├── seo_agent.py            # SEO 최적화
│   └── publisher_agent.py      # 티스토리 + 네이버 블로그 발행
│
├── tools/
│   ├── __init__.py
│   ├── github_tools.py         # GitHub API 래퍼
│   ├── search_tools.py         # 웹 검색 도구
│   ├── seo_tools.py            # SEO 분석 도구
│   └── blog_tools.py           # 티스토리 + 네이버 블로그 API
│
├── orchestrator/
│   ├── __init__.py
│   ├── workflow.py             # LangGraph StateGraph 정의
│   ├── state.py                # 공유 상태 스키마 (TypedDict)
│   └── quality_gates.py        # SEO 품질 검증 로직
│
├── config/
│   ├── settings.py             # 환경변수 및 설정값
│   └── prompts.py              # 에이전트별 시스템 프롬프트
│
├── tests/
│   ├── test_research.py
│   ├── test_writer.py
│   ├── test_seo.py
│   └── test_orchestrator.py
│
├── .github/
│   └── workflows/
│       └── auto_publish.yml    # GitHub Actions 스케줄 자동화
│
├── .env.example
├── requirements.txt
├── main.py                     # 진입점
├── marketing_agent_plan.md     # 설계 문서
└── README.md
```

---

## 설치 및 실행

### 1. 레포 클론

```bash
git clone https://github.com/meene11/auto-multi-agent.git
cd auto-multi-agent
```

### 2. 가상환경 구성

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 환경변수 설정

```bash
cp .env.example .env
```

`.env` 파일 편집:

```env
# Anthropic
ANTHROPIC_API_KEY=your_anthropic_api_key

# GitHub (README 분석용)
GITHUB_TOKEN=your_github_personal_access_token

# 티스토리
TISTORY_ACCESS_TOKEN=your_tistory_access_token
TISTORY_BLOG_NAME=your_tistory_blog_name

# 네이버 블로그
NAVER_CLIENT_ID=your_naver_client_id
NAVER_CLIENT_SECRET=your_naver_client_secret
NAVER_ACCESS_TOKEN=your_naver_access_token

# 설정
TARGET_REPO_URL=https://github.com/meene11/it-news-pipeline
SEO_SCORE_THRESHOLD=70
```

### 4. 실행

```bash
# 기본 실행 (it-news-pipeline 기준)
python main.py

# 특정 레포 지정
python main.py --repo https://github.com/meene11/it-news-pipeline

# 특정 플랫폼만 발행
python main.py --platform tistory
python main.py --platform naver
python main.py --platform all   # 기본값
```

---

## 블로그 플랫폼 연동

### 티스토리 API

OAuth 2.0 기반 REST API를 사용한다.

1. [티스토리 앱 등록](https://www.tistory.com/guide/api/manage/register) 에서 앱 생성
2. `App ID`, `Secret Key` 발급 후 Access Token 획득
3. `.env`에 `TISTORY_ACCESS_TOKEN`, `TISTORY_BLOG_NAME` 등록

```
POST https://www.tistory.com/apis/post/write
  - access_token
  - blogName
  - title
  - content (HTML)
  - tag
  - visibility (3: 발행)
```

### 네이버 블로그 Open API

네이버 로그인 API (OAuth 2.0) 기반으로 포스팅한다.

1. [네이버 개발자 센터](https://developers.naver.com/apps/#/register) 에서 앱 등록
2. **블로그 Write** 권한 활성화
3. `Client ID`, `Client Secret` 발급 후 `.env`에 등록

```
POST https://openapi.naver.com/blog/writePost.json
  - title
  - contents (HTML)
  - categoryNo
```

> Access Token 유효 시간이 1시간이므로 Refresh Token을 이용한 자동 갱신 로직이 포함되어 있다.

---

## GitHub Actions 자동화

`.github/workflows/auto_publish.yml`:

```yaml
name: Auto Blog Publish

on:
  schedule:
    - cron: '0 0 * * 1'   # 매주 월요일 오전 9시 KST (UTC 00:00)
  workflow_dispatch:        # 수동 실행 가능

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run multi-agent pipeline
        run: python main.py
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          TISTORY_ACCESS_TOKEN: ${{ secrets.TISTORY_ACCESS_TOKEN }}
          TISTORY_BLOG_NAME: ${{ secrets.TISTORY_BLOG_NAME }}
          NAVER_ACCESS_TOKEN: ${{ secrets.NAVER_ACCESS_TOKEN }}
```

---

## 구현 로드맵

| Phase | 내용 | 상태 |
|-------|------|------|
| **Phase 1** | 환경 구성, Tool 설계, Research Agent 단독 동작 확인 | 🔲 예정 |
| **Phase 2** | Writer / SEO / Publisher Agent 각각 독립 구현 | 🔲 예정 |
| **Phase 3** | LangGraph 오케스트레이터 연결 및 상태 관리 | 🔲 예정 |
| **Phase 4** | GitHub Actions 스케줄 자동화 + 알림 연동 | 🔲 예정 |

---

## 설계 원칙

1. **각 에이전트는 독립적으로 테스트 가능** — 단위 테스트 필수, 오케스트레이터 없이도 단독 실행 가능
2. **상태(State)는 오케스트레이터가 소유** — 에이전트 간 직접 통신 금지, 모든 데이터는 `BlogState`를 통해 전달
3. **도구(Tool)는 순수 함수로 작성** — 부작용 최소화, 동일 입력에 동일 출력 보장
4. **재시도 로직은 오케스트레이터에서 처리** — 에이전트 내부 재시도 금지, 품질 게이트는 LangGraph 조건 엣지로 구현

---

## 관련 프로젝트

| 프로젝트 | 설명 | 링크 |
|---------|------|------|
| it-news-pipeline | RSS 기반 IT 뉴스 수집 + AI 분석 파이프라인 (1차 포스팅 소재) | [GitHub](https://github.com/meene11/it-news-pipeline) · [배포](https://it-news-pipeline.vercel.app) |
| my_wallet_pattern_v2 | 지출 패턴 분석 풀스택 앱 | [GitHub](https://github.com/meene11/my_wallet_pattern_v2) |  [배포](https://my-wallet-pattern-v2.vercel.app) |

---

## 라이선스

MIT License
