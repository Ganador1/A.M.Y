"""
🔐 Sistema de Autenticación y Autorización AXIOM v4.1
===============================================

Módulo avanzado de autenticación OAuth2/JWT para la plataforma AXIOM v4.1,
implementando control de acceso basado en roles y scopes para operaciones
científicas seguras.

Características principales:
- 🔑 Autenticación OAuth2 con tokens JWT
- 👥 Control de acceso basado en roles (admin, researcher, lab_operator)
- 🎯 Scopes granulares para operaciones específicas
- 🔄 Sistema de refresh tokens para sesiones prolongadas
- 📊 Logging completo de operaciones de seguridad
- ⚡ Validación en tiempo real con Pydantic v2
- 🛡️ Verificación de seguridad integrada

Usuarios del sistema:
- system_admin: Acceso completo a configuración y administración
- researcher: Acceso a ejecución de experimentos y análisis
- lab_operator: Acceso limitado a equipos de laboratorio

Scopes disponibles:
- system:admin - Administración completa del sistema
- system:read - Lectura de información del sistema
- research:execute - Ejecución de experimentos de investigación
- lab:equipment - Control de equipos de laboratorio
- lab:schedule - Programación de experimentos
- experimental:run - Ejecución de protocolos experimentales
- agent:orchestrate - Orquestación de agentes multi-modales
- knowledge:write - Escritura en grafo de conocimiento
- scheduler:policy - Configuración de políticas de scheduling
- reproducibility:verify - Verificación de reproducibilidad
- publication:generate - Generación de publicaciones científicas

Ejemplos de uso:
```python
# Autenticación básica
import requests
import httpx
from app.exceptions.domain.biology import BiologyError

response = await httpx.post("/auth/token", data={
    "username": "researcher",
    "password": "research_secret",
    "grant_type": "password"
})

# Uso del token
headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
result = await httpx.get("/api/experiments", headers=headers)
```

Referencias académicas:
- OAuth 2.0 Authorization Framework (RFC 6749)
- JSON Web Token (JWT) (RFC 7519)
- Role-Based Access Control (RBAC) patterns
- Security best practices for scientific computing platforms

Notas de seguridad:
- Tokens expiran en 30 minutos por defecto
- Refresh tokens válidos por 7 días
- Logging completo de todas las operaciones
- Validación de scopes en tiempo real
"""

import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field, validator
import jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.bootstrap_logging import logger
from app.config import settings
from app.types.auth_types import (
    DecodeTokenResult,
)

# Configuración del logger
# logger = get_logger(__name__)

# Configuración de seguridad JWT
SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# Contexto de hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Instancia del router
router = APIRouter(
    prefix="/auth",
    tags=["🔐 Autenticación"],
    responses={
        401: {"description": "Credenciales inválidas"},
        403: {"description": "Acceso denegado - scopes insuficientes"},
        422: {"description": "Datos de entrada inválidos"}
    }
)

# Modelo de seguridad para tokens
security = HTTPBearer()

# ========== MODELOS PYDANTIC V2 ==========

class ScopeInfo(BaseModel):
    """
    Información detallada de un scope de acceso.

    Attributes:
        scope: Identificador único del scope
        description: Descripción funcional del scope
    """
    scope: str = Field(..., description="Identificador del scope", min_length=1, max_length=50)
    description: str = Field(..., description="Descripción del scope", min_length=10, max_length=200)

    @validator('scope')
    def validate_scope_format(cls, v):
        """Validar formato del scope."""
        if ':' not in v:
            raise ValueError('Scope debe tener formato "categoria:accion"')
        return v

class SystemInfo(BaseModel):
    """
    Información del sistema de autenticación.

    Attributes:
        scopes_available: Lista de scopes disponibles en el sistema
        token_expires_in_minutes: Tiempo de expiración de access tokens
        refresh_token_expires_in_minutes: Tiempo de expiración de refresh tokens
    """
    scopes_available: List[ScopeInfo] = Field(..., description="Scopes disponibles en el sistema")
    token_expires_in_minutes: int = Field(..., description="Expiración de access tokens (minutos)", gt=0)
    refresh_token_expires_in_minutes: int = Field(..., description="Expiración de refresh tokens (minutos)", gt=0)

class TokenResponse(BaseModel):
    """
    Respuesta completa del endpoint de tokens OAuth2.

    Attributes:
        access_token: Token JWT para acceso a recursos
        refresh_token: Token para renovar access tokens
        token_type: Tipo de token (siempre "bearer")
        expires_in: Segundos hasta expiración del access token
        scope: Scopes concedidos separados por espacios
        issued_at: Timestamp ISO de emisión del token
    """
    access_token: str = Field(..., description="Token de acceso JWT")
    refresh_token: str = Field(..., description="Token de refresco")
    token_type: str = Field(default="bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Segundos hasta expiración", gt=0)
    scope: str = Field(..., description="Scopes concedidos")
    issued_at: str = Field(..., description="Timestamp de emisión (ISO 8601)")

class RefreshRequest(BaseModel):
    """
    Solicitud de refresco de token de acceso.

    Attributes:
        refresh_token: Token de refresco válido
    """
    refresh_token: str = Field(..., description="Token de refresco válido", min_length=10)

class UserVerification(BaseModel):
    """
    Información de verificación de usuario autenticado.

    Attributes:
        valid: Estado de validez del token
        user: Nombre de usuario
        scopes: Lista de scopes activos
        expires: Timestamp de expiración (Unix)
        issued_at: Timestamp de emisión (Unix)
        token_id: Identificador único del token
    """
    valid: bool = Field(default=True, description="Token válido")
    user: str = Field(..., description="Nombre de usuario")
    scopes: List[str] = Field(default_factory=list, description="Scopes activos")
    expires: Optional[int] = Field(None, description="Expiración Unix timestamp")
    issued_at: Optional[int] = Field(None, description="Emisión Unix timestamp")
    token_id: Optional[str] = Field(None, description="ID único del token")

# ========== CONFIGURACIÓN DE SCOPES ==========

SYSTEM_SCOPES = {
    "system:admin": "Acceso administrativo completo al sistema AXIOM",
    "system:read": "Lectura de información del sistema y configuración",
    "research:execute": "Ejecución de experimentos de investigación científica",
    "lab:equipment": "Control y monitoreo de equipos de laboratorio",
    "lab:schedule": "Programación y calendarización de experimentos",
    "experimental:run": "Ejecución de protocolos experimentales validados",
    "agent:orchestrate": "Orquestación de agentes multi-modales y IA",
    "knowledge:write": "Escritura y modificación del grafo de conocimiento",
    "scheduler:policy": "Configuración de políticas de scheduling avanzado",
    "reproducibility:verify": "Verificación de reproducibilidad experimental",
    "publication:generate": "Generación automática de publicaciones científicas"
}

# ========== USUARIOS DEL SISTEMA ==========

SYSTEM_USERS = {
    "system_admin": {
        "password": (settings.system_admin_password or os.getenv("SYSTEM_ADMIN_PASSWORD", "admin_default_secret")),
        "default_scopes": [
            "system:admin", "system:read", "research:execute", "lab:equipment",
            "lab:schedule", "experimental:run", "agent:orchestrate",
            "knowledge:write", "scheduler:policy", "reproducibility:verify", "publication:generate"
        ]
    },
    "researcher": {
        "password": (settings.researcher_password or os.getenv("RESEARCHER_PASSWORD", "research_default_secret")),
        "default_scopes": [
            "system:read", "research:execute", "experimental:run",
            "agent:orchestrate", "knowledge:write", "reproducibility:verify", "publication:generate"
        ]
    },
    "lab_operator": {
        "password": (settings.lab_operator_password or os.getenv("LAB_OPERATOR_PASSWORD", "lab_default_secret")),
        "default_scopes": [
            "system:read", "lab:equipment", "lab:schedule", "experimental:run"
        ]
    }
}

# ========== FUNCIONES UTILITARIAS ==========

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Autenticar credenciales de usuario y retornar información del usuario.

    Args:
        username: Nombre de usuario del sistema
        password: Contraseña proporcionada

    Returns:
        Dict con información del usuario o None si falla autenticación

    Note:
        En desarrollo, retorna usuario dummy si auth está deshabilitado
    """
    if not settings.enable_auth_routes:
        # Auth deshabilitado - retornar usuario dummy para desarrollo
        logger.warning("🔓 Autenticación deshabilitada - modo desarrollo")
        return {
            "username": username,
            "default_scopes": list(SYSTEM_SCOPES.keys())
        }

    user = SYSTEM_USERS.get(username)
    if not user:
        logger.warning(f"👤 Usuario no encontrado: {username}")
        return None

    # En producción, usar hashing de contraseñas apropiado
    if user["password"] != password:
        logger.warning(f"🔒 Contraseña inválida para usuario: {username}")
        return None

    logger.info(f"✅ Usuario autenticado: {username}")
    return {
        "username": username,
        "default_scopes": user["default_scopes"]
    }

def create_access_token(subject: str, scopes: List[str], expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    """
    Crear token de acceso JWT con scopes incluidos.

    Args:
        subject: Identificador del usuario (username)
        scopes: Lista de scopes autorizados
        expires_minutes: Minutos hasta expiración

    Returns:
        Token JWT firmado
    """
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode = {
        "sub": subject,
        "scopes": scopes,
        "exp": expire,
        "iat": datetime.utcnow(),
        "token_type": "access",
        "jti": f"{subject}_{datetime.utcnow().timestamp()}"
    }

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.debug(f"🎫 Token de acceso creado para {subject} con scopes: {scopes}")
    return encoded_jwt

def create_refresh_token(subject: str, scopes: List[str]) -> str:
    """
    Crear token de refresco con validez extendida.

    Args:
        subject: Identificador del usuario
        scopes: Scopes autorizados

    Returns:
        Token de refresco JWT
    """
    expire = datetime.utcnow() + timedelta(days=7)  # 7 días
    to_encode = {
        "sub": subject,
        "scopes": scopes,
        "exp": expire,
        "iat": datetime.utcnow(),
        "token_type": "refresh",
        "jti": f"refresh_{subject}_{datetime.utcnow().timestamp()}"
    }

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.debug(f"🔄 Token de refresco creado para {subject}")
    return encoded_jwt

def decode_token(token: str) -> DecodeTokenResult:
    """
    Decodificar y validar token JWT.

    Args:
        token: Token JWT a decodificar

    Returns:
        Payload decodificado del token

    Raises:
        HTTPException: Si el token es inválido
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("⏰ Token expirado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado"
        )
    except jwt.InvalidTokenError:
        logger.warning("🚫 Token inválido")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

def require_scopes(required_scopes: List[str]):
    """
    Dependencia para requerir scopes específicos en endpoints.

    Args:
        required_scopes: Lista de scopes requeridos

    Returns:
        Función de dependencia para FastAPI

    Raises:
        HTTPException: Si scopes insuficientes
    """
    async def scope_dependency(token: str = Depends(security)) -> Dict[str, Any]:
        payload = decode_token(token.credentials)

        user_scopes = set(payload.get("scopes", []))
        required_set = set(required_scopes)

        if not required_set.issubset(user_scopes):
            missing = required_set - user_scopes
            logger.warning(f"🚷 Scopes insuficientes. Faltan: {missing}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Scopes insuficientes. Requiere: {required_scopes}"
            )

        return payload

    return scope_dependency

# ========== ENDPOINTS DE LA API ==========

@router.get(
    "/system/info",
    summary="📊 Obtener información del sistema de autenticación",
    response_model=SystemInfo,
    responses={
        200: {"description": "Información del sistema retornada exitosamente"},
        500: {"description": "Error interno del servidor"}
    }
)
async def get_system_info() -> SystemInfo:
    """
    Obtener información completa del sistema de autenticación.

    Retorna todos los scopes disponibles, configuración de tokens,
    y parámetros de seguridad del sistema AXIOM v4.1.

    **Autenticación:** No requerida (información pública del sistema)

    **Respuesta:**
    - Lista completa de scopes con descripciones
    - Tiempo de expiración de access tokens
    - Tiempo de expiración de refresh tokens

    **Ejemplo de respuesta:**
    ```json
    {
        "scopes_available": [
            {
                "scope": "system:admin",
                "description": "Acceso administrativo completo al sistema AXIOM"
            }
        ],
        "token_expires_in_minutes": 30,
        "refresh_token_expires_in_minutes": 10080
    }
    ```

    **Logging:** Operación registrada como INFO
    """
    logger.info("📊 Información del sistema de autenticación solicitada")

    scopes_info = [
        ScopeInfo(scope=scope, description=desc)
        for scope, desc in SYSTEM_SCOPES.items()
    ]

    return SystemInfo(
        scopes_available=scopes_info,
        token_expires_in_minutes=settings.access_token_expire_minutes,
        refresh_token_expires_in_minutes=settings.access_token_expire_minutes * 24 * 7  # 7 días
    )

@router.post(
    "/token",
    summary="🔑 Obtener tokens de acceso y refresco",
    response_model=TokenResponse,
    responses={
        200: {"description": "Tokens generados exitosamente"},
        400: {"description": "Tipo de grant no soportado"},
        401: {"description": "Credenciales inválidas"},
        422: {"description": "Datos de entrada inválidos"}
    }
)
async def create_token(
    username: str = Form(..., description="Nombre de usuario del sistema"),
    password: str = Form(..., description="Contraseña del usuario"),
    scope: str = Form(default="", description="Scopes solicitados (opcional)"),
    grant_type: str = Form(default="password", description="Tipo de grant OAuth2")
) -> TokenResponse:
    """
    Endpoint OAuth2 compatible para obtener tokens de acceso.

    Autentica al usuario y genera tokens JWT con los scopes apropiados
    según el rol del usuario en el sistema AXIOM v4.1.

    **Autenticación:** Credenciales de usuario vía form-data

    **Parámetros:**
    - **username:** Nombre de usuario registrado
    - **password:** Contraseña correspondiente
    - **scope:** Scopes específicos solicitados (opcional)
    - **grant_type:** Tipo de grant (debe ser "password")

    **Proceso:**
    1. ✅ Validación de credenciales
    2. 🔍 Determinación de scopes disponibles
    3. 🎫 Generación de access token
    4. 🔄 Generación de refresh token
    5. 📊 Logging de la operación

    **Ejemplo de uso:**
    ```bash
    curl -X POST "http://localhost:8000/auth/token" 
         -d "username=researcher&password=research_secret&grant_type=password"
    ```

    **Respuesta exitosa:**
    ```json
    {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "token_type": "bearer",
        "expires_in": 1800,
        "scope": "system:read research:execute",
        "issued_at": "2024-01-15T10:30:00Z"
    }
    ```

    **Manejo de errores:**
    - `400`: Grant type no soportado
    - `401`: Credenciales inválidas
    - `422`: Datos de entrada malformados

    **Logging:** Operación completa registrada con resultado
    **Seguridad:** Validación de scopes y logging de accesos
    """
    if grant_type != "password":
        logger.warning(f"🚫 Grant type no soportado: {grant_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported grant type"
        )

    # Autenticar usuario
    user = authenticate_user(username, password)
    if not user:
        logger.warning(f"🚷 Intento de autenticación fallido para usuario: {username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Procesar scopes solicitados
    requested_scopes = [s.strip() for s in scope.split() if s.strip()]
    if not requested_scopes:
        requested_scopes = user.get("default_scopes", [])

    # Validar y filtrar scopes
    valid_scopes = []
    user_allowed_scopes = set(user.get("default_scopes", []))

    for requested_scope in requested_scopes:
        if requested_scope in SYSTEM_SCOPES and requested_scope in user_allowed_scopes:
            valid_scopes.append(requested_scope)
        else:
            logger.warning(f"⚠️ Scope no disponible para usuario {username}: {requested_scope}")

    # Generar tokens
    access_token = create_access_token(
        subject=username,
        scopes=valid_scopes,
        expires_minutes=settings.access_token_expire_minutes
    )

    refresh_token = create_refresh_token(
        subject=username,
        scopes=valid_scopes
    )

    logger.info(f"🎫 Tokens emitidos para usuario {username} con scopes: {valid_scopes}")

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        scope=" ".join(valid_scopes),
        issued_at=datetime.utcnow().isoformat()
    )

@router.post(
    "/refresh",
    summary="🔄 Refrescar token de acceso",
    response_model=TokenResponse,
    responses={
        200: {"description": "Token refrescado exitosamente"},
        401: {"description": "Refresh token inválido"},
        422: {"description": "Datos de entrada inválidos"}
    }
)
async def refresh_access_token(request: RefreshRequest) -> TokenResponse:
    """
    Refrescar token de acceso usando un refresh token válido.

    Genera un nuevo access token manteniendo los mismos scopes,
    extendiendo la sesión del usuario sin requerir re-autenticación.

    **Autenticación:** No requerida (usa refresh token en body)

    **Parámetros:**
    - **refresh_token:** Token de refresco válido y no expirado

    **Proceso:**
    1. 🔍 Validación del refresh token
    2. 👤 Extracción de información del usuario
    3. 🎫 Generación de nuevo access token
    4. 📊 Logging de la operación

    **Ejemplo de uso:**
    ```bash
    curl -X POST "http://localhost:8000/auth/refresh" 
         -H "Content-Type: application/json" 
         -d '{"refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."}'
    ```

    **Respuesta exitosa:**
    ```json
    {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "token_type": "bearer",
        "expires_in": 1800,
        "scope": "system:read research:execute",
        "issued_at": "2024-01-15T11:00:00Z"
    }
    ```

    **Manejo de errores:**
    - `401`: Refresh token inválido o expirado
    - `422`: Datos de entrada malformados

    **Logging:** Operación registrada con resultado
    **Seguridad:** Validación completa del refresh token
    """
    try:
        # Decodificar refresh token
        payload = decode_token(request.refresh_token)

        # Validar que es un refresh token
        if payload.get("token_type") != "refresh":
            logger.warning("🚫 Token proporcionado no es de tipo refresh")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de refresco inválido"
            )

        username = payload.get("sub")
        if not username:
            logger.error("🚫 Payload del token incompleto - falta subject")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Payload del token inválido"
            )

        scopes = payload.get("scopes", [])

        # Generar nuevo access token
        access_token = create_access_token(
            subject=username,
            scopes=scopes,
            expires_minutes=settings.access_token_expire_minutes
        )

        logger.info(f"🔄 Access token refrescado para usuario {username}")

        return TokenResponse(
            access_token=access_token,
            refresh_token=request.refresh_token,  # Mantener mismo refresh token
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            scope=" ".join(scopes),
            issued_at=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except BiologyError as e:
        logger.error(f"💥 Error al refrescar token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de refresco inválido"
        )

@router.post(
    "/revoke",
    summary="🚫 Revocar tokens",
    responses={
        200: {"description": "Token revocado exitosamente"},
        401: {"description": "Token de autenticación inválido"},
        403: {"description": "Scopes insuficientes"},
        422: {"description": "Datos de entrada inválidos"}
    }
)
async def revoke_token(
    token: str = Form(..., description="Token a revocar"),
    token_type_hint: str = Form(default="access_token", description="Tipo de token (access_token/refresh_token)"),
    current_user: Dict[str, Any] = Depends(require_scopes(["system:read"]))
) -> Dict[str, str]:
    """
    Revocar un token de acceso o refresco.

    En un sistema de producción, esto agregaría el token a una lista negra
    para prevenir su uso futuro. Actualmente solo registra la revocación.

    **Autenticación:** Token válido con scope "system:read"

    **Parámetros:**
    - **token:** Token a revocar
    - **token_type_hint:** Tipo de token (access_token o refresh_token)

    **Proceso:**
    1. 🔐 Validación de autenticación del solicitante
    2. 📝 Registro de la revocación
    3. ✅ Confirmación de operación

    **Ejemplo de uso:**
    ```bash
    curl -X POST "http://localhost:8000/auth/revoke" 
         -H "Authorization: Bearer <access_token>" 
         -d "token=<token_to_revoke>&token_type_hint=access_token"
    ```

    **Respuesta exitosa:**
    ```json
    {
        "message": "Token revocado exitosamente"
    }
    ```

    **Manejo de errores:**
    - `401`: Token de autenticación inválido
    - `403`: Scopes insuficientes
    - `422`: Datos de entrada malformados

    **Logging:** Operación registrada con usuario solicitante
    **Seguridad:** Requiere autenticación y scopes apropiados
    """
    # En un sistema de producción, se mantendría una lista negra de tokens
    # Por ahora, solo registrar la revocación
    logger.info(f"🚫 Revocación de token solicitada por {current_user.get('sub')} para tipo {token_type_hint}")

    return {"message": "Token revocado exitosamente"}

@router.get(
    "/verify",
    summary="✅ Verificar token y obtener información de usuario",
    response_model=UserVerification,
    responses={
        200: {"description": "Token válido - información retornada"},
        401: {"description": "Token inválido o expirado"},
        422: {"description": "Datos de entrada inválidos"}
    }
)
async def verify_token(
    current_user: Dict[str, Any] = Depends(require_scopes([]))
) -> Dict[str, Any]:
    """
    Verificar la validez del token actual y retornar información del usuario.

    Endpoint útil para verificar sesiones activas y obtener información
    detallada del usuario autenticado y sus permisos.

    **Autenticación:** Token válido (cualquier scope)

    **Proceso:**
    1. 🔍 Validación del token proporcionado
    2. 👤 Extracción de información del usuario
    3. 📊 Retorno de datos de verificación

    **Ejemplo de uso:**
    ```bash
    curl -X GET "http://localhost:8000/auth/verify" 
         -H "Authorization: Bearer <access_token>"
    ```

    **Respuesta exitosa:**
    ```json
    {
        "valid": true,
        "user": "researcher",
        "scopes": ["system:read", "research:execute"],
        "expires": 1705320000,
        "issued_at": 1705318200,
        "token_id": "researcher_1705318200.123456"
    }
    ```

    **Manejo de errores:**
    - `401`: Token inválido o expirado
    - `422`: Datos de entrada malformados

    **Logging:** Operación registrada como DEBUG
    **Seguridad:** Validación completa del token JWT
    """
    logger.debug(f"✅ Verificación de token para usuario: {current_user.get('sub')}")

    return {
        "valid": True,
        "user": current_user.get("sub"),
        "scopes": current_user.get("scopes", []),
        "expires": current_user.get("exp"),
        "issued_at": current_user.get("iat"),
        "token_id": current_user.get("jti")
    }

# ========== DEPENDENCIAS DE CONVENIENCIA ==========

def require_system_admin():
    """
    Requerir acceso administrativo completo al sistema.

    **Scopes requeridos:** system:admin

    **Uso:**
    ```python
    @router.get("/admin/config")
    async def get_admin_config(user=Depends(require_system_admin())):
        # Solo accesible para administradores
        pass
    ```
    """
    return require_scopes(["system:admin"])

def require_research_access():
    """
    Requerir acceso para ejecución de investigación científica.

    **Scopes requeridos:** research:execute

    **Uso típico:** Endpoints de experimentos y análisis
    """
    return require_scopes(["research:execute"])

def require_lab_access():
    """
    Requerir acceso a equipos de laboratorio.

    **Scopes requeridos:** lab:equipment

    **Uso típico:** Control de instrumentos y equipos
    """
    return require_scopes(["lab:equipment"])

def require_scheduler_access():
    """
    Requerir acceso a políticas de scheduling.

    **Scopes requeridos:** scheduler:policy

    **Uso típico:** Configuración de scheduling avanzado
    """
    return require_scopes(["scheduler:policy"])

def require_agent_orchestration():
    """
    Requerir acceso a orquestación de agentes multi-modales.

    **Scopes requeridos:** agent:orchestrate

    **Uso típico:** Coordinación de agentes IA
    """
    return require_scopes(["agent:orchestrate"])

def require_knowledge_write():
    """
    Requerir acceso de escritura al grafo de conocimiento.

    **Scopes requeridos:** knowledge:write

    **Uso típico:** Modificación de conocimiento científico
    """
    return require_scopes(["knowledge:write"])
