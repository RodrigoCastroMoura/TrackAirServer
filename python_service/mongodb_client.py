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

# Instância global
mongodb_client = MongoDBClient()