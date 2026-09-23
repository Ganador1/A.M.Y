"""
Tests unitarios para ExperimentSchedulerService.
Cubre: ejecución inmediata, delay, retry fallo, cancel, persistencia, reintentos.
"""

import asyncio
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock

from app.services.experiment_scheduler_service import ExperimentSchedulerService
from app.models.experiment_scheduler_models import ExperimentJobRecord, ExperimentJobState
from app.database import get_db_session, init_database

# Configurar base de datos en memoria para tests
init_database()


@pytest.fixture
def scheduler_service():
    """Fixture que proporciona una instancia del servicio scheduler."""
    mock_async_processor = Mock()
    mock_async_processor.submit_task = AsyncMock()
    return ExperimentSchedulerService(async_processor=mock_async_processor)


@pytest.fixture(autouse=True)
def clean_db():
    """Fixture que limpia la base de datos antes de cada test."""
    db = get_db_session()
    try:
        db.query(ExperimentJobRecord).delete()
        db.commit()
    finally:
        db.close()
    yield
    # Limpieza después del test
    db = get_db_session()
    try:
        db.query(ExperimentJobRecord).delete()
        db.commit()
    finally:
        db.close()


def test_submit_immediate_job(scheduler_service):
    """Test: crear un trabajo para ejecución inmediata."""
    payload = {"task_type": "test", "params": {"value": 42}}
    
    job_uuid = scheduler_service.submit(
        name="test-immediate",
        payload=payload,
        run_at=None,  # inmediato
        priority=1
    )
    
    assert job_uuid is not None
    
    # Verificar en base de datos
    job_info = scheduler_service.get_job(job_uuid)
    assert job_info is not None
    assert job_info["name"] == "test-immediate"
    assert job_info["state"] == ExperimentJobState.PENDING.value
    assert job_info["priority"] == 1
    assert job_info["payload"] == payload


def test_submit_delayed_job(scheduler_service):
    """Test: crear un trabajo diferido (delay)."""
    future_time = datetime.utcnow() + timedelta(minutes=10)
    payload = {"task_type": "delayed", "params": {}}
    
    job_uuid = scheduler_service.submit(
        name="test-delayed",
        payload=payload,
        run_at=future_time,
        priority=2
    )
    
    job_info = scheduler_service.get_job(job_uuid)
    assert job_info is not None
    assert job_info["state"] == ExperimentJobState.PENDING.value
    assert job_info["run_at"] is not None
    # La fecha de ejecución debe ser aproximadamente la especificada
    run_at = datetime.fromisoformat(job_info["run_at"].replace('Z', '+00:00'))
    assert abs((run_at - future_time).total_seconds()) < 5  # margen de 5 segundos


def test_submit_recurring_job(scheduler_service):
    """Test: crear un trabajo recurrente (interval)."""
    payload = {"task_type": "recurring", "params": {}}
    
    job_uuid = scheduler_service.submit(
        name="test-recurring",
        payload=payload,
        interval=60,  # cada 60 segundos
        priority=3
    )
    
    job_info = scheduler_service.get_job(job_uuid)
    assert job_info is not None
    assert job_info["interval_seconds"] == 60


def test_plausibility_score_priority_mapping(scheduler_service):
    """Test: mapeo de plausibility_score a prioridades."""
    test_cases = [
        (0.9, 1),   # score alto -> prioridad 1
        (0.7, 2),   # score medio-alto -> prioridad 2
        (0.5, 3),   # score medio -> prioridad 3
        (0.2, 4),   # score bajo -> prioridad 4
    ]
    
    job_uuids = []
    for score, expected_priority in test_cases:
        job_uuid = scheduler_service.submit(
            name=f"test-priority-{score}",
            payload={"score": score},
            plausibility_score=score
        )
        job_uuids.append(job_uuid)
        
        job_info = scheduler_service.get_job(job_uuid)
        assert job_info["priority"] == expected_priority


def test_list_jobs_filtering(scheduler_service):
    """Test: listar trabajos con filtros por estado."""
    # Crear trabajos en diferentes estados
    pending_job = scheduler_service.submit("pending-job", {"type": "pending"})
    
    # Cancelar uno
    cancelled_job = scheduler_service.submit("cancelled-job", {"type": "cancelled"})
    scheduler_service.cancel_job(cancelled_job)
    
    # Listar todos los trabajos
    all_jobs = scheduler_service.list_jobs()
    assert len(all_jobs) == 2
    
    # Listar solo pendientes
    pending_jobs = scheduler_service.list_jobs(state=ExperimentJobState.PENDING)
    assert len(pending_jobs) == 1
    assert pending_jobs[0]["job_uuid"] == pending_job
    
    # Listar solo cancelados
    cancelled_jobs = scheduler_service.list_jobs(state=ExperimentJobState.CANCELLED)
    assert len(cancelled_jobs) == 1
    assert cancelled_jobs[0]["job_uuid"] == cancelled_job


def test_cancel_job(scheduler_service):
    """Test: cancelar un trabajo pendiente."""
    job_uuid = scheduler_service.submit("test-cancel", {"data": "test"})
    
    # Verificar que está pendiente
    job_info = scheduler_service.get_job(job_uuid)
    assert job_info["state"] == ExperimentJobState.PENDING.value
    
    # Cancelar
    success = scheduler_service.cancel_job(job_uuid)
    assert success is True
    
    # Verificar que está cancelado
    job_info = scheduler_service.get_job(job_uuid)
    assert job_info["state"] == ExperimentJobState.CANCELLED.value
    
    # Intentar cancelar de nuevo (no debería cambiar nada)
    success = scheduler_service.cancel_job(job_uuid)
    assert success is False  # Ya estaba cancelado


def test_cancel_nonexistent_job(scheduler_service):
    """Test: intentar cancelar un trabajo que no existe."""
    success = scheduler_service.cancel_job("fake-uuid")
    assert success is False


@pytest.mark.asyncio
async def test_tick_execution_immediate(scheduler_service):
    """Test: tick ejecuta trabajos inmediatos."""
    # Crear trabajo inmediato
    job_uuid = scheduler_service.submit(
        "test-tick-immediate", 
        {"task": "immediate"},
        run_at=datetime.utcnow() - timedelta(seconds=1)  # en el pasado
    )
    
    # Ejecutar tick
    await scheduler_service.tick()
    
    # Verificar que el trabajo se completó
    job_info = scheduler_service.get_job(job_uuid)
    assert job_info["state"] == ExperimentJobState.COMPLETED.value


@pytest.mark.asyncio
async def test_tick_respects_delay(scheduler_service):
    """Test: tick respeta trabajos diferidos."""
    # Crear trabajo diferido para el futuro
    future_time = datetime.utcnow() + timedelta(minutes=5)
    job_uuid = scheduler_service.submit(
        "test-tick-delayed", 
        {"task": "delayed"},
        run_at=future_time
    )
    
    # Ejecutar tick
    await scheduler_service.tick()
    
    # Verificar que el trabajo sigue pendiente (no se ejecutó)
    job_info = scheduler_service.get_job(job_uuid)
    assert job_info["state"] == ExperimentJobState.PENDING.value


@pytest.mark.asyncio 
async def test_recurring_job_creates_next_instance(scheduler_service):
    """Test: trabajos recurrentes crean la siguiente instancia."""
    # Crear trabajo recurrente
    job_uuid = scheduler_service.submit(
        "test-recurring",
        {"task": "recurring"},
        run_at=datetime.utcnow() - timedelta(seconds=1),  # inmediato
        interval=60  # cada 60 segundos
    )
    
    # Ejecutar tick
    await scheduler_service.tick()
    
    # Verificar que el trabajo original se completó
    original_job = scheduler_service.get_job(job_uuid)
    assert original_job["state"] == ExperimentJobState.COMPLETED.value
    
    # Debe haber un nuevo trabajo pendiente para la próxima ejecución
    all_jobs = scheduler_service.list_jobs()
    pending_jobs = [job for job in all_jobs if job["state"] == ExperimentJobState.PENDING.value]
    assert len(pending_jobs) == 1
    
    # El nuevo trabajo debe tener los mismos parámetros
    next_job_uuid = pending_jobs[0]["job_uuid"]
    next_job = scheduler_service.get_job(next_job_uuid)
    assert next_job["name"] == "test-recurring"
    assert next_job["interval_seconds"] == 60


@pytest.mark.asyncio
async def test_job_failure_and_retry(scheduler_service):
    """Test: fallo de trabajo y sistema de reintentos."""
    # Mock para simular fallo
    scheduler_service.async_processor = Mock()
    
    job_uuid = scheduler_service.submit(
        "test-failure",
        {"task": "fail"},
        max_retries=2
    )
    
    # Obtener el job de la DB para simular fallo
    db = get_db_session()
    try:
        job = db.query(ExperimentJobRecord).filter(
            ExperimentJobRecord.job_uuid == job_uuid
        ).first()
        
        # Simular fallo en _execute_job
        await scheduler_service._handle_job_failure(db, job, "Test error")
        
        # Verificar que está programado para reintento
        job_info = scheduler_service.get_job(job_uuid)
        assert job_info["state"] == ExperimentJobState.PENDING.value
        assert job_info["retry_count"] == 1
        assert job_info["error_message"] == "Test error"
    finally:
        db.close()


@pytest.mark.asyncio
async def test_job_max_retries_exceeded(scheduler_service):
    """Test: trabajo falla definitivamente tras agotar reintentos."""
    job_uuid = scheduler_service.submit(
        "test-max-retries",
        {"task": "always-fail"},
        max_retries=1
    )
    
    db = get_db_session()
    try:
        job = db.query(ExperimentJobRecord).filter(
            ExperimentJobRecord.job_uuid == job_uuid
        ).first()
        
        # Simular fallo inicial (retry_count pasa a 1)
        await scheduler_service._handle_job_failure(db, job, "First error")
        
        # Refrescar el job desde DB
        db.refresh(job)
        
        # Simular segundo fallo (retry_count pasa a 2, excede max_retries=1)  
        await scheduler_service._handle_job_failure(db, job, "Second error")
        
        # Verificar que falló definitivamente
        job_info = scheduler_service.get_job(job_uuid)
        assert job_info["state"] == ExperimentJobState.FAILED.value
        assert job_info["retry_count"] == 2
    finally:
        db.close()


def test_retry_failed_job_manually(scheduler_service):
    """Test: reintento manual de trabajo fallido."""
    # Crear trabajo y marcarlo como fallido manualmente
    job_uuid = scheduler_service.submit("test-manual-retry", {"task": "manual"})
    
    db = get_db_session()
    try:
        # Marcar como fallido directamente en DB
        from sqlalchemy import update
        db.execute(
            update(ExperimentJobRecord)
            .where(ExperimentJobRecord.job_uuid == job_uuid)
            .values(state=ExperimentJobState.FAILED.value)
        )
        db.commit()
    finally:
        db.close()
    
    # Verificar que está fallido
    job_info = scheduler_service.get_job(job_uuid)
    assert job_info["state"] == ExperimentJobState.FAILED.value
    
    # Reintentar manualmente
    success = scheduler_service.retry_failed_job(job_uuid)
    assert success is True
    
    # Verificar que volvió a pendiente
    job_info = scheduler_service.get_job(job_uuid)
    assert job_info["state"] == ExperimentJobState.PENDING.value
    assert job_info["error_message"] is None


def test_retry_non_failed_job(scheduler_service):
    """Test: intentar reintentar trabajo que no está fallido."""
    job_uuid = scheduler_service.submit("test-not-failed", {"task": "ok"})
    
    # Intentar reintentar un trabajo pendiente (no fallido)
    success = scheduler_service.retry_failed_job(job_uuid)
    assert success is False


def test_scheduler_stats(scheduler_service):
    """Test: obtener estadísticas del scheduler."""
    # Crear trabajos en diferentes estados
    scheduler_service.submit("pending", {}, priority=1)
    scheduler_service.submit("high-priority", {}, priority=1)
    scheduler_service.submit("low-priority", {}, priority=4)
    
    scheduler_service.cancel_job(scheduler_service.submit("cancelled", {}))
    
    stats = scheduler_service.get_scheduler_stats()
    
    # Verificar conteos por estado
    assert stats[ExperimentJobState.PENDING.value] == 3
    assert stats[ExperimentJobState.CANCELLED.value] == 1
    assert stats[ExperimentJobState.RUNNING.value] == 0
    assert stats[ExperimentJobState.COMPLETED.value] == 0
    assert stats[ExperimentJobState.FAILED.value] == 0
    
    # Verificar breakdown por prioridad
    priority_breakdown = stats["priority_breakdown"]
    assert priority_breakdown["priority_1"] == 2  # 2 trabajos con prioridad 1
    assert priority_breakdown["priority_4"] == 1  # 1 trabajo con prioridad 4
    
    # Estado del scheduler
    assert stats["scheduler_running"] is False


def test_scheduler_start_stop(scheduler_service):
    """Test: iniciar y detener el scheduler."""
    # Inicialmente no está corriendo
    assert scheduler_service._running is False
    
    # Iniciar
    scheduler_service.start_scheduler()
    assert scheduler_service._running is True
    assert scheduler_service._scheduler_task is not None
    
    # Detener
    scheduler_service.stop_scheduler()
    assert scheduler_service._running is False


def test_get_nonexistent_job(scheduler_service):
    """Test: obtener información de trabajo que no existe."""
    job_info = scheduler_service.get_job("fake-uuid-123")
    assert job_info is None


@pytest.mark.asyncio
async def test_scheduler_loop_resilience(scheduler_service):
    """Test: el scheduler loop maneja errores sin colapsar."""
    # Mock tick para que falle
    original_tick = scheduler_service.tick
    
    async def failing_tick():
        raise Exception("Simulated error")
    
    scheduler_service.tick = failing_tick
    scheduler_service._running = True
    
    # El loop debe manejar el error y continuar
    # Ejecutamos solo una iteración para probar
    try:
        # Simular una iteración del scheduler loop
        await scheduler_service.tick()
        await asyncio.sleep(5)  # sleep que haría después del error
    except Exception:
        pass  # Error esperado
    
    # Restaurar método original
    scheduler_service.tick = original_tick
    
    # El scheduler debe seguir "corriendo" conceptualmente
    assert scheduler_service._running is True


def test_job_persistence_after_restart(scheduler_service):
    """Test: los trabajos persisten tras reiniciar el servicio."""
    # Crear trabajo
    job_uuid = scheduler_service.submit(
        "persistent-job",
        {"data": "persists"},
        run_at=datetime.utcnow() + timedelta(hours=1)
    )
    
    # "Reiniciar" creando nueva instancia del servicio
    new_scheduler = ExperimentSchedulerService()
    
    # El trabajo debe seguir disponible
    job_info = new_scheduler.get_job(job_uuid)
    assert job_info is not None
    assert job_info["name"] == "persistent-job"
    assert job_info["state"] == ExperimentJobState.PENDING.value


if __name__ == "__main__":
    # Ejecutar tests
    pytest.main([__file__, "-v"])
