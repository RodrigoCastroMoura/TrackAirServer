from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum

class MessageType(str, Enum):
    RESP = "+RESP"
    BUFF = "+BUFF"
    ACK = "+ACK"

class CommandType(str, Enum):
    GTFRI = "GTFRI"  # Fixed Report Information
    GTIGN = "GTIGN"  # Ignition On
    GTIGF = "GTIGF"  # Ignition Off  
    GTOUT = "GTOUT"  # Output Control
    GTSRI = "GTSRI"  # Server Registration Info
    GTBSI = "GTBSI"  # Bearer Setting Info

class DeviceStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    BLOCKED = "blocked"

class VehicleData(BaseModel):
    """Vehicle tracking data model."""
    id: Optional[str] = Field(default=None, alias="_id")
    imei: str = Field(..., description="Device IMEI")
    longitude: Optional[str] = Field(default=None)
    latitude: Optional[str] = Field(default=None)
    altitude: Optional[str] = Field(default=None)
    speed: Optional[str] = Field(default=None)
    ignition: Optional[bool] = Field(default=None)
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    device_time: Optional[str] = Field(default=None)
    raw_data: Optional[str] = Field(default=None)
    
    class Config:
        allow_population_by_field_name = True

class Vehicle(BaseModel):
    """Vehicle model."""
    id: Optional[str] = Field(default=None, alias="_id")
    imei: str = Field(..., description="Device IMEI")
    cpf: Optional[str] = Field(default=None)
    plate: Optional[str] = Field(default=None, alias="ds_placa")
    ignition: Optional[bool] = Field(default=None)
    blocked: Optional[bool] = Field(default=False)
    block_command_pending: Optional[bool] = Field(default=False, alias="comandoBloqueo")
    block_warning_sent: Optional[bool] = Field(default=False, alias="avisoBloqueio")
    tracker_model: Optional[str] = Field(default=None)
    tracker_password: Optional[str] = Field(default=None)
    status: DeviceStatus = Field(default=DeviceStatus.OFFLINE)
    last_seen: Optional[datetime] = Field(default=None)
    
    class Config:
        allow_population_by_field_name = True

class Message(BaseModel):
    """System message model."""
    id: Optional[str] = Field(default=None, alias="_id")
    cpf: Optional[str] = Field(default=None)
    imei: Optional[str] = Field(default=None)
    message_type_id: int = Field(..., alias="id_tipo_Mensagem")
    message: str = Field(..., alias="ds_mensagem")
    message_html: Optional[str] = Field(default=None, alias="ds_mensagemHtml")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow, alias="dt_mensagem")
    read: Optional[bool] = Field(default=False, alias="fl_lida")
    
    class Config:
        allow_population_by_field_name = True

class Command(BaseModel):
    """Device command model."""
    id: Optional[str] = Field(default=None, alias="_id")
    imei: str = Field(..., description="Target device IMEI")
    command_type: str = Field(..., description="Command type (GTOUT, GTSRI, etc.)")
    command_data: str = Field(..., description="Full command string")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    status: str = Field(default="pending")  # pending, sent, acknowledged, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = Field(default=None)
    acknowledged_at: Optional[datetime] = Field(default=None)
    retry_count: int = Field(default=0)
    max_retries: int = Field(default=3)
    timeout_seconds: int = Field(default=30)
    
    class Config:
        allow_population_by_field_name = True

class DeviceConfiguration(BaseModel):
    """Device network configuration model."""
    id: Optional[str] = Field(default=None, alias="_id")
    imei: str = Field(..., description="Device IMEI")
    server_ip: Optional[str] = Field(default=None)
    server_port: Optional[int] = Field(default=None)
    server_domain: Optional[str] = Field(default=None)
    apn_name: Optional[str] = Field(default=None)
    apn_username: Optional[str] = Field(default=None)
    apn_password: Optional[str] = Field(default=None)
    report_interval: Optional[int] = Field(default=None)  # seconds
    heartbeat_interval: Optional[int] = Field(default=None)  # seconds
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    applied_at: Optional[datetime] = Field(default=None)
    
    class Config:
        allow_population_by_field_name = True

class ParsedMessage(BaseModel):
    """Parsed protocol message."""
    message_type: MessageType
    command_type: CommandType
    imei: str
    parameters: List[str]
    raw_data: str
    parsed_at: datetime = Field(default_factory=datetime.utcnow)
