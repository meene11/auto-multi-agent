"""
네이버 블로그 Selenium 자동 발행 도구.
사용자 제공 코드 기반 — 좌표 클릭 방식 사용.
"""

import re
import time
import pyperclip
import pyautogui
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from config.settings import settings


def _extract_blog_id(blog_id_or_url: str) -> str:
    """NAVER_BLOG_ID가 전체 URL이어도 블로그 ID만 추출한다."""
    return blog_id_or_url.rstrip("/").split("/")[-1]


def _build_driver() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
    driver.maximize_window()
    return driver


def _markdown_to_plain(md: str) -> str:
    """마크다운을 네이버 에디터용 평문으로 변환한다."""
    md = re.sub(r"^#{1,6}\s+", "\n", md, flags=re.MULTILINE)
    md = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", md)
    md = re.sub(r"`([^`]+)`", r"\1", md)
    md = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", md)
    md = re.sub(r"```[\s\S]*?```", "", md)
    md = re.sub(r"^---+$", "", md, flags=re.MULTILINE)
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip()


def post_to_naver_blog(title: str, content: str) -> str:
    if not settings.naver_id or not settings.naver_password:
        return "NAVER_ID 또는 NAVER_PASSWORD가 설정되지 않았습니다."
    if not settings.naver_blog_id:
        return "NAVER_BLOG_ID가 설정되지 않았습니다."

    blog_id = _extract_blog_id(settings.naver_blog_id)
    driver = _build_driver()

    try:
        # 1. 로그인
        driver.get("https://nid.naver.com/nidlogin.login")
        time.sleep(2)

        driver.execute_script(
            "document.getElementById('id').value=arguments[0]", settings.naver_id
        )
        driver.execute_script(
            "document.getElementById('pw').value=arguments[0]", settings.naver_password
        )
        time.sleep(1)
        driver.find_element(By.ID, "log.login").click()
        print("  [Naver] 로그인 시도!")
        time.sleep(3)

        # 캡챠 뜨면 직접 처리
        if "nidlogin" in driver.current_url or "nid.naver" in driver.current_url:
            print("  [Naver] 캡챠 떴으면 직접 풀고 로그인 완료되면 Enter 눌러 (안 떴으면 그냥 Enter)")
            input()

        # 2. 글쓰기 페이지 이동
        driver.get(f"https://blog.naver.com/{blog_id}/postwrite")
        time.sleep(7)

        # 3. 도움말 팝업 닫기
        try:
            close_btn = driver.find_element(By.CSS_SELECTOR, ".se-help-panel-close-button")
            close_btn.click()
            print("  [Naver] 도움말 팝업 닫기 성공!")
            time.sleep(1)
        except Exception:
            print("  [Naver] 도움말 없음, 계속 진행!")

        time.sleep(2)

        # 4. 제목 입력 (좌표 클릭)
        try:
            pyautogui.click(781, 352)
            time.sleep(1)
            pyperclip.copy(title)
            pyautogui.hotkey("ctrl", "v")
            print("  [Naver] 제목 입력 성공!")
        except Exception as e:
            print(f"  [Naver] 제목 입력 실패: {e}")

        time.sleep(2)

        # 5. 본문 입력 (좌표 클릭)
        try:
            pyautogui.click(516, 483)
            time.sleep(1)
            plain_content = _markdown_to_plain(content)
            pyperclip.copy(plain_content)
            pyautogui.hotkey("ctrl", "v")
            print("  [Naver] 본문 입력 성공!")
        except Exception as e:
            print(f"  [Naver] 본문 입력 실패: {e}")

        time.sleep(2)

        # 6. 발행 팝업 열기
        try:
            publish_btn = driver.find_element(By.CSS_SELECTOR, ".publish_btn__m9KHH")
            publish_btn.click()
            print("  [Naver] 발행 팝업 열기 성공!")
        except Exception as e:
            print(f"  [Naver] 발행 팝업 실패: {e}")

        time.sleep(2)

        # 7. 최종 발행
        try:
            confirm_btn = driver.find_element(By.CSS_SELECTOR, ".confirm_btn__WEaBq")
            confirm_btn.click()
            print("  [Naver] 최종 발행 성공!")
        except Exception as e:
            print(f"  [Naver] 최종 발행 실패: {e}")

        time.sleep(10)

        # 8. 블로그 확인
        blog_url = f"https://blog.naver.com/{blog_id}"
        driver.get(blog_url)
        time.sleep(5)
        print("  [Naver] 블로그 확인해봐!")

        time.sleep(30)
        return f"Naver 블로그 발행 완료: {blog_url}"

    except Exception as e:
        print(f"  [Naver] 오류 발생: {e}")
        time.sleep(30)
        return f"Naver 블로그 발행 실패: {e}"
    finally:
        driver.quit()
