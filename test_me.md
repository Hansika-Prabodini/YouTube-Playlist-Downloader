# Test Me - Interactive Test Runner

## Overview

`test_me.py` is an interactive, menu-driven test runner designed to make testing the YouTube Downloader application simple and accessible. It eliminates the need to remember complex pytest commands by providing a user-friendly interface for running various test configurations.

## Why Use test_me.py?

- **No need to memorize pytest commands** - Just select from a menu
- **Guided testing experience** - Perfect for newcomers to the project
- **Quick access to common test scenarios** - Run unit, functional, or all tests with one keystroke
- **Built-in dependency checking** - Verifies your testing environment before running tests
- **Interactive workflow** - Stay in the runner to execute multiple test configurations

## Quick Start

### Prerequisites

Before using `test_me.py`, ensure you have the required dependencies installed:

```bash
# Install required testing framework
pip install pytest

# Optional but recommended for full functionality
pip install pytest-cov pytest-benchmark
```

### Running the Test Runner

Simply execute the script:

```bash
python test_me.py
```

Or make it executable (Linux/Mac):

```bash
chmod +x test_me.py
./test_me.py
```

## Menu Options

When you run `test_me.py`, you'll see an interactive menu with the following options:

### 1. Run ALL tests (unit + functional)
Executes the complete test suite including both unit and functional tests. This is equivalent to running `pytest -v`.

**Use when**: You want to verify the entire application is working correctly.

### 2. Run UNIT tests only
Runs only the unit tests from `test_unit.py`. These tests are fast and focus on individual methods and logic components.

**Use when**: You're developing new features and want quick feedback on isolated functionality.

### 3. Run FUNCTIONAL tests only
Runs only the functional/integration tests from `test_functional.py`. These tests validate complete workflows and GUI interactions.

**Use when**: You want to verify end-to-end user scenarios without running the faster unit tests.

### 4. Run tests with COVERAGE report
Executes all tests while measuring code coverage. Shows which lines of code are tested and which aren't.

**Use when**: You want to understand how thoroughly the codebase is tested.

**Output includes**:
- Percentage of code covered by tests
- List of lines not covered by tests
- Suggestion to generate HTML report for visual coverage analysis

### 5. Run tests with VERBOSE output
Runs all tests with maximum verbosity (`-vv`) and shows print statements (`-s`).

**Use when**: You need detailed debugging information or want to see print statements from tests.

### 6. Run SPECIFIC test by name
Allows you to run a single test function by entering its name.

**Example**: Enter `test_progress_regex_with_valid_percentage` to run only that specific test.

**Use when**: You're focused on fixing or developing a specific test case.

### 7. Run tests matching KEYWORD
Runs all tests whose names contain the specified keyword.

**Example**: Enter `progress` to run all tests with "progress" in their name.

**Use when**: You want to run a group of related tests without specifying each one individually.

### 8. Show available tests (collect only)
Lists all available tests without actually running them.

**Use when**: You want to see what tests exist or find the exact name of a test.

### 9. Run last FAILED tests
Runs only the tests that failed in the previous test execution.

**Use when**: You've fixed some bugs and want to verify only the previously failing tests now pass.

### 0. Exit
Closes the test runner.

## Example Workflows

### Scenario 1: First-Time Testing

```bash
$ python test_me.py

# The runner will check dependencies
# Select option 1 to run all tests
# Review the results
# Press Enter to return to menu
# Select 0 to exit
```

### Scenario 2: Debugging a Specific Feature

```bash
$ python test_me.py

# Select option 7 (keyword matching)
# Enter keyword: "download"
# All download-related tests will run
# If some fail, select option 9 to re-run only failures
```

### Scenario 3: Checking Test Coverage

```bash
$ python test_me.py

# Select option 4 (coverage report)
# Review which code is/isn't covered
# Identify areas needing more tests
```

### Scenario 4: Quick Unit Test Feedback Loop

```bash
$ python test_me.py

# While developing, repeatedly:
# - Select option 2 (unit tests only)
# - Make code changes
# - Press Enter and select option 2 again
```

## Understanding Test Results

### Successful Test Run

```
============================== test session starts ===============================
collected 42 items

test_unit.py::test_progress_regex_with_valid_percentage PASSED          [  2%]
test_unit.py::test_progress_regex_with_invalid_formats PASSED           [  4%]
...
============================== 42 passed in 2.51s ================================
```

**Meaning**: All tests passed ✓

### Failed Test Run

```
============================== FAILURES ==========================================
____________________ test_progress_regex_with_valid_percentage __________________

    def test_progress_regex_with_valid_percentage():
>       assert extracted_percentage == expected_percentage
E       AssertionError: Expected 25.5%, got 25.0%

================================ short test summary info =========================
FAILED test_unit.py::test_progress_regex_with_valid_percentage - AssertionError
============================== 1 failed, 41 passed in 2.71s ======================
```

**Meaning**: One test failed - the assertion did not match expectations. Review the error message and fix the code or test.

## Dependency Checking

When `test_me.py` starts, it checks for:

### Required Dependencies
- ✓ **pytest** - Core testing framework (REQUIRED)

If pytest is missing, the runner will display an installation command and exit.

### Optional Dependencies
- ○ **pytest-cov** - For coverage reports (option 4)
- ○ **pytest-benchmark** - For performance testing

If optional dependencies are missing, the runner will continue but some features may not work.

## Tips and Best Practices

### 1. Run Tests Before Committing Code
Always run the full test suite (option 1) before committing changes to ensure you haven't broken existing functionality.

### 2. Use Unit Tests During Development
Unit tests (option 2) run faster than functional tests, making them ideal for rapid development cycles.

### 3. Check Coverage Regularly
Periodically run option 4 to ensure new code has corresponding tests.

### 4. Use Keywords Efficiently
When working on a specific feature (e.g., downloads, progress, regex), use option 7 with relevant keywords to run only related tests.

### 5. Debug with Verbose Mode
If a test fails and you need more information, use option 5 to see detailed output and print statements.

## Integration with TESTING.md

This interactive runner complements the comprehensive testing documentation in `TESTING.md`:

- **TESTING.md**: Detailed documentation of testing philosophy, test structure, and manual pytest commands
- **test_me.py**: Quick, interactive access to common testing scenarios

For advanced testing configurations, refer to `TESTING.md`. For everyday testing needs, use `test_me.py`.

## Troubleshooting

### Issue: "pytest not found"

**Solution**: Install pytest
```bash
pip install pytest
```

### Issue: "No tests collected"

**Possible causes**:
1. Test files not in current directory
2. Test files don't follow naming convention (test_*.py)

**Solution**: Ensure you're running from the project root directory containing `test_unit.py` and `test_functional.py`.

### Issue: Tests fail with import errors

**Solution**: Install application dependencies
```bash
pip install customtkinter yt-dlp
```

### Issue: Functional tests fail with "no display"

**Cause**: Functional tests require a GUI display environment.

**Solutions**:
- On Linux servers: Use `xvfb-run pytest test_functional.py`
- Skip functional tests: Use option 2 (unit tests only)

## Command-Line Alternatives

While `test_me.py` provides an interactive experience, you can achieve the same results with direct pytest commands:

| test_me.py Option | Equivalent pytest Command |
|-------------------|---------------------------|
| Option 1 | `pytest -v` |
| Option 2 | `pytest test_unit.py -v` |
| Option 3 | `pytest test_functional.py -v` |
| Option 4 | `pytest --cov=youtube_downloader-gui --cov-report=term-missing` |
| Option 5 | `pytest -vv -s` |
| Option 6 | `pytest -k test_name -v` |
| Option 7 | `pytest -k keyword -v` |
| Option 8 | `pytest --collect-only` |
| Option 9 | `pytest --lf -v` |

## Contributing

When adding new tests to the project:

1. Follow the existing test structure in `test_unit.py` or `test_functional.py`
2. Ensure new tests are discoverable by pytest (use `test_` prefix)
3. Run the full suite with option 1 to verify nothing broke
4. Update this documentation if you add new testing categories

## Support

For more information about:
- **Test structure and philosophy**: See `TESTING.md`
- **Project setup**: See `README.md`
- **pytest documentation**: Visit [pytest.org](https://docs.pytest.org/)

---

**Happy Testing!** 🚀
