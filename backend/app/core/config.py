import secrets
import warnings
from typing import Annotated, Any, Literal

from pydantic import (
    AnyUrl,
    BeforeValidator,
    HttpUrl,
    MySQLDsn,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 3 hours
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 3
    FRONTEND_HOST: str = "http://localhost:5173"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    PROJECT_NAME: str
    # todo: also uncomment the validator second last
    MYSQL_SERVER: str
    MYSQL_PORT: int = 3306
    MYSQL_USER: str
    MYSQL_PASSWORD: str = ""
    MYSQL_DB: str = ""
    SQLITE_DB_FILE: str = ""
    # todo: for unique users
    FIRST_SUPERUSER: str
    FIRST_SUPERUSER_PASSWORD: str
    # todo: RAG_Layer DB
    RAG_LAYER_DIR: str = "../RAG-Layer"
    # Ollama
    OLLAMA_MODEL: str
    OLLAMA_HOST: str

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> MySQLDsn:
        return MySQLDsn.build(
            scheme="mysql+pymysql",
            username=self.MYSQL_USER,
            password=self.MYSQL_PASSWORD,
            host=self.MYSQL_SERVER,
            port=self.MYSQL_PORT,
            path=f"{self.MYSQL_DB}",  # Ensure the path starts with "/"
        )

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("MYSQL_PASSWORD", self.MYSQL_PASSWORD)
        self._check_default_secret(
            "FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD
        )

        return self

    def print_all_setting(self) -> None:
        settings_dict = self.dict()
        for key, value in settings_dict.items():
            print(f"{key}: {value}")


settings = Settings()  # type: ignore
# settings.print_all_setting()