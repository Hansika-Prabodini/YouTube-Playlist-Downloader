# File Organizer Feature Documentation

## Overview

The File Organizer is a proposed CLI utility for the llm-benchmarking-py toolkit that automatically organizes files in a directory based on configurable rules. It complements the existing YouTube downloader utilities by helping users manage downloaded content and other files efficiently.

## Feature Description

The File Organizer provides intelligent file sorting and organization capabilities with the following features:

### Core Capabilities
- **Organization by File Type**: Automatically categorize files by their extensions (videos, images, documents, audio, archives, etc.)
- **Organization by Date**: Sort files based on creation date, modification date, or date patterns in filenames (e.g., YYYY-MM-DD)
- **Custom Rule-Based Organization**: Support user-defined patterns and rules for flexible file categorization
- **Interactive Mode**: Menu-driven interface consistent with the YouTube downloader CLI pattern
- **Dry-Run Preview**: Safe preview mode to see what changes would be made before committing

### File Type Categories
The organizer will support common file type groupings:
- **Videos**: `.mp4`, `.mkv`, `.avi`, `.mov`, `.webm`, `.flv`
- **Audio**: `.mp3`, `.wav`, `.flac`, `.m4a`, `.ogg`, `.aac`
- **Images**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.svg`, `.webp`
- **Documents**: `.pdf`, `.doc`, `.docx`, `.txt`, `.md`, `.rtf`, `.odt`
- **Archives**: `.zip`, `.tar`, `.gz`, `.rar`, `.7z`, `.bz2`
- **Code**: `.py`, `.js`, `.java`, `.cpp`, `.c`, `.html`, `.css`
- **Spreadsheets**: `.xlsx`, `.xls`, `.csv`, `.ods`
- **Others**: Files that don't match predefined categories

## Advantages

### 1. Practical Use Cases
- **Downloads Folder Management**: Perfect for organizing cluttered download directories
- **Media Library Organization**: Automatically sort downloaded YouTube videos and other media files
- **Document Management**: Keep document folders tidy with automatic categorization
- **Project Cleanup**: Organize files in development and testing directories

### 2. Standard Library Implementation
- Uses only Python standard library modules (`os`, `shutil`, `pathlib`)
- No external dependencies required for core functionality
- Easy to maintain and deploy alongside existing utilities
- Consistent with project's lightweight approach

### 3. Clear, Predictable Results
- Interactive confirmation prevents unwanted file movements
- Dry-run mode allows users to preview all changes before committing
- Detailed logging shows exactly which files will be moved where
- Undo information provided for manual reversal if needed

### 4. Extensibility
- Easy to add new file type categories
- Custom rule system allows user-defined organization patterns
- Plugin-style architecture for future enhancements
- Configuration file support for saved presets

## Limitations

### 1. File Movement Risks
- **Data Safety Concerns**: Moving files always carries risk of data loss if interrupted
- **Path Issues**: Long file paths or special characters may cause problems on some systems
- **Permission Errors**: May fail if user lacks write permissions in target directories
- **Mitigation**: Implement robust error handling, atomic operations where possible, and clear error messages

### 2. File Conflict Handling Complexity
- **Naming Collisions**: Multiple files with same name but different locations need conflict resolution
- **Overwrite Protection**: Must prevent accidental overwrites of existing files
- **Conflict Resolution Strategies**:
  - Automatic renaming with numeric suffixes (e.g., `file.txt`, `file (1).txt`, `file (2).txt`)
  - Interactive prompts for user decision (skip, rename, overwrite)
  - Merge strategies for similar file types
- **Implementation Challenge**: Balancing automation with safety requires careful design

### 3. Edge Cases
- **Nested Directory Structures**: Deep folder hierarchies may complicate organization
- **Symbolic Links**: Need special handling to avoid breaking links or creating loops
- **Large File Sets**: Performance considerations for organizing thousands of files
- **Network Drives**: Slower operations on network-mounted filesystems

## Technical Implementation

### Architecture Overview

```
file_organizer_cli.py
├── Main Loop (Interactive Menu)
├── Configuration Manager
├── File Scanner
├── Rule Engine
├── Organization Strategies
│   ├── TypeOrganizer
│   ├── DateOrganizer
│   └── CustomRuleOrganizer
├── Conflict Resolver
└── File Mover (with rollback support)
```

### Core Components

#### 1. Pattern Matching for File Types
```python
# Using pathlib for clean file extension detection
from pathlib import Path

FILE_TYPE_PATTERNS = {
    'Videos': {'.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv'},
    'Audio': {'.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac'},
    'Images': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'},
    # ... additional categories
}

def categorize_by_type(file_path):
    """Categorize a file based on its extension."""
    suffix = Path(file_path).suffix.lower()
    for category, extensions in FILE_TYPE_PATTERNS.items():
        if suffix in extensions:
            return category
    return 'Others'
```

#### 2. Interactive Confirmation Flow
Following the pattern established in `youtube_Download-cli.py`:

```
1. Display welcome banner
2. Prompt for source directory
3. Show organization mode options:
   - [1] Organize by file type
   - [2] Organize by date (creation/modification)
   - [3] Organize by custom rules
   - [4] Configure settings
   - [5] Exit
4. Scan directory and show file statistics
5. Display proposed organization plan (dry-run)
6. Ask for confirmation:
   - [y] Proceed with organization
   - [n] Cancel
   - [d] Show detailed plan
   - [c] Change settings
7. Execute with progress updates
8. Show completion summary
```

#### 3. Dry-Run Mode Implementation

The dry-run mode is a critical safety feature:

```python
def organize_files(source_dir, strategy, dry_run=True):
    """
    Organize files according to the selected strategy.
    
    Args:
        source_dir: Source directory path
        strategy: Organization strategy (type/date/custom)
        dry_run: If True, only show what would happen
    
    Returns:
        List of (source, destination) tuples for proposed moves
    """
    operations = []
    
    for file_path in scan_directory(source_dir):
        target_dir = strategy.get_target_directory(file_path)
        target_path = resolve_conflicts(file_path, target_dir)
        operations.append((file_path, target_path))
    
    if dry_run:
        print_operations_preview(operations)
        return operations
    else:
        execute_operations(operations)
        return operations
```

**Dry-Run Features:**
- Shows complete list of files to be moved
- Displays source → destination mapping
- Highlights potential conflicts
- Calculates total data to be moved
- Estimates time for operation
- No actual file system modifications
- Can be run multiple times safely

#### 4. Conflict Resolution

```python
def resolve_conflict(source_file, target_dir):
    """
    Resolve naming conflicts when moving files.
    
    Returns the final target path with conflict resolution applied.
    """
    target_path = Path(target_dir) / Path(source_file).name
    
    if not target_path.exists():
        return target_path
    
    # Auto-rename with numeric suffix
    base = target_path.stem
    suffix = target_path.suffix
    counter = 1
    
    while target_path.exists():
        new_name = f"{base} ({counter}){suffix}"
        target_path = Path(target_dir) / new_name
        counter += 1
    
    return target_path
```

### Required Standard Library Modules

- **`os`**: Directory operations, path manipulation, file stats
- **`shutil`**: Safe file moving operations with metadata preservation
- **`pathlib`**: Modern path handling and manipulation
- **`datetime`**: Date-based organization and timestamp handling
- **`json`**: Configuration file management (optional)
- **`re`**: Regular expression pattern matching for custom rules
- **`sys`**: Command-line argument parsing and exit handling
- **`argparse`**: Enhanced CLI argument parsing (optional enhancement)

## Code Complexity Estimate

**Estimated Lines of Code: 150-200 lines**

### Breakdown:
- **Main loop and UI** (~30-40 lines): Interactive menu, input handling, display
- **File scanning and categorization** (~25-35 lines): Directory traversal, file type detection
- **Organization strategies** (~40-50 lines): Type-based, date-based, and custom rule logic
- **Conflict resolution** (~20-25 lines): Naming collision handling
- **File operations** (~20-25 lines): Safe move operations with error handling
- **Configuration and utilities** (~15-25 lines): Settings management, helper functions

This estimate aligns with the existing `youtube_Download-cli.py` (152 lines) and maintains similar code structure and complexity.

## Use Case: Organizing Downloaded Content

### Scenario: Managing YouTube Downloads and Other Files

**Problem**: After using the YouTube Playlist Downloader, users accumulate video files mixed with other downloads (PDFs, images, documents) in their Downloads folder. The folder becomes cluttered and difficult to navigate.

**Solution**: The File Organizer provides a clean, automated way to sort these files.

### Example Workflow

```bash
$ python file_organizer_cli.py

============================================
=     File Organizer (CLI)                =
============================================

Enter directory to organize (or 'exit' to quit): ~/Downloads

Scanning directory: /home/user/Downloads
Found 47 files to organize

Organization mode:
[1] By file type (recommended)
[2] By date (creation/modification)  
[3] By custom rules
[4] Configure settings

Select mode (1-4): 1

--- Dry Run: Preview of Changes ---

Videos/ (12 files)
  ├── awesome_tutorial.mp4
  ├── music_video.mp4
  ├── conference_talk.webm
  └── ... (9 more files)

Documents/ (8 files)
  ├── research_paper.pdf
  ├── notes.txt
  ├── README.md
  └── ... (5 more files)

Images/ (15 files)
  ├── screenshot_2024.png
  ├── diagram.jpg
  └── ... (13 more files)

Audio/ (3 files)
  ├── podcast.mp3
  └── ... (2 more files)

Archives/ (5 files)
  ├── backup.zip
  └── ... (4 more files)

Others/ (4 files)
  └── ... (4 files)

Total: 47 files → 6 folders

Proceed with organization? [y/n/d/c]: y

Organizing files...
[1/47] Moving: awesome_tutorial.mp4 → Videos/
[2/47] Moving: research_paper.pdf → Documents/
...
[47/47] Moving: unknown_file.dat → Others/

✓ Organization complete!
  Moved: 47 files
  Created: 6 folders
  Conflicts resolved: 2 (auto-renamed)
  Time: 1.2s
```

### Benefits for YouTube Downloader Users

1. **Automatic Media Sorting**: Downloaded videos are automatically moved to a Videos folder
2. **Mixed Content Handling**: If downloading subtitles (.srt), thumbnails (.jpg), or metadata (.json), each goes to appropriate category
3. **Regular Maintenance**: Can be run periodically to keep Downloads folder organized
4. **Safe Preview**: Dry-run mode lets users verify organization before committing changes
5. **Batch Processing**: Handles all files at once, saving manual sorting time

## Integration with Existing Project

### Consistency with Project Patterns

The File Organizer follows the same design principles as `youtube_Download-cli.py`:

1. **Interactive CLI**: Menu-driven interface with clear prompts
2. **User Confirmation**: No automatic changes without explicit user approval
3. **Progress Feedback**: Real-time updates during file operations
4. **Error Handling**: Graceful handling of common errors with helpful messages
5. **No External Dependencies**: Uses only standard library (core functionality)
6. **Simple Entry Point**: `if __name__ == "__main__":` pattern

### Suggested Project Structure Addition

```
llm-benchmarking-py/
├── youtube_Download-cli.py       # Existing
├── youtube_downloader-gui.py     # Existing
├── file_organizer_cli.py         # New addition
└── README.md                      # Update to include File Organizer
```

### README.md Update Example

Add to the "Utilities" section:

```markdown
### File Organizer (CLI)
```bash
# prerequisites: none (uses standard library only)

# run
python file_organizer_cli.py
```

Organize files in a directory by type, date, or custom rules. Features:
- Interactive menu-driven interface
- Dry-run preview mode
- Automatic conflict resolution
- Perfect for organizing downloaded YouTube videos and other content
```

## Future Enhancements

### Potential Extensions (Out of Scope for Initial Implementation)

1. **Configuration Files**: Save and load organization presets
2. **Watch Mode**: Automatically organize new files as they appear
3. **Undo/Rollback**: Track moves and provide automatic undo functionality
4. **Smart Categorization**: Use file content or metadata for better categorization
5. **Integration**: Direct integration with YouTube downloader to auto-organize downloads
6. **GUI Version**: CustomTkinter-based GUI similar to `youtube_downloader-gui.py`
7. **Recursive Organization**: Handle nested directory structures
8. **Filter Patterns**: Include/exclude files based on patterns before organizing

## Implementation Priority

**Priority: Medium**

The File Organizer is a valuable addition that complements the existing YouTube downloader utilities. It solves a real problem (cluttered download folders) and maintains consistency with the project's design philosophy. The standard library-only approach keeps dependencies minimal, and the estimated 150-200 lines of code makes it a manageable addition.

**Recommended Next Steps:**
1. Review this documentation for approval
2. Create `file_organizer_cli.py` following the documented architecture
3. Test with various file types and edge cases
4. Update README.md with usage instructions
5. Consider adding to the utilities section of the project

## Conclusion

The File Organizer feature provides a practical, well-scoped utility that fits naturally into the llm-benchmarking-py toolkit. Its interactive design, safety features (dry-run mode), and alignment with existing CLI patterns make it an ideal companion tool for users who download content using the YouTube downloaders. The implementation is straightforward, uses only standard library modules, and addresses a common pain point in file management.
