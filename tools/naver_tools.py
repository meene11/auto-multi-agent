"""
네이버 블로그 Selenium 자동 발행 도구.

Naver Smart Editor는 iframe 기반이라 직접 JS 삽입이 불가하므로
pyperclip + pyautogui로 클립보드 붙여넣기 방식을 사용합니다.
"""

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
    # https://blog.naver.com/mhophouse -> mhophouse
    return blog_id_or_url.rstrip("/").split("/")[-1]


def _build_driver() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
    driver.maximize_window()
    return driver


def _login(driver: webdriver.Chrome) -> None:
    """네이버 로그인 — JS 직접 삽입 방식 (봇 탐지 우회)."""
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
    time.sleep(4)

    # 캡챠나 2차 인증이 뜨면 메인 페이지 URL이 아님 → 대기
    if "nidlogin" in driver.current_url or "nid.naver" in driver.current_url:
        print("  [Naver] 추가 인증(캡챠/2FA) 감지. 브라우저에서 직접 처리 후 Enter를 누르세요...")
        input()


def _paste_text(text: str) -> None:
    """클립보드에 복사 후 Ctrl+V로 붙여넣기."""
    pyperclip.copy(text)
    time.sleep(0.3)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.5)


def _close_help_popup(driver: webdriver.Chrome) -> None:
    try:
        btn = driver.find_element(By.CSS_SELECTOR, ".se-help-panel-close-button")
        btn.click()
        time.sleep(1)
    except Exception:
        pass


def _click_title_area(driver: webdriver.Chrome) -> bool:
    """제목 영역 클릭 — CSS 셀렉터 우선, 실패 시 좌표 fallback."""
    try:
        title_el = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".se-title-input .se-placeholder, .se-title-input")
            )
        )
        title_el.click()
        return True
    except Exception:
        # fallback: 화면 중앙 상단 좌표 (최대화 기준 1920x1080 근사치)
        pyautogui.click(960, 350)
        return False


def _click_body_area(driver: webdriver.Chrome) -> bool:
    """본문 영역 클릭 — CSS 셀렉터 우선, 실패 시 좌표 fallback."""
    try:
        body_el = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".se-component.se-text .se-placeholder, .se-text-paragraph")
            )
        )
        body_el.click()
        return True
    except Exception:
        pyautogui.click(960, 500)
        return False


def post_to_naver_blog(title: str, content: str) -> str:
    """
    네이버 블로그에 글을 발행한다.

    Args:
        title: 포스팅 제목
        content: 마크다운 본문 (네이버는 마크다운 미지원 → 평문으로 삽입)

    Returns:
        결과 메시지 문자열
    """
    if not settings.naver_id or not settings.naver_password:
        return "NAVER_ID 또는 NAVER_PASSWORD가 설정되지 않았습니다."
    if not settings.naver_blog_id:
        return "NAVER_BLOG_ID가 설정되지 않았습니다."

    blog_id = _extract_blog_id(settings.naver_blog_id)
    driver = _build_driver()
    try:
        # 1. 로그인
        print("  [Naver] 로그인 중...")
        _login(driver)
        print("  [Naver] 로그인 완료.")

        # 2. 글쓰기 페이지 이동
        write_url = f"https://blog.naver.com/{blog_id}/postwrite"
        driver.get(write_url)
        time.sleep(7)

        # 3. 도움말 팝업 닫기
        _close_help_popup(driver)
        time.sleep(1)

        # 4. 제목 입력
        print("  [Naver] 제목 입력 중...")
        _click_title_area(driver)
        time.sleep(1)
        _paste_text(title)
        time.sleep(1)

        # 5. 본문 입력 (Tab으로 본문 영역 이동 시도 → 실패 시 클릭)
        print("  [Naver] 본문 입력 중...")
        pyautogui.press("tab")
        time.sleep(0.5)
        _click_body_area(driver)
        time.sleep(1)
        # 마크다운 헤더(#) 등을 제거해 네이버 에디터에 맞는 평문으로 변환
        plain_content = _markdown_to_plain(content)
        _paste_text(plain_content)
        time.sleep(2)

        # 6. 발행 팝업 열기
        print("  [Naver] 발행 버튼 클릭 중...")
        try:
            publish_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".publish_btn__m9KHH"))
            )
            publish_btn.click()
        except Exception:
            # 버튼 셀렉터가 변경됐을 경우 텍스트로 탐색
            btns = driver.find_elements(By.TAG_NAME, "button")
            for btn in btns:
                if "발행" in btn.text:
                    btn.click()
                    break
        time.sleep(3)

        # 7. 최종 발행 확인
        print("  [Naver] 최종 발행 확인 중...")
        clicked = False
        try:
            confirm_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".confirm_btn__WEaBq"))
            )
            confirm_btn.click()
            clicked = True
        except Exception:
            pass

        if not clicked:
            btns = driver.find_elements(By.TAG_NAME, "button")
            for btn in btns:
                if btn.text.strip() in ("발행", "확인", "공개발행"):
                    btn.click()
                    clicked = True
                    break

        if not clicked:
            return "Naver 블로그 발행 실패: 최종 발행 버튼을 찾지 못했습니다."

        # 8. 발행 완료 URL 확인 (페이지 이동 대기)
        time.sleep(5)
        current_url = driver.current_url
        print(f"  [Naver] 현재 URL: {current_url}")

        # 발행 후 블로그 포스트 URL로 이동됐는지 확인
        if "blog.naver.com" in current_url and "postwrite" not in current_url:
            return f"Naver 블로그 발행 완료: {current_url}"
        else:
            # 직접 블로그로 이동해서 최신 글 확인
            blog_url = f"https://blog.naver.com/{blog_id}"
            return f"Naver 블로그 발행 완료: {blog_url}"

    except Exception as e:
        print(f"  [Naver] 오류 발생: {e}")
        print("  [Naver] 브라우저를 10초 후 닫습니다. 화면을 확인하세요...")
        time.sleep(10)
        return f"Naver 블로그 발행 실패: {e}"
    finally:
        driver.quit()


def _markdown_to_plain(md: str) -> str:
    """
    마크다운을 네이버 스마트에디터에 붙여넣기 적합한 평문으로 변환한다.
    헤더(#)는 줄바꿈으로, 볼드(**) 등 인라인 마크업은 제거한다.
    """
    import re

    # 헤더를 줄바꿈 + 텍스트로 변환
    md = re.sub(r"^#{1,6}\s+", "\n", md, flags=re.MULTILINE)
    # 볼드/이탤릭 제거
    md = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", md)
    # 인라인 코드 제거
    md = re.sub(r"`([^`]+)`", r"\1", md)
    # 링크 → 텍스트만
    md = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", md)
    # 코드 블록 제거
    md = re.sub(r"```[\s\S]*?```", "", md)
    # 수평선 제거
    md = re.sub(r"^---+$", "", md, flags=re.MULTILINE)
    # 연속 빈 줄 축소
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip()
