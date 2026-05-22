import json

with open("pipeline_v32_neuroscience_20251101_223558.json") as f:
    data = json.load(f)

print("=" * 80)
print("📊 ANÁLISIS PIPELINE V3.2 - POST-PROCESSING DE KEYWORDS")
print("=" * 80)
print()

# Scores
scores = data["scores"]
pub = data["publication"]

print("🏆 SCORE FINAL:", round(scores["overall"], 3))
print()
print("📈 Componentes:")
print(f"   • Paper Quality:      {scores['paper_quality']:.3f}")
print(f"   • Tool Usage:         {scores['tool_usage']:.3f}")
print(f"   • Tool Success:       {scores['tool_success']:.3f}")
print(f"   • Keyword Coverage:   {scores['keyword_coverage']:.3f}")
print()

# Post-processing
print("🔍 POST-PROCESSING DE KEYWORDS:")
print(f"   • Coverage original:  {pub['original_coverage']:.1%} ({len([k for k in pub['keywords_found'] if k.lower() in pub['text'].lower()[:1000]])}/28 estimado)")
print(f"   • Coverage mejorado:  {pub['keyword_coverage']:.1%} ({len(pub['keywords_found'])}/28)")
print(f"   • ¿Aplicado?: {'SÍ' if pub['post_processing_applied'] else 'NO'}")
print(f"   • Palabras añadidas:  +{pub['word_count'] - 688}")
print()

# Keywords encontrados
kws = pub["keywords_found"]
print(f"✅ Keywords encontrados ({len(kws)}):")
for i in range(0, len(kws), 5):
    print(f"   {', '.join(kws[i:i+5])}")
print()

# Tools
tools = data["tool_evidence"]
print(f"🔧 HERRAMIENTAS:")
print(f"   • Ejecutadas: {tools['tools_executed']}")
print(f"   • Tasa éxito: {tools['success_rate']:.3f}")
print()

# Comparación
print("📊 PROGRESIÓN COMPLETA:")
versions = [
    ("v1.0 (baseline)", 0.424),
    ("v2.0 (keywords)", 0.505),
    ("v3.0 (PlotlyService)", 0.660),
    ("v3.1 (bug fix)", 0.755),
    ("v3.2 (post-processing)", scores["overall"])
]

for name, score in versions:
    print(f"   {name:30s} {score:.3f}")

print()
print(f"🎯 MEJORA TOTAL: {scores['overall'] - 0.424:.3f} puntos (+{((scores['overall'] / 0.424) - 1) * 100:.1f}%)")
print()

# Verificar target
if scores["overall"] >= 0.80:
    print("✅ ¡TARGET >0.80 ALCANZADO!")
else:
    print(f"⚠️  Falta {0.80 - scores['overall']:.3f} puntos para target 0.80")
print()
print("=" * 80)
