import json
from app.services.dnabert2_service import DNABERT2GenomicsService
from app.services.gnome_materials_service import GNOMEMaterialsService


def run():
    results = {"dnabert2": {}, "gnome": {}}

    # DNABERT-2: secuencia realista corta con motivos comunes
    seq = "ACGTATATAACGCGTTGCAATATA"
    dna = DNABERT2GenomicsService()
    results["dnabert2"]["motifs"] = dna.predict_motifs({"sequence": seq})
    results["dnabert2"]["promoter"] = dna.classify_promoter({"sequence": seq})

    # GNOME: sugerir candidatos para objetivo de catodo de batería
    gnome = GNOMEMaterialsService()
    results["gnome"]["suggestions"] = gnome.suggest_candidates({"target": "battery cathode", "top_n": 3})
    # Propiedades conocidas de un material común
    results["gnome"]["properties_LiFePO4"] = gnome.predict_properties({"formula": "LiFePO4"})

    with open("meta4_new_services_real_data.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    print("OK\nSaved -> meta4_new_services_real_data.json")


if __name__ == "__main__":
    run()
