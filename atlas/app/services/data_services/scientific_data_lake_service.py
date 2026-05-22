"""
Scientific Data Lake Service for AXIOM

Local-first storage with optional cloud backends
(S3 via s3fs if available).
Safely ingests, catalogs, and samples large scientific datasets.

ETHICS & SAFETY
- Nunca subas datos con PII ni secretos.
- Respeta límites de tamaño configurables por entorno.
- En modo estricto, sólo permite paths dentro de DATALAKE_ROOT.
"""

from __future__ import annotations
import aiofiles
import asyncio

import os
import shutil
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, List

from app.services.base_service import BaseService
from app.services.database_service import DatabaseService
from app.config import settings
from app.exceptions.domain.biology import BiologyError
from app.types.scientific_data_lake_service_types import (
    SafeCopyLocalResult,
    CopyFromS3Result,
    GetServiceInfoResult,
    IngestResult,
    ListEntriesResult,
    SampleResult,
    StatResult,
)

try:  # Optional S3 support
    import s3fs  # type: ignore
    S3FS_AVAILABLE = True
except BiologyError:  # pragma: no cover
    s3fs = None  # type: ignore
    S3FS_AVAILABLE = False


class ScientificDataLakeService(BaseService):
    """Mass data management for scientific datasets with safe local
    storage and optional S3.
    """

    def __init__(self, db_service: Optional[DatabaseService] = None) -> None:
        super().__init__("ScientificDataLake")
        default_root = "./data/lake"
        self.root = Path(getattr(settings, "DATALAKE_ROOT", default_root) or default_root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        # Limits and policy
        try:
            self.max_file_bytes = int(
                os.getenv(
                    "MAX_DATALAKE_FILE_BYTES",
                    str(5 * 1024 * 1024 * 1024),
                )
            )  # 5GB default
        except ValueError:
            self.max_file_bytes = 5 * 1024 * 1024 * 1024
        self.strict_paths = (
            os.getenv(
                "STRICT_DATALAKE_PATHS",
                "1",
            )
            in ("1", "true", "True")
        )
        self.allowed_root = self.root
        self.allowed_exts = set((
            ".csv",
            ".json",
            ".jsonl",
            ".txt",
            ".tsv",
            ".npy",
            ".npz",
            ".pkl",
            ".gz",
            ".zip",
        ))
        # Optional S3 initialization (only if enabled)
        self.enable_s3 = (
            str(getattr(settings, "ENABLE_S3", "0")) in ("1", "true", "True")
            and S3FS_AVAILABLE
        )
        self.s3: Optional[Any] = None
        if self.enable_s3:
            try:
                # Credentials are taken from standard AWS env/config;
                # do not log secrets
                self.s3 = s3fs.S3FileSystem(anon=False)
                self.logger.info("✅ S3FS initialized for Data Lake")
            except BiologyError as e:  # pragma: no cover
                self.logger.warning(
                    f"⚠️ S3FS init failed, continuing local-only: {e}"
                )
                self.s3 = None
                self.enable_s3 = False

        self.db = db_service or DatabaseService()
        self.logger.info(
            f"✅ ScientificDataLakeService initialized at {self.root}"
        )

    # -------------- Helpers --------------
    def _is_path_allowed(self, path: str | Path) -> bool:
        try:
            p = Path(path).resolve()
            root = self.allowed_root
            common = os.path.commonpath([str(p), str(root)])
            return (not self.strict_paths) or (common == str(root))
        except BiologyError:
            return False

    def _calc_checksum(self, file_path: Path) -> str:
        try:
            sha256 = hashlib.sha256()
            with aiofiles.open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(1024 * 1024), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except BiologyError as e:
            self.logger.error(f"Checksum failed for {file_path}: {e}")
            return ""

    def _safe_copy_local(self, src: Path, dst: Path) -> SafeCopyLocalResult:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        size = dst.stat().st_size
        return {"path": str(dst), "size_bytes": size}

    def _copy_from_s3(self, s3_uri: str, dst: Path) -> CopyFromS3Result:
        if not (self.enable_s3 and self.s3):
            raise RuntimeError("S3 backend not enabled/available")
        dst.parent.mkdir(parents=True, exist_ok=True)
        # Stream download to file
        with self.s3.aiofiles.open(
            s3_uri,
            "rb",
        ) as sf, aiofiles.open(
            dst,
            "wb",
        ) as lf:  # type: ignore[attr-defined]
            shutil.copyfileobj(sf, lf, length=1024 * 1024)
        size = dst.stat().st_size
        return {"path": str(dst), "size_bytes": size}

    def _choose_target(
        self,
        namespace: str,
        name: str,
        src_path: Path,
    ) -> Path:
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        fname = src_path.name
        return self.root / namespace / name / timestamp / fname

    # -------------- Public API --------------
    async def process_request(
        self,
        request_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        try:
            action = request_data.get("action")
            if action == "ingest":
                return await self.ingest(request_data)
            if action == "list":
                return self.list_entries(request_data)
            if action == "sample":
                return self.sample(request_data)
            if action == "stat":
                return self.stat(request_data)
            if action == "info":
                return self.get_service_info()
            return {
                "success": False,
                "error": f"Unknown action: {action}",
                "available_actions": [
                    "ingest",
                    "list",
                    "sample",
                    "stat",
                    "info",
                ],
            }
        except BiologyError as e:
            return self.handle_error(e, context="process_request")

    def get_service_info(self) -> GetServiceInfoResult:
        return {
            "name": "ScientificDataLakeService",
            "version": "1.0.0",
            "root": str(self.root),
            "capabilities": [
                "ingest_local",
                "optional_s3",
                "catalog_register",
                "sample_csv_json",
                "dataset_stats",
            ],
            "limits": {
                "max_file_bytes": self.max_file_bytes,
                "strict_paths": self.strict_paths,
                "allowed_extensions": sorted(self.allowed_exts),
            },
            "backends": {"s3": bool(self.enable_s3 and self.s3)},
        }

    async def ingest(self, request_data: IngestResult) -> IngestResult:
        """Ingest a file from local path or s3:// URI into the managed lake and
        register it.
        """
        src = request_data.get("source")
        namespace = (
            str(request_data.get("namespace", "default")).strip() or "default"
        )
        name = (
            str(request_data.get("name", "dataset")).strip() or "dataset"
        )
        dataset_type = str(request_data.get("dataset_type", "generic"))
        data_format = str(request_data.get("data_format", "auto"))
        description = request_data.get("description")
        metadata = request_data.get("metadata", {}) or {}
        is_public = bool(request_data.get("is_public", False))

        if not src or not isinstance(src, str):
            return {
                "success": False,
                "error": "'source' is required (local path or s3:// URI)",
            }

        # Determine scheme
        is_s3 = src.startswith("s3://")
        try:
            if is_s3:
                if not (self.enable_s3 and self.s3):
                    return {
                        "success": False,
                        "error": "S3 not enabled/available",
                    }
                # choose local destination
                dst = self._choose_target(
                    namespace,
                    name,
                    Path(src.split("/")[-1]),
                )
                copied = self._copy_from_s3(src, dst)
                dst_path = Path(copied["path"]).resolve()
            else:
                src_path = Path(src).expanduser().resolve()
                if not src_path.exists() or not src_path.is_file():
                    return {
                        "success": False,
                        "error": f"Source file not found: {src_path}",
                    }
                # Size guard
                size = src_path.stat().st_size
                if size > self.max_file_bytes:
                    return {
                        "success": False,
                        "error": (
                            f"File exceeds max size limit: {size} > "
                            f"{self.max_file_bytes}"
                        ),
                    }
                # Extension guard (best-effort)
                if (
                    src_path.suffix
                    and self.allowed_exts
                    and src_path.suffix.lower() not in self.allowed_exts
                ):
                    self.logger.warning(
                        f"Extension {src_path.suffix} not in allowed list; "
                        "proceeding"
                    )
                dst = self._choose_target(namespace, name, src_path)
                copied = self._safe_copy_local(src_path, dst)
                dst_path = Path(copied["path"]).resolve()

            if self.strict_paths and not self._is_path_allowed(dst_path):
                return {
                    "success": False,
                    "error": "Destination violates strict path policy",
                }

            checksum = self._calc_checksum(dst_path)
            size_bytes = dst_path.stat().st_size

            # Infer data_format if auto
            if data_format == "auto":
                ext = dst_path.suffix.lower()
                if ext in (".csv", ".tsv"):
                    data_format = "csv"
                elif ext in (".json", ".jsonl"):
                    data_format = "json"
                else:
                    data_format = ext.lstrip(".") or "binary"

            # Register in database
            meta = {
                **({} if not isinstance(metadata, dict) else metadata),
                "namespace": namespace,
                "name": name,
                "checksum": checksum,
                "ingested_at": datetime.utcnow().isoformat(),
                "backend": "s3" if is_s3 else "local",
            }
            dataset = self.db.save_dataset(
                name=f"{namespace}:{name}",
                dataset_type=dataset_type,
                data_format=data_format,
                description=description,
                data_content=None,
                file_path=str(dst_path),
                metadata=meta,
                created_by=None,
                is_public=is_public,
            )

            return {
                "success": True,
                "dataset_id": getattr(dataset, "id", None),
                "file_path": str(dst_path),
                "size_bytes": size_bytes,
                "checksum": checksum,
                "data_format": data_format,
                "backend": "s3" if is_s3 else "local",
            }
        except BiologyError as e:
            return self.handle_error(e, context="ingest")

    def list_entries(self, request_data: ListEntriesResult) -> ListEntriesResult:
        """List datasets from DB and (optionally) the filesystem
        namespace tree.
        """
        try:
            dataset_type = request_data.get("dataset_type")
            is_public = request_data.get("is_public")
            user_id = request_data.get("user_id")
            limit = int(request_data.get("limit", 50))

            datasets = self.db.get_datasets(
                dataset_type=dataset_type,
                user_id=user_id,
                is_public=is_public,
                limit=limit,
            )
            ds_list = []
            for d in datasets:
                ds_list.append({
                    "id": getattr(d, "id", None),
                    "name": getattr(d, "name", None),
                    "type": getattr(d, "dataset_type", None),
                    "format": getattr(d, "data_format", None),
                    "file_path": getattr(d, "file_path", None),
                    "created_at": (
                        getattr(d, "created_at", None).isoformat()
                        if getattr(d, "created_at", None)
                        else None
                    ),
                    "is_public": getattr(d, "is_public", False),
                })

            # Optional filesystem listing
            ns = str(request_data.get("namespace", "")).strip()
            fs_entries: List[Dict[str, Any]] = []
            base = self.root / ns if ns else self.root
            if base.exists():
                for p in base.rglob("*"):
                    if p.is_file():
                        try:
                            fs_entries.append({
                                "path": str(p.relative_to(self.root)),
                                "size_bytes": p.stat().st_size,
                                "modified": datetime.utcfromtimestamp(
                                    p.stat().st_mtime
                                ).isoformat(),
                            })
                        except BiologyError:
                            continue

            return {
                "success": True,
                "datasets": ds_list,
                "filesystem": fs_entries,
            }
        except BiologyError as e:
            return self.handle_error(e, context="list_entries")

    def sample(self, request_data: SampleResult) -> SampleResult:
        """Return a lightweight sample/preview of a dataset file
        (supports csv, json, jsonl).
        """
        try:
            file_path = request_data.get("file_path")
            n = int(request_data.get("n", 5))
            if not file_path:
                return {"success": False, "error": "file_path is required"}
            p = Path(file_path).expanduser().resolve()
            if not p.exists() or not p.is_file():
                return {"success": False, "error": f"File not found: {p}"}

            ext = p.suffix.lower()
            preview: Any
            if ext in (".csv", ".tsv"):
                # Minimal CSV head without pandas dependency beyond what
                # exists in project
                import csv
                delim = "," if ext == ".csv" else "\t"
                rows: List[List[str]] = []
                with aiofiles.open(
                    p,
                    newline="",
                    encoding="utf-8",
                    errors="ignore",
                ) as f:
                    reader = csv.reader(f, delimiter=delim)
                    for i, row in enumerate(reader):
                        rows.append(row)
                        if i + 1 >= n:
                            break
                preview = {
                    "kind": "tabular",
                    "rows": rows,
                    "delimiter": "," if delim == "," else "\t",
                }
            elif ext in (".jsonl", ):
                lines: List[Any] = []
                with aiofiles.open(p, "r", encoding="utf-8", errors="ignore") as f:
                    for i, line in enumerate(f):
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            lines.append(json.loads(line))
                        except BiologyError:
                            lines.append({"raw": line})
                        if i + 1 >= n:
                            break
                preview = {"kind": "jsonl", "lines": lines}
            elif ext in (".json", ):
                with aiofiles.open(
                    p,
                    "r",
                    encoding="utf-8",
                    errors="ignore",
                ) as f:
                    try:
                        data = json.load(f)
                    except BiologyError:
                        # Fallback to head of text
                        f.seek(0)
                        data = f.read(4096)
                data_out = (
                    data if isinstance(data, (dict, list))
                    else str(data)[:4096]
                )
                preview = {
                    "kind": "json",
                    "data": data_out,
                }
            else:
                # Binary/unknown: return size and first bytes hex
                size = p.stat().st_size
                with aiofiles.open(
                    p,
                    "rb",
                ) as f:
                    head = f.read(min(64, size))
                preview = {
                    "kind": "binary",
                    "size_bytes": size,
                    "head_hex": head.hex(),
                }

            return {"success": True, "preview": preview}
        except BiologyError as e:
            return self.handle_error(e, context="sample")

    def stat(self, request_data: StatResult) -> StatResult:
        """Return basic statistics for a file within the lake."""
        try:
            file_path = request_data.get("file_path")
            if not file_path:
                return {"success": False, "error": "file_path is required"}
            p = Path(file_path).expanduser().resolve()
            if not self._is_path_allowed(p):
                return {
                    "success": False,
                    "error": "Path not within allowed root",
                }
            if not p.exists() or not p.is_file():
                return {"success": False, "error": f"File not found: {p}"}
            info = {
                "path": str(p),
                "size_bytes": p.stat().st_size,
                "modified": datetime.utcfromtimestamp(
                    p.stat().st_mtime
                ).isoformat(),
                "checksum": self._calc_checksum(p),
            }
            return {"success": True, "info": info}
        except BiologyError as e:
            return self.handle_error(e, context="stat")
# EOF
