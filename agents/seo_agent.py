import json
import time
import anthropic
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from config.settings import settings
from config.prompts import SEO_AGENT_SYSTEM_PROMPT


def run_seo(draft: str) -> dict:
    """
    블로그 초안을 SEO+GEO 분석하고 개선한다.
    반환값: { seo_score, issues, optimized_content, title, tags }
    """
    llm = ChatAnthropic(
        model="claude-sonnet-4-6",
        api_key=settings.anthropic_api_key,
        temperature=0,
    )

    messages = [
        SystemMessage(content=SEO_AGENT_SYSTEM_PROMPT),
        HumanMessage(content=f"""
아래 블로그 초안을 SEO+GEO 분석하고 개선해주세요.
반드시 JSON 형식으로만 응답해주세요. 다른 설명 없이 JSON만 반환합니다.

블로그 초안:
{draft}
""")
    ]

    for attempt in range(3):
        try:
            response = llm.invoke(messages)
            content = response.content
            break
        except anthropic.APIStatusError as e:
            if e.status_code != 529:
                raise
            wait = (attempt + 1) * 10
            print(f"  Anthropic 서버 과부하, {wait}초 후 재시도... ({attempt + 1}/3)")
            time.sleep(wait)
    else:
        raise RuntimeError("Anthropic API 재시도 3회 실패 (과부하)")

    # JSON 파싱
    try:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        return json.loads(cleaned.strip())
    except Exception:
        return {
            "seo_score": 50,
            "issues": ["JSON 파싱 실패"],
            "optimized_content": draft,
            "title": "",
            "tags": [],
        }
