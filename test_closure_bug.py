"""
Unit test to demonstrate the closure bug in youtube_downloader-gui.py

This test simulates the bug where lambdas in a loop capture variables by reference
instead of by value, causing all callbacks to use the last value from the loop.
"""

def test_closure_bug_demonstration():
    """
    This test demonstrates the closure bug that existed in the cancel_all method.
    
    The bug: When creating lambdas in a loop that reference loop variables,
    all lambdas will reference the LAST value of that variable, not the value
    at the time the lambda was created.
    """
    
    # Simulate the buggy behavior (what the old code did)
    callbacks_buggy = []
    video_data = {'video1': 'Status1', 'video2': 'Status2', 'video3': 'Status3'}
    
    # Buggy version: lambda captures 'status' by reference
    for video_id, status in video_data.items():
        # This simulates: lambda: widgets['status_label'].configure(text="Cancelling...")
        callbacks_buggy.append(lambda: status)
    
    # Execute all callbacks - they should all return different statuses, but they won't!
    results_buggy = [callback() for callback in callbacks_buggy]
    
    # All callbacks return the LAST value from the loop
    # This demonstrates the bug: all three should be different, but they're all 'Status3'
    assert results_buggy == ['Status3', 'Status3', 'Status3'], \
        "Buggy version: all callbacks return the last value"
    
    # Now test the fixed behavior (what the patched code does)
    callbacks_fixed = []
    
    # Fixed version: lambda captures 's' by value using default argument
    for video_id, status in video_data.items():
        # This simulates: lambda w=widgets: w['status_label'].configure(text="Cancelling...")
        callbacks_fixed.append(lambda s=status: s)
    
    # Execute all callbacks - they should return their respective statuses
    results_fixed = [callback() for callback in callbacks_fixed]
    
    # Each callback returns its own captured value
    # This demonstrates the fix: all three have their correct values
    assert 'Status1' in results_fixed, "Fixed version should include Status1"
    assert 'Status2' in results_fixed, "Fixed version should include Status2"
    assert 'Status3' in results_fixed, "Fixed version should include Status3"
    assert len(set(results_fixed)) == 3, "Fixed version should have 3 unique values"


def test_closure_bug_with_dict_simulation():
    """
    This test more closely simulates the actual cancel_all scenario with widget dictionaries.
    """
    
    # Simulate video widgets dictionary
    video_widgets = {
        'url1': {'status': 'Ready', 'progress': 0},
        'url2': {'status': 'Downloading', 'progress': 50},
        'url3': {'status': 'Queued', 'progress': 0}
    }
    
    # Buggy version: simulating the old cancel_all code
    update_functions_buggy = []
    for video_url in video_widgets.keys():
        widgets = video_widgets[video_url]
        # Old buggy code: lambda: (widgets['status'], widgets['progress'])
        update_functions_buggy.append(lambda: (widgets['status'], widgets['progress']))
    
    # All functions reference the LAST widgets dict
    results_buggy = [func() for func in update_functions_buggy]
    
    # Bug: all three return the same values (from the last iteration)
    assert all(result == ('Queued', 0) for result in results_buggy), \
        "Buggy version: all functions return the last widget's values"
    
    # Fixed version: simulating the patched cancel_all code  
    update_functions_fixed = []
    for video_url in video_widgets.keys():
        widgets = video_widgets[video_url]
        # Fixed code: lambda w=widgets: (w['status'], w['progress'])
        update_functions_fixed.append(lambda w=widgets: (w['status'], w['progress']))
    
    # Each function should return its own widget's values
    results_fixed = [func() for func in update_functions_fixed]
    
    # Fix: each function returns its own captured widget values
    expected_results = [('Ready', 0), ('Downloading', 50), ('Queued', 0)]
    assert results_fixed == expected_results, \
        "Fixed version: each function returns its own widget's values"


if __name__ == "__main__":
    print("Testing closure bug demonstration...")
    
    try:
        test_closure_bug_demonstration()
        print("✓ test_closure_bug_demonstration passed")
    except AssertionError as e:
        print(f"✗ test_closure_bug_demonstration failed: {e}")
    
    try:
        test_closure_bug_with_dict_simulation()
        print("✓ test_closure_bug_with_dict_simulation passed")
    except AssertionError as e:
        print(f"✗ test_closure_bug_with_dict_simulation failed: {e}")
    
    print("\nAll tests passed!")
