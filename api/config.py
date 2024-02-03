
from pydantic_core import Url
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    STABLE_HORDE_URL: Url
    ANON_API_KEY: str

    model_config = SettingsConfigDict(
        env_prefix="api_",
        env_file=".env.local"
        )


settings = Settings()