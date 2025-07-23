#!/usr/bin/env python3
"""
Monitor em tempo real para conexões GPS
Mostra logs de dispositivos conectando em tempo real
"""

import asyncio
import subprocess
import time
from datetime import datetime

class RealTimeMonitor:
    def __init__(self):
        self.log_file = "logs/gps_service.log"
        self.last_position = 0
        
    def get_timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    async def monitor_connections(self):
        """Monitora conexões em tempo real"""
        print(f"🔍 [{self.get_timestamp()}] Iniciando monitor de conexões GPS...")
        print("=" * 60)
        
        try:
            # Obtém posição atual do arquivo de log
            with open(self.log_file, 'r') as f:
                f.seek(0, 2)  # Vai para o final do arquivo
                self.last_position = f.tell()
                
            while True:
                await self.check_new_logs()
                await asyncio.sleep(1)  # Verifica a cada segundo
                
        except KeyboardInterrupt:
            print(f"\n🛑 [{self.get_timestamp()}] Monitor interrompido pelo usuário")
        except Exception as e:
            print(f"❌ [{self.get_timestamp()}] Erro no monitor: {e}")
    
    async def check_new_logs(self):
        """Verifica se há novos logs"""
        try:
            with open(self.log_file, 'r') as f:
                f.seek(self.last_position)
                new_lines = f.readlines()
                self.last_position = f.tell()
                
                for line in new_lines:
                    self.process_log_line(line.strip())
                    
        except FileNotFoundError:
            pass  # Log file não existe ainda
    
    def process_log_line(self, line):
        """Processa cada linha de log relevante"""
        if not line:
            return
            
        # Conexões
        if "Nova conexão GPS" in line:
            print(f"🔌 [{self.get_timestamp()}] {line}")
            
        # Mensagens recebidas
        elif "Recebido de" in line and "RESP:" in line:
            # Extrai apenas o tipo de mensagem
            if "GTFRI" in line:
                print(f"📍 [{self.get_timestamp()}] GPS Data recebido (GTFRI)")
            elif "GTIGN" in line:
                print(f"🔑 [{self.get_timestamp()}] Ignição LIGADA (GTIGN)")
            elif "GTIGF" in line:
                print(f"🔒 [{self.get_timestamp()}] Ignição DESLIGADA (GTIGF)")
            elif "BUFF:" in line:
                print(f"📦 [{self.get_timestamp()}] Mensagem BUFF recebida")
            else:
                print(f"📨 [{self.get_timestamp()}] Mensagem GPS recebida")
                
        # Dados salvos
        elif "Dados inseridos para IMEI" in line:
            # Extrai IMEI da linha
            imei_start = line.find("IMEI ") + 5
            imei_end = line.find(":", imei_start)
            imei = line[imei_start:imei_end] if imei_end > imei_start else "Unknown"
            print(f"💾 [{self.get_timestamp()}] Dados salvos no MongoDB - IMEI: {imei}")
            
        # Comandos enviados
        elif "Enviando comando" in line:
            if "DESBLOQUEIO" in line:
                print(f"🔓 [{self.get_timestamp()}] Comando DESBLOQUEIO enviado")
            elif "BLOQUEIO" in line:
                print(f"🔒 [{self.get_timestamp()}] Comando BLOQUEIO enviado")
            elif "IP" in line:
                print(f"🌐 [{self.get_timestamp()}] Comando troca de IP enviado")
                
        # Erros importantes
        elif "ERROR" in line or "Erro" in line:
            print(f"❌ [{self.get_timestamp()}] ERRO: {line}")
            
        # Desconexões
        elif "desconectou" in line or "Connection reset" in line:
            print(f"📴 [{self.get_timestamp()}] Dispositivo desconectado")

    def show_current_status(self):
        """Mostra status atual do sistema"""
        print("📊 STATUS DO SISTEMA GPS GV50")
        print("=" * 40)
        
        # Verifica se servidor está rodando
        try:
            result = subprocess.run(['pgrep', '-f', 'main.py'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Servidor TCP: RODANDO")
            else:
                print("❌ Servidor TCP: PARADO")
        except:
            print("❓ Servidor TCP: Status desconhecido")
            
        # Últimos logs
        try:
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_log = lines[-1].strip()
                    print(f"🕐 Último log: {last_log}")
                else:
                    print("📄 Nenhum log encontrado")
        except:
            print("📄 Arquivo de log não encontrado")
            
        print("=" * 40)

async def main():
    monitor = RealTimeMonitor()
    
    # Mostra status inicial
    monitor.show_current_status()
    print()
    
    # Inicia monitoramento
    await monitor.monitor_connections()

if __name__ == "__main__":
    asyncio.run(main())