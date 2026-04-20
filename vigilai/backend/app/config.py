from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db: str = "vigilai"
    anthropic_api_key: str = ""
    jwt_secret: str = "vigilai-dev-secret"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480
    demo_officer_email: str = "officer@vigilai.demo"
    demo_officer_password: str = "demo2026"

    class Config:
        env_file = ".env"


settings = Settings()
