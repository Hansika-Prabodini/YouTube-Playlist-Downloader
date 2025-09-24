def test_lambda_closure_bug_example():
    """
    Demonstrates the lambda closure bug that was fixed in youtube_downloader-gui.py
    
    The bug occurs when lambdas are created in a loop and they capture variables
    by reference. All lambdas end up using the last value of the loop variable.
    """
    
    # This demonstrates the bug (incorrect behavior)
    functions_with_bug = []
    for i in range(3):
        value = f"item_{i}"
        # BUG: This lambda captures 'value' by reference, not by value
        # All lambdas will use the last value of 'value' (which is "item_2")
        functions_with_bug.append(lambda: f"Processing {value}")
    
    # This demonstrates the fix (correct behavior)
    functions_fixed = []
    for i in range(3):
        value = f"item_{i}"
        # FIX: This lambda captures 'value' by value using default parameter
        # Each lambda gets its own copy of the value
        functions_fixed.append(lambda v=value: f"Processing {v}")
    
    # Test the bug - all functions return the same (last) value
    bug_results = [func() for func in functions_with_bug]
    assert bug_results == ["Processing item_2", "Processing item_2", "Processing item_2"]
    
    # Test the fix - each function returns its own value  
    fixed_results = [func() for func in functions_fixed]
    assert fixed_results == ["Processing item_0", "Processing item_1", "Processing item_2"]
    
    print("Lambda closure bug test passed!")

if __name__ == "__main__":
    test_lambda_closure_bug_example()
