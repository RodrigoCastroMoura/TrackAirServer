#!/usr/bin/env python3
"""
Script de teste para verificar se as mensagens dos protocolos estão sendo gravadas corretamente
"""

import socket
import time
import asyncio
from mongodb_client import mongodb_client
from config import get_settings

async def test_protocol_recording():
    """Envia mensagens de teste e verifica se os protocolos estão sendo gravados"""
    
    # Aguardar um pouco para garantir que o serviço esteja pronto
    await asyncio.sleep(2)
    
    # Conectar ao MongoDB para verificar os dados
    await mongodb_client.connect()
    
    # Limpar dados de teste anteriores
    await mongodb_client.db.dados_veiculo.delete_many({"IMEI": "123456789012345"})
    
    print("📤 Enviando mensagens de teste...")
    
    # Mensagens de exemplo para diferentes protocolos
    test_messages = [
        "+RESP:GTFRI,380401,123456789012345,,0,0,0,1,0.0,0,-70.000000,+2.000000,20220722120000,0720,0001,18C8,1234,00,0000$",
        "+RESP:GTIGN,380401,123456789012345,,0,1,1,0,0.0,0,-70.000000,+2.000000,20220722120100,0720,0001,18C8,1234,00,0002$",
        "+RESP:GTIGF,380401,123456789012345,,0,0,0,0,0.0,0,-70.000000,+2.000000,20220722120200,0720,0001,18C8,1234,00,0003$",
        "+RESP:GTIGL,380401,123456789012345,,12.5,0,0,0,0.0,0,-70.000000,+2.000000,20220722120300,0720,0001,18C8,1234,00,0004$"
    ]
    
    # Enviar cada mensagem para o servidor
    for i, message in enumerate(test_messages):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(('localhost', 8000))
                sock.send((message).encode('utf-8'))
                
                # Aguardar resposta do servidor (ACK)
                response = sock.recv(1024).decode('utf-8')
                print(f"✅ Mensagem {i+1} enviada. Resposta: {response.strip()}")
                
                time.sleep(1)  # Pequena pausa entre mensagens
                
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem {i+1}: {e}")
    
    # Aguardar processar as mensagens
    await asyncio.sleep(3)
    
    # Verificar se os dados foram salvos corretamente
    print("\n🔍 Verificando dados salvos no MongoDB...")
    
    dados = await mongodb_client.db.dados_veiculo.find({"IMEI": "123456789012345"}).to_list(10)
    
    print(f"📊 Encontrados {len(dados)} registros para o IMEI de teste")
    
    for i, dado in enumerate(dados):
        mensagem = dado.get('mensagem_raw', 'N/A')[:50] + '...' if len(dado.get('mensagem_raw', '')) > 50 else dado.get('mensagem_raw', 'N/A')
        ignicao = dado.get('ignicao', False)
        
        print(f"  {i+1}. Ignição: {ignicao}")
        print(f"     Mensagem: {mensagem}")
        print()
    
    # Verificar se todos os tipos de mensagem foram processados
    mensagens_com_dados = [dado for dado in dados if dado.get('mensagem_raw')]
    tipos_esperados = ['GTFRI', 'GTIGN', 'GTIGF', 'GTIGL']
    tipos_encontrados = set()
    
    for dado in mensagens_com_dados:
        mensagem_raw = dado.get('mensagem_raw', '')
        for tipo in tipos_esperados:
            if tipo in mensagem_raw:
                tipos_encontrados.add(tipo)
    
    print(f"🎯 Tipos esperados: {tipos_esperados}")
    print(f"✅ Tipos encontrados: {tipos_encontrados}")
    
    if set(tipos_esperados).issubset(tipos_encontrados):
        print("🎉 SUCESSO: Todos os tipos de mensagem foram processados corretamente!")
    else:
        tipos_faltantes = set(tipos_esperados) - tipos_encontrados
        print(f"⚠️ ATENÇÃO: Tipos não encontrados: {tipos_faltantes}")
    
    # Limpeza dos dados de teste
    await mongodb_client.db.dados_veiculo.delete_many({"IMEI": "123456789012345"})
    print("\n🧹 Dados de teste removidos.")

if __name__ == "__main__":
    print("🧪 TESTE: Verificação de gravação de protocolos GPS")
    print("=" * 50)
    asyncio.run(test_protocol_recording())