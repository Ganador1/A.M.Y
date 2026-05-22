#!/usr/bin/env python
"""Verifica firmas Ed25519 en manifests.

Uso:
  python scripts/verify_manifest_signatures.py \
      --models-dir models \
      --public-keys-dir keys/public \
      --output reports/manifest_signature_report.json

Formato claves públicas: archivos PEM (SubjectPublicKeyInfo). El fingerprint se calcula
sha256(DER) igual que en sign_manifest.py. Los nombres de archivo pueden ser libres;
se construye índice por fingerprint.

El reporte JSON incluye por manifest:
  - path
  - total_signatures
  - valid_signatures
  - invalid_signatures (lista con detalles)
  - missing_public_keys (fingerprints sin clave local)
  - unsigned (bool)
  - overall_valid (bool) -> true si todas las firmas presentes son válidas y no faltan claves

Salida global: summary con counts.

Exit code 0 siempre a menos que se use --fail-on-error para endurecer.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
from pathlib import Path
from typing import Dict, Any, List

try:  # pragma: no cover
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from cryptography.exceptions import InvalidSignature
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Dependencia 'cryptography' requerida. Instala con: pip install cryptography") from exc


def load_public_keys(dir_path: Path) -> Dict[str, Ed25519PublicKey]:
    mapping: Dict[str, Ed25519PublicKey] = {}
    if not dir_path.exists():
        return mapping
    for pem_file in dir_path.glob("*.pem"):
        data = pem_file.read_bytes()
        try:
            pub = serialization.load_pem_public_key(data)
        except ValueError:  # archivo corrupto o formato incorrecto
            continue
        if not isinstance(pub, Ed25519PublicKey):
            # Ignorar otros tipos de clave (no soportados para este flujo)
            continue
        der = pub.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        fingerprint = hashlib.sha256(der).hexdigest()
        mapping[fingerprint] = pub  # último gana si colisión improbable
    return mapping


def compute_payload(manifest: Dict[str, Any]) -> bytes:
    clone = {k: v for k, v in manifest.items() if k != "signatures"}
    return json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()


def verify_manifest(path: Path, public_keys: Dict[str, Ed25519PublicKey]) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    sigs = data.get("signatures", [])
    result = {
        "path": str(path),
        "total_signatures": len(sigs),
        "valid_signatures": 0,
        "invalid_signatures": [],
        "missing_public_keys": [],
        "unsigned": len(sigs) == 0,
        "overall_valid": True,
    }
    if not sigs:
        result["overall_valid"] = False
        return result
    payload = compute_payload(data)
    for idx, sig_entry in enumerate(sigs):
        fp = sig_entry.get("public_key_fingerprint")
        sig_b64 = sig_entry.get("sig")
        if not fp or not sig_b64:
            result["invalid_signatures"].append({"index": idx, "reason": "missing_fields"})
            continue
        pub = public_keys.get(fp)
        if pub is None:
            result["missing_public_keys"].append(fp)
            continue
        try:
            signature = base64.b64decode(sig_b64)
            pub.verify(signature, payload)
            result["valid_signatures"] += 1
        except (InvalidSignature, ValueError) as e:  # pragma: no cover
            result["invalid_signatures"].append({"index": idx, "reason": type(e).__name__})
    if result["missing_public_keys"] or result["invalid_signatures"]:
        result["overall_valid"] = False
    return result


def aggregate(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(results)
    unsigned = sum(1 for r in results if r["unsigned"])
    manifests_with_errors = sum(1 for r in results if not r["overall_valid"])
    # all_valid: al menos uno y ninguno con error y ninguno unsigned
    all_valid = total > 0 and manifests_with_errors == 0 and unsigned == 0
    return {
        "total_manifests": total,
        "unsigned": unsigned,
        "all_valid": all_valid,
        "manifests_with_errors": manifests_with_errors,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--models-dir", default="models")
    p.add_argument("--public-keys-dir", default="keys/public")
    p.add_argument("--output", default="reports/manifest_signature_report.json")
    p.add_argument("--fail-on-error", action="store_true", help="Salir !=0 si hay errores")
    args = p.parse_args()
    models_dir = Path(args.models_dir)
    pub_dir = Path(args.public_keys_dir)
    out = Path(args.output)
    manifests = sorted(models_dir.glob("*.manifest.json"))
    public_keys = load_public_keys(pub_dir)
    results = [verify_manifest(m, public_keys) for m in manifests]
    report = {"results": results, "summary": aggregate(results)}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))
    if args.fail_on_error and not report["summary"]["all_valid"]:
        return 1
    return 0

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
