import unittest
from unittest.mock import patch, MagicMock, call
import sys
import os
import json
import tkinter as tk # Required for constants like tk.NORMAL

# Add parent directory to path to import the main application
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from youtube_downloader-gui import YouTubeDownloaderApp

class TestYouTubeDownloaderGUI(unittest.TestCase):

    def setUp(self):
        # Mock customtkinter and its components
        self.patcher_ctk = patch('youtube_downloader-gui.ctk')
        self.mock_ctk = self.patcher_ctk.start()
        
        # Ensure CTk.CTk is a MagicMock instance
        self.mock_ctk.CTk = MagicMock() 
        self.mock_ctk.CTk.return_value = self.mock_ctk.CTk.return_value 
        self.mock_ctk.CTkFrame = MagicMock()
        self.mock_ctk.CTkLabel = MagicMock()
        self.mock_ctk.CTkEntry = MagicMock()
        self.mock_ctk.CTkButton = MagicMock()
        self.mock_ctk.CTkScrollableFrame = MagicMock()
        self.mock_ctk.CTkProgressBar = MagicMock()
        self.mock_ctk.CTkCheckBox = MagicMock()
        self.mock_ctk.BooleanVar = MagicMock(return_value=tk.BooleanVar())

        # Patch messagebox to prevent actual pop-ups during tests
        self.patcher_messagebox = patch('youtube_downloader-gui.messagebox')
        self.mock_messagebox = self.patcher_messagebox.start()

        # Patch threading.Thread to prevent actual threads from starting
        self.patcher_thread = patch('youtube_downloader-gui.threading.Thread')
        self.mock_thread = self.patcher_thread.start()

        # Patch subprocess.Popen to mock external command execution
        self.patcher_subprocess = patch('youtube_downloader-gui.subprocess.Popen')
        self.mock_subprocess_popen = self.patcher_subprocess.start()

        # Patch os.getcwd to control the download path
        self.patcher_os_getcwd = patch('youtube_downloader-gui.os.getcwd', return_value='/mock/download/path')
        self.mock_os_getcwd = self.patcher_os_getcwd.start()

        # Create an instance of the app - this will call __init__ and create_widgets
        # Most of the create_widgets calls will go to the mocked CTk components
        self.app = YouTubeDownloaderApp()
        self.app.after = MagicMock() # Mock the Tkinter after method
        self.app.update_idletasks = MagicMock() # Mock update_idletasks for progress bar

    def tearDown(self):
        self.patcher_ctk.stop()
        self.patcher_messagebox.stop()
        self.patcher_thread.stop()
        self.patcher_subprocess.stop()
        self.patcher_os_getcwd.stop()

    @patch('youtube_downloader-gui.subprocess.Popen')
    def test_fetch_playlist_titles_success(self, mock_popen):
        # Setup mock Popen process
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        mock_process.stdout.readline.side_effect = [
            json.dumps({'title': 'Video A', 'url': 'urlA'}) + '\n',
            json.dumps({'title': 'Video B', 'url': 'urlB'}) + '\n',
            '' # End of stream
        ]
        mock_process.wait.return_value = 0

        # Simulate calling fetch_playlist_titles
        test_url = "https://www.youtube.com/playlist?list=test_list_id"
        self.app.fetch_playlist_titles(test_url)

        # Assertions
        mock_popen.assert_called_once_with(
            ['yt-dlp', '--flat-playlist', '-j', test_url],
            stdout=MagicMock(), stderr=MagicMock(), text=True, universal_newlines=True
        )
        self.assertEqual(len(self.app.video_info_list), 2)
        self.assertEqual(self.app.video_info_list[0]['title'], 'Video A')
        self.assertEqual(self.app.video_info_list[1]['url'], 'urlB')
        
        # Verify display_videos is scheduled on the main thread
        self.app.after.assert_called_with(0, self.app.display_videos)
        self.assertFalse(self.app.is_fetching)
        self.app.load_button.configure.assert_called_with(state=tk.NORMAL)

    @patch('youtube_downloader-gui.subprocess.Popen')
    def test_fetch_playlist_titles_failure(self, mock_popen):
        # Simulate Popen raising an exception
        mock_popen.side_effect = Exception("Test error")

        test_url = "https://www.youtube.com/playlist?list=test_list_id"
        self.app.fetch_playlist_titles(test_url)

        # Assertions
        self.app.after.assert_called_once()
        # Check that the after call is to display an error message
        # We can't directly check the lambda, so we check that messagebox.showerror was called
        self.mock_messagebox.showerror.assert_called_once_with(
            "Error", "Failed to fetch playlist: Test error"
        )
        self.assertFalse(self.app.is_fetching)
        self.app.load_button.configure.assert_called_with(state=tk.NORMAL)

    @patch('youtube_downloader-gui.subprocess.Popen')
    def test_start_single_download_success(self, mock_popen):
        # Setup mock Popen process for successful download
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        mock_process.stdout.readline.side_effect = [
            '[download] 50% of 10MiB\n',
            '[download] 100% of 10MiB\n',
            '' # End of stream
        ]
        mock_process.wait.return_value = 0

        # Simulate a video being available in video_info_list
        video_url = "https://www.youtube.com/watch?v=single_video"
        video_title = "Single Test Video"
        self.app.video_info_list = [{'title': video_title, 'url': video_url}]
        
        # Setup mock widgets for the video
        mock_status_label = MagicMock()
        mock_progress_bar = MagicMock()
        mock_download_button = MagicMock()
        mock_cancel_button = MagicMock()
        mock_audio_checkbox = MagicMock()
        mock_audio_var = MagicMock(spec=tk.BooleanVar)
        mock_audio_var.get.return_value = False # Not audio only

        self.app.video_widgets[video_url] = {
            'status_label': mock_status_label,
            'progress_bar': mock_progress_bar,
            'download_button': mock_download_button,
            'cancel_button': mock_cancel_button,
            'audio_only_checkbox': mock_audio_checkbox,
            'audio_only_var': mock_audio_var
        }

        self.app.start_single_download(video_url)

        # Assertions for subprocess call
        mock_popen.assert_called_once_with(
            ['yt-dlp', '--progress', '-o', f'{self.app.download_path}/%(title)s.%(ext)s', video_url],
            stdout=MagicMock(), stderr=MagicMock(), text=True, bufsize=1, universal_newlines=True
        )

        # Assertions for GUI updates
        mock_status_label.configure.assert_any_call(text="Downloading...")
        mock_download_button.configure.assert_called_with(state=tk.DISABLED)
        mock_cancel_button.configure.assert_called_with(state=tk.NORMAL)
        mock_progress_bar.set.assert_any_call(0.5)
        mock_progress_bar.set.assert_any_call(1.0)
        mock_status_label.configure.assert_called_with(text="Download Complete!")
        mock_download_button.configure.assert_called_with(state=tk.NORMAL)
        mock_cancel_button.configure.assert_called_with(state=tk.DISABLED)

    @patch('youtube_downloader-gui.subprocess.Popen')
    def test_start_single_download_audio_only(self, mock_popen):
        # Setup mock Popen process for successful download
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        mock_process.stdout.readline.side_effect = [
            '[download] 50% of 10MiB\n',
            '[download] 100% of 10MiB\n',
            '' # End of stream
        ]
        mock_process.wait.return_value = 0

        # Simulate a video being available in video_info_list
        video_url = "https://www.youtube.com/watch?v=single_video"
        video_title = "Single Test Video"
        self.app.video_info_list = [{'title': video_title, 'url': video_url}]
        
        # Setup mock widgets for the video, with audio_only checked
        mock_status_label = MagicMock()
        mock_progress_bar = MagicMock()
        mock_download_button = MagicMock()
        mock_cancel_button = MagicMock()
        mock_audio_checkbox = MagicMock()
        mock_audio_var = MagicMock(spec=tk.BooleanVar)
        mock_audio_var.get.return_value = True # Audio only

        self.app.video_widgets[video_url] = {
            'status_label': mock_status_label,
            'progress_bar': mock_progress_bar,
            'download_button': mock_download_button,
            'cancel_button': mock_cancel_button,
            'audio_only_checkbox': mock_audio_checkbox,
            'audio_only_var': mock_audio_var
        }

        self.app.start_single_download(video_url)

        # Assertions for subprocess call (should include audio format)
        mock_popen.assert_called_once_with(
            ['yt-dlp', '-x', '--audio-format', 'mp3', '--progress', '-o', f'{self.app.download_path}/%(title)s.%(ext)s', video_url],
            stdout=MagicMock(), stderr=MagicMock(), text=True, bufsize=1, universal_newlines=True
        )

    @patch('youtube_downloader-gui.subprocess.Popen')
    def test_start_single_download_failure(self, mock_popen):
        # Setup mock Popen process for failed download
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        mock_process.stdout.readline.side_effect = [
            '[download] 50% of 10MiB\n',
            '' # End of stream
        ]
        mock_process.wait.return_value = 1 # Simulate non-zero return code (failure)

        video_url = "https://www.youtube.com/watch?v=single_video_fail"
        video_title = "Failed Test Video"
        self.app.video_info_list = [{'title': video_title, 'url': video_url}]
        
        mock_status_label = MagicMock()
        mock_progress_bar = MagicMock()
        mock_download_button = MagicMock()
        mock_cancel_button = MagicMock()
        mock_audio_checkbox = MagicMock()
        mock_audio_var = MagicMock(spec=tk.BooleanVar)
        mock_audio_var.get.return_value = False

        self.app.video_widgets[video_url] = {
            'status_label': mock_status_label,
            'progress_bar': mock_progress_bar,
            'download_button': mock_download_button,
            'cancel_button': mock_cancel_button,
            'audio_only_checkbox': mock_audio_checkbox,
            'audio_only_var': mock_audio_var
        }

        self.app.start_single_download(video_url)

        mock_status_label.configure.assert_called_with(text="Download Failed!", text_color="red")
        mock_download_button.configure.assert_called_with(state=tk.NORMAL)
        mock_cancel_button.configure.assert_called_with(state=tk.DISABLED)

    @patch('youtube_downloader-gui.threading.Thread')
    @patch('youtube_downloader-gui.subprocess.Popen')
    def test_download_all_batch_logic(self, mock_popen, mock_thread):
        # Configure mock thread to run its target immediately for testing
        mock_thread.side_effect = lambda *args, **kwargs: MagicMock(
            start=lambda: kwargs['target']() if 'target' in kwargs else None # Immediately call target
        )

        # Simulate having multiple videos in the list
        self.app.video_info_list = [
            {'title': 'Video 1', 'url': 'url1'},
            {'title': 'Video 2', 'url': 'url2'}
        ]
        
        # Need to create mock video widgets for download_all to interact with
        for video_info in self.app.video_info_list:
            video_url = video_info['url']
            mock_status_label = MagicMock()
            mock_progress_bar = MagicMock()
            mock_download_button = MagicMock()
            mock_cancel_button = MagicMock()
            mock_audio_checkbox = MagicMock()
            mock_audio_var = MagicMock(spec=tk.BooleanVar)
            mock_audio_var.get.return_value = False

            self.app.video_widgets[video_url] = {
                'status_label': mock_status_label,
                'progress_bar': mock_progress_bar,
                'download_button': mock_download_button,
                'cancel_button': mock_cancel_button,
                'audio_only_checkbox': mock_audio_checkbox,
                'audio_only_var': mock_audio_var
            }

        # Mock the Popen process for the batch download
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        mock_process.stdout.readline.side_effect = [
            '[download] 50% of 10MiB\n',
            '[download] 100% of 10MiB\n',
            '' # End of stream
        ]
        mock_process.wait.return_value = 0

        self.app.download_all()

        # Assert that threading.Thread was called with run_batch_download
        mock_thread.assert_called_once_with(target=self.app.run_batch_download)

        # Assert that subprocess.Popen was called with all URLs
        expected_command_prefix = ['yt-dlp', '--progress', '-o', f'{self.app.download_path}/%(title)s.%(ext)s']
        expected_command = expected_command_prefix + ['url1', 'url2']
        mock_popen.assert_called_once_with(
            expected_command,
            stdout=mock_popen.call_args.kwargs['stdout'], 
            stderr=mock_popen.call_args.kwargs['stderr'], 
            text=True, 
            bufsize=1, 
            universal_newlines=True
        )

        # Assert GUI updates
        self.app.status_label.configure.assert_any_call(text="Starting batch download...")
        self.app.status_label.configure.assert_any_call(text="Batch downloading: 50%")
        self.app.status_label.configure.assert_any_call(text="Batch downloading: 100%")
        self.app.status_label.configure.assert_any_call(text="Batch download completed successfully!")
        
        # Verify individual video widgets are updated
        for video_info in self.app.video_info_list:
            video_url = video_info['url']
            widgets = self.app.video_widgets[video_url]
            widgets['download_button'].configure.assert_called_with(state=tk.NORMAL)
            widgets['cancel_button'].configure.assert_called_with(state=tk.DISABLED)
            widgets['status_label'].configure.assert_called_with(text="") # Reset after batch
            widgets['progress_bar'].set.assert_called_with(0) # Reset after batch

        self.app.download_all_button.configure.assert_called_with(state=tk.NORMAL) # Should be re-enabled after batch
        self.app.cancel_all_button.configure.assert_called_with(state=tk.DISABLED) # Should be disabled after batch

    # Add a test for when audio_only is selected for a video in batch download
    @patch('youtube_downloader-gui.threading.Thread')
    @patch('youtube_downloader-gui.messagebox')
    def test_download_all_batch_mixed_audio_video(self, mock_messagebox, mock_thread):
        # Simulate having one audio-only video and one regular video
        self.app.video_info_list = [
            {'title': 'Video 1', 'url': 'url1'},
            {'title': 'Video 2', 'url': 'url2'}
        ]

        for video_info in self.app.video_info_list:
            video_url = video_info['url']
            mock_status_label = MagicMock()
            mock_progress_bar = MagicMock()
            mock_download_button = MagicMock()
            mock_cancel_button = MagicMock()
            mock_audio_checkbox = MagicMock()
            mock_audio_var = MagicMock(spec=tk.BooleanVar)
            if video_url == 'url1':
                mock_audio_var.get.return_value = True  # url1 is audio only
            else:
                mock_audio_var.get.return_value = False

            self.app.video_widgets[video_url] = {
                'status_label': mock_status_label,
                'progress_bar': mock_progress_bar,
                'download_button': mock_download_button,
                'cancel_button': mock_cancel_button,
                'audio_only_checkbox': mock_audio_checkbox,
                'audio_only_var': mock_audio_var
            }
        
        self.app.download_all()

        # Assert that a warning message box was shown
        mock_messagebox.showwarning.assert_called_once_with("Mixed Downloads", "Batch download does not support mixed video/audio formats. Please download audio-only videos individually.")
        # Assert that no batch download thread was started
        mock_thread.assert_not_called()
        # Assert that buttons are re-enabled
        self.app.download_all_button.configure.assert_called_with(state=tk.NORMAL)
        self.app.cancel_all_button.configure.assert_called_with(state=tk.DISABLED)

    @patch('youtube_downloader-gui.subprocess.Popen')
    def test_cancel_all(self, mock_popen):
        # Simulate ongoing downloads
        mock_process1 = MagicMock()
        mock_process2 = MagicMock()
        self.app.download_processes = {
            'url1': mock_process1,
            'url2': mock_process2
        }

        # Need mock widgets for the cancel logic to interact with
        mock_status_label1 = MagicMock()
        mock_progress_bar1 = MagicMock()
        mock_download_button1 = MagicMock()
        mock_cancel_button1 = MagicMock()
        mock_audio_checkbox1 = MagicMock()
        mock_audio_var1 = MagicMock(spec=tk.BooleanVar)
        mock_audio_var1.get.return_value = False

        self.app.video_widgets['url1'] = {
            'status_label': mock_status_label1,
            'progress_bar': mock_progress_bar1,
            'download_button': mock_download_button1,
            'cancel_button': mock_cancel_button1,
            'audio_only_checkbox': mock_audio_checkbox1,
            'audio_only_var': mock_audio_var1
        }
        
        mock_status_label2 = MagicMock()
        mock_progress_bar2 = MagicMock()
        mock_download_button2 = MagicMock()
        mock_cancel_button2 = MagicMock()
        mock_audio_checkbox2 = MagicMock()
        mock_audio_var2 = MagicMock(spec=tk.BooleanVar)
        mock_audio_var2.get.return_value = False

        self.app.video_widgets['url2'] = {
            'status_label': mock_status_label2,
            'progress_bar': mock_progress_bar2,
            'download_button': mock_download_button2,
            'cancel_button': mock_cancel_button2,
            'audio_only_checkbox': mock_audio_checkbox2,
            'audio_only_var': mock_audio_var2
        }


        self.app.cancel_all()

        # Assertions
        mock_process1.terminate.assert_called_once()
        mock_process2.terminate.assert_called_once()

        mock_status_label1.configure.assert_called_with(text="Cancelled", text_color="orange")
        mock_download_button1.configure.assert_called_with(state=tk.NORMAL)
        mock_cancel_button1.configure.assert_called_with(state=tk.DISABLED)

        mock_status_label2.configure.assert_called_with(text="Cancelled", text_color="orange")
        mock_download_button2.configure.assert_called_with(state=tk.NORMAL)
        mock_cancel_button2.configure.assert_called_with(state=tk.DISABLED)

        self.assertEqual(len(self.app.download_processes), 0)
        self.app.download_all_button.configure.assert_called_with(state=tk.NORMAL)
        self.app.cancel_all_button.configure.assert_called_with(state=tk.DISABLED)

if __name__ == '__main__':
    unittest.main()
