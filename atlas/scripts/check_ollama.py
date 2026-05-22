
import requests
import os

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

def check_ollama():
    try:
        print(f"Checking Ollama at {OLLAMA_BASE_URL}...")
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"Ollama is running. Found {len(models)} models.")
            for m in models:
                print(f" - {m['name']}")
        else:
            print(f"Ollama returned status {response.status_code}")
    except Exception as e:
        print(f"Could not connect to Ollama: {e}")

if __name__ == "__main__":
    check_ollama()
