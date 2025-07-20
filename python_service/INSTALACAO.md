# 🚀 Instalação e Teste do Serviço GPS GV50

## 📋 Requisitos do Servidor

- **Linux** (Ubuntu/CentOS/Debian)
- **Python 3.11+** instalado
- **Conexão à internet** para MongoDB Atlas
- **Porta TCP 8000** disponível para dispositivos GPS

## 🔧 Passo 1: Preparar o Servidor

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python e pip
sudo apt install python3 python3-pip python3-venv -y

# Verificar versão
python3 --version
```

## 📦 Passo 2: Instalar o Serviço

```bash
# Criar diretório para o serviço
mkdir /opt/gps_service
cd /opt/gps_service

# Copiar todos os arquivos do python_service para aqui
# (você pode usar scp, rsync ou git)

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install motor pydantic pydantic-settings python-dotenv

# Criar diretório de logs
mkdir logs
```

## ⚙️ Passo 3: Configurar Variáveis

Edite o arquivo `.env`:
```bash
nano .env
```

Verifique se tem:
```env
# MongoDB Atlas - SUA STRING DE CONEXÃO
MONGODB_URL=mongodb+srv://docsmartuser:hk9D7DSnyFlcPmKL@cluster0.qats6.mongodb.net/

# Configurações TCP
TCP_HOST=0.0.0.0
TCP_PORT=8000

# IPs para comandos de troca (configure conforme sua rede)
NEW_SERVER_IP=192.168.1.100
NEW_SERVER_PORT=8000
BACKUP_SERVER_IP=192.168.1.101
BACKUP_SERVER_PORT=8000
```

## 🧪 Passo 4: Testar Conexão

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Testar MongoDB
python test_connection.py
```

**Saída esperada:**
```
✓ Conectado ao MongoDB
✓ Dados GPS inseridos
✓ Veículo criado/atualizado
✅ TODOS OS TESTES PASSARAM!
```

## 🚀 Passo 5: Executar o Serviço

### Execução manual (para teste):
```bash
# Ativar ambiente virtual
source venv/bin/activate

# Executar serviço
python main.py
```

**Saída esperada:**
```
2025-07-20 17:00:00 - main - INFO - Iniciando servidor TCP GPS na porta 8000
2025-07-20 17:00:00 - main - INFO - Servidor pronto para receber dispositivos GPS
```

### Execução como serviço (produção):
```bash
# Criar arquivo de serviço systemd
sudo nano /etc/systemd/system/gps-service.service
```

Conteúdo do arquivo:
```ini
[Unit]
Description=GPS GV50 Tracking Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/gps_service
Environment=PATH=/opt/gps_service/venv/bin
ExecStart=/opt/gps_service/venv/bin/python main.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Ativar o serviço:
```bash
# Recarregar systemd
sudo systemctl daemon-reload

# Ativar serviço
sudo systemctl enable gps-service

# Iniciar serviço
sudo systemctl start gps-service

# Verificar status
sudo systemctl status gps-service
```

## 🔍 Passo 6: Testar com Dispositivo Simulado

```bash
# Em outro terminal, simular dispositivo GPS
telnet localhost 8000

# Enviar mensagem de teste:
+RESP:GTFRI,060228,123456789012345,,0,0,1,1,4.3,92,70.0,-46.633308,-23.550520,20241221163000,0460,0000,18d8,6141,00,2000.0,20241221163000,11F0$
```

**No log do serviço deve aparecer:**
```
INFO - Nova conexão de dispositivo: 127.0.0.1:xxxxx
INFO - Dados inseridos para IMEI 123456789012345
INFO - Enviando ACK para dispositivo
```

## 📊 Passo 7: Verificar Dados no MongoDB

```bash
# Testar busca de dados
python -c "
import asyncio
from mongodb_client import mongodb_client

async def test():
    await mongodb_client.connect()
    dados = await mongodb_client.buscar_dados_veiculo('123456789012345', limit=1)
    print('Dados encontrados:', dados)
    await mongodb_client.disconnect()

asyncio.run(test())
"
```

## 🎮 Passo 8: Testar Comandos

```bash
# Testar comando de bloqueio
python -c "
import asyncio
from command_api import CommandAPI

async def test():
    # Bloquear dispositivo
    await CommandAPI.bloquear_veiculo('123456789012345')
    print('Comando de bloqueio definido')
    
    # Ver status
    status = await CommandAPI.status_veiculo('123456789012345')
    print('Status:', status)

asyncio.run(test())
"
```

## 🔧 Passo 9: Firewall (se necessário)

```bash
# Permitir porta TCP 8000
sudo ufw allow 8000/tcp

# Verificar regras
sudo ufw status
```

## 📝 Logs e Monitoramento

```bash
# Ver logs do serviço
sudo journalctl -u gps-service -f

# Ver logs do arquivo
tail -f /opt/gps_service/logs/gps_service.log

# Verificar se porta está aberta
netstat -tlnp | grep :8000
```

## 🆘 Solução de Problemas

### Erro de conexão MongoDB:
- Verificar string de conexão no `.env`
- Testar: `python test_connection.py`

### Porta 8000 ocupada:
```bash
# Ver quem está usando
sudo lsof -i :8000

# Matar processo se necessário
sudo kill -9 PID
```

### Permissões:
```bash
# Dar permissões corretas
sudo chown -R $USER:$USER /opt/gps_service
chmod +x main.py
```

### Reiniciar serviço:
```bash
sudo systemctl restart gps-service
sudo systemctl status gps-service
```

## ✅ Verificação Final

1. **MongoDB conectado** ✓
2. **Servidor TCP rodando** na porta 8000 ✓  
3. **Dispositivo simulado** se conecta ✓
4. **Dados salvos** no MongoDB ✓
5. **Comandos funcionando** ✓

🎯 **Seu serviço GPS está pronto para receber dispositivos GV50!**