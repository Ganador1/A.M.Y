"""
Hypothesis Testing Skill — Formalize and test scientific hypotheses.

Provides utilities to:
- Select appropriate statistical tests
- Compute effect sizes and power
- Interpret results with proper scientific language
"""
import json
from dataclasses import dataclass
from typing import Literal

import structlog

from skills.code_experiment import CodeExperimentSkill

log = structlog.get_logger()


@dataclass
class Hypothesis:
    null_hypothesis: str
    alternative_hypothesis: str
    alpha: float = 0.05
    test_type: Literal[
        "t_test_ind",
        "t_test_rel",
        "mannwhitney",
        "wilcoxon",
        "anova",
        "chi2",
        "correlation",
    ] = "t_test_ind"
    sample_a: list[float] | None = None
    sample_b: list[float] | None = None


class HypothesisTestSkill:
    """Formulate hypotheses and run statistical tests in the sandbox."""

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.experiment_skill = CodeExperimentSkill(self.config)

    def recommend_test(
        self,
        comparison_type: str,  # "means", "proportions", "correlation", "groups"
        paired: bool = False,
        parametric: bool = True,
        group_count: int = 2,
    ) -> str:
        """Recommend a statistical test based on study design."""
        if comparison_type == "means":
            if group_count > 2:
                return "anova"
            if paired:
                return "t_test_rel" if parametric else "wilcoxon"
            return "t_test_ind" if parametric else "mannwhitney"
        elif comparison_type == "proportions":
            return "chi2"
        elif comparison_type == "correlation":
            return "correlation"
        return "t_test_ind"

    async def run_test(self, hypothesis: Hypothesis) -> dict:
        """Generate sandbox code and execute the chosen test."""
        if hypothesis.test_type == "correlation":
            code = self._build_correlation_code(hypothesis)
        elif hypothesis.test_type == "chi2":
            code = self._build_chi2_code(hypothesis)
        else:
            code = self.experiment_skill.build_statistical_test(
                description=hypothesis.alternative_hypothesis,
                test_type=hypothesis.test_type,
                sample_a=hypothesis.sample_a or [],
                sample_b=hypothesis.sample_b,
                alpha=hypothesis.alpha,
            )

        result = await self.experiment_skill.run_experiment(
            hypothesis=hypothesis.alternative_hypothesis,
            code=code,
            language="python",
        )

        interpretation = self._interpret(result, hypothesis)
        result["interpretation"] = interpretation
        return result

    def _build_correlation_code(self, hypothesis: Hypothesis) -> str:
        x = hypothesis.sample_a or []
        y = hypothesis.sample_b or []
        return f"""import numpy as np
from scipy import stats
import json

x = {x}
y = {y}

r, pvalue = stats.pearsonr(x, y)
result = {{
    "test": "Pearson correlation",
    "r": float(r),
    "pvalue": float(pvalue),
    "significant": pvalue < {hypothesis.alpha},
    "alpha": {hypothesis.alpha},
}}
print(json.dumps(result, indent=2))
with open("correlation_results.json", "w") as f:
    json.dump(result, f, indent=2)
"""

    def _build_chi2_code(self, hypothesis: Hypothesis) -> str:
        # sample_a expected as observed frequencies per category
        observed = hypothesis.sample_a or []
        return f"""import numpy as np
from scipy import stats
import json

observed = np.array({observed})
stat, pvalue = stats.chisquare(observed)
result = {{
    "test": "Chi-square goodness-of-fit",
    "statistic": float(stat),
    "pvalue": float(pvalue),
    "significant": pvalue < {hypothesis.alpha},
    "alpha": {hypothesis.alpha},
}}
print(json.dumps(result, indent=2))
with open("chi2_results.json", "w") as f:
    json.dump(result, f, indent=2)
"""

    def _interpret(self, result: dict, hypothesis: Hypothesis) -> str:
        success = result.get("success", False)
        if not success:
            return "Experiment execution failed; hypothesis remains untested."

        # Try to parse JSON stdout for p-value
        pvalue = None
        try:
            stdout = result.get("stdout", "")
            data = json.loads(stdout)
            pvalue = data.get("pvalue")
        except Exception:
            pass

        if pvalue is None:
            return "Test completed but p-value could not be parsed."

        if pvalue < hypothesis.alpha:
            return (
                f"REJECT the null hypothesis (p={pvalue:.4f} < α={hypothesis.alpha}). "
                f"Evidence supports: {hypothesis.alternative_hypothesis}"
            )
        else:
            return (
                f"FAIL TO REJECT the null hypothesis (p={pvalue:.4f} >= α={hypothesis.alpha}). "
                f"Insufficient evidence for: {hypothesis.alternative_hypothesis}"
            )
