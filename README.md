
# Automatic File Organizer

A Python-based file management automation tool that automatically organizes files into categorized folders based on their extensions.

## Project Overview

Managing hundreds of files manually can be time-consuming. This project automates file organization by identifying file types and moving files into appropriate folders.

It also detects duplicate file contents using SHA-256 hashing and handles filename conflicts to prevent accidental overwriting.

## Features

- Automatic file categorization.
- Dynamic folder creation.
- File movement using Python.
- Duplicate content detection using SHA-256.
- Duplicate filename handling.
- Exception handling for file operations.
- Activity logging.
- Automated unit testing.
- Performance testing with large datasets.

## Technologies Used

- Python
- pathlib
- shutil
- hashlib
- logging
- unittest

## Project Structure

Automatic_File_Organizer/
│
├── file_organizer.py
├── test_file_organizer.py
├── performance_test_1000.py
├── README.md
├── .gitignore
└── test_files/

## Supported File Categories

| Category | Examples |
|---|---|
| Documents | PDF, DOCX, TXT, PPTX |
| Images | PNG, JPG, JPEG, GIF |
| Videos | MP4, MOV |
| Spreadsheets | XLSX, CSV |
| Audio | MP3, WAV |
| Archives | ZIP |
| Duplicates | Files with identical contents |
| Others | Unsupported file types |

## How to Run

1. Clone the repository.
2. Open the project directory.
3. Place sample files inside the test_files folder.
4. Run the application:

   python file_organizer.py

## Run Automated Tests

Execute:

    python -m unittest -v

## Performance Testing

Execute:

    python performance_test_1000.py

## How Duplicate Detection Works

The application uses SHA-256 hashing to identify files with identical contents.

Files with matching content hashes are identified as duplicates and handled separately.

## Important Note

This application moves files rather than copying them.

Use a test directory or backup your files before running the program on important data.

## Learning Outcomes

This project demonstrates practical Python programming concepts, file system operations, automation, hashing, exception handling, logging and automated testing.


