def run_seo(title: str, content: str, tags: list[str]) -> dict:
    """
    기본 SEO 체크를 Python으로 수행한다.
    OpenAI 호출 없음 -> 비용 $0.
    """
    score = 100
    issues = []

    if len(title) < 10:
        score -= 10
        issues.append("제목이 너무 짧습니다.")
    if len(content) < 500:
        score -= 20
        issues.append("본문이 너무 짧습니다 (500자 이상 권장).")
    if len(tags) == 0:
        score -= 10
        issues.append("태그가 없습니다.")

    return {
        "seo_score": score,
        "issues": issues,
        "optimized_content": content,
        "title": title,
        "tags": tags,
    }
