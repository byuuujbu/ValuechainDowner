from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "OVSA API"
    environment: str = "local"
    postgres_db: str = "ovsa"
    postgres_user: str = "ovsa"
    postgres_password: str = "ovsa_dev_password"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
