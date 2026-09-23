"""Multi-LLM Brainstorming Module for AXIOM

Integración opcional con múltiples LLMs (OpenAI, Anthropic Claude, Google Gemini) para
brainstorming de hipótesis. Las dependencias son opcionales y se usan solo si están
instaladas y configuradas. Si ningún proveedor está disponible, se usa un fallback local
no determinista muy simple para mantener el loop funcional en entornos sin claves.

Dependencias opcionales:
- openai (recomendada)
- anthropic
- google-generativeai

Variables de entorno esperadas (opcional):
- OPENAI_API_KEY
- ANTHROPIC_API_KEY
- GOOGLE_API_KEY
"""

from typing import List, Dict, Any
import importlib
from app.config import settings
from app.exceptions.domain.mathematics import MathematicsError

class MultiLLMBrainstorm:
    def __init__(self):
        self.providers: List[str] = []

        # OpenAI
        self.openai_client = None
        openai_key = getattr(settings, "OPENAI_API_KEY", None)
        if openai_key:
            try:
                openai_mod = importlib.import_module('openai')  # type: ignore
                OpenAI = getattr(openai_mod, 'OpenAI')
                self.openai_client = OpenAI(api_key=openai_key)
                self.providers.append("openai")
            except (RuntimeError, ValueError):
                self.openai_client = None

        # Anthropic
        self.anthropic_client = None
        anthropic_key = getattr(settings, "ANTHROPIC_API_KEY", None)
        if anthropic_key:
            try:
                anthropic_mod = importlib.import_module('anthropic')  # type: ignore
                Anthropic = getattr(anthropic_mod, 'Anthropic')
                self.anthropic_client = Anthropic(api_key=anthropic_key)
                self.providers.append("anthropic")
            except (RuntimeError, ValueError, ImportError):
                self.anthropic_client = None

        # Google Gemini
        self.gemini_model = None
        google_key = getattr(settings, "GOOGLE_API_KEY", None)
        if google_key:
            try:
                genai = importlib.import_module('google.generativeai')  # type: ignore
                genai.configure(api_key=google_key)
                self.gemini_model = getattr(genai, 'GenerativeModel')('gemini-pro')
                self.providers.append("gemini")
            except (RuntimeError, ValueError, ImportError):
                self.gemini_model = None

    def generate_hypothesis(self, provider: str, prompt: str) -> str:
        """Genera una hipótesis usando el proveedor indicado, o fallback local si no hay clientes."""
        provider = provider.lower()
        if provider == "openai" and self.openai_client is not None:
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content
            except (RuntimeError, ValueError):
                pass

        if provider == "anthropic" and self.anthropic_client is not None:
            try:
                response = self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            except (RuntimeError, ValueError):
                pass

        if provider == "gemini" and self.gemini_model is not None:
            try:
                response = self.gemini_model.generate_content(prompt)
                return response.text
            except (RuntimeError, ValueError):
                pass

        # Fallback local simple (sin dependencias)
        return f"[fallback] Hipótesis generada localmente sobre: {prompt[:80]}"

    def brainstorm_hypotheses(self, initial_prompt: str, num_rounds: int = 3, num_agents: int = 3) -> List[str]:
        """Simulate brainstorming among multiple LLMs."""
        providers = self.providers[:] if self.providers else ["fallback"]
        hypotheses = []
        
        current_prompt = initial_prompt
        for _ in range(num_rounds):
            round_hypotheses = []
            for i in range(num_agents):
                provider = providers[i % len(providers)]
                hyp = self.generate_hypothesis(provider, current_prompt)
                round_hypotheses.append(hyp)
            
            # Simple aggregation for next prompt
            current_prompt = f"Based on these ideas: {'; '.join(round_hypotheses)}\nGenerate an improved hypothesis."
            hypotheses.extend(round_hypotheses)
        
        return hypotheses

    def consensus_mechanism(self, hypotheses: List[str], threshold: float = 0.7) -> str:
        """Simple consensus mechanism: Have LLMs vote on hypotheses and select the one with majority agreement."""
        votes = {hyp: 0 for hyp in set(hypotheses)}
        providers = self.providers[:] if self.providers else ["fallback"]
        
        for hyp in set(hypotheses):
            for provider in providers:
                prompt = f"Evaluate if this hypothesis is promising: '{hyp}'. Respond with 'yes' or 'no'."
                response = self.generate_hypothesis(provider, prompt).lower()
                if 'yes' in response:
                    votes[hyp] += 1
        
        # Select hypothesis with highest votes
        max_votes = max(votes.values()) if votes else 0
        if providers and max_votes / len(providers) >= threshold:
            # Elegir la hipótesis con más votos de forma segura para tipado
            best = max(votes.items(), key=lambda kv: kv[1])[0]
            return best
        else:
            return "No consensus reached."

    def brainstorm_with_consensus(self, initial_prompt: str, num_rounds: int = 3, num_agents: int = 3) -> str:
        """Brainstorm hypotheses and apply consensus to select the best one."""
        hypotheses = self.brainstorm_hypotheses(initial_prompt, num_rounds, num_agents)
        return self.consensus_mechanism(hypotheses)

    def minimal_test_hypothesis(self, hypothesis: str, test_type: str = "mathematical") -> Dict[str, Any]:
        """Perform minimal initial testing on a hypothesis using integrated tools."""
        if test_type == "mathematical":
            # Simple example: Use sympy to evaluate if hypothesis is mathematical
            try:
                import sympy
                # Assume hypothesis is something like "x**2 + 1 = 0"
                # For demo, solve a quadratic
                x = sympy.symbols('x')
                expr = sympy.parse_expr(hypothesis)
                result = sympy.solve(expr, x)
                return {"valid": True, "result": str(result), "tool": "sympy"}
            except MathematicsError as e:
                return {"valid": False, "error": str(e), "tool": "sympy"}
            except (ValueError, SyntaxError, TypeError) as e:
                # Fallback: si no es una expresión válida, devolver no válido
                return {"valid": False, "error": str(e), "tool": "sympy"}
        else:
            return {"valid": False, "error": "Unsupported test type"}

    def brainstorm_with_consensus_and_test(self, initial_prompt: str, num_rounds: int = 3, num_agents: int = 3) -> Dict[str, Any]:
        """Brainstorm, reach consensus, and perform minimal testing."""
        consensus_hyp = self.brainstorm_with_consensus(initial_prompt, num_rounds, num_agents)
        if consensus_hyp != "No consensus reached.":
            test_result = self.minimal_test_hypothesis(consensus_hyp)
            return {"hypothesis": consensus_hyp, "test": test_result}
        return {"hypothesis": None, "test": None}

# Example usage (commented out)
# brainstorm = MultiLLMBrainstorm()
# results = brainstorm.brainstorm_hypotheses("Generate hypotheses about climate change impacts on ocean ecosystems.")