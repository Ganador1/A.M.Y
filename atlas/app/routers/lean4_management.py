"""
Router de Gestión Lean4 para AXIOM
==================================

Endpoints especializados para instalación, configuración, validación
y diagnóstico de Lean4 theorem prover.

Endpoints:
- GET /detect: Detectar instalación existente
- POST /install: Instalación asistida automática
- POST /validate: Validación completa de configuración
- POST /diagnose: Diagnóstico de errores específicos
- DELETE /uninstall: Desinstalación completa
- GET /system-info: Información del sistema

Autor: AXIOM Research Team
Fecha: Septiembre 2025
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.bootstrap_logging import logger
from app.services.lean4_installer import lean4_installer
from app.services.theorem_proving.lean4_integration import Lean4Service
from app.exceptions.domain.medicine import MedicalError
from app.types.lean4_management_types import (
    DetectLean4InstallationResult,
    InstallLean4AssistedResult,
    ValidateLean4ConfigurationResult,
    DiagnoseLean4ErrorResult,
    UninstallLean4Result,
    GetSystemInformationResult,
)

router = APIRouter(prefix="/api/lean4", tags=["lean4"])

# Global service instances
lean4_service = Lean4Service()


class InstallRequest(BaseModel):
    """Request para instalación de Lean4"""
    force_reinstall: bool = Field(False, description="Forzar reinstalación si ya existe")
    include_mathlib: bool = Field(True, description="Incluir configuración de mathlib")
    custom_elan_home: Optional[str] = Field(None, description="Directorio personalizado para elan")


class DiagnosisRequest(BaseModel):
    """Request para diagnóstico de errores"""
    error_message: str = Field(..., min_length=1, description="Mensaje de error a diagnosticar")
    context: Optional[str] = Field(None, description="Contexto adicional del error")
    include_system_info: bool = Field(True, description="Incluir información del sistema")


@router.get("/detect")
async def detect_lean4_installation() -> DetectLean4InstallationResult:
    """
    🔍 Detectar Instalación Existente de Lean4
    
    Verifica si Lean4 está instalado en el sistema y proporciona
    información detallada sobre la configuración actual.
    
    **Respuesta:**
    ```json
    {
        "system_info": {
            "os": "darwin",
            "architecture": "arm64",
            "shell": "/bin/zsh"
        },
        "installation_status": {
            "fully_installed": true,
            "lean_version": "Lean (version 4.0.0)",
            "elan_version": "elan 3.0.0",
            "mathlib": {
                "found": true,
                "path": "/Users/user/.elan/toolchains"
            }
        },
        "recommendations": [
            "✅ Configuración Lean4 está funcionando correctamente"
        ]
    }
    ```
    """
    try:
        logger.info("🔍 Detectando instalación de Lean4")
        
        # Información del sistema
        system_info = await lean4_installer.detect_system_info()
        
        # Estado de instalación
        installation_status = await lean4_installer.check_existing_installation()
        
        return {
            "detection_timestamp": system_info.get("timestamp", "unknown"),
            "system_info": system_info,
            "installation_status": installation_status,
            "is_supported_system": system_info.get("is_supported", False),
            "dependencies": system_info.get("dependencies", {}),
            "next_steps": [
                "Ejecutar /validate para verificación completa",
                "Usar /install si necesita instalación",
                "Consultar /system-info para detalles del sistema"
            ]
        }
        
    except MedicalError as e:
        logger.error(f"❌ Error detectando Lean4: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/install")
async def install_lean4_assisted(request: InstallRequest) -> InstallLean4AssistedResult:
    """
    🚀 Instalación Asistida de Lean4
    
    Ejecuta una instalación automática completa de Lean4 con elan,
    configuración de toolchain y verificación post-instalación.
    
    **Características:**
    - Detección automática de SO
    - Descarga e instalación de elan
    - Configuración de Lean 4 stable toolchain
    - Verificación post-instalación
    - Configuración opcional de mathlib
    
    **Respuesta:**
    ```json
    {
        "success": true,
        "message": "Lean4 instalado exitosamente",
        "steps_completed": {
            "elan_installation": {"success": true},
            "toolchain_setup": {"success": true},
            "verification": {"all_components_working": true}
        },
        "next_steps": [
            "Reiniciar terminal o ejecutar: source ~/.bashrc",
            "Verificar instalación con: lean --version"
        ]
    }
    ```
    """
    try:
        logger.info("🚀 Iniciando instalación asistida de Lean4")
        
        # Ejecutar instalación
        installation_result = await lean4_installer.install_lean4(
            force_reinstall=request.force_reinstall
        )
        
        if installation_result.get('success', False):
            logger.info("✅ Instalación de Lean4 completada")
            
            # Ejecutar validación post-instalación
            try:
                validation_result = await lean4_service.validate_configuration()
                installation_result['post_install_validation'] = validation_result
            except MedicalError as e:
                installation_result['validation_warning'] = f"No se pudo ejecutar validación: {str(e)}"
        
        return installation_result
        
    except MedicalError as e:
        logger.error(f"❌ Error en instalación de Lean4: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate")
async def validate_lean4_configuration() -> ValidateLean4ConfigurationResult:
    """
    🔧 Validación Completa de Configuración Lean4
    
    Ejecuta una validación exhaustiva de la instalación y configuración
    de Lean4, incluyendo binarios, toolchain, mathlib y workspace.
    
    **Verificaciones:**
    - Binarios (lean, elan, lake)
    - Toolchain y versiones
    - Estado de mathlib
    - Configuración de workspace
    - Test de compilación básica
    
    **Respuesta:**
    ```json
    {
        "overall_status": "healthy",
        "system_info": {
            "os": "darwin",
            "elan_home": "/Users/user/.elan"
        },
        "binary_checks": {
            "lean": {"available": true, "path": "/Users/user/.elan/bin/lean"},
            "elan": {"available": true, "executable": true},
            "lake": {"available": true}
        },
        "compilation_test": {
            "success": true,
            "stdout": "String",
            "returncode": 0
        },
        "recommendations": [
            "✅ Configuración Lean4 está funcionando correctamente"
        ]
    }
    ```
    """
    try:
        logger.info("🔧 Validando configuración de Lean4")
        
        # Ejecutar validación completa
        validation_result = await lean4_service.validate_configuration()
        
        # Agregar información adicional del instalador
        try:
            installation_check = await lean4_installer.check_existing_installation()
            validation_result['installer_check'] = installation_check
        except MedicalError as e:
            validation_result['installer_check_error'] = str(e)
        
        logger.info(f"✅ Validación completada - Estado: {validation_result.get('overall_status', 'unknown')}")
        
        return validation_result
        
    except MedicalError as e:
        logger.error(f"❌ Error en validación de Lean4: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/diagnose")
async def diagnose_lean4_error(request: DiagnosisRequest) -> DiagnoseLean4ErrorResult:
    """
    🩺 Diagnóstico de Errores Lean4
    
    Analiza mensajes de error específicos de Lean4 y proporciona
    sugerencias de solución basadas en patrones comunes.
    
    **Tipos de error soportados:**
    - Syntax errors (expected ... got ...)
    - Type errors (type mismatch)
    - Undefined symbols (unknown identifier)
    - Import errors (could not resolve import)
    - Timeout/memory errors
    
    **Respuesta:**
    ```json
    {
        "error_analysis": {
            "error_type": "syntax_error",
            "severity": "low",
            "suggestions": [
                "Verificar paréntesis y llaves balanceados",
                "Revisar sintaxis de declaraciones"
            ]
        },
        "system_context": {
            "lean_available": true,
            "compilation_working": true
        },
        "troubleshooting_steps": [
            "Verificar sintaxis básica",
            "Consultar documentación Lean4"
        ]
    }
    ```
    """
    try:
        logger.info("🩺 Iniciando diagnóstico de error Lean4")
        
        # Ejecutar diagnóstico del error
        diagnosis = await lean4_service.diagnose_error(
            error_message=request.error_message,
            context=request.context
        )
        
        result = {
            "error_analysis": diagnosis,
            "timestamp": "2025-09-20T12:00:00Z",
            "troubleshooting_steps": diagnosis.get('suggestions', [])
        }
        
        # Incluir información del sistema si se solicita
        if request.include_system_info:
            try:
                system_validation = await lean4_service.validate_configuration()
                result['system_context'] = {
                    "lean_available": system_validation.get('binary_checks', {}).get('lean', {}).get('available', False),
                    "compilation_working": system_validation.get('compilation_test', {}).get('success', False),
                    "overall_status": system_validation.get('overall_status', 'unknown')
                }
            except MedicalError as e:
                result['system_context_error'] = str(e)
        
        logger.info(f"✅ Diagnóstico completado - Tipo: {diagnosis.get('error_type', 'unknown')}")
        
        return result
        
    except MedicalError as e:
        logger.error(f"❌ Error en diagnóstico: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/uninstall")
async def uninstall_lean4() -> UninstallLean4Result:
    """
    🗑️ Desinstalación Completa de Lean4
    
    Remueve completamente Lean4, elan y todos los archivos
    asociados del sistema. **¡Operación irreversible!**
    
    **Advertencia:**
    Esta operación eliminará:
    - Directorio ~/.elan completo
    - Todos los toolchains instalados
    - Cache de mathlib
    - Configuraciones de usuario
    
    **Respuesta:**
    ```json
    {
        "success": true,
        "message": "Lean4 desinstalado exitosamente",
        "removed_path": "/Users/user/.elan",
        "note": "Reiniciar terminal para que los cambios surtan efecto"
    }
    ```
    """
    try:
        logger.info("🗑️ Iniciando desinstalación de Lean4")
        
        # Verificar instalación existente antes de desinstalar
        existing_installation = await lean4_installer.check_existing_installation()
        
        if not existing_installation.get('elan_path_exists', False):
            return {
                "success": True,
                "message": "Lean4 no estaba instalado",
                "action": "none_required",
                "existing_installation": existing_installation
            }
        
        # Ejecutar desinstalación
        uninstall_result = await lean4_installer.uninstall_lean4()
        
        logger.info("✅ Desinstalación completada")
        
        return {
            **uninstall_result,
            "pre_uninstall_status": existing_installation,
            "warning": "Operación irreversible - todos los datos de Lean4 han sido removidos"
        }
        
    except MedicalError as e:
        logger.error(f"❌ Error en desinstalación: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system-info")
async def get_system_information() -> GetSystemInformationResult:
    """
    💻 Información Detallada del Sistema
    
    Proporciona información completa sobre el sistema operativo,
    dependencias disponibles y compatibilidad con Lean4.
    
    **Respuesta:**
    ```json
    {
        "system_details": {
            "os": "darwin",
            "architecture": "arm64",
            "python_version": "3.11.5",
            "shell": "/bin/zsh",
            "is_supported": true
        },
        "dependencies": {
            "curl": {"available": true, "version": "curl 7.88.1"},
            "git": {"available": true},
            "gcc": {"available": true}
        },
        "installation_paths": {
            "default_elan_home": "/Users/user/.elan",
            "user_home": "/Users/user"
        },
        "compatibility": {
            "lean4_supported": true,
            "installation_method": "elan_script"
        }
    }
    ```
    """
    try:
        logger.info("💻 Obteniendo información del sistema")
        
        # Obtener información completa del sistema
        system_info = await lean4_installer.detect_system_info()
        
        # Verificar estado actual de instalación
        current_installation = await lean4_installer.check_existing_installation()
        
        return {
            "system_details": {
                "os": system_info.get("os", "unknown"),
                "architecture": system_info.get("architecture", "unknown"),
                "platform": system_info.get("platform_details", "unknown"),
                "python_version": system_info.get("python_version", "unknown"),
                "shell": system_info.get("shell", "unknown"),
                "user": system_info.get("user", "unknown"),
                "is_supported": system_info.get("is_supported", False)
            },
            "dependencies": system_info.get("dependencies", {}),
            "installation_paths": {
                "default_elan_home": system_info.get("install_path", "unknown"),
                "user_home": system_info.get("user", "unknown")
            },
            "current_installation": current_installation,
            "compatibility": {
                "lean4_supported": system_info.get("is_supported", False),
                "installation_method": "elan_script" if system_info.get("is_supported", False) else "manual_required",
                "recommended_approach": "automated" if system_info.get("is_supported", False) else "manual"
            },
            "useful_commands": {
                "check_lean": "lean --version",
                "check_elan": "elan --version",
                "list_toolchains": "elan toolchain list",
                "create_project": "lake new <project_name>"
            }
        }
        
    except MedicalError as e:
        logger.error(f"❌ Error obteniendo información del sistema: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
