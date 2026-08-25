"""
File Organizer - Comprehensive Organizer Test Suite

This module validates the filesystem logic used by the File Organizer
application.

Test coverage includes:
    - File category detection.
    - Case-insensitive extensions.
    - Compound archive extensions.
    - Files without extensions.
    - Hidden files.
    - Folder scanning.
    - Directory and symbolic-link safety.
    - Stable file ordering.
    - Unique filename generation.
    - Filename collision handling.
    - File organization.
    - Content preservation.
    - Non-recursive processing.
    - Rollback after partial failures.
    - Undo operations.
    - Existing-file protection.
    - Filesystem error handling.
    - String and Path compatibility.

The tests intentionally preserve the existing public API and behavior.
"""

from __future__ import annotations

import shutil
import tempfile
import unittest

from pathlib import Path
from unittest.mock import Mock, patch

from src.organizer import (
    CATEGORY_ORDER,
    COMPOUND_EXTENSIONS,
    EXTENSION_TO_CATEGORY,
    FILE_CATEGORIES,
    _is_safe_destination_file,
    _is_safe_regular_file,
    _path_exists,
    _record_paths,
    _rollback_moves,
    _safe_category_directory,
    _split_filename,
    get_category,
    get_files,
    get_unique_path,
    organize_folder,
    undo_organization,
)

# ============================================================================
# TEST HELPERS
# ============================================================================


def remove_path(path: Path) -> None:
    """
    Remove a file, directory, or symbolic link if it exists.

    This helper is used only for test cleanup.
    """
    try:
        if path.is_symlink() or path.is_file():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)
    except FileNotFoundError:
        pass


def create_file(
    folder: Path,
    filename: str,
    content: str = "",
) -> Path:
    """
    Create a test file and return its path.
    """
    path = folder / filename
    path.write_text(content, encoding="utf-8")
    return path


# ============================================================================
# CATEGORY TESTS
# ============================================================================


class TestGetCategory(unittest.TestCase):
    def test_image_file(self):
        self.assertEqual(
            get_category(Path("photo.jpg")),
            "Images",
        )

    def test_document_file(self):
        self.assertEqual(
            get_category(Path("report.pdf")),
            "Documents",
        )

    def test_video_file(self):
        self.assertEqual(
            get_category(Path("movie.mp4")),
            "Videos",
        )

    def test_music_file(self):
        self.assertEqual(
            get_category(Path("song.mp3")),
            "Music",
        )

    def test_archive_file(self):
        self.assertEqual(
            get_category(Path("backup.zip")),
            "Archives",
        )

    def test_program_file(self):
        self.assertEqual(
            get_category(Path("program.py")),
            "Programs",
        )

    def test_unknown_file(self):
        self.assertEqual(
            get_category(Path("unknown.xyz")),
            "Others",
        )

    def test_uppercase_extension(self):
        self.assertEqual(
            get_category(Path("PHOTO.JPG")),
            "Images",
        )

    def test_compound_archive_extension(self):
        self.assertEqual(
            get_category(Path("backup.tar.gz")),
            "Archives",
        )

    def test_tar_bz2_archive(self):
        self.assertEqual(
            get_category(Path("backup.tar.bz2")),
            "Archives",
        )

    def test_tar_xz_archive(self):
        self.assertEqual(
            get_category(Path("backup.tar.xz")),
            "Archives",
        )

    def test_file_without_extension(self):
        self.assertEqual(
            get_category(Path("README")),
            "Others",
        )

    def test_hidden_file(self):
        self.assertEqual(
            get_category(Path(".gitignore")),
            "Others",
        )

    def test_extension_with_mixed_case(self):
        self.assertEqual(
            get_category(Path("PHOTO.JpG")),
            "Images",
        )

    def test_path_object_with_nested_path(self):
        self.assertEqual(
            get_category(Path("some_folder") / "photo.PNG"),
            "Images",
        )

    def test_unknown_compound_extension(self):
        self.assertEqual(
            get_category(Path("archive.tar.unknown")),
            "Others",
        )

    def test_all_registered_extensions_have_categories(self):
        for category, extensions in FILE_CATEGORIES.items():
            for extension in extensions:
                with self.subTest(
                    category=category,
                    extension=extension,
                ):
                    self.assertEqual(
                        get_category(Path(f"example{extension}")),
                        category,
                    )

    def test_registered_extensions_are_case_insensitive(self):
        for category, extensions in FILE_CATEGORIES.items():
            for extension in extensions:
                uppercase_extension = extension.upper()

                with self.subTest(
                    category=category,
                    extension=extension,
                ):
                    self.assertEqual(
                        get_category(Path(f"example{uppercase_extension}")),
                        category,
                    )

    def test_compound_extensions_are_case_insensitive(self):
        for extension in COMPOUND_EXTENSIONS:
            with self.subTest(extension=extension):
                self.assertEqual(
                    get_category(Path(f"backup{extension.upper()}")),
                    "Archives",
                )

    def test_filename_with_multiple_dots(self):
        self.assertEqual(
            get_category(Path("my.final.photo.jpg")),
            "Images",
        )

    def test_filename_with_dot_in_parent_directory(self):
        self.assertEqual(
            get_category(Path("folder.with.dots") / "report.pdf"),
            "Documents",
        )

    def test_directory_like_name_does_not_matter(self):
        self.assertEqual(
            get_category(Path("folder") / "archive.tar.gz"),
            "Archives",
        )

    def test_empty_suffix_is_others(self):
        self.assertEqual(
            get_category(Path("filename")),
            "Others",
        )

    def test_dot_only_filename_is_others(self):
        self.assertEqual(
            get_category(Path(".")),
            "Others",
        )

    def test_extension_lookup_matches_public_mapping(self):
        for extension, category in EXTENSION_TO_CATEGORY.items():
            with self.subTest(
                extension=extension,
                category=category,
            ):
                self.assertEqual(
                    get_category(Path(f"test{extension}")),
                    category,
                )


# ============================================================================
# GET FILES TESTS
# ============================================================================


class TestGetFiles(unittest.TestCase):
    def test_returns_only_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            (folder / "photo.jpg").touch()
            (folder / "document.pdf").touch()
            (folder / "subfolder").mkdir()

            files = get_files(folder)

            file_names = {file.name for file in files}

            self.assertEqual(
                file_names,
                {
                    "photo.jpg",
                    "document.pdf",
                },
            )

    def test_empty_folder(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            files = get_files(temp_dir)

            self.assertEqual(
                files,
                [],
            )

    def test_missing_folder(self):
        missing_folder = (
            Path(tempfile.gettempdir()) / "python_file_organizer_folder_that_does_not_exist"
        )

        remove_path(missing_folder)

        with self.assertRaises(FileNotFoundError):
            get_files(missing_folder)

    def test_path_is_not_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "file.txt"
            file_path.touch()

            with self.assertRaises(NotADirectoryError):
                get_files(file_path)

    def test_accepts_path_object(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            file_path = folder / "photo.jpg"
            file_path.touch()

            files = get_files(folder)

            self.assertEqual(
                files,
                [file_path],
            )

    def test_accepts_string_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            file_path = folder / "photo.jpg"
            file_path.touch()

            files = get_files(str(folder))

            self.assertEqual(
                files,
                [file_path],
            )

    def test_files_are_sorted_case_insensitively(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            (folder / "zebra.txt").touch()
            (folder / "Apple.txt").touch()
            (folder / "banana.txt").touch()

            files = get_files(folder)

            self.assertEqual(
                [file.name for file in files],
                [
                    "Apple.txt",
                    "banana.txt",
                    "zebra.txt",
                ],
            )

    def test_ignores_directories(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            (folder / "document.pdf").touch()
            (folder / "Documents").mkdir()
            (folder / "Images").mkdir()

            files = get_files(folder)

            self.assertEqual(
                files,
                [folder / "document.pdf"],
            )

    def test_ignores_symbolic_files_when_supported(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            real_file = folder / "real.txt"
            real_file.touch()

            link = folder / "linked.txt"

            try:
                link.symlink_to(real_file)
            except (OSError, NotImplementedError):
                self.skipTest("Symbolic links are not available.")

            files = get_files(folder)

            self.assertEqual(
                files,
                [real_file],
            )

    def test_get_files_permission_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            with (
                patch(
                    "src.organizer.Path.iterdir",
                    side_effect=PermissionError("Permission denied"),
                ),
                self.assertRaises(PermissionError),
            ):
                get_files(folder)

    def test_get_files_os_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            with (
                patch(
                    "src.organizer.Path.iterdir",
                    side_effect=OSError("Filesystem failure"),
                ),
                self.assertRaises(OSError) as context,
            ):
                get_files(folder)

            self.assertIn(
                "Could not read the selected folder",
                str(context.exception),
            )

    def test_nested_files_are_not_returned(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            nested = folder / "nested"
            nested.mkdir()

            (nested / "hidden.jpg").touch()
            (folder / "visible.jpg").touch()

            files = get_files(folder)

            self.assertEqual(
                files,
                [folder / "visible.jpg"],
            )

    def test_hidden_regular_file_is_returned(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            hidden = folder / ".secret"
            hidden.touch()

            files = get_files(folder)

            self.assertEqual(
                files,
                [hidden],
            )

    def test_many_files_are_sorted_deterministically(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            names = [
                "z.txt",
                "A.txt",
                "m.txt",
                "B.txt",
                "a.txt",
            ]

            for name in names:
                (folder / name).touch()

            files = get_files(folder)

            actual_names = [file.name for file in files]

            # Windows normally uses a case-insensitive filesystem, so
            # "A.txt" and "a.txt" cannot exist as two independent files.
            # Build the expected result from the files that actually exist.
            expected_names = sorted(
                {file.name for file in folder.iterdir() if file.is_file()},
                key=str.casefold,
            )

            self.assertEqual(
                actual_names,
                expected_names,
            )


# ============================================================================
# UNIQUE PATH TESTS
# ============================================================================


class TestGetUniquePath(unittest.TestCase):
    def test_returns_unique_filename(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            result = get_unique_path(
                folder,
                "photo.jpg",
            )

            self.assertEqual(
                result,
                folder / "photo_1.jpg",
            )

    def test_skips_existing_names(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            (folder / "photo_1.jpg").touch()
            (folder / "photo_2.jpg").touch()

            result = get_unique_path(
                folder,
                "photo.jpg",
            )

            self.assertEqual(
                result,
                folder / "photo_3.jpg",
            )

    def test_unique_name_without_extension(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            result = get_unique_path(
                folder,
                "README",
            )

            self.assertEqual(
                result,
                folder / "README_1",
            )

    def test_original_name_is_not_returned_when_it_exists(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            (folder / "photo.jpg").touch()

            result = get_unique_path(
                folder,
                "photo.jpg",
            )

            self.assertNotEqual(
                result,
                folder / "photo.jpg",
            )

            self.assertEqual(
                result,
                folder / "photo_1.jpg",
            )

    def test_multiple_existing_names_are_skipped(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            for number in range(1, 6):
                (folder / f"file_{number}.txt").touch()

            result = get_unique_path(
                folder,
                "file.txt",
            )

            self.assertEqual(
                result,
                folder / "file_6.txt",
            )

    def test_path_object_filename(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            result = get_unique_path(
                folder,
                Path("photo.jpg"),
            )

            self.assertEqual(
                result,
                folder / "photo_1.jpg",
            )

    def test_collision_with_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            (folder / "photo_1.jpg").mkdir()

            result = get_unique_path(
                folder,
                "photo.jpg",
            )

            self.assertEqual(
                result,
                folder / "photo_2.jpg",
            )

    def test_collision_with_symbolic_link_when_supported(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            target = folder / "target.txt"
            target.touch()

            link = folder / "photo_1.jpg"

            try:
                link.symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("Symbolic links are not available.")

            result = get_unique_path(
                folder,
                "photo.jpg",
            )

            self.assertEqual(
                result,
                folder / "photo_2.jpg",
            )

    def test_compound_extension_preserves_filename_suffix_behavior(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            result = get_unique_path(
                folder,
                "backup.tar.gz",
            )

            self.assertEqual(
                result,
                folder / "backup.tar_1.gz",
            )

# ============================================================================
# FILENAME SPLITTING TESTS
# ============================================================================


class TestSplitFilename(unittest.TestCase):
    def test_compound_extension(self):
        self.assertEqual(
            _split_filename("archive.tar.gz"),
            ("archive", ".tar.gz"),
        )

    def test_second_compound_extension(self):
        self.assertEqual(
            _split_filename("backup.tar.bz2"),
            ("backup", ".tar.bz2"),
        )

    def test_compound_extension_is_case_insensitive(self):
        self.assertEqual(
            _split_filename("BACKUP.TAR.GZ"),
            ("BACKUP", ".TAR.GZ"),
        )

    def test_regular_extension(self):
        self.assertEqual(
            _split_filename("photo.jpg"),
            ("photo", ".jpg"),
        )

    def test_filename_without_extension(self):
        self.assertEqual(
            _split_filename("README"),
            ("README", ""),
        )

    def test_multiple_dots_without_known_compound_extension(self):
        self.assertEqual(
            _split_filename("report.final.pdf"),
            ("report.final", ".pdf"),
        )
# ============================================================================
# ORGANIZATION TESTS
# ============================================================================


class TestOrganizeFolder(unittest.TestCase):
    def test_organizes_files_into_categories(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            (folder / "photo.jpg").touch()
            (folder / "document.pdf").touch()
            (folder / "song.mp3").touch()
            (folder / "movie.mp4").touch()
            (folder / "archive.zip").touch()
            (folder / "program.py").touch()
            (folder / "unknown.xyz").touch()

            moved_files = organize_folder(folder)

            self.assertEqual(
                len(moved_files),
                7,
            )

            self.assertTrue((folder / "Images" / "photo.jpg").exists())

            self.assertTrue((folder / "Documents" / "document.pdf").exists())

            self.assertTrue((folder / "Music" / "song.mp3").exists())

            self.assertTrue((folder / "Videos" / "movie.mp4").exists())

            self.assertTrue((folder / "Archives" / "archive.zip").exists())

            self.assertTrue((folder / "Programs" / "program.py").exists())

            self.assertTrue((folder / "Others" / "unknown.xyz").exists())

            self.assertFalse((folder / "photo.jpg").exists())

    def test_organize_empty_folder(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            moved_files = organize_folder(temp_dir)

            self.assertEqual(
                moved_files,
                [],
            )

    def test_handles_duplicate_filename(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            images_folder = folder / "Images"
            images_folder.mkdir()

            existing_file = images_folder / "photo.jpg"
            existing_file.touch()

            source_file = folder / "photo.jpg"
            source_file.touch()

            moved_files = organize_folder(folder)

            self.assertEqual(
                len(moved_files),
                1,
            )

            self.assertTrue((images_folder / "photo_1.jpg").exists())

            self.assertTrue(existing_file.exists())

            self.assertFalse(source_file.exists())

    def test_returned_move_information_is_correct(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            source = folder / "document.pdf"
            source.touch()

            moved_files = organize_folder(folder)

            self.assertEqual(
                len(moved_files),
                1,
            )

            item = moved_files[0]

            self.assertEqual(
                item["source"],
                source,
            )

            self.assertEqual(
                item["category"],
                "Documents",
            )

            self.assertEqual(
                item["destination"],
                (folder / "Documents" / "document.pdf"),
            )

    def test_organize_does_not_process_subdirectories(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            subfolder = folder / "Subfolder"
            subfolder.mkdir()

            nested_file = subfolder / "photo.jpg"
            nested_file.touch()

            moved_files = organize_folder(folder)

            self.assertEqual(
                moved_files,
                [],
            )

            self.assertTrue(nested_file.exists())

    def test_organize_creates_only_required_category_folder(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            (folder / "photo.jpg").touch()

            organize_folder(folder)

            self.assertTrue((folder / "Images").is_dir())

            self.assertFalse((folder / "Documents").exists())

            self.assertFalse((folder / "Videos").exists())

            self.assertFalse((folder / "Music").exists())

    def test_organize_multiple_files_same_category(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            (folder / "photo1.jpg").touch()
            (folder / "photo2.png").touch()
            (folder / "photo3.gif").touch()

            moved_files = organize_folder(folder)

            self.assertEqual(
                len(moved_files),
                3,
            )

            images_folder = folder / "Images"

            self.assertTrue((images_folder / "photo1.jpg").exists())

            self.assertTrue((images_folder / "photo2.png").exists())

            self.assertTrue((images_folder / "photo3.gif").exists())

    def test_organize_accepts_string_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            source = folder / "document.pdf"
            source.touch()

            moved_files = organize_folder(str(folder))

            self.assertEqual(
                len(moved_files),
                1,
            )

            self.assertTrue((folder / "Documents" / "document.pdf").exists())

    def test_organize_missing_folder(self):
        missing_folder = (
            Path(tempfile.gettempdir()) / "python_file_organizer_organize_missing_folder"
        )

        remove_path(missing_folder)

        with self.assertRaises(FileNotFoundError):
            organize_folder(missing_folder)

    def test_organize_path_that_is_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "document.pdf"
            file_path.touch()

            with self.assertRaises(NotADirectoryError):
                organize_folder(file_path)

    def test_organize_failure_rolls_back_previous_moves(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            first_file = folder / "first.pdf"
            second_file = folder / "second.pdf"

            first_file.write_text(
                "first",
                encoding="utf-8",
            )
            second_file.write_text(
                "second",
                encoding="utf-8",
            )

            original_move = shutil.move
            call_count = 0

            def failing_move(
                source,
                destination,
            ):
                nonlocal call_count

                call_count += 1

                if call_count == 2:
                    raise OSError("Simulated move failure")

                return original_move(
                    source,
                    destination,
                )

            with (
                patch(
                    "src.organizer.shutil.move",
                    side_effect=failing_move,
                ),
                self.assertRaises(OSError),
            ):
                organize_folder(folder)

            self.assertTrue(first_file.exists())

            self.assertTrue(second_file.exists())

            self.assertEqual(
                first_file.read_text(encoding="utf-8"),
                "first",
            )

            self.assertEqual(
                second_file.read_text(encoding="utf-8"),
                "second",
            )
    def test_rollback_skips_invalid_history_entry(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            destination = folder / "Documents" / "document.pdf"
            destination.parent.mkdir()

            destination.touch()

            moved_files = [
                {},
                {
                    "source": None,
                    "destination": destination,
                },
                {
                    "source": folder / "document.pdf",
                },
            ]

            _rollback_moves(moved_files)

            self.assertTrue(
                destination.exists()
            )

    def test_rollback_skips_symbolic_destination(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            real_target = folder / "real.txt"
            real_target.touch()

            destination = folder / "Documents" / "document.pdf"
            destination.parent.mkdir()

            try:
                destination.symlink_to(real_target)
            except (OSError, NotImplementedError):
                self.skipTest("Symbolic links are not available.")

            source = folder / "document.pdf"

            moved_files = [
                {
                    "source": source,
                    "destination": destination,
                    "category": "Documents",
                }
            ]

            _rollback_moves(moved_files)

            self.assertTrue(destination.is_symlink())
            self.assertFalse(source.exists())
    def test_organize_move_failure_on_first_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            source = folder / "document.pdf"
            source.touch()

            with (
                patch(
                    "src.organizer.shutil.move",
                    side_effect=OSError("Simulated failure"),
                ),
                self.assertRaises(OSError),
            ):
                organize_folder(folder)

            self.assertTrue(source.exists())

    def test_organize_handles_shutil_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            source = folder / "document.pdf"
            source.touch()

            with (
                patch(
                    "src.organizer.shutil.move",
                    side_effect=shutil.Error("Simulated shutil failure"),
                ),
                self.assertRaises(shutil.Error),
            ):
                organize_folder(folder)

            self.assertTrue(source.exists())

    def test_organize_preserves_file_content(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            source = folder / "document.txt"
            content = "Important content."

            source.write_text(
                content,
                encoding="utf-8",
            )

            moved_files = organize_folder(folder)

            self.assertEqual(
                len(moved_files),
                1,
            )

            destination = folder / "Documents" / "document.txt"

            self.assertTrue(destination.exists())

            self.assertEqual(
                destination.read_text(encoding="utf-8"),
                content,
            )

    def test_organize_duplicate_multiple_times(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            images = folder / "Images"
            images.mkdir()

            (images / "photo.jpg").touch()
            (images / "photo_1.jpg").touch()
            (images / "photo_2.jpg").touch()

            source = folder / "photo.jpg"
            source.touch()

            moved_files = organize_folder(folder)

            self.assertEqual(
                len(moved_files),
                1,
            )

            self.assertTrue((images / "photo_3.jpg").exists())

    def test_organize_does_not_overwrite_existing_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            images = folder / "Images"
            images.mkdir()

            existing = images / "photo.jpg"
            existing.write_text(
                "existing",
                encoding="utf-8",
            )

            source = folder / "photo.jpg"
            source.write_text(
                "new",
                encoding="utf-8",
            )

            organize_folder(folder)

            self.assertEqual(
                existing.read_text(encoding="utf-8"),
                "existing",
            )

            self.assertTrue((images / "photo_1.jpg").exists())

    def test_rollback_skips_missing_destination(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            source = folder / "document.pdf"

            moved_files = [
                {
                    "source": source,
                    "destination": (folder / "Documents" / "document.pdf"),
                    "category": "Documents",
                }
            ]



            _rollback_moves(moved_files)

            self.assertFalse(source.exists())

    def test_rollback_does_not_overwrite_source(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            source = folder / "document.pdf"
            source.write_text(
                "original",
                encoding="utf-8",
            )

            destination_folder = folder / "Documents"
            destination_folder.mkdir()

            destination = destination_folder / "document.pdf"
            destination.write_text(
                "organized",
                encoding="utf-8",
            )

            moved_files = [
                {
                    "source": source,
                    "destination": destination,
                    "category": "Documents",
                }
            ]



            _rollback_moves(moved_files)

            self.assertEqual(
                source.read_text(encoding="utf-8"),
                "original",
            )

            self.assertEqual(
                destination.read_text(encoding="utf-8"),
                "organized",
            )

    def test_rollback_handles_move_failure(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            source = folder / "document.pdf"

            destination_folder = folder / "Documents"
            destination_folder.mkdir()

            destination = destination_folder / "document.pdf"
            destination.touch()

            moved_files = [
                {
                    "source": source,
                    "destination": destination,
                    "category": "Documents",
                }
            ]



            with patch(
                "src.organizer.shutil.move",
                side_effect=OSError("Rollback failure"),
            ):
                _rollback_moves(moved_files)

            self.assertTrue(destination.exists())

    def test_organize_preserves_unicode_filename(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            source = folder / "rÃ©sumÃ©.pdf"
            source.write_text(
                "Unicode filename test.",
                encoding="utf-8",
            )

            moved_files = organize_folder(folder)

            self.assertEqual(
                len(moved_files),
                1,
            )

            destination = folder / "Documents" / "rÃ©sumÃ©.pdf"

            self.assertTrue(destination.exists())

            self.assertEqual(
                destination.read_text(encoding="utf-8"),
                "Unicode filename test.",
            )

    def test_organize_preserves_empty_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            source = folder / "empty.txt"
            source.touch()

            organize_folder(folder)

            destination = folder / "Documents" / "empty.txt"

            self.assertTrue(destination.exists())

            self.assertEqual(
                destination.stat().st_size,
                0,
            )

    def test_organize_does_not_create_unused_categories(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            source = folder / "readme.txt"
            source.touch()

            organize_folder(folder)

            created_categories = {path.name for path in folder.iterdir() if path.is_dir()}

            self.assertEqual(
                created_categories,
                {"Documents"},
            )

    def test_organize_result_order_matches_scan_order(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            create_file(folder, "z.pdf", "z")
            create_file(folder, "A.pdf", "a")
            create_file(folder, "m.pdf", "m")

            moved_files = organize_folder(folder)

            self.assertEqual(
                [Path(item["source"]).name for item in moved_files],
                [
                    "A.pdf",
                    "m.pdf",
                    "z.pdf",
                ],
            )

    def test_organize_symbolic_file_is_ignored_when_supported(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            real_file = folder / "real.pdf"
            real_file.touch()

            link = folder / "linked.pdf"

            try:
                link.symlink_to(real_file)
            except (OSError, NotImplementedError):
                self.skipTest("Symbolic links are not available.")

            moved_files = organize_folder(folder)

            self.assertEqual(
                len(moved_files),
                1,
            )

            self.assertTrue((folder / "Documents" / "real.pdf").exists())

            self.assertTrue(link.is_symlink())

    def test_organize_existing_category_directory_is_reused(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            documents = folder / "Documents"
            documents.mkdir()

            source = folder / "report.pdf"
            source.touch()

            organize_folder(folder)

            self.assertTrue(documents.is_dir())

            self.assertTrue((documents / "report.pdf").exists())

    def test_organize_rejects_category_symlink_when_supported(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            outside = Path(tempfile.mkdtemp())
            self.addCleanup(
                shutil.rmtree,
                outside,
                ignore_errors=True,
            )

            documents_link = folder / "Documents"

            try:
                documents_link.symlink_to(
                    outside,
                    target_is_directory=True,
                )
            except (OSError, NotImplementedError):
                self.skipTest("Symbolic links are not available.")

            source = folder / "report.pdf"
            source.touch()

            with self.assertRaises(OSError):
                organize_folder(folder)

            self.assertTrue(source.exists())

            self.assertFalse((outside / "report.pdf").exists())

    def test_organize_does_not_overwrite_destination_after_collision_check(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            source = folder / "document.pdf"
            source.write_text(
                "source",
                encoding="utf-8",
            )

            documents = folder / "Documents"
            documents.mkdir()

            destination = documents / "document.pdf"

            def create_destination_then_move(
                source_path,
                destination_path,
            ):
                Path(destination_path).write_text(
                    "pre-existing",
                    encoding="utf-8",
                )

                raise OSError(
                    f"Destination appeared during move: {destination_path}"
                )

            with patch(
                "src.organizer.shutil.move",
                side_effect=create_destination_then_move,
            ):
                with self.assertRaises(OSError):
                    organize_folder(folder)

            self.assertTrue(source.exists())
            self.assertEqual(
                destination.read_text(encoding="utf-8"),
                "pre-existing",
            )

    def test_safe_category_directory_handles_os_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            with patch(
                "src.organizer.Path.mkdir",
                side_effect=OSError("Filesystem failure"),
            ):
                with self.assertRaises(OSError) as context:
                    _safe_category_directory(
                        folder,
                        "Documents",
                    )

            self.assertIn(
                "Could not create category directory",
                str(context.exception),
            )

    def test_category_order_preserves_expected_order(self):
        self.assertEqual(
            CATEGORY_ORDER,
            [
                "Images",
                "Documents",
                "Videos",
                "Music",
                "Archives",
                "Programs",
                "Others",
            ],
        )
    def test_get_unique_path_treats_broken_symlink_as_collision(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            broken_link = folder / "photo_1.jpg"
            missing_target = folder / "does_not_exist.txt"

            try:
                broken_link.symlink_to(missing_target)
            except (OSError, NotImplementedError):
                self.skipTest("Symbolic links are not available.")

            result = get_unique_path(
                folder,
                "photo.jpg",
            )

            self.assertEqual(
                result,
                folder / "photo_2.jpg",
            )
    def test_organize_rejects_broken_category_symlink(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            documents_link = folder / "Documents"
            missing_target = folder / "missing_documents"

            try:
                documents_link.symlink_to(
                    missing_target,
                    target_is_directory=True,
                )
            except (OSError, NotImplementedError):
                self.skipTest("Symbolic links are not available.")

            source = folder / "report.pdf"
            source.touch()

            with self.assertRaises(OSError):
                organize_folder(folder)

            self.assertTrue(source.exists())
    def test_organize_hidden_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            source = folder / ".hidden.txt"
            source.write_text(
                "hidden",
                encoding="utf-8",
            )

            moved_files = organize_folder(folder)

            self.assertEqual(
                len(moved_files),
                1,
            )

            destination = folder / "Documents" / ".hidden.txt"

            self.assertTrue(destination.exists())
            self.assertFalse(source.exists())
    def test_organize_compound_archive(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            source = folder / "backup.tar.gz"
            source.write_text(
                "archive test",
                encoding="utf-8",
            )

            moved_files = organize_folder(folder)

            self.assertEqual(
                len(moved_files),
                1,
            )

            destination = folder / "Archives" / "backup.tar.gz"

            self.assertTrue(destination.exists())
            self.assertEqual(
                destination.read_text(encoding="utf-8"),
                "archive test",
            )
    def test_organize_file_without_extension(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            source = folder / "README"
            source.write_text(
                "readme",
                encoding="utf-8",
            )

            moved_files = organize_folder(folder)

            self.assertEqual(
                len(moved_files),
                1,
            )

            destination = folder / "Others" / "README"

            self.assertTrue(destination.exists())
            self.assertFalse(source.exists())
# ============================================================================
# UNDO TESTS
# ============================================================================


class TestUndoOrganization(unittest.TestCase):
    def test_undo_restores_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            source = folder / "document.pdf"
            source.touch()

            moved_files = organize_folder(folder)

            self.assertFalse(source.exists())

            restored_files = undo_organization(moved_files)

            self.assertEqual(
                len(restored_files),
                1,
            )

            self.assertTrue(source.exists())

            self.assertFalse((folder / "Documents" / "document.pdf").exists())

    def test_undo_empty_list(self):
        restored_files = undo_organization([])

        self.assertEqual(
            restored_files,
            [],
        )

    def test_undo_none(self):
        restored_files = undo_organization(None)

        self.assertEqual(
            restored_files,
            [],
        )

    def test_undo_skips_missing_destination(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            source = folder / "document.pdf"

            destination = folder / "Documents" / "document.pdf"

            moved_files = [
                {
                    "source": source,
                    "destination": destination,
                    "category": "Documents",
                }
            ]

            restored_files = undo_organization(moved_files)

            self.assertEqual(
                restored_files,
                [],
            )

    def test_undo_does_not_overwrite_existing_source(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            source = folder / "document.pdf"

            destination_folder = folder / "Documents"
            destination_folder.mkdir()

            destination = destination_folder / "document.pdf"

            source.write_text(
                "original",
                encoding="utf-8",
            )
            destination.write_text(
                "organized",
                encoding="utf-8",
            )

            moved_files = [
                {
                    "source": source,
                    "destination": destination,
                    "category": "Documents",
                }
            ]

            restored_files = undo_organization(moved_files)

            self.assertEqual(
                restored_files,
                [],
            )

            self.assertTrue(source.exists())

            self.assertTrue(destination.exists())

            self.assertEqual(
                source.read_text(encoding="utf-8"),
                "original",
            )

            self.assertEqual(
                destination.read_text(encoding="utf-8"),
                "organized",
            )

    def test_undo_multiple_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            first = folder / "first.pdf"
            second = folder / "second.jpg"
            third = folder / "third.mp3"

            first.write_text(
                "first",
                encoding="utf-8",
            )
            second.write_text(
                "second",
                encoding="utf-8",
            )
            third.write_text(
                "third",
                encoding="utf-8",
            )

            moved_files = organize_folder(folder)

            self.assertEqual(
                len(moved_files),
                3,
            )

            restored_files = undo_organization(moved_files)

            self.assertEqual(
                len(restored_files),
                3,
            )

            self.assertTrue(first.exists())

            self.assertTrue(second.exists())

            self.assertTrue(third.exists())

    def test_undo_restores_file_content(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            source = folder / "document.txt"

            original_content = "Important test content."

            source.write_text(
                original_content,
                encoding="utf-8",
            )

            moved_files = organize_folder(folder)

            restored_files = undo_organization(moved_files)

            self.assertEqual(
                len(restored_files),
                1,
            )

            self.assertTrue(source.exists())

            self.assertEqual(
                source.read_text(encoding="utf-8"),
                original_content,
            )

    def test_undo_skips_when_source_parent_cannot_be_created(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            source = folder / "MissingFolder" / "document.pdf"

            destination_folder = folder / "Documents"
            destination_folder.mkdir()

            destination = destination_folder / "document.pdf"

            destination.touch()

            moved_files = [
                {
                    "source": source,
                    "destination": destination,
                    "category": "Documents",
                }
            ]

            with patch(
                "src.organizer.Path.mkdir",
                side_effect=PermissionError("Permission denied"),
            ):
                restored_files = undo_organization(moved_files)

            self.assertEqual(
                restored_files,
                [],
            )

            self.assertTrue(destination.exists())

    def test_undo_does_not_fail_when_destination_disappears(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            source = folder / "document.pdf"

            destination_folder = folder / "Documents"
            destination_folder.mkdir()

            destination = destination_folder / "document.pdf"

            destination.touch()

            moved_files = [
                {
                    "source": source,
                    "destination": destination,
                    "category": "Documents",
                }
            ]

            destination.unlink()

            restored_files = undo_organization(moved_files)

            self.assertEqual(
                restored_files,
                [],
            )

    def test_undo_move_failure_is_skipped(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            source = folder / "document.pdf"

            destination_folder = folder / "Documents"
            destination_folder.mkdir()

            destination = destination_folder / "document.pdf"

            destination.touch()

            moved_files = [
                {
                    "source": source,
                    "destination": destination,
                    "category": "Documents",
                }
            ]

            with patch(
                "src.organizer.shutil.move",
                side_effect=OSError("Simulated undo failure"),
            ):
                restored_files = undo_organization(moved_files)

            self.assertEqual(
                restored_files,
                [],
            )

            self.assertTrue(destination.exists())

    def test_undo_shutil_error_is_skipped(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            source = folder / "document.pdf"

            destination_folder = folder / "Documents"
            destination_folder.mkdir()

            destination = destination_folder / "document.pdf"

            destination.touch()

            moved_files = [
                {
                    "source": source,
                    "destination": destination,
                    "category": "Documents",
                }
            ]

            with patch(
                "src.organizer.shutil.move",
                side_effect=shutil.Error("Simulated shutil failure"),
            ):
                restored_files = undo_organization(moved_files)

            self.assertEqual(
                restored_files,
                [],
            )

            self.assertTrue(destination.exists())

    def test_undo_returns_correct_move_information(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            source = folder / "document.pdf"

            source.write_text(
                "content",
                encoding="utf-8",
            )

            moved_files = organize_folder(folder)

            destination = folder / "Documents" / "document.pdf"

            restored_files = undo_organization(moved_files)

            self.assertEqual(
                restored_files,
                [
                    {
                        "source": destination,
                        "destination": source,
                    }
                ],
            )

    def test_undo_processes_operations_in_reverse_order(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            first = create_file(
                folder,
                "first.txt",
                "first",
            )
            second = create_file(
                folder,
                "second.txt",
                "second",
            )

            moved_files = organize_folder(folder)

            restored_files = undo_organization(moved_files)

            self.assertEqual(
                len(restored_files),
                2,
            )

            self.assertTrue(first.exists())

            self.assertTrue(second.exists())

    def test_undo_accepts_generator(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            source = create_file(
                folder,
                "document.pdf",
                "content",
            )

            moved_files = organize_folder(folder)

            history_generator = (item for item in moved_files)

            restored_files = undo_organization(history_generator)

            self.assertEqual(
                len(restored_files),
                1,
            )

            self.assertTrue(source.exists())

    def test_undo_invalid_history_entry_is_skipped(self):
        restored_files = undo_organization(
            [
                {},
                {
                    "source": None,
                    "destination": None,
                },
            ]
        )

        self.assertEqual(
            restored_files,
            [],
        )

    def test_undo_does_not_restore_through_symbolic_source_when_supported(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            real_source = folder / "real.txt"
            real_source.touch()

            source_link = folder / "source.txt"

            try:
                source_link.symlink_to(real_source)
            except (OSError, NotImplementedError):
                self.skipTest("Symbolic links are not available.")

            destination_folder = folder / "Documents"
            destination_folder.mkdir()

            destination = destination_folder / "source.txt"
            destination.touch()

            moved_files = [
                {
                    "source": source_link,
                    "destination": destination,
                    "category": "Documents",
                }
            ]

            restored_files = undo_organization(moved_files)

            self.assertEqual(
                restored_files,
                [],
            )

            self.assertTrue(destination.exists())
    def test_undo_skips_broken_symbolic_source(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            source = folder / "source.txt"
            missing_target = folder / "missing.txt"

            try:
                source.symlink_to(missing_target)
            except (OSError, NotImplementedError):
                self.skipTest("Symbolic links are not available.")

            destination_folder = folder / "Documents"
            destination_folder.mkdir()

            destination = destination_folder / "source.txt"
            destination.touch()

            moved_files = [
                {
                    "source": source,
                    "destination": destination,
                    "category": "Documents",
                }
            ]

            restored_files = undo_organization(moved_files)

            self.assertEqual(
                restored_files,
                [],
            )

            self.assertTrue(source.is_symlink())
            self.assertTrue(destination.exists())
    def test_undo_skips_non_mapping_history_entries(self):
        restored_files = undo_organization(
            [
                None,
                "invalid",
                123,
                [],
                {},
            ]
        )

        self.assertEqual(
            restored_files,
            [],
        )
    def test_undo_restores_valid_entries_and_skips_invalid_entries(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            source = folder / "document.pdf"
            source.write_text(
                "content",
                encoding="utf-8",
            )

            moved_files = organize_folder(folder)

            history = [
                {},
                None,
                moved_files[0],
                {"source": None, "destination": None},
            ]

            restored_files = undo_organization(history)

            self.assertEqual(
                len(restored_files),
                1,
            )

            self.assertTrue(source.exists())
# ============================================================================
# MOVE RECORD TESTS
# ============================================================================

class TestRecordPaths(unittest.TestCase):
    """Tests for safe extraction of source/destination paths."""

    def test_valid_path_values(self):
        source = Path("source.txt")
        destination = Path("Documents") / "source.txt"

        result = _record_paths(
            {
                "source": source,
                "destination": destination,
            }
        )

        self.assertEqual(
            result,
            (source, destination),
        )

    def test_valid_string_values(self):
        result = _record_paths(
            {
                "source": "source.txt",
                "destination": "Documents/source.txt",
            }
        )

        self.assertEqual(
            result,
            (
                Path("source.txt"),
                Path("Documents/source.txt"),
            ),
        )

    def test_missing_source_returns_none(self):
        result = _record_paths(
            {
                "destination": "Documents/source.txt",
            }
        )

        self.assertIsNone(result)

    def test_missing_destination_returns_none(self):
        result = _record_paths(
            {
                "source": "source.txt",
            }
        )

        self.assertIsNone(result)

    def test_non_string_source_returns_none(self):
        result = _record_paths(
            {
                "source": 123,
                "destination": "Documents/source.txt",
            }
        )

        self.assertIsNone(result)

    def test_non_path_destination_returns_none(self):
        result = _record_paths(
            {
                "source": "source.txt",
                "destination": 123,
            }
        )

        self.assertIsNone(result)

    def test_none_source_returns_none(self):
        result = _record_paths(
            {
                "source": None,
                "destination": "Documents/source.txt",
            }
        )

        self.assertIsNone(result)

    def test_none_destination_returns_none(self):
        result = _record_paths(
            {
                "source": "source.txt",
                "destination": None,
            }
        )

        self.assertIsNone(result)

    def test_empty_mapping_returns_none(self):
        self.assertIsNone(
            _record_paths({})
        )

    def test_invalid_mapping_type_returns_none(self):
        self.assertIsNone(
            _record_paths(None)
        )

    def test_extra_fields_are_ignored(self):
        source = Path("source.txt")
        destination = Path("Documents") / "source.txt"

        result = _record_paths(
            {
                "source": source,
                "destination": destination,
                "category": "Documents",
                "extra": "ignored",
            }
        )

        self.assertEqual(
            result,
            (source, destination),
        )
# ============================================================================
# PUBLIC CONSTANT TESTS
# ============================================================================

class TestPublicConstants(unittest.TestCase):
    def test_category_order_contains_all_categories(self):
        expected_categories = set(FILE_CATEGORIES)
        expected_categories.add("Others")

        self.assertEqual(
            set(CATEGORY_ORDER),
            expected_categories,
        )

    def test_category_order_has_no_duplicates(self):
        self.assertEqual(
            len(CATEGORY_ORDER),
            len(set(CATEGORY_ORDER)),
        )

    def test_extension_lookup_is_casefolded(self):
        for extension in EXTENSION_TO_CATEGORY:
            self.assertEqual(
                extension,
                extension.casefold(),
            )

    def test_file_categories_are_non_empty(self):
        for category, extensions in FILE_CATEGORIES.items():
            with self.subTest(category=category):
                self.assertTrue(extensions)

    def test_all_extensions_begin_with_dot(self):
        for category, extensions in FILE_CATEGORIES.items():
            for extension in extensions:
                with self.subTest(
                    category=category,
                    extension=extension,
                ):
                    self.assertTrue(extension.startswith("."))
# ============================================================================
# SAFETY HELPER TESTS
# ============================================================================
class TestSafetyHelpers(unittest.TestCase):
    """Tests for the internal filesystem-safety helpers."""

    def test_is_safe_regular_file_rejects_symbolic_link(self):
        fake_path = Mock()
        fake_path.is_symlink.return_value = True

        self.assertFalse(_is_safe_regular_file(fake_path))
        fake_path.is_file.assert_not_called()

    def test_is_safe_regular_file_handles_os_error(self):
        fake_path = Mock()
        fake_path.is_symlink.side_effect = OSError("Filesystem failure")

        self.assertFalse(_is_safe_regular_file(fake_path))

    def test_is_safe_regular_file_accepts_regular_file(self):
        fake_path = Mock()
        fake_path.is_symlink.return_value = False
        fake_path.is_file.return_value = True

        self.assertTrue(_is_safe_regular_file(fake_path))
    def test_is_safe_regular_file_rejects_directory(self):
        fake_path = Mock()
        fake_path.is_symlink.return_value = False
        fake_path.is_file.return_value = False

        self.assertFalse(
            _is_safe_regular_file(fake_path)
        )
    def test_path_exists_returns_true_for_existing_path(self):
        fake_path = Mock()
        fake_path.exists.return_value = True
        fake_path.is_symlink.return_value = False

        self.assertTrue(_path_exists(fake_path))

    def test_path_exists_detects_symbolic_link(self):
        fake_path = Mock()
        fake_path.exists.return_value = False
        fake_path.is_symlink.return_value = True

        self.assertTrue(_path_exists(fake_path))

    def test_path_exists_handles_os_error(self):
        fake_path = Mock()
        fake_path.exists.side_effect = OSError("Filesystem failure")

        self.assertFalse(_path_exists(fake_path))
        
    def test_path_exists_returns_false_for_missing_path(self):
        fake_path = Mock()
        fake_path.exists.return_value = False
        fake_path.is_symlink.return_value = False

        self.assertFalse(
            _path_exists(fake_path)
        )

    def test_path_exists_returns_false_when_symlink_check_fails(self):
        fake_path = Mock()
        fake_path.exists.return_value = False
        fake_path.is_symlink.side_effect = OSError(
            "Filesystem failure"
        )

        self.assertFalse(
            _path_exists(fake_path)
        )
    def test_is_safe_destination_file_rejects_symbolic_link(self):
        fake_path = Mock()
        fake_path.is_symlink.return_value = True

        self.assertFalse(_is_safe_destination_file(fake_path))
        fake_path.is_file.assert_not_called()

    def test_is_safe_destination_file_handles_os_error(self):
        fake_path = Mock()
        fake_path.is_symlink.side_effect = OSError("Filesystem failure")

        self.assertFalse(_is_safe_destination_file(fake_path))

    def test_is_safe_destination_file_accepts_regular_file(self):
        fake_path = Mock()
        fake_path.is_symlink.return_value = False
        fake_path.is_file.return_value = True

        self.assertTrue(_is_safe_destination_file(fake_path))
    def test_is_safe_destination_file_rejects_directory(self):
        fake_path = Mock()
        fake_path.is_symlink.return_value = False
        fake_path.is_file.return_value = False

        self.assertFalse(
            _is_safe_destination_file(fake_path)
        )
    def test_safe_category_directory_creates_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            result = _safe_category_directory(
                folder,
                "Documents",
            )

            self.assertEqual(
                result,
                folder / "Documents",
            )
            self.assertTrue(result.is_dir())

    def test_safe_category_directory_rejects_existing_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            category_path = folder / "Documents"

            category_path.write_text("not a directory")

            with self.assertRaises(NotADirectoryError):
                _safe_category_directory(
                    folder,
                    "Documents",
                )

    def test_safe_category_directory_rejects_symbolic_link_before_creation(self):
        fake_destination = Mock()
        fake_destination.is_symlink.return_value = True

        with patch(
            "src.organizer.Path.__truediv__",
            return_value=fake_destination,
        ):
            with self.assertRaises(OSError):
                _safe_category_directory(
                    Path("."),
                    "Documents",
                )

    def test_safe_category_directory_handles_permission_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            with patch(
                "src.organizer.Path.mkdir",
                side_effect=PermissionError("Permission denied"),
            ):
                with self.assertRaises(PermissionError) as context:
                    _safe_category_directory(
                        folder,
                        "Documents",
                    )

            self.assertIn(
                "Permission denied while accessing category directory",
                str(context.exception),
            )

    def test_safe_category_directory_rejects_symbolic_link_after_creation(self):
        fake_destination = Mock()
        fake_destination.is_symlink.side_effect = [False, True]

        with patch(
            "src.organizer.Path.__truediv__",
            return_value=fake_destination,
        ):
            fake_destination.exists.return_value = False
            fake_destination.mkdir.return_value = None

            with self.assertRaises(OSError):
                _safe_category_directory(
                    Path("."),
                    "Documents",
                )

    def test_safe_category_directory_rejects_non_directory_after_creation(self):
        fake_destination = Mock()
        fake_destination.is_symlink.return_value = False
        fake_destination.exists.return_value = False
        fake_destination.is_dir.side_effect = [False, False]

        with patch(
            "src.organizer.Path.__truediv__",
            return_value=fake_destination,
        ):
            with self.assertRaises(NotADirectoryError):
                _safe_category_directory(
                    Path("."),
                    "Documents",
                )

# ============================================================================
# TEST RUNNER
# ============================================================================


if __name__ == "__main__":
    unittest.main()
