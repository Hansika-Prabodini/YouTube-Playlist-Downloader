import pytest
import sys
import io
from contextlib import redirect_stdout

def test_added_single_function_fails_without_import():
    """Test that added_single.py fails due to missing SingleForLoop import"""
    # This test demonstrates the bug before the fix
    try:
        from added_single import single
        # Capture stdout to avoid printing during test
        with redirect_stdout(io.StringIO()) as captured_output:
            single()
        # If we reach here, the bug is fixed and test should fail
        pytest.fail("Expected NameError due to missing SingleForLoop import, but function executed successfully")
    except NameError as e:
        # This is expected - the function should fail due to missing import
        assert "SingleForLoop" in str(e)
        assert "name 'SingleForLoop' is not defined" in str(e)

def test_added_single_function_works_after_fix():
    """Test that added_single.py works correctly after fixing the import"""
    # This test will pass after we fix the import
    # For now, we'll mock the functionality since we don't have the actual SingleForLoop module
    try:
        from added_single import single
        # Capture stdout to check the output
        with redirect_stdout(io.StringIO()) as captured_output:
            single()
        output = captured_output.getvalue()
        # If no exception is raised and we get output, the fix worked
        assert "SingleForLoop" in output
    except NameError:
        # If this still fails after our fix, something is wrong
        pytest.fail("SingleForLoop import should be fixed, but NameError still occurs")
