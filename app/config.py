from functools import lru_cache

from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="allow")

    # Mysql
    MYSQL_SCHEME: str
    MYSQL_HOST: str
    MYSQL_PORT: int
    MYSQL_DATABASE: str
    MYSQL_USER: str
    MYSQL_PASSWORD: str

    # Redis
    REDIS_SCHEME: str
    REDIS_HOST: str
    REDIS_PORT: int

    # Auth
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    TOKEN_TYPE: str = "Bearer"
    ACCESS_TOKEN_EXPIRES_SECONDS: int = 15 * 60  # 15분
    REFRESH_TOKEN_EXPIRES_SECONDS: int = 7 * 24 * 60 * 60  # 7일
    REFRESH_TOKEN_COOKIE_KEY: str = "refresh_token"
    REDIS_BLACKLIST_KEY: str = "blacklist"
    REDIS_TOKEN_KEY: str = "token"

    @property
    def MYSQL_URL(self) -> str:
        return str(
            AnyUrl.build(
                scheme=self.MYSQL_SCHEME,
                username=self.MYSQL_USER,
                password=self.MYSQL_PASSWORD,
                host=self.MYSQL_HOST,
                port=self.MYSQL_PORT,
                path=self.MYSQL_DATABASE,
                query="charset=utf8mb4",
            )
        )

    @property
    def REDIS_URL(self) -> str:
        return str(
            AnyUrl.build(scheme=self.REDIS_SCHEME, host=self.REDIS_HOST, port=self.REDIS_PORT)
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type:ignore


settings = get_settings()
