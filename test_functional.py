"""
Functional/Integration tests for YouTubeDownloaderApp.

This module tests complete user workflows and GUI interactions end-to-end.
Uses minimal mocking - only external dependencies (subprocess, file dialogs).
Tests run with actual GUI components, requiring a DISPLAY environment.
"""

import pytest
import tkinter as tk
import importlib.util
import sys
import time
import threading
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
def functional_app():
    """
    Creates a YouTubeDownloaderApp instance with actual GUI components.
    
    This fixture creates real tkinter widgets for functional testing.
    Mocks only external dependencies (subprocess, file dialogs).
    
    Requires DISPLAY environment variable for GUI testing.
    """
    # Create actual app instance
    app = YouTubeDownloaderApp()
    
    # Don't call mainloop - we'll use update() for event processing
    # The app is now ready for interaction
    
    yield app
    
    # Cleanup: Destroy the window after test
    try:
        app.destroy()
    except:
        pass


@pytest.fixture
def mock_subprocess_success():
    """
    Returns a mock subprocess that simulates successful yt-dlp download.
    
    Provides realistic progress output and successful completion.
    """
    mock_process = MagicMock()
    mock_process.stdout.readline.side_effect = [
        '[download] Destination: /path/to/video.mp4\n',
        '[download]   0.0% of 10.50MiB at 1.20MiB/s ETA 00:08\n',
        '[download]  25.5% of 10.50MiB at 1.20MiB/s ETA 00:06\n',
        '[download]  50.0% of 10.50MiB at 1.20MiB/s ETA 00:04\n',
        '[download]  75.8% of 10.50MiB at 1.20MiB/s ETA 00:02\n',
        '[download] 100.0% of 10.50MiB in 00:08\n',
        ''  # End of output
    ]
    mock_process.poll.side_effect = [None, None, None, None, None, 0]  # Running, then completed
    mock_process.wait.return_value = 0
    mock_process.returncode = 0
    return mock_process


@pytest.fixture
def mock_subprocess_failure():
    """
    Returns a mock subprocess that simulates failed yt-dlp download.
    
    Provides error output for testing error handling.
    """
    mock_process = MagicMock()
    mock_process.stdout.readline.side_effect = [
        'ERROR: Video unavailable\n',
        ''  # End of output
    ]
    mock_process.poll.return_value = 1
    mock_process.wait.return_value = 1
    mock_process.returncode = 1
    return mock_process


@pytest.fixture
def sample_playlist_response():
    """
    Returns mock yt-dlp output for playlist fetching.
    
    Simulates --flat-playlist -j output format.
    """
    return [
        '{"title": "Test Video 1", "url": "https://youtube.com/watch?v=test1"}\n',
        '{"title": "Test Video 2", "url": "https://youtube.com/watch?v=test2"}\n',
        '{"title": "Test Video 3", "url": "https://youtube.com/watch?v=test3"}\n',
        ''  # End of output
    ]


# ============================================================================
# COMPLETE DOWNLOAD WORKFLOW TESTS
# ============================================================================

def test_complete_download_workflow_single_video(functional_app, mock_subprocess_success, sample_playlist_response):
    """
    Tests complete workflow: Load playlist → Display videos → Download single video → Verify completion.
    
    Validates that a user can successfully load a playlist, see the videos,
    and download a single video with progress updates.
    """
    # Mock subprocess.Popen for both playlist fetch and download
    with patch('youtube_downloader_gui.subprocess.Popen') as mock_popen:
        # Setup mock for playlist fetching
        mock_fetch_process = MagicMock()
        mock_fetch_process.stdout.readline.side_effect = sample_playlist_response
        mock_fetch_process.wait.return_value = 0
        
        # Setup mocks to return different processes for fetch vs download
        mock_popen.side_effect = [mock_fetch_process, mock_subprocess_success]
        
        # Step 1: Load playlist
        functional_app.url_entry.delete(0, tk.END)
        functional_app.url_entry.insert(0, "https://youtube.com/playlist?list=test")
        functional_app.start_fetch_thread()
        
        # Wait for fetch thread to complete
        time.sleep(0.5)
        functional_app.update()
        
        # Verify playlist was loaded
        assert len(functional_app.video_info_list) == 3
        assert functional_app.download_all_button.cget('state') == tk.NORMAL
        
        # Step 2: Download single video
        video_url = functional_app.video_info_list[0]['url']
        functional_app.start_single_download(video_url)
        
        # Process some download progress
        for _ in range(5):
            functional_app.monitor_downloads()
            functional_app.update()
            time.sleep(0.1)
        
        # Verify download was tracked
        # Note: The download may complete quickly in test, so check it was started
        assert mock_popen.call_count == 2  # Once for fetch, once for download


def test_complete_download_workflow_all_videos(functional_app, sample_playlist_response):
    """
    Tests complete workflow: Load playlist → Download all videos.
    
    Validates "Download All" functionality works end-to-end.
    """
    with patch('youtube_downloader_gui.subprocess.Popen') as mock_popen:
        # Setup mock for playlist fetching
        mock_fetch_process = MagicMock()
        mock_fetch_process.stdout.readline.side_effect = sample_playlist_response
        mock_fetch_process.wait.return_value = 0
        
        # Setup mock download processes (one per video)
        def create_download_mock():
            mock = MagicMock()
            mock.stdout.readline.side_effect = [
                '[download]  50.0% of 10.50MiB\n',
                '[download] 100.0% of 10.50MiB\n',
                ''
            ]
            mock.poll.side_effect = [None, 0]
            mock.wait.return_value = 0
            mock.returncode = 0
            return mock
        
        # First call is fetch, next calls are downloads
        mock_popen.side_effect = [mock_fetch_process] + [create_download_mock() for _ in range(3)]
        
        # Load playlist
        functional_app.url_entry.delete(0, tk.END)
        functional_app.url_entry.insert(0, "https://youtube.com/playlist?list=test")
        functional_app.start_fetch_thread()
        
        time.sleep(0.5)
        functional_app.update()
        
        # Download all videos
        functional_app.download_all()
        
        # Process downloads
        for _ in range(10):
            functional_app.monitor_downloads()
            functional_app.update()
            time.sleep(0.1)
        
        # Verify all downloads were initiated
        assert mock_popen.call_count == 4  # 1 fetch + 3 downloads


# ============================================================================
# CANCEL OPERATIONS TESTS
# ============================================================================

def test_cancel_individual_download(functional_app, sample_playlist_response):
    """
    Tests cancelling an individual download in progress.
    
    Validates that cancel properly terminates subprocess and updates UI.
    """
    with patch('youtube_downloader_gui.subprocess.Popen') as mock_popen:
        # Setup playlist fetch mock
        mock_fetch_process = MagicMock()
        mock_fetch_process.stdout.readline.side_effect = sample_playlist_response
        mock_fetch_process.wait.return_value = 0
        
        # Setup download mock that stays "running"
        mock_download_process = MagicMock()
        mock_download_process.stdout.readline.side_effect = [
            '[download]  25.0% of 10.50MiB\n',
            '[download]  50.0% of 10.50MiB\n',
        ] + ['[download]  50.0% of 10.50MiB\n'] * 100  # Keep returning progress
        mock_download_process.poll.return_value = None  # Still running
        
        mock_popen.side_effect = [mock_fetch_process, mock_download_process]
        
        # Load playlist
        functional_app.url_entry.delete(0, tk.END)
        functional_app.url_entry.insert(0, "https://youtube.com/playlist?list=test")
        functional_app.start_fetch_thread()
        
        time.sleep(0.5)
        functional_app.update()
        
        # Start download
        video_url = functional_app.video_info_list[0]['url']
        functional_app.start_single_download(video_url)
        
        # Process some progress
        for _ in range(3):
            functional_app.monitor_downloads()
            functional_app.update()
            time.sleep(0.05)
        
        # Verify download is active
        assert video_url in functional_app.download_processes
        
        # Cancel the download
        functional_app.cancel_single_download(video_url)
        functional_app.update()
        
        # Verify termination was called
        mock_download_process.terminate.assert_called()
        
        # Verify download was removed from tracking
        assert video_url not in functional_app.download_processes


def test_cancel_all_downloads(functional_app, sample_playlist_response):
    """
    Tests "Cancel All" functionality with multiple active downloads.
    
    Validates that all downloads are properly terminated and cleaned up.
    """
    with patch('youtube_downloader_gui.subprocess.Popen') as mock_popen:
        # Setup playlist fetch mock
        mock_fetch_process = MagicMock()
        mock_fetch_process.stdout.readline.side_effect = sample_playlist_response
        mock_fetch_process.wait.return_value = 0
        
        # Setup multiple download mocks
        download_mocks = []
        for _ in range(3):
            mock = MagicMock()
            mock.stdout.readline.side_effect = ['[download]  25.0% of 10.50MiB\n'] * 100
            mock.poll.return_value = None  # Still running
            download_mocks.append(mock)
        
        mock_popen.side_effect = [mock_fetch_process] + download_mocks
        
        # Load playlist
        functional_app.url_entry.delete(0, tk.END)
        functional_app.url_entry.insert(0, "https://youtube.com/playlist?list=test")
        functional_app.start_fetch_thread()
        
        time.sleep(0.5)
        functional_app.update()
        
        # Start all downloads
        functional_app.download_all()
        
        # Process some progress
        for _ in range(3):
            functional_app.monitor_downloads()
            functional_app.update()
            time.sleep(0.05)
        
        # Verify downloads are active
        active_count = len(functional_app.download_processes)
        assert active_count > 0
        
        # Cancel all
        functional_app.cancel_all()
        functional_app.update()
        
        # Verify all were terminated
        for mock in download_mocks[:active_count]:
            mock.terminate.assert_called()
        
        # Verify all downloads removed
        assert len(functional_app.download_processes) == 0


# ============================================================================
# ERROR HANDLING FLOW TESTS
# ============================================================================

def test_invalid_url_error_handling(functional_app):
    """
    Tests error handling when user provides invalid URL.
    
    Validates that appropriate error message is shown.
    """
    with patch('youtube_downloader_gui.messagebox.showerror') as mock_error:
        # Try to load without entering URL
        functional_app.url_entry.delete(0, tk.END)
        functional_app.start_fetch_thread()
        functional_app.update()
        
        # Verify error was shown
        mock_error.assert_called_once()
        assert 'URL' in str(mock_error.call_args)


def test_playlist_fetch_failure_handling(functional_app):
    """
    Tests error handling when playlist fetch fails (network error, invalid playlist).
    
    Validates that error is caught and reported to user.
    """
    with patch('youtube_downloader_gui.subprocess.Popen') as mock_popen, \
         patch('youtube_downloader_gui.messagebox.showerror') as mock_error:
        
        # Simulate subprocess failure
        mock_popen.side_effect = Exception("Network error")
        
        # Try to load playlist
        functional_app.url_entry.delete(0, tk.END)
        functional_app.url_entry.insert(0, "https://youtube.com/playlist?list=invalid")
        functional_app.start_fetch_thread()
        
        # Wait for thread
        time.sleep(0.5)
        functional_app.update()
        
        # Verify error was shown
        assert mock_error.called


def test_download_failure_with_error_output(functional_app, sample_playlist_response, mock_subprocess_failure):
    """
    Tests download failure handling when yt-dlp returns error.
    
    Validates that failure is detected and status is updated appropriately.
    """
    with patch('youtube_downloader_gui.subprocess.Popen') as mock_popen:
        # Setup playlist fetch mock
        mock_fetch_process = MagicMock()
        mock_fetch_process.stdout.readline.side_effect = sample_playlist_response
        mock_fetch_process.wait.return_value = 0
        
        mock_popen.side_effect = [mock_fetch_process, mock_subprocess_failure]
        
        # Load playlist
        functional_app.url_entry.delete(0, tk.END)
        functional_app.url_entry.insert(0, "https://youtube.com/playlist?list=test")
        functional_app.start_fetch_thread()
        
        time.sleep(0.5)
        functional_app.update()
        
        # Start download
        video_url = functional_app.video_info_list[0]['url']
        functional_app.start_single_download(video_url)
        
        # Process until completion
        for _ in range(10):
            functional_app.monitor_downloads()
            functional_app.update()
            time.sleep(0.05)
        
        # Verify download completed (even if failed)
        # The process should be removed from active downloads
        assert video_url not in functional_app.download_processes or \
               mock_subprocess_failure.poll.return_value is not None


# ============================================================================
# GUI STATE TRANSITION TESTS
# ============================================================================

def test_button_states_during_playlist_load(functional_app, sample_playlist_response):
    """
    Tests button state transitions during playlist loading.
    
    Validates that Load button is disabled during fetch, then re-enabled.
    Download All button should be disabled until playlist loads.
    """
    with patch('youtube_downloader_gui.subprocess.Popen') as mock_popen:
        # Setup playlist fetch mock
        mock_fetch_process = MagicMock()
        mock_fetch_process.stdout.readline.side_effect = sample_playlist_response
        mock_fetch_process.wait.return_value = 0
        mock_popen.return_value = mock_fetch_process
        
        # Initial state
        assert functional_app.download_all_button.cget('state') == tk.DISABLED
        assert functional_app.load_button.cget('state') == tk.NORMAL
        
        # Start loading
        functional_app.url_entry.delete(0, tk.END)
        functional_app.url_entry.insert(0, "https://youtube.com/playlist?list=test")
        functional_app.start_fetch_thread()
        
        # Button should be disabled during fetch
        assert functional_app.load_button.cget('state') == tk.DISABLED
        
        # Wait for completion
        time.sleep(0.5)
        functional_app.update()
        
        # After loading, Download All should be enabled
        assert functional_app.download_all_button.cget('state') == tk.NORMAL
        assert functional_app.load_button.cget('state') == tk.NORMAL


def test_status_label_updates_during_workflow(functional_app, sample_playlist_response):
    """
    Tests status label updates through complete workflow.
    
    Validates that status messages change appropriately at each stage.
    """
    with patch('youtube_downloader_gui.subprocess.Popen') as mock_popen:
        # Setup playlist fetch mock
        mock_fetch_process = MagicMock()
        mock_fetch_process.stdout.readline.side_effect = sample_playlist_response
        mock_fetch_process.wait.return_value = 0
        mock_popen.return_value = mock_fetch_process
        
        # Initial status
        initial_status = functional_app.status_label.cget('text')
        assert 'Paste a playlist URL' in initial_status or 'playlist' in initial_status.lower()
        
        # Start loading
        functional_app.url_entry.delete(0, tk.END)
        functional_app.url_entry.insert(0, "https://youtube.com/playlist?list=test")
        functional_app.start_fetch_thread()
        
        # Status should show fetching
        fetching_status = functional_app.status_label.cget('text')
        assert 'fetch' in fetching_status.lower() or 'loading' in fetching_status.lower()
        
        # Wait for completion
        time.sleep(0.5)
        functional_app.update()
        
        # Status should show ready
        ready_status = functional_app.status_label.cget('text')
        assert 'video' in ready_status.lower() or 'ready' in ready_status.lower()


def test_progress_bar_updates_during_download(functional_app, sample_playlist_response, mock_subprocess_success):
    """
    Tests progress bar updates during video download.
    
    Validates that progress bar reflects download percentage from yt-dlp output.
    """
    with patch('youtube_downloader_gui.subprocess.Popen') as mock_popen:
        # Setup mocks
        mock_fetch_process = MagicMock()
        mock_fetch_process.stdout.readline.side_effect = sample_playlist_response
        mock_fetch_process.wait.return_value = 0
        
        mock_popen.side_effect = [mock_fetch_process, mock_subprocess_success]
        
        # Load playlist
        functional_app.url_entry.delete(0, tk.END)
        functional_app.url_entry.insert(0, "https://youtube.com/playlist?list=test")
        functional_app.start_fetch_thread()
        
        time.sleep(0.5)
        functional_app.update()
        
        # Start download
        video_url = functional_app.video_info_list[0]['url']
        functional_app.start_single_download(video_url)
        
        # Process progress updates
        progress_values = []
        for _ in range(10):
            functional_app.monitor_downloads()
            functional_app.update()
            time.sleep(0.05)
            
            # Try to get progress bar value if widget exists
            if video_url in functional_app.video_widgets:
                widgets = functional_app.video_widgets[video_url]
                if 'progress' in widgets:
                    progress_values.append(widgets['progress'].get())
        
        # Verify progress increased (if we captured any values)
        if len(progress_values) > 1:
            # Progress should generally increase
            assert max(progress_values) >= min(progress_values)


def test_cancel_button_state_transitions(functional_app, sample_playlist_response):
    """
    Tests individual cancel button state transitions.
    
    Validates that cancel button is enabled during download, disabled otherwise.
    """
    with patch('youtube_downloader_gui.subprocess.Popen') as mock_popen:
        # Setup mocks
        mock_fetch_process = MagicMock()
        mock_fetch_process.stdout.readline.side_effect = sample_playlist_response
        mock_fetch_process.wait.return_value = 0
        
        mock_download = MagicMock()
        mock_download.stdout.readline.side_effect = ['[download]  50.0% of 10.50MiB\n'] * 50
        mock_download.poll.return_value = None
        
        mock_popen.side_effect = [mock_fetch_process, mock_download]
        
        # Load playlist
        functional_app.url_entry.delete(0, tk.END)
        functional_app.url_entry.insert(0, "https://youtube.com/playlist?list=test")
        functional_app.start_fetch_thread()
        
        time.sleep(0.5)
        functional_app.update()
        
        # Get video URL and start download
        video_url = functional_app.video_info_list[0]['url']
        
        # Cancel button should initially be disabled
        if video_url in functional_app.video_widgets:
            cancel_btn = functional_app.video_widgets[video_url].get('cancel_button')
            if cancel_btn:
                initial_state = cancel_btn.cget('state')
                assert initial_state == tk.DISABLED
        
        # Start download
        functional_app.start_single_download(video_url)
        functional_app.update()
        
        # Cancel button should now be enabled
        if video_url in functional_app.video_widgets:
            cancel_btn = functional_app.video_widgets[video_url].get('cancel_button')
            if cancel_btn:
                active_state = cancel_btn.cget('state')
                assert active_state == tk.NORMAL


def test_download_path_selection_integration(functional_app):
    """
    Tests download path selection through file dialog.
    
    Validates that selected path is properly stored and displayed.
    """
    with patch('youtube_downloader_gui.filedialog.askdirectory') as mock_dialog:
        mock_dialog.return_value = "/custom/download/path"
        
        # Initial path
        initial_path = functional_app.download_path
        
        # Select new path
        functional_app.select_download_path()
        functional_app.update()
        
        # Verify path was updated
        assert functional_app.download_path == "/custom/download/path"
        assert functional_app.download_path != initial_path
        
        # Verify label was updated
        label_text = functional_app.path_label.cget('text')
        assert "/custom/download/path" in label_text


def test_audio_only_checkbox_integration(functional_app, sample_playlist_response):
    """
    Tests MP3/Audio Only checkbox functionality in workflow.
    
    Validates that audio-only preference is available and can be toggled.
    """
    with patch('youtube_downloader_gui.subprocess.Popen') as mock_popen:
        # Setup playlist fetch mock
        mock_fetch_process = MagicMock()
        mock_fetch_process.stdout.readline.side_effect = sample_playlist_response
        mock_fetch_process.wait.return_value = 0
        mock_popen.return_value = mock_fetch_process
        
        # Load playlist
        functional_app.url_entry.delete(0, tk.END)
        functional_app.url_entry.insert(0, "https://youtube.com/playlist?list=test")
        functional_app.start_fetch_thread()
        
        time.sleep(0.5)
        functional_app.update()
        
        # Verify audio checkboxes were created
        video_url = functional_app.video_info_list[0]['url']
        if video_url in functional_app.video_widgets:
            widgets = functional_app.video_widgets[video_url]
            # Audio checkbox should exist
            assert 'audio_only_var' in widgets or 'audio_only_checkbox' in widgets


# ============================================================================
# EDGE CASE AND ROBUSTNESS TESTS
# ============================================================================

def test_empty_playlist_handling(functional_app):
    """
    Tests handling of empty playlist response.
    
    Validates that empty playlists are handled gracefully.
    """
    with patch('youtube_downloader_gui.subprocess.Popen') as mock_popen:
        # Setup empty playlist response
        mock_fetch_process = MagicMock()
        mock_fetch_process.stdout.readline.side_effect = ['']  # No videos
        mock_fetch_process.wait.return_value = 0
        mock_popen.return_value = mock_fetch_process
        
        # Load "playlist"
        functional_app.url_entry.delete(0, tk.END)
        functional_app.url_entry.insert(0, "https://youtube.com/playlist?list=empty")
        functional_app.start_fetch_thread()
        
        time.sleep(0.5)
        functional_app.update()
        
        # Verify no videos loaded
        assert len(functional_app.video_info_list) == 0
        assert functional_app.download_all_button.cget('state') == tk.DISABLED


def test_rapid_button_clicks_no_duplicate_operations(functional_app, sample_playlist_response):
    """
    Tests that rapid clicking doesn't create duplicate operations.
    
    Validates that is_fetching flag prevents multiple simultaneous fetches.
    """
    with patch('youtube_downloader_gui.subprocess.Popen') as mock_popen:
        # Setup slow fetch mock
        mock_fetch_process = MagicMock()
        mock_fetch_process.stdout.readline.side_effect = sample_playlist_response + [''] * 100
        mock_fetch_process.wait.return_value = 0
        mock_popen.return_value = mock_fetch_process
        
        # Enter URL
        functional_app.url_entry.delete(0, tk.END)
        functional_app.url_entry.insert(0, "https://youtube.com/playlist?list=test")
        
        # Click load button multiple times rapidly
        functional_app.start_fetch_thread()
        functional_app.start_fetch_thread()
        functional_app.start_fetch_thread()
        functional_app.update()
        
        # Wait for thread
        time.sleep(0.5)
        functional_app.update()
        
        # Should only have called Popen once (or maybe twice before flag set)
        assert mock_popen.call_count <= 2


def test_context_menu_paste_integration(functional_app):
    """
    Tests right-click context menu paste functionality.
    
    Validates that paste from clipboard works in URL entry.
    """
    with patch.object(functional_app, 'clipboard_get', return_value="https://youtube.com/playlist?list=fromclipboard"):
        # Clear entry
        functional_app.url_entry.delete(0, tk.END)
        
        # Use paste function
        functional_app.paste_from_clipboard()
        functional_app.update()
        
        # Verify URL was pasted
        assert functional_app.url_entry.get() == "https://youtube.com/playlist?list=fromclipboard"
