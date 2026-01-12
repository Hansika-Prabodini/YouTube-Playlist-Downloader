import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import customtkinter as ctk
import threading
import os
import sys
from yt_downloader import download_video, cancel_download
from yt_playlist import fetch_playlist_info

# Main application class
class YouTubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Configuration ---
        self.title("Nuwan's Playlist Downloader")
        self.geometry("800x600")
        self.configure(bg="#f0f0f0")
        
        # --- Variables ---
        self.download_processes = {} # Stores active download process handles for cancellation
        self.video_widgets = {}      # Stores references to widgets for each video (video_url: dict of widgets)
        self.video_info_list = []    # Holds metadata for videos in the current playlist
        self.is_fetching = False     # Flag to prevent multiple fetch operations
        self.download_path = os.getcwd() # Set default download path to current directory

        # --- GUI Elements ---
        self.create_widgets()

        # --- Start monitoring downloads ---
        # This function will periodically check the status of all active downloads
        self.after(100, self.monitor_downloads)

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
            self.path_label.configure(text=f"Save to: {self.download_path}")

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
        
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL.")
            return

        self.is_fetching = True
        self.load_button.configure(state=tk.DISABLED)
        self.status_label.configure(text="Fetching playlist titles...")
        
        # Clear previous video widgets from the display frame
        for widget in self.video_list_frame.winfo_children():
            widget.destroy()
        self.video_widgets.clear()
        self.video_info_list = []

        fetch_thread = threading.Thread(target=self.fetch_playlist_titles, args=(url,), daemon=True)
        fetch_thread.start()

    def fetch_playlist_titles(self, url):
        """Fetches video titles and URLs from a playlist."""
        try:
            result = fetch_playlist_info(url)
            
            if result['success']:
                self.video_info_list = result['videos']
                # Schedule display_videos to run on the main Tkinter thread
                self.after(0, self.display_videos)
            else:
                error_message = f"Failed to fetch playlist: {result['error_message']}"
                self.after(0, lambda msg=error_message: self.status_label.configure(text=msg))
                self.after(0, lambda msg=error_message: messagebox.showerror("Error", msg))
        
        except Exception as e:
            error_message = f"Failed to fetch playlist: {e}"
            self.after(0, lambda msg=error_message: self.status_label.configure(text=msg))
            self.after(0, lambda msg=error_message: messagebox.showerror("Error", msg))
        finally:
            self.is_fetching = False
            self.after(0, lambda: self.load_button.configure(state=tk.NORMAL))

    def display_videos(self):
        """Displays fetched video titles with download options."""
        if self.video_info_list:
            self.status_label.configure(text=f"Found {len(self.video_info_list)} videos. Ready to download.")
            self.download_all_button.configure(state=tk.NORMAL)
            self.video_widgets.clear()
            
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
                
                # Store references to widgets and their state variables
                self.video_widgets[video_url] = {
                    'status_label': status_label,
                    'progress_bar': progress_bar,
                    'download_button': download_button,
                    'cancel_button': cancel_button,
                    'audio_only_var': audio_only_video_var, # Store the BooleanVar
                }
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

        download_thread = threading.Thread(target=self.run_download, args=(video_url,), daemon=True)
        download_thread.start()

    def run_download(self, video_url):
        """Initiates and monitors the download of a single video."""
        widgets = self.video_widgets[video_url]
        
        def progress_callback(line):
            """Callback to handle progress updates from the download module."""
            # Update status label with the progress line
            self.after(0, lambda text=line: widgets['status_label'].configure(text=text))
            
            # Update progress bar if percentage is in the line
            if '[download]' in line and '%' in line:
                try:
                    # Simple string parsing for percentage (e.g., "50.2%")
                    parts = line.split('%')
                    if len(parts) > 1:
                        # Get the last part before '%' and extract the number
                        percent_str = parts[0].split()[-1]
                        percentage = float(percent_str) / 100.0
                        self.after(0, lambda p=percentage: widgets['progress_bar'].set(p))
                except (ValueError, IndexError):
                    pass
        
        try:
            # Get audio-only preference for this video
            extract_audio = widgets['audio_only_var'].get()
            
            # Call the download function from the module
            result = download_video(
                video_url=video_url,
                download_path=self.download_path,
                extract_audio=extract_audio,
                progress_callback=progress_callback
            )
            
            # Store process handle for cancellation
            if result['process']:
                self.download_processes[video_url] = result['process']
            
            # Update UI based on result
            if result['success']:
                self.after(0, lambda: widgets['status_label'].configure(text="Download Completed!"))
                self.after(0, lambda: widgets['progress_bar'].set(1.0))
            else:
                error_message = result['error_message']
                self.after(0, lambda msg=error_message: widgets['status_label'].configure(text=f"Failed: {msg}"))
                self.after(0, lambda: widgets['progress_bar'].set(0))

        except Exception as e:
            self.after(0, lambda error_msg=str(e): widgets['status_label'].configure(text=f"Error: {error_msg}"))
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
        """Cancels a specific video download."""
        if video_url in self.download_processes:
            process = self.download_processes[video_url]
            cancel_download(process)
            # The run_download's finally block will handle cleanup and UI reset
            widgets = self.video_widgets[video_url]
            self.after(0, lambda w=widgets: w['status_label'].configure(text="Cancelling..."))
            self.after(0, lambda w=widgets: w['progress_bar'].set(0))

    def cancel_all(self):
        """Cancels all active downloads."""
        self.status_label.configure(text="Cancelling all downloads...")
        
        # Create a list of keys to avoid RuntimeError: dictionary changed size during iteration
        keys_to_terminate = list(self.download_processes.keys())
        for video_url in keys_to_terminate:
            process = self.download_processes[video_url]
            cancel_download(process)
            # The run_download's finally block for each video will handle its cleanup.
            widgets = self.video_widgets[video_url]
            self.after(0, lambda w=widgets: w['status_label'].configure(text="Cancelling..."))
            self.after(0, lambda w=widgets: w['progress_bar'].set(0))

        # Global buttons will be reset by _check_global_buttons_state once all processes terminate

    def monitor_downloads(self):
        """Periodically checks the status of active downloads and updates UI."""
        # Check global button state based on active downloads
        self._check_global_buttons_state()

        # Reschedule the next check
        self.after(100, self.monitor_downloads)

    def _check_global_buttons_state(self):
        """Helper to enable/disable global Download All/Cancel All buttons."""
        active_cancels = any(
            widgets['cancel_button'].cget("state") == tk.NORMAL for widgets in self.video_widgets.values()
        )
        if not self.download_processes and not active_cancels: # No active downloads
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