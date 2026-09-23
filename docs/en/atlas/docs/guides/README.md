> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="gestión-de-claves-públicas-integridad-de-manifests"></a>
# Public Key Management (Manifest Integrity)

This directory contains **only public keys** used to verify Ed25519 signatures of artifact manifests in `models/*.manifest.json`.

<a id="objetivo"></a>
## Purpose

Ensure integrity and traceability of scientific artifacts through:

- Deterministic signature (payload = manifest without `signatures` section).
- Reproducible verification in CI (`signature-verification` job).
- Fingerprints (`public_key_fingerprint`) derived from `sha256(DER(public_key))`.

<a id="estructura"></a>
## Structure

```text
keys/
  private/              # EXCLUIDO del repositorio (no se versiona)
  public/               # (Opcional) Subcarpeta alternativa para almacenar múltiples claves
  README.md             # Este archivo
  ed25519_public_<alias>.pem  # Claves públicas PEM (SubjectPublicKeyInfo)
```

You can keep all public keys directly here or in `keys/public/` (the CI job looks in `keys/public/` by default; adjust the workflow if you change the convention).

<a id="generación-de-una-nueva-clave"></a>
## Generating a new key

Private keys **must not** be uploaded to the repository. Example of local generation:

```bash
python - <<'PY'
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from pathlib import Path
priv = Ed25519PrivateKey.generate()
priv_pem = priv.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)
Path('ed25519_private.key').write_bytes(priv_pem)
pub = priv.public_key()
pub_pem = pub.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)
Path('keys/ed25519_public_default.pem').write_bytes(pub_pem)
print('Clave generada: ed25519_public_default.pem')
PY
```

<a id="huella-fingerprint"></a>
## Fingerprint

It is calculated internally (sha256 over DER). You can verify manually:

```bash
python - <<'PY'
from cryptography.hazmat.primitives import serialization, hashes
from hashlib import sha256
from pathlib import Path
pem = Path('keys/ed25519_public_default.pem').read_bytes()
pub = serialization.load_pem_public_key(pem)
der = pub.public_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)
print('Fingerprint:', sha256(der).hexdigest())
PY
```

<a id="flujo-de-firma"></a>
## Signing Flow

1. Make sure you have the secure local private key (`keys/private/` or outside the repo).
2. Run:

```bash
python scripts/sign_manifest.py --manifest models/<archivo>.manifest.json \
  --private-key path/a/ed25519_private.key \
  --public-key-out keys/ed25519_public_default.pem
  ```

  1. Haz commit del manifest modificado (sección `signatures` añadida) y de la clave pública si es nueva.

<a id="verificación-local"></a>
## Verificación Local

 
```bash
python scripts/verify_manifest_signatures.py --models-dir models \
  --public-keys-dir keys
```

If your keys are in `keys/public/` use `--public-keys-dir keys/public`.

<a id="rotación-de-claves"></a>
## Key Rotation

Recommended every 90 days or if there is suspicion of compromise:

1. Generate a new key pair.
2. Re-sign all manifests with the new key (optionally keep previous signatures during transition).
3. Delete the old public key after validating that all manifests have the new signature.

<a id="política-de-seguridad"></a>
## Security Policy

- Do not upload private keys.
- Review PRs that add/alter public keys.
- Verify in CI (report `manifest-signature-report` attached as an artifact).

<a id="próximas-extensiones-planeado"></a>
## Upcoming Extensions (Planned)

- Timestamping (OpenTimestamps) of manifest hashes.
- Merkle tree of scientific publications with inclusion proof.
- Endpoint `/api/v1/integrity/verify` returning consolidated status.

---
Keep this file updated if conventions or paths change.
