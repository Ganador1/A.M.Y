# Pruebas nativas y uso de evidencia científica

AMY ejecuta su ciclo cognitivo real: el modelo elige entradas, acciones y conclusión. El operador define la tarea, los recursos y el contrato de evaluación. El código de herramientas, instrumentación y auditoría fue escrito por Codex; estas reproducciones de modelos conocidos no son descubrimientos científicos nuevos.

## Perfil mejor probado hasta ahora

La matriz de 36 misiones (H₂, SSH y selección diploide) obtuvo 12/12 aciertos con `qwen3.5:397b`, 8/12 con `deepseek-v4-flash:0731-cloud` y 4/12 con `glm-5.3-flash`. En Qwen, `certified_summary` mantuvo 6/6 aciertos y redujo 41,55% los tokens de entrada frente a las seis misiones con contexto completo. DeepSeek tuvo menor latencia, con más fallos científicos. Son dos repeticiones por tarea/perfil: no establecen superioridad general.

Para esas tareas el perfil probado solicita temperatura 0,2, `think=false` en Qwen/DeepSeek (`low` en GLM), contexto de 32.768 tokens, máximo de 6.144 tokens de salida y seis ciclos. El límite de salida es un máximo, no consumo fijo. Los contadores pertenecen al proveedor; los tokenizadores y modos de razonamiento difieren. No equivalen a precio ni a créditos de cuenta. Kimi está excluido del controlador.

La prueba posterior de memoria añadió 12 ejecuciones nuevas H₂: seis con índice de recibos y seis con sólo las últimas observaciones. El índice obtuvo 6/6 aciertos frente a 4/6; necesitó 154.495 tokens de entrada frente a 122.423 (+26,2%). Ambos grupos ejecutaron 29 cálculos. El índice mejora la disponibilidad de evidencia antigua; el tamaño y diseño de la muestra no prueban una mejora universal de precisión ni velocidad.

## Ejecutar una campaña nueva

Desde la raíz del repositorio, usando un directorio nuevo:

```bash
.venv/bin/python scripts/run/run_native_science_benchmark.py \
  --campaign-dir output/native-science-nueva \
  --execute --model qwen35 --profile certified_summary
```

Ese comando ejecuta seis misiones: tres ramas, dos repeticiones, memoria vacía por fila. El plan conserva las 36 combinaciones posibles; sus filtros declaran cuáles se ejecutan. Se registran fallos y filas sin resultado, y el controlador rechaza sobrescribir o saltar silenciosamente una misión existente. El código actual incluye la corrección de memoria: sus resultados deben analizarse como una campaña nueva, sin sustituir la matriz histórica.

Para repetir el contraste de memoria completo:

```bash
.venv/bin/python scripts/run/run_receipt_memory_validation.py \
  --campaign-dir output/receipt-memory-nueva --execute
```

El controlador conserva fuentes, configuración efectiva, plan, solicitudes y respuestas, decisiones, herramientas, verificaciones y memoria. Necesita Ollama Cloud configurado en el entorno. Los scripts no imprimen claves.

## Qué certifica cada capa

| Capa | Comprobación | Límite |
|---|---|---|
| Integridad | Hashes, secuencia, sellos y fuentes retenidas | Una raíz guardada fuera permite detectar cambios; no autentica al proveedor |
| Causalidad | Respuesta completa → decisión → entrada → herramienta → verificación → aprendizaje | No expone procesos internos del modelo ni garantiza todo código no instrumentado |
| H₂ | Reconstrucción numérica independiente de RHF/STO-3G con NumPy | Comparte integrales PySCF/libcint; no es una cota rigurosa ni otro motor de integrales |
| SSH | Desigualdades racionales para la brecha al cuadrado | Cadena finita abierta, hoppings positivos y onsite cero |
| Selección diploide | Recuento mendeliano exacto y trayectorias finitas racionales | Modelo ideal sin deriva/mutación/migración; no evidencia empírica |
| Conclusión | Afirmación estructurada e IDs comparados con mediciones reales | No verifica toda la prosa ni la novedad científica |

`new_facts` es un nombre heredado del protocolo del modelo. En la ruta nativa se guarda ahora en `SemanticMemory.claims`, con estado `unverified_model_claim`, confianza autoestimada y referencias separadas. No se convierte en un hecho por repetirse. Los hechos históricos permanecen; otras rutas de consolidación/reflexión necesitan revisión específica.

El índice conserva los recibos del proceso y muestra hasta 64 dentro de 48.000 caracteres. Declara cualquier omisión. Un índice incompleto no justifica afirmar un mínimo sobre experimentos ausentes. Los resultados crudos permanecen en la evidencia aunque no se muestren todos en el prompt.

## Revisar el paquete histórico

```bash
.venv/bin/python scripts/verify/package_native_science.py verify \
  output/amy-optimization-20260906/native-matrix-v1-package \
  --expected-root 6333230dc48314ab31b52e5489fb05b45bd87701dff11471bff5dae7d6b8c025
```

La orden `replay` del mismo script, con esa raíz y `--execute-verified-toolkit`, ejecuta únicamente el toolkit congelado en Python aislado con sockets bloqueados. No arranca AMY ni consulta modelos. En el paquete de 36 corridas el replay conserva cinco fallos de traza, por lo que su código de salida no indica que todas hayan pasado. Deben inspeccionarse `replay_completed`, `trace_valid`, las evaluaciones de dominio y cada conclusión por separado.

Informe y paquetes: [campaña completa](../../output/amy-optimization-20260906/REPORT.md), [paquete de 36 misiones](../../output/amy-optimization-20260906/native-matrix-v1-package-report.md), [contratos locales](../../output/amy-optimization-20260906/coverage/FINAL_REPORT.md). Los contratos de QA local fueron elegidos por Codex y no se cuentan como investigaciones autónomas del agente.
