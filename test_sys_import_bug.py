import pytest
import os
import sys
import subprocess
import tempfile
import shutil


def test_missing_api_key_causes_sys_error_before_fix():
    """
    Test that demonstrates the bug: missing sys import causes NameError.
    
    This test creates a version of the file without the sys import,
    runs it, and shows it fails with NameError before the fix.
    """
    # Create a temporary version of the file without sys import to simulate the bug
    with open('file-v1-main.py', 'r') as f:
        content = f.read()
    
    # Create buggy version (remove sys import)
    buggy_content = content.replace('import sys\n', '')
    
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
        temp_file.write(buggy_content)
        temp_file_path = temp_file.name
    
    try:
        # Create environment without API key
        test_env = os.environ.copy()
        if 'OPENAI_API_KEY' in test_env:
            del test_env['OPENAI_API_KEY']
        
        # Run the buggy version
        result = subprocess.run(
            [sys.executable, temp_file_path],
            env=test_env,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Before fix: Should fail with NameError about 'sys'
        # This demonstrates the bug exists
        assert result.returncode != 1  # Not a clean exit
        assert "NameError" in result.stderr and "sys" in result.stderr
        
    finally:
        # Clean up
        os.unlink(temp_file_path)


def test_missing_api_key_exits_cleanly_after_fix():
    """
    Test that after the fix, missing API key causes clean exit.
    
    This test runs the fixed version and shows it exits cleanly.
    """
    # Create environment without API key
    test_env = os.environ.copy()
    if 'OPENAI_API_KEY' in test_env:
        del test_env['OPENAI_API_KEY']
    
    # Run the fixed version
    result = subprocess.run(
        [sys.executable, 'file-v1-main.py'],
        env=test_env,
        capture_output=True,
        text=True,
        timeout=10
    )
    
    # After fix: Should exit cleanly with code 1
    assert result.returncode == 1
    assert "Error: OPENAI_API_KEY environment variable not set" in result.stdout
    assert "NameError" not in result.stderr  # No NameError should occur


def test_sys_import_is_present():
    """
    Test that verifies sys is properly imported in the fixed file.
    """
    with open('file-v1-main.py', 'r') as f:
        content = f.read()
    
    # Verify that sys is imported
    assert 'import sys' in content, "sys module should be imported"
    
    # Verify the import comes before the usage
    import_pos = content.find('import sys')
    usage_pos = content.find('sys.exit(1)')
    
    assert import_pos != -1, "sys import should be found"
    assert usage_pos != -1, "sys.exit usage should be found" 
    assert import_pos < usage_pos, "sys import should come before sys.exit usage"
