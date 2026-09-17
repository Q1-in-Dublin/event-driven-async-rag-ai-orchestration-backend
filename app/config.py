from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url : str
    redis_url : str
    slack_signing_secret:str
    api_key : str

    class config:
        env_file = ".env"

settings = Settings()