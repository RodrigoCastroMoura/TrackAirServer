# Configuração do Dispositivo GV50 para Long-Connection

## Problema: Dispositivo não conecta no servidor

### Verificação Rápida no Servidor:

1. **Execute o diagnóstico:**
```bash
cd python_service
./diagnostico_conectividade.sh
```

2. **Se porta estiver bloqueada, libere:**
```bash
# Ubuntu/Debian:
sudo ufw allow 8000/tcp

# CentOS/RHEL:
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

## Configuração do Dispositivo GV50

### Comandos SMS para configurar o dispositivo:

**1. Configurar servidor (substitua pelo seu IP):**
```
AT+GTSRI=gv50,123456,0,191.252.181.49,8000,0,,,,,FFFF$
```

**2. Configurar APN (exemplo Vivo):**
```
AT+GTBSI=gv50,0,zap.vivo.com.br,vivo,vivo,,,,FFFF$
```

**3. Ativar modo Long-Connection:**
```
AT+GTSSL=gv50,0,1,0,,,,FFFF$
```

**4. Configurar intervalo de envio (30 segundos):**
```
AT+GTRTO=gv50,30,30,30,30,300,300,300,300,,,,FFFF$
```

**5. Reiniciar dispositivo:**
```
AT+GTRST=gv50,0,,,FFFF$
```

### Configurações por APN (Operadoras Brasileiras):

**Vivo:**
```
AT+GTBSI=gv50,0,zap.vivo.com.br,vivo,vivo,,,,FFFF$
```

**Claro:**
```
AT+GTBSI=gv50,0,claro.com.br,claro,claro,,,,FFFF$
```

**TIM:**
```
AT+GTBSI=gv50,0,timbrasil.br,tim,tim,,,,FFFF$
```

**Oi:**
```
AT+GTBSI=gv50,0,gprs.oi.com.br,oi,oi,,,,FFFF$
```

## Verificação se Dispositivo Conectou:

### 1. Verificar logs do servidor:
```bash
tail -f python_service/logs/gps_service.log
```

### 2. Verificar conexões ativas:
```bash
netstat -an | grep :8000
```

### 3. Se aparecer uma linha como esta, está conectado:
```
tcp    0    0 0.0.0.0:8000    IP_DISPOSITIVO:PORTA    ESTABLISHED
```

## Solução de Problemas Comuns:

**1. Dispositivo não conecta:**
- Verificar se porta 8000 está liberada no firewall
- Verificar se APN está correta para a operadora
- Verificar se dispositivo tem sinal de dados (2G/3G/4G)

**2. Conecta mas não envia dados:**
- Verificar configuração de intervalo de envio
- Verificar se antena GPS tem sinal

**3. Perde conexão constantemente:**
- Verificar qualidade do sinal da operadora
- Ajustar timeout do servidor se necessário

## Comandos de Teste via SMS:

**Verificar configuração atual:**
```
AT+GTSRI=gv50,,,,,,,,FFFF$
```

**Verificar status GPS:**
```
AT+GTFRI=gv50,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,,FFFF$
```

**Verificar dados da operadora:**
```
AT+GTBSI=gv50,,,,,,,,,FFFF$
```

## Exemplo de Configuração Completa via SMS:

```
# Substitua 191.252.181.49 pelo IP real do seu servidor

# 1. Configurar servidor
AT+GTSRI=gv50,123456,0,191.252.181.49,8000,0,,,,,FFFF$

# 2. Configurar APN (exemplo Vivo)
AT+GTBSI=gv50,0,zap.vivo.com.br,vivo,vivo,,,,FFFF$

# 3. Ativar long-connection
AT+GTSSL=gv50,0,1,0,,,,FFFF$

# 4. Intervalo 30s
AT+GTRTO=gv50,30,30,30,30,300,300,300,300,,,,FFFF$

# 5. Reiniciar
AT+GTRST=gv50,0,,,FFFF$
```

Aguarde cerca de 2 minutos após o reinício e verifique se o dispositivo conectou no servidor usando o comando de diagnóstico.