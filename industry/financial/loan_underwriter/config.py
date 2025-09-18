from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    backend_url: str
    loan_parser_url: str
    credit_analyzer_url: str
    risk_assessor_url: str
    flotorch_api_key: str
    flotorch_model: str
    flotorch_endpoint: str

    class Config:
        env_file = ".env"

settings = Settings()