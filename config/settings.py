from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    github_token: str = ""

    supabase_url: str = ""
    supabase_key: str = ""
    supabase_table: str = "news_list"

    devto_api_key: str = ""

    hashnode_api_key: str = ""
    hashnode_publication_id: str = ""

    target_repo_url: str = "https://github.com/meene11/it-news-pipeline"
    seo_score_threshold: int = 70
    articles_per_run: int = 5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
