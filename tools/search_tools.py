from langchain_core.tools import tool
from duckduckgo_search import DDGS


@tool
def search_web(query: str) -> str:
    """웹에서 관련 트렌드 키워드와 정보를 검색한다."""
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=5))

    if not results:
        return "검색 결과가 없습니다."

    output = []
    for r in results:
        output.append(f"제목: {r.get('title', '')}")
        output.append(f"내용: {r.get('body', '')}")
        output.append("")

    return "\n".join(output)
