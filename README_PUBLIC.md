# A.M.Y

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache--2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](LICENSE)
[![Science: Verifiable](https://img.shields.io/badge/science-verifiable-green.svg)](SCIENCE_MANIFESTO.md)

> Una mente artificial autonoma para investigar, experimentar, validar y escribir resultados cientificos con trazabilidad reproducible.

---

## Estado Publico

| Area | Estado |
|---|---|
| Version | v1.0.0 |
| Ultima validacion | May 21, 2026 |
| Atlas | 94 herramientas cientificas en 23 dominios |
| Cobertura multi-dominio | 23 / 23 dominios generan papers end-to-end |
| Provenance | SHA-256 verificable por experimento |
| Licencia | Apache-2.0 |

El objetivo de A.M.Y no es producir texto plausible. El objetivo es ejecutar herramientas reales, guardar evidencia, rechazar afirmaciones sin provenance y mantener un registro que otra persona pueda auditar.

## Inicio Rapido

### Requisitos

- Python 3.13+
- macOS o Linux
- 8GB+ RAM recomendado
- Una clave de proveedor de modelos compatible con tu configuracion local

### Instalacion

```bash
git clone https://github.com/Ganador1/amy.git
cd amy

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

Edita `.env` con tus claves locales y ejecuta una verificacion rapida:

```bash
python test_amy_quick.py
```

### Ejecucion

```bash
# Ciclo corto de depuracion
python run_amy_debug.py

# Mision completa con generacion de paper
python run_amy_full_mission.py

# Generacion enfocada de paper
python run_amy_paper.py
```

## Arquitectura

A.M.Y mantiene un ciclo cognitivo continuo:

1. **Perceive**: sensores de literatura, archivos, tiempo y APIs recogen señales.
2. **Attend**: el workspace global decide que informacion merece foco.
3. **Think**: el razonamiento propone hipotesis y planes falsables.
4. **Act**: Atlas ejecuta herramientas cientificas o el sandbox ejecuta experimentos.
5. **Learn**: memoria episodica, semantica y procedimental registran resultados.

Atlas funciona como laboratorio cientifico debajo de A.M.Y. Sus herramientas cubren matematicas, fisica, quimica, biologia, medicina, estadistica, astronomia, neurociencia, materiales e ingenieria.

## Ciencia y Reproducibilidad

A.M.Y aplica cuatro reglas de publicacion:

- Toda afirmacion numerica debe venir de una ejecucion o una fuente verificable.
- Cada tool call escribe `data/experiments/<id>/provenance.json` y `output.txt`.
- El hash SHA-256 del output completo se cita en el paper.
- El auditor recomputa hashes y rechaza manuscritos con evidencia faltante o alterada.

Los papers curados viven en `papers/showcase/`. Los lotes de validacion multi-dominio viven en `experiments/all_domains/`.

## Seguridad y Uso Responsable

El proyecto incluye un safety kernel para bloquear usos de alto riesgo antes de ejecutar herramientas. La politica publica esta en [USE_POLICY.md](USE_POLICY.md) y los detalles de reporte estan en [SECURITY.md](SECURITY.md).

Restricciones principales:

- No desarrollo, optimizacion o asistencia para armas biologicas o quimicas.
- No vigilancia masiva ni abuso de datos personales.
- No instrucciones para evadir controles, robar credenciales o danar sistemas.
- Uso academico y comercial permitido mientras respete la licencia y la politica de uso.

## Documentacion

| Documento | Contenido |
|---|---|
| [README.md](README.md) | Estado tecnico completo |
| [SCIENCE_MANIFESTO.md](SCIENCE_MANIFESTO.md) | Principios cientificos |
| [ATLAS_TOOL_GUIDE.md](ATLAS_TOOL_GUIDE.md) | Integracion A.M.Y -> Atlas |
| [RESEARCH.md](RESEARCH.md) | Referencias y contexto |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Guia de contribucion |
| [SECURITY.md](SECURITY.md) | Reporte de vulnerabilidades y abuso |
| [USE_POLICY.md](USE_POLICY.md) | Politica de uso responsable |

## Licencia

Apache-2.0 - ver [LICENSE](LICENSE).

---

**Autor:** Giovanni Arangio

**Repositorio:** https://github.com/Ganador1/amy
