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


def get_category(file_path):
    extension = file_path.suffix.lower()

    for category, extensions in FILE_CATEGORIES.items():
        if extension in extensions:
            return category

    return "Others"


def get_files(folder):
    folder = Path(folder)

    if not folder.exists():
        raise FileNotFoundError("The selected folder does not exist.")

    if not folder.is_dir():
        raise NotADirectoryError("The selected path is not a folder.")

    return [
        item for item in folder.iterdir()
        if item.is_file()
    ]


def get_unique_path(folder, filename):
    original = Path(filename)
    counter = 1

    while True:
        new_name = f"{original.stem}_{counter}{original.suffix}"
        candidate = folder / new_name

        if not candidate.exists():
            return candidate

        counter += 1


def organize_folder(folder):
    folder = Path(folder)
    files = get_files(folder)

    moved_files = []

    for file_path in files:
        category = get_category(file_path)
        destination = folder / category

        destination.mkdir(exist_ok=True)

        target = destination / file_path.name

        if target.exists():
            target = get_unique_path(
                destination,
                file_path.name
            )

        shutil.move(str(file_path), str(target))

        moved_files.append({
            "source": file_path,
            "destination": target,
            "category": category
        })

    return moved_files


def undo_organization(moved_files):
    if not moved_files:
        return []

    restored_files = []

    for item in reversed(moved_files):
        source = Path(item["source"])
        destination = Path(item["destination"])

        if not destination.exists():
            continue

        if source.exists():
            continue

        source.parent.mkdir(parents=True, exist_ok=True)

        shutil.move(
            str(destination),
            str(source)
        )

        restored_files.append({
            "source": destination,
            "destination": source
        })

    return restored_files