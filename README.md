# Python File Organizer

A lightweight desktop application built with Python and Tkinter that automatically organizes files into categorized folders based on their file extensions.

The application provides a clean graphical interface for selecting a folder, previewing its contents, organizing files safely, and undoing the most recent organization operation.

It is designed to be simple, offline, dependency-free, and safe against accidental file overwrites.

---

## ✨ Features

- 🖥️ Clean graphical desktop interface
- 📁 Select any local folder
- 👀 Preview files before organizing
- 🗂️ Automatic file categorization
- 🔒 Safe duplicate filename handling
- ↩️ Undo the most recent organization operation
- 📦 Supports multiple common file types
- ❓ Unknown file types are placed in `Others`
- 🛡️ Prevents accidental overwriting of existing files
- 🔄 Rollback protection if organization encounters a filesystem error
- ⚡ Fast extension-based categorization
- ⌨️ Keyboard shortcuts
- 🌐 No internet connection required
- 📦 No third-party Python packages required
- 🧪 Automated unit test suite
- 🪟 Windows standalone executable available

---

## 📂 File Categories

| Category | Examples |
|---|---|
| **Images** | `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`, `.svg`, `.ico`, `.tiff` |
| **Documents** | `.pdf`, `.doc`, `.docx`, `.txt`, `.rtf`, `.odt`, `.xls`, `.xlsx`, `.csv`, `.ppt`, `.pptx` |
| **Videos** | `.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`, `.flv`, `.webm`, `.m4v` |
| **Music** | `.mp3`, `.wav`, `.aac`, `.flac`, `.ogg`, `.m4a`, `.wma` |
| **Archives** | `.zip`, `.rar`, `.7z`, `.tar`, `.gz`, `.bz2`, `.xz` |
| **Programs** | `.exe`, `.msi`, `.bat`, `.cmd`, `.sh`, `.py`, `.c`, `.cpp`, `.java`, `.js`, `.html`, `.css` |
| **Others** | File types not recognized by the organizer |

---

## 🖥️ Application Workflow

The application follows a simple workflow:

```text
Select Folder
     ↓
Preview Files
     ↓
Review Categories
     ↓
Organize Files
     ↓
Confirm Operation
     ↓
Files Moved Safely
     ↓
Undo if Required
```

---

## 🔍 Preview

Before moving anything, the application can generate a preview showing:

- Total number of files
- Number of files in each category
- Individual filenames
- The category assigned to each file

Example:

```text
File Organization Preview
==========================

Total files: 5

Category Summary
----------------
Images       1
Documents    1
Music        1
Videos       1
Others       1

Files
-----

photo.jpg
    → Images

document.pdf
    → Documents

song.mp3
    → Music
```

The preview does **not** modify any files.

---

## 🔒 Duplicate Filename Handling

Existing files are never overwritten.

If a destination already contains:

```text
photo.jpg
```

the organizer automatically generates:

```text
photo_1.jpg
```

If that also exists:

```text
photo_2.jpg
```

and so on until an available filename is found.

This behavior is also covered by the automated test suite.

---

## ↩️ Undo

The application records the most recent organization operation during the current application session.

After organizing files, **Undo** can restore the moved files to their original locations.

Important:

- Only the most recent organization operation can be undone.
- Undo history exists only during the current application session.
- Undo history is not persisted after closing the application.
- Existing files at the original location are never overwritten.

---

## 🛡️ Safe File Operations

The organizer is designed to avoid destructive file operations.

### Existing destination files

Existing files are never overwritten.

### Organization failure

If a filesystem error occurs after some files have already been moved, the application attempts to roll back previously completed moves.

### Undo conflicts

If a file already exists at its original location, the organizer does not overwrite it.

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl + O` | Select folder |
| `Ctrl + P` | Preview files |
| `Ctrl + Z` | Undo last organization |
| `Esc` | Clear current selection |

---

## 📥 Requirements

### Running from source

- Windows, Linux, or macOS
- Python 3.13 or compatible Python 3 version
- Tkinter

The application uses only Python's standard library.

No third-party Python packages are required to run the source version.

---

## 🚀 Running from Source

Clone or download the repository and open a terminal in the project root.

Run:

```powershell
python src\main.py
```

The File Organizer window will open.

---

## 📖 Basic Usage

1. Launch the application.
2. Click **Browse**.
3. Select the folder you want to organize.
4. Click **Preview**.
5. Review the detected categories.
6. Click **Organize Files**.
7. Confirm the operation.
8. Files are moved into their category folders.
9. Use **Undo** if you want to restore the most recent operation.

---

## 🪟 Windows Standalone EXE

A standalone Windows executable can be generated using PyInstaller.

The generated executable is:

```text
dist/
└── FileOrganizer/
    └── FileOrganizer.exe
```

The application can then be launched without manually running Python.

### Building the EXE

Install PyInstaller:

```powershell
python -m pip install pyinstaller
```

Build the application:

```powershell
pyinstaller --noconfirm --clean --windowed --name "FileOrganizer" --paths src src\main.py
```

The executable will be generated inside:

```text
dist\FileOrganizer\FileOrganizer.exe
```

### Current Build

The current tested Windows executable was successfully built and launched using:

```text
PyInstaller 6.22.2
Python 3.13.15
Windows 11
```

The tested executable size is approximately:

```text
1.87 MB
```

Generated PyInstaller files are intentionally excluded from Git using `.gitignore`.

---

## 🧪 Testing

The project uses Python's built-in `unittest` framework.

Run the complete test suite:

```powershell
python -m unittest discover -s tests -v
```

### Current Test Result

```text
Ran 24 tests

OK
```

All **24/24 tests pass**.

The test suite covers:

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

---

## 🔎 Syntax / Compilation Check

Run:

```powershell
python -m compileall src tests
```

A successful compilation indicates that the Python source files compile without syntax errors.

---

## 🏗️ Project Structure

```text
Python-File-Organizer/
│
├── src/
│   ├── main.py
│   ├── gui.py
│   └── organizer.py
│
├── tests/
│   └── test_organizer.py
│
├── .gitignore
└── README.md
```

### Source Files

#### `src/main.py`

Application entry point.

Starts the graphical user interface.

#### `src/gui.py`

Contains the Tkinter graphical interface.

Responsible for:

- Folder selection
- Preview generation
- Organization controls
- Undo controls
- Status messages
- Results display
- User confirmations
- Keyboard shortcuts
- Application lifecycle

#### `src/organizer.py`

Contains the core file-management logic:

- File categorization
- Extension lookup
- Folder scanning
- Unique filename generation
- File organization
- Rollback handling
- Undo operations

#### `tests/test_organizer.py`

Contains automated unit tests for the organizer logic.

---

## ⚙️ Technical Design

The project separates the graphical interface from the core file-management logic.

```text
                ┌─────────────────┐
                │    main.py      │
                │ Application     │
                │    Entry Point  │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │     gui.py      │
                │   Tkinter GUI   │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │  organizer.py   │
                │ Core File Logic │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │   File System   │
                └─────────────────┘
```

File categorization uses a precomputed extension lookup table so each file can be categorized directly without repeatedly scanning every category.

---

## 🎯 Design Goals

The project intentionally focuses on being:

- **Simple**
- **Useful**
- **Offline**
- **Fast**
- **Safe**
- **Maintainable**
- **Easy to understand**
- **Easy to test**
- **Dependency-free**
- **Protected against accidental overwrites**

---

## ⚠️ Limitations

- Undo only applies to the most recent organization operation.
- Undo history is not saved after closing the application.
- Files are categorized using their extensions.
- Files inside subdirectories are not recursively organized.
- Organization operates only on files directly inside the selected folder.
- The application does not automatically monitor folders for new files.

---

## 🧰 Technologies

- **Python**
- **Tkinter**
- **pathlib**
- **shutil**
- **collections.Counter**
- **unittest**
- **PyInstaller**

No external runtime dependencies are required.

---

## 📌 Project Status

**Version:** `1.0.0`

**Status:** Stable

The current version has been:

- Compiled successfully
- Tested with 24 automated unit tests
- Manually tested through the graphical interface
- Built successfully as a Windows executable
- Tested through the generated executable

---

## 📄 License

This project is intended for educational and personal use.