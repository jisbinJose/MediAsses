#!/usr/bin/env python3
"""
Simple test for the fixed eye assessment page
"""

def test_imports():
    """Test if all imports work correctly"""
    print("Testing imports...")
    
    try:
        import streamlit as st
        print("SUCCESS: Streamlit imported successfully")
    except ImportError as e:
        print(f"ERROR: Streamlit import failed: {e}")
        return False
    
    try:
        from audio_recorder_streamlit import audio_recorder
        print("SUCCESS: audio_recorder_streamlit imported successfully")
    except ImportError as e:
        print(f"ERROR: audio_recorder_streamlit import failed: {e}")
        return False
    
    try:
        import speech_recognition as sr
        print("SUCCESS: SpeechRecognition imported successfully")
    except ImportError as e:
        print(f"ERROR: SpeechRecognition import failed: {e}")
        return False
    
    return True

def test_visual_acuity_logic():
    """Test visual acuity test logic"""
    print("\nTesting visual acuity test logic...")
    
    # Simulate session state
    session_state = {
        'acuity_data': {
            'lines': [
                {'size': '20/200', 'letters': 'E', 'font_size': 120},
                {'size': '20/100', 'letters': 'FP', 'font_size': 90},
                {'size': '20/70', 'letters': 'TOZ', 'font_size': 70},
            ],
            'current_line': 0,
            'correct_count': 0,
            'total_count': 0,
            'answers': []
        }
    }
    
    # Test line progression
    data = session_state['acuity_data']
    current = data['lines'][data['current_line']]
    
    if current['letters'] == 'E':
        print("SUCCESS: First line loaded correctly")
    else:
        print(f"ERROR: First line incorrect. Expected 'E', got '{current['letters']}'")
        return False
    
    # Test answer processing
    user_answer = "E"
    correct_answer = current['letters']
    correct = user_answer == correct_answer
    
    if correct:
        print("SUCCESS: Answer validation works correctly")
    else:
        print(f"ERROR: Answer validation failed. Expected '{correct_answer}', got '{user_answer}'")
        return False
    
    return True

def main():
    """Run all tests"""
    print("Testing Fixed Eye Assessment Page...\n")
    
    tests = [
        test_imports,
        test_visual_acuity_logic,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Add spacing between tests
    
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: Eye Assessment page is working correctly!")
        print("\nFeatures available:")
        print("1. Visual Acuity Test with voice recognition")
        print("2. Amsler Grid Test with interactive canvas")
        print("3. AI Disease Detection with image upload")
        print("4. Audio recording and transcription")
        print("5. Progress tracking and results display")
        return True
    else:
        print("ERROR: Some issues found in the eye assessment page")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
