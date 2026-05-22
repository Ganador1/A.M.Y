"""
Reproducibility Service
Ensures reproducibility of experiments and analyses
"""

import json
import hashlib
import os
import sys
import subprocess
import platform
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
import logging
import uuid
import aiofiles
import asyncio
from app.exceptions.domain.biology import BiologyError

logger = logging.getLogger(__name__)

class EnvironmentSnapshot:
    """Captures environment information for reproducibility"""
    
    def __init__(self):
        self.timestamp = datetime.now()
        self.platform_info = self._get_platform_info()
        self.python_info = self._get_python_info()
        self.packages = self._get_installed_packages()
        self.environment_vars = self._get_environment_vars()
        self.system_info = self._get_system_info()
    
    def _get_platform_info(self) -> Dict[str, str]:
        """Get platform information"""
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "architecture": str(platform.architecture()),
            "node": platform.node()
        }
    
    def _get_python_info(self) -> Dict[str, str]:
        """Get Python environment information"""
        return {
            "version": sys.version,
            "executable": sys.executable,
            "path": sys.path.copy(),
            "prefix": sys.prefix,
            "base_prefix": getattr(sys, 'base_prefix', sys.prefix),
            "implementation": platform.python_implementation(),
            "compiler": platform.python_compiler(),
            "build": str(platform.python_build())
        }
    
    def _get_installed_packages(self) -> List[Dict[str, str]]:
        """Get installed Python packages"""
        packages = []
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "list", "--format=json"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                packages = json.loads(result.stdout)
        except BiologyError as e:
            logger.warning(f"Could not get package list: {e}")
            
        return packages
    
    def _get_environment_vars(self) -> Dict[str, str]:
        """Get relevant environment variables"""
        relevant_vars = [
            'PATH', 'PYTHONPATH', 'HOME', 'USER', 'CONDA_DEFAULT_ENV',
            'VIRTUAL_ENV', 'CUDA_VISIBLE_DEVICES', 'OMP_NUM_THREADS'
        ]
        
        env_vars = {}
        for var in relevant_vars:
            value = os.environ.get(var)
            if value:
                env_vars[var] = value
                
        return env_vars
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        info = {
            "cpu_count": os.cpu_count(),
            "current_directory": os.getcwd()
        }
        
        # Memory info (if available)
        try:
            import psutil
            info["memory_total"] = psutil.virtual_memory().total
            info["memory_available"] = psutil.virtual_memory().available
        except ImportError:
            pass
            
        return info
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "platform_info": self.platform_info,
            "python_info": self.python_info,
            "packages": self.packages,
            "environment_vars": self.environment_vars,
            "system_info": self.system_info
        }

class ExperimentRecord:
    """Records experiment details for reproducibility"""
    
    def __init__(self, experiment_id: str):
        self.experiment_id = experiment_id
        self.created_at = datetime.now()
        self.environment = EnvironmentSnapshot()
        self.parameters = {}
        self.inputs = {}
        self.outputs = {}
        self.code_snapshot = {}
        self.metadata = {}
        self.reproducibility_hash = self._calculate_hash()
    
    def _calculate_hash(self) -> str:
        """Calculate reproducibility hash"""
        hash_data = {
            "parameters": self.parameters,
            "inputs": self.inputs,
            "environment_key": {
                "python_version": self.environment.python_info.get("version"),
                "packages": [f"{p['name']}=={p['version']}" for p in self.environment.packages]
            }
        }
        
        hash_string = json.dumps(hash_data, sort_keys=True)
        return hashlib.sha256(hash_string.encode()).hexdigest()
    
    def add_parameter(self, name: str, value: Any):
        """Add experiment parameter"""
        self.parameters[name] = value
        self.reproducibility_hash = self._calculate_hash()
    
    def add_input(self, name: str, value: Any, file_path: Optional[str] = None):
        """Add experiment input"""
        input_data = {"value": value}
        
        if file_path and os.path.exists(file_path):
            input_data["file_path"] = file_path
            input_data["file_hash"] = self._hash_file(file_path)
        
        self.inputs[name] = input_data
        self.reproducibility_hash = self._calculate_hash()
    
    def add_output(self, name: str, value: Any, file_path: Optional[str] = None):
        """Add experiment output"""
        output_data = {"value": value}
        
        if file_path:
            output_data["file_path"] = file_path
            if os.path.exists(file_path):
                output_data["file_hash"] = self._hash_file(file_path)
        
        self.outputs[name] = output_data
    
    def add_code_snapshot(self, name: str, code: str, file_path: Optional[str] = None):
        """Add code snapshot"""
        code_data = {
            "code": code,
            "hash": hashlib.sha256(code.encode()).hexdigest()
        }
        
        if file_path:
            code_data["file_path"] = file_path
            
        self.code_snapshot[name] = code_data
    
    def _hash_file(self, file_path: str) -> str:
        """Calculate file hash"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
        except BiologyError as e:
            logger.error(f"Error hashing file {file_path}: {e}")
            return ""
        
        return hash_sha256.hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "experiment_id": self.experiment_id,
            "created_at": self.created_at.isoformat(),
            "environment": self.environment.to_dict(),
            "parameters": self.parameters,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "code_snapshot": self.code_snapshot,
            "metadata": self.metadata,
            "reproducibility_hash": self.reproducibility_hash
        }

class ReproducibilityService:
    """Service for managing experiment reproducibility"""
    
    def __init__(self, storage_dir: str = "./reproducibility_records"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.records: Dict[str, ExperimentRecord] = {}
        self._load_records()
    
    def _get_record_file(self, experiment_id: str) -> Path:
        """Get record file path"""
        return self.storage_dir / f"{experiment_id}.json"
    
    def _load_records(self):
        """Load existing records"""
        for record_file in self.storage_dir.glob("*.json"):
            try:
                with open(record_file, 'r') as f:
                    data = json.load(f)
                    experiment_id = data["experiment_id"]
                    # Note: We only load metadata, full records loaded on demand
                    self.records[experiment_id] = None
            except BiologyError as e:
                logger.error(f"Error loading record from {record_file}: {e}")
    
    def create_experiment(self, experiment_id: Optional[str] = None) -> str:
        """Create a new experiment record"""
        if experiment_id is None:
            experiment_id = str(uuid.uuid4())
        
        record = ExperimentRecord(experiment_id)
        self.records[experiment_id] = record
        
        logger.info(f"Created experiment record: {experiment_id}")
        return experiment_id
    
    def get_experiment(self, experiment_id: str) -> Optional[ExperimentRecord]:
        """Get experiment record"""
        if experiment_id in self.records:
            if self.records[experiment_id] is None:
                # Load from file
                record_file = self._get_record_file(experiment_id)
                if record_file.exists():
                    try:
                        with open(record_file, 'r') as f:
                            data = json.load(f)
                            # Reconstruct record (simplified)
                            record = ExperimentRecord(experiment_id)
                            record.created_at = datetime.fromisoformat(data["created_at"])
                            record.parameters = data["parameters"]
                            record.inputs = data["inputs"]
                            record.outputs = data["outputs"]
                            record.code_snapshot = data["code_snapshot"]
                            record.metadata = data["metadata"]
                            record.reproducibility_hash = data["reproducibility_hash"]
                            self.records[experiment_id] = record
                    except BiologyError as e:
                        logger.error(f"Error loading experiment {experiment_id}: {e}")
                        return None
            
            return self.records[experiment_id]
        
        return None
    
    def save_experiment(self, experiment_id: str) -> bool:
        """Save experiment record to file"""
        record = self.get_experiment(experiment_id)
        if not record:
            return False
        
        try:
            record_file = self._get_record_file(experiment_id)
            with open(record_file, 'w') as f:
                json.dump(record.to_dict(), f, indent=2)
            
            logger.info(f"Saved experiment record: {experiment_id}")
            return True
        except BiologyError as e:
            logger.error(f"Error saving experiment {experiment_id}: {e}")
            return False
    
    def list_experiments(self) -> List[str]:
        """List all experiment IDs"""
        return list(self.records.keys())
    
    def compare_experiments(self, exp_id1: str, exp_id2: str) -> Dict[str, Any]:
        """Compare two experiments for reproducibility"""
        exp1 = self.get_experiment(exp_id1)
        exp2 = self.get_experiment(exp_id2)
        
        if not exp1 or not exp2:
            return {"error": "Experiment not found"}
        
        comparison = {
            "experiments": [exp_id1, exp_id2],
            "hash_match": exp1.reproducibility_hash == exp2.reproducibility_hash,
            "parameter_diff": self._compare_dicts(exp1.parameters, exp2.parameters),
            "environment_diff": self._compare_environments(exp1.environment, exp2.environment),
            "reproducible": False
        }
        
        # Determine if experiments are reproducible
        comparison["reproducible"] = (
            comparison["hash_match"] and 
            not comparison["parameter_diff"]["changed"] and
            len(comparison["environment_diff"]["package_changes"]) == 0
        )
        
        return comparison
    
    def _compare_dicts(self, dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two dictionaries"""
        diff = {
            "added": {},
            "removed": {},
            "changed": {}
        }
        
        all_keys = set(dict1.keys()) | set(dict2.keys())
        
        for key in all_keys:
            if key not in dict1:
                diff["added"][key] = dict2[key]
            elif key not in dict2:
                diff["removed"][key] = dict1[key]
            elif dict1[key] != dict2[key]:
                diff["changed"][key] = {
                    "old": dict1[key],
                    "new": dict2[key]
                }
        
        return diff
    
    def _compare_environments(self, env1: EnvironmentSnapshot, env2: EnvironmentSnapshot) -> Dict[str, Any]:
        """Compare two environment snapshots"""
        diff = {
            "platform_match": env1.platform_info == env2.platform_info,
            "python_version_match": env1.python_info.get("version") == env2.python_info.get("version"),
            "package_changes": []
        }
        
        # Compare packages
        packages1 = {p["name"]: p["version"] for p in env1.packages}
        packages2 = {p["name"]: p["version"] for p in env2.packages}
        
        all_packages = set(packages1.keys()) | set(packages2.keys())
        
        for package in all_packages:
            if package not in packages1:
                diff["package_changes"].append({
                    "type": "added",
                    "package": package,
                    "version": packages2[package]
                })
            elif package not in packages2:
                diff["package_changes"].append({
                    "type": "removed",
                    "package": package,
                    "version": packages1[package]
                })
            elif packages1[package] != packages2[package]:
                diff["package_changes"].append({
                    "type": "version_changed",
                    "package": package,
                    "old_version": packages1[package],
                    "new_version": packages2[package]
                })
        
        return diff
    
    def generate_requirements_txt(self, experiment_id: str, output_path: str) -> bool:
        """Generate requirements.txt from experiment environment"""
        record = self.get_experiment(experiment_id)
        if not record:
            return False
        
        try:
            requirements = []
            for package in record.environment.packages:
                requirements.append(f"{package['name']}=={package['version']}")
            
            with open(output_path, 'w') as f:
                f.write('\n'.join(sorted(requirements)))
            
            return True
        except BiologyError as e:
            logger.error(f"Error generating requirements.txt: {e}")
            return False
    
    def export_experiment(self, experiment_id: str, output_path: str) -> bool:
        """Export experiment record to JSON"""
        record = self.get_experiment(experiment_id)
        if not record:
            return False
        
        try:
            with open(output_path, 'w') as f:
                json.dump(record.to_dict(), f, indent=2)
            return True
        except BiologyError as e:
            logger.error(f"Error exporting experiment: {e}")
            return False

# Global service instance
reproducibility_service = ReproducibilityService()

def create_experiment(experiment_id: Optional[str] = None) -> str:
    """Create a new experiment record"""
    return reproducibility_service.create_experiment(experiment_id)

def get_experiment_record(experiment_id: str) -> Optional[ExperimentRecord]:
    """Get an experiment record"""
    return reproducibility_service.get_experiment(experiment_id)

def save_experiment_record(experiment_id: str) -> bool:
    """Save an experiment record"""
    return reproducibility_service.save_experiment(experiment_id)
