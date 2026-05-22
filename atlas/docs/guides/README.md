# Gestión de Claves Públicas (Integridad de Manifests)

Este directorio contiene **únicamente claves públicas** usadas para verificar firmas Ed25519 de los manifests de artefactos en `models/*.manifest.json`.

## Objetivo

Garantizar integridad y trazabilidad de artefactos científicos mediante:

- Firma determinística (payload = manifest sin sección `signatures`).
- Verificación reproducible en CI (`signature-verification` job).
- Huellas (`public_key_fingerprint`) derivadas de `sha256(DER(public_key))`.

## Estructura

```text
keys/
  private/              # EXCLUIDO del repositorio (no se versiona)
  public/               # (Opcional) Subcarpeta alternativa para almacenar múltiples claves
  README.md             # Este archivo
  ed25519_public_<alias>.pem  # Claves públicas PEM (SubjectPublicKeyInfo)
```

Puedes mantener todas las claves públicas directamente aquí o en `keys/public/` (el job CI busca en `keys/public/` por defecto; ajusta el workflow si cambias la convención).

## Generación de una nueva clave

Las claves privadas **no** deben subirse al repositorio. Ejemplo de generación local:

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

## Huella (fingerprint)

Se calcula internamente (sha256 sobre DER). Puedes verificar manualmente:

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

## Flujo de Firma

1. Asegúrate de tener la clave privada local segura (`keys/private/` o fuera del repo).
2. Ejecuta:

```bash
python scripts/sign_manifest.py --manifest models/<archivo>.manifest.json \
  --private-key path/a/ed25519_private.key \
  --public-key-out keys/ed25519_public_default.pem
  ```

  1. Haz commit del manifest modificado (sección `signatures` añadida) y de la clave pública si es nueva.

## Verificación Local

 
```bash
python scripts/verify_manifest_signatures.py --models-dir models \
  --public-keys-dir keys
```

Si tus claves están en `keys/public/` usa `--public-keys-dir keys/public`.

## Rotación de Claves

Recomendado cada 90 días o si hay sospecha de compromiso:

1. Generar nuevo par de claves.
2. Firmar nuevamente todos los manifests con la nueva clave (mantener firmas previas opcionalmente durante transición).
3. Eliminar la antigua clave pública tras validar que todos los manifests tienen la nueva firma.

## Política de Seguridad

- No subir claves privadas.
- Revisar PRs que añadan/alteren claves públicas.
- Verificar en CI (reporte `manifest-signature-report` adjunto como artefacto).

## Próximas Extensiones (Planeado)

- Timestamping (OpenTimestamps) de hashes de manifests.
- Árbol Merkle de publicaciones científicas con prueba de inclusión.
- Endpoint `/api/v1/integrity/verify` devolviendo estado consolidado.

---
Mantén este archivo actualizado si cambian convenciones o rutas.
