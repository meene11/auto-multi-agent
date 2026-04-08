from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

from config.settings import settings
from config.prompts import RESEARCH_AGENT_SYSTEM_PROMPT
from tools.github_tools import fetch_github_readme, analyze_code_structure
from tools.search_tools import search_web


def build_research_agent() -> AgentExecutor:
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=settings.openai_api_key,
        temperature=0,
    )

    tools = [fetch_github_readme, analyze_code_structure, search_web]

    prompt = ChatPromptTemplate.from_messages([
        ("system", RESEARCH_AGENT_SYSTEM_PROMPT),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)


def run_research(repo_url: str) -> str:
    agent_executor = build_research_agent()
    result = agent_executor.invoke({
        "input": f"""
다음 GitHub 레포지토리를 분석해서 기술 블로그 포스팅 재료를 수집해주세요.

레포지토리 URL: {repo_url}

수행 순서:
1. fetch_github_readme 로 README 전문을 가져오세요.
2. analyze_code_structure 로 파일 구조를 파악하세요.
3. search_web 으로 이 프로젝트와 관련된 트렌드 키워드를 검색하세요.
4. 수집한 정보를 바탕으로 지정된 JSON 형식으로 리서치 결과를 반환하세요.
"""
    })
    return result["output"]
