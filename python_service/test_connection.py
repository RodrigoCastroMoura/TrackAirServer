#!/usr/bin/env python3
"""
Teste de conexão simplificado com apenas 2 tabelas
"""

import asyncio
from mongodb_client import mongodb_client
from models import DadosVeiculo, Veiculo
from logger import get_logger
from datetime import datetime

logger = get_logger(__name__)

async def test_connection():
    """Testa conexão e operações básicas."""
    try:
        print("=== TESTE DE CONEXÃO GPS SERVICE ===")
        print("Testando MongoDB Atlas...")
        
        # Conectar
        await mongodb_client.connect()
        print("✓ Conectado ao MongoDB")
        
        # Teste 1: Inserir dados GPS
        print("\n1. Testando inserção de dados GPS...")
        dados_test = DadosVeiculo(
            IMEI="123456789012345",
            longitude="-46.633308", 
            latitude="-23.550520",
            altidude="760",
            speed="60",
            ignicao=True,
            dataDevice="20240720163000"
        )
        
        dados_id = await mongodb_client.insert_dados_veiculo(dados_test)
        print(f"✓ Dados GPS inseridos: {dados_id}")
        
        # Teste 2: Criar/atualizar veículo
        print("\n2. Testando criação de veículo...")
        veiculo_test = Veiculo(
            IMEI="123456789012345",
            ds_placa="ABC-1234",
            ignicao=True,
            comandoBloqueo=True  # Comando pendente para bloquear
        )
        
        await mongodb_client.update_veiculo(veiculo_test)
        print("✓ Veículo criado/atualizado")
        
        # Teste 3: Buscar veículo
        print("\n3. Testando busca de veículo...")
        veiculo_encontrado = await mongodb_client.get_veiculo_by_imei("123456789012345")
        if veiculo_encontrado:
            print(f"✓ Veículo encontrado: {veiculo_encontrado.ds_placa}")
            print(f"  Comando bloqueio: {veiculo_encontrado.comandoBloqueo}")
            print(f"  Status bloqueado: {veiculo_encontrado.bloqueado}")
        
        # Teste 4: Verificar comandos pendentes
        print("\n4. Testando busca de comandos pendentes...")
        pendentes = await mongodb_client.get_veiculos_com_comando_pendente()
        print(f"✓ Encontrados {len(pendentes)} veículos com comandos pendentes")
        
        # Teste 5: Definir comando de bloqueio
        print("\n5. Testando definição de comando...")
        await mongodb_client.set_comando_bloqueio("123456789012345", False)  # Desbloquear
        print("✓ Comando de desbloqueio definido")
        
        # Verificar se comando foi salvo
        veiculo_atualizado = await mongodb_client.get_veiculo_by_imei("123456789012345")
        if veiculo_atualizado:
            print(f"  Novo comando: {veiculo_atualizado.comandoBloqueo}")
        
        print("\n✅ TODOS OS TESTES PASSARAM!")
        print("\nColeções criadas no MongoDB:")
        print("- dados_veiculo: Dados GPS dos dispositivos")
        print("- veiculo: Informações e comandos dos veículos")
        print("\nO serviço está pronto para usar!")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        logger.error(f"Erro no teste: {e}")
        
    finally:
        await mongodb_client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_connection())