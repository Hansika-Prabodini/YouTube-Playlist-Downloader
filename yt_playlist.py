"""
YouTube Playlist Module

This module provides functionality for fetching and parsing YouTube playlist
metadata using yt-dlp. It handles all interactions with yt-dlp for retrieving
playlist information without any GUI dependencies.

Core Functions:
    - fetch_playlist_info(): Retrieve playlist metadata and video list
    - _parse_video_entry(): Extract video information from JSON
    - _build_playlist_command(): Build yt-dlp command for playlist fetching
"""

import subprocess
import json
from typing import Dict, Any, List, Optional


def _build_playlist_command(playlist_url: str) -> list:
    """
    Build yt-dlp command arguments for fetching playlist metadata.
    
    Uses --flat-playlist to fetch metadata without downloading, and -j for JSON output.
    
    Args:
        playlist_url: The URL of the playlist or video to fetch
    
    Returns:
        List of command arguments for subprocess execution
    """
    return ["yt-dlp", "--flat-playlist", "-j", playlist_url]


def _parse_video_entry(video_json: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract relevant video information from a yt-dlp JSON entry.
    
    Args:
        video_json: Raw JSON object from yt-dlp output
    
    Returns:
        Dictionary containing extracted video information, or None if parsing fails
    """
    try:
        video_info = {
            'title': video_json.get('title', 'Unknown Title'),
            'url': video_json.get('url', ''),
            'webpage_url': video_json.get('webpage_url', video_json.get('url', '')),
            'uploader': video_json.get('uploader', video_json.get('channel', 'Unknown')),
            'duration': video_json.get('duration', None)
        }
        
        # Validate that we at least have a URL
        if not video_info['url']:
            return None
            
        return video_info
    except (KeyError, TypeError):
        return None


def _extract_playlist_title(videos_data: List[Dict[str, Any]], first_json: Dict[str, Any]) -> str:
    """
    Extract playlist title from available data.
    
    Args:
        videos_data: List of parsed video entries
        first_json: First JSON object from yt-dlp (may contain playlist info)
    
    Returns:
        Playlist title or a default title
    """
    # Try to get playlist title from the first JSON entry
    playlist_title = first_json.get('playlist_title')
    
    # If no playlist title, try 'title' field (for single videos)
    if not playlist_title:
        playlist_title = first_json.get('title')
    
    # If still no title and we have videos, use first video's title
    if not playlist_title and videos_data:
        playlist_title = videos_data[0].get('title', 'Unknown Playlist')
    
    # Final fallback
    if not playlist_title:
        playlist_title = 'Unknown Playlist'
    
    return playlist_title


def fetch_playlist_info(playlist_url: str) -> Dict[str, Any]:
    """
    Fetch playlist metadata and video list from a YouTube playlist or video URL.
    
    This function executes yt-dlp with --flat-playlist and -j flags to retrieve
    playlist metadata without downloading videos. It parses the JSON output
    line-by-line and extracts video information.
    
    Args:
        playlist_url: The URL of the YouTube playlist or individual video
    
    Returns:
        Dictionary containing:
            - 'success' (bool): True if playlist was fetched successfully
            - 'title' (str): Playlist title or video title for single videos
            - 'videos' (list): List of video dictionaries with keys:
                - 'title': Video title
                - 'url': Video URL/ID
                - 'webpage_url': Full YouTube URL
                - 'uploader': Channel name
                - 'duration': Video duration in seconds (may be None)
            - 'video_count' (int): Total number of videos found
            - 'error_message' (str): Error description if success is False
    
    Example:
        >>> result = fetch_playlist_info("https://youtube.com/playlist?list=...")
        >>> if result['success']:
        ...     print(f"Playlist: {result['title']}")
        ...     print(f"Videos: {result['video_count']}")
        ...     for video in result['videos']:
        ...         print(f"  - {video['title']}")
    
    Error Handling:
        - Returns success=False for invalid URLs
        - Returns success=False for private/unavailable playlists
        - Returns success=False for network failures
        - Returns success=False if yt-dlp is not installed
    """
    if not playlist_url or not playlist_url.strip():
        return {
            'success': False,
            'title': '',
            'videos': [],
            'video_count': 0,
            'error_message': 'Invalid URL: URL cannot be empty'
        }
    
    videos_data = []
    first_json = {}
    
    try:
        # Build command
        command = _build_playlist_command(playlist_url.strip())
        
        # Execute yt-dlp
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            universal_newlines=True
        )
        
        # Parse output line by line
        for line in iter(process.stdout.readline, ''):
            if not line.strip():
                continue
            
            try:
                video_json = json.loads(line.strip())
                
                # Store first JSON for playlist metadata
                if not first_json:
                    first_json = video_json
                
                # Parse and store video entry
                video_info = _parse_video_entry(video_json)
                if video_info:
                    videos_data.append(video_info)
                    
            except json.JSONDecodeError:
                # Ignore lines that are not valid JSON (warnings, errors, etc.)
                continue
        
        # Wait for process to complete
        return_code = process.wait()
        
        # Read any error output
        stderr_output = process.stderr.read()
        
        # Check for errors
        if return_code != 0:
            # Check for common error patterns in stderr
            error_message = stderr_output.strip()
            
            if 'Private video' in error_message or 'private' in error_message.lower():
                return {
                    'success': False,
                    'title': '',
                    'videos': [],
                    'video_count': 0,
                    'error_message': 'Playlist or video is private or unavailable'
                }
            elif 'Video unavailable' in error_message or 'unavailable' in error_message.lower():
                return {
                    'success': False,
                    'title': '',
                    'videos': [],
                    'video_count': 0,
                    'error_message': 'Video or playlist is unavailable'
                }
            elif 'network' in error_message.lower() or 'connection' in error_message.lower():
                return {
                    'success': False,
                    'title': '',
                    'videos': [],
                    'video_count': 0,
                    'error_message': 'Network error: Unable to connect to YouTube'
                }
            else:
                # Generic error
                return {
                    'success': False,
                    'title': '',
                    'videos': [],
                    'video_count': 0,
                    'error_message': error_message or f'Failed to fetch playlist (exit code: {return_code})'
                }
        
        # Check if we got any videos
        if not videos_data:
            return {
                'success': False,
                'title': '',
                'videos': [],
                'video_count': 0,
                'error_message': 'No videos found in playlist or invalid URL'
            }
        
        # Extract playlist title
        playlist_title = _extract_playlist_title(videos_data, first_json)
        
        # Return success result
        return {
            'success': True,
            'title': playlist_title,
            'videos': videos_data,
            'video_count': len(videos_data),
            'error_message': ''
        }
    
    except FileNotFoundError:
        return {
            'success': False,
            'title': '',
            'videos': [],
            'video_count': 0,
            'error_message': 'yt-dlp not found. Please ensure yt-dlp is installed and in PATH.'
        }
    
    except Exception as e:
        return {
            'success': False,
            'title': '',
            'videos': [],
            'video_count': 0,
            'error_message': f'Unexpected error: {str(e)}'
        }
