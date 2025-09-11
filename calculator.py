"""
Calculator Application

A simple Tkinter-based calculator application providing basic arithmetic operations
including number input, addition, and state management for continuous calculations.

Features:
- Main application window with Tkinter GUI
- Calculator class with proper state management
- Input validation for decimal numbers
- Error handling for GUI initialization
- Graceful window close handling

Usage:
    python calculator.py

Author: Generated Calculator Module
"""

import tkinter as tk
from tkinter import messagebox
import sys


class Calculator:
    """
    Main Calculator class handling GUI initialization, state management, 
    and calculator operations.
    
    Manages current input value, running total, and operation state for
    continuous calculations with proper input validation.
    """
    
    def __init__(self):
        """
        Initialize the Calculator application.
        
        Sets up the main window, initializes state management attributes,
        and prepares the calculator for operation.
        """
        try:
            # Initialize main window
            self.root = tk.Tk()
            self.root.title("Calculator")
            self.root.geometry("300x400")
            
            # State management attributes
            self.current_value = "0"
            self.total = 0.0
            self.operation_pending = False
            
            # Set up window close event handling
            self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
            
        except Exception as e:
            self._handle_initialization_error(e)
    
    def number_pressed(self, number):
        """
        Handle number button press events.
        
        Args:
            number (str): The number that was pressed (0-9 or decimal point)
        
        Validates input and updates the current value display accordingly.
        """
        # Method stub - to be implemented in next phase
        pass
    
    def add_pressed(self):
        """
        Handle addition operation button press.
        
        Processes the current value, updates the running total, and 
        prepares for the next number input.
        """
        # Method stub - to be implemented in next phase
        pass
    
    def clear_pressed(self):
        """
        Handle clear button press to reset calculator state.
        
        Resets current_value, total, and operation_pending to initial state.
        """
        # Method stub - to be implemented in next phase
        pass
    
    def equals_pressed(self):
        """
        Handle equals button press to complete pending operations.
        
        Calculates final result and displays it, resetting operation state.
        """
        # Method stub - to be implemented in next phase
        pass
    
    def run(self):
        """
        Start the calculator application main event loop.
        
        Begins the Tkinter mainloop to handle user interactions.
        """
        try:
            self.root.mainloop()
        except Exception as e:
            messagebox.showerror("Runtime Error", 
                               f"An error occurred while running the calculator:\n{str(e)}")
    
    def _on_closing(self):
        """
        Handle window close event gracefully.
        
        Provides clean exit from the application when window is closed.
        """
        try:
            self.root.destroy()
        except Exception as e:
            # Force exit if graceful close fails
            sys.exit(1)
    
    def _handle_initialization_error(self, error):
        """
        Handle GUI initialization errors with user-friendly messages.
        
        Args:
            error (Exception): The initialization error that occurred
        """
        error_message = f"Failed to initialize calculator GUI:\n{str(error)}"
        try:
            # Try to show error dialog if possible
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            messagebox.showerror("Initialization Error", error_message)
            root.destroy()
        except:
            # Fallback to console output if GUI is completely broken
            print(f"CRITICAL ERROR: {error_message}", file=sys.stderr)
        
        sys.exit(1)


if __name__ == "__main__":
    """
    Main execution block for direct script execution.
    
    Creates Calculator instance and starts the application with proper
    error handling for initialization failures.
    """
    try:
        calculator = Calculator()
        calculator.run()
    except KeyboardInterrupt:
        print("\nCalculator application interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error starting calculator: {str(e)}", file=sys.stderr)
        sys.exit(1)
