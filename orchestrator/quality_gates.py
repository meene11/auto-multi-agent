from orchestrator.state import BlogState
from config.settings import settings


def seo_routing(state: BlogState) -> str:
    """SEO 점수에 따라 다음 노드를 결정한다."""
    seo_score = state.get("seo_score", 0)
    rewrite_count = state.get("rewrite_count", 0)
    max_rewrites = 2

    if seo_score >= settings.seo_score_threshold:
        print(f"  SEO 점수 {seo_score}점 — 기준 통과, 발행합니다.")
        return "publish"

    if rewrite_count >= max_rewrites:
        print(f"  SEO 점수 {seo_score}점 — 재작성 횟수 초과({max_rewrites}회), 강제 발행합니다.")
        return "publish"

    print(f"  SEO 점수 {seo_score}점 — 기준 미달, 재작성합니다. ({rewrite_count + 1}/{max_rewrites})")
    return "rewrite"
