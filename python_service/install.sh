#!/bin/bash
# 🚀 Script de Instalação Automática - Serviço GPS GV50

set -e  # Parar se houver erro

echo "🚀 Instalando Serviço GPS GV50..."

# Verificar se é root
if [ "$EUID" -ne 0 ]; then
  echo "❌ Execute como root: sudo bash install.sh"
  exit 1
fi

# Atualizar sistema
echo "📦 Atualizando sistema..."
apt update && apt upgrade -y

# Instalar Python
echo "🐍 Instalando Python..."
apt install python3 python3-pip python3-venv -y

# Criar diretório do serviço
echo "📁 Criando diretório..."
mkdir -p /opt/gps_service
cp -r * /opt/gps_service/
cd /opt/gps_service

# Criar ambiente virtual
echo "🔧 Configurando ambiente Python..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
echo "📦 Instalando dependências..."
pip install motor pydantic pydantic-settings python-dotenv

# Criar diretório de logs
mkdir -p logs

# Configurar permissões
chown -R root:root /opt/gps_service
chmod +x main.py

# Criar serviço systemd
echo "⚙️ Configurando serviço..."
cat > /etc/systemd/system/gps-service.service << 'EOF'
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
EOF

# Ativar serviço
systemctl daemon-reload
systemctl enable gps-service

echo ""
echo "✅ Instalação concluída!"
echo ""
echo "📋 Próximos passos:"
echo "1. Editar /opt/gps_service/.env com sua string MongoDB"
echo "2. Testar: cd /opt/gps_service && source venv/bin/activate && python test_connection.py"
echo "3. Iniciar: sudo systemctl start gps-service"
echo "4. Ver logs: sudo journalctl -u gps-service -f"
echo ""
echo "🌐 Porta TCP 8000 será usada para dispositivos GPS"
echo "📊 Dados salvos no MongoDB Atlas automaticamente"
echo ""