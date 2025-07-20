#!/usr/bin/env python3
"""
Parser simples para protocolo GPS GV50
"""

import re
from typing import Dict, Optional
from logger import get_logger

logger = get_logger(__name__)

def parse_gv50_message(raw_message: str) -> Optional[Dict]:
    """
    Analisa mensagem do protocolo GV50.
    Exemplo: +RESP:GTFRI,060228,123456789012345,,0,0,1,1,4.3,92,70.0,-46.633308,-23.550520,20241221163000,0460,0000,18d8,6141,00,2000.0,20241221163000,11F0$
    """
    try:
        if not raw_message or not raw_message.startswith('+'):
            return None
        
        # Remover $ do final se existir
        message = raw_message.rstrip('$')
        
        # Dividir por virgulas
        parts = message.split(',')
        
        if len(parts) < 10:
            return None
            
        # Verificar se é mensagem GTFRI (dados GPS)
        if 'GTFRI' not in parts[0]:
            return None
            
        # Extrair informações básicas
        parsed = {
            'message_type': '+RESP',
            'command_type': 'GTFRI',
            'imei': parts[2] if len(parts) > 2 else '',
            'longitude': parts[11] if len(parts) > 11 else '0',
            'latitude': parts[12] if len(parts) > 12 else '0',
            'device_time': parts[13] if len(parts) > 13 else '',
            'speed': parts[8] if len(parts) > 8 else '0',
            'altitude': parts[10] if len(parts) > 10 else '0',
            'ignition': parts[6] == '1' if len(parts) > 6 else False,
            'number': parts[-1] if len(parts) > 0 else '0000'
        }
        
        logger.debug(f"Mensagem analisada: IMEI={parsed['imei']}, Lat={parsed['latitude']}, Lon={parsed['longitude']}")
        return parsed
        
    except Exception as e:
        logger.error(f"Erro ao analisar mensagem {raw_message}: {e}")
        return None

def create_ack_message(number: str) -> str:
    """Cria mensagem de ACK para o dispositivo."""
    return f"+SACK:GTFRI,{number}$"

def create_block_command(password: str = "gv50") -> str:
    """Cria comando para bloquear dispositivo."""
    return f"AT+GTOUT={password},1,0,,,,,,FFFF$"

def create_unblock_command(password: str = "gv50") -> str:
    """Cria comando para desbloquear dispositivo."""
    return f"AT+GTOUT={password},0,0,,,,,,FFFF$"

def create_ip_config_command(password: str, server_ip: str, server_port: int, 
                           backup_ip: str = "", backup_port: int = 8000) -> str:
    """Cria comando para configurar IP do servidor."""
    return (f"AT+GTSRI={password},123456,0,"
            f"{server_ip},{server_port},0,"
            f"{backup_ip or server_ip},{backup_port},,,,FFFF$")