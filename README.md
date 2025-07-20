# Serviço Python TCP para Dispositivos GPS GV50

Serviço completo em Python para receber dados de dispositivos GPS GV50 e gerenciar comunicação bidirecional.

## Funcionalidades

- **Servidor TCP Assíncrono**: Suporta múltiplas conexões simultâneas de dispositivos
- **Parser de Protocolo**: Suporte completo ao protocolo GV50 (+RESP, +BUFF, +ACK)
- **Gerenciamento de Comandos**: Envio de comandos para dispositivos (bloquear/desbloquear, configuração)
- **Configuração de Rede**: Configuração remota de IP/porta e APN dos dispositivos
- **Integração MongoDB**: Armazenamento persistente de dados
- **Gerenciamento de Dispositivos**: Rastreamento de conexões e status
- **Logs Completos**: Sistema de logs detalhado para monitoramento

## Mensagens Suportadas

### Mensagens de Entrada
- **GTFRI**: Informações de localização GPS
- **GTIGN/GTIGF**: Eventos de ignição ligada/desligada
- **GTOUT**: Confirmações de controle de saída

### Comandos de Saída
- **GTOUT**: Bloquear/desbloquear dispositivo
- **GTSRI**: Configuração do servidor (IP/porta)
- **GTBSI**: Configuração APN

## Instalação e Uso

### 1. Instalar dependências:
```bash
cd python_service
pip install -r requirements.txt
```

### 2. Configurar banco de dados:
- Instalar MongoDB no servidor
- Ajustar configurações no arquivo `.env`

### 3. Executar o serviço:
```bash
python main.py
```

O serviço irá:
- Escutar na porta configurada (padrão: 8000)
- Processar dados GPS dos dispositivos GV50
- Armazenar dados no MongoDB
- Executar comandos pendentes automaticamente
- Manter logs detalhados de todas as operações

## Configuração

Edite o arquivo `python_service/.env` para ajustar:
- URL do MongoDB
- Host e porta do servidor TCP
- Níveis de log
- Timeouts e limites de conexão

## Logs

Os logs são salvos em `logs/gps_service.log` e incluem:
- Conexões de dispositivos
- Mensagens recebidas e processadas
- Comandos enviados
- Erros e exceções
- Status de dispositivos

## Estrutura dos Dados

### Dados de Veículo (MongoDB)
- IMEI do dispositivo
- Coordenadas GPS (latitude, longitude, altitude)
- Velocidade e status de ignição
- Timestamps de dispositivo e servidor

### Comandos
- Tipo de comando (GTOUT, GTSRI, GTBSI)
- Parâmetros do comando
- Status (pendente, enviado, confirmado, falhou)
- Histórico de tentativas

### Configurações de Dispositivo
- Configurações de servidor (IP, porta)
- Configurações APN
- Intervalos de relatório
- Data de última aplicação