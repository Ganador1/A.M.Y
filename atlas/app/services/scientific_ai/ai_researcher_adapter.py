"""AI Researcher Adapter Service
Bridges AI-Researcher framework outputs into the hypothesis workflow.
Minimal integration: produce structured idea/plan insights for a given hypothesis.
"""
from __future__ import annotations
from typing import Dict, Any
import subprocess
import os
from app.services.base_service import BaseService
import asyncio

class AIResearcherAdapterService(BaseService):
    def __init__(self, root_path: str = "AI-Researcher-main"):
        super().__init__("AIResearcherAdapter")
        self.root_path = root_path
        self.env = os.environ.copy()
        # Placeholders for mapping
        self.modes = {
            "idea": "Reference-Based Ideation",
            "plan": "Detailed Idea Description"
        }

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            action = request_data.get("action")
            if action == "generate_ideas":
                return await self._run_mode(request_data, mode_key="idea")
            if action == "generate_plan":
                return await self._run_mode(request_data, mode_key="plan")
            return {"success": False, "error": f"Unknown action {action}"}
        except (subprocess.SubprocessError, OSError, ValueError) as e:
            return self.handle_error(e, "process_request")

    async def _run_mode(self, data: Dict[str, Any], mode_key: str) -> Dict[str, Any]:
        mode = self.modes.get(mode_key)
        if not mode:
            return {"success": False, "error": f"Unsupported mode {mode_key}"}
        hypothesis = data.get("hypothesis") or {}
        input_text = hypothesis.get("description") or hypothesis.get("title") or data.get("input") or ""
    # reference (paper or prior idea) could be wired in future enhancements
        # Environment variables expected by AI-Researcher
        self.env.setdefault("CATEGORY", data.get("category", "vq"))
        self.env.setdefault("INSTANCE_ID", data.get("instance_id", "rotation_vq"))
        self.env.setdefault("TASK_LEVEL", data.get("task_level", "task1"))
        self.env.setdefault("CONTAINER_NAME", "paper_eval")
        self.env.setdefault("WORKPLACE_NAME", "workplace")
        self.env.setdefault("CACHE_PATH", "cache")
        self.env.setdefault("PORT", "12345")
        self.env.setdefault("MAX_ITER_TIMES", "0")
        script = os.path.join(self.root_path, "main_ai_researcher.py")
        if not os.path.exists(script):
            return {"success": False, "error": "AI Researcher main script not found"}
        cmd = ["python", script]
        try:
            proc = subprocess.run(
                cmd,
                cwd=self.root_path,
                env=self.env,
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )
            raw_out = proc.stdout[-4000:]
            raw_err = proc.stderr[-2000:]
            success = proc.returncode == 0
            return {
                "success": success,
                "mode": mode,
                "stdout_tail": raw_out,
                "stderr_tail": raw_err,
                "returncode": proc.returncode,
                "idea_insight": input_text[:500],
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "timeout executing AI Researcher"}
        except (OSError, subprocess.SubprocessError) as e:  # noqa
            return {"success": False, "error": str(e)}
