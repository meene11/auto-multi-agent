"""
네이버 블로그 발행만 단독 테스트하는 스크립트.
OpenAI API 호출 없음 -> 과금 없음.
"""
from tools.naver_tools import post_to_naver_blog

TEST_TITLE = "네이버 자동화 테스트 제목"
TEST_CONTENT = """
테스트 본문입니다.

이 글은 자동화 테스트용으로 작성됐습니다.

- 항목 1
- 항목 2
- 항목 3

잘 올라가면 성공!
"""

if __name__ == "__main__":
    print("네이버 블로그 단독 테스트 시작...")
    result = post_to_naver_blog(title=TEST_TITLE, content=TEST_CONTENT)
    print(f"\n결과: {result}")
