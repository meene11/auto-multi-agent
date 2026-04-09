import json
import httpx
from pathlib import Path
from config.settings import settings

PUBLISHED_IDS_FILE = Path(__file__).parent.parent / "published_ids.json"


def _load_published_ids() -> set[int]:
    if PUBLISHED_IDS_FILE.exists():
        return set(json.loads(PUBLISHED_IDS_FILE.read_text(encoding="utf-8")))
    return set()


def _save_published_ids(ids: set[int]) -> None:
    PUBLISHED_IDS_FILE.write_text(json.dumps(sorted(ids)), encoding="utf-8")


def mark_as_published(article_ids: list[int]) -> None:
    """발행 완료된 기사 ID를 로컬 파일에 기록한다."""
    ids = _load_published_ids()
    ids.update(article_ids)
    _save_published_ids(ids)
    print(f"  발행 기록 저장 완료 ({len(article_ids)}개 추가, 누적 {len(ids)}개)")


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

    # 이미 발행한 기사보다 넉넉하게 가져온 후 필터링
    published_ids = _load_published_ids()
    fetch_limit = limit + len(published_ids) if published_ids else limit
    params["limit"] = str(min(fetch_limit, 100))  # 최대 100개

    response = httpx.get(url, headers=headers, params=params, timeout=15)
    if response.status_code != 200:
        raise RuntimeError(f"Supabase 조회 실패 (status: {response.status_code}): {response.text}")

    all_articles = response.json()

    # 이미 발행한 기사 제외
    new_articles = [a for a in all_articles if a.get("id") not in published_ids]

    if not new_articles:
        raise RuntimeError("발행할 새 기사가 없습니다. 모든 최근 기사가 이미 발행됐습니다.")

    print(f"  전체 {len(all_articles)}개 중 기발행 {len(published_ids)}개 제외 -> {len(new_articles)}개 신규")
    return new_articles[:limit]


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
