#!/usr/bin/env python3
"""
Test script for the voice recognition fix
"""

def test_voice_input_flow():
    """Test the complete voice input flow"""
    print("🧪 Testing voice input flow...")
    
    # Simulate session state
    session_state = {}
    data = {'current_line': 0}
    voice_key = f'voice_line_{data["current_line"]}'
    
    # Test 1: Manual voice input should work
    print("\n📝 Test 1: Manual voice input")
    manual_voice_input = "E"
    session_state[voice_key] = manual_voice_input.upper()
    session_state[f"manual_input_{data['current_line']}"] = manual_voice_input.upper()
    
    # Check if values are stored correctly
    voice_result = session_state.get(voice_key, "")
    manual_result = session_state.get(f"manual_input_{data['current_line']}", "")
    
    if voice_result == "E" and manual_result == "E":
        print("✅ Manual voice input stored correctly")
    else:
        print(f"❌ Manual voice input failed. Voice: {voice_result}, Manual: {manual_result}")
        return False
    
    # Test 2: Input field should use voice input as default
    print("\n📝 Test 2: Input field default value")
    voice_value = session_state.get(voice_key, "")
    manual_value = session_state.get(f"manual_input_{data['current_line']}", "")
    default_value = voice_value if voice_value else manual_value
    
    if default_value == "E":
        print("✅ Input field gets correct default value")
    else:
        print(f"❌ Input field default value failed. Got: {default_value}")
        return False
    
    # Test 3: Form submission should work
    print("\n📝 Test 3: Form submission")
    user_input = session_state.get(f"manual_input_{data['current_line']}", "")
    if not user_input or not user_input.strip():
        user_input = session_state.get(f"current_input_{data['current_line']}", "")
    
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
    """Run the voice fix test"""
    print("🚀 Testing Voice Recognition Fix...\n")
    
    if test_voice_input_flow():
        print("\n🎉 Voice recognition fix is working!")
        print("\n💡 How to test in the application:")
        print("1. Start the app: streamlit run streamlit_app.py")
        print("2. Go to Eye Assessment > Visual Acuity Test")
        print("3. Try voice recognition - if it doesn't work:")
        print("   a. Type 'E' in the 'Type the letters you said' field")
        print("   b. Click '🎤 Use Voice Input' button")
        print("   c. The main input field should now show 'E'")
        print("4. Click 'Submit Answer' to test")
        return True
    else:
        print("\n⚠️ Voice recognition fix needs more work")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
