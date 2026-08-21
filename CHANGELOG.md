
# Changelog

All notable changes to this project are documented in this file.

The project follows a simple version-based release history.

---

## [1.0.0] - 2026-08-20

### Added

* Desktop graphical interface built with Python and Tkinter
* Folder selection and browsing
* File preview before organization
* Automatic file categorization based on file extensions
* Images category
* Documents category
* Videos category
* Music category
* Archives category
* Programs category
* Others category for unsupported or unknown file types
* Safe duplicate filename handling
* Automatic unique filename generation
* File organization functionality
* Undo for the most recent organization operation
* Rollback protection for organization failures
* Clear/reset functionality
* Keyboard shortcuts
* Organization statistics and status information
* Automated test suite using pytest
* Windows standalone executable built with PyInstaller
* Windows ZIP release package
* Project screenshots and documentation

### Safety

* Existing destination files are never overwritten.
* Duplicate filenames receive unique names automatically.
* Organization failures attempt to roll back completed file moves.
* Undo avoids overwriting files that already exist at the original location.

### Testing

* 28 automated tests implemented.
* 28 / 28 automated tests passed.
* GUI functionality manually tested.
* Standalone Windows executable tested.
* Released Windows ZIP downloaded and tested outside the development environment.

### Packaging

* Python: 3.13.15
* PyInstaller: 6.22.2
* Platform: Windows 11
* Release package:

```text
FileOrganizer-v1.0.0-Windows.zip
```

---

## [Unreleased]

Future changes will be documented here before the next version is released.
