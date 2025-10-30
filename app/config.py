from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    MYSQL_HOST: str = "127.0.0.1"
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""  # Default empty, must be provided via environment variable
    MYSQL_DB: str = "ecommerce"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Try to get password from environment variable
mysql_password = os.getenv("MYSQL_PASSWORD")
if not mysql_password:
    raise ValueError("MYSQL_PASSWORD environment variable must be set")

settings = Settings(MYSQL_PASSWORD=mysql_password)
