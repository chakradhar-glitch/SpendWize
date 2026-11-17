from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SPENDWISE_", env_file=".env", extra="ignore"
    )

    database_url: SecretStr
    database_pool_size: int = Field(default=5, ge=1, le=50)
    database_max_overflow: int = Field(default=0, ge=0, le=50)

    @field_validator("database_url")
    @classmethod
    def postgresql_only(cls, value: SecretStr) -> SecretStr:
        try:
            url = make_url(value.get_secret_value())
            valid = url.drivername == "postgresql+psycopg" and bool(url.database)
        except Exception:
            valid = False
        if not valid:
            raise ValueError("A postgresql+psycopg database URL is required")
        return value
