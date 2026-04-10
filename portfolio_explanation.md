# itnews-multi-agent 프로젝트 상세 설명서
> 비전공자를 위한 쉬운 설명 | 작성일: 2026-04-08

---

## 목차
1. [이 프로젝트가 뭔가요?](#1-이-프로젝트가-뭔가요)
2. [왜 만들었나요?](#2-왜-만들었나요)
3. [핵심 개념 설명](#3-핵심-개념-설명)
4. [전체 워크플로우](#4-전체-워크플로우)
5. [각 에이전트 상세 설명](#5-각-에이전트-상세-설명)
6. [오케스트레이터란?](#6-오케스트레이터란)
7. [사용한 기술 스택 설명](#7-사용한-기술-스택-설명)
8. [실제 실행 결과](#8-실제-실행-결과)
9. [폴더 구조 설명](#9-폴더-구조-설명)
10. [배운 점 & 포트폴리오 포인트](#10-배운-점--포트폴리오-포인트)

---

## 1. 이 프로젝트가 뭔가요?

**한 줄 요약:** `python main.py` 명령어 하나로 IT 뉴스를 자동으로 수집해서 블로그에 글을 올려주는 AI 자동화 시스템입니다.

### 비유로 이해하기
> 마치 **기자 팀**이 있는 것처럼 생각하면 됩니다.
> - 취재기자(Research Agent): 정보를 수집합니다
> - 작성기자(Writer Agent): 기사를 씁니다
> - 편집장(SEO Agent): 기사를 검토하고 최적화합니다
> - 발행팀(Publisher Agent): 여러 매체에 동시에 올립니다
> - 편집국장(Orchestrator): 이 모든 과정을 총괄합니다

이 모든 역할을 AI가 자동으로 합니다.

---

## 2. 왜 만들었나요?

**멘토님의 숙제:** 멀티에이전트와 오케스트레이터를 이용한 자동화 시스템 만들기

**해결하려는 문제:**
- 블로그 글을 쓰는 건 시간이 많이 걸림
- IT 뉴스는 매일 업데이트되는데 일일이 정리하기 어려움
- 여러 블로그 플랫폼에 동시에 올리는 건 더 번거로움

**해결책:** AI 에이전트들이 자동으로 뉴스를 수집 → 글 작성 → 최적화 → 발행

---

## 3. 핵심 개념 설명

### 3.1 AI 에이전트(Agent)란?
> **에이전트 = 스스로 판단하고 행동하는 AI**

일반 AI(ChatGPT 등)는 질문하면 답변만 해줍니다.
에이전트는 스스로 도구를 선택해서 사용하고, 목표를 달성할 때까지 반복적으로 행동합니다.

```
일반 AI: "이 글 좀 요약해줘" → 요약 결과 출력
에이전트: "it-news-pipeline 프로젝트 분석해서 블로그 글 써줘"
         → 스스로 GitHub에서 README 읽음
         → 스스로 파일 구조 분석
         → 스스로 웹 검색으로 트렌드 파악
         → 종합해서 블로그 글 작성
```

### 3.2 멀티에이전트(Multi-Agent)란?
> **멀티에이전트 = 여러 전문가 AI가 협력하는 시스템**

하나의 AI에게 모든 걸 시키면:
- 한 번에 처리할 수 있는 양(컨텍스트)이 부족
- 모든 분야를 잘하기 어려움

여러 전문 AI로 나누면:
- 각자 자기 분야에서 최고의 성능 발휘
- 병렬로 처리 가능해서 빠름
- 독립적으로 테스트/개선 가능

### 3.3 오케스트레이터(Orchestrator)란?
> **오케스트레이터 = 여러 에이전트를 지휘하는 총감독**

오케스트라에서 지휘자가 각 악기 연주자에게 언제 무엇을 연주할지 지시하듯,
오케스트레이터는 각 에이전트에게 언제, 무엇을 할지 지시합니다.

```
오케스트레이터의 역할:
- Research 완료? → Writer한테 넘겨
- SEO 점수 미달? → Writer한테 다시 작성 요청
- 최종 완료? → Publisher한테 발행 명령
```

### 3.4 하네스 엔지니어링(Harness Engineering)이란?
> **하네스 = AI 에이전트가 사용할 수 있는 도구 모음**

에이전트 혼자서는 GitHub에 접근하거나 웹 검색을 할 수 없습니다.
하네스는 에이전트가 사용할 수 있는 도구(Tool)들을 등록하고 관리합니다.

```
이 프로젝트의 하네스 도구들:
- fetch_github_readme()    → GitHub README 읽기
- analyze_code_structure() → 파일 구조 분석
- search_web()             → 웹 검색
- post_to_devto()          → dev.to에 글 발행
- post_to_hashnode()       → Hashnode에 글 발행
```

### 3.5 LangChain이란?
> **LangChain = AI 에이전트를 쉽게 만들 수 있는 Python 라이브러리**

AI 모델(Claude, GPT 등)을 직접 연결하고, 도구를 등록하고, 에이전트를 만드는 복잡한 과정을
LangChain이 단순하게 처리해줍니다.

### 3.6 LangGraph란?
> **LangGraph = 여러 에이전트의 흐름을 그래프로 정의하는 도구**

```
Research → Write → SEO 검사
                      ↓ (점수 미달)
                   다시 Write
                      ↓ (점수 통과)
                   Publish
```
이런 복잡한 흐름(조건 분기, 반복 등)을 코드로 표현할 수 있게 해줍니다.

### 3.7 SEO란?
> **SEO(Search Engine Optimization) = 검색 엔진 최적화**

구글 등 검색엔진에서 내 글이 상위에 노출되도록 최적화하는 것입니다.
- 제목에 핵심 키워드 포함
- 적절한 소제목 구조
- 적절한 글 길이 등

### 3.8 GEO란?
> **GEO(Generative Engine Optimization) = AI 검색 최적화**

ChatGPT, Perplexity 같은 AI 검색 도구가 내 글을 답변 소스로 활용하도록 최적화하는 것입니다. SEO의 AI 버전입니다.
- 첫 문단에 핵심 내용 요약
- 구체적인 수치 포함
- 질문 형태의 소제목

---

## 4. 전체 워크플로우

```
사용자가 명령어 실행
python main.py
        │
        ▼
┌──────────────────────────────────────────┐
│           ORCHESTRATOR (LangGraph)        │
│                                          │
│  1. Research Agent에게 작업 지시         │
│     └→ GitHub/Supabase에서 데이터 수집  │
│                                          │
│  2. Writer Agent에게 작업 지시           │
│     └→ 수집된 데이터로 블로그 초안 작성 │
│                                          │
│  3. SEO Agent에게 작업 지시              │
│     └→ 글 품질 검사 (SEO+GEO 점수화)   │
│                                          │
│  4-A. 점수 70점 이상 → Publisher 실행   │
│  4-B. 점수 70점 미만 → Writer 재작성    │
│       (최대 2회까지 재시도)              │
│                                          │
│  5. Publisher Agent 실행                 │
│     └→ dev.to + Hashnode 동시 발행      │
└──────────────────────────────────────────┘
        │
        ▼
터미널에 발행된 URL 출력
```

---

## 5. 각 에이전트 상세 설명

### 5.1 Research Agent (리서치 에이전트)

**역할:** 정보 수집 전문가

**사용 도구:**
| 도구 | 하는 일 |
|------|---------|
| `fetch_github_readme` | GitHub 레포의 README 파일 전문을 가져옴 |
| `analyze_code_structure` | 레포의 파일/폴더 구조를 분석 |
| `search_web` | DuckDuckGo로 관련 트렌드 키워드 검색 |

**출력 결과 (JSON 형태):**
```json
{
  "project_name": "it-news-pipeline",
  "summary": "RSS 기반 IT 뉴스 수집 및 AI 분석 파이프라인",
  "tech_stack": ["Python", "OpenAI", "Supabase", "Vercel"],
  "key_features": ["RSS 수집", "감성 분석", "트렌드 시각화"],
  "trend_keywords": ["AI 뉴스", "데이터 파이프라인", "자동화"]
}
```

### 5.2 Writer Agent (작성 에이전트)

**역할:** 한국어 기술 블로그 작가

**입력:** Research Agent가 수집한 JSON 데이터
**출력:** 마크다운 형식의 블로그 초안

**블로그 구조:**
```
# 제목

## 들어가며
## 프로젝트 소개
## 핵심 기술 & 아키텍처
## 주요 기능 구현
## 마치며

tags: [태그1, 태그2, 태그3]
```

**특징:** 온도(temperature) 0.7로 설정 → 약간의 창의성을 허용해서 자연스러운 글쓰기

### 5.3 SEO Agent (최적화 에이전트)

**역할:** 블로그 품질 검사관 + 최적화

**검사 항목 10가지:**
```
SEO 체크리스트:
1. 제목에 핵심 키워드 있나?
2. 소제목(H2/H3) 구조가 적절한가?
3. 키워드 밀도 2~5%인가?
4. 글이 1500자 이상인가?
5. 도입부에 핵심 내용 요약 있나?
6. 태그가 4개 이하인가?

GEO 체크리스트:
7. 첫 문단에 핵심 정보 요약 있나?
8. 구체적인 수치/사실 있나?
9. 소제목이 질문 형태인가?
10. 코드가 명확하게 레이블링됐나?
```

**출력 결과:**
```json
{
  "seo_score": 85,
  "issues": ["소제목을 질문 형태로 변경 권장"],
  "optimized_content": "개선된 블로그 전문...",
  "title": "AI로 IT 뉴스 자동 분석하는 방법",
  "tags": ["ai", "pipeline", "automation", "python"]
}
```

### 5.4 Publisher Agent (발행 에이전트)

**역할:** 멀티 플랫폼 동시 발행

**발행 플랫폼:**

| 플랫폼 | API 방식 | 특징 |
|--------|---------|------|
| dev.to | REST API (api-key 인증) | 태그: 영문+숫자만 |
| Hashnode | GraphQL API | 태그: 영문+숫자+하이픈 |

---

## 6. 오케스트레이터란?

### LangGraph StateGraph 방식

오케스트레이터는 **상태(State)** 를 가지고 있습니다.
에이전트들이 작업할 때마다 이 상태를 업데이트합니다.

```python
# 공유 상태 구조
BlogState = {
    "topic": "분석할 레포 URL",
    "research_result": "리서치 결과",
    "draft": "블로그 초안",
    "seo_score": 85,
    "seo_issues": ["개선 필요 사항들"],
    "optimized_content": "최적화된 본문",
    "title": "최적화된 제목",
    "tags": ["ai", "pipeline"],
    "rewrite_count": 0,       ← 재작성 횟수 카운터
    "published_urls": {
        "devto": "https://dev.to/...",
        "hashnode": "https://..."
    }
}
```

### 품질 게이트 (Quality Gate)

```
SEO 점수 >= 70점 → 발행
SEO 점수 < 70점  → 재작성 요청
재작성 2회 초과  → 강제 발행 (무한 루프 방지)
```

---

## 7. 사용한 기술 스택 설명

| 기술 | 역할 | 비유 |
|------|------|------|
| Python | 주 개발 언어 | 모든 걸 만드는 재료 |
| LangChain | 에이전트 프레임워크 | 에이전트 설계도 |
| LangGraph | 오케스트레이터 | 에이전트들의 교통정리 |
| OpenAI GPT-4o-mini | AI 두뇌 | 실제로 생각하는 부분 |
| Claude Sonnet 4.6 | AI 두뇌 (메인) | 더 정교한 두뇌 |
| Supabase | 데이터베이스 | 뉴스 데이터 창고 |
| dev.to API | 블로그 발행 | 발행 채널 1 |
| Hashnode API | 블로그 발행 | 발행 채널 2 |
| GitHub Actions | 자동 스케줄 | 자동 타이머 |
| DuckDuckGo | 웹 검색 | 무료 검색 도구 |

---

## 8. 실제 실행 결과

### 오늘 실행한 결과 (2026-04-08)

```
============================================================
  itnews-multi-agent
  대상 레포: https://github.com/meene11/it-news-pipeline
============================================================

[1/4] Research Agent 실행 중...   ← GitHub 분석 완료
[2/4] Writer Agent 실행 중...     ← 블로그 초안 작성 완료
[3/4] SEO Agent 실행 중...
  SEO 점수 85점 — 기준 통과, 발행합니다.
[4/4] Publisher Agent 실행 중...

============================================================
  파이프라인 완료!
============================================================
  제목    : AI 기반 IT 뉴스 데이터 파이프라인 구축 방법
  SEO 점수: 85점
  태그    : ['ai', 'pipeline', 'sentiment', 'trending']
```

**발행 실패 원인 (해결 완료):**
- dev.to/Hashnode 태그가 한글이면 거절됨
- → 한글 태그를 영문으로 자동 변환하는 로직 추가

**내일 할 작업:**
- Research Agent를 Supabase 연동으로 교체
- 실제 뉴스 기사들을 가져와서 "이번 주 IT 뉴스 트렌드" 포스팅 자동화

---

## 9. 폴더 구조 설명

```
itnews-multi-agent/
│
├── agents/                    ← 에이전트들이 있는 폴더
│   ├── research_agent.py      ← 정보 수집 에이전트
│   ├── writer_agent.py        ← 글쓰기 에이전트
│   ├── seo_agent.py           ← SEO 검사 에이전트
│   └── publisher_agent.py     ← 발행 에이전트
│
├── tools/                     ← 에이전트가 사용하는 도구들
│   ├── github_tools.py        ← GitHub 읽기 도구
│   ├── search_tools.py        ← 웹 검색 도구
│   └── blog_tools.py          ← 블로그 발행 도구
│
├── orchestrator/              ← 오케스트레이터 (총감독)
│   ├── workflow.py            ← 에이전트 흐름 정의
│   ├── state.py               ← 공유 상태 구조 정의
│   └── quality_gates.py       ← SEO 점수 판단 로직
│
├── config/                    ← 설정 파일들
│   ├── settings.py            ← API 키 등 환경변수 관리
│   └── prompts.py             ← 각 에이전트의 역할 지시문
│
├── .github/workflows/
│   └── auto_publish.yml       ← GitHub Actions 자동화 설정
│
├── .env                       ← API 키 (절대 GitHub에 올리면 안 됨)
├── .env.example               ← .env 양식 (키 값 없이 GitHub에 공개)
├── requirements.txt           ← 필요한 Python 패키지 목록
└── main.py                    ← 실행 진입점 (여기서 시작)
```

---

## 10. 배운 점 & 포트폴리오 포인트

### 핵심 학습 포인트

| 항목 | 내용 |
|------|------|
| 멀티에이전트 설계 | 하나의 복잡한 작업을 전문화된 4개 에이전트로 분리 |
| 오케스트레이터 구현 | LangGraph로 조건 분기, 재시도 루프 구현 |
| 하네스 엔지니어링 | 에이전트가 사용할 도구를 등록하고 관리 |
| API 연동 | Anthropic, OpenAI, dev.to, Hashnode, GitHub API |
| 자동화 | GitHub Actions로 스케줄 실행 설정 |
| SEO+GEO | 검색엔진 + AI 검색 동시 최적화 |
| 에러 처리 | API 과부하 시 자동 재시도 로직 |
| Git 브랜치 전략 | Phase별 브랜치 생성 → main merge |

### 포트폴리오에서 강조할 점

1. **실용적인 자동화** — 실제로 블로그에 글이 발행됨
2. **최신 AI 트렌드** — 멀티에이전트, LangGraph 활용
3. **SEO+GEO 동시 적용** — 검색엔진 + AI 검색 최적화
4. **멀티 플랫폼** — dev.to + Hashnode 동시 발행
5. **확장 가능한 구조** — 에이전트 추가/교체 용이

### GitHub 링크
- **이 프로젝트:** https://github.com/meene11/itnews-multi-agent
- **데이터 소스:** https://github.com/meene11/it-news-pipeline
- **뉴스 파이프라인 배포:** https://it-news-pipeline.vercel.app
