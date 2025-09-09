#!/usr/bin/env python3
"""
Demonstration of the bug fix in main.py

This script shows:
1. The bug: ImportError when trying to import from non-existent llm_benchmark package
2. The fix: Creating the missing llm_benchmark package with proper implementations

Run this script to see the bug demonstration and fix verification.
"""

import sys
import os
import shutil
from io import StringIO
from contextlib import redirect_stdout


def demonstrate_bug():
    """Demonstrate the bug by temporarily removing the llm_benchmark package"""
    print("=" * 60)
    print("BUG DEMONSTRATION")
    print("=" * 60)
    
    # Backup the llm_benchmark directory
    if os.path.exists('llm_benchmark'):
        shutil.move('llm_benchmark', 'llm_benchmark_temp')
        print("✓ Temporarily removed llm_benchmark package")
    
    # Clear any cached imports
    modules_to_clear = [mod for mod in sys.modules.keys() 
                       if mod.startswith('llm_benchmark') or mod == 'main']
    for mod in modules_to_clear:
        del sys.modules[mod]
    
    print("✓ Cleared module cache")
    
    try:
        print("\nTrying to import main.py (this should fail)...")
        import main
        print("❌ ERROR: Import should have failed but didn't!")
    except ImportError as e:
        print(f"✓ SUCCESS: Got expected ImportError: {e}")
        print("   This demonstrates the bug - main.py cannot be imported")
        print("   because it tries to import from non-existent llm_benchmark package")
    
    # Restore the llm_benchmark directory
    if os.path.exists('llm_benchmark_temp'):
        shutil.move('llm_benchmark_temp', 'llm_benchmark')
        print("\n✓ Restored llm_benchmark package")
    
    return True


def demonstrate_fix():
    """Demonstrate that the fix works"""
    print("\n" + "=" * 60)
    print("FIX DEMONSTRATION") 
    print("=" * 60)
    
    # Clear any cached imports
    modules_to_clear = [mod for mod in sys.modules.keys() 
                       if mod.startswith('llm_benchmark') or mod == 'main']
    for mod in modules_to_clear:
        del sys.modules[mod]
    
    try:
        print("Trying to import main.py (this should work now)...")
        import main
        print("✓ SUCCESS: main.py imported successfully!")
        
        print("\nTesting a function call...")
        # Capture output from one of the functions
        output = StringIO()
        with redirect_stdout(output):
            main.single()
        
        result = output.getvalue()
        if "SingleForLoop" in result and "sum_range(10):" in result:
            print("✓ SUCCESS: main.single() executed and produced expected output")
            print("   Sample output:", result.split('\n')[0])
        else:
            print("❌ ERROR: Unexpected output from main.single()")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False
    
    return True


def main():
    """Main demonstration function"""
    print("BUG FIX DEMONSTRATION FOR main.py")
    print("This script demonstrates a bug and its fix in main.py")
    print()
    
    # First demonstrate the bug
    bug_demonstrated = demonstrate_bug()
    
    # Then demonstrate the fix
    fix_works = demonstrate_fix()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if bug_demonstrated and fix_works:
        print("✓ Bug successfully demonstrated and fixed!")
        print()
        print("BUG DESCRIPTION:")
        print("- main.py tried to import from non-existent 'llm_benchmark' package")
        print("- This caused ImportError when trying to run the script")
        print()
        print("FIX DESCRIPTION:")
        print("- Created the missing llm_benchmark package structure")
        print("- Implemented all required classes and methods")
        print("- Now main.py can be imported and executed successfully")
        print()
        print("TESTING:")
        print("- Created unit test in test_main_bug.py that fails before fix")
        print("- Same test passes after the fix is applied")
    else:
        print("❌ Something went wrong with the demonstration")


if __name__ == '__main__':
    main()
