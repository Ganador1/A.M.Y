"""
Input Sanitization Module - AXIOM ATLAS
=======================================

Módulo de sanitización de inputs para prevenir ataques de inyección.
Implementa validación y limpieza de datos de entrada del usuario.

Author: AXIOM Team
Date: 2025-01-01
Version: 1.0.0
"""

import bleach
import re
import html
import urllib.parse
from typing import Any, Optional, Union, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class InputSanitizer:
    """Sanitiza inputs del usuario para prevenir ataques de inyección"""

    # Tags HTML permitidos para contenido seguro
    ALLOWED_HTML_TAGS = [
        'p', 'br', 'strong', 'em', 'ul', 'li', 'ol', 'h1', 'h2', 'h3', 
        'h4', 'h5', 'h6', 'blockquote', 'code', 'pre'
    ]
    
    # Atributos HTML permitidos
    ALLOWED_HTML_ATTRIBUTES = {
        'a': ['href', 'title'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
        'blockquote': ['cite']
    }
    
    # Comandos shell permitidos (whitelist muy restrictivo)
    ALLOWED_SHELL_COMMANDS = [
        'ls', 'cat', 'grep', 'head', 'tail', 'wc', 'sort', 'uniq'
    ]
    
    # Patrones de validación
    SQL_IDENTIFIER_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
    PATH_PATTERN = re.compile(r'^[a-zA-Z0-9_./-]+$')
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')

    @staticmethod
    def sanitize_html(text: str) -> str:
        """Remover tags HTML peligrosos y sanitizar contenido"""
        if not isinstance(text, str):
            return str(text)
        
        # Limpiar HTML usando bleach
        cleaned = bleach.clean(
            text, 
            tags=InputSanitizer.ALLOWED_HTML_TAGS,
            attributes=InputSanitizer.ALLOWED_HTML_ATTRIBUTES,
            strip=True
        )
        
        # Escapar caracteres HTML restantes
        return html.escape(cleaned, quote=True)

    @staticmethod
    def sanitize_sql_identifier(identifier: str) -> str:
        """Validar identificadores SQL (nombres de tabla/columna)"""
        if not isinstance(identifier, str):
            raise ValueError(f"SQL identifier must be string, got {type(identifier)}")
        
        if not InputSanitizer.SQL_IDENTIFIER_PATTERN.match(identifier):
            raise ValueError(f"Invalid SQL identifier: {identifier}")
        
        return identifier

    @staticmethod
    def sanitize_path(path: str) -> str:
        """Prevenir path traversal attacks"""
        if not isinstance(path, str):
            raise ValueError(f"Path must be string, got {type(path)}")
        
        # Normalizar path
        normalized = Path(path).resolve()
        
        # Verificar path traversal
        if '..' in str(normalized) or normalized.is_absolute():
            raise ValueError(f"Invalid path: {path}")
        
        # Validar caracteres permitidos
        if not InputSanitizer.PATH_PATTERN.match(path):
            raise ValueError(f"Path contains invalid characters: {path}")
        
        return str(normalized)

    @staticmethod
    def sanitize_command(cmd: str) -> str:
        """Validar comandos shell (whitelist muy restrictivo)"""
        if not isinstance(cmd, str):
            raise ValueError(f"Command must be string, got {type(cmd)}")
        
        # Dividir comando en partes
        parts = cmd.strip().split()
        if not parts:
            raise ValueError("Empty command")
        
        command = parts[0]
        
        # Verificar si comando está en whitelist
        if command not in InputSanitizer.ALLOWED_SHELL_COMMANDS:
            raise ValueError(f"Command not allowed: {command}")
        
        # Validar argumentos (solo caracteres seguros)
        for part in parts[1:]:
            if not re.match(r'^[a-zA-Z0-9_./-]+$', part):
                raise ValueError(f"Invalid command argument: {part}")
        
        return cmd

    @staticmethod
    def sanitize_email(email: str) -> str:
        """Validar formato de email"""
        if not isinstance(email, str):
            raise ValueError(f"Email must be string, got {type(email)}")
        
        email = email.strip().lower()
        
        if not InputSanitizer.EMAIL_PATTERN.match(email):
            raise ValueError(f"Invalid email format: {email}")
        
        return email

    @staticmethod
    def sanitize_uuid(uuid_str: str) -> str:
        """Validar formato UUID"""
        if not isinstance(uuid_str, str):
            raise ValueError(f"UUID must be string, got {type(uuid_str)}")
        
        uuid_str = uuid_str.strip().lower()
        
        if not InputSanitizer.UUID_PATTERN.match(uuid_str):
            raise ValueError(f"Invalid UUID format: {uuid_str}")
        
        return uuid_str

    @staticmethod
    def sanitize_url(url: str) -> str:
        """Validar y sanitizar URLs"""
        if not isinstance(url, str):
            raise ValueError(f"URL must be string, got {type(url)}")
        
        # Parsear URL
        parsed = urllib.parse.urlparse(url)
        
        # Solo permitir HTTP/HTTPS
        if parsed.scheme not in ['http', 'https']:
            raise ValueError(f"Invalid URL scheme: {parsed.scheme}")
        
        # Reconstruir URL limpia
        clean_url = urllib.parse.urlunparse(parsed)
        
        return clean_url

    @staticmethod
    def sanitize_json_input(data: Any) -> Any:
        """Sanitizar datos JSON de entrada"""
        if isinstance(data, str):
            return InputSanitizer.sanitize_html(data)
        elif isinstance(data, dict):
            return {k: InputSanitizer.sanitize_json_input(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [InputSanitizer.sanitize_json_input(item) for item in data]
        else:
            return data

    @staticmethod
    def validate_file_upload(filename: str, allowed_extensions: List[str] = None) -> str:
        """Validar archivos subidos"""
        if not isinstance(filename, str):
            raise ValueError(f"Filename must be string, got {type(filename)}")
        
        # Limpiar nombre de archivo
        filename = Path(filename).name
        
        # Verificar extensión
        if allowed_extensions:
            ext = Path(filename).suffix.lower()
            if ext not in allowed_extensions:
                raise ValueError(f"File extension not allowed: {ext}")
        
        # Verificar caracteres peligrosos
        if not re.match(r'^[a-zA-Z0-9._-]+$', filename):
            raise ValueError(f"Filename contains invalid characters: {filename}")
        
        return filename


class SecurityValidator:
    """Validador de seguridad para datos de entrada"""
    
    @staticmethod
    def validate_experiment_input(data: dict) -> dict:
        """Validar input de experimentos"""
        if not isinstance(data, dict):
            raise ValueError("Experiment data must be a dictionary")
        
        # Sanitizar campos de texto
        if 'description' in data:
            data['description'] = InputSanitizer.sanitize_html(data['description'])
        
        if 'name' in data:
            data['name'] = InputSanitizer.sanitize_html(data['name'])
        
        if 'tags' in data and isinstance(data['tags'], list):
            data['tags'] = [InputSanitizer.sanitize_html(tag) for tag in data['tags']]
        
        return data
    
    @staticmethod
    def validate_user_input(data: dict) -> dict:
        """Validar input de usuario"""
        if not isinstance(data, dict):
            raise ValueError("User data must be a dictionary")
        
        # Sanitizar campos de usuario
        if 'email' in data:
            data['email'] = InputSanitizer.sanitize_email(data['email'])
        
        if 'username' in data:
            data['username'] = InputSanitizer.sanitize_html(data['username'])
        
        if 'full_name' in data:
            data['full_name'] = InputSanitizer.sanitize_html(data['full_name'])
        
        return data


# Decorador para sanitización automática
def sanitize_input(sanitizer_func):
    """Decorador para sanitizar inputs automáticamente"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Sanitizar argumentos posicionales
            sanitized_args = []
            for arg in args:
                if isinstance(arg, str):
                    sanitized_args.append(sanitizer_func(arg))
                else:
                    sanitized_args.append(arg)
            
            # Sanitizar argumentos de palabra clave
            sanitized_kwargs = {}
            for key, value in kwargs.items():
                if isinstance(value, str):
                    sanitized_kwargs[key] = sanitizer_func(value)
                else:
                    sanitized_kwargs[key] = value
            
            return func(*sanitized_args, **sanitized_kwargs)
        return wrapper
    return decorator
