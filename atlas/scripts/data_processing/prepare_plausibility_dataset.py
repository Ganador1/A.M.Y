"""Script CLI para construir dataset de entrenamiento de plausibility.

Uso (después de poblar fuentes externas):
  python prepare_plausibility_dataset.py --out data/plausibility_training.jsonl --limit 10000

Actualmente usa solo stubs de PeerRead y Retracted; rellena TODO para producción.
"""
from __future__ import annotations
import argparse
from app.services.plausibility_dataset_builder import build_dataset, write_jsonl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/plausibility_training.jsonl")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    dataset = build_dataset(limit=args.limit)
    if not dataset:
        print("[WARN] Dataset vacío (rellenar fuentes). Se generará archivo placeholder.")
    write_jsonl(dataset, args.out)
    print(f"[OK] Escrito {len(dataset)} registros en {args.out}")


if __name__ == "__main__":  # pragma: no cover
    main()
