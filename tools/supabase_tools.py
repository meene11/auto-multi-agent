import httpx
from config.settings import settings


def mark_as_published(article_ids: list[int]) -> None:
    """발행 완료된 기사의 is_published를 Supabase에서 true로 업데이트한다."""
    if not article_ids:
        return

    service_key = settings.supabase_service_role_key
    if not service_key:
        raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY가 설정되지 않았습니다.")

    url = f"{settings.supabase_url}/rest/v1/{settings.supabase_table}"
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }
    id_list = ",".join(str(i) for i in article_ids)
    params = {"id": f"in.({id_list})"}

    response = httpx.patch(url, headers=headers, params=params, json={"is_published": True}, timeout=15)
    if response.status_code not in (200, 204):
        raise RuntimeError(f"is_published 업데이트 실패 (status: {response.status_code}): {response.text}")

    print(f"  Supabase is_published=true 업데이트 완료 ({len(article_ids)}개)")


def fetch_articles_from_supabase(limit: int = 5) -> list[dict]:
    """Supabase news_list 테이블에서 미발행 기사만 가져온다."""
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
        "is_published": "eq.false",
        "order": "created_at.desc",
        "limit": str(limit),
    }

    response = httpx.get(url, headers=headers, params=params, timeout=15)
    if response.status_code != 200:
        raise RuntimeError(f"Supabase 조회 실패 (status: {response.status_code}): {response.text}")

    articles = response.json()

    if not articles:
        raise RuntimeError("발행할 새 기사가 없습니다. 모든 최근 기사가 이미 발행됐습니다.")

    print(f"  미발행 기사 {len(articles)}개 조회 완료")
    return articles


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
