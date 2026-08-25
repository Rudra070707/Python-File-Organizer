import queue
import threading
import tkinter as tk
from collections import Counter
from pathlib import Path
from tkinter import filedialog, messagebox

if __package__:
    from .organizer import (
        get_category,
        get_files,
        organize_folder,
        undo_organization,
    )
else:
    from organizer import (
        get_category,
        get_files,
        organize_folder,
        undo_organization,
    )


class FileOrganizerApp:
    """Premium graphical interface for the Python File Organizer."""

    # ================================================================
    # WINDOW
    # ================================================================

    WINDOW_WIDTH = 1100
    WINDOW_HEIGHT = 760
    MIN_WIDTH = 900
    MIN_HEIGHT = 650

    # ================================================================
    # COLOR SYSTEM
    # ================================================================

    COLORS = {
        "bg": "#0B1120",
        "bg_secondary": "#0F172A",
        "panel": "#151F32",
        "panel_light": "#1B263B",
        "panel_hover": "#202D45",
        "panel_active": "#24324A",
        "border": "#26344D",
        "border_light": "#33445F",
        "text": "#F8FAFC",
        "text_secondary": "#A8B3C7",
        "text_muted": "#718096",
        "blue": "#4F8CFF",
        "blue_hover": "#6BA0FF",
        "blue_dark": "#285CC4",
        "green": "#22C55E",
        "green_hover": "#34D399",
        "green_dark": "#15803D",
        "orange": "#F59E0B",
        "orange_hover": "#FBBF24",
        "red": "#EF4444",
        "red_hover": "#F87171",
        "white": "#FFFFFF",
        "black": "#000000",
        "input": "#0F172A",
        "scrollbar": "#273650",
        "scrollbar_hover": "#385071",
        "success_bg": "#0D2B1C",
        "info_bg": "#102344",
        "warning_bg": "#30240D",
        "error_bg": "#2A1115",
    }

    # ================================================================
    # CATEGORIES
    # ================================================================

    CATEGORY_ORDER = [
        "Images",
        "Documents",
        "Videos",
        "Music",
        "Archives",
        "Programs",
        "Others",
    ]

    CATEGORY_ICONS = {
        "Images": "▣",
        "Documents": "▤",
        "Videos": "▶",
        "Music": "♫",
        "Archives": "▦",
        "Programs": "◆",
        "Others": "•",
    }

    CATEGORY_COLORS = {
        "Images": "#60A5FA",
        "Documents": "#A78BFA",
        "Videos": "#F87171",
        "Music": "#34D399",
        "Archives": "#FBBF24",
        "Programs": "#FB923C",
        "Others": "#94A3B8",
    }

    # ================================================================
    # INITIALIZATION
    # ================================================================

    def __init__(self, root):
        self.root = root

        self.selected_folder = None
        self.last_operation = None
        self.is_busy = False

        self.operation_queue = queue.Queue()
        self.operation_thread = None
        self.operation_name = None
        self.operation_cancelled = False

        self.configure_window()
        self.create_widgets()
        self.bind_shortcuts()

        self.root.after(100, self.process_operation_queue)

        self.update_button_states()
        self.show_welcome()

    # ================================================================
    # WINDOW CONFIGURATION
    # ================================================================

    def configure_window(self):
        self.root.title("File Organizer")

        self.root.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")

        self.root.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)

        self.root.configure(bg=self.COLORS["bg"])

        self.root.option_add("*tearOff", False)

        self.root.protocol("WM_DELETE_WINDOW", self.close_application)

        self.root.bind("<Configure>", self._on_window_resize)

    def _on_window_resize(self, event):
        if event.widget is not self.root:
            return

        width = event.width

        if hasattr(self, "result_text"):
            if width < 1000:
                self.result_text.config(font=("Consolas", 9))
            else:
                self.result_text.config(font=("Consolas", 10))

    # ================================================================
    # MAIN UI
    # ================================================================

    def create_widgets(self):
        self.create_top_bar()
        self.create_folder_card()
        self.create_action_bar()
        self.create_results_area()
        self.create_status_bar()

    # ================================================================
    # TOP BAR
    # ================================================================

    def create_top_bar(self):
        top = tk.Frame(self.root, bg=self.COLORS["bg"])

        top.pack(fill="x", padx=42, pady=(28, 18))

        # ------------------------------------------------------------
        # LEFT
        # ------------------------------------------------------------

        title_frame = tk.Frame(top, bg=self.COLORS["bg"])

        title_frame.pack(side="left")

        icon = tk.Label(
            title_frame,
            text="▦",
            font=("Segoe UI Symbol", 29, "bold"),
            bg=self.COLORS["bg"],
            fg=self.COLORS["blue"],
        )

        icon.pack(side="left", padx=(0, 12))

        text_frame = tk.Frame(title_frame, bg=self.COLORS["bg"])

        text_frame.pack(side="left")

        title = tk.Label(
            text_frame,
            text="File Organizer",
            font=("Segoe UI", 25, "bold"),
            bg=self.COLORS["bg"],
            fg=self.COLORS["text"],
        )

        title.pack(anchor="w")

        subtitle = tk.Label(
            text_frame,
            text="Smart • Local • Safe file organization",
            font=("Segoe UI", 10),
            bg=self.COLORS["bg"],
            fg=self.COLORS["text_secondary"],
        )

        subtitle.pack(anchor="w", pady=(2, 0))

        # ------------------------------------------------------------
        # RIGHT STATUS
        # ------------------------------------------------------------

        status_container = tk.Frame(
            top,
            bg=self.COLORS["panel"],
            highlightbackground=self.COLORS["border"],
            highlightthickness=1,
        )

        status_container.pack(side="right", padx=(20, 0), pady=5)

        self.connection_dot = tk.Label(
            status_container,
            text="●",
            font=("Segoe UI", 9),
            bg=self.COLORS["panel"],
            fg=self.COLORS["green"],
        )

        self.connection_dot.pack(side="left", padx=(10, 5))

        self.header_status = tk.Label(
            status_container,
            text="LOCAL • READY",
            font=("Segoe UI", 8, "bold"),
            bg=self.COLORS["panel"],
            fg=self.COLORS["text_secondary"],
        )

        self.header_status.pack(side="left", padx=(0, 10), pady=7)

    def update_header_status(self, busy=False):
        if busy:
            self.header_status.config(text="LOCAL • WORKING", fg=self.COLORS["orange"])

            self.connection_dot.config(fg=self.COLORS["orange"])

        else:
            self.header_status.config(text="LOCAL • READY", fg=self.COLORS["green"])

            self.connection_dot.config(fg=self.COLORS["green"])

    # ================================================================
    # FOLDER CARD
    # ================================================================

    def create_folder_card(self):
        outer = tk.Frame(self.root, bg=self.COLORS["border"])

        outer.pack(fill="x", padx=42, pady=(0, 14))

        card = tk.Frame(outer, bg=self.COLORS["panel"])

        card.pack(fill="both", expand=True, padx=1, pady=1)

        content = tk.Frame(card, bg=self.COLORS["panel"])

        content.pack(fill="x", padx=20, pady=18)

        # ------------------------------------------------------------
        # HEADER
        # ------------------------------------------------------------

        heading_row = tk.Frame(content, bg=self.COLORS["panel"])

        heading_row.pack(fill="x")

        folder_icon = tk.Label(
            heading_row,
            text="⌂",
            font=("Segoe UI Symbol", 16, "bold"),
            bg=self.COLORS["panel"],
            fg=self.COLORS["blue"],
        )

        folder_icon.pack(side="left", padx=(0, 8))

        folder_title = tk.Label(
            heading_row,
            text="Source Folder",
            font=("Segoe UI", 11, "bold"),
            bg=self.COLORS["panel"],
            fg=self.COLORS["text"],
        )

        folder_title.pack(side="left")

        folder_hint = tk.Label(
            heading_row,
            text="Choose the folder containing the files",
            font=("Segoe UI", 9),
            bg=self.COLORS["panel"],
            fg=self.COLORS["text_muted"],
        )

        folder_hint.pack(side="right")

        # ------------------------------------------------------------
        # PATH
        # ------------------------------------------------------------

        path_frame = tk.Frame(content, bg=self.COLORS["panel"])

        path_frame.pack(fill="x", pady=(12, 0))

        entry_container = tk.Frame(path_frame, bg=self.COLORS["border_light"])

        entry_container.pack(side="left", fill="x", expand=True)

        self.folder_entry = tk.Entry(
            entry_container,
            font=("Segoe UI", 10),
            state="readonly",
            readonlybackground=self.COLORS["input"],
            fg=self.COLORS["text"],
            relief="flat",
            bd=0,
            insertbackground=self.COLORS["text"],
        )

        self.folder_entry.pack(fill="x", padx=1, pady=1, ipady=8)

        self.browse_button = tk.Button(
            path_frame,
            text="  Browse Folder  ",
            command=self.select_folder,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            relief="flat",
            bd=0,
            bg=self.COLORS["blue"],
            fg=self.COLORS["white"],
            activebackground=self.COLORS["blue_hover"],
            activeforeground=self.COLORS["white"],
        )

        self.browse_button.pack(side="left", padx=(10, 0), ipady=7)

        self.add_hover_effect(self.browse_button, self.COLORS["blue"], self.COLORS["blue_hover"])

    # ================================================================
    # ACTION BAR
    # ================================================================

    def create_action_bar(self):
        frame = tk.Frame(self.root, bg=self.COLORS["bg"])

        frame.pack(fill="x", padx=42, pady=(0, 16))

        self.preview_button = self.create_button(
            frame,
            "Preview",
            self.preview_files,
            self.COLORS["panel_light"],
            self.COLORS["panel_hover"],
            width=14,
        )

        self.preview_button.pack(side="left", padx=(0, 7))

        self.organize_button = self.create_button(
            frame,
            "Organize Files",
            self.organize_files,
            self.COLORS["green_dark"],
            self.COLORS["green"],
            width=16,
        )

        self.organize_button.pack(side="left", padx=7)

        self.undo_button = self.create_button(
            frame,
            "Undo",
            self.undo_last_operation,
            self.COLORS["panel_light"],
            self.COLORS["panel_hover"],
            width=14,
        )

        self.undo_button.pack(side="left", padx=7)

        self.clear_button = self.create_button(
            frame,
            "Clear",
            self.clear,
            self.COLORS["panel_light"],
            self.COLORS["panel_hover"],
            width=14,
        )

        self.clear_button.pack(side="left", padx=7)

        shortcut = tk.Label(
            frame,
            text=("Ctrl+O  Browse    •    Ctrl+P  Preview    •    Ctrl+Z  Undo    •    Esc  Clear"),
            font=("Segoe UI", 8),
            bg=self.COLORS["bg"],
            fg=self.COLORS["text_muted"],
        )

        shortcut.pack(side="right", padx=(15, 0))

    # ================================================================
    # BUTTON FACTORY
    # ================================================================

    def create_button(self, parent, text, command, background, hover_background, width=14):
        button = tk.Button(
            parent,
            text=text,
            command=command,
            width=width,
            height=2,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            relief="flat",
            bd=0,
            bg=background,
            fg=self.COLORS["text"],
            activebackground=hover_background,
            activeforeground=self.COLORS["text"],
            disabledforeground=self.COLORS["text_muted"],
        )

        self.add_hover_effect(button, background, hover_background)

        return button

    def add_hover_effect(self, widget, normal_color, hover_color):
        def on_enter(event):
            if str(widget["state"]) != "disabled":
                widget.config(bg=hover_color)

        def on_leave(event):
            if str(widget["state"]) != "disabled":
                widget.config(bg=normal_color)

        widget.bind("<Enter>", on_enter)

        widget.bind("<Leave>", on_leave)

    # ================================================================
    # RESULTS AREA
    # ================================================================

    def create_results_area(self):
        heading = tk.Frame(self.root, bg=self.COLORS["bg"])

        heading.pack(fill="x", padx=42, pady=(0, 7))

        result_title = tk.Label(
            heading,
            text="Activity",
            font=("Segoe UI", 11, "bold"),
            bg=self.COLORS["bg"],
            fg=self.COLORS["text"],
        )

        result_title.pack(side="left")

        self.result_count_label = tk.Label(
            heading,
            text="",
            font=("Segoe UI", 9, "bold"),
            bg=self.COLORS["bg"],
            fg=self.COLORS["blue"],
        )

        self.result_count_label.pack(side="right")

        result_outer = tk.Frame(self.root, bg=self.COLORS["border"])

        result_outer.pack(fill="both", expand=True, padx=42, pady=(0, 15))

        result_frame = tk.Frame(result_outer, bg=self.COLORS["panel"])

        result_frame.pack(fill="both", expand=True, padx=1, pady=1)

        scrollbar = tk.Scrollbar(
            result_frame,
            orient="vertical",
            bg=self.COLORS["scrollbar"],
            troughcolor=self.COLORS["panel"],
            activebackground=self.COLORS["scrollbar_hover"],
            relief="flat",
            bd=0,
        )

        scrollbar.pack(side="right", fill="y")

        self.result_text = tk.Text(
            result_frame,
            height=14,
            font=("Consolas", 10),
            bg=self.COLORS["panel"],
            fg=self.COLORS["text_secondary"],
            insertbackground=self.COLORS["text"],
            selectbackground=self.COLORS["blue_dark"],
            selectforeground=self.COLORS["white"],
            relief="flat",
            bd=0,
            wrap="word",
            padx=20,
            pady=18,
            spacing1=2,
            spacing3=2,
            yscrollcommand=scrollbar.set,
        )

        self.result_text.pack(side="left", fill="both", expand=True)

        scrollbar.config(command=self.result_text.yview)

        self.result_text.config(state=tk.DISABLED)

        # ------------------------------------------------------------
        # TEXT TAGS
        # ------------------------------------------------------------

        self.result_text.tag_configure(
            "heading", foreground=self.COLORS["text"], font=("Consolas", 11, "bold")
        )

        self.result_text.tag_configure(
            "accent", foreground=self.COLORS["blue"], font=("Consolas", 10, "bold")
        )

        self.result_text.tag_configure(
            "success", foreground=self.COLORS["green"], font=("Consolas", 10, "bold")
        )

        self.result_text.tag_configure("muted", foreground=self.COLORS["text_muted"])

        self.result_text.tag_configure(
            "category", foreground=self.COLORS["orange"], font=("Consolas", 10, "bold")
        )

        for category, color in self.CATEGORY_COLORS.items():
            self.result_text.tag_configure(
                f"category_{category.lower()}", foreground=color, font=("Consolas", 10, "bold")
            )

    # ================================================================
    # STATUS BAR
    # ================================================================

    def create_status_bar(self):
        status = tk.Frame(self.root, bg=self.COLORS["bg_secondary"], height=32)

        status.pack(fill="x", side="bottom")

        status.pack_propagate(False)

        self.status_dot = tk.Label(
            status,
            text="●",
            font=("Segoe UI", 8),
            bg=self.COLORS["bg_secondary"],
            fg=self.COLORS["green"],
        )

        self.status_dot.pack(side="left", padx=(42, 7))

        self.status_label = tk.Label(
            status,
            text="Ready",
            font=("Segoe UI", 9),
            bg=self.COLORS["bg_secondary"],
            fg=self.COLORS["text_secondary"],
            anchor="w",
        )

        self.status_label.pack(side="left")

        self.offline_label = tk.Label(
            status,
            text="LOCAL PROCESSING • NO INTERNET REQUIRED",
            font=("Segoe UI", 8, "bold"),
            bg=self.COLORS["bg_secondary"],
            fg=self.COLORS["text_muted"],
        )

        self.offline_label.pack(side="right", padx=42)

    # ================================================================
    # KEYBOARD SHORTCUTS
    # ================================================================

    def bind_shortcuts(self):
        self.root.bind("<Control-o>", self._shortcut_browse)

        self.root.bind("<Control-p>", self._shortcut_preview)

        self.root.bind("<Control-z>", self._shortcut_undo)

        self.root.bind("<Escape>", self._shortcut_clear)

    def _shortcut_browse(self, event):
        self.select_folder()
        return "break"

    def _shortcut_preview(self, event):
        self.preview_files()
        return "break"

    def _shortcut_undo(self, event):
        self.undo_last_operation()
        return "break"

    def _shortcut_clear(self, event):
        self.clear()
        return "break"

    # ================================================================
    # UI HELPERS
    # ================================================================

    def set_status(self, message):
        self.status_label.config(text=message)

    def set_busy(self, busy, message=None):
        self.is_busy = busy

        if message:
            self.set_status(message)

        self.update_header_status(busy)

        if busy:
            self.status_dot.config(fg=self.COLORS["orange"])
        else:
            self.status_dot.config(fg=self.COLORS["green"])

        self.update_button_states()
        self.root.update_idletasks()

    def show_welcome(self):
        self.show_message(
            "WELCOME TO FILE ORGANIZER\n\n"
            "Select a folder to begin organizing your files.\n\n"
            "Workflow\n"
            "────────────────────────────────────────\n"
            "1. Select a folder\n"
            "2. Preview detected files\n"
            "3. Organize files by category\n"
            "4. Undo the last organization if needed\n\n"
            "All processing is performed locally on your computer."
        )

        self.set_status("Ready • Select a folder to get started")

    def show_message(self, message):
        self.result_text.config(state=tk.NORMAL)

        self.result_text.delete("1.0", tk.END)

        self.result_text.insert(tk.END, message)

        self.result_text.config(state=tk.DISABLED)

        self.result_count_label.config(text="")

        self.result_text.see("1.0")

    def show_result(self, message, count=None):
        self.result_text.config(state=tk.NORMAL)

        self.result_text.delete("1.0", tk.END)

        self.result_text.insert(tk.END, message)

        self.result_text.config(state=tk.DISABLED)

        if count is None:
            self.result_count_label.config(text="")
        else:
            file_word = "FILE" if count == 1 else "FILES"

            self.result_count_label.config(text=f"{count:,} {file_word}")

        self.result_text.see("1.0")

    def set_folder_entry(self, folder):
        self.folder_entry.config(state=tk.NORMAL)

        self.folder_entry.delete(0, tk.END)

        self.folder_entry.insert(0, folder)

        self.folder_entry.config(state="readonly")

    def format_filename(self, filename, max_length=72):
        filename = str(filename)

        if len(filename) <= max_length:
            return filename

        path = Path(filename)

        suffix = path.suffix
        stem = path.stem

        available = max_length - len(suffix) - 3

        if available <= 5:
            return filename[: max_length - 3] + "..."

        return stem[:available] + "..." + suffix

    def validate_selected_folder(self):
        if not self.selected_folder:
            return False

        folder = Path(self.selected_folder)

        try:
            exists = folder.exists()
            is_dir = folder.is_dir()
        except OSError as error:
            messagebox.showerror(
                "Folder Error", f"Could not access the selected folder.\n\n{error}"
            )

            return False

        if not exists:
            messagebox.showerror("Folder Error", "The selected folder no longer exists.")

            self.selected_folder = None
            self.last_operation = None

            self.set_folder_entry("")
            self.update_button_states()

            return False

        if not is_dir:
            messagebox.showerror("Folder Error", "The selected path is no longer a folder.")

            self.selected_folder = None
            self.last_operation = None

            self.set_folder_entry("")
            self.update_button_states()

            return False

        return True

    # ================================================================
    # BUTTON STATES
    # ================================================================

    def update_button_states(self):
        has_folder = bool(self.selected_folder)

        has_undo = bool(self.last_operation)

        if self.is_busy:
            self.preview_button.config(state=tk.DISABLED, bg=self.COLORS["panel"])

            self.organize_button.config(state=tk.DISABLED, bg=self.COLORS["panel"])

            self.undo_button.config(state=tk.DISABLED, bg=self.COLORS["panel"])

            self.clear_button.config(state=tk.DISABLED, bg=self.COLORS["panel"])

            self.browse_button.config(state=tk.DISABLED, bg=self.COLORS["panel"])

            return

        # ------------------------------------------------------------
        # PREVIEW
        # ------------------------------------------------------------

        self.preview_button.config(state=(tk.NORMAL if has_folder else tk.DISABLED))

        # ------------------------------------------------------------
        # ORGANIZE
        # ------------------------------------------------------------

        self.organize_button.config(state=(tk.NORMAL if has_folder else tk.DISABLED))

        # ------------------------------------------------------------
        # UNDO
        # ------------------------------------------------------------

        self.undo_button.config(state=(tk.NORMAL if has_undo else tk.DISABLED))

        # ------------------------------------------------------------
        # CLEAR
        # ------------------------------------------------------------

        self.clear_button.config(state=tk.NORMAL)

        # ------------------------------------------------------------
        # BROWSE
        # ------------------------------------------------------------

        self.browse_button.config(state=tk.NORMAL)

        # ------------------------------------------------------------
        # COLORS
        # ------------------------------------------------------------

        if has_folder:
            self.preview_button.config(bg=self.COLORS["panel_light"])

            self.organize_button.config(bg=self.COLORS["green_dark"])

        else:
            self.preview_button.config(bg=self.COLORS["panel"])

            self.organize_button.config(bg=self.COLORS["panel"])

        if has_undo:
            self.undo_button.config(bg=self.COLORS["panel_light"])
        else:
            self.undo_button.config(bg=self.COLORS["panel"])

    # ================================================================
    # CATEGORY HELPERS
    # ================================================================

    def get_category_counts(self, files):
        counts = Counter()

        for file_path in files:
            counts[get_category(file_path)] += 1

        return counts

    def create_category_summary(self, counts, total):
        lines = ["CATEGORY BREAKDOWN", "────────────────────────────────────────", ""]

        for category in self.CATEGORY_ORDER:
            count = counts.get(category, 0)

            if count <= 0:
                continue

            percentage = count / total * 100 if total else 0

            icon = self.CATEGORY_ICONS.get(category, "•")

            lines.append(f"{icon} {category:<12}{count:>5}   {percentage:>5.1f}%")

        return lines

    # ================================================================
    # BACKGROUND OPERATIONS
    # ================================================================

    def run_background_operation(self, operation_name, function, *args):
        if self.is_busy:
            return

        self.operation_name = operation_name
        self.operation_cancelled = False

        self.set_busy(True, f"{operation_name}...")

        self.operation_thread = threading.Thread(
            target=self._background_worker, args=(function, args), daemon=True
        )

        self.operation_thread.start()

    def _background_worker(self, function, args):
        try:
            result = function(*args)

            self.operation_queue.put(("success", result))

        except Exception as error:
            self.operation_queue.put(("error", error))

    def process_operation_queue(self):
        try:
            while True:
                result_type, result = self.operation_queue.get_nowait()

                self.handle_operation_result(result_type, result)

        except queue.Empty:
            pass

        if self.root.winfo_exists():
            self.root.after(100, self.process_operation_queue)

    def handle_operation_result(self, result_type, result):
        if result_type == "success":
            self.handle_operation_success(result)

        elif result_type == "error":
            self.handle_operation_error(result)

    def handle_operation_success(self, result):
        self.set_busy(False)

        if self.operation_name == "Preview":
            self.handle_preview_success(result)

        elif self.operation_name == "Organization":
            self.handle_organization_success(result)

        elif self.operation_name == "Undo":
            self.handle_undo_success(result)

        self.operation_name = None
        self.operation_thread = None

    def handle_operation_error(self, error):
        operation = self.operation_name or "Operation"

        self.set_busy(False)

        self.operation_name = None
        self.operation_thread = None

        if isinstance(error, PermissionError):
            messagebox.showerror(
                "Permission Error",
                (f"{operation} could not be completed because permission was denied.\n\n{error}"),
            )

        elif isinstance(error, FileNotFoundError):
            messagebox.showerror(
                "File Not Found",
                (
                    f"{operation} could not be completed "
                    f"because a required file or folder "
                    f"could not be found.\n\n"
                    f"{error}"
                ),
            )

        elif isinstance(error, NotADirectoryError):
            messagebox.showerror(
                "Folder Error", (f"The selected path is no longer a valid folder.\n\n{error}")
            )

        elif isinstance(error, OSError):
            messagebox.showerror(
                "File System Error", (f"{operation} could not be completed.\n\n{error}")
            )

        else:
            messagebox.showerror(
                "Unexpected Error",
                (f"An unexpected error occurred during {operation.lower()}.\n\n{error}"),
            )

        self.set_status(f"{operation} failed.")

    # ================================================================
    # PREVIEW SUCCESS
    # ================================================================

    def handle_preview_success(self, files):
        if not files:
            self.show_message(
                "NO FILES FOUND\n\n"
                "The selected folder does not contain "
                "any files to organize.\n\n"
                "Subfolders are intentionally ignored."
            )

            self.set_status("Selected folder contains no files.")

            return

        preview = self.create_preview(files)

        self.show_result(preview, len(files))

        self.set_status(f"Preview ready • {len(files):,} file(s) detected")

    # ================================================================
    # PREVIEW
    # ================================================================

    def create_preview(self, files):
        counts = self.get_category_counts(files)

        lines = [
            "FILE ORGANIZATION PREVIEW",
            "════════════════════════════════════════",
            "",
            f"Total files detected: {len(files)}",
            "",
        ]

        lines.extend(self.create_category_summary(counts, len(files)))

        lines.extend(["", "FILES TO BE ORGANIZED", "────────────────────────────────────────", ""])

        for file_path in files:
            category = get_category(file_path)

            icon = self.CATEGORY_ICONS.get(category, "•")

            lines.append(f"{icon} {self.format_filename(file_path.name)}")

            lines.append(f"    └─ {category}")

            lines.append("")

        return "\n".join(lines)

    def preview_files(self):
        if self.is_busy:
            return

        if not self.selected_folder:
            messagebox.showwarning("No Folder Selected", "Please select a folder first.")
            return

        if not self.validate_selected_folder():
            return

        self.run_background_operation("Preview", get_files, self.selected_folder)

    # ================================================================
    # ORGANIZATION SUCCESS
    # ================================================================

    def handle_organization_success(self, moved_files):
        if not moved_files:
            self.last_operation = None

            self.show_message("NOTHING TO ORGANIZE\n\nNo files were found in the selected folder.")

            self.set_status("No files were found to organize.")

            self.update_button_states()

            return

        self.last_operation = moved_files

        summary = self.create_organization_summary(moved_files)

        self.show_result(summary, len(moved_files))

        self.set_status(f"Organization complete • {len(moved_files):,} file(s) moved")

        self.update_button_states()

        messagebox.showinfo(
            "Organization Complete",
            (
                f"Successfully organized "
                f"{len(moved_files):,} file(s).\n\n"
                "The Undo button is now available "
                "for this operation."
            ),
        )

    # ================================================================
    # ORGANIZATION SUMMARY
    # ================================================================

    def create_organization_summary(self, moved_files):
        counts = Counter(item["category"] for item in moved_files)

        lines = [
            "ORGANIZATION COMPLETE",
            "════════════════════════════════════════",
            "",
            (f"Successfully organized {len(moved_files)} file(s)."),
            "",
        ]

        lines.extend(self.create_category_summary(counts, len(moved_files)))

        lines.extend(["", "FILES ORGANIZED", "────────────────────────────────────────", ""])

        for item in moved_files:
            category = item["category"]

            icon = self.CATEGORY_ICONS.get(category, "•")

            source = item.get("source")
            destination = item.get("destination")

            filename = source.name if source is not None else "Unknown file"

            lines.append(f"{icon} {self.format_filename(filename)}")

            lines.append(f"    └─ {category}")

            if destination is not None:
                lines.append(f"       → {destination.name}")

            lines.append("")

        return "\n".join(lines)

    # ================================================================
    # ORGANIZE
    # ================================================================

    def organize_files(self):
        if self.is_busy:
            return

        if not self.selected_folder:
            messagebox.showwarning("No Folder Selected", "Please select a folder first.")
            return

        if not self.validate_selected_folder():
            return

        try:
            files = get_files(self.selected_folder)

        except FileNotFoundError as error:
            messagebox.showerror("Folder Error", f"Could not find the selected folder.\n\n{error}")
            return

        except NotADirectoryError as error:
            messagebox.showerror("Folder Error", f"The selected path is not a folder.\n\n{error}")
            return

        except PermissionError as error:
            messagebox.showerror(
                "Permission Error",
                (f"The application does not have permission to read this folder.\n\n{error}"),
            )
            return

        except OSError as error:
            messagebox.showerror(
                "Folder Error", (f"Could not read the selected folder.\n\n{error}")
            )
            return

        if not files:
            self.show_message(
                "NOTHING TO ORGANIZE\n\n"
                "No regular files were found directly "
                "inside the selected folder."
            )

            self.set_status("No files were found to organize.")

            return

        counts = self.get_category_counts(files)

        summary_lines = self.create_category_summary(counts, len(files))

        confirmation_text = (
            f"Organize {len(files)} file(s) in this folder?\n\n"
            "Files will be moved into these categories:\n\n" + "\n".join(summary_lines[3:]) + "\n\n"
            "Existing destination files will not be overwritten.\n"
            "Duplicate filenames will receive a safe suffix.\n\n"
            "Files will be moved immediately after confirmation.\n\n"
            "Continue?"
        )

        confirmation = messagebox.askyesno("Confirm Organization", confirmation_text)

        if not confirmation:
            return

        self.run_background_operation("Organization", organize_folder, self.selected_folder)

    # ================================================================
    # UNDO SUMMARY
    # ================================================================

    def create_undo_summary(self, restored_files):
        lines = [
            "UNDO COMPLETE",
            "════════════════════════════════════════",
            "",
            (f"Successfully restored {len(restored_files)} file(s)."),
            "",
            "RESTORED FILES",
            "────────────────────────────────────────",
            "",
        ]

        for item in restored_files:
            source = item.get("source")

            filename = source.name if source is not None else "Unknown file"

            lines.append(f"↶ {self.format_filename(filename)}")

            lines.append("    └─ Original location restored")

            lines.append("")

        return "\n".join(lines)

    # ================================================================
    # UNDO
    # ================================================================

    def undo_last_operation(self):
        if self.is_busy:
            return

        if not self.last_operation:
            messagebox.showinfo(
                "Nothing to Undo", ("There is no organization operation available to undo.")
            )
            return

        confirmation = messagebox.askyesno(
            "Confirm Undo",
            (
                "Restore the files to their original "
                "locations?\n\n"
                f"{len(self.last_operation):,} file(s) are "
                "available for restoration.\n\n"
                "Existing files at the original locations "
                "will never be overwritten.\n\n"
                "Continue?"
            ),
        )

        if not confirmation:
            return

        operation = list(self.last_operation)

        self.run_background_operation("Undo", self._perform_undo, operation)

    def get_remaining_undo_items(self, operation):
        """
        Return only files that still appear to need restoration.

        A file remains pending when its destination still exists
        and its original source does not exist.
        """

        remaining = []

        for item in operation:
            source = Path(item["source"])

            destination = Path(item["destination"])

            if destination.exists() and not source.exists():
                remaining.append(item)

        return remaining

    def handle_undo_success(self, result):
        operation, restored_files = result

        if not restored_files:
            remaining = self.get_remaining_undo_items(operation)

            if remaining:
                self.last_operation = remaining

                self.show_message(
                    "NOTHING WAS RESTORED\n\n"
                    "The files could not be restored because "
                    "their original locations are unavailable "
                    "or already contain files.\n\n"
                    "The Undo operation remains available."
                )

                self.set_status(f"Undo incomplete • {len(remaining)} file(s) remain")

            else:
                self.last_operation = None

                self.show_message("NOTHING WAS RESTORED\n\nNo files could be restored.")

                self.set_status("No files could be restored.")

            self.update_button_states()
            return

        remaining = self.get_remaining_undo_items(operation)

        summary = self.create_undo_summary(restored_files)

        if remaining:
            summary += (
                "\n"
                "PARTIAL UNDO\n"
                "────────────────────────────────────────\n\n"
                f"{len(remaining)} file(s) could not be restored.\n"
                "The Undo button remains available so you can "
                "try again later."
            )

        self.show_result(summary, len(restored_files))

        if remaining:
            self.last_operation = remaining

            self.set_status(
                f"Partial undo • {len(restored_files):,} restored • {len(remaining):,} remaining"
            )

            messagebox.showwarning(
                "Partial Undo",
                (
                    f"{len(restored_files):,} file(s) were restored.\n\n"
                    f"{len(remaining):,} file(s) could not be "
                    "restored and remain in Undo history."
                ),
            )

        else:
            self.last_operation = None

            self.set_status(f"Undo complete • {len(restored_files):,} file(s) restored")

            messagebox.showinfo(
                "Undo Complete", (f"Successfully restored {len(restored_files):,} file(s).")
            )

        self.update_button_states()

    def _perform_undo(self, operation):
        restored_files = undo_organization(operation)

        return operation, restored_files

    # ================================================================
    # FOLDER SELECTION
    # ================================================================

    def select_folder(self):
        if self.is_busy:
            return

        folder = filedialog.askdirectory(title="Select folder to organize")

        if not folder:
            return

        selected_path = Path(folder)

        try:
            if not selected_path.exists():
                messagebox.showerror("Invalid Folder", "The selected folder no longer exists.")
                return

            if not selected_path.is_dir():
                messagebox.showerror("Invalid Folder", "The selected path is not a folder.")
                return

        except OSError as error:
            messagebox.showerror(
                "Folder Error", (f"Could not access the selected folder.\n\n{error}")
            )
            return

        # ------------------------------------------------------------
        # New folder invalidates previous undo history.
        # ------------------------------------------------------------

        self.selected_folder = str(selected_path)

        self.last_operation = None

        self.set_folder_entry(self.selected_folder)

        self.update_button_states()

        self.show_message(
            "FOLDER SELECTED\n\n"
            f"{self.selected_folder}\n\n"
            "Click Preview to inspect the files "
            "before organizing them."
        )

        self.set_status(f"Folder selected • {self.selected_folder}")

    # ================================================================
    # CLEAR
    # ================================================================

    def clear(self):
        if self.is_busy:
            return

        if self.last_operation:
            confirmation = messagebox.askyesno(
                "Clear Current Session",
                (
                    "An organization operation can still be undone.\n\n"
                    "Clearing now will discard the Undo history.\n\n"
                    "The files themselves will NOT be restored "
                    "automatically.\n\n"
                    "Continue?"
                ),
            )

            if not confirmation:
                return

        self.selected_folder = None
        self.last_operation = None

        self.set_folder_entry("")

        self.update_button_states()

        self.show_welcome()

    # ================================================================
    # CLOSE
    # ================================================================

    def close_application(self):
        if self.is_busy:
            messagebox.showwarning(
                "Operation In Progress",
                (
                    "Please wait until the current "
                    "operation finishes before closing "
                    "the application."
                ),
            )

            return

        if self.last_operation:
            confirmation = messagebox.askyesno(
                "Exit File Organizer",
                (
                    "There is an organization operation "
                    "that can still be undone.\n\n"
                    "If you exit now, the Undo history "
                    "will be lost.\n\n"
                    "The files will remain in their current "
                    "organized locations.\n\n"
                    "Are you sure you want to exit?"
                ),
            )

            if not confirmation:
                return

        self.root.destroy()


# ====================================================================
# APPLICATION ENTRY POINT
# ====================================================================


def start_app():
    """Create and start the File Organizer application."""

    root = tk.Tk()

    FileOrganizerApp(root)

    root.mainloop()


# ====================================================================
# DIRECT EXECUTION
# ====================================================================

if __name__ == "__main__":
    start_app()
