import tkinter as tk
from tkinter import filedialog, messagebox
from collections import Counter
from pathlib import Path

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

    WINDOW_WIDTH = 940
    WINDOW_HEIGHT = 720
    MIN_WIDTH = 820
    MIN_HEIGHT = 620

    # ================================================================
    # COLOR SYSTEM
    # ================================================================

    COLORS = {
        "bg": "#0B1120",
        "bg_secondary": "#111827",
        "panel": "#151F32",
        "panel_light": "#1B263B",
        "panel_hover": "#202D45",

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
    }

    # ================================================================
    # CATEGORY ORDER
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

        self.configure_window()
        self.create_widgets()
        self.bind_shortcuts()

        self.update_button_states()

        self.show_message(
            "Welcome to File Organizer\n\n"
            "Select a folder to begin organizing your files."
        )

        self.set_status(
            "Ready • Select a folder to get started"
        )

    # ================================================================
    # WINDOW CONFIGURATION
    # ================================================================

    def configure_window(self):
        self.root.title("File Organizer")
        self.root.geometry(
            f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}"
        )
        self.root.minsize(
            self.MIN_WIDTH,
            self.MIN_HEIGHT
        )

        self.root.configure(
            bg=self.COLORS["bg"]
        )

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close_application
        )

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
        top = tk.Frame(
            self.root,
            bg=self.COLORS["bg"]
        )

        top.pack(
            fill="x",
            padx=42,
            pady=(28, 18)
        )

        # Left side
        title_frame = tk.Frame(
            top,
            bg=self.COLORS["bg"]
        )

        title_frame.pack(
            side="left"
        )

        icon = tk.Label(
            title_frame,
            text="▦",
            font=("Segoe UI Symbol", 27, "bold"),
            bg=self.COLORS["bg"],
            fg=self.COLORS["blue"]
        )

        icon.pack(
            side="left",
            padx=(0, 12)
        )

        text_frame = tk.Frame(
            title_frame,
            bg=self.COLORS["bg"]
        )

        text_frame.pack(
            side="left"
        )

        title = tk.Label(
            text_frame,
            text="File Organizer",
            font=("Segoe UI", 25, "bold"),
            bg=self.COLORS["bg"],
            fg=self.COLORS["text"]
        )

        title.pack(
            anchor="w"
        )

        subtitle = tk.Label(
            text_frame,
            text="Smart • Local • Safe file organization",
            font=("Segoe UI", 10),
            bg=self.COLORS["bg"],
            fg=self.COLORS["text_secondary"]
        )

        subtitle.pack(
            anchor="w",
            pady=(2, 0)
        )

        # Right side status
        status_container = tk.Frame(
            top,
            bg=self.COLORS["panel"],
            highlightbackground=self.COLORS["border"],
            highlightthickness=1
        )

        status_container.pack(
            side="right",
            padx=(20, 0),
            pady=5
        )

        self.connection_dot = tk.Label(
            status_container,
            text="●",
            font=("Segoe UI", 9),
            bg=self.COLORS["panel"],
            fg=self.COLORS["green"]
        )

        self.connection_dot.pack(
            side="left",
            padx=(10, 5)
        )

        self.header_status = tk.Label(
            status_container,
            text="LOCAL • OFFLINE",
            font=("Segoe UI", 8, "bold"),
            bg=self.COLORS["panel"],
            fg=self.COLORS["text_secondary"]
        )

        self.header_status.pack(
            side="left",
            padx=(0, 10),
            pady=7
        )

    # ================================================================
    # FOLDER CARD
    # ================================================================

    def create_folder_card(self):
        outer = tk.Frame(
            self.root,
            bg=self.COLORS["border"]
        )

        outer.pack(
            fill="x",
            padx=42,
            pady=(0, 14)
        )

        card = tk.Frame(
            outer,
            bg=self.COLORS["panel"]
        )

        card.pack(
            fill="both",
            expand=True,
            padx=1,
            pady=1
        )

        content = tk.Frame(
            card,
            bg=self.COLORS["panel"]
        )

        content.pack(
            fill="x",
            padx=20,
            pady=18
        )

        # Header row
        heading_row = tk.Frame(
            content,
            bg=self.COLORS["panel"]
        )

        heading_row.pack(
            fill="x"
        )

        folder_icon = tk.Label(
            heading_row,
            text="⌂",
            font=("Segoe UI Symbol", 15, "bold"),
            bg=self.COLORS["panel"],
            fg=self.COLORS["blue"]
        )

        folder_icon.pack(
            side="left",
            padx=(0, 8)
        )

        folder_title = tk.Label(
            heading_row,
            text="Source Folder",
            font=("Segoe UI", 11, "bold"),
            bg=self.COLORS["panel"],
            fg=self.COLORS["text"]
        )

        folder_title.pack(
            side="left"
        )

        folder_hint = tk.Label(
            heading_row,
            text="Choose the folder containing the files",
            font=("Segoe UI", 9),
            bg=self.COLORS["panel"],
            fg=self.COLORS["text_muted"]
        )

        folder_hint.pack(
            side="right"
        )

        # Path row
        path_frame = tk.Frame(
            content,
            bg=self.COLORS["panel"]
        )

        path_frame.pack(
            fill="x",
            pady=(12, 0)
        )

        entry_container = tk.Frame(
            path_frame,
            bg=self.COLORS["border_light"]
        )

        entry_container.pack(
            side="left",
            fill="x",
            expand=True
        )

        self.folder_entry = tk.Entry(
            entry_container,
            font=("Segoe UI", 10),
            state="readonly",
            readonlybackground=self.COLORS["input"],
            fg=self.COLORS["text"],
            relief="flat",
            bd=0,
            insertbackground=self.COLORS["text"]
        )

        self.folder_entry.pack(
            fill="x",
            padx=1,
            pady=1,
            ipady=8
        )

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
            activeforeground=self.COLORS["white"]
        )

        self.browse_button.pack(
            side="left",
            padx=(10, 0),
            ipady=7
        )

        self.add_hover_effect(
            self.browse_button,
            self.COLORS["blue"],
            self.COLORS["blue_hover"]
        )

    # ================================================================
    # ACTION BAR
    # ================================================================

    def create_action_bar(self):
        frame = tk.Frame(
            self.root,
            bg=self.COLORS["bg"]
        )

        frame.pack(
            fill="x",
            padx=42,
            pady=(0, 16)
        )

        # Preview
        self.preview_button = self.create_button(
            frame,
            "Preview",
            self.preview_files,
            self.COLORS["panel_light"],
            self.COLORS["panel_hover"],
            width=14
        )

        self.preview_button.pack(
            side="left",
            padx=(0, 7)
        )

        # Organize
        self.organize_button = self.create_button(
            frame,
            "Organize Files",
            self.organize_files,
            self.COLORS["green_dark"],
            self.COLORS["green"],
            width=16
        )

        self.organize_button.pack(
            side="left",
            padx=7
        )

        # Undo
        self.undo_button = self.create_button(
            frame,
            "Undo",
            self.undo_last_operation,
            self.COLORS["panel_light"],
            self.COLORS["panel_hover"],
            width=14
        )

        self.undo_button.pack(
            side="left",
            padx=7
        )

        # Clear
        self.clear_button = self.create_button(
            frame,
            "Clear",
            self.clear,
            self.COLORS["panel_light"],
            self.COLORS["panel_hover"],
            width=14
        )

        self.clear_button.pack(
            side="left",
            padx=7
        )

        # Shortcut hint
        shortcut = tk.Label(
            frame,
            text="Ctrl+O  Browse    •    Ctrl+P  Preview    •    Ctrl+Z  Undo    •    Esc  Clear",
            font=("Segoe UI", 8),
            bg=self.COLORS["bg"],
            fg=self.COLORS["text_muted"]
        )

        shortcut.pack(
            side="right",
            padx=(15, 0)
        )

    # ================================================================
    # BUTTON FACTORY
    # ================================================================

    def create_button(
        self,
        parent,
        text,
        command,
        background,
        hover_background,
        width=14
    ):
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
            disabledforeground=self.COLORS["text_muted"]
        )

        self.add_hover_effect(
            button,
            background,
            hover_background
        )

        return button

    def add_hover_effect(
        self,
        widget,
        normal_color,
        hover_color
    ):
        def on_enter(event):
            if str(widget["state"]) != "disabled":
                widget.config(
                    bg=hover_color
                )

        def on_leave(event):
            if str(widget["state"]) != "disabled":
                widget.config(
                    bg=normal_color
                )

        widget.bind(
            "<Enter>",
            on_enter
        )

        widget.bind(
            "<Leave>",
            on_leave
        )

    # ================================================================
    # RESULTS AREA
    # ================================================================

    def create_results_area(self):
        heading = tk.Frame(
            self.root,
            bg=self.COLORS["bg"]
        )

        heading.pack(
            fill="x",
            padx=42,
            pady=(0, 7)
        )

        result_title = tk.Label(
            heading,
            text="Activity",
            font=("Segoe UI", 11, "bold"),
            bg=self.COLORS["bg"],
            fg=self.COLORS["text"]
        )

        result_title.pack(
            side="left"
        )

        self.result_count_label = tk.Label(
            heading,
            text="",
            font=("Segoe UI", 9, "bold"),
            bg=self.COLORS["bg"],
            fg=self.COLORS["blue"]
        )

        self.result_count_label.pack(
            side="right"
        )

        # Outer border
        result_outer = tk.Frame(
            self.root,
            bg=self.COLORS["border"]
        )

        result_outer.pack(
            fill="both",
            expand=True,
            padx=42,
            pady=(0, 15)
        )

        result_frame = tk.Frame(
            result_outer,
            bg=self.COLORS["panel"]
        )

        result_frame.pack(
            fill="both",
            expand=True,
            padx=1,
            pady=1
        )

        scrollbar = tk.Scrollbar(
            result_frame,
            orient="vertical",
            bg=self.COLORS["scrollbar"],
            troughcolor=self.COLORS["panel"],
            activebackground=self.COLORS["scrollbar_hover"],
            relief="flat",
            bd=0
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

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
            wrap="none",
            padx=18,
            pady=16,
            spacing1=2,
            spacing3=2,
            yscrollcommand=scrollbar.set
        )

        self.result_text.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.config(
            command=self.result_text.yview
        )

        self.result_text.config(
            state=tk.DISABLED
        )

        # Text tags
        self.result_text.tag_configure(
            "heading",
            foreground=self.COLORS["text"],
            font=("Consolas", 11, "bold")
        )

        self.result_text.tag_configure(
            "accent",
            foreground=self.COLORS["blue"],
            font=("Consolas", 10, "bold")
        )

        self.result_text.tag_configure(
            "success",
            foreground=self.COLORS["green"],
            font=("Consolas", 10, "bold")
        )

        self.result_text.tag_configure(
            "muted",
            foreground=self.COLORS["text_muted"]
        )

        self.result_text.tag_configure(
            "category",
            foreground=self.COLORS["orange"],
            font=("Consolas", 10, "bold")
        )

    # ================================================================
    # STATUS BAR
    # ================================================================

    def create_status_bar(self):
        status = tk.Frame(
            self.root,
            bg=self.COLORS["bg_secondary"],
            height=32
        )

        status.pack(
            fill="x",
            side="bottom"
        )

        status.pack_propagate(False)

        self.status_dot = tk.Label(
            status,
            text="●",
            font=("Segoe UI", 8),
            bg=self.COLORS["bg_secondary"],
            fg=self.COLORS["green"]
        )

        self.status_dot.pack(
            side="left",
            padx=(42, 7)
        )

        self.status_label = tk.Label(
            status,
            text="Ready",
            font=("Segoe UI", 9),
            bg=self.COLORS["bg_secondary"],
            fg=self.COLORS["text_secondary"],
            anchor="w"
        )

        self.status_label.pack(
            side="left"
        )

        self.offline_label = tk.Label(
            status,
            text="OFFLINE • NO INTERNET REQUIRED",
            font=("Segoe UI", 8, "bold"),
            bg=self.COLORS["bg_secondary"],
            fg=self.COLORS["text_muted"]
        )

        self.offline_label.pack(
            side="right",
            padx=42
        )

    # ================================================================
    # KEYBOARD SHORTCUTS
    # ================================================================

    def bind_shortcuts(self):
        self.root.bind(
            "<Control-o>",
            lambda event: self.select_folder()
        )

        self.root.bind(
            "<Control-p>",
            lambda event: self.preview_files()
        )

        self.root.bind(
            "<Control-z>",
            lambda event: self.undo_last_operation()
        )

        self.root.bind(
            "<Escape>",
            lambda event: self.clear()
        )

    # ================================================================
    # UI HELPERS
    # ================================================================

    def set_status(self, message):
        self.status_label.config(
            text=message
        )

    def show_message(self, message):
        self.result_text.config(
            state=tk.NORMAL
        )

        self.result_text.delete(
            "1.0",
            tk.END
        )

        self.result_text.insert(
            tk.END,
            message
        )

        self.result_text.config(
            state=tk.DISABLED
        )

        self.result_count_label.config(
            text=""
        )

    def show_result(self, message, count=None):
        self.result_text.config(
            state=tk.NORMAL
        )

        self.result_text.delete(
            "1.0",
            tk.END
        )

        self.result_text.insert(
            tk.END,
            message
        )

        self.result_text.config(
            state=tk.DISABLED
        )

        if count is None:
            self.result_count_label.config(
                text=""
            )
        else:
            self.result_count_label.config(
                text=f"{count} FILE(S)"
            )

    def set_folder_entry(self, folder):
        self.folder_entry.config(
            state=tk.NORMAL
        )

        self.folder_entry.delete(
            0,
            tk.END
        )

        self.folder_entry.insert(
            0,
            folder
        )

        self.folder_entry.config(
            state="readonly"
        )

    def update_button_states(self):
        has_folder = bool(
            self.selected_folder
        )

        has_undo = bool(
            self.last_operation
        )

        self.preview_button.config(
            state=(
                tk.NORMAL
                if has_folder
                else tk.DISABLED
            )
        )

        self.organize_button.config(
            state=(
                tk.NORMAL
                if has_folder
                else tk.DISABLED
            )
        )

        self.undo_button.config(
            state=(
                tk.NORMAL
                if has_undo
                else tk.DISABLED
            )
        )

        # Update button colors after state change
        if has_folder:
            self.preview_button.config(
                bg=self.COLORS["panel_light"]
            )

            self.organize_button.config(
                bg=self.COLORS["green_dark"]
            )
        else:
            self.preview_button.config(
                bg=self.COLORS["panel"]
            )

            self.organize_button.config(
                bg=self.COLORS["panel"]
            )

        if has_undo:
            self.undo_button.config(
                bg=self.COLORS["panel_light"]
            )
        else:
            self.undo_button.config(
                bg=self.COLORS["panel"]
            )

    # ================================================================
    # CATEGORY HELPERS
    # ================================================================

    def get_category_counts(self, files):
        counts = Counter()

        for file_path in files:
            counts[
                get_category(file_path)
            ] += 1

        return counts

    def create_category_summary(self, counts, total):
        lines = [
            "CATEGORY BREAKDOWN",
            "────────────────────────────────────────",
            ""
        ]

        for category in self.CATEGORY_ORDER:
            count = counts.get(
                category,
                0
            )

            if count <= 0:
                continue

            percentage = (
                count / total * 100
                if total
                else 0
            )

            icon = self.CATEGORY_ICONS.get(
                category,
                "•"
            )

            lines.append(
                f"{icon} {category:<12}"
                f"{count:>5}   "
                f"{percentage:>5.1f}%"
            )

        return lines

    # ================================================================
    # PREVIEW
    # ================================================================

    def create_preview(self, files):
        counts = self.get_category_counts(
            files
        )

        lines = [
            "FILE ORGANIZATION PREVIEW",
            "════════════════════════════════════════",
            "",
            f"Total files detected: {len(files)}",
            "",
        ]

        lines.extend(
            self.create_category_summary(
                counts,
                len(files)
            )
        )

        lines.extend([
            "",
            "FILES TO BE ORGANIZED",
            "────────────────────────────────────────",
            ""
        ])

        for file_path in files:
            category = get_category(
                file_path
            )

            icon = self.CATEGORY_ICONS.get(
                category,
                "•"
            )

            lines.append(
                f"{icon} {file_path.name}"
            )

            lines.append(
                f"    └─ {category}"
            )

            lines.append("")

        return "\n".join(lines)

    def preview_files(self):
        if not self.selected_folder:
            messagebox.showwarning(
                "No Folder Selected",
                "Please select a folder first."
            )
            return

        self.set_status(
            "Scanning selected folder..."
        )

        self.root.update_idletasks()

        try:
            files = get_files(
                self.selected_folder
            )

            if not files:
                self.show_message(
                    "NO FILES FOUND\n\n"
                    "The selected folder does not contain "
                    "any files to organize."
                )

                self.set_status(
                    "Selected folder contains no files."
                )

                return

            preview = self.create_preview(
                files
            )

            self.show_result(
                preview,
                len(files)
            )

            self.set_status(
                f"Preview ready • {len(files)} file(s) detected"
            )

        except (
            FileNotFoundError,
            NotADirectoryError
        ) as error:

            self.set_status(
                "Unable to access selected folder."
            )

            messagebox.showerror(
                "Folder Error",
                str(error)
            )

        except OSError as error:

            self.set_status(
                "Folder could not be read."
            )

            messagebox.showerror(
                "File System Error",
                f"Could not read the folder.\n\n{error}"
            )

    # ================================================================
    # ORGANIZATION SUMMARY
    # ================================================================

    def create_organization_summary(
        self,
        moved_files
    ):
        counts = Counter(
            item["category"]
            for item in moved_files
        )

        lines = [
            "ORGANIZATION COMPLETE",
            "════════════════════════════════════════",
            "",
            f"Successfully organized "
            f"{len(moved_files)} file(s).",
            "",
        ]

        lines.extend(
            self.create_category_summary(
                counts,
                len(moved_files)
            )
        )

        lines.extend([
            "",
            "FILES ORGANIZED",
            "────────────────────────────────────────",
            ""
        ])

        for item in moved_files:
            category = item["category"]

            icon = self.CATEGORY_ICONS.get(
                category,
                "•"
            )

            lines.append(
                f"{icon} {item['source'].name}"
            )

            lines.append(
                f"    └─ {category}"
            )

            lines.append("")

        return "\n".join(lines)

    # ================================================================
    # ORGANIZE
    # ================================================================

    def organize_files(self):
        if not self.selected_folder:
            messagebox.showwarning(
                "No Folder Selected",
                "Please select a folder first."
            )
            return

        confirmation = messagebox.askyesno(
            "Confirm Organization",
            (
                "Organize all files in this folder?\n\n"
                "• Files will be moved into category folders.\n"
                "• Existing files will not be overwritten.\n"
                "• Duplicate names will receive a safe suffix.\n\n"
                "Continue?"
            )
        )

        if not confirmation:
            return

        self.set_status(
            "Organizing files..."
        )

        self.root.update_idletasks()

        try:
            moved_files = organize_folder(
                self.selected_folder
            )

            if not moved_files:
                self.last_operation = None

                self.update_button_states()

                self.show_message(
                    "NOTHING TO ORGANIZE\n\n"
                    "No files were found in the selected folder."
                )

                self.set_status(
                    "No files were found to organize."
                )

                return

            self.last_operation = moved_files

            self.update_button_states()

            summary = (
                self.create_organization_summary(
                    moved_files
                )
            )

            self.show_result(
                summary,
                len(moved_files)
            )

            self.set_status(
                f"Organization complete • "
                f"{len(moved_files)} file(s) moved"
            )

            messagebox.showinfo(
                "Organization Complete",
                (
                    f"Successfully organized "
                    f"{len(moved_files)} file(s).\n\n"
                    "The Undo button is now available "
                    "for this operation."
                )
            )

        except (
            FileNotFoundError,
            NotADirectoryError
        ) as error:

            self.set_status(
                "Organization failed."
            )

            messagebox.showerror(
                "Organization Error",
                str(error)
            )

        except OSError as error:

            self.set_status(
                "Organization failed."
            )

            messagebox.showerror(
                "File System Error",
                (
                    "Could not organize the files.\n\n"
                    f"{error}"
                )
            )

    # ================================================================
    # UNDO SUMMARY
    # ================================================================

    def create_undo_summary(
        self,
        restored_files
    ):
        lines = [
            "UNDO COMPLETE",
            "════════════════════════════════════════",
            "",
            f"Successfully restored "
            f"{len(restored_files)} file(s).",
            "",
            "RESTORED FILES",
            "────────────────────────────────────────",
            ""
        ]

        for item in restored_files:
            lines.append(
                f"↶ {item['source'].name}"
            )

            lines.append(
                "    └─ Original location restored"
            )

            lines.append("")

        return "\n".join(lines)

    # ================================================================
    # UNDO
    # ================================================================

    def undo_last_operation(self):
        if not self.last_operation:
            messagebox.showinfo(
                "Nothing to Undo",
                (
                    "There is no organization operation "
                    "available to undo."
                )
            )
            return

        confirmation = messagebox.askyesno(
            "Confirm Undo",
            (
                "Restore the files to their original "
                "locations?\n\n"
                "This will reverse the most recent "
                "organization operation."
            )
        )

        if not confirmation:
            return

        self.set_status(
            "Restoring files..."
        )

        self.root.update_idletasks()

        try:
            restored_files = undo_organization(
                self.last_operation
            )

            self.last_operation = None

            self.update_button_states()

            if not restored_files:
                self.show_message(
                    "NOTHING WAS RESTORED\n\n"
                    "No files could be restored."
                )

                self.set_status(
                    "No files could be restored."
                )

                return

            summary = self.create_undo_summary(
                restored_files
            )

            self.show_result(
                summary,
                len(restored_files)
            )

            self.set_status(
                f"Undo complete • "
                f"{len(restored_files)} file(s) restored"
            )

            messagebox.showinfo(
                "Undo Complete",
                (
                    f"Successfully restored "
                    f"{len(restored_files)} file(s)."
                )
            )

        except OSError as error:

            self.set_status(
                "Undo operation failed."
            )

            messagebox.showerror(
                "Undo Error",
                (
                    "Could not restore the files.\n\n"
                    f"{error}"
                )
            )

    # ================================================================
    # FOLDER SELECTION
    # ================================================================

    def select_folder(self):
        folder = filedialog.askdirectory(
            title="Select folder to organize"
        )

        if not folder:
            return

        selected_path = Path(
            folder
        )

        if not selected_path.exists():
            messagebox.showerror(
                "Invalid Folder",
                "The selected folder no longer exists."
            )
            return

        if not selected_path.is_dir():
            messagebox.showerror(
                "Invalid Folder",
                "The selected path is not a folder."
            )
            return

        self.selected_folder = str(
            selected_path
        )

        # Selecting another folder invalidates
        # the previous undo operation.
        self.last_operation = None

        self.set_folder_entry(
            self.selected_folder
        )

        self.update_button_states()

        self.show_message(
            "FOLDER SELECTED\n\n"
            f"{self.selected_folder}\n\n"
            "Click Preview to inspect the files "
            "before organizing them."
        )

        self.set_status(
            f"Folder selected • {self.selected_folder}"
        )

    # ================================================================
    # CLEAR
    # ================================================================

    def clear(self):
        self.selected_folder = None
        self.last_operation = None

        self.set_folder_entry(
            ""
        )

        self.update_button_states()

        self.show_message(
            "WELCOME TO FILE ORGANIZER\n\n"
            "Select a folder to begin organizing "
            "your files."
        )

        self.set_status(
            "Ready • Select a folder to get started"
        )

    # ================================================================
    # CLOSE
    # ================================================================

    def close_application(self):
        if self.last_operation:
            confirmation = messagebox.askyesno(
                "Exit File Organizer",
                (
                    "There is an organization operation "
                    "that can still be undone.\n\n"
                    "If you exit now, the Undo history "
                    "will be lost.\n\n"
                    "Are you sure you want to exit?"
                )
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

    FileOrganizerApp(
        root
    )

    root.mainloop()