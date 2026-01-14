"""
System Health Check Script
Tests all critical endpoints and functionality
"""
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:1356/api/v1"

def test_health():
    """Test health endpoint"""
    print("[TEST] Testing /health...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "models_loaded" in data
        print(f"   [OK] Health: {data['status']}, Models: {data['models_loaded']}")
        return True
    except Exception as e:
        print(f"   [FAIL] Health check failed: {e}")
        return False

def test_models_info():
    """Test models info endpoint"""
    print("[TEST] Testing /models/info...")
    try:
        response = requests.get(f"{BASE_URL}/models/info", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert "num_models" in data
        assert data["num_models"] == 3
        print(f"   [OK] Models info: {data['num_models']} models loaded")
        return True
    except Exception as e:
        print(f"   [FAIL] Models info failed: {e}")
        return False

def test_classes():
    """Test classes endpoint"""
    print("[TEST] Testing /models/classes...")
    try:
        response = requests.get(f"{BASE_URL}/models/classes", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert "total_classes" in data
        assert data["total_classes"] == 11
        print(f"   [OK] Classes: {data['total_classes']} classes")
        return True
    except Exception as e:
        print(f"   [FAIL] Classes failed: {e}")
        return False

def test_statistics():
    """Test statistics endpoint"""
    print("[TEST] Testing /statistics...")
    try:
        response = requests.get(f"{BASE_URL}/statistics", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert "total_predictions" in data
        print(f"   [OK] Statistics: {data['total_predictions']} total predictions")
        return True
    except Exception as e:
        print(f"   [FAIL] Statistics failed: {e}")
        return False

def test_history():
    """Test history endpoint"""
    print("[TEST] Testing /history...")
    try:
        response = requests.get(f"{BASE_URL}/history?limit=5", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "predictions" in data
        print(f"   [OK] History: {len(data['predictions'])} records")
        return True
    except Exception as e:
        print(f"   [FAIL] History failed: {e}")
        return False

def test_model_files():
    """Check if model files exist"""
    print("[TEST] Checking model files...")
    model_files = [
        "../models/best_model_resnet50_improved.pth",
        "../models/best_model_efficientnet_b0_improved.pth",
        "../models/best_model_mobilenet_v3_large_improved.pth"
    ]
    
    all_exist = True
    for model_file in model_files:
        path = Path(__file__).parent / model_file
        if path.exists():
            size_mb = path.stat().st_size / (1024 * 1024)
            print(f"   [OK] {path.name}: {size_mb:.1f} MB")
        else:
            print(f"   [FAIL] {path.name}: NOT FOUND")
            all_exist = False
    
    return all_exist

def main():
    print("="*60)
    print("SYSTEM HEALTH CHECK")
    print("="*60)
    print()
    
    results = []
    
    # Test model files
    results.append(("Model Files", test_model_files()))
    print()
    
    # Test API endpoints
    results.append(("Health", test_health()))
    results.append(("Models Info", test_models_info()))
    results.append(("Classes", test_classes()))
    results.append(("Statistics", test_statistics()))
    results.append(("History", test_history()))
    
    print()
    print("="*60)
    print("RESULTS")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{name:20} {status}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("[SUCCESS] All tests passed! System is healthy.")
        return 0
    else:
        print("[WARNING] Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())

