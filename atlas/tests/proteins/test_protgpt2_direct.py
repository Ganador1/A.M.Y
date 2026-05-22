"""Lightweight ProtGPT2 smoke test.

Converted from interactive script to a single pytest-friendly test with
conditional skip to avoid failing CI when model download isn't possible.
"""

import os
import pytest

try:  # Conditional import to allow environment without transformers
    import torch  # type: ignore
    from transformers import AutoTokenizer, AutoModelForCausalLM  # type: ignore
except Exception:  # pragma: no cover
    AutoTokenizer = None  # type: ignore
    AutoModelForCausalLM = None  # type: ignore
    torch = None  # type: ignore


@pytest.mark.slow
def test_protgpt2_smoke():
    if not os.environ.get("ENABLE_PROTGPT2_TEST"):
        pytest.skip("ProtGPT2 test deshabilitado (definir ENABLE_PROTGPT2_TEST=1 para ejecutarlo)")
    if AutoTokenizer is None or AutoModelForCausalLM is None:
        pytest.skip("transformers not available")

    model_name = "nferruz/ProtGPT2"
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)
    except Exception as e:  # network / cache issues
        pytest.skip(f"model load skipped: {e}")

    inputs = tokenizer("protein", return_tensors="pt")
    if torch is not None:
        with torch.no_grad():
            out = model.generate(inputs['input_ids'], max_length=20, do_sample=True, top_k=20)
    else:  # Fallback (shouldn't happen due to earlier skip)
        out = model.generate(inputs['input_ids'], max_length=20)
    seq = tokenizer.decode(out[0], skip_special_tokens=True)
    assert isinstance(seq, str) and len(seq) >= 1
