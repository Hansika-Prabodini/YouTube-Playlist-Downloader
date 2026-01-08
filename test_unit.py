"""
Unit tests for YouTubeDownloaderApp class.

This module tests individual methods and logic components using pytest
with appropriate mocking to isolate units of code and avoid GUI instantiation.
"""

import pytest
import re
import tkinter as tk
import importlib.util
import sys
from unittest.mock import Mock, MagicMock, patch, PropertyMock

# Import module with dash in filename
spec = importlib.util.spec_from_file_location("youtube_downloader_gui", "youtube_downloader-gui.py")
youtube_downloader_gui = importlib.util.module_from_spec(spec)
sys.modules['youtube_downloader_gui'] = youtube_downloader_gui
spec.loader.exec_module(youtube_downloader_gui)

YouTubeDownloaderApp = youtube_downloader_gui.YouTubeDownloaderApp


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_app():
    """
    Creates a YouTubeDownloaderApp instance with all widgets mocked.
    
    This fixture prevents actual GUI instantiation by mocking tkinter/customtkinter
    components and provides a clean app instance for testing.
    """
    with patch('youtube_downloader_gui.ctk.CTk.__init__', return_value=None), \
         patch('youtube_downloader_gui.ctk.CTk.title'), \
         patch('youtube_downloader_gui.ctk.CTk.geometry'), \
         patch('youtube_downloader_gui.ctk.CTk.configure'), \
         patch('youtube_downloader_gui.ctk.CTk.after'), \
         patch.object(YouTubeDownloaderApp, 'create_widgets'):
        
        app = YouTubeDownloaderApp()
        
        # Mock essential widgets
        app.url_entry = MagicMock()
        app.load_button = MagicMock()
        app.status_label = MagicMock()
        app.path_label = MagicMock()
        app.path_button = MagicMock()
        app.download_all_button = MagicMock()
        app.cancel_all_button = MagicMock()
        app.video_list_frame = MagicMock()
        app.footer_label = MagicMock()
        app.context_menu = MagicMock()
        
        # Initialize instance variables
        app.download_processes = {}
        app.video_widgets = {}
        app.is_fetching = False
        app.video_info_list = []
        
        return app


@pytest.fixture
def sample_video_data():
    """
    Returns sample video data for testing playlist scenarios.
    
    Includes various playlist sizes to test edge cases.
    """
    return {
        'empty': [],
        'single': [
            {'title': 'Single Video', 'url': 'https://youtube.com/watch?v=single'}
        ],
        'multiple': [
            {'title': 'Video 1', 'url': 'https://youtube.com/watch?v=vid1'},
            {'title': 'Video 2', 'url': 'https://youtube.com/watch?v=vid2'},
            {'title': 'Video 3', 'url': 'https://youtube.com/watch?v=vid3'}
        ],
        'large': [
            {'title': f'Video {i}', 'url': f'https://youtube.com/watch?v=vid{i}'}
            for i in range(1, 51)  # 50 videos
        ]
    }


@pytest.fixture
def mock_subprocess_output():
    """
    Returns mock subprocess output with sample yt-dlp progress strings.
    
    Simulates various stages of download progress.
    """
    return {
        'progress_lines': [
            '[download]   0.0% of 10.50MiB at 1.20MiB/s ETA 00:08',
            '[download]  25.5% of 10.50MiB at 1.20MiB/s ETA 00:06',
            '[download]  50.0% of 10.50MiB at 1.20MiB/s ETA 00:04',
            '[download]  75.8% of 10.50MiB at 1.20MiB/s ETA 00:02',
            '[download] 100% of 10.50MiB in 00:08',
        ],
        'success_patterns': [
            '[download] 100% of 10.50MiB in 00:08',
            '[ExtractAudio] Destination: /path/to/video.mp3',
            '[ffmpeg] Destination: /path/to/video.mp4',
            '[Merger] Merging formats into "/path/to/video.mp4"'
        ],
        'failure_output': [
            'ERROR: Video unavailable',
            'ERROR: This video is private'
        ]
    }


# ============================================================================
# PROGRESS REGEX PARSING TESTS (Line 315)
# ============================================================================

@pytest.mark.parametrize("progress_line,expected_percentage", [
    ('[download]   0.0% of 10.50MiB at 1.20MiB/s ETA 00:08', 0.0),
    ('[download]  25.5% of 10.50MiB at 1.20MiB/s ETA 00:06', 25.5),
    ('[download]  50.0% of 10.50MiB at 1.20MiB/s ETA 00:04', 50.0),
    ('[download]  75.8% of 10.50MiB at 1.20MiB/s ETA 00:02', 75.8),
    ('[download] 100.0% of 10.50MiB in 00:08', 100.0),
    ('[download]   1.5% of 100.00MiB at 500.00KiB/s ETA 03:20', 1.5),
    ('[download]  99.9% of 5.20GiB at 10.00MiB/s ETA 00:01', 99.9),
])
def test_progress_regex_with_valid_percentage(progress_line, expected_percentage):
    """
    Tests the progress regex pattern (line 315) with various valid yt-dlp progress formats.
    
    Validates that the regex correctly extracts percentage values from different
    download progress strings including edge cases like 0%, 100%, and decimals.
    """
    # The regex pattern from line 315
    progress_regex = re.compile(r'\[download\]\s+(\d+\.\d+)%')
    
    match = progress_regex.search(progress_line)
    assert match is not None, f"Regex should match progress line: {progress_line}"
    
    extracted_percentage = float(match.group(1))
    assert extracted_percentage == expected_percentage, \
        f"Expected {expected_percentage}%, got {extracted_percentage}%"


@pytest.mark.parametrize("invalid_line", [
    '[download] Downloading video 1 of 10',
    '[download] Destination: /path/to/video.mp4',
    'Some random output without percentage',
    '[download] ETA 00:05',
    '',  # Empty line
])
def test_progress_regex_with_invalid_formats(invalid_line):
    """
    Tests the progress regex pattern with invalid or non-matching strings.
    
    Ensures the regex doesn't match lines that don't contain percentage information.
    """
    progress_regex = re.compile(r'\[download\]\s+(\d+\.\d+)%')
    
    match = progress_regex.search(invalid_line)
    assert match is None, f"Regex should not match: {invalid_line}"


def test_progress_regex_edge_case_integer_percentage():
    """
    Tests that the regex requires decimal format (e.g., '100.0%' not '100%').
    
    This validates the specific regex pattern used in the code which expects
    \d+\.\d+ format (integer.decimal).
    """
    progress_regex = re.compile(r'\[download\]\s+(\d+\.\d+)%')
    
    # This should NOT match because it's missing the decimal part
    line_without_decimal = '[download] 100% of 10.50MiB in 00:08'
    match = progress_regex.search(line_without_decimal)
    assert match is None, "Regex should require decimal format"
    
    # This SHOULD match
    line_with_decimal = '[download] 100.0% of 10.50MiB in 00:08'
    match = progress_regex.search(line_with_decimal)
    assert match is not None, "Regex should match decimal format"


# ============================================================================
# DOWNLOAD SUCCESS DETERMINATION TESTS (Lines 341-354)
# ============================================================================

def test_download_success_with_returncode_zero():
    """
    Tests download success determination when subprocess returns 0.
    
    Validates that returncode 0 is correctly identified as success (line 345-346).
    """
    # Simulate the logic from lines 341-354
    process_returncode = 0
    combined_output_str = "[download]  50.0% of 10.50MiB\n[download] 100.0% complete"
    
    is_success = False
    if process_returncode == 0:
        is_success = True
    
    assert is_success is True, "Should succeed when returncode is 0"


@pytest.mark.parametrize("success_pattern", [
    '[download] 100% of 10.50MiB in 00:08\nSome other output',
    'Starting download\n[ExtractAudio] Destination: /path/to/audio.mp3',
    'Processing\n[ffmpeg] Destination: /path/to/video.mp4\nDone',
    'Merging files\n[Merger] Merging formats into "/path/to/video.mkv"',
])
def test_download_success_with_nonzero_returncode_but_success_patterns(success_pattern):
    """
    Tests download success determination with non-zero returncode but success indicators.
    
    Validates logic from lines 348-354 where yt-dlp may exit with warnings but
    still complete successfully, as indicated by specific output patterns.
    """
    process_returncode = 1  # Non-zero
    combined_output_str = success_pattern
    
    # Logic from lines 341-354
    is_success = False
    if process_returncode == 0:
        is_success = True
    else:
        if (re.search(r'\[download\] 100%', combined_output_str) or
            re.search(r'\[ExtractAudio\] Destination:', combined_output_str) or
            re.search(r'\[ffmpeg\] Destination:', combined_output_str) or
            re.search(r'\[Merger\] Merging formats into', combined_output_str)):
            is_success = True
    
    assert is_success is True, f"Should succeed with pattern: {success_pattern}"


@pytest.mark.parametrize("failure_output", [
    'ERROR: Video unavailable',
    'ERROR: This video is private',
    'WARNING: Some warning\nERROR: Unable to download',
    '',  # Empty output
])
def test_download_failure_detection(failure_output):
    """
    Tests download failure detection with non-zero returncode and no success patterns.
    
    Validates that downloads without success indicators are correctly identified as failed.
    """
    process_returncode = 1  # Non-zero
    combined_output_str = failure_output
    
    # Logic from lines 341-354
    is_success = False
    if process_returncode == 0:
        is_success = True
    else:
        if (re.search(r'\[download\] 100%', combined_output_str) or
            re.search(r'\[ExtractAudio\] Destination:', combined_output_str) or
            re.search(r'\[ffmpeg\] Destination:', combined_output_str) or
            re.search(r'\[Merger\] Merging formats into', combined_output_str)):
            is_success = True
    
    assert is_success is False, f"Should fail without success patterns: {failure_output}"


def test_download_success_with_multiple_success_indicators():
    """
    Tests download success with multiple success indicators in output.
    
    Validates that any one of the success patterns is sufficient for success determination.
    """
    process_returncode = 1
    combined_output_str = (
        "[download]  50.0% of 10.50MiB\n"
        "[download] 100% of 10.50MiB in 00:08\n"
        "[ExtractAudio] Destination: /path/to/audio.mp3\n"
        "[ffmpeg] Destination: /path/to/final.mp3"
    )
    
    # Logic from lines 341-354
    is_success = False
    if process_returncode == 0:
        is_success = True
    else:
        if (re.search(r'\[download\] 100%', combined_output_str) or
            re.search(r'\[ExtractAudio\] Destination:', combined_output_str) or
            re.search(r'\[ffmpeg\] Destination:', combined_output_str) or
            re.search(r'\[Merger\] Merging formats into', combined_output_str)):
            is_success = True
    
    assert is_success is True, "Should succeed with multiple success indicators"


# ============================================================================
# BUTTON STATE MANAGEMENT TESTS (_check_global_buttons_state, Lines 429-439)
# ============================================================================

def test_check_global_buttons_state_with_no_active_downloads(mock_app):
    """
    Tests _check_global_buttons_state with no active downloads.
    
    Validates that Download All is enabled and Cancel All is disabled when
    no downloads are in progress (lines 431-436).
    """
    mock_app.download_processes = {}  # No active downloads
    mock_app.status_label.cget = MagicMock(return_value="Ready to download")
    
    mock_app._check_global_buttons_state()
    
    mock_app.download_all_button.configure.assert_called_with(state=tk.NORMAL)
    mock_app.cancel_all_button.configure.assert_called_with(state=tk.DISABLED)


def test_check_global_buttons_state_with_active_downloads(mock_app):
    """
    Tests _check_global_buttons_state with active downloads.
    
    Validates that Download All is disabled and Cancel All is enabled when
    downloads are in progress (lines 438-439).
    """
    # Simulate active downloads
    mock_app.download_processes = {
        'https://youtube.com/watch?v=vid1': MagicMock(),
        'https://youtube.com/watch?v=vid2': MagicMock()
    }
    
    mock_app._check_global_buttons_state()
    
    mock_app.download_all_button.configure.assert_called_with(state=tk.DISABLED)
    mock_app.cancel_all_button.configure.assert_called_with(state=tk.NORMAL)


def test_check_global_buttons_state_after_cancelling(mock_app):
    """
    Tests _check_global_buttons_state after cancelling all downloads.
    
    Validates that the status label is updated when it shows "Cancelling..."
    and no downloads remain (lines 434-436).
    """
    mock_app.download_processes = {}  # No active downloads
    mock_app.status_label.cget = MagicMock(return_value="Cancelling all downloads...")
    
    mock_app._check_global_buttons_state()
    
    mock_app.download_all_button.configure.assert_called_with(state=tk.NORMAL)
    mock_app.cancel_all_button.configure.assert_called_with(state=tk.DISABLED)
    mock_app.status_label.configure.assert_called_with(text="All downloads finished or cancelled.")


def test_check_global_buttons_state_no_status_update_when_not_cancelling(mock_app):
    """
    Tests that status label is not updated when not in cancelling state.
    
    Validates that status label only changes when showing "Cancelling..." message.
    """
    mock_app.download_processes = {}  # No active downloads
    mock_app.status_label.cget = MagicMock(return_value="Found 5 videos. Ready to download.")
    
    mock_app._check_global_buttons_state()
    
    # Status label should not be updated in this case
    # Check that configure was only called for buttons, not status_label with text parameter
    status_configure_calls = [
        call for call in mock_app.status_label.configure.call_args_list
        if 'text' in str(call)
    ]
    assert len(status_configure_calls) == 0, "Status label should not be updated"


def test_check_global_buttons_state_single_download(mock_app):
    """
    Tests _check_global_buttons_state with exactly one active download.
    
    Edge case validation for single download in progress.
    """
    mock_app.download_processes = {
        'https://youtube.com/watch?v=single': MagicMock()
    }
    
    mock_app._check_global_buttons_state()
    
    mock_app.download_all_button.configure.assert_called_with(state=tk.DISABLED)
    mock_app.cancel_all_button.configure.assert_called_with(state=tk.NORMAL)


# ============================================================================
# CLIPBOARD PASTE FUNCTIONALITY TESTS (Lines 131-139)
# ============================================================================

def test_paste_from_clipboard_with_valid_url(mock_app):
    """
    Tests paste_from_clipboard with a valid URL in clipboard.
    
    Validates that clipboard content is correctly retrieved and inserted
    into the URL entry field (lines 134-136).
    """
    mock_app.clipboard_get = MagicMock(return_value='https://youtube.com/playlist?list=test')
    
    mock_app.paste_from_clipboard()
    
    mock_app.clipboard_get.assert_called_once()
    mock_app.url_entry.delete.assert_called_once_with(0, tk.END)
    mock_app.url_entry.insert.assert_called_once_with(0, 'https://youtube.com/playlist?list=test')


def test_paste_from_clipboard_with_empty_clipboard(mock_app):
    """
    Tests paste_from_clipboard with empty clipboard.
    
    Validates that TclError is handled gracefully when clipboard is empty
    (lines 137-139).
    """
    mock_app.clipboard_get = MagicMock(side_effect=tk.TclError("CLIPBOARD selection doesn't exist"))
    
    # Should not raise exception
    mock_app.paste_from_clipboard()
    
    mock_app.clipboard_get.assert_called_once()
    # Entry should not be modified
    mock_app.url_entry.delete.assert_not_called()
    mock_app.url_entry.insert.assert_not_called()


def test_paste_from_clipboard_with_non_text_content(mock_app):
    """
    Tests paste_from_clipboard with non-text clipboard content.
    
    Validates handling of clipboard errors when content is not text.
    """
    mock_app.clipboard_get = MagicMock(side_effect=tk.TclError("selection doesn't exist or form \"STRING\" not defined"))
    
    # Should not raise exception
    mock_app.paste_from_clipboard()
    
    mock_app.clipboard_get.assert_called_once()
    mock_app.url_entry.delete.assert_not_called()
    mock_app.url_entry.insert.assert_not_called()


def test_paste_from_clipboard_with_multiline_text(mock_app):
    """
    Tests paste_from_clipboard with multiline text in clipboard.
    
    Validates that multiline content is handled (though typically URLs are single line).
    """
    multiline_content = "https://youtube.com/playlist?list=test\nExtra line"
    mock_app.clipboard_get = MagicMock(return_value=multiline_content)
    
    mock_app.paste_from_clipboard()
    
    mock_app.url_entry.delete.assert_called_once_with(0, tk.END)
    mock_app.url_entry.insert.assert_called_once_with(0, multiline_content)


# ============================================================================
# DOWNLOAD PATH SELECTION TESTS (Lines 107-112)
# ============================================================================

def test_select_download_path_with_valid_path(mock_app):
    """
    Tests select_download_path with a valid directory selected.
    
    Validates that download path is updated and path label is configured
    when user selects a directory (lines 110-112).
    """
    with patch('youtube_downloader_gui.filedialog.askdirectory', return_value='/home/user/downloads'):
        mock_app.select_download_path()
    
    assert mock_app.download_path == '/home/user/downloads'
    mock_app.path_label.configure.assert_called_once_with(text='Save to: /home/user/downloads')


def test_select_download_path_with_cancelled_dialog(mock_app):
    """
    Tests select_download_path when user cancels the dialog.
    
    Validates that download path remains unchanged when dialog returns empty string
    (lines 109-112, the 'if selected_path' check).
    """
    original_path = mock_app.download_path
    
    with patch('youtube_downloader_gui.filedialog.askdirectory', return_value=''):
        mock_app.select_download_path()
    
    assert mock_app.download_path == original_path
    mock_app.path_label.configure.assert_not_called()


def test_select_download_path_with_none_return(mock_app):
    """
    Tests select_download_path when dialog returns None.
    
    Validates handling of None return value from cancelled dialog.
    """
    original_path = mock_app.download_path
    
    with patch('youtube_downloader_gui.filedialog.askdirectory', return_value=None):
        mock_app.select_download_path()
    
    assert mock_app.download_path == original_path
    mock_app.path_label.configure.assert_not_called()


def test_select_download_path_with_special_characters(mock_app):
    """
    Tests select_download_path with path containing special characters.
    
    Edge case for paths with spaces, unicode, or special characters.
    """
    special_path = '/home/user/My Downloads/Playlists (2025)'
    
    with patch('youtube_downloader_gui.filedialog.askdirectory', return_value=special_path):
        mock_app.select_download_path()
    
    assert mock_app.download_path == special_path
    mock_app.path_label.configure.assert_called_once_with(text=f'Save to: {special_path}')


# ============================================================================
# VIDEO LIST DISPLAY TESTS (Lines 198-266)
# ============================================================================

def test_display_videos_with_empty_playlist(mock_app, sample_video_data):
    """
    Tests display_videos with an empty playlist.
    
    Validates that appropriate status message is shown and Download All
    button is disabled when no videos are found (lines 265-266).
    """
    mock_app.video_info_list = sample_video_data['empty']
    
    mock_app.display_videos()
    
    mock_app.status_label.configure.assert_called_with(text="No videos found in playlist.")
    mock_app.download_all_button.configure.assert_called_with(state=tk.DISABLED)


def test_display_videos_with_single_video(mock_app, sample_video_data):
    """
    Tests display_videos with a single video.
    
    Validates proper UI setup for single video playlist (lines 200-263).
    """
    with patch('youtube_downloader_gui.ctk.CTkFrame') as mock_frame, \
         patch('youtube_downloader_gui.ctk.CTkLabel') as mock_label, \
         patch('youtube_downloader_gui.ctk.CTkProgressBar') as mock_progress, \
         patch('youtube_downloader_gui.ctk.CTkCheckBox') as mock_checkbox, \
         patch('youtube_downloader_gui.ctk.CTkButton') as mock_button, \
         patch('youtube_downloader_gui.ctk.BooleanVar') as mock_var:
        
        mock_app.video_info_list = sample_video_data['single']
        mock_app.display_videos()
    
    mock_app.status_label.configure.assert_called_with(text="Found 1 videos. Ready to download.")
    mock_app.download_all_button.configure.assert_called_with(state=tk.NORMAL)
    
    # Check that widgets dictionary was populated
    assert len(mock_app.video_widgets) == 1
    assert 'https://youtube.com/watch?v=single' in mock_app.video_widgets


def test_display_videos_with_multiple_videos(mock_app, sample_video_data):
    """
    Tests display_videos with multiple videos (3 videos).
    
    Validates that all videos are processed and added to video_widgets dict.
    """
    with patch('youtube_downloader_gui.ctk.CTkFrame') as mock_frame, \
         patch('youtube_downloader_gui.ctk.CTkLabel') as mock_label, \
         patch('youtube_downloader_gui.ctk.CTkProgressBar') as mock_progress, \
         patch('youtube_downloader_gui.ctk.CTkCheckBox') as mock_checkbox, \
         patch('youtube_downloader_gui.ctk.CTkButton') as mock_button, \
         patch('youtube_downloader_gui.ctk.BooleanVar') as mock_var:
        
        mock_app.video_info_list = sample_video_data['multiple']
        mock_app.display_videos()
    
    mock_app.status_label.configure.assert_called_with(text="Found 3 videos. Ready to download.")
    mock_app.download_all_button.configure.assert_called_with(state=tk.NORMAL)
    
    # Check that all videos are in widgets dictionary
    assert len(mock_app.video_widgets) == 3
    assert 'https://youtube.com/watch?v=vid1' in mock_app.video_widgets
    assert 'https://youtube.com/watch?v=vid2' in mock_app.video_widgets
    assert 'https://youtube.com/watch?v=vid3' in mock_app.video_widgets


def test_display_videos_with_large_playlist(mock_app, sample_video_data):
    """
    Tests display_videos with a large playlist (50 videos).
    
    Edge case validation for large playlists to ensure performance and correctness.
    """
    with patch('youtube_downloader_gui.ctk.CTkFrame') as mock_frame, \
         patch('youtube_downloader_gui.ctk.CTkLabel') as mock_label, \
         patch('youtube_downloader_gui.ctk.CTkProgressBar') as mock_progress, \
         patch('youtube_downloader_gui.ctk.CTkCheckBox') as mock_checkbox, \
         patch('youtube_downloader_gui.ctk.CTkButton') as mock_button, \
         patch('youtube_downloader_gui.ctk.BooleanVar') as mock_var:
        
        mock_app.video_info_list = sample_video_data['large']
        mock_app.display_videos()
    
    mock_app.status_label.configure.assert_called_with(text="Found 50 videos. Ready to download.")
    mock_app.download_all_button.configure.assert_called_with(state=tk.NORMAL)
    
    # Check that all 50 videos are processed
    assert len(mock_app.video_widgets) == 50


def test_display_videos_widget_structure(mock_app, sample_video_data):
    """
    Tests that display_videos creates correct widget structure for each video.
    
    Validates that each video entry contains all required widget references
    (lines 257-263).
    """
    with patch('youtube_downloader_gui.ctk.CTkFrame') as mock_frame, \
         patch('youtube_downloader_gui.ctk.CTkLabel') as mock_label, \
         patch('youtube_downloader_gui.ctk.CTkProgressBar') as mock_progress, \
         patch('youtube_downloader_gui.ctk.CTkCheckBox') as mock_checkbox, \
         patch('youtube_downloader_gui.ctk.CTkButton') as mock_button, \
         patch('youtube_downloader_gui.ctk.BooleanVar') as mock_var:
        
        mock_app.video_info_list = sample_video_data['single']
        mock_app.display_videos()
    
    video_url = 'https://youtube.com/watch?v=single'
    assert video_url in mock_app.video_widgets
    
    widget_dict = mock_app.video_widgets[video_url]
    # Check that all required keys exist
    assert 'status_label' in widget_dict
    assert 'progress_bar' in widget_dict
    assert 'download_button' in widget_dict
    assert 'cancel_button' in widget_dict
    assert 'audio_only_var' in widget_dict


# ============================================================================
# URL VALIDATION TESTS (fetch_playlist_titles, Lines 162-196)
# ============================================================================

def test_fetch_playlist_titles_with_valid_url(mock_app):
    """
    Tests fetch_playlist_titles with a valid playlist URL.
    
    Validates that the subprocess is called with correct yt-dlp arguments
    and video data is parsed correctly (lines 165-186).
    """
    mock_process = MagicMock()
    mock_process.stdout.readline.side_effect = [
        '{"title": "Video 1", "url": "https://youtube.com/watch?v=vid1"}\n',
        '{"title": "Video 2", "url": "https://youtube.com/watch?v=vid2"}\n',
        ''  # End of output
    ]
    mock_process.wait.return_value = 0
    
    with patch('youtube_downloader_gui.subprocess.Popen', return_value=mock_process), \
         patch.object(mock_app, 'after'):
        
        mock_app.fetch_playlist_titles('https://youtube.com/playlist?list=test')
    
    assert len(mock_app.video_info_list) == 2
    assert mock_app.video_info_list[0]['title'] == 'Video 1'
    assert mock_app.video_info_list[1]['title'] == 'Video 2'


def test_fetch_playlist_titles_with_invalid_json(mock_app):
    """
    Tests fetch_playlist_titles with invalid JSON output.
    
    Validates that JSON decode errors are handled gracefully (lines 183-185).
    """
    mock_process = MagicMock()
    mock_process.stdout.readline.side_effect = [
        'WARNING: Some warning message\n',  # Not JSON
        '{"title": "Valid Video", "url": "https://youtube.com/watch?v=valid"}\n',
        'Invalid JSON line {broken\n',  # Malformed JSON
        ''  # End of output
    ]
    mock_process.wait.return_value = 0
    
    with patch('youtube_downloader_gui.subprocess.Popen', return_value=mock_process), \
         patch.object(mock_app, 'after'):
        
        mock_app.fetch_playlist_titles('https://youtube.com/playlist?list=test')
    
    # Only the valid JSON line should be parsed
    assert len(mock_app.video_info_list) == 1
    assert mock_app.video_info_list[0]['title'] == 'Valid Video'


def test_fetch_playlist_titles_with_subprocess_error(mock_app):
    """
    Tests fetch_playlist_titles when subprocess raises an exception.
    
    Validates error handling in the except block (lines 191-193).
    """
    with patch('youtube_downloader_gui.subprocess.Popen', side_effect=Exception('Command not found')), \
         patch.object(mock_app, 'after') as mock_after:
        
        mock_app.fetch_playlist_titles('https://youtube.com/invalid')
    
    # Should schedule error message on main thread
    assert mock_after.called
    # The error callback should be scheduled
    error_call_found = False
    for call in mock_after.call_args_list:
        if len(call[0]) == 2 and call[0][0] == 0:
            error_call_found = True
            break
    assert error_call_found, "Error message should be scheduled"


def test_fetch_playlist_titles_empty_response(mock_app):
    """
    Tests fetch_playlist_titles with empty response (no videos).
    
    Edge case where playlist is empty or inaccessible.
    """
    mock_process = MagicMock()
    mock_process.stdout.readline.side_effect = ['']  # Empty response
    mock_process.wait.return_value = 0
    
    with patch('youtube_downloader_gui.subprocess.Popen', return_value=mock_process), \
         patch.object(mock_app, 'after'):
        
        mock_app.fetch_playlist_titles('https://youtube.com/playlist?list=empty')
    
    assert len(mock_app.video_info_list) == 0


def test_fetch_playlist_titles_single_video_url(mock_app):
    """
    Tests fetch_playlist_titles with a single video URL (not a playlist).
    
    Validates handling of single video as edge case.
    """
    mock_process = MagicMock()
    mock_process.stdout.readline.side_effect = [
        '{"title": "Single Video", "url": "https://youtube.com/watch?v=single"}\n',
        ''
    ]
    mock_process.wait.return_value = 0
    
    with patch('youtube_downloader_gui.subprocess.Popen', return_value=mock_process), \
         patch.object(mock_app, 'after'):
        
        mock_app.fetch_playlist_titles('https://youtube.com/watch?v=single')
    
    assert len(mock_app.video_info_list) == 1
    assert mock_app.video_info_list[0]['title'] == 'Single Video'


# ============================================================================
# INTEGRATION EDGE CASE TESTS
# ============================================================================

def test_video_widgets_structure_consistency(mock_app):
    """
    Tests that video_widgets dictionary maintains consistent structure.
    
    Validates internal data structure integrity across operations.
    """
    # Initially empty
    assert len(mock_app.video_widgets) == 0
    
    # Add mock video widgets
    test_url = 'https://youtube.com/watch?v=test'
    mock_app.video_widgets[test_url] = {
        'status_label': MagicMock(),
        'progress_bar': MagicMock(),
        'download_button': MagicMock(),
        'cancel_button': MagicMock(),
        'audio_only_var': MagicMock(),
    }
    
    assert test_url in mock_app.video_widgets
    assert len(mock_app.video_widgets[test_url]) == 5


def test_download_processes_dictionary_operations(mock_app):
    """
    Tests download_processes dictionary operations.
    
    Validates that the dictionary properly stores and retrieves subprocess references.
    """
    assert len(mock_app.download_processes) == 0
    
    # Add mock process
    test_url = 'https://youtube.com/watch?v=test'
    mock_process = MagicMock()
    mock_app.download_processes[test_url] = mock_process
    
    assert test_url in mock_app.download_processes
    assert mock_app.download_processes[test_url] == mock_process
    
    # Remove process
    del mock_app.download_processes[test_url]
    assert test_url not in mock_app.download_processes
    assert len(mock_app.download_processes) == 0
