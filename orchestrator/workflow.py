from langgraph.graph import StateGraph, END

from orchestrator.state import BlogState
from orchestrator.quality_gates import seo_routing


def research_node(state: BlogState) -> BlogState:
    from agents.research_agent import run_research
    print("\n[1/4] Research Agent 실행 중...")
    result = run_research(state["topic"])
    return {**state, "research_result": result}


def write_node(state: BlogState) -> BlogState:
    from agents.writer_agent import run_writer
    rewrite_count = state.get("rewrite_count", 0)
    is_rewrite = rewrite_count > 0

    if is_rewrite:
        print(f"\n[재작성 {rewrite_count}회] Writer Agent 실행 중...")
        issues = "\n".join(state.get("seo_issues", []))
        input_data = f"{state['research_result']}\n\n이전 작성의 개선 필요 사항:\n{issues}"
    else:
        print("\n[2/4] Writer Agent 실행 중...")
        input_data = state["research_result"]

    draft = run_writer(input_data)
    return {**state, "draft": draft, "rewrite_count": rewrite_count + (1 if is_rewrite else 0)}


def seo_node(state: BlogState) -> BlogState:
    from agents.seo_agent import run_seo
    print("\n[3/4] SEO Agent 실행 중...")
    seo_result = run_seo(state["draft"])
    return {
        **state,
        "seo_score": seo_result.get("seo_score", 0),
        "seo_issues": seo_result.get("issues", []),
        "optimized_content": seo_result.get("optimized_content", state["draft"]),
        "title": seo_result.get("title", ""),
        "tags": seo_result.get("tags", []),
    }


def publish_node(state: BlogState) -> BlogState:
    from agents.publisher_agent import run_publisher
    print("\n[4/4] Publisher Agent 실행 중...")
    result = run_publisher(
        title=state["title"],
        content=state["optimized_content"],
        tags=state["tags"],
    )
    return {**state, "published_urls": result}


def build_workflow() -> StateGraph:
    graph = StateGraph(BlogState)

    # 노드 등록
    graph.add_node("research", research_node)
    graph.add_node("write", write_node)
    graph.add_node("seo", seo_node)
    graph.add_node("publish", publish_node)

    # 엣지 연결
    graph.set_entry_point("research")
    graph.add_edge("research", "write")
    graph.add_edge("write", "seo")

    # SEO 조건 분기
    graph.add_conditional_edges(
        "seo",
        seo_routing,
        {
            "publish": "publish",
            "rewrite": "write",
        }
    )

    graph.add_edge("publish", END)

    return graph.compile()


def run_pipeline(repo_url: str) -> BlogState:
    """전체 파이프라인 실행 진입점"""
    workflow = build_workflow()

    initial_state: BlogState = {
        "topic": repo_url,
        "research_result": "",
        "draft": "",
        "seo_score": 0,
        "seo_issues": [],
        "optimized_content": "",
        "title": "",
        "tags": [],
        "rewrite_count": 0,
        "published_urls": {},
    }

    return workflow.invoke(initial_state)
