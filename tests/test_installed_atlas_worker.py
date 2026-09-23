"""Exercise the actual worker process against a separate minimal laboratory."""
import json
import os
from pathlib import Path
import subprocess
import sys


def test_worker_honors_separate_atlas_root(tmp_path):
    atlas = tmp_path / 'separate laboratory'
    atlas.mkdir()
    (atlas / 'run_agent_with_tools.py').write_text(
        'class DynamicToolRegistry:\n'
        '    def __init__(self): self.tools = {}\n'
        '    def list_tools(self): return ["external-laboratory-marker"]\n'
    )
    script = Path(__file__).resolve().parents[1] / 'core/atlas_worker.py'
    env = {**os.environ, 'AMY_ATLAS_ROOT': str(atlas)}
    result = subprocess.run([sys.executable, '-B', str(script)],
                            input='{"id": 1, "action": "list_tools"}\n',
                            text=True, capture_output=True, cwd=tmp_path,
                            env=env, timeout=15)
    assert result.returncode == 0, result.stderr
    rows = [json.loads(line) for line in result.stdout.splitlines()]
    assert any(row.get('id') == 1 and row.get('result') == ['external-laboratory-marker'] for row in rows)
