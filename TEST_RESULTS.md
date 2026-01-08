YouTube Downloader GUI - Manual Test Results for yt-dlp Error Handling

Overview
This document records manual testing of the improved yt-dlp error handling across fetching and downloading flows. It follows the provided scenarios and validates behavior, UI responsiveness, and messaging. Use this as a checklist during execution and record results in the Actual Result/Notes fields.

How to simulate missing yt-dlp
- Linux/macOS (bash):
  - Temporarily remove yt-dlp from PATH for the shell used to launch the app:
    - export _OLD_PATH="$PATH" && export PATH="/usr/bin:/bin"  # or a path that does not include yt-dlp
  - Alternative: temporarily move/rename the executable (requires sudo if installed system-wide):
    - which yt-dlp  # note the path, e.g., /usr/local/bin/yt-dlp
    - sudo mv "$(which yt-dlp)" "$(which yt-dlp)".bak
  - Restore after testing:
    - export PATH="$_OLD_PATH"
    - sudo mv "/usr/local/bin/yt-dlp.bak" "/usr/local/bin/yt-dlp"  # adjust path as needed
- Windows (PowerShell):
  - Temporarily override PATH for the PowerShell session:
    - $env:_OLD_PATH = $env:PATH; $env:PATH = "C:\\Windows;C:\\Windows\\System32"  # or use a path that does not contain yt-dlp
  - Alternative: rename yt-dlp.exe (if you have permissions):
    - Rename-Item (Get-Command yt-dlp).Source -NewName { $_.Name + ".bak" }
  - Restore after testing:
    - $env:PATH = $env:_OLD_PATH
    - Rename-Item (Get-Command yt-dlp).Source.Replace(".bak", "") -NewName { [System.IO.Path]::GetFileNameWithoutExtension($_.Name) + ".exe" }

Expected standard error dialog for missing yt-dlp
Title: yt-dlp Not Found
Message (exactly):
yt-dlp is not installed or not found in PATH.

Please install it with:
python -m pip install yt-dlp

Scenario 1: yt-dlp Not Available
- Preparation
  - [ ] Make yt-dlp unavailable (see instructions above)
  - [ ] Confirm missing via which yt-dlp (macOS/Linux) or where yt-dlp (Windows) — should not find it
- Steps and Expected Results
  1) Launch the application
     - Expected: App starts without error
     - Actual Result/Notes: ______________________________
  2) Enter a valid YouTube playlist URL and click "Load Playlist"
     - Expected: Error dialog appears with title "yt-dlp Not Found"; message matches exactly (see above)
     - Expected: Global status label updates to "Error: yt-dlp not found."
     - Expected: Load Playlist button is re-enabled
     - Actual Result/Notes: ______________________________
  3) Enter a valid single YouTube video URL and click "Download"
     - Expected: Same error dialog appears
     - Expected: The video row status label shows "Error: yt-dlp not found."
     - Expected: Progress bar resets to 0, Download button re-enabled, Cancel disabled
     - Actual Result/Notes: ______________________________

Scenario 2: yt-dlp Available (Regression)
- Preparation
  - [ ] Restore yt-dlp to PATH (which/where should succeed)
- Steps and Expected Results
  1) Launch the application
     - Expected: App starts without error; status label prompts to load playlist
     - Actual Result/Notes: ______________________________
  2) Load a valid YouTube playlist URL
     - Expected: Playlist loads; number of videos shown; Download All enabled
     - Actual Result/Notes: ______________________________
  3) Download a single video
     - Expected: Progress updates; completes successfully; status shows "Download Completed!" and progress 100%
     - Actual Result/Notes: ______________________________
  4) Use "Download All"
     - Expected: Each video starts; Cancel All enabled; upon completion, buttons return to normal; global status may show "All downloads finished or cancelled."
     - Actual Result/Notes: ______________________________
  5) Invalid/malformed URL
     - Step: Enter an invalid URL (e.g., not a YouTube URL) and click Load Playlist or attempt single download
     - Expected: Generic error handling triggers (not the yt-dlp missing dialog); error messages remain consistent with prior behavior
     - Actual Result/Notes: ______________________________

Scenario 3: Cross-Platform Verification
- For each available platform (Windows/Linux/macOS):
  - [ ] Verify shutil.which('yt-dlp') behavior by making yt-dlp available/unavailable
  - [ ] Confirm messagebox dialogs display properly and the message formatting (line breaks) matches the exact expected text
  - [ ] UI responsiveness: buttons re-enable as expected; no hangs or crashes
  - Notes per platform:
    - Windows: __________________________________________
    - Linux:   __________________________________________
    - macOS:   __________________________________________

Success Criteria Validation
- [ ] Missing yt-dlp is correctly detected and actionable dialog shown (Scenarios 1 & 3)
- [ ] Other FileNotFoundError cases are not masked (handlers re-raise when yt-dlp exists)
- [ ] All functionality works when yt-dlp is available (Scenario 2)
- [ ] Generic error handling still catches non-yt-dlp errors (Scenario 2 step 5)
- [ ] UI remains responsive and updates correctly (buttons/status/progress) in all cases
- [ ] Cross-platform behavior validated where possible

Implementation notes (for maintainers)
- Fetch flow: FileNotFoundError is intercepted; if shutil.which('yt-dlp') is None, shows standardized dialog and updates global status; else re-raises to generic handler. Finally block resets is_fetching and re-enables Load button.
- Download flow: Similar handling per video; status label updated to "Error: yt-dlp not found." and progress reset to 0; finally cleans up process tracking and re-enables per-video Download button, disables Cancel, and calls _check_global_buttons_state.
- UI thread safety: All UI updates are scheduled via self.after(0, ...), ensuring main-thread execution.
- README alignment: README now includes a note mirroring the exact dialog text for missing yt-dlp.

Test Data
- Example playlist URL: https://www.youtube.com/playlist?list=PLl-K7zZEsYLm7jZ3z2RNGc1Tx7sZ5Vx0E (replace with any publicly accessible playlist)
- Example single video URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ

Execution Log
Date: ____________
Tester: __________
Environment: Windows | Linux | macOS; Python __.__; yt-dlp version _____

Results Summary
- Scenario 1: Pass | Fail (details: ____________________________________)
- Scenario 2: Pass | Fail (details: ____________________________________)
- Scenario 3: Pass | Fail (details: ____________________________________)

Sign-off
- Tester Signature: ____________________  Date: __________
