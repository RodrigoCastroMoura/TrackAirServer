#!/usr/bin/env python3
"""
Verificação simples para dados BUFF na base de dados
"""

import asyncio
from mongodb_client import mongodb_client

async def verificar_dados_buff():
    """Verifica se existem dados BUFF na tabela dados_veiculo"""
    
    print("🔍 Verificando dados BUFF na tabela dados_veiculo...")
    
    try:
        await mongodb_client.connect()
        
        # Buscar dados que contenham BUFF na mensagem_raw
        dados_buff = await mongodb_client.database.dados_veiculo.find({
            'mensagem_raw': {'$regex': r'\+BUFF:'}
        }).to_list(100)
        
        # Buscar dados que contenham RESP para comparação
        dados_resp = await mongodb_client.database.dados_veiculo.find({
            'mensagem_raw': {'$regex': r'\+RESP:'}
        }).to_list(100)
        
        print(f"📊 Resultados da verificação:")
        print(f"   - Registros com +BUFF: {len(dados_buff)}")
        print(f"   - Registros com +RESP: {len(dados_resp)}")
        print(f"   - Total de registros: {len(dados_buff) + len(dados_resp)}")
        
        if len(dados_buff) > 0:
            print("\n✅ CONFIRMADO: Sistema ESTÁ gravando dados BUFF na tabela dados_veiculo!")
            
            print("\n📋 Exemplos de dados BUFF encontrados:")
            for i, dado in enumerate(dados_buff[:3]):
                mensagem = dado.get('mensagem_raw', 'N/A')
                imei = dado.get('IMEI', 'N/A')
                ignition = dado.get('ignicao', 'N/A')
                
                # Extrair protocolo da mensagem
                protocolo = 'DESCONHECIDO'
                if '+BUFF:GTFRI' in mensagem:
                    protocolo = 'GTFRI'
                elif '+BUFF:GTIGN' in mensagem:
                    protocolo = 'GTIGN'
                elif '+BUFF:GTIGF' in mensagem:
                    protocolo = 'GTIGF'
                elif '+BUFF:GTIGL' in mensagem:
                    protocolo = 'GTIGL'
                
                print(f"  {i+1}. IMEI: {imei} | Protocolo: {protocolo} | Ignição: {ignition}")
                print(f"     Mensagem: {mensagem[:70]}...")
        else:
            print("\n❌ Sistema NÃO está gravando dados BUFF na tabela dados_veiculo!")
            
            if len(dados_resp) > 0:
                print(f"⚠️ Mas encontrei {len(dados_resp)} registros RESP - sistema funciona para RESP")
            else:
                print("⚠️ Também não encontrei dados RESP - verificar se sistema está funcionando")
        
        # Buscar todos os tipos de mensagem
        print("\n🎯 Análise de tipos de mensagem:")
        
        cursor = mongodb_client.database.dados_veiculo.find({}, {'mensagem_raw': 1})
        tipos_encontrados = set()
        
        async for doc in cursor:
            mensagem = doc.get('mensagem_raw', '')
            if '+BUFF:' in mensagem:
                tipos_encontrados.add('BUFF')
            if '+RESP:' in mensagem:
                tipos_encontrados.add('RESP')
            if '+ACK:' in mensagem:
                tipos_encontrados.add('ACK')
        
        print(f"   - Tipos de mensagem encontrados: {list(tipos_encontrados)}")
        
    except Exception as e:
        print(f"❌ Erro ao verificar dados: {e}")

if __name__ == "__main__":
    asyncio.run(verificar_dados_buff())