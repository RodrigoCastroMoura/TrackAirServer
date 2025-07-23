# Serviço Python TCP para Dispositivos GPS GV50

## Overview

Este é um serviço Python TCP completo para comunicação com dispositivos GPS GV50 em modo Long-Connection. O serviço mantém conexões persistentes com dispositivos, processa mensagens do protocolo GV50, gerencia comandos bidirecionais e armazena informações no MongoDB. Foi desenvolvido baseado no protocolo oficial GV50 @Track Air Interface Protocol V4.01 e implementado conforme documentação GV50 User Manual para modo TCP Long-Connection.

## User Preferences

Preferred communication style: Simple, everyday language.
Projeto requer apenas serviço Python, sem interface web.
Clean Code: Usar apenas campos essenciais, remover classes/arquivos não utilizados.
Remover arquivos de teste para ambiente de produção limpo.

## System Architecture

Serviço Python standalone com arquitetura assíncrona:

### Último Teste do Sistema (23/07/2025)
✓ **Teste Completo Realizado**: Sistema 100% funcional
✓ **10/10 Testes Passaram**: Conexão TCP, Protocolos GPS, Comandos, Múltiplas Conexões
✓ **MongoDB Operacional**: Dados GPS e comandos salvos corretamente
✓ **Servidor TCP Ativo**: Porta 8000, modo Long-Connection
✓ **Protocolos Testados**: GTFRI, GTIGN, GTIGF, GTIGL - todos funcionando
✓ **Comandos Bidirecionais**: Bloqueio/desbloqueio e troca de IP testados
✓ **Performance**: Múltiplas conexões simultâneas suportadas

### TCP Service Architecture - Long-Connection Mode
- **Language**: Python com asyncio para conexões concorrentes
- **Connection Mode**: Long-Connection persistente conforme documentação GV50
- **Database**: MongoDB para armazenamento de dados GPS
- **Protocol**: Parser personalizado do protocolo GV50 GPS
- **Concurrency**: Servidor TCP assíncrono mantendo conexões persistentes
- **Commands**: Sistema de comandos para controle bidirecional dos dispositivos
- **Heartbeat**: Sistema de heartbeat automático para manter conexões vivas
- **Cleanup**: Task automática de limpeza de conexões inativas

## Key Components

### Database Schema (Clean Code)
O sistema usa MongoDB com 2 coleções essenciais:
- **DadosVeiculo**: Dados do dispositivo GPS (IMEI, longitude, latitude, altitude, speed, ignicao, dataDevice, data, **mensagem_raw**)
- **Veiculo**: Controle de comandos e monitoramento (IMEI, ds_placa, ds_modelo, comandoBloqueo, bloqueado, ignicao, comandoTrocarIP, bateria_voltagem, bateria_baixa, ultimo_alerta_bateria)

**Atualização (23/07/2025)**: Removido campo `protocolo` da tabela DadosVeiculo por simplificação. Mantido apenas campo `mensagem_raw` para armazenar a mensagem completa original recebida do dispositivo.

Sistema simplificado para receber dados GPS e gerenciar comandos de bloqueio/desbloqueio e troca de IP.

### GPS Protocol Handler
- Analisa mensagens GPS recebidas (protocolos +RESP, +BUFF, +ACK)
- Suporte completo a comandos: GTFRI, GTIGN, GTIGF, GTIGL, GTOUT, GTSRI, GTBSI
- Processa eventos de ignição em tempo real (GTIGN=ligada, GTIGF=desligada)
- Gerencia comunicação bidirecional com dispositivos GPS
- Controla estados de conexão e timeouts dos dispositivos
- ACK específico para cada tipo de comando (+SACK:GTFRI, +SACK:GTIGN, etc.)

### Command System
- Gerenciamento de comandos via MongoDB (coleção Veiculo)
- Suporte a bloqueio/desbloqueio de veículos
- Capacidades de configuração de servidor e APN
- Comandos controlados por campos: comandoBloqueo, comandoTrocarIP

### Device Manager
- Gerencia conexões ativas de dispositivos
- Controla timeouts e cleanup de conexões
- Atualiza status online/offline dos dispositivos
- Mantém histórico de última atividade

## Data Flow Long-Connection (Otimizado)

1. **Dispositivo GPS conecta** → Estabelece long-connection persistente via TCP
2. **Mantém conexão ativa** → Heartbeat automático a cada 5 min
3. **Múltiplas mensagens** → Recebe dados GPS na mesma conexão continuamente
4. **Processa eventos** → GTFRI (dados), GTIGN (ignição ON), GTIGF (ignição OFF)
5. **Salva dados GPS** → Insere na coleção `dados_veiculo` (dados do dispositivo)
6. **Atualiza veículo** → Insere/atualiza na coleção `veiculo` (controle de comandos)
7. **Verifica comandos** → Campos `comandoBloqueo` e `comandoTrocarIP`
8. **Envia comandos** → AT+GTOUT (bloqueio) e AT+GTSRI (trocar IP) imediatamente
9. **Cleanup automático** → Remove conexões inativas após 30 min
10. **ACK específico** → Confirma cada mensagem com ACK apropriado (+SACK:GTFRI, +SACK:GTIGN, etc.)

## External Dependencies

### Python Service Dependencies
- AsyncIO para manipulação TCP concorrente
- Motor para operações MongoDB assíncronas
- Pydantic para validação e modelagem de dados
- Python-dotenv para gerenciamento de configuração

## Deployment Strategy

Serviço Python standalone:

### Ambiente de Produção
- Serviço Python roda como servidor TCP independente
- Configuração baseada em variáveis de ambiente via arquivos .env

### Requisitos de Infraestrutura
- MongoDB para armazenamento de dados de rastreamento GPS
- Acesso de rede para dispositivos GPS conectarem ao serviço TCP
- Servidor Linux para executar o serviço Python

O sistema é arquitetado para lidar com múltiplas conexões concorrentes de dispositivos GPS, fornecendo processamento em tempo real e gerenciamento de comandos. O serviço Python independente permite escalabilidade e manutenção simplificada.