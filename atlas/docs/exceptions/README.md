# Exception Hierarchy Guide

**AXIOM ATLAS** uses a custom exception hierarchy to provide clear, specific error handling across all domains. This guide explains when and how to use each exception type.

---

## 🎯 Quick Reference

| Exception Type | Use When | Example |
|----------------|----------|---------|
| `BiologyError` | Biology domain errors | Protein analysis fails |
| `ChemistryError` | Chemistry domain errors | Molecular simulation fails |
| `DatabaseError` | DB operations fail | Connection pool exhausted |
| `LLMError` | LLM/AI service fails | Ollama unavailable |
| `InputValidationError` | Invalid user input | Missing required field |
| `EthicsViolationError` | Ethics gate rejects | Dangerous experiment |

---

## 📁 Exception Hierarchy

```
AtlasException (base)
├── AtlasDomainError
│   ├── BiologyError
│   │   ├── ProteinAnalysisError
│   │   ├── SequenceAlignmentError
│   │   ├── GenomicsError
│   │   └── StructurePredictionError
│   ├── ChemistryError
│   │   ├── MolecularDynamicsError
│   │   ├── ReactionSimulationError
│   │   └── QuantumChemistryError
│   ├── PhysicsError
│   │   ├── QuantumSimulationError
│   │   ├── ParticlePhysicsError
│   │   └── ThermodynamicsError
│   ├── MathematicsError
│   │   ├── SymbolicMathError
│   │   └── NumericalError
│   ├── MedicineError
│   ├── NeuroscienceError
│   └── EngineeringError
├── AtlasInfrastructureError
│   ├── DatabaseError
│   │   ├── SessionNotFoundError
│   │   ├── QueryTimeoutError
│   │   └── ConnectionPoolExhaustedError
│   ├── CacheError
│   ├── APIError
│   └── StorageError
├── AtlasExternalError
│   ├── LLMError
│   │   ├── OllamaUnavailableError
│   │   ├── ModelNotFoundError
│   │   └── TokenLimitExceededError
│   ├── ScientificAPIError
│   │   ├── UniProtError
│   │   └── PubChemError
│   └── ServiceUnavailableError
├── AtlasValidationError
│   ├── InputValidationError
│   ├── OutputValidationError
│   └── EthicsViolationError
└── AtlasSecurityError
```

---

## 🔧 Usage Examples

### Biology Domain

```python
from app.exceptions.domain.biology import (
    ProteinAnalysisError,
    StructurePredictionError
)
from app.exceptions.external.scientific_api import UniProtError

async def analyze_protein(uniprot_id: str) -> dict:
    """Analyze protein structure and function."""

    # Validate input
    if not uniprot_id:
        raise InputValidationError(
            "UniProt ID required",
            error_code="MISSING_UNIPROT_ID"
        )

    try:
        # Fetch from external API
        protein_data = await fetch_from_uniprot(uniprot_id)

    except UniProtError as e:
        # External API failed - chain the exception
        raise ProteinAnalysisError(
            f"Failed to fetch protein data for {uniprot_id}",
            error_code="UNIPROT_FETCH_FAILED",
            details={"uniprot_id": uniprot_id},
            cause=e  # Chain original error
        ) from e

    try:
        # Predict structure
        if protein_data['length'] > 2000:
            raise StructurePredictionError(
                "Protein too large for AlphaFold",
                error_code="PROTEIN_TOO_LARGE",
                details={
                    "length": protein_data['length'],
                    "max_length": 2000
                }
            )

        structure = await predict_structure_alphafold(protein_data)

    except MemoryError as e:
        raise StructurePredictionError(
            "Insufficient memory for structure prediction",
            error_code="MEMORY_ERROR",
            cause=e
        ) from e

    return {"protein": protein_data, "structure": structure}
```

### Database Operations

```python
from app.exceptions.infrastructure.database import (
    DatabaseError,
    QueryTimeoutError,
    ConnectionPoolExhaustedError
)

async def get_experiments(db: AsyncSession) -> list:
    """Fetch experiments from database."""

    try:
        result = await asyncio.wait_for(
            db.execute(select(Experiment)),
            timeout=30.0
        )
        return result.scalars().all()

    except asyncio.TimeoutError as e:
        raise QueryTimeoutError(
            "Database query exceeded 30s timeout",
            error_code="QUERY_TIMEOUT",
            details={"timeout": 30, "query": "select experiments"},
            cause=e
        ) from e

    except Exception as e:
        # Last resort fallback
        raise DatabaseError(
            "Unexpected database error",
            details={"operation": "get_experiments"},
            cause=e
        ) from e
```

### LLM/AI Services

```python
from app.exceptions.external.llm import (
    OllamaUnavailableError,
    ModelNotFoundError,
    TokenLimitExceededError
)

async def generate_hypothesis(prompt: str) -> str:
    """Generate hypothesis using LLM."""

    try:
        response = await ollama_client.generate(
            model="mistral:7b",
            prompt=prompt
        )

    except ConnectionError as e:
        raise OllamaUnavailableError(
            "Ollama service not responding",
            error_code="OLLAMA_CONNECTION_FAILED",
            details={"url": "http://localhost:11434"},
            cause=e
        ) from e

    except KeyError as e:
        if "model" in str(e):
            raise ModelNotFoundError(
                "Model 'mistral:7b' not found",
                error_code="MODEL_NOT_FOUND",
                details={"model": "mistral:7b"},
                cause=e
            ) from e

    if len(response['response']) == 0:
        raise TokenLimitExceededError(
            "Response truncated - token limit exceeded",
            error_code="TOKEN_LIMIT",
            details={"prompt_length": len(prompt)}
        )

    return response['response']
```

---

## 🎨 Exception Attributes

All custom exceptions inherit these attributes:

```python
class AtlasException(Exception):
    def __init__(
        self,
        message: str,
        *,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.cause = cause
```

**Usage:**

```python
error = ProteinAnalysisError(
    "Protein not found",
    error_code="PROTEIN_NOT_FOUND",
    details={"uniprot_id": "P12345", "attempted_databases": ["uniprot", "pdb"]},
    cause=original_exception
)

# Access attributes
print(error.message)      # "Protein not found"
print(error.error_code)   # "PROTEIN_NOT_FOUND"
print(error.details)      # {"uniprot_id": "P12345", ...}
print(error.cause)        # original_exception
```

---

## 🔄 Exception Chaining

Always chain exceptions to preserve context:

```python
# ✅ GOOD - Chain with 'from e'
try:
    external_api_call()
except ExternalAPIError as e:
    raise ProteinAnalysisError(
        "Failed to fetch data",
        cause=e
    ) from e

# ❌ BAD - Loses context
try:
    external_api_call()
except ExternalAPIError:
    raise ProteinAnalysisError("Failed to fetch data")
```

---

## 🚫 Anti-Patterns to Avoid

### ❌ DON'T: Use bare except

```python
# ❌ NEVER DO THIS
try:
    operation()
except:
    pass
```

### ❌ DON'T: Catch generic Exception

```python
# ❌ TOO GENERIC
try:
    analyze_protein()
except Exception as e:
    logger.error(f"Error: {e}")
```

### ❌ DON'T: Silent failures

```python
# ❌ SILENCES ERRORS
try:
    critical_operation()
except SpecificError:
    return None  # Lost the error!
```

### ✅ DO: Use specific exceptions

```python
# ✅ CORRECT
try:
    analyze_protein(protein_id)
except ProteinAnalysisError as e:
    logger.error(f"Protein analysis failed: {e}")
    raise  # Re-raise for caller to handle
except InputValidationError as e:
    logger.warning(f"Invalid input: {e}")
    return {"error": e.to_dict()}
```

---

## 📊 Serialization for APIs

Exceptions can be serialized for API responses:

```python
try:
    result = await some_operation()
except AtlasException as e:
    return JSONResponse(
        status_code=400,
        content=e.to_dict()
    )

# Response:
{
  "error": "PROTEIN_NOT_FOUND",
  "message": "Protein P12345 not found",
  "details": {
    "uniprot_id": "P12345",
    "databases_searched": ["uniprot", "pdb"]
  }
}
```

---

## 🔍 Finding the Right Exception

### Decision Tree

1. **Is it domain-specific?** → Use `AtlasDomainError` subclass
   - Biology? → `BiologyError`
   - Chemistry? → `ChemistryError`
   - etc.

2. **Is it infrastructure?** → Use `AtlasInfrastructureError` subclass
   - Database? → `DatabaseError`
   - Cache? → `CacheError`
   - API? → `APIError`

3. **Is it external service?** → Use `AtlasExternalError` subclass
   - LLM? → `LLMError`
   - Scientific API? → `ScientificAPIError`

4. **Is it validation?** → Use `AtlasValidationError` subclass
   - User input? → `InputValidationError`
   - Ethics? → `EthicsViolationError`

5. **Is it security?** → Use `AtlasSecurityError`

6. **Not sure?** → Use parent class (e.g., `AtlasDomainError`)

---

## 🧪 Testing Exceptions

```python
import pytest
from app.exceptions.domain.biology import ProteinAnalysisError

def test_protein_analysis_raises_error():
    """Test that invalid protein raises correct exception."""

    service = ComputationalBiologyService()

    with pytest.raises(ProteinAnalysisError) as exc_info:
        await service.analyze_protein("INVALID_ID")

    # Check error attributes
    error = exc_info.value
    assert error.error_code == "PROTEIN_NOT_FOUND"
    assert "INVALID_ID" in error.details['uniprot_id']
    assert error.cause is not None  # Should chain original exception
```

---

## 📖 Full Exception Catalog

### Domain Exceptions

**Biology** (`app/exceptions/domain/biology.py`):
- `BiologyError` - Base for all biology errors
- `ProteinAnalysisError` - Protein structure/function analysis
- `SequenceAlignmentError` - Sequence alignment failures
- `GenomicsError` - Genomic analysis errors
- `StructurePredictionError` - AlphaFold/structure prediction

**Chemistry** (`app/exceptions/domain/chemistry.py`):
- `ChemistryError` - Base for chemistry errors
- `MolecularDynamicsError` - MD simulation failures
- `ReactionSimulationError` - Chemical reaction errors

**Physics** (`app/exceptions/domain/physics.py`):
- `PhysicsError` - Base for physics errors
- `QuantumSimulationError` - Quantum computing errors
- `ParticlePhysicsError` - Particle simulation errors

### Infrastructure Exceptions

**Database** (`app/exceptions/infrastructure/database.py`):
- `DatabaseError` - Base database error
- `SessionNotFoundError` - DB session unavailable
- `QueryTimeoutError` - Query exceeded timeout
- `ConnectionPoolExhaustedError` - No connections available

**Cache** (`app/exceptions/infrastructure/cache.py`):
- `CacheError` - Base cache error
- `CacheConnectionError` - Redis unavailable
- `CacheKeyError` - Key not found

### External Service Exceptions

**LLM** (`app/exceptions/external/llm.py`):
- `LLMError` - Base LLM error
- `OllamaUnavailableError` - Ollama service down
- `ModelNotFoundError` - Model not available
- `TokenLimitExceededError` - Context length exceeded

**Scientific APIs** (`app/exceptions/external/scientific_api.py`):
- `ScientificAPIError` - Base API error
- `UniProtError` - UniProt API failures
- `PubChemError` - PubChem API failures

---

## 🔄 Migration Guide

### From Generic Exceptions

**Before:**
```python
try:
    result = analyze_protein(id)
except Exception as e:  # ❌ Too generic
    logger.error(f"Error: {e}")
    raise
```

**After:**
```python
from app.exceptions.domain.biology import ProteinAnalysisError

try:
    result = analyze_protein(id)
except ProteinAnalysisError as e:  # ✅ Specific
    logger.error(f"Protein analysis failed: {e}")
    raise
```

### Adding New Exceptions

1. Determine category (domain, infrastructure, external, validation)
2. Add to appropriate file in `app/exceptions/`
3. Inherit from correct parent class
4. Add docstring with usage example
5. Update this README with new exception
6. Add tests

**Example:**
```python
# app/exceptions/domain/biology.py

class PopulationModelError(BiologyError):
    """
    Raised when population dynamics simulation fails.

    Example:
        >>> raise PopulationModelError(
        ...     "Negative population encountered",
        ...     error_code="INVALID_POPULATION",
        ...     details={"population": -10, "species": "rabbits"}
        ... )
    """
    pass
```

---

## 🎓 Best Practices

1. **Always use specific exceptions** - Never bare `except:` or generic `Exception`
2. **Chain exceptions** - Use `from e` to preserve context
3. **Provide details** - Include relevant data in `details` dict
4. **Use error codes** - Consistent codes for monitoring/alerting
5. **Log before raising** - Help with debugging
6. **Document exceptions** - Add to docstrings what can be raised
7. **Test exception paths** - Ensure errors are handled correctly

---

## 📞 Support

- **Questions:** [GitHub Discussions](https://github.com/org/axiom-atlas/discussions)
- **Issues:** [Report bugs](https://github.com/org/axiom-atlas/issues)
- **Examples:** See `tests/unit/exceptions/` for comprehensive examples

---

**Last Updated:** 2025-09-30
**Maintainer:** @core-team
