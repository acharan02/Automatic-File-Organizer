from pathlib import Path
import hashlib
import logging
import shutil

# STEP 1: Define project paths
BASE_DIR = Path(__file__).resolve().parent
FOLDER_PATH = BASE_DIR / "test_files"

# STEP 2: Define file categories
FILE_TYPES = {
    ".pdf": "Documents",
    ".docx": "Documents",
    ".txt": "Documents",
    ".pptx": "Documents",
    ".png": "Images",
    ".jpg": "Images",
    ".jpeg": "Images",
    ".gif": "Images",
    ".mp4": "Videos",
    ".mov": "Videos",
    ".xlsx": "Spreadsheets",
    ".csv": "Spreadsheets",
    ".mp3": "Audio",
    ".wav": "Audio",
    ".zip": "Archives",
}

# STEP 3: Configure logging
logging.basicConfig(
    filename=str(BASE_DIR / "file_organizer.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)


def get_category(file_path: Path) -> str:
    """Return the destination category for a file based on its extension."""
    return FILE_TYPES.get(file_path.suffix.lower(), "Others")


def calculate_sha256(file_path: Path) -> str:
    """Calculate a SHA-256 digest without loading the whole file into memory."""
    digest = hashlib.sha256()
    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create_category_folders(folder_path: Path) -> None:
    """Create all destination folders, including Duplicates and Others."""
    categories = set(FILE_TYPES.values()) | {"Others", "Duplicates"}
    for category in sorted(categories):
        category_path = folder_path / category
        category_path.mkdir(exist_ok=True)
        logging.info("Folder ready: %s", category)


def get_existing_hashes(folder_path: Path) -> set[str]:
    """Hash files already stored in category folders to detect repeat content."""
    known_hashes: set[str] = set()
    for child in folder_path.iterdir():
        if not child.is_dir():
            continue
        for existing_file in child.iterdir():
            if existing_file.is_file():
                try:
                    known_hashes.add(calculate_sha256(existing_file))
                except OSError as error:
                    logging.warning(
                        "Could not hash existing file %s: %s",
                        existing_file,
                        error,
                    )
    return known_hashes


def get_destination_path(file_path: Path, destination_folder: Path) -> Path:
    """Return a non-conflicting destination, preserving the existing file."""
    destination_path = destination_folder / file_path.name
    if destination_path.exists():
        logging.warning("Duplicate filename detected: %s", file_path.name)
        counter = 1
        while destination_path.exists():
            new_name = f"{file_path.stem} ({counter}){file_path.suffix}"
            destination_path = destination_folder / new_name
            counter += 1
    return destination_path


def organize_files(folder_path: Path) -> dict[str, int] | None:
    """Organize root-level files, routing identical content into Duplicates."""
    folder_path = Path(folder_path)

    if not folder_path.exists():
        folder_path.mkdir(parents=True, exist_ok=True)

    if not folder_path.is_dir():
        logging.error("Target path is not a directory: %s", folder_path)
        print("Error: Target path is not a folder.")
        return None

    logging.info("File Organizer started: %s", folder_path)
    create_category_folders(folder_path)

    # Include content already present in category folders in duplicate checks.
    known_hashes = get_existing_hashes(folder_path)
    moved_count = 0
    failed_count = 0

    # Sorting makes processing order predictable for repeatable tests.
    files_to_process = sorted(
        (item for item in folder_path.iterdir() if item.is_file()),
        key=lambda item: item.name.casefold(),
    )

    for file_path in files_to_process:
        try:
            file_hash = calculate_sha256(file_path)

            if file_hash in known_hashes:
                category = "Duplicates"
                logging.info("Duplicate content detected: %s", file_path.name)
            else:
                category = get_category(file_path)

            destination_folder = folder_path / category
            destination_path = get_destination_path(file_path, destination_folder)

            shutil.move(str(file_path), str(destination_path))
            known_hashes.add(file_hash)
            moved_count += 1

            logging.info("Moved %s -> %s", file_path.name, category)
            print(f"Moved {file_path.name} -> {category}")

        except FileNotFoundError as error:
            failed_count += 1
            logging.error("File not found: %s", error)

        except PermissionError as error:
            failed_count += 1
            logging.error("Permission denied: %s", error)

        except shutil.Error as error:
            failed_count += 1
            logging.error("File operation failed: %s", error)

        except OSError as error:
            failed_count += 1
            logging.error("Operating system error: %s", error)

    summary = {"moved": moved_count, "failed": failed_count}
    logging.info(
        "Organizer completed. Moved: %d, Failed: %d",
        moved_count,
        failed_count,
    )
    print("\nAutomation completed!")
    print("Successfully moved:", moved_count)
    print("Failed operations:", failed_count)
    return summary


if __name__ == "__main__":
    organize_files(FOLDER_PATH)
