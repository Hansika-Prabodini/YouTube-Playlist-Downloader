# UI Components Test Suite Documentation

## Purpose Statement

This test suite provides comprehensive validation for the R-based GUI components built using RGtk2 and gWidgets2RGtk2 frameworks. The tests ensure that:

1. **UI Initialization**: All GUI widgets initialize correctly without errors
2. **Component Existence**: Required widgets (window, buttons, URL entry, scrollable container) are properly created
3. **Widget Properties**: All widgets have correct labels, dimensions, and initial states
4. **Window Configuration**: Main window has proper title, dimensions, and configuration
5. **Accessibility**: Widgets are programmatically accessible and can be manipulated via API
6. **Reliability**: UI components behave consistently across different environments

These tests serve as both validation tools and living documentation for the expected UI structure and behavior. They help catch regressions during development and ensure the GUI meets functional requirements.

## What's Being Tested

### 1. GTK Environment Initialization
- **Test**: `GTK environment initializes correctly`
- **Validates**:
  - RGtk2 package is installed and loadable
  - gWidgets2RGtk2 package is installed and loadable
  - GTK libraries can be loaded without errors
  - Display server is available (X11 or Wayland)

### 2. UI Creation
- **Test**: `UI components can be created without errors`
- **Validates**:
  - ui.R file exists in the project root
  - ui.R sources without syntax errors or runtime exceptions
  - GTK initialization completes successfully

### 3. Widget Existence
- **Test**: `all required widgets exist after UI initialization`
- **Validates**:
  - Main window widget is defined
  - URL entry widget exists (supports multiple naming conventions: url_entry, urlEntry, url_input)
  - Download button exists (supports multiple naming conventions: download_btn, downloadBtn, download_button)
  - Scrollable container exists (supports multiple naming conventions: scroll_container, scrollContainer, scroll_window)

### 4. Widget Labels and Types
- **Test**: `widget labels are set correctly`
- **Validates**:
  - Buttons are proper GButton S3 objects
  - Window is a proper GWindow S3 object
  - All widgets have correct class types from gWidgets2 framework

### 5. Widget States
- **Test**: `widgets have correct initial enabled/disabled states`
- **Validates**:
  - Download button is initially enabled
  - Widgets have appropriate initial state for user interaction

### 6. Window Dimensions
- **Test**: `window has correct dimensions`
- **Validates**:
  - Window width is positive and at least 200 pixels
  - Window height is positive and at least 150 pixels
  - Dimensions are reasonable for the application's use case

### 7. Window Title
- **Test**: `window has correct title`
- **Validates**:
  - Window has a non-empty title string
  - Title is of character type

### 8. Scrollable Container Configuration
- **Test**: `scrollable container is properly configured`
- **Validates**:
  - Scrollable container exists and is not null
  - Container is a proper GComponent or derived class
  - Container is properly initialized

### 9. Scrollable Container Accessibility
- **Test**: `scrollable container is accessible and functional`
- **Validates**:
  - Container is visible (not hidden)
  - Container is accessible for adding child widgets

### 10. Programmatic Widget Access
- **Test**: `widgets are retrievable by name or reference`
- **Validates**:
  - UI environment contains widget objects
  - Window object is retrievable by name
  - At least one button object can be found
  - At least one entry/input widget can be found
  - Naming conventions are consistent and discoverable

### 11. URL Entry Widget Configuration
- **Test**: `URL entry widget is properly configured`
- **Validates**:
  - URL entry widget exists
  - Widget is a GEdit or GComponent object
  - Widget is enabled and visible
  - Widget is ready for user input

### 12. Mock Button Click Events
- **Test**: `button click events can be simulated`
- **Status**: Currently skipped (requires additional mocking framework)
- **Future Implementation**: Will test event handler simulation and response

### 13. UI Cleanup
- **Test**: `UI can be properly disposed/cleaned up`
- **Validates**:
  - Window disposal doesn't throw errors
  - GTK resources can be properly released

## Setup Requirements

### Required R Packages

Install the following packages before running tests:

```r
# Core GTK and GUI packages
install.packages("RGtk2")
install.packages("gWidgets2RGtk2")

# Testing framework
install.packages("testthat")

# Optional: for future mock event testing
install.packages("mockery")
```

### System Dependencies

#### Linux (Ubuntu/Debian)
```bash
# GTK+ 2.x libraries
sudo apt-get update
sudo apt-get install -y libgtk2.0-dev

# X11 development libraries
sudo apt-get install -y libx11-dev

# For headless testing
sudo apt-get install -y xvfb
```

#### Linux (Fedora/RHEL/CentOS)
```bash
# GTK+ 2.x libraries
sudo dnf install gtk2-devel

# X11 development libraries
sudo dnf install libX11-devel

# For headless testing
sudo dnf install xorg-x11-server-Xvfb
```

#### macOS
```bash
# Using Homebrew
brew install gtk+

# XQuartz for X11 support (if needed)
brew install --cask xquartz
```

#### Windows
- Install GTK+ runtime from: https://gtk.org/download/windows.php
- RGtk2 should handle most dependencies automatically
- Ensure PATH includes GTK bin directory

### Display Server Requirements

**Interactive Environments**: Tests run normally if a display server is available (e.g., during local development with a GUI).

**Headless/CI Environments**: Use Xvfb (X Virtual Framebuffer) to provide a virtual display:

```bash
# Start Xvfb on display :99
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99

# Now run tests
Rscript -e "testthat::test_file('test_ui_components.R')"
```

Or use `xvfb-run` wrapper:

```bash
xvfb-run Rscript -e "testthat::test_file('test_ui_components.R')"
```

### Verifying Setup

Before running the full test suite, verify your environment:

```r
# Check package availability
requireNamespace("RGtk2", quietly = TRUE)
requireNamespace("gWidgets2RGtk2", quietly = TRUE)
requireNamespace("testthat", quietly = TRUE)

# Test GTK initialization
library(RGtk2)
library(gWidgets2RGtk2)
w <- gwindow("Test", visible = FALSE)
dispose(w)
# If no errors, your setup is ready!
```

## Execution Instructions

### Running All Tests

#### Using testthat::test_file() (Recommended for single file)
```r
# From R console
library(testthat)
test_file('test_ui_components.R')
```

#### Using devtools::test() (Recommended for package development)
```r
# From R console (if this is part of an R package)
library(devtools)
test()
```

#### From Command Line
```bash
# Run tests directly
Rscript -e "library(testthat); test_file('test_ui_components.R')"

# With Xvfb for headless environments
xvfb-run Rscript -e "library(testthat); test_file('test_ui_components.R')"
```

### Running Specific Tests

```r
library(testthat)

# Run only GTK initialization test
test_file('test_ui_components.R', filter = "GTK environment")

# Run only widget existence tests
test_file('test_ui_components.R', filter = "widgets exist")

# Run only window configuration tests
test_file('test_ui_components.R', filter = "window")
```

### Verbose Output

```r
# Get detailed test output
library(testthat)
test_file('test_ui_components.R', reporter = "progress")

# Or use stop reporter for more detail
test_file('test_ui_components.R', reporter = "stop")
```

### Continuous Integration

Example GitHub Actions workflow snippet:

```yaml
- name: Install system dependencies
  run: |
    sudo apt-get update
    sudo apt-get install -y libgtk2.0-dev xvfb

- name: Install R packages
  run: |
    Rscript -e "install.packages(c('RGtk2', 'gWidgets2RGtk2', 'testthat'))"

- name: Run UI tests
  run: |
    xvfb-run Rscript -e "testthat::test_file('test_ui_components.R')"
```

## Known Limitations

### 1. X11/Display Server Requirement

**Limitation**: GTK applications require a display server (X11, Wayland, or Windows display system) to initialize, even if windows are never shown.

**Impact**: Tests cannot run in truly headless environments without Xvfb or similar virtual display solution.

**Workaround**: Use Xvfb (X Virtual Framebuffer) for CI/CD pipelines and headless servers:
```bash
xvfb-run Rscript -e "testthat::test_file('test_ui_components.R')"
```

### 2. Mock Event Testing Limited

**Limitation**: Mock button click events test is currently skipped because GTK event simulation requires complex setup and the mockery package integration is not yet implemented.

**Impact**: Cannot currently test event handler behavior programmatically.

**Future Work**: 
- Implement event handler mocking using mockery package
- Create test fixtures that allow handler functions to be tested independently
- Explore GTK signal emission for event simulation

### 3. Platform-Specific Behavior

**Limitation**: GTK rendering and widget behavior may vary slightly across platforms (Linux, macOS, Windows).

**Impact**: Some tests (especially dimension and property tests) may need platform-specific expectations.

**Workaround**: Use conditional test logic based on `Sys.info()['sysname']` if needed.

### 4. Asynchronous Operations

**Limitation**: Tests assume synchronous widget creation. If ui.R uses asynchronous initialization, tests may fail intermittently.

**Impact**: Race conditions in test execution.

**Workaround**: Add appropriate wait/polling mechanisms if async operations are detected.

### 5. GTK Version Dependencies

**Limitation**: Tests assume GTK 2.x through RGtk2. GTK 3.x has different R bindings.

**Impact**: Cannot test GTK3-based UIs without modifying test suite.

**Note**: RGtk2 is based on GTK 2.x, which is mature but older. Consider migration path to GTK 3.x in the future.

## Troubleshooting Tips

### Error: "RGtk2 package not available"

**Problem**: RGtk2 package not installed or not loadable.

**Solutions**:
1. Install the package: `install.packages("RGtk2")`
2. Check system GTK libraries are installed (see Setup Requirements)
3. On Linux, ensure `pkg-config` can find GTK: `pkg-config --modversion gtk+-2.0`
4. On Windows, ensure GTK runtime is in PATH

### Error: "unable to open display"

**Problem**: No X11 display server available.

**Solutions**:
1. In local environment, ensure X server is running
2. In SSH sessions, use X forwarding: `ssh -X user@host`
3. In headless/CI, use Xvfb: `xvfb-run Rscript ...`
4. Set DISPLAY environment variable: `export DISPLAY=:0`

### Error: "cannot load shared object libgtk-x11-2.0.so"

**Problem**: GTK shared libraries not found.

**Solutions**:
1. Install GTK development libraries (see Setup Requirements)
2. Update library cache: `sudo ldconfig` (Linux)
3. Check LD_LIBRARY_PATH includes GTK lib directory
4. Reinstall RGtk2: `install.packages("RGtk2", type = "source")`

### Error: "ui.R file must exist"

**Problem**: The test cannot find ui.R in the project root.

**Solutions**:
1. Ensure ui.R exists and is in the same directory as test_ui_components.R
2. Set working directory: `setwd("/path/to/project")`
3. Verify file permissions allow reading
4. Complete ticket #2 (Create ui.R) before running tests

### Warning: "GTK packages not available" (tests skipped)

**Problem**: Tests are being skipped due to missing dependencies.

**Solutions**:
1. This is expected behavior if GTK is intentionally not available
2. Install missing packages: `install.packages(c("RGtk2", "gWidgets2RGtk2"))`
3. Review Setup Requirements section
4. Tests will skip gracefully rather than fail

### Error: "Widget not found" or "object not found"

**Problem**: Expected widget doesn't exist in ui.R environment.

**Solutions**:
1. Check ui.R creates all required widgets
2. Verify widget naming conventions match test expectations
3. Ensure ui.R assigns widgets to environment (not just local variables)
4. Review ui.R implementation for completeness

### Tests pass locally but fail in CI

**Problem**: Environment differences between local and CI.

**Solutions**:
1. Ensure CI uses Xvfb: `xvfb-run ...`
2. Check GTK libraries are installed in CI: add to dependency installation step
3. Verify R package versions match between environments
4. Add verbose logging to identify specific failure point
5. Check CI environment variables (DISPLAY, HOME, etc.)

### GTK initialization is slow

**Problem**: Test suite takes long time to initialize GTK.

**Solutions**:
1. This is normal for GTK initialization (one-time cost)
2. Consider grouping all UI tests together to share initialization
3. Use test fixtures or setup functions to initialize once
4. Cache GTK initialization state if possible

### Memory leaks or resource warnings

**Problem**: Tests report memory issues or unclosed resources.

**Solutions**:
1. Ensure all widgets are properly disposed: `dispose(widget)`
2. Add cleanup code in test teardown
3. Use `on.exit()` in tests to guarantee cleanup
4. Close windows explicitly before test completion
5. Monitor with: `gc()` to force garbage collection

## Best Practices for Maintaining Tests

1. **Keep tests independent**: Each test should set up and tear down its own environment
2. **Use descriptive names**: Test names should clearly describe what's being validated
3. **Skip appropriately**: Use `skip_if_not()` for optional dependencies
4. **Test both positive and negative cases**: Verify both correct behavior and error handling
5. **Update tests with UI changes**: When ui.R changes, update tests immediately
6. **Document assumptions**: Add comments explaining why specific values are expected
7. **Version control**: Track test changes alongside ui.R changes
8. **Review regularly**: Ensure tests still provide value as application evolves

## Additional Resources

- **testthat documentation**: https://testthat.r-lib.org/
- **RGtk2 documentation**: https://www.rdocumentation.org/packages/RGtk2
- **gWidgets2RGtk2 documentation**: https://www.rdocumentation.org/packages/gWidgets2RGtk2
- **GTK documentation**: https://www.gtk.org/docs/
- **Xvfb usage**: `man Xvfb` or https://www.x.org/releases/X11R7.6/doc/man/man1/Xvfb.1.xhtml

## Support

For issues specific to:
- **Test failures**: Review troubleshooting section above
- **GTK setup**: Consult RGtk2 package documentation and system GTK installation guides
- **Test framework**: Refer to testthat package documentation
- **UI implementation**: Review ui.R code and application requirements

---

**Last Updated**: [Current Date]  
**Test Suite Version**: 1.0  
**Compatible with**: R >= 3.6.0, RGtk2 >= 2.20.36, gWidgets2RGtk2 >= 1.0-7, testthat >= 3.0.0
