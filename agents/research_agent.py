from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

from config.settings import settings
from config.prompts import RESEARCH_AGENT_SYSTEM_PROMPT
from tools.github_tools import fetch_github_readme, analyze_code_structure
from tools.search_tools import search_web


def run_research(repo_url: str) -> str:
    llm = ChatAnthropic(
        model="claude-sonnet-4-6",
        api_key=settings.anthropic_api_key,
        temperature=0,
    )

    tools = [fetch_github_readme, analyze_code_structure, search_web]
    agent = create_react_agent(llm, tools)

    messages = [
        SystemMessage(content=RESEARCH_AGENT_SYSTEM_PROMPT),
        HumanMessage(content=f"""
다음 GitHub 레포지토리를 분석해서 기술 블로그 포스팅 재료를 수집해주세요.

레포지토리 URL: {repo_url}

수행 순서:
1. fetch_github_readme 로 README 전문을 가져오세요.
2. analyze_code_structure 로 파일 구조를 파악하세요.
3. search_web 으로 이 프로젝트와 관련된 트렌드 키워드를 검색하세요.
4. 수집한 정보를 바탕으로 지정된 JSON 형식으로 리서치 결과를 반환하세요.
""")
    ]

    result = agent.invoke({"messages": messages})
    return result["messages"][-1].content
