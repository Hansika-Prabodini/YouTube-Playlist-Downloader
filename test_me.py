#!/usr/bin/env python3
"""
Interactive Test Runner for YouTube Downloader

This script provides an easy-to-use interface for running the test suite
without needing to remember pytest commands. It offers various test execution
options through a simple menu system.

Usage:
    python test_me.py
    
Requirements:
    - pytest
    - pytest-cov (optional, for coverage reports)
    - pytest-benchmark (optional, for benchmark tests)
"""

import sys
import subprocess
import os


def print_header():
    """Print the application header."""
    print("\n" + "="*70)
    print("  YouTube Downloader - Interactive Test Runner")
    print("="*70 + "\n")


def print_menu():
    """Print the main menu options."""
    print("Select a testing option:\n")
    print("  1. Run ALL tests (unit + functional)")
    print("  2. Run UNIT tests only")
    print("  3. Run FUNCTIONAL tests only")
    print("  4. Run tests with COVERAGE report")
    print("  5. Run tests with VERBOSE output")
    print("  6. Run SPECIFIC test by name")
    print("  7. Run tests matching KEYWORD")
    print("  8. Show available tests (collect only)")
    print("  9. Run last FAILED tests")
    print("  0. Exit")
    print()


def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")
    
    required = {
        'pytest': 'pytest',
    }
    
    optional = {
        'pytest-cov': 'pytest_cov',
        'pytest-benchmark': 'pytest_benchmark',
    }
    
    missing_required = []
    missing_optional = []
    
    for name, module in required.items():
        try:
            __import__(module)
            print(f"  ✓ {name} is installed")
        except ImportError:
            missing_required.append(name)
            print(f"  ✗ {name} is NOT installed")
    
    for name, module in optional.items():
        try:
            __import__(module)
            print(f"  ✓ {name} is installed (optional)")
        except ImportError:
            missing_optional.append(name)
            print(f"  ○ {name} is NOT installed (optional)")
    
    if missing_required:
        print(f"\n⚠ Missing required dependencies: {', '.join(missing_required)}")
        print("Install with: pip install pytest")
        return False
    
    if missing_optional:
        print(f"\nℹ Missing optional dependencies: {', '.join(missing_optional)}")
        print("Install with: pip install pytest-cov pytest-benchmark")
    
    print()
    return True


def run_command(cmd_args):
    """Execute a pytest command and display results."""
    cmd = ['pytest'] + cmd_args
    print(f"\nExecuting: {' '.join(cmd)}")
    print("-" * 70 + "\n")
    
    try:
        result = subprocess.run(cmd, cwd=os.getcwd())
        return result.returncode
    except KeyboardInterrupt:
        print("\n\nTest execution interrupted by user.")
        return 1
    except Exception as e:
        print(f"\n⚠ Error executing tests: {e}")
        return 1


def main():
    """Main function to run the interactive test menu."""
    print_header()
    
    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)
    
    while True:
        print_menu()
        choice = input("Enter your choice (0-9): ").strip()
        
        if choice == '0':
            print("\nExiting test runner. Goodbye!\n")
            sys.exit(0)
        
        elif choice == '1':
            # Run all tests
            run_command(['-v'])
        
        elif choice == '2':
            # Run unit tests only
            run_command(['test_unit.py', '-v'])
        
        elif choice == '3':
            # Run functional tests only
            run_command(['test_functional.py', '-v'])
        
        elif choice == '4':
            # Run with coverage
            print("\nGenerating coverage report...")
            returncode = run_command(['--cov=youtube_downloader-gui', '--cov-report=term-missing', '-v'])
            if returncode == 0:
                print("\n✓ Coverage report generated above.")
                print("For HTML report, run: pytest --cov=youtube_downloader-gui --cov-report=html")
        
        elif choice == '5':
            # Run with verbose output
            run_command(['-vv', '-s'])
        
        elif choice == '6':
            # Run specific test
            test_name = input("\nEnter test name (e.g., test_progress_regex_with_valid_percentage): ").strip()
            if test_name:
                # Search in both test files
                run_command(['-k', test_name, '-v'])
            else:
                print("No test name provided.")
        
        elif choice == '7':
            # Run tests matching keyword
            keyword = input("\nEnter keyword to match (e.g., 'progress'): ").strip()
            if keyword:
                run_command(['-k', keyword, '-v'])
            else:
                print("No keyword provided.")
        
        elif choice == '8':
            # Show available tests
            run_command(['--collect-only', '-q'])
        
        elif choice == '9':
            # Run last failed tests
            run_command(['--lf', '-v'])
        
        else:
            print("\n⚠ Invalid choice. Please select a number from 0 to 9.\n")
            continue
        
        # Pause before showing menu again
        input("\nPress Enter to continue...")
        print("\n" * 2)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest runner interrupted. Goodbye!\n")
        sys.exit(0)
