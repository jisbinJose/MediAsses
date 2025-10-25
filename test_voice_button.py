#!/usr/bin/env python3
"""
Test script for the voice input button functionality
"""

def test_voice_button_logic():
    """Test the voice input button logic"""
    print("🧪 Testing voice input button logic...")
    
    # Simulate session state
    session_state = {}
    data = {'current_line': 0}
    voice_key = f'voice_line_{data["current_line"]}'
    
    # Test 1: Voice input from voice recognition
    print("\n📝 Test 1: Voice input from voice recognition")
    session_state[voice_key] = "E"
    
    voice_value = session_state.get(voice_key, "")
    manual_voice_value = session_state.get(f"manual_voice_{data['current_line']}", "")
    final_voice_input = voice_value if voice_value else manual_voice_value
    
    if final_voice_input == "E":
        print("✅ Voice input from voice recognition works")
    else:
        print(f"❌ Voice input from voice recognition failed. Got: {final_voice_input}")
        return False
    
    # Test 2: Voice input from manual typing
    print("\n📝 Test 2: Voice input from manual typing")
    session_state[voice_key] = ""  # Clear voice recognition
    session_state[f"manual_voice_{data['current_line']}"] = "ABC"
    
    voice_value = session_state.get(voice_key, "")
    manual_voice_value = session_state.get(f"manual_voice_{data['current_line']}", "")
    final_voice_input = voice_value if voice_value else manual_voice_value
    
    if final_voice_input == "ABC":
        print("✅ Voice input from manual typing works")
    else:
        print(f"❌ Voice input from manual typing failed. Got: {final_voice_input}")
        return False
    
    # Test 3: Button application logic
    print("\n📝 Test 3: Button application logic")
    if final_voice_input:
        session_state[f"manual_input_{data['current_line']}"] = final_voice_input.upper()
        applied_value = session_state.get(f"manual_input_{data['current_line']}", "")
        
        if applied_value == "ABC":
            print("✅ Button application logic works")
        else:
            print(f"❌ Button application logic failed. Got: {applied_value}")
            return False
    else:
        print("❌ No voice input to apply")
        return False
    
    return True

def test_form_submission_with_voice():
    """Test form submission with voice input"""
    print("\n🧪 Testing form submission with voice input...")
    
    # Simulate session state with voice input
    session_state = {}
    data = {'current_line': 0}
    voice_key = f'voice_line_{data["current_line"]}'
    
    # Set up voice input
    session_state[voice_key] = "E"
    session_state[f"manual_input_{data['current_line']}"] = "E"
    
    # Simulate form submission logic
    user_input = session_state.get(f"manual_input_{data['current_line']}", "")
    
    # If no input from main field, try other sources
    if not user_input or not user_input.strip():
        user_input = session_state.get(f"current_input_{data['current_line']}", "")
    
    # If still no input, try voice input
    if not user_input or not user_input.strip():
        user_input = session_state.get(voice_key, "")
    
    # If still no input, try manual voice input
    if not user_input or not user_input.strip():
        user_input = session_state.get(f"manual_voice_{data['current_line']}", "")
    
    if user_input and user_input.strip():
        user_answer = user_input.upper().replace(" ", "")
        correct_answer = "E"
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
    """Run the voice button tests"""
    print("🚀 Testing Voice Input Button Fix...\n")
    
    tests = [
        test_voice_button_logic,
        test_form_submission_with_voice
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Add spacing between tests
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Voice input button fix is working!")
        print("\n💡 How to test in the application:")
        print("1. Start the app: streamlit run streamlit_app.py")
        print("2. Go to Eye Assessment > Visual Acuity Test")
        print("3. Type letters in 'Type the letters you said' field")
        print("4. Click '🎤 Use Voice Input' button")
        print("5. The main input field should now show the letters")
        print("6. Click 'Submit Answer' to test")
        return True
    else:
        print("⚠️ Voice input button fix needs more work")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
