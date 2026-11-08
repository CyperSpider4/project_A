from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str
    cors_origins: list[str]


@lru_cache
def get_settings() -> Settings:
    return Settings()





# from dataclasses import dataclass


# @dataclass(frozen=True)
# class Settings:
#     DATABASE_URL: str
#     cors_origins: list[str]


# def get_settings() -> Settings:
#     return Settings(
#         DATABASE_URL="postgresql+psycopg://postgres:admin@127.0.0.1:5432/postgres",
#         cors_origins=["http://localhost:3000"]
#     )


