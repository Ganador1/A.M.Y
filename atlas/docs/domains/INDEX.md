# Índice de dominios (canónico)

Este directorio centraliza la documentación **canónica** por dominio. En el código existen archivos de documentación dentro de `app/domains/<dominio>/*.md`; esos archivos suelen ser buenos como “notas cercanas al código”, pero pueden quedar desfasados o duplicados.

Regla práctica recomendada:
- Documentación navegable y estable: `docs/domains/<dominio>/...`
- Notas cercanas al código: `app/domains/<dominio>/*.md`

## Dominios
- Astronomy: `docs/domains/astronomy/README.md`
- Climate: `docs/domains/climate/README.md`
- Chemistry: `docs/domains/chemistry/README.md`
- Engineering: `docs/domains/engineering/README.md`
- Medicine: `docs/domains/medicine/README.md`
- Neuroscience: `docs/domains/neuroscience/README.md`
- Physics: `docs/domains/physics/README.md`

## Dominios ya existentes en docs/
- Biology: `docs/domains/biology/README.md`
- Mathematics: `docs/domains/mathematics/README.md`

## Notas
- Los routers “consolidados por dominio” suelen vivir en `app/domains/<dominio>/routers/api.py` y declaran un `prefix` (por ejemplo `"/astronomy"`). El **path final** depende de dónde se incluya el router en la app.
- Los routers “de plataforma” (muchos endpoints) viven en `app/routers/` y se registran vía `app/routers/router_registry.py`.
