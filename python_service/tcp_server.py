#!/usr/bin/env python3
"""
Servidor TCP simples para dispositivos GPS GV50
Recebe dados GPS e verifica comandos de bloqueio
"""

import asyncio
from typing import Dict, Set
from datetime import datetime
from protocol_parser import parse_gv50_message
from mongodb_client import mongodb_client
from models import DadosVeiculo, Veiculo
from config import get_settings
from logger import get_logger

logger = get_logger(__name__)

class GPSDeviceHandler:
    """Manipulador para conexões de dispositivos GPS."""
    
    def __init__(self):
        self.connected_devices: Dict[str, asyncio.StreamWriter] = {}
        self.settings = get_settings()
        
    async def handle_device(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Manipula conexão de um dispositivo GPS."""
        client_ip = writer.get_extra_info('peername')[0]
        logger.info(f"Nova conexão GPS de {client_ip}")
        
        imei = None
        try:
            while True:
                # Ler dados do dispositivo
                data = await reader.read(1024)
                if not data:
                    break
                    
                message = data.decode('utf-8').strip()
                logger.info(f"Recebido de {client_ip}: {message}")
                
                # Processar mensagem do protocolo GV50
                parsed = parse_gv50_message(message)
                if parsed and parsed.get('imei'):
                    imei = parsed['imei']
                    self.connected_devices[imei] = writer
                    
                    # Salvar dados GPS no MongoDB
                    await self.save_gps_data(parsed, message)
                    
                    # Verificar comandos pendentes
                    await self.check_pending_commands(imei, writer)
                    
                    # Enviar ACK
                    await self.send_ack(writer, parsed.get('number', '0000'))
                    
        except asyncio.IncompleteReadError:
            logger.info(f"Dispositivo {client_ip} desconectado")
        except Exception as e:
            logger.error(f"Erro ao processar dispositivo {client_ip}: {e}")
        finally:
            if imei and imei in self.connected_devices:
                del self.connected_devices[imei]
            writer.close()
            await writer.wait_closed()
            
    async def save_gps_data(self, parsed_data: dict, raw_message: str):
        """Salva dados GPS no MongoDB."""
        try:
            # Criar objeto DadosVeiculo
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
            
            # Inserir no MongoDB
            await mongodb_client.insert_dados_veiculo(dados)
            
            # Atualizar status do veículo
            veiculo = await mongodb_client.get_veiculo_by_imei(parsed_data['imei'])
            if not veiculo:
                # Criar novo veículo se não existe
                veiculo = Veiculo(
                    IMEI=parsed_data['imei'],
                    ignicao=parsed_data.get('ignition', False)
                )
            else:
                # Atualizar ignição
                veiculo.ignicao = parsed_data.get('ignition', False)
                
            await mongodb_client.update_veiculo(veiculo)
            
        except Exception as e:
            logger.error(f"Erro ao salvar dados GPS: {e}")
            
    async def check_pending_commands(self, imei: str, writer: asyncio.StreamWriter):
        """Verifica e envia comandos pendentes para o dispositivo."""
        try:
            veiculo = await mongodb_client.get_veiculo_by_imei(imei)
            if not veiculo:
                return
                
            # Verificar comando de bloqueio/desbloqueio
            if veiculo.comandoBloqueo is not None:
                if veiculo.comandoBloqueo:
                    command = "AT+GTOUT=gv50,1,0,,,,,,FFFF$"  # Bloquear
                    logger.info(f"Enviando comando de BLOQUEIO para {imei}")
                else:
                    command = "AT+GTOUT=gv50,0,0,,,,,,FFFF$"  # Desbloquear  
                    logger.info(f"Enviando comando de DESBLOQUEIO para {imei}")
                    
                # Enviar comando
                writer.write(command.encode('utf-8'))
                await writer.drain()
                
                # Limpar comando após envio
                await mongodb_client.clear_comando_bloqueio(imei)
                
                # Atualizar status de bloqueado
                veiculo.bloqueado = veiculo.comandoBloqueo
                await mongodb_client.update_veiculo(veiculo)
            
            # Verificar comando de trocar IP
            if veiculo.comandoTrocarIP:
                await self.send_ip_config_command(imei, writer)
                await mongodb_client.clear_comando_trocar_ip(imei)
            
        except Exception as e:
            logger.error(f"Erro ao verificar comandos para {imei}: {e}")
            
    async def send_ip_config_command(self, imei: str, writer: asyncio.StreamWriter):
        """Envia comando para configurar novo IP do servidor."""
        try:
            settings = self.settings
            
            # Verificar se há IPs configurados
            if not settings.new_server_ip:
                logger.warning(f"Novo IP do servidor não configurado para {imei}")
                return
                
            # Comando GTSRI para configurar novo servidor
            # Formato: AT+GTSRI=gv50,password,0,server_ip,server_port,0,backup_ip,backup_port,,,FFFF$
            command = (
                f"AT+GTSRI=gv50,123456,0,"
                f"{settings.new_server_ip},{settings.new_server_port},0,"
                f"{settings.backup_server_ip or settings.new_server_ip},"
                f"{settings.backup_server_port},,,,FFFF$"
            )
            
            logger.info(f"Enviando comando de CONFIGURAÇÃO IP para {imei}")
            logger.info(f"Novo IP: {settings.new_server_ip}:{settings.new_server_port}")
            
            # Enviar comando
            writer.write(command.encode('utf-8'))
            await writer.drain()
            
        except Exception as e:
            logger.error(f"Erro ao enviar comando de IP para {imei}: {e}")
            
    async def send_ack(self, writer: asyncio.StreamWriter, number: str):
        """Envia ACK para o dispositivo."""
        try:
            ack_message = f"+SACK:GTFRI,{number}$"
            writer.write(ack_message.encode('utf-8'))
            await writer.drain()
            logger.debug(f"ACK enviado: {ack_message}")
        except Exception as e:
            logger.error(f"Erro ao enviar ACK: {e}")

class TCPServer:
    """Servidor TCP principal para dispositivos GPS."""
    
    def __init__(self):
        self.settings = get_settings()
        self.device_handler = GPSDeviceHandler()
        self.server = None
        
    async def start_server(self):
        """Inicia o servidor TCP."""
        try:
            # Conectar ao MongoDB primeiro
            await mongodb_client.connect()
            
            # Iniciar servidor TCP
            self.server = await asyncio.start_server(
                self.device_handler.handle_device,
                self.settings.tcp_host,
                self.settings.tcp_port
            )
            
            addr = self.server.sockets[0].getsockname()
            logger.info(f"Servidor GPS iniciado em {addr[0]}:{addr[1]}")
            
            # Manter servidor rodando
            async with self.server:
                await self.server.serve_forever()
                
        except Exception as e:
            logger.error(f"Erro ao iniciar servidor: {e}")
            raise
            
    async def stop_server(self):
        """Para o servidor TCP."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("Servidor GPS parado")
            
        await mongodb_client.disconnect()

# Instância global
tcp_server = TCPServer()