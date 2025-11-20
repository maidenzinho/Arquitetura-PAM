from flask import Flask, request, jsonify
import requests
import pyotp
import time

app = Flask(__name__)

# Configuração MFA (em produção usar variáveis de ambiente)
MFA_SECRET = "JBSWY3DPEHPK3PXP"  # Secret para TOTP
VAULT_URL = "http://vault-ca:8080"

totp = pyotp.TOTP(MFA_SECRET)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "signer-app"})

@app.route('/mfa-setup', methods=['GET'])
def mfa_setup():
    """Endpoint para mostrar QR Code para configuração MFA"""
    provisioning_uri = totp.provisioning_uri("user@pam-system", issuer_name="PAM System")
    return jsonify({
        "secret": MFA_SECRET,
        "provisioning_uri": provisioning_uri,
        "instruction": "Use este secret em seu app authenticator"
    })

@app.route('/request-certificate', methods=['POST'])
from flask import Flask, request, jsonify
import requests
import pyotp
import time

app = Flask(__name__)

# Configuração MFA (em produção usar variáveis de ambiente)
MFA_SECRET = "JBSWY3DPEHPK3PXP"  # Secret para TOTP
VAULT_URL = "http://vault-ca:8080"

totp = pyotp.TOTP(MFA_SECRET)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "signer-app"})

@app.route('/mfa-setup', methods=['GET'])
def mfa_setup():
    """Endpoint para mostrar QR Code para configuração MFA"""
    provisioning_uri = totp.provisioning_uri("user@pam-system", issuer_name="PAM System")
    return jsonify({
        "secret": MFA_SECRET,
        "provisioning_uri": provisioning_uri,
        "instruction": "Use este secret em seu app authenticator"
    })

@app.route('/request-certificate', methods=['POST'])
def request_certificate():
    print("📨 Recebendo solicitação de certificado...")
    
    data = request.json
    public_key = data.get('public_key')
    mfa_code = data.get('mfa_code')
    
    if not public_key or not mfa_code:
        return jsonify({"error": "Chave pública e código MFA são obrigatórios"}), 400
    
    # Validar MFA
    if not totp.verify(mfa_code):
        print("❌ MFA inválido")
        return jsonify({"error": "Código MFA inválido"}), 401
    
    print("✅ MFA validado com sucesso")
    
    # Enviar para Vault para assinatura
    try:
        print("🔄 Enviando chave para Vault CA...")
        response = requests.post(f"{VAULT_URL}/sign", 
                               json={"public_key": public_key},
                               timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Certificado assinado com sucesso")
            return jsonify({
                "status": "success",
                "certificate": result["certificate"],
                "expires_in": result["expires_in"]
            })
        else:
            print("❌ Erro no Vault")
            return jsonify({"error": "Falha na assinatura do certificado"}), 500
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return jsonify({"error": "Falha na comunicação com Vault"}), 500

if __name__ == '__main__':
    print("🔑 Signer App iniciando na porta 5000...")
    print(f"📱 Secret MFA: {MFA_SECRET}")
    app.run(host='0.0.0.0', port=5000, debug=True)
