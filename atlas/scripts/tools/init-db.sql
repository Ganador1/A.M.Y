-- AXIOM META 4 - Database Initialization Script
-- ==============================================
-- Inicialización completa de PostgreSQL para Phase 3 + Phase 4

-- Crear base de datos si no existe
-- Nota: Esto debe ejecutarse fuera de una transacción

-- Configurar extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Crear esquema para métricas de monitoreo
CREATE SCHEMA IF NOT EXISTS monitoring;

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de cálculos/simulaciones
CREATE TABLE IF NOT EXISTS calculations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    operation_type VARCHAR(100) NOT NULL,
    operation_name VARCHAR(255) NOT NULL,
    input_data JSONB,
    result_data JSONB,
    status VARCHAR(50) DEFAULT 'pending',
    execution_time FLOAT,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para optimización
CREATE INDEX IF NOT EXISTS idx_calculations_user_id ON calculations(user_id);
CREATE INDEX IF NOT EXISTS idx_calculations_status ON calculations(status);
CREATE INDEX IF NOT EXISTS idx_calculations_operation_type ON calculations(operation_type);
CREATE INDEX IF NOT EXISTS idx_calculations_created_at ON calculations(created_at DESC);

-- Tabla de métricas del sistema (Phase 4)
CREATE TABLE IF NOT EXISTS monitoring.system_metrics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    cpu_percent FLOAT,
    memory_percent FLOAT,
    disk_percent FLOAT,
    network_bytes_sent BIGINT,
    network_bytes_recv BIGINT,
    load_average_1m FLOAT,
    load_average_5m FLOAT,
    load_average_15m FLOAT,
    temperature_celsius FLOAT,
    hostname VARCHAR(255)
);

-- Tabla de métricas de aplicación
CREATE TABLE IF NOT EXISTS monitoring.application_metrics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    service_name VARCHAR(100),
    endpoint VARCHAR(255),
    method VARCHAR(10),
    status_code INTEGER,
    response_time FLOAT,
    request_size INTEGER,
    response_size INTEGER,
    user_agent TEXT,
    ip_address INET
);

-- Tabla de alertas del sistema
CREATE TABLE IF NOT EXISTS monitoring.alerts (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    alert_type VARCHAR(100),
    severity VARCHAR(20) CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    message TEXT,
    service_name VARCHAR(100),
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB
);

-- Tabla de logs de auditoría (Phase 4)
CREATE TABLE IF NOT EXISTS monitoring.audit_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100),
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    details JSONB
);

-- Tabla de sesiones de usuario (Phase 4)
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT
);

-- Tabla de configuraciones del sistema
CREATE TABLE IF NOT EXISTS system_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(255) UNIQUE NOT NULL,
    config_value JSONB,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER REFERENCES users(id) ON DELETE SET NULL
);

-- Índices para optimización de monitoreo
CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON monitoring.system_metrics(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_application_metrics_timestamp ON monitoring.application_metrics(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_application_metrics_service ON monitoring.application_metrics(service_name);
CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON monitoring.alerts(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_resolved ON monitoring.alerts(resolved);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON monitoring.audit_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);

-- Políticas de retención de datos (Phase 4)
-- Crear función para limpieza automática
CREATE OR REPLACE FUNCTION monitoring.cleanup_old_data()
RETURNS void AS $$
BEGIN
    -- Limpiar métricas del sistema mayores a 30 días
    DELETE FROM monitoring.system_metrics
    WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '30 days';

    -- Limpiar métricas de aplicación mayores a 7 días
    DELETE FROM monitoring.application_metrics
    WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '7 days';

    -- Limpiar alertas resueltas mayores a 90 días
    DELETE FROM monitoring.alerts
    WHERE resolved = true AND timestamp < CURRENT_TIMESTAMP - INTERVAL '90 days';

    -- Limpiar logs de auditoría mayores a 1 año
    DELETE FROM monitoring.audit_logs
    WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '1 year';

    -- Limpiar sesiones expiradas
    DELETE FROM user_sessions
    WHERE expires_at < CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

-- Insertar usuario administrador por defecto
INSERT INTO users (username, email, hashed_password, full_name, is_superuser)
VALUES ('admin', 'admin@axiom.local', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewfLkIwF/4zRzKC', 'AXIOM Administrator', true)
ON CONFLICT (username) DO NOTHING;

-- Insertar configuraciones por defecto
INSERT INTO system_config (config_key, config_value, description) VALUES
('system.maintenance_mode', 'false', 'Modo de mantenimiento del sistema'),
('monitoring.enabled', 'true', 'Habilitar monitoreo del sistema'),
('security.rate_limit_requests', '100', 'Límite de requests por minuto'),
('cache.ttl_seconds', '3600', 'TTL por defecto del cache en segundos'),
('database.max_connections', '20', 'Máximo número de conexiones a la base de datos')
ON CONFLICT (config_key) DO NOTHING;

-- Crear vistas útiles para monitoreo
CREATE OR REPLACE VIEW monitoring.system_health AS
SELECT
    DATE_TRUNC('hour', timestamp) as hour,
    AVG(cpu_percent) as avg_cpu,
    AVG(memory_percent) as avg_memory,
    AVG(disk_percent) as avg_disk,
    COUNT(*) as samples_count
FROM monitoring.system_metrics
WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY DATE_TRUNC('hour', timestamp)
ORDER BY hour DESC;

CREATE OR REPLACE VIEW monitoring.api_performance AS
SELECT
    service_name,
    endpoint,
    method,
    AVG(response_time) as avg_response_time,
    COUNT(*) as total_requests,
    SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as error_count
FROM monitoring.application_metrics
WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
GROUP BY service_name, endpoint, method
ORDER BY avg_response_time DESC;

-- Comentarios en las tablas para documentación
COMMENT ON TABLE users IS 'Usuarios del sistema AXIOM';
COMMENT ON TABLE calculations IS 'Registro de cálculos y simulaciones ejecutadas';
COMMENT ON TABLE monitoring.system_metrics IS 'Métricas del sistema operativo';
COMMENT ON TABLE monitoring.application_metrics IS 'Métricas de rendimiento de la aplicación';
COMMENT ON TABLE monitoring.alerts IS 'Alertas y notificaciones del sistema';
COMMENT ON TABLE monitoring.audit_logs IS 'Logs de auditoría para compliance';
COMMENT ON TABLE user_sessions IS 'Sesiones activas de usuarios';
COMMENT ON TABLE system_config IS 'Configuraciones del sistema';

-- Otorgar permisos necesarios
GRANT USAGE ON SCHEMA monitoring TO axiom_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA monitoring TO axiom_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA monitoring TO axiom_user;

-- Notificar finalización
DO $$
BEGIN
    RAISE NOTICE 'AXIOM META 4 database initialization completed successfully';
    RAISE NOTICE 'Created tables: users, calculations, system_metrics, application_metrics, alerts, audit_logs, user_sessions, system_config';
    RAISE NOTICE 'Created indexes and views for optimal performance';
    RAISE NOTICE 'Default admin user created: admin@axiom.local';
END $$;
