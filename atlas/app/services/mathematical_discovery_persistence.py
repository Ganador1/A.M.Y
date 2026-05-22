"""Stub discovery persistence."""
import json


class DiscoveryPersistence:
    def __init__(self, storage_path: str):
        self.storage_path = storage_path

    def save(self, result):
        with open(self.storage_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"conjecture": result.conjecture, "status": result.status}) + "\n")
