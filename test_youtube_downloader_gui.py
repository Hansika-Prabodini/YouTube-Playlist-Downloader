import unittest
from unittest.mock import patch, Mock, MagicMock, call
import tkinter as tk
import threading
import json
import time
import os
import subprocess
from io import StringIO

# Import the application under test
import sys
import importlib.util
import os

# Load the GUI module (handles hyphenated filename)
gui_module_path = os.path.join(os.path.dirname(__file__), 'youtube_downloader-gui.py')
spec = importlib.util.spec_from_file_location("youtube_downloader_gui", gui_module_path)
gui_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gui_module)
YouTubeDownloaderApp = gui_module.YouTubeDownloaderApp


class TestYouTubeDownloaderApp(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment and initialize app instance."""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window during tests
        
        # Create app instance with mocked dependencies
        with patch('tkinter.filedialog'), patch('tkinter.messagebox'):
            self.app = YouTubeDownloaderApp(self.root)
        
        # Store original methods for cleanup
        self.original_after = self.root.after
        self.threads_created = []
    
    def tearDown(self):
        """Clean up after tests."""
        # Cancel any running downloads
        if hasattr(self.app, 'cancel_event'):
            self.app.cancel_event.set()
        
        # Wait for threads to finish
        for thread in self.threads_created:
            if thread.is_alive():
                thread.join(timeout=1)
        
        # Destroy the root window
        try:
            self.root.destroy()
        except tk.TclError:
            pass
    
    def create_sample_playlist_json(self):
        """Create sample playlist JSON data for testing."""
        return json.dumps({
            "entries": [
                {
                    "title": "Sample Video 1",
                    "id": "abc123",
                    "url": "https://www.youtube.com/watch?v=abc123",
                    "duration": 180
                },
                {
                    "title": "Sample Video 2", 
                    "id": "def456",
                    "url": "https://www.youtube.com/watch?v=def456",
                    "duration": 240
                }
            ],
            "title": "Sample Playlist"
        })
    
    def create_mock_video_info(self, index=0):
        """Create mock video info for testing."""
        videos = [
            {"title": "Sample Video 1", "id": "abc123", "duration": 180},
            {"title": "Sample Video 2", "id": "def456", "duration": 240}
        ]
        return videos[index] if index < len(videos) else videos[0]
    
    def test_widget_creation(self):
        """Test that all widgets are created and properly initialized."""
        # Check main frame exists
        self.assertIsInstance(self.app.main_frame, tk.Frame)
        
        # Check URL entry exists
        self.assertTrue(hasattr(self.app, 'url_entry'))
        
        # Check buttons exist
        self.assertTrue(hasattr(self.app, 'load_button'))
        self.assertTrue(hasattr(self.app, 'download_all_button'))
        self.assertTrue(hasattr(self.app, 'cancel_all_button'))
        
        # Check treeview exists
        self.assertTrue(hasattr(self.app, 'tree'))
        
        # Check path selection elements exist
        self.assertTrue(hasattr(self.app, 'path_entry'))
        self.assertTrue(hasattr(self.app, 'select_path_button'))
    
    @patch('tkinter.filedialog.askdirectory')
    def test_select_download_path(self, mock_askdirectory):
        """Test download path selection functionality."""
        mock_askdirectory.return_value = "/test/path"
        
        self.app.select_download_path()
        
        mock_askdirectory.assert_called_once()
        self.assertEqual(self.app.path_entry.get(), "/test/path")
    
    @patch('tkinter.filedialog.askdirectory')
    def test_select_download_path_cancelled(self, mock_askdirectory):
        """Test download path selection when user cancels."""
        mock_askdirectory.return_value = ""
        original_path = self.app.path_entry.get()
        
        self.app.select_download_path()
        
        # Path should remain unchanged
        self.assertEqual(self.app.path_entry.get(), original_path)
    
    def test_url_entry_and_load_button(self):
        """Test URL entry and load button functionality."""
        test_url = "https://www.youtube.com/playlist?list=test123"
        
        # Set URL in entry
        self.app.url_entry.delete(0, tk.END)
        self.app.url_entry.insert(0, test_url)
        
        # Verify URL was set
        self.assertEqual(self.app.url_entry.get(), test_url)
        
        # Check load button is enabled by default
        self.assertEqual(self.app.load_button['state'], 'normal')
    
    def test_context_menu_operations(self):
        """Test context menu creation and operations."""
        # Create a mock event
        event = Mock()
        event.x_root = 100
        event.y_root = 100
        
        # Test context menu creation
        with patch.object(self.app, 'tree') as mock_tree:
            mock_tree.identify_row.return_value = "item1"
            mock_tree.item.return_value = {"values": ("Title", "ID", "Duration")}
            
            # This should not raise an exception
            try:
                self.app.show_context_menu(event)
            except tk.TclError:
                pass  # Expected in test environment
    
    @patch('tkinter.Tk.clipboard_get')
    def test_paste_from_clipboard(self, mock_clipboard_get):
        """Test clipboard paste functionality."""
        test_url = "https://www.youtube.com/playlist?list=test123"
        mock_clipboard_get.return_value = test_url
        
        self.app.paste_from_clipboard()
        
        self.assertEqual(self.app.url_entry.get(), test_url)
    
    @patch('tkinter.Tk.clipboard_get')
    def test_paste_from_clipboard_error(self, mock_clipboard_get):
        """Test clipboard paste error handling."""
        mock_clipboard_get.side_effect = tk.TclError("No clipboard data")
        
        # Should not raise exception
        self.app.paste_from_clipboard()
    
    @patch('subprocess.Popen')
    def test_fetch_playlist_titles_success(self, mock_popen):
        """Test successful playlist fetching."""
        mock_process = Mock()
        mock_process.communicate.return_value = (self.create_sample_playlist_json(), "")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        self.app.url_entry.insert(0, "https://www.youtube.com/playlist?list=test123")
        
        # Mock the display_videos method
        with patch.object(self.app, 'display_videos') as mock_display:
            self.app.fetch_playlist_titles()
            
            # Wait a bit for thread to execute
            time.sleep(0.1)
            
            mock_popen.assert_called_once()
            mock_display.assert_called_once()
    
    @patch('subprocess.Popen')
    @patch('tkinter.messagebox.showerror')
    def test_fetch_playlist_titles_error(self, mock_showerror, mock_popen):
        """Test playlist fetching error handling."""
        mock_process = Mock()
        mock_process.communicate.return_value = ("", "Error message")
        mock_process.returncode = 1
        mock_popen.return_value = mock_process
        
        self.app.url_entry.insert(0, "invalid_url")
        self.app.fetch_playlist_titles()
        
        # Wait a bit for thread to execute
        time.sleep(0.1)
        
        mock_showerror.assert_called_once()
    
    def test_display_videos(self):
        """Test video display functionality."""
        sample_data = json.loads(self.create_sample_playlist_json())
        
        # Clear existing items
        for item in self.app.tree.get_children():
            self.app.tree.delete(item)
        
        self.app.display_videos(sample_data)
        
        # Check that videos were added to treeview
        items = self.app.tree.get_children()
        self.assertEqual(len(items), 2)
        
        # Check first item
        item_values = self.app.tree.item(items[0])['values']
        self.assertEqual(item_values[0], "Sample Video 1")
        self.assertEqual(item_values[1], "abc123")
    
    @patch('threading.Thread')
    def test_start_single_download(self, mock_thread):
        """Test single video download initiation."""
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance
        
        video_info = self.create_mock_video_info()
        
        self.app.start_single_download(video_info, audio_only=False)
        
        # Check thread was created and started
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()
    
    @patch('subprocess.Popen')
    def test_run_download_success(self, mock_popen):
        """Test download process execution."""
        mock_process = Mock()
        mock_process.poll.return_value = None
        mock_process.stdout.readline.side_effect = [
            b"[download] 50.0% of 10.0MiB",
            b"[download] 100% of 10.0MiB",
            b""
        ]
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process
        
        video_info = self.create_mock_video_info()
        
        # Mock progress bar update
        with patch.object(self.app.root, 'after'):
            result = self.app.run_download(video_info, "/test/path", False)
            
            self.assertTrue(result)
    
    @patch('subprocess.Popen')
    def test_run_download_failure(self, mock_popen):
        """Test download process failure handling."""
        mock_process = Mock()
        mock_process.poll.return_value = None
        mock_process.stdout.readline.return_value = b""
        mock_process.wait.return_value = 1
        mock_popen.return_value = mock_process
        
        video_info = self.create_mock_video_info()
        
        result = self.app.run_download(video_info, "/test/path", False)
        
        self.assertFalse(result)
    
    def test_download_all_functionality(self):
        """Test download all videos functionality."""
        sample_data = json.loads(self.create_sample_playlist_json())
        self.app.display_videos(sample_data)
        
        with patch.object(self.app, 'start_single_download') as mock_start:
            self.app.download_all()
            
            # Should start downloads for all videos
            self.assertEqual(mock_start.call_count, 2)
    
    def test_cancel_single_download(self):
        """Test single download cancellation."""
        video_id = "abc123"
        
        # Add a mock process to active downloads
        mock_process = Mock()
        self.app.active_downloads[video_id] = mock_process
        
        self.app.cancel_single_download(video_id)
        
        # Process should be terminated
        mock_process.terminate.assert_called_once()
        
        # Should be removed from active downloads
        self.assertNotIn(video_id, self.app.active_downloads)
    
    def test_cancel_all_downloads(self):
        """Test cancel all downloads functionality."""
        # Add mock processes to active downloads
        video_ids = ["abc123", "def456"]
        mock_processes = []
        
        for vid_id in video_ids:
            mock_process = Mock()
            mock_processes.append(mock_process)
            self.app.active_downloads[vid_id] = mock_process
        
        self.app.cancel_all()
        
        # All processes should be terminated
        for mock_process in mock_processes:
            mock_process.terminate.assert_called_once()
        
        # Active downloads should be cleared
        self.assertEqual(len(self.app.active_downloads), 0)
    
    def test_monitor_downloads(self):
        """Test download monitoring and button state management."""
        # Add some active downloads
        self.app.active_downloads["abc123"] = Mock()
        self.app.active_downloads["def456"] = Mock()
        
        # Monitor should detect active downloads
        with patch.object(self.app.root, 'after') as mock_after:
            self.app.monitor_downloads()
            
            # Should schedule next monitor call
            mock_after.assert_called_once()
    
    def test_audio_only_download(self):
        """Test audio-only download option."""
        video_info = self.create_mock_video_info()
        
        with patch('threading.Thread') as mock_thread:
            self.app.start_single_download(video_info, audio_only=True)
            
            # Thread should be created with audio_only=True
            mock_thread.assert_called_once()
            args, kwargs = mock_thread.call_args
            self.assertTrue(args[2])  # audio_only parameter
    
    def test_progress_bar_updates(self):
        """Test progress bar updates during downloads."""
        video_id = "abc123"
        progress_value = 50
        
        # Mock progress bar
        mock_progress_bar = Mock()
        self.app.progress_bars[video_id] = mock_progress_bar
        
        self.app.update_progress_bar(video_id, progress_value)
        
        mock_progress_bar.set.assert_called_once_with(progress_value / 100)
    
    def test_status_label_updates(self):
        """Test status label updates during downloads."""
        video_id = "abc123"
        status = "Downloading..."
        
        # Mock status label
        mock_status_label = Mock()
        self.app.status_labels[video_id] = mock_status_label
        
        self.app.update_status_label(video_id, status)
        
        mock_status_label.configure.assert_called_once_with(text=status)
    
    def test_empty_playlist_handling(self):
        """Test handling of empty playlists."""
        empty_playlist = {"entries": [], "title": "Empty Playlist"}
        
        self.app.display_videos(empty_playlist)
        
        # Tree should be empty
        items = self.app.tree.get_children()
        self.assertEqual(len(items), 0)
    
    def test_invalid_json_handling(self):
        """Test handling of invalid JSON responses."""
        with patch('tkinter.messagebox.showerror') as mock_showerror:
            self.app.display_videos("invalid json")
            
            mock_showerror.assert_called_once()
    
    @patch('subprocess.Popen')
    def test_integration_workflow(self, mock_popen):
        """Test complete workflow from URL input to download completion."""
        # Mock successful playlist fetch
        mock_process = Mock()
        mock_process.communicate.return_value = (self.create_sample_playlist_json(), "")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        # Set URL
        test_url = "https://www.youtube.com/playlist?list=test123"
        self.app.url_entry.insert(0, test_url)
        
        # Set download path
        self.app.path_entry.delete(0, tk.END)
        self.app.path_entry.insert(0, "/test/downloads")
        
        # Fetch playlist
        with patch.object(self.app, 'display_videos') as mock_display:
            self.app.fetch_playlist_titles()
            time.sleep(0.1)  # Wait for thread
            
            mock_display.assert_called_once()
        
        # Simulate successful video display
        sample_data = json.loads(self.create_sample_playlist_json())
        self.app.display_videos(sample_data)
        
        # Verify videos are displayed
        items = self.app.tree.get_children()
        self.assertEqual(len(items), 2)


if __name__ == '__main__':
    unittest.main()
