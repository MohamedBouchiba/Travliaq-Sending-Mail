from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, Field


class Settings(BaseSettings):
    supabase_url: AnyHttpUrl = Field(alias="SUPABASE_URL")
    supabase_service_key: str = Field(alias="SUPABASE_SERVICE_KEY")
    resend_api_key: str = Field(alias="RESEND_API_KEY")
    email_from: str = Field(alias="EMAIL_FROM")
    llm_api_key: str = Field(alias="OPEN_ROUTER_SK")
    llm_model_name: str = Field(alias="LLM_MODEL_NAME")
    frontend_trip_base_url: AnyHttpUrl = Field(alias="FRONTEND_TRIP_BASE_URL")
    env: str = Field(default="DEV", alias="ENV")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
