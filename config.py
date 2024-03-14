import datetime
from pydantic import BaseSettings, AnyHttpUrl
from typing import Optional
import pathlib
import os

env_name = os.getenv("ACTIVE_ENVIRONMENT")


class Settings(BaseSettings):
    DB_API: AnyHttpUrl
    DB_NAME: str
    DB_REGION: str
    INITIAL_TIMEOUT_MINUTES: datetime.timedelta
    STATUS_URL: AnyHttpUrl
    WEB_SOCKET_API: AnyHttpUrl

    class Config:
        print(pathlib.Path(__file__).resolve().parents[0])
        env_file = pathlib.Path.joinpath(pathlib.Path(__file__).resolve().parents[0], f"configs/{env_name}.env")
        print(env_file)


if __name__ == "__main__":
    settings = Settings()
    print(settings.dict())
