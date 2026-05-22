# 🔐 Guía de Seguridad: Gestión de API Keys en AXIOM Atlas

**Última actualización:** 9 de Octubre, 2025
**Nivel de Seguridad:** Producción
**Cifrado:** Fernet (AES-128)

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Sistema de Seguridad](#sistema-de-seguridad)
3. [Instalación](#instalación)
4. [Configuración de API Keys](#configuración-de-api-keys)
5. [Uso Avanzado](#uso-avanzado)
6. [Mejores Prácticas](#mejores-prácticas)
7. [Troubleshooting](#troubleshooting)
8. [Referencias](#referencias)

---

## 🎯 Introducción

### ¿Por qué usar el sistema de seguridad integrado?

❌ **Método inseguro (NO recomendado):**
```bash
# Almacenar en texto plano en .env
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxx  # ⚠️ INSEGURO
```

✅ **Método seguro (RECOMENDADO):**
```bash
# API key cifrada con Fernet (AES-128)
python scripts/security/manage_api_keys.py set HUGGINGFACE hf_xxxxxxxxxxxxx
# ✅ Almacenada cifrada en .api_keys.enc
```

### Ventajas del Sistema Seguro

| Característica | .env (texto plano) | Sistema Seguro |
|---------------|-------------------|----------------|
| **Cifrado** | ❌ No | ✅ Fernet (AES-128) |
| **Permisos restrictivos** | ⚠️ Manual | ✅ Automático (600) |
| **Rotación de claves** | ❌ No | ✅ Sí |
| **Audit log** | ❌ No | ✅ Sí |
| **Fallback seguro** | ❌ No | ✅ Sí |
| **Gestión centralizada** | ❌ No | ✅ CLI integrada |
| **Git-safe** | ⚠️ Requiere .gitignore | ✅ Por diseño |

---

## 🏗️ Sistema de Seguridad

### Arquitectura

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

### Componentes

1. **SecretsManager** ([`app/config/secrets_manager.py`](../../app/config/secrets_manager.py))
   - Cifrado Fernet (AES-128)
   - Gestión de claves
   - Rotación de claves

2. **APIKeysManager** ([`app/config/api_keys_manager.py`](../../app/config/api_keys_manager.py))
   - Gestión centralizada de API keys
   - Almacenamiento cifrado
   - Fallback a ENV

3. **CLI Manager** ([`scripts/security/manage_api_keys.py`](../../scripts/security/manage_api_keys.py))
   - Interfaz de línea de comandos
   - Gestión interactiva
   - Importación/exportación

---

## 💻 Instalación

### Requisitos

```bash
# Instalar dependencias de seguridad
pip install cryptography rich

# Verificar instalación
python -c "from cryptography.fernet import Fernet; print('✅ Cryptography OK')"
```

### Inicialización

```bash
# Inicializar sistema de seguridad
python scripts/security/manage_api_keys.py stats

# Salida esperada:
# 🔐 Secrets Manager inicializado: .secrets.key
# 📊 Estadísticas del Gestor de API Keys
# ...
```

Esto crea automáticamente:
- `.secrets.key` - Clave maestra de cifrado (permisos 600)
- `.api_keys.enc` - Almacenamiento cifrado de API keys (se crea al guardar primera key)

---

## 🔑 Configuración de API Keys

### Opción 1: CLI Interactiva (Recomendado)

#### Configurar API Key

```bash
# Configurar Hugging Face
python scripts/security/manage_api_keys.py set HUGGINGFACE hf_xxxxxxxxxxxxx

# Configurar OpenAI
python scripts/security/manage_api_keys.py set OPENAI sk-xxxxxxxxxxxxxxx

# Configurar Groq
python scripts/security/manage_api_keys.py set GROQ gsk_xxxxxxxxxxxx
```

#### Listar Proveedores

```bash
python scripts/security/manage_api_keys.py list
```

Salida:
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

#### Ver API Key Específica

```bash
python scripts/security/manage_api_keys.py get HUGGINGFACE
```

#### Eliminar API Key

```bash
python scripts/security/manage_api_keys.py remove OPENAI
```

### Opción 2: Importar desde Variables de Entorno

Si ya tienes API keys en variables de entorno:

```bash
# 1. Configurar variables de entorno
export HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxx
export OPENAI_API_KEY=sk-xxxxxxxxxxxxxxx
export GROQ_API_KEY=gsk_xxxxxxxxxxxx

# 2. Importar todas a almacenamiento seguro
python scripts/security/manage_api_keys.py import

# Salida:
# 📥 Importando API keys desde variables de entorno...
# 📥 Importada API key para HUGGINGFACE desde HUGGINGFACE_API_KEY
# 📥 Importada API key para OPENAI desde OPENAI_API_KEY
# 📥 Importada API key para GROQ desde GROQ_API_KEY
# ✅ Importadas 3 API keys exitosamente
```

### Opción 3: Programáticamente

```python
from app.config.api_keys_manager import get_api_keys_manager

# Obtener instancia del manager
manager = get_api_keys_manager()

# Configurar API key
manager.set_api_key("HUGGINGFACE", "hf_xxxxxxxxxxxxx", save=True)

# Obtener API key
api_key = manager.get_api_key("HUGGINGFACE")
print(f"API Key: {api_key[:10]}...")

# Verificar si existe
if manager.has_api_key("OPENAI"):
    print("✅ OpenAI configurado")
```

---

## 🚀 Uso Avanzado

### Exportar Configuración

```bash
# Generar .env.example con template
python scripts/security/manage_api_keys.py export

# Especificar archivo de salida
python scripts/security/manage_api_keys.py export -o .env.production
```

Genera:
```bash
# API Keys Configuration for AXIOM Atlas
# Copy this file to .env and fill in your actual API keys

# ============================================================
# CLOUD AI PROVIDERS
# ============================================================

# ✅ Configured
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# ❌ Not configured
# OPENAI_API_KEY=your_openai_api_key_here

...
```

### Rotar Clave de Cifrado

⚠️ **ADVERTENCIA:** Esta operación descifra y vuelve a cifrar todas las API keys.

```bash
python scripts/security/manage_api_keys.py rotate

# Con contraseña personalizada
python scripts/security/manage_api_keys.py rotate
# Prompt: Nueva contraseña (vacío para clave aleatoria): mi-password-segura
```

### Ver Estadísticas

```bash
python scripts/security/manage_api_keys.py stats
```

Salida:
```
📊 Estadísticas del Gestor de API Keys

 Total de proveedores        10
 Proveedores configurados    3 ✅
 Proveedores sin configurar  7 ❌
 Archivo de almacenamiento   .api_keys.enc
 Archivo existe              ✅
 Fallback a ENV habilitado   ✅
```

### Usar en Código

```python
from app.config.api_keys_manager import get_api_key

# Función de conveniencia
api_key = get_api_key("HUGGINGFACE")

# Usar en provider
from app.services.llm_providers.huggingface_provider import HuggingFaceProvider

# Automáticamente usa el sistema seguro
provider = HuggingFaceProvider()
# Busca en: almacenamiento cifrado → ENV → falla
```

---

## 🛡️ Mejores Prácticas

### Seguridad

1. **Nunca commits archivos sensibles**
   ```gitignore
   # .gitignore
   .secrets.key        # ✅ Clave de cifrado
   .api_keys.enc       # ✅ API keys cifradas
   .env                # ✅ Variables de entorno
   .env.local          # ✅ ENV local
   ```

2. **Permisos restrictivos**
   ```bash
   # Automático, pero verificar
   ls -la .secrets.key  # debe ser: -rw------- (600)
   ls -la .api_keys.enc # debe ser: -rw------- (600)
   ```

3. **Rotación periódica de claves**
   ```bash
   # Cada 90 días (recomendado)
   python scripts/security/manage_api_keys.py rotate
   ```

4. **Backup seguro**
   ```bash
   # Backup de clave maestra (guardar offline)
   cp .secrets.key .secrets.key.backup

   # Encriptar con GPG (opcional)
   gpg --symmetric --cipher-algo AES256 .secrets.key.backup
   ```

### Desarrollo

1. **Desarrollo local**
   ```bash
   # Usa variables de entorno para desarrollo
   export HUGGINGFACE_API_KEY=hf_dev_key

   # En producción, importar a sistema seguro
   python scripts/security/manage_api_keys.py import
   ```

2. **CI/CD**
   ```yaml
   # GitHub Actions example
   env:
     HUGGINGFACE_API_KEY: ${{ secrets.HUGGINGFACE_API_KEY }}
     OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

   # En el job, importar a sistema seguro
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

### Producción

1. **Servidor de producción**
   ```bash
   # 1. Copiar clave maestra
   scp .secrets.key user@server:/path/to/atlas/

   # 2. Copiar API keys cifradas
   scp .api_keys.enc user@server:/path/to/atlas/

   # 3. O importar desde ENV seguras
   ssh user@server "cd /path/to/atlas && python scripts/security/manage_api_keys.py import"
   ```

2. **Docker**
   ```dockerfile
   # Dockerfile
   FROM python:3.13

   # Copiar archivos de seguridad
   COPY .secrets.key /app/
   COPY .api_keys.enc /app/

   # Permisos
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

## 🐛 Troubleshooting

### Error: "Cipher no inicializado"

**Causa:** Archivo `.secrets.key` no encontrado o corrupto

**Solución:**
```bash
# Eliminar archivo corrupto
rm .secrets.key

# Re-inicializar
python scripts/security/manage_api_keys.py stats

# Re-importar API keys
python scripts/security/manage_api_keys.py import
```

### Error: "No se encontró API key"

**Causa:** API key no configurada

**Solución:**
```bash
# Verificar estado
python scripts/security/manage_api_keys.py list

# Configurar API key
python scripts/security/manage_api_keys.py set HUGGINGFACE hf_xxxxxxxxxxxxx
```

### Error: "Invalid encrypted data or key"

**Causa:** Clave de cifrado cambió después de cifrar

**Solución:**
```bash
# Restaurar backup de clave
cp .secrets.key.backup .secrets.key

# O re-configurar todas las API keys
python scripts/security/manage_api_keys.py remove HUGGINGFACE -y
python scripts/security/manage_api_keys.py set HUGGINGFACE hf_xxxxxxxxxxxxx
```

### Provider no usa API key cifrada

**Causa:** Provider no actualizado

**Solución:**
```python
# Verificar que el provider busca en APIKeysManager
from app.services.llm_providers.huggingface_provider import HuggingFaceProvider

provider = HuggingFaceProvider()

# Debe mostrar:
# 🔐 Usando API key desde almacenamiento seguro cifrado
```

---

## 📚 Referencias

### Archivos del Sistema

| Archivo | Descripción | Permisos |
|---------|-------------|----------|
| `.secrets.key` | Clave maestra de cifrado Fernet | 600 |
| `.api_keys.enc` | API keys cifradas | 600 |
| `app/config/secrets_manager.py` | Gestor de secretos con Fernet | - |
| `app/config/api_keys_manager.py` | Gestor de API keys | - |
| `scripts/security/manage_api_keys.py` | CLI de gestión | 755 |

### Proveedores Soportados

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

### Algoritmos de Cifrado

- **Fernet** (AES-128 en modo CBC con HMAC-SHA256)
- **PBKDF2** para derivación de claves desde contraseña
- **100,000 iteraciones** para key derivation
- **Permisos 600** (lectura/escritura solo propietario)

### Comandos CLI

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

## ✅ Checklist de Seguridad

### Desarrollo

- [ ] `.gitignore` incluye `.secrets.key` y `.api_keys.enc`
- [ ] API keys configuradas con CLI
- [ ] Tests usan fixtures con mock API keys
- [ ] No hay API keys en código fuente

### Staging

- [ ] Clave maestra transferida de forma segura
- [ ] API keys importadas desde ENV seguras
- [ ] Permisos verificados (600)
- [ ] Tests de integración pasan

### Producción

- [ ] Clave maestra backed up (offline)
- [ ] API keys rotadas en los últimos 90 días
- [ ] Monitoreo de acceso configurado
- [ ] Plan de recuperación documentado

---

## 🎯 Resumen

### Flujo de Trabajo Recomendado

```bash
# 1. Inicializar
python scripts/security/manage_api_keys.py stats

# 2. Configurar API keys
python scripts/security/manage_api_keys.py set HUGGINGFACE hf_xxxxxxxxxxxxx

# 3. Verificar
python scripts/security/manage_api_keys.py list

# 4. Usar en aplicación
python examples/huggingface_multiagent_demo.py
```

### Ventajas

✅ Cifrado de grado empresarial (AES-128)
✅ Gestión centralizada con CLI
✅ Fallback automático a ENV
✅ Rotación de claves sencilla
✅ Git-safe por diseño
✅ Permisos automáticos (600)
✅ Backup y recuperación
✅ Audit log integrado

---

**🔐 ¡Tu infraestructura de API keys está ahora asegurada profesionalmente!**

*Última actualización: 9 de Octubre, 2025*
