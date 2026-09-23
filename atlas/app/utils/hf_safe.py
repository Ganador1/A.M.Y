"""Helpers para cargar componentes de Hugging Face con tolerancia a fallos/offline."""

from __future__ import annotations

import logging
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)


def _hf_disabled() -> bool:
    """Determina si las integraciones HF deben estar deshabilitadas."""
    flag = os.getenv("AXIOM_DISABLE_HF", "0").lower() in {"1", "true", "yes"}
    offline = os.getenv("HF_HUB_OFFLINE", "0").lower() in {"1", "true", "yes"}
    return flag or offline


def safe_load_pipeline(task: str, model: str, **kwargs: Any) -> Any:
    """Carga `transformers.pipeline` de forma segura; devuelve None en caso de fallo."""
    if _hf_disabled():
        logger.warning("HF pipeline deshabilitado por configuración (task=%s, model=%s)", task, model)
        return None

    try:
        from transformers import pipeline  # type: ignore

        return pipeline(task, model=model, **kwargs)
    except Exception as exc:  # pragma: no cover - entornos sin red/modelos
        logger.warning(
            "No se pudo cargar pipeline HF (task=%s, model=%s): %s", task, model, exc
        )
        return None


def safe_load_tokenizer(model: str, **kwargs: Any) -> Optional[Any]:
    """Carga `AutoTokenizer` y devuelve None si falla."""
    if _hf_disabled():
        logger.warning("HF tokenizer deshabilitado por configuración (model=%s)", model)
        return None

    try:
        from transformers import AutoTokenizer  # type: ignore

        return AutoTokenizer.from_pretrained(model, **kwargs)
    except Exception as exc:  # pragma: no cover
        logger.warning("No se pudo cargar tokenizer HF (model=%s): %s", model, exc)
        return None


def safe_load_seq2seq_model(model: str, device: Any = None, **kwargs: Any) -> Optional[Any]:
    """Carga `AutoModelForSeq2SeqLM` con tolerancia a fallos."""
    if _hf_disabled():
        logger.warning("HF seq2seq model deshabilitado por configuración (model=%s)", model)
        return None

    try:
        from transformers import AutoModelForSeq2SeqLM  # type: ignore

        loaded_model = AutoModelForSeq2SeqLM.from_pretrained(model, **kwargs)
        if device is not None:
            try:
                loaded_model = loaded_model.to(device)
            except Exception as exc:  # pragma: no cover
                logger.warning("No se pudo mover el modelo a %s: %s", device, exc)
        return loaded_model
    except Exception as exc:  # pragma: no cover
        logger.warning("No se pudo cargar seq2seq model HF (model=%s): %s", model, exc)
        return None


def configure_offline_mode() -> None:
    """Parchea transformers para modo offline/generar stubs.

    Importante: *no* debemos importar el paquete real `transformers` cuando
    `AXIOM_DISABLE_HF` esté activo, porque su import puede ser lento y causar
    bloqueos en la recolección de tests. En su lugar creamos un módulo stub y lo
    registramos en `sys.modules` para que futuros imports usen el stub.
    """
    if not _hf_disabled():
        return

    import sys
    import types

    def _stub_pipeline(*args: Any, **kwargs: Any):  # pragma: no cover - stub
        class _Stub:
            def __call__(self, inputs: Any, *a: Any, **kw: Any) -> Any:
                if isinstance(inputs, list):
                    return [{"label": "NEUTRAL", "score": 0.5} for _ in inputs]
                return {"label": "NEUTRAL", "score": 0.5}

        logger.warning("usando pipeline HF stub (offline)")
        return _Stub()

    class _StubTokenizer:
        @staticmethod
        def from_pretrained(name: str, **kwargs: Any) -> Any:  # pragma: no cover - stub
            logger.warning("AutoTokenizer.from_pretrained stub called for %s", name)

            class _T:
                def __call__(self, texts, **kw):
                    # Minimal tokenization placeholder
                    if isinstance(texts, list):
                        return {"input_ids": [[0] for _ in texts]}
                    return {"input_ids": [0]}

                def encode(self, text: str, **kw):
                    return [0]

            return _T()

    class _StubModel:
        @staticmethod
        def from_pretrained(name: str, **kwargs: Any) -> Any:  # pragma: no cover - stub
            logger.warning("AutoModel.from_pretrained stub called for %s", name)

            class _M:
                def to(self, device: Any) -> "_M":
                    # No-op for device transfer
                    return self

                def eval(self) -> "_M":
                    # No-op model.eval()
                    return self

                def __call__(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
                    return {"last_hidden_state": None}

            return _M()

    module_name = "transformers"

    class _StubModelSeqCls:
        @staticmethod
        def from_pretrained(name: str, **kwargs: Any) -> Any:
            logger.warning("AutoModelForSequenceClassification.from_pretrained stub called for %s", name)
            class _M:
                def to(self, device: Any) -> "_M":
                    return self
                def eval(self) -> "_M":
                    return self
                def __call__(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
                    return {"logits": None}
            return _M()

    class _StubModelCausalLM:
        @staticmethod
        def from_pretrained(name: str, **kwargs: Any) -> Any:
            logger.warning("AutoModelForCausalLM.from_pretrained stub called for %s", name)
            class _M:
                def to(self, device: Any) -> "_M":
                    return self
                def eval(self) -> "_M":
                    return self
                def __call__(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
                    return {"logits": None}
            return _M()

    class _StubModelTokenCls:
        @staticmethod
        def from_pretrained(name: str, **kwargs: Any) -> Any:
            logger.warning("AutoModelForTokenClassification.from_pretrained stub called for %s", name)
            class _M:
                def to(self, device: Any) -> "_M":
                    return self
                def eval(self) -> "_M":
                    return self
                def __call__(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
                    return {"logits": None}
            return _M()

    if module_name in sys.modules:
        # El paquete ya está cargado; parcheamos la función pipeline y clases directamente
        try:
            mod = sys.modules[module_name]
            setattr(mod, "pipeline", _stub_pipeline)
            setattr(mod, "AutoTokenizer", _StubTokenizer)
            setattr(mod, "AutoModelForSeq2SeqLM", _StubModel)
            setattr(mod, "AutoModel", _StubModel)
            setattr(mod, "AutoModelForSequenceClassification", _StubModelSeqCls)
            setattr(mod, "AutoModelForCausalLM", _StubModelCausalLM)
            setattr(mod, "AutoModelForTokenClassification", _StubModelTokenCls)
        except Exception:
            logger.exception("No se pudo parchear el paquete transformers en sys.modules")
    else:
        # Insertamos un módulo stub ligero para evitar que se importe el paquete
        stub = types.ModuleType(module_name)
        stub.pipeline = _stub_pipeline
        stub.AutoTokenizer = _StubTokenizer
        stub.AutoModelForSeq2SeqLM = _StubModel
        stub.AutoModel = _StubModel
        stub.AutoModelForSequenceClassification = _StubModelSeqCls
        stub.AutoModelForCausalLM = _StubModelCausalLM
        stub.AutoModelForTokenClassification = _StubModelTokenCls
        sys.modules[module_name] = stub
        # Submódulos comunes que otros paquetes importan directamente
        pipelines_mod = types.ModuleType(module_name + ".pipelines")
        pipelines_mod.pipeline = _stub_pipeline
        sys.modules[module_name + ".pipelines"] = pipelines_mod
        logger.debug("Registrado stub de 'transformers' y submódulos en sys.modules (offline)")
