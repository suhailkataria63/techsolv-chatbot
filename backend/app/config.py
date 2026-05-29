from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "social-video-rag-api"
    env: str = "development"
    openai_api_key: str = ""
    google_api_key: str = ""
    chroma_dir: str = "./storage/chroma"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
