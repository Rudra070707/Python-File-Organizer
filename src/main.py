"""
File Organizer - Application Entry Point

This module is the executable entry point for the File Organizer
desktop application.

Responsibilities:
    - Import the GUI application launcher.
    - Start the application through a dedicated main() function.
    - Ensure the application starts only when this file is executed
      directly.

Design goals:
    - Minimal and reliable entry point.
    - Clear application lifecycle.
    - Safe import behavior.
    - Easy testing and reuse.
    - No GUI initialization during module import.
"""

from __future__ import annotations

if __package__:
    from .gui import start_app
else:
    from gui import start_app


def main() -> None:
    """
    Start the File Organizer application.

    Keeping application startup inside a dedicated function makes this
    module easier to test and prevents the GUI from starting when the
    module is imported by another module.
    """
    start_app()


if __name__ == "__main__":
    main()
