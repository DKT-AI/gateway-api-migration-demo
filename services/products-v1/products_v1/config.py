from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    service_name: str = "products-v1"
    service_version: str = "1.0.0"
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000


settings = Settings()
