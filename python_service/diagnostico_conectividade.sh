#!/bin/bash

echo "=========================================="
echo "🔍 DIAGNÓSTICO DE CONECTIVIDADE GPS GV50"
echo "=========================================="

# Verificar se está rodando como root para comandos de firewall
if [[ $EUID -eq 0 ]]; then
   SUDO=""
else
   SUDO="sudo"
fi

echo ""
echo "1️⃣ Verificando serviço Python..."
SERVICE_RUNNING=$(ps aux | grep "python.*main.py" | grep -v grep)
if [ -n "$SERVICE_RUNNING" ]; then
    echo "✅ Serviço GPS está rodando:"
    echo "$SERVICE_RUNNING"
else
    echo "❌ Serviço GPS NÃO está rodando"
    echo "   Execute: python main.py"
fi

echo ""
echo "2️⃣ Verificando porta 8000..."
PORT_LISTENING=$(netstat -tulpn 2>/dev/null | grep ":8000" | head -1)
if [ -n "$PORT_LISTENING" ]; then
    echo "✅ Porta 8000 está escutando:"
    echo "$PORT_LISTENING"
else
    echo "❌ Porta 8000 NÃO está escutando"
    echo "   Verifique se o serviço está iniciado"
fi

echo ""
echo "3️⃣ Testando conectividade local..."
TELNET_TEST=$(timeout 3 bash -c "</dev/tcp/127.0.0.1/8000" 2>/dev/null && echo "OK" || echo "FAIL")
if [ "$TELNET_TEST" = "OK" ]; then
    echo "✅ Conexão local na porta 8000 funciona"
else
    echo "❌ Conexão local na porta 8000 falhou"
fi

echo ""
echo "4️⃣ Verificando firewall..."

# Ubuntu/Debian UFW
if command -v ufw >/dev/null 2>&1; then
    echo "Sistema: Ubuntu/Debian (UFW)"
    UFW_STATUS=$($SUDO ufw status | grep -i inactive)
    if [ -n "$UFW_STATUS" ]; then
        echo "✅ UFW está desabilitado (sem bloqueio)"
    else
        UFW_8000=$($SUDO ufw status | grep "8000")
        if [ -n "$UFW_8000" ]; then
            echo "✅ Porta 8000 liberada no UFW:"
            echo "$UFW_8000"
        else
            echo "❌ Porta 8000 NÃO está liberada no UFW"
            echo "   Execute: sudo ufw allow 8000/tcp"
        fi
    fi

# CentOS/RHEL firewalld
elif command -v firewall-cmd >/dev/null 2>&1; then
    echo "Sistema: CentOS/RHEL (firewalld)"
    FIREWALLD_RUNNING=$($SUDO firewall-cmd --state 2>/dev/null)
    if [ "$FIREWALLD_RUNNING" = "running" ]; then
        FIREWALLD_8000=$($SUDO firewall-cmd --list-ports | grep "8000")
        if [ -n "$FIREWALLD_8000" ]; then
            echo "✅ Porta 8000 liberada no firewalld"
        else
            echo "❌ Porta 8000 NÃO está liberada no firewalld"
            echo "   Execute: sudo firewall-cmd --permanent --add-port=8000/tcp"
            echo "           sudo firewall-cmd --reload"
        fi
    else
        echo "✅ Firewalld não está rodando"
    fi

# iptables
elif command -v iptables >/dev/null 2>&1; then
    echo "Sistema: iptables"
    IPTABLES_8000=$($SUDO iptables -L | grep "8000")
    if [ -n "$IPTABLES_8000" ]; then
        echo "✅ Regra para porta 8000 encontrada no iptables"
    else
        echo "⚠️ Nenhuma regra específica para porta 8000 no iptables"
        echo "   Execute: sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT"
    fi
else
    echo "ℹ️ Sistema de firewall não identificado"
fi

echo ""
echo "5️⃣ Verificando IP público..."
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "N/A")
echo "IP público do servidor: $PUBLIC_IP"

echo ""
echo "6️⃣ Verificando logs recentes..."
if [ -f "logs/gps_service.log" ]; then
    echo "📋 Últimas 5 linhas do log:"
    tail -5 logs/gps_service.log
else
    echo "⚠️ Arquivo de log não encontrado"
fi

echo ""
echo "=========================================="
echo "🎯 RESUMO E SOLUÇÕES:"
echo "=========================================="

# Análise final e recomendações
if [ -z "$SERVICE_RUNNING" ]; then
    echo "❗ PROBLEMA: Serviço não está rodando"
    echo "   SOLUÇÃO: cd python_service && python main.py"
fi

if [ -z "$PORT_LISTENING" ]; then
    echo "❗ PROBLEMA: Porta 8000 não está escutando"
    echo "   SOLUÇÃO: Iniciar o serviço GPS"
fi

if [ "$TELNET_TEST" = "FAIL" ]; then
    echo "❗ PROBLEMA: Conectividade local falhou"
    echo "   SOLUÇÃO: Verificar serviço e configurações"
fi

# UFW específico
if command -v ufw >/dev/null 2>&1; then
    UFW_STATUS=$($SUDO ufw status | grep -i inactive)
    if [ -z "$UFW_STATUS" ]; then
        UFW_8000=$($SUDO ufw status | grep "8000")
        if [ -z "$UFW_8000" ]; then
            echo "❗ PROBLEMA: Porta 8000 bloqueada no UFW"
            echo "   SOLUÇÃO: sudo ufw allow 8000/tcp"
        fi
    fi
fi

# firewalld específico  
if command -v firewall-cmd >/dev/null 2>&1; then
    FIREWALLD_RUNNING=$($SUDO firewall-cmd --state 2>/dev/null)
    if [ "$FIREWALLD_RUNNING" = "running" ]; then
        FIREWALLD_8000=$($SUDO firewall-cmd --list-ports | grep "8000")
        if [ -z "$FIREWALLD_8000" ]; then
            echo "❗ PROBLEMA: Porta 8000 bloqueada no firewalld"
            echo "   SOLUÇÃO: sudo firewall-cmd --permanent --add-port=8000/tcp"
            echo "           sudo firewall-cmd --reload"
        fi
    fi
fi

echo ""
echo "🔧 COMANDOS RÁPIDOS PARA CORREÇÃO:"
echo "=========================================="

if command -v ufw >/dev/null 2>&1; then
    echo "# Para Ubuntu/Debian:"
    echo "sudo ufw allow 8000/tcp"
    echo "sudo ufw reload"
elif command -v firewall-cmd >/dev/null 2>&1; then
    echo "# Para CentOS/RHEL:"
    echo "sudo firewall-cmd --permanent --add-port=8000/tcp"
    echo "sudo firewall-cmd --reload"
else
    echo "# Para iptables:"
    echo "sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT"
fi

echo ""
echo "📝 Para testar após correção:"
echo "telnet $PUBLIC_IP 8000"
echo ""