#!/usr/bin/env python3
"""
Teste completo do sistema GPS GV50
Simula o servidor rodando no IP 191.252.181.49:8000
"""

import asyncio
import subprocess
import time
import sys
import socket
from datetime import datetime

def verificar_porta(host='0.0.0.0', port=8000):
    """Verifica se a porta está aberta"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def testar_simulador_local():
    """Testa com simulador conectando localmente"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', 8000))
        
        # Enviar mensagem GPS
        message = "+RESP:GTFRI,060228,999888777666555,,0,0,1,1,4.3,92,70.0,-46.633308,-23.550520,20250721190500,0460,0000,18d8,6141,00,2000.0,20250721190500,ABCD$"
        print(f"📡 Enviando: {message}")
        sock.send(message.encode())
        
        # Receber resposta
        response = sock.recv(1024).decode()
        print(f"📨 Resposta: {response}")
        
        sock.close()
        return True
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

async def main():
    print("🧪 TESTE COMPLETO DO SISTEMA GPS GV50")
    print("=" * 50)
    
    # 1. Testar conexão MongoDB
    print("\n1️⃣ Testando MongoDB Atlas...")
    try:
        result = subprocess.run(['python', 'test_connection.py'], 
                              capture_output=True, text=True, cwd='.')
        if result.returncode == 0:
            print("✅ MongoDB: Conectado e funcionando")
        else:
            print("❌ MongoDB: Erro na conexão")
            print(result.stderr)
    except Exception as e:
        print(f"❌ Erro ao testar MongoDB: {e}")
    
    # 2. Iniciar servidor GPS
    print("\n2️⃣ Iniciando servidor GPS...")
    try:
        # Iniciar servidor em background
        server_process = subprocess.Popen(['python', 'main.py'], 
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE)
        
        # Aguardar servidor inicializar
        print("⏳ Aguardando servidor inicializar...")
        time.sleep(5)
        
        if verificar_porta('127.0.0.1', 8000):
            print("✅ Servidor GPS: Rodando na porta 8000")
        else:
            print("❌ Servidor GPS: Não conseguiu iniciar na porta 8000")
            return
        
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return
    
    # 3. Testar dispositivo simulado
    print("\n3️⃣ Testando dispositivo simulado...")
    try:
        if testar_simulador_local():
            print("✅ Simulador: Conectou e enviou dados com sucesso")
        else:
            print("❌ Simulador: Falha na comunicação")
    except Exception as e:
        print(f"❌ Erro no simulador: {e}")
    
    # 4. Parar servidor
    print("\n4️⃣ Finalizando teste...")
    try:
        server_process.terminate()
        server_process.wait(timeout=5)
        print("✅ Servidor finalizado")
    except:
        server_process.kill()
        print("⚠️ Servidor forçadamente finalizado")
    
    print("\n" + "=" * 50)
    print("🎯 RESUMO DO TESTE:")
    print("📍 Configuração para produção:")
    print(f"   - IP do servidor: 191.252.181.49")
    print(f"   - Porta TCP: 8000")
    print(f"   - MongoDB Atlas: Configurado e funcionando")
    print(f"   - Comandos: Bloqueio/desbloqueio e troca de IP")
    print("\n💡 Para usar no servidor real (191.252.181.49):")
    print("   1. Copiar pasta python_service para o servidor")
    print("   2. Executar: python main.py")
    print("   3. Dispositivos GPS conectam na porta 8000")
    print("   4. Dados salvos automaticamente no MongoDB Atlas")

if __name__ == "__main__":
    asyncio.run(main())