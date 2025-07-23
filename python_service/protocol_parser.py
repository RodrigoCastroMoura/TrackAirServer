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
    Suporta múltiplos tipos: GTFRI, GTIGN, GTIGF, GTIGL, GTOUT, GTSRI, GTBSI
    """
    try:
        if not raw_message or not raw_message.startswith('+'):
            return None
        
        # Remover $ do final se existir
        message = raw_message.rstrip('$')
        
        # Dividir por virgulas
        parts = message.split(',')
        
        if len(parts) < 3:
            return None
        
        # Extrair tipo de comando da primeira parte
        message_header = parts[0]  # Ex: +RESP:GTFRI ou +RESP:GTIGN
        
        # Identificar tipo de mensagem
        command_type = None
        for cmd in ['GTFRI', 'GTIGN', 'GTIGF', 'GTIGL', 'GTOUT', 'GTSRI', 'GTBSI']:
            if cmd in message_header:
                command_type = cmd
                break
                
        if not command_type:
            logger.debug(f"Tipo de comando não reconhecido: {message_header}")
            return None
        
        # Identificar tipo de mensagem (+RESP, +BUFF, +ACK)
        message_type = '+RESP'  # Default
        if '+BUFF:' in message_header:
            message_type = '+BUFF'
        elif '+ACK:' in message_header:
            message_type = '+ACK'
        elif '+RESP:' in message_header:
            message_type = '+RESP'
        
        # Estrutura básica para todos os tipos
        parsed = {
            'message_type': message_type,
            'command_type': command_type,
            'imei': parts[2] if len(parts) > 2 else '',
            'number': parts[-1] if len(parts) > 0 else '0000',
            'raw_message': raw_message
        }
        
        # Processar diferentes tipos de mensagem
        if command_type == 'GTFRI':
            # Mensagem de dados GPS fixos
            if len(parts) >= 14:
                parsed['longitude'] = parts[11]
                parsed['latitude'] = parts[12]
                parsed['device_time'] = parts[13]
                parsed['speed'] = parts[8]
                parsed['altitude'] = parts[10]
                parsed['ignition'] = 'true' if (len(parts) > 6 and parts[6] == '1') else 'false'
                
        elif command_type in ['GTIGN', 'GTIGF']:
            # Eventos de ignição (ON/OFF)
            ignition_state = command_type == 'GTIGN'  # True se ligada, False se desligada
            
            if len(parts) >= 13:
                parsed['ignition'] = 'true' if ignition_state else 'false'
                parsed['ignition_event'] = 'true'  # Marca como evento de ignição
                parsed['longitude'] = parts[10] if len(parts) > 10 else '0'
                parsed['latitude'] = parts[11] if len(parts) > 11 else '0'
                parsed['device_time'] = parts[12] if len(parts) > 12 else ''
                parsed['speed'] = '0'  # Eventos de ignição geralmente são com veículo parado
                parsed['altitude'] = parts[9] if len(parts) > 9 else '0'
            logger.info(f"Evento de ignição detectado: IMEI={parsed['imei']}, Estado={'LIGADA' if ignition_state else 'DESLIGADA'}")
                
        elif command_type == 'GTIGL':
            # Evento de bateria baixa (Low External Power)
            if len(parts) >= 13:
                # GTIGL: Protocolo para bateria baixa do veículo
                parsed['battery_voltage'] = parts[5] if len(parts) > 5 else '0'  # Voltagem da bateria
                parsed['battery_low'] = 'true'  # Marca que bateria está baixa
                parsed['longitude'] = parts[10] if len(parts) > 10 else '0'
                parsed['latitude'] = parts[11] if len(parts) > 11 else '0'
                parsed['device_time'] = parts[12] if len(parts) > 12 else ''
                parsed['speed'] = '0'  # Geralmente parado quando bateria baixa
                parsed['altitude'] = parts[9] if len(parts) > 9 else '0'
                parsed['ignition'] = 'false'  # Provavelmente desligado se bateria baixa
            logger.warning(f"🔋 ALERTA BATERIA BAIXA: IMEI={parsed['imei']}, Voltagem={parsed.get('battery_voltage', 'N/A')}V")
            
        else:
            # Outros tipos (GTOUT, GTSRI, GTBSI)
            logger.debug(f"Mensagem de comando/resposta: {command_type}")
            
        logger.debug(f"Mensagem analisada: Tipo={command_type}, IMEI={parsed['imei']}")
        return parsed
        
    except Exception as e:
        logger.error(f"Erro ao analisar mensagem {raw_message}: {e}")
        return None

def create_ack_message(number: str, command_type: str = "GTFRI") -> str:
    """Cria mensagem de ACK para o dispositivo baseada no tipo de comando."""
    return f"+SACK:{command_type},{number}$"

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