#!/usr/bin/env python3
"""
Teste de conexão com MongoDB Atlas
"""

import asyncio
from mongodb_client import mongodb_client
from logger import get_logger

logger = get_logger(__name__)

async def test_connection():
    """Testa a conexão com MongoDB Atlas."""
    try:
        print("Testando conexão com MongoDB Atlas...")
        
        # Conectar ao MongoDB
        await mongodb_client.connect()
        
        # Testar operação básica
        print("✓ Conexão estabelecida com sucesso!")
        
        # Listar coleções existentes
        collections = await mongodb_client.database.list_collection_names()
        print(f"✓ Coleções encontradas: {collections}")
        
        # Testar inserção de dados de teste
        from models import VehicleData
        from datetime import datetime
        
        test_data = VehicleData(
            imei="123456789012345",
            longitude="-46.633308",
            latitude="-23.550520",
            altitude="760",
            speed="0",
            ignition=False,
            timestamp=datetime.utcnow(),
            device_time="20241221163000",
            raw_data="+RESP:GTFRI,060228,123456789012345,,0,0,1,1,4.3,92,70.0,-46.633308,-23.550520,20241221163000,0460,0000,18d8,6141,00,2000.0,20241221163000,11F0$"
        )
        
        # Inserir dados de teste
        vehicle_id = await mongodb_client.insert_vehicle_data(test_data)
        print(f"✓ Dados de teste inseridos com ID: {vehicle_id}")
        
        # Buscar dados inseridos
        vehicle_data = await mongodb_client.get_vehicle_data_by_imei("123456789012345", 1)
        if vehicle_data:
            print(f"✓ Dados recuperados: {len(vehicle_data)} registro(s)")
            print(f"  IMEI: {vehicle_data[0].imei}")
            print(f"  Posição: {vehicle_data[0].latitude}, {vehicle_data[0].longitude}")
            print(f"  Timestamp: {vehicle_data[0].timestamp}")
        
        print("\n✅ Teste de conexão concluído com sucesso!")
        print("O serviço está pronto para receber dados dos dispositivos GPS.")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        logger.error(f"Erro no teste de conexão: {e}")
        
    finally:
        await mongodb_client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_connection())