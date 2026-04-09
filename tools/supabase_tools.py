import httpx
from config.settings import settings


def fetch_articles_from_supabase(limit: int = 5) -> list[dict]:
    """Supabase news_list 테이블에서 최근 기사를 가져온다."""
    if not settings.supabase_url or not settings.supabase_key:
        raise RuntimeError("SUPABASE_URL 또는 SUPABASE_KEY가 설정되지 않았습니다.")

    url = f"{settings.supabase_url}/rest/v1/{settings.supabase_table}"
    headers = {
        "apikey": settings.supabase_key,
        "Authorization": f"Bearer {settings.supabase_key}",
        "Content-Type": "application/json",
    }
    params = {
        "select": "id,title,url,created_at,summary,sentiment,source",
        "summary": "not.is.null",
        "order": "created_at.desc",
        "limit": str(limit),
    }

    response = httpx.get(url, headers=headers, params=params, timeout=15)
    if response.status_code == 200:
        articles = response.json()
        if not articles:
            raise RuntimeError(f"Supabase 테이블 '{settings.supabase_table}'에 기사가 없습니다.")
        return articles
    raise RuntimeError(f"Supabase 조회 실패 (status: {response.status_code}): {response.text}")


def format_articles_for_research(articles: list[dict]) -> str:
    """news_list 기사 목록을 Writer Agent용 텍스트로 포맷팅한다."""
    lines = [f"총 {len(articles)}개의 최신 IT 뉴스 기사입니다.\n"]
    for i, article in enumerate(articles, 1):
        title = article.get("title") or "제목 없음"
        summary = article.get("summary") or ""
        url = article.get("url") or ""
        source = article.get("source") or ""
        sentiment = article.get("sentiment") or ""
        created_at = article.get("created_at") or ""

        lines.append(f"--- 기사 {i} ---")
        lines.append(f"제목: {title}")
        if source:
            lines.append(f"출처: {source}")
        if created_at:
            lines.append(f"작성일: {created_at[:10]}")
        if sentiment:
            lines.append(f"감성: {sentiment}")
        if url:
            lines.append(f"원문: {url}")
        lines.append(f"요약:\n{summary}")
        lines.append("")

    return "\n".join(lines)
