import tempfile
import unittest
from pathlib import Path

from file_organizer import organize_files


class OrganizeFilesTests(unittest.TestCase):
    def test_identical_contents_with_different_names_go_to_duplicates(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            folder = Path(temporary_directory)
            (folder / "first.txt").write_bytes(b"same contents")
            (folder / "second.bin").write_bytes(b"same contents")

            organize_files(folder)

            self.assertEqual(
                (folder / "Documents" / "first.txt").read_bytes(),
                b"same contents",
            )
            self.assertEqual(
                (folder / "Duplicates" / "second.bin").read_bytes(),
                b"same contents",
            )

    def test_different_contents_with_same_name_are_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            folder = Path(temporary_directory)
            documents = folder / "Documents"
            documents.mkdir()
            (documents / "report.txt").write_bytes(b"existing contents")
            (folder / "report.txt").write_bytes(b"incoming contents")

            organize_files(folder)

            self.assertEqual(
                (documents / "report.txt").read_bytes(),
                b"existing contents",
            )
            self.assertEqual(
                (documents / "report (1).txt").read_bytes(),
                b"incoming contents",
            )

    def test_duplicate_of_existing_organized_file_goes_to_duplicates(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            folder = Path(temporary_directory)
            images = folder / "Images"
            images.mkdir()
            (images / "known.png").write_bytes(b"known contents")
            (folder / "copy.txt").write_bytes(b"known contents")

            organize_files(folder)

            self.assertEqual(
                (folder / "Duplicates" / "copy.txt").read_bytes(),
                b"known contents",
            )

    def test_mixed_sample_batch_is_organized_without_losing_files(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            folder = Path(temporary_directory)
            documents = folder / "Documents"
            duplicates = folder / "Duplicates"
            images = folder / "Images"
            documents.mkdir()
            duplicates.mkdir()
            images.mkdir()
            (documents / "report.txt").write_bytes(b"older report")
            (duplicates / "backup.dat").write_bytes(b"older duplicate")
            (images / "photo.png").write_bytes(b"image contents")
            (folder / "report.txt").write_bytes(b"new report")
            (folder / "portrait.png").write_bytes(b"portrait contents")
            (folder / "backup.dat").write_bytes(b"image contents")
            (folder / "clip.mp4").write_bytes(b"video contents")
            (folder / "data.csv").write_bytes(b"csv contents")
            (folder / "sheet.xlsx").write_bytes(b"spreadsheet contents")

            organize_files(folder)

            expected_files = {
                documents / "report.txt": b"older report",
                documents / "report (1).txt": b"new report",
                images / "photo.png": b"image contents",
                images / "portrait.png": b"portrait contents",
                duplicates / "backup (1).dat": b"image contents",
                duplicates / "backup.dat": b"older duplicate",
                folder / "Videos" / "clip.mp4": b"video contents",
                folder / "Spreadsheets" / "data.csv": b"csv contents",
                folder / "Spreadsheets" / "sheet.xlsx": b"spreadsheet contents",
            }
            for path, contents in expected_files.items():
                with self.subTest(path=path.name):
                    self.assertEqual(path.read_bytes(), contents)

    def test_running_twice_does_not_move_files_again(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            folder = Path(temporary_directory)
            (folder / "photo.png").write_bytes(b"image data")

            first_run = organize_files(folder)
            second_run = organize_files(folder)

            self.assertEqual(first_run, {"moved": 1, "failed": 0})
            self.assertEqual(second_run, {"moved": 0, "failed": 0})
            self.assertTrue((folder / "Images" / "photo.png").exists())


if __name__ == "__main__":
    unittest.main()
