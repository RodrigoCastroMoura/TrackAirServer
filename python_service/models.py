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
    """Informações do veículo - igual ao C#."""
    _id: Optional[str] = None
    IMEI: str
    Cpf: Optional[str] = None
    id_marca: Optional[int] = None
    id_rastreador: Optional[str] = None
    id_status: Optional[int] = None
    ds_placa: Optional[str] = None
    ds_modelo: Optional[str] = None
    nm_ano: Optional[int] = None
    nm_modelo: Optional[int] = None
    nm_chip: Optional[str] = None
    avisoBloqueio: Optional[bool] = None
    comandoBloqueo: Optional[bool] = None  # True = comando para bloquear
    bloqueado: Optional[bool] = None       # True = já está bloqueado
    auxBloqueado: Optional[bool] = None
    comandoTempo: Optional[bool] = None
    tempoIgnicaoON: Optional[str] = None
    tempoIgnicaoOFF: Optional[str] = None
    ignicao: bool = False
    cd_user_cadm: Optional[str] = None
    ts_user_cadm: Optional[datetime] = None
    cd_user_manu: Optional[str] = None
    ts_user_manu: Optional[datetime] = Field(default_factory=datetime.utcnow)