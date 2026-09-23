"""
LLM Providers for AXIOM Atlas
Multi-provider support for maximum flexibility
"""

try:
    from app.services.llm_providers.groq_provider import groq_provider, GroqProvider
    GROQ_AVAILABLE = True
except Exception:
    GROQ_AVAILABLE = False
    groq_provider = None
    GroqProvider = None

try:
    from app.services.llm_providers.huggingface_provider import huggingface_provider, HuggingFaceProvider
    HUGGINGFACE_AVAILABLE = True
except Exception:
    HUGGINGFACE_AVAILABLE = False
    huggingface_provider = None
    HuggingFaceProvider = None

__all__ = [
    "groq_provider",
    "GroqProvider",
    "huggingface_provider",
    "HuggingFaceProvider",
    "GROQ_AVAILABLE",
    "HUGGINGFACE_AVAILABLE"
]
