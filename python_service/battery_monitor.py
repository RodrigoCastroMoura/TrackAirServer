#!/usr/bin/env python3
"""
Monitor de bateria para sistema GPS GV50
Funções auxiliares para processamento de alertas de bateria baixa
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from logger import get_logger

logger = get_logger(__name__)

class BatteryMonitor:
    """Monitor de status de bateria para dispositivos GPS."""
    
    # Limiares de voltagem da bateria (em Volts)
    VOLTAGE_CRITICAL = 10.5   # Bateria crítica - dispositivo vai desligar
    VOLTAGE_LOW = 11.0        # Bateria baixa - alerta vermelho
    VOLTAGE_WARNING = 11.5    # Bateria em aviso - alerta amarelo
    VOLTAGE_NORMAL = 12.0     # Bateria normal - sem alerta
    
    @classmethod
    def get_battery_status(cls, voltage: float) -> Dict[str, any]:
        """
        Avalia status da bateria baseado na voltagem.
        
        Args:
            voltage: Voltagem da bateria em Volts
            
        Returns:
            Dict com status, nivel, cor e mensagem
        """
        if voltage <= cls.VOLTAGE_CRITICAL:
            return {
                'status': 'CRÍTICA',
                'level': 'critical',
                'color': '🔴',
                'emoji': '🚨',
                'message': 'Dispositivo pode desligar a qualquer momento!',
                'action_required': True,
                'estimated_time': '< 30 min'
            }
        elif voltage <= cls.VOLTAGE_LOW:
            return {
                'status': 'BAIXA',
                'level': 'low',
                'color': '🟠',
                'emoji': '⚠️',
                'message': 'Bateria necessita atenção urgente',
                'action_required': True,
                'estimated_time': '< 2 horas'
            }
        elif voltage <= cls.VOLTAGE_WARNING:
            return {
                'status': 'AVISO',
                'level': 'warning',
                'color': '🟡',
                'emoji': '🔋',
                'message': 'Bateria em nível baixo',
                'action_required': False,
                'estimated_time': '< 6 horas'
            }
        else:
            return {
                'status': 'NORMAL',
                'level': 'normal',
                'color': '🟢',
                'emoji': '✅',
                'message': 'Bateria em nível normal',
                'action_required': False,
                'estimated_time': '> 12 horas'
            }
    
    @classmethod
    def should_alert(cls, voltage: float, last_alert: Optional[datetime] = None, 
                    min_interval_minutes: int = 30) -> bool:
        """
        Verifica se deve enviar alerta baseado na voltagem e último alerta.
        
        Args:
            voltage: Voltagem atual
            last_alert: Timestamp do último alerta
            min_interval_minutes: Intervalo mínimo entre alertas
            
        Returns:
            True se deve alertar, False caso contrário
        """
        # Sempre alertar se bateria crítica
        if voltage <= cls.VOLTAGE_CRITICAL:
            return True
            
        # Não alertar se bateria normal
        if voltage > cls.VOLTAGE_WARNING:
            return False
            
        # Verificar intervalo desde último alerta
        if last_alert:
            time_since_alert = datetime.utcnow() - last_alert
            if time_since_alert < timedelta(minutes=min_interval_minutes):
                return False
                
        return True
    
    @classmethod
    def get_log_level(cls, voltage: float) -> str:
        """Retorna nível de log apropriado baseado na voltagem."""
        if voltage <= cls.VOLTAGE_CRITICAL:
            return 'CRITICAL'
        elif voltage <= cls.VOLTAGE_LOW:
            return 'ERROR'  
        elif voltage <= cls.VOLTAGE_WARNING:
            return 'WARNING'
        else:
            return 'INFO'
    
    @classmethod
    def format_battery_message(cls, imei: str, voltage: float, 
                             coordinates: Optional[Dict] = None) -> str:
        """
        Formata mensagem de log para bateria.
        
        Args:
            imei: IMEI do dispositivo
            voltage: Voltagem da bateria
            coordinates: Coordenadas opcionais (lat, lon)
            
        Returns:
            Mensagem formatada para log
        """
        status = cls.get_battery_status(voltage)
        
        location_str = ""
        if coordinates and coordinates.get('latitude') and coordinates.get('longitude'):
            location_str = f" | Localização: {coordinates['latitude']}, {coordinates['longitude']}"
        
        return (f"{status['emoji']} BATERIA {status['status']}: "
                f"IMEI={imei} | Voltagem={voltage:.2f}V | "
                f"Tempo estimado: {status['estimated_time']}{location_str}")
    
    @classmethod
    def get_mongodb_update(cls, voltage: float) -> Dict[str, any]:
        """
        Retorna dados para atualizar no MongoDB.
        
        Args:
            voltage: Voltagem da bateria
            
        Returns:
            Dict com campos para atualizar no veículo
        """
        status = cls.get_battery_status(voltage)
        
        return {
            'bateria_voltagem': voltage,
            'bateria_baixa': status['level'] in ['critical', 'low', 'warning'],
            'ultimo_alerta_bateria': datetime.utcnow() if status['action_required'] else None
        }

# Função de conveniência para usar no tcp_server.py
def process_battery_alert(imei: str, voltage_str: str, coordinates: Dict = None) -> Dict[str, any]:
    """
    Processa alerta de bateria e retorna dados para log e MongoDB.
    
    Args:
        imei: IMEI do dispositivo
        voltage_str: Voltagem como string
        coordinates: Coordenadas opcionais
        
    Returns:
        Dict com dados processados
    """
    try:
        voltage = float(voltage_str)
    except (ValueError, TypeError):
        logger.error(f"Erro ao converter voltagem da bateria: {voltage_str}")
        return {
            'success': False,
            'error': 'Voltagem inválida'
        }
    
    status = BatteryMonitor.get_battery_status(voltage)
    log_message = BatteryMonitor.format_battery_message(imei, voltage, coordinates)
    mongodb_update = BatteryMonitor.get_mongodb_update(voltage)
    log_level = BatteryMonitor.get_log_level(voltage)
    
    return {
        'success': True,
        'voltage': voltage,
        'status': status,
        'log_message': log_message,
        'log_level': log_level,
        'mongodb_update': mongodb_update,
        'should_alert': BatteryMonitor.should_alert(voltage)
    }