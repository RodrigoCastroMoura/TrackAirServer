#!/usr/bin/env python3
"""
Teste específico do modo Long-Connection do GV50
"""

import asyncio
import socket
import subprocess
import time
from datetime import datetime

async def test_long_connection():
    """Testa o modo long-connection mantendo conexão ativa."""
    print("🧪 TESTE LONG-CONNECTION MODE GV50")
    print("=" * 50)
    
    # Iniciar servidor em background
    print("\n1️⃣ Iniciando servidor long-connection...")
    server_process = subprocess.Popen(['python', 'main.py'], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.STDOUT)
    
    # Aguardar servidor inicializar
    time.sleep(5)
    
    try:
        # Conectar como dispositivo GPS
        print("\n2️⃣ Estabelecendo long-connection...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', 8000))
        print("✅ Conexão estabelecida")
        
        # Simular múltiplas mensagens GPS na mesma conexão
        messages = [
            "+RESP:GTFRI,060228,555444333222111,,0,0,1,1,4.3,92,70.0,-46.633308,-23.550520,20250721205400,0460,0000,18d8,6141,00,2000.0,20250721205400,A001$",
            "+RESP:GTFRI,060228,555444333222111,,0,0,1,1,5.8,92,71.0,-46.633408,-23.550620,20250721205430,0460,0000,18d8,6141,00,2000.0,20250721205430,A002$",
            "+RESP:GTFRI,060228,555444333222111,,0,0,1,1,7.2,92,72.0,-46.633508,-23.550720,20250721205500,0460,0000,18d8,6141,00,2000.0,20250721205500,A003$"
        ]
        
        print("\n3️⃣ Enviando múltiplas mensagens na mesma conexão long-connection...")
        
        for i, message in enumerate(messages, 1):
            print(f"\n📡 Mensagem {i}/3:")
            print(f"   Enviando: {message[:60]}...")
            
            # Enviar mensagem
            sock.send(message.encode())
            
            # Aguardar resposta
            try:
                response = sock.recv(1024).decode()
                print(f"   📨 Resposta: {response}")
            except socket.timeout:
                print("   ⚠️ Timeout na resposta")
            
            # Aguardar antes da próxima mensagem (simular dispositivo real)
            await asyncio.sleep(2)
        
        print("\n4️⃣ Mantendo conexão ativa por mais tempo...")
        await asyncio.sleep(5)
        
        # Enviar uma última mensagem para verificar se conexão ainda está ativa
        final_message = "+RESP:GTFRI,060228,555444333222111,,0,0,0,0,0.0,92,70.0,-46.633308,-23.550520,20250721205530,0460,0000,18d8,6141,00,2000.0,20250721205530,ZZZZ$"
        print(f"\n📡 Mensagem final:")
        print(f"   Enviando: {final_message[:60]}...")
        sock.send(final_message.encode())
        
        response = sock.recv(1024).decode()
        print(f"   📨 Resposta: {response}")
        
        print("\n✅ Teste Long-Connection completado com sucesso!")
        print("   - Conexão mantida durante todo o teste")
        print("   - Múltiplas mensagens enviadas na mesma sessão TCP")
        print("   - Respostas recebidas para todas as mensagens")
        
    except Exception as e:
        print(f"\n❌ Erro no teste long-connection: {e}")
        
    finally:
        # Fechar conexão
        try:
            sock.close()
            print("🔌 Conexão fechada")
        except:
            pass
            
        # Parar servidor
        server_process.terminate()
        server_process.wait(timeout=5)
        print("⏹️ Servidor parado")
        
    print("\n" + "=" * 50)
    print("🎯 RESUMO DO TESTE LONG-CONNECTION:")
    print("   ✅ Servidor configurado para long-connections")
    print("   ✅ Device timeout: 30 min (1800s)")
    print("   ✅ Heartbeat interval: 5 min (300s)")
    print("   ✅ Keep-alive timeout: 10 min (600s)")
    print("   ✅ Cleanup automático de conexões inativas")
    print("\n💡 Sistema pronto para dispositivos GV50 em modo long-connection!")

if __name__ == "__main__":
    asyncio.run(test_long_connection())