# Configuração de Firewall para Serviço GPS GV50

## Problema Comum: Dispositivos GPS não conseguem conectar

Quando os dispositivos GPS GV50 não conseguem conectar ao servidor, geralmente é devido ao firewall bloqueando a porta TCP.

## Solução: Liberar Porta no Firewall

### 1. Verificar porta atual do serviço
```bash
cd python_service
grep "tcp_port" .env
# Porta padrão: 8000
```

### 2. Para Ubuntu/Debian (UFW):
```bash
# Verificar status do firewall
sudo ufw status

# Liberar porta 8000 para TCP
sudo ufw allow 8000/tcp

# Verificar se regra foi adicionada
sudo ufw status numbered
```

### 3. Para CentOS/RHEL/Rocky Linux (firewalld):
```bash
# Verificar status do firewall
sudo firewall-cmd --state

# Liberar porta 8000 permanentemente
sudo firewall-cmd --permanent --add-port=8000/tcp

# Recarregar configuração
sudo firewall-cmd --reload

# Verificar se porta foi liberada
sudo firewall-cmd --list-ports
```

### 4. Para sistemas com iptables:
```bash
# Liberar porta 8000 para TCP
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT

# Salvar regras (Ubuntu/Debian)
sudo iptables-save > /etc/iptables/rules.v4

# Salvar regras (CentOS/RHEL)
sudo service iptables save
```

## Verificação de Conectividade

### 1. Testar se porta está aberta localmente:
```bash
# Iniciar o serviço GPS
cd python_service
python main.py &

# Testar conexão local
telnet 127.0.0.1 8000
# Ou com nc
nc -zv 127.0.0.1 8000
```

### 2. Testar conexão externa:
```bash
# De outro servidor, testar:
telnet SEU_IP_SERVIDOR 8000
nc -zv SEU_IP_SERVIDOR 8000
```

## Configuração do Dispositivo GV50

Certifique-se que o dispositivo está configurado com:
- **Protocolo**: TCP 
- **Modo**: Long-Connection
- **IP do Servidor**: 191.252.181.49
- **Porta**: 8000
- **APN**: Conforme operadora

## Logs para Diagnóstico

```bash
# Ver logs do serviço em tempo real
tail -f python_service/logs/gps_service.log

# Ver conexões ativas na porta
netstat -tulpn | grep :8000
ss -tulpn | grep :8000
```

## Comando Completo para Liberação (Ubuntu):
```bash
# Script completo de liberação
sudo ufw allow 8000/tcp
sudo ufw reload
sudo ufw status
echo "Porta 8000/TCP liberada para dispositivos GPS GV50"
```

## Troubleshooting Adicional

Se ainda não conectar, verificar:

1. **Serviço rodando**: `ps aux | grep python`
2. **Porta escutando**: `netstat -tulpn | grep :8000`  
3. **Logs de conexão**: Verificar arquivos de log
4. **Operadora**: APN e configurações de dados do dispositivo
5. **IP público**: Confirmar se 191.252.181.49 está correto

## Teste de Conectividade Rápido

```bash
# Script de teste rápido
#!/bin/bash
echo "=== TESTE CONECTIVIDADE GPS GV50 ==="
echo "1. Verificando se serviço está rodando..."
ps aux | grep python | grep main.py

echo "2. Verificando porta 8000..."
netstat -tulpn | grep :8000

echo "3. Testando conexão local..."
timeout 5 telnet 127.0.0.1 8000

echo "4. Verificando firewall..."
sudo ufw status | grep 8000
```