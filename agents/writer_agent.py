import time
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from config.settings import settings
from config.prompts import WRITER_AGENT_SYSTEM_PROMPT


def run_writer(research_result: str) -> str:
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=settings.openai_api_key,
        temperature=0.7,
    )

    messages = [
        SystemMessage(content=WRITER_AGENT_SYSTEM_PROMPT),
        HumanMessage(content=f"""
아래는 Supabase에서 가져온 최신 IT 뉴스 기사들입니다.
각 기사의 제목과 내용을 읽고, 독자가 핵심을 빠르게 파악할 수 있는 IT 뉴스 요약 블로그 포스팅을 작성해주세요.

기사 목록:
{research_result}

위 기사들을 바탕으로 한국어 IT 뉴스 요약 블로그 포스팅을 마크다운 형식으로 작성해주세요.
제목, 각 기사 요약, 한 줄 정리, 태그까지 모두 포함해주세요.
""")
    ]

    for attempt in range(3):
        try:
            response = llm.invoke(messages)
            return response.content
        except Exception as e:
            if "429" in str(e) or "rate" in str(e).lower():
                wait = (attempt + 1) * 10
                print(f"  API 한도 초과, {wait}초 후 재시도... ({attempt + 1}/3)")
                time.sleep(wait)
            else:
                raise

    raise RuntimeError("OpenAI API 재시도 3회 실패")
