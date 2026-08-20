from pathlib import Path
import shutil


# ============================================================================
# FILE CATEGORIES
# ============================================================================

FILE_CATEGORIES = {
    "Images": {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".webp",
        ".svg",
        ".ico",
        ".tiff",
        ".tif",
    },

    "Documents": {
        ".pdf",
        ".doc",
        ".docx",
        ".txt",
        ".rtf",
        ".odt",
        ".xls",
        ".xlsx",
        ".csv",
        ".ppt",
        ".pptx",
    },

    "Videos": {
        ".mp4",
        ".mkv",
        ".avi",
        ".mov",
        ".wmv",
        ".flv",
        ".webm",
        ".m4v",
    },

    "Music": {
        ".mp3",
        ".wav",
        ".aac",
        ".flac",
        ".ogg",
        ".m4a",
        ".wma",
    },

    "Archives": {
        ".zip",
        ".rar",
        ".7z",
        ".tar",
        ".gz",
        ".bz2",
        ".xz",
    },

    "Programs": {
        ".exe",
        ".msi",
        ".bat",
        ".cmd",
        ".sh",
        ".py",
        ".c",
        ".cpp",
        ".java",
        ".js",
        ".html",
        ".css",
    },
}


# ============================================================================
# SPECIAL COMPOUND EXTENSIONS
# ============================================================================

COMPOUND_EXTENSIONS = {
    ".tar.gz",
    ".tar.bz2",
    ".tar.xz",
}


# ============================================================================
# PRECOMPUTED EXTENSION LOOKUP
# ============================================================================

EXTENSION_TO_CATEGORY = {
    extension: category
    for category, extensions in FILE_CATEGORIES.items()
    for extension in extensions
}


# ============================================================================
# CATEGORY DETECTION
# ============================================================================

def get_category(file_path):
    """
    Return the category for a file based on its extension.

    Matching is case-insensitive.

    Compound archive extensions such as:
        .tar.gz
        .tar.bz2
        .tar.xz

    are supported.

    Unknown extensions are classified as "Others".
    """

    file_path = Path(file_path)

    filename = file_path.name.casefold()

    # Check compound extensions first.
    for extension in COMPOUND_EXTENSIONS:
        if filename.endswith(extension):
            return "Archives"

    # Check normal extension.
    extension = file_path.suffix.casefold()

    return EXTENSION_TO_CATEGORY.get(
        extension,
        "Others",
    )


# ============================================================================
# FOLDER VALIDATION
# ============================================================================

def _validate_folder(folder):
    """
    Validate and normalize a folder path.

    Returns:
        Path: validated folder path.

    Raises:
        FileNotFoundError:
            If the folder does not exist.

        NotADirectoryError:
            If the supplied path is not a directory.

        PermissionError:
            If the folder cannot be accessed.
    """

    folder = Path(folder)

    if not folder.exists():
        raise FileNotFoundError(
            "The selected folder does not exist."
        )

    if not folder.is_dir():
        raise NotADirectoryError(
            "The selected path is not a folder."
        )

    # Verify that the directory can actually be inspected.
    try:
        next(folder.iterdir(), None)
    except PermissionError:
        raise PermissionError(
            "Permission denied while accessing the selected folder."
        )

    return folder


# ============================================================================
# FOLDER SCANNING
# ============================================================================

def get_files(folder):
    """
    Return regular files directly inside the selected folder.

    Subdirectories are ignored.

    Symbolic links are ignored to avoid unexpectedly moving files
    located outside the selected folder.

    Files are returned in stable case-insensitive alphabetical order.
    """

    folder = _validate_folder(folder)

    files = []

    try:
        for item in folder.iterdir():

            # Never follow symbolic links.
            if item.is_symlink():
                continue

            # Only process regular files.
            if item.is_file():
                files.append(item)

    except PermissionError:
        raise PermissionError(
            "Permission denied while reading the selected folder."
        )

    except OSError as error:
        raise OSError(
            f"Could not read the selected folder: {error}"
        ) from error

    # Stable ordering makes previews, testing, and operation
    # results predictable.
    files.sort(
        key=lambda path: path.name.casefold()
    )

    return files


# ============================================================================
# UNIQUE FILENAME GENERATION
# ============================================================================

def get_unique_path(folder, filename):
    """
    Return a unique path inside folder.

    The original filename is never returned.

    Examples:

        photo.jpg
        -> photo_1.jpg

        photo.jpg with photo_1.jpg existing
        -> photo_2.jpg

        README with README_1 existing
        -> README_2
    """

    folder = Path(folder)
    original = Path(filename)

    counter = 1

    while True:
        new_name = (
            f"{original.stem}_{counter}"
            f"{original.suffix}"
        )

        candidate = folder / new_name

        if not candidate.exists():
            return candidate

        counter += 1


# ============================================================================
# SAFE DESTINATION PATH
# ============================================================================

def _get_destination_path(destination, filename):
    """
    Return the safest available destination path for a filename.

    The original filename is preserved whenever possible.

    If a collision exists, a unique filename is generated.
    """

    destination = Path(destination)
    filename = Path(filename)

    target = destination / filename.name

    if not target.exists():
        return target

    return get_unique_path(
        destination,
        filename.name,
    )


# ============================================================================
# ORGANIZATION
# ============================================================================

def organize_folder(folder):
    """
    Organize files in a folder into category subdirectories.

    Returns:
        list[dict]:
            Information about every successfully moved file.

    Each dictionary contains:

        source
            Original file path.

        destination
            Final destination path.

        category
            Category assigned to the file.

    Files keep their original filename whenever possible.

    If a filename collision occurs, a safe suffix is added.

    If a move fails after previous files have already been moved,
    the function attempts to restore those previous files before
    re-raising the original filesystem error.

    Existing files are never overwritten.
    """

    folder = _validate_folder(folder)

    files = get_files(folder)

    moved_files = []

    try:

        for file_path in files:

            # Determine category before creating anything.
            category = get_category(file_path)

            destination = folder / category

            # Create category folder only when necessary.
            destination.mkdir(
                exist_ok=True
            )

            # Calculate a collision-safe destination.
            target = _get_destination_path(
                destination,
                file_path.name,
            )

            # Move the file.
            shutil.move(
                str(file_path),
                str(target),
            )

            # Record successful move only AFTER the move succeeds.
            moved_files.append(
                {
                    "source": file_path,
                    "destination": target,
                    "category": category,
                }
            )

    except (OSError, shutil.Error):

        # Attempt to restore every file that was successfully moved
        # before the failure occurred.
        _rollback_moves(
            moved_files
        )

        # Re-raise the original error.
        raise

    return moved_files


# ============================================================================
# ROLLBACK
# ============================================================================

def _rollback_moves(moved_files):
    """
    Best-effort rollback for a partially completed organization.

    A moved file is restored only when:

    - its destination still exists
    - its original source does not exist

    Existing source files are never overwritten.

    Rollback errors are intentionally ignored so the original
    organization failure can be re-raised to the caller.
    """

    for item in reversed(moved_files):

        source = Path(
            item["source"]
        )

        destination = Path(
            item["destination"]
        )

        # Destination no longer exists.
        if not destination.exists():
            continue

        # Never overwrite an existing source file.
        if source.exists():
            continue

        try:

            source.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            # If another process created the source between
            # the existence check and this move, avoid overwriting it.
            if source.exists():
                continue

            shutil.move(
                str(destination),
                str(source),
            )

        except (OSError, shutil.Error):
            # Never hide the original organization failure.
            continue


# ============================================================================
# UNDO
# ============================================================================

def undo_organization(moved_files):
    """
    Restore files from the most recent organization operation.

    Files are processed in reverse order.

    Existing files at the original location are never overwritten.

    Missing destination files are skipped.

    If a destination filename is unexpectedly occupied by another file,
    the file is NOT overwritten.

    Returns:
        list[dict]:
            Information about every successfully restored file.

    Each dictionary contains:

        source
            Previous organized location.

        destination
            Original location.
    """

    if not moved_files:
        return []

    restored_files = []

    for item in reversed(moved_files):

        source = Path(
            item["source"]
        )

        destination = Path(
            item["destination"]
        )

        # The organized file has already disappeared.
        if not destination.exists():
            continue

        # Never overwrite an existing source file.
        if source.exists():
            continue

        try:

            source.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            # Re-check immediately before moving.
            # This protects against a file appearing at the
            # original location after the first check.
            if source.exists():
                continue

            shutil.move(
                str(destination),
                str(source),
            )

            restored_files.append(
                {
                    "source": destination,
                    "destination": source,
                }
            )

        except (OSError, shutil.Error):
            # Continue attempting to restore remaining files.
            continue

    return restored_files