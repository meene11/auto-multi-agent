from tools.blog_tools import post_to_devto, post_to_hashnode
from tools.supabase_tools import mark_as_published
from config.settings import settings


def run_publisher(title: str, content: str, tags: list[str], article_ids: list[int] = None, skip_naver: bool = False) -> dict:
    """
    dev.to, Hashnode, 네이버 블로그에 동시 발행한다.
    반환값: { devto: "...", hashnode: "...", naver: "..." }
    """
    print(f"  [dev.to] 발행 중...")
    devto_result = post_to_devto.invoke({
        "title": title,
        "content": content,
        "tags": tags,
        "published": True,
    })

    print(f"  [Hashnode] 발행 중...")
    hashnode_result = post_to_hashnode.invoke({
        "title": title,
        "content": content,
        "tags": tags,
    })

    naver_result = "-"
    if skip_naver:
        print(f"  [Naver] 스케줄 모드 - 건너뜀.")
    elif settings.naver_id and settings.naver_password and settings.naver_blog_id:
        print(f"  [Naver] 발행 중... (브라우저 자동화)")
        from tools.naver_tools import post_to_naver_blog
        naver_result = post_to_naver_blog(title=title, content=content)
    else:
        print(f"  [Naver] NAVER_ID/PASSWORD/BLOG_ID 미설정, 건너뜀.")

    # 발행 완료된 기사 ID를 로컬 파일에 기록
    if article_ids:
        mark_as_published(article_ids)

    return {
        "devto": devto_result,
        "hashnode": hashnode_result,
        "naver": naver_result,
    }
