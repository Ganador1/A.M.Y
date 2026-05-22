#!/usr/bin/env python
"""Firmar manifests con Ed25519.

Uso:
  python scripts/sign_manifest.py --manifest models/plausibility_v4_rf.manifest.json --private-key keys/ed25519_private.key --public-key-out keys/ed25519_public.pem

Si no existe la clave privada, se genera automáticamente (carpeta destino debe existir o se crea).
La firma se añade a la sección `signatures` del manifest (alg=ed25519, sig=base64, public_key_fingerprint=sha256 del public key DER).

Requisitos: cryptography
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

try:  # pragma: no cover
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
except ImportError:  # pragma: no cover
    Ed25519PrivateKey = None  # type: ignore
    serialization = None  # type: ignore


def _ensure_crypto():
    if Ed25519PrivateKey is None or serialization is None:  # pragma: no cover - ruta error
        raise SystemExit("Dependencia 'cryptography' no instalada. Instala con: pip install cryptography")
    # Pistas para análisis estático
    assert Ed25519PrivateKey is not None
    assert serialization is not None


def load_or_create_private_key(path: Path) -> Any:
    _ensure_crypto()
    # A partir de aquí el analizador sabe que no son None
    assert Ed25519PrivateKey is not None
    assert serialization is not None
    if path.exists():
        data = path.read_bytes()
        return serialization.load_pem_private_key(data, password=None)
    key = Ed25519PrivateKey.generate()
    path.parent.mkdir(parents=True, exist_ok=True)
    pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    path.write_bytes(pem)
    return key


def write_public_key(key, path: Path) -> str:
    _ensure_crypto()
    assert serialization is not None
    public = key.public_key()
    pem = public.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(pem)
    # Fingerprint (sha256 del DER)
    der = public.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return hashlib.sha256(der).hexdigest()


def compute_manifest_payload(manifest: Dict[str, Any]) -> bytes:
    # Excluir sección signatures para firmar determinísticamente
    clone = {k: v for k, v in manifest.items() if k != "signatures"}
    return json.dumps(clone, sort_keys=True, separators=(",", ":")).encode()


def sign_manifest(manifest_path: Path, priv_key_path: Path, pub_key_out: Path | None, with_timestamp: bool = False) -> None:
    if not manifest_path.exists():
        raise SystemExit(f"Manifest no encontrado: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    key = load_or_create_private_key(priv_key_path)
    if pub_key_out:
        fingerprint = write_public_key(key, pub_key_out)
    else:
        _ensure_crypto()
        assert serialization is not None
        public = key.public_key()
        der = public.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        fingerprint = hashlib.sha256(der).hexdigest()
    payload = compute_manifest_payload(manifest)
    signature = key.sign(payload)
    sig_b64 = base64.b64encode(signature).decode()
    manifest.setdefault("signatures", [])
    sig_entry = {
        "alg": "ed25519",
        "sig": sig_b64,
        "public_key_fingerprint": fingerprint,
    }
    if with_timestamp:
        sig_entry["ts"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    manifest["signatures"].append(sig_entry)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(json.dumps({"signed": str(manifest_path), "fingerprint": fingerprint}, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--private-key", required=True)
    parser.add_argument("--public-key-out", default=None)
    parser.add_argument("--with-timestamp", action="store_true", help="Añade campo ts con timestamp UTC ISO8601 a la firma")
    args = parser.parse_args()
    sign_manifest(
        Path(args.manifest),
        Path(args.private_key),
        Path(args.public_key_out) if args.public_key_out else None,
        with_timestamp=args.with_timestamp,
    )
    return 0

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
