from __future__ import annotations
import abc
from typing import Any, Dict, List, Optional

class FetchBatch:
    """Resultado de una obtención paginada."""
    def __init__(self, items: List[Dict[str, Any]], next_state: Optional[Dict[str, Any]], raw_count: int):
        self.items = items
        self.next_state = next_state
        self.raw_count = raw_count

class BaseFetcher(abc.ABC):
    source_name: str

    @abc.abstractmethod
    def fetch_batch(self, state: Optional[Dict[str, Any]] = None) -> FetchBatch:
        """Obtiene un batch y devuelve items normalizados y el siguiente estado.
        state puede incluir cursores/paginadores.
        """
        raise NotImplementedError
