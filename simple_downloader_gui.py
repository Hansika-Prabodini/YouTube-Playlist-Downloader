import tkinter as tk
from tkinter import ttk


class FileDownloaderApp:
    def __init__(self):
        # Create main window
        self.root = tk.Tk()
        self.root.title("File Downloader")
        self.root.geometry("600x200")
        
        # Set minimum size constraints
        self.root.minsize(400, 150)
        
        # Center window on screen
        self.center_window()
        
        # Create and configure the GUI components
        self.create_widgets()
        
    def center_window(self):
        """Center the window on the screen"""
        # Update window to get proper dimensions
        self.root.update_idletasks()
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate center position
        window_width = 600
        window_height = 200
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Set window position
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
    def create_widgets(self):
        """Create and layout all GUI components"""
        # Main container frame with padding
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # URL input section
        url_frame = tk.Frame(main_frame)
        url_frame.pack(fill=tk.X, pady=(0, 15))
        
        # URL label
        url_label = tk.Label(url_frame, text="Enter URL:", font=("Arial", 11))
        url_label.pack(anchor=tk.W, pady=(0, 5))
        
        # URL input field
        self.url_entry = tk.Entry(url_frame, font=("Arial", 11), width=60)
        self.url_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Download button
        self.download_button = tk.Button(
            url_frame, 
            text="Download File",
            font=("Arial", 11, "bold"),
            bg="#007ACC",
            fg="white",
            activebackground="#005A9E",
            activeforeground="white",
            cursor="hand2",
            command=self.on_download_click
        )
        self.download_button.pack(pady=(0, 10))
        
        # Status label
        self.status_label = tk.Label(
            main_frame,
            text="Ready - Enter a URL and click Download File to begin",
            font=("Arial", 10),
            fg="gray",
            wraplength=550,
            justify=tk.CENTER
        )
        self.status_label.pack(pady=(10, 0))
        
    def on_download_click(self):
        """Handle download button click (placeholder functionality)"""
        url = self.url_entry.get().strip()
        if url:
            self.status_label.config(text=f"Download button clicked! URL: {url[:50]}{'...' if len(url) > 50 else ''}")
        else:
            self.status_label.config(text="Please enter a URL before clicking download")
            
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


if __name__ == "__main__":
    # Create and run the application
    app = FileDownloaderApp()
    app.run()
