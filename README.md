# YouTube Playlist Downloader

This repository contains two versions of a comprehensive YouTube playlist and single video downloader: a Graphical User Interface (GUI) application and a Command-Line Interface (CLI) script. Both tools leverage the powerful `yt-dlp` library to efficiently download videos from YouTube with advanced features and customization options.

## Project Structure

```
├── youtube_downloader-gui.py    # GUI version with modern interface
├── youtube_Download-cli.py      # Command-line version
├── EDA_01.R                     # R script for data analysis
└── README.md                    # This documentation file
```

## Features

### GUI Application (`youtube_downloader-gui.py`)

- **Modern User Interface**: Clean, user-friendly graphical interface built with CustomTkinter
- **Playlist Loading**: Load YouTube playlist URLs to preview all video titles
- **Individual Video Downloads**: Select and download specific videos from playlists
- **Batch Download**: Download all videos in a playlist with one click
- **MP3 Audio Extraction**: Option to download audio-only in MP3 format
- **Real-time Progress Bars**: Visual progress indicators for each downloading video
- **Download Management**: Cancel individual downloads or all active downloads
- **Custom Save Directory**: Choose where to save your downloaded files
- **Right-Click Context Menu**: Convenient paste functionality
- **URL Validation**: Automatic validation of YouTube URLs
- **Error Handling**: Graceful error handling with user-friendly messages

### CLI Script (`youtube_Download-cli.py`)

- **Terminal-Based Interface**: Full functionality from the command line
- **Interactive Playlist Loading**: Enter YouTube URLs and see all available videos
- **Flexible Selection**: Choose videos by number, ranges (e.g., 5-8), or download all
- **MP3 Download Option**: Convert videos to audio format during download
- **Real-time Progress**: Shows detailed yt-dlp download progress in terminal
- **Batch Processing**: Efficient handling of multiple video downloads
- **Custom Output Directory**: Specify download location

## Requirements

- **Python**: Version 3.8+ (Python 3.9+ recommended)
- **yt-dlp**: Modern YouTube downloader library
- **customtkinter**: Modern UI library (GUI only)
- **tkinter**: Standard Python GUI library (usually pre-installed)

## Installation

### Step 1: Install Python

1. Download Python from [python.org](https://python.org)
2. **Important**: During installation on Windows, check "Add Python to PATH"
3. Verify installation:
   ```bash
   python --version
   ```

### Step 2: Install Required Packages

```bash
# Install yt-dlp (required for both versions)
python -m pip install yt-dlp

# Install CustomTkinter (required for GUI version only)
python -m pip install customtkinter
```

### Step 3: Download the Scripts

Clone this repository or download the Python files directly to your desired directory.

## Usage

### GUI Application

1. **Navigate to the project directory**:
   ```bash
   cd path/to/your/project/folder
   ```

2. **Run the GUI application**:
   ```bash
   python youtube_downloader-gui.py
   ```

3. **Using the GUI**:
   - Paste a YouTube playlist or video URL in the input field
   - Click "Load Playlist" to preview available videos
   - Select individual videos or choose "Download All"
   - Choose video or MP3 format
   - Select your preferred download directory
   - Monitor progress with the built-in progress bars

### CLI Application

1. **Navigate to the project directory**:
   ```bash
   cd path/to/your/project/folder
   ```

2. **Run the CLI script**:
   ```bash
   python youtube_Download-cli.py
   ```

3. **Using the CLI**:
   - Enter a YouTube playlist or video URL when prompted
   - Review the list of available videos
   - Choose download options:
     - Specific video numbers (e.g., `1,3,5`)
     - Ranges (e.g., `1-5`)
     - All videos (`all`)
   - Select format (video or MP3)
   - Monitor download progress in real-time

## Examples

### Valid YouTube URLs

**Playlist URLs**:
```
https://www.youtube.com/playlist?list=PLxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
https://youtube.com/playlist?list=PLxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Individual Video URLs**:
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://youtu.be/dQw4w9WgXcQ
```

### CLI Usage Examples

```bash
# Basic usage
python youtube_Download-cli.py

# Example interaction:
Enter YouTube URL: https://www.youtube.com/playlist?list=PLrAXtmRdnEQy6nuLMlE6J6CAia2Ghm5Cn
# (Videos will be listed)
Select videos to download (e.g., 1,3,5 or 1-10 or 'all'): 1-5
Download as MP3? (y/n): n
```

## Troubleshooting

### Common Issues

1. **"yt-dlp not found" or "No module named 'yt_dlp'"**
   ```bash
   # Solution: Install or reinstall yt-dlp
   python -m pip install --upgrade yt-dlp
   ```

2. **"No module named 'customtkinter'"** (GUI only)
   ```bash
   # Solution: Install CustomTkinter
   python -m pip install customtkinter
   ```

3. **Network connectivity issues**
   - Check your internet connection
   - Some networks may block YouTube downloads
   - Try using a different network or VPN

4. **"Invalid URL" errors**
   - Ensure the YouTube URL is complete and correct
   - Make sure the playlist is public (not private)
   - Try copying the URL directly from your browser

5. **Permission errors**
   - Run with administrator/root privileges if needed
   - Check that the download directory is writable
   - Ensure sufficient disk space

6. **Downloads fail or stop unexpectedly**
   - Update yt-dlp to the latest version:
     ```bash
     python -m pip install --upgrade yt-dlp
     ```
   - The video might be region-restricted or removed
   - Try downloading individual videos instead of entire playlists

### Getting Help

If you encounter issues not covered here:

1. Check that all requirements are properly installed
2. Ensure you're using a supported Python version (3.8+)
3. Verify that the YouTube URL is accessible in your browser
4. Try running the scripts with administrator privileges

## Additional Notes

- **R Script**: The `EDA_01.R` file contains exploratory data analysis code that may be related to download statistics or video metadata analysis
- **File Formats**: Both applications support various video formats and quality options provided by yt-dlp
- **Updates**: Keep yt-dlp updated regularly as YouTube frequently changes its API
