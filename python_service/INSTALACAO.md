# Serviço GPS GV50 - Instalação e Atualização

Sistema TCP Python para comunicação com dispositivos GPS GV50 em modo Long-Connection.

## 📋 Pré-requisitos

- **Servidor Linux** (Ubuntu 18.04+ / CentOS 7+ recomendado)
- **Python 3.8+**
- **MongoDB 4.4+**
- **Git**
- **Acesso root/sudo**

---

## 🚀 Instalação Inicial

### 1. Preparar o Ambiente

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências do sistema
sudo apt install -y python3 python3-pip python3-venv git mongodb

# Iniciar MongoDB
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

### 2. Clonar e Configurar o Projeto

```bash
# Clonar repositório
cd /opt
sudo git clone <repository-url> gps-gv50
sudo chown -R $USER:$USER /opt/gps-gv50
cd /opt/gps-gv50/python_service

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências Python
pip install -r requirements.txt
```

### 3. Configurar Variáveis de Ambiente

```bash
# Criar arquivo de configuração
cat > .env << EOF
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=gps_tracking

# TCP Server Configuration  
TCP_PORT=8000
TCP_HOST=0.0.0.0

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/gps_service.log

# Server Configuration (opcional para troca de IP)
NEW_SERVER_IP=191.252.181.49
NEW_SERVER_PORT=8000
BACKUP_SERVER_IP=191.252.181.49
BACKUP_SERVER_PORT=8001
EOF

# Criar diretório de logs
mkdir -p logs
```

### 4. Configurar MongoDB

```bash
# Conectar ao MongoDB
mongo

# Criar banco de dados e índices
use gps_tracking

# Criar índices para performance
db.dados_veiculo.createIndex({IMEI: 1, data: -1})
db.dados_veiculo.createIndex({data: -1})
db.veiculo.createIndex({IMEI: 1})

# Sair do MongoDB
exit
```

### 5. Configurar como Serviço Systemd

```bash
# Criar arquivo de serviço
sudo cat > /etc/systemd/system/gps-gv50.service << EOF
[Unit]
Description=GPS GV50 TCP Service
After=network.target mongodb.service
Requires=mongodb.service

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=/opt/gps-gv50/python_service
Environment=PATH=/opt/gps-gv50/python_service/venv/bin
ExecStart=/opt/gps-gv50/python_service/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Recarregar systemd e iniciar serviço
sudo systemctl daemon-reload
sudo systemctl enable gps-gv50
sudo systemctl start gps-gv50
```

### 6. Verificar Instalação

```bash
# Verificar status do serviço
sudo systemctl status gps-gv50

# Verificar logs em tempo real
tail -f logs/gps_service.log

# Verificar se porta está escutando
sudo netstat -tlnp | grep :8000
```

---

## 🔄 Atualização do Sistema

### Atualização Simples (mesma versão)

```bash
# Parar serviço
sudo systemctl stop gps-gv50

# Navegar para diretório
cd /opt/gps-gv50

# Fazer backup da configuração
cp python_service/.env python_service/.env.backup

# Atualizar código
git pull origin main

# Ativar ambiente virtual
cd python_service
source venv/bin/activate

# Atualizar dependências (se necessário)
pip install -r requirements.txt

# Restaurar configuração se necessário
cp .env.backup .env

# Reiniciar serviço
sudo systemctl start gps-gv50
sudo systemctl status gps-gv50
```

### Atualização com Mudanças de Banco (versão maior)

```bash
# Parar serviço
sudo systemctl stop gps-gv50

# Fazer backup completo do banco
mongodump --db gps_tracking --out /backup/mongodb/$(date +%Y%m%d_%H%M%S)

# Atualizar código
cd /opt/gps-gv50
git pull origin main

# Verificar mudanças no banco
cd python_service
source venv/bin/activate

# Executar migrações se existirem
# python migrations.py (se aplicável)

# Reiniciar serviço
sudo systemctl start gps-gv50

# Verificar funcionamento
tail -f logs/gps_service.log
```

---

## 🔧 Comandos Úteis

### Gerenciamento do Serviço
```bash
# Iniciar
sudo systemctl start gps-gv50

# Parar  
sudo systemctl stop gps-gv50

# Reiniciar
sudo systemctl restart gps-gv50

# Ver status
sudo systemctl status gps-gv50

# Ver logs
sudo journalctl -u gps-gv50 -f
```

### Monitoramento
```bash
# Logs do sistema
tail -f logs/gps_service.log

# Conexões ativas
sudo netstat -an | grep :8000

# Processos Python
ps aux | grep python

# Uso de recursos
htop
```

### MongoDB
```bash
# Conectar ao banco
mongo gps_tracking

# Ver dispositivos conectados
db.veiculo.find().pretty()

# Ver últimos dados GPS
db.dados_veiculo.find().sort({data: -1}).limit(10).pretty()

# Contar registros
db.dados_veiculo.count()
```

---

## 🚗 Comandos de Controle

### Bloquear Veículo
```javascript
db.veiculo.updateOne(
  {IMEI: "555444333222111"}, 
  {$set: {comandoBloqueo: true}}
)
```

### Desbloquear Veículo
```javascript
db.veiculo.updateOne(
  {IMEI: "555444333222111"}, 
  {$set: {comandoBloqueo: false}}
)
```

### Trocar IP do Dispositivo
```javascript
db.veiculo.updateOne(
  {IMEI: "555444333222111"}, 
  {$set: {comandoTrocarIP: true}}
)
```

---

## 🔥 Firewall e Segurança

```bash
# Abrir porta 8000 para dispositivos GPS
sudo ufw allow 8000/tcp

# Restringir acesso MongoDB (apenas local)
sudo ufw deny 27017

# Ver status do firewall
sudo ufw status
```

---

## ❌ Solução de Problemas

### Serviço não inicia
```bash
# Verificar logs detalhados
sudo journalctl -u gps-gv50 --no-pager

# Verificar MongoDB
sudo systemctl status mongodb

# Testar manualmente
cd /opt/gps-gv50/python_service
source venv/bin/activate
python main.py
```

### Porta ocupada
```bash
# Encontrar processo usando porta 8000
sudo lsof -i :8000

# Matar processo se necessário
sudo kill -9 <PID>
```

### Problemas de conexão MongoDB
```bash
# Reiniciar MongoDB
sudo systemctl restart mongodb

# Verificar se está rodando
sudo systemctl status mongodb

# Testar conexão
mongo --eval "db.adminCommand('ismaster')"
```

---

## 📊 Estrutura do Projeto

```
/opt/gps-gv50/
├── python_service/
│   ├── main.py              # Entrada principal
│   ├── tcp_server.py        # Servidor TCP
│   ├── protocol_parser.py   # Parser GV50
│   ├── mongodb_client.py    # Cliente MongoDB
│   ├── models.py           # Modelos de dados
│   ├── config.py           # Configurações
│   ├── logger.py           # Sistema de logs

│   ├── requirements.txt    # Dependências
│   ├── .env               # Configuração
│   ├── logs/              # Logs do sistema
│   └── venv/              # Ambiente virtual
└── README.md
```

Sistema pronto para produção em servidor Linux!