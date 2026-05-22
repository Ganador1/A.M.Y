"""
File Sensor — Monitors local files and directories for changes.

Watches directories for new files, modified files, or data changes.
Useful for detecting new datasets, logs, or research outputs.
"""
import os
from datetime import datetime

import structlog

log = structlog.get_logger()


class FileSensor:
    """Sensor that monitors files and directories for changes."""

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.watch_paths = self.config.get("watch_paths", ["./data", "./papers"])
        self.extensions = self.config.get("extensions", [".json", ".csv", ".txt", ".md", ".py"])
        self._file_states: dict[str, float] = {}  # path -> last_modified
        self._initialized = False

    def _scan_files(self) -> dict[str, float]:
        """Scan watched paths and return file states."""
        states = {}
        for path in self.watch_paths:
            if not os.path.exists(path):
                continue
            if os.path.isfile(path):
                states[path] = os.path.getmtime(path)
            else:
                for root, _, files in os.walk(path):
                    for filename in files:
                        if any(filename.endswith(ext) for ext in self.extensions):
                            filepath = os.path.join(root, filename)
                            states[filepath] = os.path.getmtime(filepath)
        return states

    def sense(self) -> list[dict]:
        """Detect file changes and return observations."""
        current_states = self._scan_files()
        observations = []

        if not self._initialized:
            # First run: just record states
            self._file_states = current_states
            self._initialized = True
            return []

        # Detect new files
        for path, mtime in current_states.items():
            if path not in self._file_states:
                observations.append({
                    "source": "file_sensor",
                    "type": "new_file",
                    "path": path,
                    "timestamp": datetime.now().isoformat(),
                })
            elif mtime > self._file_states[path]:
                observations.append({
                    "source": "file_sensor",
                    "type": "modified_file",
                    "path": path,
                    "timestamp": datetime.now().isoformat(),
                })

        # Detect deleted files
        for path in self._file_states:
            if path not in current_states:
                observations.append({
                    "source": "file_sensor",
                    "type": "deleted_file",
                    "path": path,
                    "timestamp": datetime.now().isoformat(),
                })

        self._file_states = current_states
        return observations
