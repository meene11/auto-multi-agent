from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str
    github_token: str = ""

    tistory_access_token: str = ""
    tistory_blog_name: str = ""

    naver_client_id: str = ""
    naver_client_secret: str = ""
    naver_access_token: str = ""

    target_repo_url: str = "https://github.com/meene11/it-news-pipeline"
    seo_score_threshold: int = 70

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
