"""
Data Analysis Skill — Download public datasets and analyze them reproducibly.

Because the sandbox runs with --network=none, datasets are downloaded on the
host and then passed into the sandbox for analysis. Provenance is tracked for
every dataset and every analysis run.
"""
import hashlib
import json
import time
import urllib.request
from pathlib import Path

import structlog

from sandbox.executor import SandboxExecutor

log = structlog.get_logger()

DATASETS_DIR = Path("data/datasets")
DATASETS_DIR.mkdir(parents=True, exist_ok=True)
ANALYSES_DIR = Path("data/experiments")
ANALYSES_DIR.mkdir(parents=True, exist_ok=True)


class DataAnalysisSkill:
    """Download, cache, and analyze public datasets."""

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.executor = SandboxExecutor(self.config)

    def download_file(self, url: str, filename: str | None = None) -> Path:
        """Download a file to data/datasets/ and return its path."""
        if filename is None:
            filename = url.split("/")[-1] or "download"
        target = DATASETS_DIR / filename

        if target.exists():
            log.info("dataset.cache_hit", path=str(target))
            return target

        log.info("dataset.downloading", url=url, target=str(target))
        req = urllib.request.Request(url, headers={"User-Agent": "AMY-Research-Agent/1.0"})
        with urllib.request.urlopen(req, timeout=60) as response:
            target.write_bytes(response.read())
        log.info("dataset.downloaded", path=str(target), size=target.stat().st_size)
        return target

    def _compute_id(self, code: str, dataset_paths: list[str]) -> str:
        payload = json.dumps({"code": code, "datasets": dataset_paths}, sort_keys=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]

    async def analyze_csv(
        self,
        dataset_path: Path,
        description: str,
        analysis_type: str = "summary",
        target_column: str | None = None,
        group_column: str | None = None,
    ) -> dict:
        """
        Run a sandboxed analysis on a CSV file.
        analysis_type: 'summary', 'correlation', 'group_comparison', 'histograms'
        """
        if not dataset_path.exists():
            return {"success": False, "error": f"Dataset not found: {dataset_path}"}

        experiment_id = self._compute_id(analysis_type, [str(dataset_path.resolve())])
        work_dir = ANALYSES_DIR / experiment_id
        work_dir.mkdir(parents=True, exist_ok=True)

        # Copy dataset into the work directory so Docker can mount it
        local_data = work_dir / dataset_path.name
        if not local_data.exists():
            local_data.write_bytes(dataset_path.read_bytes())

        if analysis_type == "summary":
            code = f"""import pandas as pd
import json

df = pd.read_csv("{dataset_path.name}")
result = {{
    "shape": df.shape,
    "columns": df.columns.tolist(),
    "summary": df.describe().to_dict(),
    "missing": df.isnull().sum().to_dict(),
}}
print(json.dumps(result, indent=2))
with open("analysis_results.json", "w") as f:
    json.dump(result, f, indent=2)
"""
        elif analysis_type == "correlation":
            code = f"""import pandas as pd
import json
import numpy as np

df = pd.read_csv("{dataset_path.name}")
numeric_df = df.select_dtypes(include=[np.number])
corr = numeric_df.corr().to_dict()
result = {{"correlation_matrix": corr, "numeric_columns": numeric_df.columns.tolist()}}
print(json.dumps(result, indent=2))
with open("analysis_results.json", "w") as f:
    json.dump(result, f, indent=2)
"""
        elif analysis_type == "group_comparison" and target_column and group_column:
            code = f"""import pandas as pd
import json
from scipy import stats
import numpy as np

df = pd.read_csv("{dataset_path.name}")
groups = df["{group_column}"].dropna().unique().tolist()
numeric_data = []
for g in groups:
    subset = df[df["{group_column}"] == g]["{target_column}"].dropna()
    numeric_data.append(subset.tolist())

if len(numeric_data) >= 2 and all(len(g) > 1 for g in numeric_data[:2]):
    stat, pvalue = stats.ttest_ind(numeric_data[0], numeric_data[1])
else:
    stat, pvalue = None, None

result = {{
    "groups": groups,
    "group_sizes": [len(g) for g in numeric_data],
    "group_means": [float(np.mean(g)) if len(g) > 0 else None for g in numeric_data],
    "t_statistic": float(stat) if stat is not None else None,
    "pvalue": float(pvalue) if pvalue is not None else None,
}}
print(json.dumps(result, indent=2))
with open("analysis_results.json", "w") as f:
    json.dump(result, f, indent=2)
"""
        elif analysis_type == "histograms":
            code = f"""import pandas as pd
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("{dataset_path.name}")
numeric_df = df.select_dtypes(include=[np.number])
fig_paths = []
for col in numeric_df.columns:
    plt.figure()
    numeric_df[col].hist(bins=20)
    plt.title(col)
    plt.savefig(f"hist_{{col}}.png")
    plt.close()
    fig_paths.append(f"hist_{{col}}.png")

result = {{"histograms": fig_paths, "numeric_columns": numeric_df.columns.tolist()}}
print(json.dumps(result, indent=2))
with open("analysis_results.json", "w") as f:
    json.dump(result, f, indent=2)
"""
        else:
            code = f"""import pandas as pd
import json

df = pd.read_csv("{dataset_path.name}")
result = {{"shape": df.shape, "columns": df.columns.tolist()}}
print(json.dumps(result, indent=2))
with open("analysis_results.json", "w") as f:
    json.dump(result, f, indent=2)
"""

        # Run inside Docker, mounting the work directory
        result = await self.executor.execute(code, language="python")

        provenance = {
            "experiment_id": experiment_id,
            "description": description,
            "timestamp": time.time(),
            "dataset": str(local_data),
            "analysis_type": analysis_type,
            "success": result.get("success"),
            "stdout": result.get("stdout", ""),
            "stderr": result.get("stderr", ""),
            "result_files": result.get("result_files", {}),
        }
        prov_path = work_dir / "provenance.json"
        prov_path.write_text(json.dumps(provenance, indent=2), encoding="utf-8")

        return {
            "experiment_id": experiment_id,
            **result,
            "provenance_path": str(prov_path),
        }

    async def run_custom_analysis(
        self,
        dataset_paths: list[Path],
        code: str,
        description: str,
    ) -> dict:
        """Run arbitrary analysis code against one or more local datasets."""
        dataset_strs = [str(p.resolve()) for p in dataset_paths]
        experiment_id = self._compute_id(code, dataset_strs)
        work_dir = ANALYSES_DIR / experiment_id
        work_dir.mkdir(parents=True, exist_ok=True)

        for p in dataset_paths:
            local = work_dir / p.name
            if not local.exists():
                local.write_bytes(p.read_bytes())

        result = await self.executor.execute(code, language="python")

        provenance = {
            "experiment_id": experiment_id,
            "description": description,
            "timestamp": time.time(),
            "datasets": dataset_strs,
            "code": code,
            "success": result.get("success"),
            "stdout": result.get("stdout", ""),
            "stderr": result.get("stderr", ""),
            "result_files": result.get("result_files", {}),
        }
        prov_path = work_dir / "provenance.json"
        prov_path.write_text(json.dumps(provenance, indent=2), encoding="utf-8")

        return {
            "experiment_id": experiment_id,
            **result,
            "provenance_path": str(prov_path),
        }
