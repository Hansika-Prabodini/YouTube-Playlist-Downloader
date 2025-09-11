import unittest
from unittest.mock import patch, MagicMock
import os
import sys


class TestSysImportBug(unittest.TestCase):
    """Test for the sys import bug in file-v1-main.py"""
    
    def test_buggy_code_without_sys_import_raises_nameerror(self):
        """
        Test that demonstrates the original bug: calling sys.exit() without importing sys.
        This test shows what would happen BEFORE the fix.
        """
        # Simulate the original buggy code (without sys import)
        buggy_code = '''
import os
from unittest.mock import MagicMock

# Simulate missing environment variable scenario
if not os.getenv("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY environment variable not set.")
    sys.exit(1)  # BUG: sys is not imported!
'''
        
        # Clear OPENAI_API_KEY to trigger the problematic code path
        with patch.dict(os.environ, {}, clear=True):
            # Mock print to avoid output during test
            with patch('builtins.print'):
                # Create execution globals without sys
                exec_globals = {
                    'os': os,
                    'MagicMock': MagicMock
                }
                
                # This should raise NameError: name 'sys' is not defined
                with self.assertRaises(NameError) as context:
                    exec(buggy_code, exec_globals)
                
                # Verify the error is specifically about 'sys' not being defined
                self.assertIn("'sys' is not defined", str(context.exception))

    def test_fixed_code_with_sys_import_works_correctly(self):
        """
        Test that demonstrates the fix: importing sys allows sys.exit() to work.
        This test shows what happens AFTER the fix.
        """
        # Simulate the fixed code (with sys import)
        fixed_code = '''
import os
import sys  # FIX: sys is now imported
from unittest.mock import MagicMock

# Simulate missing environment variable scenario  
if not os.getenv("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY environment variable not set.")
    sys.exit(1)  # This now works because sys is imported
'''
        
        # Clear OPENAI_API_KEY to trigger the code path
        with patch.dict(os.environ, {}, clear=True):
            # Mock print to avoid output during test
            with patch('builtins.print'):
                # Mock sys.exit to capture the call instead of actually exiting
                with patch('sys.exit') as mock_exit:
                    # Create execution globals with sys
                    exec_globals = {
                        'os': os,
                        'sys': sys,
                        'MagicMock': MagicMock
                    }
                    
                    # Execute the fixed code - should not raise NameError
                    try:
                        exec(fixed_code, exec_globals)
                    except NameError as e:
                        if "'sys' is not defined" in str(e):
                            self.fail("Fixed code still has NameError - sys import didn't work")
                        else:
                            # Re-raise if it's a different NameError
                            raise
                    
                    # Verify sys.exit(1) was called correctly
                    mock_exit.assert_called_once_with(1)

    def test_file_v1_main_actual_code_after_fix(self):
        """
        Test that the actual fixed file-v1-main.py imports sys correctly.
        This ensures our fix actually works in the real file.
        """
        # Read the fixed file content
        with open('file-v1-main.py', 'r') as f:
            file_content = f.read()
        
        # Verify sys is imported
        self.assertIn('import sys', file_content)
        
        # Verify sys.exit(1) is still in the code
        self.assertIn('sys.exit(1)', file_content)
        
        # Test that the fixed file can be parsed without syntax errors
        try:
            compile(file_content, 'file-v1-main.py', 'exec')
        except SyntaxError as e:
            self.fail(f"Fixed file has syntax errors: {e}")


if __name__ == '__main__':
    unittest.main()
