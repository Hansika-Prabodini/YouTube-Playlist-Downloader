import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import customtkinter as ctk
import subprocess
import threading
import json
import os
import sys
import re
import time # Added import for time module

# Main application class
class YouTubeDownloaderApp(ctk.CTk):
    """Main application class for the YouTube Playlist Downloader GUI."""
    def __init__(self):
        """Initializes the application window, variables, and starts monitoring thread."""
        super().__init__()

        # --- Window Configuration ---
        self.title("Nuwan's Playlist Downloader")
        self.geometry("800x600")
        self.configure(bg="#f0f0f0")
        
        # --- Variables ---
        self.download_processes = {} # Stores active subprocesses (video_url: subprocess.Popen object)
        self.video_widgets = {}      # Stores references to widgets for each video (video_url: dict of widgets)
        self.is_fetching = False     # Flag to prevent multiple fetch operations
        self.download_path = os.getcwd() # Set default download path to current directory
        self.title_to_url_map = {} # Added to map video titles to URLs for batch processing

        # --- GUI Elements ---
        self.create_widgets()

        # --- Start monitoring downloads ---
        # This function will periodically check the status of all active downloads
        self.after(100, self.monitor_downloads)

    def create_widgets(self):
        """Creates and lays out all the widgets (UI elements) in the main window."""
        # Header Frame: Contains URL input and Load button
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=10, fill=tk.X)

        ctk.CTkLabel(header_frame, text="Playlist URL:", font=("Arial", 14)).pack(side=tk.LEFT, padx=5)

        self.url_entry = ctk.CTkEntry(header_frame, width=500)
        self.url_entry.pack(side=tk.LEFT, padx=5, expand=True)

        self.load_button = ctk.CTkButton(
            header_frame,
            text="Load Playlist",
            command=self.start_fetch_thread,
            font=("Arial", 12, "bold")
        )
        self.load_button.pack(side=tk.LEFT, padx=5)

        # Download Path Selector Frame: Contains path label and change folder button
        path_frame = ctk.CTkFrame(self, fg_color="transparent")
        path_frame.pack(pady=5, fill=tk.X, padx=10)
        
        self.path_label = ctk.CTkLabel(path_frame, text=f"Save to: {self.download_path}", font=("Arial", 10), text_color="gray")
        self.path_label.pack(side=tk.LEFT, padx=5, expand=True)
        
        self.path_button = ctk.CTkButton(
            path_frame,
            text="Change Folder",
            command=self.select_download_path,
            font=("Arial", 10, "bold"),
            width=120
        )
        self.path_button.pack(side=tk.LEFT, padx=5)

        # Status Label: Displays general application status (e.g., fetching, ready, error)
        self.status_label = ctk.CTkLabel(self, text="Paste a playlist URL and click 'Load Playlist'.", font=("Arial", 12))
        self.status_label.pack(pady=10)

        # Video List Frame (Scrollable): Holds individual video entries
        self.video_list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.video_list_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Control Buttons Frame: Contains Download All and Cancel All buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=10)

        self.download_all_button = ctk.CTkButton(
            button_frame,
            text="Download All",
            command=self.download_all,
            state=tk.DISABLED,
            font=("Arial", 12, "bold")
        )
        self.download_all_button.pack(side=tk.LEFT, padx=10)

        self.cancel_all_button = ctk.CTkButton(
            button_frame,
            text="Cancel All",
            command=self.cancel_all,
            state=tk.DISABLED,
            fg_color="red",
            hover_color="#c70000",
            font=("Arial", 12, "bold")
        )
        self.cancel_all_button.pack(side=tk.LEFT, padx=10)

        # Footer: Copyright information
        self.footer_label = ctk.CTkLabel(self, text="Nuwan Kaushalya © 2025", text_color="gray")
        self.footer_label.pack(side=tk.BOTTOM, pady=5)
        
        # Initialize right-click context menu for URL entry
        self.create_context_menu()

    def select_download_path(self):
        """Opens a file dialog to select the download directory."""
        selected_path = filedialog.askdirectory()
        if selected_path:
            self.download_path = selected_path
            self.path_label.configure(text=f"Save to: {self.download_path}")

    def create_context_menu(self):
        """Creates and binds the right-click context menu for the URL entry field."""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Cut", command=lambda: self.url_entry.event_generate("<<Cut>>"))
        self.context_menu.add_command(label="Copy", command=lambda: self.url_entry.event_generate("<<Copy>>"))
        self.context_menu.add_command(label="Paste", command=self.paste_from_clipboard)

        # Bind the right-click event to the URL entry widget
        self.url_entry.bind("<Button-3>", self.show_context_menu)
    def show_context_menu(self, event):
        """Displays the context menu at the mouse cursor position on right-click event."""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    def paste_from_clipboard(self):
        """Gets content from the clipboard and pastes it into the URL entry field."""
        try:
            clipboard_content = self.clipboard_get()
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, clipboard_content)
        except tk.TclError:
            # Handle cases where clipboard is empty or non-text content
            pass
    def start_fetch_thread(self):
        """Initiates fetching playlist titles in a separate thread."""
        if self.is_fetching:
            return
        
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a URL.")
            return

        self.is_fetching = True
        self.load_button.configure(state=tk.DISABLED)
        self.status_label.configure(text="Fetching playlist titles...")
        
        # Clear previous video widgets and free memory
        for widget in self.video_list_frame.winfo_children():
            widget.destroy()
        self.video_widgets.clear()
        self.download_processes.clear()

        fetch_thread = threading.Thread(target=self.fetch_playlist_titles, args=(url,))
        fetch_thread.start()

    def fetch_playlist_titles(self, url):
        """Fetches video titles and URLs from the provided playlist URL using yt-dlp in flat-list mode.
        Parses JSON output line-by-line to build the video info list."""
        try:
            command = ["yt-dlp", "--flat-playlist", "-j", url]
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True
            )
            self.video_info_list = []
            # Use faster JSON parsing with error handling
            decoder = json.JSONDecoder()
            buffer = ""
            for line in iter(process.stdout.readline, ''):
                buffer += line
                try:
                    while buffer:
                        video_json, idx = decoder.raw_decode(buffer)
                        self.video_info_list.append({
                            'title': video_json['title'],
                            'url': video_json['url']
                        })
                        buffer = buffer[idx:].lstrip()
                except (json.JSONDecodeError, ValueError):
                    continue  # Wait for more complete JSON data
            process.wait()

            # Schedule display_videos to run on the main Tkinter thread
            self.after(0, self.display_videos)

        except Exception as e:
            # Schedule error message to run on the main Tkinter thread
            self.after(0, lambda error_msg=e: messagebox.showerror("Error", f"Failed to fetch playlist: {error_msg}"))
        finally:
            self.is_fetching = False
            self.load_button.configure(state=tk.NORMAL)

    def display_videos(self):
        """Displays fetched video titles with download options."""
        if self.video_info_list:
            self.status_label.configure(text=f"Found {len(self.video_info_list)} videos. Ready to download.")
            self.download_all_button.configure(state=tk.NORMAL)
            
            for video_info in self.video_info_list:
                video_url = video_info['url']
                
                # Frame for each video row
                row_frame = ctk.CTkFrame(self.video_list_frame, fg_color="transparent")
                row_frame.pack(fill=tk.X, pady=2, padx=5)

                # Video Title Label
                ctk.CTkLabel(row_frame, text=video_info['title'], anchor="w", font=("Arial", 12)).pack(side=tk.LEFT, padx=5, expand=True)

                # Status Label for individual video download
                status_label = ctk.CTkLabel(row_frame, text="", fg_color="transparent", font=("Arial", 10))
                status_label.pack(side=tk.LEFT, padx=5)
                
                # Progress Bar for individual video download
                progress_bar = ctk.CTkProgressBar(row_frame, orientation="horizontal", width=150)
                progress_bar.set(0)
                progress_bar.pack(side=tk.LEFT, padx=5)

                # Audio Only Checkbox for each video
                audio_only_video_var = ctk.BooleanVar(value=False)
                audio_only_checkbox = ctk.CTkCheckBox(
                    row_frame,
                    text="MP3", # Shorter text for individual checkbox
                    variable=audio_only_video_var,
                    font=("Arial", 9)
                )
                audio_only_checkbox.pack(side=tk.LEFT, padx=5)

                # Download button for individual video
                download_button = ctk.CTkButton(
                    row_frame,
                    text="Download",
                    command=lambda url=video_url: self.start_single_download(url),
                    font=("Arial", 12, "bold"),
                    width=100
                )
                download_button.pack(side=tk.RIGHT, padx=5)

                # Cancel button for individual video
                cancel_button = ctk.CTkButton(
                    row_frame,
                    text="Cancel",
                    command=lambda url=video_url: self.cancel_single_download(url),
                    state=tk.DISABLED,
                    fg_color="red",
                    hover_color="#c70000",
                    width=60,
                    font=("Arial", 10, "bold")
                )
                cancel_button.pack(side=tk.RIGHT, padx=5)
                
                # Store only necessary widget references to reduce memory
                self.video_widgets[video_url] = {
                    'progress_bar': progress_bar,
                    'status_label': status_label,
                    'audio_only_var': audio_only_video_var,
                    # Store button states directly instead of widget references
                    'download_state': tk.NORMAL,
                    'cancel_state': tk.DISABLED
                }
                # Configure button commands to use lambda with stored URL
                download_button.configure(
                    command=lambda url=video_url: self.start_single_download(url)
                cancel_button.configure(
                    command=lambda url=video_url: self.cancel_single_download(url))
        else:
            self.status_label.configure(text="No videos found in playlist.")
            self.download_all_button.configure(state=tk.DISABLED)

    def start_single_download(self, video_url):
        """Prepares and starts the download of a single video in a new thread."""
        if video_url in self.download_processes: # Prevent double-clicking
            return
        
        # Disable global download all and enable global cancel all
        self.download_all_button.configure(state=tk.DISABLED)
        self.cancel_all_button.configure(state=tk.NORMAL)
        
        widgets = self.video_widgets[video_url]
        widgets['download_button'].configure(state=tk.DISABLED)
        widgets['cancel_button'].configure(state=tk.NORMAL) # Enable cancel button
        widgets['status_label'].configure(text="Starting...")

        download_thread = threading.Thread(target=self.run_download, args=(video_url,))
        download_thread.start()

    def run_download(self, video_url):
        """Executes the yt-dlp command for a single video."""
        widgets = self.video_widgets[video_url]
        full_output = [] # To store all lines from yt-dlp for final analysis
        
        try:
            # Base command arguments
            command = ["yt-dlp", "--progress"]
            
            # Add output template with selected path
            output_template = os.path.join(self.download_path, "%(title)s.%(ext)s")
            command.extend(["-o", output_template])

            # Check if audio-only is selected for THIS video
            if widgets['audio_only_var'].get():
                command.extend(["--extract-audio", "--audio-format", "mp3", "--no-playlist"])
            
            command.append(video_url) # Add the video URL last

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, # Merge stdout and stderr for simpler parsing
                text=True,
                bufsize=1, # Line-buffered output
                universal_newlines=True
            )
            self.download_processes[video_url] = process
            
            # Read output in a loop to update progress
            progress_regex = re.compile(r'\[download\]\s+(\d+\.\d+)%')
            
            # Buffer updates to reduce GUI refreshes
            last_update_time = 0
            update_interval = 0.2  # seconds between GUI updates
            
            while True:
                line = process.stdout.readline()
                if not line:  # No more output
                    break
                
                # Only store last few lines to reduce memory usage
                if len(full_output) >= 20:
                    full_output.pop(0)
                full_output.append(line)

                current_time = time.time()
                if current_time - last_update_time >= update_interval:
                    match = progress_regex.search(line)
                    if match:
                        try:
                            percentage = float(match.group(1)) / 100.0
                            widgets['progress_bar'].set(percentage)
                            widgets['status_label'].configure(text=line.strip())
                        except (ValueError, IndexError):
                            widgets['status_label'].configure(text=line.strip())
                    last_update_time = current_time

                if process.poll() is not None and not line.strip():
                    break
            
            process.wait() # Wait for the subprocess to truly complete

            # --- FINAL STATUS DETERMINATION ---
            is_success = False
            combined_output_str = "".join(full_output)

            if process.returncode == 0:
                is_success = True
            else:
                # Even if returncode is non-zero, check for success indicators in output
                # This handles cases where yt-dlp exits with warnings but completes successfully
                if (re.search(r'\[download\] 100%', combined_output_str) or # Explicit 100% download
                    re.search(r'\[ExtractAudio\] Destination:', combined_output_str) or # Audio extracted
                    re.search(r'\[ffmpeg\] Destination:', combined_output_str) or     # ffmpeg conversion/merge
                    re.search(r'\[Merger\] Merging formats into', combined_output_str)): # Video/audio merged
                    is_success = True
            
            # Update UI on the main thread based on final determination
            if is_success:
                self.after(0, lambda: widgets['status_label'].configure(text="Download Completed!"))
                self.after(0, lambda: widgets['progress_bar'].set(1.0)) # Ensure 100%
            else:
                error_message = combined_output_str.strip()
                if not error_message: # Fallback if output is empty
                    error_message = f"Unknown error (Exit Code: {process.returncode})"
                self.after(0, lambda e_msg=error_message: widgets['status_label'].configure(text=f"Download Failed! {e_msg}"))
                self.after(0, lambda: widgets['progress_bar'].set(0)) # Reset or show failed state

        except Exception as e:
            self.after(0, lambda error_msg=e: widgets['status_label'].configure(text=f"Error: {error_msg}"))
        finally:
            # Cleanup and reset UI for this specific video
            if video_url in self.download_processes:
                del self.download_processes[video_url]
            
            self.after(0, lambda: widgets['download_button'].configure(state=tk.NORMAL))
            self.after(0, lambda: widgets['cancel_button'].configure(state=tk.DISABLED))
            
            # Check if all downloads are complete to re-enable global download_all
            self.after(0, self._check_global_buttons_state)


    def download_all(self):
        """Starts downloading all videos in the loaded playlist in a batch."""
        if not self.video_info_list:
            messagebox.showinfo("No Videos", "No videos to download. Please load a playlist first.")
            return

        self.download_all_button.configure(state=tk.DISABLED)
        self.cancel_all_button.configure(state=tk.NORMAL)
        self.status_label.configure(text="Starting batch download...")

        # Disable individual download buttons and reset status
        for video_info in self.video_info_list:
            video_url = video_info['url']
            widgets = self.video_widgets[video_url]
            widgets['download_button'].configure(state=tk.DISABLED)
            widgets['cancel_button'].configure(state=tk.DISABLED) # Individual cancel not needed during batch
            widgets['status_label'].configure(text="Queued for batch...")
            widgets['progress_bar'].set(0)

        download_thread = threading.Thread(target=self.run_batch_download)
        download_thread.start()

    def cancel_single_download(self, video_url):
        """Terminates the subprocess for a specific video download."""
        if video_url in self.download_processes:
            process = self.download_processes[video_url]
            process.terminate() # Send termination signal
            # The run_download's finally block will handle cleanup and UI reset
            widgets = self.video_widgets[video_url]
            self.after(0, lambda: widgets['status_label'].configure(text="Cancelling...")) # Immediate feedback
            self.after(0, lambda: widgets['progress_bar'].set(0)) # Reset progress bar immediately

    def cancel_all(self):
        """Terminates all active download subprocesses."""
        self.status_label.configure(text="Cancelling all downloads...")
        
        # Create a list of keys to avoid RuntimeError: dictionary changed size during iteration
        keys_to_terminate = list(self.download_processes.keys())
        for video_url in keys_to_terminate:
            process = self.download_processes[video_url]
            process.terminate()
            # The run_download's finally block for each video will handle its cleanup.
            widgets = self.video_widgets[video_url]
            self.after(0, lambda: widgets['status_label'].configure(text="Cancelling...")) # Immediate feedback
            self.after(0, lambda: widgets['progress_bar'].set(0)) # Reset progress bar immediately

        # Global buttons will be reset by _check_global_buttons_state once all processes terminate

    def run_batch_download(self):
        """Executes a single yt-dlp command for all selected videos."""
        full_output = []
        try:
            base_command = ["yt-dlp", "--progress"]
            # Add output template with selected path
            output_template = os.path.join(self.download_path, "%(title)s.%(ext)s")
            base_command.extend(["-o", output_template])

            video_urls_to_download = []
            for video_info in self.video_info_list:
                video_url = video_info['url']
                widgets = self.video_widgets[video_url]
                if widgets['audio_only_var'].get():
                    # If audio_only is selected for any video, we need to download them individually
                    # or implement more complex logic to handle mixed downloads in batch.
                    # For now, we'll assume batch download is only for video or all audio.
                    self.after(0, lambda: messagebox.showwarning("Mixed Downloads", "Batch download does not support mixed video/audio formats. Please download audio-only videos individually."))
                    self.after(0, self.reset_individual_video_states)
                    self.after(0, self._check_global_buttons_state)
                    return
                video_urls_to_download.append(video_url)
            
            command = base_command + video_urls_to_download

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            self.download_processes["batch_download"] = process  # Use a common key for the batch process
            
            progress_regex = re.compile(r'\[download\]\s+(\d+\.\d+)%')
            for line in iter(process.stdout.readline, ''):
                full_output.append(line)
                match = progress_regex.search(line)
                if match:
                    try:
                        percentage = float(match.group(1)) / 100.0
                        # Update a global progress bar or overall status if needed
                        self.after(0, lambda p=percentage: self.status_label.configure(text=f"Batch downloading: {int(p*100)}%"))
                    except (ValueError, IndexError):
                        pass
                # Update individual video statuses if yt-dlp provides specific info for each video in batch
                # This is complex and might require parsing yt-dlp's verbose output for specific video identifiers.
                # For now, we'll keep it simple and update the global status.

            process.wait()

            if process.returncode == 0:
                self.after(0, lambda: self.status_label.configure(text="Batch download completed successfully!"))
                self.after(0, self.reset_individual_video_states)
            else:
                error_message = "".join(full_output).strip() or f"Unknown error (Exit Code: {process.returncode})"
                self.after(0, lambda msg=error_message: self.status_label.configure(text=f"Batch download failed! {msg}"))
                self.after(0, self.reset_individual_video_states)

        except Exception as e:
            self.after(0, lambda error_msg=e: messagebox.showerror("Error", f"Batch download failed: {error_msg}"))
            self.after(0, self.reset_individual_video_states)
        finally:
            if "batch_download" in self.download_processes:
                del self.download_processes["batch_download"]
            self.after(0, self._check_global_buttons_state)

    def monitor_downloads(self):
        """Periodically checks the status of active downloads and updates UI."""
        if self.download_processes:  # Only check if there are active downloads
            self._check_global_buttons_state()
            # Use longer delay when no downloads are active
            self.after(1000 if not self.download_processes else 100, self.monitor_downloads)
        else:
            self.after(1000, self.monitor_downloads)  # Check less frequently when idle

    def _check_global_buttons_state(self):
        """Helper to enable/disable global Download All/Cancel All buttons."""
        if not self.download_processes: # No active downloads
            self.download_all_button.configure(state=tk.NORMAL)
            self.cancel_all_button.configure(state=tk.DISABLED)
            # Only change global status label if it's currently showing "Cancelling..."
            if self.status_label.cget("text").startswith("Cancelling"):
                 self.status_label.configure(text="All downloads finished or cancelled.")
        else:
            self.download_all_button.configure(state=tk.DISABLED)
            self.cancel_all_button.configure(state=tk.NORMAL)

    def reset_individual_video_states(self):
        """Resets the UI elements for all individual videos."""
        for video_url, widgets in self.video_widgets.items():
            self.after(0, lambda w=widgets: w['status_label'].configure(text=""))
            self.after(0, lambda w=widgets: w['progress_bar'].set(0))
            self.after(0, lambda w=widgets: w['download_button'].configure(state=tk.NORMAL))
            self.after(0, lambda w=widgets: w['cancel_button'].configure(state=tk.DISABLED))

if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop()
