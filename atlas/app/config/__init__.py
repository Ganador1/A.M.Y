"""
AXIOM Configuration Package
Centraliza la gestión de configuración y mantiene compatibilidad con
``from app.core.config import settings`` tras la conversión a paquete.

Este archivo integra el contenido previo de ``app/config.py`` para evitar
el conflicto de nombres (module vs package) que rompía los imports.

Ahora incluye soporte para configuraciones específicas por ambiente.
"""

import logging
from typing import Optional, List
from pydantic import BaseModel, field_validator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import secrets
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# Cargar configuración específica del ambiente ANTES de crear Settings
def _load_environment_config():
    """Carga configuración específica del ambiente"""
    env = os.getenv("ENV", "development")
    
    # Mapear ambientes a archivos
    env_files = {
        "development": "env.development",
        "dev": "env.development", 
        "testing": "env.testing",
        "test": "env.testing",
        "staging": "env.staging",
        "stage": "env.staging",
        "production": "env.production",
        "prod": "env.production"
    }
    
    env_file = env_files.get(env.lower(), "env.development")
    
    # Buscar el archivo en config/environments/
    config_dir = Path(__file__).parent.parent.parent / "config" / "environments"
    env_path = config_dir / env_file
    
    if env_path.exists():
        logger.info("Loading configuration for environment '%s' from %s", env, env_path)
        
        # Leer y cargar variables de entorno
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                if key not in os.environ:
                    os.environ[key] = value
    else:
        logger.warning("Environment configuration file not found: %s (env=%s). Falling back to defaults.", env_path, env)

# Cargar configuración del ambiente
_load_environment_config()

# Validar configuraciones YAML al inicio
try:
    from .startup_validation import validate_configuration_on_startup
    validate_configuration_on_startup()
except Exception as e:
    logger.warning("Configuration validation error: %s. Continuing with default configuration.", e, exc_info=True)

# Inicializar Secrets Manager
try:
    from .secrets_manager import create_secrets_manager
    secrets_manager = create_secrets_manager()
    key_info = secrets_manager.get_key_info()
    logger.info("Secrets Manager initialized using key file: %s", key_info.get("key_file"))
except Exception as e:
    logger.warning("Failed to initialize Secrets Manager: %s", e, exc_info=True)
    secrets_manager = None


class Settings(BaseSettings):
	"""Application settings"""

	# Server Configuration
	host: str = "0.0.0.0"
	port: int = 8002
	debug: bool = False
	reload: bool = False

	# API Configuration
	api_v1_prefix: str = "/api"
	docs_url: str = "/docs"
	redoc_url: str = "/redoc"
	openapi_url: str = "/openapi.json"
	# CORS
	cors_allow_origins: List[str] = [
		"http://localhost",
		"http://127.0.0.1",
		"http://localhost:8002",
		"http://127.0.0.1:8002",
	]

	# Security
	# Prefer env var; otherwise generate a random token at startup (non-persistent)
	secret_key: str = Field(default_factory=lambda: os.getenv("SECRET_KEY", "") or secrets.token_urlsafe(32))
	algorithm: str = "HS256"
	access_token_expire_minutes: int = 30
	# Simple Bearer auth for sensitive routes (opt-in via env)
	enable_auth_routes: bool = Field(default=False)
	api_bearer_token: Optional[str] = Field(default=None)

	# Database Configuration
	database_url: Optional[str] = Field(default="postgresql://giovanniarangio@localhost:5432/axiom_meta4")
	database_pool_size: int = 10
	database_max_overflow: int = 20
	database_pool_timeout: int = 30
	database_pool_recycle: int = 3600
	enable_database: bool = Field(default=True)

	# Redis/Cache Configuration
	redis_url: Optional[str] = "redis://localhost:6379"
	redis_db: int = 0
	redis_password: Optional[str] = None
	cache_ttl: int = 300  # 5 minutes default TTL
	enable_redis_cache: bool = True

	# External APIs
	huggingface_api_key: Optional[str] = None
	openai_api_key: Optional[str] = None

	# Agent 2 Bridge Configuration
	agent2_base_url: Optional[str] = Field(default='http://localhost:8000')

	# Local LLM Configuration (Ollama / HF / MLX)
	enable_local_llm: bool = Field(default=True)
	# backends: 'ollama' | 'mlx' (Apple Silicon, mlx-lm) | 'transformers'
	llm_backend: str = Field(default='ollama')
	# Ollama configuration
	ollama_api_url: str = Field(default='http://localhost:11434')
	ollama_model: str = Field(default='mistral:7b')
	# Default HF models (choose small-ish defaults; can be overridden via env)
	# Use a tiny GPT-2 variant for wide compatibility on CPU-only environments
	hf_model_id: str = Field(default='sshleifer/tiny-gpt2')
	# Optional science-tuned alternative (example): BioMistral 7B
	hf_model_id_science: Optional[str] = Field(default=None)  # e.g., 'BioMistral/BioMistral-7B'
	# MLX model identifier or local path (if pre-converted to MLX format)
	mlx_model_id: Optional[str] = Field(default='mlx-community/SmolLM2-135M-Instruct-mlx')  # small MLX model
	llm_max_new_tokens: int = Field(default=384)
	llm_temperature: float = Field(default=0.2)
	# Some repos (e.g., certain Qwen variants) require trust_remote_code
	llm_trust_remote_code: bool = Field(default=True)

	# Computational Limits
	max_computation_time: int = 30  # seconds
	max_plot_points: int = 10000
	max_matrix_size: int = 1000
	max_polynomial_degree: int = 20
	# Request limits (mitigate big form/multipart DoS)
	max_request_bytes: int = Field(default=5 * 1024 * 1024)  # 5MB por defecto

	# Logging
	log_level: str = "INFO"
	log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

	# GPU Configuration
	enable_gpu: bool = True
	gpu_memory_fraction: float = 0.8  # Fraction of GPU memory to use
	gpu_device: Optional[str] = None  # Auto-detect if None
	enable_mps: bool = True  # Enable MPS on Apple Silicon
	enable_cuda: bool = True  # Enable CUDA on NVIDIA GPUs

	# Distributed Computing Configuration
	enable_distributed: bool = False
	distributed_backend: str = "gloo"  # gloo, nccl, mpi
	world_size: int = 1
	rank: int = 0
	master_addr: str = "localhost"
	master_port: int = 12355

	# Advanced Algorithms Configuration
	enable_advanced_algorithms: bool = True
	algorithm_precision: str = "high"  # low, medium, high
	parallel_computation_threshold: int = 1000  # Min size for parallel processing
	memory_optimization_level: str = "auto"  # none, basic, advanced, auto

	
	# Additional Environment Variables (migrated from os.getenv)
	# Security
	system_admin_password: Optional[str] = Field(default=None)
	researcher_password: Optional[str] = Field(default=None)
	lab_operator_password: Optional[str] = Field(default=None)
	integrity_hmac_key: Optional[str] = Field(default=None)
	
	# Telemetry & Observability
	jaeger_port: Optional[str] = Field(default=None)
	console_exporter: bool = Field(default=False)
	otlp_enabled: bool = Field(default=False)
	sentry_profiles_sample_rate: float = Field(default=0.0)
	service_name: str = Field(default="axiom")
	sentry_traces_sample_rate: float = Field(default=0.0)
	service_version: str = Field(default="1.0.0")
	jaeger_enabled: bool = Field(default=False)
	sentry_environment: str = Field(default="development")
	jaeger_host: str = Field(default="localhost")
	hostname: str = Field(default="localhost")
	otlp_endpoint: Optional[str] = Field(default=None)
	otel_enabled: bool = Field(default=False)
	otel_service_name: str = Field(default="axiom")
	otel_exporter_otlp_endpoint: Optional[str] = Field(default=None)
	
	# Logging
	log_level: str = Field(default="INFO")
	
	# Distributed Computing
	kubernetes_namespace: Optional[str] = Field(default=None)
	kubernetes_service_host: Optional[str] = Field(default=None)
	k8s_verify_tls: bool = Field(default=True)
	pytorch_mps_high_watermark_ratio: float = Field(default=0.0)
	master_addr: str = Field(default="localhost")
	rank: int = Field(default=0)
	master_port: int = Field(default=12355)
	world_size: int = Field(default=1)
	
	# Database Additional
	db_user: Optional[str] = Field(default=None)
	db_name: Optional[str] = Field(default=None)
	db_password: Optional[str] = Field(default=None)
	db_port: Optional[str] = Field(default=None)
	db_echo: bool = Field(default=False)
	db_host: Optional[str] = Field(default=None)
	
	# Environment
	atlas_env: str = Field(default="development")

	
	# Additional Environment Variables (Round 2)
	# Literature & APIs
	lit_http_ua: str = Field(default="AXIOM/1.0")
	materials_project_api_key: Optional[str] = Field(default=None)
	lit_http_max_retries: int = Field(default=3)
	openalex_mailto: Optional[str] = Field(default=None)
	lit_http_backoff: float = Field(default=1.0)
	lit_http_timeout: int = Field(default=30)
	
	# Async Tools
	async_tool_fail_fast: bool = Field(default=False)
	async_tool_retry_attempts: int = Field(default=3)
	async_tool_timeout: int = Field(default=30)
	async_tool_max_concurrent: int = Field(default=10)
	
	# Tool Adapter Cache
	tool_adapter_cache_size: int = Field(default=1000)
	tool_adapter_cache_ttl: int = Field(default=300)
	
	# Data Lake
	enable_s3: bool = Field(default=False)
	datalake_root: str = Field(default="/tmp/axiom_datalake")
	
	# Services Configuration
	axiom_skip_autoinit: bool = Field(default=False)
	axiom_config_dir: Optional[str] = Field(default=None)
	mlflow_tracking_uri: Optional[str] = Field(default=None)
	ecl_base_url: Optional[str] = Field(default=None)
	ecl_api_key: Optional[str] = Field(default=None)
	ecl_simulation: bool = Field(default=False)
	
	# System Environment
	user: Optional[str] = Field(default=None)
	shell: Optional[str] = Field(default=None)
	path: Optional[str] = Field(default=None)
	
	# Data Versioning
	allowed_data_root: Optional[str] = Field(default=None)
	strict_data_paths: bool = Field(default=True)
	max_version_file_bytes: int = Field(default=100 * 1024 * 1024)  # 100MB
	
	# Validation
	validation_retention_days: int = Field(default=30)
	validation_snapshot_interval: int = Field(default=3600)  # 1 hour
	
	# Redis
	allow_redis_pickle: bool = Field(default=False)
	
	# Lean4 Integration
	lean_bin: Optional[str] = Field(default=None)
	elan_home: Optional[str] = Field(default=None)
	lean_timeout_ms: int = Field(default=30000)
	
	# Lab Automation
	lab_robot_type: Optional[str] = Field(default=None)
	lab_deck_layout: Optional[str] = Field(default=None)
	lab_simulation: bool = Field(default=False)
	
	# External API Keys
	openai_api_key: Optional[str] = Field(default=None)
	google_api_key: Optional[str] = Field(default=None)
	anthropic_api_key: Optional[str] = Field(default=None)
	mp_api_key: Optional[str] = Field(default=None)

	@field_validator('cors_allow_origins', mode='before')
	@classmethod
	def _parse_cors(cls, v):
		# BaseSettings will handle env var loading automatically
		return v

	model_config = SettingsConfigDict(
		env_file=".env",
		env_file_encoding="utf-8",
		case_sensitive=False,
		env_prefix="",
		extra="ignore"
	)


# Global settings instance (backwards compatible export)
settings = Settings()

__all__ = ["Settings", "settings", "secrets_manager"]
