"""
Cryptography Router

Router FastAPI para operaciones criptográficas básicas utilizando algoritmos RSA.
Proporciona endpoints REST API para generación de claves RSA, encriptación y desencriptación
de mensajes utilizando criptografía de clave pública. Diseñado para uso educativo y de
demostración con énfasis en prácticas de seguridad responsables.

⚠️ Uso responsable: no envíes, registres ni devuelvas claves privadas o PII.
Usa tamaños de clave seguros y almacena secretos fuera de este servicio.
Consulta `ETHICS_AND_SAFETY.md`.

Capacidades principales:
- Generación de pares de claves RSA (pública y privada) con tamaños configurables
- Encriptación de mensajes utilizando clave pública RSA
- Desencriptación de mensajes utilizando clave privada RSA
- Validación automática de integridad de claves y mensajes
- Manejo seguro de datos sensibles con limpieza automática de memoria
- Soporte para múltiples tamaños de clave RSA estándar (1024, 2048, 4096 bits)
- Codificación automática de mensajes en base64 para transmisión segura
- Verificación de formato y validez de claves antes del procesamiento

Endpoints disponibles:
- POST /rsa/keys: Generación de claves RSA públicas y privadas
- POST /rsa/encrypt: Encriptación de mensajes con clave pública RSA
- POST /rsa/decrypt: Desencriptación de mensajes con clave privada RSA

Dependencias:
- generate_rsa_keys: Función de generación de claves RSA
- rsa_encrypt: Función de encriptación RSA
- rsa_decrypt: Función de desencriptación RSA
- RSAKeyRequest: Solicitud de generación de claves
- RSAEncryptRequest: Solicitud de encriptación
- RSADecryptRequest: Solicitud de desencriptación

Consideraciones éticas y de seguridad:
- No usar para datos sensibles en producción sin auditoría de seguridad
- Implementar rotación regular de claves
- Usar HTTPS para todas las comunicaciones
- No almacenar claves privadas en logs o bases de datos
- Limitar el tamaño de mensajes para prevenir ataques DoS
- Validar entrada de usuario para prevenir inyección de código

Uso típico:
    from app.routers.cryptography import router

    # El router se integra automáticamente en la aplicación FastAPI
    # Los endpoints están disponibles sin prefijo específico
"""

from fastapi import APIRouter
from app.models.models import RSAKeyRequest, RSAEncryptRequest, RSADecryptRequest
from app.services.cryptography import generate_rsa_keys, rsa_encrypt, rsa_decrypt

router = APIRouter()

@router.post("/rsa/keys")
def get_rsa_keys(request: RSAKeyRequest):
    """
    Generate RSA public and private keys.
    """
    return generate_rsa_keys(request.bits)

@router.post("/rsa/encrypt")
def post_rsa_encrypt(request: RSAEncryptRequest):
    """
    Encrypt a message using an RSA public key.
    """
    encrypted_message = rsa_encrypt(request.public_key, request.message)
    return {"encrypted_message": encrypted_message}

@router.post("/rsa/decrypt")
def post_rsa_decrypt(request: RSADecryptRequest):
    """
    Decrypt a message using an RSA private key.
    """
    decrypted_message = rsa_decrypt(request.private_key, request.encrypted_message)
    return {"decrypted_message": decrypted_message}
