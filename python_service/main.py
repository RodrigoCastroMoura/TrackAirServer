#!/usr/bin/env python3
"""
Serviço Python TCP para dispositivos GPS GV50
Sistema simplificado com apenas 2 tabelas: DadosVeiculo e Veiculo
"""

import asyncio
import signal
import sys
from tcp_server import tcp_server
from logger import get_logger

logger = get_logger(__name__)

class GPSService:
    """Serviço principal GPS."""
    
    def __init__(self):
        self.running = False
        
    async def start(self):
        """Inicia o serviço GPS."""
        self.running = True
        logger.info("=== INICIANDO SERVIÇO GPS GV50 - LONG CONNECTION MODE ===")
        logger.info("Sistema simplificado: DadosVeiculo + Veiculo")
        logger.info("Modo: TCP Long-Connection conforme documentação GV50")
        logger.info("Funcionalidades: Recebe dados GPS, gerencia bloqueio/desbloqueio e conexões persistentes")
        
        try:
            await tcp_server.start_server()
        except KeyboardInterrupt:
            logger.info("Serviço interrompido pelo usuário")
        except Exception as e:
            logger.error(f"Erro no serviço: {e}")
        finally:
            await self.stop()
            
    async def stop(self):
        """Para o serviço GPS."""
        if self.running:
            logger.info("=== PARANDO SERVIÇO GPS ===")
            await tcp_server.stop_server()
            self.running = False

def signal_handler(signum, frame):
    """Handler para sinais de sistema."""
    logger.info(f"Recebido sinal {signum}")
    sys.exit(0)

async def main():
    """Função principal."""
    # Configurar handlers de sinal
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Iniciar serviço
    service = GPSService()
    await service.start()

if __name__ == "__main__":
    asyncio.run(main())