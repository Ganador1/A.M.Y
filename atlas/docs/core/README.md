# 🧱 Core Framework

The `app/core` module provides the fundamental building blocks for the AXIOM application. It handles essential services like database connections, caching, configuration management, and authentication.

## Critical Subsystems

### 💾 Data & State
- **Database (`database.py`, `database_health.py`)**: Manages SQLAlchemy connections, session handling, and health checks for the primary PostgreSQL database.
- **Cache (`cache.py`, `cache_improved.py`)**: Redis-based caching layer for high-speed data retrieval and session storage.

### ⚙️ Configuration
- **Config (`config.py`)**: Centralized configuration management using Pydantic settings. Handles environment variables and secrets.

### 🛡 Security
- **RBAC (`rbac.py`)**: Role-Based Access Control system for managing user permissions.
- **JWT (`jwt_handler.py`)**: JSON Web Token generation and validation for secure API authentication.

### 📊 Observability
- **Logging (`logging_config.py`, `bootstrap_logging.py`)**: Structured logging setup.
- **Telemetry (`telemetry.py`, `metrics.py`)**: OpenTelemetry integration for distributed tracing and Prometheus metrics collection.
- **Rate Limit (`rate_limit.py`)**: Token bucket rate limiting to protect API endpoints.

### ⚡ Concurrency
- **Async Processor (`async_processor.py`)**: Utilities for handling asynchronous background tasks.
- **Executors (`executors.py`)**: Thread and process pool management for CPU-bound tasks.
