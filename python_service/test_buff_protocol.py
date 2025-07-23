#!/usr/bin/env python3
"""
Teste específico para verificar se mensagens BUFF estão sendo gravadas na tabela dados_veiculo
"""

import socket
import time
import asyncio
from mongodb_client import mongodb_client
from config import get_settings

async def test_buff_protocol():
    """Testa se mensagens BUFF estão sendo gravadas na tabela dados_veiculo"""
    
    print("🧪 TESTE: Verificação de gravação de protocolos BUFF")
    print("=" * 55)
    
    # Conectar ao MongoDB
    await mongodb_client.connect()
    
    # Limpar dados de teste anteriores
    test_imei = "TESTBUFF123456789"
    await mongodb_client.database.dados_veiculo.delete_many({"IMEI": test_imei})
    
    print(f"📤 Enviando mensagens BUFF para IMEI: {test_imei}")
    
    # Mensagens BUFF de exemplo
    buff_messages = [
        f"+BUFF:GTFRI,380401,{test_imei},,0,0,0,1,45.2,0,-70.123456,+2.654321,20250723140000,0720,0001,18C8,1234,00,0001$",
        f"+BUFF:GTIGN,380401,{test_imei},,0,1,1,0,0.0,0,-70.111111,+2.222222,20250723140100,0720,0001,18C8,1234,00,0002$",
        f"+BUFF:GTIGF,380401,{test_imei},,0,0,0,0,0.0,0,-70.333333,+2.444444,20250723140200,0720,0001,18C8,1234,00,0003$",
        f"+BUFF:GTIGL,380401,{test_imei},,10.2,0,0,0,0.0,0,-70.555555,+2.666666,20250723140300,0720,0001,18C8,1234,00,0004$"
    ]
    
    # Enviar cada mensagem BUFF
    for i, message in enumerate(buff_messages):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(10)
                sock.connect(('localhost', 8000))
                sock.send(message.encode('utf-8'))
                
                # Aguardar resposta do servidor
                response = sock.recv(1024).decode('utf-8')
                protocol_type = message.split(':')[1].split(',')[0]  # Extrair GTFRI, GTIGN, etc.
                print(f"✅ BUFF:{protocol_type} enviado. Resposta: {response.strip()}")
                
                time.sleep(1)  # Pausa entre mensagens
                
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem BUFF {i+1}: {e}")
    
    # Aguardar processamento
    print("\n⏱️ Aguardando processamento das mensagens...")
    await asyncio.sleep(3)
    
    # Verificar dados salvos
    print("\n🔍 Verificando dados BUFF salvos no MongoDB...")
    dados_buff = await mongodb_client.database.dados_veiculo.find({"IMEI": test_imei}).to_list(10)
    
    print(f"📊 Encontrados {len(dados_buff)} registros BUFF para o IMEI de teste")
    
    if len(dados_buff) == 0:
        print("❌ ERRO: Nenhum dado BUFF foi salvo na tabela dados_veiculo!")
        return
    
    # Analisar cada registro salvo
    for i, dado in enumerate(dados_buff):
        message_raw = dado.get('mensagem_raw', 'N/A')
        message_type = '+BUFF' if '+BUFF:' in message_raw else 'Desconhecido'
        protocol = 'DESCONHECIDO'
        
        # Extrair protocolo da mensagem raw
        if '+BUFF:GTFRI' in message_raw:
            protocol = 'GTFRI'
        elif '+BUFF:GTIGN' in message_raw:
            protocol = 'GTIGN'
        elif '+BUFF:GTIGF' in message_raw:
            protocol = 'GTIGF'
        elif '+BUFF:GTIGL' in message_raw:
            protocol = 'GTIGL'
        
        ignicao = dado.get('ignicao', 'N/A')
        longitude = dado.get('longitude', 'N/A')
        latitude = dado.get('latitude', 'N/A')
        
        print(f"  {i+1}. Tipo: {message_type} | Protocolo: {protocol}")
        print(f"     Ignição: {ignicao} | Long: {longitude} | Lat: {latitude}")
        print(f"     Mensagem: {message_raw[:60]}...")
        print()
    
    # Verificar se todos os tipos BUFF foram processados
    tipos_esperados = ['GTFRI', 'GTIGN', 'GTIGF', 'GTIGL']
    tipos_encontrados = set()
    
    for dado in dados_buff:
        message_raw = dado.get('mensagem_raw', '')
        for tipo in tipos_esperados:
            if f'+BUFF:{tipo}' in message_raw:
                tipos_encontrados.add(tipo)
    
    print(f"🎯 Tipos BUFF esperados: {tipos_esperados}")
    print(f"✅ Tipos BUFF encontrados: {list(tipos_encontrados)}")
    
    if set(tipos_esperados).issubset(tipos_encontrados):
        print("🎉 SUCESSO: Todos os tipos de mensagem BUFF foram gravados corretamente!")
        print("✅ CONFIRMADO: Sistema está gravando dados BUFF na tabela dados_veiculo")
    else:
        tipos_faltantes = set(tipos_esperados) - tipos_encontrados
        print(f"⚠️ ATENÇÃO: Tipos BUFF não encontrados: {tipos_faltantes}")
    
    # Verificar diferença entre RESP e BUFF
    print("\n📋 Verificando se sistema diferencia RESP de BUFF...")
    
    # Enviar uma mensagem RESP para comparação
    resp_message = f"+RESP:GTFRI,380401,{test_imei},,0,0,0,1,55.5,0,-70.999999,+2.888888,20250723140400,0720,0001,18C8,1234,00,0005$"
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(10)
            sock.connect(('localhost', 8000))
            sock.send(resp_message.encode('utf-8'))
            response = sock.recv(1024).decode('utf-8')
            print(f"✅ RESP:GTFRI enviado para comparação. Resposta: {response.strip()}")
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem RESP: {e}")
    
    await asyncio.sleep(2)
    
    # Verificar novamente todos os dados
    todos_dados = await mongodb_client.database.dados_veiculo.find({"IMEI": test_imei}).to_list(20)
    
    buff_count = sum(1 for d in todos_dados if '+BUFF:' in d.get('mensagem_raw', ''))
    resp_count = sum(1 for d in todos_dados if '+RESP:' in d.get('mensagem_raw', ''))
    
    print(f"📈 Resumo final:")
    print(f"   - Mensagens BUFF gravadas: {buff_count}")
    print(f"   - Mensagens RESP gravadas: {resp_count}")
    print(f"   - Total de registros: {len(todos_dados)}")
    
    if buff_count > 0:
        print("✅ CONFIRMADO: Sistema está gravando mensagens BUFF na tabela dados_veiculo!")
    else:
        print("❌ PROBLEMA: Sistema NÃO está gravando mensagens BUFF!")
    
    # Limpeza dos dados de teste
    await mongodb_client.database.dados_veiculo.delete_many({"IMEI": test_imei})
    print("\n🧹 Dados de teste removidos.")

if __name__ == "__main__":
    asyncio.run(test_buff_protocol())