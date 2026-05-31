from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_CORS_ORIGINS = ",".join(
    [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]
)


class Settings(BaseSettings):
    app_name: str = "social-video-rag-api"
    env: str = "development"
    openai_api_key: str = ""
    google_api_key: str = ""
    chroma_dir: str = "./storage/chroma"
    instagram_cookies_file: str = ""
    cors_origins: str = DEFAULT_CORS_ORIGINS

    @property
    def allowed_cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
