import json

with open("pipeline_v33_neuroscience_run3_20251101_224711.json") as f:
    data = json.load(f)

paper = data["publication"]["text"]

print("=" * 90)
print("📄 PAPER CIENTÍFICO GENERADO - AXIOM ATLAS v3.3")
print("=" * 90)
print()
print(paper)
print()
print("=" * 90)
print(f"📊 Palabras: {len(paper.split())}")
print(f"📚 Keywords: {len(data['publication']['keywords_found'])}/28")
print(f"🏆 Score: {data['scores']['overall']:.3f}")
print("=" * 90)
