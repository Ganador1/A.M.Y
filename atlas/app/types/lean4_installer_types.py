"""
TypedDict definitions for lean4_installer router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class DetectSystemInfoResult(TypedDict, total=False):
    """Detecta información del sistema para instalación"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class CheckSystemDependenciesResult(TypedDict, total=False):
    """Verifica dependencias del sistema"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class CheckCommandResult(TypedDict, total=False):
    """Verifica si un comando está disponible"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class CheckExistingInstallationResult(TypedDict, total=False):
    """Verifica si Lean4 ya está instalado"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class CheckMathlibInstallationResult(TypedDict, total=False):
    """Verifica el estado de mathlib"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class InstallLean4Result(TypedDict, total=False):
    """Instala Lean4 automáticamente"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class InstallElanResult(TypedDict, total=False):
    """Ejecuta la instalación de elan"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class SetupLeanToolchainResult(TypedDict, total=False):
    """Configura el toolchain de Lean"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class SetupMathlibResult(TypedDict, total=False):
    """Configura mathlib4 (opcional)"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class VerifyInstallationResult(TypedDict, total=False):
    """Verifica que la instalación fue exitosa"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class UninstallLean4Result(TypedDict, total=False):
    """Desinstala Lean4 completamente"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

