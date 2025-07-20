# Serviço Python TCP para Dispositivos GPS GV50

## Overview

Este é um serviço Python TCP completo para comunicação com dispositivos GPS GV50. O serviço recebe dados de localização, processa mensagens do protocolo GV50, gerencia comandos bidirecionais e armazena informações no MongoDB. Foi desenvolvido baseado no protocolo oficial GV50 @Track Air Interface Protocol V4.01 e no exemplo C# fornecido.

## User Preferences

Preferred communication style: Simple, everyday language.
Projeto requer apenas serviço Python, sem interface web.

## System Architecture

Serviço Python standalone com arquitetura assíncrona:

### TCP Service Architecture
- **Language**: Python com asyncio para conexões concorrentes
- **Database**: MongoDB para armazenamento de dados GPS
- **Protocol**: Parser personalizado do protocolo GV50 GPS
- **Concurrency**: Servidor TCP assíncrono tratando múltiplas conexões de dispositivos
- **Commands**: Sistema de comandos para controle bidirecional dos dispositivos

## Key Components

### Database Schema
O sistema usa MongoDB para armazenamento de dados:
- **MongoDB** (via Motor): Dados de rastreamento GPS e comunicações de dispositivos

Principais entidades incluem:
- Veículos com rastreamento por IMEI
- Dados de rastreamento veicular (coordenadas GPS, velocidade, status de ignição)
- Comandos para controle de dispositivos (bloquear/desbloquear, configuração)
- Configurações e gerenciamento de status dos dispositivos

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

## Data Flow

1. **Ingestão de Dados GPS**: Dispositivos GPS conectam ao serviço Python TCP via sockets TCP
2. **Processamento de Protocolo**: Serviço Python analisa mensagens GPS recebidas e armazena dados no MongoDB
3. **Execução de Comandos**: Comandos enfileirados são enviados para dispositivos via conexão TCP
4. **Persistência de Dados**: Todos os dados de veículo e comando armazenados no MongoDB

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