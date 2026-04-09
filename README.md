# auto-multi-agent

> Supabase에 수집된 IT 뉴스를 AI 멀티에이전트가 자동으로 블로그 포스팅으로 변환하여 발행하는 자동화 시스템

---

## 프로젝트 소개

`it-news-pipeline`이 매일 수집한 IT 뉴스 기사를 가져와, 기사 제목과 요약을 기반으로 블로그 포스팅을 자동 생성하고 **dev.to · Hashnode · 네이버 블로그**에 동시 발행하는 멀티에이전트 시스템입니다.

**핵심 특징:**
- 실행 비용 **$0** — OpenAI 없이 Python 템플릿으로 글 생성
- 발행 기록 자동 관리 — 중복 포스팅 방지
- 기사 내용 기반 **동적 제목 생성** — 매번 다른 제목

---

## 시스템 아키텍처

```
[Supabase - news_list 테이블]
  it-news-pipeline이 매일 수집한 IT 뉴스
        ↓
[Research Agent]
  새 기사 5개 조회 (발행 이력 자동 제외)
        ↓
[Writer Agent]
  기사 키워드 추출 → 동적 제목 생성 → 마크다운 포스팅 생성
        ↓
[SEO Agent]
  제목 길이 · 본문 길이 · 태그 수 기본 체크
        ↓
[Publisher Agent]
  ├─ dev.to      REST API 자동 발행
  ├─ Hashnode    GraphQL API 자동 발행
  └─ 네이버 블로그 Selenium 브라우저 자동화
        ↓
[published_ids.json]
  발행된 기사 ID 저장 → 다음 실행 때 중복 방지
```

---

## 에이전트 구성

| 에이전트 | 역할 | 방식 |
|---|---|---|
| Research Agent | Supabase에서 미발행 기사 조회 | httpx REST API |
| Writer Agent | 기사 → 블로그 포스팅 변환 | Python 템플릿 (LLM 없음) |
| SEO Agent | 기본 SEO 품질 체크 | Python 코드 |
| Publisher Agent | 3개 플랫폼 동시 발행 | API + Selenium |

---

## 기술 스택

| 분류 | 기술 |
|---|---|
| 파이프라인 오케스트레이터 | LangGraph |
| 데이터베이스 | Supabase (PostgreSQL REST API) |
| 웹 자동화 | Selenium, pyautogui, pyperclip |
| HTTP 클라이언트 | httpx |
| 환경 설정 | pydantic-settings |

---

## 디렉토리 구조

```
auto-multi-agent/
│
├── main.py                  # 진입점
├── test_naver.py            # 네이버 단독 테스트 (비용 없음)
├── run_scheduled.bat        # 스케줄러 자동 실행용
│
├── agents/
│   ├── research_agent.py    # Supabase 기사 조회
│   ├── writer_agent.py      # 포스팅 생성 + 동적 제목
│   ├── seo_agent.py         # SEO 체크
│   └── publisher_agent.py   # 발행 총괄
│
├── tools/
│   ├── supabase_tools.py    # Supabase 연동 + 발행 기록 관리
│   ├── blog_tools.py        # dev.to, Hashnode API
│   └── naver_tools.py       # 네이버 Selenium 자동화
│
├── orchestrator/
│   ├── workflow.py          # LangGraph 파이프라인
│   ├── state.py             # 공유 상태 정의
│   └── quality_gates.py     # SEO 분기 처리
│
├── config/
│   ├── settings.py          # 환경변수 로드
│   └── prompts.py           # 프롬프트 (예비)
│
└── docs/
    └── project_introduction.md  # 프로젝트 소개 문서
```

---

## 설치 및 실행

```bash
# 1. 클론
git clone https://github.com/meene11/auto-multi-agent.git
cd auto-multi-agent

# 2. 가상환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux

# 3. 패키지 설치
pip install -r requirements.txt

# 4. 환경변수 설정
cp .env.example .env
# .env 파일에 각 API 키 입력
```

### 환경변수 (.env)

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_TABLE=news_list         # 기본값
ARTICLES_PER_RUN=5               # 1회 발행 기사 수

# dev.to
DEVTO_API_KEY=your_devto_api_key

# Hashnode
HASHNODE_API_KEY=your_hashnode_api_key
HASHNODE_PUBLICATION_ID=your_publication_id

# 네이버 블로그
NAVER_ID=your_naver_id
NAVER_PASSWORD=your_naver_password
NAVER_BLOG_ID=your_blog_id       # 또는 전체 URL
```

### 실행

```bash
# 전체 발행 (dev.to + Hashnode + 네이버)
python main.py

# 네이버 제외 발행
python main.py --skip-naver

# 네이버만 단독 테스트
python test_naver.py
```

---

## 발행 플랫폼

| 플랫폼 | 방식 | 특징 |
|---|---|---|
| dev.to | REST API | 완전 자동, 개발자 커뮤니티 |
| Hashnode | GraphQL API | 완전 자동, 개발자 블로그 |
| 네이버 블로그 | Selenium | 반자동 (캡챠 시 수동 처리) |

---

## 중복 발행 방지

```
1회 실행 → 기사 [1,2,3,4,5] 발행 → published_ids.json 저장
2회 실행 → [1,2,3,4,5] 자동 제외 → 기사 [6,7,8,9,10] 발행
```

---

## 동적 제목 생성

기사에서 핵심 키워드(인텔, AI, 삼성 등)를 추출해 10가지 패턴 중 하나로 제목 생성:

```
"인텔·AWS, 오늘 IT 뉴스 다 잡았다"
"지금 IT판 뜨거운 이슈: LG과 셀트리온"
"AI·반도체에서 시작된 오늘의 IT 흐름"
```

---

## 실행 비용

| 항목 | 비용 |
|---|---|
| 기사 조회 (Supabase) | 무료 |
| 글 작성 (Python 템플릿) | 무료 |
| 발행 3개 플랫폼 | 무료 |
| **합계** | **$0** |
