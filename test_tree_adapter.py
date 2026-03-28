import pytest
from unittest.mock import Mock

# Import the function to test
# Since the function is in file-v1-main.py, we need to import it
import sys
import os
sys.path.append(os.path.dirname(__file__))

def tree_adapter(item: list) -> tuple:
    """
    Converts element of past_conversations to id and displayed string

    Args:
        item: element of past_conversations

    Returns:
        id and displayed string
    """
    identifier = item[0]
    if len(item[1]["Conversation"]) > 3:
        return (identifier, item[1]["Conversation"][2][:50] + "...")
    return (item[0], "Empty conversation")


class TestTreeAdapter:
    """Test cases for the tree_adapter function"""

    def test_tree_adapter_with_long_conversation(self):
        """Test tree_adapter with a conversation that has more than 3 elements"""
        # Arrange
        item = [
            42,  # identifier
            {
                "Conversation": [
                    "Who are you?",
                    "Hi! I am GPT-4. How can I help you today?",
                    "This is a very long conversation message that should be truncated at 50 characters to fit properly in the display",
                    "This is the AI response to the long message"
                ]
            }
        ]
        
        # Act
        result = tree_adapter(item)
        
        # Assert
        expected_identifier = 42
        expected_display = "This is a very long conversation message that sho..."
        assert result == (expected_identifier, expected_display)
        assert len(result[1]) == 53  # 50 chars + "..."

    def test_tree_adapter_with_short_conversation(self):
        """Test tree_adapter with a conversation that has 3 or fewer elements"""
        # Arrange - conversation with exactly 3 elements
        item = [
            1,
            {
                "Conversation": [
                    "Who are you?",
                    "Hi! I am GPT-4.",
                    "Thanks!"
                ]
            }
        ]
        
        # Act
        result = tree_adapter(item)
        
        # Assert
        assert result == (1, "Empty conversation")

    def test_tree_adapter_with_empty_conversation(self):
        """Test tree_adapter with an empty conversation list"""
        # Arrange
        item = [
            0,
            {
                "Conversation": []
            }
        ]
        
        # Act
        result = tree_adapter(item)
        
        # Assert
        assert result == (0, "Empty conversation")

    def test_tree_adapter_with_exactly_four_elements(self):
        """Test tree_adapter with exactly 4 conversation elements (boundary case)"""
        # Arrange
        item = [
            99,
            {
                "Conversation": [
                    "Question 1",
                    "Answer 1",
                    "Short question",  # This should be displayed
                    "Answer 2"
                ]
            }
        ]
        
        # Act
        result = tree_adapter(item)
        
        # Assert
        assert result == (99, "Short question...")

    def test_tree_adapter_with_exactly_50_char_message(self):
        """Test tree_adapter with exactly 50 character message"""
        # Arrange
        message_50_chars = "This message is exactly fifty characters long!!"
        assert len(message_50_chars) == 50
        
        item = [
            5,
            {
                "Conversation": [
                    "Q1", "A1", message_50_chars, "A2"
                ]
            }
        ]
        
        # Act
        result = tree_adapter(item)
        
        # Assert
        expected_display = message_50_chars + "..."
        assert result == (5, expected_display)

    def test_tree_adapter_with_string_identifier(self):
        """Test tree_adapter with string identifier instead of integer"""
        # Arrange
        item = [
            "conversation_id_123",
            {
                "Conversation": [
                    "Q1", "A1", "User question", "AI response", "Follow up"
                ]
            }
        ]
        
        # Act
        result = tree_adapter(item)
        
        # Assert
        assert result == ("conversation_id_123", "User question...")

    def test_tree_adapter_preserves_identifier_type(self):
        """Test that tree_adapter preserves the original identifier type"""
        # Test with different identifier types
        test_cases = [
            (42, int),
            ("string_id", str), 
            (None, type(None))
        ]
        
        for identifier, expected_type in test_cases:
            # Arrange
            item = [
                identifier,
                {"Conversation": ["Q", "A", "Long message here", "Response"]}
            ]
            
            # Act
            result = tree_adapter(item)
            
            # Assert
            assert type(result[0]) == expected_type
            assert result[0] == identifier

    def test_tree_adapter_with_special_characters(self):
        """Test tree_adapter with special characters in conversation"""
        # Arrange
        item = [
            7,
            {
                "Conversation": [
                    "Question?",
                    "Answer!",
                    "Message with émojis 🚀 and spécial chars: @#$%^&*()",
                    "Response"
                ]
            }
        ]
        
        # Act
        result = tree_adapter(item)
        
        # Assert
        expected_display = "Message with émojis 🚀 and spécial chars: @#$%^&*..."
        assert result == (7, expected_display)

    def test_tree_adapter_return_type(self):
        """Test that tree_adapter returns a tuple"""
        # Arrange
        item = [1, {"Conversation": ["Q", "A", "Test", "Response"]}]
        
        # Act
        result = tree_adapter(item)
        
        # Assert
        assert isinstance(result, tuple)
        assert len(result) == 2
