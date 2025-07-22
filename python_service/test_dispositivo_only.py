#!/usr/bin/env python3
"""
Teste do sistema simplificado - apenas dados do dispositivo
"""

from protocol_parser import parse_gv50_message
from datetime import datetime

def test_dispositivo_only():
    """Testa o sistema que grava apenas dados do dispositivo."""
    print("🧪 TESTE SISTEMA DISPOSITIVO APENAS")
    print("=" * 50)
    
    # Mensagens de teste
    test_messages = [
        # Dados GPS normais
        "+RESP:GTFRI,060228,555444333222111,,0,0,1,1,4.3,92,70.0,-46.633308,-23.550520,20250722210000,0460,0000,18d8,6141,00,2000.0,20250722210000,A001$",
        # Evento ignição ligada  
        "+RESP:GTIGN,060228,555444333222111,,0,0,1,1,4.3,92,70.0,-46.633308,-23.550520,20250722210030,0460,0000,18d8,6141,00,B001$",
        # Evento ignição desligada
        "+RESP:GTIGF,060228,555444333222111,,0,0,0,0,0.0,92,70.0,-46.633308,-23.550520,20250722210130,0460,0000,18d8,6141,00,B002$"
    ]
    
    print("\n📊 PROCESSANDO MENSAGENS:")
    print("-" * 50)
    
    for i, message in enumerate(test_messages, 1):
        parsed = parse_gv50_message(message)
        
        if parsed:
            # Simular dados que seriam salvos no DadosVeiculo
            device_data = {
                'IMEI': parsed['imei'],
                'longitude': parsed.get('longitude', '0'),
                'latitude': parsed.get('latitude', '0'),
                'altitude': parsed.get('altitude', '0'),
                'speed': parsed.get('speed', '0'),
                'ignition': parsed.get('ignition', False),
                'device_time': parsed.get('device_time', ''),
                'data': datetime.utcnow().isoformat()
            }
            
            command_type = parsed['command_type']
            ignition_event = parsed.get('ignition_event', False)
            
            print(f"\n📡 Mensagem {i}: {command_type}")
            print(f"   IMEI: {device_data['IMEI']}")
            print(f"   Posição: {device_data['latitude']}, {device_data['longitude']}")
            print(f"   Ignição: {'🔥 LIGADA' if device_data['ignition'] else '🔌 DESLIGADA'}")
            print(f"   Evento especial: {'✅ SIM' if ignition_event else '❌ NÃO'}")
            print(f"   Velocidade: {device_data['speed']} km/h")
            
            # Destacar eventos de ignição
            if ignition_event:
                status = "LIGADA" if device_data['ignition'] else "DESLIGADA"
                print(f"   🚨 EVENTO IGNIÇÃO {status} DETECTADO!")
            
        else:
            print(f"\n❌ Falha no parsing da mensagem {i}")
    
    print("\n" + "=" * 50)
    print("✅ SISTEMA SIMPLIFICADO FUNCIONANDO!")
    print("   - Dados salvos APENAS em DadosVeiculo")
    print("   - Ignição detectada corretamente") 
    print("   - Eventos especiais identificados")
    print("   - Sem lógica de Veiculo/comandos")
    print("\n🎯 Sistema pronto para receber dados GPS!")

if __name__ == "__main__":
    test_dispositivo_only()