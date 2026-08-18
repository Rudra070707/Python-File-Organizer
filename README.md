# Python File Organizer

A simple desktop application built with Python that automatically organizes files into categories based on their file extensions.

The application provides a graphical interface for selecting a folder, previewing how files will be categorized, organizing them, and undoing the most recent organization operation.

## Features

- Graphical desktop interface
- Select any local folder
- Preview files before moving them
- Automatically categorize files by extension
- Safely handle duplicate filenames
- Undo the most recent organization operation
- Handles unknown file types using an `Others` category
- Input and file-system error handling
- No internet connection required
- No external Python packages required
- Automated unit test suite

## File Categories

| Category | Examples |
|---|---|
| Images | `.jpg`, `.png`, `.gif`, `.svg`, `.webp` |
| Documents | `.pdf`, `.docx`, `.txt`, `.xlsx`, `.pptx` |
| Videos | `.mp4`, `.mkv`, `.avi`, `.mov`, `.webm` |
| Music | `.mp3`, `.wav`, `.flac`, `.ogg`, `.m4a` |
| Archives | `.zip`, `.rar`, `.7z`, `.tar`, `.gz` |
| Programs | `.exe`, `.py`, `.c`, `.cpp`, `.java`, `.js`, `.html` |
| Others | File types not recognized by the organizer |

## Project Structure

```text
```text
Python-File-Organizer/
|
+-- src/
|   +-- main.py
|   +-- gui.py
|   `-- organizer.py
|
+-- tests/
|   `-- test_organizer.py
|
+-- .gitignore
`-- README.md
```

### Source Files

#### `src/main.py`

Application entry point.

Starts the graphical user interface.

#### `src/gui.py`

Contains the Tkinter graphical interface and connects user actions to the organizer logic.

#### `src/organizer.py`

Contains the core file-management logic:

- File categorization
- Folder scanning
- Duplicate filename handling
- File organization
- Undo operations

#### `tests/test_organizer.py`

Contains automated unit tests for the organizer logic.

## Requirements

- Windows, Linux, or macOS
- Python 3.13 or compatible Python 3 version
- Tkinter

The application uses only Python's standard library.

No `pip install` is required.

## Running the Application

From the project root:

```powershell
python src\main.py
```

The File Organizer window will open.

### Basic Usage

1. Click **Browse**.
2. Select the folder you want to organize.
3. Click **Preview**.
4. Review the detected categories.
5. Click **Organize Files**.
6. Confirm the operation.
7. Use **Undo** if you want to restore the files.

## Duplicate Files

If a file with the same name already exists in a destination category, the application does not overwrite it.

For example:

```text
photo.jpg
photo_1.jpg
photo_2.jpg
```

The organizer automatically finds the next available filename.

## Undo

The application keeps track of the most recent organization operation during the current application session.

After organizing files, clicking **Undo** restores the moved files to their original locations.

Undo does not persist after the application is closed.

## Testing

The project contains an automated unit test suite using Python's built-in `unittest` framework.

Run all tests from the project root:

```powershell
python -m unittest discover -s tests -v
```

The current test suite covers:

- File type categorization
- Uppercase extensions
- Unknown extensions
- Compound extensions
- Folder scanning
- Empty folders
- Invalid paths
- Unique filename generation
- Duplicate filenames
- File organization
- Organization results
- Undo operations
- Missing undo destinations
- Protection against overwriting existing files

## Syntax / Compilation Check

To check the project for Python syntax errors:

```powershell
python -m compileall src tests
```

## Design Goals

The project intentionally focuses on being:

- Simple
- Useful
- Offline
- Easy to understand
- Easy to maintain
- Safe against accidental overwrites
- Fully testable
- Free from unnecessary dependencies

## Limitations

- Undo only applies to the most recent organization operation.
- Undo history is not saved after closing the application.
- Files are categorized using their extensions.
- The application organizes files within the selected folder and does not recursively organize files inside subfolders.

## License

This project is intended for educational and personal use.