from pathlib import Path
import shutil


FILE_CATEGORIES = {
    "Images": {
        ".jpg", ".jpeg", ".png", ".gif", ".bmp",
        ".webp", ".svg", ".ico", ".tiff", ".tif"
    },
    "Documents": {
        ".pdf", ".doc", ".docx", ".txt", ".rtf",
        ".odt", ".xls", ".xlsx", ".csv", ".ppt", ".pptx"
    },
    "Videos": {
        ".mp4", ".mkv", ".avi", ".mov", ".wmv",
        ".flv", ".webm", ".m4v"
    },
    "Music": {
        ".mp3", ".wav", ".aac", ".flac", ".ogg",
        ".m4a", ".wma"
    },
    "Archives": {
        ".zip", ".rar", ".7z", ".tar", ".gz",
        ".bz2", ".xz"
    },
    "Programs": {
        ".exe", ".msi", ".bat", ".cmd", ".sh",
        ".py", ".c", ".cpp", ".java", ".js",
        ".html", ".css"
    }
}


# Precomputed extension lookup table.
# This avoids scanning every category for every file.
EXTENSION_TO_CATEGORY = {
    extension: category
    for category, extensions in FILE_CATEGORIES.items()
    for extension in extensions
}


def get_category(file_path):
    """
    Return the category for a file based on its extension.

    Unknown extensions are classified as "Others".
    Extension matching is case-insensitive.
    """
    file_path = Path(file_path)
    extension = file_path.suffix.lower()

    return EXTENSION_TO_CATEGORY.get(
        extension,
        "Others"
    )


def get_files(folder):
    """
    Return all files directly inside the selected folder.

    Subdirectories are intentionally ignored.
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

    return [
        item
        for item in folder.iterdir()
        if item.is_file()
    ]


def get_unique_path(folder, filename):
    """
    Return a unique path inside folder.

    Example:
        photo.jpg
        photo_1.jpg
        photo_2.jpg
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


def organize_folder(folder):
    """
    Organize files in a folder into category subdirectories.

    Returns a list describing every successful move.

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

            target = destination / file_path.name

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


def _rollback_moves(moved_files):
    """
    Best-effort rollback for an incomplete organization.

    Only moves a file back when:
    - the destination still exists
    - the original source does not exist

    Existing files at the original location are never overwritten.
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
                exist_ok=True
            )

            shutil.move(
                str(destination),
                str(source)
            )

        except OSError:
            # Do not hide the original organization error.
            # The caller will receive the original exception.
            continue


def undo_organization(moved_files):
    """
    Restore files from the most recent organization operation.

    Files are processed in reverse order.

    Existing files at the original location are never overwritten.
    """
    if not moved_files:
        return []

    restored_files = []

    for item in reversed(moved_files):
        source = Path(item["source"])
        destination = Path(item["destination"])

        # The organized file no longer exists.
        if not destination.exists():
            continue

        # Never overwrite an existing file.
        if source.exists():
            continue

        source.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        shutil.move(
            str(destination),
            str(source)
        )

        restored_files.append({
            "source": destination,
            "destination": source
        })

    return restored_files