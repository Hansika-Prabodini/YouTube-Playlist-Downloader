import subprocess
import sys
import os
import re
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Optional, Set

import yt_playlist
import yt_downloader

# UI Constants
APP_TITLE = "============================================"
APP_NAME = "= YouTube Playlist Downloader (CLI)      ="
DIVIDER = "--------------------------------------------------"
VIDEOS_HEADER = "\n------------------ Videos Found ------------------"

# Error Messages
ERROR_YTDLP_NOT_FOUND = "Error: yt-dlp is not installed or not in your system's PATH."
ERROR_YTDLP_INSTALL_MSG = "Please install it by running: pip install yt-dlp"
ERROR_NO_VIDEOS = "Could not find any videos at that URL. Please try again."
ERROR_FETCH_INFO = "An error occurred while fetching info: {}"
ERROR_DOWNLOAD = "An error occurred during download: {}"
ERROR_INVALID_RANGE = "Invalid range. Please enter valid numbers."
ERROR_INVALID_RANGE_FORMAT = "Invalid range format. Use numbers and a dash (e.g., 1-10)."
ERROR_INVALID_NUMBER = "Invalid number. Please enter a valid number from the list."
ERROR_INVALID_INPUT = "Invalid input. Please use numbers or 'all'."
ERROR_NO_SELECTION = "No videos selected. Please try again."

# User Prompts
PROMPT_PLAYLIST_URL = "\nEnter YouTube Playlist URL (or 'exit' to quit): "
PROMPT_SELECTION = "\nEnter the number(s) to download (e.g., 1, 5, 8-10) or 'all': "

# Status Messages
MSG_FETCHING = "\nFetching playlist info..."
MSG_DOWNLOAD_START = "\n[{}/{}] Starting download for: {}"
MSG_DOWNLOAD_SUCCESS = "Download of '{}' completed successfully."
MSG_DOWNLOAD_FAILED = "Download of '{}' failed."

def main() -> None:
    """Main function to run the command-line interface."""

    # Check if yt-dlp is installed
    try:
        subprocess.run(["yt-dlp", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print(ERROR_YTDLP_NOT_FOUND)
        print(ERROR_YTDLP_INSTALL_MSG)
        sys.exit(1)

    print(APP_TITLE)
    print(APP_NAME)
    print(APP_TITLE)

    while True:
        playlist_url = input(PROMPT_PLAYLIST_URL)
        if playlist_url.lower() == 'exit':
            break

        print(MSG_FETCHING)
        result = yt_playlist.fetch_playlist_info(playlist_url)

        if result['success'] and result['videos']:
            selected_videos = prompt_for_selection(result['videos'])
            if selected_videos:
                download_videos(selected_videos)
        else:
            print(result['error_message'] or ERROR_NO_VIDEOS)

def parse_selection_input(selection_input: str, max_index: int) -> Optional[Set[int]]:
    """
    Parses user selection input into a set of indices.
    
    Args:
        selection_input: User input string (e.g., "1, 5, 8-10")
        max_index: Maximum valid index
        
    Returns:
        A set of valid indices (1-based), or None if input is invalid
    """
    selected_indices = set()
    parts = re.split(r'[,\s]+', selection_input)
    
    for part in parts:
        if not part:
            continue
        
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
                if 1 <= start <= end <= max_index:
                    selected_indices.update(range(start, end + 1))
                else:
                    print(ERROR_INVALID_RANGE)
                    return None
            except ValueError:
                print(ERROR_INVALID_RANGE_FORMAT)
                return None
        else:
            try:
                index = int(part)
                if 1 <= index <= max_index:
                    selected_indices.add(index)
                else:
                    print(ERROR_INVALID_NUMBER)
                    return None
            except ValueError:
                print(ERROR_INVALID_INPUT)
                return None
    
    return selected_indices


def prompt_for_selection(video_list: List[Dict[str, str]]) -> Optional[List[Dict[str, str]]]:
    """
    Displays videos and prompts user for selection.
    
    Args:
        video_list: List of video dictionaries with 'title' and 'url'
        
    Returns:
        List of selected videos, or None if cancelled
    """
    print(VIDEOS_HEADER)
    for i, video in enumerate(video_list, 1):
        print(f"[{i:2}] {video['title']}")
    print(DIVIDER)
    
    while True:
        selection_input = input(PROMPT_SELECTION).strip().lower()
        
        if selection_input == 'all':
            return video_list

        selected_indices = parse_selection_input(selection_input, len(video_list))
        
        if selected_indices:
            return [video_list[i-1] for i in sorted(selected_indices)]
        elif selected_indices is not None:
            # Empty set - valid input but no videos selected
            print(ERROR_NO_SELECTION)

def download_videos(videos_to_download: List[Dict[str, str]], max_workers: int = 1) -> None:
    """
    Downloads the selected videos using yt_downloader.download_video().

    Supports optional concurrent downloads via ThreadPoolExecutor. Pass
    max_workers > 1 to download multiple videos simultaneously.

    Args:
        videos_to_download: List of video dictionaries (from yt_playlist.fetch_playlist_info)
                            containing at least 'title', 'url', and 'webpage_url'.
        max_workers: Number of parallel download workers (default: 1 = sequential).
    """
    total = len(videos_to_download)
    download_dir = os.getcwd()

    def _download_one(index_video: tuple) -> None:
        i, video = index_video
        title = video.get('title', 'Unknown')
        # Prefer the full webpage URL; fall back to the raw 'url' field (may be an ID)
        video_url = video.get('webpage_url') or video.get('url', '')

        print(MSG_DOWNLOAD_START.format(i, total, title))

        def progress_cb(line: str) -> None:
            sys.stdout.write(line + '\n')
            sys.stdout.flush()

        result = yt_downloader.download_video(
            video_url=video_url,
            download_path=download_dir,
            progress_callback=progress_cb
        )

        if result['success']:
            print(MSG_DOWNLOAD_SUCCESS.format(title))
        else:
            print(MSG_DOWNLOAD_FAILED.format(title))
            if result['error_message']:
                print(f"  Reason: {result['error_message']}")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(_download_one, enumerate(videos_to_download, 1))


if __name__ == "__main__":
    main()