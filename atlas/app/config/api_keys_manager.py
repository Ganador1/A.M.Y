"""
AXIOM API Keys Manager
Gestión segura de API keys para proveedores cloud (Hugging Face, Groq, OpenAI, etc.)
usando el SecretsManager con cifrado Fernet
"""

import os
import logging
from typing import Optional, Dict, List
from pathlib import Path
import json

from app.config.secrets_manager import SecretsManager, create_secrets_manager

logger = logging.getLogger(__name__)


class APIKeysManager:
    """
    Gestor centralizado y seguro de API keys para proveedores cloud

    Características:
    - Cifrado con Fernet (AES-128)
    - Almacenamiento seguro en archivo cifrado
    - Fallback a variables de entorno
    - Rotación de claves
    - Audit log
    """

    # Proveedores soportados
    SUPPORTED_PROVIDERS = [
        "HUGGINGFACE",
        "OPENAI",
        "ANTHROPIC",
        "GROQ",
        "TOGETHER",
        "COHERE",
        "REPLICATE",
        "GOOGLE_AI",
        "AWS_BEDROCK",
        "AZURE_OPENAI",
        "OLLAMA"
    ]

    def __init__(
        self,
        secrets_manager: Optional[SecretsManager] = None,
        storage_file: str = ".api_keys.enc",
        enable_env_fallback: bool = True
    ):
        """
        Inicializa el gestor de API keys

        Args:
            secrets_manager: Instancia de SecretsManager (se crea una si no se provee)
            storage_file: Archivo para almacenar API keys cifradas
            enable_env_fallback: Si hacer fallback a variables de entorno
        """
        self.secrets_manager = secrets_manager or create_secrets_manager()
        self.storage_file = Path(storage_file)
        self.enable_env_fallback = enable_env_fallback
        self._api_keys: Dict[str, str] = {}

        # Cargar API keys existentes
        self._load_api_keys()

        logger.info(f"🔐 APIKeysManager inicializado ({len(self._api_keys)} keys cargadas)")

    def _load_api_keys(self):
        """Carga API keys desde el archivo cifrado"""
        if not self.storage_file.exists():
            logger.info("No hay archivo de API keys cifrado. Usando configuración inicial.")
            return

        try:
            with open(self.storage_file, 'r') as f:
                encrypted_data = json.load(f)

            # Descifrar cada API key
            for provider, encrypted_key in encrypted_data.items():
                try:
                    decrypted = self.secrets_manager.decrypt_secret(encrypted_key)
                    self._api_keys[provider] = decrypted
                except Exception as e:
                    logger.error(f"Error descifrando API key para {provider}: {e}")

            logger.info(f"✅ Cargadas {len(self._api_keys)} API keys desde archivo cifrado")

        except Exception as e:
            logger.error(f"Error cargando API keys: {e}")

    def _save_api_keys(self):
        """Guarda API keys en archivo cifrado"""
        try:
            encrypted_data = {}

            for provider, api_key in self._api_keys.items():
                encrypted_data[provider] = self.secrets_manager.encrypt_secret(
                    f"api_key_{provider.lower()}",
                    api_key
                )

            # Guardar archivo cifrado
            with open(self.storage_file, 'w') as f:
                json.dump(encrypted_data, f, indent=2)

            # Permisos restrictivos
            os.chmod(self.storage_file, 0o600)

            logger.info(f"💾 Guardadas {len(encrypted_data)} API keys de forma segura")

        except Exception as e:
            logger.error(f"Error guardando API keys: {e}")
            raise

    def set_api_key(self, provider: str, api_key: str, save: bool = True):
        """
        Establece una API key para un proveedor

        Args:
            provider: Nombre del proveedor (ej: 'HUGGINGFACE')
            api_key: API key a almacenar
            save: Si guardar inmediatamente en archivo cifrado
        """
        provider_upper = provider.upper()

        if provider_upper not in self.SUPPORTED_PROVIDERS:
            logger.warning(
                f"Proveedor '{provider}' no está en la lista de soportados. "
                f"Soportados: {', '.join(self.SUPPORTED_PROVIDERS)}"
            )

        # Validar formato básico
        if not api_key or len(api_key) < 10:
            raise ValueError(f"API key inválida para {provider}")

        self._api_keys[provider_upper] = api_key
        logger.info(f"✅ API key configurada para {provider_upper}")

        if save:
            self._save_api_keys()

    def get_api_key(self, provider: str, fallback_env: bool = True) -> Optional[str]:
        """
        Obtiene una API key para un proveedor

        Args:
            provider: Nombre del proveedor
            fallback_env: Si hacer fallback a variable de entorno

        Returns:
            API key o None si no existe
        """
        provider_upper = provider.upper()

        # 1. Intentar desde almacenamiento cifrado
        if provider_upper in self._api_keys:
            return self._api_keys[provider_upper]

        # 2. Fallback a variable de entorno
        if fallback_env and self.enable_env_fallback:
            env_var = f"{provider_upper}_API_KEY"
            env_value = os.getenv(env_var)

            if env_value:
                logger.info(f"📥 Usando API key de variable de entorno: {env_var}")
                # Opcionalmente, guardar para próximas veces
                # self.set_api_key(provider, env_value, save=True)
                return env_value

        logger.warning(f"⚠️ No se encontró API key para {provider_upper}")
        return None

    def has_api_key(self, provider: str) -> bool:
        """Verifica si existe una API key para un proveedor"""
        return self.get_api_key(provider) is not None

    def remove_api_key(self, provider: str, save: bool = True):
        """
        Elimina una API key

        Args:
            provider: Nombre del proveedor
            save: Si guardar cambios inmediatamente
        """
        provider_upper = provider.upper()

        if provider_upper in self._api_keys:
            del self._api_keys[provider_upper]
            logger.info(f"🗑️ API key eliminada para {provider_upper}")

            if save:
                self._save_api_keys()
            return True

        return False

    def list_providers(self) -> List[Dict[str, any]]:
        """
        Lista proveedores y su estado

        Returns:
            Lista de proveedores con información de estado
        """
        providers_info = []

        for provider in self.SUPPORTED_PROVIDERS:
            has_key = self.has_api_key(provider)
            api_key = self.get_api_key(provider) if has_key else None

            # Maskear API key para mostrar
            masked_key = None
            if api_key:
                if len(api_key) > 10:
                    masked_key = api_key[:8] + "..." + api_key[-4:]
                else:
                    masked_key = api_key[:4] + "..."

            providers_info.append({
                "provider": provider,
                "configured": has_key,
                "masked_key": masked_key,
                "source": "encrypted" if provider in self._api_keys else "env" if has_key else None
            })

        return providers_info

    def rotate_encryption_key(self, new_password: Optional[str] = None):
        """
        Rota la clave de cifrado

        ADVERTENCIA: Esto requiere descifrar y volver a cifrar todas las API keys

        Args:
            new_password: Nueva contraseña para la clave de cifrado
        """
        logger.warning("🔄 Iniciando rotación de clave de cifrado...")

        # Guardar API keys desencriptadas temporalmente
        temp_api_keys = self._api_keys.copy()

        # Rotar clave del SecretsManager
        self.secrets_manager.rotate_key(new_password)

        # Re-cifrar y guardar
        self._api_keys = temp_api_keys
        self._save_api_keys()

        logger.info("✅ Clave de cifrado rotada exitosamente")

    def import_from_env(self, save: bool = True) -> int:
        """
        Importa API keys desde variables de entorno

        Args:
            save: Si guardar en archivo cifrado

        Returns:
            Número de keys importadas
        """
        imported = 0

        for provider in self.SUPPORTED_PROVIDERS:
            env_var = f"{provider}_API_KEY"
            env_value = os.getenv(env_var)

            if env_value and provider not in self._api_keys:
                self.set_api_key(provider, env_value, save=False)
                imported += 1
                logger.info(f"📥 Importada API key para {provider} desde {env_var}")

        if save and imported > 0:
            self._save_api_keys()

        logger.info(f"✅ Importadas {imported} API keys desde variables de entorno")
        return imported

    def export_to_env_example(self, output_file: str = ".env.example") -> str:
        """
        Genera un archivo .env.example con las API keys configuradas

        Args:
            output_file: Archivo de salida

        Returns:
            Contenido generado
        """
        lines = [
            "# API Keys Configuration for AXIOM Atlas",
            "# Copy this file to .env and fill in your actual API keys",
            "",
            "# ============================================================",
            "# CLOUD AI PROVIDERS",
            "# ============================================================",
            ""
        ]

        for provider_info in self.list_providers():
            provider = provider_info["provider"]
            configured = provider_info["configured"]

            env_var = f"{provider}_API_KEY"

            if configured:
                lines.append(f"# ✅ Configured")
                lines.append(f"{env_var}=your_{provider.lower()}_api_key_here")
            else:
                lines.append(f"# ❌ Not configured")
                lines.append(f"# {env_var}=your_{provider.lower()}_api_key_here")

            lines.append("")

        content = "\n".join(lines)

        # Guardar archivo
        with open(output_file, 'w') as f:
            f.write(content)

        logger.info(f"📄 Generado {output_file}")
        return content

    def get_stats(self) -> Dict[str, any]:
        """Obtiene estadísticas del gestor de API keys"""
        providers_info = self.list_providers()
        configured_count = sum(1 for p in providers_info if p["configured"])

        return {
            "total_providers": len(self.SUPPORTED_PROVIDERS),
            "configured_providers": configured_count,
            "unconfigured_providers": len(self.SUPPORTED_PROVIDERS) - configured_count,
            "storage_file": str(self.storage_file),
            "storage_exists": self.storage_file.exists(),
            "env_fallback_enabled": self.enable_env_fallback,
            "providers": providers_info
        }


# Instancia global del gestor de API keys
_api_keys_manager: Optional[APIKeysManager] = None


def get_api_keys_manager() -> APIKeysManager:
    """
    Obtiene la instancia global del APIKeysManager (Singleton)

    Returns:
        Instancia del APIKeysManager
    """
    global _api_keys_manager

    if _api_keys_manager is None:
        _api_keys_manager = APIKeysManager()

    return _api_keys_manager


def get_api_key(provider: str) -> Optional[str]:
    """
    Función de conveniencia para obtener una API key

    Args:
        provider: Nombre del proveedor

    Returns:
        API key o None
    """
    manager = get_api_keys_manager()
    return manager.get_api_key(provider)


# Exportar funciones principales
__all__ = [
    "APIKeysManager",
    "get_api_keys_manager",
    "get_api_key"
]
