from tools.blog_tools import post_to_devto, post_to_hashnode
from config.settings import settings


def run_publisher(title: str, content: str, tags: list[str]) -> dict:
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
    if settings.naver_id and settings.naver_password and settings.naver_blog_id:
        print(f"  [Naver] 발행 중... (브라우저 자동화)")
        from tools.naver_tools import post_to_naver_blog
        naver_result = post_to_naver_blog(title=title, content=content)
    else:
        print(f"  [Naver] NAVER_ID/PASSWORD/BLOG_ID 미설정, 건너뜀.")

    return {
        "devto": devto_result,
        "hashnode": hashnode_result,
        "naver": naver_result,
    }
