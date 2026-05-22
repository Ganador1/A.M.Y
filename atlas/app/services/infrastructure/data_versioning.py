"""
Data Versioning Service for AXIOM
Manages scientific data versioning and provenance using DVC

ETHICS & SAFETY NOTICE
- Do NOT version datos con PII, secretos, claves o material con licencia restrictiva.
- Controla cuotas y costes: define límites de tamaño por archivo con MAX_VERSION_FILE_BYTES (p. ej. 524288000 = 500MB).
- Rutas: para mayor seguridad puedes activar STRICT_DATA_PATHS=1 y ALLOWED_DATA_ROOT=./data para evitar paths fuera del área de datos.
- DVC es opcional; si no está instalado, el servicio sigue funcionando sin tracking DVC.
- Todos los comandos externos se ejecutan con timeout para evitar procesos colgados.
Consulta ETHICS_AND_SAFETY.md para más detalles.
"""

import os
import subprocess
import json
from typing import Dict, List, Any
from datetime import datetime
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
import shutil

from app.services.base_service import BaseService
from app.core.bootstrap_logging import logger
from app.config import settings
from app.exceptions.domain.biology import BiologyError
from app.types.data_versioning_types import (
    ProcessRequestResult,
    VersionDataResult,
    GetVersionResult,
    ListVersionsResult,
    CompareVersionsResult,
    RevertToVersionResult,
    CreateProvenanceReportResult,
)


@dataclass
class DataVersion:
    """Data version representation"""
    version_id: str
    data_path: str
    checksum: str
    size_bytes: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "AXIOM"
    tags: List[str] = field(default_factory=list)


class DataVersioningService(BaseService):
    """
    Service for versioning scientific data
    Provides data provenance, versioning, and reproducibility
    """

    def __init__(self):
        super().__init__("DataVersioning")
        self.dvc_root = Path("./data")  # Data directory
        self.dvc_root.mkdir(exist_ok=True)
        self.versions_file = self.dvc_root / "versions.json"
        self.data_versions: Dict[str, DataVersion] = {}

        # Limits and path policy (configurable by environment variables)
        # Default 500MB per file unless overridden
        try:
            # Try lowercase first (Pydantic settings), then uppercase (legacy/env)
            raw_max = getattr(settings, "max_version_file_bytes", None)
            if raw_max is None:
                raw_max = getattr(settings, "MAX_VERSION_FILE_BYTES", None)
            
            self.max_file_bytes = int(raw_max) if raw_max is not None else 500 * 1024 * 1024
        except ValueError:
            self.max_file_bytes = 500 * 1024 * 1024
            
        # Strict paths
        strict_val = getattr(settings, "strict_data_paths", None)
        if strict_val is None:
            strict_val = getattr(settings, "STRICT_DATA_PATHS", "0")
            
        self.strict_paths = str(strict_val).lower() in ("1", "true", "yes")
        
        # Allowed root
        root_val = getattr(settings, "allowed_data_root", None)
        if root_val is None:
            root_val = getattr(settings, "ALLOWED_DATA_ROOT", str(self.dvc_root))
            
        self.allowed_root = Path(root_val if root_val else str(self.dvc_root)).resolve()

    # Initialize DVC if not already done
        self._initialize_dvc()

        # Load existing versions
        self._load_versions()

        logger.info("✅ DataVersioningService initialized")

    def _initialize_dvc(self):
        """Initialize DVC in the project if not already done"""
        try:
            # Check if DVC is already initialized
            if not (Path(".") / ".dvc").exists():
                # Initialize DVC
                result = self._run_cmd(["dvc", "init", "--no-scm"], cwd=".", timeout=20)
                if result.returncode == 0:
                    logger.info("✅ DVC initialized successfully")
                else:
                    logger.warning(f"⚠️ DVC initialization failed: {result.stderr}")

            # Create data directory if it doesn't exist
            self.dvc_root.mkdir(exist_ok=True)

        except BiologyError as e:
            logger.error(f"❌ Failed to initialize DVC: {e}")

    def _run_cmd(self, args: List[str], cwd: str | None = None, timeout: int = 20):
        """Run a subprocess command with safety guards (exists check + timeout)."""
        try:
            exe = args[0]
            if shutil.which(exe) is None:
                class _ResNotFound:  # minimal shim for result compatibility
                    returncode = 127
                    stdout = ""
                    stderr = f"{exe} not found in PATH"

                return _ResNotFound()
            return subprocess.run(
                args,
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as te:
            class _ResTimeout:
                returncode = 124
                stdout = te.stdout or ""
                stderr = f"Timeout after {timeout}s: {' '.join(args)}"

            return _ResTimeout()
        except BiologyError as e:
            class _ResError:
                returncode = 1
                stdout = ""
                stderr = str(e)

            return _ResError()

    def _is_path_allowed(self, data_path: str) -> bool:
        """Check whether data_path complies with path policy when strict mode is on.

        Uses pathlib.Path.is_relative_to for robust containment checks (symlinks and '../').
        """
        try:
            path = Path(data_path).resolve()
            root = self.allowed_root
            # Robust containment via commonpath to avoid /var vs /private/var issues on macOS
            common = os.path.commonpath([str(path), str(root)])
            return common == str(root)
        except BiologyError:
            return False

    def _load_versions(self):
        """Load existing data versions from storage"""
        try:
            if self.versions_file.exists():
                with open(self.versions_file, 'r') as f:
                    versions_data = json.load(f)
                    for v_data in versions_data:
                        # Backward-compatible parsing of datetime fields
                        if isinstance(v_data.get("created_at"), str):
                            try:
                                v_data["created_at"] = datetime.fromisoformat(v_data["created_at"])  # type: ignore[assignment]
                            except BiologyError:
                                v_data["created_at"] = datetime.now()
                        version = DataVersion(**v_data)
                        self.data_versions[version.version_id] = version
                logger.info(f"✅ Loaded {len(self.data_versions)} data versions")
        except BiologyError as e:
            logger.error(f"❌ Failed to load versions: {e}")

    def _save_versions(self):
        """Save data versions to storage"""
        try:
            versions_data = []
            for version in self.data_versions.values():
                v_dict = {
                    "version_id": version.version_id,
                    "data_path": version.data_path,
                    "checksum": version.checksum,
                    "size_bytes": version.size_bytes,
                    "metadata": version.metadata,
                    "created_at": version.created_at.isoformat(),
                    "created_by": version.created_by,
                    "tags": version.tags
                }
                versions_data.append(v_dict)

            with open(self.versions_file, 'w') as f:
                json.dump(versions_data, f, indent=2)

        except BiologyError as e:
            logger.error(f"❌ Failed to save versions: {e}")

    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA256 checksum of a file"""
        try:
            sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except BiologyError as e:
            logger.error(f"❌ Failed to calculate checksum for {file_path}: {e}")
            return ""

    async def process_request(self, request_data: ProcessRequestResult) -> ProcessRequestResult:
        """Process data versioning requests"""
        try:
            action = request_data.get("action", "")

            if action == "version_data":
                return await self.version_data(request_data)
            elif action == "get_version":
                return self.get_version(request_data)
            elif action == "list_versions":
                return self.list_versions(request_data)
            elif action == "compare_versions":
                return self.compare_versions(request_data)
            elif action == "revert_to_version":
                return await self.revert_to_version(request_data)
            elif action == "create_provenance_report":
                return self.create_provenance_report(request_data)
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}",
                    "available_actions": [
                        "version_data", "get_version", "list_versions",
                        "compare_versions", "revert_to_version", "create_provenance_report"
                    ]
                }

        except BiologyError as e:
            return self.handle_error(e, "process_request")

    async def version_data(self, request_data: VersionDataResult) -> VersionDataResult:
        """Create a new version of data"""
        try:
            data_path = request_data.get("data_path")
            metadata = request_data.get("metadata", {})
            tags = request_data.get("tags", [])
            allow_external = bool(request_data.get("allow_external_path", False))

            if not data_path:
                return {
                    "success": False,
                    "error": "data_path is required"
                }

            # Check if file exists
            if not os.path.exists(data_path):
                return {
                    "success": False,
                    "error": f"Data file {data_path} does not exist"
                }

            # Optional strict path policy
            # Observability: log path policy evaluation
            try:
                resolved_path = str(Path(data_path).resolve()) if data_path else ""
            except BiologyError:
                resolved_path = data_path or ""
            allowed = self._is_path_allowed(data_path)
            logger.info(
                f"Path policy: strict={self.strict_paths}, allowed_root={self.allowed_root}, data_path={data_path}, resolved={resolved_path}, allowed={allowed}"
            )

            if self.strict_paths and not allowed:
                return {
                    "success": False,
                    "error": f"Data path '{data_path}' is outside allowed root '{self.allowed_root}'."
                }
            if (not self.strict_paths) and (not allowed) and (not allow_external):
                logger.warning(
                    f"⚠️ Versioning external path detected: {data_path}. Set STRICT_DATA_PATHS=1 to block or pass allow_external_path=True explicitly."
                )

            # Calculate checksum and size
            checksum = self._calculate_checksum(data_path)
            size_bytes = os.path.getsize(data_path)

            # Enforce file size limit
            if size_bytes > self.max_file_bytes:
                return {
                    "success": False,
                    "error": f"File size {size_bytes}B exceeds limit {self.max_file_bytes}B (env MAX_VERSION_FILE_BYTES)."
                }

            # Check if this exact version already exists
            for existing_version in self.data_versions.values():
                if existing_version.checksum == checksum and existing_version.data_path == data_path:
                    logger.info(
                        f"Duplicate detected for path={data_path} with version_id={existing_version.version_id} — returning existing version (idempotent)."
                    )
                    return {
                        "success": True,
                        "message": f"Identical version already exists: {existing_version.version_id}",
                        "version_id": existing_version.version_id,
                        "data_path": data_path,
                        "checksum": checksum,
                        "size_bytes": size_bytes,
                        "existing": True
                    }

            # Create new version
            version_id = f"v_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{checksum[:8]}"
            version = DataVersion(
                version_id=version_id,
                data_path=data_path,
                checksum=checksum,
                size_bytes=size_bytes,
                metadata=metadata,
                tags=tags
            )

            # Add to DVC tracking
            try:
                result = self._run_cmd(["dvc", "add", data_path], cwd=".", timeout=60)
                if result.returncode == 0:
                    logger.info(f"✅ Added {data_path} to DVC tracking")
                else:
                    logger.warning(f"⚠️ DVC add failed: {result.stderr}")
            except BiologyError as e:
                logger.warning(f"⚠️ DVC integration failed: {e}")

            # Store version
            self.data_versions[version_id] = version
            self._save_versions()

            logger.info(f"✅ Created data version: {version_id} for {data_path}")

            return {
                "success": True,
                "message": f"Data version '{version_id}' created successfully",
                "version_id": version_id,
                "data_path": data_path,
                "checksum": checksum,
                "size_bytes": size_bytes
            }

        except BiologyError as e:
            return self.handle_error(e, "version_data")

    def get_version(self, request_data: GetVersionResult) -> GetVersionResult:
        """Get details of a data version"""
        try:
            version_id = request_data.get("version_id")

            if not version_id or version_id not in self.data_versions:
                return {
                    "success": False,
                    "error": f"Version {version_id} not found"
                }

            version = self.data_versions[version_id]

            return {
                "success": True,
                "version": {
                    "version_id": version.version_id,
                    "data_path": version.data_path,
                    "checksum": version.checksum,
                    "size_bytes": version.size_bytes,
                    "metadata": version.metadata,
                    "created_at": version.created_at.isoformat(),
                    "created_by": version.created_by,
                    "tags": version.tags
                }
            }

        except BiologyError as e:
            return self.handle_error(e, "get_version")

    def list_versions(self, request_data: ListVersionsResult) -> ListVersionsResult:
        """List data versions with optional filtering"""
        try:
            data_path = request_data.get("data_path")
            tags = request_data.get("tags", [])

            versions = []
            for version in self.data_versions.values():
                # Apply filters
                if data_path and version.data_path != data_path:
                    continue
                if tags and not any(tag in version.tags for tag in tags):
                    continue

                versions.append({
                    "version_id": version.version_id,
                    "data_path": version.data_path,
                    "checksum": version.checksum[:16] + "...",  # Truncated for display
                    "size_bytes": version.size_bytes,
                    "created_at": version.created_at.isoformat(),
                    "tags": version.tags
                })

            return {
                "success": True,
                "versions": versions,
                "total_count": len(versions),
                "filters_applied": {
                    "data_path": data_path,
                    "tags": tags
                }
            }

        except BiologyError as e:
            return self.handle_error(e, "list_versions")

    def compare_versions(self, request_data: CompareVersionsResult) -> CompareVersionsResult:
        """Compare two data versions"""
        try:
            version_id_1 = request_data.get("version_id_1")
            version_id_2 = request_data.get("version_id_2")

            if not version_id_1 or not version_id_2:
                return {
                    "success": False,
                    "error": "Both version_id_1 and version_id_2 are required"
                }

            if version_id_1 not in self.data_versions or version_id_2 not in self.data_versions:
                return {
                    "success": False,
                    "error": "One or both versions not found"
                }

            v1 = self.data_versions[version_id_1]
            v2 = self.data_versions[version_id_2]

            comparison = {
                "version_1": {
                    "version_id": v1.version_id,
                    "data_path": v1.data_path,
                    "checksum": v1.checksum,
                    "size_bytes": v1.size_bytes,
                    "created_at": v1.created_at.isoformat()
                },
                "version_2": {
                    "version_id": v2.version_id,
                    "data_path": v2.data_path,
                    "checksum": v2.checksum,
                    "size_bytes": v2.size_bytes,
                    "created_at": v2.created_at.isoformat()
                },
                "differences": {
                    "same_checksum": v1.checksum == v2.checksum,
                    "same_size": v1.size_bytes == v2.size_bytes,
                    "same_path": v1.data_path == v2.data_path,
                    "size_difference": v2.size_bytes - v1.size_bytes,
                    "time_difference_hours": (v2.created_at - v1.created_at).total_seconds() / 3600
                }
            }

            return {
                "success": True,
                "message": "Version comparison completed",
                "comparison": comparison
            }

        except BiologyError as e:
            return self.handle_error(e, "compare_versions")

    async def revert_to_version(self, request_data: RevertToVersionResult) -> RevertToVersionResult:
        """Revert data to a previous version"""
        try:
            version_id = request_data.get("version_id")
            target_path = request_data.get("target_path")

            if not version_id or version_id not in self.data_versions:
                return {
                    "success": False,
                    "error": f"Version {version_id} not found"
                }

            version = self.data_versions[version_id]

            if not target_path:
                target_path = version.data_path

            # For now, just copy the file (in a real implementation, you'd restore from DVC)
            try:
                import shutil
                shutil.copy2(version.data_path, target_path)
                logger.info(f"✅ Reverted {version.data_path} to version {version_id}")

                return {
                    "success": True,
                    "message": f"Data reverted to version {version_id}",
                    "version_id": version_id,
                    "target_path": target_path
                }

            except BiologyError as e:
                return {
                    "success": False,
                    "error": f"Failed to revert data: {e}"
                }

        except BiologyError as e:
            return self.handle_error(e, "revert_to_version")

    def create_provenance_report(self, request_data: CreateProvenanceReportResult) -> CreateProvenanceReportResult:
        """Create a provenance report for data"""
        try:
            data_path = request_data.get("data_path")

            if not data_path:
                return {
                    "success": False,
                    "error": "data_path is required"
                }

            # Find all versions for this data path
            versions = [v for v in self.data_versions.values() if v.data_path == data_path]

            if not versions:
                return {
                    "success": False,
                    "error": f"No versions found for {data_path}"
                }

            # Sort by creation time
            versions.sort(key=lambda x: x.created_at)

            # Create provenance report
            report = {
                "data_path": data_path,
                "total_versions": len(versions),
                "first_version": versions[0].created_at.isoformat(),
                "latest_version": versions[-1].created_at.isoformat(),
                "version_history": [],
                "provenance_chain": []
            }

            # Build version history using list comprehension
            report["version_history"] = [
                {
                    "version_id": version.version_id,
                    "created_at": version.created_at.isoformat(),
                    "checksum": version.checksum,
                    "size_bytes": version.size_bytes,
                    "metadata": version.metadata,
                    "tags": version.tags
                }
                for version in versions
            ]

            # Build provenance chain
            for i in range(1, len(versions)):
                prev_version = versions[i-1]
                version = versions[i]
                report["provenance_chain"].append({
                    "from_version": prev_version.version_id,
                    "to_version": version.version_id,
                        "changes": {
                            "size_changed": version.size_bytes != prev_version.size_bytes,
                            "size_difference": version.size_bytes - prev_version.size_bytes,
                            "time_elapsed_hours": (version.created_at - prev_version.created_at).total_seconds() / 3600
                        }
                    })

            return {
                "success": True,
                "message": "Provenance report created successfully",
                "report": report
            }

        except BiologyError as e:
            return self.handle_error(e, "create_provenance_report")
