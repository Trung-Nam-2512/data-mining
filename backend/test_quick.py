"""
Quick API Test Script
"""
import requests
import json

BASE_URL = "http://localhost:1356/api/v1"

def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

def test_models_info():
    """Test models info endpoint"""
    print("\n=== Testing Models Info ===")
    response = requests.get(f"{BASE_URL}/models/info")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

def test_classes():
    """Test classes endpoint"""
    print("\n=== Testing Classes ===")
    response = requests.get(f"{BASE_URL}/models/classes")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total Classes: {data['total_classes']}")
    print(f"Poisonous: {data['poisonous_count']}, Edible: {data['edible_count']}")
    
def test_prediction(image_path: str):
    """Test prediction endpoint with an image"""
    print(f"\n=== Testing Prediction with {image_path} ===")
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            data = {'top_k': 3}
            response = requests.post(f"{BASE_URL}/predict", files=files, data=data)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print("\n🔍 Ensemble Prediction:")
                ensemble = result['ensemble_prediction']
                print(f"  Genus: {ensemble['genus']}")
                print(f"  Confidence: {ensemble['confidence']:.2f}%")
                print(f"  Toxicity: {ensemble['toxicity']['label']}")
                
                print("\n📊 Individual Models:")
                for model in result['individual_models']:
                    print(f"  - {model['model']}: {model['genus']} ({model['confidence']:.2f}%)")
            else:
                print(response.text)
    except FileNotFoundError:
        print(f"❌ File not found: {image_path}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("="*60)
    print("MUSHROOM CLASSIFICATION API - QUICK TEST")
    print("="*60)
    
    # Test basic endpoints
    test_health()
    test_models_info()
    test_classes()
    
    # Test prediction if you have a test image
    # Uncomment and provide path to your test image:
    # test_prediction("path/to/mushroom.jpg")
    
    print("\n" + "="*60)
    print("✅ All basic tests passed!")
    print("="*60)
    print("\n📖 For interactive testing, visit:")
    print("   http://localhost:1356/docs")
    print()


