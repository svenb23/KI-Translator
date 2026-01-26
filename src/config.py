from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    deepl_api_key: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
