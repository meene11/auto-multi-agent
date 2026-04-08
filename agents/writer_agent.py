from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

from config.settings import settings
from config.prompts import WRITER_AGENT_SYSTEM_PROMPT


def run_writer(research_result: str) -> str:
    llm = ChatAnthropic(
        model="claude-sonnet-4-6",
        api_key=settings.anthropic_api_key,
        temperature=0.7,  # 글쓰기는 약간의 창의성 허용
    )

    agent = create_react_agent(llm, tools=[])

    messages = [
        SystemMessage(content=WRITER_AGENT_SYSTEM_PROMPT),
        HumanMessage(content=f"""
아래 리서치 결과를 바탕으로 기술 블로그 포스팅을 작성해주세요.

리서치 결과:
{research_result}

위 내용을 참고해서 개발자 독자를 위한 한국어 기술 블로그 포스팅을 마크다운 형식으로 작성해주세요.
제목, 본문, 태그까지 모두 포함해주세요.
""")
    ]

    result = agent.invoke({"messages": messages})
    return result["messages"][-1].content
