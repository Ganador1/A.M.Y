# Examples (Selected)

Colección reducida de ejemplos prácticos. Para lista completa usar `/docs` interactivo.

## Topología

```bash
curl -X POST http://localhost:8000/api/topology/report -H "Content-Type: application/json" -d '{"points":[[0,0],[1,1],[2,2]]}'
```

## Derivadas Parciales

```bash
curl -X POST http://localhost:8000/calculus/partial-derivative -H "Content-Type: application/json" -d '{"expression":"x*y**2","variables":["x","y"],"points":{"x":2,"y":3}}'
```

## PDE (Calor 1D)

```bash
curl -X POST http://localhost:8000/pde/heat-1d -H "Content-Type: application/json" -d '{"length":1.0,"nx":10,"time":0.1}'
```

## Plausibility

```bash
curl -X POST http://localhost:8000/api/plausibility/evaluate -H "Content-Type: application/json" -d '{"hypothesis_id":"H1","domain":"physics","description":"New resonance pattern"}'
```

## Scheduler

```bash
curl -X POST http://localhost:8000/api/scheduler/jobs -H "Content-Type: application/json" -d '{"job_type":"analysis","payload":{"task":"topology_report"}}'
```
