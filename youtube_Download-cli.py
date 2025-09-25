import subprocess
import json
import sys
import os
import re

# Define the yt-dlp executable as a constant for easier modification and clarity
YT_DLP_EXEC = "yt-dlp"

def main():
    """Main function to run the command-line interface."""
    
    # Check if yt-dlp is installed
    try:
        # Run yt-dlp --version silently to check for its presence and functionality
        subprocess.run([YT_DLP_EXEC, "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (FileNotFoundError, subprocess.CalledProcessError):
        # If yt-dlp is not found or fails to run, inform the user and exit
        print(f"Error: '{YT_DLP_EXEC}' is not installed or not in your system's PATH.")
        print("Please install it by running: pip install yt-dlp")
        sys.exit(1)

    print("============================================")
    print("= YouTube Playlist Downloader (CLI)      =")
    print("============================================")
    
    while True:
        playlist_url = input("\nEnter YouTube Playlist URL (or 'exit' to quit): ")
        if playlist_url.lower() == 'exit':
            break

        print("\nFetching playlist info...")
        videos = fetch_playlist_info(playlist_url)

        if videos:
            selected_videos = prompt_for_selection(videos)
            if selected_videos:
                download_videos(selected_videos)
        else:
            print("Could not find any videos at that URL. Please try again.")

def fetch_playlist_info(url):
    """
    Fetches video titles and URLs from a playlist using yt-dlp.
    Returns a list of dicts with 'title' and 'url', or an empty list on error.
    """
    try:
        command = [
            YT_DLP_EXEC,
            "--flat-playlist",  # List all entries in a playlist without downloading info for each
            "-j",               # Output JSON format for each video entry
            "--no-warnings",    # Hide warnings for a cleaner output
            url
        ]
        
        # Popen allows reading stdout/stderr in real-time, crucial for large outputs
        # text=True and encoding='utf-8' ensure proper text handling
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8')

        video_info_list = []
        # Iterate over stdout line by line until EOF (empty string)
        for line in iter(process.stdout.readline, ''):
            if line.strip(): # Process only non-empty lines
                try:
                    video_json = json.loads(line)
                    # Extract relevant info. '--flat-playlist -j' outputs minimal data.
                    # Use .get() with fallbacks for robustness against missing keys.
                    video_info_list.append({
                        'title': video_json.get('title', 'Untitled Video'),
                        'url': video_json.get('url', video_json.get('webpage_url', '')) # 'url' might not always be direct, 'webpage_url' is a fallback
                    })
                except json.JSONDecodeError:
                    # If yt-dlp outputs non-JSON data (e.g., an error message redirected to stdout),
                    # print a warning to stderr but try to continue processing other lines.
                    print(f"Warning: Could not parse line as JSON: '{line.strip()}'", file=sys.stderr)
                except KeyError as ke:
                    # Catch cases where expected keys like 'title' or 'url' might be missing
                    print(f"Warning: Missing expected key in JSON data: {ke} for line '{line.strip()}'", file=sys.stderr)
        
        # Ensure the subprocess has finished and collect its exit code
        process.wait()

        if process.returncode != 0:
            # If yt-dlp itself failed (e.g., playlist not found, network error), report it.
            # Error messages would have been printed to stderr (redirected to stdout) already.
            print(f"Error: '{YT_DLP_EXEC}' command failed with exit code {process.returncode} while fetching info.", file=sys.stderr)
            return [] # Return empty list if yt-dlp failed

        return video_info_list

    except FileNotFoundError:
        # Although checked in main(), this provides a specific error in case of dynamic PATH issues.
        print(f"Error: '{YT_DLP_EXEC}' command not found. Please ensure it's installed and in your PATH.", file=sys.stderr)
        return []
    except Exception as e:
        # Catch any other unexpected errors during the process
        print(f"An unexpected error occurred while fetching info: {e}", file=sys.stderr)
        return []

def prompt_for_selection(video_list):
    """Displays videos and prompts user for selection."""
    print("\n------------------ Videos Found ------------------")
    for i, video in enumerate(video_list, 1):
        print(f"[{i:2}] {video['title']}")
    print("--------------------------------------------------")
    
    while True:
        selection_input = input("\nEnter the number(s) to download (e.g., 1, 5, 8-10) or 'all': ").strip().lower()
        
        if selection_input == 'all':
            return video_list

        selected_indices = set()
        
        # Parse ranges and individual numbers
        parts = re.split(r'[,\s]+', selection_input)
        
        valid_input = True
        for part in parts:
            if not part:
                continue
            
            if '-' in part:
                try:
                    start, end = map(int, part.split('-'))
                    if 1 <= start <= end <= len(video_list):
                        selected_indices.update(range(start, end + 1))
                    else:
                        print("Invalid range. Please enter valid numbers.")
                        valid_input = False
                        break
                except ValueError:
                    print("Invalid range format. Use numbers and a dash (e.g., 1-10).")
                    valid_input = False
                    break
            else:
                try:
                    index = int(part)
                    if 1 <= index <= len(video_list):
                        selected_indices.add(index)
                    else:
                        print("Invalid number. Please enter a valid number from the list.")
                        valid_input = False
                        break
                except ValueError:
                    print("Invalid input. Please use numbers or 'all'.")
                    valid_input = False
                    break
        
        if valid_input and selected_indices:
            return [video_list[i-1] for i in sorted(selected_indices)]
        else:
            if valid_input:
                print("No videos selected. Please try again.")

def download_videos(videos_to_download):
    """Downloads the selected videos."""
    for i, video in enumerate(videos_to_download, 1):
        print(f"\n[{i}/{len(videos_to_download)}] Starting download for: {video['title']}")
        
        try:
            # Construct the yt-dlp command.
            # --progress option shows a visual progress bar.
            # Additional options (e.g., output template, format selection) can be added here.
            command = [YT_DLP_EXEC, "--progress", video['url']]
            
            # Use Popen to show real-time progress by reading from stdout/stderr.
            # text=True and encoding='utf-8' for correct text output.
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8')
            
            # Read and print output line by line to display real-time progress from yt-dlp
            for line in iter(process.stdout.readline, ''):
                sys.stdout.write(line)
                sys.stdout.flush() # Ensure output is immediately written to console
            
            # Wait for the process to complete and free system resources.
            # communicate() also ensures all pipes are drained if not already fully read.
            process.communicate()
            
            if process.returncode == 0:
                print(f"Download of '{video['title']}' completed successfully.")
            else:
                # yt-dlp typically prints its own error messages, so just indicate failure.
                print(f"Download of '{video['title']}' failed with exit code {process.returncode}.", file=sys.stderr)
                
        except FileNotFoundError:
            # Provide a specific error if yt-dlp is somehow not found during download
            print(f"Error: '{YT_DLP_EXEC}' command not found. Please ensure it's installed and in your PATH.", file=sys.stderr)
            print(f"Download of '{video['title']}' failed due to missing executable.", file=sys.stderr)
        except Exception as e:
            # Catch any other unexpected errors during the download attempt
            print(f"An unexpected error occurred during download of '{video['title']}': {e}", file=sys.stderr)

if __name__ == "__main__":
    main()