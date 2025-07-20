import os
from typing import Optional
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

load_dotenv()

class Config(BaseSettings):
    """Configuration settings for the GPS tracking service."""
    
    # MongoDB Configuration
    mongodb_url: str = Field(default="mongodb://localhost:27017", env="MONGODB_URL")
    mongodb_database: str = Field(default="gps_tracking_service", env="MONGODB_DATABASE")
    
    # TCP Server Configuration
    tcp_host: str = Field(default="0.0.0.0", env="TCP_HOST")
    tcp_port: int = Field(default=8000, env="TCP_PORT")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/gps_service.log", env="LOG_FILE")
    
    # Service Configuration
    max_connections: int = Field(default=1000, env="MAX_CONNECTIONS")
    command_timeout: int = Field(default=30, env="COMMAND_TIMEOUT")
    device_timeout: int = Field(default=300, env="DEVICE_TIMEOUT")
    
    class Config:
        env_file = ".env"

config = Config()
