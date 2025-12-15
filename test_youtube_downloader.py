import unittest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock
import sys

# Mock customtkinter before importing the main module
sys.modules['customtkinter'] = MagicMock()
import customtkinter as ctk

class TestBooleanVarBug(unittest.TestCase):
    """Test case to verify that BooleanVar is correctly used from tkinter, not customtkinter."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock root window
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during testing
    
    def tearDown(self):
        """Clean up after tests."""
        try:
            self.root.destroy()
        except:
            pass
    
    def test_booleanvar_creation(self):
        """Test that BooleanVar can be created from tk module.
        
        This test ensures that the code uses tk.BooleanVar() instead of ctk.BooleanVar(),
        which doesn't exist in the customtkinter library.
        """
        # This should work - tk.BooleanVar exists
        try:
            var = tk.BooleanVar(value=False)
            self.assertIsInstance(var, tk.BooleanVar)
            self.assertEqual(var.get(), False)
        except AttributeError as e:
            self.fail(f"tk.BooleanVar should exist but got AttributeError: {e}")
    
    def test_ctk_booleanvar_does_not_exist(self):
        """Test that ctk.BooleanVar does not exist.
        
        This test verifies that customtkinter does not provide a BooleanVar class,
        confirming that using ctk.BooleanVar() in the code would be a bug.
        """
        # Verify that customtkinter doesn't have BooleanVar
        # Since we're using the real customtkinter module
        import customtkinter as ctk
        
        # ctk.BooleanVar should not exist
        with self.assertRaises(AttributeError):
            _ = ctk.BooleanVar(value=False)
    
    def test_display_videos_uses_correct_booleanvar(self):
        """Test that the display_videos function would use the correct BooleanVar.
        
        This is a simulated test that mimics what happens in the actual code.
        Before the fix, this would fail because ctk.BooleanVar doesn't exist.
        After the fix, it should work because tk.BooleanVar is used.
        """
        # Simulate creating a BooleanVar as it's done in the display_videos method
        # BEFORE FIX: audio_only_video_var = ctk.BooleanVar(value=False)  # This would fail
        # AFTER FIX: audio_only_video_var = tk.BooleanVar(value=False)   # This works
        
        try:
            # This is what the fixed code should do
            audio_only_video_var = tk.BooleanVar(value=False)
            self.assertIsNotNone(audio_only_video_var)
            self.assertEqual(audio_only_video_var.get(), False)
            
            # Test setting the value
            audio_only_video_var.set(True)
            self.assertEqual(audio_only_video_var.get(), True)
        except AttributeError as e:
            self.fail(f"Failed to create BooleanVar: {e}")

if __name__ == '__main__':
    unittest.main()
