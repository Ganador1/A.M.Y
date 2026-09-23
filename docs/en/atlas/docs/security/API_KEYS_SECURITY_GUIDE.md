> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="-guía-de-seguridad-gestión-de-api-keys-en-axiom-atlas"></a>
# 🔐 Security Guide: API Key Management in AXIOM Atlas

**Last updated:** 9 of October, 2025
**Security Level:** Production
**Encryption:** Fernet (AES-128)

---

<a id="-tabla-de-contenidos"></a>
## 📋 Table of Contents

1. [Introduction](#introducción)
2. [Security System](#sistema-de-seguridad)
3. [Installation](#instalación)
4. [API Keys Configuration](#configuración-de-api-keys)
5. [Advanced Usage](#uso-avanzado)
6. [Best Practices](#mejores-prácticas)
7. [Troubleshooting](#troubleshooting)
8. [References](#referencias)

---

<a id="-introducción"></a>
## 🎯 Introduction

<a id="por-qué-usar-el-sistema-de-seguridad-integrado"></a>
### Why use the integrated security system?

❌ **Insecure method (NOT recommended):**
```bash
<a id="almacenar-en-texto-plano-en-env"></a>
# Almacenar en texto plano en .env
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxx  # ⚠️ INSEGURO
```

✅ **Secure method (RECOMMENDED):**
```bash
<a id="api-key-cifrada-con-fernet-aes-128"></a>
# API key cifrada con Fernet (AES-128)
python scripts/security/manage_api_keys.py set HUGGINGFACE hf_xxxxxxxxxxxxx
<a id="-almacenada-cifrada-en-api_keysenc"></a>
# ✅ Almacenada cifrada en .api_keys.enc
```

<a id="ventajas-del-sistema-seguro"></a>
### Advantages of the Secure System

| Feature | .env (plain text) | Secure System |
|---------------|-------------------|----------------|
| **Encryption** | ❌ No | ✅ Fernet (AES-128) |
| **Restrictive permissions** | ⚠️ Manual | ✅ Automatic (600) |
| **Key rotation** | ❌ No | ✅ Yes |
| **Audit log** | ❌ No | ✅ Yes |
| **Secure fallback** | ❌ No | ✅ Yes |
| **Centralized management** | ❌ No | ✅ Integrated CLI |
| **Git-safe** | ⚠️ Requires .gitignore | ✅ By design |

---

<a id="-sistema-de-seguridad"></a>
## 🏗️ Security System

<a id="arquitectura"></a>
### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Aplicación                            │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Hugging Face Provider                             │ │
│  │  ┌──────────────────────────────────────────────┐  │ │
│  │  │  APIKeysManager.get_api_key("HUGGINGFACE")   │  │ │
│  │  └────────────────────┬─────────────────────────┘  │ │
│  └───────────────────────┼────────────────────────────┘ │
└────────────────────────────┼─────────────────────────────┘
                             │
                ┌────────────▼────────────┐
                │   APIKeysManager        │
                │  ┌──────────────────┐   │
                │  │ 1. Check cache   │   │
                │  │ 2. Check file    │   │
                │  │ 3. Check ENV     │   │
                │  └──────────────────┘   │
                └────────────┬────────────┘
                             │
            ┌────────────────┴────────────────┐
            │                                 │
      ┌─────▼──────┐                  ┌──────▼─────┐
      │ .api_keys  │                  │    ENV     │
      │  .enc      │                  │  FALLBACK  │
      │ (cifrado)  │                  │            │
      └────────────┘                  └────────────┘
            │
     ┌──────▼──────┐
     │  Secrets    │
     │  Manager    │
     │  (Fernet)   │
     └─────────────┘
           │
     ┌─────▼──────┐
     │ .secrets   │
     │   .key     │
     │  (600)     │
     └────────────┘
```

<a id="componentes"></a>
### Components

1. **SecretsManager** ([`app/config/secrets_manager.py`](../../../../../atlas/app/config/secrets_manager.py))
   - Fernet encryption (AES-128)
   - Key management
   - Key rotation

2. **APIKeysManager** ([`app/config/api_keys_manager.py`](../../../../../atlas/app/config/api_keys_manager.py))
   - Centralized API key management
   - Encrypted storage
   - Fallback to ENV

3. **CLI Manager** (`scripts/security/manage_api_keys.py` (historical resource not included))
   - Command-line interface
   - Interactive management
   - Import/export

---

<a id="-instalación"></a>
## 💻 Installation

<a id="requisitos"></a>
### Requirements

```bash
<a id="instalar-dependencias-de-seguridad"></a>
# Instalar dependencias de seguridad
pip install cryptography rich

<a id="verificar-instalación"></a>
# Verificar instalación
python -c "from cryptography.fernet import Fernet; print('✅ Cryptography OK')"
```

<a id="inicialización"></a>
### Initialization

```bash
<a id="inicializar-sistema-de-seguridad"></a>
# Inicializar sistema de seguridad
python scripts/security/manage_api_keys.py stats

<a id="salida-esperada"></a>
# Salida esperada:
<a id="-secrets-manager-inicializado-secretskey"></a>
# 🔐 Secrets Manager inicializado: .secrets.key
<a id="-estadísticas-del-gestor-de-api-keys"></a>
# 📊 Estadísticas del Gestor de API Keys
<a id=""></a>
# ...
```

This automatically creates:
- `.secrets.key` - Master encryption key (permissions 600)
- `.api_keys.enc` - Encrypted API key storage (created when saving the first key)

---

<a id="-configuración-de-api-keys"></a>
## 🔑 API Keys Configuration

<a id="opción-1-cli-interactiva-recomendado"></a>
### Option 1: Interactive CLI (Recommended)

<a id="configurar-api-key"></a>
#### Configure API Key

```bash
<a id="configurar-hugging-face"></a>
# Configurar Hugging Face
python scripts/security/manage_api_keys.py set HUGGINGFACE hf_xxxxxxxxxxxxx

<a id="configurar-openai"></a>
# Configurar OpenAI
python scripts/security/manage_api_keys.py set OPENAI sk-xxxxxxxxxxxxxxx

<a id="configurar-groq"></a>
# Configurar Groq
python scripts/security/manage_api_keys.py set GROQ gsk_xxxxxxxxxxxx
```

<a id="listar-proveedores"></a>
#### List Providers

```bash
python scripts/security/manage_api_keys.py list
```

Output:
```
┏━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Proveedor    ┃ Estado ┃ API Key (masked) ┃ Fuente    ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ HUGGINGFACE  │   ✅   │ hf_EYAts...kPGo  │ encrypted │
│ OPENAI       │   ✅   │ sk-proj_...5T1I  │ encrypted │
│ GROQ         │   ✅   │ gsk_HWYm...cDLa  │ encrypted │
│ ANTHROPIC    │   ❌   │ -                │ -         │
│ TOGETHER     │   ❌   │ -                │ -         │
...
```

<a id="ver-api-key-específica"></a>
#### View Specific API Key

```bash
python scripts/security/manage_api_keys.py get HUGGINGFACE
```

<a id="eliminar-api-key"></a>
#### Delete API Key

```bash
python scripts/security/manage_api_keys.py remove OPENAI
```

<a id="opción-2-importar-desde-variables-de-entorno"></a>
### Option 2: Import from Environment Variables

If you already have API keys in environment variables:

```bash
<a id="1-configurar-variables-de-entorno"></a>
# 1. Configurar variables de entorno
export HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxx
export OPENAI_API_KEY=sk-xxxxxxxxxxxxxxx
export GROQ_API_KEY=gsk_xxxxxxxxxxxx

<a id="2-importar-todas-a-almacenamiento-seguro"></a>
# 2. Importar todas a almacenamiento seguro
python scripts/security/manage_api_keys.py import

<a id="salida"></a>
# Salida:
<a id="-importando-api-keys-desde-variables-de-entorno"></a>
# 📥 Importando API keys desde variables de entorno...
<a id="-importada-api-key-para-huggingface-desde-huggingface_api_key"></a>
# 📥 Importada API key para HUGGINGFACE desde HUGGINGFACE_API_KEY
<a id="-importada-api-key-para-openai-desde-openai_api_key"></a>
# 📥 Importada API key para OPENAI desde OPENAI_API_KEY
<a id="-importada-api-key-para-groq-desde-groq_api_key"></a>
# 📥 Importada API key para GROQ desde GROQ_API_KEY
<a id="-importadas-3-api-keys-exitosamente"></a>
# ✅ Importadas 3 API keys exitosamente
```

<a id="opción-3-programáticamente"></a>
### Option 3: Programmatically

```python
from app.config.api_keys_manager import get_api_keys_manager

<a id="obtener-instancia-del-manager"></a>
# Obtener instancia del manager
manager = get_api_keys_manager()

<a id="configurar-api-key-1"></a>
# Configurar API key
manager.set_api_key("HUGGINGFACE", "hf_xxxxxxxxxxxxx", save=True)

<a id="obtener-api-key"></a>
# Obtener API key
api_key = manager.get_api_key("HUGGINGFACE")
print(f"API Key: {api_key[:10]}...")

<a id="verificar-si-existe"></a>
# Verificar si existe
if manager.has_api_key("OPENAI"):
    print("✅ OpenAI configurado")
```

---

<a id="-uso-avanzado"></a>
## 🚀 Advanced Usage

<a id="exportar-configuración"></a>
### Export Configuration

```bash
<a id="generar-envexample-con-template"></a>
# Generar .env.example con template
python scripts/security/manage_api_keys.py export

<a id="especificar-archivo-de-salida"></a>
# Especificar archivo de salida
python scripts/security/manage_api_keys.py export -o .env.production
```

Generates:
```bash
<a id="api-keys-configuration-for-axiom-atlas"></a>
# API Keys Configuration for AXIOM Atlas
<a id="copy-this-file-to-env-and-fill-in-your-actual-api-keys"></a>
# Copy this file to .env and fill in your actual API keys

<a id="-1"></a>
# ============================================================
<a id="cloud-ai-providers"></a>
# CLOUD AI PROVIDERS
<a id="-2"></a>
# ============================================================

<a id="-configured"></a>
# ✅ Configured
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

<a id="-not-configured"></a>
# ❌ Not configured
<a id="openai_api_keyyour_openai_api_key_here"></a>
# OPENAI_API_KEY=your_openai_api_key_here

...
```

<a id="rotar-clave-de-cifrado"></a>
### Rotate Encryption Key

⚠️ **WARNING:** This operation decrypts and re-encrypts all API keys.

```bash
python scripts/security/manage_api_keys.py rotate

<a id="con-contraseña-personalizada"></a>
# Con contraseña personalizada
python scripts/security/manage_api_keys.py rotate
<a id="prompt-nueva-contraseña-vacío-para-clave-aleatoria-mi-password-segura"></a>
# Prompt: Nueva contraseña (vacío para clave aleatoria): mi-password-segura
```

<a id="ver-estadísticas"></a>
### View Statistics

```bash
python scripts/security/manage_api_keys.py stats
```

Output:
```
📊 Estadísticas del Gestor de API Keys

 Total de proveedores        10
 Proveedores configurados    3 ✅
 Proveedores sin configurar  7 ❌
 Archivo de almacenamiento   .api_keys.enc
 Archivo existe              ✅
 Fallback a ENV habilitado   ✅
```

<a id="usar-en-código"></a>
### Use in Code

```python
from app.config.api_keys_manager import get_api_key

<a id="función-de-conveniencia"></a>
# Función de conveniencia
api_key = get_api_key("HUGGINGFACE")

<a id="usar-en-provider"></a>
# Usar en provider
from app.services.llm_providers.huggingface_provider import HuggingFaceProvider

<a id="automáticamente-usa-el-sistema-seguro"></a>
# Automáticamente usa el sistema seguro
provider = HuggingFaceProvider()
<a id="busca-en-almacenamiento-cifrado--env--falla"></a>
# Busca en: almacenamiento cifrado → ENV → falla
```

---

<a id="-mejores-prácticas"></a>
## 🛡️ Best Practices

<a id="seguridad"></a>
### Security

1. **Never commit sensitive files**
   ```gitignore
   # .gitignore
   .secrets.key        # ✅ Encryption key
   .api_keys.enc       # ✅ Encrypted API keys
   .env                # ✅ Environment variables
   .env.local          # ✅ Local ENV
   ```

2. **Restrictive permissions**
   ```bash
   # Automatic, but verify
   ls -la .secrets.key  # should be: -rw------- (600)
   ls -la .api_keys.enc # should be: -rw------- (600)
   ```

3. **Periodic key rotation**
   ```bash
   # Every 90 days (recommended)
   python scripts/security/manage_api_keys.py rotate
   ```

4. **Secure backup**
   ```bash
   # Backup of master key (store offline)
   cp .secrets.key .secrets.key.backup

   # Encrypt with GPG (optional)
   gpg --symmetric --cipher-algo AES256 .secrets.key.backup
   ```

<a id="desarrollo"></a>
### Development

1. **Local development**
   ```bash
   # Use environment variables for development
   export HUGGINGFACE_API_KEY=hf_dev_key

   # In production, import to secure system
   python scripts/security/manage_api_keys.py import
   ```

2. **CI/CD**
   ```yaml
   # GitHub Actions example
   env:
     HUGGINGFACE_API_KEY: ${{ secrets.HUGGINGFACE_API_KEY }}
     OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

   # In the job, import to secure system
   - name: Import API Keys
     run: python scripts/security/manage_api_keys.py import
   ```

3. **Testing**
   ```python
   # tests/conftest.py
   import pytest
   from app.config.api_keys_manager import get_api_keys_manager

   @pytest.fixture
   def mock_api_keys():
       manager = get_api_keys_manager()
       manager.set_api_key("HUGGINGFACE", "hf_test_key", save=False)
       yield manager
       # Cleanup
       manager.remove_api_key("HUGGINGFACE", save=False)
   ```

<a id="producción"></a>
### Production

1. **Production server**
   ```bash
   # 1. Copy master key
   scp .secrets.key user@server:/path/to/atlas/

   # 2. Copy encrypted API keys
   scp .api_keys.enc user@server:/path/to/atlas/

   # 3. Or import from secure ENV
   ssh user@server "cd /path/to/atlas && python scripts/security/manage_api_keys.py import"
   ```

2. **Docker**
   ```dockerfile
   # Dockerfile
   FROM python:3.13

   # Copy security files
   COPY .secrets.key /app/
   COPY .api_keys.enc /app/

   # Permissions
   RUN chmod 600 /app/.secrets.key
   RUN chmod 600 /app/.api_keys.enc
   ```

3. **Kubernetes**
   ```yaml
   # kubernetes-secret.yaml
   apiVersion: v1
   kind: Secret
   metadata:
     name: axiom-api-keys
   type: Opaque
   data:
     secrets-key: <base64-encoded-.secrets.key>
     api-keys-enc: <base64-encoded-.api_keys.enc>
   ```

---

<a id="-troubleshooting"></a>
## 🐛 Troubleshooting

<a id="error-cipher-no-inicializado"></a>
### Error: "Cipher not initialized"

**Cause:** File `.secrets.key` not found or corrupted

**Solution:**
```bash
<a id="eliminar-archivo-corrupto"></a>
# Eliminar archivo corrupto
rm .secrets.key

<a id="re-inicializar"></a>
# Re-inicializar
python scripts/security/manage_api_keys.py stats

<a id="re-importar-api-keys"></a>
# Re-importar API keys
python scripts/security/manage_api_keys.py import
```

<a id="error-no-se-encontró-api-key"></a>
### Error: "API key not found"

**Cause:** API key not configured

**Solution:**
```bash
<a id="verificar-estado"></a>
# Verificar estado
python scripts/security/manage_api_keys.py list

<a id="configurar-api-key-2"></a>
# Configurar API key
python scripts/security/manage_api_keys.py set HUGGINGFACE hf_xxxxxxxxxxxxx
```

<a id="error-invalid-encrypted-data-or-key"></a>
### Error: "Invalid encrypted data or key"

**Cause:** Encryption key changed after encryption

**Solution:**
```bash
<a id="restaurar-backup-de-clave"></a>
# Restaurar backup de clave
cp .secrets.key.backup .secrets.key

<a id="o-re-configurar-todas-las-api-keys"></a>
# O re-configurar todas las API keys
python scripts/security/manage_api_keys.py remove HUGGINGFACE -y
python scripts/security/manage_api_keys.py set HUGGINGFACE hf_xxxxxxxxxxxxx
```

<a id="provider-no-usa-api-key-cifrada"></a>
### Provider does not use encrypted API key

**Cause:** Provider not updated

**Solution:**
```python
<a id="verificar-que-el-provider-busca-en-apikeysmanager"></a>
# Verificar que el provider busca en APIKeysManager
from app.services.llm_providers.huggingface_provider import HuggingFaceProvider

provider = HuggingFaceProvider()

<a id="debe-mostrar"></a>
# Debe mostrar:
<a id="-usando-api-key-desde-almacenamiento-seguro-cifrado"></a>
# 🔐 Usando API key desde almacenamiento seguro cifrado
```

---

<a id="-referencias"></a>
## 📚 References

<a id="archivos-del-sistema"></a>
### System Files

| File | Description | Permissions |
|---------|-------------|----------|
| `.secrets.key` | Fernet master encryption key | 600 |
| `.api_keys.enc` | Encrypted API keys | 600 |
| `app/config/secrets_manager.py` | Secrets manager with Fernet | - |
| `app/config/api_keys_manager.py` | API keys manager | - |
| `scripts/security/manage_api_keys.py` | Management CLI | 755 |

<a id="proveedores-soportados"></a>
### Supported Providers

```python
SUPPORTED_PROVIDERS = [
    "HUGGINGFACE",    # Hugging Face Inference API
    "OPENAI",         # OpenAI GPT-4, etc.
    "ANTHROPIC",      # Claude, etc.
    "GROQ",           # Groq ultra-fast inference
    "TOGETHER",       # Together AI
    "COHERE",         # Cohere models
    "REPLICATE",      # Replicate models
    "GOOGLE_AI",      # Google AI (Gemini, etc.)
    "AWS_BEDROCK",    # AWS Bedrock
    "AZURE_OPENAI"    # Azure OpenAI Service
]
```

<a id="algoritmos-de-cifrado"></a>
### Encryption Algorithms

- **Fernet** (AES-128 in CBC mode with HMAC-SHA256)
- **PBKDF2** for key derivation from password
- **100,000 iterations** for key derivation
- **Permissions 600** (owner read/write only)

<a id="comandos-cli"></a>
### CLI Commands

```bash
set <provider> <api_key>  # Configurar API key
get <provider>            # Obtener API key (masked)
list                      # Listar proveedores
remove <provider>         # Eliminar API key
import                    # Importar desde ENV
export                    # Exportar a .env.example
stats                     # Estadísticas
rotate                    # Rotar clave de cifrado
test                      # Test de conexión
```

---

<a id="-checklist-de-seguridad"></a>
## ✅ Security Checklist

<a id="desarrollo-1"></a>
### Development

- [ ] `.gitignore` includes `.secrets.key` and `.api_keys.enc`
- [ ] API keys configured with CLI
- [ ] Tests use fixtures with mock API keys
- [ ] No API keys in source code

<a id="staging"></a>
### Staging

- [ ] Master key transferred securely
- [ ] API keys imported from secure ENV
- [ ] Permissions verified (600)
- [ ] Integration tests pass

<a id="producción-1"></a>
### Production

- [ ] Master key backed up (offline)
- [ ] API keys rotated in the last 90 days
- [ ] Access monitoring configured
- [ ] Recovery plan documented

---

<a id="-resumen"></a>
## 🎯 Summary

<a id="flujo-de-trabajo-recomendado"></a>
### Recommended Workflow

```bash
<a id="1-inicializar"></a>
# 1. Inicializar
python scripts/security/manage_api_keys.py stats

<a id="2-configurar-api-keys"></a>
# 2. Configurar API keys
python scripts/security/manage_api_keys.py set HUGGINGFACE hf_xxxxxxxxxxxxx

<a id="3-verificar"></a>
# 3. Verificar
python scripts/security/manage_api_keys.py list

<a id="4-usar-en-aplicación"></a>
# 4. Usar en aplicación
python examples/huggingface_multiagent_demo.py
```

<a id="ventajas"></a>
### Advantages

✅ Enterprise-grade encryption (AES-128)
✅ Centralized management with CLI
✅ Automatic fallback to ENV
✅ Simple key rotation
✅ Git-safe by design
✅ Automatic permissions (600)
✅ Backup and recovery
✅ Integrated audit log

---

**🔐 Your API key infrastructure is now professionally secured!**

*Last updated: 9 of October, 2025*
