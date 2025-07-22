import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Config(BaseSettings):
    """Configuration settings for the GPS tracking service."""
    
    # MongoDB Configuration
    mongodb_url: str = Field(default="mongodb://localhost:27017")
    mongodb_database: str = Field(default="gps_tracking_service")
    
    # TCP Server Configuration
    tcp_host: str = Field(default="0.0.0.0")
    tcp_port: int = Field(default=8000)
    
    # Logging Configuration
    log_level: str = Field(default="INFO")
    log_file: str = Field(default="logs/gps_service.log")
    
    # Service Configuration - Long Connection Mode
    max_connections: int = Field(default=1000)
    command_timeout: int = Field(default=30)
    device_timeout: int = Field(default=1800)  # 30 min para long-connection
    heartbeat_interval: int = Field(default=300)  # 5 min heartbeat  
    keep_alive_timeout: int = Field(default=600)  # 10 min keep-alive
    connection_mode: str = Field(default="long-connection")  # Modo de conexão GV50
    
    # IP Configuration for devices
    new_server_ip: str = Field(default="")
    new_server_port: int = Field(default=8000)
    backup_server_ip: str = Field(default="")
    backup_server_port: int = Field(default=8000)
    
    class Config:
        env_file = ".env"

def get_settings():
    return Config()

config = get_settings()
