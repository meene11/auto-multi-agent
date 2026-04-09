from typing import TypedDict


class BlogState(TypedDict):
    articles: list[dict]     # Supabase에서 가져온 기사 목록
    title: str               # 포스팅 제목
    content: str             # 포스팅 본문 (마크다운)
    tags: list[str]          # 태그 목록
    seo_score: int           # SEO 점수
    published_urls: dict     # 발행된 URL { devto, hashnode, naver }
