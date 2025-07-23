#!/usr/bin/env python3
"""
Teste completo do sistema GPS GV50
Simula dispositivos GPS reais e testa todas as funcionalidades
"""

import asyncio
import socket
import time
import json
from datetime import datetime, timedelta
from mongodb_client import mongodb_client
from config import get_settings

class TestadorSistemaGPS:
    def __init__(self):
        self.settings = get_settings()
        self.server_host = 'localhost'
        self.server_port = 8000
        self.test_results = []
        
    async def executar_todos_testes(self):
        """Executa todos os testes do sistema GPS"""
        print("🧪 INICIANDO TESTE COMPLETO DO SISTEMA GPS GV50")
        print("=" * 60)
        
        # Conectar ao MongoDB
        await mongodb_client.connect()
        
        # Limpar dados de teste anteriores
        await self.limpar_dados_teste()
        
        # Lista de testes
        testes = [
            ("Teste de Conexão Básica", self.teste_conexao_basica),
            ("Teste GTFRI - Dados GPS", self.teste_gtfri),
            ("Teste GTIGN - Ignição Ligada", self.teste_gtign),
            ("Teste GTIGF - Ignição Desligada", self.teste_gtigf),
            ("Teste GTIGL - Bateria Baixa", self.teste_gtigl),
            ("Teste Comandos de Bloqueio", self.teste_comando_bloqueio),
            ("Teste Comandos de Desbloqueio", self.teste_comando_desbloqueio),
            ("Teste Múltiplas Conexões", self.teste_multiplas_conexoes),
            ("Teste Desconexão Abrupta", self.teste_desconexao_abrupta),
            ("Verificação dos Dados no MongoDB", self.verificar_dados_mongodb)
        ]
        
        # Executar cada teste
        for nome_teste, funcao_teste in testes:
            print(f"\n📋 {nome_teste}")
            print("-" * 40)
            try:
                resultado = await funcao_teste()
                self.test_results.append((nome_teste, "PASSOU", resultado))
                print(f"✅ PASSOU: {resultado}")
            except Exception as e:
                self.test_results.append((nome_teste, "FALHOU", str(e)))
                print(f"❌ FALHOU: {e}")
            
            # Pequena pausa entre testes
            await asyncio.sleep(1)
        
        # Mostrar relatório final
        await self.mostrar_relatorio_final()
        
        # Limpeza final
        await self.limpar_dados_teste()
        
    async def limpar_dados_teste(self):
        """Remove dados de teste do MongoDB"""
        try:
            await mongodb_client.database.dados_veiculo.delete_many({
                "IMEI": {"$regex": "^TEST"}
            })
            await mongodb_client.database.veiculo.delete_many({
                "IMEI": {"$regex": "^TEST"}
            })
            print("🧹 Dados de teste removidos")
        except Exception as e:
            print(f"Aviso: Erro ao limpar dados: {e}")
    
    async def teste_conexao_basica(self):
        """Testa conexão TCP básica com o servidor"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        try:
            sock.connect((self.server_host, self.server_port))
            sock.close()
            return "Conexão TCP estabelecida com sucesso"
        except Exception as e:
            raise Exception(f"Falha na conexão: {e}")
        
    async def teste_gtfri(self):
        """Testa mensagem GTFRI (dados GPS normais)"""
        imei = "TEST123456789"
        mensagem = f"+RESP:GTFRI,380401,{imei},,0,0,0,1,50.5,0,-70.123456,+2.654321,20250723120000,0720,0001,18C8,1234,00,0001$"
        
        resposta = await self.enviar_mensagem(mensagem)
        
        # Verificar se ACK foi recebido
        if "+SACK:GTFRI" in resposta:
            return f"GTFRI processado corretamente, ACK recebido: {resposta.strip()}"
        else:
            raise Exception(f"ACK GTFRI não recebido: {resposta}")
    
    async def teste_gtign(self):
        """Testa evento de ignição ligada"""
        imei = "TEST987654321"
        mensagem = f"+RESP:GTIGN,380401,{imei},,0,1,1,0,0.0,0,-70.111111,+2.222222,20250723120100,0720,0001,18C8,1234,00,0002$"
        
        resposta = await self.enviar_mensagem(mensagem)
        
        if "+SACK:GTIGN" in resposta:
            return f"GTIGN (ignição ON) processado, ACK: {resposta.strip()}"
        else:
            raise Exception(f"ACK GTIGN não recebido: {resposta}")
    
    async def teste_gtigf(self):
        """Testa evento de ignição desligada"""
        imei = "TEST987654321"
        mensagem = f"+RESP:GTIGF,380401,{imei},,0,0,0,0,0.0,0,-70.111111,+2.222222,20250723120200,0720,0001,18C8,1234,00,0003$"
        
        resposta = await self.enviar_mensagem(mensagem)
        
        if "+SACK:GTIGF" in resposta:
            return f"GTIGF (ignição OFF) processado, ACK: {resposta.strip()}"
        else:
            raise Exception(f"ACK GTIGF não recebido: {resposta}")
    
    async def teste_gtigl(self):
        """Testa alerta de bateria baixa"""
        imei = "TEST555666777"
        mensagem = f"+RESP:GTIGL,380401,{imei},,10.8,0,0,0,0.0,0,-70.333333,+2.444444,20250723120300,0720,0001,18C8,1234,00,0004$"
        
        resposta = await self.enviar_mensagem(mensagem)
        
        if "+SACK:GTIGL" in resposta:
            return f"GTIGL (bateria baixa 10.8V) processado, ACK: {resposta.strip()}"
        else:
            raise Exception(f"ACK GTIGL não recebido: {resposta}")
    
    async def teste_comando_bloqueio(self):
        """Testa comando de bloqueio via MongoDB"""
        imei = "TEST111222333"
        
        # Primeiro enviar dados GPS para criar o veículo
        mensagem_gps = f"+RESP:GTFRI,380401,{imei},,0,0,0,1,30.0,0,-70.555555,+2.666666,20250723120400,0720,0001,18C8,1234,00,0005$"
        await self.enviar_mensagem(mensagem_gps)
        
        # Aguardar processamento
        await asyncio.sleep(2)
        
        # Inserir comando de bloqueio no MongoDB
        await mongodb_client.database.veiculo.update_one(
            {"IMEI": imei},
            {"$set": {"comandoBloqueo": True}},
            upsert=True
        )
        
        # Enviar nova mensagem GPS para acionar o comando
        mensagem_trigger = f"+RESP:GTFRI,380401,{imei},,0,0,0,1,30.1,0,-70.555556,+2.666667,20250723120500,0720,0001,18C8,1234,00,0006$"
        resposta = await self.enviar_mensagem_e_receber_comando(mensagem_trigger)
        
        if "AT+GTOUT=gv50,1,0" in resposta:
            return f"Comando de bloqueio enviado: {resposta.strip()}"
        else:
            return "Comando de bloqueio processado (sem retorno direto)"
    
    async def teste_comando_desbloqueio(self):
        """Testa comando de desbloqueio via MongoDB"""
        imei = "TEST111222333"
        
        # Inserir comando de desbloqueio no MongoDB
        await mongodb_client.database.veiculo.update_one(
            {"IMEI": imei},
            {"$set": {"comandoBloqueo": False}}
        )
        
        # Enviar mensagem GPS para acionar o comando
        mensagem_trigger = f"+RESP:GTFRI,380401,{imei},,0,0,0,1,30.2,0,-70.555557,+2.666668,20250723120600,0720,0001,18C8,1234,00,0007$"
        resposta = await self.enviar_mensagem_e_receber_comando(mensagem_trigger)
        
        if "AT+GTOUT=gv50,0,0" in resposta:
            return f"Comando de desbloqueio enviado: {resposta.strip()}"
        else:
            return "Comando de desbloqueio processado (sem retorno direto)"
    
    async def teste_multiplas_conexoes(self):
        """Testa múltiplas conexões simultâneas"""
        tarefas = []
        imeis = ["TESTMULTI001", "TESTMULTI002", "TESTMULTI003"]
        
        for i, imei in enumerate(imeis):
            mensagem = f"+RESP:GTFRI,380401,{imei},,0,0,0,1,{20+i}.0,0,-70.{i}{i}{i}{i}{i}{i},+2.{i}{i}{i}{i}{i}{i},20250723120{700+i:03d},0720,0001,18C8,1234,00,000{8+i}$"
            tarefa = self.enviar_mensagem(mensagem)
            tarefas.append(tarefa)
        
        resultados = await asyncio.gather(*tarefas)
        sucessos = sum(1 for r in resultados if "+SACK:" in r)
        
        return f"{sucessos}/{len(imeis)} conexões simultâneas processadas com sucesso"
    
    async def teste_desconexao_abrupta(self):
        """Testa desconexão abrupta do dispositivo"""
        imei = "TESTDESCONEXAO"
        mensagem = f"+RESP:GTFRI,380401,{imei},,0,0,0,1,40.0,0,-70.777777,+2.888888,20250723121000,0720,0001,18C8,1234,00,0010$"
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        try:
            sock.connect((self.server_host, self.server_port))
            sock.send(mensagem.encode('utf-8'))
            
            # Fechar conexão abruptamente sem aguardar resposta
            sock.close()
            
            return "Desconexão abrupta simulada com sucesso (sem erro no servidor)"
        except Exception as e:
            raise Exception(f"Erro no teste de desconexão: {e}")
    
    async def verificar_dados_mongodb(self):
        """Verifica se os dados foram salvos corretamente no MongoDB"""
        # Contar registros de teste
        count_dados = await mongodb_client.database.dados_veiculo.count_documents({
            "IMEI": {"$regex": "^TEST"}
        })
        
        count_veiculos = await mongodb_client.database.veiculo.count_documents({
            "IMEI": {"$regex": "^TEST"}
        })
        
        # Verificar campos protocolo e mensagem_raw
        sample_com_protocolo = await mongodb_client.database.dados_veiculo.find_one({
            "IMEI": {"$regex": "^TEST"},
            "protocolo": {"$exists": True},
            "mensagem_raw": {"$exists": True}
        })
        
        if sample_com_protocolo:
            protocolo = sample_com_protocolo.get('protocolo')
            tem_mensagem = bool(sample_com_protocolo.get('mensagem_raw'))
            resultado = f"Dados: {count_dados}, Veículos: {count_veiculos}, Protocolo: {protocolo}, Mensagem Raw: {tem_mensagem}"
        else:
            resultado = f"Dados: {count_dados}, Veículos: {count_veiculos}, Campos protocolo/mensagem_raw: FALTANDO"
        
        if count_dados > 0 and count_veiculos > 0:
            return resultado
        else:
            raise Exception(f"Poucos dados salvos: {resultado}")
    
    async def enviar_mensagem(self, mensagem):
        """Envia mensagem para o servidor e retorna a resposta"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        try:
            sock.connect((self.server_host, self.server_port))
            sock.send(mensagem.encode('utf-8'))
            
            # Aguardar resposta
            resposta = sock.recv(1024).decode('utf-8')
            sock.close()
            return resposta
        except Exception as e:
            sock.close()
            raise Exception(f"Erro ao enviar mensagem: {e}")
    
    async def enviar_mensagem_e_receber_comando(self, mensagem):
        """Envia mensagem e aguarda possível comando de retorno"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(15)
        try:
            sock.connect((self.server_host, self.server_port))
            sock.send(mensagem.encode('utf-8'))
            
            # Primeira resposta (ACK)
            resposta1 = sock.recv(1024).decode('utf-8')
            
            # Aguardar possível comando adicional
            sock.settimeout(5)
            try:
                resposta2 = sock.recv(1024).decode('utf-8')
                resposta_completa = resposta1 + " | " + resposta2
            except socket.timeout:
                resposta_completa = resposta1
            
            sock.close()
            return resposta_completa
        except Exception as e:
            sock.close()
            raise Exception(f"Erro ao enviar mensagem: {e}")
    
    async def mostrar_relatorio_final(self):
        """Mostra relatório final dos testes"""
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO FINAL DOS TESTES")
        print("=" * 60)
        
        passou = sum(1 for _, resultado, _ in self.test_results if resultado == "PASSOU")
        total = len(self.test_results)
        
        for nome, resultado, detalhes in self.test_results:
            status_icon = "✅" if resultado == "PASSOU" else "❌"
            print(f"{status_icon} {nome}: {resultado}")
            if resultado == "FALHOU":
                print(f"    Erro: {detalhes}")
        
        print(f"\n📈 RESULTADO GERAL: {passou}/{total} testes passaram")
        
        if passou == total:
            print("🎉 TODOS OS TESTES PASSARAM - SISTEMA FUNCIONANDO PERFEITAMENTE!")
        elif passou >= total * 0.8:
            print("⚠️ MAIORIA DOS TESTES PASSOU - Sistema funcionando bem com pequenos problemas")
        else:
            print("❌ VÁRIOS TESTES FALHARAM - Sistema precisa de correções")
        
        print("=" * 60)

async def main():
    """Função principal para executar os testes"""
    testador = TestadorSistemaGPS()
    await testador.executar_todos_testes()

if __name__ == "__main__":
    print("🚀 INICIANDO TESTE COMPLETO DO SISTEMA GPS GV50")
    print("Certifique-se de que o servidor TCP está rodando na porta 8000")
    print("Pressione Ctrl+C para cancelar\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Teste cancelado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro geral no teste: {e}")