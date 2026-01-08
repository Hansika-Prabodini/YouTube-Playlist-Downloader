# Use List - Interactive Launcher

## Overview

`use_list.py` is an interactive, menu-driven launcher designed to make using the YouTube Downloader applications simple and accessible. It eliminates the need to remember file names and command syntax by providing a user-friendly interface for launching both GUI and CLI versions, checking dependencies, and accessing documentation.

## Why Use use_list.py?

- **No need to remember file names** - Just select from a menu
- **Easy application switching** - Quickly switch between GUI and CLI versions
- **Built-in dependency checking** - Verifies your environment before launching
- **Guided installation** - Install missing dependencies directly from the launcher
- **Quick access to documentation** - View usage information without leaving the terminal
- **Beginner-friendly** - Perfect for first-time users

## Quick Start

### Prerequisites

Before using `use_list.py`, ensure you have Python installed:

- **Python 3.7+** is required
- Download from: [python.org](https://www.python.org)

### Running the Launcher

Simply execute the script:

```bash
python use_list.py
```

Or make it executable (Linux/Mac):

```bash
chmod +x use_list.py
./use_list.py
```

## Menu Options

When you run `use_list.py`, you'll see an interactive menu with the following options:

### 1. Launch GUI Application

Starts the graphical user interface version of the YouTube Downloader (`youtube_downloader-gui.py`).

**Requirements**:
- yt-dlp
- customtkinter

**What it does**:
- Checks if customtkinter is installed
- Verifies the GUI script file exists
- Launches the graphical application window
- Allows you to download videos with a visual interface

**Use when**: You prefer a visual interface with buttons, progress bars, and mouse interactions.

### 2. Launch CLI Application

Starts the command-line interface version of the YouTube Downloader (`youtube_Download-cli.py`).

**Requirements**:
- yt-dlp

**What it does**:
- Verifies the CLI script file exists
- Launches the terminal-based application
- Provides an interactive command-line experience
- Downloads videos directly from the terminal

**Use when**: You prefer working in the terminal or don't have customtkinter installed.

### 3. Check Dependencies

Scans your system for required and optional dependencies.

**Checks for**:
- Python version (recommends 3.7+)
- yt-dlp (required for both GUI and CLI)
- customtkinter (required for GUI only)

**Output includes**:
- ✓ Installed and working dependencies
- ✗ Missing required dependencies
- ○ Missing optional dependencies
- Installation commands for missing packages

**Use when**: 
- First time using the application
- Troubleshooting launch issues
- Verifying your environment is properly configured

### 4. View GUI Documentation

Displays comprehensive documentation for the GUI application.

**Information includes**:
- Feature list
- Usage instructions
- Requirements
- Step-by-step guide

**Use when**: You want to learn about GUI features without launching the application or reading README.md.

### 5. View CLI Documentation

Displays comprehensive documentation for the CLI application.

**Information includes**:
- Feature list
- Usage instructions
- Command examples
- Requirements

**Use when**: You want to learn about CLI features without launching the application or reading README.md.

### 6. Install Dependencies

Provides a guided installation process for required packages.

**Installation options**:
1. Install ALL dependencies (yt-dlp + customtkinter)
2. Install yt-dlp only (CLI will work)
3. Install customtkinter only (for GUI)
0. Cancel

**What it does**:
- Uses pip to install selected packages
- Shows installation progress
- Confirms successful installation
- Provides fallback manual commands if automated installation fails

**Use when**: 
- Setting up the application for the first time
- Missing dependencies detected by option 3
- Want to add GUI support to a CLI-only installation

### 0. Exit

Closes the launcher and returns to your terminal.

## Example Workflows

### Scenario 1: First-Time User Setup

```bash
$ python use_list.py

# The launcher menu appears
# Select option 3 to check dependencies
# Review what's missing
# Select option 6 to install dependencies
# Choose option 1 (Install ALL)
# Wait for installation to complete
# Select option 1 or 2 to launch the application
```

### Scenario 2: Regular Usage (GUI User)

```bash
$ python use_list.py

# Select option 1 (Launch GUI)
# GUI window opens
# Use the application
# Close the GUI when done
# Press Enter to return to launcher menu
# Select option 0 to exit
```

### Scenario 3: Regular Usage (CLI User)

```bash
$ python use_list.py

# Select option 2 (Launch CLI)
# CLI interface starts
# Enter playlist URLs and download
# Type 'exit' in CLI when done
# Press Enter to return to launcher menu
# Select option 0 to exit
```

### Scenario 4: Troubleshooting

```bash
$ python use_list.py

# Try to launch GUI (option 1)
# Receive error about missing customtkinter
# Select option 3 to verify dependencies
# See that customtkinter is missing
# Select option 6 to install dependencies
# Choose option 3 (Install customtkinter only)
# Try launching GUI again (option 1)
# Success!
```

### Scenario 5: Learning Before Using

```bash
$ python use_list.py

# Select option 4 to view GUI docs
# Read about GUI features
# Press Enter to return to menu
# Select option 5 to view CLI docs
# Read about CLI features
# Decide which version to use
# Launch chosen application
```

## Understanding Messages

### Success Messages

```
✓ Successfully installed: yt-dlp, customtkinter
```
**Meaning**: Dependencies were installed successfully.

```
✓ Python 3.10.5 is installed
✓ yt-dlp is installed
✓ customtkinter is installed (required for GUI)
```
**Meaning**: Your environment is properly configured.

### Warning Messages

```
⚠ Missing required dependencies: yt-dlp
Install with: pip install yt-dlp
```
**Meaning**: Core dependencies are missing. Use option 6 to install.

```
⚠ Error: youtube_downloader-gui.py not found in current directory.
```
**Meaning**: You're running the launcher from the wrong directory. Navigate to the project folder.

```
⚠ Error: customtkinter is not installed.
The GUI application requires customtkinter.
```
**Meaning**: GUI cannot launch without customtkinter. Use option 6 to install it.

### Info Messages

```
ℹ Missing optional dependencies: customtkinter
Install with: pip install customtkinter
Note: GUI application requires customtkinter
```
**Meaning**: CLI will work, but GUI requires additional installation.

## System Requirements

### For All Features
- **Python**: 3.7 or higher
- **yt-dlp**: Video downloading engine
- **customtkinter**: Modern GUI framework

### For CLI Only
- **Python**: 3.7 or higher
- **yt-dlp**: Video downloading engine

## Tips and Best Practices

### 1. Always Check Dependencies First
When using the launcher for the first time or after a fresh Python installation, use option 3 to verify your environment.

### 2. Use the Guided Installer
Rather than manually running pip commands, use option 6 for a guided installation experience.

### 3. Keep the Launcher in the Project Directory
The launcher looks for `youtube_downloader-gui.py` and `youtube_Download-cli.py` in the current directory. Always run it from the project root.

### 4. Review Documentation Before First Launch
If you're new to the application, review the documentation (options 4 and 5) before launching to understand available features.

### 5. Use GUI for Visual Feedback, CLI for Speed
- **GUI**: Better for browsing playlists and monitoring multiple downloads
- **CLI**: Faster to launch and more suitable for scripting or remote sessions

## Integration with Other Tools

This launcher complements the other utilities in the project:

- **README.md**: Comprehensive project documentation
- **test_me.py**: Interactive test runner for developers
- **use_list.py**: Interactive launcher for end users (this tool)

**When to use each**:
- Use `README.md` for detailed documentation and manual setup
- Use `test_me.py` if you're developing or testing the code
- Use `use_list.py` for everyday usage and quick access to the applications

## Troubleshooting

### Issue: "python: command not found"

**Solution**: Python is not installed or not in your PATH.
1. Install Python from [python.org](https://www.python.org)
2. During installation, check "Add Python to PATH" (Windows)
3. Verify with: `python --version`

### Issue: "use_list.py not found"

**Possible causes**:
1. You're not in the correct directory
2. File was not downloaded/created

**Solution**: 
```bash
cd path/to/youtube-downloader
ls -la  # Verify use_list.py exists
python use_list.py
```

### Issue: "Permission denied" (Linux/Mac)

**Solution**: Make the file executable
```bash
chmod +x use_list.py
./use_list.py
```

### Issue: Failed to install dependencies

**Solution**: Try manual installation
```bash
# For all features
pip install yt-dlp customtkinter

# For CLI only
pip install yt-dlp
```

If pip doesn't work, try:
```bash
python -m pip install yt-dlp customtkinter
```

### Issue: GUI launches but appears broken

**Possible causes**:
1. Outdated customtkinter version
2. Display server issues (Linux)

**Solution**:
```bash
# Update customtkinter
pip install --upgrade customtkinter

# For Linux, ensure display is set
echo $DISPLAY  # Should show :0 or similar
```

### Issue: CLI works but GUI doesn't launch

**Cause**: customtkinter is not installed

**Solution**: Use option 6, then choose option 3 to install customtkinter, or:
```bash
pip install customtkinter
```

## Advanced Usage

### Running Without the Launcher

If you prefer direct access:

```bash
# Launch GUI directly
python youtube_downloader-gui.py

# Launch CLI directly
python youtube_Download-cli.py
```

### Scripting with the Launcher

While the launcher is interactive, you can automate dependency checks:

```python
import subprocess
import sys

# Check if dependencies are installed
result = subprocess.run([sys.executable, 'use_list.py'], 
                       input='3\n0\n', 
                       capture_output=True, 
                       text=True)
print(result.stdout)
```

## Frequently Asked Questions

### Q: Do I need to use the launcher?

**A:** No, it's optional. You can run `youtube_downloader-gui.py` or `youtube_Download-cli.py` directly. The launcher just makes it easier.

### Q: Can I use the CLI without installing customtkinter?

**A:** Yes! The CLI only requires yt-dlp. customtkinter is only needed for the GUI.

### Q: Will this work on Windows/Mac/Linux?

**A:** Yes, the launcher is cross-platform. It works on any system with Python 3.7+.

### Q: Can I customize the launcher?

**A:** Yes! `use_list.py` is a regular Python script. Feel free to modify it for your needs.

### Q: Does the launcher require internet?

**A:** Only when installing dependencies (option 6). Launching applications works offline.

### Q: Can I use this in a virtual environment?

**A:** Absolutely! The launcher respects your Python environment and will use the active virtualenv.

## Getting Help

If you encounter issues not covered here:

1. Check `README.md` for general project information
2. Verify your Python version: `python --version`
3. Check dependency status with option 3
4. Try reinstalling dependencies with option 6

## Summary

`use_list.py` is your friendly gateway to the YouTube Downloader applications. Whether you're a first-time user or a regular, it provides a consistent, easy-to-use interface for launching applications, managing dependencies, and accessing documentation—all without leaving your terminal.

**Quick Reference**:
- **Option 1**: Launch GUI (needs customtkinter)
- **Option 2**: Launch CLI (lightweight)
- **Option 3**: Check what's installed
- **Option 6**: Install what's missing
- **Option 0**: Exit

Enjoy downloading! 🎥
