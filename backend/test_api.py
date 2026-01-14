"""
Simple API test script
Run this after starting the API to verify it works
"""
import requests
import json
from pathlib import Path

API_URL = "http://localhost:1356"


def test_health():
    """Test health endpoint"""
    print("\n1. Testing /api/v1/health...")
    try:
        response = requests.get(f"{API_URL}/api/v1/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_models_info():
    """Test models info endpoint"""
    print("\n2. Testing /api/v1/models/info...")
    try:
        response = requests.get(f"{API_URL}/api/v1/models/info")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_classes():
    """Test classes endpoint"""
    print("\n3. Testing /api/v1/models/classes...")
    try:
        response = requests.get(f"{API_URL}/api/v1/models/classes")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Total classes: {data.get('total_classes')}")
        print(f"   Poisonous: {data.get('poisonous_count')}")
        print(f"   Edible: {data.get('edible_count')}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_prediction(image_path: str):
    """Test prediction endpoint"""
    print(f"\n4. Testing /api/v1/predict with image...")
    
    if not Path(image_path).exists():
        print(f"   ⚠️ Image not found: {image_path}")
        print(f"   Skipping prediction test")
        return False
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (Path(image_path).name, f, 'image/jpeg')}
            data = {'top_k': 3}
            
            response = requests.post(
                f"{API_URL}/api/v1/predict",
                files=files,
                data=data
            )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            pred = result['ensemble_prediction']
            print(f"   ✅ Prediction: {pred['genus']} ({pred['confidence']:.1f}%)")
            print(f"   Toxicity: {pred['toxicity']['label']}")
            print(f"   Processing time: {result.get('processing_time_ms', 0):.0f}ms")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("="*70)
    print("Mushroom Classification API - Test Script")
    print("="*70)
    
    results = []
    
    # Test 1: Health
    results.append(("Health Check", test_health()))
    
    # Test 2: Models Info
    results.append(("Models Info", test_models_info()))
    
    # Test 3: Classes
    results.append(("Classes", test_classes()))
    
    # Test 4: Prediction (with sample image if available)
    # Thay đổi path này thành đường dẫn ảnh test của bạn
    sample_image = "../tests/test_data/sample_images/mushroom.jpg"
    results.append(("Prediction", test_prediction(sample_image)))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:<20} {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*70)


if __name__ == "__main__":
    main()


