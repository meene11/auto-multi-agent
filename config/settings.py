from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    github_token: str = ""

    devto_api_key: str = ""

    hashnode_api_key: str = ""
    hashnode_publication_id: str = ""

    target_repo_url: str = "https://github.com/meene11/it-news-pipeline"
    seo_score_threshold: int = 70

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
