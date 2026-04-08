import json
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

from config.settings import settings
from config.prompts import SEO_AGENT_SYSTEM_PROMPT


def run_seo(draft: str) -> dict:
    """
    블로그 초안을 SEO 분석하고 개선한다.
    반환값: { seo_score, issues, optimized_content, title, tags }
    """
    llm = ChatAnthropic(
        model="claude-sonnet-4-6",
        api_key=settings.anthropic_api_key,
        temperature=0,
    )

    agent = create_react_agent(llm, tools=[])

    messages = [
        SystemMessage(content=SEO_AGENT_SYSTEM_PROMPT),
        HumanMessage(content=f"""
아래 블로그 초안을 SEO 분석하고 개선해주세요.
반드시 JSON 형식으로만 응답해주세요. 다른 설명 없이 JSON만 반환합니다.

블로그 초안:
{draft}
""")
    ]

    result = agent.invoke({"messages": messages})
    content = result["messages"][-1].content

    # JSON 파싱 시도
    try:
        # 마크다운 코드블록 제거 후 파싱
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        return json.loads(cleaned.strip())
    except Exception:
        # 파싱 실패 시 기본값 반환
        return {
            "seo_score": 50,
            "issues": ["JSON 파싱 실패"],
            "optimized_content": draft,
            "title": "",
            "tags": [],
        }
