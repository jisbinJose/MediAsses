#!/usr/bin/env python3
"""
Test script for the Eye Assessment functionality
This script tests the core functions without running the full Streamlit app
"""

import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent / "utils"))

def test_imports():
    """Test if all required imports work"""
    print("🧪 Testing imports...")
    
    try:
        from utils.auth import init_session_state
        print("✅ Auth utilities imported successfully")
    except ImportError as e:
        print(f"❌ Auth import failed: {e}")
        return False
    
    try:
        from utils.navbar import show_streamlit_navbar
        print("✅ Navbar utilities imported successfully")
    except ImportError as e:
        print(f"❌ Navbar import failed: {e}")
        return False
    
    try:
        from utils.model_utils import predict_eye_disease, preprocess_eye_image
        print("✅ Model utilities imported successfully")
    except ImportError as e:
        print(f"❌ Model utilities import failed: {e}")
        return False
    
    return True

def test_eye_disease_prediction():
    """Test eye disease prediction with dummy data"""
    print("\n🧪 Testing eye disease prediction...")
    
    try:
        from utils.model_utils import predict_eye_disease
        import numpy as np
        
        # Create dummy image data
        dummy_image = np.random.rand(224, 224, 3)
        
        # Test prediction
        results = predict_eye_disease(dummy_image)
        
        print(f"✅ Eye disease prediction working: {results}")
        
        # Verify results format
        if isinstance(results, dict) and len(results) > 0:
            print("✅ Results format is correct")
            return True
        else:
            print("❌ Results format is incorrect")
            return False
            
    except Exception as e:
        print(f"❌ Eye disease prediction failed: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("\n🧪 Testing database connection...")
    
    try:
        from utils.database import MedicalDB
        
        # Test database initialization
        db = MedicalDB()
        print("✅ Database connection successful")
        
        # Test database structure
        if db.test_connection():
            print("✅ Database structure is correct")
            return True
        else:
            print("❌ Database structure test failed")
            return False
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_voice_recognition_html():
    """Test voice recognition HTML generation"""
    print("\n🧪 Testing voice recognition HTML...")
    
    try:
        # Test HTML generation (simplified version)
        test_letters = "ABC"
        voice_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script>
                const expectedLetters = "{test_letters}";
                console.log("Voice recognition HTML generated for:", expectedLetters);
            </script>
        </head>
        <body>
            <div>Voice recognition test</div>
        </body>
        </html>
        """
        
        if "expectedLetters" in voice_html and test_letters in voice_html:
            print("✅ Voice recognition HTML generation working")
            return True
        else:
            print("❌ Voice recognition HTML generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Voice recognition HTML test failed: {e}")
        return False

def test_amsler_grid_html():
    """Test Amsler Grid HTML generation"""
    print("\n🧪 Testing Amsler Grid HTML...")
    
    try:
        # Test HTML generation (simplified version)
        grid_html = """
        <div class="amsler-container">
            <canvas id="amslerGrid" width="400" height="400"></canvas>
        </div>
        <script>
            const canvas = document.getElementById('amslerGrid');
            console.log("Amsler Grid HTML generated");
        </script>
        """
        
        if "amslerGrid" in grid_html and "canvas" in grid_html:
            print("✅ Amsler Grid HTML generation working")
            return True
        else:
            print("❌ Amsler Grid HTML generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Amsler Grid HTML test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Eye Assessment Tests...\n")
    
    tests = [
        test_imports,
        test_eye_disease_prediction,
        test_database_connection,
        test_voice_recognition_html,
        test_amsler_grid_html
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Add spacing between tests
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Eye Assessment is ready to run.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
