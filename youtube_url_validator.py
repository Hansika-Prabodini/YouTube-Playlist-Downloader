"""
YouTube URL Validator

A security utility module for validating YouTube URLs in both CLI and GUI downloaders.
Supports multiple YouTube URL formats and provides robust edge case handling.

Author: Security Enhancement Module
Date: 2025
"""

import re
from typing import Optional


# Compile regex pattern once for performance
# This pattern matches:
# - Standard YouTube watch URLs: https://www.youtube.com/watch?v=VIDEO_ID
# - Shortened URLs: https://youtu.be/VIDEO_ID
# - Playlist URLs: https://www.youtube.com/playlist?list=PLAYLIST_ID
# - Both http and https protocols
# - Optional www subdomain
# - Query parameters (e.g., &t=123s, &index=1, &list=...)
YOUTUBE_URL_PATTERN = re.compile(
    r'^'  # Start of string
    r'(?:https?://)?'  # Optional protocol (http or https)
    r'(?:www\.)?'  # Optional www subdomain
    r'(?:'  # Start of domain group
        r'youtube\.com/'  # youtube.com domain
        r'(?:'  # Start of path group
            r'watch\?'  # watch path with query string
            r'(?=.*v=[\w-]+)'  # Positive lookahead for v= parameter with video ID
            r'[^\s]*'  # Any characters except whitespace (query parameters)
            r'|'  # OR
            r'playlist\?'  # playlist path with query string
            r'(?=.*list=[\w-]+)'  # Positive lookahead for list= parameter with playlist ID
            r'[^\s]*'  # Any characters except whitespace (query parameters)
        r')'
        r'|'  # OR
        r'youtu\.be/'  # youtu.be domain (shortened URL)
        r'[\w-]+'  # Video ID (alphanumeric, underscore, dash)
        r'(?:\?[^\s]*)?'  # Optional query parameters
    r')'
    r'$',  # End of string
    re.IGNORECASE
)


def is_valid_youtube_url(url: Optional[str]) -> bool:
    """
    Validates if a given URL is a valid YouTube URL.
    
    This function uses regex pattern matching to verify that the provided URL
    conforms to supported YouTube URL formats. It handles edge cases gracefully
    without raising exceptions.
    
    Supported URL Formats:
    ----------------------
    1. Standard watch URL:
       - https://www.youtube.com/watch?v=dQw4w9WgXcQ
       - http://youtube.com/watch?v=dQw4w9WgXcQ
       - https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s
       - https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf&index=1
    
    2. Shortened URL:
       - https://youtu.be/dQw4w9WgXcQ
       - http://youtu.be/dQw4w9WgXcQ
       - https://youtu.be/dQw4w9WgXcQ?t=42s
    
    3. Playlist URL:
       - https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf
       - http://youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf
    
    Invalid URL Examples:
    --------------------
    - Empty string: ""
    - None value: None
    - Non-YouTube domain: "https://vimeo.com/123456789"
    - Malformed YouTube URL: "youtube.com/notavalidpath"
    - Missing video ID: "https://www.youtube.com/watch?v="
    - Invalid characters: "https://www.youtube.com/watch?v=<script>"
    
    Args:
        url: The URL string to validate. Can be None or empty string.
    
    Returns:
        bool: True if the URL is a valid YouTube URL, False otherwise.
              Returns False for None, empty strings, and invalid URLs.
    
    Examples:
        >>> is_valid_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        True
        
        >>> is_valid_youtube_url("https://youtu.be/dQw4w9WgXcQ")
        True
        
        >>> is_valid_youtube_url("https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf")
        True
        
        >>> is_valid_youtube_url("")
        False
        
        >>> is_valid_youtube_url(None)
        False
        
        >>> is_valid_youtube_url("https://vimeo.com/123456789")
        False
    
    Note:
        This function does not verify if the video/playlist actually exists on
        YouTube, only that the URL format is valid.
    """
    # Handle None and non-string types
    if url is None or not isinstance(url, str):
        return False
    
    # Handle empty strings and whitespace-only strings
    url = url.strip()
    if not url:
        return False
    
    # Match against the compiled regex pattern
    return bool(YOUTUBE_URL_PATTERN.match(url))


def get_validation_error_message(url: Optional[str]) -> str:
    """
    Provides a descriptive error message for common invalid URL patterns.
    
    This function analyzes the URL and returns a user-friendly error message
    explaining why the URL is invalid.
    
    Args:
        url: The URL string to analyze.
    
    Returns:
        str: A descriptive error message, or an empty string if the URL is valid.
    
    Examples:
        >>> get_validation_error_message(None)
        'URL cannot be empty or None.'
        
        >>> get_validation_error_message("")
        'URL cannot be empty or None.'
        
        >>> get_validation_error_message("https://vimeo.com/123456789")
        'URL is not a YouTube URL. Please provide a valid YouTube link.'
        
        >>> get_validation_error_message("https://www.youtube.com/watch?v=")
        'YouTube URL is missing a video ID.'
        
        >>> get_validation_error_message("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        ''
    """
    # Check if URL is valid first
    if is_valid_youtube_url(url):
        return ""
    
    # Handle None and empty strings
    if url is None or not isinstance(url, str):
        return "URL cannot be empty or None."
    
    url = url.strip()
    if not url:
        return "URL cannot be empty or None."
    
    # Check for non-YouTube domains
    if not ('youtube.com' in url.lower() or 'youtu.be' in url.lower()):
        return "URL is not a YouTube URL. Please provide a valid YouTube link."
    
    # Check for missing video ID in watch URLs
    if 'watch?' in url and ('v=' not in url or url.endswith('v=')):
        return "YouTube URL is missing a video ID."
    
    # Check for missing playlist ID in playlist URLs
    if 'playlist?' in url and ('list=' not in url or url.endswith('list=')):
        return "YouTube playlist URL is missing a playlist ID."
    
    # Generic malformed URL message
    return "YouTube URL format is invalid. Please check the URL and try again."


# If run as a script, provide simple testing interface
if __name__ == "__main__":
    print("YouTube URL Validator - Test Suite")
    print("=" * 50)
    
    # Test cases
    test_urls = [
        # Valid URLs
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", True, "Standard watch URL"),
        ("http://youtube.com/watch?v=dQw4w9WgXcQ", True, "Watch URL without www"),
        ("https://youtu.be/dQw4w9WgXcQ", True, "Shortened URL"),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s", True, "Watch URL with timestamp"),
        ("https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf", True, "Playlist URL"),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf&index=1", True, "Watch URL with playlist"),
        ("https://youtu.be/dQw4w9WgXcQ?t=42s", True, "Shortened URL with timestamp"),
        
        # Invalid URLs
        ("", False, "Empty string"),
        (None, False, "None value"),
        ("https://vimeo.com/123456789", False, "Non-YouTube domain"),
        ("youtube.com/notavalidpath", False, "Malformed path"),
        ("https://www.youtube.com/watch?v=", False, "Missing video ID"),
        ("https://www.youtube.com/playlist?list=", False, "Missing playlist ID"),
        ("not a url at all", False, "Not a URL"),
        ("https://www.youtube.com/", False, "YouTube homepage without video"),
    ]
    
    passed = 0
    failed = 0
    
    for url, expected, description in test_urls:
        result = is_valid_youtube_url(url)
        status = "✓ PASS" if result == expected else "✗ FAIL"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"\n{status}: {description}")
        print(f"  URL: {repr(url)}")
        print(f"  Expected: {expected}, Got: {result}")
        
        if not result:
            error_msg = get_validation_error_message(url)
            if error_msg:
                print(f"  Error: {error_msg}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed out of {len(test_urls)} tests")
    
    if failed == 0:
        print("✓ All tests passed!")
    else:
        print(f"✗ {failed} test(s) failed.")
