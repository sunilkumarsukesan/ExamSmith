"""
Test script for response formatter
Run this to verify formatting is working correctly
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend" / "retrival"))

from services.response_formatter import ResponseFormatter, format_chat_response


def test_definition_formatting():
    """Test definition detection and formatting"""
    text = "A metaphor is defined as a figure of speech that describes something as if it were something else."
    result = format_chat_response(text)
    print("Test 1: Definition Formatting")
    print("Input:", text)
    print("Output:", result)
    print()


def test_list_formatting():
    """Test list detection and formatting"""
    text = """Here are the key features of poetry:

- Uses figurative language for effect
- Often has rhythm and meter
- Conveys deep emotions
- Uses literary devices like metaphor"""
    
    result = format_chat_response(text)
    print("Test 2: List Formatting")
    print("Input:", text)
    print("Output:")
    print(result)
    print()


def test_numbered_list():
    """Test numbered list formatting"""
    text = """Steps to analyze a poem:

1. Read the poem carefully and understand the basic meaning
2. Identify the literary devices used
3. Look for themes and messages
4. Consider the emotions conveyed"""
    
    result = format_chat_response(text)
    print("Test 3: Numbered List Formatting")
    print("Input:", text)
    print("Output:")
    print(result)
    print()


def test_key_point():
    """Test key point detection"""
    text = "Remember: Poetry requires careful reading to understand the deeper meanings and symbolism."
    result = format_chat_response(text)
    print("Test 4: Key Point Formatting")
    print("Input:", text)
    print("Output:", result)
    print()


def test_complex_response():
    """Test complex response with multiple elements"""
    text = """The poem "Where the Mind is Without Fear" is a powerful work of literature. Here's what you need to know:

Theme Definition: The main message is about freedom and self-determination

Key Concepts:
- Freedom of thought and expression
- Pursuit of knowledge
- Individual empowerment
- Critique of societal constraints

Important: This poem reflects Tagore's vision of an ideal nation.

Example: The line "Where the mind is without fear" itself is a metaphor for complete freedom.

Remember: Understanding the context helps in appreciating the poem's significance."""
    
    result = format_chat_response(text)
    print("Test 5: Complex Response Formatting")
    print("Input:", text[:100] + "...")
    print("Output:")
    print(result)
    print()


def test_plain_text():
    """Test with plain paragraph"""
    text = "Poetry is a creative form of expression that uses language in unique and artistic ways to convey emotions and ideas."
    result = format_chat_response(text)
    print("Test 6: Plain Text Formatting")
    print("Input:", text)
    print("Output:", result)
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("Response Formatter Test Suite")
    print("=" * 60)
    print()
    
    try:
        test_definition_formatting()
        test_list_formatting()
        test_numbered_list()
        test_key_point()
        test_complex_response()
        test_plain_text()
        
        print("=" * 60)
        print("All tests completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
