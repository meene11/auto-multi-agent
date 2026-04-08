import httpx
import base64
from langchain_core.tools import tool
from config.settings import settings


def _github_headers() -> dict:
    headers = {"Accept": "application/vnd.github+json"}
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"
    return headers


def _parse_owner_repo(repo_url: str) -> tuple[str, str]:
    """https://github.com/owner/repo 형태에서 owner, repo 추출"""
    parts = repo_url.rstrip("/").rstrip(".git").split("/")
    return parts[-2], parts[-1]


@tool
def fetch_github_readme(repo_url: str) -> str:
    """GitHub 레포지토리의 README 전문을 가져온다."""
    owner, repo = _parse_owner_repo(repo_url)
    url = f"https://api.github.com/repos/{owner}/{repo}/readme"

    response = httpx.get(url, headers=_github_headers(), timeout=10)
    if response.status_code != 200:
        return f"README를 가져오지 못했습니다. (status: {response.status_code})"

    content = response.json().get("content", "")
    decoded = base64.b64decode(content).decode("utf-8")
    return decoded


@tool
def analyze_code_structure(repo_url: str) -> str:
    """GitHub 레포지토리의 파일/폴더 구조를 가져온다."""
    owner, repo = _parse_owner_repo(repo_url)
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/HEAD?recursive=1"

    response = httpx.get(url, headers=_github_headers(), timeout=10)
    if response.status_code != 200:
        return f"구조를 가져오지 못했습니다. (status: {response.status_code})"

    tree = response.json().get("tree", [])
    paths = [item["path"] for item in tree if item["type"] == "blob"]

    # 주요 파일만 추려서 반환 (최대 50개)
    result = "\n".join(paths[:50])
    return f"파일 구조:\n{result}"
