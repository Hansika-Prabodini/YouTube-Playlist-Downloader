import re

def test_file_selection():
    # Simulate user selecting files and applying regex
    selected_files = ["src/python/example.py", "src/java/Example.java"]
    regex_pattern = r".*\.py$"
    # Use re.search to find files matching the pattern anywhere in the string
    included_files = [f for f in selected_files if re.search(regex_pattern, f)]
    assert "src/python/example.py" in included_files
    assert "src/java/Example.java" not in included_files