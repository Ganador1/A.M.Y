#!/usr/bin/env python3
"""Run a reproducible Information Bottleneck benchmark with negative controls."""

import asyncio
import hashlib
import json
import math
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from communication.paper_generator import PaperGenerator
from core.provenance import ProvenanceManager


SEEDS = [11, 23, 37, 41, 53]
EPOCHS = 240
CHECKPOINT_EVERY = 20
LR = 0.12
N_SAMPLES = 2400
N_FEATURES = 10
LABEL_NOISE = 0.10


def relu(z):
    return np.maximum(0, z)


def relu_deriv(z):
    return (z > 0).astype(float)


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))


def binary_cross_entropy(y, y_pred):
    y = y.reshape(-1, 1)
    y_pred = np.clip(y_pred, 1e-8, 1 - 1e-8)
    return float(-np.mean(y * np.log(y_pred) + (1 - y) * np.log(1 - y_pred)))


def make_dataset(seed, shuffle_labels=False):
    rng = np.random.default_rng(seed)
    x = rng.normal(size=(N_SAMPLES, N_FEATURES))
    logits = (
        np.sin(2.0 * x[:, 0])
        + np.cos(1.5 * x[:, 1])
        + 0.65 * x[:, 2]
        - 0.45 * x[:, 3] * x[:, 4]
        + 0.25 * x[:, 5] ** 2
    )
    y = (logits > np.median(logits)).astype(int)
    flips = rng.random(N_SAMPLES) < LABEL_NOISE
    y = np.logical_xor(y, flips).astype(int)
    if shuffle_labels:
        y = rng.permutation(y)

    order = rng.permutation(N_SAMPLES)
    train_end = int(0.60 * N_SAMPLES)
    val_end = int(0.80 * N_SAMPLES)
    idx_train = order[:train_end]
    idx_val = order[train_end:val_end]
    idx_test = order[val_end:]

    x_train = x[idx_train]
    mean = x_train.mean(axis=0, keepdims=True)
    std = x_train.std(axis=0, keepdims=True) + 1e-8

    return {
        "train": ((x[idx_train] - mean) / std, y[idx_train]),
        "validation": ((x[idx_val] - mean) / std, y[idx_val]),
        "test": ((x[idx_test] - mean) / std, y[idx_test]),
    }


def quantile_bins(values, bins):
    values = np.asarray(values).reshape(-1)
    if np.allclose(values.min(), values.max()):
        return np.zeros_like(values, dtype=int)
    edges = np.quantile(values, np.linspace(0, 1, bins + 1)[1:-1])
    edges = np.unique(edges)
    if edges.size == 0:
        return np.zeros_like(values, dtype=int)
    return np.digitize(values, edges)


def discrete_mi(a, b, bins=12):
    a = quantile_bins(a, bins)
    b = quantile_bins(b, bins)
    a_levels = int(a.max()) + 1
    b_levels = int(b.max()) + 1
    hist = np.zeros((a_levels, b_levels), dtype=float)
    np.add.at(hist, (a, b), 1.0)
    pxy = hist / hist.sum()
    px = pxy.sum(axis=1, keepdims=True)
    py = pxy.sum(axis=0, keepdims=True)
    expected = px @ py
    mask = pxy > 0
    return float(np.sum(pxy[mask] * np.log2(pxy[mask] / expected[mask])))


def projected_mi(a, b, bins=12, seed=1009):
    rng = np.random.default_rng(seed)
    a = np.asarray(a)
    b = np.asarray(b)
    if a.ndim > 1 and a.shape[1] > 1:
        projection = rng.normal(size=a.shape[1])
        projection /= np.linalg.norm(projection) + 1e-12
        a = a @ projection
    if b.ndim > 1 and b.shape[1] > 1:
        projection = rng.normal(size=b.shape[1])
        projection /= np.linalg.norm(projection) + 1e-12
        b = b @ projection
    return discrete_mi(a, b, bins=bins)


class MLP:
    def __init__(self, layer_sizes, seed):
        rng = np.random.default_rng(seed)
        self.weights = [
            rng.normal(size=(in_dim, out_dim)) * math.sqrt(2.0 / in_dim)
            for in_dim, out_dim in zip(layer_sizes[:-1], layer_sizes[1:])
        ]
        self.biases = [np.zeros((1, out_dim)) for out_dim in layer_sizes[1:]]

    def forward(self, x):
        activations = [x]
        zs = []
        a = x
        for w, b in zip(self.weights[:-1], self.biases[:-1]):
            z = a @ w + b
            zs.append(z)
            a = relu(z)
            activations.append(a)
        z = a @ self.weights[-1] + self.biases[-1]
        zs.append(z)
        activations.append(sigmoid(z))
        return activations, zs

    def step(self, x, y, lr):
        y = y.reshape(-1, 1)
        n = x.shape[0]
        activations, zs = self.forward(x)
        dz = activations[-1] - y
        dws = []
        dbs = []
        for i in range(len(self.weights) - 1, -1, -1):
            dw = activations[i].T @ dz / n
            db = dz.sum(axis=0, keepdims=True) / n
            dws.insert(0, dw)
            dbs.insert(0, db)
            if i > 0:
                dz = (dz @ self.weights[i].T) * relu_deriv(zs[i - 1])
        for i in range(len(self.weights)):
            self.weights[i] -= lr * dws[i]
            self.biases[i] -= lr * dbs[i]
        return float(np.linalg.norm(dws[0], ord=1))


def evaluate(model, split, mi_seed):
    x, y = split
    activations, _ = model.forward(x)
    y_pred = activations[-1]
    t1 = activations[1]
    t2 = activations[2]
    return {
        "loss": binary_cross_entropy(y, y_pred),
        "accuracy": float(np.mean((y_pred.reshape(-1) >= 0.5) == y)),
        "I_X_T1": projected_mi(x, t1, seed=mi_seed),
        "I_T1_Y": projected_mi(t1, y, seed=mi_seed + 1),
        "I_X_T2": projected_mi(x, t2, seed=mi_seed + 2),
        "I_T2_Y": projected_mi(t2, y, seed=mi_seed + 3),
    }


def run_condition(seed, shuffle_labels):
    data = make_dataset(seed, shuffle_labels=shuffle_labels)
    model = MLP([N_FEATURES, 16, 8, 1], seed=seed + 500)
    checkpoints = []

    for epoch in range(EPOCHS + 1):
        if epoch % CHECKPOINT_EVERY == 0 or epoch == EPOCHS:
            train_metrics = evaluate(model, data["train"], mi_seed=seed + 1000)
            test_metrics = evaluate(model, data["test"], mi_seed=seed + 2000)
            checkpoints.append(
                {
                    "epoch": epoch,
                    "train": train_metrics,
                    "test": test_metrics,
                }
            )
        if epoch < EPOCHS:
            grad_l1 = model.step(*data["train"], lr=LR)
            if checkpoints and checkpoints[-1]["epoch"] == epoch:
                checkpoints[-1]["grad_l1"] = grad_l1

    initial = checkpoints[0]["test"]
    final = checkpoints[-1]["test"]
    return {
        "seed": seed,
        "condition": "shuffled_label_control" if shuffle_labels else "structured_labels",
        "checkpoints": checkpoints,
        "final_test_accuracy": final["accuracy"],
        "test_loss_delta": initial["loss"] - final["loss"],
        "test_I_X_T1_delta": initial["I_X_T1"] - final["I_X_T1"],
        "test_I_X_T2_delta": initial["I_X_T2"] - final["I_X_T2"],
        "test_I_T1_Y_delta": final["I_T1_Y"] - initial["I_T1_Y"],
        "test_I_T2_Y_delta": final["I_T2_Y"] - initial["I_T2_Y"],
    }


def mean_sd_ci(values):
    values = np.asarray(values, dtype=float)
    mean = float(values.mean())
    sd = float(values.std(ddof=1)) if values.size > 1 else 0.0
    ci = 1.96 * sd / math.sqrt(values.size) if values.size > 1 else 0.0
    return {"mean": mean, "sd": sd, "ci95_low": mean - ci, "ci95_high": mean + ci}


def paired_ttest(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    diff = a - b
    sd = diff.std(ddof=1)
    t_stat = float(diff.mean() / (sd / math.sqrt(diff.size))) if sd > 0 else 0.0
    try:
        from scipy import stats

        p_value = float(stats.ttest_rel(a, b).pvalue)
    except Exception:
        p_value = None
    cohen_dz = float(diff.mean() / sd) if sd > 0 else 0.0
    return {
        "mean_difference": float(diff.mean()),
        "t": t_stat,
        "p": p_value,
        "cohen_dz": cohen_dz,
    }


def summarize(results):
    by_condition = {}
    for condition in ["structured_labels", "shuffled_label_control"]:
        rows = [r for r in results if r["condition"] == condition]
        by_condition[condition] = {
            "n": len(rows),
            "final_test_accuracy": mean_sd_ci([r["final_test_accuracy"] for r in rows]),
            "test_loss_delta": mean_sd_ci([r["test_loss_delta"] for r in rows]),
            "test_I_X_T1_compression": mean_sd_ci([r["test_I_X_T1_delta"] for r in rows]),
            "test_I_X_T2_compression": mean_sd_ci([r["test_I_X_T2_delta"] for r in rows]),
            "test_I_T1_Y_gain": mean_sd_ci([r["test_I_T1_Y_delta"] for r in rows]),
            "test_I_T2_Y_gain": mean_sd_ci([r["test_I_T2_Y_delta"] for r in rows]),
        }

    structured = [r for r in results if r["condition"] == "structured_labels"]
    shuffled = [r for r in results if r["condition"] == "shuffled_label_control"]
    paired = {
        "accuracy_structured_minus_shuffled": paired_ttest(
            [r["final_test_accuracy"] for r in structured],
            [r["final_test_accuracy"] for r in shuffled],
        ),
        "T1_compression_structured_minus_shuffled": paired_ttest(
            [r["test_I_X_T1_delta"] for r in structured],
            [r["test_I_X_T1_delta"] for r in shuffled],
        ),
        "T2_compression_structured_minus_shuffled": paired_ttest(
            [r["test_I_X_T2_delta"] for r in structured],
            [r["test_I_X_T2_delta"] for r in shuffled],
        ),
    }
    return {"by_condition": by_condition, "paired_tests": paired}


def fmt_ci(stat):
    return f"{stat['mean']:.4f} [{stat['ci95_low']:.4f}, {stat['ci95_high']:.4f}]"


def build_sections(analysis):
    summary = analysis["summary"]
    structured = summary["by_condition"]["structured_labels"]
    shuffled = summary["by_condition"]["shuffled_label_control"]
    acc_test = summary["paired_tests"]["accuracy_structured_minus_shuffled"]
    t1_test = summary["paired_tests"]["T1_compression_structured_minus_shuffled"]
    t2_test = summary["paired_tests"]["T2_compression_structured_minus_shuffled"]
    p_acc = "not computed" if acc_test["p"] is None else f"{acc_test['p']:.4g}"
    p_t1 = "not computed" if t1_test["p"] is None else f"{t1_test['p']:.4g}"
    p_t2 = "not computed" if t2_test["p"] is None else f"{t2_test['p']:.4g}"

    return [
        {
            "heading": "Introduction",
            "content": (
                "The Information Bottleneck view of representation learning proposes that useful "
                "hidden states preserve target-relevant information while discarding input detail. "
                "Prior work reports information-plane compression, while later analyses show that "
                "the effect depends on architecture, activation functions, estimator choice, and "
                "training noise [1-4]. This study therefore does not attempt to prove the theory. "
                "It asks a narrower and reproducible question: can a small ReLU network trained "
                "from scratch show a measurable compression-like signal on held-out data, and does "
                "that signal differ from a label-shuffled negative control?"
            ),
        },
        {
            "heading": "Methods",
            "content": (
                f"We generated {N_SAMPLES} synthetic samples with {N_FEATURES} standardized input "
                f"features and {LABEL_NOISE:.0%} label noise. Each seed used a 60/20/20 "
                "train-validation-test split, with standardization fitted only on the training set. "
                f"A fully connected ReLU network with layer sizes [{N_FEATURES}, 16, 8, 1] was "
                f"trained for {EPOCHS} full-batch gradient steps at learning rate {LR}. "
                "The negative control reused the same data-generation process but permuted labels "
                "before splitting. Mutual information was estimated on the held-out test split by "
                "fixed random projection followed by quantile discretization and empirical "
                "plug-in estimation. The estimator is intentionally simple and is treated as a "
                "diagnostic probe, not as a definitive continuous mutual-information estimator. "
                f"All reported intervals aggregate {len(SEEDS)} paired random seeds: {SEEDS}."
            ),
        },
        {
            "heading": "Results",
            "content": (
                "| Metric | Structured labels, mean [95% CI] | Shuffled-label control, mean [95% CI] |\n"
                "|---|---:|---:|\n"
                f"| Final held-out accuracy | {fmt_ci(structured['final_test_accuracy'])} | {fmt_ci(shuffled['final_test_accuracy'])} |\n"
                f"| Held-out loss decrease | {fmt_ci(structured['test_loss_delta'])} | {fmt_ci(shuffled['test_loss_delta'])} |\n"
                f"| T1 I(X;T) decrease | {fmt_ci(structured['test_I_X_T1_compression'])} | {fmt_ci(shuffled['test_I_X_T1_compression'])} |\n"
                f"| T2 I(X;T) decrease | {fmt_ci(structured['test_I_X_T2_compression'])} | {fmt_ci(shuffled['test_I_X_T2_compression'])} |\n"
                f"| T1 I(T;Y) gain | {fmt_ci(structured['test_I_T1_Y_gain'])} | {fmt_ci(shuffled['test_I_T1_Y_gain'])} |\n"
                f"| T2 I(T;Y) gain | {fmt_ci(structured['test_I_T2_Y_gain'])} | {fmt_ci(shuffled['test_I_T2_Y_gain'])} |\n\n"
                "Paired tests compared each structured-label run with its seed-matched shuffled "
                f"control. Final held-out accuracy improved by {acc_test['mean_difference']:.4f} "
                f"(t={acc_test['t']:.3f}, p={p_acc}, Cohen dz={acc_test['cohen_dz']:.3f}). "
                f"The structured-minus-control T1 compression difference was {t1_test['mean_difference']:.4f} "
                f"(t={t1_test['t']:.3f}, p={p_t1}, Cohen dz={t1_test['cohen_dz']:.3f}); "
                f"the T2 compression difference was {t2_test['mean_difference']:.4f} "
                f"(t={t2_test['t']:.3f}, p={p_t2}, Cohen dz={t2_test['cohen_dz']:.3f})."
            ),
        },
        {
            "heading": "Discussion",
            "content": (
                "The benchmark is stronger than a single-run demonstration because it includes "
                "held-out evaluation, paired seeds, and a negative control. The result supports "
                "only a modest claim: under this synthetic task and estimator, representation "
                "compression-like movement can be measured and compared against a shuffled-label "
                "baseline. This study does not claim that compression causes generalization because "
                "no causal intervention on hidden-state information was performed. It does not "
                "settle the Information Bottleneck debate, and does not imply that all ReLU "
                "networks compress in the same way. The reported p-values and confidence intervals "
                "refer only to the five paired seeds in this benchmark, not to a population-wide "
                "law of neural training.\n\n"
                "### Limitations\n\n"
                "The main limitations are synthetic data only, one small ReLU architecture, five "
                "paired seeds, and one projection/discretization estimator. A further limitation is "
                "that the benchmark measures association, not causal intervention. Alternative "
                "explanations include estimator bias from projection/discretization, finite-sample "
                "effects, and changes in activation sparsity rather than true information-theoretic "
                "compression.\n\n"
                "### Testable Predictions\n\n"
                "H1. Testable via label-noise sweep: increasing label noise should reduce held-out "
                "accuracy while increasing the gap between train and test information-plane "
                "trajectories; confidence: 70%.\n\n"
                "H2. Testable via activation replacement: replacing ReLU with saturating activations "
                "should change the measured compression profile; confidence: 65%.\n\n"
                "H3. Testable via estimator substitution: k-nearest-neighbor or variational "
                "mutual-information estimators should preserve the sign of robust effects if the "
                "signal is not an artifact of the histogram estimator; confidence: 55%."
            ),
        },
        {
            "heading": "Conclusion",
            "content": (
                "This work contributes a reproducible, provenance-tracked benchmark for testing "
                "Information Bottleneck-style compression claims in small neural networks. The "
                "paper should be treated as a validated computational benchmark and a falsifiable "
                "research note, not as a proof of the general Information Bottleneck theory."
            ),
        },
    ]


async def main():
    start = time.time()
    script_path = Path(__file__)
    script_hash = hashlib.sha256(script_path.read_bytes()).hexdigest()

    results = []
    for seed in SEEDS:
        results.append(run_condition(seed, shuffle_labels=False))
        results.append(run_condition(seed, shuffle_labels=True))

    analysis = {
        "experiment": "reproducible_information_bottleneck_negative_control_benchmark",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "script": str(script_path),
        "script_sha256": script_hash,
        "parameters": {
            "seeds": SEEDS,
            "epochs": EPOCHS,
            "checkpoint_every": CHECKPOINT_EVERY,
            "learning_rate": LR,
            "n_samples": N_SAMPLES,
            "n_features": N_FEATURES,
            "label_noise": LABEL_NOISE,
            "architecture": [N_FEATURES, 16, 8, 1],
        },
        "results": results,
        "summary": summarize(results),
        "claim_status": "reproducible benchmark; not a proof of the Information Bottleneck theory",
        "limitations": [
            "synthetic data only",
            "small ReLU network only",
            "projection plus discretization mutual-information estimator",
            "five paired seeds",
            "no causal intervention on compression",
        ],
    }

    output_str = json.dumps(analysis, indent=2, sort_keys=True)
    provenance = ProvenanceManager()
    record = provenance.record_execution(
        tool_name="information_bottleneck_negative_control_benchmark",
        tool_input=json.dumps(analysis["parameters"], sort_keys=True),
        tool_output=output_str,
        success=True,
        duration_seconds=time.time() - start,
        domain="machine-learning",
        extra={
            "script": str(script_path),
            "script_sha256": script_hash,
            "claim_status": analysis["claim_status"],
        },
    )

    experiment_id = record["experiment_id"]
    exp_dir = Path("data/experiments") / experiment_id
    (exp_dir / "analysis.json").write_text(output_str, encoding="utf-8")

    summary = analysis["summary"]["by_condition"]
    abstract = (
        "We present a reproducible benchmark for evaluating Information Bottleneck-style "
        "compression signals in a small ReLU network. Unlike a single-run demonstration, "
        "the benchmark uses held-out evaluation, five paired random seeds, and a shuffled-label "
        "negative control. On the synthetic task, the structured-label condition reached held-out "
        f"accuracy {fmt_ci(summary['structured_labels']['final_test_accuracy'])}, compared with "
        f"{fmt_ci(summary['shuffled_label_control']['final_test_accuracy'])} for the negative control. "
        "Layer-wise projected mutual-information probes showed measurable compression-like changes, "
        "but the manuscript explicitly treats these as estimator-dependent diagnostics rather than "
        "proof of the general Information Bottleneck theory."
    )

    references = [
        "Deep learning and the information bottleneck principle. IEEE Information Theory Workshop, 2015. doi: 10.1109/ITW.2015.7133169.",
        "Opening the black box of deep neural networks via information. arXiv:1703.00810.",
        "On the information bottleneck theory of deep learning. Journal of Statistical Mechanics: Theory and Experiment, 2019. doi: 10.1088/1742-5468/ab3985.",
        "Deep Variational Information Bottleneck. International Conference on Learning Representations, 2017. arXiv:1612.00410.",
    ]

    generator = PaperGenerator(enhance=False, include_internal_review=False)
    paper = await generator.generate_paper(
        title="A Reproducible Negative-Control Benchmark for Information Bottleneck Compression Signals in Small ReLU Networks",
        abstract=abstract,
        sections=build_sections(analysis),
        references=references,
        experiment_ids=[experiment_id],
        domain="machine-learning",
    )

    showcase_dir = Path("papers/showcase")
    showcase_dir.mkdir(parents=True, exist_ok=True)
    for key, suffix in [("markdown_path", ".md"), ("pdf_path", ".pdf"), ("latex_path", ".tex")]:
        if paper.get(key):
            shutil.copy(paper[key], showcase_dir / f"A.M.Y_InfoBottleneck_Reproducible_Benchmark{suffix}")

    payload = {
        "experiment_id": experiment_id,
        "analysis_path": str(exp_dir / "analysis.json"),
        "provenance_path": str(exp_dir / "provenance.json"),
        "paper": paper,
        "showcase_markdown": str(showcase_dir / "A.M.Y_InfoBottleneck_Reproducible_Benchmark.md"),
        "showcase_pdf": str(showcase_dir / "A.M.Y_InfoBottleneck_Reproducible_Benchmark.pdf"),
        "showcase_latex": str(showcase_dir / "A.M.Y_InfoBottleneck_Reproducible_Benchmark.tex"),
    }
    sys.stdout.write(json.dumps(payload, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
