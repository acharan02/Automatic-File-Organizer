"""Generate and organize 1,000 temporary sample files to benchmark the organizer."""
from collections import Counter
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
from time import perf_counter

from file_organizer import organize_files

FILE_COUNT = 1_000
DUPLICATE_COUNT = 100
EXTENSIONS = [
    ".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg", ".gif",
    ".mp4", ".mov", ".xlsx", ".csv", ".mp3", ".wav", ".zip", ".bin",
]
PAYLOAD_SIZE = 16 * 1024  # 16 KiB per file


def make_payload(index: int) -> bytes:
    seed = f"sample-file-content-{index:04d}-".encode("utf-8")
    return (seed * ((PAYLOAD_SIZE // len(seed)) + 1))[:PAYLOAD_SIZE]


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="file_organizer_benchmark_") as temp_dir:
        test_folder = Path(temp_dir) / "test_files"
        test_folder.mkdir()

        # Create 900 unique files.
        unique_payloads = []
        for index in range(FILE_COUNT - DUPLICATE_COUNT):
            payload = make_payload(index)
            unique_payloads.append(payload)
            extension = EXTENSIONS[index % len(EXTENSIONS)]
            (test_folder / f"sample_{index:04d}{extension}").write_bytes(payload)

        # Add 100 files whose contents match the first 100 files,
        # while their names may have different extensions.
        for duplicate_index in range(DUPLICATE_COUNT):
            source_index = duplicate_index
            extension = EXTENSIONS[(FILE_COUNT - DUPLICATE_COUNT + duplicate_index) % len(EXTENSIONS)]
            duplicate_path = test_folder / f"duplicate_{duplicate_index:04d}{extension}"
            duplicate_path.write_bytes(unique_payloads[source_index])

        # Suppress one line per file so the benchmark prints only its summary.
        start = perf_counter()
        with redirect_stdout(StringIO()):
            first_result = organize_files(test_folder)
        first_run_seconds = perf_counter() - start

        folder_counts = Counter()
        root_files = [path for path in test_folder.iterdir() if path.is_file()]
        for category_folder in test_folder.iterdir():
            if category_folder.is_dir():
                folder_counts[category_folder.name] = sum(
                    1 for item in category_folder.iterdir() if item.is_file()
                )

        total_organized = sum(folder_counts.values())
        duplicate_files = folder_counts.get("Duplicates", 0)

        start = perf_counter()
        with redirect_stdout(StringIO()):
            second_result = organize_files(test_folder)
        second_run_seconds = perf_counter() - start

        print("\n--- PERFORMANCE TEST SUMMARY ---")
        print(f"Input files: {FILE_COUNT}")
        print(f"File size: {PAYLOAD_SIZE // 1024} KiB each")
        print(f"Expected identical-content duplicates: {DUPLICATE_COUNT}")
        print(f"First run result: {first_result}")
        print(f"First run time: {first_run_seconds:.4f} seconds")
        print(f"Files organized across folders: {total_organized}")
        print(f"Files remaining in root: {len(root_files)}")
        print(f"Files in Duplicates: {duplicate_files}")
        print("Folder counts:")
        for category, count in sorted(folder_counts.items()):
            print(f"  {category}: {count}")
        print(f"Second run result: {second_result}")
        print(f"Second run time: {second_run_seconds:.4f} seconds")

        # Fail loudly if the benchmark reveals a data-loss or repeat-run issue.
        assert first_result == {"moved": FILE_COUNT, "failed": 0}, first_result
        assert total_organized == FILE_COUNT, total_organized
        assert len(root_files) == 0, root_files
        assert duplicate_files == DUPLICATE_COUNT, duplicate_files
        assert second_result == {"moved": 0, "failed": 0}, second_result
        print("\nPASS: All 1,000 files were handled correctly; no files were lost.")


if __name__ == "__main__":
    main()
