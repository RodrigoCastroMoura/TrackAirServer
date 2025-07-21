#!/usr/bin/env python3
"""
Simulador de dispositivo GPS GV50 para testes
"""

import asyncio
import socket
import time
from datetime import datetime

class GPSDeviceSimulator:
    def __init__(self, host='191.252.181.49', port=8000):
        self.host = host
        self.port = port
        self.socket = None
        
    async def connect(self):
        """Conecta ao servidor GPS"""
        print(f"🔌 Conectando ao servidor {self.host}:{self.port}...")
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.host, self.port))
            print("✅ Conectado com sucesso!")
            return True
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            return False
    
    def send_gps_data(self, imei='123456789012345'):
        """Envia dados GPS simulados"""
        # Coordenadas de São Paulo como exemplo
        lat = -23.550520
        lon = -46.633308
        
        # Timestamp atual
        now = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # Mensagem GPS no formato GV50
        message = (
            f"+RESP:GTFRI,060228,{imei},,0,0,1,1,4.3,92,70.0,"
            f"{lon},{lat},{now},0460,0000,18d8,6141,00,2000.0,"
            f"{now},11F0$"
        )
        
        print(f"📡 Enviando: {message}")
        self.socket.send(message.encode())
        
        # Aguardar resposta
        try:
            response = self.socket.recv(1024).decode()
            print(f"📨 Resposta: {response}")
        except:
            print("⚠️ Nenhuma resposta recebida")
    
    def disconnect(self):
        """Desconecta do servidor"""
        if self.socket:
            self.socket.close()
            print("🔌 Desconectado")

async def main():
    print("🧪 SIMULADOR DE DISPOSITIVO GPS GV50\n")
    
    simulator = GPSDeviceSimulator()
    
    if await simulator.connect():
        try:
            # Simular 3 envios de dados GPS
            for i in range(3):
                print(f"\n📍 Enviando dados GPS #{i+1}...")
                simulator.send_gps_data()
                await asyncio.sleep(2)
                
            print("\n✅ Simulação concluída!")
            
        except KeyboardInterrupt:
            print("\n⏹️ Simulação interrompida pelo usuário")
        except Exception as e:
            print(f"\n❌ Erro durante simulação: {e}")
        finally:
            simulator.disconnect()
    else:
        print("❌ Não foi possível conectar ao servidor")
        print("💡 Verifique se o serviço GPS está rodando:")
        print("   sudo systemctl status gps-service")

if __name__ == "__main__":
    asyncio.run(main())