from datetime import datetime


def run_writer(articles: list[dict]) -> dict:
    """
    Supabase 기사 목록을 Python 템플릿으로 블로그 포스팅으로 변환한다.
    OpenAI 호출 없음 -> 비용 $0.
    """
    today = datetime.now().strftime("%Y년 %m월 %d일")
    title = f"[IT 뉴스 요약] {today} 주요 기사 {len(articles)}선"

    lines = []
    lines.append(f"# {title}\n")
    lines.append(f"> 오늘의 주요 IT 뉴스 {len(articles)}개를 빠르게 정리했습니다.\n")

    for i, article in enumerate(articles, 1):
        art_title = article.get("title") or "제목 없음"
        summary = article.get("summary") or ""
        source = article.get("source") or ""
        url = article.get("url") or ""
        sentiment = article.get("sentiment") or ""

        lines.append(f"## {i}. {art_title}\n")
        if summary:
            lines.append(f"{summary}\n")
        if sentiment:
            sentiment_label = {"positive": "긍정", "negative": "부정", "neutral": "중립"}.get(sentiment, sentiment)
            lines.append(f"**감성 분석:** {sentiment_label}\n")
        if source and url:
            lines.append(f"출처: [{source}]({url})\n")
        elif url:
            lines.append(f"[원문 보기]({url})\n")
        lines.append("")

    lines.append("---\n")
    lines.append("*본 포스팅은 최신 IT 뉴스를 자동으로 수집·요약하여 발행됩니다.*\n")

    content = "\n".join(lines)
    tags = _extract_tags(articles)

    return {
        "title": title,
        "content": content,
        "tags": tags,
    }


def _extract_tags(articles: list[dict]) -> list[str]:
    """기사 제목에서 키워드를 추출해 태그를 생성한다."""
    keyword_map = {
        "AI": "AI", "인공지능": "AI", "반도체": "반도체", "삼성": "삼성",
        "애플": "애플", "구글": "구글", "메타": "메타", "엔비디아": "엔비디아",
        "비트코인": "비트코인", "암호화폐": "암호화폐", "스타트업": "스타트업",
        "클라우드": "클라우드", "보안": "보안", "로봇": "로봇", "전기차": "전기차",
        "테슬라": "테슬라", "오픈AI": "AI", "챗GPT": "AI", "LLM": "AI",
        "네이버": "네이버", "카카오": "카카오", "SKT": "SKT", "KT": "KT",
    }

    found = []
    all_text = " ".join(a.get("title", "") + " " + a.get("summary", "") for a in articles)

    for keyword, tag in keyword_map.items():
        if keyword in all_text and tag not in found:
            found.append(tag)
        if len(found) >= 4:
            break

    # 기본 태그로 채우기
    defaults = ["IT뉴스", "테크", "뉴스요약", "technology"]
    for d in defaults:
        if len(found) >= 4:
            break
        if d not in found:
            found.append(d)

    return found[:4]
