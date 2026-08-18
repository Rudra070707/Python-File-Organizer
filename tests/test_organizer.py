import tempfile
import unittest
from pathlib import Path

from src.organizer import (
    get_category,
    get_files,
    get_unique_path,
    organize_folder,
    undo_organization,
)


class TestGetCategory(unittest.TestCase):

    def test_image_file(self):
        self.assertEqual(
            get_category(Path("photo.jpg")),
            "Images"
        )

    def test_document_file(self):
        self.assertEqual(
            get_category(Path("report.pdf")),
            "Documents"
        )

    def test_video_file(self):
        self.assertEqual(
            get_category(Path("movie.mp4")),
            "Videos"
        )

    def test_music_file(self):
        self.assertEqual(
            get_category(Path("song.mp3")),
            "Music"
        )

    def test_archive_file(self):
        self.assertEqual(
            get_category(Path("backup.zip")),
            "Archives"
        )

    def test_program_file(self):
        self.assertEqual(
            get_category(Path("program.py")),
            "Programs"
        )

    def test_unknown_file(self):
        self.assertEqual(
            get_category(Path("unknown.xyz")),
            "Others"
        )

    def test_uppercase_extension(self):
        self.assertEqual(
            get_category(Path("PHOTO.JPG")),
            "Images"
        )

    def test_compound_archive_extension(self):
        self.assertEqual(
            get_category(Path("backup.tar.gz")),
            "Archives"
        )


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
                {"photo.jpg", "document.pdf"}
            )

    def test_empty_folder(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            files = get_files(temp_dir)

            self.assertEqual(files, [])

    def test_missing_folder(self):
        missing_folder = (
            Path(tempfile.gettempdir())
            / "python_file_organizer_folder_that_does_not_exist"
        )

        with self.assertRaises(FileNotFoundError):
            get_files(missing_folder)

    def test_path_is_not_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "file.txt"
            file_path.touch()

            with self.assertRaises(NotADirectoryError):
                get_files(file_path)


class TestGetUniquePath(unittest.TestCase):

    def test_returns_unique_filename(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            result = get_unique_path(
                folder,
                "photo.jpg"
            )

            self.assertEqual(
                result,
                folder / "photo_1.jpg"
            )

    def test_skips_existing_names(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            (folder / "photo_1.jpg").touch()
            (folder / "photo_2.jpg").touch()

            result = get_unique_path(
                folder,
                "photo.jpg"
            )

            self.assertEqual(
                result,
                folder / "photo_3.jpg"
            )

    def test_unique_name_without_extension(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            result = get_unique_path(
                folder,
                "README"
            )

            self.assertEqual(
                result,
                folder / "README_1"
            )


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

            self.assertEqual(len(moved_files), 7)

            self.assertTrue(
                (folder / "Images" / "photo.jpg").exists()
            )

            self.assertTrue(
                (folder / "Documents" / "document.pdf").exists()
            )

            self.assertTrue(
                (folder / "Music" / "song.mp3").exists()
            )

            self.assertTrue(
                (folder / "Videos" / "movie.mp4").exists()
            )

            self.assertTrue(
                (folder / "Archives" / "archive.zip").exists()
            )

            self.assertTrue(
                (folder / "Programs" / "program.py").exists()
            )

            self.assertTrue(
                (folder / "Others" / "unknown.xyz").exists()
            )

            self.assertFalse(
                (folder / "photo.jpg").exists()
            )

    def test_organize_empty_folder(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            moved_files = organize_folder(temp_dir)

            self.assertEqual(moved_files, [])

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

            self.assertEqual(len(moved_files), 1)

            self.assertTrue(
                (images_folder / "photo_1.jpg").exists()
            )

            self.assertTrue(
                existing_file.exists()
            )

            self.assertFalse(
                source_file.exists()
            )

    def test_returned_move_information_is_correct(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            source = folder / "document.pdf"
            source.touch()

            moved_files = organize_folder(folder)

            self.assertEqual(len(moved_files), 1)

            item = moved_files[0]

            self.assertEqual(
                item["source"],
                source
            )

            self.assertEqual(
                item["category"],
                "Documents"
            )

            self.assertEqual(
                item["destination"],
                folder / "Documents" / "document.pdf"
            )


class TestUndoOrganization(unittest.TestCase):

    def test_undo_restores_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            source = folder / "document.pdf"
            source.touch()

            moved_files = organize_folder(folder)

            self.assertFalse(source.exists())

            restored_files = undo_organization(
                moved_files
            )

            self.assertEqual(
                len(restored_files),
                1
            )

            self.assertTrue(
                source.exists()
            )

            self.assertFalse(
                (
                    folder
                    / "Documents"
                    / "document.pdf"
                ).exists()
            )

    def test_undo_empty_list(self):
        restored_files = undo_organization([])

        self.assertEqual(
            restored_files,
            []
        )

    def test_undo_skips_missing_destination(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            source = folder / "document.pdf"
            destination = (
                folder
                / "Documents"
                / "document.pdf"
            )

            moved_files = [
                {
                    "source": source,
                    "destination": destination,
                    "category": "Documents",
                }
            ]

            restored_files = undo_organization(
                moved_files
            )

            self.assertEqual(
                restored_files,
                []
            )

    def test_undo_does_not_overwrite_existing_source(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            source = folder / "document.pdf"

            destination_folder = folder / "Documents"
            destination_folder.mkdir()

            destination = (
                destination_folder
                / "document.pdf"
            )

            source.write_text("original")
            destination.write_text("organized")

            moved_files = [
                {
                    "source": source,
                    "destination": destination,
                    "category": "Documents",
                }
            ]

            restored_files = undo_organization(
                moved_files
            )

            self.assertEqual(
                restored_files,
                []
            )

            self.assertTrue(source.exists())
            self.assertTrue(destination.exists())

            self.assertEqual(
                source.read_text(),
                "original"
            )


if __name__ == "__main__":
    unittest.main()