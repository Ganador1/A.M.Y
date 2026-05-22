import asyncio
import json
from pathlib import Path
from datetime import datetime

from app.services.experiment_tracking import ExperimentTrackingService
from app.services.dnabert2_service import DNABERT2GenomicsService


async def main():
    exp = ExperimentTrackingService()
    dna = DNABERT2GenomicsService()

    # 1) Iniciar experimento en MLflow
    params = {
        "pipeline": "genomics_motif_scan",
        "dataset": "synthetic_v1",
        "workflow_steps": [
            {"id": "s1", "name": "load_sequence"},
            {"id": "s2", "name": "predict_motifs", "after": "s1"},
            {"id": "s3", "name": "classify_promoter", "after": "s2"},
        ],
    }
    res_start = await exp.start_experiment({
        "action": "start_experiment",
        "name": "DNABERT2_E2E",
        "description": "End-to-end genomics example (motifs + promoter)",
        "parameters": params,
        "tags": {"domain": "genomics", "example": "true"},
    })
    assert res_start.get("success"), res_start
    experiment_id = res_start["experiment_id"]

    # 2) Ejecutar análisis y registrar métricas/artefactos
    seq = "ACGTATATAACGCGTTGCAATATA"
    motifs = dna.predict_motifs({"sequence": seq})
    promoter = dna.classify_promoter({"sequence": seq})

    # Log de métricas clave
    motif_count = sum(len(m.get("positions", [])) for m in motifs.get("motifs", [])) if motifs.get("success") else 0
    exp.log_metric({
        "experiment_id": experiment_id,
        "metric_name": "motif_count",
        "metric_value": motif_count,
        "step": 1,
    })
    exp.log_metric({
        "experiment_id": experiment_id,
        "metric_name": "promoter_probability",
        "metric_value": promoter.get("probability", 0.0),
        "step": 1,
    })

    # Guardar resultados como artefacto
    out_dir = Path("artifacts")
    out_dir.mkdir(exist_ok=True)
    artifact_path = out_dir / f"dnabert2_e2e_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(artifact_path, "w") as f:
        json.dump({"sequence": seq, "motifs": motifs, "promoter": promoter}, f, indent=2)

    exp.log_artifact({
        "experiment_id": experiment_id,
        "artifact_path": str(artifact_path),
        "artifact_name": "results",
    })

    # 3) Finalizar experimento
    exp.end_experiment({
        "experiment_id": experiment_id,
        "status": "completed",
    })

    print("OK MLflow E2E")
    print(json.dumps({
        "experiment_id": experiment_id,
        "artifact": str(artifact_path)
    }, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
