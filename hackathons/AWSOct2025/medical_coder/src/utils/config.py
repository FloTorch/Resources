from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    flotorch_api_key: str
    flotorch_base_url: str
    aws_api_key: str
    pinecone_api_key: str


settings = Settings() # type: ignore