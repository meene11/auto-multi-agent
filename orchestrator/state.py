from typing import TypedDict


class BlogState(TypedDict):
    articles: list[dict]        # Supabase에서 가져온 기사 목록
    research_result: str        # Research Agent 출력 (기사 포맷팅 결과)
    draft: str                  # Writer Agent 출력
    seo_score: int              # SEO Agent 점수
    seo_issues: list[str]       # SEO 개선 사항
    optimized_content: str      # SEO 최적화된 본문
    title: str                  # SEO 최적화된 제목
    tags: list[str]             # 태그 목록
    rewrite_count: int          # 재작성 횟수 (무한 루프 방지)
    published_urls: dict        # 발행된 URL { devto, hashnode }
