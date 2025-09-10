import unittest
import sys
import os
import shutil
from unittest.mock import patch
from io import StringIO


class TestMainImports(unittest.TestCase):
    """Test that demonstrates the import bug in main.py"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        # Create a backup of the current llm_benchmark if it exists
        cls.backup_exists = os.path.exists('llm_benchmark')
        if cls.backup_exists:
            if os.path.exists('llm_benchmark_backup'):
                shutil.rmtree('llm_benchmark_backup')
            shutil.move('llm_benchmark', 'llm_benchmark_backup')
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        # Restore the backup if it existed
        if cls.backup_exists and os.path.exists('llm_benchmark_backup'):
            if os.path.exists('llm_benchmark'):
                shutil.rmtree('llm_benchmark')
            shutil.move('llm_benchmark_backup', 'llm_benchmark')
    
    def test_main_imports_without_llm_benchmark_package(self):
        """Test that demonstrates the import bug - this will fail without the package"""
        # Remove llm_benchmark temporarily to test the bug
        if os.path.exists('llm_benchmark'):
            shutil.move('llm_benchmark', 'llm_benchmark_temp')
        
        try:
            # Clear any cached imports
            if 'main' in sys.modules:
                del sys.modules['main']
            
            # This should fail because llm_benchmark doesn't exist
            with self.assertRaises(ImportError):
                import main
        finally:
            # Restore llm_benchmark 
            if os.path.exists('llm_benchmark_temp'):
                shutil.move('llm_benchmark_temp', 'llm_benchmark')
    
    def test_main_imports_successfully_with_fix(self):
        """This test should pass after the fix when llm_benchmark package exists"""
        try:
            # Clear any cached imports to ensure fresh import
            modules_to_clear = [mod for mod in sys.modules.keys() if mod.startswith('llm_benchmark') or mod == 'main']
            for mod in modules_to_clear:
                del sys.modules[mod]
            
            # This should succeed with the fix
            import main
            
            # Test that we can call some functions without error
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                main.single()  # Test just one function to avoid too much output
            
            output = mock_stdout.getvalue()
            self.assertIn("SingleForLoop", output)
            self.assertIn("sum_range(10):", output)
            
        except ImportError as e:
            self.fail(f"ImportError occurred: {e}")
        except Exception as e:
            self.fail(f"Unexpected error: {e}")

    def test_individual_functions_exist(self):
        """Test that main.py has all expected functions"""
        # Clear cached imports
        if 'main' in sys.modules:
            del sys.modules['main']
        
        import main
        self.assertTrue(hasattr(main, 'single'))
        self.assertTrue(hasattr(main, 'double'))
        self.assertTrue(hasattr(main, 'sql'))
        self.assertTrue(hasattr(main, 'primes'))
        self.assertTrue(hasattr(main, 'sort'))
        self.assertTrue(hasattr(main, 'dslist'))
        self.assertTrue(hasattr(main, 'strops'))
        self.assertTrue(hasattr(main, 'main'))


if __name__ == '__main__':
    unittest.main()
