# 🔐 Sistema PAM - Autenticação com Certificados SSH Expiráveis

## 📋 Descrição do Projeto
Sistema de autenticação PAM (Privileged Access Management) que utiliza certificados SSH de curta duração (10 minutos) com autenticação multi-fator (MFA) para acesso seguro a servidores.

## 🏗️ Arquitetura do Sistema

```
👤 USUÁRIO
    │
    ↓ (Script cliente)
🔑 SIGNER APP (Porta 5000)
    │  ✅ Valida MFA
    ↓
🏦 VAULT CA (Porta 8080)
    │  ✅ Assina certificados
    ↓  
🖥️ SSH SERVER (Porta 2223)
    │  ✅ Aceita certificados
    ↓
🔓 ACESSO CONCEDIDO
```

## 📁 Estrutura do Projeto

```
arquitetura-pam/
├── 📦 docker-compose.yml
├── 🔑 signer-app/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
├── 🏦 vault-ca/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── vault-server.py
├── 🖥️ ssh-server/
│   ├── Dockerfile
│   └── wait-and-run.sh
├── 👤 client/
│   └── get-certificate.sh
└── 📚 README.md
```

## 🚀 Guia Rápido de Execução

### Pré-requisitos
- Docker e Docker Compose instalados
- Python 3.x (para o script cliente)
- Git (para clonar o repositório)

### ⚡ Execução Rápida (5 minutos)

1. **Clone e entre no projeto:**
```bash
git clone [url-desse-repositório]
cd Arquitetura-PAM
```

2. **Suba os containers:**
```bash
docker compose up -d
```

3. **Aguarde os serviços iniciarem (30 segundos):**
```bash
docker compose logs -f
```

4. **Execute o cliente:**
```bash
cd client
chmod +x get-certificate.sh
./get-certificate.sh
```

5. **🎉 Pronto! Você deve ver:**
```
🎉 CONEXÃO SSH BEM-SUCEDIDA! Sistema PAM funcionando!
testuser
```

## 🛠️ Configuração Detalhada

### 1. Verificar Instalação do Docker
```bash
docker --version
docker compose version
```

### 2. Build dos Containers
```bash
# Build completo
docker compose build

# Ou build individual
docker compose build vault-ca
docker compose build signer-app  
docker compose build ssh-server
```

### 3. Iniciar Sistema
```bash
# Iniciar em background
docker compose up -d

# Verificar status
docker compose ps

# Ver logs em tempo real
docker compose logs -f
```

### 4. Testar Serviços
```bash
# Testar Signer App
curl http://localhost:5000/health

# Testar Vault CA
curl http://localhost:8080/health

# Ver configuração MFA
curl http://localhost:5000/mfa-setup
```

## 🔑 Como Funciona o Fluxo

### Passo a Passo do Cliente:
1. **Gera par de chaves SSH** (`/tmp/pam_key`)
2. **Obtém código MFA** automático (TOTP)
3. **Solicita certificado** ao Signer App
4. **Signer valida MFA** e envia para Vault CA
5. **Vault assina certificado** com 10min de validade
6. **Conecta via SSH** usando certificado

### Teste Manual:
```bash
# Gerar chaves manualmente
ssh-keygen -t rsa -b 4096 -f /tmp/minha_chave -N ""

# Obter MFA (código muda a cada 30s)
python3 -c "import pyotp; totp = pyotp.TOTP('JBSWY3DPEHPK3PXP'); print(totp.now())"

# Testar conexão SSH
ssh -i /tmp/pam_key \
    -o CertificateFile=/tmp/pam_key-cert.pub \
    -p 2223 \
    testuser@localhost
```

## 🐛 Solução de Problemas Comuns

### Erro: "Port already in use"
```bash
# Verificar portas em uso
sudo netstat -tulpn | grep :5000
sudo netstat -tulpn | grep :8080  
sudo netstat -tulpn | grep :2223

# Parar serviços conflitantes ou alterar ports no docker-compose.yml
```

### Erro: "Certificate not generated"
```bash
# Verificar logs do Vault
docker compose logs vault-ca

# Rebuildar se necessário
docker compose restart vault-ca
```

### Erro: "MFA invalid"
```bash
# Verificar tempo do sistema
date

# Usar código MFA manual (consultar logs do Signer)
# Secret: JBSWY3DPEHPK3PXP
```

### Erro: Python/pyotp não encontrado
```bash
# Instalar dependências no host
pip3 install pyotp

# Ou usar código manual (script pedirá)
```

### Limpar tudo e recomeçar:
```bash
docker compose down -v
docker system prune -f
```

## 📊 Comandos Úteis para Demonstração

```bash
# 1. Mostrar containers rodando
docker compose ps

# 2. Mostrar fluxo completo
./client/get-certificate.sh

# 3. Ver detalhes do certificado
ssh-keygen -L -f /tmp/pam_key-cert.pub

# 4. Monitorar logs em tempo real
docker compose logs -f

# 5. Testar saúde dos serviços
curl -s http://localhost:5000/health | jq
curl -s http://localhost:8080/health | jq
```

## 🔒 Configurações de Segurança

- ✅ **MFA obrigatório** para obter certificados
- ✅ **Certificados de 10 minutos** - janela temporal curta
- ✅ **Autenticação apenas por certificados** - sem senhas
- ✅ **CA dedicada** - isolada em container
- ✅ **Network segregada** - comunicação interna entre containers

## 📝 Para o Relatório

### Pontos a documentar:
1. ✅ Estrutura do projeto e arquitetura
2. ✅ Containers buildados e rodando
3. ✅ Serviços respondendo (`/health`)
4. ✅ Fluxo completo funcionando
5. ✅ Conexão SSH bem-sucedida
6. ✅ Validade do certificado (verificar com `ssh-keygen -L`)

### Evidências para capturar:
- Print do terminal com mensagem de sucesso
- Output do comando `docker compose ps`
- Resposta dos endpoints de health
- Detalhes do certificado gerado

## 🆘 Suporte

Se encontrar problemas:

1. **Verifique os logs:**
```bash
docker compose logs
docker compose logs [servico]
```

2. **Confirme as portas:**
```bash
ss -tulpn | grep -E ':(5000|8080|2223)'
```

3. **Reinicie o sistema:**
```bash
docker compose restart
```

4. **Recomece do zero:**
```bash
docker compose down -v
docker compose up -d
```

---

**🎉 Boa sorte!** Siga os passos na ordem e qualquer dúvida, consulte a seção de solução de problemas.
