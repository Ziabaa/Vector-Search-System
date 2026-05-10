from pathlib import Path
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)


class BaseSystemSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(env_path),
        env_file_encoding="utf-8",
        extra="ignore",
    )


class ApiConfig(BaseSystemSettings):
    host: str = Field(validation_alias="APP_HOST")
    port: str = Field(validation_alias="APP_PORT")


class DataBaseConfig(BaseSystemSettings):
    server: str = Field(validation_alias="DB_SERVER")
    user: str = Field(validation_alias="DB_USER")
    password: str = Field(validation_alias="DB_PASSWORD")
    database: str = Field(validation_alias="DB_DATABASE")


class WeaviateConfig(BaseSystemSettings):
    host: str = Field(validation_alias="VECTOR_HTTP_HOST")
    port: str = Field(validation_alias="VECTOR_HTTP_PORT")
    grpc_port: str = Field(validation_alias="VECTOR_GRPC_PORT")
    grpc_host: str = Field(validation_alias="VECTOR_GRPC_HOST")


class TelegramLoggingConfig(BaseSystemSettings):
    bot_token: str = Field(validation_alias="TELEGRAM_LOGGER_BOT_TOKEN")
    chat_id: str = Field(validation_alias="TELEGRAM_LOGGER_BOT_CHAT")


class AiProvidersConfig(BaseSystemSettings):
    openai_key: str = Field(validation_alias="OPENAI_API_KEY")


class AuthorisationConfig(BaseSystemSettings):
    WEAVIATE_AUTHORISATION_KEY: str = Field(validation_alias="WEAVIATE_AUTHORISATION_KEY")
    SERPAPI_KEY: str = Field(validation_alias="SERPAPI_KEY")
    OPEN_WEATHER_MAP_KEY: str = Field(validation_alias="OPEN_WEATHER_MAP_KEY")


class Settings(BaseSystemSettings):
    api: ApiConfig = Field(default_factory=ApiConfig)
    database: DataBaseConfig = Field(default_factory=DataBaseConfig)
    weaviate: WeaviateConfig = Field(default_factory=WeaviateConfig)
    telegram_logging: TelegramLoggingConfig = Field(default_factory=TelegramLoggingConfig)
    ai_providers: AiProvidersConfig = Field(default_factory=AiProvidersConfig)
    authorisation: AuthorisationConfig = Field(default_factory=AuthorisationConfig)


settings = Settings()
