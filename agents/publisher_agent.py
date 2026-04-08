from tools.blog_tools import post_to_devto, post_to_hashnode


def run_publisher(title: str, content: str, tags: list[str]) -> dict:
    """
    dev.to와 Hashnode에 동시 발행한다.
    반환값: { devto: "url", hashnode: "url" }
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

    return {
        "devto": devto_result,
        "hashnode": hashnode_result,
    }
