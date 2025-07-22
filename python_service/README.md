# Serviço GPS GV50

Sistema Python TCP para comunicação com dispositivos GPS GV50 em modo Long-Connection.

## 🎯 Características

- **TCP Long-Connection** com dispositivos GPS GV50
- **Protocolo GV50 oficial** conforme documentação V4.01
- **MongoDB** para armazenamento de dados
- **Detecção de ignição** em tempo real (GTIGN/GTIGF)
- **Comandos bidirecionais** (bloqueio/desbloqueio/troca IP)
- **Múltiplas conexões** simultâneas
- **Sistema de logs** completo
- **Heartbeat automático** para manter conexões vivas

## 📊 Dados Processados

### Coleção `dados_veiculo` (dados do dispositivo):
- IMEI, longitude, latitude, altitude
- Velocidade, status de ignição
- Timestamps do dispositivo e recebimento

### Coleção `veiculo` (controle de comandos):
- Comandos de bloqueio/desbloqueio
- Comandos de troca de IP
- Status atual dos dispositivos

## 🚀 Instalação Rápida

```bash
# Ver documentação completa
cat INSTALACAO.md

# Instalação básica
git clone <repo-url> && cd python_service
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # configurar variáveis
python main.py
```

## 🔧 Configuração

Arquivo `.env`:
```bash
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=gps_tracking
TCP_PORT=8000
TCP_HOST=0.0.0.0
NEW_SERVER_IP=191.252.181.49
```

## 📡 Protocolo GV50

Mensagens suportadas:
- **GTFRI**: dados GPS regulares
- **GTIGN**: evento ignição ligada  
- **GTIGF**: evento ignição desligada
- **GTOUT**: comandos de bloqueio
- **GTSRI**: comandos de troca de IP

## 🚗 Comandos de Controle

```javascript
// Bloquear veículo
db.veiculo.updateOne({IMEI: "123456789"}, {$set: {comandoBloqueo: true}})

// Desbloquear veículo  
db.veiculo.updateOne({IMEI: "123456789"}, {$set: {comandoBloqueo: false}})

// Trocar IP
db.veiculo.updateOne({IMEI: "123456789"}, {$set: {comandoTrocarIP: true}})
```

## 📚 Documentação

- **`INSTALACAO.md`** - Guia completo de instalação e atualização
- **Logs** - `logs/gps_service.log`
- **Configuração** - arquivo `.env`

Sistema pronto para produção no servidor 191.252.181.49!