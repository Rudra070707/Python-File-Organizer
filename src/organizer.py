from pathlib import Path
import shutil


# ---------------------------------------------------------------------------
# File categories
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Special compound extensions
# ---------------------------------------------------------------------------

COMPOUND_EXTENSIONS = {
    ".tar.gz",
    ".tar.bz2",
    ".tar.xz",
}


# ---------------------------------------------------------------------------
# Precomputed extension lookup
# ---------------------------------------------------------------------------

EXTENSION_TO_CATEGORY = {
    extension: category
    for category, extensions in FILE_CATEGORIES.items()
    for extension in extensions
}


# ---------------------------------------------------------------------------
# Category detection
# ---------------------------------------------------------------------------

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

    filename = file_path.name.lower()

    # Check compound extensions first.
    for extension in COMPOUND_EXTENSIONS:
        if filename.endswith(extension):
            return "Archives"

    # Check normal extension.
    extension = file_path.suffix.lower()

    return EXTENSION_TO_CATEGORY.get(
        extension,
        "Others",
    )


# ---------------------------------------------------------------------------
# Folder scanning
# ---------------------------------------------------------------------------

def get_files(folder):
    """
    Return regular files directly inside the selected folder.

    Subdirectories are ignored.

    Symbolic links are ignored to avoid unexpectedly moving files
    located outside the selected folder.
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

    files = []

    for item in folder.iterdir():
        if item.is_symlink():
            continue

        if item.is_file():
            files.append(item)

    # Stable ordering makes previews, testing, and operation
    # results predictable.
    files.sort(
        key=lambda path: path.name.casefold()
    )

    return files


# ---------------------------------------------------------------------------
# Unique filename generation
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Organization
# ---------------------------------------------------------------------------

def organize_folder(folder):
    """
    Organize files in a folder into category subdirectories.

    Returns a list describing every successful move.

    Files keep their original filename unless a file with the
    same name already exists in the destination category folder.
    In that case, a unique filename is generated.

    If a move fails after previous files have already been moved,
    the function attempts to restore those previous files before
    re-raising the original filesystem error.
    """
    folder = Path(folder)
    files = get_files(folder)

    moved_files = []

    try:
        for file_path in files:
            category = get_category(file_path)
            destination = folder / category

            destination.mkdir(
                exist_ok=True
            )

            # Preserve the original filename whenever possible.
            target = destination / file_path.name

            # Only generate a unique name when there is
            # actually a filename collision.
            if target.exists():
                target = get_unique_path(
                    destination,
                    file_path.name
                )

            shutil.move(
                str(file_path),
                str(target)
            )

            moved_files.append({
                "source": file_path,
                "destination": target,
                "category": category
            })

    except OSError:
        _rollback_moves(moved_files)
        raise

    return moved_files


# ---------------------------------------------------------------------------
# Rollback
# ---------------------------------------------------------------------------

def _rollback_moves(moved_files):
    """
    Best-effort rollback for a partially completed organization.

    A moved file is restored only when:

    - its destination still exists
    - its original source does not exist

    Existing source files are never overwritten.

    Any rollback error is intentionally ignored so that the original
    organization error can be re-raised to the caller.
    """

    for item in reversed(moved_files):
        source = Path(item["source"])
        destination = Path(item["destination"])

        if not destination.exists():
            continue

        if source.exists():
            continue

        try:
            source.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            shutil.move(
                str(destination),
                str(source),
            )

        except OSError:
            # Never hide the original organization failure.
            continue


# ---------------------------------------------------------------------------
# Undo
# ---------------------------------------------------------------------------

def undo_organization(moved_files):
    """
    Restore files from the most recent organization operation.

    Files are processed in reverse order.

    Existing files at the original location are never overwritten.

    Returns a list describing every successfully restored file.
    """

    if not moved_files:
        return []

    restored_files = []

    for item in reversed(moved_files):
        source = Path(item["source"])
        destination = Path(item["destination"])

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

        except OSError:
            # Continue attempting to restore the remaining files.
            continue

    return restored_files