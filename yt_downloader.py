"""
YouTube Downloader Module

This module provides functionality for downloading videos and audio from YouTube
using yt-dlp. It handles subprocess management, real-time progress streaming,
and download cancellation without any GUI dependencies.

Core Functions:
    - download_video(): Execute yt-dlp download with progress callbacks
    - cancel_download(): Terminate running download processes
"""

import subprocess
import os
import re
from typing import Optional, Callable, Dict, Any


def _build_ytdlp_command(
    video_url: str,
    download_path: str,
    extract_audio: bool = False
) -> list:
    """
    Build yt-dlp command arguments based on download options.
    
    Args:
        video_url: The URL of the video to download
        download_path: Directory path where the file will be saved
        extract_audio: If True, extract audio as MP3; if False, download video
    
    Returns:
        List of command arguments for subprocess execution
    """
    command = ["yt-dlp", "--progress"]
    
    # Set output template with download path
    output_template = os.path.join(download_path, "%(title)s.%(ext)s")
    command.extend(["-o", output_template])
    
    # Add format selection or audio extraction flags
    if extract_audio:
        command.extend(["--extract-audio", "--audio-format", "mp3", "--no-playlist"])
    else:
        # Use best video format with mp4 extension
        command.extend(["-f", "best[ext=mp4]"])
    
    command.append(video_url)
    return command


def download_video(
    video_url: str,
    download_path: str,
    extract_audio: bool = False,
    progress_callback: Optional[Callable[[str], None]] = None,
    cancel_check: Optional[Callable[[], bool]] = None
) -> Dict[str, Any]:
    """
    Download a video or extract audio using yt-dlp with real-time progress updates.
    
    This function executes yt-dlp in a subprocess and streams output line-by-line,
    allowing the caller to monitor progress through callbacks. It supports graceful
    cancellation and comprehensive error handling.
    
    Args:
        video_url: The URL of the video to download
        download_path: Directory path where the file will be saved
        extract_audio: If True, extract audio as MP3; if False, download video (default: False)
        progress_callback: Optional callback function that receives progress text lines
        cancel_check: Optional callback that returns True if download should be cancelled
    
    Returns:
        Dictionary containing:
            - 'success' (bool): True if download completed successfully
            - 'process' (subprocess.Popen): The subprocess handle (or None if failed to start)
            - 'error_message' (str): Error description if success is False
            - 'output' (str): Combined output from yt-dlp
    
    Example:
        >>> def on_progress(line):
        ...     print(f"Progress: {line}")
        >>> 
        >>> result = download_video(
        ...     "https://youtube.com/watch?v=...",
        ...     "/downloads",
        ...     extract_audio=True,
        ...     progress_callback=on_progress
        ... )
        >>> if result['success']:
        ...     print("Download completed!")
    """
    full_output = []
    process = None
    
    try:
        # Build command based on options
        command = _build_ytdlp_command(video_url, download_path, extract_audio)
        
        # Start subprocess
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Merge stderr into stdout
            text=True,
            bufsize=1,  # Line-buffered output
            universal_newlines=True
        )
        
        # Progress regex pattern to detect download percentage
        progress_regex = re.compile(r'\[download\]\s+(\d+(?:\.\d+)?)%')
        
        # Stream output line by line
        while True:
            # Check if caller requested cancellation
            if cancel_check and cancel_check():
                process.terminate()
                process.wait()
                return {
                    'success': False,
                    'process': process,
                    'error_message': 'Download cancelled by user',
                    'output': ''.join(full_output)
                }
            
            line = process.stdout.readline()
            if not line:  # No more output
                break
            
            full_output.append(line)
            
            # Invoke progress callback if provided
            if progress_callback:
                progress_callback(line.strip())
            
            # Check if process terminated early
            if process.poll() is not None and not line.strip():
                break
        
        # Wait for process to complete
        process.wait()
        
        # Determine success based on return code and output patterns
        combined_output = ''.join(full_output)
        is_success = _determine_success(process.returncode, combined_output)
        
        if is_success:
            return {
                'success': True,
                'process': process,
                'error_message': '',
                'output': combined_output
            }
        else:
            error_msg = combined_output.strip() or f"Unknown error (Exit Code: {process.returncode})"
            return {
                'success': False,
                'process': process,
                'error_message': error_msg,
                'output': combined_output
            }
    
    except FileNotFoundError:
        return {
            'success': False,
            'process': None,
            'error_message': 'yt-dlp not found. Please ensure yt-dlp is installed and in PATH.',
            'output': ''
        }
    
    except Exception as e:
        return {
            'success': False,
            'process': process,
            'error_message': f"Download error: {str(e)}",
            'output': ''.join(full_output)
        }


def _determine_success(return_code: int, output: str) -> bool:
    """
    Determine if download was successful based on return code and output patterns.
    
    yt-dlp may return non-zero exit codes even for successful downloads with warnings.
    This function checks for success indicators in the output.
    
    Args:
        return_code: Process return code
        output: Combined stdout/stderr output from yt-dlp
    
    Returns:
        True if download was successful, False otherwise
    """
    if return_code == 0:
        return True
    
    # Check for success indicators even with non-zero return code
    success_patterns = [
        r'\[download\] 100%',                      # Explicit 100% download
        r'\[ExtractAudio\] Destination:',          # Audio extracted successfully
        r'\[ffmpeg\] Destination:',                # ffmpeg conversion/merge completed
        r'\[Merger\] Merging formats into',        # Video/audio merge completed
        r'has already been downloaded'             # File already exists (success case)
    ]
    
    for pattern in success_patterns:
        if re.search(pattern, output):
            return True
    
    return False


def cancel_download(process_handle: subprocess.Popen) -> bool:
    """
    Terminate a running yt-dlp download process.
    
    This function sends a termination signal to the subprocess and waits
    for it to exit gracefully.
    
    Args:
        process_handle: The subprocess.Popen object returned from download_video()
    
    Returns:
        True if process was terminated successfully, False otherwise
    
    Example:
        >>> result = download_video("https://...", "/downloads")
        >>> # ... later, to cancel:
        >>> if result['process']:
        ...     cancel_download(result['process'])
    """
    if process_handle is None:
        return False
    
    try:
        if process_handle.poll() is None:  # Process is still running
            process_handle.terminate()
            # Give it a moment to terminate gracefully
            try:
                process_handle.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't terminate
                process_handle.kill()
                process_handle.wait()
        return True
    except Exception as e:
        # Process may have already terminated
        return False


if __name__ == "__main__":
    # Example usage and testing
    def progress_printer(line: str):
        """Example progress callback that prints output."""
        print(f"[PROGRESS] {line}")
    
    # Test download (commented out to avoid accidental downloads)
    # result = download_video(
    #     "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    #     os.getcwd(),
    #     extract_audio=False,
    #     progress_callback=progress_printer
    # )
    # 
    # if result['success']:
    #     print("Download completed successfully!")
    # else:
    #     print(f"Download failed: {result['error_message']}")
    
    print("yt_downloader module loaded successfully.")
    print("Use download_video() to download videos or extract audio.")
