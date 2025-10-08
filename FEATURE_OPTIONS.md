# Feature Options for YouTube Downloader CLI Enhancement

This document compares potential feature additions to the existing YouTube Downloader CLI utility. Each option is evaluated based on its utility, implementation complexity, and alignment with the project's goals.

---

## Option 2: Batch Rename with Pattern Support

### Feature Description

A comprehensive batch renaming utility that allows users to rename multiple downloaded files using various pattern matching and transformation techniques. This feature would enable users to organize and standardize filenames after downloading videos from YouTube playlists.

The batch rename feature supports multiple renaming strategies:

**Sequential Numbering**: Rename files with a base name and sequential numbers (e.g., `video_001.mp4`, `video_002.mp4`, `video_003.mp4`). This is ideal for creating ordered series from playlist downloads.

**Find and Replace**: Simple text replacement within filenames. Users can specify a text pattern to find and what to replace it with (e.g., replace all spaces with underscores, remove special characters, or substitute common abbreviations).

**Regex Pattern Matching**: Advanced users can leverage regular expressions for complex pattern matching and replacement operations. This allows for sophisticated transformations like extracting date patterns, reformatting text, or conditional replacements based on filename structure.

**Case Conversion**: Transform filename casing across multiple files:
- Convert to UPPERCASE
- Convert to lowercase
- Convert to Title Case
- Convert to camelCase or snake_case

### Advantages

1. **High Utility for Media Organization**: Particularly valuable for users downloading multiple videos or photos. Downloaded YouTube videos often have inconsistent or verbose naming conventions that benefit from standardization.

2. **Standard Library Only**: Implementation relies entirely on Python's standard library (`os`, `re`, `pathlib`), requiring no additional dependencies. This keeps the utility lightweight and maintains the project's minimal dependency philosophy.

3. **Immediate Visible Results**: Unlike background tasks or data processing features, file renaming provides instant, tangible feedback. Users can immediately see the organizational improvement in their file system.

4. **Natural CLI Fit**: Batch renaming operations map well to command-line workflows. The feature complements the existing YouTube downloader by addressing the common next step: organizing downloaded content.

5. **Reusable Utility**: While designed for organizing YouTube downloads, the batch rename tool can be used for any file organization task, making it a versatile addition to the toolkit.

### Limitations

1. **Regex Complexity for Users**: Regular expressions can be intimidating and confusing for non-technical users. Providing regex support may lead to user errors, invalid patterns, or unexpected results. Clear documentation and example patterns would be essential.

2. **Name Collision Handling**: When multiple files would be renamed to the same target name (collision), the system must handle this gracefully. Solutions include:
   - Automatic suffixing (file.mp4, file_1.mp4, file_2.mp4)
   - Prompting the user for resolution
   - Aborting the operation with a warning
   
   Each approach has trade-offs between automation and user control.

3. **Undo Feature Difficulty**: Implementing a reliable undo mechanism is complex. Options include:
   - Maintaining a rename log file mapping old names to new names
   - Creating backup copies before renaming (storage overhead)
   - Using file system transaction capabilities (platform-dependent)
   
   Without undo functionality, users risk losing their original filename organization permanently.

4. **Cross-Platform Path Handling**: Different operating systems have varying restrictions on filename characters, path separators, and length limits. The implementation must handle these differences carefully to avoid corrupting filenames or causing errors.

### Implementation Details

#### Preview-Before-Apply Workflow

The implementation follows a two-phase approach to prevent accidental data loss:

1. **Preview Phase**: 
   - Scan the target directory and identify files matching the selection criteria
   - Apply the renaming pattern/transformation in memory
   - Display a table showing `Original Name → New Name` for each file
   - Detect and highlight potential name collisions
   - Show warnings for any problematic transformations (e.g., invalid characters)

2. **Confirmation Phase**:
   - Prompt user to review the preview
   - Require explicit confirmation (yes/no) before proceeding
   - Allow user to cancel or modify the pattern

3. **Execution Phase**:
   - Perform the actual file renaming operations
   - Provide progress feedback for large batches
   - Log all successful renames for potential undo functionality
   - Report any errors encountered during the process

#### Pattern Type Implementations

**Sequential Numbering**:
- Format: `{base_name}_{number:03d}{extension}`
- User specifies: base name, starting number, padding width
- Example: `lecture_001.mp4`, `lecture_002.mp4`, `lecture_003.mp4`

**Find and Replace**:
- Simple string substitution using `str.replace()`
- User specifies: find pattern, replacement string
- Case-sensitive and case-insensitive modes
- Example: Replace "IMG_" with "Photo_"

**Regex Pattern Support**:
- Uses Python's `re` module for pattern matching
- User provides: regex pattern, replacement pattern with capture groups
- Validation of regex syntax before application
- Example: `r'(\d{4})(\d{2})(\d{2})_.*'` → `r'\1-\2-\3'` converts `20240115_video.mp4` to `2024-01-15.mp4`

**Case Conversion**:
- Uppercase: `filename.upper()`
- Lowercase: `filename.lower()`
- Title Case: `filename.title()`
- Custom functions for camelCase and snake_case transformations

#### File Selection and Filtering

- Support for file extension filters (e.g., only .mp4, .mkv files)
- Option to include/exclude subdirectories (recursive mode)
- File selection by pattern matching (glob patterns)
- Interactive selection mode for manual file choosing

### Technical Requirements

**Code Complexity Estimate**: 180-220 lines
- Core renaming logic: ~60 lines
- Preview and confirmation system: ~40 lines
- Pattern type implementations: ~50 lines
- Error handling and validation: ~30 lines
- CLI interface and user prompts: ~40 lines

**Required Standard Library Modules**:
- `os`: File system operations (rename, path checking)
- `re`: Regular expression pattern matching
- `pathlib`: Modern path manipulation (Path objects)
- `sys`: User input/output and exit handling
- `typing`: Type hints for maintainable code (optional but recommended)

**No External Dependencies**: The feature can be implemented entirely with Python's standard library, maintaining the project's lightweight nature.

### Use Case: Organizing Downloaded YouTube Videos

**Scenario**: A user downloads a 20-video Python tutorial playlist from YouTube. The downloaded files have names like:

```
Python Tutorial Part 1 - Introduction to Variables-abc123XYZ.mp4
Python Tutorial Part 2 - Understanding Lists-def456ABC.mp4
Learn Python - Part 3  Data Types Explained-ghi789DEF.mp4
...
```

**Problems**:
- Inconsistent naming patterns ("Part 1" vs "- Part 3")
- YouTube video IDs appended to filenames
- Varying use of hyphens and spaces
- Difficult to sort naturally in file explorers

**Solution with Batch Rename**:

1. **Step 1 - Remove YouTube IDs** (Regex Replace):
   - Pattern: `-[a-zA-Z0-9]{11}\.mp4$`
   - Replacement: `.mp4`
   - Result: Removes the YouTube video ID suffix

2. **Step 2 - Standardize Format** (Find and Replace):
   - Find: "Python Tutorial Part"
   - Replace: "Tutorial"
   - Result: Consistent prefix for all files

3. **Step 3 - Apply Sequential Numbering**:
   - Base name: "Python_Tutorial"
   - Format: `Python_Tutorial_{number:02d}.mp4`
   - Result: `Python_Tutorial_01.mp4`, `Python_Tutorial_02.mp4`, etc.

**Final Result**:
```
Python_Tutorial_01.mp4
Python_Tutorial_02.mp4
Python_Tutorial_03.mp4
...
Python_Tutorial_20.mp4
```

Clean, consistent, properly sorted filenames that are easy to navigate and understand at a glance.

### Integration with YouTube Downloader CLI

The batch rename feature would integrate seamlessly with the existing `youtube_Download-cli.py`:

1. **Post-Download Option**: After successfully downloading videos, prompt user: "Would you like to rename the downloaded files? (yes/no)"

2. **Standalone Mode**: Can also be invoked independently for organizing existing file collections

3. **Shared Directory Context**: Use the same download directory as the YouTube downloader, reducing configuration overhead

4. **Consistent CLI Interface**: Follow the same interactive prompt style used in the existing downloader for familiar user experience

---

*This documentation is part of a comparative analysis for enhancing the YouTube Downloader CLI utility.*
