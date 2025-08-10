import sys

def validate_model(model_name, ollama_url):
    try:
        response = requests.get(f"{ollama_url}/api/tags")
        available = [m["model"] for m in response.json().get("models", [])]
        if model_name not in available:
            print(f"❌ Model '{model_name}' not found in Ollama. Available: {available}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to connect to Ollama: {e}")
        sys.exit(1)

# Then call it before initializing
validate_model(model_name, ollama_url)