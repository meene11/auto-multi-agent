from langgraph.graph import StateGraph, END

from orchestrator.state import BlogState


def research_node(state: BlogState) -> BlogState:
    from tools.supabase_tools import fetch_articles_from_supabase
    from config.settings import settings
    print("\n[1/3] Supabase에서 기사 조회 중...")
    articles = fetch_articles_from_supabase(limit=settings.articles_per_run)
    print(f"  {len(articles)}개 기사 로드 완료.")
    return {**state, "articles": articles}


def write_node(state: BlogState) -> BlogState:
    from agents.writer_agent import run_writer
    print("\n[2/3] 블로그 포스팅 포맷팅 중...")
    result = run_writer(state["articles"])
    return {
        **state,
        "title": result["title"],
        "content": result["content"],
        "tags": result["tags"],
    }


def publish_node(state: BlogState) -> BlogState:
    from agents.publisher_agent import run_publisher
    from agents.seo_agent import run_seo
    # 간단 SEO 체크
    seo = run_seo(state["title"], state["content"], state["tags"])
    print(f"\n  SEO 점수: {seo['seo_score']}점")

    print("\n[3/3] 발행 중...")
    article_ids = [a["id"] for a in state.get("articles", []) if a.get("id")]
    result = run_publisher(
        title=state["title"],
        content=state["content"],
        tags=state["tags"],
        article_ids=article_ids,
    )
    return {**state, "seo_score": seo["seo_score"], "published_urls": result}


def build_workflow() -> StateGraph:
    graph = StateGraph(BlogState)

    graph.add_node("research", research_node)
    graph.add_node("write", write_node)
    graph.add_node("publish", publish_node)

    graph.set_entry_point("research")
    graph.add_edge("research", "write")
    graph.add_edge("write", "publish")
    graph.add_edge("publish", END)

    return graph.compile()


def run_pipeline() -> BlogState:
    workflow = build_workflow()

    initial_state: BlogState = {
        "articles": [],
        "title": "",
        "content": "",
        "tags": [],
        "seo_score": 0,
        "published_urls": {},
    }

    return workflow.invoke(initial_state)
