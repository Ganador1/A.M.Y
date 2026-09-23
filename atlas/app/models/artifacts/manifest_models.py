"""
Manifest Models - AXIOM META 4
Pydantic v2 models for artifact manifests based on manifest.schema.json.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, ConfigDict, validator
from enum import Enum


class ArtifactType(str, Enum):
    """Types of artifacts"""
    MODEL = "model"
    DATASET = "dataset"
    SCALER = "scaler"
    ENCODER = "encoder"
    PIPELINE = "pipeline"
    METADATA = "metadata"
    REPORT = "report"
    CONFIG = "config"


class ArtifactFormat(str, Enum):
    """Artifact file formats"""
    PICKLE = "pickle"
    JOBLIB = "joblib"
    JSON = "json"
    CSV = "csv"
    PARQUET = "parquet"
    HDF5 = "hdf5"
    ONNX = "onnx"
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"


class SignatureAlgorithm(str, Enum):
    """Signature algorithms"""
    ED25519 = "ed25519"


class ArtifactItem(BaseModel):
    """Individual artifact item within a manifest"""
    
    model_config = ConfigDict(extra="forbid")
    
    path: str = Field(..., description="Relative path to the artifact")
    type: ArtifactType = Field(..., description="Type of artifact")
    hash_sha256: str = Field(..., pattern=r"^[a-f0-9]{64}$", description="SHA256 hash of the artifact")
    size_bytes: Optional[int] = Field(None, ge=0, description="Size of artifact in bytes")
    format: Optional[ArtifactFormat] = Field(None, description="File format of the artifact")


class DatasetInfo(BaseModel):
    """Dataset information"""
    
    model_config = ConfigDict(extra="forbid")
    
    name: str = Field(..., description="Dataset name")
    version: str = Field(..., description="Dataset version")
    hash: str = Field(..., description="Dataset hash")
    dvc_ref: Optional[str] = Field(None, description="DVC reference")


class CalibrationMetrics(BaseModel):
    """Calibration metrics"""
    
    model_config = ConfigDict(extra="forbid")
    
    ece: Optional[float] = Field(None, ge=0.0, le=1.0, description="Expected Calibration Error")
    brier: Optional[float] = Field(None, ge=0.0, le=2.0, description="Brier Score")


class MetricsInfo(BaseModel):
    """Performance metrics information"""
    
    model_config = ConfigDict(extra="forbid")
    
    primary: float = Field(..., description="Primary metric value")
    secondary: Optional[Dict[str, float]] = Field(None, description="Secondary metrics")
    calibration: Optional[CalibrationMetrics] = Field(None, description="Calibration metrics")


class LineageInfo(BaseModel):
    """Lineage and provenance information"""
    
    model_config = ConfigDict(extra="forbid")
    
    parents: Optional[List[str]] = Field(None, description="Parent artifact IDs")
    provenance_graph_hash: Optional[str] = Field(None, description="Hash of provenance graph")


class HashInfo(BaseModel):
    """Hash information for integrity"""
    
    model_config = ConfigDict(extra="forbid")
    
    manifest_sha256: Optional[str] = Field(None, pattern=r"^[a-f0-9]{64}$", description="Hash of manifest content")


class SignatureInfo(BaseModel):
    """Digital signature information"""
    
    model_config = ConfigDict(extra="forbid")
    
    alg: SignatureAlgorithm = Field(..., description="Signature algorithm")
    sig: str = Field(..., pattern=r"^[A-Za-z0-9+/=]+$", description="Base64-encoded signature")
    public_key_fingerprint: str = Field(..., pattern=r"^[a-f0-9]{64}$", description="Public key fingerprint")
    ts: Optional[datetime] = Field(None, description="Signature timestamp")


class ArtifactManifest(BaseModel):
    """
    Complete artifact manifest based on manifest.schema.json.
    Provides type safety and validation for artifact metadata.
    """
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid"
    )
    
    # Required fields
    id: str = Field(..., pattern=r"^[a-zA-Z0-9_.-]+$", description="Unique artifact identifier")
    name: str = Field(..., description="Human-readable artifact name")
    version: str = Field(..., pattern=r"^v?[0-9]+(\.[0-9]+){0,2}(-[A-Za-z0-9_.]+)?$", description="Artifact version")
    created_at: datetime = Field(..., description="Creation timestamp")
    git_commit: str = Field(..., pattern=r"^[a-f0-9]{7,40}$", description="Git commit hash")
    metrics: MetricsInfo = Field(..., description="Performance metrics")
    artifacts: List[ArtifactItem] = Field(..., min_items=1, description="List of artifact items")
    
    # Optional fields
    description: Optional[str] = Field(None, description="Artifact description")
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")
    dataset: Optional[DatasetInfo] = Field(None, description="Dataset information")
    parameters: Optional[Dict[str, Union[int, float, str, bool, None]]] = Field(None, description="Model parameters")
    lineage: Optional[LineageInfo] = Field(None, description="Lineage information")
    hashes: Optional[HashInfo] = Field(None, description="Hash information")
    signatures: Optional[List[SignatureInfo]] = Field(None, description="Digital signatures")
    
    @validator('artifacts')
    def validate_unique_paths(cls, v):
        """Ensure artifact paths are unique"""
        paths = [artifact.path for artifact in v]
        if len(paths) != len(set(paths)):
            raise ValueError("Artifact paths must be unique")
        return v
    
    def get_artifact_by_path(self, path: str) -> Optional[ArtifactItem]:
        """Get artifact by path"""
        for artifact in self.artifacts:
            if artifact.path == path:
                return artifact
        return None
    
    def get_artifacts_by_type(self, artifact_type: ArtifactType) -> List[ArtifactItem]:
        """Get all artifacts of a specific type"""
        return [artifact for artifact in self.artifacts if artifact.type == artifact_type]
    
    def get_primary_model_artifact(self) -> Optional[ArtifactItem]:
        """Get the primary model artifact"""
        model_artifacts = self.get_artifacts_by_type(ArtifactType.MODEL)
        if model_artifacts:
            # Return the first model artifact, or one with 'model' in the name
            for artifact in model_artifacts:
                if 'model' in artifact.path.lower():
                    return artifact
            return model_artifacts[0]
        return None
    
    def compute_manifest_hash(self) -> str:
        """Compute SHA256 hash of manifest content (excluding signatures)"""
        import hashlib
        import json
        
        # Create a copy without signatures for hashing
        manifest_dict = self.model_dump(exclude={'signatures', 'hashes'})
        
        # Sort keys for deterministic hashing
        manifest_json = json.dumps(manifest_dict, sort_keys=True, default=str)
        return hashlib.sha256(manifest_json.encode()).hexdigest()
    
    def is_signed(self) -> bool:
        """Check if manifest has valid signatures"""
        return bool(self.signatures and len(self.signatures) > 0)
    
    def get_signature_by_fingerprint(self, fingerprint: str) -> Optional[SignatureInfo]:
        """Get signature by public key fingerprint"""
        if not self.signatures:
            return None
        
        for signature in self.signatures:
            if signature.public_key_fingerprint == fingerprint:
                return signature
        return None
    
    def add_signature(self, signature: SignatureInfo) -> None:
        """Add a signature to the manifest"""
        if not self.signatures:
            self.signatures = []
        
        # Remove existing signature with same fingerprint
        self.signatures = [
            sig for sig in self.signatures 
            if sig.public_key_fingerprint != signature.public_key_fingerprint
        ]
        
        # Add new signature
        self.signatures.append(signature)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format matching JSON schema"""
        return self.model_dump(mode='json', exclude_none=True)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ArtifactManifest':
        """Create manifest from dictionary"""
        return cls.model_validate(data)
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'ArtifactManifest':
        """Load manifest from JSON file"""
        import json
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return cls.from_dict(data)
    
    def save_to_file(self, file_path: str) -> None:
        """Save manifest to JSON file"""
        import json
        
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2, default=str)