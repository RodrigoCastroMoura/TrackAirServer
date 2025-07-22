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

### Coleção `dados_veiculo` (todos os protocolos GPS):
- IMEI, longitude, latitude, altitude, velocidade
- Status de ignição, timestamps do dispositivo
- Tipo de protocolo (GTFRI, GTIGN, GTIGF, GTIGL, GTOUT, GTSRI, GTBSI)
- Mensagem original completa (raw_message)
- Dados específicos: bateria, eventos, comandos, info celular

### Coleção `veiculo` (controle de comandos):
- Comandos de bloqueio/desbloqueio
- Comandos de troca de IP
- Status atual dos dispositivos
- Monitoramento de bateria (voltagem, alertas, timestamps)

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
- **GTIGL**: alerta de bateria baixa (voltagem crítica)
- **GTOUT**: comandos de bloqueio
- **GTSRI**: comandos de troca de IP

## 🚗 Comandos de Controle (via MongoDB)

```javascript
// Bloquear veículo
db.veiculo.updateOne({IMEI: "123456789"}, {$set: {comandoBloqueo: true}})

// Desbloquear veículo  
db.veiculo.updateOne({IMEI: "123456789"}, {$set: {comandoBloqueo: false}})

// Trocar IP
db.veiculo.updateOne({IMEI: "123456789"}, {$set: {comandoTrocarIP: true}})
```

Sistema executa comandos automaticamente quando dispositivo envia próxima mensagem GPS.

## 🔋 Monitoramento de Bateria

Sistema monitora automaticamente bateria através do protocolo GTIGL:

**Níveis de alerta:**
- 🚨 **CRÍTICA**: ≤ 10.5V (dispositivo vai desligar)
- ⚠️ **BAIXA**: ≤ 11.0V (atenção urgente)
- 🔋 **AVISO**: ≤ 11.5V (nível baixo)
- ✅ **NORMAL**: > 12.0V (funcionamento normal)

**Consultar bateria:**
```javascript
// Ver status de bateria
db.veiculo.find({bateria_baixa: true}).pretty()

// Histórico de alertas
db.veiculo.find({ultimo_alerta_bateria: {$exists: true}}).sort({ultimo_alerta_bateria: -1})

// Ver todos protocolos por IMEI
db.dados_veiculo.find({IMEI: "123456789"}).sort({data: -1})

// Ver apenas alertas de bateria baixa
db.dados_veiculo.find({protocol_type: "GTIGL"}).sort({data: -1})

// Ver eventos de ignição
db.dados_veiculo.find({$or: [{protocol_type: "GTIGN"}, {protocol_type: "GTIGF"}]}).sort({data: -1})

// Ver comandos executados
db.dados_veiculo.find({comando_executado: {$exists: true}}).sort({data: -1})

// Contar registros por tipo
db.dados_veiculo.aggregate([{$group: {_id: "$protocol_type", count: {$sum: 1}}}])
```

Sistema executa comandos automaticamente quando dispositivo envia próxima mensagem GPS.

## 📚 Documentação

- **`INSTALACAO.md`** - Guia completo de instalação e atualização
- **Logs** - `logs/gps_service.log`
- **Configuração** - arquivo `.env`

Sistema pronto para produção no servidor 191.252.181.49!