import os
import sys
import asyncio
import time

# Evitar inicialización de base de datos en import
os.environ.setdefault('PYTEST_RUNNING', '1')
os.environ.setdefault('SKIP_DB_INIT', '1')
os.environ.setdefault('ENABLE_DATABASE', 'false')

# Asegurar path del proyecto
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.append(ROOT)

from app.services.protgpt2_service import ProtGPT2ProteinDesignService  # noqa: E402


async def run_real_protgpt2_test():
    print("=== ProtGPT2 Real Features Test ===")
    start = time.time()

    service = ProtGPT2ProteinDesignService()
    print(f"Model loaded: {service.model_loaded}")
    print(f"Device: {service.device}")
    print(f"Model name: {service.model_name}")

    if not service.model_loaded:
        print("ERROR: Model not loaded (using mock). Aborting real test.")
        return 1

    prompt = "small binding protein with high stability"

    # Intentar varias veces por si la secuencia es demasiado corta tras limpieza
    attempts = [
        dict(temperature=0.9, top_p=0.95, max_length=160),
        dict(temperature=0.8, top_p=0.9, max_length=200),
        dict(temperature=1.0, top_p=0.98, max_length=220),
    ]

    last_error = None
    for i, params in enumerate(attempts, 1):
        print(f"\nAttempt {i} with params: {params}")
        try:
            result = await service.generate_protein_sequence(prompt, **params)
            if result.get('success'):
                data = result['data']
                protein = data['generated_protein']
                seq = protein['sequence']
                perplexity = protein.get('perplexity_score')
                confidence = protein.get('confidence_score')

                print("SUCCESS: Real generation completed")
                print(f"Sequence length: {len(seq)}")
                print(f"Sequence preview: {seq[:80]}...")
                print(f"Perplexity: {perplexity:.2f}")
                print(f"Confidence: {confidence:.3f}")
                print("Properties:")
                for k, v in data['sequence_analysis']['properties'].items():
                    print(f"  - {k}: {v}")

                elapsed = time.time() - start
                print(f"Total time: {elapsed:.1f}s")
                return 0
            else:
                last_error = result.get('error')
                print(f"WARN: Generation failed: {last_error}")
        except Exception as e:
            last_error = str(e)
            print(f"ERROR: Exception during generation: {e}")

    print("\nFAIL: All attempts failed")
    if last_error:
        print(f"Last error: {last_error}")
    return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_real_protgpt2_test())
    sys.exit(exit_code)
