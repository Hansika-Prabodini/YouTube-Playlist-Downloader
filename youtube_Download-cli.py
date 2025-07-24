import subprocess
import json
import sys
import os
import re

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        result = subprocess.run(
            ["yt-dlp", "--version"], 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            return True
        return False
    except FileNotFoundError:
        return False

def main():
    """Main function to run the command-line interface."""
    
    # Check if yt-dlp is installed - only do this once at startup
    if not check_dependencies():
        print("Error: yt-dlp is not installed or not in your system's PATH.")
        print("Please install it by running: pip install yt-dlp")
        sys.exit(1)

    print("============================================")
    print("= YouTube Playlist Downloader (CLI)      =")
    print("============================================")
    
    # Cache for previously fetched playlists to avoid re-fetching
    playlist_cache = {}
    
    while True:
        playlist_url = input("\nEnter YouTube Playlist URL (or 'exit' to quit): ")
        if playlist_url.lower() in ('exit', 'quit'):
            break

        # Check if we've already fetched this playlist
        if playlist_url in playlist_cache:
            print("\nUsing cached playlist info...")
            videos = playlist_cache[playlist_url]
        else:
            print("\nFetching playlist info...")
            videos = fetch_playlist_info(playlist_url)
            # Cache the playlist if it has videos
            if videos:
                playlist_cache[playlist_url] = videos

        if videos:
            selected_videos = prompt_for_selection(videos)
            if selected_videos:
                try:
                    download_videos(selected_videos)
                except KeyboardInterrupt:
                    print("\nDownload process interrupted. Returning to main menu.")
        else:
            print("Could not find any videos at that URL. Please try again.")

def fetch_playlist_info(url):
    """Fetches video titles and URLs from a playlist."""
    try:
        command = [
            "yt-dlp",
            "--flat-playlist",
            "-j",
            "--no-warnings", # Hide warnings for a cleaner output
            "--quiet",       # Further reduce unnecessary output
            url
        ]
        
        # Use subprocess.run instead of Popen for simpler handling
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False  # Don't raise exception on non-zero exit, handle it in our code
        )
        
        if result.returncode != 0:
            print(f"Error fetching playlist: {result.stderr}")
            return []
            
        video_info_list = []
        # Process lines all at once
        for line in result.stdout.splitlines():
            if not line.strip():
                continue
                
            try:
                video_json = json.loads(line)
                # Only store the fields we actually need
                if 'title' in video_json and 'url' in video_json:
                    video_info_list.append({
                        'title': video_json['title'],
                        'url': video_json['url']
                    })
            except json.JSONDecodeError:
                continue  # Skip invalid JSON lines
                
        return video_info_list

    except Exception as e:
        print(f"An error occurred while fetching info: {e}")
        return []

def prompt_for_selection(video_list):
    """Displays videos and prompts user for selection."""
    # Calculate the maximum index width for proper formatting
    max_idx_width = len(str(len(video_list)))
    
    print("\n------------------ Videos Found ------------------")
    for i, video in enumerate(video_list, 1):
        print(f"[{i:{max_idx_width}}] {video['title']}")
    print("--------------------------------------------------")
    
    while True:
        selection_input = input("\nEnter the number(s) to download (e.g., 1, 5, 8-10) or 'all': ").strip().lower()
        
        if selection_input == 'all':
            return video_list

        # More efficient selection parsing with precompiled regex patterns
        selected_indices = set()
        valid_input = True
        
        # Split by commas first, more efficient than complex regex split
        parts = [p.strip() for p in selection_input.split(',') if p.strip()]
        
        if not parts:
            print("No valid selection provided. Please try again.")
            continue
            
        # Process each part
        for part in parts:
            # Check for range format (e.g., "5-8")
            if '-' in part:
                try:
                    range_parts = part.split('-', 1)  # Split only on first hyphen
                    start = int(range_parts[0].strip())
                    end = int(range_parts[1].strip())
                    
                    # Validate range
                    if 1 <= start <= end <= len(video_list):
                        selected_indices.update(range(start, end + 1))
                    else:
                        print(f"Invalid range '{part}'. Please use numbers between 1 and {len(video_list)}.")
                        valid_input = False
                        break
                except ValueError:
                    print(f"Invalid range format '{part}'. Use numbers and a dash (e.g., 5-8).")
                    valid_input = False
                    break
            # Individual number
            else:
                try:
                    index = int(part)
                    if 1 <= index <= len(video_list):
                        selected_indices.add(index)
                    else:
                        print(f"Invalid number '{index}'. Please enter a number between 1 and {len(video_list)}.")
                        valid_input = False
                        break
                except ValueError:
                    print(f"Invalid input '{part}'. Please use numbers or 'all'.")
                    valid_input = False
                    break
        
        # Return selected videos if valid selection was made
        if valid_input and selected_indices:
            return [video_list[i-1] for i in sorted(selected_indices)]
        elif valid_input:
            print("No videos selected. Please try again.")

def download_videos(videos_to_download):
    """Downloads the selected videos."""
    total_videos = len(videos_to_download)
    
    # Ask user for batch mode if there are multiple videos
    batch_mode = False
    if total_videos > 1:
        batch_choice = input(f"\nDownload {total_videos} videos in batch mode? (y/n): ").lower()
        batch_mode = batch_choice.startswith('y')
    
    if batch_mode:
        # Download in batch mode (more efficient for multiple videos)
        print(f"\nStarting batch download of {total_videos} videos...")
        urls = [video['url'] for video in videos_to_download]
        
        try:
            # Create command for batch download
            command = [
                "yt-dlp",
                "--progress",
                "--no-simulate",
                "--no-post-overwrites",
            ] + urls  # Add all URLs at once
            
            # Use Popen to show real-time progress
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1024
            )
            
            # Process output
            try:
                for line in iter(process.stdout.readline, ''):
                    sys.stdout.write(line)
                    sys.stdout.flush()
            except KeyboardInterrupt:
                process.terminate()
                print("\nBatch download cancelled by user.")
                return
                
            process.wait()
            
            if process.returncode == 0:
                print(f"\nBatch download of {total_videos} videos completed successfully.")
            else:
                print(f"\nBatch download process exited with code {process.returncode}.")
                
        except Exception as e:
            print(f"An error occurred during batch download: {e}")
            
    else:
        # Download videos individually
        for i, video in enumerate(videos_to_download, 1):
            print(f"\n[{i}/{total_videos}] Starting download for: {video['title']}")
            
            try:
                # Create command with optimized parameters
                command = [
                    "yt-dlp", 
                    "--progress", 
                    "--no-simulate",
                    "--no-post-overwrites",
                    video['url']
                ]
                
                # Use Popen to show real-time progress with optimized buffer handling
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1024
                )
                
                # Process output more efficiently
                try:
                    for line in iter(process.stdout.readline, ''):
                        sys.stdout.write(line)
                        sys.stdout.flush()
                except KeyboardInterrupt:
                    # Handle user interruption gracefully
                    process.terminate()
                    print("\nDownload cancelled by user.")
                    if input("\nContinue with remaining videos? (y/n): ").lower() != 'y':
                        return
                    continue
                    
                process.wait()
                
                if process.returncode == 0:
                    print(f"Download of '{video['title']}' completed successfully.")
                else:
                    print(f"Download of '{video['title']}' failed with exit code {process.returncode}.")
                    
            except Exception as e:
                print(f"An error occurred during download: {e}")

if __name__ == "__main__":
    main()