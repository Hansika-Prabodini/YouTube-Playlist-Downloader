#!/usr/bin/env python3
"""
Interactive Launcher for YouTube Downloader

This script provides an easy-to-use interface for launching the YouTube
Downloader applications without needing to remember exact command syntax.
It offers a simple menu system to run either the GUI or CLI version, check
dependencies, and access documentation.

Usage:
    python use_list.py
    
Requirements:
    - Python 3.7+
    - yt-dlp
    - customtkinter (for GUI only)
"""

import sys
import subprocess
import os


def print_header():
    """Print the application header."""
    print("\n" + "="*70)
    print("  YouTube Downloader - Interactive Launcher")
    print("="*70 + "\n")


def print_menu():
    """Print the main menu options."""
    print("Select an option:\n")
    print("  1. Launch GUI Application")
    print("  2. Launch CLI Application")
    print("  3. Check Dependencies")
    print("  4. View GUI Documentation")
    print("  5. View CLI Documentation")
    print("  6. Install Dependencies")
    print("  0. Exit")
    print()


def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...\n")
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 7):
        print(f"  ✓ Python {python_version.major}.{python_version.minor}.{python_version.micro} is installed")
    else:
        print(f"  ✗ Python version is {python_version.major}.{python_version.minor}.{python_version.micro} (3.7+ recommended)")
    
    # Check required dependencies
    required = {
        'yt-dlp': 'yt_dlp',
    }
    
    optional = {
        'customtkinter': 'customtkinter',
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
            print(f"  ✓ {name} is installed (required for GUI)")
        except ImportError:
            missing_optional.append(name)
            print(f"  ○ {name} is NOT installed (required for GUI)")
    
    if missing_required:
        print(f"\n⚠ Missing required dependencies: {', '.join(missing_required)}")
        print("Install with: pip install yt-dlp")
        return False
    
    if missing_optional:
        print(f"\nℹ Missing optional dependencies: {', '.join(missing_optional)}")
        print("Install with: pip install customtkinter")
        print("Note: GUI application requires customtkinter")
    
    print()
    return True


def install_dependencies():
    """Guide user through installing dependencies."""
    print("\n" + "-"*70)
    print("Installing Dependencies")
    print("-"*70 + "\n")
    
    print("Select what to install:\n")
    print("  1. Install ALL dependencies (yt-dlp + customtkinter)")
    print("  2. Install yt-dlp only (CLI will work)")
    print("  3. Install customtkinter only (for GUI)")
    print("  0. Cancel")
    print()
    
    choice = input("Enter your choice (0-3): ").strip()
    
    if choice == '0':
        return
    elif choice == '1':
        packages = ['yt-dlp', 'customtkinter']
    elif choice == '2':
        packages = ['yt-dlp']
    elif choice == '3':
        packages = ['customtkinter']
    else:
        print("\n⚠ Invalid choice.")
        return
    
    print(f"\nInstalling: {', '.join(packages)}...\n")
    try:
        cmd = [sys.executable, '-m', 'pip', 'install'] + packages
        subprocess.run(cmd, check=True)
        print(f"\n✓ Successfully installed: {', '.join(packages)}")
    except subprocess.CalledProcessError:
        print(f"\n✗ Failed to install packages. Try manually: pip install {' '.join(packages)}")
    except Exception as e:
        print(f"\n✗ Error: {e}")


def launch_gui():
    """Launch the GUI application."""
    print("\n" + "-"*70)
    print("Launching GUI Application...")
    print("-"*70 + "\n")
    
    # Check if customtkinter is available
    try:
        import customtkinter
    except ImportError:
        print("⚠ Error: customtkinter is not installed.")
        print("The GUI application requires customtkinter.")
        print("\nInstall it with: pip install customtkinter")
        print("Or use option 6 from the main menu to install dependencies.")
        return
    
    # Check if the GUI script exists
    if not os.path.exists('youtube_downloader-gui.py'):
        print("⚠ Error: youtube_downloader-gui.py not found in current directory.")
        return
    
    try:
        subprocess.run([sys.executable, 'youtube_downloader-gui.py'])
    except KeyboardInterrupt:
        print("\nGUI application closed.")
    except Exception as e:
        print(f"\n⚠ Error launching GUI: {e}")


def launch_cli():
    """Launch the CLI application."""
    print("\n" + "-"*70)
    print("Launching CLI Application...")
    print("-"*70 + "\n")
    
    # Check if the CLI script exists
    if not os.path.exists('youtube_Download-cli.py'):
        print("⚠ Error: youtube_Download-cli.py not found in current directory.")
        return
    
    try:
        subprocess.run([sys.executable, 'youtube_Download-cli.py'])
    except KeyboardInterrupt:
        print("\nCLI application closed.")
    except Exception as e:
        print(f"\n⚠ Error launching CLI: {e}")


def view_gui_docs():
    """Display GUI documentation."""
    print("\n" + "-"*70)
    print("GUI Application Documentation")
    print("-"*70 + "\n")
    
    docs = """
The GUI Application (youtube_downloader-gui.py) provides a graphical interface
for downloading YouTube videos and playlists.

FEATURES:
  • User-friendly graphical window
  • Load and browse YouTube playlists
  • Download individual videos or entire playlists
  • Visual progress bars for each download
  • Cancel individual or all downloads
  • Choose custom save directory
  • Audio-only (MP3) download option
  • Right-click paste support

HOW TO USE:
  1. Launch the GUI application (option 1 from main menu)
  2. Paste a YouTube playlist or video URL in the input field
  3. Click "Load Playlist" to fetch video information
  4. Select videos to download or use "Download All"
  5. Optionally check "MP3" for audio-only downloads
  6. Choose a save directory with "Change Folder"
  7. Monitor progress bars for download status

REQUIREMENTS:
  • Python 3.7+
  • yt-dlp
  • customtkinter

For more details, see README.md
    """
    print(docs)


def view_cli_docs():
    """Display CLI documentation."""
    print("\n" + "-"*70)
    print("CLI Application Documentation")
    print("-"*70 + "\n")
    
    docs = """
The CLI Application (youtube_Download-cli.py) provides a command-line interface
for downloading YouTube videos and playlists.

FEATURES:
  • Terminal-based interface
  • Load YouTube playlists with video listings
  • Select specific videos by number or range
  • Download all videos at once
  • Real-time download progress
  • Organized file output

HOW TO USE:
  1. Launch the CLI application (option 2 from main menu)
  2. Enter a YouTube playlist URL when prompted
  3. View the list of videos with their numbers
  4. Select videos to download:
     - Enter specific numbers: 1, 3, 5
     - Enter ranges: 1-5, 8-10
     - Enter 'all' to download everything
  5. Watch the download progress in the terminal
  6. Downloaded files are saved in the 'downloads' folder

REQUIREMENTS:
  • Python 3.7+
  • yt-dlp

For more details, see README.md
    """
    print(docs)


def main():
    """Main function to run the interactive launcher."""
    print_header()
    
    while True:
        print_menu()
        choice = input("Enter your choice (0-6): ").strip()
        
        if choice == '0':
            print("\nExiting launcher. Goodbye!\n")
            sys.exit(0)
        
        elif choice == '1':
            # Launch GUI
            launch_gui()
        
        elif choice == '2':
            # Launch CLI
            launch_cli()
        
        elif choice == '3':
            # Check dependencies
            check_dependencies()
        
        elif choice == '4':
            # View GUI docs
            view_gui_docs()
        
        elif choice == '5':
            # View CLI docs
            view_cli_docs()
        
        elif choice == '6':
            # Install dependencies
            install_dependencies()
        
        else:
            print("\n⚠ Invalid choice. Please select a number from 0 to 6.\n")
            continue
        
        # Pause before showing menu again
        input("\nPress Enter to continue...")
        print("\n" * 2)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nLauncher interrupted. Goodbye!\n")
        sys.exit(0)
