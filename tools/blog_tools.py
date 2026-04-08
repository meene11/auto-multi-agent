import re
import httpx
from langchain_core.tools import tool
from config.settings import settings


def _to_devto_tag(tag: str) -> str:
    """dev.to용 태그 변환 — 영문+숫자만 허용 (하이픈 불가)"""
    tag_map = {
        "AI": "ai", "인공지능": "ai", "머신러닝": "machinelearning",
        "딥러닝": "deeplearning", "파이썬": "python", "파이프라인": "pipeline",
        "데이터": "data", "자동화": "automation", "뉴스": "news",
        "분석": "analytics", "감성": "sentiment", "트렌드": "trending",
        "시각화": "dataviz", "크롤링": "webscraping", "백엔드": "backend",
        "프론트엔드": "frontend", "데이터베이스": "database", "클라우드": "cloud",
        "서버": "server", "API": "api", "개발": "dev", "프로젝트": "project",
    }
    for kor, eng in tag_map.items():
        tag = tag.replace(kor, eng)
    # 영문+숫자만 남기고 소문자화
    result = re.sub(r"[^a-zA-Z0-9]", "", tag).lower()
    return result or "dev"


def _to_hashnode_slug(tag: str) -> str:
    """Hashnode용 태그 slug 변환 — 영문+숫자+하이픈 허용"""
    tag_map = {
        "AI": "ai", "인공지능": "ai", "머신러닝": "machine-learning",
        "딥러닝": "deep-learning", "파이썬": "python", "파이프라인": "pipeline",
        "데이터": "data", "자동화": "automation", "뉴스": "news",
        "분석": "analytics", "감성": "sentiment", "트렌드": "trend",
        "시각화": "visualization", "크롤링": "crawling", "백엔드": "backend",
        "프론트엔드": "frontend", "데이터베이스": "database", "클라우드": "cloud",
        "서버": "server", "API": "api", "개발": "dev", "프로젝트": "project",
    }
    for kor, eng in tag_map.items():
        tag = tag.replace(kor, eng)
    slug = re.sub(r"[^a-zA-Z0-9\s-]", "", tag)
    slug = slug.strip().lower().replace(" ", "-")
    slug = re.sub(r"-+", "-", slug)
    return slug or "dev"


@tool
def post_to_devto(title: str, content: str, tags: list[str], published: bool = True) -> str:
    """dev.to에 블로그 포스트를 발행한다."""
    if not settings.devto_api_key:
        return "DEVTO_API_KEY가 설정되지 않았습니다."

    url = "https://dev.to/api/articles"
    headers = {
        "api-key": settings.devto_api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "article": {
            "title": title,
            "body_markdown": content,
            "tags": [_to_devto_tag(t) for t in tags[:4]],
            "published": published,
        }
    }

    response = httpx.post(url, json=payload, headers=headers, timeout=15)
    if response.status_code in (200, 201):
        data = response.json()
        return f"dev.to 발행 완료: {data.get('url', '')}"
    return f"dev.to 발행 실패 (status: {response.status_code}): {response.text}"


@tool
def post_to_hashnode(title: str, content: str, tags: list[str]) -> str:
    """Hashnode에 블로그 포스트를 발행한다."""
    if not settings.hashnode_api_key:
        return "HASHNODE_API_KEY가 설정되지 않았습니다."
    if not settings.hashnode_publication_id:
        return "HASHNODE_PUBLICATION_ID가 설정되지 않았습니다."

    url = "https://gql.hashnode.com"
    headers = {
        "Authorization": settings.hashnode_api_key,
        "Content-Type": "application/json",
    }
    tag_list = [{"name": _to_hashnode_slug(t), "slug": _to_hashnode_slug(t)} for t in tags[:5]]
    query = """
    mutation PublishPost($input: PublishPostInput!) {
      publishPost(input: $input) {
        post {
          url
          title
        }
      }
    }
    """
    variables = {
        "input": {
            "title": title,
            "contentMarkdown": content,
            "tags": tag_list,
            "publicationId": settings.hashnode_publication_id,
        }
    }

    response = httpx.post(url, json={"query": query, "variables": variables}, headers=headers, timeout=15)
    if response.status_code == 200:
        data = response.json()
        if "errors" in data:
            return f"Hashnode 발행 실패: {data['errors']}"
        post_url = data.get("data", {}).get("publishPost", {}).get("post", {}).get("url", "")
        return f"Hashnode 발행 완료: {post_url}"
    return f"Hashnode 발행 실패 (status: {response.status_code}): {response.text}"
