"""
Test simple del pipeline de hipótesis usando endpoints disponibles
"""
import json
import http.client
import uuid

BASE_URL = "localhost:8002"

def test_endpoints():
    print("🧪 Probando endpoints disponibles...")
    
    # 1. Probar endpoint de generación de hipótesis existente
    conn = http.client.HTTPConnection(BASE_URL, timeout=30)
    
    # Usar el endpoint que existe: /api/scientific-hypothesis/generate-hypothesis
    payload = {
        "domain": "mathematics",
        "topic": "prime number patterns",
        "complexity": "basic"
    }
    
    headers = {"Content-Type": "application/json"}
    body = json.dumps(payload)
    
    try:
        conn.request("POST", "/api/scientific-hypothesis/generate-hypothesis", body=body, headers=headers)
        resp = conn.getresponse()
        data = resp.read().decode("utf-8")
        
        print(f"📊 Generación de hipótesis (status {resp.status}):")
        try:
            result = json.loads(data)
            print(json.dumps(result, indent=2)[:500], "...")
            
            if resp.status == 200 and "hypothesis" in data.lower():
                print("✅ Endpoint de generación funciona")
                return True
        except:
            print(f"Raw response: {data[:200]}...")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error conectando: {e}")
        
    return False

if __name__ == "__main__":
    test_endpoints()