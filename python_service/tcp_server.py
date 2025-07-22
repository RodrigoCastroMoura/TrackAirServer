#!/usr/bin/env python3
"""
Servidor TCP simples para dispositivos GPS GV50
Recebe dados GPS e verifica comandos de bloqueio
"""

import asyncio
from typing import Dict, Set, Optional
from datetime import datetime, timedelta
from protocol_parser import parse_gv50_message, create_ack_message, create_block_command, create_unblock_command, create_ip_config_command
from mongodb_client import mongodb_client
from models import DadosVeiculo, Veiculo
from config import get_settings
from logger import get_logger

logger = get_logger(__name__)

class GPSDeviceHandler:
    """Manipulador para conexões de dispositivos GPS - Long Connection Mode."""
    
    def __init__(self):
        self.connected_devices: Dict[str, dict] = {}  # IMEI -> {writer, last_seen, client_ip}
        self.settings = get_settings()
        self.cleanup_task: Optional[asyncio.Task] = None
        
    async def handle_device(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Manipula conexão de um dispositivo GPS - Long Connection Mode."""
        client_ip = writer.get_extra_info('peername')[0]
        logger.info(f"Nova conexão GPS long-connection de {client_ip}")
        
        imei = None
        device_info = None
        
        try:
            # Configurar timeout de leitura
            while True:
                try:
                    # Aguardar dados com timeout
                    data = await asyncio.wait_for(
                        reader.read(1024), 
                        timeout=self.settings.keep_alive_timeout
                    )
                    
                    if not data:
                        logger.info(f"Dispositivo {client_ip} encerrou conexão")
                        break
                        
                    message = data.decode('utf-8').strip()
                    logger.info(f"[Long-Conn] Recebido de {client_ip}: {message}")
                    
                    # Processar mensagem do protocolo GV50
                    parsed = parse_gv50_message(message)
                    if parsed and parsed.get('imei'):
                        imei = parsed['imei']
                        
                        # Registrar/atualizar dispositivo conectado
                        device_info = {
                            'writer': writer,
                            'last_seen': datetime.now(),
                            'client_ip': client_ip,
                            'reader': reader
                        }
                        self.connected_devices[imei] = device_info
                        
                        # Salvar dados GPS no MongoDB
                        await self.save_gps_data(parsed, message)
                        
                        # Log eventos especiais de ignição
                        if parsed.get('ignition_event'):
                            ignition_status = "LIGADA" if parsed.get('ignition') else "DESLIGADA"
                            logger.info(f"🔥 Evento ignição {ignition_status}: IMEI={parsed['imei']}")
                        
                        # Verificar comandos pendentes (crítico para long-connection)
                        await self.check_pending_commands(imei, writer)
                        
                        # Enviar ACK específico para o tipo de comando
                        command_type = parsed.get('command_type', 'GTFRI')
                        await self.send_ack(writer, parsed.get('number', '0000'), command_type)
                    
                    # Heartbeat implícito - qualquer mensagem mantém conexão viva
                    if device_info:
                        device_info['last_seen'] = datetime.now()
                        
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout na conexão long-connection de {client_ip}")
                    # Enviar heartbeat request se necessário
                    if imei:
                        await self.send_heartbeat_request(writer)
                    continue
                    
        except asyncio.IncompleteReadError:
            logger.info(f"Dispositivo {client_ip} desconectado (incomplete read)")
        except ConnectionResetError:
            logger.info(f"Dispositivo {client_ip} resetou conexão")
        except Exception as e:
            logger.error(f"Erro ao processar dispositivo long-connection {client_ip}: {e}")
        finally:
            # Cleanup da conexão
            if imei and imei in self.connected_devices:
                logger.info(f"Removendo dispositivo {imei} das conexões ativas")
                del self.connected_devices[imei]
            
            if not writer.is_closing():
                writer.close()
                try:
                    await writer.wait_closed()
                except:
                    pass
            
    async def save_gps_data(self, parsed_data: dict, raw_message: str):
        """Salva apenas dados do dispositivo GPS no MongoDB."""
        try:
            # Criar objeto DadosVeiculo (dados do dispositivo)
            dados = DadosVeiculo(
                IMEI=parsed_data['imei'],
                longitude=parsed_data.get('longitude', '0'),
                latitude=parsed_data.get('latitude', '0'), 
                altidude=parsed_data.get('altitude', '0'),
                speed=parsed_data.get('speed', '0'),
                ignicao=parsed_data.get('ignition', False),
                dataDevice=parsed_data.get('device_time', ''),
                data=datetime.utcnow()
            )
            
            # Inserir apenas dados do dispositivo no MongoDB
            await mongodb_client.insert_dados_veiculo(dados)
            
            logger.debug(f"Dados dispositivo salvos: IMEI={parsed_data['imei']}, Ignição={parsed_data.get('ignition', False)}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar dados do dispositivo: {e}")
            
    async def check_pending_commands(self, imei: str, writer: asyncio.StreamWriter):
        """Verifica e envia comandos pendentes para o dispositivo."""
        try:
            # Sistema simplificado - comandos podem ser implementados futuramente se necessário
            # Por enquanto, só armazenamos dados do dispositivo
            logger.debug(f"Verificando comandos para dispositivo {imei}")
            return
            
        except Exception as e:
            logger.error(f"Erro ao verificar comandos para {imei}: {e}")
            

    async def send_ack(self, writer: asyncio.StreamWriter, number: str, command_type: str = "GTFRI"):
        """Envia ACK para o dispositivo."""
        try:
            ack_message = create_ack_message(number, command_type)
            writer.write(ack_message.encode('utf-8'))
            await writer.drain()
            logger.debug(f"ACK enviado: {ack_message}")
        except Exception as e:
            logger.error(f"Erro ao enviar ACK: {e}")
    
    async def send_heartbeat_request(self, writer: asyncio.StreamWriter):
        """Envia heartbeat request para manter conexão viva no modo long-connection."""
        try:
            # Comando heartbeat conforme documentação GV50
            heartbeat = "AT+GTHBD=gv50$"
            writer.write(heartbeat.encode('utf-8'))
            await writer.drain()
            logger.debug("Heartbeat request enviado para manter long-connection")
        except Exception as e:
            logger.error(f"Erro ao enviar heartbeat: {e}")
    
    async def cleanup_stale_connections(self):
        """Remove conexões inativas - task para modo long-connection."""
        logger.info("Iniciando task de cleanup para long-connections")
        while True:
            try:
                now = datetime.now()
                stale_devices = []
                
                for imei, device_info in self.connected_devices.items():
                    last_seen = device_info['last_seen']
                    inactive_time = now - last_seen
                    
                    if inactive_time > timedelta(seconds=self.settings.device_timeout):
                        stale_devices.append(imei)
                        logger.warning(f"Dispositivo {imei} inativo há {inactive_time} (long-connection)")
                
                # Remover dispositivos inativos
                for imei in stale_devices:
                    device_info = self.connected_devices.get(imei)
                    if device_info:
                        writer = device_info['writer']
                        if not writer.is_closing():
                            writer.close()
                        del self.connected_devices[imei]
                        logger.info(f"Long-connection {imei} removida por timeout ({self.settings.device_timeout}s)")
                
                # Estatísticas de conexões ativas
                active_count = len(self.connected_devices)
                if active_count > 0:
                    logger.info(f"Long-connections ativas: {active_count}")
                
                # Aguardar próximo ciclo
                await asyncio.sleep(self.settings.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"Erro no cleanup long-connections: {e}")
                await asyncio.sleep(60)

class TCPServer:
    """Servidor TCP principal para dispositivos GPS."""
    
    def __init__(self):
        self.settings = get_settings()
        self.device_handler = GPSDeviceHandler()
        self.server = None
        
    async def start_server(self):
        """Inicia o servidor TCP em modo Long-Connection."""
        try:
            # Conectar ao MongoDB primeiro
            await mongodb_client.connect()
            
            # Iniciar task de cleanup para long-connections
            cleanup_coro = self.device_handler.cleanup_stale_connections()
            self.device_handler.cleanup_task = asyncio.create_task(cleanup_coro)
            
            # Iniciar servidor TCP
            self.server = await asyncio.start_server(
                self.device_handler.handle_device,
                self.settings.tcp_host,
                self.settings.tcp_port
            )
            
            addr = self.server.sockets[0].getsockname()
            logger.info(f"Servidor GPS Long-Connection iniciado em {addr[0]}:{addr[1]}")
            logger.info(f"Configurações Long-Connection:")
            logger.info(f"  - Device timeout: {self.settings.device_timeout}s")
            logger.info(f"  - Heartbeat interval: {self.settings.heartbeat_interval}s") 
            logger.info(f"  - Keep-alive timeout: {self.settings.keep_alive_timeout}s")
            
            # Manter servidor rodando
            async with self.server:
                await self.server.serve_forever()
                
        except Exception as e:
            logger.error(f"Erro ao iniciar servidor long-connection: {e}")
            raise
            
    async def stop_server(self):
        """Para o servidor TCP e cleanup tasks."""
        try:
            if self.device_handler.cleanup_task:
                self.device_handler.cleanup_task.cancel()
                
            if self.server:
                self.server.close()
                await self.server.wait_closed()
                
            # Fechar todas as conexões ativas
            for imei, device_info in self.device_handler.connected_devices.items():
                writer = device_info['writer']
                if not writer.is_closing():
                    writer.close()
                    
            self.device_handler.connected_devices.clear()
            await mongodb_client.disconnect()
            logger.info("Servidor Long-Connection parado")
            
        except Exception as e:
            logger.error(f"Erro ao parar servidor: {e}")
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("Servidor GPS parado")
            
        await mongodb_client.disconnect()

# Instância global
tcp_server = TCPServer()