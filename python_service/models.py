from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class DadosVeiculo(BaseModel):
    """Dados de rastreamento do veículo - igual ao C#."""
    _id: Optional[str] = None
    IMEI: str
    longitude: str
    latitude: str
    altidude: str  # mantendo mesmo nome que no C#
    speed: str
    ignicao: Optional[bool] = None
    data: Optional[datetime] = None
    dataDevice: str

class Veiculo(BaseModel):
    """Informações do veículo - simplificado para clean code."""
    _id: Optional[str] = None
    IMEI: str
    ds_placa: Optional[str] = None  # Placa do veículo
    ds_modelo: Optional[str] = None  # Modelo do veículo
    comandoBloqueo: Optional[bool] = None  # True = bloquear, False = desbloquear, None = sem comando
    bloqueado: Optional[bool] = False  # Status atual de bloqueio
    ignicao: bool = False  # Status da ignição
    ts_user_manu: Optional[datetime] = Field(default_factory=datetime.utcnow)  # Última atualização