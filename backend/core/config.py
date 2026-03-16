from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str = "super-secret-key-change-it"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    
    yandex_smtp_host: str = "smtp.yandex.ru"
    yandex_smtp_port: int = 465
    yandex_smtp_user: str = ""
    yandex_smtp_password: str = ""
    
    storage_dir: str = "./storage"
    database_url: str = "sqlite:///./abox.db"

    class Config:
        env_file = ".env"

settings = Settings()
