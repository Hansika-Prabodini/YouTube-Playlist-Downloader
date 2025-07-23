# youtube_Download-cli.py

import subprocess
import json
import sys
import os
import re
from typing import List, Dict, Set

# --- Configuration ---
DOWNLOAD_DIR = "downloads"

def main():
    """Main function to run the command-line interface."""

    # --- Pre-run Checks ---
    # Check if yt-dlp is installed
    try:
        subprocess.run(["yt-dlp", "--version"], check=True, capture_output=True)
    except FileNotFoundError:
        print("Error: yt-dlp is not installed or not in your system's PATH.", file=sys.stderr)
        print("Please install it (e.g., 'pip install yt-dlp') and ensure it's accessible.", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError:
        print("Error: yt-dlp is installed but seems to be broken.", file=sys.stderr)
        sys.exit(1)

    # Create download directory if it doesn't exist
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)


    print("=============================================")
    print("=      YouTube Playlist Downloader (CLI)    =")
    print("=============================================")

    # --- Main Application Loop ---
    while True:
        playlist_url = input("\nEnter YouTube Playlist URL (or 'exit' to quit): ").strip()
        if playlist_url.lower() == 'exit':
            print("Exiting.")
            break

        if not playlist_url:
            continue

        print("\nFetching playlist info...")
        videos = fetch_playlist_info(playlist_url)

        if videos:
            selected_videos = prompt_for_selection(videos)
            if selected_videos:
                download_videos(selected_videos, DOWNLOAD_DIR)
        else:
            # Error messages from fetch_playlist_info are printed within the function
            print("Please check the URL and try again.")


def fetch_playlist_info(url: str) -> List[Dict[str, str]]:
    """
    Fetches video titles and URLs from a playlist using yt-dlp.
    Args:
        url: The URL of a YouTube playlist.
    Returns:
        A list of video info dictionaries, or an empty list if an error occurs.
    """
    try:
        command = [
            "yt-dlp",
            "--flat-playlist",
            "-j",           # Get JSON output
            "--no-warnings",
            url
        ]
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True  # Raise CalledProcessError for non-zero exit codes
        )

        video_info_list: List[Dict[str, str]] = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            try:
                video_json = json.loads(line)
                # Ensure basic fields are present
                if 'title' in video_json and 'url' in video_json:
                    video_info_list.append({
                        'title': video_json['title'],
                        'url': video_json['url']
                    })
            except json.JSONDecodeError:
                print(f"Warning: Could not decode JSON line: {line}", file=sys.stderr)

        if not video_info_list:
            print("No videos found in the playlist.", file=sys.stderr)

        return video_info_list

    except FileNotFoundError:
        # This error is already checked in main, but good practice to have it here too.
        print("Error: yt-dlp not found.", file=sys.stderr)
        return []
    except subprocess.CalledProcessError as e:
        print(f"Error executing yt-dlp: {e}", file=sys.stderr)
        print(f"Stderr: {e.stderr.strip()}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"An unexpected error occurred while fetching info: {e}", file=sys.stderr)
        return []


def _parse_user_selection(selection_input: str, max_index: int) -> Set[int]:
    """
    Parses the user's video selection string (e.g., '1, 3-5, 7').
    Args:
        selection_input: The raw string from the user.
        max_index: The total number of videos available for selection.
    Returns:
        A set of integer indices corresponding to the user's selection.
    Raises:
        ValueError: If the input is invalid.
    """
    selected_indices: Set[int] = set()
    parts = re.split(r'[,\s]+', selection_input)

    for part in parts:
        if not part:
            continue

        if '-' in part:
            try:
                start_str, end_str = part.split('-', 1)
                if not start_str or not end_str:
                    raise ValueError(f"Invalid range format: '{part}'.")
                
                start = int(start_str)
                end = int(end_str)

                if start > end:
                    raise ValueError(f"Start of range '{start}' cannot be greater than end '{end}'.")
                if 1 <= start and end <= max_index:
                    selected_indices.update(range(start, end + 1))
                else:
                    raise ValueError(f"Range '{part}' is out of bounds (1-{max_index}).")
            except (ValueError, TypeError):
                raise ValueError(f"Invalid range format: '{part}'. Please use 'start-end'.")
        else:
            try:
                index = int(part)
                if 1 <= index <= max_index:
                    selected_indices.add(index)
                else:
                    raise ValueError(f"Index '{part}' is out of bounds (1-{max_index}).")
            except (ValueError, TypeError):
                 raise ValueError(f"Invalid number: '{part}'. Please enter a valid integer.")
    
    return selected_indices


def prompt_for_selection(video_list: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Displays a list of videos and prompts the user to select which ones to download.
    Args:
        video_list: A list of video dictionaries, each with 'title' and 'url'.
    Returns:
        A list of selected video dictionaries. Returns an empty list if no selection is made.
    """
    print("\n------------------ Videos Found ------------------")
    for i, video in enumerate(video_list, 1):
        print(f"[{i:2}] {video['title']}")
    print("--------------------------------------------------")
    
    while True:
        selection_input = input(
            "\nEnter video numbers to download (e.g., 1, 5, 8-10), or 'all': "
        ).strip().lower()
        
        if not selection_input:
            print("No input received. Please try again.")
            continue

        if selection_input == 'all':
            return video_list

        try:
            selected_indices = _parse_user_selection(selection_input, len(video_list))
            if selected_indices:
                # Sort indices to download in a predictable order
                sorted_indices = sorted(list(selected_indices))
                return [video_list[i - 1] for i in sorted_indices]
            else:
                # This case is unlikely if input is given but results in no selections
                print("No videos were selected. Please enter numbers from the list.")
        except ValueError as e:
            print(f"Error: {e}. Please try again.")

def download_videos(videos_to_download: List[Dict[str, str]], download_dir: str) -> None:
    """
    Downloads the selected videos one by one using yt-dlp.
    Args:
        videos_to_download: A list of video dictionaries to download.
        download_dir: The directory to save downloaded files.
    """
    total_videos = len(videos_to_download)
    print(f"\n--- Starting Download of {total_videos} Video(s) ---")

    for i, video in enumerate(videos_to_download, 1):
        print(f"\n[{i}/{total_videos}] Downloading: {video['title']}")
        
        try:
            # Output template for organized downloads
            output_template = os.path.join(download_dir, "%(title)s [%(id)s].%(ext)s")

            command = [
                "yt-dlp",
                "--progress",
                "-o", output_template,
                video['url']
            ]

            # Run command and stream output directly to console
            subprocess.run(command, check=True)
            
            print(f"✔ Successfully downloaded '{video['title']}'.")

        except subprocess.CalledProcessError:
            print(f"✘ Error downloading '{video['title']}'. yt-dlp returned an error.", file=sys.stderr)
        except Exception as e:
            print(f"✘ An unexpected error occurred during download of '{video['title']}': {e}", file=sys.stderr)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Exiting.")
        sys.exit(0)
