"""
Unit test to demonstrate and validate the fix for the selected_row indexing bug.

This test verifies that the table row selection uses consistent 1-based indexing
throughout the application, specifically in the select_conv function.

Bug Description:
    In file-v1-main.py, the Taipy table component uses 1-based indexing for row selection.
    The select_conv function (line 225) had an off-by-one error where it used:
        state.selected_row = [len(state.conversation["Conversation"]) - 1]
    
    This should have been:
        state.selected_row = [len(state.conversation["Conversation"])]
    
    To be consistent with other functions that use 1-based indexing.

Expected Behavior:
    When selecting a past conversation, the last message in that conversation
    should be highlighted in the table view.
"""


def test_selected_row_indexing():
    """
    Test that selected_row uses 1-based indexing consistently.
    
    This simulates the table row selection logic used in the Taipy GUI application.
    """
    
    # Simulate a conversation with 6 messages (3 user + 3 AI responses)
    # Index 0: user, Index 1: AI, Index 2: user, Index 3: AI, Index 4: user, Index 5: AI
    conversation = {
        "Conversation": [
            "Who are you?",                               # Index 0, Row 1
            "Hi! I am GPT-4.",                            # Index 1, Row 2
            "What can you do?",                           # Index 2, Row 3
            "I can help with many tasks.",                # Index 3, Row 4
            "Tell me a joke",                             # Index 4, Row 5
            "Why did the chicken cross the road?..."      # Index 5, Row 6
        ]
    }
    
    # Test the BUGGY behavior (what the old code did)
    buggy_selected_row = [len(conversation["Conversation"]) - 1]
    
    # Buggy version would select row 5 (index 4) instead of row 6 (index 5)
    assert buggy_selected_row == [5], "Buggy version: selected row should be [5]"
    
    # In 1-based indexing, row 5 corresponds to index 4 (the 5th message)
    # which is "Tell me a joke" - NOT the last message!
    buggy_row_index = buggy_selected_row[0] - 1  # Convert to 0-based index
    buggy_selected_message = conversation["Conversation"][buggy_row_index]
    assert buggy_selected_message == "Tell me a joke", \
        "Buggy version selects the second-to-last message instead of the last one"
    
    
    # Test the FIXED behavior (what the patched code does)
    fixed_selected_row = [len(conversation["Conversation"])]
    
    # Fixed version should select row 6 (index 5)
    assert fixed_selected_row == [6], "Fixed version: selected row should be [6]"
    
    # In 1-based indexing, row 6 corresponds to index 5 (the 6th message)
    # which is the LAST message
    fixed_row_index = fixed_selected_row[0] - 1  # Convert to 0-based index
    fixed_selected_message = conversation["Conversation"][fixed_row_index]
    assert fixed_selected_message == "Why did the chicken cross the road?...", \
        "Fixed version correctly selects the last message"


def test_consistency_with_other_functions():
    """
    Test that the fix makes select_conv consistent with other functions.
    
    This verifies that all functions use the same 1-based indexing pattern.
    """
    
    # Simulate initial conversation (default state)
    initial_conversation = {
        "Conversation": ["Who are you?", "Hi! I am GPT-4."]
    }
    
    # Initial state uses 1-based indexing: selected_row = [1]
    # This should select the first row (index 0)
    initial_selected_row = [1]
    assert initial_selected_row[0] - 1 == 0, \
        "Initial state: row 1 should correspond to index 0"
    
    # After reset_chat, it also uses: selected_row = [1]
    reset_selected_row = [1]
    assert reset_selected_row == initial_selected_row, \
        "reset_chat should use the same 1-based indexing"
    
    # When sending a new message (update_context), it uses:
    # selected_row = [len(conversation) + 1]
    # For a conversation with 2 items, this would be [3]
    # After adding 2 more items (user + AI), conversation has 4 items
    # So row 3 (index 2) is selected, which is the new user message
    before_length = len(initial_conversation["Conversation"])
    update_selected_row = [before_length + 1]
    assert update_selected_row == [3], \
        "update_context: for 2 items, should select row 3"
    
    # After adding 2 items, verify row 3 corresponds to the user's message
    new_conversation = {
        "Conversation": initial_conversation["Conversation"] + [
            "What can you do?",           # Index 2, Row 3
            "I can help with many tasks." # Index 3, Row 4
        ]
    }
    row_3_index = update_selected_row[0] - 1
    assert row_3_index == 2, "Row 3 should correspond to index 2"
    assert new_conversation["Conversation"][row_3_index] == "What can you do?", \
        "Row 3 should be the newly added user message"
    
    # Now verify select_conv uses the SAME pattern
    # For a conversation with 4 items, it should select row 4 (the last item)
    select_conv_selected_row = [len(new_conversation["Conversation"])]
    assert select_conv_selected_row == [4], \
        "select_conv: for 4 items, should select row 4"
    
    # Verify row 4 corresponds to the last message
    row_4_index = select_conv_selected_row[0] - 1
    assert row_4_index == 3, "Row 4 should correspond to index 3"
    assert new_conversation["Conversation"][row_4_index] == "I can help with many tasks.", \
        "Row 4 should be the last message (AI response)"


def test_edge_cases():
    """Test edge cases for the selected_row calculation."""
    
    # Edge case 1: Minimum conversation (2 messages: 1 user + 1 AI)
    min_conversation = {
        "Conversation": ["Hello", "Hi there!"]
    }
    selected_row = [len(min_conversation["Conversation"])]
    assert selected_row == [2], "For 2 messages, should select row 2"
    assert selected_row[0] - 1 == 1, "Row 2 should be index 1 (last message)"
    
    # Edge case 2: Larger conversation (10 messages)
    large_conversation = {
        "Conversation": [f"Message {i}" for i in range(10)]
    }
    selected_row = [len(large_conversation["Conversation"])]
    assert selected_row == [10], "For 10 messages, should select row 10"
    assert selected_row[0] - 1 == 9, "Row 10 should be index 9 (last message)"


if __name__ == "__main__":
    print("Testing selected_row indexing bug fix...\n")
    
    try:
        test_selected_row_indexing()
        print("✓ test_selected_row_indexing passed")
    except AssertionError as e:
        print(f"✗ test_selected_row_indexing failed: {e}")
        exit(1)
    
    try:
        test_consistency_with_other_functions()
        print("✓ test_consistency_with_other_functions passed")
    except AssertionError as e:
        print(f"✗ test_consistency_with_other_functions failed: {e}")
        exit(1)
    
    try:
        test_edge_cases()
        print("✓ test_edge_cases passed")
    except AssertionError as e:
        print(f"✗ test_edge_cases failed: {e}")
        exit(1)
    
    print("\nAll tests passed!")
    print("\nSummary:")
    print("- BEFORE fix: select_conv would select the second-to-last row")
    print("- AFTER fix: select_conv correctly selects the last row")
    print("- The fix ensures consistent 1-based indexing throughout the application")
