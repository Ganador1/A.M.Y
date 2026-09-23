"""
AXIOM Secrets Management
Gestión segura de secretos usando cifrado con Fernet
"""

import os
import base64
from pathlib import Path
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import secrets

class SecretsManager:
    """
    Gestor de secretos para AXIOM usando cifrado Fernet
    """
    
    def __init__(self, key_file: str = ".secrets.key", password: Optional[str] = None):
        """
        Inicializa el gestor de secretos
        
        Args:
            key_file: Archivo donde se almacena la clave de cifrado
            password: Contraseña para derivar la clave (opcional)
        """
        self.key_file = Path(key_file)
        self.cipher = None
        self._initialize_cipher(password)
    
    def _initialize_cipher(self, password: Optional[str] = None):
        """Inicializa el cifrador Fernet"""
        if self.key_file.exists():
            # Cargar clave existente
            with open(self.key_file, 'rb') as f:
                key = f.read()
        else:
            # Generar nueva clave
            if password:
                # Derivar clave desde contraseña
                salt = os.urandom(16)
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                )
                key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            else:
                # Generar clave aleatoria
                key = Fernet.generate_key()
            
            # Guardar clave
            with open(self.key_file, 'wb') as f:
                f.write(key)
            
            # Establecer permisos restrictivos
            os.chmod(self.key_file, 0o600)
        
        self.cipher = Fernet(key)
    
    def encrypt(self, value: str) -> bytes:
        """
        Cifra un valor
        
        Args:
            value: Valor a cifrar
            
        Returns:
            Valor cifrado como bytes
        """
        if not self.cipher:
            raise RuntimeError("Cipher no inicializado")
        
        return self.cipher.encrypt(value.encode())
    
    def decrypt(self, encrypted_value: bytes) -> str:
        """
        Descifra un valor
        
        Args:
            encrypted_value: Valor cifrado
            
        Returns:
            Valor descifrado como string
        """
        if not self.cipher:
            raise RuntimeError("Cipher no inicializado")
        
        return self.cipher.decrypt(encrypted_value).decode()
    
    def encrypt_secret(self, key: str, value: str) -> Dict[str, Any]:
        """
        Cifra un secreto y retorna metadatos
        
        Args:
            key: Clave del secreto
            value: Valor a cifrar
            
        Returns:
            Diccionario con metadatos del secreto cifrado
        """
        encrypted = self.encrypt(value)
        
        return {
            'key': key,
            'encrypted_value': base64.b64encode(encrypted).decode(),
            'algorithm': 'fernet',
            'created_at': str(Path().cwd()),  # Timestamp simplificado
        }
    
    def decrypt_secret(self, secret_data: Dict[str, Any]) -> str:
        """
        Descifra un secreto desde metadatos
        
        Args:
            secret_data: Metadatos del secreto
            
        Returns:
            Valor descifrado
        """
        encrypted_bytes = base64.b64decode(secret_data['encrypted_value'])
        return self.decrypt(encrypted_bytes)
    
    def rotate_key(self, new_password: Optional[str] = None):
        """
        Rota la clave de cifrado (requiere descifrar y volver a cifrar todos los secretos)
        """
        # Esta implementación requeriría acceso a todos los secretos existentes
        # Por simplicidad, generamos una nueva clave
        if self.key_file.exists():
            self.key_file.unlink()
        
        self._initialize_cipher(new_password)
    
    def get_key_info(self) -> Dict[str, Any]:
        """
        Obtiene información sobre la clave de cifrado
        
        Returns:
            Información de la clave
        """
        return {
            'key_file': str(self.key_file),
            'key_exists': self.key_file.exists(),
            'key_size': self.key_file.stat().st_size if self.key_file.exists() else 0,
            'algorithm': 'fernet',
        }

class SecureSettings:
    """
    Configuración segura que integra SecretsManager con Settings
    """
    
    def __init__(self, secrets_manager: Optional[SecretsManager] = None):
        self.secrets_manager = secrets_manager or SecretsManager()
        self._encrypted_secrets: Dict[str, Dict[str, Any]] = {}
    
    def set_secret(self, key: str, value: str):
        """
        Establece un secreto cifrado
        
        Args:
            key: Clave del secreto
            value: Valor a cifrar
        """
        self._encrypted_secrets[key] = self.secrets_manager.encrypt_secret(key, value)
    
    def get_secret(self, key: str) -> Optional[str]:
        """
        Obtiene un secreto descifrado
        
        Args:
            key: Clave del secreto
            
        Returns:
            Valor descifrado o None si no existe
        """
        if key not in self._encrypted_secrets:
            return None
        
        try:
            return self.secrets_manager.decrypt_secret(self._encrypted_secrets[key])
        except Exception as e:
            print(f"Error descifrando secreto {key}: {e}")
            return None
    
    def list_secrets(self) -> list[str]:
        """
        Lista todas las claves de secretos
        
        Returns:
            Lista de claves de secretos
        """
        return list(self._encrypted_secrets.keys())
    
    def remove_secret(self, key: str) -> bool:
        """
        Elimina un secreto
        
        Args:
            key: Clave del secreto
            
        Returns:
            True si se eliminó exitosamente
        """
        if key in self._encrypted_secrets:
            del self._encrypted_secrets[key]
            return True
        return False

def create_secrets_manager() -> SecretsManager:
    """
    Factory function para crear SecretsManager con configuración por defecto
    """
    # Usar variable de entorno para la contraseña si está disponible
    password = os.getenv('AXIOM_SECRETS_PASSWORD')
    
    return SecretsManager(password=password)

def demo_secrets_management():
    """
    Demostración del uso de SecretsManager
    """
    print("🔐 Demostración de Secrets Management...")
    print("=" * 50)
    
    # Crear gestor de secretos
    secrets_manager = create_secrets_manager()
    
    # Información de la clave
    key_info = secrets_manager.get_key_info()
    print(f"📁 Archivo de clave: {key_info['key_file']}")
    print(f"🔑 Clave existe: {key_info['key_exists']}")
    print(f"📏 Tamaño de clave: {key_info['key_size']} bytes")
    
    # Crear configuración segura
    secure_settings = SecureSettings(secrets_manager)
    
    # Establecer algunos secretos de ejemplo
    test_secrets = {
        'api_key_openai': 'sk-test-openai-key-12345',
        'api_key_google': 'AIza-test-google-key-67890',
        'database_password': 'super-secret-db-password',
    }
    
    print(f"\n🔒 Cifrando {len(test_secrets)} secretos...")
    for key, value in test_secrets.items():
        secure_settings.set_secret(key, value)
        print(f"   ✓ {key}")
    
    # Listar secretos
    print(f"\n📋 Secretos disponibles: {secure_settings.list_secrets()}")
    
    # Descifrar y mostrar (solo las primeras 10 caracteres por seguridad)
    print(f"\n🔓 Descifrando secretos (mostrando solo primeros 10 caracteres):")
    for key in secure_settings.list_secrets():
        decrypted = secure_settings.get_secret(key)
        if decrypted:
            masked = decrypted[:10] + "..." if len(decrypted) > 10 else decrypted
            print(f"   - {key}: {masked}")
    
    print(f"\n✅ Demostración completada exitosamente!")

if __name__ == "__main__":
    demo_secrets_management()
