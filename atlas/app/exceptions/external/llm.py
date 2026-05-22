"""LLM Exceptions"""

from app.exceptions.base import AtlasExternalError


class LLMError(AtlasExternalError):
    """Base LLM error"""
    pass


class OllamaUnavailableError(LLMError):
    """Ollama service not responding"""
    pass


# Backwards-compatible aliases expected by tests and callers
class OllamaError(OllamaUnavailableError):
    """Generic Ollama error (backwards-compatible name)."""
    pass


class OpenAIError(LLMError):
    """Errors returned by OpenAI integration (compatibility class)."""
    pass


class ModelNotFoundError(LLMError):
    """Requested model not available"""
    pass


class TokenLimitExceededError(LLMError):
    """Exceeded model token limit"""
    pass