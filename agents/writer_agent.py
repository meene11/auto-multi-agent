import time
import anthropic
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from config.settings import settings
from config.prompts import WRITER_AGENT_SYSTEM_PROMPT


def run_writer(research_result: str) -> str:
    llm = ChatAnthropic(
        model="claude-sonnet-4-6",
        api_key=settings.anthropic_api_key,
        temperature=0.7,
    )

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

    for attempt in range(3):
        try:
            response = llm.invoke(messages)
            return response.content
        except anthropic.APIStatusError as e:
            if e.status_code != 529:
                raise
            wait = (attempt + 1) * 10
            print(f"  Anthropic 서버 과부하, {wait}초 후 재시도... ({attempt + 1}/3)")
            time.sleep(wait)

    raise RuntimeError("Anthropic API 재시도 3회 실패 (과부하)")
