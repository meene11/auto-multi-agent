import hashlib
from datetime import datetime


# 기사 키워드 추출용 사전
KEYWORD_MAP = {
    "인텔": "인텔", "Intel": "인텔",
    "삼성": "삼성", "Samsung": "삼성",
    "애플": "애플", "Apple": "애플",
    "구글": "구글", "Google": "구글",
    "메타": "메타", "Meta": "메타",
    "엔비디아": "엔비디아", "NVIDIA": "엔비디아",
    "마이크로소프트": "MS", "Microsoft": "MS",
    "테슬라": "테슬라", "Tesla": "테슬라",
    "아마존": "아마존", "Amazon": "아마존", "AWS": "AWS",
    "AI": "AI", "인공지능": "AI", "챗GPT": "AI", "GPT": "AI",
    "LLM": "AI", "오픈AI": "AI", "OpenAI": "AI",
    "반도체": "반도체", "칩": "반도체",
    "비트코인": "비트코인", "암호화폐": "암호화폐",
    "로봇": "로봇", "자율주행": "자율주행",
    "전기차": "전기차", "배터리": "배터리",
    "클라우드": "클라우드", "데이터센터": "데이터센터",
    "보안": "보안", "해킹": "해킹",
    "스타트업": "스타트업", "IPO": "IPO",
    "네이버": "네이버", "카카오": "카카오",
    "LG": "LG", "SK": "SK", "KT": "KT",
    "셀트리온": "셀트리온", "바이오": "바이오",
    "이스라엘": "이스라엘", "중동": "중동",
    "중국": "중국", "미국": "미국", "일본": "일본",
}

# 제목 패턴 풀 — {k1}, {k2} 는 키워드 자리, {date}는 날짜
TITLE_PATTERNS = [
    "{k1}·{k2}, 오늘 IT 뉴스 다 잡았다",
    "지금 IT판 뜨거운 이슈: {k1}과 {k2}",
    "{k1}부터 {k2}까지, 오늘의 기술 뉴스",
    "오늘 꼭 알아야 할 IT 뉴스: {k1}·{k2} 중심으로",
    "{k1}과 {k2}이 이끄는 {date} IT 동향",
    "이 뉴스 놓치면 안 돼: {k1}, {k2} 핵심 정리",
    "{k1}·{k2} 중심, 오늘의 테크 브리핑",
    "{date} IT 핫이슈: {k1}과 {k2} 무슨 일?",
    "테크 뉴스 한방 정리 — {k1}과 {k2}의 하루",
    "{k1}·{k2}에서 시작된 오늘의 IT 흐름",
]


def _extract_keywords(articles: list[dict]) -> list[str]:
    """기사 제목에서 핵심 키워드를 순서대로 추출한다."""
    found = []
    seen = set()
    all_text = " ".join(a.get("title", "") + " " + a.get("summary", "") for a in articles)

    for keyword, label in KEYWORD_MAP.items():
        if keyword in all_text and label not in seen:
            found.append(label)
            seen.add(label)
        if len(found) >= 4:
            break

    return found


def _generate_title(articles: list[dict]) -> str:
    """기사 내용 기반으로 매번 다른 제목을 생성한다."""
    keywords = _extract_keywords(articles)
    today = datetime.now().strftime("%m월 %d일")

    # 키워드가 2개 이상이면 패턴 사용, 부족하면 기사 제목 직접 활용
    if len(keywords) >= 2:
        k1, k2 = keywords[0], keywords[1]
    elif len(keywords) == 1:
        k1 = keywords[0]
        k2 = "IT 업계"
    else:
        # 키워드 못 찾으면 첫 기사 제목 앞 15자 활용
        first_title = articles[0].get("title", "오늘의 IT") if articles else "오늘의 IT"
        k1 = first_title[:15].rstrip()
        k2 = "최신 뉴스"

    # 기사 ID 합으로 패턴 인덱스 결정 → 같은 기사 묶음엔 항상 같은 패턴
    ids_str = "".join(str(a.get("id", 0)) for a in articles)
    idx = int(hashlib.md5(ids_str.encode()).hexdigest(), 16) % len(TITLE_PATTERNS)
    pattern = TITLE_PATTERNS[idx]

    return pattern.format(k1=k1, k2=k2, date=today)


def run_writer(articles: list[dict]) -> dict:
    """
    Supabase 기사 목록을 Python 템플릿으로 블로그 포스팅으로 변환한다.
    OpenAI 호출 없음 -> 비용 $0.
    """
    title = _generate_title(articles)

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
    found = []
    seen = set()
    all_text = " ".join(a.get("title", "") + " " + a.get("summary", "") for a in articles)

    for keyword, label in KEYWORD_MAP.items():
        if keyword in all_text and label not in seen:
            found.append(label)
            seen.add(label)
        if len(found) >= 4:
            break

    defaults = ["IT뉴스", "테크", "뉴스요약", "technology"]
    for d in defaults:
        if len(found) >= 4:
            break
        if d not in seen:
            found.append(d)
            seen.add(d)

    return found[:4]
