from config.settings import settings
from tools.supabase_tools import fetch_articles_from_supabase, format_articles_for_research


def run_research() -> tuple[list[dict], str]:
    """
    Supabase에서 최근 기사를 가져와 리서치 결과로 반환한다.
    Returns:
        (articles, formatted_text)
    """
    print(f"  Supabase에서 기사 {settings.articles_per_run}개 조회 중...")
    articles = fetch_articles_from_supabase(limit=settings.articles_per_run)
    print(f"  {len(articles)}개 기사 로드 완료.")
    formatted = format_articles_for_research(articles)
    return articles, formatted
