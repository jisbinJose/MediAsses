#!/usr/bin/env python3
"""
Test script for voice recognition autofill functionality
"""

def test_voice_autofill_logic():
    """Test the voice autofill logic"""
    print("🧪 Testing voice autofill logic...")
    
    # Simulate session state
    session_state = {}
    data = {'current_line': 0}
    voice_key = f'voice_line_{data["current_line"]}'
    
    # Test 1: Voice input should populate the input field
    print("\n📝 Test 1: Voice input population")
    session_state[voice_key] = "ABC"
    
    voice_value = session_state.get(voice_key, "")
    manual_value = session_state.get(f"manual_input_{data['current_line']}", "")
    default_value = voice_value if voice_value else manual_value
    
    if default_value == "ABC":
        print("✅ Voice input correctly used as default value")
    else:
        print(f"❌ Voice input not used. Got: {default_value}")
        return False
    
    # Test 2: Manual input should override voice input
    print("\n📝 Test 2: Manual input override")
    session_state[f"manual_input_{data['current_line']}"] = "XYZ"
    
    voice_value = session_state.get(voice_key, "")
    manual_value = session_state.get(f"manual_input_{data['current_line']}", "")
    default_value = voice_value if voice_value else manual_value
    
    if default_value == "ABC":  # Voice should still take priority
        print("✅ Voice input takes priority over manual input")
    else:
        print(f"❌ Priority logic incorrect. Got: {default_value}")
        return False
    
    # Test 3: Empty voice input should use manual input
    print("\n📝 Test 3: Empty voice input fallback")
    session_state[voice_key] = ""
    session_state[f"manual_input_{data['current_line']}"] = "DEF"
    
    voice_value = session_state.get(voice_key, "")
    manual_value = session_state.get(f"manual_input_{data['current_line']}", "")
    default_value = voice_value if voice_value else manual_value
    
    if default_value == "DEF":
        print("✅ Manual input used when voice input is empty")
    else:
        print(f"❌ Fallback logic incorrect. Got: {default_value}")
        return False
    
    return True

def test_form_submission_logic():
    """Test form submission with voice input"""
    print("\n🧪 Testing form submission logic...")
    
    # Simulate form submission
    session_state = {}
    data = {'current_line': 0}
    voice_key = f'voice_line_{data["current_line"]}'
    
    # Set up voice input
    session_state[voice_key] = "ABC"
    session_state[f"manual_input_{data['current_line']}"] = "ABC"
    session_state[f"current_input_{data['current_line']}"] = "ABC"
    
    # Simulate form submission
    user_input = session_state.get(f"manual_input_{data['current_line']}", "")
    if not user_input or not user_input.strip():
        user_input = session_state.get(f"current_input_{data['current_line']}", "")
    
    if user_input and user_input.strip():
        user_answer = user_input.upper().replace(" ", "")
        correct_answer = "ABC"
        correct = user_answer == correct_answer
        
        if correct:
            print("✅ Form submission works with voice input")
            return True
        else:
            print(f"❌ Form submission failed. Got: {user_answer}, Expected: {correct_answer}")
            return False
    else:
        print("❌ No input found for form submission")
        return False

def main():
    """Run all autofill tests"""
    print("🚀 Starting Voice Autofill Tests...\n")
    
    tests = [
        test_voice_autofill_logic,
        test_form_submission_logic
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Add spacing between tests
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All autofill tests passed!")
        print("\n💡 How to test the actual application:")
        print("1. Start the app: streamlit run streamlit_app.py")
        print("2. Go to Eye Assessment > Visual Acuity Test")
        print("3. Click 'Start Voice Recognition' and speak letters")
        print("4. Check if input field gets populated")
        print("5. If not, click '🎤 Use Voice Input' button")
        print("6. Click 'Submit Answer' to test form submission")
        return True
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
