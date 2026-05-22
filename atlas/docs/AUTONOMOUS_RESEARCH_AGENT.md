# 🤖 Autonomous Research Agent

## Overview

The Autonomous Research Agent is a complete scientific research workflow that:
1. **Generates hypotheses** based on a domain and topic
2. **Dynamically discovers and executes tools** from a registry of 44+ tools
3. **Drafts scientific papers** based on experimental results
4. **Performs peer review** with iterative refinement until acceptance

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 AUTONOMOUS RESEARCH AGENT                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │   Groq API  │  │ DynamicTool  │  │  ServiceLocator   │  │
│  │  LLM Cloud  │  │   Registry   │  │  (28 services)    │  │
│  └──────┬──────┘  └──────┬───────┘  └─────────┬─────────┘  │
│         │                │                    │             │
│         ▼                ▼                    ▼             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    RESEARCH LOOP                      │  │
│  │  1. Hypothesis Generation (LLM)                      │  │
│  │  2. Tool Selection & Execution                       │  │
│  │  3. Paper Drafting (LLM)                             │  │
│  │  4. Peer Review (LLM)                                │  │
│  │  5. Iterate until ACCEPT (score ≥ 8)                 │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# Basic usage - specify domain and topic
python run_agent_with_tools.py mathematics "prime gap distribution"
python run_agent_with_tools.py chemistry "molecular orbital energy levels"
python run_agent_with_tools.py biology "DNA thermal stability"
python run_agent_with_tools.py physics "hydrogen spectral lines"

# Run integrated tests across all domains
python test_integrated_research_agent.py
```

## Tool Registry

### DynamicToolRegistry Class

The `DynamicToolRegistry` automatically discovers and registers tools from:
1. **Builtin Tools**: Mathematical, chemical, biological, physical, and statistical tools
2. **ServiceLocator**: 28 AXIOM services across 9 domains

### Available Tools by Domain

#### Mathematics (6 tools)
| Tool | Description | Example Input |
|------|-------------|---------------|
| `sympy_solve_equation` | Solve algebraic equations | `x**2 - 4 = 0` |
| `sympy_simplify` | Simplify expressions | `(x**2 - 1)/(x - 1)` |
| `sympy_derivative` | Compute derivatives | `x**3, x` |
| `sympy_integrate` | Compute integrals | `x**2, x` |
| `sympy_prime_analysis` | Analyze prime numbers | `prime_count:10000` |
| `prime_gap_analysis` | Analyze prime gaps | `10000` |

#### Chemistry (12 tools)
| Tool | Description | Example Input |
|------|-------------|---------------|
| `molecular_orbital_energy` | Hückel MO analysis | `6:1.4` (benzene) |
| `bond_energy_analyzer` | Bond energy lookup | `C-C`, `C=O`, `O-H` |
| `molecular_weight_calc` | Calculate MW | `C6H12O6`, `H2O` |
| `service_computationalchemistryservice` | Full chemistry service | (service request) |
| `service_materialsdiscoveryservice` | Materials discovery | (service request) |

#### Biology (5 tools)
| Tool | Description | Example Input |
|------|-------------|---------------|
| `dna_analyzer` | DNA sequence analysis | `ATCGATCGATCG` |
| `protein_properties` | Protein property calculation | `MVLSPADKTNVK` |
| `service_genomicsservice` | Genomics service | (service request) |
| `service_dnabert2genomicsservice` | DNABERT2 analysis | (service request) |
| `service_computationalbiologyservice` | Computational biology | (service request) |

#### Physics (8 tools)
| Tool | Description | Example Input |
|------|-------------|---------------|
| `quantum_energy_levels` | Quantum mechanics | `hydrogen:3`, `harmonic:2,0.5` |
| `service_quantumcomputingservice` | Quantum computing | (service request) |
| `service_particlephysicsservice` | Particle physics | (service request) |
| `service_solidstatephysicsservice` | Solid state physics | (service request) |
| `service_plasmaphysicsservice` | Plasma physics | (service request) |

#### Statistics (4 tools)
| Tool | Description | Example Input |
|------|-------------|---------------|
| `numpy_statistics` | Basic statistics | `mean:[1,2,3,4,5]` |
| `numpy_distribution` | Generate distributions | `normal:1000,0,1` |
| `numpy_correlation` | Correlation analysis | `correlation:[1,2,3],[4,5,6]` |
| `hypothesis_tester` | Statistical tests | `pearson:[1,2,3]:[4,5,6]` |

## Research Loop Details

### Phase 1: Hypothesis Generation
The agent uses Groq's `llama-3.3-70b-versatile` model to generate:
- A clear, testable hypothesis statement
- Mathematical formulation
- Required tools from the registry

### Phase 2: Tool Selection & Execution
The LLM selects appropriate tools and provides inputs. Tools are executed in sequence:
```
TOOL: molecular_orbital_energy | INPUT: 6:1.4
TOOL: bond_energy_analyzer | INPUT: C-C
TOOL: numpy_statistics | INPUT: mean:[1.4, 1.5, 1.6]
```

### Phase 3: Paper Drafting
Results are compiled into a scientific paper with:
- Abstract (100 words)
- Methods (tools used)
- Results (data interpretation)
- Discussion

### Phase 4: Peer Review
The paper is evaluated with:
- Decision: ACCEPT / REVISE / REJECT
- Score: 1-10
- Strengths and weaknesses
- Required changes (if REVISE)

### Iteration Until Acceptance
The loop continues with the following logic:

1. **Paper ACCEPTED**: When score ≥ `target_score` (default: 8) or explicit "ACCEPT" without "REVISE"
2. **Continue Iteration**: When score < target_score and iterations remaining
3. **Auto-Extend**: When max_iterations reached but score ≥ 5 (showing progress), extends by 2 more iterations
4. **Stop**: When score < 5 (no significant progress)

**Structured Return Value:**
```python
{
    "status": "accepted" | "rejected" | "completed",
    "final_score": 8,
    "iterations_used": 3,
    "paper": "## Abstract\n...",
    "review": "Decision: ACCEPT\nScore: 8..."
}
```

**Rate Limiting:**
- 3-second delay between API calls to avoid Groq rate limits
- Automatic retry on API errors with 5-second delay

## API Integration

The agent is integrated into `ScientificAIService`:

```python
from app.services.scientific_ai.scientific_ai import ScientificAIService

service = ScientificAIService()
result = service.autonomous_research_cycle({
    "operation": "autonomous_research",
    "domain": "chemistry",
    "topic": "molecular stability patterns",
    "max_iterations": 5
})
```

## Configuration

### Environment Variables
```bash
# Groq API (required)
GROQ_API_KEY=gsk_your_key_here

# Optional: Ollama fallback
OLLAMA_BASE_URL=http://localhost:11434
```

### Tool Registry Configuration
Tools are automatically registered from:
1. `run_agent_with_tools.py` - Builtin tools
2. `app/domains/service_locator.py` - ServiceLocator services

## Example Output

```
🔬 Autonomous Research Agent
   Domain: chemistry
   Topic: molecular orbital conjugation in aromatic hydrocarbons
================================================================

📦 Tool Discovery:
   Total tools available: 44
   Domain-specific tools (chemistry): 12

🔄 ITERATION 1
================================================================

📝 Phase 1: Generating Hypothesis...
   Hypothesis: The molecular orbital energy levels of aromatic 
   hydrocarbons are proportional to the inverse of bond length...

🔧 Phase 2: Selecting and Executing Tools...
   🔨 Executing: molecular_orbital_energy
      Input: 6:1.4
      ✅ Result: Hückel MO Analysis (6 carbon conjugated system):
        Energy levels (eV): [-10.505, -9.117, -7.113, -4.887, -2.883, -1.495]
        HOMO-LUMO gap: 2.226 eV

📄 Phase 3: Drafting Paper...
   Abstract: This study investigates the relationship between...

🔍 Phase 4: Peer Review...
   Decision: REVISE
   Score: 6
   Required Changes: [...]

🔄 ITERATION 2
...

✅ Paper ACCEPTED after 3 iteration(s)! Score: 8/10
```

## Files

| File | Description |
|------|-------------|
| `run_agent_with_tools.py` | Main autonomous agent script with DynamicToolRegistry |
| `test_integrated_research_agent.py` | Multi-domain test runner |
| `test_groq_hypothesis_generation.py` | Groq API integration test |
| `app/services/scientific_ai/scientific_ai.py` | Service integration |

## Function Signature

```python
async def autonomous_research_agent(
    domain: str,           # "mathematics", "chemistry", "biology", "physics"
    topic: str,            # Research topic to investigate
    max_iterations: int = 2,  # Initial max (auto-extends if progress)
    target_score: int = 8     # Score threshold for acceptance
) -> Dict[str, Any]:
    """
    Returns:
        {
            "status": "accepted" | "rejected" | "completed",
            "final_score": int,
            "iterations_used": int,
            "paper": str,
            "review": str
        }
    """
```

## Dependencies

- `groq` - Cloud LLM provider
- `sympy` - Symbolic mathematics
- `numpy` - Numerical computing
- `scipy` - Scientific computing
- `langchain_classic` - Agent framework (ReAct pattern)

## Related Documentation

- [Scientific AI Service](../docs/ADVANCED_SERVICES.md)
- [Multi-Agent System](../docs/MULTI_AGENT.md)
- [ServiceLocator](../docs/configuration.md)
