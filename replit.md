# Serviço Python TCP para Dispositivos GPS GV50

## Overview

Este é um serviço Python TCP completo para comunicação com dispositivos GPS GV50 em modo Long-Connection. O serviço mantém conexões persistentes com dispositivos, processa mensagens do protocolo GV50, gerencia comandos bidirecionais e armazena informações no MongoDB. Foi desenvolvido baseado no protocolo oficial GV50 @Track Air Interface Protocol V4.01 e implementado conforme documentação GV50 User Manual para modo TCP Long-Connection.

## User Preferences

Preferred communication style: Simple, everyday language.
Projeto requer apenas serviço Python, sem interface web.
Clean Code: Usar apenas campos essenciais, remover classes/arquivos não utilizados.

## System Architecture

Serviço Python standalone com arquitetura assíncrona:

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
O sistema usa MongoDB com apenas 2 coleções essenciais:
- **DadosVeiculo**: Dados GPS (IMEI, longitude, latitude, altitude, speed, ignicao, dataDevice)  
- **Veiculo**: Controle de bloqueio (IMEI, ds_placa, ds_modelo, comandoBloqueo, bloqueado, ignicao)

Sistema simplificado para receber dados GPS e gerenciar comandos de bloqueio/desbloqueio.

### GPS Protocol Handler
- Analisa mensagens GPS recebidas (protocolos +RESP, +BUFF, +ACK)
- Suporte a vários tipos de comando (GTFRI, GTIGN, GTIGF, GTOUT, GTSRI, GTBSI)
- Gerencia comunicação bidirecional com dispositivos GPS
- Controla estados de conexão e timeouts dos dispositivos

### Command System
- Gerenciamento de comandos baseado em fila para dispositivos GPS
- Suporte a bloqueio/desbloqueio de veículos
- Capacidades de configuração de servidor e APN
- Rastreamento de status de comandos (pendente, enviado, confirmado, falhou)

### Device Manager
- Gerencia conexões ativas de dispositivos
- Controla timeouts e cleanup de conexões
- Atualiza status online/offline dos dispositivos
- Mantém histórico de última atividade

## Data Flow Long-Connection (Otimizado)

1. **Dispositivo GPS conecta** → Estabelece long-connection persistente via TCP
2. **Mantém conexão ativa** → Heartbeat automático a cada 5 min
3. **Múltiplas mensagens** → Recebe dados GPS na mesma conexão continuamente
4. **Salva dados GPS** → Insere na coleção `dados_veiculo` em tempo real
5. **Atualiza veículo** → Insere/atualiza na coleção `veiculo`
6. **Verifica comandos** → Campos `comandoBloqueo` e `comandoTrocarIP`
7. **Envia comandos** → AT+GTOUT (bloqueio) e AT+GTSRI (trocar IP) imediatamente
8. **Cleanup automático** → Remove conexões inativas após 30 min
9. **ACK imediato** → Confirma cada mensagem GPS recebida

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