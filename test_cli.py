import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Assuming the functions are in youtube_Download-cli.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from youtube_Download-cli import fetch_playlist_info, prompt_for_selection, download_videos

class TestYoutubeDLCLI(unittest.TestCase):

    @patch('youtube_Download-cli.subprocess.Popen')
    def test_fetch_playlist_info(self, mock_popen):
        # Configure the mock Popen instance
        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        # Simulate stdout from yt-dlp
        mock_process.stdout.readline.side_effect = [
            json.dumps({'title': 'Video 1', 'url': 'url1'}),
            json.dumps({'title': 'Video 2', 'url': 'url2'}),
            '' # End of stream
        ]
        mock_process.wait.return_value = 0 # Simulate successful command execution

        url = "https://www.youtube.com/playlist?list=some_playlist_id"
        result = fetch_playlist_info(url)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['title'], 'Video 1')
        self.assertEqual(result[1]['url'], 'url2')

        # Verify that subprocess.Popen was called correctly
        mock_popen.assert_called_once_with(
            ['yt-dlp', '--flat-playlist', '-j', '--no-warnings', url],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True
        )

    @patch('builtins.input')
    def test_prompt_for_selection_all(self, mock_input):
        mock_input.return_value = 'all'
        video_list = [{'title': 'Video 1', 'url': 'url1'}, {'title': 'Video 2', 'url': 'url2'}]
        selected = prompt_for_selection(video_list)
        self.assertEqual(selected, video_list)

    @patch('builtins.input')
    def test_prompt_for_selection_single(self, mock_input):
        mock_input.return_value = '1'
        video_list = [{'title': 'Video 1', 'url': 'url1'}, {'title': 'Video 2', 'url': 'url2'}]
        selected = prompt_for_selection(video_list)
        self.assertEqual(selected, [video_list[0]])

    @patch('builtins.input')
    def test_prompt_for_selection_range(self, mock_input):
        mock_input.return_value = '1-2'
        video_list = [{'title': 'Video 1', 'url': 'url1'}, {'title': 'Video 2', 'url': 'url2'}]
        selected = prompt_for_selection(video_list)
        self.assertEqual(selected, video_list)

    @patch('youtube_Download-cli.subprocess.Popen')
    @patch('sys.stdout.write')
    def test_download_videos(self, mock_stdout_write, mock_popen):
        mock_process = MagicMock()
        mock_popen.return_value = mock_process
        mock_process.stdout.readline.side_effect = ['progress line 1\n', 'progress line 2\n', '']
        mock_process.wait.return_value = 0

        videos_to_download = [{'title': 'Video 1', 'url': 'url1'}]
        download_videos(videos_to_download)

        mock_popen.assert_called_once_with(
            ['yt-dlp', '--progress', 'url1'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        self.assertEqual(mock_stdout_write.call_count, 2) # For the progress lines

if __name__ == '__main__':
    unittest.main()
