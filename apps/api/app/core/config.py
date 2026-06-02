from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "OVSA API"
    environment: str = "local"
    postgres_db: str = "ovsa"
    postgres_user: str = "ovsa"
    postgres_password: str = "ovsa_dev_password"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    data_provider_mode: str = "sample"
    fmp_api_key: str | None = None
    fmp_base_url: str = "https://financialmodelingprep.com/stable"
    sec_company_tickers_url: str = "https://www.sec.gov/files/company_tickers.json"
    sec_companyfacts_url_template: str = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    sec_user_agent: str | None = None
    display_usd_krw_rate: str | None = None

    model_config = SettingsConfigDict(env_file=("../../.env", ".env"), extra="ignore")


settings = Settings()


def get_database_url() -> str:
    return (
        "postgresql+psycopg://"
        f"{settings.postgres_user}:{settings.postgres_password}"
        f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
    )
