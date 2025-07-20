# Serviço GPS GV50 - Clean Code

Serviço Python TCP simplificado para dispositivos GPS GV50.

## Estrutura Clean Code

### Apenas 2 Tabelas MongoDB:

**DadosVeiculo**: Armazena dados GPS recebidos
- IMEI, longitude, latitude, altitude, speed, ignicao, dataDevice

**Veiculo**: Controla bloqueio/desbloqueio e configuração IP (campos essenciais)
- IMEI, ds_placa, ds_modelo, comandoBloqueo, bloqueado, comandoTrocarIP, ignicao

## Como Usar

### 1. Instalar dependências:
```bash
pip install -r requirements.txt
```

### 2. Configurar MongoDB e IPs (.env):
```bash
MONGODB_URL=mongodb+srv://...
MONGODB_DATABASE=gps_tracking_service
TCP_HOST=0.0.0.0
TCP_PORT=8000

# Configuração de IPs para dispositivos
NEW_SERVER_IP=192.168.1.100
NEW_SERVER_PORT=8000
BACKUP_SERVER_IP=192.168.1.101
BACKUP_SERVER_PORT=8000
```

### 3. Testar conexão:
```bash
python test_connection.py
```

### 4. Executar serviço:
```bash
python main.py
```

## Funcionalidades

- ✅ Recebe dados GPS via TCP
- ✅ Salva no MongoDB (2 tabelas)
- ✅ Verifica comandos de bloqueio/desbloqueio
- ✅ Configura novos IPs dos dispositivos
- ✅ Envia comandos AT via protocolo GV50
- ✅ API para controle externo

## API de Comandos

```python
from command_api import CommandAPI

# Bloquear veículo
await CommandAPI.bloquear_veiculo("IMEI")

# Desbloquear veículo  
await CommandAPI.desbloquear_veiculo("IMEI")

# Trocar IP do dispositivo
await CommandAPI.trocar_ip_dispositivo("IMEI")

# Ver status
status = await CommandAPI.status_veiculo("IMEI")
```

## Fluxo Simplificado

1. Dispositivo GPS → Conecta TCP → Envia dados
2. Servidor → Salva `DadosVeiculo` → Atualiza `Veiculo`  
3. Verifica `comandoBloqueo` e `comandoTrocarIP` → Envia comandos se pendentes
4. Limpa comandos → Atualiza status após envio