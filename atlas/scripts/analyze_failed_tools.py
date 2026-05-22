import json

with open("pipeline_v32_neuroscience_20251101_223558.json") as f:
    data = json.load(f)

print("=" * 80)
print("🔧 ANÁLISIS DE HERRAMIENTAS FALLIDAS")
print("=" * 80)
print()

evidence_items = data["tool_evidence"]["details"]["evidence_items"]

failed = [item for item in evidence_items if not item["success"]]
success = [item for item in evidence_items if item["success"]]

print(f"✅ Exitosas: {len(success)}/10")
print(f"❌ Fallidas: {len(failed)}/10")
print()

print("❌ HERRAMIENTAS FALLIDAS:")
print("-" * 80)
for i, item in enumerate(failed, 1):
    print(f"\n{i}. {item['source']} - {item['operation']}")
    print(f"   Error: {item['raw_result'].get('error', 'Unknown')}")
    print(f"   Tipo: {item['raw_result'].get('type', 'N/A')}")
    if 'supported_operations' in item['raw_result']:
        print(f"   Operaciones soportadas: {', '.join(item['raw_result']['supported_operations'][:3])}...")

print()
print("=" * 80)
