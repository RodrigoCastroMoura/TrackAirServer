#!/usr/bin/env python3
"""
API simples para definir comandos de bloqueio/desbloqueio
Pode ser usada por outros sistemas para controlar os veículos
"""

from mongodb_client import mongodb_client
from logger import get_logger

logger = get_logger(__name__)

class CommandAPI:
    """API para gerenciar comandos de bloqueio/desbloqueio."""
    
    @staticmethod
    async def bloquear_veiculo(imei: str) -> bool:
        """Define comando para bloquear veículo."""
        try:
            result = await mongodb_client.set_comando_bloqueio(imei, True)
            if result:
                logger.info(f"API: Comando de BLOQUEIO definido para {imei}")
            return result
        except Exception as e:
            logger.error(f"Erro ao bloquear veículo {imei}: {e}")
            return False
    
    @staticmethod
    async def desbloquear_veiculo(imei: str) -> bool:
        """Define comando para desbloquear veículo."""
        try:
            result = await mongodb_client.set_comando_bloqueio(imei, False)
            if result:
                logger.info(f"API: Comando de DESBLOQUEIO definido para {imei}")
            return result
        except Exception as e:
            logger.error(f"Erro ao desbloquear veículo {imei}: {e}")
            return False
    
    @staticmethod
    async def status_veiculo(imei: str) -> dict:
        """Obtém status atual do veículo."""
        try:
            veiculo = await mongodb_client.get_veiculo_by_imei(imei)
            if not veiculo:
                return {"erro": f"Veículo {imei} não encontrado"}
                
            return {
                "imei": veiculo.IMEI,
                "placa": veiculo.ds_placa,
                "ignicao": veiculo.ignicao,
                "bloqueado": veiculo.bloqueado,
                "comando_pendente": veiculo.comandoBloqueo,
                "ultima_atualizacao": veiculo.ts_user_manu.isoformat() if veiculo.ts_user_manu else None
            }
        except Exception as e:
            logger.error(f"Erro ao obter status do veículo {imei}: {e}")
            return {"erro": str(e)}
    
    @staticmethod
    async def listar_comandos_pendentes() -> list:
        """Lista todos os veículos com comandos pendentes."""
        try:
            veiculos = await mongodb_client.get_veiculos_com_comando_pendente()
            result = []
            
            for veiculo in veiculos:
                result.append({
                    "imei": veiculo.IMEI,
                    "placa": veiculo.ds_placa,
                    "comando": "bloquear" if veiculo.comandoBloqueo else "desbloquear",
                    "ignicao": veiculo.ignicao
                })
                
            return result
        except Exception as e:
            logger.error(f"Erro ao listar comandos pendentes: {e}")
            return []

# Exemplo de uso da API
if __name__ == "__main__":
    import asyncio
    
    async def test_api():
        await mongodb_client.connect()
        
        # Bloquear veículo
        await CommandAPI.bloquear_veiculo("123456789012345")
        
        # Ver status
        status = await CommandAPI.status_veiculo("123456789012345")
        print(f"Status: {status}")
        
        # Listar comandos pendentes
        pendentes = await CommandAPI.listar_comandos_pendentes()
        print(f"Comandos pendentes: {pendentes}")
        
        await mongodb_client.disconnect()
    
    asyncio.run(test_api())