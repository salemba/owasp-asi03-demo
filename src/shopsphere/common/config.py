from __future__ import annotations

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Base settings shared by all components."""

    model_config = SettingsConfigDict(env_prefix="SHOPSPHERE_", env_file=".env", extra="ignore")

    service_name: str = "shopsphere"
    environment: str = "dev"
    vuln_profile: bool = True
    log_level: str = "INFO"

    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "shopsphere"
    database_user: str = "shopsphere"
    database_password: SecretStr

    openai_api_key: SecretStr
    anthropic_api_key: SecretStr

    llm_provider: str = "mock"
    telemetry_enabled: bool = True
    otel_exporter_otlp_endpoint: str = "http://localhost:4317"

    @property
    def database_dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.database_user}:{self.database_password.get_secret_value()}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )
