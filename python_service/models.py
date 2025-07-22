from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class DadosVeiculo(BaseModel):
    """Dados de rastreamento do veículo - todos os protocolos GPS."""
    _id: Optional[str] = None
    IMEI: str
    longitude: str
    latitude: str
    altidude: str  # mantendo mesmo nome que no C#
    speed: str
    ignicao: Optional[bool] = None
    data: Optional[datetime] = None
    dataDevice: str
    # Campos para todos os protocolos GPS
    protocol_type: str  # GTFRI, GTIGN, GTIGF, GTIGL, GTOUT, GTSRI, GTBSI
    raw_message: Optional[str] = None  # Mensagem original completa
    # Campos específicos para bateria (GTIGL)
    bateria_voltagem: Optional[float] = None
    bateria_baixa: Optional[bool] = False
    # Campos para eventos especiais
    evento_ignicao: Optional[bool] = False  # True se for evento de ignição
    comando_executado: Optional[str] = None  # Para GTOUT, GTSRI
    # Campos para informação celular (GTBSI)
    cell_id: Optional[str] = None
    lac_code: Optional[str] = None

class Veiculo(BaseModel):
    """Informações do veículo - simplificado para clean code."""
    _id: Optional[str] = None
    IMEI: str
    ds_placa: Optional[str] = None  # Placa do veículo
    ds_modelo: Optional[str] = None  # Modelo do veículo
    comandoBloqueo: Optional[bool] = None  # True = bloquear, False = desbloquear, None = sem comando
    bloqueado: Optional[bool] = False  # Status atual de bloqueio
    comandoTrocarIP: Optional[bool] = None  # True = comando para trocar IP pendente
    ignicao: bool = False  # Status da ignição
    # Campos para monitoramento de bateria
    bateria_voltagem: Optional[float] = None  # Voltagem atual da bateria
    bateria_baixa: Optional[bool] = False  # True se bateria estiver baixa
    ultimo_alerta_bateria: Optional[datetime] = None  # Timestamp do último alerta
    ts_user_manu: Optional[datetime] = Field(default_factory=datetime.utcnow)  # Última atualização