"""
Data Versioning Service
Provides data versioning and tracking capabilities
"""

import json
import hashlib
import os
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
import logging
import aiofiles
import asyncio
from app.services.base_service import BaseService

logger = logging.getLogger(__name__)

class DataVersion:
    """Represents a data version"""
    
    def __init__(self, version_id: str, data_path: str, metadata: Dict[str, Any]):
        self.version_id = version_id
        self.data_path = data_path
        self.metadata = metadata
        self.created_at = datetime.now()
        self.hash = self._calculate_hash()
    
    def _calculate_hash(self) -> str:
        """Calculate hash of the data"""
        try:
            if os.path.exists(self.data_path):
                with open(self.data_path, 'rb') as f:
                    content = f.read()
                    return hashlib.sha256(content).hexdigest()
            return hashlib.sha256(str(self.metadata).encode()).hexdigest()
        except AtlasException as e:
            logger.error(f"Error calculating hash: {e}")
            return ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "version_id": self.version_id,
            "data_path": self.data_path,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "hash": self.hash
        }

class DataVersioningService(BaseService):
    """Service for data versioning and tracking"""
    
    def __init__(self, base_path: str = "./data_versions"):
        super().__init__("DataVersioningService")
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.versions: Dict[str, DataVersion] = {}
        self.version_history: List[str] = []
        self._load_versions()
    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a service request"""
        action = request_data.get("action")
        if action == "create_version":
            return await asyncio.to_thread(self.create_version, 
                request_data.get("data_path"),
                request_data.get("metadata"),
                request_data.get("allow_external_path", False)
            )
        elif action == "get_version":
            return await asyncio.to_thread(self.get_version, request_data.get("version_id"))
        elif action == "list_versions":
            return await asyncio.to_thread(self.list_versions)
        elif action == "get_history":
            return await asyncio.to_thread(self.get_history)
        else:
            return {"success": False, "error": f"Unknown action: {action}"}

    
    def _get_version_file(self) -> Path:
        """Get versions metadata file path"""
        return self.base_path / "versions.json"
    
    def _load_versions(self):
        """Load existing versions from disk"""
        version_file = self._get_version_file()
        if version_file.exists():
            try:
                with open(version_file, 'r') as f:
                    data = json.load(f)
                    for version_data in data.get("versions", []):
                        version = DataVersion(
                            version_data["version_id"],
                            version_data["data_path"],
                            version_data["metadata"]
                        )
                        version.created_at = datetime.fromisoformat(version_data["created_at"])
                        version.hash = version_data["hash"]
                        self.versions[version.version_id] = version
                    self.version_history = data.get("history", [])
            except AtlasException as e:
                logger.error(f"Error loading versions: {e}")
    
    def _save_versions(self):
        """Save versions metadata to disk"""
        try:
            data = {
                "versions": [v.to_dict() for v in self.versions.values()],
                "history": self.version_history
            }
            with open(self._get_version_file(), 'w') as f:
                json.dump(data, f, indent=2)
        except AtlasException as e:
            logger.error(f"Error saving versions: {e}")
    
    def create_version(self, 
                      data_path: str, 
                      metadata: Optional[Dict[str, Any]] = None,
                      version_id: Optional[str] = None) -> str:
        """Create a new data version"""
        if metadata is None:
            metadata = {}
        
        if version_id is None:
            version_id = f"v_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Copy data to versioned storage
        version_data_path = self.base_path / version_id
        version_data_path.mkdir(parents=True, exist_ok=True)
        
        if os.path.isfile(data_path):
            dest_path = version_data_path / Path(data_path).name
            shutil.copy2(data_path, dest_path)
            final_data_path = str(dest_path)
        elif os.path.isdir(data_path):
            dest_path = version_data_path / "data"
            shutil.copytree(data_path, dest_path, dirs_exist_ok=True)
            final_data_path = str(dest_path)
        else:
            final_data_path = data_path
        
        # Create version object
        version = DataVersion(version_id, final_data_path, metadata)
        
        # Store version
        self.versions[version_id] = version
        self.version_history.append(version_id)
        self._save_versions()
        
        logger.info(f"Created data version: {version_id}")
        return version_id
    
    def get_version(self, version_id: str) -> Optional[DataVersion]:
        """Get a specific version"""
        return self.versions.get(version_id)
    
    def list_versions(self) -> List[Dict[str, Any]]:
        """List all versions"""
        return [version.to_dict() for version in self.versions.values()]
    
    def get_latest_version(self) -> Optional[DataVersion]:
        """Get the latest version"""
        if not self.version_history:
            return None
        latest_id = self.version_history[-1]
        return self.versions.get(latest_id)
    
    def compare_versions(self, version_id1: str, version_id2: str) -> Dict[str, Any]:
        """Compare two versions"""
        v1 = self.get_version(version_id1)
        v2 = self.get_version(version_id2)
        
        if not v1 or not v2:
            return {"error": "Version not found"}
        
        return {
            "version_1": v1.to_dict(),
            "version_2": v2.to_dict(),
            "hash_match": v1.hash == v2.hash,
            "metadata_diff": self._compare_metadata(v1.metadata, v2.metadata)
        }
    
    def _compare_metadata(self, meta1: Dict[str, Any], meta2: Dict[str, Any]) -> Dict[str, Any]:
        """Compare metadata between versions"""
        diff = {
            "added": {},
            "removed": {},
            "changed": {}
        }
        
        all_keys = set(meta1.keys()) | set(meta2.keys())
        
        for key in all_keys:
            if key not in meta1:
                diff["added"][key] = meta2[key]
            elif key not in meta2:
                diff["removed"][key] = meta1[key]
            elif meta1[key] != meta2[key]:
                diff["changed"][key] = {
                    "old": meta1[key],
                    "new": meta2[key]
                }
        
        return diff
    
    def delete_version(self, version_id: str) -> bool:
        """Delete a version"""
        if version_id not in self.versions:
            return False
        
        try:
            # Remove from memory
            del self.versions[version_id]
            if version_id in self.version_history:
                self.version_history.remove(version_id)
            
            # Remove from disk
            version_path = self.base_path / version_id
            if version_path.exists():
                shutil.rmtree(version_path)
            
            self._save_versions()
            logger.info(f"Deleted version: {version_id}")
            return True
        except AtlasException as e:
            logger.error(f"Error deleting version {version_id}: {e}")
            return False
    
    def restore_version(self, version_id: str, target_path: str) -> bool:
        """Restore a version to a target path"""
        version = self.get_version(version_id)
        if not version:
            return False
        
        try:
            if os.path.exists(version.data_path):
                if os.path.isfile(version.data_path):
                    shutil.copy2(version.data_path, target_path)
                else:
                    shutil.copytree(version.data_path, target_path, dirs_exist_ok=True)
                return True
        except AtlasException as e:
            logger.error(f"Error restoring version {version_id}: {e}")
            return False
        
        return False
    
    def tag_version(self, version_id: str, tag: str) -> bool:
        """Tag a version with a label"""
        version = self.get_version(version_id)
        if not version:
            return False
        
        version.metadata["tag"] = tag
        self._save_versions()
        return True
    
    def get_version_by_tag(self, tag: str) -> Optional[DataVersion]:
        """Get version by tag"""
        for version in self.versions.values():
            if version.metadata.get("tag") == tag:
                return version
        return None
    
    def export_version_info(self, output_path: str) -> bool:
        """Export version information to file"""
        try:
            version_info = {
                "versions": self.list_versions(),
                "history": self.version_history,
                "exported_at": datetime.now().isoformat()
            }
            
            with open(output_path, 'w') as f:
                json.dump(version_info, f, indent=2)
            return True
        except AtlasException as e:
            logger.error(f"Error exporting version info: {e}")
            return False

class DataVersioningManager:
    """Manager for multiple data versioning services"""
    
    def __init__(self):
        self.services: Dict[str, DataVersioningService] = {}
    
    def get_service(self, dataset_name: str) -> DataVersioningService:
        """Get or create a versioning service for a dataset"""
        if dataset_name not in self.services:
            self.services[dataset_name] = DataVersioningService(
                f"./data_versions/{dataset_name}"
            )
        return self.services[dataset_name]
    
    def list_datasets(self) -> List[str]:
        """List all managed datasets"""
        return list(self.services.keys())

# Global manager instance
versioning_manager = DataVersioningManager()

def get_versioning_service(dataset_name: str = "default") -> DataVersioningService:
    """Get a data versioning service"""
    return versioning_manager.get_service(dataset_name)

def version_data(data_path: str, 
                dataset_name: str = "default",
                metadata: Optional[Dict[str, Any]] = None,
                version_id: Optional[str] = None) -> str:
    """Convenience function to version data"""
    service = get_versioning_service(dataset_name)
    return service.create_version(data_path, metadata, version_id)
