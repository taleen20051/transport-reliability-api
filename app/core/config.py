from pydantic_settings import BaseSettings, SettingsConfigDict

# Central application settings loaded from environment variables.
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

# Create one shared settings object for use across the application.
settings = Settings()