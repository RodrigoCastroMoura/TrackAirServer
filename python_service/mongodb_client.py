#!/usr/bin/env python3
"""
Cliente MongoDB simplificado para apenas 2 tabelas: DadosVeiculo e Veiculo
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import Optional, List
from models import DadosVeiculo, Veiculo
from config import get_settings
from logger import get_logger

logger = get_logger(__name__)

class MongoDBClient:
    """Cliente MongoDB para gerenciar apenas DadosVeiculo e Veiculo."""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database = None
        self.settings = get_settings()
        
    async def connect(self):
        """Conecta ao MongoDB."""
        try:
            self.client = AsyncIOMotorClient(self.settings.mongodb_url)
            self.database = self.client[self.settings.mongodb_database]
            
            # Testar conexão
            await self.client.admin.command('ping')
            logger.info(f"Conectado ao MongoDB: {self.settings.mongodb_database}")
            
        except Exception as e:
            logger.error(f"Erro ao conectar MongoDB: {e}")
            raise
            
    async def disconnect(self):
        """Desconecta do MongoDB."""
        if self.client:
            self.client.close()
            logger.info("Desconectado do MongoDB")
            
    async def insert_dados_veiculo(self, dados: DadosVeiculo) -> str:
        """Insere dados GPS do veículo."""
        try:
            collection = self.database.dados_veiculo
            dados_dict = dados.dict(exclude={'_id'})
            dados_dict['data'] = datetime.utcnow()
            
            result = await collection.insert_one(dados_dict)
            logger.info(f"Dados inseridos para IMEI {dados.IMEI}: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Erro ao inserir dados do veículo: {e}")
            raise
            
    async def get_veiculo_by_imei(self, imei: str) -> Optional[Veiculo]:
        """Busca veículo por IMEI."""
        try:
            collection = self.database.veiculo
            result = await collection.find_one({"IMEI": imei})
            
            if result:
                result['_id'] = str(result['_id'])
                return Veiculo(**result)
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar veículo {imei}: {e}")
            return None
            
    async def update_veiculo(self, veiculo: Veiculo) -> bool:
        """Atualiza informações do veículo."""
        try:
            collection = self.database.veiculo
            veiculo_dict = veiculo.dict(exclude={'_id'})
            veiculo_dict['ts_user_manu'] = datetime.utcnow()
            
            result = await collection.update_one(
                {"IMEI": veiculo.IMEI},
                {"$set": veiculo_dict},
                upsert=True
            )
            
            logger.info(f"Veículo {veiculo.IMEI} atualizado")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar veículo {veiculo.IMEI}: {e}")
            return False
            
    async def set_comando_bloqueio(self, imei: str, bloquear: bool) -> bool:
        """Define comando de bloqueio/desbloqueio para o veículo."""
        try:
            collection = self.database.veiculo
            
            update_data = {
                "comandoBloqueo": bloquear,
                "ts_user_manu": datetime.utcnow()
            }
            
            result = await collection.update_one(
                {"IMEI": imei},
                {"$set": update_data},
                upsert=True
            )
            
            action = "bloqueio" if bloquear else "desbloqueio"
            logger.info(f"Comando de {action} definido para IMEI {imei}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao definir comando para {imei}: {e}")
            return False
    
    async def set_comando_trocar_ip(self, imei: str, trocar: bool = True) -> bool:
        """Define comando para trocar IP do dispositivo."""
        try:
            collection = self.database.veiculo
            
            update_data = {
                "comandoTrocarIP": trocar,
                "ts_user_manu": datetime.utcnow()
            }
            
            result = await collection.update_one(
                {"IMEI": imei},
                {"$set": update_data},
                upsert=True
            )
            
            logger.info(f"Comando de trocar IP definido para IMEI {imei}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao definir comando trocar IP para {imei}: {e}")
            return False
            
    async def clear_comando_bloqueio(self, imei: str) -> bool:
        """Limpa comando de bloqueio após envio."""
        try:
            collection = self.database.veiculo
            
            result = await collection.update_one(
                {"IMEI": imei},
                {"$set": {
                    "comandoBloqueo": None,
                    "ts_user_manu": datetime.utcnow()
                }}
            )
            
            logger.info(f"Comando de bloqueio limpo para IMEI {imei}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao limpar comando para {imei}: {e}")
            return False
    
    async def clear_comando_trocar_ip(self, imei: str) -> bool:
        """Limpa comando de trocar IP após envio."""
        try:
            collection = self.database.veiculo
            
            result = await collection.update_one(
                {"IMEI": imei},
                {"$set": {
                    "comandoTrocarIP": None,
                    "ts_user_manu": datetime.utcnow()
                }}
            )
            
            logger.info(f"Comando de trocar IP limpo para IMEI {imei}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao limpar comando trocar IP para {imei}: {e}")
            return False
            
    async def get_veiculos_com_comando_pendente(self) -> List[Veiculo]:
        """Busca veículos com comandos pendentes (bloqueio ou trocar IP)."""
        try:
            collection = self.database.veiculo
            cursor = collection.find({
                "$or": [
                    {"comandoBloqueo": {"$ne": None}},
                    {"comandoTrocarIP": {"$ne": None}}
                ]
            })
            
            veiculos = []
            async for doc in cursor:
                doc['_id'] = str(doc['_id'])
                veiculos.append(Veiculo(**doc))
                
            logger.info(f"Encontrados {len(veiculos)} veículos com comandos pendentes")
            return veiculos
            
        except Exception as e:
            logger.error(f"Erro ao buscar comandos pendentes: {e}")
            return []
    
    async def atualizar_status_parada(self, imei: str, speed: str, ignicao: bool) -> bool:
        """Atualiza status de parada prolongada do veículo."""
        try:
            collection = self.database.veiculo
            now = datetime.utcnow()
            
            # Buscar status atual
            veiculo = await collection.find_one({"IMEI": imei})
            
            # Verificar se está parado (speed = 0) e com ignição OFF
            esta_parado = (speed == "0" or speed == 0) and not ignicao
            
            update_data = {
                "ignicao": ignicao,
                "ts_user_manu": now
            }
            
            if esta_parado:
                # Se estava parado e continua parado, manter tempo inicial
                if veiculo and veiculo.get("tempo_parado_iniciado"):
                    # Manter tempo anterior
                    pass
                else:
                    # Começou a parar agora
                    update_data["tempo_parado_iniciado"] = now
                    update_data["alertado_parada_prolongada"] = False
                    logger.info(f"Veículo {imei} parou com ignição OFF em {now}")
            else:
                # Veículo em movimento ou ignição ligada - resetar controle de parada
                if veiculo and veiculo.get("tempo_parado_iniciado"):
                    logger.info(f"Veículo {imei} voltou a se mover ou ligou ignição")
                
                update_data["tempo_parado_iniciado"] = None
                update_data["alertado_parada_prolongada"] = False
            
            await collection.update_one(
                {"IMEI": imei},
                {"$set": update_data},
                upsert=True
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao atualizar status parada {imei}: {e}")
            return False
    
    async def verificar_paradas_prolongadas(self, tempo_limite_segundos: int) -> List[Veiculo]:
        """Busca veículos com parada prolongada que ainda não foram alertados."""
        try:
            collection = self.database.veiculo
            now = datetime.utcnow()
            tempo_limite = now - timedelta(seconds=tempo_limite_segundos)
            
            cursor = collection.find({
                "tempo_parado_iniciado": {"$ne": None, "$lt": tempo_limite},
                "alertado_parada_prolongada": {"$ne": True}
            })
            
            veiculos = []
            async for doc in cursor:
                doc['_id'] = str(doc['_id'])
                veiculos.append(Veiculo(**doc))
                
            if veiculos:
                logger.info(f"Encontrados {len(veiculos)} veículos com parada prolongada")
                
            return veiculos
            
        except Exception as e:
            logger.error(f"Erro ao verificar paradas prolongadas: {e}")
            return []
    
    async def marcar_alertado_parada_prolongada(self, imei: str) -> bool:
        """Marca veículo como já alertado sobre parada prolongada."""
        try:
            collection = self.database.veiculo
            
            await collection.update_one(
                {"IMEI": imei},
                {"$set": {
                    "alertado_parada_prolongada": True,
                    "ts_user_manu": datetime.utcnow()
                }}
            )
            
            logger.info(f"Veículo {imei} marcado como alertado sobre parada prolongada")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao marcar alerta parada {imei}: {e}")
            return False

# Instância global
mongodb_client = MongoDBClient()