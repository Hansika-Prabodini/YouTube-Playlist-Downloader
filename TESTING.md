# Testing Documentation

## Table of Contents

1. [Overview](#overview)
2. [Installation & Setup](#installation--setup)
3. [Running Tests](#running-tests)
4. [Test File Structure](#test-file-structure)
5. [Writing New Tests](#writing-new-tests)
6. [Troubleshooting](#troubleshooting)

---

## Overview

### Testing Philosophy

This test suite is designed to comprehensively test the YouTube Downloader GUI application **without refactoring the existing codebase**. The application follows a monolithic structure with all functionality contained in a single `YouTubeDownloaderApp` class, and the tests are written to work with this architecture as-is.

### Three-Tier Testing Approach

The test suite is organized into three distinct test types, each serving a specific purpose:

#### 1. **Unit Tests** (`test_unit.py`)
- **Purpose**: Test individual methods and logic components in isolation
- **Approach**: Uses extensive mocking to avoid GUI instantiation and subprocess calls
- **Coverage**: Regex patterns, state management, clipboard operations, path selection, playlist parsing, and download success determination
- **Key Benefits**: Fast execution, precise isolation of units, easy debugging

#### 2. **Benchmark Tests** (`test_benchmark.py`)
- **Purpose**: Measure and track performance metrics across different operations
- **Approach**: Uses pytest-benchmark to record execution times and memory usage
- **Coverage**: Playlist loading, video display rendering, state management operations, widget creation
- **Key Benefits**: Performance regression detection, optimization guidance, baseline establishment

#### 3. **Functional/Integration Tests** (`test_functional.py`)
- **Purpose**: Test complete user workflows and GUI interactions end-to-end
- **Approach**: Tests actual GUI components with minimal mocking, simulates user actions
- **Coverage**: Full download workflows, GUI state transitions, error handling, cancellation flows
- **Key Benefits**: Validates real-world usage scenarios, catches integration issues

### No-Refactoring Philosophy

**Why this matters**: The existing application is a working, monolithic GUI application. Rather than refactoring the code to make it more "testable" (which could introduce bugs), these tests are designed to:

- Work with the existing class structure
- Mock only external dependencies (tkinter widgets, subprocess calls)
- Test the actual code paths that execute in production
- Provide confidence when making future changes

This approach means:
- Tests may require more elaborate mocking setups
- Some tests validate implementation details (like line numbers in comments)
- The test structure mirrors the monolithic nature of the code
- Future refactoring can be done safely with these tests as a safety net

---

## Installation & Setup

### Python Version Requirements

- **Recommended**: Python 3.14 (as specified in project README)
- **Minimum**: Python 3.8+ (for pytest and customtkinter compatibility)

### Required Dependencies

Install all testing dependencies using pip:

```bash
# Core testing framework
pip install pytest

# Benchmark testing support
pip install pytest-benchmark

# Code coverage reporting
pip install pytest-cov

# Application dependencies (required for imports)
pip install customtkinter
pip install yt-dlp
```

### Complete Installation Command

```bash
pip install pytest pytest-benchmark pytest-cov customtkinter yt-dlp
```

### Requirements File

Alternatively, create a `requirements-test.txt` file:

```text
# Application dependencies
customtkinter>=5.0.0
yt-dlp>=2023.0.0

# Testing dependencies
pytest>=7.0.0
pytest-benchmark>=4.0.0
pytest-cov>=4.0.0
```

Then install with:

```bash
pip install -r requirements-test.txt
```

### Verify Installation

```bash
# Check pytest is installed
pytest --version

# Check pytest-benchmark is available
pytest --benchmark-help

# Verify all imports work
python -c "import pytest, customtkinter, subprocess; print('All dependencies available')"
```

---

## Running Tests

### Running All Tests

Execute the entire test suite:

```bash
pytest
```

With verbose output:

```bash
pytest -v
```

### Running Individual Test Files

#### Unit Tests Only

```bash
pytest test_unit.py -v
```

#### Benchmark Tests Only

```bash
pytest test_benchmark.py -v
```

#### Functional Tests Only

```bash
pytest test_functional.py -v
```

### Running Specific Test Functions

Run a single test by name:

```bash
pytest test_unit.py::test_progress_regex_with_valid_percentage -v
```

Run tests matching a pattern:

```bash
pytest -k "progress_regex" -v
```

Run tests by marker (if markers are defined):

```bash
pytest -m "slow" -v
```

### Running Benchmarks

#### Run Only Benchmark Tests

```bash
pytest test_benchmark.py --benchmark-only
```

#### Skip Benchmarks (Run Regular Tests Only)

```bash
pytest --benchmark-skip
```

#### Save Benchmark Results

```bash
pytest test_benchmark.py --benchmark-save=baseline
```

#### Compare Against Saved Baseline

```bash
pytest test_benchmark.py --benchmark-compare=baseline
```

#### Benchmark with Statistics

```bash
pytest test_benchmark.py --benchmark-only --benchmark-verbose
```

### Code Coverage

#### Generate Coverage Report

```bash
pytest --cov=youtube_downloader-gui --cov-report=html
```

#### View Coverage in Terminal

```bash
pytest --cov=youtube_downloader-gui --cov-report=term-missing
```

#### Coverage for Specific Test File

```bash
pytest test_unit.py --cov=youtube_downloader-gui --cov-report=term
```

### Useful pytest Flags

| Flag | Description |
|------|-------------|
| `-v` | Verbose output (show individual test names) |
| `-s` | Show print statements and output |
| `-x` | Stop at first failure |
| `--lf` | Run last failed tests only |
| `--ff` | Run failed tests first, then the rest |
| `-k EXPRESSION` | Run tests matching the given expression |
| `--maxfail=N` | Stop after N failures |
| `--tb=short` | Shorter traceback format |
| `-q` | Quiet output (minimal) |
| `--collect-only` | Show which tests would be run without executing them |

### Example Command Combinations

```bash
# Run all unit tests with coverage and stop on first failure
pytest test_unit.py --cov=youtube_downloader-gui --cov-report=term -x -v

# Run only failed tests from last run, with verbose output
pytest --lf -v

# Run benchmarks and save results, showing full output
pytest test_benchmark.py --benchmark-only --benchmark-save=current -s

# Run all tests except benchmarks, with coverage report
pytest --benchmark-skip --cov=youtube_downloader-gui --cov-report=html -v

# Run specific test category with detailed output
pytest -k "clipboard" -v -s
```

---

## Test File Structure

### `test_unit.py` - Unit Tests

**Lines of Code**: 804 lines

**Purpose**: Tests individual methods and logic units in complete isolation using mocks.

#### Test Categories Covered

1. **Progress Regex Parsing Tests** (Lines 119-186)
   - Validates the regex pattern used to extract download percentages from yt-dlp output
   - Tests valid formats: `[download] 25.5% of 10.50MiB at 1.20MiB/s ETA 00:06`
   - Tests edge cases: 0%, 100%, decimals, invalid formats
   - **Key Tests**: `test_progress_regex_with_valid_percentage`, `test_progress_regex_edge_case_integer_percentage`

2. **Download Success Determination Tests** (Lines 189-294)
   - Tests logic for determining if a download completed successfully
   - Validates return code checking (line 345-346 in main code)
   - Tests success pattern matching (lines 348-354 in main code)
   - Success patterns: `[download] 100%`, `[ExtractAudio]`, `[ffmpeg]`, `[Merger]`
   - **Key Tests**: `test_download_success_with_returncode_zero`, `test_download_failure_detection`

3. **Button State Management Tests** (Lines 296-386)
   - Tests `_check_global_buttons_state` method (lines 429-439 in main code)
   - Validates Download All / Cancel All button state logic
   - Tests scenarios: no downloads, active downloads, after cancellation
   - **Key Tests**: `test_check_global_buttons_state_with_active_downloads`, `test_check_global_buttons_state_after_cancelling`

4. **Clipboard Paste Functionality Tests** (Lines 388-455)
   - Tests `paste_from_clipboard` method (lines 131-139 in main code)
   - Validates clipboard content retrieval and error handling
   - Tests edge cases: empty clipboard, non-text content, multiline text
   - **Key Tests**: `test_paste_from_clipboard_with_valid_url`, `test_paste_from_clipboard_with_empty_clipboard`

5. **Download Path Selection Tests** (Lines 457-519)
   - Tests `select_download_path` method (lines 107-112 in main code)
   - Validates file dialog interactions
   - Tests scenarios: valid path, cancelled dialog, special characters
   - **Key Tests**: `test_select_download_path_with_valid_path`, `test_select_download_path_with_cancelled_dialog`

6. **Video List Display Tests** (Lines 521-640)
   - Tests `display_videos` method (lines 198-266 in main code)
   - Validates UI rendering for different playlist sizes
   - Tests widget creation and video_widgets dictionary population
   - **Key Tests**: `test_display_videos_with_large_playlist`, `test_display_videos_widget_structure`

7. **URL Validation and Playlist Fetching Tests** (Lines 642-756)
   - Tests `fetch_playlist_titles` method (lines 162-196 in main code)
   - Validates yt-dlp subprocess calls and JSON parsing
   - Tests error handling for invalid JSON and subprocess failures
   - **Key Tests**: `test_fetch_playlist_titles_with_valid_url`, `test_fetch_playlist_titles_with_invalid_json`

#### Mocking Approach

The `mock_app` fixture (lines 28-63) provides a fully mocked app instance:
- Mocks CTk initialization to prevent GUI window creation
- Mocks all widget attributes (url_entry, buttons, labels, etc.)
- Initializes essential instance variables (download_processes, video_widgets)
- Allows testing of methods without tkinter mainloop

#### Fixtures Available

- `mock_app`: Mocked YouTubeDownloaderApp instance
- `sample_video_data`: Sample playlist data (empty, single, multiple, large)
- `mock_subprocess_output`: Sample yt-dlp output strings for testing

### `test_benchmark.py` - Benchmark Tests

**Purpose**: Measures performance of key operations to detect regressions and establish baselines.

#### Benchmark Categories

1. **Playlist Loading Performance**
   - Measures time to parse JSON output from yt-dlp
   - Tests different playlist sizes: 10, 50, 100 videos
   - Baseline expectation: <100ms for 50 videos

2. **Video Display Rendering**
   - Measures widget creation time for different playlist sizes
   - Tests UI responsiveness with large playlists
   - Baseline expectation: <500ms for 50 videos

3. **State Management Operations**
   - Measures button state checking performance
   - Tests with varying numbers of active downloads
   - Baseline expectation: <10ms per operation

4. **Widget Creation Performance**
   - Measures time to create individual video row widgets
   - Tests memory allocation patterns
   - Baseline expectation: <20ms per video row

#### Using Benchmark Results

```bash
# Run and save baseline
pytest test_benchmark.py --benchmark-only --benchmark-save=v1.0

# After code changes, compare
pytest test_benchmark.py --benchmark-only --benchmark-compare=v1.0

# Generate histogram (requires pygal)
pytest test_benchmark.py --benchmark-only --benchmark-histogram
```

### `test_functional.py` - Functional Tests

**Purpose**: Tests complete user workflows and GUI interactions end-to-end.

#### Test Workflows

1. **Complete Download Workflow**
   - Load playlist → Select videos → Download → Verify completion
   - Tests actual subprocess execution (with mocked yt-dlp)
   - Validates progress updates and state transitions

2. **Cancel Operations**
   - Tests cancelling individual downloads
   - Tests "Cancel All" functionality
   - Validates process termination and cleanup

3. **Error Handling Flows**
   - Tests invalid URL handling
   - Tests network error scenarios
   - Tests disk full / permission denied scenarios

4. **GUI State Transitions**
   - Tests button enable/disable logic through complete workflows
   - Tests status label updates
   - Tests progress bar animations

#### Mocking Strategy for Functional Tests

- Minimal mocking: Only external dependencies (subprocess, file dialogs)
- Actual GUI components are created (requires DISPLAY environment variable)
- Tests run in Tk mainloop with threading support

---

## Writing New Tests

### Adding Unit Tests

#### Template for Method Testing

```python
def test_new_method_with_valid_input(mock_app):
    """
    Tests new_method with valid input parameters.
    
    Validates that [specific behavior] occurs when [specific condition].
    References lines X-Y in main code.
    """
    # Arrange: Set up test data and mocks
    mock_app.some_widget.configure = MagicMock()
    test_input = "test_value"
    
    # Act: Call the method under test
    result = mock_app.new_method(test_input)
    
    # Assert: Verify expected behavior
    assert result == expected_value
    mock_app.some_widget.configure.assert_called_once_with(expected_param="value")
```

#### Example: Testing a New Validation Method

```python
def test_validate_url_with_valid_youtube_url(mock_app):
    """
    Tests validate_url with a valid YouTube URL.
    
    Validates that URLs matching YouTube patterns are accepted.
    """
    valid_urls = [
        'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'https://youtube.com/playlist?list=PLtest123',
        'https://youtu.be/dQw4w9WgXcQ'
    ]
    
    for url in valid_urls:
        result = mock_app.validate_url(url)
        assert result is True, f"Should validate: {url}"

def test_validate_url_with_invalid_url(mock_app):
    """
    Tests validate_url with invalid URLs.
    
    Validates that non-YouTube URLs are rejected.
    """
    invalid_urls = [
        'https://vimeo.com/123456',
        'not_a_url',
        '',
        'ftp://youtube.com/video'
    ]
    
    for url in invalid_urls:
        result = mock_app.validate_url(url)
        assert result is False, f"Should reject: {url}"
```

#### Parametrized Testing Example

```python
import pytest

@pytest.mark.parametrize("input_value,expected_output", [
    ("value1", "output1"),
    ("value2", "output2"),
    ("edge_case", "special_output"),
])
def test_method_with_various_inputs(mock_app, input_value, expected_output):
    """Tests method with multiple input/output pairs."""
    result = mock_app.some_method(input_value)
    assert result == expected_output
```

### Adding Benchmark Tests

#### Template for Benchmark Test

```python
def test_benchmark_operation_name(benchmark, mock_app):
    """
    Benchmarks [operation name] performance.
    
    Measures execution time for [specific scenario].
    Baseline expectation: <Xms
    """
    # Setup
    test_data = prepare_test_data()
    
    # Benchmark the operation
    result = benchmark(mock_app.operation_name, test_data)
    
    # Optional: Verify correctness
    assert result is not None
```

#### Example: Benchmarking Playlist Parsing

```python
def test_benchmark_parse_playlist_json(benchmark):
    """
    Benchmarks JSON parsing performance for playlist data.
    
    Measures time to parse 50 video JSON objects.
    Baseline expectation: <50ms
    """
    import json
    
    # Generate test data
    test_json_lines = [
        json.dumps({"title": f"Video {i}", "url": f"https://youtube.com/watch?v=vid{i}"})
        for i in range(50)
    ]
    
    def parse_json_lines():
        results = []
        for line in test_json_lines:
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError:
                pass
        return results
    
    # Run benchmark
    result = benchmark(parse_json_lines)
    
    # Verify
    assert len(result) == 50
```

### Adding Functional Tests

#### Template for Workflow Test

```python
def test_complete_workflow_name(functional_app):
    """
    Tests complete [workflow name] from start to finish.
    
    Validates that [expected outcome] occurs when user [performs actions].
    """
    # Setup
    with patch('youtube_downloader_gui.subprocess.Popen') as mock_popen:
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        # Simulate user actions
        functional_app.url_entry.insert(0, "https://youtube.com/playlist?list=test")
        functional_app.load_button.invoke()
        
        # Wait for async operations
        functional_app.update()
        functional_app.after(100)
        
        # Verify state changes
        assert functional_app.download_all_button['state'] == tk.NORMAL
        assert len(functional_app.video_widgets) > 0
```

#### Example: Testing Download and Cancel Flow

```python
def test_download_and_cancel_workflow(functional_app):
    """
    Tests starting a download and then cancelling it.
    
    Validates that cancel properly terminates subprocess and updates UI.
    """
    with patch('youtube_downloader_gui.subprocess.Popen') as mock_popen:
        # Setup mock subprocess
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Process running
        mock_popen.return_value = mock_process
        
        # Load playlist
        functional_app.video_info_list = [
            {'title': 'Test Video', 'url': 'https://youtube.com/watch?v=test'}
        ]
        functional_app.display_videos()
        functional_app.update()
        
        # Start download
        video_url = 'https://youtube.com/watch?v=test'
        functional_app.start_single_download(video_url)
        functional_app.update()
        
        # Verify download started
        assert video_url in functional_app.download_processes
        
        # Cancel download
        functional_app.cancel_single_download(video_url)
        functional_app.update()
        
        # Verify cancellation
        mock_process.terminate.assert_called_once()
        assert video_url not in functional_app.download_processes
```

### Mocking Guidelines

#### When to Mock

1. **Always Mock**:
   - Subprocess calls (`subprocess.Popen`)
   - File system operations (`filedialog.askdirectory`)
   - Clipboard operations (may fail in headless environments)
   - Network operations (implied in yt-dlp calls)

2. **Sometimes Mock**:
   - Widget creation (unit tests: yes, functional tests: no)
   - Time-based operations (`after` calls)
   - Threading operations (for unit tests)

3. **Never Mock** (in unit tests testing these specific things):
   - Pure Python logic (regex, string operations)
   - Data structure operations (dict, list manipulations)
   - Mathematical calculations

#### Subprocess Mocking Pattern

```python
from unittest.mock import MagicMock, patch

def test_operation_with_subprocess(mock_app):
    """Tests operation that spawns subprocess."""
    
    # Create mock process
    mock_process = MagicMock()
    mock_process.stdout.readline.side_effect = [
        '[download]  50.0% of 10.50MiB\n',
        '[download] 100.0% of 10.50MiB\n',
        ''  # End of output
    ]
    mock_process.wait.return_value = 0
    mock_process.poll.return_value = 0
    
    # Patch subprocess.Popen
    with patch('youtube_downloader_gui.subprocess.Popen', return_value=mock_process):
        result = mock_app.some_download_operation()
    
    # Verify subprocess was called correctly
    assert mock_process.wait.called
```

#### Tkinter Widget Mocking Pattern

```python
from unittest.mock import MagicMock

def test_widget_interaction(mock_app):
    """Tests interaction with tkinter widgets."""
    
    # Widget already mocked in fixture, just configure behavior
    mock_app.some_button.cget = MagicMock(return_value=tk.NORMAL)
    mock_app.some_entry.get = MagicMock(return_value="user_input")
    
    # Call method that uses widgets
    mock_app.process_input()
    
    # Verify widget methods were called
    mock_app.some_entry.get.assert_called_once()
    mock_app.some_button.configure.assert_called_with(state=tk.DISABLED)
```

### Testing Best Practices

1. **Test One Thing**: Each test should validate one specific behavior
2. **Clear Names**: Test names should describe what is being tested and under what conditions
3. **Arrange-Act-Assert**: Structure tests with clear setup, execution, and verification phases
4. **Independent Tests**: Tests should not depend on execution order
5. **Meaningful Assertions**: Use descriptive assertion messages
6. **Document Line References**: When testing specific code logic, reference the line numbers in comments

---

## Troubleshooting

### DISPLAY Environment Variable Issues

**Problem**: Tests fail with `_tkinter.TclError: couldn't connect to display`

**Cause**: GUI tests require an X11 display server, which may not be available in:
- Headless CI/CD environments
- SSH sessions without X11 forwarding
- Docker containers without display configuration

**Solution 1: Use Xvfb (Virtual Framebuffer)**

```bash
# Install Xvfb
sudo apt-get install xvfb  # Ubuntu/Debian
sudo yum install xorg-x11-server-Xvfb  # CentOS/RHEL

# Run tests with Xvfb
xvfb-run pytest
```

**Solution 2: Set Up Virtual Display in CI**

```yaml
# GitHub Actions example
- name: Set up display
  run: |
    sudo apt-get install -y xvfb
    export DISPLAY=:99
    Xvfb :99 -screen 0 1024x768x24 &
    sleep 3
```

**Solution 3: Skip GUI Tests in Headless Environments**

```bash
# Only run unit tests (no GUI)
pytest test_unit.py --benchmark-skip
```

### Common Mock-Related Errors

#### Error: `AttributeError: 'MagicMock' object has no attribute 'X'`

**Cause**: Mock object doesn't have expected attribute configured

**Solution**: Configure mock attributes in fixture or test setup

```python
# Wrong
mock_app.widget.some_method()  # May fail if widget is None

# Right
mock_app.widget = MagicMock()
mock_app.widget.some_method.return_value = expected_value
mock_app.widget.some_method()
```

#### Error: `AssertionError: Expected X to be called but it wasn't`

**Cause**: Code path didn't execute as expected, or mock was configured incorrectly

**Solution**: Verify test logic and add debug output

```python
# Add debug output
print(f"Mock called: {mock_object.method.called}")
print(f"Call count: {mock_object.method.call_count}")
print(f"Call args: {mock_object.method.call_args_list}")

# Check if mock was ever called
if not mock_object.method.called:
    pytest.fail("Method was never called - check test logic")
```

#### Error: `TypeError: 'Mock' object is not iterable`

**Cause**: Trying to iterate over a mock that should return an iterable

**Solution**: Configure mock to return appropriate iterable

```python
# Wrong
mock_object.get_items.return_value = MagicMock()  # Can't iterate

# Right
mock_object.get_items.return_value = ['item1', 'item2', 'item3']
# Or for iterator
mock_object.get_items.return_value = iter(['item1', 'item2'])
```

### Subprocess Mocking Pitfalls

#### Problem: `readline()` Returns Entire Output at Once

**Cause**: `side_effect` not properly configured for line-by-line reading

**Solution**: Use `side_effect` with list of lines

```python
# Wrong
mock_process.stdout.readline.return_value = "line1\nline2\nline3\n"

# Right
mock_process.stdout.readline.side_effect = [
    "line1\n",
    "line2\n",
    "line3\n",
    ""  # Important: empty string to end iteration
]
```

#### Problem: Process Never "Completes"

**Cause**: `poll()` or `wait()` not returning completion status

**Solution**: Configure both return codes

```python
mock_process = MagicMock()
mock_process.wait.return_value = 0  # Success
mock_process.poll.return_value = 0  # Process finished
mock_process.returncode = 0         # Also set returncode attribute
```

#### Problem: `communicate()` vs `stdout.readline()`

**Cause**: Code uses different methods to read subprocess output

**Solution**: Mock the method actually used in code

```python
# If code uses communicate()
mock_process.communicate.return_value = (b"output", b"")

# If code uses readline() in loop
mock_process.stdout.readline.side_effect = ["line1\n", "line2\n", ""]

# Check the actual code to see which pattern it uses!
```

### Threading-Related Test Failures

#### Problem: Test Completes Before Thread Finishes

**Cause**: Asynchronous operations not properly awaited in tests

**Solution**: Wait for threads or use synchronous test patterns

```python
import threading

def test_async_operation(mock_app):
    """Tests operation that uses threading."""
    
    # Start operation
    mock_app.start_fetch_thread()
    
    # Wait for thread to complete
    for thread in threading.enumerate():
        if thread != threading.current_thread():
            thread.join(timeout=5.0)  # Wait max 5 seconds
    
    # Now verify results
    assert mock_app.video_info_list is not None
```

#### Problem: Tests Hang Indefinitely

**Cause**: Thread waiting on a condition that never occurs in test

**Solution**: Mock threading or use timeout

```python
# Mock threading to make synchronous
with patch('threading.Thread') as mock_thread:
    # Make thread.start() immediately call the target function
    def start_thread_immediately(target=None, args=None, **kwargs):
        if target:
            target(*args if args else ())
    
    mock_thread.return_value.start = MagicMock(side_effect=start_thread_immediately)
    
    # Now test runs synchronously
    mock_app.start_fetch_thread()
```

### Import and Module Errors

#### Problem: `ModuleNotFoundError: No module named 'youtube_downloader_gui'`

**Cause**: File has dash in name, making import difficult

**Solution**: Use importlib as shown in test files

```python
import importlib.util
import sys

spec = importlib.util.spec_from_file_location(
    "youtube_downloader_gui", 
    "youtube_downloader-gui.py"
)
youtube_downloader_gui = importlib.util.module_from_spec(spec)
sys.modules['youtube_downloader_gui'] = youtube_downloader_gui
spec.loader.exec_module(youtube_downloader_gui)

# Now can use
YouTubeDownloaderApp = youtube_downloader_gui.YouTubeDownloaderApp
```

### Coverage Issues

#### Problem: Coverage Report Shows 0%

**Cause**: Module name doesn't match file name due to dash

**Solution**: Use the file name directly with --cov

```bash
# Wrong
pytest --cov=youtube_downloader_gui

# Right
pytest --cov=youtube_downloader-gui

# Or with module name after importlib setup
pytest --cov=youtube_downloader_gui --cov-report=term
```

### Performance Issues

#### Problem: Tests Run Very Slowly

**Possible Causes and Solutions**:

1. **Benchmark tests running when not needed**
   ```bash
   pytest --benchmark-skip  # Skip all benchmarks
   ```

2. **Excessive widget creation**
   ```python
   # In unit tests, mock widget creation
   with patch('customtkinter.CTkFrame'):
       # Test code here
   ```

3. **Thread/subprocess timeouts too long**
   ```python
   # Reduce timeout values in tests
   thread.join(timeout=1.0)  # Instead of 5.0
   ```

### Common Test Patterns Not Working

#### Problem: Pytest Doesn't Find Tests

**Causes and Solutions**:

1. **File name doesn't match pattern**
   - Test files must start with `test_` or end with `_test.py`
   - Test functions must start with `test_`

2. **Tests in wrong directory**
   ```bash
   # Run pytest from project root where test files are located
   cd /path/to/project
   pytest
   ```

3. **Import errors prevent test collection**
   ```bash
   # See why tests aren't collected
   pytest --collect-only
   ```

### Getting Help

When tests fail and troubleshooting doesn't help:

1. **Run with maximum verbosity**
   ```bash
   pytest -vv -s --tb=long
   ```

2. **Collect test information without running**
   ```bash
   pytest --collect-only -q
   ```

3. **Check pytest configuration**
   ```bash
   pytest --version
   pytest --markers
   ```

4. **Enable pytest debugging**
   ```bash
   pytest --pdb  # Drop into debugger on failure
   ```

5. **Review test logs**
   - Check line numbers in error messages
   - Match against source code line references in test comments
   - Verify mock configurations match actual code paths

---

## Additional Resources

- **API Documentation**: See `API.md` for detailed method signatures and behavior
- **pytest Documentation**: https://docs.pytest.org/
- **pytest-benchmark Guide**: https://pytest-benchmark.readthedocs.io/
- **unittest.mock Guide**: https://docs.python.org/3/library/unittest.mock.html
- **CustomTkinter Docs**: https://customtkinter.tomschimansky.com/

---

## Quick Reference

### Running Tests Cheat Sheet

```bash
# All tests
pytest

# Unit tests only
pytest test_unit.py -v

# With coverage
pytest --cov=youtube_downloader-gui --cov-report=html

# Benchmarks only
pytest test_benchmark.py --benchmark-only

# Stop on first failure
pytest -x

# Last failed tests
pytest --lf

# Specific test
pytest test_unit.py::test_progress_regex_with_valid_percentage -v
```

### Test Writing Checklist

- [ ] Test name clearly describes what is being tested
- [ ] Docstring explains purpose and references code lines
- [ ] Uses appropriate fixture (`mock_app`, `sample_video_data`, etc.)
- [ ] Follows Arrange-Act-Assert pattern
- [ ] Mocks external dependencies appropriately
- [ ] Has meaningful assertion messages
- [ ] Tests one specific behavior
- [ ] Is independent of other tests

---

**Last Updated**: 2025
**Test Suite Version**: 1.0
**Compatible with**: YouTube Downloader GUI v1.0
