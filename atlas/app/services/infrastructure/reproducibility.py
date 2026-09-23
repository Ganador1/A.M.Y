"""
Reproducibility Service
Genera un paquete reproducible (manifest + opcionales artefactos) para un experimento.

Incluye:
- Manifest con metadatos del experimento (MLflow), parámetros, métricas, artefactos
- Información del entorno (Python, plataforma, dependencias instaladas)
- Mapeo de artefactos a versiones de datos conocidas (si existen en DataVersioningService)
- ZIP listo para descargar en static/exports

Seguridad y ética:
- No copia artefactos grandes por defecto; limite configurable via max_artifact_bytes
- Omite archivos inexistentes o inaccesibles
"""

from __future__ import annotations
import aiofiles
import asyncio

from typing import Dict, Any, List
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, UTC
import json
import os
import shutil
import sys
import platform
from app.exceptions.domain.biology import BiologyError

try:
    # Python 3.8+
    from importlib import metadata as importlib_metadata  # type: ignore
except BiologyError:  # pragma: no cover - fallback
    import importlib_metadata  # type: ignore

from app.services.base_service import BaseService
from app.types.reproducibility_types import (
    ProcessRequestResult,
    CollectEnvInfoResult,
)


@dataclass
class ExportOptions:
    include_artifacts: bool = False
    max_artifact_bytes: int = 5 * 1024 * 1024  # 5MB por defecto


class ReproducibilityService(BaseService):
    def __init__(self) -> None:
        super().__init__("Reproducibility")
        self.exports_dir = Path("static/exports")
        self.exports_dir.mkdir(parents=True, exist_ok=True)

    async def process_request(self, request_data: ProcessRequestResult) -> ProcessRequestResult:
        """Procesa acciones del servicio de reproducibilidad.
        Acciones soportadas:
        - export_package: genera ZIP con manifest (y opcionalmente artefactos pequeños)
        - cleanup_exports: elimina bundles/ZIP antiguos según retención
        """
        try:
            action = request_data.get("action")
            if action == "export_package":
                exp_service = request_data.get("experiment_service")
                data_service = request_data.get("data_versioning_service")
                experiment_id = request_data.get("experiment_id")
                if not isinstance(experiment_id, str) or not experiment_id:
                    return {"success": False, "error": "experiment_id is required"}
                include_artifacts = bool(request_data.get("include_artifacts", False))
                max_bytes = int(request_data.get("max_artifact_bytes", 5 * 1024 * 1024))
                retention_max_bundles = request_data.get("retention_max_bundles")
                return self.create_reproducible_package(
                    experiment_service=exp_service,
                    data_versioning_service=data_service,
                    experiment_id=experiment_id,
                    include_artifacts=include_artifacts,
                    max_artifact_bytes=max_bytes,
                    retention_max_bundles=retention_max_bundles,
                )
            elif action == "cleanup_exports":
                max_bundles = int(request_data.get("max_bundles", 10))
                deleted = self.cleanup_old_exports(max_bundles=max_bundles)
                return {"success": True, "deleted": deleted, "kept": max_bundles}
            return {"success": False, "error": f"Unknown action: {action}"}
        except BiologyError as e:
            return self.handle_error(e, "process_request")

    def _collect_env_info(self) -> CollectEnvInfoResult:
        """Recolecta información básica del entorno para reproducibilidad."""
        try:
            packages: List[Dict[str, str]] = []
            for dist in importlib_metadata.distributions():
                name = getattr(dist, "metadata", {}).get("Name") if hasattr(dist, "metadata") else None
                version = getattr(dist, "version", None)
                # Fallbacks
                if not name:
                    try:
                        name = dist.metadata["Name"]  # type: ignore[index]
                    except BiologyError:
                        name = getattr(dist, "name", None)
                if not version:
                    version = getattr(dist, "metadata", {}).get("Version") if hasattr(dist, "metadata") else None
                if name and version:
                    packages.append({"name": str(name), "version": str(version)})
        except BiologyError:
            packages = []

        return {
            "python_version": sys.version,
            "platform": platform.platform(),
            "executable": sys.executable,
            "packages": packages,
        }

    def _build_manifest(
        self,
        experiment: Dict[str, Any],
        data_versions_index: Dict[str, Dict[str, Any]],
        options: ExportOptions,
    ) -> Dict[str, Any]:
        """Construye el manifest JSON."""
        artifacts_info: List[Dict[str, Any]] = []
        for art in experiment.get("artifacts", []) or []:
            art_path = str(art)
            info = {
                "path": art_path,
                "exists": os.path.exists(art_path),
                "size_bytes": os.path.getsize(art_path) if os.path.exists(art_path) else None,
            }
            # Vincular versión de datos si existe
            dv = data_versions_index.get(art_path)
            if dv:
                info.update({
                    "data_version_id": dv.get("version_id"),
                    "data_checksum": dv.get("checksum"),
                    "data_size_bytes": dv.get("size_bytes"),
                })
            artifacts_info.append(info)

        manifest: Dict[str, Any] = {
            "type": "axiom_reproducible_package",
            "schema_version": "1.0",
            "created_at": datetime.now(UTC).isoformat(),
            "experiment": {
                "experiment_id": experiment.get("experiment_id"),
                "name": experiment.get("name"),
                "description": experiment.get("description"),
                "parameters": experiment.get("parameters", {}),
                "metrics": experiment.get("metrics", {}),
                "tags": experiment.get("tags", {}),
                "status": experiment.get("status"),
                "created_at": experiment.get("created_at"),
                "completed_at": experiment.get("completed_at"),
                "mlflow_run_id": experiment.get("run_id"),
            },
            "artifacts": artifacts_info,
            "environment": self._collect_env_info(),
            "export_options": {
                "include_artifacts": options.include_artifacts,
                "max_artifact_bytes": options.max_artifact_bytes,
            },
        }
        return manifest

    def create_reproducible_package(
        self,
        *,
        experiment_service,
        data_versioning_service,
        experiment_id: str,
        include_artifacts: bool = False,
    max_artifact_bytes: int = 5 * 1024 * 1024,
    retention_max_bundles: int | None = None,
    ) -> Dict[str, Any]:
        """
        Genera un paquete reproducible para un experimento dado.

        Requiere instancias compartidas de experiment_service y data_versioning_service
        para acceder al estado en memoria.
        """
        if not experiment_id:
            return {"success": False, "error": "experiment_id is required"}

        # Obtener experimento
        exp_result = experiment_service.get_experiment({"experiment_id": experiment_id})
        if not exp_result.get("success"):
            return {"success": False, "error": exp_result.get("error", "Experiment not found")}

        experiment = exp_result["experiment"]

        # Índice de versiones de datos por data_path
        data_versions_index: Dict[str, Dict[str, Any]] = {}
        try:
            for v in data_versioning_service.data_versions.values():
                data_versions_index[v.data_path] = {
                    "version_id": v.version_id,
                    "checksum": v.checksum,
                    "size_bytes": v.size_bytes,
                }
        except BiologyError:
            pass

        options = ExportOptions(include_artifacts=include_artifacts, max_artifact_bytes=max_artifact_bytes)

        # Crear carpeta del bundle
        safe_exp = str(experiment.get("name") or experiment_id).replace(" ", "_")
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        bundle_dir = self.exports_dir / f"bundle_{safe_exp}_{stamp}"
        bundle_dir.mkdir(parents=True, exist_ok=True)

        # Escribir manifest
        manifest = self._build_manifest(experiment, data_versions_index, options)
        manifest_path = bundle_dir / "manifest.json"
        with aiofiles.open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        # Copiar artefactos pequeños si está habilitado
        copied_artifacts: List[str] = []
        skipped_artifacts: List[Dict[str, Any]] = []
        if options.include_artifacts:
            artifacts = experiment.get("artifacts", []) or []
            artifacts_dir = bundle_dir / "artifacts"
            artifacts_dir.mkdir(exist_ok=True)
            for art in artifacts:
                ap = str(art)
                if not os.path.exists(ap):
                    skipped_artifacts.append({"path": ap, "reason": "not_found"})
                    continue
                try:
                    size = os.path.getsize(ap)
                except BiologyError:
                    size = None
                if size is None or size > options.max_artifact_bytes:
                    skipped_artifacts.append({"path": ap, "reason": "too_large", "size_bytes": size})
                    continue
                try:
                    dest = artifacts_dir / os.path.basename(ap)
                    shutil.copy2(ap, dest)
                    copied_artifacts.append(str(dest))
                except BiologyError as e:
                    skipped_artifacts.append({"path": ap, "reason": f"copy_error: {e}"})

        # Empaquetar en ZIP
        zip_base = str(bundle_dir)
        archive_path = shutil.make_archive(zip_base, "zip", root_dir=bundle_dir)

        rel_zip = os.path.relpath(archive_path, start=".")
        # Para servir desde /static, el zip debe estar bajo static/
        # ensure bundle_dir already under static/exports

        summary = {
            "experiment_id": experiment_id,
            "experiment_name": experiment.get("name"),
            "artifacts_total": len(experiment.get("artifacts", []) or []),
            "artifacts_copied": len(copied_artifacts),
            "artifacts_skipped": skipped_artifacts,
            "manifest_path": str(manifest_path),
            "zip_path": rel_zip,
            "download_url": f"/static/exports/{Path(rel_zip).name}" if "static/exports" in rel_zip else f"/{rel_zip}",
        }

        # Retention cleanup opcional
        try:
            if isinstance(retention_max_bundles, int) and retention_max_bundles > 0:
                self.cleanup_old_exports(max_bundles=retention_max_bundles)
        except BiologyError:
            # limpieza es best-effort, no afecta resultado
            pass

        return {"success": True, "message": "Reproducible package created", "summary": summary}

    def cleanup_old_exports(self, *, max_bundles: int = 10) -> int:
        """Elimina bundles/ZIP antiguos manteniendo los más recientes.

        - max_bundles: cuántos bundles mantener como máximo.
        Devuelve el número de bundles eliminados.
        """
        try:
            bundles = [p for p in self.exports_dir.iterdir() if p.is_dir() and p.name.startswith("bundle_")]
        except FileNotFoundError:
            return 0
        bundles_sorted = sorted(bundles, key=lambda p: p.stat().st_mtime, reverse=True)
        to_delete = bundles_sorted[max(0, max_bundles):]
        deleted = 0
        for d in to_delete:
            try:
                # eliminar zip asociado
                zip_path = d.with_suffix(".zip")
                if zip_path.exists():
                    try:
                        zip_path.unlink()
                    except BiologyError:
                        pass
                shutil.rmtree(d, ignore_errors=True)
                deleted += 1
            except BiologyError:
                # seguir con el resto
                pass
        return deleted
