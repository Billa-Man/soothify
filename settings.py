from pydantic_settings import BaseSettings, SettingsConfigDict

# class Settings(BaseSettings):
#   model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


class Settings(BaseSettings):
  model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

  # OpenAI API
  OPENAI_MODEL_ID: str = "gpt-4o-mini"
  OPENAI_API_KEY: str | None = "YOUR_OPENAI_API_KEY"

  # MongoDB database
  DATABASE_HOST: str = "YOUR_MONGODB_DATABASE_HOST"
  DATABASE_NAME: str = "YOUR_MONGODB_DATABASE_NAME"

  # Hume AI
  HUME_API_KEY: str = "YOUR_HUME_API_KEY"
  HUME_SECRET_KEY: str = "YOUR_HUME_SECRET_KEY"
  HUME_CONFIG_ID: str = "YOUR_HUME_CONFIG_ID"

settings = Settings()