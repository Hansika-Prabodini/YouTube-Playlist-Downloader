import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import customtkinter as ctk
import subprocess
import threading
import json
import os
import sys
import re
import io
from functools import partial
from collections import defaultdict

# Precompiled regex patterns
PROGRESS_REGEX = re.compile(r'\[download\]\s+(\d+\.\d+)%')
SUCCESS_PATTERNS = [
    re.compile(pattern) for pattern in [
        r'\[download\] 100%', 
        r'\[ExtractAudio\] Destination:', 
        r'\[ffmpeg\] Destination:', 
        r'\[Merger\] Merging formats into'
    ]
]

# Main application class
class YouTubeDownloaderApp(ctk.CTk):
    def __init__(self):
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
        self._path_cache = self.download_path  # Cache for path string to reduce string operations
        self.pending_ui_updates = defaultdict(dict)  # Store pending UI updates to batch them
        self.video_info_list = []    # Store video information

        # --- GUI Elements ---
        self.create_widgets()

        # --- Start monitoring downloads ---
        # This function will periodically check the status of all active downloads
        self.after(250, self.monitor_downloads)  # Reduced frequency (250ms instead of 100ms)

    def create_widgets(self):
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
            self._path_cache = selected_path  # Update cache
            self.path_label.configure(text=f"Save to: {selected_path}")

    def create_context_menu(self):
        """Creates and binds the right-click context menu for the URL entry."""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Cut", command=lambda: self.url_entry.event_generate("<<Cut>>"))
        self.context_menu.add_command(label="Copy", command=lambda: self.url_entry.event_generate("<<Copy>>"))
        self.context_menu.add_command(label="Paste", command=self.paste_from_clipboard)

        # Bind the right-click event to the URL entry widget
        self.url_entry.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        """Displays the context menu at the mouse cursor position."""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def paste_from_clipboard(self):
        """Gets content from the clipboard and pastes it into the URL entry."""
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
        
        # Clear previous video widgets from the display frame
        for widget in self.video_list_frame.winfo_children():
            widget.destroy()

        fetch_thread = threading.Thread(target=self.fetch_playlist_titles, args=(url,))
        fetch_thread.start()

    def fetch_playlist_titles(self, url):
        """Fetches video titles and URLs from a playlist using yt-dlp."""
        try:
            # Add --no-warnings to reduce output parsing overhead
            command = ["yt-dlp", "--flat-playlist", "-j", "--no-warnings", url]
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,  # Separate stderr
                text=True,
                bufsize=1,  # Line buffered for better memory management
                universal_newlines=True
            )

            # Clear the list before adding new items
            self.video_info_list = []
            
            # Process JSON output efficiently
            for line in iter(process.stdout.readline, ''):
                if not line.strip():
                    continue
                    
                try:
                    video_json = json.loads(line)
                    # Only extract required fields - title and url
                    self.video_info_list.append({
                        'title': video_json.get('title', 'Untitled Video'),
                        'url': video_json.get('url', '')
                    })
                except json.JSONDecodeError:
                    pass  # Skip invalid JSON
            
            # Wait with timeout to prevent hanging
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.terminate()
                
            # Schedule display_videos to run on the main Tkinter thread
            self.after(0, self.display_videos)

        except Exception as e:
            # Schedule error message to run on the main Tkinter thread
            self.after(0, lambda error_msg=str(e): messagebox.showerror("Error", f"Failed to fetch playlist: {error_msg}"))
        finally:
            self.is_fetching = False
            self.after(0, lambda: self.load_button.configure(state=tk.NORMAL))

    def display_videos(self):
        """Displays fetched video titles with download options."""
        if not self.video_info_list:
            self.status_label.configure(text="No videos found in playlist.")
            self.download_all_button.configure(state=tk.DISABLED)
            return

        # Batch these UI updates for efficiency
        video_count = len(self.video_info_list)
        self.status_label.configure(text=f"Found {video_count} videos. Ready to download.")
        self.download_all_button.configure(state=tk.NORMAL)
        
        # Clear existing widgets if any - more efficient than destroying one by one
        for widget in self.video_list_frame.winfo_children():
            widget.destroy()
            
        # Create widgets in batches for better performance
        batch_size = 10  # Process 10 videos at a time to keep UI responsive
        
        def create_video_widgets(start_idx):
            end_idx = min(start_idx + batch_size, video_count)
            
            for i in range(start_idx, end_idx):
                video_info = self.video_info_list[i]
                video_url = video_info['url']
                
                # Frame for each video row
                row_frame = ctk.CTkFrame(self.video_list_frame, fg_color="transparent")
                row_frame.pack(fill=tk.X, pady=2, padx=5)

                # Video Title Label (reuse font reference)
                title_font = ("Arial", 12)
                ctk.CTkLabel(row_frame, text=video_info['title'], anchor="w", 
                             font=title_font).pack(side=tk.LEFT, padx=5, expand=True)

                # Status Label for individual video download
                status_label = ctk.CTkLabel(row_frame, text="", fg_color="transparent", 
                                           font=("Arial", 10))
                status_label.pack(side=tk.LEFT, padx=5)
                
                # Progress Bar for individual video download
                progress_bar = ctk.CTkProgressBar(row_frame, orientation="horizontal", width=150)
                progress_bar.set(0)
                progress_bar.pack(side=tk.LEFT, padx=5)

                # Fetch available resolutions
                resolutions = self.fetch_resolutions(video_url)
                resolution_var = tk.StringVar(value=resolutions[0] if resolutions else "")
                resolution_dropdown = ctk.CTkOptionMenu(
                    row_frame,
                    variable=resolution_var,
                    values=resolutions,
                    font=("Arial", 9)
                )
                resolution_dropdown.pack(side=tk.LEFT, padx=5)

                # Audio Only Checkbox for each video
                audio_only_video_var = ctk.BooleanVar(value=False)
                audio_only_checkbox = ctk.CTkCheckBox(
                    row_frame,
                    text="MP3",
                    variable=audio_only_video_var,
                    font=("Arial", 9)
                )
                audio_only_checkbox.pack(side=tk.LEFT, padx=5)

                # Use partial instead of lambda for better memory efficiency
                download_button = ctk.CTkButton(
                    row_frame,
                    text="Download",
                    command=partial(self.start_single_download, video_url, resolution_var),
                    font=("Arial", 12, "bold"),
                    width=100
                )
                download_button.pack(side=tk.RIGHT, padx=5)

                # Cancel button for individual video
                cancel_button = ctk.CTkButton(
                    row_frame,
                    text="Cancel",
                    command=partial(self.cancel_single_download, video_url),
                    state=tk.DISABLED,
                    fg_color="red",
                    hover_color="#c70000",
                    width=60,
                    font=("Arial", 10, "bold")
                )
                cancel_button.pack(side=tk.RIGHT, padx=5)
                
                # Store references to widgets and their state variables
                self.video_widgets[video_url] = {
                    'status_label': status_label,
                    'progress_bar': progress_bar,
                    'download_button': download_button,
                    'cancel_button': cancel_button,
                    'audio_only_var': audio_only_video_var, # Store the BooleanVar
                }
            
            # If more videos to process, schedule the next batch
            if end_idx < video_count:
                self.after(1, lambda: create_video_widgets(end_idx))
        
        # Start the first batch of widget creation
        create_video_widgets(0)

    def fetch_resolutions(self, video_url):
        """Fetches available resolutions for a video using yt-dlp."""
        try:
            command = ["yt-dlp", "-F", video_url]
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True
            )
            output, _ = process.communicate()
            resolutions = []
            for line in output.splitlines():
                if "video only" in line or "audio only" in line:
                    continue
                match = re.search(r'(\d{3,4}x\d{3,4})', line)
                if match:
                    resolutions.append(match.group(1))
            return resolutions
        except Exception as e:
            print(f"Error fetching resolutions: {e}")
            return []

    def start_single_download(self, video_url, resolution_var):
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
        
        # Use StringIO for better memory efficiency instead of a list
        output_buffer = io.StringIO()
        last_progress = 0  # Track last progress to reduce UI updates
        ui_update_counter = 0  # Counter to batch UI updates
        
        try:
            # Base command arguments with optimized options
            command = ["yt-dlp", "--progress"]
            # Add selected resolution format
            resolution = resolution_var.get()
            if resolution:
                command.extend(["-f", f"bestvideo[height<={resolution.split('x')[1]}]+bestaudio/best[height<={resolution.split('x')[1]}]"])
            
            # Add output template with cached path
            output_template = os.path.join(self._path_cache, "%(title)s.%(ext)s")
            command.extend(["-o", output_template])

            # Check if audio-only is selected
            if widgets['audio_only_var'].get():
                command.extend(["--extract-audio", "--audio-format", "mp3", "--no-playlist"])
            
            command.append(video_url)

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            self.download_processes[video_url] = process
            
            # Initialize pending updates for this video URL
            pending_updates = {}
            
            # Process output in chunks for better efficiency
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                
                # Keep only the most recent 100 lines to reduce memory usage
                if output_buffer.tell() > 10000:  # ~100 lines
                    # Clear buffer but keep the last 2000 chars for success detection
                    content = output_buffer.getvalue()
                    output_buffer = io.StringIO()
                    output_buffer.write(content[-2000:] if len(content) > 2000 else content)
                
                output_buffer.write(line)
                
                # Early termination check
                if process.poll() is not None and not line.strip():
                    break
                
                # Parse progress and update UI less frequently
                match = PROGRESS_REGEX.search(line)
                if match:
                    try:
                        percentage = float(match.group(1)) / 100.0
                        
                        # Only update UI if progress changed significantly (at least 1%)
                        if abs(percentage - last_progress) >= 0.01:
                            last_progress = percentage
                            
                            # Store updates to be applied later in batch
                            pending_updates['progress'] = percentage
                            pending_updates['status'] = line.strip()
                            
                            # Apply updates every few iterations to reduce overhead
                            ui_update_counter += 1
                            if ui_update_counter >= 5:  # Update UI every 5 progress changes
                                self._batch_update_ui(video_url, pending_updates)
                                pending_updates = {}
                                ui_update_counter = 0
                    except (ValueError, IndexError):
                        pending_updates['status'] = line.strip()
                else:
                    # For non-progress lines, only update status if it's important
                    # (contains certain keywords)
                    lower_line = line.lower()
                    if any(keyword in lower_line for keyword in ['error', 'warning', 'destination', 'merging']):
                        pending_updates['status'] = line.strip()
                        # Apply these important updates immediately
                        self._batch_update_ui(video_url, pending_updates)
                        pending_updates = {}
                        ui_update_counter = 0
            
            # Apply any remaining updates
            if pending_updates:
                self._batch_update_ui(video_url, pending_updates)
            
            # Wait for process to complete with timeout
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.terminate()
                process.wait(timeout=2)

            # --- FINAL STATUS DETERMINATION ---
            output_str = output_buffer.getvalue()
            output_buffer.close()  # Free memory
            
            is_success = process.returncode == 0
            
            if not is_success:
                # Check for success patterns even if returncode is non-zero
                for pattern in SUCCESS_PATTERNS:
                    if pattern.search(output_str):
                        is_success = True
                        break
            
            # Update UI for final status - in batch
            final_updates = {
                'status': "Download Completed!" if is_success else "Download Failed!",
                'progress': 1.0 if is_success else 0.0,
                'download_button_state': tk.NORMAL,
                'cancel_button_state': tk.DISABLED
            }
            
            # Apply final updates
            self._batch_update_ui(video_url, final_updates)

        except Exception as e:
            # Handle exception and update UI
            self._batch_update_ui(video_url, {
                'status': f"Error: {str(e)}",
                'progress': 0.0,
                'download_button_state': tk.NORMAL,
                'cancel_button_state': tk.DISABLED
            })
        finally:
            # Clean up resources
            if video_url in self.download_processes:
                del self.download_processes[video_url]
                
            # Schedule a check to update global buttons state
            self.after(50, self._check_global_buttons_state)
            
    def _batch_update_ui(self, video_url, updates):
        """Helper method to batch UI updates and apply them at once"""
        if video_url not in self.video_widgets:
            return
        
        widgets = self.video_widgets[video_url]
        
        # Schedule a single UI update for efficiency
        def update_ui():
            if 'progress' in updates:
                widgets['progress_bar'].set(updates['progress'])
            if 'status' in updates:
                widgets['status_label'].configure(text=updates['status'])
            if 'download_button_state' in updates:
                widgets['download_button'].configure(state=updates['download_button_state'])
            if 'cancel_button_state' in updates:
                widgets['cancel_button'].configure(state=updates['cancel_button_state'])
                
        # Schedule the batch update
        self.after(0, update_ui)


    def download_all(self):
        """Starts downloading all videos in the loaded playlist."""
        self.download_all_button.configure(state=tk.DISABLED)
        self.cancel_all_button.configure(state=tk.NORMAL)
        
        # Start downloads with slight delay between each to prevent resource contention
        def start_downloads_sequentially(index=0):
            if index >= len(self.video_info_list):
                return
                
            video_url = self.video_info_list[index]['url']
            if video_url not in self.download_processes:
                self.start_single_download(video_url)
            
            # Schedule next download with a small delay
            self.after(200, lambda: start_downloads_sequentially(index + 1))
        
        # Start the sequential download process
        start_downloads_sequentially()

    def cancel_single_download(self, video_url):
        """Terminates the subprocess for a specific video download."""
        if video_url in self.download_processes:
            process = self.download_processes[video_url]
            process.terminate()
            # Use batch update for UI changes
            self._batch_update_ui(video_url, {
                'status': "Cancelling...",
                'progress': 0.0
            })

    def cancel_all(self):
        """Terminates all active download subprocesses."""
        self.status_label.configure(text="Cancelling all downloads...")
        
        # Create a list of keys to avoid dictionary changed size during iteration
        keys_to_terminate = list(self.download_processes.keys())
        
        # Batch UI updates for all videos being cancelled
        updates_by_video = {}
        for video_url in keys_to_terminate:
            process = self.download_processes[video_url]
            process.terminate()
            updates_by_video[video_url] = {
                'status': "Cancelling...",
                'progress': 0.0
            }
        
        # Apply all UI updates at once
        def apply_all_updates():
            for url, updates in updates_by_video.items():
                if url in self.video_widgets:
                    widgets = self.video_widgets[url]
                    widgets['status_label'].configure(text=updates['status'])
                    widgets['progress_bar'].set(updates['progress'])
                    
        # Schedule a single UI update for efficiency
        if updates_by_video:
            self.after(0, apply_all_updates)

    def monitor_downloads(self):
        """Periodically checks the status of active downloads and updates UI."""
        # We just need to check if there are any processes left to decide global button state
        self._check_global_buttons_state()

        # Check for any terminated processes that didn't clean up properly
        active_processes = list(self.download_processes.keys())
        for video_url in active_processes:
            process = self.download_processes[video_url]
            if process.poll() is not None:
                # Process has terminated but wasn't removed from dictionary
                # This could happen if the process was terminated externally
                if video_url in self.download_processes:
                    del self.download_processes[video_url]
                    self._batch_update_ui(video_url, {
                        'status': "Download interrupted",
                        'progress': 0.0,
                        'download_button_state': tk.NORMAL,
                        'cancel_button_state': tk.DISABLED
                    })

        # Reschedule the next check with reduced frequency for lower overhead
        self.after(250, self.monitor_downloads)

    def _check_global_buttons_state(self):
        """Helper to enable/disable global Download All/Cancel All buttons."""
        has_active_downloads = bool(self.download_processes)
        
        # Avoid unnecessary UI updates
        current_download_all_state = str(self.download_all_button.cget("state"))
        current_cancel_all_state = str(self.cancel_all_button.cget("state"))
        
        # Only update if state needs to change
        if not has_active_downloads:
            if current_download_all_state != "normal":
                self.download_all_button.configure(state=tk.NORMAL)
            if current_cancel_all_state != "disabled":
                self.cancel_all_button.configure(state=tk.DISABLED)
                
            # Only change global status label if it's currently showing "Cancelling..."
            current_text = self.status_label.cget("text")
            if current_text.startswith("Cancelling"):
                self.status_label.configure(text="All downloads finished or cancelled.")
        else:
            if current_download_all_state != "disabled":
                self.download_all_button.configure(state=tk.DISABLED)
            if current_cancel_all_state != "normal":
                self.cancel_all_button.configure(state=tk.NORMAL)


if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop()
                # Keep only recent important information for error reporting
                if "[download]" in line or "[ExtractAudio]" in line or "[Merger]" in line or "ERROR" in line:
                    line_buffer = (line_buffer + line)[-500:]  # Keep only last 500 chars
                
                # Check if process terminated early (e.g., cancelled)
                if process.poll() is not None and not line.strip(): 
                    break  # Exit if process is done and no more output

                # Update progress with throttling
                match = PROGRESS_REGEX.search(line)
                if match:
                    try:
                        percentage = float(match.group(1)) / 100.0
                        current_time = time.time()
                        # Only update UI at most 4 times per second to reduce overhead
                        if current_time - last_progress_update_time >= update_interval:
                            self._schedule_batch_ui_update(video_url, 'progress', percentage)
                            self._schedule_batch_ui_update(video_url, 'status', line.strip())
                            last_progress_update_time = current_time
                    except (ValueError, IndexError):
                        pass
                elif "ERROR" in line:
                    # Always show errors immediately
                    self._schedule_batch_ui_update(video_url, 'status', line.strip())
            
            process.wait()  # Wait for the subprocess to truly complete

            # --- FINAL STATUS DETERMINATION ---
            is_success = process.returncode == 0 or success_indicators_found
            
            # Update UI on the main thread based on final determination
            if is_success:
                self._schedule_batch_ui_update(video_url, 'status', "Download Completed!")
                self._schedule_batch_ui_update(video_url, 'progress', 1.0)  # Ensure 100%
            else:
                error_message = line_buffer.strip() if line_buffer else f"Unknown error (Exit Code: {process.returncode})"
                self._schedule_batch_ui_update(video_url, 'status', f"Download Failed! Check log.")
                self._schedule_batch_ui_update(video_url, 'progress', 0)  # Reset progress bar

        except Exception as e:
            self._schedule_batch_ui_update(video_url, 'status', f"Error: {str(e)}")
        finally:
            # Cleanup resources
            if video_url in self.download_processes:
                # Ensure process is terminated
                try:
                    if self.download_processes[video_url].poll() is None:
                        self.download_processes[video_url].terminate()
                except:
                    pass
                del self.download_processes[video_url]
            
            # Reset UI for this specific video
            self._schedule_batch_ui_update(video_url, 'download_button', tk.NORMAL)
            self._schedule_batch_ui_update(video_url, 'cancel_button', tk.DISABLED)
            
            # Force process batch updates
            if self.update_scheduled:
                self._process_batch_ui_updates()
            
            # Check if all downloads are complete to re-enable global download_all
            self.after(0, self._check_global_buttons_state)


    def download_all(self):
        """Starts downloading all videos in the loaded playlist."""
        if not hasattr(self, 'video_info_list') or not self.video_info_list:
            return
            
        # Update global button state immediately
        self.download_all_button.configure(state=tk.DISABLED)
        self.cancel_all_button.configure(state=tk.NORMAL)
        
        # Limit concurrent downloads to avoid overwhelming system resources
        MAX_CONCURRENT_DOWNLOADS = 3
        active_downloads = 0
        
        # First collect the videos to download
        videos_to_download = []
        for video_info in self.video_info_list:
            video_url = video_info['url']
            if video_url not in self.download_processes:
                videos_to_download.append(video_url)
        
        # Start downloads with limited concurrency
        for video_url in videos_to_download:
            if active_downloads >= MAX_CONCURRENT_DOWNLOADS:
                break
                
            self.start_single_download(video_url)
            active_downloads += 1
        
        # If there are more videos to download, set up a timer to check and start more
        if active_downloads < len(videos_to_download):
            self.remaining_downloads = videos_to_download[active_downloads:]
            self.after(1000, self._continue_download_all)
    
    def _continue_download_all(self):
        """Continues downloading videos when slots become available."""
        if not hasattr(self, 'remaining_downloads') or not self.remaining_downloads:
            return
            
        # Check how many downloads we can start
        MAX_CONCURRENT_DOWNLOADS = 3
        current_downloads = len(self.download_processes)
        slots_available = MAX_CONCURRENT_DOWNLOADS - current_downloads
        
        if slots_available > 0 and self.remaining_downloads:
            # Start up to slots_available new downloads
            videos_to_start = self.remaining_downloads[:slots_available]
            self.remaining_downloads = self.remaining_downloads[slots_available:]
            
            for video_url in videos_to_start:
                if video_url not in self.download_processes:
                    self.start_single_download(video_url)
        
        # If there are still more videos, schedule another check
        if self.remaining_downloads:
            self.after(1000, self._continue_download_all)

    def cancel_single_download(self, video_url):
        """Terminates the subprocess for a specific video download."""
        if video_url in self.download_processes:
            try:
                process = self.download_processes[video_url]
                # Try to kill process more forcefully for faster termination
                if sys.platform == 'win32':
                    # On Windows, use taskkill for more reliable termination
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(process.pid)],
                                 stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
                else:
                    # On Unix, use SIGKILL for forceful termination
                    os.kill(process.pid, 9)  # SIGKILL
            except:
                # Fallback to normal termination
                try:
                    process.terminate()
                except:
                    pass
                    
            # Update UI immediately for better responsiveness
            self._schedule_batch_ui_update(video_url, 'status', "Cancelling...")
            self._schedule_batch_ui_update(video_url, 'progress', 0)
            
            # Force-process updates immediately
            self._process_batch_ui_updates()

    def cancel_all(self):
        """Terminates all active download subprocesses."""
        if not self.download_processes:
            return
            
        self.status_label.configure(text="Cancelling all downloads...")
        
        # Use a single list to avoid dictionary changed size during iteration
        for video_url in list(self.download_processes.keys()):
            self.cancel_single_download(video_url)
            
        # Batch process all UI updates at once
        if self.update_scheduled:
            self._process_batch_ui_updates()

    def monitor_downloads(self):
        """Periodically checks the status of active downloads and updates UI.
        Runs at a reduced frequency (250ms instead of 100ms) to decrease CPU usage.
        """
        # Clean up any zombie processes
        self._cleanup_finished_processes()
        
        # Update global button states
        self._check_global_buttons_state()

        # Reschedule the next check with reduced frequency (250ms)
        self.after(250, self.monitor_downloads)
        
    def _cleanup_finished_processes(self):
        """Check and remove any processes that have finished but weren't properly cleaned up."""
        for video_url in list(self.download_processes.keys()):
            process = self.download_processes[video_url]
            # Check if the process has finished
            if process.poll() is not None:
                # Process has finished; make sure UI is updated and process is removed
                if video_url in self.video_widgets:
                    widgets = self.video_widgets[video_url]
                    # Only update if not already updated
                    if widgets['download_button'].cget("state") == tk.DISABLED:
                        self._schedule_batch_ui_update(video_url, 'download_button', tk.NORMAL)
                        self._schedule_batch_ui_update(video_url, 'cancel_button', tk.DISABLED)
                        
                # Remove from active processes dictionary
                del self.download_processes[video_url]

    def _check_global_buttons_state(self):
        """Helper to enable/disable global Download All/Cancel All buttons."""
        has_active_downloads = bool(self.download_processes)
        
        # Use a single batch update instead of multiple configure calls
        if not has_active_downloads: 
            self.download_all_button.configure(state=tk.NORMAL)
            self.cancel_all_button.configure(state=tk.DISABLED)
            
            # Only change global status label if it's currently showing "Cancelling..."
            current_status = self.status_label.cget("text")
            if current_status.startswith("Cancelling"):
                self.status_label.configure(text="All downloads finished or cancelled.")
        else:
            # Only update if state needs changing
            if self.download_all_button.cget("state") != tk.DISABLED:
                self.download_all_button.configure(state=tk.DISABLED)
            if self.cancel_all_button.cget("state") != tk.NORMAL:
                self.cancel_all_button.configure(state=tk.NORMAL)

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
            
            while True:
                line = process.stdout.readline()
                if not line: # No more output
                    break
                
                full_output.append(line) # Store every line

                # Check if process terminated early (e.g., cancelled)
                if process.poll() is not None and not line.strip(): 
                    break # Exit if process is done and no more output

                match = progress_regex.search(line)
                if match:
                    try:
                        percentage = float(match.group(1)) / 100.0
                        self.after(0, lambda p=percentage: widgets['progress_bar'].set(p))
                        self.after(0, lambda l=line.strip(): widgets['status_label'].configure(text=l))
                    except (ValueError, IndexError):
                        self.after(0, lambda l=line.strip(): widgets['status_label'].configure(text=l))
                else:
                    self.after(0, lambda l=line.strip(): widgets['status_label'].configure(text=l))
            
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
        """Starts downloading all videos in the loaded playlist."""
        self.download_all_button.configure(state=tk.DISABLED)
        self.cancel_all_button.configure(state=tk.NORMAL)
        
        for video_info in self.video_info_list:
            video_url = video_info['url']
            # Only start if not already downloading
            if video_url not in self.download_processes:
                self.start_single_download(video_url)

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

    def monitor_downloads(self):
        """Periodically checks the status of active downloads and updates UI."""
        # The actual status update logic is now primarily within run_download's loop and finally block.
        # This monitor is mainly for global button state and general app status.
        
        # We just need to check if there are any processes left to decide global button state
        self._check_global_buttons_state()

        # Reschedule the next check
        self.after(100, self.monitor_downloads)

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


if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop()