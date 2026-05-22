from __future__ import annotations
import os
import json
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

# Intento opcional de usar transformer ligero si disponible, sin torchvision
os.environ.setdefault("TRANSFORMERS_NO_TORCHVISION", "1")
try:  # noqa: SIM105
    from sentence_transformers import SentenceTransformer  # type: ignore
    _ST_AVAILABLE = True
except Exception:  # pragma: no cover
    _ST_AVAILABLE = False
try:  # fallback huggingface base
    from transformers import AutoTokenizer, AutoModel  # type: ignore
    _HF_AVAILABLE = True
except Exception:
    _HF_AVAILABLE = False

ENRICHED_PATH = Path("data/plausibility_training_v4_enriched.jsonl")
OUT_PARQUET = Path("data/plausibility_training_v4_embeddings.parquet")
TFIDF_MODEL_PATH = Path("data/tfidf_v4.pkl")
MODEL_NAME = "distilbert-base-uncased"
ST_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
BATCH_SIZE = 64
TEXT_FIELD_PRIORITY = ["abstract", "title"]


def read_jsonl(p: Path) -> List[Dict[str, Any]]:
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]


def choose_text(record: Dict[str, Any]) -> str:
    for f in TEXT_FIELD_PRIORITY:
        val = record.get(f)
        if isinstance(val, str) and len(val.strip()) > 20:
            return val.strip()
    parts = [str(record.get("title") or ""), str(record.get("abstract") or "")]
    return " ".join([p for p in parts if p]).strip()


def build_transformer_embeddings(texts: List[str]) -> tuple[np.ndarray, str]:  # pragma: no cover (best-effort)
    import torch
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModel.from_pretrained(MODEL_NAME)
    model.eval()
    vecs: List[np.ndarray] = []
    with torch.no_grad():
        for i in range(0, len(texts), BATCH_SIZE):
            batch_texts = texts[i : i + BATCH_SIZE]
            toks = tokenizer(batch_texts, padding=True, truncation=True, max_length=256, return_tensors="pt")
            out = model(**toks)
            hidden = out.last_hidden_state  # (B, L, H)
            attn_mask = toks["attention_mask"].unsqueeze(-1)
            summed = (hidden * attn_mask).sum(dim=1)
            lengths = attn_mask.sum(dim=1)
            mean_pooled = summed / lengths
            mean_pooled = torch.nn.functional.normalize(mean_pooled, p=2, dim=1)
            vecs.append(mean_pooled.cpu().numpy())
    mat = np.vstack(vecs)
    return mat, "distilbert_mean_pool"


def build_tfidf_embeddings(texts: List[str]) -> tuple[np.ndarray, str]:
    tfidf = TfidfVectorizer(max_features=768, ngram_range=(1, 2))
    mat_sparse = tfidf.fit_transform(texts)
    mat = mat_sparse.toarray()
    joblib.dump(tfidf, TFIDF_MODEL_PATH)
    norms = np.linalg.norm(mat, axis=1, keepdims=True) + 1e-12
    mat = mat / norms
    return mat, "tfidf_ngrams"


def build_sentence_transformer(texts: List[str]) -> tuple[np.ndarray, str]:  # pragma: no cover
    model = SentenceTransformer(ST_MODEL_NAME)
    emb = model.encode(texts, batch_size=64, normalize_embeddings=True, show_progress_bar=False)
    return np.array(emb), 'st_all_minilm_l6'


def main():
    rows = read_jsonl(ENRICHED_PATH)
    if not rows:
        print("No hay datos enriquecidos para generar embeddings.")
        return
    texts = [choose_text(r) for r in rows]
    if _ST_AVAILABLE:
        try:
            mat, method = build_sentence_transformer(texts)
        except Exception as e:
            print(f"Fallo sentence-transformers ({e}); intentando HF base...")
            if _HF_AVAILABLE:
                try:
                    mat, method = build_transformer_embeddings(texts)
                except Exception as e2:
                    print(f"Fallo HF base ({e2}); usando TF-IDF.")
                    mat, method = build_tfidf_embeddings(texts)
            else:
                mat, method = build_tfidf_embeddings(texts)
    elif _HF_AVAILABLE:
        try:
            mat, method = build_transformer_embeddings(texts)
        except Exception as e:
            print(f"Fallo HF base ({e}); usando TF-IDF.")
            mat, method = build_tfidf_embeddings(texts)
    else:
        mat, method = build_tfidf_embeddings(texts)
    ids: List[str] = []
    for r in rows:
        pid = r.get("paper_id") or r.get("doi") or r.get("id") or str(abs(hash((r.get("title") or "") + str(r.get("year")))))
        ids.append(pid)
    df = pd.DataFrame({"paper_id": ids, "embedding": list(mat.tolist()), "embedding_method": method})
    OUT_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT_PARQUET, index=False)
    print(f"Embeddings guardados: {OUT_PARQUET} ({len(df)} registros, dim={mat.shape[1]}, método={method})")


if __name__ == "__main__":
    main()
